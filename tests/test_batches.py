import re
from pathlib import Path

import pandas as pd

from hallmarkcite.report import metrics_for, suspicion

ROOT = Path(__file__).resolve().parents[1]
KEY_RE = re.compile(r"@\w+\s*\{\s*([^,\s]+)\s*,")


def _keys(path: Path) -> list[str]:
    return KEY_RE.findall(path.read_text(encoding="utf-8"))


def test_bibliography_matches_labels():
    labels = pd.read_csv(ROOT / "data" / "labels.csv")
    assert labels["bibtex_key"].is_unique
    combined = _keys(ROOT / "data" / "hallmark_public.bib")
    assert combined == labels["bibtex_key"].tolist()
    assert "HALLUCINATED" not in (ROOT / "data" / "hallmark_public.bib").read_text(encoding="utf-8")

    seen = []
    for path in sorted((ROOT / "data" / "batches").glob("part_*.bib")):
        slot = int(path.stem.split("_")[1])
        keys = _keys(path)
        part = labels[labels["batch"] == slot]
        assert keys == part["bibtex_key"].tolist()
        assert part["dedup_key"].is_unique
        text = path.read_text(encoding="utf-8")
        assert "HALLUCINATED" not in text
        assert "url =" not in text
        seen.extend(keys)
    assert sorted(seen) == sorted(labels["bibtex_key"])


def test_suspicion_stays_inside_label_bins():
    assert suspicion("hallucination", 0) > suspicion("not_found", 1)
    assert suspicion("not_found", 0) > suspicion("minor_error", 1)
    assert suspicion("minor_error", 0) > suspicion("verified", 0)
    assert suspicion("verified", 1) < suspicion("verified", 0)


def test_not_found_is_a_miss_until_that_rule_is_used():
    frame = pd.DataFrame(
        [
            {
                "split": "dev_public",
                "label": "HALLUCINATED",
                "vc_status": "not_found",
                "vc_confidence": 0.8,
                "hallucination_type": "plausible_fabrication",
            },
            {
                "split": "dev_public",
                "label": "VALID",
                "vc_status": "verified",
                "vc_confidence": 0.9,
                "hallucination_type": "",
            },
            {
                "split": "dev_public",
                "label": "HALLUCINATED",
                "vc_status": "minor_error",
                "vc_confidence": 0.7,
                "hallucination_type": "wrong_venue",
            },
        ]
    )
    strict = metrics_for(frame, "dev_public", "hallucination")
    assert strict["recall"] == 0
    assert strict["fpr"] == 0
    wider = metrics_for(frame, "dev_public", "hall_or_nf")
    assert wider["tp"] == 1
    assert wider["recall"] == 0.5
    assert wider["fpr"] == 0
    broad = metrics_for(frame, "dev_public", "not_verified")
    assert broad["recall"] == 1
    assert broad["fpr"] == 0
