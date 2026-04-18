# Blue-State vs Red-State DiD (Grants Pass)

_Generated: 2026-04-18T02:39:26_

## Design

Alternative treatment definition: **political environment of the CoC's state**
rather than lead-agency type. CoCs in states that voted Biden in the 2020
presidential election (Electoral College) are treated; Trump-voting states
are the control. Territories (PR/VI/GU) are excluded from this DiD.

- **Treatment (blue):** 416 CoC-years across 26 states
- **Control (red):** 227 CoC-years across 25 states
- **Pre period:** FY2022, FY2023 (before June 2024 ruling)
- **Post period:** FY2024 (applications submitted Oct 30, 2024)

### Theoretical expectation

Blue-state CoCs face stronger progressive pressure against
criminalization, so should differentially expand reported anti-crim
activity in FY2024 (β_DiD > 0). Alternative null: blue-state CoCs were
already high pre-Grants Pass, leaving little room to respond — or the
ruling uniformly affected reporting across political contexts.

### Parallel-trends check

| Year | Red | Blue | Δ (Blue − Red) |
|---|---|---|---|
| 2022 | 0.734 | 0.701 | -0.033 |
| 2023 | 0.769 | 0.709 | -0.060 |
| 2024 | 0.782 | 0.826 | +0.044 |

FY22→FY23 pre-trend: red +0.035, blue +0.008.
FY23→FY24 post-shock: red +0.013, blue +0.117.

## Coefficient table

| Variable | B1·DV1 OLS+CoC FE | B2·DV1 OLS+CoC+Year FE | B3·DV1 frac-logit + Mundlak | B4·DV1 event study (pre-trend placebo) | B5·DV2 engagement-only | B6·DV3 binary (implemented) |
|---|---|---|---|---|---|---|
| Blue state (treatment) | — | — | -0.312<br><span class='hint'>(0.207)</span> | -0.227<br><span class='hint'>(0.241)</span> | -0.585<br><span class='hint'>(0.692)</span> | -0.489<br><span class='hint'>(0.315)</span> |
| FY2023 indicator | — | — | — | +0.216<br><span class='hint'>(0.158)</span> | — | — |
| Post-Grants Pass (FY2024) | +0.058*<br><span class='hint'>(0.034)</span> | — | +0.210<br><span class='hint'>(0.203)</span> | +0.334<br><span class='hint'>(0.223)</span> | -0.619<br><span class='hint'>(0.488)</span> | +0.703**<br><span class='hint'>(0.326)</span> |
| Blue × FY2023 (placebo) | — | — | — | -0.146<br><span class='hint'>(0.204)</span> | — | — |
| <strong>Blue × Post ← β_DiD</strong> | +0.057<br><span class='hint'>(0.046)</span> | +0.056<br><span class='hint'>(0.067)</span> | +0.548**<br><span class='hint'>(0.262)</span> | +0.462<br><span class='hint'>(0.292)</span> | +0.427<br><span class='hint'>(0.668)</span> | +0.886**<br><span class='hint'>(0.433)</span> |
| Housing First adoption | -0.133<br><span class='hint'>(0.089)</span> | -0.136<br><span class='hint'>(0.126)</span> | -0.492<br><span class='hint'>(0.407)</span> | -0.534<br><span class='hint'>(0.392)</span> | +0.074<br><span class='hint'>(1.118)</span> | -0.579<br><span class='hint'>(0.750)</span> |
| HMIS ES coverage | +0.123<br><span class='hint'>(0.081)</span> | +0.122<br><span class='hint'>(0.119)</span> | +0.602<br><span class='hint'>(0.406)</span> | +0.585<br><span class='hint'>(0.415)</span> | +0.123<br><span class='hint'>(0.777)</span> | +0.686<br><span class='hint'>(0.646)</span> |
| log(total beds + 1) | -0.014<br><span class='hint'>(0.052)</span> | -0.013<br><span class='hint'>(0.077)</span> | -0.118<br><span class='hint'>(0.286)</span> | -0.110<br><span class='hint'>(0.290)</span> | +0.252<br><span class='hint'>(0.768)</span> | -0.177<br><span class='hint'>(0.523)</span> |
| PLE in CES (binary) | -0.043<br><span class='hint'>(0.060)</span> | -0.044<br><span class='hint'>(0.087)</span> | -0.191<br><span class='hint'>(0.344)</span> | -0.183<br><span class='hint'>(0.351)</span> | -1.407<br><span class='hint'>(0.986)</span> | -0.119<br><span class='hint'>(0.531)</span> |
| (Intercept) | +0.883**<br><span class='hint'>(0.397)</span> | +0.910<br><span class='hint'>(0.575)</span> | -1.674**<br><span class='hint'>(0.768)</span> | -1.793**<br><span class='hint'>(0.777)</span> | +0.431<br><span class='hint'>(1.506)</span> | -3.576***<br><span class='hint'>(1.098)</span> |
| **N** | 595 | 595 | 595 | 595 | 595 | 595 |

Cluster-robust SEs at the CoC level in parentheses · `*** p<0.01, ** p<0.05, * p<0.10`.

## Key estimates

- **Primary β_DiD (B3 DV1 frac-logit + Mundlak):** β = 0.548** (SE 0.262, p = 0.036)
- **Wild-cluster bootstrap p:** 0.036 (based on 999 Rademacher replicates)
- **Pre-trend placebo (B4):** β = -0.146 (SE 0.204, p = 0.474)
- **DV2 engagement-only (B5):** β = 0.427 (SE 0.668, p = 0.523)
- **DV3 implemented-binary (B6):** β = 0.886** (SE 0.433, p = 0.041)

## Interpretation

- Blue-state CoCs showed a 0.548 logit-point larger differential change from pre to post than red-state CoCs; this is statistically significant at p < .05.
- The FY2023 placebo is not significant (p ≈ 0.47); parallel-trends assumption is plausible.

## Caveats

1. **State-level treatment is coarse.** A CoC in a blue-state red county
   (e.g., rural Pennsylvania) is treated identically to a CoC in a blue-state
   blue county (e.g., Philadelphia). Local political environment likely matters
   more than state-level. A future version could use county partisan vote share.
2. **2020 classification is static.** Some 2020 blue states (Georgia, Arizona)
   are highly competitive; some 2020 red states (North Carolina) nearly flipped.
3. **Selection into lead-agency.** Blue states may have more nonprofit-led CoCs.
   The blue-state effect and the nonprofit effect could be correlated — a joint
   specification would disentangle them (add both variables + interaction).
4. **Grants Pass exposure.** The ruling affects all states equally, but local
   political will to enact or resist anti-camping ordinances varies. The DiD
   captures *reporting differential*, not behavioral differential.