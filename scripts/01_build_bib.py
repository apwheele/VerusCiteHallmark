"""Build the blinded Hallmark bibliography and collision-free batches.

VerusCite marks a later entry as a duplicate when the normalized title and
authors match an earlier entry, and it does not check that duplicate on its
own. Hallmark puts a real paper and a copy with the venue, year, or DOI
changed into the same split. One file would copy the first verdict onto the
second. This script writes the combined BibTeX file, then slices each
collision-free set into uploads of at most MAX_PER_UPLOAD entries. The worker
soft-stops a document at 20 minutes, and a larger file would not finish.

Labels stay in data/labels.csv. They are not written into the BibTeX.
"""

from __future__ import annotations

import json
import os
import re
import subprocess
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HALLMARK_ROOT = Path(os.environ.get("HALLMARK_ROOT", r"G:\hallmark"))
CITECHECK_ROOT = Path(os.environ.get("CITECHECK_ROOT", r"G:\CiteCheck"))
DATA_DIR = HALLMARK_ROOT / "data" / "v1.2"
PINNED_COMMIT = "c62d296d1d2e3e6f9cb325e37963b63350ab2ca4"
# A 25-entry probe finished in 76 seconds. The worker soft-stops a document
# at 20 minutes, so each upload stays at or under this size.
MAX_PER_UPLOAD = 300
PROBE = {"n": 25, "seconds": 76}

SPLITS = (
    ("dev_public", "dev_public.jsonl", "dev_public_blind.jsonl"),
    ("test_public", "test_public.jsonl", "test_public_blind.jsonl"),
    ("stress_test", "stress_test.jsonl", "stress_test_blind.jsonl"),
)

FIELD_ORDER = ["author", "title", "year", "booktitle", "journal", "doi"]
KEY_RE = re.compile(r"@\w+\s*\{\s*([^,\s]+)\s*,")


def _load_jsonl(path: Path) -> list[dict]:
    rows = []
    with path.open(encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


def _commit() -> str:
    try:
        out = subprocess.check_output(
            ["git", "rev-parse", "HEAD"],
            cwd=HALLMARK_ROOT,
            text=True,
        )
    except (OSError, subprocess.CalledProcessError):
        return ""
    return out.strip()


def _import_parser():
    sys.path[:0] = [str(CITECHECK_ROOT), str(CITECHECK_ROOT / "python")]
    from services.bibliography_import import parse_bibliography_text
    from shared.citation_utils import _dedup_identity_keys

    return parse_bibliography_text, _dedup_identity_keys


def _clean(value: str) -> str:
    return re.sub(r"\s+", " ", str(value).replace("\n", " ")).strip()


def format_entry(entry: dict) -> str:
    fields = entry["fields"]
    names = [name for name in FIELD_ORDER if _clean(fields.get(name, ""))]
    names += [name for name in fields if name not in FIELD_ORDER and _clean(fields.get(name, ""))]
    lines = [f"@{entry['bibtex_type']}{{{entry['key']},"]
    for name in names:
        lines.append(f"  {name} = {{{_clean(fields[name])}}},")
    lines.append("}")
    return "\n".join(lines)


def format_file(entries: list[dict], header: str) -> str:
    blocks = [header.rstrip(), ""]
    for entry in entries:
        blocks.append(format_entry(entry))
        blocks.append("")
    return "\n".join(blocks)


def _title_key(citation: dict, identity_keys) -> str:
    keys = identity_keys(citation)
    for key in keys:
        if key.startswith("title:"):
            return key
    if keys:
        return keys[0]
    raw = (citation.get("raw_text") or "")[:160]
    return f"raw:{raw}"


def _key_from_raw(raw: str) -> str | None:
    match = KEY_RE.search(raw or "")
    return match.group(1) if match else None


def load_entries() -> list[dict]:
    entries = []
    for split, full_name, blind_name in SPLITS:
        labels = {row["bibtex_key"]: row for row in _load_jsonl(DATA_DIR / full_name)}
        for index, blind in enumerate(_load_jsonl(DATA_DIR / blind_name)):
            key = blind["bibtex_key"]
            labeled = labels[key]
            entries.append(
                {
                    "key": key,
                    "split": split,
                    "order": index,
                    "bibtex_type": blind["bibtex_type"],
                    "fields": blind["fields"],
                    "label": labeled["label"],
                    "hallucination_type": labeled.get("hallucination_type") or "",
                    "difficulty_tier": labeled.get("difficulty_tier") or "",
                    "generation_method": labeled.get("generation_method") or "",
                }
            )
    return entries


def main() -> None:
    commit = _commit()
    if commit and commit != PINNED_COMMIT:
        print(f"Hallmark HEAD is {commit}, expected {PINNED_COMMIT}")
    parse_bibliography_text, identity_keys = _import_parser()
    entries = load_entries()
    by_key = {entry["key"]: entry for entry in entries}

    header = (
        "% Hallmark public splits, blinded (no url, no labels).\n"
        f"% Source https://github.com/rpatrik96/hallmark commit {PINNED_COMMIT}\n"
        "% Splits: dev_public, test_public, stress_test. Version 1.2.4."
    )
    combined = format_file(entries, header)
    parsed = parse_bibliography_text(combined)
    if len(parsed) != len(entries):
        found = {_key_from_raw(row.get("raw_text") or "") for row in parsed}
        missing = [entry["key"] for entry in entries if entry["key"] not in found]
        raise SystemExit(f"Parser kept {len(parsed)} of {len(entries)}. Missing: {missing[:10]}")

    groups: dict[str, list[str]] = defaultdict(list)
    dedup_of: dict[str, str] = {}
    for citation in parsed:
        key = _key_from_raw(citation.get("raw_text") or "")
        if key is None or key not in by_key:
            raise SystemExit(f"Could not read a known key from {citation.get('title')!r}")
        dedup = _title_key(citation, identity_keys)
        dedup_of[key] = dedup
        groups[dedup].append(key)

    collision_slot: dict[str, int] = {}
    for members in groups.values():
        members.sort(key=lambda key: (by_key[key]["split"], by_key[key]["order"], key))
        for slot, key in enumerate(members):
            collision_slot[key] = slot

    # Within one collision slot every title-and-author key is unique, so any
    # slice of that slot is still safe to upload together.
    by_collision: dict[int, list[str]] = defaultdict(list)
    for entry in entries:
        by_collision[collision_slot[entry["key"]]].append(entry["key"])
    batch_of: dict[str, int] = {}
    slot_index = 0
    for collision in sorted(by_collision):
        members = by_collision[collision]
        for start in range(0, len(members), MAX_PER_UPLOAD):
            for key in members[start : start + MAX_PER_UPLOAD]:
                batch_of[key] = slot_index
            slot_index += 1

    n_batches = slot_index
    out_dir = ROOT / "data"
    batch_dir = out_dir / "batches"
    batch_dir.mkdir(parents=True, exist_ok=True)
    max_collision = max(len(members) for members in by_collision.values())

    combined_path = out_dir / "hallmark_public.bib"
    combined_path.write_text(combined, encoding="utf-8")

    for slot in range(n_batches):
        chosen = [entry for entry in entries if batch_of[entry["key"]] == slot]
        text = format_file(
            chosen,
            header + f"\n% Collision-free batch {slot + 1} of {n_batches}.",
        )
        path = batch_dir / f"part_{slot:02d}.bib"
        path.write_text(text, encoding="utf-8")
        checked = parse_bibliography_text(text)
        duplicates = [row for row in checked if row.get("is_duplicate")]
        if len(checked) != len(chosen) or duplicates:
            raise SystemExit(
                f"{path.name}: parsed {len(checked)} of {len(chosen)}, "
                f"duplicates {len(duplicates)}"
            )

    for stale in batch_dir.glob("part_*.bib"):
        slot = int(stale.stem.split("_")[1])
        if slot >= n_batches:
            stale.unlink()

    import pandas as pd

    rows = []
    for entry in entries:
        rows.append(
            {
                "bibtex_key": entry["key"],
                "split": entry["split"],
                "label": entry["label"],
                "hallucination_type": entry["hallucination_type"],
                "difficulty_tier": entry["difficulty_tier"],
                "generation_method": entry["generation_method"],
                "batch": batch_of[entry["key"]],
                "dedup_key": dedup_of[entry["key"]],
            }
        )
    labels = pd.DataFrame(rows)
    labels.to_csv(out_dir / "labels.csv", index=False)

    extras = len(labels) - labels["dedup_key"].nunique()
    mixed = sum(part["label"].nunique() > 1 for _, part in labels.groupby("dedup_key"))
    sizes = {int(batch): int(size) for batch, size in labels.groupby("batch").size().items()}
    # One credit per 100 citations in a document, rounded up. Duplicates are
    # free, and these files have none.
    credits = sum((size + 99) // 100 for size in sizes.values())
    source = {
        "repo": "https://github.com/rpatrik96/hallmark",
        "commit": commit or PINNED_COMMIT,
        "pinned_commit": PINNED_COMMIT,
        "version": "1.2.4",
        "blind": True,
        "splits": [name for name, _, _ in SPLITS],
        "n": len(entries),
        "batches": n_batches,
        "max_collision": max_collision,
        "max_per_upload": MAX_PER_UPLOAD,
        "probe": PROBE,
        "credits": credits,
        "batch_sizes": sizes,
    }
    (out_dir / "SOURCE.json").write_text(json.dumps(source, indent=2) + "\n", encoding="utf-8")
    print(f"entries {len(labels)} batches {n_batches} sizes {sizes}")
    print(f"would-be duplicates in one file {extras} mixed groups {mixed}")
    print(f"credits at one per 100 citations, rounded up per file: {credits}")


if __name__ == "__main__":
    main()
