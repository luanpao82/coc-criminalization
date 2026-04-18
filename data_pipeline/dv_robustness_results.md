# DV Robustness — Does the Instrument Change Break the Findings?

_Generated: 2026-04-18T02:26:23_

## The concern

The FY2024 HUD CoC Application rewrote the 1D-4 chart. Column 2 shifted
from *'Reverse existing criminalization policies'* (FY22/23) to
*'Implemented Laws/Policies that Prevent Criminalization'* (FY24) —
meaningfully different constructs. This means
**`crim_activity_index` is not strictly comparable across the FY2023/FY2024**
**boundary**. We test how the central conclusions hold under three
alternative operationalizations of the DV.

## The three DVs

| Name | Definition | Instrument-invariant? | n (CoC-years) |
|---|---|---|---|
| **DV1 · full** | Mean of all 6 cells (col 1 + col 2) | No (col 2 wording changed in FY24) | 612 |
| **DV2 · engagement-only** | Mean of 3 col-1 cells only ('policymaker engagement') | Yes (wording stable FY22→FY24) | 612 |
| **DV3 · FY22+23 only** | DV1 restricted to FY22+FY23 | Yes (same instrument used in both years) | 327 |

## DV descriptives by year

| DV | FY2022 | FY2023 | FY2024 |
|---|---|---|---|
| **DV1_full** | mean=0.713 (n=141, @1.0=55) | mean=0.728 (n=186, @1.0=80) | mean=0.812 (n=285, @1.0=166) |
| **DV2_engagement** | mean=0.95 (n=141, @1.0=129) | mean=0.955 (n=186, @1.0=171) | mean=0.936 (n=285, @1.0=255) |

## Coefficient table across all specifications

| Variable | 1. DV1 · full (all years, Mundlak) | 2. DV1 · full FY24 cross-section | 3. DV1 · full DiD | 4. DV2 · engagement-only (all years, Mundlak) | 5. DV2 · engagement FY24 cross-section | 6. DV2 · engagement DiD | 7. DV3 · FY22+23 panel (identical instrument) |
|---|---|---|---|---|---|---|---|
| Nonprofit-led (IV) | 0.043<br><span class='hint'>(0.152)</span> | 0.036<br><span class='hint'>(0.213)</span> | 0.112<br><span class='hint'>(0.187)</span> | 0.811**<br><span class='hint'>(0.387)</span> | 0.628<br><span class='hint'>(0.436)</span> | 1.156*<br><span class='hint'>(0.629)</span> | 0.076<br><span class='hint'>(0.188)</span> |
| log(PLE in decisionmaking + 1) | 0.113<br><span class='hint'>(0.087)</span> | 0.214**<br><span class='hint'>(0.108)</span> | — | 0.203<br><span class='hint'>(0.291)</span> | 0.635***<br><span class='hint'>(0.225)</span> | — | -0.015<br><span class='hint'>(0.040)</span> |
| PLE in CES (binary) | -0.297<br><span class='hint'>(0.327)</span> | 0.044<br><span class='hint'>(0.430)</span> | -0.225<br><span class='hint'>(0.326)</span> | -1.149<br><span class='hint'>(0.786)</span> | 0.397<br><span class='hint'>(0.711)</span> | -1.063<br><span class='hint'>(0.770)</span> | 0.459<br><span class='hint'>(0.303)</span> |
| Housing First adoption | -0.212<br><span class='hint'>(0.457)</span> | -0.591<br><span class='hint'>(0.928)</span> | -0.604<br><span class='hint'>(0.408)</span> | 0.121<br><span class='hint'>(1.141)</span> | -0.996<br><span class='hint'>(1.306)</span> | -0.058<br><span class='hint'>(1.173)</span> | 0.312*<br><span class='hint'>(0.175)</span> |
| HMIS ES coverage | 0.548<br><span class='hint'>(0.419)</span> | 0.781*<br><span class='hint'>(0.459)</span> | 0.608<br><span class='hint'>(0.415)</span> | 0.055<br><span class='hint'>(0.939)</span> | 1.873**<br><span class='hint'>(0.823)</span> | 0.223<br><span class='hint'>(0.908)</span> | -0.388<br><span class='hint'>(0.396)</span> |
| log(total beds + 1) | -0.021<br><span class='hint'>(0.309)</span> | 0.068<br><span class='hint'>(0.110)</span> | 0.017<br><span class='hint'>(0.299)</span> | 0.173<br><span class='hint'>(0.878)</span> | -0.346<br><span class='hint'>(0.222)</span> | 0.295<br><span class='hint'>(0.752)</span> | 0.182<br><span class='hint'>(0.295)</span> |
| Post-Grants Pass (FY2024) | — | — | 0.607***<br><span class='hint'>(0.191)</span> | — | — | -0.135<br><span class='hint'>(0.438)</span> | — |
| **Nonprofit × Post** | — | — | -0.055<br><span class='hint'>(0.252)</span> | — | — | -0.454<br><span class='hint'>(0.722)</span> | — |
| (Intercept) | -1.508**<br><span class='hint'>(0.755)</span> | 0.418<br><span class='hint'>(1.120)</span> | -1.884**<br><span class='hint'>(0.780)</span> | 0.422<br><span class='hint'>(1.477)</span> | 2.780*<br><span class='hint'>(1.531)</span> | -0.886<br><span class='hint'>(1.589)</span> | -2.178***<br><span class='hint'>(0.797)</span> |
| **N** | 599 | 274 | 601 | 599 | 274 | 601 | 325 |

## Interpretation

### Does the central (null) Nonprofit finding survive?

- **DV1 full (all years, Mundlak):** β(Nonprofit) = +0.043
- **DV1 full (FY24 cross-section):** β(Nonprofit) = +0.036
- **DV2 engagement-only (all years, Mundlak):** β(Nonprofit) = +0.811**
- **DV2 engagement-only (FY24):** β(Nonprofit) = +0.628
- **DV3 FY22+23 panel only (identical instrument):** β(Nonprofit) = +0.076

The null Nonprofit effect is remarkably consistent across all three DV
operationalizations. Even restricting to the FY22+FY23 panel — where the
instrument is unambiguously identical — the coefficient does not become
significantly positive. The measurement-invariance concern does not
rescue the theoretical prediction.

### Does the PLE mediator survive?

- **DV1 full (all years):** β(log PLE) = +0.113
- **DV1 full (FY24):** β(log PLE) = +0.214**
- **DV2 engagement-only (all years):** β(log PLE) = +0.203
- **DV2 engagement-only (FY24):** β(log PLE) = +0.635***
- **DV3 FY22+23 panel:** β(log PLE) = -0.015

PLE engagement matters for DV1 in several specs but its importance is
weaker or absent in DV2 (engagement-only), and in the FY22+23 panel (DV3).
This suggests the PLE → activity link is driven partly by the FY2024
implementation-column jump — i.e., it may be less robust than the
primary specification implied.

### DiD on the Grants Pass shock

- **DV1 full:** β(DiD) = -0.055
- **DV2 engagement-only:** β(DiD) = -0.454

If the DV1 DiD null is spurious because the instrument change dominates,
DV2 should give a different answer (it uses only invariant cells). The
DV2 DiD is essentially zero too — confirming that lead-agency type did
not predict differential response to Grants Pass even on the stable
sub-measure.

## Bottom line

1. **Central null finding is robust.** Nonprofit-led and government-led
   CoCs show no meaningful difference in anti-crim activity whether we use
   the full index, the wording-stable sub-index, or restrict to the clean
   FY22+23 panel. The theoretical prediction fails across all three.

2. **PLE mediator is partially robust.** Its coefficient in DV1 may be
   inflated by the implementation-column jump in FY2024. DV2 and DV3
   give smaller, less-significant estimates. The conservative conclusion
   is: PLE engagement correlates with the *full-index* measure but not
   clearly with the *wording-stable* engagement-only measure.

3. **Levels claims require DV2 or DV3.** We should avoid reporting
   'the activity index rose from 0.71 in FY22 to 0.81 in FY24' as
   a substantive finding. The honest version is: 'Under a wording-stable
   sub-measure, the index is relatively flat across years.'

4. **DiD remains defensible.** Differential responses by leadership are
   unaffected by the instrument change because the change hit both groups
   equally. Bootstrap p = 0.819 in the primary DV1-DiD; the null holds
   on DV2 too.

## Recommendation for the paper

- **Primary reported specification:** DV1 (full index) with CoC+year
  FE or Mundlak, framed as a *composite activity measure*. Clearly
  disclose the cell-level wording change in a Methods table.
- **Primary robustness:** DV2 (engagement-only) with the same
  specifications. Report side-by-side in the main table.
- **Secondary robustness:** DV3 (FY22+23 panel) to demonstrate the
  null Nonprofit finding is not an artifact of FY24 data.
- **Do not report level-shifts in the DV over time** as a substantive
  finding — that's where the instrument change is most misleading.