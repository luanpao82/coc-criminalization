---
title: Main Variables — Construct Map and Year-to-Year Comparison
project: CoC Criminalization / PLE Engagement (Lee & Kim, UCF)
status: reference document (v0.1)
last_updated: 2026-04-18
related:
  - "[[KL_From_Inclusive_to_Influence]]"
  - "[[data_construction_methodology]]"
  - "[[codebook]]"
  - "[[pilot_findings]]"
  - "[[progress/README]]"
---

# Main Variables — HUD CoC Consolidated Application

This document is the **authoritative reference** for which HUD CoC
Application variables map to which construct in the study, what each
variable actually means in the source PDF, and whether the variable
has the same meaning across FY2022, FY2023, and FY2024.

Read this before writing analysis code. Several variables that *look*
panel-safe by their ID (e.g., `1d_4_1_policymakers`) are actually
measuring a different construct in FY2022/2023 than in FY2024 —
analyzing them as a single panel column will produce misleading
estimates.

Conventions used below:
- **🟢 identical** — same question text, same response options
- **🟡 equivalent** — same construct, minor rewording (safe to panel)
- **🔴 changed** — construct itself shifted; do **not** treat as the same variable

---

## 1. Governance / Leadership Structure (Independent Variable)

The paper's first RQ: does CoC lead agency type (nonprofit vs. government)
shape PLE engagement and criminalization responses?

### 1A-1 CoC Name and Number → `1a_1a`, `1a_1b`

- **FY2022 / 2023 / 2024**: identical prompt — *"CoC Name and Number"* 🟢
- **Source:** auto-populated by HUD e-snaps; e.g. `AL-500 - Birmingham/Jefferson, St. Clair, Shelby Counties CoC`
- **Use:** CoC identifier (panel key). Manual coders split into `1a_1a` (the ID `AL-500`) and `1a_1b` (the place name).

### 1A-2 Collaborative Applicant Name → `1a_2`

- **FY2022 / 2023 / 2024**: identical prompt — *"Collaborative Applicant Name"* 🟢
- **Substantive use:** the organization that coordinates the CoC. Examples: `One Roof` (nonprofit), `City of Little Rock` (government), `County of Santa Clara` (government), `CARES of NY, Inc.` (nonprofit).
- **Operationalization:** hand-code each Collaborative Applicant as `{nonprofit, city_govt, county_govt, state_govt, tribal, other}` — this becomes the primary IV for the study's central hypothesis.

### 1A-3 CoC Designation → `1a_3`

- **FY2022 / 2023 / 2024**: identical prompt 🟢
- **Response options:** `CA` (Collaborative Applicant), `UFA` (Unified Funding Agency), `UFC` (Unified Funding Community — rare)
- **Meaning:** HUD's formal designation. UFAs are a smaller, more-integrated operational model; most CoCs are CAs.
- **Use:** categorical control / secondary IV.

### 1A-4 HMIS Lead → `1a_4`

- **FY2022 / 2023 / 2024**: identical prompt 🟢
- **Use:** operational complement to the Collaborative Applicant. In many CoCs the HMIS lead is a different entity (e.g., state Institute for Community Alliances) — useful secondary measure of sector distribution.

---

## 2. PLE Engagement (Mediator / Secondary IV)

RQ 2: does more institutionalized PLE engagement correspond to less
punitive local responses?

### 1B-1 row 6: "Homeless or Formerly Homeless Persons" → `1b_1_6_meetings`, `1b_1_6_voted`, `1b_1_6_ces`

- **FY2022 / 2023 / 2024**: the 1B-1 participation chart keeps row 6 as "Homeless or Formerly Homeless Persons" with the same three columns (CoC meetings / voted including board / coordinated entry participation). 🟢
- **Meaning:** whether PLE are included in CoC meetings (participation), whether they vote on CoC business and board elections (decision-making authority), and whether they participate in CES operations (service-delivery role).
- **Important caveat:** this is self-reported Yes/No — a CoC can say "Yes" to "Voted" even if only tokenistic. Combine with the counts variable below for a more robust measure.

### 1D-10a (FY2024) ≡ 1D-11a (FY2022 / FY2023) — PLE active participation counts

- **FY2022** `1D-11a`: **5 rows × 2 cols** 🔴
  - Row labels: (1) Included in local planning, (2) Review/recommend revisions to local policies, (3) Participate on CoC committees, (4) Included in decisionmaking processes, (5) Included in local competition rating factors
- **FY2023** `1D-11a`: **4 rows × 2 cols** 🟡
  - Row labels: (1) Included in decisionmaking, (2) CoC committees, (3) Local competition rating factors, (4) Coordinated entry process
- **FY2024** `1D-10a` → `1d_10a_{1..4}_{years,unsheltered}`: **4 rows × 2 cols** 🟡
  - Row labels: (1) *Routinely* included in decisionmaking (wording tweaked), (2) CoC committees, (3) Local competition rating factors, (4) Coordinated entry process
- **Columns (all 3 years):** "# PLE within last 7 years or current program participant" | "# PLE coming from unsheltered situations"
- **Panel strategy:**
  - Treat **FY2023 row 1 ≈ FY2024 row 1** (decisionmaking) even though FY2024 adds "Routinely"
  - Rows 2, 3, 4 are identical between FY2023 and FY2024
  - **FY2022 requires manual crosswalk**: FY2022 row 3 ≡ FY2023/24 row 2; FY2022 row 4 ≡ FY2023/24 row 1; FY2022 row 5 ≡ FY2023/24 row 3. FY2022 has no equivalent of "coordinated entry process" (FY2023/24 row 4). FY2022 rows 1–2 have no FY2023/24 equivalent.
- **Analytical recommendation:** build a panel-safe summary variable `ple_engagement_total = sum(1d_10a_*_years)` for FY2023/24, and use FY2022 as a separate slice.

### 1B-1a (narrative) — Experience Promoting Racial Equity

- **FY2022 / 2023 / 2024**: stable question text 🟢
- **Class D narrative** — not yet extracted (Stage 2 LLM task).

### 1D-11 (FY2022) / 1D-11 (FY2023 YHDP) / 1D-11 (FY2024) — Lived Experience Outreach

- **FY2022** `1D-11`: narrative — outreach efforts to engage PLE
- **FY2024** `1D-11`: narrative — involving individuals with lived experience
- Wording has shifted each year — treat as equivalent construct but code separately.

---

## 3. Criminalization Responses (Dependent Variable)

RQ 3: does PLE engagement correlate with less punitive local policy?

### 1D-4 "Strategies to Prevent Criminalization of Homelessness" → `1d_4_{1..3}_{policymakers,prevent_crim}`

**⚠ This is the most important construct-level change to understand.**

- **FY2022 / FY2023** `1D-4`: **4 rows × 2 cols** 🔴 construct changed in 2024
  - **Rows (strategies):**
    1. Engaged/educated local policymakers
    2. Engaged/educated law enforcement
    3. Engaged/educated local business leaders
    4. Implemented community wide plans
    5. (Other — limit 500 chars; drop)
  - **Columns (goal of the strategy):**
    - "Ensure Homelessness is not Criminalized"
    - "Reverse Existing Criminalization Policies"

- **FY2024** `1D-4`: **3 rows × 2 cols** 🔴
  - **Rows (practices):**
    1. Increase utilization of co-responder / social-services-led responses over law enforcement
    2. Minimize use of law enforcement to enforce bans on public sleeping / camping / basic life functions
    3. Avoid imposing criminal sanctions (fines, fees, incarceration) for public sleeping / camping / life functions
    4. (Other — drop)
  - **Columns (stage of implementation):**
    - "Engaged/Educated Legislators and Policymakers"
    - "Implemented Laws/Policies/Practices that Prevent Criminalization of Homelessness"

**Why this matters for analysis:**

The manual spreadsheet's field IDs (`1d_4_1_policymakers`, `1d_4_1_prevent_crim`, etc.) match the **FY2024 row/column structure**. When the pipeline extracts from an FY2022 PDF and writes to the same field IDs, the *numbers are there* but they answer a **different question**:

- FY2024 `1d_4_1_policymakers` = "Did you engage legislators on co-responder responses?"
- FY2022 `1d_4_1_policymakers` = "Did you engage local policymakers on ensuring homelessness is not criminalized?" (the FY2022 chart's row 1, column 1)

These are **related but distinct constructs**. Pooling them into a single panel column would violate measurement invariance.

**Recommended panel strategies (pick one):**

1. **Split the panels**: run FY2022+FY2023 with the old 1D-4 schema (construct A: "engagement strategies toward criminalization stance"), and FY2024 alone with the new 1D-4 schema (construct B: "practices to decriminalize basic life functions"). Report both; do not average them.
2. **Harmonize at the composite level**: build a single aggregate score per CoC per year (e.g., "CoC engaged any actor to prevent/reverse criminalization in this year") — defensible if justified in the paper as a high-level behavioral index.
3. **Focus on FY2023–FY2024 panel only** for primary analysis; use FY2022 as a pre-period indicator of general activity level.

### 1D-5 (FY2022 / FY2023) — Rapid Rehousing beds
### 1D-5 was renumbered across years — check crosswalk before using

---

## 4. CoC Coordination and Context (Controls)

### 1B-1 full chart (33 canonical rows × 3 cols) → `1b_1_{1..33}_{meetings,voted,ces}`

- **FY2022 / 2023 / 2024**: chart structure is stable; FY2024 adds optional "Other" rows (34, 35) that are not in the canonical schema. 🟢 for canonical rows 1–33.
- **Use:** breadth-of-participation index. The sum of Yes answers across rows is a reasonable "inclusiveness" score.

### 1C-1 Coordination with Federal/State/Local Orgs → `1c_1_{1..17}`

- **Stable across years** 🟢 — same 17 canonical organization types with Yes/No/Nonexistent responses.
- **Use:** cross-sector coordination index.

### 1C-4 Children/Youth — SEAs, LEAs, School Districts → `1c_4_{1..4}`

- **Stable across years** 🟢

### 1C-4c Early Childhood Partnerships → `1c_4c_{1..9}_{mou,oth}`

- **Stable across years** 🟢

### 1D-2 Housing First → `1d_2_1`, `1d_2_2`, `1d_2_3`

- **Stable across years** 🟢 — 3 numeric sub-answers (count of projects, count adopting Housing First, % with Housing First).
- **Use:** proxy for CoC's service orientation (Housing First adoption is strongly correlated with less-punitive posture, per literature).

### 1D-6 Mainstream Benefits Training → `1d_6_{1..6}`

- **Stable across years** 🟢

### 2A-5 HMIS Bed Coverage → `2a_5_{1..6}_{non_vsp, vsp, hmis, coverage}`

- **FY2022**: 4 cols (HIC beds, Dedicated for DV, HMIS beds, Coverage Rate) 🟡
- **FY2023**: 4 cols (Beds in HIC, VSP beds in HIC, Beds in HMIS, Coverage Rate) 🟡
- **FY2024**: 4 cols (Non-VSP beds, VSP beds, HMIS+VSP beds, Coverage Rate) 🟡
- **Only the "Coverage Rate" column is comparable across all three years** as the same measure.
- **Use:** CoC data infrastructure maturity / size. Coverage rate is panel-safe. Bed counts (non-VSP, VSP, HMIS) need care — column meaning shifted.

### 2B Point-in-Time count metadata (`2b_1`, `2b_2`, `2b_3`, `2b_4`)

- **Stable across years** 🟢
- `2b_1` is the PIT count date; `2b_2` the HDX submission date; `2b_3` and `2b_4` are narratives.

### 2C System Performance → `2c_1a_1`, `2c_1a_2`, `2c_2`, `2c_3`, `2c_4`, `2c_5`

- **Stable across years** 🟢 for the categorical gates; narrative components should be LLM-extracted.

---

## 5. Narrative / Class-D Variables (Not Yet Extracted)

These require Stage-2 LLM extraction with verbatim-quote requirement
(see `data_construction_methodology.md` §4.2). Until then they are
flagged as unavailable for analysis.

| Variable | Construct | Year notes |
|---|---|---|
| `1b_1a` | Experience Promoting Racial Equity | 🟢 stable |
| `1b_3` | Strategy to Solicit/Consider Opinions on Ending Homelessness | 🟢 stable |
| `1c_4a` | Formal Partnerships with Youth Education Providers | 🟢 stable |
| `1c_5a`, `1c_5b`, `1c_5d`, `1c_5e`, `1c_5f` | DV / SA collaboration details | wording shifted between FY2023 and FY2024 🔴 |
| `1c_6a` | LGBTQ+ Anti-discrimination | 🟢 stable |
| `1c_7a` | Written Policies on Homeless Admission Preferences with PHAs | 🟢 stable |
| `1d_2a` | Project Evaluation for Housing First Compliance | 🟢 stable |
| `1d_3` | Street Outreach Scope | 🟢 stable |
| `1d_6a` | Information/Training on Mainstream Benefits | 🟢 stable |
| `1d_7`, `1d_7a` | Non-Congregate Sheltering | 🟢 stable |
| `1d_8`, `1d_8a`, `1d_8b` | Affirmatively Furthering Fair Housing (FY2024 new) | 🔴 year_specific to FY2024 |
| `1d_9a` — `1d_9d` | Racial equity assessment + strategies | wording shifted; separately code |
| `1d_10b`, `1d_10c` | Professional dev / feedback from PLE | FY2024; in FY2022/23 under 1D-11b/c 🟡 |
| `1d_11` | Lived Experience Outreach (narrative) | 🟡 equivalent across years |

---

## 6. Recommended Analytical Variable Set

For the core paper's three research questions, we recommend:

### IV — CoC leadership structure
- `1a_2` (manual coding: nonprofit vs. government)
- `1a_3` (CoC designation: CA / UFA)

### Mediator — PLE engagement (composite)
- `1b_1_6_meetings`, `1b_1_6_voted`, `1b_1_6_ces` (Homeless/Formerly Homeless as CoC participants)
- `1d_10a_{1..4}_years`, `1d_10a_{1..4}_unsheltered` (counts of PLE in governance) — **FY2023 + FY2024 panel only**
- Stage-2 (LLM) narrative code from `1b_1a` and `1d_11` (when extracted)

### DV — Criminalization posture
- **FY2022 + FY2023 panel**: `1d_4_1_prevent_crim` ("Engaged/educated local policymakers to ensure homelessness is not criminalized") as primary; other `1d_4_*` rows as secondary
- **FY2024 cross-section**: `1d_4_{1..3}_prevent_crim` as a composite (three distinct harm-reduction practices)
- Do **not** pool the two panels into a single column

### Controls
- `1a_3` (designation)
- `1d_2_3` (% Housing First adoption)
- `2a_5_1_coverage` through `2a_5_6_coverage` (HMIS bed coverage per project type — panel-safe)
- CoC geographic size / population (external: U.S. Census + HIC totals from `2a_5_*_non_vsp` summed)
- Urbanicity / region (derive from `1a_1a` and external geocoder)

---

## 7. Variables We Recommend Excluding (for now)

| Field | Reason |
|---|---|
| `1c_2_{1..4}` | ESG consultation — not in 2022 PDF at this exact location; requires year-specific extraction fix |
| `1c_5_{1..3}` | DV/SA collaboration — structure changed meaningfully across years |
| `1c_5c_{1..6}_{proj,ces}` | DV training chart — changed between FY2022 and FY2024 |
| `1d_9_{1,2}` | Racial equity assessment gate — exists only in FY2024 at this question number |
| `1d_9b_{1..11}` | Racial equity strategies chart — FY2024-only at this ID |
| `1e_*` | Local competition / ranking — extractor coverage not yet validated |
| `4a_*` | DV Bonus — separate sub-population analysis |

---

## 8. Cross-reference with Pipeline Artifacts

- **`panel_field_map.csv`** — categorizes every field as panel_safe / mostly_panel / year_specific / sparse based on empirical extraction coverage
- **`crosswalk.csv`** — HUD question ID mapping across years (complements this document, which is the *substantive* mapping)
- **`crosswalk_review.md`** — 34 items flagged for PI review where automated label matching could not resolve the crosswalk
- **`codebook.md`** — full 331-variable codebook with observed values
- **`coc_panel_wide.xlsx`** sheet `panel_safe` — immediate analysis-ready subset
