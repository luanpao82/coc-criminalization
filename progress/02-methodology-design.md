---
title: 02 — Methodology Design
order: 2
status: complete
last_updated: 2026-04-17
---

# Methodology Design

Having seen what the corpus actually looks like, we designed an extraction
pipeline that treats the manual spreadsheet as a *reference to be
validated*, not as ground truth in the traditional sense. The design is
documented formally in [[data_construction_methodology]]; this page
captures the decisions *in plain language*.

## Four decisions that shaped the design

### Decision 1 — Treat the manual spreadsheet as a provisional reference

The original plan was to use `coc_apps_all_info.xlsx` as ground truth.
Fifteen coders had already spent weeks on it; it was the obvious
benchmark. But a spreadsheet produced by 15 people over several months
contains coder drift, typos, and interpretation differences. If we used
it naively, the pipeline would be trained to *match the spreadsheet*,
including its errors.

**Resolution:** the pipeline is benchmarked against the spreadsheet, but
a **small audit subsample** is reconciled against the source PDFs and
treated as the "cleaned" reference. The spreadsheet itself gets corrected
as automation surfaces provable discrepancies.

### Decision 2 — One schema, year-specific extractors

HUD's questions renumber year-to-year (e.g., FY2022's `1D-9/10/11/12` are
restructured into FY2024's `1D-4/5/6` family). We keep a single canonical
schema — the FY2024 numbering already used by the spreadsheet — and build
per-year extractors that follow a crosswalk onto it.

**Why this matters:** the alternative (a separate schema per year) splits
the dataset into incompatible shards and makes panel analysis harder.
The crosswalk lets researchers read the data as a single panel while
preserving each year's provenance.

### Decision 3 — Anchor-then-parse, never whole-document parsing

HUD application PDFs have ~69 pages. A single regex or parser that tries
to read the whole document at once is brittle — one layout quirk
propagates errors across dozens of variables. Instead, the extractor
**locates each question number as an anchor and parses only the local
block that follows.** If one block fails, the other 330 variables are
unaffected.

### Decision 4 — Provenance on every cell

Every output record carries `source_page`, `extractor`, `confidence`, and
(for narrative fields) a **verbatim quotation of the evidentiary
sentence**. This makes every value auditable against the source PDF. It
is the single most important design constraint for defensibility, and it
follows directly from the human-in-the-loop recommendations in Ziems et
al. (2024).

## The four variable classes

| Class | Examples | Share (est.) | Target accuracy | Validation |
|---|---|---|---|---|
| A. Categorical | Yes / No / Nonexistent; CA / UFA | ~60% | ≥ 99% | Exact match on controlled vocabulary |
| B. Numeric | PIT counts, bed-coverage % | ~15% | ≥ 99% | Exact match after unit normalization |
| C. Identifier / Label | CoC name, HMIS lead | ~10% | ≥ 97% | Case/whitespace-normalized string match |
| D. Narrative | Criminalization-prevention text, racial-equity text | ~15% | ≥ 90% reviewer acceptance | Reviewer approves LLM-produced structured summary + verbatim quotation |

Splitting accuracy by class was essential. Measured as a single number,
the 2,500-character narrative fields would drag the headline down. By
setting per-class floors we can ship each stage as it crosses its
threshold.

## The three-stage pipeline

```
Stage 1: deterministic extractors (A/B/C variables)
         → common schema with provenance
         
Stage 2: LLM-assisted extraction (D variables)
         → drafts/ layer with required verbatim evidence
         
Stage 3: reviewer approval
         → canonical dataset (commit)
```

Stage 3 is non-negotiable. The LLM never writes to the final dataset
directly; a human reviews every narrative-derived value alongside the
PDF evidence it cites.

## The 98% convergence loop

Each discrepancy between automation and the reference is categorized:

1. **E1** — extractor bug (fix the parser)
2. **E2** — mapping error (fix the crosswalk)
3. **E3** — reference-standard error (fix the manual data)
4. **E4** — format variant (strengthen the adapter)
5. **E5** — narrative paraphrase (tune the prompt or accept the output)
6. **E6** — source noise (improve OCR preprocessing)

Exit criteria: weighted ≥ 98%, per-class floors met, two consecutive
iterations with zero residual E1 / E2. Iteration history is logged in
`iterations.csv`.

## Why this is publishable

Methodologically this combines three well-established streams — content
analysis, text-as-data, and LLM-assisted annotation — with a convergence
discipline borrowed from iterative software quality practice. The
citation backbone in [[data_construction_methodology]] places each design
choice in the relevant literature.

Next: [[03-schema-and-crosswalk]]
