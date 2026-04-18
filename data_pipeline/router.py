"""Corpus-scale router.

Reads `file_inventory.csv`, picks the right extractor per file, and writes
one JSON record file per (coc_id, year). Computes a summary at the end.

Routing rules:
  * native PDF → extract_pdf_native
  * scanned PDF with DOCX available → extract_docx
  * scanned PDF without DOCX → flag (OCR adapter not yet implemented)
  * DOCX (no PDF or PDF is scanned) → extract_docx
"""
from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path

from pipeline_utils import PIPELINE_DIR, load_inventory, write_records

from extract_pdf_native import extract_for as extract_pdf
from extract_docx import extract_for_docx

SUMMARY = PIPELINE_DIR / "extraction_summary.csv"


def route(coc_id: str, year: str, rows: list[dict]) -> tuple[str, str]:
    """Return (extractor_label, reason)."""
    pdfs = [r for r in rows if r["format"] == "pdf"]
    docxs = [r for r in rows if r["format"] == "docx"]
    pdf_scanned = any(r["is_scanned"] == "TRUE" for r in pdfs)
    if pdfs and not pdf_scanned:
        return "pdf_native", "native PDF available"
    if docxs:
        return "docx", "scanned PDF → fall back to DOCX" if pdf_scanned else "DOCX only"
    return "ocr_required", "scanned PDF with no DOCX; OCR adapter not implemented"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--year", default="2024", help="Year to process")
    ap.add_argument("--limit", type=int, default=0, help="Stop after N CoCs (0=all)")
    ap.add_argument("--only", default="", help="Comma-separated CoC IDs to restrict to")
    args = ap.parse_args()

    inv = load_inventory()
    by_cy: dict[tuple, list[dict]] = {}
    for r in inv:
        if r["year"] != args.year:
            continue
        by_cy.setdefault((r["coc_id"], r["year"]), []).append(r)

    coc_ids = sorted({k[0] for k in by_cy.keys()})
    only = set(args.only.split(",")) if args.only else set()
    if only:
        coc_ids = [c for c in coc_ids if c in only]

    if args.limit:
        coc_ids = coc_ids[: args.limit]

    counts = Counter()
    rows_summary = []
    for coc_id in coc_ids:
        rows = by_cy[(coc_id, args.year)]
        extractor, reason = route(coc_id, args.year, rows)
        n_records = 0
        if extractor == "pdf_native":
            records = extract_pdf(coc_id, args.year)
            write_records(coc_id, args.year, records)
            n_records = len(records)
        elif extractor == "docx":
            records = extract_for_docx(coc_id, args.year)
            write_records(coc_id, args.year, records)
            n_records = len(records)
        else:
            records = []
            n_records = 0
        rows_summary.append({
            "coc_id": coc_id, "year": args.year,
            "extractor": extractor, "n_records": n_records,
            "needs_review": sum(1 for r in records if r.get("needs_review")),
            "reason": reason,
        })
        counts[extractor] += 1
        if len(rows_summary) % 25 == 0:
            print(f"  [{len(rows_summary)}/{len(coc_ids)}] processed")

    # Write summary
    import csv
    with SUMMARY.open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows_summary[0].keys()))
        w.writeheader()
        w.writerows(rows_summary)
    print()
    print(f"Processed {len(coc_ids)} CoCs for FY{args.year}")
    print(f"Extractor distribution: {dict(counts)}")
    print(f"Summary -> {SUMMARY}")


if __name__ == "__main__":
    main()
