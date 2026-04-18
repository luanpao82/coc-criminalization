# Panel Regression Results — Research Model v1

_Generated: 2026-04-18T01:39:23_

## Research model

DV = `crim_activity_index` (fraction of 1D-4 cells = Yes, bounded [0, 1]).

Four specifications:
- **M1** — OLS with two-way (CoC + year) fixed effects; direct IV effect only, no mediators.
- **M2** — Adds the PLE-engagement mediator set (log of decisionmaking PLE counts + two binary breadth indicators).
- **M3** — FY2024 cross-section (no CoC FE, HC3 SEs); exploits richer FY2024 variables.
- **M4** — Pooled fractional logit with CoC-clustered SEs; handles censoring at 0 and 1 in the DV.

Significance: `*** p<0.01, ** p<0.05, * p<0.10` · cluster-robust SEs at the CoC level.

## Coefficient table

| Variable | M1 (OLS-FE, direct) | M2 (OLS-FE + mediators) | M3 (FY24 cross-section) | M4 (Frac. logit, pooled) |
|---|---|---|---|---|
| Nonprofit-led CoC (IV) | — | — | -0.044<br><span class='hint'>(0.038)</span> | -0.249<br><span class='hint'>(0.202)</span> |
| log(PLE in decisionmaking + 1) | — | 0.000<br><span class='hint'>(0.024)</span> | 0.010<br><span class='hint'>(0.017)</span> | 0.180**<br><span class='hint'>(0.078)</span> |
| PLE voted in CoC (binary) | — | — | 0.772<br><span class='hint'>(2.591)</span> | 21.563***<br><span class='hint'>(0.262)</span> |
| PLE in CES (binary) | — | -0.003<br><span class='hint'>(0.091)</span> | 0.035<br><span class='hint'>(0.078)</span> | 0.133<br><span class='hint'>(0.226)</span> |
| Housing First adoption (share) | -0.161<br><span class='hint'>(0.150)</span> | -0.080<br><span class='hint'>(0.247)</span> | -0.157***<br><span class='hint'>(0.058)</span> | 0.189<br><span class='hint'>(0.410)</span> |
| HMIS ES coverage (share) | 0.089<br><span class='hint'>(0.118)</span> | 0.084<br><span class='hint'>(0.121)</span> | 0.112<br><span class='hint'>(0.111)</span> | 0.493<br><span class='hint'>(0.317)</span> |
| log(total beds + 1) | -0.040<br><span class='hint'>(0.079)</span> | -0.044<br><span class='hint'>(0.086)</span> | 0.006<br><span class='hint'>(0.017)</span> | 0.100<br><span class='hint'>(0.093)</span> |
| (Intercept) | 1.154*<br><span class='hint'>(0.617)</span> | 1.110*<br><span class='hint'>(0.668)</span> | 0.058<br><span class='hint'>(2.594)</span> | -22.144***<br><span class='hint'>(0.713)</span> |
| **N (obs)** | 408 | 406 | 187 | 406 |
| **R² (within / pseudo)** | 0.019 | 0.008 | 0.090 | 0.099 |

## Interpretation highlights

### The Nonprofit-led effect
- M1 (TWFE, direct): β = (absorbed by CoC FE)
- M2 (TWFE, with mediators): β = (absorbed by CoC FE)
- M3 (FY24 cross-section): β = -0.044
- M4 (pooled frac. logit): β = -0.249

With CoC fixed effects absorbing time-invariant CoC characteristics (M1, M2, M4),
the nonprofit-led dummy is identified only off CoCs that change leadership during the
panel window — of which there are very few. The **FY2024 cross-section (M3)** is the
cleaner identification for the Nonprofit-vs-government question.

### PLE engagement (mediator path M → Y)
- log(PLE decisionmaking count): M2=0.000, M3=0.010
- PLE voted (binary): M2=(absorbed by CoC FE)
- PLE in CES (binary): M2=-0.003

### Controls
- Housing First adoption: M2=-0.080
- HMIS ES coverage: M2=0.084
- log(total beds): M2=-0.044

## Caveats

1. **IV coverage.** Rule-based coding of `1a_2` classified ~217 of 321 CoCs
   (~68%). Unclassified CoCs drop from IV models; manual refinement of the
   classifier would expand the sample.
2. **DV instrument change.** M1–M3 use the harmonized `crim_activity_index`; M4
   uses it with fractional-logit corrections for 0/1 censoring. See
   `dv_harmonization_results.md`.
3. **Absorbed variation.** TWFE absorbs ~all Nonprofit_led variation for
   CoCs stable across years. Interpret M3 (cross-section) alongside M1/M2.