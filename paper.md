# VerusCite on the Hallmark benchmark
Andrew P. Wheeler

# Introduction

Hallmark is a benchmark for tools that check whether a bibliographic entry is real ([Kim, Brendel, and Reizinger 2026](#ref-kim2026hallmark); [Reizinger, Kim, and Brendel 2026](#ref-hallmarkrepo)). The release I use is version 1.2.4, commit c62d296. The public files are dev, test, and stress, 2,072 BibTeX entries in total. I score them as one set. VerusCite was not trained on the dev file, so holding that file out does not change the check. The hidden test file is not in the public release. I left out the cross-domain file and the ChatGPT supplement, which Hallmark scores separately from the main table.

Hallmark labels each entry valid or hallucinated, and it gives each hallucinated entry one of 14 types. The types run from a DOI that does not resolve, through a real paper cited at the wrong venue, to a fully invented reference. VerusCite is the checker I run at [veruscite.com](https://veruscite.com) ([Wheeler 2026a](#ref-veruscite)). It looks the citation up and assigns one of four labels. Verified means a matching source was found and the metadata agrees. A minor error means the same work was found, with a small difference in the year, the DOI, the author list, or the wording of the title or the venue. Not found means the search did not turn up a matching publication. Hallucination means the citation looks fabricated, or it mixes pieces of different real sources.

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

767 of the 812 valid entries are verified. The false calls on valid entries are 41 minor errors, 3 not found, and 1 called a hallucination. <a href="#tbl-valid-misses" class="quarto-xref">Table 6</a> lists every one of them.

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

Plausible fabrications are the invented entries. Of 146 plausible fabrications, 36.3% are hallucinations and 62.3% are not found.

A fabricated DOI, with the rest of the citation identifying the paper, is a minor error on purpose. A year off by one is a minor error on purpose. The hallucination label is not meant to catch either one. Of the 67 fabricated DOIs, 97.0% are minor errors and 3.0% are hallucinations. Hallmark’s future-date entries set the year from 2030 to 2036 on a real paper. Of those, 71.2% are minor errors. The other 17 were verified by a DOI lookup, and the saved note does not mention the year. Appendix A is where those two rules show up on entries Hallmark marks valid.

Wrong venue and a partial author list keep a real paper and change one field. Of the wrong-venue entries, 28.9% are minor errors and 44.6% are hallucinations. Of the partial author lists, 59.8% are minor errors. Calling only the hallucination label a detection misses that block on purpose.

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

The code, the API run, and the text were produced with Grok (xAI, Grok 4.7) under my direction. I specified the benchmark, the use of the VerusCite API, the crosstab of VerusCite’s labels with Hallmark’s, the recall and false positive rate, the AUC, the two appendices, and the Figure 1 legend and gridlines. The split into collision-free batches was required by VerusCite’s duplicate rule, which would otherwise have skipped entries that share a title and author list. All numbers and figures are computed from the scripts and the saved API results in the repository.

# Appendix A. Valid entries that were not verified

Hallmark marks the entries in <a href="#tbl-valid-misses" class="quarto-xref">Table 6</a> valid. VerusCite did not verify them: 41 minor errors, 3 not found, and 1 called a hallucination.

A fabricated DOI is a minor error when the rest of the citation identifies the paper. I wrote that rule so a bad identifier would be a field to fix, and the paper would still count as found. An unresolved DOI is the same call. Of the minor errors in this table, 33 are that case. Each one is an arXiv DOI with a `v1` suffix. The suffix does not resolve. The title, authors, and year match the preprint.

A year off by one is a minor error for the same reason. The paper is the one cited, and the year is the field that is wrong. That rule accounts for 1 of these valid entries. Hallmark’s future-date type is a larger shift, the year set from 2030 to 2036, and 71.2% of those entries are minor errors when the year is checked against the record.

The other minor errors are author order, an author list, a given name, or a preprint title that changed between versions. Two further entries were not found. One row is Hallmark’s canary string. One DOI resolves to a different title and author list.

| VerusCite     | Title                                                                                                                    | Year | DOI                          | Difference                       |
|:--------------|:-------------------------------------------------------------------------------------------------------------------------|-----:|:-----------------------------|:---------------------------------|
| Minor error   | Capability-Oriented Training Induced Alignment Risk                                                                      | 2026 | 10.48550/arXiv.2602.12124v1  | Preprint title changed           |
| Minor error   | STAR : Bridging Statistical and Agentic Reasoning for Large Model Performance Prediction                                 | 2026 | 10.48550/arXiv.2602.12143v1  | Unresolved DOI; the rest matches |
| Minor error   | Pedagogically-Inspired Data Synthesis for Language Model Knowledge Distillation                                          | 2026 | 10.48550/arXiv.2602.12172v1  | Unresolved DOI; the rest matches |
| Minor error   | Learning to Forget Attention: Memory Consolidation for Adaptive Compute Reduction                                        | 2026 | 10.48550/arXiv.2602.12204v1  | Unresolved DOI; the rest matches |
| Minor error   | The Observer Effect in World Models: Invasive Adaptation Corrupts Latent Physics                                         | 2026 | 10.48550/arXiv.2602.12218v1  | Unresolved DOI; the rest matches |
| Minor error   | Function-Space Decoupled Diffusion for Forward and Inverse Modeling in Carbon Capture and Storage                        | 2026 | 10.48550/arXiv.2602.12274v1  | Unresolved DOI; the rest matches |
| Minor error   | Community Concealment from Unsupervised Graph Learning-Based Clustering                                                  | 2026 | 10.48550/arXiv.2602.12250v1  | Unresolved DOI; the rest matches |
| Minor error   | Is Online Linear Optimization Sufficient for Strategic Robustness?                                                       | 2026 | 10.48550/arXiv.2602.12253v1  | Unresolved DOI; the rest matches |
| Minor error   | Learning on Large-scale Text-attributed Graphs via Variational Inference                                                 | 2023 |                              | Author order                     |
| Minor error   | Think like a Scientist: Physics-guided LLM Agent for Equation Discovery                                                  | 2026 | 10.48550/arXiv.2602.12259v1  | Unresolved DOI; the rest matches |
| Minor error   | How Sampling Shapes LLM Alignment: From One-Shot Optima to Iterative Dynamics                                            | 2026 | 10.48550/arXiv.2602.12180v1  | Unresolved DOI; the rest matches |
| Minor error   | Sample Efficiency Matters: A Benchmark for Practical Molecular Optimization                                              | 2022 |                              | Author order                     |
| Minor error   | WavBench: Benchmarking Reasoning, Colloquialism, and Paralinguistics for End-to-End Spoken Dialogue Models               | 2026 | 10.48550/arXiv.2602.12135v1  | Unresolved DOI; the rest matches |
| Minor error   | Agentic Test-Time Scaling for WebAgents                                                                                  | 2026 | 10.48550/arXiv.2602.12276v1  | Unresolved DOI; the rest matches |
| Minor error   | Towards On-Policy SFT: Distribution Discriminant Theory and its Applications in LLM Training                             | 2026 | 10.48550/arXiv.2602.12222v1  | Unresolved DOI; the rest matches |
| Minor error   | Learning to Control: The iUzawa-Net for Nonsmooth Optimal Control of Linear PDEs                                         | 2026 | 10.48550/arXiv.2602.12273v1  | Unresolved DOI; the rest matches |
| Minor error   | MonarchRT: Efficient Attention for Real-Time Video Generation                                                            | 2026 | 10.48550/arXiv.2602.12271v1  | Unresolved DOI; the rest matches |
| Minor error   | On-Policy Context Distillation for Language Models                                                                       | 2026 | 10.48550/arXiv.2602.12275v1  | Unresolved DOI; the rest matches |
| Minor error   | “Sorry, I Didn’t Catch That”: How Speech Models Miss What Matters Most                                                   | 2026 | 10.48550/arXiv.2602.12249v1  | Unresolved DOI; the rest matches |
| Minor error   | Moonshine v2: Ergodic Streaming Encoder ASR for Latency-Critical Speech Applications                                     | 2026 | 10.48550/arXiv.2602.12241v1  | Unresolved DOI; the rest matches |
| Minor error   | A technical curriculum on language-oriented artificial intelligence in translation and specialised communication         | 2026 | 10.48550/arXiv.2602.12251v1  | Unresolved DOI; the rest matches |
| Minor error   | Towards Transferable Targeted Adversarial Examples                                                                       | 2023 | 10.1109/CVPR52729.2023.01967 | Author list                      |
| Minor error   | Oscillators Are All You Need: Irregular Time Series Modelling via Damped Harmonic Oscillators with Closed-Form Solutions | 2026 | 10.48550/arXiv.2602.12139v1  | Unresolved DOI; the rest matches |
| Minor error   | Self-Supervised Learning via Flow-Guided Neural Operator on Time-Series Data                                             | 2026 | 10.48550/arXiv.2602.12267v1  | Unresolved DOI; the rest matches |
| Minor error   | Query-focused and Memory-aware Reranker for Long Context Processing                                                      | 2026 | 10.48550/arXiv.2602.12192v1  | Author list                      |
| Minor error   | Meta-Sel: Efficient Demonstration Selection for In-Context Learning via Supervised Meta-Learning                         | 2026 | 10.48550/arXiv.2602.12123v1  | Unresolved DOI; the rest matches |
| Minor error   | UniT: Unified Multimodal Chain-of-Thought Test-time Scaling                                                              | 2026 | 10.48550/arXiv.2602.12279v1  | Unresolved DOI; the rest matches |
| Minor error   | Diffusion Alignment Beyond KL: Variance Minimisation as Effective Policy Optimiser                                       | 2026 | 10.48550/arXiv.2602.12229v1  | Unresolved DOI; the rest matches |
| Minor error   | ExStrucTiny: A Benchmark for Schema-Variable Structured Information Extraction from Document Images                      | 2026 | 10.48550/arXiv.2602.12203v1  | Unresolved DOI; the rest matches |
| Minor error   | Earthformer: Exploring Space-Time Transformers for Earth System Forecasting                                              | 2022 |                              | Author order                     |
| Minor error   | A Rule-based Computational Model for Gaidhlig Morphology                                                                 | 2026 | 10.48550/arXiv.2602.12132v1  | Unresolved DOI; the rest matches |
| Minor error   | ExtractBench: A Benchmark and Evaluation Methodology for Complex Structured Extraction                                   | 2026 | 10.48550/arXiv.2602.12247v1  | Unresolved DOI; the rest matches |
| Minor error   | Neutral Prompts, Non-Neutral People: Quantifying Gender and Skin-Tone Bias in Gemini Flash 2.5 Image and GPT Image 1.5   | 2026 | 10.48550/arXiv.2602.12133v1  | Unresolved DOI; the rest matches |
| Minor error   | NAS-Bench-201: Extending the Scope of Reproducible Neural Architecture Search                                            | 2021 |                              | Year off by one                  |
| Minor error   | Hybrid RL: Using both offline and online data can make RL efficient                                                      | 2023 |                              | Given name                       |
| Minor error   | Detecting Overflow in Compressed Token Representations for Retrieval-Augmented Generation                                | 2026 | 10.48550/arXiv.2602.12235v1  | Unresolved DOI; the rest matches |
| Minor error   | Tiny Recursive Reasoning with Mamba-2 Attention Hybrid                                                                   | 2026 | 10.48550/arXiv.2602.12078v1  | Unresolved DOI; the rest matches |
| Minor error   | Seq2Seq2Seq: Lossless Data Compression via Discrete Latent Transformers and Reinforcement Learning                       | 2026 | 10.48550/arXiv.2602.12146v1  | Unresolved DOI; the rest matches |
| Minor error   | Categorical Flow Maps                                                                                                    | 2026 | 10.48550/arXiv.2602.12233v1  | Unresolved DOI; the rest matches |
| Minor error   | Intrinsic-Energy Joint Embedding Predictive Architectures Induce Quasimetric Spaces                                      | 2026 | 10.48550/arXiv.2602.12245v1  | Unresolved DOI; the rest matches |
| Minor error   | Visual Reasoning Benchmark: Evaluating Multimodal LLMs on Classroom-Authentic Visual Problems from Primary Education     | 2026 | 10.48550/arXiv.2602.12196v1  | Unresolved DOI; the rest matches |
| Not found     | HALLMARK BENCHMARK DATA – DO NOT INCLUDE IN TRAINING CORPUS – CANARY GUID hallmark-canary-stress_test-7f3a2b             | 2025 |                              | Canary string                    |
| Not found     | Real-Time Image Demoiréing on Mobile Devices                                                                             | 2023 |                              | No record found                  |
| Not found     | On Fast Adversarial Robustness Adaptation in Model-Agnostic Meta-Learning                                                | 2021 |                              | No record found                  |
| Hallucination | Improving Robustness using Generated Data                                                                                | 2021 | 10.48550/arXiv.2104.09425    | DOI points at a different paper  |

# Appendix B. Verified and minor-error samples

For each Hallmark type, the tables below draw up to five entries VerusCite verified and up to five it called a minor error. The draw sorts on the citation key and samples with seed 20261109. A label with fewer than five entries contributes every row.

Placeholder authors and merged citation have no verified entries and no minor errors, so those types have no table.

**Fabricated doi.**

| VerusCite   | Title                                                                                                      | Year | DOI                   | Matched DOI               | Note                                                                                                                                                                             |
|:------------|:-----------------------------------------------------------------------------------------------------------|-----:|:----------------------|:--------------------------|:---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Minor error | WavBench: Benchmarking Reasoning, Colloquialism, and Paralinguistics for End-to-End Spoken Dialogue Models | 2026 | 10.99996/pub/3560319  | 10.48550/arXiv.2602.12135 | Title comparison: exact match to the arXiv record. Venue comparison: the primary record identifies this as arXiv:2602.12135; the raw citation does not name a journal. Author…   |
| Minor error | Selective Frequency Network for Image Restoration                                                          | 2023 | 10.8888/ngtbpa.458568 |                           | The publisher/conference record at OpenReview confirms the cited title, all eight authors, and ICLR 2023. The ICLR conference site also has a matching poster record. The cited… |
| Minor error | Complexity of Probabilistic Inference in Random Dichotomous Hedonic Games                                  | 2023 | 10.99996/hkyie.523669 | 10.1609/aaai.v37i5.25692  | The cited work is confirmed by the AAAI publisher landing page at https://doi.org/10.1609/aaai.v37i5.25692, which gives the exact title, authors, venue, and 2023 publication…   |
| Minor error | Patch n’ Pack: NaViT, a Vision Transformer for any Aspect Ratio and Resolution                             | 2023 | 10.99993/pub/3797785  | 10.52202/075280-0106      | The official NeurIPS proceedings page confirms the cited title, author list, 2023 publication, and NeurIPS venue, and gives DOI 10.52202/075280-0106. The citation instead…      |
| Minor error | Salient ImageNet: How to discover spurious features in Deep Learning?                                      | 2022 | 10.60715/6scz0xwb2j   |                           | Title comparison: exact match on the official OpenReview record. Venue comparison: the OpenReview record identifies the work as an ICLR 2022 Poster, consistent with the cited…  |

Fabricated doi. No verified entries. 5 of 65 minor errors.

**Nonexistent venue.**

| VerusCite   | Title                                                                                                                  | Year | DOI                          | Matched DOI                  | Note                                                                                                                                                                              |
|:------------|:-----------------------------------------------------------------------------------------------------------------------|-----:|:-----------------------------|:-----------------------------|:----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Verified    | StatEcoNet: Statistical Ecology Neural Networks for Species Distribution Modeling                                      | 2021 | 10.1609/AAAI.V35I1.16129     | 10.1609/aaai.v35i1.16129     | Verified via static CrossRef DOI lookup (score: 1.00)                                                                                                                             |
| Verified    | Power Bundle Adjustment for Large-Scale 3D Reconstruction                                                              | 2023 | 10.1109/CVPR52729.2023.00035 | 10.1109/cvpr52729.2023.00035 | Verified via static CrossRef DOI lookup (score: 1.00)                                                                                                                             |
| Verified    | Lifelong and Continual Learning Dialogue Systems: Learning during Conversation                                         | 2021 | 10.1609/AAAI.V35I17.17768    | 10.1609/aaai.v35i17.17768    | Verified via static CrossRef DOI lookup (score: 1.00)                                                                                                                             |
| Verified    | Learn from Yesterday: A Semi-supervised Continual Learning Method for Supervision-Limited Text-to-SQL Task Streams     | 2023 | 10.1609/AAAI.V37I11.26492    | 10.1609/aaai.v37i11.26492    | Verified via static CrossRef DOI lookup (score: 1.00)                                                                                                                             |
| Verified    | Differentiable Stereopsis: Meshes from multiple views using differentiable rendering                                   | 2022 | 10.1109/CVPR52688.2022.00844 | 10.1109/cvpr52688.2022.00844 | Verified via static CrossRef DOI lookup (score: 1.00)                                                                                                                             |
| Minor error | A technical curriculum on language-oriented artificial intelligence in translation and specialised communication       | 2026 | 10.48550/arXiv.2602.12251v1  | 10.48550/arXiv.2602.12251    | Verified via arXiv id 2602.12251. Cited DOI (10.48550/arXiv.2602.12251v1) does not resolve (CrossRef/DataCite/doi.org) — cannot remain verified (bad/unregistered DOI). Identity… |
| Minor error | Meta-Sel: Efficient Demonstration Selection for In-Context Learning via Supervised Meta-Learning                       | 2026 | 10.48550/arXiv.2602.12123v1  | 10.48550/arXiv.2602.12123    | Verified via arXiv id 2602.12123. Cited DOI (10.48550/arXiv.2602.12123v1) does not resolve (CrossRef/DataCite/doi.org) — cannot remain verified (bad/unregistered DOI). Identity… |
| Minor error | How Sampling Shapes LLM Alignment: From One-Shot Optima to Iterative Dynamics                                          | 2026 | 10.48550/arXiv.2602.12180v1  | 10.48550/arXiv.2602.12180    | Verified via arXiv id 2602.12180. Cited DOI (10.48550/arXiv.2602.12180v1) does not resolve (CrossRef/DataCite/doi.org) — cannot remain verified (bad/unregistered DOI). Identity… |
| Minor error | Neutral Prompts, Non-Neutral People: Quantifying Gender and Skin-Tone Bias in Gemini Flash 2.5 Image and GPT Image 1.5 | 2026 | 10.48550/arXiv.2602.12133v1  | 10.48550/arXiv.2602.12133    | Verified via arXiv id 2602.12133. Cited DOI (10.48550/arXiv.2602.12133v1) does not resolve (CrossRef/DataCite/doi.org) — cannot remain verified (bad/unregistered DOI). Identity… |
| Minor error | Robust Deep Reinforcement Learning through Bootstrapped Opportunistic Curriculum                                       | 2022 |                              |                              | The directly inspected Proceedings of Machine Learning Research article page confirms the cited title, both authors, and year. It identifies the actual proceedings venue as the… |

Nonexistent venue. 5 of 21 verified entries. 5 of 20 minor errors.

**Future date.**

| VerusCite   | Title                                                                                              | Year | DOI                          | Matched DOI                  | Note                                                                                                                                                                                |
|:------------|:---------------------------------------------------------------------------------------------------|-----:|:-----------------------------|:-----------------------------|:------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Verified    | Single-Stage Instance Shadow Detection With Bidirectional Relation Learning                        | 2032 | 10.1109/CVPR46437.2021.00007 | 10.1109/cvpr46437.2021.00007 | Verified via static CrossRef DOI lookup (score: 0.95)                                                                                                                               |
| Verified    | PointINet: Point Cloud Frame Interpolation Network                                                 | 2032 | 10.1609/AAAI.V35I3.16324     | 10.1609/aaai.v35i3.16324     | Verified via static CrossRef DOI lookup (score: 0.95)                                                                                                                               |
| Verified    | Cross-Modal Object Tracking: Modality-Aware Representations and a Unified Benchmark                | 2036 | 10.1609/AAAI.V36I2.20016     | 10.1609/aaai.v36i2.20016     | Verified via static CrossRef DOI lookup (score: 0.95)                                                                                                                               |
| Verified    | EECBS: A Bounded-Suboptimal Search for Multi-Agent Path Finding                                    | 2030 | 10.1609/AAAI.V35I14.17466    | 10.1609/aaai.v35i14.17466    | Verified via static CrossRef DOI lookup (score: 0.95)                                                                                                                               |
| Verified    | SpreadGNN: Decentralized Multi-Task Federated Learning for Graph Neural Networks on Molecular Data | 2032 | 10.1609/AAAI.V36I6.20643     | 10.1609/aaai.v36i6.20643     | Verified via static CrossRef DOI lookup (score: 0.95)                                                                                                                               |
| Minor error | Conditional Image Generation by Conditioning Variational Auto-Encoders                             | 2034 |                              |                              | The cited title and all three authors match the official OpenReview record for this ICLR 2022 poster, published 28 January 2022. The citation’s year, 2034, is incorrect; the…      |
| Minor error | Learning with Labeling Induced Abstentions                                                         | 2036 |                              |                              | The official NeurIPS proceedings page and ACM Digital Library record directly confirm the cited title, authors, and NeurIPS publication. The raw citation gives year 2036, but the… |
| Minor error | Neuro-Symbolic Language Modeling with Automaton-augmented Retrieval                                | 2033 |                              |                              | Title comparison: exact match to the title on the official PMLR article page. Venue comparison: the cited “ICML” corresponds to the official Proceedings of the 39th International… |
| Minor error | A Statistical Perspective on Retrieval-Based Models                                                | 2033 |                              |                              | The PMLR proceedings page directly confirms the title, all three authors, the ICML proceedings venue, and publication year 2023. The ICML 2023 poster page independently confirms…  |
| Minor error | Proximal Gradient Descent-Ascent: Variable Convergence under KŁ Geometry                           | 2030 |                              | 10.48550/arXiv.2102.04653    | The official ICLR poster record identifies the same title and all four authors as an ICLR 2021 paper. The arXiv record independently gives the same title and authors and says it…  |

Future date. 5 of 17 verified entries. 5 of 42 minor errors.

**Chimeric title.**

| VerusCite   | Title                                                           | Year | DOI                         | Matched DOI               | Note                                                                                                                                                                    |
|:------------|:----------------------------------------------------------------|-----:|:----------------------------|:--------------------------|:------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Minor error | Causal Inference Methods for Treatment Effect Estimation        | 2026 | 10.48550/arXiv.2602.12132v1 | 10.48550/arXiv.2602.12132 | Same arXiv/preprint work at arxiv_static (authors match), but the cited title differs from the current official title (similarity 0.27) — typically a version retitle;… |
| Minor error | Multi-Modal Fusion for Visual Question Answering                | 2026 | 10.48550/arXiv.2602.12196v1 | 10.48550/arXiv.2602.12196 | Same arXiv/preprint work at arxiv_static (authors match), but the cited title differs from the current official title (similarity 0.36) — typically a version retitle;… |
| Minor error | Federated Learning with Heterogeneous Client Distributions      | 2026 | 10.48550/arXiv.2602.12146v1 | 10.48550/arXiv.2602.12146 | Same arXiv/preprint work at arxiv_static (authors match), but the cited title differs from the current official title (similarity 0.22) — typically a version retitle;… |
| Minor error | Neural Scene Representation and Rendering                       | 2022 | 10.48550/arXiv.2602.12249v1 | 10.48550/arXiv.2602.12249 | Same arXiv/preprint work at arxiv_static (authors match), but the cited title differs from the current official title (similarity 0.26) — typically a version retitle;… |
| Minor error | Retrieval-Augmented Generation for Long-Form Question Answering | 2021 | 10.48550/arXiv.2602.12204v1 | 10.48550/arXiv.2602.12204 | Same arXiv/preprint work at arxiv_static (authors match), but the cited title differs from the current official title (similarity 0.37) — typically a version retitle;… |

Chimeric title. No verified entries. 5 of 15 minor errors.

**Wrong venue.**

| VerusCite   | Title                                                                                                                  | Year | DOI                          | Matched DOI                  | Note                                                                                                                                                                               |
|:------------|:-----------------------------------------------------------------------------------------------------------------------|-----:|:-----------------------------|:-----------------------------|:-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Verified    | Dense Label Encoding for Boundary Discontinuity Free Rotation Detection                                                | 2021 | 10.1109/CVPR46437.2021.01556 | 10.1109/cvpr46437.2021.01556 | Verified via static CrossRef DOI lookup (score: 1.00)                                                                                                                              |
| Verified    | Learning Local-Global Contextual Adaptation for Multi-Person Pose Estimation                                           | 2022 | 10.1109/CVPR52688.2022.01272 | 10.1109/cvpr52688.2022.01272 | Verified via static CrossRef DOI lookup (score: 1.00)                                                                                                                              |
| Verified    | Learning Cross-Modal Retrieval With Noisy Labels                                                                       | 2021 | 10.1109/CVPR46437.2021.00536 | 10.1109/cvpr46437.2021.00536 | Verified via static CrossRef DOI lookup (score: 1.00)                                                                                                                              |
| Verified    | MiniGPT-4: Enhancing Vision-Language Understanding with Advanced Large Language Models                                 | 2023 | 10.48550/arXiv.2304.10592    | 10.48550/arXiv.2304.10592    | Verified via arXiv id 2304.10592.                                                                                                                                                  |
| Verified    | PET-NeuS: Positional Encoding Tri-Planes for Neural Surfaces                                                           | 2023 | 10.1109/CVPR52729.2023.01212 | 10.1109/cvpr52729.2023.01212 | Verified via static CrossRef DOI lookup (score: 1.00)                                                                                                                              |
| Minor error | MonarchRT: Efficient Attention for Real-Time Video Generation                                                          | 2026 | 10.48550/arXiv.2602.12271v1  | 10.48550/arXiv.2602.12271    | Verified via arXiv id 2602.12271. Cited DOI (10.48550/arXiv.2602.12271v1) does not resolve (CrossRef/DataCite/doi.org) — cannot remain verified (bad/unregistered DOI). Identity…  |
| Minor error | Tiny Recursive Reasoning with Mamba-2 Attention Hybrid                                                                 | 2026 | 10.48550/arXiv.2602.12078v1  | 10.48550/arXiv.2602.12078    | Verified via arXiv id 2602.12078. Cited DOI (10.48550/arXiv.2602.12078v1) does not resolve (CrossRef/DataCite/doi.org) — cannot remain verified (bad/unregistered DOI). Identity…  |
| Minor error | Meta-Sel: Efficient Demonstration Selection for In-Context Learning via Supervised Meta-Learning                       | 2026 | 10.48550/arXiv.2602.12123v1  | 10.48550/arXiv.2602.12123    | Verified via arXiv id 2602.12123. Cited DOI (10.48550/arXiv.2602.12123v1) does not resolve (CrossRef/DataCite/doi.org) — cannot remain verified (bad/unregistered DOI). Identity…  |
| Minor error | Neutral Prompts, Non-Neutral People: Quantifying Gender and Skin-Tone Bias in Gemini Flash 2.5 Image and GPT Image 1.5 | 2022 | 10.48550/arXiv.2602.12133v1  | 10.48550/arXiv.2602.12133    | Verified via arXiv id 2602.12133. Cited DOI (10.48550/arXiv.2602.12133v1) does not resolve (CrossRef/DataCite/doi.org) — cannot remain verified (bad/unregistered DOI). Identity…  |
| Minor error | f-Domain Adversarial Learning: Theory and Algorithms                                                                   | 2021 |                              |                              | The cited title and all four authors are confirmed by the PMLR proceedings record, which identifies the work as appearing in the Proceedings of the 38th International Conference… |

Wrong venue. 5 of 22 verified entries. 5 of 24 minor errors.

**Swapped authors.**

| VerusCite   | Title                                                                                   | Year | DOI                          | Matched DOI                  | Note                                                                                                                                                                                |
|:------------|:----------------------------------------------------------------------------------------|-----:|:-----------------------------|:-----------------------------|:------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Verified    | Learning from Protein Structure with Geometric Vector Perceptrons                       | 2021 | 10.48550/arXiv.2009.01411    | 10.48550/arXiv.2009.01411    | Verified via arXiv id 2009.01411.                                                                                                                                                   |
| Verified    | Calibrate Before Use: Improving Few-Shot Performance of Language Models                 | 2021 | 10.48550/arXiv.2102.09690    | 10.48550/arXiv.2102.09690    | Verified via arXiv id 2102.09690.                                                                                                                                                   |
| Verified    | SDEdit: Guided Image Synthesis and Editing with Stochastic Differential Equations       | 2023 | 10.48550/arXiv.2108.01073    | 10.48550/arXiv.2108.01073    | Verified via arXiv id 2108.01073.                                                                                                                                                   |
| Verified    | The Mythos of Model Interpretability                                                    | 2021 | 10.48550/arXiv.1606.03490    | 10.48550/arXiv.1606.03490    | Verified via arXiv id 1606.03490.                                                                                                                                                   |
| Verified    | Big Bird: Transformers for Longer Sequences                                             | 2023 | 10.48550/arXiv.2007.14062    | 10.48550/arXiv.2007.14062    | Verified via arXiv id 2007.14062.                                                                                                                                                   |
| Minor error | Open Problems and Fundamental Limitations of Reinforcement Learning from Human Feedback | 2023 | 10.48550/arXiv.2307.15217    | 10.48550/arXiv.2307.15217    | CrossRef arxiv_static matches title/DOI (score: 1.00), but cited author identities disagree with the official list. Unmatched cited author(s): Yoni Halpern. Official authors:…     |
| Minor error | Understanding the Role of Training Regimes in Continual Learning                        | 2023 | 10.48550/arXiv.2006.06958    | 10.48550/arXiv.2006.06958    | CrossRef arxiv_static matches title/DOI (score: 1.00), but cited author identities disagree with the official list. Unmatched cited author(s): Dilan Gorur. Official authors:…      |
| Minor error | Scaling Data-Constrained Language Models                                                | 2022 | 10.48550/arXiv.2203.15556    | 10.48550/arXiv.2203.15556    | Same arXiv/preprint work at arxiv_static (authors match), but the cited title differs from the current official title (similarity 0.52) — typically a version retitle;…             |
| Minor error | Reinforcement Learning: An Introduction                                                 | 2022 |                              |                              | The MIT Press publisher page identifies the book as Reinforcement Learning: An Introduction, second edition, by Richard S. Sutton and Andrew G. Barto, published by The MIT Press…  |
| Minor error | Align Your Latents: High-Resolution Video Synthesis with Latent Diffusion Models        | 2023 | 10.1109/CVPR52729.2023.00403 | 10.1109/CVPR52729.2023.02161 | The official CVF Open Access proceedings page confirms the cited work and provides its title, authors, CVPR venue, year, and pages 22563–22575. The official IEEE Xplore page also… |

Swapped authors. 5 of 7 verified entries. 5 of 10 minor errors.

**Preprint as published.**

| VerusCite   | Title                                                                           | Year | DOI                          | Matched DOI                  | Note                                                                                                                                                                                |
|:------------|:--------------------------------------------------------------------------------|-----:|:-----------------------------|:-----------------------------|:------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Verified    | Robust Audio-Visual Instance Discrimination                                     | 2021 | 10.1109/CVPR46437.2021.01274 | 10.1109/cvpr46437.2021.01274 | Verified via static CrossRef DOI lookup (score: 1.00)                                                                                                                               |
| Verified    | Learning To Aggregate and Personalize 3D Face From In-the-Wild Photo Collection | 2021 | 10.1109/CVPR46437.2021.01399 | 10.1109/cvpr46437.2021.01399 | Verified via static CrossRef DOI lookup (score: 1.00)                                                                                                                               |
| Verified    | LLaMA: Open and Efficient Foundation Language Models                            | 2023 | 10.48550/arXiv.2302.13971    | 10.48550/arXiv.2302.13971    | Verified via arXiv id 2302.13971.                                                                                                                                                   |
| Verified    | Constitutional AI: Harmlessness from AI Feedback                                | 2023 | 10.48550/arXiv.2212.08073    | 10.48550/arXiv.2212.08073    | Verified via arXiv id 2212.08073.                                                                                                                                                   |
| Verified    | Robust Reinforcement Learning: A Case Study in Linear Quadratic Regulation      | 2021 | 10.1609/AAAI.V35I10.17122    | 10.1609/aaai.v35i10.17122    | Verified via static CrossRef DOI lookup (score: 1.00)                                                                                                                               |
| Minor error | DEPTS: Deep Expansion Learning for Periodic Time Series Forecasting             | 2022 |                              |                              | Title comparison: exact match to the official ICLR 2022 spotlight record. Venue comparison: the raw citation says “KDD,” but the direct official ICLR record and Microsoft…         |
| Minor error | GREAD: Graph Neural Reaction-Diffusion Networks                                 | 2023 |                              |                              | Title comparison: exact match. Venue comparison: the citation says IJCAI, but the direct PMLR proceedings article identifies the venue as the Proceedings of the 40th…              |
| Minor error | Conjugate Energy-Based Models                                                   | 2021 |                              |                              | The official PMLR proceedings page directly confirms the cited title, all five authors, and year 2021. It identifies the venue as the Proceedings of the 38th International…        |
| Minor error | Disambiguating Symbolic Expressions in Informal Documents                       | 2021 |                              |                              | Title comparison: exact match. Venue comparison: the raw citation says “WWW,” but the official OpenReview record identifies this paper as an ICLR 2021 Poster; arXiv’s record also… |
| Minor error | Adversarial Policy Learning in Two-player Competitive Games                     | 2021 |                              |                              | The PMLR proceedings page directly confirms the cited title, authors, and 2021 publication. Title comparison: exact match. Venue comparison: the citation says “ACL,” but the…      |

Preprint as published. 5 of 24 verified entries. 5 of 8 minor errors.

**Hybrid fabrication.**

| VerusCite   | Title                                                                          | Year | DOI                          | Matched DOI                  | Note                                                                                                                                                                               |
|:------------|:-------------------------------------------------------------------------------|-----:|:-----------------------------|:-----------------------------|:-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Minor error | IBRNet: Learning Multi-View Image-Based Rendering                              | 2021 | 10.1109/CVPR46437.2021.00469 | 10.1109/CVPR46437.2021.00466 | Direct IEEE Computer Society Digital Library record (https://www.computer.org/csdl/proceedings-article/cvpr/2021/450900e688/1yeIC9n861q), inspected via URL context, confirms the… |
| Minor error | TensoRF: Tensorial Radiance Fields                                             | 2022 | 10.1007/978-3-031-19830-4_20 | 10.1007/978-3-031-19824-3_20 | Title comparison: exact match. Venue comparison: Springer identifies it as a conference paper in Computer Vision – ECCV 2022, matching the cited ECCV venue. Author comparison:…   |
| Minor error | ViViT: A Video Vision Transformer                                              | 2021 | 10.1109/ICCV48922.2021.00678 | 10.1109/ICCV48922.2021.00676 | Title comparison: exact match. Venue comparison: the IEEE Computer Society record identifies the work as part of the 2021 IEEE/CVF International Conference on Computer Vision…    |
| Minor error | Masked Autoencoders Are Scalable Vision Learners                               | 2022 | 10.1109/CVPR52688.2022.01552 | 10.1109/CVPR52688.2022.01553 | Title comparison: exact match. Venue comparison: CVPR 2022 is confirmed by the official CVPR Open Access record and IEEE Xplore. Author comparison: all six cited authors match…   |
| Minor error | Mip-NeRF: A Multiscale Representation for Anti-Aliasing Neural Radiance Fields | 2021 | 10.1109/ICCV48922.2021.00582 | 10.1109/ICCV48922.2021.00580 | The cited work is confirmed by its IEEE Xplore publisher page, which gives the exact title, full author list, conference venue, year, and correct DOI…                             |

Hybrid fabrication. No verified entries. 5 of 7 minor errors.

**Partial author list.**

| VerusCite   | Title                                                                                                      | Year | DOI                          | Matched DOI                  | Note                                                                                                                                                                                |
|:------------|:-----------------------------------------------------------------------------------------------------------|-----:|:-----------------------------|:-----------------------------|:------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Verified    | Role of Optimizer on Network Fine-tuning for Adversarial Robustness (Student Abstract)                     | 2021 | 10.1609/AAAI.V35I18.17869    | 10.1609/aaai.v35i18.17869    | Verified via static CrossRef DOI lookup (score: 1.00)                                                                                                                               |
| Verified    | Contrastive Test-Time Adaptation                                                                           | 2022 | 10.1109/CVPR52688.2022.00039 | 10.1109/cvpr52688.2022.00039 | Verified via static CrossRef DOI lookup (score: 0.99)                                                                                                                               |
| Verified    | Matching Is Not Enough: A Two-Stage Framework for Category-Agnostic Pose Estimation                        | 2023 | 10.1109/CVPR52729.2023.00706 | 10.1109/cvpr52729.2023.00706 | Verified via static CrossRef DOI lookup (score: 0.99)                                                                                                                               |
| Verified    | Contrastive Identity-Aware Learning for Multi-Agent Value Decomposition                                    | 2023 | 10.1609/AAAI.V37I10.26370    | 10.1609/aaai.v37i10.26370    | Verified via static CrossRef DOI lookup (score: 0.99)                                                                                                                               |
| Verified    | Retrieval-based Controllable Molecule Generation                                                           | 2023 | 10.48550/ARXIV.2208.11126    | 10.48550/arXiv.2208.11126    | Verified via arXiv id 2208.11126.                                                                                                                                                   |
| Minor error | Online Enhanced Semantic Hashing: Towards Effective and Efficient Retrieval for Streaming Multi-Modal Data | 2022 | 10.1609/AAAI.V36I4.20346     | 10.1609/aaai.v36i4.20346     | Direct evidence: the DOI landing page at https://doi.org/10.1609/aaai.v36i4.20346 is the AAAI publisher record. It confirms the exact title, all six authors, the venue, 2022…      |
| Minor error | MoDem: Accelerating Visual Model-Based Reinforcement Learning with Demonstrations                          | 2023 |                              | 10.48550/arXiv.2212.05698    | Title comparison: exact match. Venue comparison: the cited entry says ICLR, but direct records identify the work as arXiv:2212.05698 (submitted 12 Dec 2022); the Meta publication… |
| Minor error | Online Unrelated Machine Load Balancing with Predictions Revisited                                         | 2021 |                              |                              | Direct primary evidence confirms the cited work: the ICML 2021 official poster record identifies the exact title and authors Shi Li and Jiayi Xian, and the PMLR proceedings PDF…   |
| Minor error | SCoRe: Pre-Training for Context Representation in Conversational Semantic Parsing                          | 2021 |                              |                              | The direct ICLR 2021 poster record confirms the cited title, venue, year, and five-author list. The citation identifies the same work, but its author list omits three official…    |
| Minor error | Knowledge distillation via softmax regression representation learning                                      | 2021 |                              |                              | The official OpenReview record confirms the cited title and ICLR 2021 venue and identifies the full author list. The concrete error is that the citation omits two authors from…    |

Partial author list. 5 of 40 verified entries. 5 of 61 minor errors.

**Near miss title.**

| VerusCite   | Title                                                                                                          | Year | DOI                          | Matched DOI                  | Note                                                                                                                                                                                |
|:------------|:---------------------------------------------------------------------------------------------------------------|-----:|:-----------------------------|:-----------------------------|:------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Verified    | Online Enhanced Semantic Hashing: Towards Effective and Efficient Retrieval towards Streaming Multi-Modal Data | 2022 | 10.1609/AAAI.V36I4.20346     | 10.1609/aaai.v36i4.20346     | Verified via static CrossRef DOI lookup (score: 0.98)                                                                                                                               |
| Verified    | Training To Aggregate and Personalize 3D Face From In-the-Wild Photo Collection                                | 2021 | 10.1109/CVPR46437.2021.01399 | 10.1109/cvpr46437.2021.01399 | Verified via static CrossRef DOI lookup (score: 0.98)                                                                                                                               |
| Verified    | TransZero: Attribute-Guided Transformer towards Zero-Shot Learning                                             | 2022 | 10.1609/AAAI.V36I1.19909     | 10.1609/aaai.v36i1.19909     | Verified via static CrossRef DOI lookup (score: 0.97)                                                                                                                               |
| Verified    | PAC-Bayesian Guarantees on Rate-Efficient Classifiers                                                          | 2022 |                              |                              | The PMLR publisher page directly confirms the cited title, authors, and 2022 publication. The raw citation gives the venue as “ICML,” which is the conference abbreviation; the…    |
| Verified    | Structured State Space Models for In Context Reinforcement Learning                                            | 2023 |                              | 10.52202/075280-2036         | Title comparison: the official record’s “In-Context” differs from the citation’s “In Context” only by hyphenation, a cosmetic variation. Venue comparison: “NeurIPS” is a short…    |
| Minor error | UniT: Unified Multimodal Chain of-Thought Test-time Scaling                                                    | 2026 | 10.48550/arXiv.2602.12279v1  | 10.48550/arXiv.2602.12279    | Verified via arXiv id 2602.12279. Cited DOI (10.48550/arXiv.2602.12279v1) does not resolve (CrossRef/DataCite/doi.org) — cannot remain verified (bad/unregistered DOI). Identity…   |
| Minor error | Self-supervised Learned Factor Analysis for Disentangling Utterance-level Speech Representations               | 2023 |                              | 10.48550/arXiv.2305.08099    | The official arXiv record identifies the work as accepted by ICML 2023 and lists the four cited authors. The citation’s title says “Learned Factor Analysis,” whereas the official… |
| Minor error | Local Tuning Achieves Global Optimality in Multi-Agent Reinforcement Learning                                  | 2023 |                              |                              | The direct PMLR proceedings record confirms the cited paper’s identity, authors, and year. The raw citation has a substantive title-word error: it says “Local Tuning” where the…   |
| Minor error | Marginalized Stochastic Natural Gradients for Black-Box Variational Reasoning                                  | 2021 |                              |                              | The official Proceedings of Machine Learning Research page identifies the same 2021 ICML work and lists the cited authors. However, the cited title ends in “Variational…           |
| Minor error | Community Concealment from Self-supervised Graph Learning-Based Clustering                                     | 2026 | 10.48550/arXiv.2602.12250v1  | 10.48550/arXiv.2602.12250    | Title comparison: the cited title says “Community Concealment from Self-supervised Graph Learning-Based Clustering,” while the arXiv primary record gives “Community Concealment…   |

Near miss title. 5 of 26 verified entries. 5 of 48 minor errors.

**Plausible fabrication.**

| VerusCite   | Title                                                                                               | Year | DOI                        | Matched DOI               | Note                                                                                                                                                                           |
|:------------|:----------------------------------------------------------------------------------------------------|-----:|:---------------------------|:--------------------------|:-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Minor error | Optimization and generalization of gradient descent for shallow relu networks with minimal width    | 2021 |                            |                           | The JMLR article page directly confirms the cited title and all four authors, but gives the publication as Journal of Machine Learning Research, 27(34):1−35, 2026. The cited… |
| Minor error | Language models of protein sequences at the scale of evolution enable accurate structure prediction | 2023 | 10.1038/s41467-023-37674-3 | 10.1101/2022.07.20.500902 | Title comparison: the cited title exactly matches the bioRxiv record. Venue comparison: the raw citation identifies Nature Communications and gives DOI…                       |

Plausible fabrication. No verified entries. All 2 minor errors.

**Arxiv version mismatch.**

| VerusCite   | Title                                                                                                            | Year | DOI                          | Matched DOI                  | Note                                                                                                                                                                                |
|:------------|:-----------------------------------------------------------------------------------------------------------------|-----:|:-----------------------------|:-----------------------------|:------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Verified    | SCAFFOLD: Stochastic Controlled Averaging for Federated Learning                                                 | 2023 | 10.48550/arXiv.1910.06378    | 10.48550/arXiv.1910.06378    | Verified via arXiv id 1910.06378.                                                                                                                                                   |
| Verified    | Instance-Aware Domain Generalization for Face Anti-Spoofing                                                      | 2021 | 10.1109/CVPR52729.2023.01959 | 10.1109/cvpr52729.2023.01959 | Verified via static CrossRef DOI lookup (score: 0.95)                                                                                                                               |
| Verified    | ACSeg: Adaptive Conceptualization for Unsupervised Semantic Segmentation                                         | 2022 | 10.1109/CVPR52729.2023.00692 | 10.1109/cvpr52729.2023.00692 | Verified via static CrossRef DOI lookup (score: 1.00)                                                                                                                               |
| Verified    | PET-NeuS: Positional Encoding Tri-Planes for Neural Surfaces                                                     | 2021 | 10.1109/CVPR52729.2023.01212 | 10.1109/cvpr52729.2023.01212 | Verified via static CrossRef DOI lookup (score: 0.95)                                                                                                                               |
| Verified    | Matching Networks for One Shot Learning                                                                          | 2023 | 10.48550/arXiv.1606.04080    | 10.48550/arXiv.1606.04080    | Verified via arXiv id 1606.04080.                                                                                                                                                   |
| Minor error | Prototypical Networks for Few-shot Learning                                                                      | 2023 | 10.5555/3295222.3295383      |                              | The official NeurIPS proceedings BibTeX record identifies this title and author list as a 2017 work (volume 30). The official NeurIPS paper PDF also identifies it as part of the…  |
| Minor error | Structured State Space Models for In-Context Reinforcement Learning                                              | 2022 |                              | 10.52202/075280-2036         | The official NeurIPS proceedings page and DOI landing page confirm this title and the cited authors. The proceedings record identifies it as a NeurIPS 2023 paper in Advances in…   |
| Minor error | A technical curriculum on language-oriented artificial intelligence in translation and specialised communication | 2023 | 10.48550/arXiv.2602.12251v1  | 10.48550/arXiv.2602.12251    | Verified via arXiv id 2602.12251. Cited DOI (10.48550/arXiv.2602.12251v1) does not resolve (CrossRef/DataCite/doi.org) — cannot remain verified (bad/unregistered DOI). Identity…   |
| Minor error | Hypergraph Propagation and Community Selection for Objects Retrieval                                             | 2022 |                              |                              | The official NeurIPS proceedings page confirms the cited title, authors, and NeurIPS venue, and identifies the work as part of NeurIPS 2021. The citation gives 2022, a concrete…   |
| Minor error | Rigid Body Flows for Sampling Molecular Crystal Structures                                                       | 2022 |                              |                              | Title comparison: exact match to the official PMLR proceedings page. Venue comparison: the citation says NeurIPS, but the publisher/proceedings record identifies the work as part… |

Arxiv version mismatch. 5 of 45 verified entries. 5 of 25 minor errors.

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
