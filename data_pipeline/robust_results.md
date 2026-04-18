# Robust Re-Analysis — Improvements & Final Estimates

_Generated: 2026-04-18T01:55:24_

## What changed from the first-pass analysis

| Issue (v1) | Fix (v2) |
|---|---|
| IV coverage 68% (104 unresolved) | Manual classifier overrides for all 104 — **IV coverage now 99%** (320 of 321) |
| `1b_1_6_voted` caused near-perfect separation | Dropped; `1b_1_6_ces` retained as binary mediator |
| OLS on bounded DV | **Fractional logit (Papke-Wooldridge)** as primary estimator |
| IV absorbed by CoC fixed effects | **Mundlak correction** — include CoC means of time-varying covariates; recovers IV identifiability |
| NYC bed-count outlier | Winsorized at 99th percentile before log1p |
| Conservative clustered SEs on small N | **Wild-cluster bootstrap** for DiD coefficient |
| No heterogeneity | Nonprofit × HF and Nonprofit × HMIS interactions |
| Unbalanced panel unreliable | **Balanced 3-year panel** robustness model |

## Sample

- Full sample: **651** CoC-year records.
- With IV coded: **646** CoC-years.
- Balanced 3-year panel: **125 CoCs × 3 years = 375** obs.
- Nonprofit-led share: 332 / 646 = 51.4%

## Parallel-trends check (updated sample)

| Year | Government | Nonprofit | Δ (Nonprofit − Gov) |
|---|---|---|---|
| 2022 | 0.724 | 0.703 | -0.021 |
| 2023 | 0.726 | 0.730 | +0.004 |
| 2024 | 0.808 | 0.816 | +0.008 |

- FY22 → FY23 pre-trend: government +0.002, nonprofit +0.027 — parallel.
- FY23 → FY24 post-shock: government +0.082, nonprofit +0.086.

## Coefficient table (all specifications)

| Variable | R1·frac-logit | R2·frac+Mundlak | R3·FY24 frac | R4·OLS-TWFE | R5·balanced panel | R6·×HF | R7·×HMIS | D1·DiD OLS-FE | D2·DiD frac+Mundlak |
|---|---|---|---|---|---|---|---|---|---|
| Nonprofit-led (IV) | 0.052<br><span class='hint'>(0.152)</span> | 0.045<br><span class='hint'>(0.152)</span> | 0.036<br><span class='hint'>(0.213)</span> | — | 0.205<br><span class='hint'>(0.205)</span> | -0.070<br><span class='hint'>(0.748)</span> | 0.286<br><span class='hint'>(0.511)</span> | — | 0.115<br><span class='hint'>(0.187)</span> |
| log(PLE in decisionmaking + 1) | 0.253***<br><span class='hint'>(0.071)</span> | 0.114<br><span class='hint'>(0.087)</span> | 0.214**<br><span class='hint'>(0.108)</span> | 0.015<br><span class='hint'>(0.021)</span> | 0.075<br><span class='hint'>(0.096)</span> | 0.253***<br><span class='hint'>(0.071)</span> | 0.253***<br><span class='hint'>(0.071)</span> | — | — |
| PLE in CES (binary) | -0.058<br><span class='hint'>(0.191)</span> | -0.313<br><span class='hint'>(0.309)</span> | 0.044<br><span class='hint'>(0.430)</span> | -0.059<br><span class='hint'>(0.084)</span> | 0.079<br><span class='hint'>(0.280)</span> | -0.057<br><span class='hint'>(0.192)</span> | -0.060<br><span class='hint'>(0.191)</span> | -0.058<br><span class='hint'>(0.057)</span> | -0.341<br><span class='hint'>(0.314)</span> |
| Housing First adoption | 0.532<br><span class='hint'>(0.399)</span> | -0.228<br><span class='hint'>(0.459)</span> | -0.591<br><span class='hint'>(0.928)</span> | -0.090<br><span class='hint'>(0.176)</span> | -0.061<br><span class='hint'>(0.471)</span> | 0.475<br><span class='hint'>(0.713)</span> | 0.534<br><span class='hint'>(0.402)</span> | -0.140<br><span class='hint'>(0.088)</span> | -0.637<br><span class='hint'>(0.412)</span> |
| HMIS ES coverage | 0.548**<br><span class='hint'>(0.274)</span> | 0.547<br><span class='hint'>(0.419)</span> | 0.781*<br><span class='hint'>(0.459)</span> | 0.116<br><span class='hint'>(0.121)</span> | 0.600<br><span class='hint'>(0.419)</span> | 0.547**<br><span class='hint'>(0.274)</span> | 0.726<br><span class='hint'>(0.491)</span> | 0.121<br><span class='hint'>(0.082)</span> | 0.611<br><span class='hint'>(0.411)</span> |
| log(total beds + 1, 99%-winsorized) | 0.116<br><span class='hint'>(0.076)</span> | -0.018<br><span class='hint'>(0.308)</span> | 0.068<br><span class='hint'>(0.110)</span> | -0.009<br><span class='hint'>(0.080)</span> | -0.045<br><span class='hint'>(0.446)</span> | 0.116<br><span class='hint'>(0.076)</span> | 0.119<br><span class='hint'>(0.076)</span> | 0.005<br><span class='hint'>(0.053)</span> | 0.031<br><span class='hint'>(0.296)</span> |
| Nonprofit × Housing First | — | — | — | — | — | 0.126<br><span class='hint'>(0.757)</span> | — | — | — |
| Nonprofit × HMIS coverage | — | — | — | — | — | — | -0.275<br><span class='hint'>(0.584)</span> | — | — |
| CoC-mean of log(PLE) [Mundlak] | — | 0.169<br><span class='hint'>(0.111)</span> | — | — | 0.363***<br><span class='hint'>(0.128)</span> | — | — | — | — |
| CoC-mean of PLE CES [Mundlak] | — | 0.288<br><span class='hint'>(0.389)</span> | — | — | -0.352<br><span class='hint'>(0.420)</span> | — | — | — | 0.432<br><span class='hint'>(0.394)</span> |
| CoC-mean of HF % [Mundlak] | — | 1.012<br><span class='hint'>(0.638)</span> | — | — | 1.154*<br><span class='hint'>(0.692)</span> | — | — | — | 1.405**<br><span class='hint'>(0.577)</span> |
| CoC-mean of HMIS cov [Mundlak] | — | 0.001<br><span class='hint'>(0.582)</span> | — | — | 0.073<br><span class='hint'>(0.674)</span> | — | — | — | 0.010<br><span class='hint'>(0.572)</span> |
| CoC-mean of log beds [Mundlak] | — | 0.109<br><span class='hint'>(0.318)</span> | — | — | 0.055<br><span class='hint'>(0.461)</span> | — | — | — | 0.168<br><span class='hint'>(0.306)</span> |
| Post-Grants Pass (FY2024) | — | — | — | — | — | — | — | 0.094***<br><span class='hint'>(0.035)</span> | 0.615***<br><span class='hint'>(0.191)</span> |
| **Nonprofit × Post** ← β_DiD | — | — | — | — | — | — | — | 0.007<br><span class='hint'>(0.045)</span> | -0.063<br><span class='hint'>(0.253)</span> |
| (Intercept) | -1.347**<br><span class='hint'>(0.647)</span> | -1.521**<br><span class='hint'>(0.756)</span> | 0.418<br><span class='hint'>(1.120)</span> | 0.839<br><span class='hint'>(0.614)</span> | -1.615*<br><span class='hint'>(0.853)</span> | -1.294<br><span class='hint'>(0.868)</span> | -1.528**<br><span class='hint'>(0.744)</span> | 0.770*<br><span class='hint'>(0.405)</span> | -1.901**<br><span class='hint'>(0.783)</span> |
| **N obs** | 599 | 599 | 274 | 599 | 345 | 599 | 599 | 601 | 601 |

Cluster-robust SEs at the CoC level in parentheses · `*** p<0.01, ** p<0.05, * p<0.10`.

## Primary estimate — Nonprofit effect

- R1 (pooled frac-logit, no FE): β = 0.052, SE 0.152, p = 0.730
- R2 (+ Mundlak, full sample): β = 0.045, SE 0.152, p = 0.767
- R3 (FY24 cross-section frac-logit): β = 0.036, SE 0.213, p = 0.864
- R5 (balanced panel + Mundlak): β = 0.205, SE 0.205, p = 0.318

### PLE mediator (log count)
- R1: β = 0.253***, SE 0.071, p = 0.000
- R2 (within-CoC variation): β = 0.114, SE 0.087, p = 0.191
- R3 (FY24 only): β = 0.214**, SE 0.108, p = 0.047
- R5 (balanced): β = 0.075, SE 0.096, p = 0.434

### Housing First control
- R1: β = 0.532, SE 0.399, p = 0.183
- R2: β = -0.228, SE 0.459, p = 0.620
- R3 (FY24): β = -0.591, SE 0.928, p = 0.524

### Heterogeneity
- Nonprofit × Housing First (R6): β = 0.126, SE 0.757, p = 0.868
- Nonprofit × HMIS coverage (R7): β = -0.275, SE 0.584, p = 0.637

## DiD estimates (Grants Pass shock)

- D1 (OLS + CoC FE): β = 0.007, SE 0.045, p = 0.870
- D2 (frac-logit + Mundlak): β = -0.063, SE 0.253, p = 0.802
- **Wild-cluster bootstrap p-value for β_DiD: 0.819** (based on 999 Rademacher replicates; observed |t| = 0.248)

## Bottom line

- **Nonprofit-led effect:** in the FY2024 cross-section fractional logit, β = 0.036 (p = 0.864). The direction is positive relative to government-led CoCs.
- **PLE in decisionmaking (log count):** Mundlak frac-logit β = 0.114 (p = 0.191). A 1-unit increase on the log scale (~2.7× more PLE) is associated with a 0.114 logit-unit change in `crim_activity_index`.
- **DiD around Grants Pass:** β = -0.063 (cluster p = 0.802; wild-cluster bootstrap p = 0.819). Nonprofit-led CoCs did not differentially expand anti-criminalization activity after Grants Pass.

## Remaining caveats

1. **Time-invariant IV.** Mundlak recovers the main effect but assumes within-
   vs between-CoC exogeneity decomposes cleanly. An instrumental variable    (e.g., historical lead-agency mandates) would be stronger if available.
2. **Small DiD sample.** Only 3 years; event study has a single treated period.
3. **Self-report.** DV is CoC's self-reported activity; external behavioral DV    (NLHR ordinances, FBI UCR) remains the strongest robustness next step.
4. **Instrument change.** FY2024 HUD 1D-4 redesign overlaps with Grants Pass    ruling; bootstrap DiD is conservative but cannot fully decompose the two shocks.