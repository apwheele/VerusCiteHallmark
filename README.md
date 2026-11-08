# VerusCite on Hallmark

VerusCite scored on the public splits of the Hallmark citation benchmark
(Kim, Brendel, and Reizinger, arXiv:2607.18360, data release 1.2.4).

The scored bibliography is the blinded dev, test, and stress splits, 2,072
entries. Hallmark's hidden split is not in the public files. The cross-domain
split and the ChatGPT supplement are not in this run.

VerusCite marks a later entry as a duplicate when the title and authors match
an earlier entry, and it does not check the duplicate on its own. Hallmark
includes the real paper and a copy with the venue, year, or DOI changed, so
one file would skip those copies. The upload is eleven files. Entries that
share a title and author list are in different files, and each file has at
most 300 entries. A 25-entry probe of this bibliography finished in 76
seconds, and the worker stops a document at 20 minutes, so the 1,661-entry
collision set would not finish as one file. `data/hallmark_public.bib` is the
combined file. The numbers in the paper come from the eleven uploads.

The paper is `paper.pdf` (also `paper.md`), from `paper.qmd` and
`references.bib`.

## Reproducing

The Hallmark files were read from a local clone at `G:\hallmark`, commit
`c62d296d1d2e3e6f9cb325e37963b63350ab2ca4`. The script checks duplicates with
the parser in a local CiteCheck checkout (`G:\CiteCheck` by default).

```bash
uv sync
uv run python -m ipykernel install --user --name hallmarkcite --display-name "Python (hallmarkcite)"

# rebuild data/hallmark_public.bib, data/batches/part_*.bib, and data/labels.csv
uv run python scripts/01_build_bib.py

# upload, poll, write results/veruscite.csv and the share links
# VC_API_KEY is read from .env (not committed)
uv run python scripts/02_submit.py

quarto render paper.qmd
```

`02_submit.py --combined` uploads the single BibTeX file. Copies that share a
title and author list come back as duplicates. The paper does not use that
run. A finished `results/documents.json` is reused on the next run, so
re-running the script polls instead of uploading again.

VerusCite bills one credit per 100 citations in a document, rounded up.
These eleven files are 2,072 citations and 24 credits. The key in `.env` is
`VC_API_KEY`.

## Layout

- `paper.qmd`, `references.bib` -- the note.
- `data/hallmark_public.bib` -- the blinded bibliography.
- `data/batches/` -- the eleven files that were uploaded.
- `data/labels.csv` -- Hallmark's labels, types, and the batch assignment.
- `data/SOURCE.json` -- the Hallmark commit the bibliography was built from.
- `scripts/01_build_bib.py`, `scripts/02_submit.py` -- rebuild and upload.
- `results/veruscite.csv` -- one row per entry, joined to the API result.
- `results/api/` -- the raw results payloads.
- `results/documents.json` -- document ids and share links.
- `src/hallmarkcite/report.py` -- the tables and the ROC score.
- `tests/` -- batch checks and the recall definitions.

## License

MIT, see `LICENSE`. Hallmark's data is theirs; the bibliography is rebuilt
from their public blinded splits.
