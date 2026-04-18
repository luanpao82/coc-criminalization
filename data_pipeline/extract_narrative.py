"""Stage-2 LLM narrative extractor.

Extracts structured codes from the priority narrative variables:

  1b_1a           — Experience Promoting Racial Equity
  1b_3            — Strategy to Solicit/Consider Opinions on Ending Homelessness
  1d_3            — Street Outreach Scope
  1d_6a           — Information & Training on Mainstream Benefits
  ple_umbrella    — Involving PLE in Service Delivery & Decisionmaking
                    (anchors: FY22/23 = 1D-11; FY24 = 1D-10)
  ple_prof_dev    — Professional Development & Employment for PLE
                    (anchors: FY22/23 = 1D-11b; FY24 = 1D-10b)
  ple_feedback    — Routinely Gathering Feedback from PLE
                    (anchors: FY22/23 = 1D-11c; FY24 = 1D-10c)
  2c_1            — Reduction in First Time Homeless — Risk Factors

Design rules (per data_construction_methodology.md §4.2)
  * Each LLM call MUST return verbatim sentence quotations as evidence.
  * Outputs land in drafts/, never directly into the canonical dataset.
  * Reviewer approval before any draft is promoted to the final xlsx.
  * Uses prompt caching: the system prompt + codebook excerpt are cached.

Usage
-----
  export ANTHROPIC_API_KEY=sk-...
  python3 extract_narrative.py --dry-run --limit 3
  python3 extract_narrative.py --year 2024 --limit 10
  python3 extract_narrative.py --all
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
import time
from pathlib import Path

from pipeline_utils import DATA_DIR, PIPELINE_DIR, find_source_file, pdftotext_layout

DRAFTS_DIR = PIPELINE_DIR / "drafts"
DRAFTS_DIR.mkdir(parents=True, exist_ok=True)

MODEL = "claude-opus-4-7"

NARRATIVE_SPECS = {
    "1b_1a": {
        "anchor": r"\b1B-1a\.",
        "next_anchor": r"\b1B-2\.",
        "title": "Experience Promoting Racial Equity",
        "schema": {
            "engages_black_brown_communities": "bool — does the CoC describe concrete engagement with Black and Brown communities?",
            "pwle_on_governance_bodies": "bool — are people with lived experience on board/committees?",
            "anti_racism_training": "bool — does the CoC describe anti-racism/diversity training?",
            "data_disaggregated_by_race": "bool — does the CoC use race-disaggregated data?",
            "partnerships_with_poc_led_orgs": "bool — partnerships with Black/Brown-led nonprofits?",
            "summary": "string — one-sentence summary of the CoC's racial-equity approach",
            "evidence": "list[string] — up to 3 verbatim quotations supporting the codes above",
        },
    },
    "1b_3": {
        "anchor": r"\b1B-3\.",
        "next_anchor": r"\b1B-4\.",
        "title": "Strategy to Solicit/Consider Opinions on Ending Homelessness",
        "schema": {
            "public_meetings_mentioned": "bool — does the CoC hold public meetings / town halls?",
            "surveys_used": "bool — surveys or focus groups referenced?",
            "pwle_voice_mentioned": "bool — people with lived experience explicitly referenced in opinion solicitation?",
            "racial_equity_consultation": "bool — Black/Brown/Indigenous communities mentioned in consultation?",
            "summary": "string — one-sentence summary",
            "evidence": "list[string] — up to 3 verbatim quotations",
        },
    },
    "1d_3": {
        "anchor": r"\b1D-3\.",
        "next_anchor": r"\b1D-4\.",
        "title": "Street Outreach Scope",
        "schema": {
            "covers_entire_geography": "bool — does outreach cover the entire CoC geography?",
            "frequency": "string — how often outreach occurs (e.g., 'daily', 'weekly')",
            "engages_unsheltered_specifically": "bool",
            "uses_hmis_tracking": "bool",
            "summary": "string — one-sentence summary",
            "evidence": "list[string] — up to 3 verbatim quotations",
        },
    },
    "1d_6a": {
        "anchor": r"\b1D-6a\.",
        "next_anchor": r"\b1D-7\.",
        "title": "Information and Training on Mainstream Benefits",
        "schema": {
            "annual_training_described": "bool",
            "benefits_enrolled_at_intake": "bool — describes enrollment support at intake?",
            "healthcare_coordination": "bool — explicit coordination with healthcare providers?",
            "summary": "string",
            "evidence": "list[string] — up to 3 verbatim quotations",
        },
    },
    "ple_umbrella": {
        "anchors_by_year": {
            "2022": {"anchor": r"\b1D-11\.",  "next_anchor": r"\b1D-11a\.|\b1E-1\."},
            "2023": {"anchor": r"\b1D-11\.",  "next_anchor": r"\b1D-11a\.|\b1E-1\."},
            "2024": {"anchor": r"\b1D-10\.",  "next_anchor": r"\b1D-10a\.|\b1E-1\."},
        },
        "title": "Involving Individuals with Lived Experience in Service Delivery and Decisionmaking",
        "schema": {
            "ple_on_board": "bool — PLE formally seated on the CoC governing board?",
            "ple_on_committees": "bool — PLE on CoC committees/workgroups?",
            "ple_compensated": "bool — are PLE compensated (wage/stipend/transport) for their time?",
            "ple_hiring_advertised": "bool — are PLE roles publicly advertised rather than hand-picked?",
            "formal_policy": "bool — is there a written/codified policy governing PLE engagement?",
            "decisionmaking_authority": "bool — do PLE have voting or veto power on policy decisions (beyond advisory)?",
            "summary": "string — one-sentence summary of the CoC's PLE engagement structure",
            "evidence": "list[string] — up to 3 verbatim quotations supporting the codes above",
        },
    },
    "ple_prof_dev": {
        "anchors_by_year": {
            "2022": {"anchor": r"\b1D-11b\.", "next_anchor": r"\b1D-11c\.|\b1E-1\."},
            "2023": {"anchor": r"\b1D-11b\.", "next_anchor": r"\b1D-11c\.|\b1E-1\."},
            "2024": {"anchor": r"\b1D-10b\.", "next_anchor": r"\b1D-10c\.|\b1E-1\."},
        },
        "title": "Professional Development and Employment Opportunities for Individuals with Lived Experience",
        "schema": {
            "paid_positions_exist": "bool — are there paid staff positions for PLE described?",
            "compensation_policy_formal": "bool — formal written compensation policy (rates/schedule)?",
            "training_pipeline_described": "bool — training, mentorship, or certification pathway for PLE?",
            "career_advancement_described": "bool — promotion or advancement path described, not only entry-level?",
            "scope_beyond_tokenism": "bool — evidence of PLE in substantive roles (supervisory/programmatic) rather than single advisory seat?",
            "summary": "string — one-sentence summary",
            "evidence": "list[string] — up to 3 verbatim quotations",
        },
    },
    "ple_feedback": {
        "anchors_by_year": {
            "2022": {"anchor": r"\b1D-11c\.", "next_anchor": r"\b1D-12\.|\b1E-1\."},
            "2023": {"anchor": r"\b1D-11c\.", "next_anchor": r"\b1D-12\.|\b1E-1\."},
            "2024": {"anchor": r"\b1D-10c\.", "next_anchor": r"\b1D-11\.|\b1E-1\."},
        },
        "title": "Routinely Gathering Feedback and Addressing Challenges of Individuals with Lived Experience",
        "schema": {
            "feedback_mechanism_formal": "bool — formal channel (standing meeting, survey, focus group) vs ad-hoc?",
            "feedback_frequency": "string — stated cadence (e.g., 'monthly', 'quarterly', 'annual', 'continuous'); null if unstated",
            "acts_on_feedback": "bool — concrete example of feedback causing a policy/practice change?",
            "addresses_barriers": "bool — accommodations described (language, transport, childcare, tech access)?",
            "closes_the_loop": "bool — does the CoC report back to PLE on how feedback was used?",
            "summary": "string — one-sentence summary",
            "evidence": "list[string] — up to 3 verbatim quotations",
        },
    },
    "2c_1": {
        "anchor": r"\b2C-1\.",
        "next_anchor": r"\b2C-1a\.",
        "title": "Reduction in First Time Homeless — Risk Factors",
        "schema": {
            "uses_hmis_data": "bool",
            "targets_specific_risk_factors": "list[string] — risk factors mentioned (eviction, discharge, rent burden, etc.)",
            "prevention_services_mentioned": "bool",
            "summary": "string",
            "evidence": "list[string] — up to 3 verbatim quotations",
        },
    },
}


SYSTEM_PROMPT = """You are an expert research assistant extracting structured codes from HUD Continuum of Care (CoC) application narratives.

Your job: given the narrative text for a single question, return ONLY a JSON object matching the schema. Every coded claim must be supported by a verbatim quotation from the source text in the `evidence` field. If the text does not contain enough information to code a field, use `null`; do NOT fabricate.

Rules:
- Output JSON only, no prose before or after.
- `evidence` must contain exact verbatim substrings from the input.
- If the entire narrative is blank or irrelevant, return {"summary": "no response", "evidence": []} with all other fields null.
"""


def slice_narrative(pdf_path: Path, start_pat: str, end_pat: str) -> tuple[str, int | None]:
    """Return (narrative_text, source_page) between two question anchors."""
    full = pdftotext_layout(pdf_path)
    pages = full.split("\x0c")
    if pages and pages[-1].strip() == "":
        pages = pages[:-1]
    start_re = re.compile(start_pat)
    end_re = re.compile(end_pat)
    collecting = False
    buf = []
    start_page = None
    for i, t in enumerate(pages, start=1):
        if not collecting:
            m = start_re.search(t)
            if m:
                collecting = True
                start_page = i
                # Start from just after the title line
                buf.append(t[m.end():])
                if end_re.search(t, m.end()):
                    break
        else:
            em = end_re.search(t)
            if em:
                buf.append(t[: em.start()])
                break
            buf.append(t)
    text = "\n".join(buf).strip()
    # Trim header/footer noise
    text = re.sub(r"\n\s*(Applicant:|Project:|FY20\d{2} CoC Application|Page \d+)[^\n]*", "", text)
    return text, start_page


def build_user_prompt(narrative_text: str, field_id: str) -> str:
    spec = NARRATIVE_SPECS[field_id]
    schema_str = "\n".join(f'  "{k}": {v}' for k, v in spec["schema"].items())
    return f"""Question: {spec["title"]} (HUD field {field_id})

Schema:
{{
{schema_str}
}}

Narrative text:
\"\"\"
{narrative_text}
\"\"\"

Return a JSON object matching the schema above. Remember: every non-null field must be backed by a verbatim quote in `evidence`.
"""


def call_claude(client, system_prompt: str, user_prompt: str, cache: bool = True) -> dict:
    """Call Claude and parse JSON response."""
    system_blocks = [{"type": "text", "text": system_prompt}]
    if cache:
        system_blocks[0]["cache_control"] = {"type": "ephemeral"}
    resp = client.messages.create(
        model=MODEL,
        max_tokens=1500,
        system=system_blocks,
        messages=[{"role": "user", "content": user_prompt}],
    )
    raw = resp.content[0].text.strip()
    # Strip any accidental fences
    raw = re.sub(r"^```(?:json)?\s*|\s*```$", "", raw, flags=re.MULTILINE)
    try:
        return json.loads(raw)
    except json.JSONDecodeError as e:
        return {"_parse_error": str(e), "_raw": raw[:500]}


def resolve_anchors(spec: dict, year: str) -> tuple[str, str]:
    """Pick (anchor, next_anchor) for this year — year-branched fields override
    the shared defaults. Raises KeyError if a year-branched field has no entry
    for the requested year (fail loud rather than fall back silently)."""
    if "anchors_by_year" in spec:
        yr_spec = spec["anchors_by_year"][year]
        return yr_spec["anchor"], yr_spec["next_anchor"]
    return spec["anchor"], spec["next_anchor"]


def process_one(client, coc_id: str, year: str, field_id: str, dry_run: bool) -> dict | None:
    pdf_path = find_source_file(coc_id, year)
    if pdf_path is None or pdf_path.suffix.lower() != ".pdf":
        return None
    spec = NARRATIVE_SPECS[field_id]
    anchor, next_anchor = resolve_anchors(spec, year)
    text, page = slice_narrative(pdf_path, anchor, next_anchor)
    if len(text) < 30:
        return {"coc_id": coc_id, "year": year, "field_id": field_id,
                "status": "no_narrative", "source_page": page}
    user_prompt = build_user_prompt(text[:8000], field_id)
    if dry_run:
        print(f"\n[dry-run] {coc_id} {year} {field_id} — page {page}, len {len(text)}")
        print(user_prompt[:500], "...")
        return {"coc_id": coc_id, "year": year, "field_id": field_id,
                "status": "dry_run", "source_page": page, "text_preview": text[:300]}
    codes = call_claude(client, SYSTEM_PROMPT, user_prompt)
    return {
        "coc_id": coc_id, "year": year, "field_id": field_id,
        "source_page": page,
        "codes": codes,
        "narrative_length": len(text),
        "status": "coded",
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true", help="Print prompts without calling API")
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--year", choices=["2022", "2023", "2024"], default="2024")
    ap.add_argument("--field", choices=list(NARRATIVE_SPECS.keys()),
                    default="1b_1a",
                    help="Which narrative field to process (default: 1b_1a)")
    ap.add_argument("--all", action="store_true", help="Run every CoC × year × field combination")
    args = ap.parse_args()

    if not args.dry_run:
        api_key = os.environ.get("ANTHROPIC_API_KEY")
        if not api_key:
            print("ERROR: ANTHROPIC_API_KEY not set. Export it before running, or use --dry-run.")
            sys.exit(1)
        import anthropic
        client = anthropic.Anthropic()
    else:
        client = None

    # Build (coc_id, year, field_id) queue
    import csv as _csv
    inv_path = PIPELINE_DIR / "file_inventory.csv"
    with inv_path.open() as f:
        inv = list(_csv.DictReader(f))
    target_years = ["2022", "2023", "2024"] if args.all else [args.year]
    target_fields = list(NARRATIVE_SPECS.keys()) if args.all else [args.field]
    cocs_per_year = {
        y: sorted({r["coc_id"] for r in inv
                   if r["year"] == y and r["format"] == "pdf" and r["is_scanned"] != "TRUE"})
        for y in target_years
    }

    queue = []
    for y in target_years:
        for fld in target_fields:
            for coc in cocs_per_year[y]:
                queue.append((coc, y, fld))
    if args.limit:
        queue = queue[: args.limit]
    print(f"Queue: {len(queue)} calls")

    out_path = DRAFTS_DIR / f"narrative_{args.field if not args.all else 'all'}_{args.year}.jsonl"
    written = 0
    with out_path.open("a") as f:
        for i, (coc, yr, fld) in enumerate(queue, start=1):
            rec = process_one(client, coc, yr, fld, dry_run=args.dry_run)
            if rec:
                f.write(json.dumps(rec) + "\n")
                written += 1
            if i % 10 == 0:
                print(f"  [{i}/{len(queue)}] processed")
            # Simple politeness on API calls
            if not args.dry_run:
                time.sleep(0.1)
    print(f"wrote {written} records to {out_path}")


if __name__ == "__main__":
    main()
