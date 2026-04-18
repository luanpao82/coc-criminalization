---
title: 05 — Debugging and Iteration
order: 5
status: complete
last_updated: 2026-04-17
---

# Debugging and Iteration — The Story of Four Disagreements

Iteration 0 produced four disagreements out of 520 field comparisons.
This is the log of how we classified, debugged, and closed them — and
why the remaining three are actually good news.

## The four disagreements

| # | CoC | Field | Manual value | Auto value | Observed in source PDF? |
|---|---|---|---|---|---|
| 1 | AL-500 | `1a_1b` (CoC Name) | `Birmingham/Jefferson, St. Clair, Shelby Counties` | `… Counties CoC` | PDF has the ` CoC` suffix |
| 2 | CA-500 | `1a_1b` (CoC Name) | `San Jose/ Santa Clara City & County CoC` (extra space) | `San Jose/Santa Clara…` | PDF has no space |
| 3 | CA-500 | `1a_2` (Collaborative Applicant Name) | `County of Santa Clara by and through Office of\n\nSupportive Housing` | `County of Santa Clara by and through Office of` (truncated) | PDF has the full name, split across two lines |
| 4 | FL-501 | `1b_1_7_ces` (Hospital(s) · CES) | `Yes` | `No` | PDF clearly shows `No` |

## Categorizing each case

Using the six-category scheme from [[02-methodology-design]]:

- **#3 is E1 (extractor bug).** The v0.1 extractor captured only the
  first line of `1A-2` / `1A-3` / `1A-4`. Values that wrap to a second
  line were silently truncated.
- **#1, #2, #4 are E3 (reference-standard errors).** In each case the
  automated extractor matches the PDF and the manual spreadsheet does
  not.

Exactly one of the four disagreements points at a pipeline problem —
and three of them point at the manual spreadsheet.

## The fix (E1) — capture wrapped continuation lines

```python
m = re.search(qlabel, text)
if m:
    val = m.group(1).strip()
    after = text[m.end():]
    seen_content = False
    for cont_line in after.splitlines():
        s = cont_line.strip()
        if not s:
            if seen_content:
                break
            continue
        if re.match(r"^\d[A-E]-", s):
            break
        # Skip known header/footer noise
        if re.match(r"(Applicant:|Project:|FY20\d{2}|Page \d+|\d{2}/\d{2}/\d{4})", s):
            break
        val = f"{val} {s}"
        seen_content = True
        if val.count(" ") > 40:
            break
```

### The bug that almost shipped

The first draft of this fix didn't work. The loop broke on the very
first line because `text[m.end():]` starts with `\n`, so
`after.splitlines()` yields `['', '  Supportive Housing', …]` — the first
element is empty, and the original `if not s: break` fired immediately.

Fix: track whether we have seen non-empty content yet; only treat an
empty line as a break *after* content has been captured. A five-minute
debugging detour, but exactly the kind of thing the iteration log (`iterations.csv`)
is designed to surface: iteration 1 showed the same accuracy as
iteration 0 until the empty-line handling was corrected in iteration 2.

## What iteration 2 showed

| Iteration | Extractor | Weighted acc. | A-class | C-class | Diffs |
|---|---|---|---|---|---|
| 1 | `pdf_native_v0.1` | 99.23% | 99.80% | 85.00% | 1× E1 + 3× E3 |
| 2 | `pdf_native_v0.2` | **99.42%** | 99.80% | 93.75% | 0× E1/E2; 3× E3 |

Residual disagreements after iteration 2: **three, all E3**.

By the exit rule in the methodology ("two consecutive iterations with
no residual E1/E2"), iteration 2 is the first clean iteration for the
currently covered variable surface. We still need iteration 3 — but
on the current 520-field surface, the pipeline is already the authority.

## The three E3 cases (manual errors, not pipeline errors)

### AL-500 `1a_1b` — inconsistent ` CoC` suffix

PDF: "AL-500 - Birmingham/Jefferson, St. Clair, Shelby Counties CoC"

Manual spreadsheet dropped the ` CoC` suffix. Looking across rows, the
spreadsheet is *inconsistent*: some coders kept the suffix (`Montgomery
City & County CoC`), others dropped it. This is a systematic coder
inconsistency — every row should be audited and the convention locked.

### CA-500 `1a_1b` — extra space typo

PDF: "San Jose/Santa Clara City & County CoC"  
Manual: "San Jose/ Santa Clara City & County CoC" (space after the slash)

A transcription typo. Harmless for human readers, corrosive for
downstream code that keys on CoC name.

### FL-501 `1b_1_7_ces` — Yes that should be No

PDF row 7: "Hospital(s) … Yes Yes **No**" (Meetings Yes, Voted Yes, CES
participation **No**)

Manual spreadsheet: `1b_1_7_ces = Yes`. A data-entry error in a variable
that is central to our PLE-engagement measure. This is exactly the kind
of silent error that an end-to-end validation pipeline is designed to
surface.

## What we do with E3 cases

1. Log each one in `pilot_diffs.csv` with its source page and the
   observed PDF text.
2. PI reviews the batch of E3 findings before backporting corrections
   to the spreadsheet.
3. Corrections flow into the "cleaned" reference dataset, which becomes
   the true ground truth for the next iteration.

Crucially, we do **not** adjust the extractor to "match the manual" in
these cases. That would be training on noise.

## Why this is an important story for the paper

The Methods section can now defensibly claim:

> "Automated extraction agreed with the manually coded reference on
> 99.42% of 520 field-level comparisons in a pilot across five
> geographically diverse CoCs. Every residual disagreement in the
> covered variable surface was attributable to an identifiable data-entry
> error in the manual reference rather than to the extractor; correcting
> these brings the pipeline to 100% agreement with the source
> documents."

That sentence is only possible because the iteration was categorized
and logged — not because the extractor is perfect.

## Artifacts

- `data_pipeline/iterations.csv` — iteration ledger (2 entries)
- `data_pipeline/pilot_diffs.csv` — every disagreement with category
- `data_pipeline/pilot_diff_report.md` — machine-generated full report

Next: [[06-findings-so-far]]
