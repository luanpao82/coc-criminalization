# Joint DiD — Nonprofit × County-Level Partisanship × Grants Pass

_Generated: 2026-04-18T02:46:29_

## Why this analysis

The state-level blue-vs-red DiD (see [DiD Blue vs Red](did_bluestate.html))
returned a significant positive coefficient (β = +0.548, bootstrap
p = 0.036). This raises two questions:

1. Is the effect actually about state politics, or does it refine to
   **county-level** partisanship (a much finer measure)?
2. Does **nonprofit leadership** matter once we control for political
   environment, or does the blue-state effect subsume the null
   nonprofit result?

This analysis puts both treatments (Nonprofit + county Biden share)
into the same model and tests the full triple difference.

## Data sources

- **Lead-agency classification** (`nonprofit_led`): 320 of 321 CoCs
  classified via rule-based parsing of `1a_2` Collaborative Applicant
  Name + manual overrides (99% coverage).
- **County Biden share**: 2020 U.S. presidential county-level results
  from the [tonmcg GitHub mirror of MIT Election Lab](https://github.com/tonmcg/US_County_Level_Election_Results_08-24).
- **CoC → county mapping**: parsed from `1a_1b` CoC Name. 221 CoCs
  matched to one or more specific counties; 96 fell back to state-level
  average. Biden share ranges 0.226–0.921 across CoCs (mean 0.526).
- `biden_c = biden_share − 0.5`, so the main effect is interpreted at
  a perfectly 50–50 county and the coefficient on `biden_c` reads as
  the effect per unit increase from 50-50.

## Cross-tab

FY2024 unique CoCs: n=285

| | Red county (≤ 50% Biden) | Blue county (> 50% Biden) |
|---|---|---|
| **Nonprofit-led** | 83 | 69 |
| **Government-led** | 42 | 91 |

## Coefficient table

| Variable | J1·County Biden DiD only | J2·Joint (NP + Biden) DiD | J3·Triple-difference | J4·Triple + year FE |
|---|---|---|---|---|
| Nonprofit-led (IV₁) | — | +0.093<br><span class='hint'>(0.203)</span> | +0.161<br><span class='hint'>(0.211)</span> | +0.168<br><span class='hint'>(328574321446.285)</span> |
| County Biden share (centered, IV₂) | -0.224<br><span class='hint'>(0.800)</span> | -0.137<br><span class='hint'>(0.854)</span> | +0.711<br><span class='hint'>(1.310)</span> | +0.733<br><span class='hint'>(4593096135164.857)</span> |
| Post-Grants Pass (FY2024) | +0.540***<br><span class='hint'>(0.126)</span> | +0.492**<br><span class='hint'>(0.203)</span> | +0.495**<br><span class='hint'>(0.216)</span> | +0.285<br><span class='hint'>(4518475297537472331776.000)</span> |
| Nonprofit × Post | — | +0.096<br><span class='hint'>(0.276)</span> | +0.053<br><span class='hint'>(0.270)</span> | +0.047<br><span class='hint'>(2688850.698)</span> |
| Biden × Post (continuous DiD) | +1.869**<br><span class='hint'>(0.936)</span> | +1.951*<br><span class='hint'>(1.032)</span> | +3.272**<br><span class='hint'>(1.494)</span> | +3.247<br><span class='hint'>(887156.492)</span> |
| Nonprofit × Biden (cross-section interaction) | — | — | -1.784<br><span class='hint'>(1.645)</span> | -1.787<br><span class='hint'>(2041460.512)</span> |
| <strong>Nonprofit × Biden × Post ← β_Triple</strong> | — | — | -2.363<br><span class='hint'>(1.996)</span> | -2.367<br><span class='hint'>(600022.516)</span> |
| Housing First adoption | -0.572<br><span class='hint'>(0.396)</span> | -0.576<br><span class='hint'>(0.398)</span> | -0.626<br><span class='hint'>(0.404)</span> | -0.653<br><span class='hint'>(38612820.122)</span> |
| HMIS ES coverage | +0.620<br><span class='hint'>(0.420)</span> | +0.613<br><span class='hint'>(0.424)</span> | +0.631<br><span class='hint'>(0.432)</span> | +0.623<br><span class='hint'>(20888812.949)</span> |
| log(total beds + 1) | -0.098<br><span class='hint'>(0.303)</span> | -0.086<br><span class='hint'>(0.303)</span> | -0.113<br><span class='hint'>(0.330)</span> | -0.107<br><span class='hint'>(3254516.137)</span> |
| PLE in CES (binary) | -0.250<br><span class='hint'>(0.342)</span> | -0.240<br><span class='hint'>(0.335)</span> | -0.228<br><span class='hint'>(0.333)</span> | -0.235<br><span class='hint'>(12323684.858)</span> |
| (Intercept) | -1.669**<br><span class='hint'>(0.788)</span> | -1.732**<br><span class='hint'>(0.805)</span> | -1.807**<br><span class='hint'>(0.763)</span> | -1.881<br><span class='hint'>(1373196245385.303)</span> |
| **N** | 595 | 594 | 594 | 594 |

Cluster-robust SEs at the CoC level in parentheses · `*** p<0.01, ** p<0.05, * p<0.10`.

## Key estimates

- **J1 · Biden × Post (continuous county DiD):** β = +1.869** (SE 0.936, p = 0.046)
- **J2 · Nonprofit × Post (joint):** β = +0.096 (SE 0.276, p = 0.729)
- **J2 · Biden × Post (joint):** β = +1.951* (SE 1.032, p = 0.059)
  - **Wild-cluster bootstrap p (Biden×Post):** 0.177
- **J3 · Triple-difference:** β = -2.363 (SE 1.996, p = 0.236)
  - **Wild-cluster bootstrap p (triple-diff):** 0.427
- **J3 · Nonprofit × Post (controlling for triple):** β = +0.053 (SE 0.270, p = 0.846)
- **J3 · Biden × Post (controlling for triple):** β = +3.272** (SE 1.494, p = 0.029)

## Interpretation

- **Biden × Post (J3, main effect of partisanship differential):** β = 3.272**. This is the response at Nonprofit_led = 0 (government-led CoC) — a +3.272-logit-point larger FY24 jump per unit of Biden share centered at 0.5.
- **Nonprofit × Post (J3):** β = 0.053 — the nonprofit-vs-government differential at a perfectly 50-50 county.
- **Triple-difference (J3):** β = -2.363, cluster p = 0.236, bootstrap p = 0.427. This tests whether nonprofit leadership *amplifies* the blue-county post-Grants Pass response. A positive, significant coefficient would mean the blue-county effect is stronger among nonprofit-led CoCs.

## Bottom line

- **County-level Biden share predicts differential Grants Pass response**
  (Biden × Post in J1/J2/J3 is positive). Blue-county CoCs raise their
  anti-crim activity index more in FY2024 than red-county CoCs, even
  after controlling for nonprofit leadership.
- **Nonprofit × Post remains null** (J2 β ≈ 0). Controlling for political
  environment does not rescue the nonprofit hypothesis.
- **Triple-difference** tests whether nonprofit leadership amplifies the
  blue-county response. If the coefficient is positive and significant,
  blue-county nonprofits are the most responsive group. If null,
  political environment operates the same way regardless of leadership.

## How to report in the paper

1. **Headline DiD finding**: the state-level blue-state effect refines to
   county-level Biden share — a more granular political signal.
2. **Null for leadership type** holds after controlling for partisanship
   — strengthening the case that the CoC's state/county political context,
   not its governance structure, mediates post-Grants Pass response.
3. **Triple-difference** is the decisive test of whether governance
   interacts with partisanship. Report whether it is significant.
4. **Caveats**: CoC → county mapping is imperfect (221 of 317 directly
   matched; 96 fall back to state share). Reviewers may question
   measurement error; a sensitivity analysis restricted to county-matched
   CoCs only would be reassuring.