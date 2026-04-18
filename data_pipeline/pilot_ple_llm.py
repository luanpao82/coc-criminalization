"""Stage-2 LLM pilot on PLE narratives.

Selects a stratified sample of CoC-years from the enriched raw file,
runs the 3 PLE narrative extractors (umbrella, prof_dev, feedback) for
each, and writes structured JSON codes to drafts/.

Output:
  drafts/pilot_ple_codes.jsonl  — one record per (coc_id, year, field)
  drafts/pilot_ple_variables.csv — aggregated per (coc_id, year), with
                                   indices computed from the structured codes

Usage:
  export ANTHROPIC_API_KEY=sk-ant-...
  python3 pilot_ple_llm.py --n-cocs 18       # 18 × 3 fields = 54 calls
  python3 pilot_ple_llm.py --dry-run         # inspect selection without hitting API
"""
from __future__ import annotations
import argparse, json, os, sys, time
from pathlib import Path
import pandas as pd

sys.path.insert(0, str(Path(__file__).parent))
from pipeline_utils import PIPELINE_DIR
from extract_narrative import (
    NARRATIVE_SPECS, SYSTEM_PROMPT, build_user_prompt, call_claude,
)

PLE_FIELDS = ["ple_umbrella", "ple_prof_dev", "ple_feedback"]
RAW_PATH = PIPELINE_DIR / "coc_raw_with_ple_narratives.xlsx"
OUT_JSONL = PIPELINE_DIR / "pilot_ple_codes.jsonl"
OUT_CSV = PIPELINE_DIR / "pilot_ple_variables.csv"


def select_sample(raw: pd.DataFrame, n_cocs: int, seed: int = 42) -> pd.DataFrame:
    """Stratified random sample: equal CoCs per year, all 3 PLE fields must be ok."""
    eligible = raw.copy()
    for fld in PLE_FIELDS:
        eligible = eligible[eligible[f"{fld}_status_code"] == "ok"]
    eligible = eligible[eligible["year"].isin([2022, 2023, 2024])]
    per_year = max(1, n_cocs // 3)
    rng = pd.Series(range(len(eligible))).sample(frac=1, random_state=seed).tolist()
    eligible = eligible.iloc[rng].copy()
    picked = (eligible.groupby("year", group_keys=False)
                      .apply(lambda g: g.head(per_year)))
    return picked.sort_values(["year", "coc_id"]).reset_index(drop=True)


def score_record(codes: dict, field: str) -> dict:
    """Turn structured codes into a small dict of numeric indicators.

    Only bool-valued codes contribute; true=1 false=0 null=NaN. Scores are
    hand-mapped to the construct hypothesis:
      - representation: ple_on_board, ple_on_committees, formal_policy,
                        decisionmaking_authority
      - compensation:   ple_compensated, paid_positions_exist,
                        compensation_policy_formal
      - feedback_loop:  feedback_mechanism_formal, acts_on_feedback,
                        closes_the_loop, addresses_barriers
    """
    def b(key):
        v = codes.get(key)
        return int(bool(v)) if isinstance(v, bool) else (float("nan") if v is None else None)

    out = {}
    if field == "ple_umbrella":
        for k in ("ple_on_board", "ple_on_committees", "ple_compensated",
                  "ple_hiring_advertised", "formal_policy", "decisionmaking_authority"):
            out[k] = b(k)
    elif field == "ple_prof_dev":
        for k in ("paid_positions_exist", "compensation_policy_formal",
                  "training_pipeline_described", "career_advancement_described",
                  "scope_beyond_tokenism"):
            out[k] = b(k)
    elif field == "ple_feedback":
        for k in ("feedback_mechanism_formal", "acts_on_feedback",
                  "addresses_barriers", "closes_the_loop"):
            out[k] = b(k)
        out["feedback_frequency"] = codes.get("feedback_frequency")
    return out


def build_variables(records: list[dict]) -> pd.DataFrame:
    """Aggregate per-field records into one row per (coc_id, year).

    Scoring convention (Krippendorff 2018, §4.3 on direct inference): absent
    evidence in a narrative response that directly elicits the practice is
    coded as absence of the indicator, i.e. None → 0. Explicit False stays 0,
    True → 1. Indices are therefore share-of-indicators-affirmed ∈ [0,1].
    """
    from collections import defaultdict
    rows = defaultdict(dict)
    for r in records:
        if r.get("status") != "coded":
            continue
        key = (r["coc_id"], int(r["year"]))
        rows[key].update(r.get("scores", {}))
        rows[key].setdefault("coc_id", r["coc_id"])
        rows[key].setdefault("year", int(r["year"]))
    df = pd.DataFrame(list(rows.values()))
    if df.empty:
        return df

    repr_cols = ["ple_on_board", "ple_on_committees", "formal_policy", "decisionmaking_authority"]
    comp_cols = ["ple_compensated", "paid_positions_exist", "compensation_policy_formal"]
    fb_cols = ["feedback_mechanism_formal", "acts_on_feedback", "addresses_barriers", "closes_the_loop"]

    def _score(df, cols):
        avail = [c for c in cols if c in df.columns]
        if not avail:
            return pd.Series([float("nan")] * len(df), index=df.index)
        # None/NaN → 0 (absent evidence), True → 1, False → 0
        return df[avail].fillna(0).astype(float).mean(axis=1)

    df["ple_representation"] = _score(df, repr_cols)
    df["ple_compensation"]   = _score(df, comp_cols)
    df["ple_feedback_loop"]  = _score(df, fb_cols)
    df["ple_institution"] = df[["ple_representation", "ple_compensation", "ple_feedback_loop"]].mean(axis=1)
    # Also compute an "available-case" robustness variant that skips None
    def _score_avail(df, cols):
        avail = [c for c in cols if c in df.columns]
        if not avail:
            return pd.Series([float("nan")] * len(df), index=df.index)
        return df[avail].astype(float).mean(axis=1, skipna=True)
    df["ple_representation_availcase"] = _score_avail(df, repr_cols)
    df["ple_compensation_availcase"]   = _score_avail(df, comp_cols)
    df["ple_feedback_loop_availcase"]  = _score_avail(df, fb_cols)

    return df.sort_values(["coc_id", "year"])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--n-cocs", type=int, default=18, help="CoCs to sample (×3 fields)")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--seed", type=int, default=42)
    args = ap.parse_args()

    raw = pd.read_excel(RAW_PATH)
    sample = select_sample(raw, args.n_cocs, args.seed)
    print(f"Selected {len(sample)} CoC-years × {len(PLE_FIELDS)} fields "
          f"= {len(sample) * len(PLE_FIELDS)} LLM calls")
    print(sample[["coc_id", "year"] + [f"{f}_length" for f in PLE_FIELDS]].to_string(index=False))

    if args.dry_run:
        return

    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        print("\nERROR: ANTHROPIC_API_KEY not set.")
        print("Run: export ANTHROPIC_API_KEY=sk-ant-...   then re-invoke this script.")
        sys.exit(1)
    import anthropic
    client = anthropic.Anthropic()

    records: list[dict] = []
    with OUT_JSONL.open("w") as fh:
        for i, (_, row) in enumerate(sample.iterrows(), start=1):
            coc_id, year = row["coc_id"], int(row["year"])
            for field in PLE_FIELDS:
                text = row[f"{field}_text"]
                page = row[f"{field}_source_page"]
                length = int(row[f"{field}_length"])
                if not isinstance(text, str) or length < 30:
                    continue
                user_prompt = build_user_prompt(text[:8000], field)
                codes = call_claude(client, SYSTEM_PROMPT, user_prompt)
                scores = score_record(codes, field) if "_parse_error" not in codes else {}
                rec = {
                    "coc_id": coc_id,
                    "year": year,
                    "field_id": field,
                    "source_page": int(page) if pd.notna(page) else None,
                    "narrative_length": length,
                    "codes": codes,
                    "scores": scores,
                    "status": "coded" if "_parse_error" not in codes else "parse_error",
                }
                records.append(rec)
                fh.write(json.dumps(rec) + "\n")
                fh.flush()
                print(f"  [{i:2d}/{len(sample)}] {coc_id} FY{year} {field:14s} → "
                      f"{'coded' if rec['status']=='coded' else 'parse_error'} "
                      f"(evidence={len(codes.get('evidence', [])) if isinstance(codes, dict) else 0})")
                time.sleep(0.2)  # politeness

    print(f"\nWrote {len(records)} raw records → {OUT_JSONL}")
    vars_df = build_variables(records)
    vars_df.to_csv(OUT_CSV, index=False)
    print(f"Wrote {len(vars_df)} aggregated CoC-year rows → {OUT_CSV}")
    print("\n-- sample of derived variables --")
    show_cols = ["coc_id", "year", "ple_representation", "ple_compensation",
                 "ple_feedback_loop", "ple_institution"]
    print(vars_df[show_cols].round(2).to_string(index=False))


if __name__ == "__main__":
    main()
