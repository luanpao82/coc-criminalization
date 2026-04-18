---
title: DV Harmonization — Doing Longitudinal Analysis Despite the 2024 Form Change
project: CoC Criminalization / PLE Engagement (Lee & Kim, UCF)
status: strategy note (v0.1) — for PI discussion
last_updated: 2026-04-18
related:
  - "[[main_variables]]"
  - "[[KL_From_Inclusion_to_Influence]]"
  - "[[data_construction_methodology]]"
---

# Longitudinal Analysis Despite the FY2024 DV Shift

## The problem in one sentence

FY2022 and FY2023 asked *"did you engage [policymakers | law enforcement | business leaders] to [ensure homelessness is not criminalized | reverse existing criminalization policies]?"*, and FY2024 replaced this with *"did you [engage policymakers | implement laws] for [co-responder responses | minimizing law enforcement | avoiding criminal sanctions]?"* — same topic, different construct, different items. Treating them as the same variable in a panel violates measurement invariance and biases estimates.

## Eight strategies, from weakest to strongest

### Strategy 1 — Composite "activity index" (simplest, least controversial)

**Operationalization.** For each CoC × year compute:
```
crim_activity_t = (# "Yes" across all 1D-4 cells) / (max possible cells)
                FY2022/23: denominator = 8  (4 rows × 2 cols)
                FY2024:    denominator = 6  (3 rows × 2 cols)
```

**Justification.** Both forms ask "is the CoC actively doing *anything* to prevent/reduce homelessness criminalization?" The indicator set differs, but the underlying "activity level" construct is defensibly the same.

**Limitation.** Loses information about *which kind* of activity. A CoC that says Yes to all 6 FY2024 cells (1.00) is coded the same as one that says Yes to all 8 FY2022 cells (1.00), even though the 2024 "all Yes" behavior includes harder things like "avoiding criminal sanctions."

**When to use.** Simple descriptive models, exploratory analysis, as a first-pass DV before more nuanced models.

### Strategy 2 — Policymaker-engagement common thread (most defensible)

Both forms include "engagement with policymakers" as a distinct dimension:

- **FY2022/2023** has a *row* for "Engaged/educated local policymakers" (row 1).
- **FY2024** has a *column* for "Engaged/Educated Legislators and Policymakers" (col 1).

Because this dimension is **explicitly present in both instruments**, you can construct a panel-safe binary:

```
engaged_policymakers_crim_t ∈ {0, 1}
FY2022/23: 1 if (row 1, col 1 "ensure not criminalized") = Yes
              OR (row 1, col 2 "reverse existing policies") = Yes
FY2024:    1 if any of (row 1 col 1, row 2 col 1, row 3 col 1) = Yes
```

**Justification.** Both instruments ask at item level "did the CoC engage policymakers on criminalization issues?" — the answer is observed in both. Aggregating within year to a CoC-level binary removes the item-count discrepancy.

**Limitation.** Coarse (binary, not graded). Ignores the FY2024 distinction between "engaged" and "implemented laws."

**When to use.** Primary DV for the paper's central RQ ("does PLE engagement → less punitive posture?"). The construct "policymaker engagement on anti-criminalization" is the conceptual heart of the argument and survives the form change.

### Strategy 3 — Harmonized crosswalk with expert judgment

Hand-code a mapping between FY2022/23 and FY2024 items, producing 3–4 comparable dimensions across all years:

| Harmonized dimension | FY2022/23 source | FY2024 source |
|---|---|---|
| Engaged policymakers on criminalization | row 1 (either col) | any row, col 1 |
| Engaged law enforcement on criminalization | row 2 (either col) | row 1 or 2 (either col) — co-responder / minimize LE |
| Implemented anti-criminalization practices | row 4 (either col) "community-wide plans" | row 2 or 3, col 2 — minimized LE / avoided sanctions |
| Engaged business leaders | row 3 (either col) | — (no equivalent in FY2024) |

**Justification.** Preserves multi-dimensional structure while acknowledging that FY2024's items are closer to *practice* whereas FY2022/23's were closer to *stance and engagement*. The "engaged business leaders" dimension is dropped (FY2024 didn't ask).

**Limitation.** The mapping is a judgment call; PIs and reviewers may disagree. Reproducibility requires documenting the mapping publicly.

**When to use.** Primary analysis when you want to keep 3–4 sub-constructs rather than collapse to one. Defensible in a Methods section if the crosswalk is justified theoretically.

### Strategy 4 — Partial measurement invariance in SEM

Formally admit that the DV indicators differ across waves and model it as a latent variable with partial invariance:

- Latent `AntiCrimStance_t` measured by the observed 1D-4 items in year t
- Constrain factor loadings for items that are conceptually equivalent across years (e.g., "engaged policymakers" appears in both forms)
- Allow intercepts to vary by wave
- Estimate change in the latent variable over time

**Justification.** This is the standard psychometric response to non-invariance. Produces unbiased estimates of latent change even when item sets differ.

**Limitation.** With only 3 waves and binary indicators, the SEM may be under-identified or numerically unstable. Typically needs ≥ 5 indicators per wave for identification.

**When to use.** When you have the statistical expertise (or a methodologist coauthor) to implement it properly, and a reviewer is likely to demand measurement invariance testing.

### Strategy 5 — Pooled time-specific measurement model (Meredith & Horn framework)

A less demanding alternative to full SEM: treat each year's DV as a separate outcome variable but estimate them jointly in a seemingly-unrelated-regression or multilevel framework. Report the coefficients separately per wave and test whether they have the same sign / magnitude.

**Justification.** Does not force a single panel DV; each wave's measurement is allowed to stand alone, but joint estimation lets you test parallel patterns ("is the PLE → criminalization relationship the same shape in FY2022, FY2023, and FY2024?").

**Limitation.** No single "effect over time" estimate. Harder to talk about in a paper.

**When to use.** When the point of the paper is the *direction and magnitude consistency* rather than a single panel effect.

### Strategy 6 — External corroboration as the DV, HUD as IV/mediator

Replace the HUD-reported anti-criminalization DV with an **external behavioral measure**:

- **National Homelessness Law Center** "Housing Not Handcuffs" annual reports — city-level counts of ordinances banning sleeping, panhandling, sitting/lying, camping. Updated each year. CoC-level aggregation is straightforward.
- **FBI Uniform Crime Reports** — citations / arrests for vagrancy, disorderly conduct, trespass; proxy for local enforcement posture.
- **State / city ordinance databases** (NLHR, Eviction Lab) — direct measures of local punitive policy.

Use 1D-4 as a self-report *covariate* or *mediator* ("CoCs that report more anti-criminalization engagement also have fewer punitive ordinances — but do the ordinances persist regardless of the CoC's stated engagement?").

**Justification.** Solves the measurement-invariance problem by changing the DV entirely to something measured consistently year-to-year by third parties. This is also the most theoretically defensible framing — the paper argues about *actual policy/enforcement outcomes*, not CoCs' self-reported engagement.

**Limitation.** Requires substantial additional data collection. NLHR reports are available but not always at CoC geography; need to crosswalk city to CoC.

**When to use.** Ideal. This is the strongest design if time/budget permit. Consider reframing the paper: "CoCs' reported anti-criminalization activity (HUD 1D-4) is one mechanism; the DV is the actual ordinance / enforcement outcome."

### Strategy 7 — Two-wave design, not three

Drop FY2022 or FY2024 from the primary analysis and report the other two as the panel.

Two defensible combinations:

- **FY2023 + FY2024 only.** Both use the V.B.1.k NOFO section; FY2023 uses the older item set and FY2024 the newer one, so *even this pair has non-invariance*. Weaker option.
- **FY2022 + FY2023 only.** Identical instrument across both waves; can build a clean 2-wave panel. Loses the FY2024 data entirely (half of all CoCs).

**Justification.** Simplicity. Reviewers can't attack a panel where the instrument is literally identical.

**Limitation.** Wastes the largest year's data (FY2024 has 292 CoCs) or loses the ability to see change around the FY2024 policy/instrument change.

**When to use.** Robustness check: run the main model on FY2022+FY2023 as a sanity check, and report that the effect size is consistent with the full 3-year harmonized model.

### Strategy 8 — Treat the instrument change itself as the finding

**Framing shift.** Do a methodological / descriptive paper: "HUD changed how it asks CoCs about criminalization in FY2024; here is what that change reveals about evolving federal expectations, and here is how it affects panel measurement." The FY2024 shift is itself a policy signal — HUD moved from *"are you engaging on criminalization?"* to *"are you actually decriminalizing specific practices?"* — that's a substantive policy/administrative change worth analyzing.

**When to use.** If the main paper runs into measurement invariance dead ends, this becomes a spin-off methodological piece that complements the main paper rather than replaces it.

---

## Recommended path

Combine **Strategy 2 + Strategy 6**, with **Strategy 1 as a robustness check**:

### Primary DV (panel-safe): policymaker-engagement binary
- Construct: "Did the CoC engage policymakers on criminalization issues in year t?"
- Operationalized from 1D-4 in all 3 years using the mapping in Strategy 2
- Binary; supports logistic fixed-effects panel models

### Reinforcing DV (external): local anti-homelessness ordinance count
- Source: NLHR / Housing Not Handcuffs dataset, CoC-level aggregation
- Continuous; supports count / rate models
- Provides behavioral validation of the self-report DV

### Robustness: composite activity index (Strategy 1)
- 0–1 normalized proportion of Yes cells
- Report as supplement to show the main finding isn't an artifact of how the DV is collapsed

### In the Methods section
1. Explicitly state the FY2024 instrument change.
2. Show that the policymaker-engagement binary is observable in both forms.
3. Report the harmonized composite as the primary estimate, and the external ordinance DV as the pre-registered robustness check.
4. Include a measurement-invariance appendix (Strategy 4) if a reviewer asks.

This gives the paper one panel-safe DV (defensible), one external-data DV (stronger identification), and a composite robustness check — while honestly flagging that FY2022/23 and FY2024 are not mechanical equivalents.

---

## Practical next steps in this project

1. **Re-code 1D-4 in the extractor** to produce three standardized outputs per CoC-year:
   - `crim_activity_index` (Strategy 1, 0–1)
   - `engaged_policymakers_crim_bin` (Strategy 2, 0/1)
   - `crim_harmonized_dims` (Strategy 3, 3–4 sub-dimensions)
   These can be computed from the already-extracted `1d_4_*` cells with a small transform.

2. **Acquire NLHR "Housing Not Handcuffs" dataset** and build a CoC-to-jurisdiction crosswalk.

3. **Decide with the PI team** which strategy becomes primary. The rest become appendices or sensitivity analyses.

4. **Document the chosen strategy in `main_variables.md`** as the canonical DV definition before any modeling begins.

## Why "can we do 3-year longitudinal?" = "yes, carefully"

The measurement change is real and must be handled explicitly — but it is not fatal. Every strategy above has been used in the social-science literature when confronting non-invariant instruments across waves. The weakest response would be to ignore it (run `1d_4_*` as if the meaning were stable); the strongest is to combine a defensible harmonized self-report DV with an external behavioral DV and report both. We can do 3 years. We cannot do 3 years *naively*.
