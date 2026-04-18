# Multilevel DiD — State + County (within-state) Political Environment

_Generated: 2026-04-18T03:19:57_

## Why multilevel

`blue_state` (state-level 2020 winner) and `biden_share` (county-level
continuous) are highly correlated — putting both in the same model
directly produces collinearity. We apply a Mundlak-style decomposition
at the multilevel structure to separate them:

```
state_mean_biden   = average Biden share of counties in state
biden_within_state = county_biden_share − state_mean_biden
```

After this decomposition:
- `blue_state × Post` captures the **state-level** DiD
  (political environment of the state you're in).
- `biden_within_state × Post` captures the **within-state county** DiD
  (how much bluer your county is than the rest of your state).

These two are statistically orthogonal, so we can estimate both
simultaneously. We also keep `nonprofit_led × Post` for completeness.

## Estimator

- Fractional logit (Papke-Wooldridge) for bounded [0, 1] DV
- **State-level cluster-robust SE** (higher level in hierarchy)
- Wild-cluster bootstrap p-values (Rademacher, state-clustered, 999 reps)
- Mundlak-adjusted time-varying controls
- Estimated on both unbalanced (651 obs) and balanced (375 obs) panels

## Coefficient table

| Variable | Unbalanced (n=594) | Balanced (n=341) |
|---|---|---|
| Nonprofit-led (IV₁) | +0.058<br><span class='hint'>(0.172)</span> | +0.167<br><span class='hint'>(0.190)</span> |
| Blue state (IV₂, state-level) | -0.299<br><span class='hint'>(0.216)</span> | -0.312<br><span class='hint'>(0.241)</span> |
| Biden-within-state (IV₃, county − state mean) | +0.624<br><span class='hint'>(0.852)</span> | -0.194<br><span class='hint'>(1.147)</span> |
| Post-Grants Pass | +0.159<br><span class='hint'>(0.302)</span> | +0.299<br><span class='hint'>(0.357)</span> |
| Nonprofit × Post | +0.091<br><span class='hint'>(0.280)</span> | +0.391<br><span class='hint'>(0.449)</span> |
| <strong>Blue state × Post (state DiD)</strong> | +0.572*<br><span class='hint'>(0.311)</span> | +0.225<br><span class='hint'>(0.410)</span> |
| <strong>Biden-within × Post (within-state county DiD)</strong> | +0.454<br><span class='hint'>(1.558)</span> | +2.680<br><span class='hint'>(2.044)</span> |
| Housing First adoption | -0.498<br><span class='hint'>(0.387)</span> | -0.365<br><span class='hint'>(0.500)</span> |
| HMIS ES coverage | +0.594*<br><span class='hint'>(0.331)</span> | +0.479*<br><span class='hint'>(0.286)</span> |
| log(total beds + 1) | -0.111<br><span class='hint'>(0.296)</span> | -0.007<br><span class='hint'>(0.478)</span> |
| PLE in CES | -0.195<br><span class='hint'>(0.382)</span> | +0.110<br><span class='hint'>(0.398)</span> |
| [Mundlak] HF mean | +1.434***<br><span class='hint'>(0.465)</span> | +1.689**<br><span class='hint'>(0.849)</span> |
| [Mundlak] HMIS mean | +0.015<br><span class='hint'>(0.463)</span> | +0.391<br><span class='hint'>(0.591)</span> |
| [Mundlak] log beds mean | +0.276<br><span class='hint'>(0.280)</span> | +0.187<br><span class='hint'>(0.453)</span> |
| [Mundlak] PLE mean | +0.249<br><span class='hint'>(0.516)</span> | -0.141<br><span class='hint'>(0.712)</span> |
| (Intercept) | -1.541**<br><span class='hint'>(0.736)</span> | -2.321**<br><span class='hint'>(0.972)</span> |

Cluster-robust SE at the state level in parentheses · `*** p<0.01, ** p<0.05, * p<0.10`.

## Wild-cluster bootstrap p-values (state-clustered, 999 reps)

| DiD term | Unbalanced | Balanced |
|---|---|---|
| Nonprofit × Post | 0.803 | 0.534 |
| **Blue state × Post** | **0.095** | **0.698** |
| **Biden-within × Post** | **0.932** | **0.416** |

## 2×2 Quadrant means (unbalanced sample)

| Year | Red state × Red county | Red state × Blue county | Blue state × Red county | Blue state × Blue county |
|---|---|---|---|---|
| FY2022 | 0.721 | 0.769 | 0.646 | 0.721 |
| FY2023 | 0.782 | 0.729 | 0.672 | 0.720 |
| FY2024 | 0.751 | 0.872 | 0.813 | 0.831 |

## Key findings

### Both political dimensions, **same model**, unbalanced:
- Nonprofit × Post: β = +0.091 (cluster p = 0.744, bootstrap p = 0.803)
- Blue state × Post: β = +0.572* (cluster p = 0.066, bootstrap p = 0.095)
- Biden-within × Post: β = +0.454 (cluster p = 0.771, bootstrap p = 0.932)

### Balanced panel (clean DiD contrast):
- Nonprofit × Post: β = +0.391 (cluster p = 0.383, bootstrap p = 0.534)
- Blue state × Post: β = +0.225 (cluster p = 0.583, bootstrap p = 0.698)
- Biden-within × Post: β = +2.680 (cluster p = 0.190, bootstrap p = 0.416)

## Which level matters — automated diagnosis

### Unbalanced
- **State level dominates** (blue state bootstrap p=0.095, within-state n.s. at p=0.932). State-level political environment is the channel; county-level adds little.

### Balanced
- **Neither significant** after joint estimation (blue state bootstrap p=0.698, within-state p=0.416). Either the political-environment effect is absorbed by the joint specification, or the sample is underpowered for the multilevel decomposition.

## Quadrant trajectory reading

The 2×2 panel mean table above shows FY-by-FY activity index for each
state × county political combination. Compare FY2023 → FY2024 differences:

- If Blue state × Blue county jumps most → both state AND county matter
- If Blue state × Red county ≈ Blue state × Blue county → state dominates
- If Red state × Blue county ≈ Blue state × Blue county → county dominates
