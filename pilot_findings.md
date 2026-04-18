---
title: Pilot Extraction — Findings Summary
project: CoC Criminalization / PLE Engagement (Lee & Kim, UCF)
status: iteration 1 complete
last_updated: 2026-04-17
related:
  - "[[data_construction_methodology]]"
  - "[[codebook]]"
---

# Pilot Extraction Findings (iteration 1)

Small-scope proof-of-concept for the automated data construction pipeline
described in [[data_construction_methodology]].

## Scope

- **CoCs**: AL-500, CA-500, FL-501, NY-600, TX-600 (5 CoCs)
- **Year**: FY2024 only
- **Variables covered by this extractor version (v0.2)**: 104 per CoC
  - `1a_1a`, `1a_1b`, `1a_2`, `1a_3`, `1a_4` (5 identifier / label fields)
  - `1b_1_{1..33}_{meetings,voted,ces}` (99 categorical fields — full 1B-1 chart)
- **Total field comparisons**: 520

## Headline numbers

| Iteration | Extractor version | Weighted accuracy | A (categorical) | C (label) | Diffs |
|---|---|---|---|---|---|
| 0 | pdf_native_v0.1 | **99.23%** | 99.80% | 91.67% | 4 |
| 1 | pdf_native_v0.2 | **99.42%** | 99.80% | 93.75% | 3 |

Target is **≥ 98% weighted** with per-class floors (A ≥ 99, C ≥ 97). The
pilot **exceeds the overall and A-class floors** on iteration 1. C-class is
at 93.75% against the manual reference, but — as detailed below — the three
remaining C-class disagreements are all attributable to the **manual
reference, not the automated extractor**. After correcting the manual
spreadsheet, the pilot is at **100% agreement**.

## The three residual disagreements (post iteration 1)

All three are cases where the automated extractor is consistent with the
source PDF and the manual entry is not.

| # | CoC | Field | Manual value | Auto value | Source evidence | Category |
|---|---|---|---|---|---|---|
| 1 | AL-500 | `1a_1b` (CoC Name) | `Birmingham/Jefferson, St. Clair, Shelby Counties` | `Birmingham/Jefferson, St. Clair, Shelby Counties CoC` | PDF 1A-1 says "... Counties CoC"; most other manual rows retain the " CoC" suffix (e.g. `Montgomery City & County CoC`) | **E3 coder-inconsistency** |
| 2 | CA-500 | `1a_1b` (CoC Name) | `San Jose/ Santa Clara City & County CoC` (extra space) | `San Jose/Santa Clara City & County CoC` | PDF has no space; manual value has an inserted space after the slash | **E3 manual typo** |
| 3 | FL-501 | `1b_1_7_ces` (Hospital(s) · CES participation) | `Yes` | `No` | PDF row 7 reads "Hospital(s) … Yes Yes **No**" | **E3 manual data error** |

## Iteration record

- **Iteration 0** (baseline): v0.1 extractor; 4 diffs total. One real
  extractor bug (E1) identified — `1a_2`/`1a_3`/`1a_4` did not capture values
  that wrap across two lines, producing a truncated `1a_2` for CA-500.
- **Iteration 1**: v0.2 extractor adds wrap-aware continuation capture.
  The CA-500 `1a_2` diff is resolved. Per the exit rule in
  [[data_construction_methodology]] §5.4 (two consecutive iterations with no
  residual E1/E2), **iteration 1 is the first "clean" iteration** for the
  currently covered variable surface.

## What this tells us

1. **For 1A-family identifiers and the full 1B-1 participation chart,
   automated extraction is already more reliable than the manual
   coding.** Every remaining disagreement in the pilot is a manual error
   surfaced by the automated run.
2. **The anchor-then-parse + row-label matching strategy works.**
   Zero `needs_review` flags were raised on any 1B-1 row across the 5 CoCs;
   every canonical row was matched by label.
3. **The 520-field comparison is small.** We should not generalize to
   "98% target met" until the extractor covers more sections (1C, 1D, 1E,
   2A–2C, 3A, 4A) and is run on a larger pilot.

## Immediate next steps (already queued in the task list)

1. Extend the extractor to cover Section 1C (`1c_1_*` through `1c_7*`),
   Section 1D (criminalization-relevant fields including `1d_4_*`),
   Section 1E (local competition), and the HMIS / PIT tables in Section 2.
2. Add a DOCX adapter using `python-docx` for the eight DOCX-only sources
   (CA-505/509/511/513/521, MI-501, NV-500; CA-521 also has a scanned-PDF
   counterpart).
3. Add an OCR adapter (`ocrmypdf` preprocessing) for the 19 scanned PDFs
   identified in `file_inventory.csv`.
4. Begin Stage-2 LLM-assisted extraction for narrative variables
   (`1b_1a`, `1b_3`, `1d_4_*_prevent_crim`, etc.) with verbatim-quote
   requirement and human approval.
5. Backport the 3 surfaced manual errors into the reference xlsx (after PI
   review) to clean the ground truth before running the expanded pilot.

## Artifacts generated

- `data_pipeline/file_inventory.csv` — 677 source files indexed
- `data_pipeline/crosswalk.csv` — 113 canonical families mapped across years
- `data_pipeline/crosswalk_review.md` — 34 items for PI adjudication
- `data_pipeline/codebook.md` — first-pass codebook (331 variables)
- `data_pipeline/extracted/*.json` — per-CoC extracted records
- `data_pipeline/pilot_diff_report.md` — machine-generated diff report
- `data_pipeline/pilot_diffs.csv` — every disagreement, one row per field
- `data_pipeline/iterations.csv` — iteration ledger (2 rows so far)
