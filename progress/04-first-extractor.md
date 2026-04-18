---
title: 04 — The First Extractor
order: 4
status: complete
last_updated: 2026-04-17
---

# The First Extractor

With the inventory, codebook, and crosswalk in place, the next decision
was *what to build first*. We chose the smallest slice that would prove
every architectural idea in one pass.

## Scope of v0.1

Two question groups, 104 variables per CoC:

- **1A-1 through 1A-4** — CoC identifiers, designation, and HMIS lead
  (5 variables of class C and A)
- **1B-1 participation chart** — 33 rows × 3 columns of Yes/No/Nonexistent
  responses about CoC meetings, voting, and coordinated-entry
  participation (99 categorical variables of class A)

Together these cover roughly **one-third of the canonical schema** and
exercise the three hardest parts of the design:

1. Splitting a combined field (`1A-1. CoC Name and Number: AL-500 - …`)
   into two canonical columns.
2. Handling multi-line values that wrap across PDF lines.
3. Parsing a 33-row table whose row count varies per CoC (some add an
   "Other" row, some don't — row matching must be by *label*, not
   *position*).

## Design choices inside the extractor

### Page-level provenance

Rather than running `pdftotext` on the whole document, the extractor
iterates page-by-page and keeps the page number with every extracted
value. This adds a small amount of I/O for a large gain in
auditability: any disagreement can be traced back to a specific page in
a few clicks.

### Anchor-then-parse, implemented literally

```python
m = re.search(r"1A-2\.\s*Collaborative Applicant Name:\s*([^\n\r]+)", text)
```

Each question gets its own regex anchor. A failure to find the anchor
produces no value — never a wrong value — and the absence is loud enough
to surface in QA.

### Canonical row labels, not positional indices

The 33 1B-1 rows have stable labels (`"Affordable Housing Developer(s)"`,
`"Indian Tribes and Tribally Designated Housing Entities (TDHEs)…"`,
etc.), and the extractor carries those labels as a Python list. For each
numbered row in the PDF, the extractor validates that the observed label
starts with the canonical label's first 20 characters (case-insensitive,
whitespace-normalized). If it doesn't, the cell is marked
`needs_review=True` and never silently coerced.

On the 5-CoC pilot set this check passed on every row.

### Every output record carries the same shape

```json
{
  "coc_id": "AL-500",
  "year": "2024",
  "field_id": "1b_1_7_ces",
  "value": "No",
  "raw_text": "Hospital(s)",
  "source_page": 3,
  "extractor": "pdf_native_v0.2",
  "confidence": 1.0,
  "needs_review": false,
  "note": ""
}
```

Downstream code (diff runner, reviewer UI, LLM prompt builder) all
consume this shape. Changing the output schema is a one-place edit.

## Running v0.1 for the first time

```
$ python3 extract_pdf_native.py --coc AL-500 --year 2024
wrote 104 records -> extracted/AL-500_2024.json
```

Zero `needs_review` flags on AL-500. The first run produced the full
expected number of records with clean provenance. That was a milestone
because the design of a pipeline shows up first in the *shape* of its
output — whether the output has a place for provenance, confidence, and
review flags determines everything else.

## Iteration 0 — the first pilot

With v0.1 working on one CoC, we expanded to five (AL-500, CA-500,
FL-501, NY-600, TX-600), computed agreement against the manual
spreadsheet, and categorized every disagreement:

| Class | Match rate | Diffs |
|---|---|---|
| A — categorical (Yes/No/Nonexistent) | **99.80%** | 1 |
| C — label (identifier strings) | 85.00% | 3 |
| Weighted | **99.23%** | 4 total |

Four disagreements total on 520 comparisons. Three of them would turn
out to be manual errors rather than pipeline problems — that story is
in [[05-debugging-and-iteration]].

## Artifacts

- `data_pipeline/extract_pdf_native.py` — the extractor module
- `data_pipeline/pipeline_utils.py` — shared helpers (ID normalization,
  page-by-page text extraction, categorical value normalization)
- `data_pipeline/pilot_run.py` — runs the extractor on the pilot set and
  diffs against the manual spreadsheet

Next: [[05-debugging-and-iteration]]
