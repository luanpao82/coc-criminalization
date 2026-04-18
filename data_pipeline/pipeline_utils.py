"""Shared helpers for the CoC application extraction pipeline.

Keeping this tiny and dependency-light on purpose; extractors import it
rather than duplicate normalization logic.
"""
from __future__ import annotations

import csv
import json
import re
import subprocess
from pathlib import Path
from typing import Iterable

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
DATA_DIR = Path(
    "/Users/seongho/Library/CloudStorage/OneDrive-UniversityofCentralFlorida/"
    "Desktop/Prof. An/01 Research/2026 CoC Anti-Criminalization on Homelessness/Data"
)
PIPELINE_DIR = Path(
    "/Users/seongho/Desktop/Obsidian/10-Research/coc_criminalization/data_pipeline"
)
EXTRACTED_DIR = PIPELINE_DIR / "extracted"
DRAFTS_DIR = PIPELINE_DIR / "drafts"


# ---------------------------------------------------------------------------
# ID normalization
# ---------------------------------------------------------------------------
COC_ID_RE = re.compile(r"^(?P<state>[A-Za-z]{2})_(?P<num>\d{3})_(?P<year>20\d{2})$")


def normalize_coc_id(stem: str):
    cleaned = re.sub(r"[\-_]+", "_", stem)
    m = COC_ID_RE.match(cleaned)
    if not m:
        return None, None
    return f"{m.group('state').upper()}-{m.group('num')}", m.group("year")


def load_inventory() -> list[dict]:
    path = PIPELINE_DIR / "file_inventory.csv"
    with path.open() as f:
        return list(csv.DictReader(f))


def find_source_file(coc_id: str, year: str, prefer_docx_if_scanned: bool = True):
    """Return the best source file for a (coc_id, year).

    Rules:
      - If a DOCX exists and the PDF is scanned, prefer DOCX.
      - Otherwise prefer native PDF.
      - Return Path or None.
    """
    rows = [r for r in load_inventory() if r["coc_id"] == coc_id and r["year"] == year]
    if not rows:
        return None
    pdfs = [r for r in rows if r["format"] == "pdf"]
    docxs = [r for r in rows if r["format"] == "docx"]
    if prefer_docx_if_scanned and docxs:
        scanned_pdf = any(r.get("is_scanned") == "TRUE" for r in pdfs)
        if scanned_pdf or not pdfs:
            return DATA_DIR / docxs[0]["original_filename"]
    if pdfs:
        native = [r for r in pdfs if r.get("is_scanned") != "TRUE"]
        pick = native[0] if native else pdfs[0]
        return DATA_DIR / pick["original_filename"]
    if docxs:
        return DATA_DIR / docxs[0]["original_filename"]
    return None


# ---------------------------------------------------------------------------
# PDF anchor parsing
# ---------------------------------------------------------------------------
# Match patterns like "1B-1.", "1C-4a.", "1D-10a.", "1E-5b.", etc.
QUESTION_ANCHOR_RE = re.compile(
    r"(?P<qid>\d[A-E]-\d+[a-z]?)\.\s+(?P<title>[^\n\r]{3,250})"
)


def pdftotext_layout(path: Path, first: int | None = None, last: int | None = None) -> str:
    args = ["pdftotext", "-layout"]
    if first is not None:
        args += ["-f", str(first)]
    if last is not None:
        args += ["-l", str(last)]
    args += [str(path), "-"]
    return subprocess.run(args, capture_output=True, text=True, timeout=180).stdout


def extract_question_anchors(text: str) -> dict[str, str]:
    """Map question id ('1B-1', '1D-4', ...) to the first title seen."""
    anchors: dict[str, str] = {}
    for m in QUESTION_ANCHOR_RE.finditer(text):
        qid = m.group("qid")
        if qid not in anchors:
            anchors[qid] = m.group("title").strip()
    return anchors


# ---------------------------------------------------------------------------
# Controlled vocabulary / codebook
# ---------------------------------------------------------------------------
CATEGORICAL_YES_NO_NONEXIST = {"Yes", "No", "Nonexistent"}
DESIGNATION_VOCAB = {"CA", "UFA", "UFC"}


def normalize_categorical(value: str | None) -> str | None:
    """Fold case-variants into canonical form; return None if unmappable."""
    if value is None:
        return None
    s = str(value).strip().strip("`'\"")
    if not s:
        return None
    low = s.lower()
    if low == "yes" or low == "y":
        return "Yes"
    if low == "no" or low == "n":
        return "No"
    if low == "nonexistent":
        return "Nonexistent"
    if low in {"n/a", "na", "not applicable"}:
        return "N/A"
    return s  # leave untouched for non-categorical variables


def normalize_label(value: str | None) -> str:
    if value is None:
        return ""
    s = str(value)
    s = s.replace("\n", " ")
    s = re.sub(r"\s+", " ", s).strip()
    return s


# ---------------------------------------------------------------------------
# Common output record
# ---------------------------------------------------------------------------
def make_record(
    *,
    coc_id: str,
    year: str,
    field_id: str,
    value,
    raw_text: str = "",
    source_page: int | None = None,
    source_bbox: Iterable | None = None,
    extractor: str = "",
    extractor_version: str = "0.1",
    confidence: float = 1.0,
    needs_review: bool = False,
    note: str = "",
) -> dict:
    return {
        "coc_id": coc_id,
        "year": year,
        "field_id": field_id,
        "value": value,
        "raw_text": raw_text,
        "source_page": source_page,
        "source_bbox": list(source_bbox) if source_bbox else None,
        "extractor": extractor,
        "extractor_version": extractor_version,
        "confidence": confidence,
        "needs_review": needs_review,
        "note": note,
    }


def write_records(coc_id: str, year: str, records: list[dict]) -> Path:
    EXTRACTED_DIR.mkdir(parents=True, exist_ok=True)
    out = EXTRACTED_DIR / f"{coc_id}_{year}.json"
    with out.open("w") as f:
        json.dump(records, f, indent=2, default=str)
    return out
