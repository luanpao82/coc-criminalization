"""Build file_inventory.csv from the Data folder.

Columns:
  original_filename  — as found on disk
  coc_id             — normalized (e.g., "AL-500")
  year               — 2022 / 2023 / 2024
  format             — pdf / docx
  num_pages          — PDFs only
  text_chars         — first-page text length (scan detection proxy)
  is_scanned         — heuristic: True if native text extraction is near-empty
  name_issue         — True if original filename used non-canonical separators
  notes
"""
from __future__ import annotations

import csv
import re
import subprocess
import sys
import zipfile
from pathlib import Path

DATA_DIR = Path(
    "/Users/seongho/Library/CloudStorage/OneDrive-UniversityofCentralFlorida/"
    "Desktop/Prof. An/01 Research/2026 CoC Anti-Criminalization on Homelessness/Data"
)
OUT_PATH = Path(
    "/Users/seongho/Desktop/Obsidian/10-Research/coc_criminalization/"
    "data_pipeline/file_inventory.csv"
)

# Accept patterns like AL_500_2024, AL-500_2024, FL-_601_2022, WY-500_2024.
CANDIDATE_RE = re.compile(
    r"^(?P<state>[A-Za-z]{2})[\-_]+(?P<num>\d{3})_(?P<year>20\d{2})$"
)
VALID_YEARS = {"2022", "2023", "2024"}


def normalize_coc_id(stem: str):
    # Strip stray characters like the "FL-_601_2022" dash+underscore combo.
    cleaned = re.sub(r"[\-_]+", "_", stem)
    m = re.match(r"^(?P<state>[A-Za-z]{2})_(?P<num>\d{3})_(?P<year>20\d{2})$", cleaned)
    if not m:
        return None, None, None
    state = m.group("state").upper()
    return f"{state}-{m.group('num')}", m.group("year"), cleaned


def pdf_metadata(path: Path):
    try:
        info = subprocess.run(
            ["pdfinfo", str(path)], capture_output=True, text=True, timeout=30
        )
        num_pages = None
        for line in info.stdout.splitlines():
            if line.startswith("Pages:"):
                num_pages = int(line.split(":", 1)[1].strip())
                break
        # Extract first-page text to detect scanned PDFs.
        txt = subprocess.run(
            ["pdftotext", "-layout", "-f", "1", "-l", "1", str(path), "-"],
            capture_output=True,
            text=True,
            timeout=60,
        )
        first_page_chars = len(txt.stdout.strip())
        return num_pages, first_page_chars
    except Exception as exc:
        return None, f"ERR:{exc}"


def docx_chars(path: Path):
    try:
        with zipfile.ZipFile(path) as z:
            with z.open("word/document.xml") as f:
                raw = f.read().decode("utf-8", errors="ignore")
        # crude tag strip
        return len(re.sub(r"<[^>]+>", " ", raw).strip())
    except Exception as exc:
        return f"ERR:{exc}"


def main():
    rows = []
    unmatched = []
    for path in sorted(DATA_DIR.iterdir()):
        if path.is_dir():
            continue
        if path.name.startswith("."):
            continue
        suffix = path.suffix.lower()
        if suffix not in {".pdf", ".docx"}:
            continue
        stem = path.stem
        coc_id, year, cleaned = normalize_coc_id(stem)
        if coc_id is None or year not in VALID_YEARS:
            unmatched.append(path.name)
            continue
        name_issue = cleaned != stem or "-" in stem and "_" in stem[:6]
        row = {
            "original_filename": path.name,
            "coc_id": coc_id,
            "year": year,
            "format": suffix.lstrip("."),
            "num_pages": "",
            "text_chars": "",
            "is_scanned": "",
            "name_issue": "TRUE" if name_issue else "FALSE",
            "notes": "",
        }
        if suffix == ".pdf":
            pages, chars = pdf_metadata(path)
            row["num_pages"] = pages if pages is not None else ""
            row["text_chars"] = chars if not isinstance(chars, str) else ""
            if isinstance(chars, int):
                # HUD applications always have a header on page 1; < 80 chars implies scan.
                row["is_scanned"] = "TRUE" if chars < 80 else "FALSE"
            else:
                row["notes"] = str(chars)
        else:
            chars = docx_chars(path)
            row["text_chars"] = chars if not isinstance(chars, str) else ""
            row["is_scanned"] = "FALSE"
            if isinstance(chars, str):
                row["notes"] = chars
        rows.append(row)

    # Duplicate detection: multiple files per (coc_id, year)
    from collections import defaultdict

    seen = defaultdict(list)
    for r in rows:
        seen[(r["coc_id"], r["year"])].append(r)
    for key, group in seen.items():
        if len(group) > 1:
            fmts = sorted({g["format"] for g in group})
            for g in group:
                existing = g["notes"]
                dup_note = f"duplicate({'+'.join(fmts)})"
                g["notes"] = f"{existing}; {dup_note}" if existing else dup_note

    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with OUT_PATH.open("w", newline="") as f:
        w = csv.DictWriter(
            f,
            fieldnames=[
                "original_filename",
                "coc_id",
                "year",
                "format",
                "num_pages",
                "text_chars",
                "is_scanned",
                "name_issue",
                "notes",
            ],
        )
        w.writeheader()
        for r in sorted(rows, key=lambda r: (r["coc_id"], r["year"], r["format"])):
            w.writerow(r)

    print(f"wrote {len(rows)} rows -> {OUT_PATH}")
    if unmatched:
        print("UNMATCHED FILES (not ingested):")
        for name in unmatched:
            print(" ", name)
    # quick diagnostics
    from collections import Counter

    by_year = Counter(r["year"] for r in rows)
    by_fmt = Counter(r["format"] for r in rows)
    scanned = sum(1 for r in rows if r["is_scanned"] == "TRUE")
    print("by year:", dict(by_year))
    print("by format:", dict(by_fmt))
    print("scanned(heuristic):", scanned)
    print("name_issues:", sum(1 for r in rows if r["name_issue"] == "TRUE"))
    print("duplicate keys:", sum(1 for v in seen.values() if len(v) > 1))


if __name__ == "__main__":
    main()
