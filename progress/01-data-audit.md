---
title: 01 — What the Corpus Actually Looks Like
order: 1
status: complete
last_updated: 2026-04-17
---

# What the Corpus Actually Looks Like

Before writing any extraction code, we ran a full audit of the source
folder. The instinct was to skip this step — after all, the files are
"just" HUD application PDFs — but the audit immediately surfaced structural
heterogeneity that any pipeline has to absorb.

## The one-line answer

**677 files, three fiscal years, two file formats, and 19 scans that will
require OCR.** Every row of `file_inventory.csv` carries its own
identifiers, format, page count, scan flag, and duplicate markers, which
downstream routers read to pick the right extractor.

## What we inspected

- Every file in the project's `Data/` folder
- Filename conventions, file format, page count, and first-page text length
- Presence of multiple files for the same CoC × year (DOCX and PDF)
- Files whose names didn't match any expected pattern

## What we found

| Dimension | Count | Comment |
|---|---|---|
| Total files ingested | 677 | One file per CoC × year (with a few duplicates) |
| Unmatched / out-of-scope | 1 | `NHA CCMA Study Guide [Final].pdf` — unrelated |
| Fiscal years | 3 | FY2022: 172 · FY2023: 197 · FY2024: 308 |
| Formats | 2 | PDF: 670 · DOCX: 7 |
| Scanned PDFs (heuristic) | 19 | First-page text < 80 chars, needs OCR |
| Duplicate (CoC, year) pairs | 8 | Usually PDF + DOCX of the same CoC |
| Filename anomalies | 4 | Inconsistent `-` vs `_` separators |

## Examples that changed our plan

- **CA-521 (2024)** has both a PDF and a DOCX. The PDF is scanned (zero
  native text) — the DOCX is the actually-usable source. The file inventory
  flags this so the router prefers the DOCX automatically.
- **LA-506 (2023)** appears twice — `LA-506_2023.pdf` and `LA_506_2023.pdf`.
  MD5 check confirmed they are byte-identical. This is a filename
  duplicate, not a content conflict.
- **FL-_601 (2022), WY-500 (2024), VA-521 (2023)** use a hyphen where the
  convention is an underscore. Rather than silently rewriting filenames
  (which breaks provenance to the original file), we normalized the
  `coc_id` in the inventory and preserved the original name.

## Why this step matters

Every downstream artifact — the codebook, the crosswalk, the extractor
router — keys on `(coc_id, year)`. If we had skipped the audit we would
have:

1. Silently dropped 19 scanned PDFs on the assumption that `pdftotext`
   always works.
2. Extracted from the wrong file for ~8 DOCX-preferred cases.
3. Hit downstream `KeyError`s on the 4 filename anomalies.

This step took roughly ten minutes of compute and saved far more than that
in later debugging.

## Artifact

- `data_pipeline/file_inventory.csv` — 677 rows, one per source file

Next: [[02-methodology-design]]
