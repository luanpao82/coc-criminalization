---
title: Harmonized DV — Empirical Results and Recommendation
project: CoC Criminalization / PLE Engagement (Lee & Kim, UCF)
status: empirical finding (v0.1)
last_updated: 2026-04-18
related:
  - "[[dv_harmonization_strategies]]"
  - "[[main_variables]]"
  - "[[progress/README]]"
---

# Harmonized DV — Empirical Results

Four harmonized DVs were computed across 612 (CoC × year) records
spanning FY2022–FY2024. Their distributions reveal which harmonization
strategy actually works empirically.

## The four candidate DVs

| Variable | Strategy | Definition |
|---|---|---|
| `crim_activity_index` | 1 — composite | Share of 1D-4 cells = Yes (continuous 0–1) |
| `engaged_policymakers_crim` | 2 — common dimension | Any Yes in "policymakers" dimension per year |
| `engaged_law_enforce_crim` | — auxiliary | Any Yes in law-enforcement-relevant rows |
| `implemented_anticrim_practice` | — auxiliary | Any Yes in "implemented / reverse existing" column |

## Summary statistics

| DV | FY2022 mean | FY2023 mean | FY2024 mean | SD (pooled) |
|---|---|---|---|---|
| `crim_activity_index` | 0.713 | 0.728 | 0.812 | ~0.26 |
| `engaged_policymakers_crim` | 0.972 | 0.978 | 0.968 | ~0.17 |
| `engaged_law_enforce_crim` | 0.965 | 0.962 | 0.975 | ~0.18 |
| `implemented_anticrim_practice` | 0.553 | 0.565 | 0.796 | ~0.45 |

## The empirical finding

1. **`engaged_policymakers_crim` has a hard ceiling at 97%.** Nearly every CoC says "Yes, we engaged policymakers on criminalization." This binary has almost no variance, making it **statistically useless as a panel DV** despite being the most defensible harmonization.

2. **`engaged_law_enforce_crim` has the same ceiling at 96%.** Also useless.

3. **`crim_activity_index` is the best candidate.**
   - Continuous 0–1 measure with stable mean (0.71–0.81) across years
   - SD ~0.26 — substantial variance
   - The FY2024 rise (+0.08) is consistent with both substantive change (post-Grants Pass CoCs doing more work) and instrument change (FY2024 items easier to answer Yes).
   - Year fixed effects absorb the instrument-driven component.

4. **`implemented_anticrim_practice` jumped 24 points in FY2024** — almost certainly instrument-driven (FY2024 column renamed from "reverse existing" to "implemented laws/policies"). Use only with year FE; do not interpret the FY2023→FY2024 jump as substantive change.

## Revised recommendation

- **Primary DV:** `crim_activity_index` (continuous, 0–1, panel-safe variance)
- **Secondary / interpretive DV:** `implemented_anticrim_practice` (captures actual policy action, but always paired with year FE)
- **Drop from panel analysis:** `engaged_policymakers_crim`, `engaged_law_enforce_crim` (ceiling effects)

The paper's econometric model in its simplest form:

```
Y_it = β0 + β1 · PLE_engagement_it + β2 · NonprofitLed_i
     + β3 · Controls_it + γ_t (year FE) + α_i (CoC FE) + ε_it
```

where `Y_it = crim_activity_index`. The CoC fixed effects absorb time-invariant CoC characteristics; the year fixed effects absorb the FY2024 instrument change and any common secular trend.

## Sample

| Panel balance | # CoCs |
|---|---|
| Full 3-year panel | **100** |
| 2-year panel | 93 |
| 1-year only | 126 |

For fixed-effects estimation, the balanced 3-year panel (100 × 3 = 300 observations) is the cleanest subsample. The unbalanced panel (612 obs) is usable if the model tolerates missing waves.

## Distribution of `crim_activity_index`

Non-trivial dispersion in all years — not dominated by any single value:

| Bucket | FY2022 | FY2023 | FY2024 |
|---|---|---|---|
| 0.00 (no activity) | 3 | 3 | 6 |
| (0, 0.25] | 2 | 1 | 5 |
| (0.25, 0.50] | 59 | 80 | 53 |
| (0.50, 0.75] | 10 | 11 | 37 |
| (0.75, 1.00) | 12 | 11 | 18 |
| 1.00 (all-Yes) | 55 | 80 | 166 |
| **N** | 141 | 186 | 285 |

The mass at 1.00 and the 0.50 bump (3 of 6 cells = 0.5) are the two modes. A Tobit or fractional-response model may be preferable to OLS to handle the censoring at 0 and 1.

## Files

- `data_pipeline/harmonized_dv.csv` — 612 rows, 4 DVs + cell counts
- `data_pipeline/harmonized_dv.xlsx` — same, Excel format
- `data_pipeline/coc_panel_wide.xlsx` sheet `dv_harmonized` — appended to the panel file

## Next practical step

1. Merge `harmonized_dv.csv` into `coc_panel_wide.xlsx[panel_safe]` on `(coc_id, year)` so analysts have one file with both the panel-safe independent variables and the harmonized DV.
2. Build the two-way fixed-effects regression in R/Stata/Python as a first-pass replication benchmark; iterate from there.
