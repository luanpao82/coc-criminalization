---
title: 07 — Extending Coverage (Iteration 3)
order: 7
status: complete
last_updated: 2026-04-17
---

# Iteration 3 — Extending to the Criminalization-Relevant Variables

The pilot in [[05-debugging-and-iteration]] proved that the
anchor-then-parse design works for 1A-family identifiers and the big
1B-1 participation chart. Iteration 3 extends coverage to five more
question groups — including the criminalization-strategies chart
(`1D-4`) that is substantively central to the study.

## Scope added in v0.3

| Section | Structure | Variables added |
|---|---|---|
| 1C-1 — Coordination with federal/state/local orgs | 17 rows × 1 col (Yes/No/Nonexistent) | `1c_1_1`..`1c_1_17` (17) |
| 1C-2 — ESG consultation | 4 rows × 1 col | `1c_2_1`..`1c_2_4` (4) |
| 1C-3 — Ensuring families are not separated | 5 rows × 1 col | `1c_3_1`..`1c_3_5` (5) |
| 1D-1 — Preventing people transitioning from public systems | 4 rows × 1 col | `1d_1_1`..`1d_1_4` (4) |
| 1D-2 — Housing First numeric | 3 scalar numbers | `1d_2_1`, `1d_2_2` (integers), `1d_2_3` (percent) |
| 1D-4 — **Strategies to Prevent Criminalization** | 3 rows × 2 cols | `1d_4_{1..3}_policymakers`, `1d_4_{1..3}_prevent_crim` (6) |

Coverage jumps from **104 → 143 variables per CoC** (~43% of the
canonical schema) and — critically — now includes every field that
appears in our criminalization hypothesis.

## Design refactor: the generic chart extractor

Rather than duplicate the 1B-1 parser for each new table, v0.3
introduces `extract_generic_chart(...)` parameterized by:

- `start_anchor` / `end_anchor` — regex strings bracketing the chart
- `n_rows`, `n_cols` — canonical chart shape
- `field_template` — Python format string producing field IDs
  (e.g. `"1d_4_{row}_{col}"`)
- `column_suffixes` — optional suffix list for multi-column charts

A 17-row single-column chart (`1C-1`) and a 3-row two-column chart
(`1D-4`) are now one function call each. This is the kind of refactor
that should happen *after* the first worked example, not before — we
only knew what the generic function needed to parameterize once we had
the concrete 1B-1 version working.

## A numeric variable — 1D-2

`1D-2` is interesting because it mixes conventions. Sub-questions 1 and
2 are integers (project counts); sub-question 3 is a percentage. Coders
entered the percentage inconsistently: some as `100%`, some as `100`,
some as `1.0` (treating it as a fraction). The extractor emits a
normalized float (fraction in [0, 1]) and preserves the raw string in
`raw_text`, and the diff runner's `B_percent` comparator tolerates any
of the three formats. This is a small but representative example of how
"unit normalization before comparison" is load-bearing.

## Results

| Iteration | Extractor | Variables covered | Comparisons | Weighted | A-class | Diffs | Residual category |
|---|---|---|---|---|---|---|---|
| 1 | v0.1 | 104 | 520 | 99.23% | 99.80% | 4 | 1× E1 + 3× E3 |
| 2 | v0.2 | 104 | 520 | 99.42% | 99.80% | 3 | 3× E3 only |
| 3 | **v0.3** | **143** | **715** | **99.30%** | **99.56%** | **5** | **5× E3 only** |

Weighted accuracy dipped slightly from 99.42% → 99.30% because the
denominator grew (more comparisons) and two new manual errors surfaced
on NY-600. But the composition of residuals is the important number:
zero E1 / E2 errors again.

## The two new manual errors we surfaced

`NY-600` `1c_1_6` (Housing and services funded through State
Government): manual says `No`, PDF clearly says `Yes`.

`NY-600` `1c_1_8` (Housing and services funded through U.S. Department
of Justice): manual says `Yes`, PDF clearly says `No`.

Both are on the same page of the same CoC's application. This is a
pattern worth flagging for the ground-truth audit: when a single CoC
produces multiple errors, check whether the coder was tired, the row
numbering was misread, or a spreadsheet cut-and-paste went sideways.

## Cumulative E3 findings

After iteration 3, the pipeline has surfaced **five** clearly
documentable manual errors across five pilot CoCs (a ~0.7% rate on the
covered surface). This is a small but non-trivial finding for the
broader ground-truth audit — it suggests that a 20-CoC × full-schema
audit (Task #2) could reasonably expect to identify 30–60 manual
corrections.

## Next

- Continue extending the extractor to cover the rest of 1C (1C-4 family,
  1C-5 DV/SA, 1C-7 PHA) and 1D (1D-5 through 1D-11).
- Add the narrative Stage-2 extraction for `1d_2a`, `1d_4_*` rationale
  text, and the criminalization-adjacent free-text fields — using Claude
  with the verbatim-quote requirement described in [[02-methodology-design]].
- Add the DOCX adapter so CA-521 and the seven other DOCX-only CoCs can
  be included in subsequent iterations.
