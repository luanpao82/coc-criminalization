---
title: 03 — Schema and Crosswalk
order: 3
status: complete (v0.1 drafts)
last_updated: 2026-04-17
---

# Schema and Crosswalk

This step produced two artifacts that every downstream component reads:
the **codebook** (what each variable means) and the **crosswalk** (how
years align). Both are versioned as v0.1 drafts; PI review turns them
into locked canonical references.

## The codebook

The manual spreadsheet's 331 columns are the *de facto* schema, but
column headers alone don't tell us:

- What values are permitted?
- Is the variable categorical, numeric, free-text, or narrative?
- How is "missing" distinguished from "not applicable" from "not asked"?

`data_pipeline/build_codebook.py` automates the first-pass answer:

1. Read rows 1–4 of the `2024` sheet (field id, section, subsection, label).
2. Observe the values that coders actually entered in rows 5–315.
3. Classify each variable into one of the four classes (A/B/C/D) by
   inspecting its observed value domain.
4. Emit a Markdown codebook organized by HUD section, with an "observed
   domain" column that exposes coder inconsistency (`'Yes'×279;'yes'×6;
   'No'×4;'Nonexistent'×1`) for PI review.

The observed-domain column is deliberately ugly: every case-variant and
typo is visible, which is exactly what PIs need to see before they lock
the controlled vocabulary.

### Missing-value conventions

| Convention | Meaning |
|---|---|
| `Nonexistent` | HUD-provided option — entity does not exist in the CoC's area |
| `N/A` | Prior gate answer excludes the question |
| `NA_not_asked_this_year` | Variable did not exist in this year's form (crosswalk-derived) |
| blank | Source PDF is genuinely missing a value — needs human review |

This distinction matters for analysis. A CoC that skipped a question and
a CoC that was never asked the question look identical as empty cells but
carry very different analytical meaning.

## The crosswalk

HUD revised the application across FY2022, FY2023, and FY2024. Questions
moved, merged, and changed wording. The crosswalk (`crosswalk.csv`) is
the single source of truth for how a canonical FY2024 field maps to the
question that produced it in earlier years.

### How it's built

`data_pipeline/build_crosswalk.py` does this automatically:

1. Take one representative CoC that has all three years (AL-500).
2. For each year, run `pdftotext -layout` and regex out every question
   anchor and its title (e.g., `1B-1. Inclusive Structure and
   Participation…`).
3. For each canonical FY2024 variable group, attempt an exact qid match
   in FY2022 and FY2023. If the qid doesn't exist, fall back to fuzzy
   title matching (`difflib.SequenceMatcher`) above a 0.60 threshold.
4. Flag any mapping with similarity below 0.85 for PI review.

### Results

- **113 canonical families** identified (after grouping suffixes — a
  variable like `1b_1_7_ces` belongs to the `1b_1` family because it
  shares a source question with `1b_1_7_meetings` and `1b_1_7_voted`).
- **79 families** auto-matched across all three years with high confidence.
- **34 families** flagged for review — most are 1C-5 and 1D-4 sub-questions
  where HUD's wording shifted significantly year-to-year.

The 34 flagged items are listed in `crosswalk_review.md` in a single
table, making PI adjudication a one-sitting exercise rather than a
per-year slog.

### A concrete example of why this matters

FY2022 `1D-9` ("Coordinated Entry System – Assessment Process") was
restructured by FY2024 into multiple sub-questions under `1D-9` and
`1D-10`. A naive string match would say these are "the same question" in
2022 and 2024 — but the underlying construct has fractured. Flagging
these for PI review prevents the panel data from carrying silent
measurement shifts.

## Artifacts

- `data_pipeline/codebook.md` (opens in Obsidian as [[codebook]])
- `data_pipeline/crosswalk.csv` — 113 canonical families
- `data_pipeline/crosswalk_review.md` — 34 items flagged for PI review

Next: [[04-first-extractor]]
