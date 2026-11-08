"""Tables and scores for the Hallmark evaluation.

Every number in the paper comes from here. VerusCite's confidence is how sure
it is of the label it assigned, not the probability that the entry is a
Hallmark hallucination. The suspicion score keeps the four labels in order and
uses confidence only to break ties inside a label.
"""

from __future__ import annotations

import json
from pathlib import Path

import pandas as pd
from sklearn.metrics import auc, roc_curve, roc_auc_score

ROOT = Path(__file__).resolve().parents[2]

STATUS_ORDER = ["verified", "minor_error", "not_found", "hallucination"]
STATUS_LABELS = {
    "verified": "Verified",
    "minor_error": "Minor error",
    "not_found": "Not found",
    "hallucination": "Hallucination",
}

# Higher means "more like a Hallmark hallucination" for the ROC score.
STATUS_RANK = {name: i for i, name in enumerate(STATUS_ORDER)}

RULES = {
    "hallucination": ("hallucination",),
    "hall_or_nf": ("hallucination", "not_found"),
    "not_verified": ("hallucination", "not_found", "minor_error"),
}
RULE_LABELS = {
    "hallucination": "Hallucination only",
    "hall_or_nf": "Hallucination or not found",
    "not_verified": "Anything but verified",
}

# Hallmark types that describe a real paper cited with the wrong metadata.
# The benchmark paper treats these as the unstable part of the label.
REAL_PAPER_TYPES = (
    "wrong_venue",
    "preprint_as_published",
    "partial_author_list",
    "arxiv_version_mismatch",
)

TYPE_ORDER = [
    "fabricated_doi",
    "nonexistent_venue",
    "placeholder_authors",
    "future_date",
    "chimeric_title",
    "wrong_venue",
    "swapped_authors",
    "preprint_as_published",
    "hybrid_fabrication",
    "merged_citation",
    "partial_author_list",
    "near_miss_title",
    "plausible_fabrication",
    "arxiv_version_mismatch",
]
TYPE_LABELS = {name: name.replace("_", " ") for name in TYPE_ORDER}

TYPE_TIER = {
    "fabricated_doi": 1,
    "nonexistent_venue": 1,
    "placeholder_authors": 1,
    "future_date": 1,
    "chimeric_title": 2,
    "wrong_venue": 2,
    "swapped_authors": 2,
    "preprint_as_published": 2,
    "hybrid_fabrication": 2,
    "merged_citation": 2,
    "partial_author_list": 2,
    "near_miss_title": 3,
    "plausible_fabrication": 3,
    "arxiv_version_mismatch": 3,
}

SPLIT_LABELS = {
    "dev_public": "Dev",
    "test_public": "Test",
    "dev_test": "Dev and test",
    "stress_test": "Stress",
}


def suspicion(status: str, confidence: float) -> float:
    """Rank label, with confidence as a tie-break that stays inside the bin.

    Verified is the low end. A more confident verified call scores lower.
    The other labels score higher when VerusCite is more confident in them.
    """
    rank = STATUS_RANK[status]
    conf = min(1.0, max(0.0, float(confidence)))
    frac = (1.0 - conf) if status == "verified" else conf
    return rank + 0.999 * frac


def load_joined(root: Path | None = None) -> pd.DataFrame:
    root = root or ROOT
    df = pd.read_csv(root / "results" / "veruscite.csv")
    df["vc_confidence"] = pd.to_numeric(df["vc_confidence"], errors="coerce").fillna(0.0)
    df["hallucination_type"] = df["hallucination_type"].fillna("")
    df["generation_method"] = df["generation_method"].fillna("")
    return df


def scored(df: pd.DataFrame) -> pd.DataFrame:
    """Rows with a real VerusCite label. Duplicates were not checked on their own."""
    return df[df["vc_status"].isin(STATUS_ORDER)].copy()


def subset(df: pd.DataFrame, split: str) -> pd.DataFrame:
    if split == "dev_test":
        return df[df["split"].isin(["dev_public", "test_public"])].copy()
    return df[df["split"] == split].copy()


def metrics_for(df: pd.DataFrame, split: str, rule: str) -> dict:
    sub = scored(subset(df, split))
    positive = sub["label"].eq("HALLUCINATED")
    flagged = sub["vc_status"].isin(RULES[rule])
    n_pos = int(positive.sum())
    n_neg = int((~positive).sum())
    tp = int((positive & flagged).sum())
    fp = int((~positive & flagged).sum())
    return {
        "split": split,
        "rule": rule,
        "n": int(len(sub)),
        "n_pos": n_pos,
        "n_neg": n_neg,
        "tp": tp,
        "fp": fp,
        "fn": n_pos - tp,
        "tn": n_neg - fp,
        "recall": tp / n_pos if n_pos else float("nan"),
        "fpr": fp / n_neg if n_neg else float("nan"),
        "precision": tp / (tp + fp) if (tp + fp) else float("nan"),
    }


def fold_frame(df: pd.DataFrame, mode: str) -> pd.DataFrame:
    """Apply Hallmark's two ways of setting aside the real-paper types.

    ``drop`` removes those types from the scored set. ``as_valid`` keeps them
    and treats them as valid, so flagging one is a false positive.
    """
    real = df["hallucination_type"].isin(REAL_PAPER_TYPES)
    out = df.copy()
    if mode == "drop":
        return out.loc[~real].copy()
    if mode == "as_valid":
        out.loc[real, "label"] = "VALID"
        return out
    raise ValueError(mode)


def auc_for(df: pd.DataFrame, split: str, *, fine: bool = True) -> float:
    sub = scored(subset(df, split))
    y = sub["label"].eq("HALLUCINATED").astype(int)
    if y.nunique() < 2:
        return float("nan")
    if fine:
        scores = [
            suspicion(status, conf)
            for status, conf in zip(sub["vc_status"], sub["vc_confidence"], strict=True)
        ]
    else:
        scores = [STATUS_RANK[status] for status in sub["vc_status"]]
    return float(roc_auc_score(y, scores))


def roc_for(df: pd.DataFrame, split: str = "dev_test") -> dict:
    sub = scored(subset(df, split))
    y = sub["label"].eq("HALLUCINATED").astype(int).to_numpy()
    scores = [
        suspicion(status, conf)
        for status, conf in zip(sub["vc_status"], sub["vc_confidence"], strict=True)
    ]
    fpr, tpr, _ = roc_curve(y, scores)
    points = {}
    for rule in RULES:
        m = metrics_for(df, split, rule)
        points[rule] = {"fpr": m["fpr"], "recall": m["recall"]}
    return {"fpr": fpr, "tpr": tpr, "auc": float(auc(fpr, tpr)), "points": points}


def crosstab_counts(df: pd.DataFrame, split: str) -> pd.DataFrame:
    sub = scored(subset(df, split))
    rows = []
    for label, name in (("VALID", "Valid"), ("HALLUCINATED", "Hallucinated")):
        part = sub[sub["label"] == label]
        rec = {"Hallmark": name, "n": int(len(part))}
        for status in STATUS_ORDER:
            rec[STATUS_LABELS[status]] = int((part["vc_status"] == status).sum())
        rows.append(rec)
    return pd.DataFrame(rows)


def type_table(df: pd.DataFrame, split: str = "dev_test") -> pd.DataFrame:
    sub = scored(subset(df, split))
    sub = sub[sub["label"].eq("HALLUCINATED")]
    rows = []
    for name in TYPE_ORDER:
        part = sub[sub["hallucination_type"] == name]
        n = int(len(part))
        rec = {"Type": TYPE_LABELS[name], "Tier": TYPE_TIER[name], "n": n}
        for status in STATUS_ORDER:
            rec[STATUS_LABELS[status]] = int((part["vc_status"] == status).sum()) if n else 0
        rec["Recall, hallucination"] = (
            rec["Hallucination"] / n if n else float("nan")
        )
        rec["Recall, hallucination or not found"] = (
            (rec["Hallucination"] + rec["Not found"]) / n if n else float("nan")
        )
        rows.append(rec)
    return pd.DataFrame(rows)


def duplicate_summary(labels: pd.DataFrame) -> dict:
    """What one combined upload would have done, from the saved batch keys."""
    groups = labels.groupby("dedup_key")
    mixed = 0
    for _, part in groups:
        if part["label"].nunique() > 1:
            mixed += 1
    return {
        "n": int(len(labels)),
        "groups": int(labels["dedup_key"].nunique()),
        "extras": int(len(labels) - labels["dedup_key"].nunique()),
        "mixed_groups": mixed,
        "batches": int(labels["batch"].nunique()),
    }


def load_labels(root: Path | None = None) -> pd.DataFrame:
    root = root or ROOT
    return pd.read_csv(root / "data" / "labels.csv")


def load_source(root: Path | None = None) -> dict:
    root = root or ROOT
    return json.loads((root / "data" / "SOURCE.json").read_text(encoding="utf-8"))


def load_jobs(root: Path | None = None) -> list[dict]:
    root = root or ROOT
    path = root / "results" / "documents.json"
    if not path.exists():
        return []
    payload = json.loads(path.read_text(encoding="utf-8"))
    return list(payload.get("jobs", []))


def shares(root: Path | None = None) -> list[dict]:
    jobs = load_jobs(root)
    return sorted(jobs, key=lambda job: job["batch"])
