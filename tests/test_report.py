from hallmarkcite.report import (
    AUTHOR_LIST_DIFF,
    AUTHOR_ORDER_DIFF,
    CANARY_DIFF,
    DOI_DIFF,
    GIVEN_NAME_DIFF,
    NO_RECORD_DIFF,
    OTHER_PAPER_DIFF,
    SAMPLE_N,
    TITLE_DIFF,
    TYPE_ORDER,
    YEAR_DIFF,
    _one_line,
    future_year_span,
    has_version_suffix_doi,
    load_joined,
    sample_display,
    suspicion,
    type_sample_tables,
    valid_miss_plain_diff_count,
    valid_miss_records,
    valid_miss_table,
    valid_miss_version_doi_count,
    valid_miss_version_suffixes,
)


def _close(left, right):
    assert abs(left - right) < 1e-12


def test_one_line_escapes_pandoc_citations():
    text = _one_line("The raw BibTeX uses @inproceedings, and `@article`.")
    assert text == "The raw BibTeX uses \\@inproceedings, and `\\@article`."


def test_suspicion_uses_confidence_inside_the_label():
    # Verified adds 0.999 * (1 - confidence). The other labels add 0.999 * confidence.
    _close(suspicion("verified", 0.90), 0.999 * 0.10)
    _close(suspicion("verified", 0.20), 0.999 * 0.80)
    _close(suspicion("minor_error", 0.80), 1 + 0.999 * 0.80)
    _close(suspicion("minor_error", 0.40), 1 + 0.999 * 0.40)
    _close(suspicion("not_found", 0.60), 2 + 0.999 * 0.60)
    _close(suspicion("hallucination", 0.70), 3 + 0.999 * 0.70)
    assert suspicion("verified", 1) == 0
    assert suspicion("hallucination", 1) < 4


def test_valid_misses_are_the_unverified_valid_entries():
    records = valid_miss_records(load_joined())
    table = valid_miss_table(load_joined())
    assert len(records) == 45
    assert len(table) == 45
    assert list(table.columns) == ["VerusCite", "Citation", "DOI", "Trace"]
    assert table["VerusCite"].value_counts().to_dict() == {
        "Minor error": 41,
        "Not found": 3,
        "Hallucination": 1,
    }
    assert records["Difference"].value_counts().to_dict() == {
        DOI_DIFF: 33,
        AUTHOR_ORDER_DIFF: 3,
        AUTHOR_LIST_DIFF: 2,
        NO_RECORD_DIFF: 2,
        TITLE_DIFF: 1,
        YEAR_DIFF: 1,
        GIVEN_NAME_DIFF: 1,
        CANARY_DIFF: 1,
        OTHER_PAPER_DIFF: 1,
    }
    unresolved = records.loc[records["Difference"] == DOI_DIFF, "vc_doi"]
    assert unresolved.str.lower().str.endswith("v1").all()
    assert table["Trace"].tolist() == records["vc_notes"].map(_one_line).tolist()
    assert int(table["Trace"].str.len().max()) > 180
    titles = records["vc_title"].map(_one_line)
    for title, citation in zip(titles, table["Citation"], strict=True):
        assert title in citation
        assert citation.index(". ") > 0
    has_doi = records["vc_doi"].fillna("").astype(str).str.strip().ne("")
    assert table.loc[has_doi.to_numpy(), "DOI"].str.contains("https://doi.org/", regex=False).all()
    gowal = table.loc[records["bibtex_key"].eq("ed071a6dfa34").to_numpy()].iloc[0]
    assert "NeurIPS" in gowal["Citation"]
    assert "Gowal" in gowal["Citation"]
    assert "https://doi.org/10.48550/arXiv.2104.09425" in gowal["DOI"]
    assert "[article](https://arxiv.org/abs/2104.09425)" in gowal["DOI"]
    canary = table.loc[records["bibtex_key"].eq("__canary__stress_test").to_numpy()].iloc[0]
    assert "Benchmark Authors" in canary["Citation"]
    assert "stress\\_test" in canary["Citation"]
    assert "not a finding of fabrication" in canary["Trace"]


def test_thirty_five_valid_misses_have_a_version_suffix_doi():
    records = valid_miss_records(load_joined())
    versioned = records["vc_doi"].map(has_version_suffix_doi)
    assert valid_miss_version_doi_count(load_joined()) == 35
    assert int(versioned.sum()) == 35
    assert set(records.loc[versioned, "vc_status"]) == {"minor_error"}
    assert valid_miss_version_suffixes(load_joined()) == ["v1"]
    assert int((records.loc[versioned, "Difference"] == DOI_DIFF).sum()) == 33
    other = records.loc[versioned & records["Difference"].ne(DOI_DIFF), "Difference"]
    assert sorted(other.tolist()) == sorted([TITLE_DIFF, AUTHOR_LIST_DIFF])
    assert len(records) - int(versioned.sum()) == 10
    assert valid_miss_plain_diff_count(load_joined(), AUTHOR_ORDER_DIFF) == 3
    assert valid_miss_plain_diff_count(load_joined(), YEAR_DIFF) == 1
    assert valid_miss_plain_diff_count(load_joined(), GIVEN_NAME_DIFF) == 1
    assert valid_miss_plain_diff_count(load_joined(), AUTHOR_LIST_DIFF) == 1


def test_future_dates_span_2030_to_2036():
    assert future_year_span(load_joined()) == (2030, 2036)


def test_type_samples_take_at_most_five_and_repeat():
    first = type_sample_tables(load_joined())
    second = type_sample_tables(load_joined())
    assert [table["type"] for table in first] == list(TYPE_ORDER)
    empty = [
        table["type"]
        for table in first
        if table["n_verified"] == 0 and table["n_minor"] == 0
    ]
    assert empty == ["placeholder_authors", "merged_citation"]
    for table, again in zip(first, second, strict=True):
        rows = table["rows"]
        assert list(rows["bibtex_key"]) == list(again["rows"]["bibtex_key"])
        for status, total in (
            ("verified", table["n_verified"]),
            ("minor_error", table["n_minor"]),
        ):
            shown = int(rows["vc_status"].eq(status).sum()) if len(rows) else 0
            assert shown == min(total, SAMPLE_N)


def test_sample_display_keeps_the_full_note_and_the_citation():
    tables = type_sample_tables(load_joined())
    shown = next(table["rows"] for table in tables if len(table["rows"]))
    display = sample_display(shown)
    assert list(display.columns) == ["VerusCite", "Citation", "DOI", "Trace"]
    assert display["Trace"].tolist() == shown["vc_notes"].map(_one_line).tolist()
    assert display["DOI"].str.contains("https://doi.org/", regex=False).any()
    titles = shown["vc_title"].map(_one_line)
    for title, citation in zip(titles, display["Citation"], strict=True):
        assert title in citation
        assert len(citation) > len(title)
