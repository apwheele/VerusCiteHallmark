"""Quiet watcher for the VerusCite upload. Prints only when the run ends or stalls.

Progress goes to results/watch.log. Stdout is reserved for DONE, FAILED, and
ACTION_REQUIRED so a monitor can wake on those lines.
"""

from __future__ import annotations

import json
import os
import sys
import time
from pathlib import Path

import requests

ROOT = Path(__file__).resolve().parents[1]
API = "https://veruscite.com/api/v1"
POLL_SECONDS = 30
STALL_SECONDS = 25 * 60


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


def log(text: str) -> None:
    path = ROOT / "results" / "watch.log"
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(text + "\n")


def progressed(doc: dict) -> int:
    """Citations finished for the stall counter.

    While a document is running, verified_citations is the progress counter.
    After it completes, that field is the count of the verified label, which
    is smaller. Counting a finished document as its total keeps the sum from
    falling and looking like a stall.
    """
    total = int(doc.get("total_citations") or 0)
    done = int(doc.get("verified_citations") or 0)
    if doc.get("finished") or doc.get("status") == "completed":
        return total
    return done


def main() -> None:
    load_env()
    key = os.environ.get("VC_API_KEY") or os.environ.get("VERUSCITE_API_KEY")
    if not key:
        print("FAILED: VC_API_KEY is not set")
        return
    headers = {"Authorization": f"Bearer {key}"}
    state_path = ROOT / "results" / "watch_state.json"
    last_sum = None
    last_change = time.time()
    stalled = False
    # Wait until the submit script has recorded document ids.
    deadline = time.time() + 15 * 60
    jobs_path = ROOT / "results" / "documents.json"
    while not jobs_path.exists():
        if time.time() > deadline:
            print("FAILED: results/documents.json was not written")
            return
        time.sleep(5)

    while True:
        try:
            payload = json.loads(jobs_path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError) as exc:
            log(f"state read {type(exc).__name__}")
            time.sleep(POLL_SECONDS)
            continue
        jobs = payload.get("jobs") or []
        if not jobs:
            if time.time() > deadline:
                print("FAILED: documents.json has no jobs")
                return
            time.sleep(5)
            continue

        snapshots = []
        failed = None
        finished = 0
        for job in jobs:
            try:
                response = requests.get(
                    f"{API}/documents/{job['document_id']}",
                    headers=headers,
                    timeout=60,
                )
            except requests.RequestException as exc:
                log(f"transport {type(exc).__name__}")
                time.sleep(POLL_SECONDS)
                break
            if response.status_code >= 400:
                print(f"FAILED: document {job['document_id']} HTTP {response.status_code}")
                return
            doc = response.json()
            if doc.get("status") == "failed":
                failed = doc
            if doc.get("finished") and doc.get("status") == "completed":
                finished += 1
            snapshots.append(
                (
                    job["batch"],
                    doc.get("status"),
                    doc.get("verified_citations"),
                    doc.get("total_citations"),
                    progressed(doc),
                )
            )
        else:
            progress = sum(int(item[4] or 0) for item in snapshots)
            now = time.time()
            if last_sum is None or progress != last_sum:
                last_sum = progress
                last_change = now
                stalled = False
            log(
                " ".join(
                    f"b{b}:{status}:{done}/{total}"
                    for b, status, done, total, _progressed in snapshots
                )
            )
            if failed is not None:
                print(
                    "FAILED: document "
                    f"{failed.get('id')} {failed.get('error')} {failed.get('error_message')}"
                )
                return
            if finished == len(jobs):
                csv_path = ROOT / "results" / "veruscite.csv"
                # The submit script writes the joined table after the share links.
                if csv_path.exists() and all(job.get("share_url") for job in jobs):
                    print(f"DONE: {len(jobs)} documents, {progress} citations")
                    return
                log("finished waiting for share urls and veruscite.csv")
            elif not stalled and now - last_change > STALL_SECONDS:
                stalled = True
                print(
                    "ACTION_REQUIRED: no new verified citations for "
                    f"{int(STALL_SECONDS / 60)} minutes ({progress} so far)"
                )
            state_path.write_text(
                json.dumps({"progress": progress, "finished": finished, "n": len(jobs)}),
                encoding="utf-8",
            )
            time.sleep(POLL_SECONDS)


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(f"FAILED: watcher {type(exc).__name__}: {exc}")
        sys.exit(1)
