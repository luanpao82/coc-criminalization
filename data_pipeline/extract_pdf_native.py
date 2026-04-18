"""Native-PDF extractor (v0.1) for FY2024 CoC applications.

Scope of this first pass
------------------------
This adapter extracts variables whose signal is already reliable in the
`pdftotext -layout` output:

  * 1A-1 .. 1A-4  (1a_1a, 1a_1b, 1a_2, 1a_3, 1a_4)
  * 1B-1 participation chart — 33 canonical rows × 3 columns
    (1b_1_{1..33}_{meetings,voted,ces})

Everything else is deferred to later extractor versions; running this on a
CoC produces a partial but auditable record set with source-page provenance
on every value.
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

from pipeline_utils import (
    CATEGORICAL_YES_NO_NONEXIST,
    extract_question_anchors,
    find_source_file,
    make_record,
    normalize_categorical,
    normalize_label,
    pdftotext_layout,
    write_records,
)

EXTRACTOR_NAME = "pdf_native_v0.6"

# Canonical 33 row labels for 1B-1 (FY2024). Order matters.
B1_CANONICAL_LABELS = [
    "Affordable Housing Developer(s)",
    "CDBG/HOME/ESG Entitlement Jurisdiction",
    "Disability Advocates",
    "Disability Service Organizations",
    "EMS/Crisis Response Team(s)",
    "Homeless or Formerly Homeless Persons",
    "Hospital(s)",
    "Indian Tribes and Tribally Designated Housing Entities (TDHEs) (Tribal Organizations)",
    "Law Enforcement",
    "Lesbian, Gay, Bisexual, Transgender (LGBTQ+) Advocates",
    "LGBTQ+ Service Organizations",
    "Local Government Staff/Officials",
    "Local Jail(s)",
    "Mental Health Service Organizations",
    "Mental Illness Advocates",
    "Organizations led by and serving Black, Brown, Indigenous and other People of Color",
    "Organizations led by and serving LGBTQ+ persons",
    "Organizations led by and serving people with disabilities",
    "Other homeless subpopulation advocates",
    "Public Housing Authorities",
    "School Administrators/Homeless Liaisons",
    "Street Outreach Team(s)",
    "Substance Abuse Advocates",
    "Substance Abuse Service Organizations",
    "Agencies Serving Survivors of Human Trafficking",
    "Victim Service Providers",
    "Domestic Violence Advocates",
    "Other Victim Service Organizations",
    "State Domestic Violence Coalition",
    "State Sexual Assault Coalition",
    "Youth Advocates",
    "Youth Homeless Organizations",
    "Youth Service Providers",
]


def extract_1A(pages_text: list[tuple[int, str]], coc_id: str, year: str):
    """Return records for 1a_1a, 1a_1b, 1a_2, 1a_3, 1a_4."""
    records = []
    # Search page-by-page so we can record source_page
    for page_num, text in pages_text:
        # 1A-1: split "AL-500 - Name" -> number + name
        m = re.search(r"1A-1\.\s*CoC Name and Number:\s*([^\n\r]+)", text)
        if m:
            raw = m.group(1).strip()
            # Format: "AL-500 - Birmingham/Jefferson, St. Clair, Shelby ..."
            # The full name may wrap to the next line; grab the continuation if present.
            after = text[m.end():]
            cont = re.match(r"\s*([^\n]*)\n", after)
            if cont:
                extra = cont.group(1).strip()
                if extra and not re.match(r"^\d[A-E]-", extra) and "1A-" not in extra:
                    raw = f"{raw} {extra}"
            raw = normalize_label(raw)
            split = re.match(r"^([A-Z]{2}-\d{3})\s*-\s*(.+)$", raw)
            if split:
                coc_num, coc_name = split.group(1), split.group(2).strip()
            else:
                coc_num, coc_name = raw, raw
            records.append(
                make_record(
                    coc_id=coc_id, year=year, field_id="1a_1a",
                    value=coc_num, raw_text=raw, source_page=page_num,
                    extractor=EXTRACTOR_NAME,
                )
            )
            records.append(
                make_record(
                    coc_id=coc_id, year=year, field_id="1a_1b",
                    value=coc_name, raw_text=raw, source_page=page_num,
                    extractor=EXTRACTOR_NAME,
                )
            )

        for fid, qlabel in [
            ("1a_2", r"1A-2\.\s*Collaborative Applicant Name:\s*([^\n\r]+)"),
            ("1a_3", r"1A-3\.\s*CoC Designation:\s*([^\n\r]+)"),
            ("1a_4", r"1A-4\.\s*HMIS Lead:\s*([^\n\r]+)"),
        ]:
            m = re.search(qlabel, text)
            if m:
                val = m.group(1).strip()
                # Capture wrapped continuation(s). Skip leading blank lines,
                # then break on the first blank after content, or a new anchor.
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
                    if re.match(r"(Applicant:|Project:|FY20\d{2}|Page \d+|\d{2}/\d{2}/\d{4})", s):
                        break
                    val = f"{val} {s}"
                    seen_content = True
                    # Only grab up to 3 continuation lines to be safe
                    if val.count(" ") > 40:
                        break
                val = normalize_label(val)
                records.append(
                    make_record(
                        coc_id=coc_id, year=year, field_id=fid,
                        value=val, raw_text=val, source_page=page_num,
                        extractor=EXTRACTOR_NAME,
                    )
                )
    return records


B1_ROW_RE = re.compile(
    r"^\s*(\d{1,2})\.\s+(?P<label>.+?)\s{2,}"
    r"(?P<meet>Yes|No|Nonexistent)\s{2,}"
    r"(?P<vote>Yes|No|Nonexistent)\s{2,}"
    r"(?P<ces>Yes|No|Nonexistent)\s*$"
)
B1_ROW_WRAPPED_RE = re.compile(
    r"^\s*(\d{1,2})\.\s+(?P<label>.+?)\s+"
    r"(?P<meet>Yes|No|Nonexistent)\s+"
    r"(?P<vote>Yes|No|Nonexistent)\s+"
    r"(?P<ces>Yes|No|Nonexistent)\s*$"
)


def _canonical_b1_index(observed_label: str) -> int | None:
    """Map an observed 1B-1 row label to its FY2024-canonical index (1..33).

    Matches by longest common prefix, with minimum set to 70% of the
    canonical-label length (so short labels like "Hospital(s)" still match).
    """
    if not observed_label:
        return None
    target = re.sub(r"\s+", " ", observed_label.strip().lower())
    best_idx = None
    best_score = 0
    for i, canon in enumerate(B1_CANONICAL_LABELS, start=1):
        c = re.sub(r"\s+", " ", canon.lower())
        # Score: shared prefix length
        n = 0
        for a, b in zip(target, c):
            if a == b:
                n += 1
            else:
                break
        # Require at least 70% of the canonical label OR 15 chars
        threshold = max(8, int(len(c) * 0.7))
        if n >= threshold and n > best_score:
            best_score = n
            best_idx = i
    return best_idx


def extract_1B1(pages_text: list[tuple[int, str]], coc_id: str, year: str):
    """Return 99 records (33 canonical rows × 3 columns) for 1B-1 chart.

    Matches rows to the FY2024 canonical labels; PDF row ORDER is ignored
    (FY2022 had a different alphabetic sort), so values are stored by
    canonical position, not observed position.
    """
    records = []
    # canonical_idx -> {label, meetings, voted, ces, page}
    rows_by_num: dict[int, dict] = {}
    for page_num, text in pages_text:
        lines = text.splitlines()
        pending_num = None
        pending_label_lines: list[str] = []
        for i, line in enumerate(lines):
            m = B1_ROW_RE.match(line)
            alt = None
            if not m:
                alt = B1_ROW_WRAPPED_RE.match(line)
            if m or alt:
                mm = m or alt
                row_num = int(mm.group(1))
                if row_num < 1 or row_num > 40:
                    continue
                label = normalize_label(mm.group("label").strip())
                canon_idx = _canonical_b1_index(label)
                if canon_idx is None:
                    pending_num = None
                    continue
                rows_by_num[canon_idx] = {
                    "label": label,
                    "meetings": mm.group("meet"),
                    "voted": mm.group("vote"),
                    "ces": mm.group("ces"),
                    "page": page_num,
                }
                pending_num = canon_idx
                pending_label_lines = []
            else:
                # Possible continuation: indented non-numbered, no Yes/No,
                # comes right after a matched row.
                if pending_num is None:
                    continue
                stripped = line.strip()
                if not stripped or re.search(r"\b(Yes|No|Nonexistent)\b", stripped):
                    pending_num = None
                    continue
                # Only take one continuation line
                if pending_label_lines:
                    pending_num = None
                    continue
                pending_label_lines.append(stripped)
                rec = rows_by_num.get(pending_num)
                if rec:
                    rec["label"] = normalize_label(rec["label"] + " " + stripped)
                pending_num = None

    # Emit records for canonical rows 1..33
    for i, canonical_label in enumerate(B1_CANONICAL_LABELS, start=1):
        row = rows_by_num.get(i)
        meet = normalize_categorical(row["meetings"]) if row else None
        vote = normalize_categorical(row["voted"]) if row else None
        ces = normalize_categorical(row["ces"]) if row else None
        page = row["page"] if row else None
        # When row is present it already passed canonical-label matching.
        observed_label = row["label"] if row else ""
        label_ok = bool(row)
        need_review = not row
        for field_suffix, val in [
            ("meetings", meet), ("voted", vote), ("ces", ces),
        ]:
            records.append(
                make_record(
                    coc_id=coc_id, year=year,
                    field_id=f"1b_1_{i}_{field_suffix}",
                    value=val,
                    raw_text=observed_label,
                    source_page=page,
                    extractor=EXTRACTOR_NAME,
                    confidence=1.0 if label_ok else 0.5,
                    needs_review=need_review,
                    note=(
                        "label_mismatch" if row and not label_ok
                        else ("row_missing" if not row else "")
                    ),
                )
            )
    return records


def extract_generic_chart(
    pages_text: list[tuple[int, str]],
    coc_id: str,
    year: str,
    *,
    start_anchor: str,
    end_anchor: str,
    n_rows: int,
    n_cols: int,
    field_template: str,
    column_suffixes: list[str] | None = None,
    allowed_values: set[str] | None = None,
) -> list[dict]:
    """Parse a numbered Yes/No chart between two question anchors.

    * ``start_anchor``/``end_anchor`` are regex strings matching the opening
      and closing question numbers (e.g. r"\b1C-3\.", r"\b1C-4\.").
    * ``n_rows``/``n_cols`` describe the canonical shape of the chart.
    * ``field_template``: Python format string using ``row`` (1..n_rows) and
      ``col`` (suffix from ``column_suffixes`` if provided else index).
      Examples: ``"1c_1_{row}"``, ``"1d_4_{row}_{col}"``.
    * ``column_suffixes``: optional list of strings for the column axis; if
      provided, length must equal ``n_cols`` and its values are interpolated
      as ``{col}`` in ``field_template``.
    * ``allowed_values``: set of strings considered valid values. Defaults to
      ``{"Yes", "No", "Nonexistent"}``. Anything else marks the record
      ``needs_review``.
    """
    allowed = allowed_values or CATEGORICAL_YES_NO_NONEXIST
    alt_pat = "|".join(sorted(allowed, key=len, reverse=True))
    # Row pattern: "1. <label> <col1> <col2> ..."
    row_re = re.compile(
        r"^\s*(\d{1,2})\.\s+(?P<label>.+?)"
        + r"".join([rf"\s+(?P<c{i}>{alt_pat})" for i in range(n_cols)])
        + r"\s*$"
    )

    # Slice text between anchors (combine pages, but track page per row).
    captured_rows: dict[int, dict] = {}
    start_re = re.compile(start_anchor)
    end_re = re.compile(end_anchor)

    in_section = False
    for page_num, text in pages_text:
        if not in_section:
            if start_re.search(text):
                in_section = True
                post_start = text[start_re.search(text).end():]
                source = post_start
            else:
                continue
        else:
            source = text
        if in_section and end_re.search(source):
            source = source[: end_re.search(source).start()]
            # after this we stop consuming further pages
            next_in_section = False
        else:
            next_in_section = True

        for line in source.splitlines():
            m = row_re.match(line)
            if not m:
                continue
            row_num = int(m.group(1))
            if row_num < 1 or row_num > n_rows:
                continue
            captured_rows[row_num] = {
                "label": normalize_label(m.group("label")),
                "cols": [m.group(f"c{i}") for i in range(n_cols)],
                "page": page_num,
            }

        in_section = next_in_section
        if not in_section:
            break

    records = []
    for i in range(1, n_rows + 1):
        row = captured_rows.get(i)
        page = row["page"] if row else None
        for ci in range(n_cols):
            suffix = column_suffixes[ci] if column_suffixes else str(ci + 1)
            field_id = field_template.format(row=i, col=suffix)
            raw_val = row["cols"][ci] if row else None
            val = normalize_categorical(raw_val) if raw_val else None
            if val and val not in allowed and val != "N/A":
                needs_review = True
                note = f"out_of_vocab:{raw_val!r}"
            elif not row:
                needs_review = True
                note = "row_missing"
            else:
                needs_review = False
                note = ""
            records.append(
                make_record(
                    coc_id=coc_id, year=year, field_id=field_id,
                    value=val,
                    raw_text=row["label"] if row else "",
                    source_page=page,
                    extractor=EXTRACTOR_NAME,
                    confidence=1.0 if row else 0.0,
                    needs_review=needs_review,
                    note=note,
                )
            )
    return records


def extract_1D2_numeric(pages_text: list[tuple[int, str]], coc_id: str, year: str):
    """1D-2 has three sub-answers rendered as "1. <text> <number>" with the
    numeric value at the far right. Pull by row index 1..3.
    """
    records: list[dict] = []
    start_re = re.compile(r"\b1D-2\.")
    end_re = re.compile(r"\b1D-2a\.")
    row_re = re.compile(r"^\s*(?P<n>[1-3])\.\s+(?P<label>.+?)\s+(?P<val>[\d.]+%?)\s*$")
    in_section = False
    captured: dict[int, dict] = {}
    for page_num, text in pages_text:
        if not in_section:
            m = start_re.search(text)
            if not m:
                continue
            in_section = True
            source = text[m.end():]
        else:
            source = text
        e = end_re.search(source)
        if e:
            source = source[: e.start()]
            last_page = True
        else:
            last_page = False
        for line in source.splitlines():
            m = row_re.match(line)
            if not m:
                continue
            n = int(m.group("n"))
            captured[n] = {
                "label": normalize_label(m.group("label")),
                "val": m.group("val"),
                "page": page_num,
            }
        if last_page:
            break

    for n in (1, 2, 3):
        r = captured.get(n)
        if not r:
            records.append(
                make_record(
                    coc_id=coc_id, year=year, field_id=f"1d_2_{n}",
                    value=None, raw_text="", source_page=None,
                    extractor=EXTRACTOR_NAME,
                    confidence=0.0, needs_review=True, note="row_missing",
                )
            )
            continue
        raw = r["val"].strip()
        # For n=3, HUD stores as a percent; coders entered mix of 1.0 / 100 / 100%.
        # Preserve raw_text exactly; produce a normalized numeric value as well.
        if "%" in raw:
            try:
                val = float(raw.rstrip("%")) / 100.0
            except ValueError:
                val = raw
        else:
            try:
                val = float(raw)
            except ValueError:
                val = raw
        records.append(
            make_record(
                coc_id=coc_id, year=year, field_id=f"1d_2_{n}",
                value=val, raw_text=raw, source_page=r["page"],
                extractor=EXTRACTOR_NAME,
                confidence=1.0, needs_review=False,
            )
        )
    return records


NUMERIC_TOKEN_RE = re.compile(r"[\d,]+\.?\d*%?")


def extract_numeric_chart(
    pages_text: list[tuple[int, str]],
    coc_id: str,
    year: str,
    *,
    start_anchor: str,
    end_anchor: str,
    n_rows: int,
    n_cols: int,
    field_template: str,
    column_suffixes: list[str],
) -> list[dict]:
    """Parse a numbered chart whose values are numeric or percentage tokens."""
    row_re = re.compile(
        r"^\s*(\d{1,2})\.\s+(?P<label>.+?)"
        + r"".join([rf"\s+(?P<c{i}>[\d,]+\.?\d*%?)" for i in range(n_cols)])
        + r"\s*$"
    )
    captured: dict[int, dict] = {}
    start_re = re.compile(start_anchor)
    end_re = re.compile(end_anchor)
    in_section = False
    for page_num, text in pages_text:
        if not in_section:
            m = start_re.search(text)
            if not m:
                continue
            in_section = True
            source = text[m.end():]
        else:
            source = text
        e = end_re.search(source)
        if e:
            source = source[: e.start()]
            last = True
        else:
            last = False
        for line in source.splitlines():
            m = row_re.match(line)
            if not m:
                continue
            row_num = int(m.group(1))
            if row_num < 1 or row_num > n_rows:
                continue
            captured[row_num] = {
                "label": normalize_label(m.group("label")),
                "cols": [m.group(f"c{i}") for i in range(n_cols)],
                "page": page_num,
            }
        if last:
            break

    records = []
    for i in range(1, n_rows + 1):
        row = captured.get(i)
        for ci, suffix in enumerate(column_suffixes):
            field_id = field_template.format(row=i, col=suffix)
            if not row:
                records.append(
                    make_record(
                        coc_id=coc_id, year=year, field_id=field_id,
                        value=None, raw_text="", source_page=None,
                        extractor=EXTRACTOR_NAME, confidence=0.0,
                        needs_review=True, note="row_missing",
                    )
                )
                continue
            raw = row["cols"][ci].replace(",", "")
            try:
                if raw.endswith("%"):
                    val = round(float(raw.rstrip("%")) / 100.0, 4)
                else:
                    val = float(raw)
                    if val.is_integer():
                        val = int(val)
                conf = 1.0
                nr = False
                note = ""
            except ValueError:
                val = row["cols"][ci]
                conf = 0.4
                nr = True
                note = "num_parse_fail"
            records.append(
                make_record(
                    coc_id=coc_id, year=year, field_id=field_id,
                    value=val, raw_text=row["label"], source_page=row["page"],
                    extractor=EXTRACTOR_NAME,
                    confidence=conf, needs_review=nr, note=note,
                )
            )
    return records


def extract_scalar_cat(
    pages_text: list[tuple[int, str]],
    coc_id: str,
    year: str,
    *,
    qid_pattern: str,
    field_id: str,
    end_pattern: str | None = None,
) -> dict | None:
    """Extract a single Yes/No/Nonexistent value appearing on the line that
    follows a question anchor (or on the same line after the label)."""
    start_re = re.compile(qid_pattern)
    value_re = re.compile(r"\b(Yes|No|Nonexistent)\b")
    for page_num, text in pages_text:
        m = start_re.search(text)
        if not m:
            continue
        end = len(text)
        if end_pattern:
            em = re.search(end_pattern, text[m.end():])
            if em:
                end = m.end() + em.start()
        block = text[m.end(): end]
        # Take the last Yes/No before the next question anchor — the answer
        # sits at the far right of the section header's answer row.
        matches = list(value_re.finditer(block))
        if matches:
            val = normalize_categorical(matches[-1].group(1))
            return make_record(
                coc_id=coc_id, year=year, field_id=field_id,
                value=val, raw_text=val, source_page=page_num,
                extractor=EXTRACTOR_NAME, confidence=0.8,
            )
    return make_record(
        coc_id=coc_id, year=year, field_id=field_id,
        value=None, raw_text="", source_page=None,
        extractor=EXTRACTOR_NAME, confidence=0.0,
        needs_review=True, note="no_value_found",
    )


def extract_scalar_label(
    pages_text: list[tuple[int, str]],
    coc_id: str,
    year: str,
    *,
    qid_pattern: str,
    field_id: str,
    end_pattern: str,
    value_regex: str,
) -> dict:
    """Extract a single labelled value (date, string, name) following a qid.

    `value_regex` isolates the target (date pattern, HMIS vendor name, etc.)
    from within the question's body text.
    """
    start_re = re.compile(qid_pattern)
    end_re = re.compile(end_pattern)
    val_re = re.compile(value_regex)
    for page_num, text in pages_text:
        sm = start_re.search(text)
        if not sm:
            continue
        em = end_re.search(text, sm.end())
        block = text[sm.end(): em.start() if em else len(text)]
        m = val_re.search(block)
        if m:
            val = m.group(0).strip()
            return make_record(
                coc_id=coc_id, year=year, field_id=field_id,
                value=val, raw_text=val, source_page=page_num,
                extractor=EXTRACTOR_NAME, confidence=0.9,
            )
    return make_record(
        coc_id=coc_id, year=year, field_id=field_id,
        value=None, raw_text="", source_page=None,
        extractor=EXTRACTOR_NAME, confidence=0.0,
        needs_review=True, note="no_value_found",
    )


def extract_1D5_rrh(pages_text, coc_id, year):
    """1D-5 RRH beds — HIC/HMIS flag + prior-year + current-year integers.

    Typical 2024 layout:
        Enter the total number of RRH beds ... reported HIC    179    164
    The 2023/2024 numbers are the last two integers on the data line; the
    HIC/HMIS flag precedes them on the same line.
    """
    start_re = re.compile(r"\b1D-5\.")
    end_re = re.compile(r"\b1D-6\.")
    data_line_re = re.compile(
        r"Enter the total number of RRH beds[^\n]*?"
        r"(?P<flag>HIC|HMIS)?\s+(?P<a>\d{1,6})\s+(?P<b>\d{1,6})\s*$",
        re.MULTILINE,
    )
    for page_num, text in pages_text:
        sm = start_re.search(text)
        if not sm:
            continue
        em = end_re.search(text, sm.end())
        block = text[sm.end(): em.start() if em else len(text)]
        # Scan each line for the data row (numbers at end of line)
        for line in block.splitlines():
            m = re.search(r"RRH beds[^\n]*?\b(HIC|HMIS)\b[\s]*(\d{1,6})\s+(\d{1,6})\s*$", line)
            if not m:
                # Try without flag token
                m = re.search(r"RRH beds[^\n]*?(\d{1,6})\s+(\d{1,6})\s*$", line)
                if m:
                    flag, a, b = ("HIC" if "HIC" in line else "HMIS"), m.group(1), m.group(2)
                else:
                    continue
            else:
                flag, a, b = m.group(1), m.group(2), m.group(3)
            return [
                make_record(coc_id=coc_id, year=year, field_id="1d_5_hmis",
                            value=flag, raw_text=flag, source_page=page_num,
                            extractor=EXTRACTOR_NAME),
                make_record(coc_id=coc_id, year=year, field_id="1d_5_2023",
                            value=int(a), raw_text=a, source_page=page_num,
                            extractor=EXTRACTOR_NAME),
                make_record(coc_id=coc_id, year=year, field_id="1d_5_2024",
                            value=int(b), raw_text=b, source_page=page_num,
                            extractor=EXTRACTOR_NAME),
            ]
    return []


def extract_1C7_pha(pages_text, coc_id, year):
    """1C-7 PHA table — 2 rows × 4 cols (pha_name, ph_hhm, ph_limit_hhm, psh).

    The data rows may live on the page after the 1C-7 header. We join the
    first 3 pages starting from the 1C-7 anchor to be safe.
    """
    start_re = re.compile(r"\b1C-7\.")
    end_re = re.compile(r"\b1C-7a\.")
    records = []
    joined = []
    capture = False
    start_page = None
    for page_num, text in pages_text:
        if not capture:
            if start_re.search(text):
                capture = True
                start_page = page_num
        if capture:
            joined.append((page_num, text))
            if end_re.search(text):
                break
    if not joined:
        return records
    block = "\n".join(t for _, t in joined)
    page_num = start_page
    lines = block.splitlines()
    data_rows: list[dict] = []
    pha_re = re.compile(
        r"^(?P<name>[A-Z][^%\n]{3,70}?)\s{2,}"
        r"(?P<pct>\d{1,3}%?)\s+"
        r"(?P<pref>Yes[A-Za-z \-]*|No|N/A)\s{2,}"
        r"(?P<psh>Yes|No|N/A)\s*$"
    )
    for line in lines:
        if not line.strip():
            continue
        if re.match(r"^\s*(You must upload|Enter information|Public Housing Agency Name|CoC Program|FY20|Applicant:|Project:|Page )", line):
            continue
        m = pha_re.match(line)
        if not m:
            continue
        data_rows.append({
            "name": m.group("name").strip(),
            "pct": m.group("pct"),
            "pref": "Yes" if m.group("pref").lower().startswith("yes") else m.group("pref"),
            "psh": m.group("psh"),
            "page": page_num,
        })
        if len(data_rows) >= 2:
            break
    for i, r in enumerate(data_rows, start=1):
        records.append(make_record(
            coc_id=coc_id, year=year, field_id=f"1c_7_pha_name_{i}",
            value=r["name"], raw_text=r["name"],
            source_page=r["page"], extractor=EXTRACTOR_NAME,
        ))
        records.append(make_record(
            coc_id=coc_id, year=year, field_id=f"1c_7_ph_hhm_{i}",
            value=r["pct"], raw_text=r["pct"],
            source_page=r["page"], extractor=EXTRACTOR_NAME,
        ))
        records.append(make_record(
            coc_id=coc_id, year=year, field_id=f"1c_7_ph_limit_hhm_{i}",
            value=normalize_categorical(r["pref"]), raw_text=r["pref"],
            source_page=r["page"], extractor=EXTRACTOR_NAME,
        ))
        records.append(make_record(
            coc_id=coc_id, year=year, field_id=f"1c_7_psh_{i}",
            value=normalize_categorical(r["psh"]), raw_text=r["psh"],
            source_page=r["page"], extractor=EXTRACTOR_NAME,
        ))
    return records


def extract_for(coc_id: str, year: str) -> list[dict]:
    path = find_source_file(coc_id, year)
    if path is None or path.suffix.lower() != ".pdf":
        print(f"[skip] {coc_id} {year}: no native PDF")
        return []
    # Single pdftotext call for the whole document; split pages on form-feed.
    full = pdftotext_layout(path)
    pages = full.split("\x0c")
    if pages and pages[-1].strip() == "":
        pages = pages[:-1]
    pages_text = [(i + 1, t) for i, t in enumerate(pages)]
    records = []
    records.extend(extract_1A(pages_text, coc_id, year))
    records.extend(extract_1B1(pages_text, coc_id, year))
    # 1C-1 — Coordination with federal/state/local organizations (17 rows × 1 col)
    records.extend(
        extract_generic_chart(
            pages_text, coc_id, year,
            start_anchor=r"\b1C-1\.",
            end_anchor=r"\b1C-2\.",
            n_rows=17, n_cols=1,
            field_template="1c_1_{row}",
            column_suffixes=[""],
        )
    )
    # 1C-2 — ESG consultation (4 rows × 1 col)
    records.extend(
        extract_generic_chart(
            pages_text, coc_id, year,
            start_anchor=r"\b1C-2\.",
            end_anchor=r"\b1C-3\.",
            n_rows=4, n_cols=1,
            field_template="1c_2_{row}",
            column_suffixes=[""],
        )
    )
    # 1C-3 — Ensuring families not separated (5 rows × 1 col)
    records.extend(
        extract_generic_chart(
            pages_text, coc_id, year,
            start_anchor=r"\b1C-3\.",
            end_anchor=r"\b1C-4\.",
            n_rows=5, n_cols=1,
            field_template="1c_3_{row}",
            column_suffixes=[""],
        )
    )
    # 1D-1 — Preventing people transitioning from public systems (4 rows × 1 col)
    records.extend(
        extract_generic_chart(
            pages_text, coc_id, year,
            start_anchor=r"\b1D-1\.",
            end_anchor=r"\b1D-2\.",
            n_rows=4, n_cols=1,
            field_template="1d_1_{row}",
            column_suffixes=[""],
        )
    )
    # 1D-2 — Housing First numeric answers (3 values)
    records.extend(extract_1D2_numeric(pages_text, coc_id, year))
    # 1D-4 — Strategies to Prevent Criminalization (3 rows × 2 cols)
    records.extend(
        extract_generic_chart(
            pages_text, coc_id, year,
            start_anchor=r"\b1D-4\.",
            end_anchor=r"\b1D-5\.",
            n_rows=3, n_cols=2,
            field_template="1d_4_{row}_{col}",
            column_suffixes=["policymakers", "prevent_crim"],
        )
    )
    # 1D-6 — Mainstream benefits training (6 canonical rows × 1 col)
    records.extend(
        extract_generic_chart(
            pages_text, coc_id, year,
            start_anchor=r"\b1D-6\.",
            end_anchor=r"\b1D-6a\.",
            n_rows=6, n_cols=1,
            field_template="1d_6_{row}",
            column_suffixes=[""],
        )
    )
    # 1D-9b — Strategies to prevent racial disparities (11 rows × 1 col)
    records.extend(
        extract_generic_chart(
            pages_text, coc_id, year,
            start_anchor=r"\b1D-9b\.",
            end_anchor=r"\b1D-9c\.",
            n_rows=11, n_cols=1,
            field_template="1d_9b_{row}",
            column_suffixes=[""],
        )
    )
    # 1C-4c — Written/formal agreements with early childhood providers (9 × 2)
    records.extend(
        extract_generic_chart(
            pages_text, coc_id, year,
            start_anchor=r"\b1C-4c\.",
            end_anchor=r"\b1C-5\.",
            n_rows=9, n_cols=2,
            field_template="1c_4c_{row}_{col}",
            column_suffixes=["mou", "oth"],
        )
    )
    # 1C-5c — Coordinated annual DV training (6 × 2)
    records.extend(
        extract_generic_chart(
            pages_text, coc_id, year,
            start_anchor=r"\b1C-5c\.",
            end_anchor=r"\b1C-5d\.",
            n_rows=6, n_cols=2,
            field_template="1c_5c_{row}_{col}",
            column_suffixes=["proj", "ces"],
        )
    )
    # 1C-7c — Include PHA units in coordinated entry (7 × 1)
    records.extend(
        extract_generic_chart(
            pages_text, coc_id, year,
            start_anchor=r"\b1C-7c\.",
            end_anchor=r"\b1C-7d\.",
            n_rows=7, n_cols=1,
            field_template="1c_7c_{row}",
            column_suffixes=[""],
        )
    )
    # 1D-10a (FY2024) / 1D-11a (FY2022/23) — Lived experience numeric counts.
    # FY2023/24 share a 4-row structure; FY2022 had 5 rows with different labels.
    if year == "2024":
        records.extend(
            extract_numeric_chart(
                pages_text, coc_id, year,
                start_anchor=r"\b1D-10a\.",
                end_anchor=r"\b1D-10b\.",
                n_rows=4, n_cols=2,
                field_template="1d_10a_{row}_{col}",
                column_suffixes=["years", "unsheltered"],
            )
        )
    elif year == "2023":
        # Same 4 rows, same semantics; different question number.
        records.extend(
            extract_numeric_chart(
                pages_text, coc_id, year,
                start_anchor=r"\b1D-11a\.",
                end_anchor=r"\b1D-11b\.",
                n_rows=4, n_cols=2,
                field_template="1d_10a_{row}_{col}",
                column_suffixes=["years", "unsheltered"],
            )
        )
    else:  # year == "2022"
        # FY2022 had 5 rows. Map the three that conceptually align to the
        # FY2024 schema; rows 1, 2 drop. Crosswalk:
        #   FY2022 row 4 (decisionmaking)        -> 1d_10a_1_*
        #   FY2022 row 3 (CoC committees)        -> 1d_10a_2_*
        #   FY2022 row 5 (rating factors)        -> 1d_10a_3_*
        # 1d_10a_4_* (coordinated entry process) does not exist in FY2022.
        raw = extract_numeric_chart(
            pages_text, coc_id, year,
            start_anchor=r"\b1D-11a\.",
            end_anchor=r"\b1D-11b\.",
            n_rows=5, n_cols=2,
            field_template="__raw1d11a_{row}_{col}",
            column_suffixes=["years", "unsheltered"],
        )
        raw_by = {r["field_id"]: r for r in raw}
        mapping = {
            "1d_10a_1_years": "__raw1d11a_4_years",
            "1d_10a_1_unsheltered": "__raw1d11a_4_unsheltered",
            "1d_10a_2_years": "__raw1d11a_3_years",
            "1d_10a_2_unsheltered": "__raw1d11a_3_unsheltered",
            "1d_10a_3_years": "__raw1d11a_5_years",
            "1d_10a_3_unsheltered": "__raw1d11a_5_unsheltered",
        }
        for canon_id, raw_id in mapping.items():
            src = raw_by.get(raw_id)
            if not src:
                continue
            src = dict(src)  # copy
            src["field_id"] = canon_id
            src["note"] = (src.get("note") or "") + ";FY2022_crosswalk_from_1D-11a"
            records.append(src)
    # 2A-5 — HMIS bed coverage (6 × 4: non_vsp, vsp, hmis, coverage)
    records.extend(
        extract_numeric_chart(
            pages_text, coc_id, year,
            start_anchor=r"\b2A-5\.",
            end_anchor=r"\b2A-5a\.",
            n_rows=6, n_cols=4,
            field_template="2a_5_{row}_{col}",
            column_suffixes=["non_vsp", "vsp", "hmis", "coverage"],
        )
    )
    # 1C-4 — Children/Youth collaboration (4 × 1)
    records.extend(
        extract_generic_chart(
            pages_text, coc_id, year,
            start_anchor=r"\b1C-4\.",
            end_anchor=r"\b1C-4a\.",
            n_rows=4, n_cols=1,
            field_template="1c_4_{row}",
            column_suffixes=[""],
        )
    )
    # 1C-5 — DV/SA collaboration (3 × 1, row 4 is "Other" — skip)
    records.extend(
        extract_generic_chart(
            pages_text, coc_id, year,
            start_anchor=r"\b1C-5\.",
            end_anchor=r"\b1C-5a\.",
            n_rows=3, n_cols=1,
            field_template="1c_5_{row}",
            column_suffixes=[""],
        )
    )
    # 1D-9 scalar — "Has your CoC conducted a racial disparities assessment in the last 3 years?"
    rec = extract_scalar_cat(
        pages_text, coc_id, year,
        qid_pattern=r"\b1D-9\.",
        field_id="1d_9_1",
        end_pattern=r"\b1D-9a\.",
    )
    records.append(rec)
    # Scalar Yes/No questions that appear as a single answer after the qid
    for qid, fid, end in [
        (r"\b2A-6\.", "2a_6", r"\b2B-"),
        (r"\b3A-1\.", "3a_1", r"\b3A-2\."),
        (r"\b3A-2\.", "3a_2", r"\b3B-"),
        (r"\b3C-1\.", "3c_1", r"\b4A-"),
        (r"\b4A-1\.", "4a_1", r"\b4A-1a\."),
    ]:
        rec = extract_scalar_cat(
            pages_text, coc_id, year,
            qid_pattern=qid, field_id=fid, end_pattern=end,
        )
        records.append(rec)
    # 2C-1a — Displaced persons impact (2 × 1 Yes/No)
    records.extend(
        extract_generic_chart(
            pages_text, coc_id, year,
            start_anchor=r"\b2C-1a\.",
            end_anchor=r"\b2C-2\.",
            n_rows=2, n_cols=1,
            field_template="2c_1a_{row}",
            column_suffixes=[""],
        )
    )
    # 1E-2 — Project review/ranking process (5 × 1 Yes/No)
    records.extend(
        extract_generic_chart(
            pages_text, coc_id, year,
            start_anchor=r"\b1E-2\.",
            end_anchor=r"\b1E-2a\.",
            n_rows=5, n_cols=1,
            field_template="1e_2_{row}",
            column_suffixes=[""],
        )
    )
    # Scalar Yes/No: 1E-4a reallocation
    records.append(extract_scalar_cat(
        pages_text, coc_id, year,
        qid_pattern=r"\b1E-4a\.",
        field_id="1e_4a",
        end_pattern=r"\b1E-5\.",
    ))
    # 1D-9 row 2: date of racial disparities assessment
    records.append(extract_scalar_label(
        pages_text, coc_id, year,
        qid_pattern=r"\b1D-9\.", field_id="1d_9_2",
        end_pattern=r"\b1D-9a\.",
        value_regex=r"\b\d{1,2}/\d{1,2}/\d{2,4}\b",
    ))
    # HMIS / PIT metadata scalars
    records.append(extract_scalar_label(
        pages_text, coc_id, year,
        qid_pattern=r"\b2A-1\.", field_id="2a_1",
        end_pattern=r"\b2A-2\.",
        value_regex=r"HMIS Vendor.*?\n.*?([A-Z][A-Za-z0-9 &.,\-]{2,60})",
    ))
    # 2A-1 is tricky: HMIS vendor name. Use a different strategy: take
    # the last token of "Enter the name of the HMIS Vendor ... <name>".
    # Override with a simpler pattern grabbing whatever comes after the prompt line.
    records[-1] = extract_scalar_label(
        pages_text, coc_id, year,
        qid_pattern=r"HMIS Vendor your CoC is currently using",
        field_id="2a_1", end_pattern=r"\b2A-2\.",
        value_regex=r"\s{3,}(?P<v>[A-Z][A-Za-z0-9 &.,/\-]{1,60})\s*$",
    )
    records.append(extract_scalar_label(
        pages_text, coc_id, year,
        qid_pattern=r"\b2A-2\.", field_id="2a_2",
        end_pattern=r"\b2A-3\.",
        value_regex=r"(Single CoC|Multiple CoCs|Statewide|National)",
    ))
    records.append(extract_scalar_label(
        pages_text, coc_id, year,
        qid_pattern=r"\b2A-3\.", field_id="2a_3",
        end_pattern=r"\b2A-4\.",
        value_regex=r"\b\d{1,2}/\d{1,2}/\d{2,4}\b",
    ))
    records.append(extract_scalar_label(
        pages_text, coc_id, year,
        qid_pattern=r"\b2B-1\.", field_id="2b_1",
        end_pattern=r"\b2B-2\.",
        value_regex=r"\b\d{1,2}/\d{1,2}/\d{2,4}\b",
    ))
    records.append(extract_scalar_label(
        pages_text, coc_id, year,
        qid_pattern=r"\b2B-2\.", field_id="2b_2",
        end_pattern=r"\b2B-3\.",
        value_regex=r"\b\d{1,2}/\d{1,2}/\d{2,4}\b",
    ))
    # 1D-5 — RRH beds numeric
    records.extend(extract_1D5_rrh(pages_text, coc_id, year))
    # 1C-7 — PHA table
    records.extend(extract_1C7_pha(pages_text, coc_id, year))

    # 1C-7b — Moving On Strategy (4 × 1 Yes/No)
    records.extend(
        extract_generic_chart(
            pages_text, coc_id, year,
            start_anchor=r"\b1C-7b\.",
            end_anchor=r"\b1C-7c\.",
            n_rows=4, n_cols=1,
            field_template="1c_7b_{row}",
            column_suffixes=[""],
        )
    )
    # 1C-7d row 1 Yes/No (joint applications)
    records.append(extract_scalar_cat(
        pages_text, coc_id, year,
        qid_pattern=r"\b1C-7d\.", field_id="1c_7d_1",
        end_pattern=r"\b1C-7e\.",
    ))
    # 1C-7d row 2 label (Program Funding Source) — best-effort
    records.append(extract_scalar_label(
        pages_text, coc_id, year,
        qid_pattern=r"Enter the type of competitive project", field_id="1c_7d_2",
        end_pattern=r"\b1C-7e\.",
        value_regex=r"\s{3,}(?P<v>[A-Z][A-Za-z0-9 /,&\-]{2,80})\s*$",
    ))
    # 1C-7e — HCV coordination scalar Yes/No
    records.append(extract_scalar_cat(
        pages_text, coc_id, year,
        qid_pattern=r"\b1C-7e\.", field_id="1c_7e",
        end_pattern=r"\b1D-1\.",
    ))
    # 1E-1 — Two dates
    dates = []
    start_re = re.compile(r"\b1E-1\.")
    end_re = re.compile(r"\b1E-2\.")
    date_re = re.compile(r"\b\d{1,2}/\d{1,2}/\d{2,4}\b")
    for page_num, text in pages_text:
        sm = start_re.search(text)
        if not sm:
            continue
        em = end_re.search(text, sm.end())
        block = text[sm.end(): em.start() if em else len(text)]
        ds = date_re.findall(block)
        for i, d in enumerate(ds[:2], start=1):
            records.append(make_record(
                coc_id=coc_id, year=year, field_id=f"1e_1_{i}",
                value=d, raw_text=d, source_page=page_num,
                extractor=EXTRACTOR_NAME, confidence=0.85,
            ))
        break
    # 1E-2 has a potential 6th row; extend earlier chart to 6 rows
    # (re-extract to replace in place isn't clean; instead add only row 6 as a supplement)
    records.extend(
        extract_generic_chart(
            pages_text, coc_id, year,
            start_anchor=r"\b1E-2\.",
            end_anchor=r"\b1E-2a\.",
            n_rows=6, n_cols=1,
            field_template="1e_2_{row}",
            column_suffixes=[""],
        )
    )
    # 1E-2a — 2 integers + 1 label
    start_re = re.compile(r"\b1E-2a\.")
    end_re = re.compile(r"\b1E-2b\.")
    for page_num, text in pages_text:
        sm = start_re.search(text)
        if not sm:
            continue
        em = end_re.search(text, sm.end())
        block = text[sm.end(): em.start() if em else len(text)]
        # Row 1: max points — find "maximum number of points ... <N>"
        m1 = re.search(r"maximum number of points[^\n]*?(\d{1,4})\s*$", block, re.MULTILINE)
        m2 = re.search(r"how many renewal projects[^\n]*?(\d{1,4})\s*$", block, re.IGNORECASE | re.MULTILINE)
        m3 = re.search(r"renewal project type did most applicants use[^\n]*?\s{3,}(?P<v>[A-Z][A-Za-z0-9 /\-]{1,30})\s*$", block, re.MULTILINE)
        if m1:
            records.append(make_record(
                coc_id=coc_id, year=year, field_id="1e_2a_1",
                value=int(m1.group(1)), raw_text=m1.group(1), source_page=page_num,
                extractor=EXTRACTOR_NAME,
            ))
        if m2:
            records.append(make_record(
                coc_id=coc_id, year=year, field_id="1e_2a_2",
                value=int(m2.group(1)), raw_text=m2.group(1), source_page=page_num,
                extractor=EXTRACTOR_NAME,
            ))
        if m3:
            records.append(make_record(
                coc_id=coc_id, year=year, field_id="1e_2a_3",
                value=m3.group("v").strip(), raw_text=m3.group("v").strip(),
                source_page=page_num, extractor=EXTRACTOR_NAME,
            ))
        break
    # 1E-5 — 3 Yes/No rows + 1 date
    start_re = re.compile(r"\b1E-5\.")
    end_re = re.compile(r"\b1E-5a\.")
    for page_num, text in pages_text:
        sm = start_re.search(text)
        if not sm:
            continue
        em = end_re.search(text, sm.end())
        block = text[sm.end(): em.start() if em else len(text)]
        # Rows 1-3: numbered Yes/No lines
        for i in (1, 2, 3):
            pat = rf"^\s*{i}\.\s+.+?\s+(Yes|No|N/A)\s*$"
            m = re.search(pat, block, re.MULTILINE)
            if m:
                records.append(make_record(
                    coc_id=coc_id, year=year, field_id=f"1e_5_{i}",
                    value=normalize_categorical(m.group(1)),
                    raw_text=m.group(1), source_page=page_num,
                    extractor=EXTRACTOR_NAME,
                ))
        # Row 4: date
        m = re.search(r"enter the date your CoC notified[^\n]*?(\d{1,2}/\d{1,2}/\d{2,4})",
                      block, re.IGNORECASE)
        if m:
            records.append(make_record(
                coc_id=coc_id, year=year, field_id="1e_5_4",
                value=m.group(1), raw_text=m.group(1),
                source_page=page_num, extractor=EXTRACTOR_NAME,
            ))
        break
    # 1E-5a — date
    records.append(extract_scalar_label(
        pages_text, coc_id, year,
        qid_pattern=r"\b1E-5a\.", field_id="1e_5a",
        end_pattern=r"\b1E-5b\.",
        value_regex=r"\b\d{1,2}/\d{1,2}/\d{2,4}\b",
    ))
    # 1E-5b — Yes/No
    records.append(extract_scalar_cat(
        pages_text, coc_id, year,
        qid_pattern=r"\b1E-5b\.", field_id="1e_5b",
        end_pattern=r"\b1E-5c\.",
    ))
    # 1E-5c — date
    records.append(extract_scalar_label(
        pages_text, coc_id, year,
        qid_pattern=r"\b1E-5c\.", field_id="1e_5c",
        end_pattern=r"\b1E-5d\.",
        value_regex=r"\b\d{1,2}/\d{1,2}/\d{2,4}\b",
    ))
    # 1E-5d — date
    records.append(extract_scalar_label(
        pages_text, coc_id, year,
        qid_pattern=r"\b1E-5d\.", field_id="1e_5d",
        end_pattern=r"\b2A-1\.",
        value_regex=r"\b\d{1,2}/\d{1,2}/\d{2,4}\b",
    ))
    # 4A-1a — DV Bonus project types (2 × 1 Yes/No)
    records.extend(
        extract_generic_chart(
            pages_text, coc_id, year,
            start_anchor=r"\b4A-1a\.",
            end_anchor=r"\b4A-[23]\.",
            n_rows=2, n_cols=1,
            field_template="4a_1a_{row}",
            column_suffixes=[""],
        )
    )

    # Clean up generic chart suffix — when suffix is "" we produced "1c_1_1_" with trailing _.
    fixed = []
    for r in records:
        fid = r["field_id"]
        if fid.endswith("_"):
            r["field_id"] = fid.rstrip("_")
        fixed.append(r)
    return fixed


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--coc", required=True)
    ap.add_argument("--year", required=True)
    args = ap.parse_args()
    records = extract_for(args.coc, args.year)
    out = write_records(args.coc, args.year, records)
    print(f"wrote {len(records)} records -> {out}")


if __name__ == "__main__":
    main()
