---
title: Codebook — HUD CoC Application Variables (v0.1 draft)
project: CoC Criminalization / PLE Engagement (Lee & Kim, UCF)
status: working draft — PI review required before adoption
last_updated: 2026-04-17
schema_version: FY2024
related:
  - "[[data_construction_methodology]]"
  - "[[KL_From_Inclusion_to_Influence]]"
---

# Codebook

This codebook catalogues every variable in the canonical FY2024 schema (~331 columns), organized by HUD application section. Value domains are inferred from the manually coded `coc_apps_all_info.xlsx` and should be treated as a **first-pass draft**: observed values reflect what coders entered, not necessarily what is permitted. PIs must review and lock the controlled vocabulary before the iteration loop begins.

## Missing-value conventions

| Convention | Meaning |
|---|---|
| `Nonexistent` | HUD option: the entity/process does not exist in the CoC's geographic area |
| `N/A` | Question is skipped because a prior gate answer excluded it |
| `NA_not_asked_this_year` | Variable did not exist in this year's form (crosswalk-derived) |
| blank | Source PDF is genuinely missing a value — needs human review |


## Variable type taxonomy

| Code | Class | Example | Validation |
|---|---|---|---|
| `categorical` | A | Yes/No/Nonexistent | Exact match against locked vocab |
| `categorical_designation` | A | CA / UFA | Exact match |
| `integer` | B | PIT count, HIC beds | Exact match after unit normalization |
| `numeric` | B | Percentages, dollars | Exact within rounding tolerance |
| `percent` | B | Bed coverage % | Normalized to decimal |
| `label` | C | CoC name, PHA name | Case/whitespace-normalized string match |
| `narrative` | D | 1B-1a racial-equity response | Reviewer acceptance + verbatim evidence |
| `UNOBSERVED` | — | No value seen in manual xlsx | PI must specify expected type |


## CoC Name

| field_id | sub-group | label | type | observed domain | likely Q (FY2024) |
|---|---|---|---|---|---|
| `1a_1a` |  |  | label | 'AK-501'×1; 'AL-500'×1; 'AL-502'×1; 'AL-504'×1; 'AL-506'×1 | 1A-1a |

## CoC Number

| field_id | sub-group | label | type | observed domain | likely Q (FY2024) |
|---|---|---|---|---|---|
| `1a_1b` |  |  | label | 'Oakland, Berkeley/Alameda County CoC'×2; 'Alaska Balance of State'×1; 'Birmingham/Jefferson, St. Clair, Shelby Counties'×1; 'Florence/Northwest Alabama CoC'×1; 'Montgomery City & County CoC'×1 | 1A-1b |

## Collaborative Applicant Name

| field_id | sub-group | label | type | observed domain | likely Q (FY2024) |
|---|---|---|---|---|---|
| `1a_2` |  |  | label | 'CARES of NY, Inc.'×11; 'Alameda County'×2; 'Institute for Community Alliances'×2; 'Alaska Coalition on Housing & Homelessness'×1; 'One Roof'×1 | 1A-2 — *Collaborative Applicant Name: One Roof* |

## CoC Designation

| field_id | sub-group | label | type | observed domain | likely Q (FY2024) |
|---|---|---|---|---|---|
| `1a_3` |  |  | label | 'CA'×280; 'UFA'×11; 'UFC'×1 | 1A-3 — *CoC Designation: CA* |

## HMIS Lead

| field_id | sub-group | label | type | observed domain | likely Q (FY2024) |
|---|---|---|---|---|---|
| `1a_4` |  |  | label | 'Institute for Community Alliances'×17; 'CARES of NY, Inc.'×9; 'NJ HMFA'×5; 'Georgia Department of Community Affairs'×3; 'Volusia/Flagler County Coalition for the\n\nHomeless'×2 | 1A-4 — *HMIS Lead: One Roof* |

## Inclusive Structure and Participation – Participation in Coordinated Entry

| field_id | sub-group | label | type | observed domain | likely Q (FY2024) |
|---|---|---|---|---|---|
| `1b_1_1_meetings` | Affordable Housing Developer(s) | Participated in CoC Meetings | label | 'Yes'×279; 'yes'×6; 'No'×4; 'Nonexistent'×1 | 1B-1 · 1_meetings — *Inclusive Structure and Participation–Participation in Coord* |
| `1b_1_1_voted` | Affordable Housing Developer(s) | Voted, Including Electing CoC Board Members | label | 'Yes'×248; 'No'×37; 'yes'×3; 'no'×2 | 1B-1 · 1_voted — *Inclusive Structure and Participation–Participation in Coord* |
| `1b_1_1_ces` | Affordable Housing Developer(s) | Participated in CoC's Coordinated Entry System | label | 'Yes'×221; 'No'×64; 'yes'×5 | 1B-1 · 1_ces — *Inclusive Structure and Participation–Participation in Coord* |
| `1b_1_2_meetings` | CDBG/HOME/ESG Entitlement Jurisdiction | Participated in CoC Meetings | label | 'Yes'×268; 'Nonexistent'×10; 'yes'×6; 'No'×5; '`Yes'×1 | 1B-1 · 2_meetings — *Inclusive Structure and Participation–Participation in Coord* |
| `1b_1_2_voted` | CDBG/HOME/ESG Entitlement Jurisdiction | Voted, Including Electing CoC Board Members | label | 'Yes'×256; 'No'×27; 'yes'×6; 'no'×1 | 1B-1 · 2_voted — *Inclusive Structure and Participation–Participation in Coord* |
| `1b_1_2_ces` | CDBG/HOME/ESG Entitlement Jurisdiction | Participated in CoC's Coordinated Entry System | label | 'Yes'×236; 'No'×47; 'yes'×6 | 1B-1 · 2_ces — *Inclusive Structure and Participation–Participation in Coord* |
| `1b_1_3_meetings` | Disability Advocates | Participated in CoC Meetings | label | 'Yes'×273; 'No'×7; 'yes'×5; 'Nonexistent'×2; 'Y'×2 | 1B-1 · 3_meetings — *Inclusive Structure and Participation–Participation in Coord* |
| `1b_1_3_voted` | Disability Advocates | Voted, Including Electing CoC Board Members | label | 'Yes'×244; 'No'×34; 'yes'×5; 'Y'×4; 'Yed'×2 | 1B-1 · 3_voted — *Inclusive Structure and Participation–Participation in Coord* |
| `1b_1_3_ces` | Disability Advocates | Participated in CoC's Coordinated Entry System | label | 'Yes'×237; 'No'×48; 'yes'×4 | 1B-1 · 3_ces — *Inclusive Structure and Participation–Participation in Coord* |
| `1b_1_4_meetings` | Disability Service Organizations | Participated in CoC Meetings | label | 'Yes'×277; 'No'×7; 'yes'×5 | 1B-1 · 4_meetings — *Inclusive Structure and Participation–Participation in Coord* |
| `1b_1_4_voted` | Disability Service Organizations | Voted, Including Electing CoC Board Members | label | 'Yes'×246; 'No'×34; 'yes'×4; 'Yed'×3; 'Y'×2 | 1B-1 · 4_voted — *Inclusive Structure and Participation–Participation in Coord* |
| `1b_1_4_ces` | Disability Service Organizations | Participated in CoC's Coordinated Entry System | label | 'Yes'×245; 'No'×40; 'yes'×4 | 1B-1 · 4_ces — *Inclusive Structure and Participation–Participation in Coord* |
| `1b_1_5_meetings` | EMS/Crisis Response Team(s) | Participated in CoC Meetings | label | 'Yes'×243; 'No'×40; 'yes'×5; 'Nonexistent'×1 | 1B-1 · 5_meetings — *Inclusive Structure and Participation–Participation in Coord* |
| `1b_1_5_voted` | EMS/Crisis Response Team(s) | Voted, Including Electing CoC Board Members | label | 'Yes'×191; 'No'×93; 'no'×3; 'yes'×2 | 1B-1 · 5_voted — *Inclusive Structure and Participation–Participation in Coord* |
| `1b_1_5_ces` | EMS/Crisis Response Team(s) | Participated in CoC's Coordinated Entry System | label | 'Yes'×181; 'No'×103; 'yes'×5 | 1B-1 · 5_ces — *Inclusive Structure and Participation–Participation in Coord* |
| `1b_1_6_meetings` | Homeless or Formerly Homeless Persons | Participated in CoC Meetings | label | 'Yes'×281; 'yes'×6; 'No'×1 | 1B-1 · 6_meetings — *Inclusive Structure and Participation–Participation in Coord* |
| `1b_1_6_voted` | Homeless or Formerly Homeless Persons | Voted, Including Electing CoC Board Members | label | 'Yes'×279; 'yes'×5; 'No'×3; 'YEs'×1 | 1B-1 · 6_voted — *Inclusive Structure and Participation–Participation in Coord* |
| `1b_1_6_ces` | Homeless or Formerly Homeless Persons | Participated in CoC's Coordinated Entry System | label | 'Yes'×259; 'No'×23; 'yes'×5; 'NO'×1 | 1B-1 · 6_ces — *Inclusive Structure and Participation–Participation in Coord* |
| `1b_1_7_meetings` | Hospital(s) | Participated in CoC Meetings | label | 'Yes'×253; 'No'×29; 'yes'×4; 'N'×1; 'no'×1 | 1B-1 · 7_meetings — *Inclusive Structure and Participation–Participation in Coord* |
| `1b_1_7_voted` | Hospital(s) | Voted, Including Electing CoC Board Members | label | 'Yes'×194; 'No'×90; 'no'×2; 'yes'×2 | 1B-1 · 7_voted — *Inclusive Structure and Participation–Participation in Coord* |
| `1b_1_7_ces` | Hospital(s) | Participated in CoC's Coordinated Entry System | label | 'Yes'×185; 'No'×97; 'yes'×5 | 1B-1 · 7_ces — *Inclusive Structure and Participation–Participation in Coord* |
| `1b_1_8_meetings` | Indian Tribes and Tribally Designated Housing Entities (TDHEs) (Tribal Organizations) | Participated in CoC Meetings | label | 'Nonexistent'×178; 'Yes'×65; 'No'×40; 'N'×2; 'yes'×1 | 1B-1 · 8_meetings — *Inclusive Structure and Participation–Participation in Coord* |
| `1b_1_8_voted` | Indian Tribes and Tribally Designated Housing Entities (TDHEs) (Tribal Organizations) | Voted, Including Electing CoC Board Members | label | 'No'×245; 'Yes'×39; 'no'×3; 'yes'×1 | 1B-1 · 8_voted — *Inclusive Structure and Participation–Participation in Coord* |
| `1b_1_8_ces` | Indian Tribes and Tribally Designated Housing Entities (TDHEs) (Tribal Organizations) | Participated in CoC's Coordinated Entry System | label | 'No'×238; 'Yes'×43; 'no'×5; 'yes'×1; 'NO'×1 | 1B-1 · 8_ces — *Inclusive Structure and Participation–Participation in Coord* |
| `1b_1_9_meetings` | Law Enforcement | Participated in CoC Meetings | label | 'Yes'×246; 'No'×38; 'yes'×4 | 1B-1 · 9_meetings — *Inclusive Structure and Participation–Participation in Coord* |
| `1b_1_9_voted` | Law Enforcement | Voted, Including Electing CoC Board Members | label | 'Yes'×162; 'No'×122; 'yes'×2; 'no'×2 | 1B-1 · 9_voted — *Inclusive Structure and Participation–Participation in Coord* |
| `1b_1_9_ces` | Law Enforcement | Participated in CoC's Coordinated Entry System | label | 'Yes'×180; 'No'×102; 'yes'×5; 'NO'×1 | 1B-1 · 9_ces — *Inclusive Structure and Participation–Participation in Coord* |
| `1b_1_10_meetings` | Lesbian, Gay, Bisexual, Transgender (LGBTQ+) Advocates | Participated in CoC Meetings | label | 'Yes'×270; 'No'×14; 'yes'×4 | 1B-1 · 10_meetings — *Inclusive Structure and Participation–Participation in Coord* |
| `1b_1_10_voted` | Lesbian, Gay, Bisexual, Transgender (LGBTQ+) Advocates | Voted, Including Electing CoC Board Members | label | 'Yes'×245; 'No'×39; 'yes'×4 | 1B-1 · 10_voted — *Inclusive Structure and Participation–Participation in Coord* |
| `1b_1_10_ces` | Lesbian, Gay, Bisexual, Transgender (LGBTQ+) Advocates | Participated in CoC's Coordinated Entry System | label | 'Yes'×232; 'No'×50; 'yes'×4; 'Yez'×1; 'Y'×1 | 1B-1 · 10_ces — *Inclusive Structure and Participation–Participation in Coord* |
| `1b_1_11_meetings` | LGBTQ+ Service Organizations | Participated in CoC Meetings | label | 'Yes'×243; 'No'×23; 'Nonexistent'×15; 'yes'×4; 'N'×1 | 1B-1 · 11_meetings — *Inclusive Structure and Participation–Participation in Coord* |
| `1b_1_11_voted` | LGBTQ+ Service Organizations | Voted, Including Electing CoC Board Members | label | 'Yes'×202; 'No'×79; 'yes'×3; 'no'×2; 'NO'×2 | 1B-1 · 11_voted — *Inclusive Structure and Participation–Participation in Coord* |
| `1b_1_11_ces` | LGBTQ+ Service Organizations | Participated in CoC's Coordinated Entry System | label | 'Yes'×203; 'No'×81; 'yes'×3 | 1B-1 · 11_ces — *Inclusive Structure and Participation–Participation in Coord* |
| `1b_1_12_meetings` | Local Government Staff/Officials | Participated in CoC Meetings | label | 'Yes'×279; 'yes'×4; 'No'×3; 'YES'×1 | 1B-1 · 12_meetings — *Inclusive Structure and Participation–Participation in Coord* |
| `1b_1_12_voted` | Local Government Staff/Officials | Voted, Including Electing CoC Board Members | label | 'Yes'×266; 'No'×16; 'yes'×2; 'N'×1; 'no'×1 | 1B-1 · 12_voted — *Inclusive Structure and Participation–Participation in Coord* |
| `1b_1_12_ces` | Local Government Staff/Officials | Participated in CoC's Coordinated Entry System | label | 'Yes'×244; 'No'×39; 'yes'×3; 'YES'×1 | 1B-1 · 12_ces — *Inclusive Structure and Participation–Participation in Coord* |
| `1b_1_13_meetings` | Local Jail(s) | Participated in CoC Meetings | label | 'Yes'×190; 'No'×89; 'Nonexistent'×3; 'no'×3; 'N'×1 | 1B-1 · 13_meetings — *Inclusive Structure and Participation–Participation in Coord* |
| `1b_1_13_voted` | Local Jail(s) | Voted, Including Electing CoC Board Members | label | 'No'×177; 'Yes'×104; 'no'×4; 'yes'×1; 'NO'×1 | 1B-1 · 13_voted — *Inclusive Structure and Participation–Participation in Coord* |
| `1b_1_13_ces` | Local Jail(s) | Participated in CoC's Coordinated Entry System | label | 'Yes'×146; 'No'×137; 'no'×2; 'yes'×1; 'YEs'×1 | 1B-1 · 13_ces — *Inclusive Structure and Participation–Participation in Coord* |
| `1b_1_14_meetings` | Mental Health Service Organizations | Participated in CoC Meetings | label | 'Yes'×283; 'yes'×3; 'No'×1 | 1B-1 · 14_meetings — *Inclusive Structure and Participation–Participation in Coord* |
| `1b_1_14_voted` | Mental Health Service Organizations | Voted, Including Electing CoC Board Members | label | 'Yes'×273; 'No'×7; 'Y'×3; 'yes'×3; 'y'×1 | 1B-1 · 14_voted — *Inclusive Structure and Participation–Participation in Coord* |
| `1b_1_14_ces` | Mental Health Service Organizations | Participated in CoC's Coordinated Entry System | label | 'Yes'×271; 'No'×13; 'yes'×3 | 1B-1 · 14_ces — *Inclusive Structure and Participation–Participation in Coord* |
| `1b_1_15_meetings` | Mental Illness Advocates | Participated in CoC Meetings | label | 'Yes'×279; 'yes'×3; 'No'×2; 'Y'×2; 'y'×1 | 1B-1 · 15_meetings — *Inclusive Structure and Participation–Participation in Coord* |
| `1b_1_15_voted` | Mental Illness Advocates | Voted, Including Electing CoC Board Members | label | 'Yes'×265; 'No'×19; 'yes'×3 | 1B-1 · 15_voted — *Inclusive Structure and Participation–Participation in Coord* |
| `1b_1_15_ces` | Mental Illness Advocates | Participated in CoC's Coordinated Entry System | label | 'Yes'×253; 'No'×31; 'yes'×3 | 1B-1 · 15_ces — *Inclusive Structure and Participation–Participation in Coord* |
| `1b_1_16_meetings` | Organizations led by and serving Black, Brown, Indigenous and other People of Color | Participated in CoC Meetings | label | 'Yes'×271; 'No'×11; 'yes'×3; 'Nonexistent'×2 | 1B-1 · 16_meetings — *Inclusive Structure and Participation–Participation in Coord* |
| `1b_1_16_voted` | Organizations led by and serving Black, Brown, Indigenous and other People of Color | Voted, Including Electing CoC Board Members | label | 'Yes'×249; 'No'×34; 'yes'×3; 'YES'×1 | 1B-1 · 16_voted — *Inclusive Structure and Participation–Participation in Coord* |
| `1b_1_16_ces` | Organizations led by and serving Black, Brown, Indigenous and other People of Color | Participated in CoC's Coordinated Entry System | label | 'Yes'×244; 'No'×40; 'yes'×3 | 1B-1 · 16_ces — *Inclusive Structure and Participation–Participation in Coord* |
| `1b_1_17_meetings` | Organizations led by and serving LGBTQ+ persons | Participated in CoC Meetings | label | 'Yes'×250; 'No'×27; 'Nonexistent'×6; 'yes'×3; 'N o'×1 | 1B-1 · 17_meetings — *Inclusive Structure and Participation–Participation in Coord* |
| `1b_1_17_voted` | Organizations led by and serving LGBTQ+ persons | Voted, Including Electing CoC Board Members | label | 'Yes'×213; 'No'×71; 'yes'×3 | 1B-1 · 17_voted — *Inclusive Structure and Participation–Participation in Coord* |
| `1b_1_17_ces` | Organizations led by and serving LGBTQ+ persons | Participated in CoC's Coordinated Entry System | label | 'Yes'×212; 'No'×72; 'yes'×3 | 1B-1 · 17_ces — *Inclusive Structure and Participation–Participation in Coord* |
| `1b_1_18_meetings` | Organizations led by and serving people with disabilities | Participated in CoC Meetings | label | 'Yes'×247; 'No'×27; 'Nonexistent'×9; 'yes'×2; 'nonexistent'×1 | 1B-1 · 18_meetings — *Inclusive Structure and Participation–Participation in Coord* |
| `1b_1_18_voted` | Organizations led by and serving people with disabilities | Voted, Including Electing CoC Board Members | label | 'Yes'×207; 'No'×77; 'yes'×2; 'no'×1 | 1B-1 · 18_voted — *Inclusive Structure and Participation–Participation in Coord* |
| `1b_1_18_ces` | Organizations led by and serving people with disabilities | Participated in CoC's Coordinated Entry System | label | 'Yes'×211; 'No'×72; 'yes'×2; 'no'×1; 'YEs'×1 | 1B-1 · 18_ces — *Inclusive Structure and Participation–Participation in Coord* |
| `1b_1_19_meetings` | Other homeless subpopulation advocates | Participated in CoC Meetings | label | 'Yes'×271; 'No'×6; 'Nonexistent'×5; 'yes'×3; 'Y'×2 | 1B-1 · 19_meetings — *Inclusive Structure and Participation–Participation in Coord* |
| `1b_1_19_voted` | Other homeless subpopulation advocates | Voted, Including Electing CoC Board Members | label | 'Yes'×268; 'No'×14; 'yes'×3; 'Y'×2 | 1B-1 · 19_voted — *Inclusive Structure and Participation–Participation in Coord* |
| `1b_1_19_ces` | Other homeless subpopulation advocates | Participated in CoC's Coordinated Entry System | label | 'Yes'×253; 'No'×30; 'yes'×3; 'YEs'×1 | 1B-1 · 19_ces — *Inclusive Structure and Participation–Participation in Coord* |
| `1b_1_20_meetings` | Public Housing Authorities | Participated in CoC Meetings | label | 'Yes'×275; 'No'×8; 'yes'×3; 'Nonexistent'×1 | 1B-1 · 20_meetings — *Inclusive Structure and Participation–Participation in Coord* |
| `1b_1_20_voted` | Public Housing Authorities | Voted, Including Electing CoC Board Members | label | 'Yes'×248; 'No'×36; 'yes'×3 | 1B-1 · 20_voted — *Inclusive Structure and Participation–Participation in Coord* |
| `1b_1_20_ces` | Public Housing Authorities | Participated in CoC's Coordinated Entry System | label | 'Yes'×246; 'No'×37; 'yes'×4 | 1B-1 · 20_ces — *Inclusive Structure and Participation–Participation in Coord* |
| `1b_1_21_meetings` | School Administrators/Homeless Liaisons | Participated in CoC Meetings | label | 'Yes'×268; 'No'×15; 'yes'×2; 'no'×1; 'YEs'×1 | 1B-1 · 21_meetings — *Inclusive Structure and Participation–Participation in Coord* |
| `1b_1_21_voted` | School Administrators/Homeless Liaisons | Voted, Including Electing CoC Board Members | label | 'Yes'×214; 'No'×70; 'yes'×2; 'no'×1 | 1B-1 · 21_voted — *Inclusive Structure and Participation–Participation in Coord* |
| `1b_1_21_ces` | School Administrators/Homeless Liaisons | Participated in CoC's Coordinated Entry System | label | 'Yes'×212; 'No'×70; 'yes'×2; 'NO'×2; 'no'×1 | 1B-1 · 21_ces — *Inclusive Structure and Participation–Participation in Coord* |
| `1b_1_22_meetings` | Street Outreach Team(s) | Participated in CoC Meetings | label | 'Yes'×281; 'yes'×3; 'No'×2; 'Nonexistent'×1 | 1B-1 · 22_meetings — *Inclusive Structure and Participation–Participation in Coord* |
| `1b_1_22_voted` | Street Outreach Team(s) | Voted, Including Electing CoC Board Members | label | 'Yes'×271; 'No'×13; 'yes'×3 | 1B-1 · 22_voted — *Inclusive Structure and Participation–Participation in Coord* |
| `1b_1_22_ces` | Street Outreach Team(s) | Participated in CoC's Coordinated Entry System | label | 'Yes'×277; 'No'×7; 'yes'×3 | 1B-1 · 22_ces — *Inclusive Structure and Participation–Participation in Coord* |
| `1b_1_23_meetings` | Substance Abuse Advocates | Participated in CoC Meetings | label | 'Yes'×276; 'No'×5; 'Nonexistent'×3; 'yes'×3 | 1B-1 · 23_meetings — *Inclusive Structure and Participation–Participation in Coord* |
| `1b_1_23_voted` | Substance Abuse Advocates | Voted, Including Electing CoC Board Members | label | 'Yes'×260; 'No'×23; 'yes'×4 | 1B-1 · 23_voted — *Inclusive Structure and Participation–Participation in Coord* |
| `1b_1_23_ces` | Substance Abuse Advocates | Participated in CoC's Coordinated Entry System | label | 'Yes'×245; 'No'×38; 'yes'×3; 'y'×1 | 1B-1 · 23_ces — *Inclusive Structure and Participation–Participation in Coord* |
| `1b_1_24_meetings` | Substance Abuse Service Organizations | Participated in CoC Meetings | label | 'Yes'×279; 'No'×5; 'yes'×3 | 1B-1 · 24_meetings — *Inclusive Structure and Participation–Participation in Coord* |
| `1b_1_24_voted` | Substance Abuse Service Organizations | Voted, Including Electing CoC Board Members | label | 'Yes'×261; 'No'×23; 'yes'×2; 'no'×1 | 1B-1 · 24_voted — *Inclusive Structure and Participation–Participation in Coord* |
| `1b_1_24_ces` | Substance Abuse Service Organizations | Participated in CoC's Coordinated Entry System | label | 'Yes'×259; 'No'×25; 'yes'×3 | 1B-1 · 24_ces — *Inclusive Structure and Participation–Participation in Coord* |
| `1b_1_25_meetings` | Agencies Serving Survivors of Human Trafficking | Participated in CoC Meetings | label | 'Yes'×274; 'No'×7; 'Nonexistent'×3; 'yes'×3 | 1B-1 · 25_meetings — *Inclusive Structure and Participation–Participation in Coord* |
| `1b_1_25_voted` | Agencies Serving Survivors of Human Trafficking | Voted, Including Electing CoC Board Members | label | 'Yes'×258; 'No'×26; 'yes'×3 | 1B-1 · 25_voted — *Inclusive Structure and Participation–Participation in Coord* |
| `1b_1_25_ces` | Agencies Serving Survivors of Human Trafficking | Participated in CoC's Coordinated Entry System | label | 'Yes'×250; 'No'×34; 'yes'×3 | 1B-1 · 25_ces — *Inclusive Structure and Participation–Participation in Coord* |
| `1b_1_26_meetings` | Victim Service Providers | Participated in CoC Meetings | label | 'Yes'×281; 'yes'×3; 'Nonexistent'×2; 'No'×1 | 1B-1 · 26_meetings — *Inclusive Structure and Participation–Participation in Coord* |
| `1b_1_26_voted` | Victim Service Providers | Voted, Including Electing CoC Board Members | label | 'Yes'×275; 'No'×9; 'yes'×3 | 1B-1 · 26_voted — *Inclusive Structure and Participation–Participation in Coord* |
| `1b_1_26_ces` | Victim Service Providers | Participated in CoC's Coordinated Entry System | label | 'Yes'×268; 'No'×16; 'yes'×3 | 1B-1 · 26_ces — *Inclusive Structure and Participation–Participation in Coord* |
| `1b_1_27_meetings` | Domestic Violence Advocates | Participated in CoC Meetings | label | 'Yes'×281; 'yes'×3; 'No'×2; 'yy'×1 | 1B-1 · 27_meetings — *Inclusive Structure and Participation–Participation in Coord* |
| `1b_1_27_voted` | Domestic Violence Advocates | Voted, Including Electing CoC Board Members | label | 'Yes'×273; 'No'×11; 'yes'×3 | 1B-1 · 27_voted — *Inclusive Structure and Participation–Participation in Coord* |
| `1b_1_27_ces` | Domestic Violence Advocates | Participated in CoC's Coordinated Entry System | label | 'Yes'×257; 'No'×27; 'yes'×3 | 1B-1 · 27_ces — *Inclusive Structure and Participation–Participation in Coord* |
| `1b_1_28_meetings` | Other Victim Service Organizations | Participated in CoC Meetings | label | 'Yes'×235; 'No'×27; 'Nonexistent'×22; 'yes'×2; 'nonexistent'×1 | 1B-1 · 28_meetings — *Inclusive Structure and Participation–Participation in Coord* |
| `1b_1_28_voted` | Other Victim Service Organizations | Voted, Including Electing CoC Board Members | label | 'Yes'×214; 'No'×70; 'yes'×2; 'no'×1 | 1B-1 · 28_voted — *Inclusive Structure and Participation–Participation in Coord* |
| `1b_1_28_ces` | Other Victim Service Organizations | Participated in CoC's Coordinated Entry System | label | 'Yes'×202; 'No'×82; 'yes'×2; 'no'×1 | 1B-1 · 28_ces — *Inclusive Structure and Participation–Participation in Coord* |
| `1b_1_29_meetings` | State Domestic Violence Coalition | Participated in CoC Meetings | label | 'Yes'×191; 'No'×84; 'Nonexistent'×9; 'yes'×2; 'no'×1 | 1B-1 · 29_meetings — *Inclusive Structure and Participation–Participation in Coord* |
| `1b_1_29_voted` | State Domestic Violence Coalition | Voted, Including Electing CoC Board Members | label | 'No'×146; 'Yes'×137; 'yes'×2; 'Nonexistent'×1; 'no'×1 | 1B-1 · 29_voted — *Inclusive Structure and Participation–Participation in Coord* |
| `1b_1_29_ces` | State Domestic Violence Coalition | Participated in CoC's Coordinated Entry System | label | 'No'×148; 'Yes'×135; 'yes'×2; 'no'×1; 'NO'×1 | 1B-1 · 29_ces — *Inclusive Structure and Participation–Participation in Coord* |
| `1b_1_30_meetings` | State Sexual Assault Coalition | Participated in CoC Meetings | label | 'Yes'×166; 'No'×110; 'Nonexistent'×8; 'yes'×2; 'no'×1 | 1B-1 · 30_meetings — *Inclusive Structure and Participation–Participation in Coord* |
| `1b_1_30_voted` | State Sexual Assault Coalition | Voted, Including Electing CoC Board Members | label | 'No'×166; 'Yes'×116; 'yes'×2; ''×1; 'Nonexistent'×1 | 1B-1 · 30_voted — *Inclusive Structure and Participation–Participation in Coord* |
| `1b_1_30_ces` | State Sexual Assault Coalition | Participated in CoC's Coordinated Entry System | label | 'No'×160; 'Yes'×123; 'yes'×2; 'no'×1; 'NO'×1 | 1B-1 · 30_ces — *Inclusive Structure and Participation–Participation in Coord* |
| `1b_1_31_meetings` | Youth Advocates | Participated in CoC Meetings | label | 'Yes'×278; 'No'×5; 'yes'×3; 'Nonexistent'×1 | 1B-1 · 31_meetings — *Inclusive Structure and Participation–Participation in Coord* |
| `1b_1_31_voted` | Youth Advocates | Voted, Including Electing CoC Board Members | label | 'Yes'×261; 'No'×21; 'yes'×3; 'YEs'×2 | 1B-1 · 31_voted — *Inclusive Structure and Participation–Participation in Coord* |
| `1b_1_31_ces` | Youth Advocates | Participated in CoC's Coordinated Entry System | label | 'Yes'×254; 'No'×29; 'yes'×3; 'Empty'×1 | 1B-1 · 31_ces — *Inclusive Structure and Participation–Participation in Coord* |
| `1b_1_32_meetings` | Youth Homeless Organizations | Participated in CoC Meetings | label | 'Yes'×262; 'Nonexistent'×18; 'No'×5; 'yes'×2 | 1B-1 · 32_meetings — *Inclusive Structure and Participation–Participation in Coord* |
| `1b_1_32_voted` | Youth Homeless Organizations | Voted, Including Electing CoC Board Members | label | 'Yes'×243; 'No'×41; 'yes'×2; 'no'×1 | 1B-1 · 32_voted — *Inclusive Structure and Participation–Participation in Coord* |
| `1b_1_32_ces` | Youth Homeless Organizations | Participated in CoC's Coordinated Entry System | label | 'Yes'×251; 'No'×33; 'yes'×2; 'no'×1 | 1B-1 · 32_ces — *Inclusive Structure and Participation–Participation in Coord* |
| `1b_1_33_meetings` | Youth Service Providers | Participated in CoC Meetings | label | 'Yes'×280; 'yes'×4; 'Nonexistent'×3 | 1B-1 · 33_meetings — *Inclusive Structure and Participation–Participation in Coord* |
| `1b_1_33_voted` | Youth Service Providers | Voted, Including Electing CoC Board Members | label | 'Yes'×264; 'No'×20; 'yes'×3 | 1B-1 · 33_voted — *Inclusive Structure and Participation–Participation in Coord* |
| `1b_1_33_ces` | Youth Service Providers | Participated in CoC's Coordinated Entry System | label | 'Yes'×266; 'No'×18; 'yes'×3; ''×1 | 1B-1 · 33_ces — *Inclusive Structure and Participation–Participation in Coord* |

## (uncategorized)

| field_id | sub-group | label | type | observed domain | likely Q (FY2024) |
|---|---|---|---|---|---|
| `1b_1a` |  |  | narrative | avg_chars~1835; examples trimmed | 1B-1a — *Experience Promoting Racial Equity.* |
| `1b_2` |  |  | narrative | avg_chars~2154; examples trimmed | 1B-2 — *Open Invitation for New Members.* |
| `1b_3` |  |  | narrative | avg_chars~2286; examples trimmed | 1B-3 — *CoC’s Strategy to Solicit/Consider Opinions on Preventing an* |
| `1b_4` |  |  | narrative | avg_chars~2215; examples trimmed | 1B-4 — *Public Notification for Proposals from Organizations Not Pre* |
| `1c_1_1` |  |  | label | 'Yes'×233; 'Nonexistent'×28; 'No'×21; 'yes'×2; 'no'×1 | 1C-1 · 1 — *Coordination with Federal, State, Local, Private, and Other * |
| `1c_1_2` |  |  | label | 'Yes'×235; 'No'×46; 'yes'×3; 'n'×1 | 1C-1 · 2 — *Coordination with Federal, State, Local, Private, and Other * |
| `1c_1_3` |  |  | label | 'Yes'×277; 'yes'×3; 'Nonexistent'×2; 'y'×2; 'YEs'×1 | 1C-1 · 3 — *Coordination with Federal, State, Local, Private, and Other * |
| `1c_1_4` |  |  | label | 'Yes'×281; 'yes'×3; 'No'×1 | 1C-1 · 4 — *Coordination with Federal, State, Local, Private, and Other * |
| `1c_1_5` |  |  | label | 'Yes'×270; 'No'×10; 'yes'×3; 'Nonexistent'×2 | 1C-1 · 5 — *Coordination with Federal, State, Local, Private, and Other * |
| `1c_1_6` |  |  | label | 'Yes'×280; 'yes'×3; 'No'×1; 'Nonexistent'×1 | 1C-1 · 6 — *Coordination with Federal, State, Local, Private, and Other * |
| `1c_1_7` |  |  | label | 'Yes'×268; 'No'×10; 'yes'×4; 'Nonexistent'×3 | 1C-1 · 7 — *Coordination with Federal, State, Local, Private, and Other * |
| `1c_1_8` |  |  | label | 'Yes'×249; 'No'×22; 'Nonexistent'×11; 'yes'×2; 'v'×1 | 1C-1 · 8 — *Coordination with Federal, State, Local, Private, and Other * |
| `1c_1_9` |  |  | label | 'Yes'×240; 'Nonexistent'×31; 'No'×10; 'yes'×3; 'Nonexsistent'×1 | 1C-1 · 9 — *Coordination with Federal, State, Local, Private, and Other * |
| `1c_1_10` |  |  | label | 'Nonexistent'×176; 'Yes'×70; 'No'×36; 'N'×1; 'yes'×1 | 1C-1 · 10 — *Coordination with Federal, State, Local, Private, and Other * |
| `1c_1_11` |  |  | label | 'Yes'×271; 'No'×11; 'yes'×3 | 1C-1 · 11 — *Coordination with Federal, State, Local, Private, and Other * |
| `1c_1_12` |  |  | label | 'Yes'×261; 'No'×13; 'Nonexistent'×8; 'yes'×3 | 1C-1 · 12 — *Coordination with Federal, State, Local, Private, and Other * |
| `1c_1_13` |  |  | label | 'Yes'×261; 'No'×13; 'Nonexistent'×8; 'yes'×2; 'nonexistent'×1 | 1C-1 · 13 — *Coordination with Federal, State, Local, Private, and Other * |
| `1c_1_14` |  |  | label | 'Yes'×258; 'No'×22; 'yes'×3; 'YEs'×1; 'Nonexistent'×1 | 1C-1 · 14 — *Coordination with Federal, State, Local, Private, and Other * |
| `1c_1_15` |  |  | label | 'Yes'×275; 'No'×5; 'yes'×3; 'Nonexistent'×2 | 1C-1 · 15 — *Coordination with Federal, State, Local, Private, and Other * |
| `1c_1_16` |  |  | label | 'Yes'×221; 'Nonexistent'×49; 'No'×11; 'Nonexsistent'×2; 'YES'×1 | 1C-1 · 16 — *Coordination with Federal, State, Local, Private, and Other * |
| `1c_1_17` |  |  | label | 'Yes'×263; 'No'×16; 'Nonexistent'×3; 'yes'×3 | 1C-1 · 17 — *Coordination with Federal, State, Local, Private, and Other * |
| `1c_2_1` |  |  | label | 'Yes'×277; 'No'×4; 'yes'×3; '1. The County of Hudson and City of Jersey City are the only direct ESG\nrecipients in the CoC’s areas and together they chair the HCAEH. ESG/CoC\nprogram staff from both entities participate in each jurisdiction’s application and\nreview committee for funding allocations for ESG & CoC. This coordination\nallows for funding decisions that best utilize the different funding sources\navailable. The State of NJ also provides ESG funds within the CoC area and\nrequires HCAEH approval, through letters of support, for all ESG priority\nprojects. The CoC also provides comment on how the State uses its ESG\nfunding through the public comment period.'×1 | 1C-2 · 1 — *CoC Consultation with ESG Program Recipients.* |
| `1c_2_2` |  |  | label | 'Yes'×280; 'yes'×3; 'No'×1 | 1C-2 · 2 — *CoC Consultation with ESG Program Recipients.* |
| `1c_2_3` |  |  | label | 'Yes'×280; 'yes'×3; 'No'×1 | 1C-2 · 3 — *CoC Consultation with ESG Program Recipients.* |
| `1c_2_4` |  |  | label | 'Yes'×275; 'No'×5; 'yes'×3; 'YEs'×1 | 1C-2 · 4 — *CoC Consultation with ESG Program Recipients.* |
| `1c_3_1` |  |  | label | 'Yes'×196; 'No'×86; 'yes'×2; 'no'×1 | 1C-3 · 1 — *Ensuring Families are not Separated.* |
| `1c_3_2` |  |  | label | 'Yes'×210; 'No'×71; 'yes'×3; 'YEs'×1 | 1C-3 · 2 — *Ensuring Families are not Separated.* |
| `1c_3_3` |  |  | label | 'Yes'×270; 'No'×12; 'yes'×3 | 1C-3 · 3 — *Ensuring Families are not Separated.* |
| `1c_3_4` |  |  | label | 'Yes'×251; 'No'×31; 'yes'×3 | 1C-3 · 4 — *Ensuring Families are not Separated.* |
| `1c_3_5` |  |  | label | 'No'×166; 'Yes'×115; 'yes'×2; 'no'×1; 'YEs'×1 | 1C-3 · 5 — *Ensuring Families are not Separated.* |
| `1c_4_1` |  |  | label | 'Yes'×275; 'No'×7; 'yes'×3 | 1C-4 · 1 — *CoC Collaboration Related to Children and Youth–SEAs, LEAs, * |
| `1c_4_2` |  |  | label | 'Yes'×225; 'No'×57; 'yes'×3 | 1C-4 · 2 — *CoC Collaboration Related to Children and Youth–SEAs, LEAs, * |
| `1c_4_3` |  |  | label | 'Yes'×272; 'No'×10; 'yes'×3 | 1C-4 · 3 — *CoC Collaboration Related to Children and Youth–SEAs, LEAs, * |
| `1c_4_4` |  |  | label | 'Yes'×276; 'No'×6; 'yes'×3 | 1C-4 · 4 — *CoC Collaboration Related to Children and Youth–SEAs, LEAs, * |
| `1c_4a` |  |  | narrative | avg_chars~1747; examples trimmed | 1C-4a — *Formal Partnerships with Youth Education Providers, SEAs, LE* |
| `1c_4b` |  |  | narrative | avg_chars~1698; examples trimmed | 1C-4b — *Informing Individuals and Families Who Have Recently Begun E* |
| `1c_4c_1_mou` |  |  | label | 'No'×174; 'Yes'×107; 'yes'×2; 'no'×1; 'Empty'×1 | 1C-4c · 1_mou — *Written/Formal Agreements or Partnerships with Early Childho* |
| `1c_4c_1_oth` |  |  | label | 'Yes'×151; 'No'×131; 'yes'×2; 'no'×1 | 1C-4c · 1_oth — *Written/Formal Agreements or Partnerships with Early Childho* |
| `1c_4c_2_mou` |  |  | label | 'No'×224; 'Yes'×55; 'Y'×2; 'yes'×2; 'no'×1 | 1C-4c · 2_mou — *Written/Formal Agreements or Partnerships with Early Childho* |
| `1c_4c_2_oth` |  |  | label | 'No'×170; 'Yes'×109; 'yes'×2; 'YEs'×2; 'no'×1 | 1C-4c · 2_oth — *Written/Formal Agreements or Partnerships with Early Childho* |
| `1c_4c_3_mou` |  |  | label | 'No'×158; 'Yes'×123; 'yes'×2; 'no'×1; 'Empty'×1 | 1C-4c · 3_mou — *Written/Formal Agreements or Partnerships with Early Childho* |
| `1c_4c_3_oth` |  |  | label | 'Yes'×161; 'No'×121; 'yes'×2; 'no'×1 | 1C-4c · 3_oth — *Written/Formal Agreements or Partnerships with Early Childho* |
| `1c_4c_4_mou` |  |  | label | 'No'×150; 'Yes'×131; 'yes'×2; 'no'×1; 'Empty'×1 | 1C-4c · 4_mou — *Written/Formal Agreements or Partnerships with Early Childho* |
| `1c_4c_4_oth` |  |  | label | 'Yes'×165; 'No'×116; 'yes'×2; 'no'×1; 'YEs'×1 | 1C-4c · 4_oth — *Written/Formal Agreements or Partnerships with Early Childho* |
| `1c_4c_5_mou` |  |  | label | 'No'×222; 'Yes'×59; 'yes'×2; 'no'×1; 'Empty'×1 | 1C-4c · 5_mou — *Written/Formal Agreements or Partnerships with Early Childho* |
| `1c_4c_5_oth` |  |  | label | 'No'×184; 'Yes'×98; 'no'×2; 'yes'×1 | 1C-4c · 5_oth — *Written/Formal Agreements or Partnerships with Early Childho* |
| `1c_4c_6_mou` |  |  | label | 'No'×141; 'Yes'×140; 'yes'×2; 'no'×1; 'Empty'×1 | 1C-4c · 6_mou — *Written/Formal Agreements or Partnerships with Early Childho* |
| `1c_4c_6_oth` |  |  | label | 'Yes'×167; 'No'×114; 'yes'×2; 'no'×1; 'YEs'×1 | 1C-4c · 6_oth — *Written/Formal Agreements or Partnerships with Early Childho* |
| `1c_4c_7_mou` |  |  | label | 'No'×218; 'Yes'×62; 'no'×2; 'yes'×1; 'Y'×1 | 1C-4c · 7_mou — *Written/Formal Agreements or Partnerships with Early Childho* |
| `1c_4c_7_oth` |  |  | label | 'No'×174; 'Yes'×108; 'no'×3 | 1C-4c · 7_oth — *Written/Formal Agreements or Partnerships with Early Childho* |
| `1c_4c_8_mou` |  |  | label | 'No'×178; 'Yes'×103; 'yes'×2; 'no'×1; 'Empty'×1 | 1C-4c · 8_mou — *Written/Formal Agreements or Partnerships with Early Childho* |
| `1c_4c_8_oth` |  |  | label | 'Yes'×147; 'No'×135; 'yes'×2; 'no'×1 | 1C-4c · 8_oth — *Written/Formal Agreements or Partnerships with Early Childho* |
| `1c_4c_9_mou` |  |  | label | 'No'×270; 'Yes'×11; 'no'×3; 'Empty'×1 | 1C-4c · 9_mou — *Written/Formal Agreements or Partnerships with Early Childho* |
| `1c_4c_9_oth` |  |  | label | 'No'×265; 'Yes'×16; 'no'×2; 'yes'×1; 'NO'×1 | 1C-4c · 9_oth — *Written/Formal Agreements or Partnerships with Early Childho* |
| `1c_5_1` |  |  | label | 'Yes'×240; 'No'×42; 'yes'×2; 'no'×1 | 1C-5 · 1 — *Addressing Needs of Survivors of Domestic Violence, Dating V* |
| `1c_5_2` |  |  | label | 'Yes'×220; 'No'×62; 'yes'×2; 'no'×1 | 1C-5 · 2 — *Addressing Needs of Survivors of Domestic Violence, Dating V* |
| `1c_5_3` |  |  | label | 'Yes'×275; 'No'×7; 'yes'×3 | 1C-5 · 3 — *Addressing Needs of Survivors of Domestic Violence, Dating V* |
| `1c_5a` |  |  | narrative | avg_chars~1991; examples trimmed | 1C-5a — *Collaborating with Federally Funded Programs and Victim Serv* |
| `1c_5b` |  |  | narrative | avg_chars~1995; examples trimmed | 1C-5b — *Implemented Safety Planning, Confidentiality Protocols in Yo* |
| `1c_5c_1_proj` |  |  | label | 'Yes'×273; 'No'×8; 'yes'×3 | 1C-5c · 1_proj — *Coordinated Annual Training on Best Practices to Address the* |
| `1c_5c_1_ces` |  |  | label | 'Yes'×273; 'No'×8; 'yes'×3 | 1C-5c · 1_ces — *Coordinated Annual Training on Best Practices to Address the* |
| `1c_5c_2_proj` |  |  | label | 'Yes'×278; 'yes'×3; 'No'×3 | 1C-5c · 2_proj — *Coordinated Annual Training on Best Practices to Address the* |
| `1c_5c_2_ces` |  |  | label | 'Yes'×276; 'No'×5; 'yes'×3 | 1C-5c · 2_ces — *Coordinated Annual Training on Best Practices to Address the* |
| `1c_5c_3_proj` |  |  | label | 'Yes'×277; 'yes'×3; 'No'×2; 'yES'×1; 'YES'×1 | 1C-5c · 3_proj — *Coordinated Annual Training on Best Practices to Address the* |
| `1c_5c_3_ces` |  |  | label | 'Yes'×277; 'No'×4; 'yes'×3 | 1C-5c · 3_ces — *Coordinated Annual Training on Best Practices to Address the* |
| `1c_5c_4_proj` |  |  | label | 'Yes'×276; 'yes'×4; 'No'×2; 'YEs'×1; 'Y'×1 | 1C-5c · 4_proj — *Coordinated Annual Training on Best Practices to Address the* |
| `1c_5c_4_ces` |  |  | label | 'Yes'×275; 'No'×6; 'yes'×3 | 1C-5c · 4_ces — *Coordinated Annual Training on Best Practices to Address the* |
| `1c_5c_5_proj` |  |  | label | 'Yes'×279; 'yes'×3; 'No'×2 | 1C-5c · 5_proj — *Coordinated Annual Training on Best Practices to Address the* |
| `1c_5c_5_ces` |  |  | label | 'Yes'×275; 'No'×6; 'yes'×3 | 1C-5c · 5_ces — *Coordinated Annual Training on Best Practices to Address the* |
| `1c_5c_6_proj` |  |  | label | 'Yes'×277; 'No'×4; 'yes'×3 | 1C-5c · 6_proj — *Coordinated Annual Training on Best Practices to Address the* |
| `1c_5c_6_ces` |  |  | label | 'Yes'×274; 'No'×7; 'yes'×3 | 1C-5c · 6_ces — *Coordinated Annual Training on Best Practices to Address the* |
| `1c_5d` |  |  | narrative | avg_chars~2096; examples trimmed | 1C-5d — *Implemented VAWA-Required Written Emergency Transfer Plan Po* |
| `1c_5e` |  |  | narrative | avg_chars~1681; examples trimmed | 1C-5e — *Facilitating Safe Access to Housing and Services for Survivo* |
| `1c_5f` |  |  | narrative | avg_chars~1755; examples trimmed | 1C-5f — *Identifying and Removing Barriers for Survivors of Domestic * |
| `1c_6a` |  |  | narrative | avg_chars~2045; examples trimmed | 1C-6a — *Anti-Discrimination Policy–Updating Policies–Assisting Provi* |
| `1c_7_pha_name_1` |  |  | label | 'Michigan State Housing Development Authority'×6; 'NJ Dept of Community Affairs'×6; 'Empty'×4; 'Springfield Housing Authority'×3; 'Housing Authority of Alameda County'×2 | 1C-7 · pha_name_1 — *Public Housing Agencies within Your CoC’s Geographic Area–Ne* |
| `1c_7_ph_hhm_1` |  |  | label | 'Empty'×19; '0.0'×18; '0.25'×10; '1.0'×8; '0.1'×8 | 1C-7 · ph_hhm_1 — *Public Housing Agencies within Your CoC’s Geographic Area–Ne* |
| `1c_7_ph_limit_hhm_1` |  |  | label | 'Yes-Both'×112; 'Yes-HCV'×98; 'No'×47; 'Yes-Public Housing'×19; 'Empty'×5 | 1C-7 · ph_limit_hhm_1 — *Public Housing Agencies within Your CoC’s Geographic Area–Ne* |
| `1c_7_psh_1` |  |  | label | 'Yes'×142; 'No'×132; 'Empty'×7; 'yes'×2; 'no'×1 | 1C-7 · psh_1 — *Public Housing Agencies within Your CoC’s Geographic Area–Ne* |
| `1c_7_pha_name_2` |  |  | label | 'Empty'×66; 'NYS Housing Trust Fund Corporation'×7; 'Oklahoma Housing Finance Agency'×4; 'Oakland Housing Authority'×2; 'Shasta County Housing Authority'×2 | 1C-7 · pha_name_2 — *Public Housing Agencies within Your CoC’s Geographic Area–Ne* |
| `1c_7_ph_hhm_2` |  |  | label | 'Empty'×75; '0.0'×31; '1.0'×10; '0.05'×8; '0.34'×6 | 1C-7 · ph_hhm_2 — *Public Housing Agencies within Your CoC’s Geographic Area–Ne* |
| `1c_7_ph_limit_hhm_2` |  |  | label | 'Yes-HCV'×78; 'Empty'×67; 'Yes-Both'×56; 'No'×55; 'Yes-Public Housing'×13 | 1C-7 · ph_limit_hhm_2 — *Public Housing Agencies within Your CoC’s Geographic Area–Ne* |
| `1c_7_psh_2` |  |  | label | 'No'×142; 'Empty'×67; 'Yes'×62; 'yes'×1; 'no'×1 | 1C-7 · psh_2 — *Public Housing Agencies within Your CoC’s Geographic Area–Ne* |
| `1c_7a` |  |  | narrative | avg_chars~1505; examples trimmed | 1C-7a — *Written Policies on Homeless Admission Preferences with PHAs* |
| `1c_7b_1` |  |  | label | 'Yes'×167; 'No'×114; 'yes'×3; 'no'×1 | 1C-7b · 1 — *Moving On Strategy with Affordable Housing Providers.* |
| `1c_7b_2` |  |  | label | 'Yes'×257; 'No'×24; 'yes'×4 | 1C-7b · 2 — *Moving On Strategy with Affordable Housing Providers.* |
| `1c_7b_3` |  |  | label | 'Yes'×222; 'No'×57; 'yes'×3; 'Empty'×1; 'NO'×1 | 1C-7b · 3 — *Moving On Strategy with Affordable Housing Providers.* |
| `1c_7b_4` |  |  | label | 'Yes'×223; 'No'×58; 'yes'×3; 'Empty'×1 | 1C-7b · 4 — *Moving On Strategy with Affordable Housing Providers.* |
| `1c_7c_1` |  |  | label | 'Yes'×256; 'No'×26; 'yes'×2; 'no'×1 | 1C-7c · 1 — *Include Units from PHA Administered Programs in Your CoC’s C* |
| `1c_7c_2` |  |  | label | 'No'×168; 'Yes'×114; 'no'×2; 'yes'×1 | 1C-7c · 2 — *Include Units from PHA Administered Programs in Your CoC’s C* |
| `1c_7c_3` |  |  | label | 'Yes'×184; 'No'×98; 'yes'×2; 'no'×1 | 1C-7c · 3 — *Include Units from PHA Administered Programs in Your CoC’s C* |
| `1c_7c_4` |  |  | label | 'Yes'×215; 'No'×67; 'yes'×3 | 1C-7c · 4 — *Include Units from PHA Administered Programs in Your CoC’s C* |
| `1c_7c_5` |  |  | label | 'Yes'×164; 'No'×117; 'no'×2; 'yes'×1; 'YEs'×1 | 1C-7c · 5 — *Include Units from PHA Administered Programs in Your CoC’s C* |
| `1c_7c_6` |  |  | label | 'No'×208; 'Yes'×74; 'yes'×2; 'no'×1 | 1C-7c · 6 — *Include Units from PHA Administered Programs in Your CoC’s C* |
| `1c_7c_7` |  |  | label | 'No'×168; 'Yes'×114; 'no'×3 | 1C-7c · 7 — *Include Units from PHA Administered Programs in Your CoC’s C* |
| `1c_7d_1` |  |  | label | 'Yes'×156; 'No'×126; 'yes'×2; 'no'×1 | 1C-7d · 1 — *Submitting CoC and PHA Joint Applications for Funding for Pe* |
| `1c_7d_2` |  |  | label | 'Empty'×84; 'N/A'×24; 'FUP'×17; 'Family Unification Program (FUP)'×6; 'Stability Vouchers'×5 | 1C-7d · 2 — *Submitting CoC and PHA Joint Applications for Funding for Pe* |
| `1c_7e` |  |  | label | 'Yes'×236; 'No'×43; 'yes'×3; 'Empty'×3 | 1C-7e — *Coordinating with PHA(s) to Apply for or Implement HCV Dedic* |
| `1d_1_1` |  |  | label | 'Yes'×257; 'No'×24; 'yes'×2; 'no'×1; 'Yes`'×1 | 1D-1 · 1 — *Preventing People Transitioning from Public Systems from Exp* |
| `1d_1_2` |  |  | label | 'Yes'×271; 'No'×11; 'yes'×3 | 1D-1 · 2 — *Preventing People Transitioning from Public Systems from Exp* |
| `1d_1_3` |  |  | label | 'Yes'×242; 'No'×40; 'yes'×3 | 1D-1 · 3 — *Preventing People Transitioning from Public Systems from Exp* |
| `1d_1_4` |  |  | label | 'Yes'×268; 'No'×13; 'yes'×3; 'N'×1 | 1D-1 · 4 — *Preventing People Transitioning from Public Systems from Exp* |
| `1d_2_1` |  |  | label | '12.0'×21; '4.0'×16; '5.0'×16; '9.0'×16; '6.0'×15 | 1D-2 · 1 — *Housing First–Lowering Barriers to Entry.* |
| `1d_2_2` |  |  | label | '12.0'×21; '5.0'×16; '4.0'×15; '6.0'×15; '9.0'×15 | 1D-2 · 2 — *Housing First–Lowering Barriers to Entry.* |
| `1d_2_3` |  |  | label | '1.0'×209; '100.0'×51; '0.0'×6; '100%'×4; '0.97'×2 | 1D-2 · 3 — *Housing First–Lowering Barriers to Entry.* |
| `1d_2a` |  |  | narrative | avg_chars~2195; examples trimmed | 1D-2a — *Project Evaluation for Housing First Compliance.* |
| `1d_3` |  |  | narrative | avg_chars~2035; examples trimmed | 1D-3 — *Street Outreach–Data–Reaching People Least Likely to Request* |
| `1d_4_1_policymakers` |  |  | label | 'Yes'×263; 'No'×19; 'yes'×3 | 1D-4 · 1_policymakers — *Strategies to Prevent Criminalization of Homelessness.* |
| `1d_4_1_prevent_crim` |  |  | label | 'Yes'×208; 'No'×73; 'yes'×3; 'Empty'×1 | 1D-4 · 1_prevent_crim — *Strategies to Prevent Criminalization of Homelessness.* |
| `1d_4_2_policymakers` |  |  | label | 'Yes'×264; 'No'×18; 'yes'×3 | 1D-4 · 2_policymakers — *Strategies to Prevent Criminalization of Homelessness.* |
| `1d_4_2_prevent_crim` |  |  | label | 'Yes'×183; 'No'×98; 'yes'×3 | 1D-4 · 2_prevent_crim — *Strategies to Prevent Criminalization of Homelessness.* |
| `1d_4_3_policymakers` |  |  | label | 'Yes'×257; 'No'×23; 'yes'×3; 'Empty'×1; 'y'×1 | 1D-4 · 3_policymakers — *Strategies to Prevent Criminalization of Homelessness.* |
| `1d_4_3_prevent_crim` |  |  | label | 'Yes'×174; 'No'×106; 'yes'×3; 'Empty'×1 | 1D-4 · 3_prevent_crim — *Strategies to Prevent Criminalization of Homelessness.* |
| `1d_5_hmis` |  |  | label | 'HIC'×230; 'Longitudinal\nHMIS Data'×34; 'Longitudinal HMIS Data'×17; 'Empty'×3; 'hic'×1 | 1D-5 · hmis — *Rapid Rehousing–RRH Beds as Reported in the Housing Inventor* |
| `1d_5_2023` |  |  | label | '14.0'×4; '0.0'×4; '62.0'×4; '30.0'×3; '101.0'×3 | 1D-5 · 2023 — *Rapid Rehousing–RRH Beds as Reported in the Housing Inventor* |
| `1d_5_2024` |  |  | label | '40.0'×4; 'Empty'×3; '97.0'×3; '0.0'×3; '80.0'×3 | 1D-5 · 2024 — *Rapid Rehousing–RRH Beds as Reported in the Housing Inventor* |
| `1d_6_1` |  |  | label | 'Yes'×263; 'No'×18; 'yes'×3; 'N'×1 | 1D-6 · 1 — *Mainstream Benefits–CoC Annual Training of Project Staff.* |
| `1d_6_2` |  |  | label | 'Yes'×261; 'No'×20; 'yes'×4 | 1D-6 · 2 — *Mainstream Benefits–CoC Annual Training of Project Staff.* |
| `1d_6_3` |  |  | label | 'Yes'×264; 'No'×18; 'yes'×3 | 1D-6 · 3 — *Mainstream Benefits–CoC Annual Training of Project Staff.* |
| `1d_6_4` |  |  | label | 'Yes'×257; 'No'×22; 'yes'×3; 'N'×1; 'y'×1 | 1D-6 · 4 — *Mainstream Benefits–CoC Annual Training of Project Staff.* |
| `1d_6_5` |  |  | label | 'Yes'×266; 'No'×16; 'yes'×3 | 1D-6 · 5 — *Mainstream Benefits–CoC Annual Training of Project Staff.* |
| `1d_6_6` |  |  | label | 'Yes'×265; 'No'×17; 'yes'×3 | 1D-6 · 6 — *Mainstream Benefits–CoC Annual Training of Project Staff.* |
| `1d_6a` |  |  | narrative | avg_chars~1951; examples trimmed | 1D-6a — *Information and Training on Mainstream Benefits and Other As* |
| `1d_7` |  |  | narrative | avg_chars~1937; examples trimmed | 1D-7 |
| `1d_7a` |  |  | narrative | avg_chars~1854; examples trimmed | 1D-7a |
| `1d_8` |  |  | narrative | avg_chars~2279; examples trimmed | 1D-8 — *Coordinated Entry Standard Processes.* |
| `1d_8a` |  |  | narrative | avg_chars~2297; examples trimmed | 1D-8a — *Coordinated Entry–Program Participant-Centered* |
| `1d_8b` |  |  | narrative | avg_chars~2044; examples trimmed | 1D-8b — *Coordinated Entry–Informing Program Participants about Their* |
| `1d_9_1` |  |  | label | 'Yes'×258; 'No'×15; 'yes'×3; '2. The LCoC uses the CoC Racial Equity Analysis Tool to uncover any disparate impact and outcomes of providers’ policies and services on people of different races in LCoC funded housing or services. We generate a dashboard report using data disaggregated by race that shows incidences or patterns that we need to address.'×1; 'We use data from the Massachusetts CoC group. Its Racial Equity Working Group meets quarterly to analyze findings from the Racial Equity Analysis Tools for each CoC in the state. If it finds any disparities it will work with the CoC of concern and develop corrective strategies as needed.'×1 | 1D-9 · 1 — *Advancing Racial Equity in Homelessness–Conducting Assessmen* |
| `1d_9_2` |  |  | label | '2024-06-13 00:00:00'×9; 'Empty'×8; '2024-06-30 00:00:00'×5; '2024-07-15 00:00:00'×5; '2024-09-02 00:00:00'×4 | 1D-9 · 2 — *Advancing Racial Equity in Homelessness–Conducting Assessmen* |
| `1d_9a` |  |  | narrative | avg_chars~1907; examples trimmed | 1D-9a — *Using Data to Determine if Racial Disparities Exist in Your * |
| `1d_9b_1` |  |  | label | 'Yes'×238; 'No'×44; 'yes'×3 | 1D-9b · 1 — *Implemented Strategies to Prevent or Eliminate Racial Dispar* |
| `1d_9b_2` |  |  | label | 'Yes'×267; 'No'×14; 'yes'×3; 'n'×1 | 1D-9b · 2 — *Implemented Strategies to Prevent or Eliminate Racial Dispar* |
| `1d_9b_3` |  |  | label | 'Yes'×271; 'No'×11; 'yes'×3 | 1D-9b · 3 — *Implemented Strategies to Prevent or Eliminate Racial Dispar* |
| `1d_9b_4` |  |  | label | 'Yes'×265; 'No'×17; 'yes'×3 | 1D-9b · 4 — *Implemented Strategies to Prevent or Eliminate Racial Dispar* |
| `1d_9b_5` |  |  | label | 'Yes'×264; 'No'×17; 'yes'×3 | 1D-9b · 5 — *Implemented Strategies to Prevent or Eliminate Racial Dispar* |
| `1d_9b_6` |  |  | label | 'Yes'×245; 'No'×37; 'yes'×3 | 1D-9b · 6 — *Implemented Strategies to Prevent or Eliminate Racial Dispar* |
| `1d_9b_7` |  |  | label | 'Yes'×272; 'No'×9; 'yes'×3; 'N'×1 | 1D-9b · 7 — *Implemented Strategies to Prevent or Eliminate Racial Dispar* |
| `1d_9b_8` |  |  | label | 'Yes'×262; 'No'×20; 'yes'×3 | 1D-9b · 8 — *Implemented Strategies to Prevent or Eliminate Racial Dispar* |
| `1d_9b_9` |  |  | label | 'Yes'×272; 'No'×10; 'yes'×3 | 1D-9b · 9 — *Implemented Strategies to Prevent or Eliminate Racial Dispar* |
| `1d_9b_10` |  |  | label | 'Yes'×278; 'No'×4; 'yes'×3 | 1D-9b · 10 — *Implemented Strategies to Prevent or Eliminate Racial Dispar* |
| `1d_9b_11` |  |  | label | 'Yes'×257; 'No'×24; 'yes'×3; 'N'×1 | 1D-9b · 11 — *Implemented Strategies to Prevent or Eliminate Racial Dispar* |
| `1d_9c` |  |  | narrative | avg_chars~1768; examples trimmed | 1D-9c — *Plan for Ongoing Evaluation of System-level Processes, Polic* |
| `1d_9d` |  |  | narrative | avg_chars~1723; examples trimmed | 1D-9d — *Plan for Using Data to Track Progress on Preventing or Elimi* |
| `1d_10` |  |  | narrative | avg_chars~1793; examples trimmed | 1D-10 — *Involving Individuals with Lived Experience of Homelessness * |
| `1d_10a_1_years` |  |  | label | '2.0'×28; '3.0'×27; '8.0'×19; '4.0'×17; '5.0'×16 | 1D-10a · 1_years — *Active CoC Participation of Individuals with Lived Experienc* |
| `1d_10a_1_unsheltered` |  |  | label | '0.0'×38; '1.0'×35; '2.0'×34; '3.0'×30; '4.0'×20 | 1D-10a · 1_unsheltered — *Active CoC Participation of Individuals with Lived Experienc* |
| `1d_10a_2_years` |  |  | label | '8.0'×25; '5.0'×23; '4.0'×22; '3.0'×17; '2.0'×17 | 1D-10a · 2_years — *Active CoC Participation of Individuals with Lived Experienc* |
| `1d_10a_2_unsheltered` |  |  | label | '1.0'×37; '3.0'×36; '2.0'×34; '0.0'×31; '4.0'×23 | 1D-10a · 2_unsheltered — *Active CoC Participation of Individuals with Lived Experienc* |
| `1d_10a_3_years` |  |  | label | '2.0'×59; '1.0'×49; '3.0'×30; '0.0'×30; '4.0'×21 | 1D-10a · 3_years — *Active CoC Participation of Individuals with Lived Experienc* |
| `1d_10a_3_unsheltered` |  |  | label | '0.0'×77; '1.0'×65; '2.0'×46; '3.0'×29; '5.0'×14 | 1D-10a · 3_unsheltered — *Active CoC Participation of Individuals with Lived Experienc* |
| `1d_10a_4_years` |  |  | label | '3.0'×40; '2.0'×34; '1.0'×31; '5.0'×20; '4.0'×19 | 1D-10a · 4_years — *Active CoC Participation of Individuals with Lived Experienc* |
| `1d_10a_4_unsheltered` |  |  | label | '0.0'×52; '1.0'×51; '2.0'×40; '3.0'×36; '4.0'×23 | 1D-10a · 4_unsheltered — *Active CoC Participation of Individuals with Lived Experienc* |
| `1d_10b` |  |  | narrative | avg_chars~1801; examples trimmed | 1D-10b — *Professional Development and Employment Opportunities for In* |
| `1d_10c` |  |  | narrative | avg_chars~2169; examples trimmed | 1D-10c — *Routinely Gathering Feedback and Addressing Challenges of In* |
| `1d_11` |  |  | narrative | avg_chars~1808; examples trimmed | 1D-11 — *Increasing Affordable Housing Supply.* |
| `1e_1_1` |  |  | label | '2024-08-05 00:00:00'×18; '2024-08-14 00:00:00'×15; '2024-08-19 00:00:00'×14; '2024-08-12 00:00:00'×14; '2024-08-09 00:00:00'×13 | 1E-1 · 1 — *Web Posting of Advance Public Notice of Your CoC’s Local Com* |
| `1e_1_2` |  |  | label | '2024-08-12 00:00:00'×17; '2024-08-05 00:00:00'×15; '2024-08-13 00:00:00'×13; '2024-08-15 00:00:00'×13; '2024-08-09 00:00:00'×12 | 1E-1 · 2 — *Web Posting of Advance Public Notice of Your CoC’s Local Com* |
| `1e_2_1` |  |  | label | 'Yes'×278; 'yes'×4; 'Empty'×1; 'No'×1 | 1E-2 · 1 — *Project Review and Ranking Process Your CoC Used in Its Loca* |
| `1e_2_2` |  |  | label | 'Yes'×276; 'yes'×4; 'y'×1; 'Empty'×1; 'YEs'×1 | 1E-2 · 2 — *Project Review and Ranking Process Your CoC Used in Its Loca* |
| `1e_2_3` |  |  | label | 'Yes'×274; 'yes'×6; 'No'×3; 'Empty'×1 | 1E-2 · 3 — *Project Review and Ranking Process Your CoC Used in Its Loca* |
| `1e_2_4` |  |  | label | 'Yes'×276; 'yes'×4; 'No'×3; 'Empty'×1 | 1E-2 · 4 — *Project Review and Ranking Process Your CoC Used in Its Loca* |
| `1e_2_5` |  |  | label | 'Yes'×250; 'No'×29; 'yes'×4; 'Empty'×1 | 1E-2 · 5 — *Project Review and Ranking Process Your CoC Used in Its Loca* |
| `1e_2_6` |  |  | label | 'Yes'×257; 'No'×20; 'yes'×4; 'Empty'×2; 'N'×1 | 1E-2 · 6 — *Project Review and Ranking Process Your CoC Used in Its Loca* |
| `1e_2a_1` |  |  | label | '100.0'×90; '110.0'×11; '200.0'×9; '115.0'×6; '120.0'×6 | 1E-2a · 1 — *Scored Project Forms for One Project from Your CoC’s Local C* |
| `1e_2a_2` |  |  | label | '4.0'×20; '5.0'×18; '8.0'×18; '11.0'×17; '7.0'×17 | 1E-2a · 2 — *Scored Project Forms for One Project from Your CoC’s Local C* |
| `1e_2a_3` |  |  | label | 'PH-PSH'×227; 'PH-RRH'×35; 'Tie'×12; 'None'×3; 'Joint TH-RRH'×2 | 1E-2a · 3 — *Scored Project Forms for One Project from Your CoC’s Local C* |
| `1e_2b` |  |  | narrative | avg_chars~2077; examples trimmed | 1E-2b — *Addressing Severe Barriers in the Local Project Review and R* |
| `1e_3` |  |  | percent | examples: ['1. Project ranking and review criteria are ultimately selected, reviewed and\napproved by the CoC GAB. The CoC GAB is a diverse group whose\nmembership generally reflects the diversity of the BoS’ overall race and\nethnicity as well as homeless population demographics. Over the past year, 27\nto 40% of the GAB are BIPOC which is greater than the state demographics\nand roughly the same as the homeless population. AZ disparity evaluations\nshow that American Indians are the most over-represented ethnic demographic\nin the BoS and this demographic is represented on the GAB as our other ethnic\ngroups that are present but not over represented. The GAB members provided\ninput in the initial scoring tool drafts and the final approval of the criteria for both\nrenewal and bonus projects.\n2. As noted above, final ranking of renewal projects and scoring of bonus\nprojects is conducted by the GAB. In addition to reviewing scoring on objective\ncriteria for renewal projects, diverse GAB members also reviewed all bonus\nprojects and provided input into overall ranking.\n3. While renewal scoring includes questions related to diversity, the bonus\nproject application requires applicants to discuss their understanding of their\ngeographic and demographic populations including its diversity and cultural\nneeds. These responses were reviewed and incorporated in bonus project\nscoring and overall ranking and review. Addressing racial, ethnic or other\ndisparities in the ranking and review process primarily focused on the bonus\nprojects and how to determine where and for whom these projects would be\nbest suited to meet unmet needs. To determine need, specific questions were\nasked in the application about the relation of the demographics in the\ncommunity related to those served by the program. Agencies had to\ndemonstrate how their outreach and collaboration ensured a broad reach to\nlocations where persons experiencing homelessness gather. The two bonus\nprojects propose to serve multiple counties which are vastly different in their\ndemographic composition. It should be noted that while the GAB considered\nissues of racial and ethnic diversity, they also emphasized maintaining\ngeographic coverage since many ethnic and racial disparities are related to\nspecific county demographics and lack of adequate housing in those areas\ncould exacerbate existing disparities and access to housing.', '1) The CoC assessed & identified critical inequities– BIPOC community\nmembers experience disproportionate rates of homelessness (Black/ African\nAmericans make up 16.9% of homeless pop./ 2.5% of general pop;\nHispanic/Latinx people make up 43.7% of homeless pop/ 27% of general pop.).\nThe CoC used input from people of different races in designing the local\ncompetition through active efforts to increase diversity among CoC\nmembership, direct invitations & racial diversity on the CoC Board. The CoC\nhas offers an annual Intro to CoC Funding training targeting providers, partners\n& staff who are new to the CoC, lowering barriers to CoC participation for\nsmaller CBOs w/ deep ties to communities over-represented in the homeless\npop. Avg. participation in the NOFO Committee, which reviews & revises draft\nscoring & ranking process annually, including refining & revising a racial equity\n\nscoring factor, doubled b/w 2019 & 2023. NOFO Committee is open-\nmembership, open-attendance & widely advertised. In 2022, the CoC began\n\ndirectly inviting ORGS LED BY PEOPLE OF COLOR to attend NOFA\nCommittee mtgs. The CoC does not collect demographic information from\nNOFA Committee attendees or from the CoC Board that approves the local\nscoring factors & process, but both are racially diverse.\n2) R&R scoring panel recruitment targeted groups & individuals w/ lived\nexperience being unhoused & prioritized a diverse panel. The R&R panel\nincluded 9 members, 8 of whom had lived experience being unhoused, 1 with\nexp. of housing instability, & 33% BIPOC. The CoC Board, which reviewed &\napproved the final Priority Listing, is also racially diverse.\n3) A Racial Equity scoring factor evaluates new & renewal projects on strategies\nthey use to advance racial equity. This factor evaluates based on how\nrepresentative project staff is of the population served, strategies to adjust hiring\napproaches to diversify staff, & strategies to retain & empower BIPOC staff. The\nfactor also evaluates applicants on specific strategies to “address racial\ninequities and ensure culturally responsive programming” (e.g. “community\nadvisory body, equity committee, ongoing evaluation of racial equity in policy,\nservices, program impacts”). Applicants must provide “specific examples\nincluding any substantive changes to project design or service delivery that\nwere made within the agency”. In a separate factor, applicants must identify\nknown barriers faced by their clients & how they address those barriers.', '1. CoC used input from ppl of different races & ethnicities to determine rating\nfactors for project applications, including those overrepresented in homeless\npop. in SF (Black, Indigenous, & Latine/x). Funding Committee (primarily\nmembers of color: 75%) reviewed local scoring criteria starting Jan ‘24 to allow\nfor discussion & input. Collected input on rating factors & strategized\nincorporation of racial equity & lived experience (LE) in scoring. Meetings were\nopen to public & CoC’s diverse providers & advertised thru community\nnewsletter. Community input informed revisions to scoring (e.g., increasing pts\nrelated to advancing racial equity & data quality, eliminating lower priority\nfactors). After 5 monthly meetings, Funding Committee presented proposed\nchanges to Board, which includes ppl of races & ethnicities overrepresented in\nhomeless pop.& ppl w/ LE. Board discussed & approved rating factors &\nscoring.\n2. CoC included ppl of different races & ethnicities in review, selection & ranking\nof projects. Board & Collab. Applicant conducted targeted outreach (email,\nflyers, direct recruitment) to recruit Priority Panel w/ emphasis on recruiting ppl\nof races & ethnicities overrepresented in homeless pop. & other key populations\n(e.g., LGBTQ+ community). Specific outreach was conducted w/ local\nworkgrps/committees comprised of ppl w/ LE & survivors of domestic violence.\nPriority Panel (reviews & ranks projects) was diverse (75% were BIPOC women\nof African-American, Southwest Asian, Southeast Asian American ethnicities) &\nincluded members w/ LE. Panel reviewed projects & recommended ranked list\napproved by Board (w/ members from races overrepresented in SF homeless\npop. & members w/LE).\n3. CoC rated & ranked projects based on degree to which projects IDed & took\nsteps to address barriers to participation faced by ppl of different races &\nethnicities & those overrepresented in homeless pop., with question included in\nscoring factors (10/100pts). Projects are scored on cultural competency, & pt\nvalue for addressing racial equity & barriers was increased for renewal projects\n(14/100 pts, 2nd highest rated factor). Projects also scored on collection &\nimplementation of client feedback (9-10pts/100), intended to ID & eliminate\nbarriers, particularly by ppl of races & ethnicities overrepresented in homeless\npop. Diverse Priority Panel received training on scoring factors & reviewed apps\n& scored & ranked projects based on narratives & objective criteria.'] | 1E-3 — *Advancing Racial Equity through Participation of Over-Repres* |
| `1e_4` |  |  | narrative | avg_chars~1638; examples trimmed | 1E-4 — *Reallocation–Reviewing Performance of Existing Projects.* |
| `1e_4a` |  |  | label | 'No'×205; 'Yes'×71; 'Empty'×3; 'no'×3; 'yes'×1 | 1E-4a — *Reallocation Between FY 2019 and FY 2024.* |
| `1e_5_1` |  |  | label | 'No'×173; 'Yes'×104; 'no'×4; 'Empty'×3 | 1E-5 · 1 — *Projects Rejected/Reduced–Notification Outside of e-snaps.* |
| `1e_5_2` |  |  | label | 'No'×192; 'Yes'×85; 'no'×3; 'Empty'×2; 'NNo'×1 | 1E-5 · 2 — *Projects Rejected/Reduced–Notification Outside of e-snaps.* |
| `1e_5_3` |  |  | label | 'Yes'×159; 'No'×89; 'Empty'×27; 'empty'×2; 'no'×1 | 1E-5 · 3 — *Projects Rejected/Reduced–Notification Outside of e-snaps.* |
| `1e_5_4` |  |  | label | 'Empty'×101; '2024-10-15 00:00:00'×19; '2024-10-14 00:00:00'×16; '2024-10-11 00:00:00'×15; '2024-10-10 00:00:00'×10 | 1E-5 · 4 — *Projects Rejected/Reduced–Notification Outside of e-snaps.* |
| `1e_5a` |  |  | label | '2024-10-15 00:00:00'×37; '2024-10-11 00:00:00'×31; '2024-10-14 00:00:00'×24; '2024-10-09 00:00:00'×22; '2024-10-10 00:00:00'×18 | 1E-5a — *Projects Accepted–Notification Outside of e-snaps.* |
| `1e_5b` |  |  | label | 'Yes'×274; 'yes'×4; 'Empty'×4; 'No'×1 | 1E-5b — *Local Competition Selection Results for All Projects.* |
| `1e_5c` |  |  | label | '2024-10-28 00:00:00'×73; '2024-10-25 00:00:00'×52; 'Empty'×37; '2024-10-24 00:00:00'×19; '2024-10-21 00:00:00'×14 | 1E-5c — *Web Posting of CoC-Approved Consolidated Application 2 Days * |
| `1e_5d` |  |  | label | '2024-10-28 00:00:00'×80; '2024-10-25 00:00:00'×51; 'Empty'×38; '2024-10-24 00:00:00'×18; '2024-10-23 00:00:00'×14 | 1E-5d — *Notification to Community Members and Key* |
| `2a_1` |  |  | label | 'Wellsky'×66; 'WellSky'×33; 'Bitfocus'×15; 'Foothold Technology'×14; 'Eccovia'×11 | 2A-1 — *HMIS Vendor.* |
| `2a_2` |  |  | label | 'Single CoC'×155; 'Multiple CoCs'×63; 'Statewide'×53; 'single CoC'×7; 'statewide'×1 | 2A-2 — *HMIS Implementation Coverage Area.* |
| `2a_3` |  |  | label | '2024-05-10 00:00:00'×76; '2024-05-09 00:00:00'×58; '2024-05-08 00:00:00'×26; '2024-05-07 00:00:00'×15; '2024-05-01 00:00:00'×7 | 2A-3 — *HIC Data Submission in HDX.* |
| `2a_4` |  |  | narrative | avg_chars~1236; examples trimmed | 2A-4 — *Comparable Databases for DV Providers–CoC and HMIS Lead Supp* |
| `2a_5_1_non_vsp` |  |  | label | '250.0'×4; '0.0'×3; '24.0'×3; '220.0'×3; '202.0'×3 | 2A-5 · 1_non_vsp — *Bed Coverage Rate–Using HIC, HMIS Data–CoC Merger Bonus Poin* |
| `2a_5_1_vsp` |  |  | label | '0.0'×52; '24.0'×9; '15.0'×6; '45.0'×5; '16.0'×5 | 2A-5 · 1_vsp — *Bed Coverage Rate–Using HIC, HMIS Data–CoC Merger Bonus Poin* |
| `2a_5_1_hmis` |  |  | label | '0.0'×4; '126.0'×3; '313.0'×3; '334.0'×3; '74.0'×3 | 2A-5 · 1_hmis — *Bed Coverage Rate–Using HIC, HMIS Data–CoC Merger Bonus Poin* |
| `2a_5_1_coverage` |  |  | label | '1.0'×74; '100.0'×12; '0.0'×4; '96.2'×2; '92.95'×2 | 2A-5 · 1_coverage — *Bed Coverage Rate–Using HIC, HMIS Data–CoC Merger Bonus Poin* |
| `2a_5_2_non_vsp` |  |  | label | '0.0'×220; '20.0'×5; '10.0'×4; '8.0'×4; '30.0'×4 | 2A-5 · 2_non_vsp — *Bed Coverage Rate–Using HIC, HMIS Data–CoC Merger Bonus Poin* |
| `2a_5_2_vsp` |  |  | label | '0.0'×277; 'Empty'×3; '22.0'×1 | 2A-5 · 2_vsp — *Bed Coverage Rate–Using HIC, HMIS Data–CoC Merger Bonus Poin* |
| `2a_5_2_hmis` |  |  | label | '0.0'×223; '20.0'×5; '10.0'×4; '30.0'×4; '14.0'×3 | 2A-5 · 2_hmis — *Bed Coverage Rate–Using HIC, HMIS Data–CoC Merger Bonus Poin* |
| `2a_5_2_coverage` |  |  | label | '0.0'×209; '1.0'×49; '100.0'×15; 'Empty'×7; 'empty'×1 | 2A-5 · 2_coverage — *Bed Coverage Rate–Using HIC, HMIS Data–CoC Merger Bonus Poin* |
| `2a_5_3_non_vsp` |  |  | label | '0.0'×19; '23.0'×6; '18.0'×5; '27.0'×5; '30.0'×4 | 2A-5 · 3_non_vsp — *Bed Coverage Rate–Using HIC, HMIS Data–CoC Merger Bonus Poin* |
| `2a_5_3_vsp` |  |  | label | '0.0'×140; '10.0'×7; '8.0'×7; '11.0'×6; '42.0'×5 | 2A-5 · 3_vsp — *Bed Coverage Rate–Using HIC, HMIS Data–CoC Merger Bonus Poin* |
| `2a_5_3_hmis` |  |  | label | '0.0'×28; '23.0'×6; '27.0'×4; '46.0'×4; '47.0'×4 | 2A-5 · 3_hmis — *Bed Coverage Rate–Using HIC, HMIS Data–CoC Merger Bonus Poin* |
| `2a_5_3_coverage` |  |  | label | '1.0'×116; '0.0'×22; '100.0'×16; 'Empty'×3; '0.82'×3 | 2A-5 · 3_coverage — *Bed Coverage Rate–Using HIC, HMIS Data–CoC Merger Bonus Poin* |
| `2a_5_4_non_vsp` |  |  | label | '0.0'×7; '146.0'×5; '64.0'×4; '97.0'×4; '48.0'×4 | 2A-5 · 4_non_vsp — *Bed Coverage Rate–Using HIC, HMIS Data–CoC Merger Bonus Poin* |
| `2a_5_4_vsp` |  |  | label | '0.0'×158; '18.0'×5; '5.0'×4; '34.0'×4; '10.0'×3 | 2A-5 · 4_vsp — *Bed Coverage Rate–Using HIC, HMIS Data–CoC Merger Bonus Poin* |
| `2a_5_4_hmis` |  |  | label | '0.0'×10; '80.0'×4; '31.0'×4; '64.0'×4; '97.0'×3 | 2A-5 · 4_hmis — *Bed Coverage Rate–Using HIC, HMIS Data–CoC Merger Bonus Poin* |
| `2a_5_4_coverage` |  |  | label | '1.0'×175; '100.0'×45; '0.0'×7; 'Empty'×2; '0.5405'×2 | 2A-5 · 4_coverage — *Bed Coverage Rate–Using HIC, HMIS Data–CoC Merger Bonus Poin* |
| `2a_5_5_non_vsp` |  |  | label | '0.0'×6; '216.0'×3; '409.0'×2; '285.0'×2; '180.0'×2 | 2A-5 · 5_non_vsp — *Bed Coverage Rate–Using HIC, HMIS Data–CoC Merger Bonus Poin* |
| `2a_5_5_vsp` |  |  | label | '0.0'×236; '14.0'×2; 'Empty'×2; '23.0'×2; '26.0'×2 | 2A-5 · 5_vsp — *Bed Coverage Rate–Using HIC, HMIS Data–CoC Merger Bonus Poin* |
| `2a_5_5_hmis` |  |  | label | '0.0'×13; '24.0'×2; '285.0'×2; '3812.0'×2; '565.0'×2 | 2A-5 · 5_hmis — *Bed Coverage Rate–Using HIC, HMIS Data–CoC Merger Bonus Poin* |
| `2a_5_5_coverage` |  |  | label | '1.0'×104; '100.0'×24; '0.0'×8; '74.32'×2; 'Empty'×2 | 2A-5 · 5_coverage — *Bed Coverage Rate–Using HIC, HMIS Data–CoC Merger Bonus Poin* |
| `2a_5_6_non_vsp` |  |  | label | '0.0'×100; '97.0'×3; '33.0'×3; '4.0'×3; '35.0'×2 | 2A-5 · 6_non_vsp — *Bed Coverage Rate–Using HIC, HMIS Data–CoC Merger Bonus Poin* |
| `2a_5_6_vsp` |  |  | label | '0.0'×263; '45.0'×2; 'Empty'×2; '51.0'×1; '149.0'×1 | 2A-5 · 6_vsp — *Bed Coverage Rate–Using HIC, HMIS Data–CoC Merger Bonus Poin* |
| `2a_5_6_hmis` |  |  | label | '0.0'×117; '97.0'×3; '28.0'×3; '33.0'×3; '23.0'×3 | 2A-5 · 6_hmis — *Bed Coverage Rate–Using HIC, HMIS Data–CoC Merger Bonus Poin* |
| `2a_5_6_coverage` |  |  | label | '0.0'×113; '1.0'×84; '100.0'×30; 'Empty'×4; '91.89'×1 | 2A-5 · 6_coverage — *Bed Coverage Rate–Using HIC, HMIS Data–CoC Merger Bonus Poin* |
| `2a_5a` |  |  | percent | examples: ["1. Based on the differences in the column headers between last year's\napplication and this year's, the calculation methodology changed. If we had\nused the same math, we would have 88% of ES and 88% of TH bed coverage.\nPSH would have been the same, since there are no VSP bed implications to\nPSH coverage. Now that we are aware of the calculation change, we will be\nconnecting with the victim service providers that are currently indicated as not\nparticipating in a comparable database. In 2024 VSPs in Alaska were given an\nopportunity and strongly encouraged to transfer to a new platform, VELA. We've\nworked extensively with the providers and the developers to meet all of the\nrequirements of a comparable database that allows for the reporting needed.\nProviders may not know that the database they are now using is comparable.\nThe low percentage of coverage for PSH still has to do with the fact that VASH\nproviders are not required to participate in HMIS. The reason VASH beds are\nnot in is due to the VA not being incentivized to participate in HMIS. In the\nmeantime, the CoC is negotiating funding to support an evaluation of new HMIS\nsoftware for Alaska. This project is slated to begin in 2025. Data matching and\nthe ability to more easily and inexpensively share data between systems will be\na part of the evaluation criteria. The OPH beds represent Emergency Housing\nVouchers and are in the system because referrals are made through\nCoordinated Entry. These are tracked because of CE referral, and by AHFC\nafter receiving the voucher after implementation, not through a\nhousing/homeless provider.\n2. Concerted outreach efforts with VSPs statewide are underway. As a part of\nthis relationship building, CoC staff will work with them to update information\nprior to the 2025 HIC. This step will address TH and ES bed coverage. A new\nHMIS software RFP will include the requirement for easier data sharing, which\nwill address the PSH coverage level. The CoC will work with the HMIS lead to\nfind a solution for the OPH coverage level, which may involve the need for\nAHFC cooperation.", '1. N/A, because our coverage rate is 93.60%-100%.\n2. N/A, because our coverage rate is 93.60%-100%.', '1.A total of 148 beds listed in our region are not included as beds with HMIS\ncoverage (135 VASH vouchers (PSH) and 13 shelter beds (ES) contracted by\nthe VA Coalition). VA contracted agencies in our region do not use the local\nHMIS data system for tracking clients, but their HIC numbers are included,\ncausing our coverage rates to appear lower than they actually are. Inclusion of\nthese beds in the calculation increases the CoC’s bed coverage rate to 100%\nPSH and 86.7%% in ES. The CoC is in conversation with our local Veterans\nAdministration about their plan for HMIS implementation in the near future. To\nincrease the utilization beds in PSH, we will continue to work with the VA to\ninput the HMIS data and/or to assist us in providing a bridge of data from the\nHOME VA database to the HMIS database.\n2.The CoC’s goal is to continue to maintain these rates above 85% over the\nnext 12 months with the following strategies: 1) Provide education to\ncurrent/potential HMIS participating agencies on the use of community-wide\ndata to inform program planning, 2) Engage and encourage HMIS participation\nwith non-HMIS participating shelter/housing service agencies sharing the\nbenefits of HMIS participation—scalable systems, information and resource\nsharing, funding leverage, and collaboration among service providers, 3)\nExplore technology funding resources to support participation in HMIS, and 4)\nFacilitate training for HMIS users and administrators to promote use of\ntechnology.'] | 2A-5a — *Partial Credit for Bed Coverage Rates at or Below 84.99 for * |
| `2a_6` |  |  | label | 'Yes'×255; 'No'×19; 'yes'×5; 'no'×1; 'Empty'×1 | 2A-6 — *Longitudinal System Analysis (LSA) Submission in HDX 2.0.* |
| `2b_1` |  |  | label | '2024-01-24 00:00:00'×93; '2024-01-23 00:00:00'×56; '2024-01-25 00:00:00'×45; '2024-01-22 00:00:00'×24; '2024-01-31 00:00:00'×24 | 2B-1 — *PIT Count Date.* |
| `2b_2` |  |  | label | '2024-05-10 00:00:00'×96; '2024-05-09 00:00:00'×75; '2024-05-08 00:00:00'×30; '2024-05-07 00:00:00'×7; '2024-05-06 00:00:00'×6 | 2B-2 — *PIT Count Data–HDX Submission Date.* |
| `2b_3` |  |  | narrative | avg_chars~1584; examples trimmed | 2B-3 — *PIT Count–Effectively Counting Youth in Your CoC’s Most Rece* |
| `2b_4` |  |  | narrative | avg_chars~1195; examples trimmed | 2B-4 — *PIT Count–Methodology Change–CoC Merger Bonus Points.* |
| `2c_1` |  |  | narrative | avg_chars~2074; examples trimmed | 2C-1 — *Reducing the Number of First Time Homeless–Risk Factors Your* |
| `2c_1a_1` |  |  | label | 'No'×260; 'Yes'×15; 'no'×3; 'Nonexistent'×1; 'yes'×1 | 2C-1a · 1 — *Impact of Displaced Persons on Number of First Time Homeless* |
| `2c_1a_2` |  |  | label | 'No'×224; 'Yes'×51; 'yes'×4; 'Nonexistent'×1; 'Empty'×1 | 2C-1a · 2 — *Impact of Displaced Persons on Number of First Time Homeless* |
| `2c_2` |  |  | narrative | avg_chars~2066; examples trimmed | 2C-2 — *Reducing Length of Time Homeless–CoC’s Strategy.* |
| `2c_3` |  |  | narrative | avg_chars~2114; examples trimmed | 2C-3 — *Successful Permanent Housing Placement or Retention –CoC’s S* |
| `2c_4` |  |  | narrative | avg_chars~2009; examples trimmed | 2C-4 — *Reducing Returns to Homelessness–CoC’s Strategy.* |
| `2c_5` |  |  | narrative | avg_chars~1972; examples trimmed | 2C-5 — *Increasing Employment Cash Income–CoC's Strategy.* |
| `2c_5a` |  |  | narrative | avg_chars~1625; examples trimmed | 2C-5a — *Increasing Non-employment Cash Income–CoC’s Strategy* |
| `3a_1` |  |  | label | 'Yes'×140; 'No'×135; 'yes'×3; 'no'×2; 'Empty'×2 | 3A-1 — *New PH-PSH/PH-RRH Project–Leveraging Housing Resources.* |
| `3a_2` |  |  | label | 'Yes'×176; 'No'×99; 'yes'×3; 'no'×2; 'Empty'×2 | 3A-2 — *New PH-PSH/PH-RRH Project–Leveraging Healthcare Resources.* |
| `3c_1` |  |  | label | 'No'×274; 'no'×4; 'Yes'×1; 'Empty'×1; 'Nonexistent'×1 | 3C-1 — *Designating SSO/TH/Joint TH and PH-RRH Component Projects to* |
| `4a_1` |  |  | label | 'Yes'×180; 'No'×97; 'yes'×2; 'no'×2; 'Empty'×1 | 4A-1 — *New DV Bonus Project Applicants.* |
| `4a_1a_1` |  |  | label | 'No'×155; 'Empty'×77; 'Yes'×25; 'no'×3; 'empty'×3 | 4A-1a · 1 — *DV Bonus Project Types.* |
| `4a_1a_2` |  |  | label | 'Yes'×168; 'Empty'×78; 'No'×10; 'yes'×4; 'N/A'×3 | 4A-1a · 2 — *DV Bonus Project Types.* |

## Variables flagged for PI adjudication

*(none at first pass)*

## Narrative variables — require Stage-2 LLM extraction + reviewer approval

- `1b_1a` — None
- `1b_2` — None
- `1b_3` — None
- `1b_4` — None
- `1c_4a` — None
- `1c_4b` — None
- `1c_5a` — None
- `1c_5b` — None
- `1c_5d` — None
- `1c_5e` — None
- `1c_5f` — None
- `1c_6a` — None
- `1c_7a` — None
- `1d_2a` — None
- `1d_3` — None
- `1d_6a` — None
- `1d_7` — None
- `1d_7a` — None
- `1d_8` — None
- `1d_8a` — None
- `1d_8b` — None
- `1d_9a` — None
- `1d_9c` — None
- `1d_9d` — None
- `1d_10` — None
- `1d_10b` — None
- `1d_10c` — None
- `1d_11` — None
- `1e_2b` — None
- `1e_4` — None
- `2a_4` — None
- `2b_3` — None
- `2b_4` — None
- `2c_1` — None
- `2c_2` — None
- `2c_3` — None
- `2c_4` — None
- `2c_5` — None
- `2c_5a` — None
