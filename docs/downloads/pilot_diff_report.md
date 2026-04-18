# Pilot Diff Report

Generated: 2026-04-17T23:34:54
Extractor: `pdf_native_v0.1`  Pilot: ['AL-500', 'CA-500', 'FL-501', 'NY-600', 'TX-600']  Year: 2024

## Headline numbers

- **Overall agreement (weighted):** 97.190% (1176/1210 fields)
- **Adjusted agreement** (excludes manual-blank cells the extractor filled): 99.577% (1176/1181 fields)
- **Per class:**
  - `A_categorical`: 99.212% (1007/1015)
  - `B_integer`: 87.143% (122/140)
  - `B_percent`: 82.857% (29/35)
  - `C_label`: 90.000% (18/20)

## Per CoC

| CoC | match | total | acc |
|---|---|---|---|
| AL-500 | 241 | 242 | 99.587% |
| CA-500 | 241 | 242 | 99.587% |
| FL-501 | 241 | 242 | 99.587% |
| NY-600 | 240 | 242 | 99.174% |
| TX-600 | 213 | 242 | 88.017% |

## Diffs (first 50)

| CoC | field | class | manual | auto | reason |
|---|---|---|---|---|---|
| AL-500 | `1a_1b` | C_label | Birmingham/Jefferson, St. Clair, Shelby Counties | Birmingham/Jefferson, St. Clair, Shelby Counties CoC | manual='birmingham/jefferson, st. clair, shelby counties'/auto='birmingham/jeffe |
| CA-500 | `1a_1b` | C_label | San Jose/ Santa Clara City & County CoC | San Jose/Santa Clara City & County CoC | manual='san jose/ santa clara city & county coc'/auto='san jose/santa clara city |
| FL-501 | `1b_1_7_ces` | A_categorical | Yes | No | manual='Yes'/auto='No' |
| NY-600 | `1c_1_6` | A_categorical | No | Yes | manual='No'/auto='Yes' |
| NY-600 | `1c_1_8` | A_categorical | Yes | No | manual='Yes'/auto='No' |
| TX-600 | `2a_5_1_non_vsp` | B_integer |  | 1617 | manual_blank |
| TX-600 | `2a_5_1_vsp` | B_integer |  | 268 | manual_blank |
| TX-600 | `2a_5_1_hmis` | B_integer |  | 1744 | manual_blank |
| TX-600 | `2a_5_1_coverage` | B_percent |  | 0.9252 | manual_blank |
| TX-600 | `2a_5_2_non_vsp` | B_integer |  | 55 | manual_blank |
| TX-600 | `2a_5_2_vsp` | B_integer |  | 0 | manual_blank |
| TX-600 | `2a_5_2_hmis` | B_integer |  | 55 | manual_blank |
| TX-600 | `2a_5_2_coverage` | B_percent |  | 1.0 | manual_blank |
| TX-600 | `2a_5_3_non_vsp` | B_integer |  | 1277 | manual_blank |
| TX-600 | `2a_5_3_vsp` | B_integer |  | 128 | manual_blank |
| TX-600 | `2a_5_3_hmis` | B_integer |  | 279 | manual_blank |
| TX-600 | `2a_5_3_coverage` | B_percent |  | 0.1986 | manual_blank |
| TX-600 | `2a_5_4_non_vsp` | B_integer |  | 1636 | manual_blank |
| TX-600 | `2a_5_4_vsp` | B_integer |  | 69 | manual_blank |
| TX-600 | `2a_5_4_hmis` | B_integer |  | 1636 | manual_blank |
| TX-600 | `2a_5_4_coverage` | B_percent |  | 0.9595 | manual_blank |
| TX-600 | `2a_5_5_non_vsp` | B_integer |  | 2487 | manual_blank |
| TX-600 | `2a_5_5_vsp` | B_integer |  | 0 | manual_blank |
| TX-600 | `2a_5_5_hmis` | B_integer |  | 2487 | manual_blank |
| TX-600 | `2a_5_5_coverage` | B_percent |  | 1.0 | manual_blank |
| TX-600 | `2a_5_6_non_vsp` | B_integer |  | 1034 | manual_blank |
| TX-600 | `2a_5_6_vsp` | B_integer |  | 0 | manual_blank |
| TX-600 | `2a_5_6_hmis` | B_integer |  | 1034 | manual_blank |
| TX-600 | `2a_5_6_coverage` | B_percent |  | 1.0 | manual_blank |
| TX-600 | `2a_6` | A_categorical |  | Yes | manual_blank |
| TX-600 | `3a_1` | A_categorical |  | Yes | manual_blank |
| TX-600 | `3a_2` | A_categorical |  | Yes | manual_blank |
| TX-600 | `3c_1` | A_categorical |  | No | manual_blank |
| TX-600 | `4a_1` | A_categorical |  | Yes | manual_blank |

## Disagreement categories (rough)

- manual_blank (possible manual skip): **29**
- value_mismatch: **5**