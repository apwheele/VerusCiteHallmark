# VerusCite on the Hallmark benchmark
Andrew P. Wheeler

# Introduction

Hallmark is a benchmark for tools that check whether a bibliographic entry is real ([Kim, Brendel, and Reizinger 2026](#ref-kim2026hallmark); [Reizinger, Kim, and Brendel 2026](#ref-hallmarkrepo)). The release I use is version 1.2.4, commit c62d296. The public files are dev, test, and stress, 2,072 BibTeX entries in total. I score them as one set. VerusCite was not trained on the dev file, so holding that file out does not change the check. The hidden test file is not in the public release. I left out the cross-domain file and the ChatGPT supplement, which Hallmark scores separately from the main table.

Hallmark labels each entry valid or hallucinated, and it gives each hallucinated entry one of 14 types. The types run from a DOI that does not resolve, through a real paper cited at the wrong venue, to a fully invented reference. VerusCite is the checker I run at [veruscite.com](https://veruscite.com) ([Wheeler 2026a](#ref-veruscite)). It looks the citation up and assigns one of four labels. Verified means a matching source was found and the metadata agrees. A minor error means the same work was found, with a small difference in the year, the author list, or the wording of the title or the venue. Not found means the search did not turn up a matching publication. Hallucination means the citation looks fabricated, or it mixes pieces of different real sources.

The two positive classes are different questions. Hallmark counts a real paper with the wrong venue, a preprint cited as the published version, a shortened author list, and an arXiv record with the venue and year mixed together as hallucinations. Those four types are 29.8% of the hallucinated entries, and Hallmark’s own paper shows that verifier rankings move when they are taken out of the positive class. VerusCite is built to call a real paper with a small metadata difference a minor error. I also expect some invented entries to come back as not found, because the search missed them, and that label is separate from hallucination. Recall of the hallucination label will be lower for both reasons.

# What was checked

I used Hallmark’s blinded entries. The blind files drop the url field, so a checker cannot treat a link as proof, and they do not contain the labels. I wrote one BibTeX file, `data/hallmark_public.bib`, with Hallmark’s key as the citation key. The labels, types, and batch assignments are in `data/labels.csv`. Nothing in the BibTeX tells the checker which entries are the positive class.

I did not send that file as one document. VerusCite marks a later entry as a duplicate when its title and authors match an earlier entry, and it copies the first verdict onto the duplicate. It does that so a bibliography that lists the same paper twice is only checked once. In this file, 411 of the 2,072 entries share a title and author list with another entry. They fall in 1,661 groups, and 290 of those groups contain both a valid entry and a hallucinated one. A changed venue, a future year, or a DOI that does not belong to the paper is often the same title and authors as the real record. One upload would have skipped the copy.

I split the file into 11 uploads. Entries that share a title and author list go in different files. A 25-entry file from this bibliography finished in 76 seconds, and the worker stops a document at 20 minutes. The largest collision-free set is 1,661 entries, so each file also has at most 300 entries. Each entry was checked once, through the API ([Wheeler 2026b](#ref-verusciteapi)). The reports are:

| Part | Entries | Report                                                                            |
|------|--------:|-----------------------------------------------------------------------------------|
| 1    |     300 | [report](https://veruscite.com/share/tHvO6qZrYrSZ42WTquiLMzHzUcpiOeAVraips9P8etw) |
| 2    |     300 | [report](https://veruscite.com/share/7r6g5IKIs7aUS8s8oSnFH6HuCvbH-usBsoP5aPmncEg) |
| 3    |     300 | [report](https://veruscite.com/share/l2Jj_j3Z3wSGCyi2wtuDl-HA_S0DLEJRLkYvjPNQzew) |
| 4    |     300 | [report](https://veruscite.com/share/AmhnS-Sy5zVsBYBBbT4s4Gc6mxHHwcAO6yWXxNu0hl4) |
| 5    |     300 | [report](https://veruscite.com/share/chgxR5WUOlysBCyCkizJkGukKS6zb4cMApQK4Hv6ghE) |
| 6    |     161 | [report](https://veruscite.com/share/5Dluo6vK-LJqeoOoEqqQ02GNTjOg-uETueJASn4Utj0) |
| 7    |     296 | [report](https://veruscite.com/share/lgZAhbaGleqLI0NQ70R5lnE7A-Sb2-yr48lZ13hWiks) |
| 8    |      91 | [report](https://veruscite.com/share/zzBAlPHCd6bpNLOpQt6FgJFG2RnSzkQiNDWYtNDT3iA) |
| 9    |      17 | [report](https://veruscite.com/share/RQqMjOfVNLaVQhdTBKW8SW8DOKq5U1CYnDDyrs3JJ1A) |
| 10   |       5 | [report](https://veruscite.com/share/ybeaKu2sx0iAjQaEXTxsX6-uNUqKQfZujlN-Q47tB2c) |
| 11   |       2 | [report](https://veruscite.com/share/TP7OTvFjVI-jnDFV9NJRHYCN7V0XIv8t81luR-E60K0) |

`scripts/02_submit.py` uploads those batches, polls until they finish, writes a public link for each, and joins the results to the labels. Passing `--combined` uploads the single file instead. That run marks the copies as duplicates, so I do not use it for the numbers below. VerusCite bills one credit per 100 citations in a document, rounded up. These uploads are 2,072 citations and 24 credits.

The scored set is the full public release: 1,260 hallucinated entries and 812 valid ones. Every entry in the joined file has one of the four labels. There are 0 duplicates in the saved results.

# Crosstab

<a href="#tbl-cross" class="quarto-xref">Table 2</a> is VerusCite’s label against Hallmark’s, for every public entry.

| Hallmark     |     n | Verified | Minor error | Not found | Hallucination |
|:-------------|------:|---------:|------------:|----------:|--------------:|
| Valid        |   812 |      767 |          41 |         3 |             1 |
| Hallucinated | 1,260 |      202 |         327 |        98 |           633 |

767 of the 812 valid entries are verified. The false calls on valid entries are 41 minor errors, 3 not found, and 1 called a hallucination.

Of the hallucinated entries, 633 are hallucinations, 98 are not found, 327 are minor errors, and 202 are verified. The verified hallucinated entries are the ones VerusCite accepted. The minor errors are mostly the real papers Hallmark still calls hallucinations. The not found row is the miss the hallucination label does not get credit for.

<a href="#fig-types" class="quarto-xref">Figure 1</a> and <a href="#tbl-types" class="quarto-xref">Table 3</a> break the hallucinated class out by type. The types are in Hallmark’s order, tier 1 then tier 2 then tier 3.

![](paper_files/figure-commonmark/fig-types-output-1.png)

| Type                   | Tier |   n | Verified | Minor error | Not found | Hallucination |
|:-----------------------|-----:|----:|---------:|------------:|----------:|--------------:|
| fabricated doi         |    1 |  67 |        0 |          65 |         0 |             2 |
| nonexistent venue      |    1 |  76 |       21 |          20 |         0 |            35 |
| placeholder authors    |    1 |  74 |        0 |           0 |         0 |            74 |
| future date            |    1 |  59 |       17 |          42 |         0 |             0 |
| chimeric title         |    2 |  70 |        0 |          15 |         2 |            53 |
| wrong venue            |    2 |  83 |       22 |          24 |         0 |            37 |
| swapped authors        |    2 | 133 |        7 |          10 |         0 |           116 |
| preprint as published  |    2 |  61 |       24 |           8 |         0 |            29 |
| hybrid fabrication     |    2 |  62 |        0 |           7 |         1 |            54 |
| merged citation        |    2 | 105 |        0 |           0 |         1 |           104 |
| partial author list    |    2 | 102 |       40 |          61 |         0 |             1 |
| near miss title        |    3 |  92 |       26 |          48 |         3 |            15 |
| plausible fabrication  |    3 | 146 |        0 |           2 |        91 |            53 |
| arxiv version mismatch |    3 | 130 |       45 |          25 |         0 |            60 |

Plausible fabrications and fabricated DOIs are the clean invented entries. Of 146 plausible fabrications, 36.3% are hallucinations and 62.3% are not found. Of 67 fabricated DOIs, 3.0% are hallucinations and 0.0% are not found.

Wrong venue, a future year, and a partial author list keep a real paper and change one field. Of the wrong-venue entries, 28.9% are minor errors and 44.6% are hallucinations. Of the future-date entries, 71.2% are minor errors. Of the partial author lists, 59.8% are minor errors. Calling only the hallucination label a detection misses that block on purpose.

Near-miss titles sit in between. 52.2% are minor errors and 16.3% are hallucinations. A one or two word change in the title is the case VerusCite’s minor-error rule is written for, and it is also a Hallmark hallucination.

# Recall and false positives

I score three rules. The strict rule counts only VerusCite’s hallucination label as a detection. The second counts hallucination or not found, which is the strict rule plus the lookups that did not return a paper. The third counts anything other than verified, so a minor error is also a detection. Recall is the share of Hallmark’s hallucinated entries that the rule flags. The false positive rate is the share of valid entries that it flags. <a href="#tbl-rates" class="quarto-xref">Table 4</a> has both, with the counts.

| Rule                       | Caught        | Recall | False positives | FPR  |
|:---------------------------|:--------------|:-------|:----------------|:-----|
| Hallucination only         | 633 / 1,260   | 50.2%  | 1 / 812         | 0.1% |
| Hallucination or not found | 731 / 1,260   | 58.0%  | 4 / 812         | 0.5% |
| Anything but verified      | 1,058 / 1,260 | 84.0%  | 45 / 812        | 5.5% |

The hallucination label catches 633 of 1,260 hallucinated entries, recall 50.2%, and it flags 1 of 812 valid entries, a false positive rate of 0.1%.

Counting not found with hallucination raises recall to 58.0% (731 of 1,260) and raises the false positive rate to 0.5% (4 of 812). The extra true positives are the 98 hallucinated entries labeled not found. The extra false positives are the 3 valid entries with the same label. Not found is doing both jobs: it holds missed hallucinations, and it holds real papers the search did not return.

Counting minor errors as well raises recall to 84.0% and the false positive rate to 5.5%. That rule flags every entry VerusCite did not fully accept. Most of the recall it adds, relative to the not-found rule, is the real-paper types.

Hallmark’s published table is on the dev file alone: a DOI lookup at detection rate 0.218 and false positive rate 0.043, Gemini 2.5 Pro at 0.476 and 0.050, and bibtex-updater, which they treat as a co-designed upper bound, at 0.820 and 0.051 when abstentions are scored as valid ([Kim, Brendel, and Reizinger 2026](#ref-kim2026hallmark)). The rates above are the full public set. Their detection rate also credits a wrong venue, which VerusCite’s hallucination label does not.

<a href="#tbl-fold" class="quarto-xref">Table 5</a> recomputes the rates the two ways Hallmark uses when those four real-paper types stop counting as hallucinations. Dropping them removes the entries from the scored set. Scoring them as valid means a flag on one of them is a false positive.

| Real-paper types            | Rule                       | Recall | FPR   | Hallucinated n | Valid n |
|:----------------------------|:---------------------------|:-------|:------|---------------:|--------:|
| Dropped from the scored set | Hallucination only         | 57.2%  | 0.1%  |            884 |     812 |
| Dropped from the scored set | Hallucination or not found | 68.3%  | 0.5%  |            884 |     812 |
| Dropped from the scored set | Anything but verified      | 92.0%  | 5.5%  |            884 |     812 |
| Scored as valid             | Hallucination only         | 57.2%  | 10.8% |            884 |   1,188 |
| Scored as valid             | Hallucination or not found | 68.3%  | 11.0% |            884 |   1,188 |
| Scored as valid             | Anything but verified      | 92.0%  | 24.4% |            884 |   1,188 |

Under the strict rule, dropping those types moves recall from 50.2% to 57.2%. The false positive rate stays 0.1%, because the dropped entries were hallucinated, so the valid count does not change. Treating them as valid moves the false positive rate to 10.8%. Flagging a wrong venue is then a false alarm, which is what the hallucination label mostly avoids by putting those entries in minor error.

# A score and the ROC curve

The four labels are already an order: verified, minor error, not found, hallucination. VerusCite also stores a confidence between 0 and 1. That number is how sure it is of the label it chose. It is not the probability that Hallmark would call the entry hallucinated, so I do not treat it as a calibrated probability of the benchmark label.

I still want one score, so that a threshold can move from the strict rule to the broader ones. The label sets the band. Inside the band, higher confidence moves a verified entry down, toward the safe end, and moves the other three labels up. A threshold at the hallucination band is the strict rule. A threshold at the not-found band adds not found. A threshold at the minor-error band adds minor errors. <a href="#fig-roc" class="quarto-xref">Figure 2</a> is the ROC curve for that score on the full public set. The three marked points are the three rules, computed from the labels directly, so they do not depend on the tie-break.

![](paper_files/figure-commonmark/fig-roc-output-1.png)

The area under the curve is 0.937. Using the four labels alone, with confidence ignored, the area is 0.907.

The area is higher than the strict rule’s recall because the score gets credit for ranking a minor error above a verified entry, and a not found above a minor error, even when the hallucination label is off. That is the useful reading of the curve. The operating point a venue would actually ship is one of the three points, and the left-hand one is the hallucination label, with recall 50.2% and false positive rate 0.1%. Moving right buys the not-found and minor-error entries back, and it pays for them in false positives.

# Limits

This is a check of bibliographic metadata, which is also what Hallmark measures. I did not ask whether a manuscript’s claim is supported by the cited paper. The public entries are mostly papers from major machine-learning venues. A bibliography of books, reports, or legal citations would land in different places, and not found would be more common for work that is real and absent from the indexes VerusCite searches.

The duplicate rule is a property of the product, not of the benchmark. A user who uploads one file in which the same title and authors appear twice will get one check. I split the file so the numbers above are one check per entry. The links in <a href="#tbl-links" class="quarto-xref">Table 1</a> are that run.

Hallmark has not settled whether a real paper with the wrong venue is a hallucination. <a href="#tbl-fold" class="quarto-xref">Table 5</a> is there so the rates can be read either way. I would use the hallucination label when the question is whether the reference was invented, and I would read minor errors as a separate list of metadata to fix.

# AI use disclosure

The code, the API run, and the text were produced with Grok (xAI, Grok 4.7) under my direction. I specified the benchmark, the use of the VerusCite API, the crosstab of VerusCite’s labels with Hallmark’s, the recall and false positive rate, and the AUC. The split into collision-free batches was required by VerusCite’s duplicate rule, which would otherwise have skipped entries that share a title and author list. All numbers and figures are computed from the scripts and the saved API results in the repository.

# References

<div id="refs" class="references csl-bib-body hanging-indent" entry-spacing="0">

<div id="ref-kim2026hallmark" class="csl-entry">

Kim, Kayoon, Wieland Brendel, and Patrik Reizinger. 2026. “HALLMARK: How to Diagnose LLM Citation Verifiers and When to Deploy Them.” <https://arxiv.org/abs/2607.18360>.

</div>

<div id="ref-hallmarkrepo" class="csl-entry">

Reizinger, Patrik, Kayoon Kim, and Wieland Brendel. 2026. “HALLMARK: Citation Hallucination Detection Benchmark.” <https://github.com/rpatrik96/hallmark>.

</div>

<div id="ref-veruscite" class="csl-entry">

Wheeler, Andrew P. 2026a. “VerusCite.” <https://veruscite.com>.

</div>

<div id="ref-verusciteapi" class="csl-entry">

———. 2026b. “VerusCite API.” <https://veruscite.com/docs/api/>.

</div>

</div>
