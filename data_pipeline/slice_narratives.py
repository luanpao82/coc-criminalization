"""Slice narrative text blocks for a batch of CoCs × fields.

Saves each narrative as a plain-text file in drafts/texts/{coc}_{year}_{field}.txt
so they can be read by a human reviewer OR by the Claude Code session that's
doing the coding.

Unlike extract_narrative.py, this script does NOT call any API. It only
prepares the input payloads.
"""
from __future__ import annotations

import argparse
import csv
import re
from pathlib import Path

from pipeline_utils import PIPELINE_DIR, find_source_file, pdftotext_layout
from extract_narrative import NARRATIVE_SPECS, slice_narrative

OUT_DIR = PIPELINE_DIR / "drafts" / "texts"
OUT_DIR.mkdir(parents=True, exist_ok=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--year", choices=["2022", "2023", "2024"], default="2024")
    ap.add_argument("--field", choices=list(NARRATIVE_SPECS.keys()), required=True)
    ap.add_argument("--cocs", default="AL-500,CA-500,FL-501,NY-600,TX-600",
                    help="Comma-separated CoC IDs")
    ap.add_argument("--limit", type=int, default=0, help="Stop after N successful slices")
    args = ap.parse_args()

    spec = NARRATIVE_SPECS[args.field]
    cocs = [c.strip() for c in args.cocs.split(",") if c.strip()]
    written = []
    for coc in cocs:
        pdf = find_source_file(coc, args.year)
        if pdf is None or pdf.suffix.lower() != ".pdf":
            continue
        text, page = slice_narrative(pdf, spec["anchor"], spec["next_anchor"])
        if len(text) < 30:
            continue
        out = OUT_DIR / f"{coc}_{args.year}_{args.field}.txt"
        out.write_text(
            f"# {coc} / FY{args.year} / {args.field}\n"
            f"# Title: {spec['title']}\n"
            f"# Source page: {page}\n"
            f"# Length: {len(text)} chars\n\n"
            f"{text[:5000]}\n"
        )
        written.append(out)
        if args.limit and len(written) >= args.limit:
            break

    print(f"wrote {len(written)} slices to {OUT_DIR}")
    for p in written:
        print(f"  {p.name}")


if __name__ == "__main__":
    main()
