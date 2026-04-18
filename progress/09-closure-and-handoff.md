---
title: 09 — Closure and Handoff
order: 9
status: session-close snapshot
last_updated: 2026-04-17
---

# Closure and Handoff

This page closes out the first concentrated development session of the
data-construction pipeline. It catalogues what shipped, what the next
owner needs to know, and what remains.

## What shipped

### Documentation (all in `coc_criminalization/`)
- `data_construction_methodology.md` — formal Methods document with
  citations to Krippendorff, Neuendorf, Cohen, Landis & Koch, Hallgren,
  McHugh, Grimmer & Stewart, Grimmer/Roberts/Stewart, Gilardi et al.,
  Törnberg, Ziems et al., Herring/Yarbrough/Alatorre, Robinson, Shinn &
  Khadduri. Ready to slot into a paper's Methods section.
- `codebook.md` — first-pass codebook for all 331 variables, grouped by
  section with observed value domains.
- `pilot_findings.md` — snapshot of iterations 1–2.
- `progress/` — nine narrative pages (this one included) designed for
  publication as a methodology website.

### Code (all in `coc_criminalization/data_pipeline/`)
- `pipeline_utils.py` — shared helpers.
- `build_file_inventory.py` → `file_inventory.csv` (677 rows).
- `build_codebook.py` → `codebook.md`.
- `build_crosswalk.py` → `crosswalk.csv` (113 families) + `crosswalk_review.md` (34 flagged).
- `extract_pdf_native.py` v0.4 — native PDF adapter covering 242 fields.
- `extract_docx.py` v0.1 — DOCX adapter (partial coverage; used for CA-521).
- `router.py` — corpus-wide routing + execution (292 CoCs in 55 s).
- `pilot_run.py` — 5-CoC pilot diff runner with class-specific comparators.
- `corpus_diff.py` — full-corpus diff against manual xlsx.
- `build_review_ui.py` → `review_ui.html` — static HTML reviewer console.

### Outputs
- `extracted/` — 292 JSON files, one per CoC, ~242 records each.
- `extraction_summary.csv` — per-CoC routing record.
- `corpus_diffs.csv` — 2,324 disagreements with class, source page, reason.
- `corpus_agreement.md` — machine-generated agreement report.
- `iterations.csv` — iteration ledger (4 iterations).

## Final numbers

| Metric | Value |
|---|---|
| CoCs processed | 292 (of 301 available FY2024) |
| Variables extracted per CoC | 242 (~73% of canonical schema) |
| Field comparisons against manual | 69,361 |
| **Weighted agreement** | **96.65%** |
| **Adjusted agreement** (exclude manual-blank cells) | **98.25%** ✅ |
| Auto-fill candidates (manual blank, auto extracted) | 1,131 |
| True value disagreements | 1,193 |
| CoCs failing due to scanned/corrupt text | 9 (need OCR) |

## Handoff — open items

### Task #2 — formal ground-truth audit
The corpus run generated a list of **~1,131 backfill candidates** and
**~1,193 value disagreements** that should be sampled and adjudicated.
A 20-CoC stratified audit (across coders Koko, Kulsum, Adamaris,
Andy, Cristina, Devin) would quantify per-coder error rates and
produce a cleaned reference dataset. Estimated effort: one focused
week for a senior RA.

### OCR adapter
Nine CoCs failed extraction because their PDFs use font encodings that
`pdftotext` cannot decode (e.g., WA-504 renders as `$SSOLFDQW` for
"Applicant"). Running `ocrmypdf` on these nine files and re-routing
them through the native extractor should recover most or all of them.
No architectural changes needed — the router already has an
`ocr_required` path waiting to be wired.

### DOCX adapter — full parity
The v0.1 DOCX adapter extracts 1A identifier fields and table-based
sections cleanly but misses the 1B-1 chart on the 8 DOCX-only CoCs.
The issue is layout: DOCX rendering puts numbered rows in table cells
rather than as `N. label ... value` lines. Either (a) render tables
with explicit padding so the PDF-compatible regex still matches, or
(b) add a dedicated table-walker for DOCX. Either is a 1-day fix.

### Stage-2 LLM narrative extraction
Forty-one narrative variables (including `1d_2a`, the criminalization
rationale in `1d_4`, and the long free-text `1b_1a`, `1b_3`) are not
yet covered. The architecture is in `data_construction_methodology.md`
Stage 2: Claude + prompt caching + verbatim-quote requirement + drafts
layer. When LLM budget is approved, this plugs in as a new adapter
that writes to `drafts/` instead of `extracted/`.

### 2022 and 2023 sheets
The current target is FY2024 only. The crosswalk is in place; adding
2022 and 2023 panels requires running the router with `--year 2022`
and `--year 2023` and routing each extracted record through
`crosswalk.csv` to remap question IDs to the canonical schema.
Estimated effort: one day once the 2024 pipeline is PI-approved.

### Reviewer workflow
`review_ui.html` is a static page; a full workflow would store the
accept/edit/reject decisions and push backports into the spreadsheet.
An Obsidian-friendly alternative: emit one Markdown file per
disagreement batch that PIs can walk through and annotate in place.

## A note on what we did not do

The pipeline does **not** automatically patch the manual spreadsheet.
Every proposed backport must go through PI review first. This is a
deliberate design choice — an automated pipeline that silently
"corrects" human data ruins provenance and trust. The separation
between `drafts/` and the canonical `coc_apps_all_info.xlsx` exists
for exactly this reason.

## Where to start next session

1. Skim `progress/README.md` — everything links from there.
2. Open `review_ui.html` in a browser and spend 20 minutes on the
   "value mismatches" tab to build intuition for the residual errors.
3. Run the 20-CoC ground-truth audit (Task #2) — this is the single
   most consequential remaining step because it calibrates trust in
   both the manual reference and the pipeline.
4. Decide whether to prioritize OCR (unlock 9 more CoCs) or Stage-2
   LLM (unlock narrative variables) next.

Back to [[README]]
