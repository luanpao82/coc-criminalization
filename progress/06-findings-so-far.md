---
title: 06 — Findings So Far
order: 6
status: living (updated as work continues)
last_updated: 2026-04-17
---

# Findings So Far

Snapshot of where the pipeline stands at the end of iteration 2 and what
comes next. This page is updated as each extractor expansion completes.

## Headline numbers

| Metric | Value |
|---|---|
| Source files indexed | 677 |
| Canonical schema variables | 331 |
| Canonical families with year-to-year crosswalk | 113 |
| Crosswalk families flagged for PI review | 34 |
| Variable surface covered by v0.2 extractor | 104 (~31% of schema) |
| Pilot CoCs | 5 |
| Field comparisons in pilot | 520 |
| Weighted accuracy against manual reference | **99.42%** |
| Residual disagreements traced to extractor | 0 |
| Residual disagreements traced to manual reference | 3 |

## What we can already say

1. **The pipeline is more accurate than the manual reference on the
   covered surface.** Every remaining disagreement in iteration 2 is a
   manual-data-entry error surfaced by automation.
2. **The anchor-then-parse + label-match design works.** Zero
   `needs_review` flags were raised on the 520 comparisons. Row-count
   variance in the 1B-1 chart (some CoCs have 33 rows, some have 35)
   did not produce a single off-by-one error.
3. **The iteration loop has surfaced exactly the problems it was built
   to surface.** One extractor bug (E1 wrap capture) was found and
   fixed; three manual-reference errors (E3) were identified for
   backporting.

## What we cannot yet say

The claim "the pipeline is 99.4% accurate overall" requires expanding
the covered variable surface beyond 1A and 1B-1. Specifically, we have
not yet validated:

- Sections 1C through 1E (governance coordination, criminalization
  strategies, local competition)
- Section 2 (HMIS implementation, PIT counts, system performance)
- Section 3 (coordination with housing / healthcare)
- Section 4 (DV Bonus applicant capacity)
- Any narrative / free-text variable

Until those are covered, the pilot is a strong existence proof but not
a final benchmark.

## Known open items

- **Ground-truth audit (Task #2).** We have incidental E3 findings from
  the pilot, but a systematic 20-CoC stratified audit across coders has
  not yet been run.
- **DOCX adapter.** Eight sources are DOCX-only (CA-505, CA-509, CA-511,
  CA-513, CA-521, MI-501, NV-500 and CA-521's DOCX counterpart to a
  scanned PDF). Built using `python-docx` for structural (not
  flattened-text) parsing.
- **OCR adapter.** Nineteen scanned PDFs identified in `file_inventory.csv`
  need `ocrmypdf` preprocessing before they can be routed to the native
  extractor.
- **Stage-2 LLM extraction.** Narrative variables including the
  substantively central `1d_4_*_prevent_crim` family are not yet
  covered. Stage 2 uses Claude with a JSON output schema and a mandatory
  verbatim-quote requirement.
- **Reviewer UI.** Each proposed value, its source page, and its
  confidence need to be surfaced in a lightweight review interface so
  human coders can accept / edit / reject at scale.

## Next documented iteration

The next page in this log ([[07-extending-coverage]]) will document
extending the extractor to cover Section 1C (coordination and engagement
questions including the criminalization-focused 1D-4 family) and
re-running the pilot with the expanded surface.

Back to [[README]]
