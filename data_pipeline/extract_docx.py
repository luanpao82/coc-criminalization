"""DOCX adapter — reads CoC applications exported as Word documents.

The DOCX files in the corpus (CA-505/509/511/513/521, MI-501, NV-500, and
CA-521 as DOCX counterpart to a scanned PDF) preserve HUD's logical
structure as paragraphs and tables. The strategy is to flatten the
document into a "layout text" stream similar to `pdftotext -layout`
output, then reuse the existing native-PDF extractors.

Design choice: rather than reimplement every chart parser for the DOCX
model, we render table rows into fixed-width text that the anchor-based
parsers can consume unchanged. This keeps one extraction code path.
"""
from __future__ import annotations

import argparse
import re
import xml.etree.ElementTree as ET
import zipfile
from pathlib import Path

from pipeline_utils import find_source_file, write_records

from extract_pdf_native import extract_for as extract_for_pdf
from extract_pdf_native import (
    extract_1A,
    extract_1B1,
    extract_generic_chart,
    extract_numeric_chart,
    extract_scalar_cat,
    extract_1D2_numeric,
)

WORD_NS = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"


def iter_docx_blocks(path: Path):
    """Yield ('para', text) or ('table', list_of_rows) tuples preserving order."""
    with zipfile.ZipFile(path) as z:
        raw = z.read("word/document.xml")
    root = ET.fromstring(raw)
    body = root.find(f"{WORD_NS}body")
    if body is None:
        return
    for el in list(body):
        tag = el.tag.replace(WORD_NS, "")
        if tag == "p":
            texts = [t.text or "" for t in el.iter(f"{WORD_NS}t")]
            yield "para", "".join(texts)
        elif tag == "tbl":
            rows = []
            for tr in el.findall(f"{WORD_NS}tr"):
                cells = []
                for tc in tr.findall(f"{WORD_NS}tc"):
                    cell_text = "".join(t.text or "" for t in tc.iter(f"{WORD_NS}t"))
                    cells.append(cell_text.strip())
                rows.append(cells)
            yield "table", rows


def render_to_layout_text(path: Path) -> str:
    """Render a DOCX to a pdftotext-layout-style text block.

    Tables are formatted with wide whitespace between columns so the
    existing anchor-based parsers see the same visual shape as in PDFs.
    """
    out_lines: list[str] = []
    for kind, content in iter_docx_blocks(path):
        if kind == "para":
            if content.strip():
                out_lines.append(content)
        else:  # table
            for row_cells in content:
                # Filter empty, join with wide spacing
                non_empty = [c for c in row_cells if c]
                if not non_empty:
                    continue
                line = (" " * 4).join(non_empty)
                out_lines.append(line)
            out_lines.append("")
    return "\n".join(out_lines)


def _docx_path(coc_id: str, year: str) -> Path | None:
    from pipeline_utils import load_inventory, DATA_DIR
    for r in load_inventory():
        if r["coc_id"] == coc_id and r["year"] == year and r["format"] == "docx":
            return DATA_DIR / r["original_filename"]
    return None


def extract_for_docx(coc_id: str, year: str) -> list[dict]:
    """Run the same extractors as pdf_native, but over docx-derived layout text."""
    path = _docx_path(coc_id, year)
    if path is None:
        return []
    text = render_to_layout_text(path)
    # Pretend it's a single page
    pages_text = [(1, text)]
    records = []
    records.extend(extract_1A(pages_text, coc_id, year))
    records.extend(extract_1B1(pages_text, coc_id, year))
    records.extend(
        extract_generic_chart(
            pages_text, coc_id, year,
            start_anchor=r"\b1C-1\.", end_anchor=r"\b1C-2\.",
            n_rows=17, n_cols=1, field_template="1c_1_{row}", column_suffixes=[""],
        )
    )
    records.extend(
        extract_generic_chart(
            pages_text, coc_id, year,
            start_anchor=r"\b1C-4\.", end_anchor=r"\b1C-4a\.",
            n_rows=4, n_cols=1, field_template="1c_4_{row}", column_suffixes=[""],
        )
    )
    records.extend(
        extract_generic_chart(
            pages_text, coc_id, year,
            start_anchor=r"\b1D-4\.", end_anchor=r"\b1D-5\.",
            n_rows=3, n_cols=2, field_template="1d_4_{row}_{col}",
            column_suffixes=["policymakers", "prevent_crim"],
        )
    )
    records.extend(
        extract_generic_chart(
            pages_text, coc_id, year,
            start_anchor=r"\b1D-6\.", end_anchor=r"\b1D-6a\.",
            n_rows=6, n_cols=1, field_template="1d_6_{row}", column_suffixes=[""],
        )
    )
    records.extend(
        extract_numeric_chart(
            pages_text, coc_id, year,
            start_anchor=r"\b2A-5\.", end_anchor=r"\b2A-5a\.",
            n_rows=6, n_cols=4,
            field_template="2a_5_{row}_{col}",
            column_suffixes=["non_vsp", "vsp", "hmis", "coverage"],
        )
    )
    # Set extractor version label on each record
    for r in records:
        r["extractor"] = "docx_v0.1"
    return records


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--coc", required=True)
    ap.add_argument("--year", required=True)
    args = ap.parse_args()
    records = extract_for_docx(args.coc, args.year)
    out = write_records(args.coc, args.year, records)
    print(f"wrote {len(records)} records -> {out}")


if __name__ == "__main__":
    main()
