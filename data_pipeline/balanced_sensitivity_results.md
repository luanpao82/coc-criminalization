# Balanced vs Unbalanced Panel — Sensitivity

_Generated: 2026-04-18T02:55:16_

## Why compare

The unbalanced panel has **651** CoC-year rows across
**325** CoCs, but only **125**
CoCs appear in all three fiscal years. The remaining CoCs contribute
to main effects but add nothing to the within-CoC pre-vs-post
contrast that drives DiD identification. This note re-estimates the
main specifications on the **balanced 3-year panel** (same CoCs each
year) as a sensitivity check.

## Composition differences

| | Unbalanced | Balanced |
|---|---|---|
| CoCs | 325 | 125 |
| Observations | 651 | 375 |
| CoCs in all 3 years | 125 | 125 (by construction) |

## Side-by-side key DiD coefficients

| Specification | Panel | Focal DiD coef | Cluster p | N |
|---|---|---|---|---|
| N1 (Nonprofit × Post) | Unbalanced | -0.055 (SE 0.252) | 0.828 | 601 |
| N1 (Nonprofit × Post) | Balanced   | +0.278 (SE 0.351) | 0.428 | 346 |
| B1 (Blue-state × Post) | Unbalanced | +0.548** (SE 0.262) | 0.036 | 595 |
| B1 (Blue-state × Post) | Balanced   | +0.129 (SE 0.338) | 0.702 | 341 |
| J2 (Joint NP + Biden × Post) | Unbalanced | +1.951* (SE 1.032) | 0.059 | 594 |
| J2 (Joint NP + Biden × Post) | Balanced   | +3.200** (SE 1.370) | 0.020 | 341 |

## Full coefficient table

| Variable | N1 unbal | N1 bal | B1 unbal | B1 bal | J2 unbal | J2 bal |
|---|---|---|---|---|---|---|
| Nonprofit-led (IV) | +0.112<br><span class='hint'>(0.187)</span> | +0.225<br><span class='hint'>(0.231)</span> | — | — | +0.093<br><span class='hint'>(0.203)</span> | +0.181<br><span class='hint'>(0.247)</span> |
| Blue state (IV) | — | — | -0.312<br><span class='hint'>(0.207)</span> | -0.341<br><span class='hint'>(0.252)</span> | — | — |
| County Biden share (centered) | — | — | — | — | -0.137<br><span class='hint'>(0.854)</span> | -0.663<br><span class='hint'>(1.035)</span> |
| Post-Grants Pass | +0.607***<br><span class='hint'>(0.191)</span> | +0.507**<br><span class='hint'>(0.246)</span> | +0.210<br><span class='hint'>(0.203)</span> | +0.525**<br><span class='hint'>(0.256)</span> | +0.492**<br><span class='hint'>(0.203)</span> | +0.272<br><span class='hint'>(0.258)</span> |
| Nonprofit × Post | -0.055<br><span class='hint'>(0.252)</span> | +0.278<br><span class='hint'>(0.351)</span> | — | — | +0.096<br><span class='hint'>(0.276)</span> | +0.564<br><span class='hint'>(0.398)</span> |
| Blue × Post / Biden × Post | — | — | +0.548**<br><span class='hint'>(0.262)</span> | +0.129<br><span class='hint'>(0.338)</span> | — | — |
| (continuous Biden × Post) | — | — | — | — | +1.951*<br><span class='hint'>(1.032)</span> | +3.200**<br><span class='hint'>(1.370)</span> |
| Housing First adoption | -0.604<br><span class='hint'>(0.408)</span> | -0.366<br><span class='hint'>(0.412)</span> | -0.492<br><span class='hint'>(0.407)</span> | -0.384<br><span class='hint'>(0.409)</span> | -0.576<br><span class='hint'>(0.398)</span> | -0.322<br><span class='hint'>(0.407)</span> |
| HMIS ES coverage | +0.608<br><span class='hint'>(0.415)</span> | +0.541<br><span class='hint'>(0.413)</span> | +0.602<br><span class='hint'>(0.406)</span> | +0.579<br><span class='hint'>(0.395)</span> | +0.613<br><span class='hint'>(0.424)</span> | +0.494<br><span class='hint'>(0.410)</span> |
| log(total beds + 1) | +0.017<br><span class='hint'>(0.299)</span> | +0.084<br><span class='hint'>(0.446)</span> | -0.118<br><span class='hint'>(0.286)</span> | -0.043<br><span class='hint'>(0.435)</span> | -0.086<br><span class='hint'>(0.303)</span> | -0.056<br><span class='hint'>(0.428)</span> |
| PLE in CES | -0.225<br><span class='hint'>(0.326)</span> | +0.106<br><span class='hint'>(0.332)</span> | -0.191<br><span class='hint'>(0.344)</span> | +0.103<br><span class='hint'>(0.353)</span> | -0.240<br><span class='hint'>(0.335)</span> | +0.126<br><span class='hint'>(0.326)</span> |
| (Intercept) | -1.884**<br><span class='hint'>(0.780)</span> | -2.584***<br><span class='hint'>(0.888)</span> | -1.674**<br><span class='hint'>(0.768)</span> | -2.217**<br><span class='hint'>(0.927)</span> | -1.732**<br><span class='hint'>(0.805)</span> | -2.489***<br><span class='hint'>(0.885)</span> |

Cluster-robust SEs at the CoC level in parentheses · `*** p<0.01, ** p<0.05, * p<0.10`.

## Interpretation

### N1 (Nonprofit × Post)
- **Unbalanced:** β = -0.055 (p = 0.828)
- **Balanced:** β = +0.278 (p = 0.428)
- Difference (bal − unbal): +0.333
- Null in both — robust null.

### B1 (Blue-state × Post)
- **Unbalanced:** β = +0.548** (p = 0.036)
- **Balanced:** β = +0.129 (p = 0.702)
- Difference (bal − unbal): -0.419
- ⚠ **Significance flips between panels** — interpret with caution.

### J2 (Joint NP + Biden × Post)
- **Unbalanced:** β = +1.951* (p = 0.059)
- **Balanced:** β = +3.200** (p = 0.020)
- Difference (bal − unbal): +1.249
- ✅ Significant in both — robust to panel composition.

## Decision: which panel to use in the paper?

### Arguments for unbalanced (current primary)
- More observations → more statistical power (651 vs 375 rows).
- FY2022 has 166 CoCs but FY2024 has 292; using all observations is
  standard practice when missingness is not strongly selection-biased.
- Frac-logit with CoC clusters handles unbalanced panels cleanly.
- CoC fixed effects (implicit via Mundlak) identify only off multi-
  year CoCs anyway, so single-year CoCs contribute to main effects.

### Arguments for balanced (robustness)
- **Same CoCs in pre and post** → cleanest DiD contrast.
- Rules out **compositional changes** as an alternative explanation
  (e.g., the FY2024 jump being driven by newly-added CoCs rather
  than existing CoCs responding).
- Parallel-trends assumption easier to defend when the comparison
  is literally the same CoCs across years.
- Pre-registered 'within-CoC' interpretation is more natural.

### Recommendation

**Report the unbalanced panel as primary** (more power; standard
DiD econometric practice) and **the balanced panel as a
robustness check** in the appendix. The balanced sensitivity above
lets reviewers verify that sample composition is not driving the
DiD estimates.