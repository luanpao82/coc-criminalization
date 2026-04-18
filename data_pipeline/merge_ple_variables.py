"""Merge LLM-derived PLE variables onto the wide panel.

Consumes:
  drafts/pilot_ple_variables.csv  (or ple_variables.csv for full run)
  coc_panel_wide.xlsx

Produces:
  coc_panel_wide_with_ple.xlsx  — original wide panel + PLE sub-indices

The merge is a LEFT JOIN on (coc_id, year). CoC-years without LLM codes
(e.g., Special NOFO, scanned, not yet coded in pilot sample) receive NaN
for the PLE columns. Downstream analysis scripts can use dropna or
indicator variables to handle missingness.
"""
from __future__ import annotations
import argparse
from pathlib import Path
import pandas as pd

PLE_VAR_COLS = [
    "ple_representation", "ple_compensation", "ple_feedback_loop",
    "ple_institution",
]
# Also carry individual bool items in case someone wants finer analysis
PLE_ITEM_COLS = [
    # umbrella
    "ple_on_board", "ple_on_committees", "ple_compensated",
    "ple_hiring_advertised", "formal_policy", "decisionmaking_authority",
    # prof_dev
    "paid_positions_exist", "compensation_policy_formal",
    "training_pipeline_described", "career_advancement_described",
    "scope_beyond_tokenism",
    # feedback
    "feedback_mechanism_formal", "acts_on_feedback",
    "addresses_barriers", "closes_the_loop",
]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--ple-vars", default="pilot_ple_variables.csv",
                    help="CSV with LLM-coded PLE indices per CoC-year")
    ap.add_argument("--panel", default="coc_panel_wide.xlsx")
    ap.add_argument("--out", default="coc_panel_wide_with_ple.xlsx")
    args = ap.parse_args()

    panel = pd.read_excel(args.panel)
    ple = pd.read_csv(args.ple_vars)
    print(f"Panel: {len(panel)} rows")
    print(f"PLE vars: {len(ple)} rows  (coverage: {len(ple)/len(panel):.1%} of panel)")

    # Only bring over PLE columns that exist in ple
    keep = ["coc_id", "year"] + [c for c in PLE_VAR_COLS + PLE_ITEM_COLS if c in ple.columns]
    merged = panel.merge(ple[keep], on=["coc_id", "year"], how="left",
                         suffixes=("", "_ple"))
    print(f"After merge: {len(merged)} rows × {len(merged.columns)} cols")

    # Coverage report
    for c in PLE_VAR_COLS:
        if c in merged.columns:
            nz = merged[c].notna().sum()
            print(f"  {c}: {nz}/{len(merged)} non-null ({nz/len(merged):.1%})")

    merged.to_excel(args.out, index=False)
    print(f"Wrote {args.out} ({Path(args.out).stat().st_size/1024:.0f} KB)")


if __name__ == "__main__":
    main()
