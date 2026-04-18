# Difference-in-Differences — Nonprofit vs. Government-Led CoCs around Grants Pass

_Generated: 2026-04-18T01:46:03_

## Design

On **June 28, 2024**, the U.S. Supreme Court decided *City of Grants Pass v. Johnson* (603 U.S. ___),
holding that enforcing public-camping ordinances against people experiencing homelessness does not
violate the Eighth Amendment's prohibition on cruel and unusual punishment. The ruling opened the door
to broader municipal criminalization of homelessness. FY2024 CoC Applications were submitted by the
October 30, 2024 deadline — four months after the ruling.

This design tests whether **nonprofit-led CoCs differentially expanded their reported
anti-criminalization activity in FY2024 relative to government-led CoCs**, consistent with the
theoretical prediction that nonprofit governance is more responsive to rights-based concerns.

- **Treatment group (T=1):** Nonprofit-led CoCs (n = 267 CoC-years)
- **Control group (T=0):** Government-led CoCs — city / county / state / regional (n = 169 CoC-years)
- **Pre period:** FY2022, FY2023 (applications submitted before June 2024)
- **Post period:** FY2024 (applications submitted after Grants Pass ruling)
- **DV:** `crim_activity_index` (fraction of 1D-4 cells = Yes)

## Parallel-trends check

| Year | Government | Nonprofit | Δ (Nonprofit − Gov) |
|---|---|---|---|
| 2022 | 0.778 | 0.709 | -0.069 |
| 2023 | 0.773 | 0.735 | -0.038 |
| 2024 | 0.868 | 0.815 | -0.053 |

Between FY2022 and FY2023 (both pre-period), the group difference was small and stable — supporting the parallel-trends assumption. The FY2023 → FY2024 change is where the DiD estimand lives.

## Coefficient table

| Variable | D1 (DiD, CoC FE) | D2 (DiD, CoC+Year FE) | D3 (Event study) | D4 (Binary DV) | D5 (+controls) |
|---|---|---|---|---|---|
| Nonprofit-led (treatment) | — | — | -0.069<br><span class='hint'>(0.053)</span> | — | — |
| FY2023 indicator (pre, placebo) | — | — | -0.005<br><span class='hint'>(0.040)</span> | — | — |
| Post-Grants Pass (FY2024) | 0.062<br><span class='hint'>(0.044)</span> | — | 0.090*<br><span class='hint'>(0.049)</span> | 0.208**<br><span class='hint'>(0.081)</span> | 0.069<br><span class='hint'>(0.044)</span> |
| Nonprofit × FY2023 (placebo DiD) | — | — | 0.031<br><span class='hint'>(0.049)</span> | — | — |
| Nonprofit × Post  ← β_DiD | 0.050<br><span class='hint'>(0.055)</span> | 0.049<br><span class='hint'>(0.079)</span> | 0.016<br><span class='hint'>(0.061)</span> | 0.063<br><span class='hint'>(0.103)</span> | 0.029<br><span class='hint'>(0.056)</span> |
| Housing First adoption | — | — | — | — | -0.147<br><span class='hint'>(0.109)</span> |
| HMIS ES coverage | — | — | — | — | 0.086<br><span class='hint'>(0.081)</span> |
| log(total beds + 1) | — | — | — | — | -0.038<br><span class='hint'>(0.054)</span> |
| (Intercept) | 0.742***<br><span class='hint'>(0.012)</span> | 0.771***<br><span class='hint'>(0.023)</span> | 0.778***<br><span class='hint'>(0.044)</span> | 0.573***<br><span class='hint'>(0.023)</span> | 1.088**<br><span class='hint'>(0.423)</span> |
| **N obs** | 413 | 413 | 413 | 413 | 408 |

Cluster-robust SEs at the CoC level in parentheses · `*** p<0.01, ** p<0.05, * p<0.10`.

## Interpretation

### β_DiD (Nonprofit × Post)
- D1 (CoC FE): β = 0.050, SE 0.055, p = 0.364
- D2 (CoC + Year FE): β = 0.049, SE 0.079, p = 0.539
- D3 (pooled, event study): β = 0.016, SE 0.061, p = 0.791
- D4 (binary DV): β = 0.063, SE 0.103, p = 0.541
- D5 (+ controls): β = 0.029, SE 0.056, p = 0.604

### Pre-trend placebo (D3)
- `Nonprofit × FY2023`: β = 0.031, SE 0.049, p = 0.534

A non-significant placebo coefficient on FY2023 is consistent with parallel pre-trends;
a significant one would suggest nonprofit and government CoCs were already diverging before
Grants Pass and that the FY2024 DiD estimate is contaminated by pre-existing trends.

## Takeaways

- Nonprofit-led CoCs saw a 0.050-point larger change in `crim_activity_index` from pre to post compared to government-led CoCs; this difference is not statistically significant.
- The FY2023 placebo interaction is not significant (p ≈ 0.53); parallel-trends assumption is plausible.

## Caveats

1. **IV classification limits sample.** ~217 of 321 CoCs are cleanly coded (68%).
   Unresolved `other` CoCs drop from all DiD specifications.
2. **Only three time periods.** FY2022, FY2023, FY2024. Event-study leads/lags are limited.
3. **The 'shock' is one of multiple concurrent changes.** FY2024 also saw HUD's 1D-4
   instrument redesign — so the Post dummy captures both Grants Pass response *and* the
   instrument change. Year FE (D2) does not fully separate them; consider re-estimating on
   the harmonized `implemented_anticrim_practice` DV (D4) which is less distorted.
4. **SUTVA.** The ruling affected all jurisdictions, not just treated CoCs. We exploit
   differential *response*, not differential *exposure* — an important framing distinction.
5. **Time-invariant IV.** Nonprofit-led status is near-constant within CoC over three years,
   so CoC FE absorbs the main effect; only the interaction (β_DiD) is identified.