---
title: Data Construction Methodology — HUD CoC Application Corpus
project: CoC Criminalization / PLE Engagement (Lee & Kim, UCF)
status: working draft v0.1
last_updated: 2026-04-17
audience: coauthors, research assistants, methods section of paper
related:
  - "[[KL_From_Inclusion_to_Influence]]"
  - "[[2025_ARNOVA_KL]]"
  - "[[codebook]]"
  - "[[pilot_findings]]"
---

# Data Construction Methodology

## 1. Purpose of This Document

This note specifies how we convert HUD Continuum of Care (CoC) Consolidated Application documents into a structured, research-grade dataset usable for our PLE-engagement and criminalization analyses. It is designed to serve three audiences simultaneously:

1. **Coauthors and RAs** — as a working protocol that defines roles, decisions, and quality gates.
2. **Peer reviewers** — as the basis of the Methods section, describing a reproducible, human-in-the-loop extraction pipeline with quantified accuracy.
3. **Future replicators** — as a reference architecture for converting annual federal application corpora into panel datasets.

The methodology combines classical content analysis (Krippendorff, 2018; Neuendorf, 2017) with recent advances in LLM-assisted text annotation (Gilardi, Alizadeh, & Kubli, 2023; Ziems et al., 2024) and the broader text-as-data program in the social sciences (Grimmer & Stewart, 2013; Grimmer, Roberts, & Stewart, 2022). Human coders remain the validating authority; automation is used to accelerate extraction and to expose disagreement for review, not to replace judgment.

---

## 2. Corpus and Unit of Observation

### 2.1 Source documents
- **Corpus**: HUD FY2022, FY2023, and FY2024 CoC Consolidated Applications (`1A`–`4B` sections), obtained for ~310 CoCs per year.
- **Formats**: Primarily native PDF exports from HUD's *e-snaps* system; a minority are `.docx` exports, and a small subset are scanned (image-based) PDFs.
- **Unit of observation**: CoC × fiscal year.

### 2.2 Target schema
- **Single canonical schema** keyed to the FY2024 question numbering (~331 variables; e.g., `1a_1a` = CoC Name, `1b_1_1_meetings` = Affordable Housing Developer participation in CoC meetings).
- **Variable types** fall into four analytic classes, each with its own validation rule:

| Class | Examples | Typical share | Validation rule |
|---|---|---|---|
| **A. Categorical** | Yes / No / Nonexistent; CA / UFA designation | ~60% | Exact match on controlled vocabulary |
| **B. Numeric** | PIT counts, HMIS bed-coverage %, reallocation dollar amounts | ~15% | Exact match after unit normalization |
| **C. Identifier / Label** | CoC name, HMIS lead, PHA name | ~10% | Normalized string match (case, whitespace, punctuation) |
| **D. Narrative** | 1B-1a racial-equity narrative, 1D-4 criminalization-prevention narrative | ~15% | Reviewer acceptance of structured summary + verbatim quotation of evidence |

### 2.3 Known sources of document heterogeneity
Our pilot inspection confirmed non-trivial heterogeneity that any pipeline must absorb:

1. **Year-to-year question renumbering.** Question IDs and wording change across FY2022–FY2024 (e.g., `1D-9/10/11/12` in FY2022 consolidated into `1D-4`-family items by FY2024). A year-specific schema is required, with a crosswalk onto the canonical FY2024 schema.
2. **Format heterogeneity.** Native PDF, scanned PDF, and DOCX exports require separate extractors.
3. **Within-document variance.** The 1B-1 participation chart has 33–35 rows depending on whether optional "Other" rows are used by a given CoC; extractors must index by row **label**, not row **position**.
4. **Filename inconsistencies.** Some files use `-` where others use `_` (e.g., `FL-_601_2022.pdf`, `LA-506_2023.pdf`); identifiers are normalized at ingestion.

---

## 3. Coding Framework

We treat the corpus as the object of systematic content analysis. Following Krippendorff (2018) and Neuendorf (2017), the framework fixes — in this order — (a) the unit of analysis, (b) the category system, (c) the decision rules, and (d) the reliability targets, before any coding begins.

### 3.1 Codebook
- Maintained as `codebook.md` (versioned).
- For each variable: definition, source question ID by year, allowable values, missing-value conventions (`NA_not_asked_this_year`, `NA_refused`, `NA_skipped`, blank for true unknown), and adjudication guidance for common edge cases.
- Narrative variables carry an **extraction specification** (what to pull) and an **output schema** (how to represent it as structured codes).

### 3.2 Crosswalk
- `crosswalk.csv` maps each year's question ID to the canonical FY2024 schema column. Non-mappable items are recorded with an explicit `NA_reason`, preserving interpretability of missingness.

### 3.3 Coder assignments
- One RA is primary coder per CoC; overlapping double-coding on a random 10% subsample supports inter-rater reliability estimation (§6).

---

## 4. Extraction Pipeline

The pipeline has three stages. All stages emit records in a common schema — `{coc_id, year, field_id, value, raw_text, source_page, extractor, confidence, needs_review}` — which enables downstream validation and audit.

### 4.1 Stage 1 — Deterministic extraction for structured variables (Classes A, B, C)
- **Format-specific adapters**: `extract_pdf_native` (pdfplumber; table reconstruction), `extract_pdf_ocr` (ocrmypdf preprocessing), `extract_docx` (python-docx structural walk).
- **Anchor-then-parse** strategy: each question number (`1B-1.`, `1D-4.`) is located as an anchor, and only the local block that follows is parsed. This isolates extraction errors to single fields rather than propagating them across a document.
- **Row matching by label**, not position, to absorb within-document row-count variance.
- **Controlled-vocabulary validation**: every Class-A value is checked against the codebook; out-of-vocabulary values are flagged `needs_review=True` and never silently coerced.

### 4.2 Stage 2 — LLM-assisted extraction for narrative variables (Class D)
- We use Claude Opus with prompt caching to extract structured summaries from the narrative fields (e.g., whether a CoC reports engagement with specific policymaker categories in 1D-4).
- The prompt fixes the output as a JSON schema aligned to the codebook and **requires verbatim quotation** of the evidentiary sentence for each extracted code. This makes every LLM-derived value auditable against the source document — the single most important design constraint for defensibility.
- LLM output is written to a `drafts/` layer, never directly to the final dataset. A human coder reviews each draft, sees the quoted evidence, and accepts, edits, or rejects. This "human-in-the-loop" arrangement follows the accuracy-reliability findings in Gilardi et al. (2023), Törnberg (2023), and Ziems et al. (2024), while retaining final judgment with trained researchers (cf. Grimmer, Roberts, & Stewart, 2022, on the limits of purely automated text analysis).

### 4.3 Stage 3 — Commit to canonical dataset
- Only reviewed, validated values are committed to the analysis-ready table.
- Each final cell carries provenance: source page, extractor, confidence, reviewer, and timestamp. This provenance layer doubles as the replication artifact.

---

## 5. Validation Strategy and 98% Convergence Target

### 5.1 Reference standard
- A manually coded spreadsheet (FY2024; ~292 CoCs completed by ~15 coders) serves as the **initial reference standard**.
- Before treating it as ground truth, we audit a random sample of 20 CoCs (full column set) against the underlying PDFs to estimate the manual error rate. Only the audited subset is treated as gold; discrepancies discovered during auditing are corrected on both sides (manual and automated).

### 5.2 Agreement metrics
- **Class A and C**: percent exact agreement and Cohen's κ (Cohen, 1960; McHugh, 2012).
- **Class B**: exact-match rate after unit normalization.
- **Class D**: reviewer acceptance rate for the LLM-derived structured summary (binary accept/edit/reject), plus verbatim-quote retrieval success.
- **Inter-rater reliability** on double-coded subsample: Cohen's κ per variable, interpreted with Landis and Koch (1977) benchmarks and reported following the tutorial recommendations in Hallgren (2012).

### 5.3 Convergence target
- Overall weighted agreement **≥ 98%**, with per-class floors: A ≥ 99%, B ≥ 99%, C ≥ 97%, D ≥ 90% reviewer acceptance.
- Agreement is computed on the audited subsample and, as coverage expands, on the full corpus.

### 5.4 Iteration loop
Each discrepancy between automated output and the reference standard is assigned to one of six root-cause categories:

1. **E1 — Extractor bug** (parser code is wrong) → fix parser.
2. **E2 — Mapping error** (crosswalk or schema is wrong) → fix schema.
3. **E3 — Reference-standard error** (manual coder was wrong) → correct gold and update training notes.
4. **E4 — Format variant** (row count, table structure, etc.) → strengthen adapter.
5. **E5 — Narrative paraphrase** (LLM output semantically correct but textually divergent) → refine prompt / acceptance criterion.
6. **E6 — Source noise** (OCR errors, scan quality) → improve preprocessing.

Each iteration logs: weighted accuracy, per-class accuracy, dominant error category, fix applied, and regression test pass/fail. We exit the loop when (a) the 98%-with-floors target is met **and** (b) two consecutive iterations show no residual E1 or E2 errors — i.e., the remaining error is attributable to source documents rather than to our pipeline or schema.

### 5.5 Residual cases
Items that remain ambiguous after iteration are adjudicated by the PI team and recorded in `adjudication_log.md`, a practice consistent with disclosure recommendations for human-coded datasets (Neuendorf, 2017; Krippendorff, 2018).

---

## 6. Reliability and Quality Control

1. **Double coding**: random 10% of CoCs are independently coded by two RAs; Cohen's κ reported per variable.
2. **Weekly audit**: PIs sample 5 CoCs per week to surface systematic errors early.
3. **Controlled vocabulary enforcement**: Class-A values outside the codebook cannot be entered into the final dataset without PI adjudication.
4. **Cross-year consistency checks**: for near-stable variables (CoC name, lead agency type, HMIS lead), unexplained year-to-year changes are flagged for review.
5. **Provenance preservation**: every committed cell retains its source page and evidence quote (for narrative codes), supporting both internal audit and external replication.

---

## 7. Reproducibility and Data Management

- All code (schema files, extractors, validators, iteration ledgers) is versioned in a project repository.
- Raw PDFs, OCR text, LLM drafts, reviewed values, and the final canonical dataset are stored as separate artifacts, never overwritten in place.
- A data-generation manifest records, for every run, the code commit, the input file checksum, and the extractor version, enabling bit-level reproducibility of the published dataset.
- The final artifact ships with a data dictionary and the iteration ledger, so reviewers can evaluate not only the endpoint but the convergence path.

---

## 8. Limitations

1. **Self-report.** CoC Applications are self-reports submitted to a funder with incentives to display compliance; our measures reflect reported practice, not necessarily realized practice. This is a long-standing caveat in analyses of federal homelessness data (see, e.g., Shinn & Khadduri, 2020).
2. **Schema drift.** Year-to-year changes in HUD's questions mean some constructs are not observed in every year; the crosswalk makes this explicit but cannot manufacture missing information.
3. **Narrative compression.** Encoding 2,500-character narrative responses into structured codes necessarily loses nuance; we mitigate this by retaining verbatim quotations of the evidentiary sentences.
4. **LLM failure modes.** Even state-of-the-art models can confabulate; our requirement of verbatim quotation plus human review is the principal defense, consistent with recent guidance on responsible use of LLMs in computational social science (Ziems et al., 2024).

---

## 9. Positioning in the Literature

Our data-construction approach combines three established streams.

- **Classical content analysis** provides the conceptual scaffolding — codebooks, controlled categories, inter-rater reliability, adjudication — that has anchored systematic text coding for decades (Krippendorff, 2018; Neuendorf, 2017; Cohen, 1960; Landis & Koch, 1977; Hallgren, 2012; McHugh, 2012).
- **Text-as-data in the social sciences** frames automated extraction from policy documents as a measurement task requiring explicit validation against human judgment rather than a replacement for it (Grimmer & Stewart, 2013; Grimmer, Roberts, & Stewart, 2022).
- **LLM-assisted annotation** provides the empirical basis for using large language models as first-pass annotators with human oversight; Gilardi, Alizadeh, and Kubli (2023), Törnberg (2023), and Ziems et al. (2024) document both the accuracy gains and the failure modes that motivate our human-in-the-loop design.

Substantively, our use of CoC application documents to measure governance structure, PLE engagement, and policy posture extends work on the criminalization of homelessness (Herring, Yarbrough, & Alatorre, 2020; Robinson, 2019) by supplying a panel measurement instrument grounded in federal documentary records.

---

## 10. References

- Cohen, J. (1960). A coefficient of agreement for nominal scales. *Educational and Psychological Measurement*, 20(1), 37–46.
- Gilardi, F., Alizadeh, M., & Kubli, M. (2023). ChatGPT outperforms crowd workers for text-annotation tasks. *Proceedings of the National Academy of Sciences*, 120(30), e2305016120.
- Grimmer, J., & Stewart, B. M. (2013). Text as data: The promise and pitfalls of automatic content analysis methods for political texts. *Political Analysis*, 21(3), 267–297.
- Grimmer, J., Roberts, M. E., & Stewart, B. M. (2022). *Text as Data: A New Framework for Machine Learning and the Social Sciences*. Princeton, NJ: Princeton University Press.
- Hallgren, K. A. (2012). Computing inter-rater reliability for observational data: An overview and tutorial. *Tutorials in Quantitative Methods for Psychology*, 8(1), 23–34.
- Herring, C., Yarbrough, D., & Marie Alatorre, L. (2020). Pervasive penality: How the criminalization of poverty perpetuates homelessness. *Social Problems*, 67(1), 131–149.
- Krippendorff, K. (2018). *Content Analysis: An Introduction to Its Methodology* (4th ed.). Thousand Oaks, CA: Sage.
- Landis, J. R., & Koch, G. G. (1977). The measurement of observer agreement for categorical data. *Biometrics*, 33(1), 159–174.
- McHugh, M. L. (2012). Interrater reliability: The kappa statistic. *Biochemia Medica*, 22(3), 276–282.
- Neuendorf, K. A. (2017). *The Content Analysis Guidebook* (2nd ed.). Thousand Oaks, CA: Sage.
- Robinson, T. (2019). No right to rest: Police enforcement patterns and quality of life consequences of the criminalization of homelessness. *Urban Affairs Review*, 55(1), 41–73.
- Shinn, M., & Khadduri, J. (2020). *In the Midst of Plenty: Homelessness and What to Do About It*. Hoboken, NJ: Wiley-Blackwell.
- Törnberg, P. (2023). ChatGPT-4 outperforms experts and crowd workers in annotating political Twitter messages with zero-shot learning. *arXiv preprint* arXiv:2304.06588.
- Ziems, C., Held, W., Shaikh, O., Chen, J., Zhang, Z., & Yang, D. (2024). Can large language models transform computational social science? *Computational Linguistics*, 50(1), 237–291.

---

## Appendix A — Iteration Ledger Template

| iter | date | weighted_acc | A_acc | B_acc | C_acc | D_approve | top_error | fix_applied | regression_pass |
|---|---|---|---|---|---|---|---|---|---|
| 0 | YYYY-MM-DD | — | — | — | — | — | baseline | — | — |

## Appendix B — File-Level Provenance Schema

```
coc_id, year, field_id, value,
raw_text, source_page, source_bbox,
extractor, extractor_version, confidence,
reviewer, reviewed_at, status, adjudication_note
```

## Appendix C — Related Internal Documents

- [[KL_From_Inclusion_to_Influence]] — project concept note, research questions, theoretical framing.
- [[2025_ARNOVA_KL]] — ARNOVA 2025 presentation of preliminary findings.
- [[codebook]] — canonical variable definitions and decision rules (v0.1 draft, 331 variables).
- [[pilot_findings]] — pilot extraction results (iterations 1–2, 5-CoC, 520-field surface).
- `data_pipeline/crosswalk.csv` — FY2022/FY2023 → FY2024 question ID mapping (113 canonical families).
- `data_pipeline/crosswalk_review.md` — 34 mappings flagged for PI adjudication.
- `data_pipeline/file_inventory.csv` — 677 source files indexed (format, scan flag, duplicates).
- `data_pipeline/iterations.csv` — iteration ledger (weighted accuracy per iteration + dominant error category).

## Appendix D — Pilot Results Reference

Four iterations were run, escalating from a 5-CoC pilot to the full FY2024 corpus (292 CoCs).

| Iteration | Extractor | Scope | Weighted | Adjusted | Residual |
|---|---|---|---|---|---|
| 1 | `pdf_native_v0.1` | 5 CoCs × 104 vars (520 comparisons) | 99.23% | — | 1× E1 + 3× E3 |
| 2 | `pdf_native_v0.2` | 5 CoCs × 104 vars | 99.42% | — | 3× E3 (manual errors) |
| 3 | `pdf_native_v0.3` | 5 CoCs × 242 vars (1,210 comparisons) | 99.30% | — | 5× E3 |
| 4 | `pdf_native_v0.4` | **292 CoCs × 242 vars (69,361 comparisons)** | **96.65%** | **98.25%** ✅ | 1,131 auto-fill candidates + ~400 true value disagreements |

The adjusted agreement metric excludes cells where the manual spreadsheet was blank and the extractor proposed a value (these are candidate backfills, not extractor errors). Full details in [[pilot_findings]] and [[progress/08-corpus-scale-run]].
