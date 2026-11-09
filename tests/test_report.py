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
    future_year_span,
    load_joined,
    type_sample_tables,
    valid_miss_table,
)


def test_valid_misses_are_the_unverified_valid_entries():
    table = valid_miss_table(load_joined())
    assert len(table) == 45
    assert table["VerusCite"].value_counts().to_dict() == {
        "Minor error": 41,
        "Not found": 3,
        "Hallucination": 1,
    }
    assert table["Difference"].value_counts().to_dict() == {
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
    unresolved = table.loc[table["Difference"] == DOI_DIFF, "DOI"]
    assert unresolved.str.lower().str.endswith("v1").all()


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
