"""Upload the collision-free BibTeX batches to the VerusCite API and save results.

Reads VC_API_KEY from the environment or from .env in the repo root. The key
is not printed. Re-running the script polls documents already in
results/documents.json instead of uploading them again.

    uv run python scripts/02_submit.py
    uv run python scripts/02_submit.py --combined
"""

from __future__ import annotations

import argparse
import json
import os
import re
import time
from pathlib import Path

import pandas as pd
import requests

ROOT = Path(__file__).resolve().parents[1]
API = os.environ.get("VERUSCITE_API_BASE", "https://veruscite.com/api/v1")
KEY_RE = re.compile(r"@\w+\s*\{\s*([^,\s]+)\s*,")
POLL_SECONDS = 30


def load_env() -> None:
    path = ROOT / ".env"
    if not path.exists():
        return
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        name, value = line.split("=", 1)
        os.environ.setdefault(name.strip(), value.strip().strip('"').strip("'"))


def api_key() -> str:
    load_env()
    key = os.environ.get("VC_API_KEY") or os.environ.get("VERUSCITE_API_KEY")
    if not key:
        raise SystemExit("Set VC_API_KEY in .env or the environment.")
    return key


def headers() -> dict[str, str]:
    return {"Authorization": f"Bearer {api_key()}"}


def jobs_path() -> Path:
    return ROOT / "results" / "documents.json"


def load_state() -> dict:
    path = jobs_path()
    if path.exists():
        return json.loads(path.read_text(encoding="utf-8"))
    return {"api": API, "jobs": []}


def save_state(state: dict) -> None:
    """Write documents.json. Dropbox often denies an immediate replace, so retry."""
    path = jobs_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = json.dumps(state, indent=2) + "\n"
    last_error: Exception | None = None
    for attempt in range(12):
        temporary = path.with_name(f"documents.{os.getpid()}.{attempt}.tmp")
        try:
            temporary.write_text(payload, encoding="utf-8")
            os.replace(temporary, path)
            return
        except PermissionError as exc:
            last_error = exc
            time.sleep(0.4 * (attempt + 1))
        finally:
            if temporary.exists():
                try:
                    temporary.unlink()
                except OSError:
                    pass
    try:
        path.write_text(payload, encoding="utf-8")
    except OSError as exc:
        raise SystemExit(f"Could not write {path.name}: {last_error or exc}") from exc


def request(method: str, url: str, **kwargs):
    attempts = 5 if method == "GET" else 1
    last_error = "no response"
    for attempt in range(attempts):
        try:
            response = requests.request(method, url, headers=headers(), timeout=180, **kwargs)
        except requests.RequestException as exc:
            last_error = type(exc).__name__
            if method != "GET":
                raise SystemExit(f"{method} {url} failed: {last_error}") from exc
            time.sleep(5 * (attempt + 1))
            continue
        if response.status_code in (502, 503, 504) and method == "GET" and attempt + 1 < attempts:
            time.sleep(5 * (attempt + 1))
            continue
        if response.status_code >= 400:
            raise SystemExit(f"{method} {url} -> {response.status_code}: {response.text[:500]}")
        return response
    raise SystemExit(f"{method} {url} failed: {last_error}")


def upload(path: Path, batch: int) -> dict:
    with path.open("rb") as handle:
        response = request(
            "POST",
            f"{API}/documents",
            files={"file": (path.name, handle, "application/x-bibtex")},
        )
    doc_id = response.json()["document"]["id"]
    print(f"uploaded batch {batch} as document {doc_id}", flush=True)
    return {
        "batch": batch,
        "file": str(path.relative_to(ROOT)).replace("\\", "/"),
        "document_id": doc_id,
        "share_url": None,
    }


def annotate(job: dict, n_batches: int) -> None:
    """Rename the document. The id is already saved, so a failed patch is not a re-upload."""
    batch = job["batch"]
    note = (
        "Hallmark v1.2.4 blinded public splits "
        "(dev_public, test_public, stress_test). "
        f"Collision-free batch {batch + 1} of {n_batches}. "
        "https://github.com/rpatrik96/hallmark"
    )
    request(
        "PATCH",
        f"{API}/documents/{job['document_id']}",
        json={
            "filename": f"Hallmark public part {batch + 1} of {n_batches}",
            "notes": note,
        },
    )


def poll_until_done(state: dict) -> None:
    pending = [job for job in state["jobs"] if not job.get("share_url")]
    while pending:
        still = []
        for job in pending:
            doc = request("GET", f"{API}/documents/{job['document_id']}").json()
            status = doc.get("status")
            done = doc.get("verified_citations")
            total = doc.get("total_citations")
            print(
                f"batch {job['batch']} doc {job['document_id']} "
                f"{status} {done}/{total}",
                flush=True,
            )
            if status == "failed":
                raise SystemExit(
                    f"Document {job['document_id']} failed: "
                    f"{doc.get('error')} {doc.get('error_message')}"
                )
            if doc.get("finished") and status == "completed":
                save_results(job)
                share = request("POST", f"{API}/documents/{job['document_id']}/share").json()
                job["share_url"] = share.get("share_url") or doc.get("share_url")
                print(f"batch {job['batch']} share {job['share_url']}", flush=True)
                save_state(state)
            else:
                still.append(job)
        pending = still
        if pending:
            time.sleep(POLL_SECONDS)


def save_results(job: dict) -> None:
    payload = request("GET", f"{API}/documents/{job['document_id']}/results").json()
    out = ROOT / "results" / "api" / f"part_{job['batch']:02d}.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(payload), encoding="utf-8")
    job["saved_results"] = str(out.relative_to(ROOT)).replace("\\", "/")


def join_table(state: dict) -> None:
    labels = pd.read_csv(ROOT / "data" / "labels.csv")
    rows = []
    for job in state["jobs"]:
        payload = json.loads((ROOT / job["saved_results"]).read_text(encoding="utf-8"))
        for citation in payload.get("citations", []):
            if citation.get("version") not in (None, "original"):
                continue
            match = KEY_RE.search(citation.get("raw_text") or "")
            key = match.group(1) if match else ""
            authors = citation.get("authors") or []
            if isinstance(authors, list):
                authors = " and ".join(str(author) for author in authors)
            rows.append(
                {
                    "bibtex_key": key,
                    "batch": job["batch"],
                    "document_id": job["document_id"],
                    "vc_id": citation.get("id"),
                    "vc_status": citation.get("status") or "",
                    "vc_confidence": citation.get("confidence"),
                    "vc_title": citation.get("title") or "",
                    "vc_authors": authors,
                    "vc_year": citation.get("year"),
                    "vc_doi": citation.get("doi") or "",
                    "vc_matched_title": citation.get("matched_title") or "",
                    "vc_matched_doi": citation.get("matched_doi") or "",
                    "vc_notes": citation.get("notes") or "",
                    "vc_verification_method": citation.get("verification_method") or "",
                }
            )
    found = pd.DataFrame(rows)
    if found["bibtex_key"].duplicated().any():
        dupes = found.loc[found["bibtex_key"].duplicated(keep=False), "bibtex_key"].unique()
        raise SystemExit(f"Duplicate keys in API results: {list(dupes)[:8]}")
    merged = labels.merge(found, on=["bibtex_key", "batch"], how="left", indicator=True)
    missing = int((merged["_merge"] != "both").sum())
    if missing:
        keys = merged.loc[merged["_merge"] != "both", "bibtex_key"].head(8).tolist()
        raise SystemExit(f"{missing} labels did not match an API row, for example {keys}")
    merged = merged.drop(columns=["_merge"])
    out = ROOT / "results" / "veruscite.csv"
    merged.to_csv(out, index=False)
    print(f"wrote {out} ({len(merged)} rows)", flush=True)


def batch_files(combined: bool) -> list[tuple[int, Path]]:
    if combined:
        return [(0, ROOT / "data" / "hallmark_public.bib")]
    paths = sorted((ROOT / "data" / "batches").glob("part_*.bib"))
    if not paths:
        raise SystemExit("No batches. Run scripts/01_build_bib.py first.")
    files = []
    for path in paths:
        slot = int(path.stem.split("_")[1])
        files.append((slot, path))
    return files


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--combined",
        action="store_true",
        help="Upload the one combined file. Same-title copies are marked duplicate and not checked.",
    )
    args = parser.parse_args()
    state = load_state()
    if args.combined and state["jobs"] and any(job["batch"] != 0 or "part_" in job["file"] for job in state["jobs"]):
        raise SystemExit("results/documents.json already has the batch jobs. Not uploading the combined file over them.")
    files = batch_files(args.combined)
    known = {job["batch"]: job for job in state["jobs"]}
    n_batches = len(files)
    for slot, path in files:
        if slot in known and known[slot].get("document_id"):
            print(f"batch {slot} already document {known[slot]['document_id']}", flush=True)
            annotate(known[slot], n_batches)
            continue
        job = upload(path, slot)
        state["jobs"] = [item for item in state["jobs"] if item["batch"] != slot]
        state["jobs"].append(job)
        state["jobs"].sort(key=lambda item: item["batch"])
        save_state(state)
        annotate(job, n_batches)
    poll_until_done(state)
    join_table(state)


if __name__ == "__main__":
    main()
