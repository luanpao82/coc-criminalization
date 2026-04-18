"""Compute descriptive statistics for the anti-criminalization activity index
and write them to `descriptive_stats.json` for the site page to consume.

Produces:
  1. Sample composition by year (N, % nonprofit-led)
  2. Activity index descriptives by year (overall + by leadership)
  3. Cell-level breakdown of the 1D-4 chart (6 cells × 3 years)
  4. Year-over-year change (Δ) statistics
  5. Paired comparison: CoCs present in all 3 years
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd

from pipeline_utils import PIPELINE_DIR

ANALYSIS_XLSX = PIPELINE_DIR / "coc_analysis_ready.xlsx"
OUT = PIPELINE_DIR / "descriptive_stats.json"

CELL_LABELS = {
    "1d_4_1_policymakers": ("Row 1 · Policymaker engagement",
                             "FY22/23: engaged local policymakers to prevent criminalization · "
                             "FY24: engaged legislators on co-responder responses"),
    "1d_4_1_prevent_crim": ("Row 1 · Implementation",
                             "FY22/23: reverse existing criminalization policies · "
                             "FY24: implemented laws for co-responder responses"),
    "1d_4_2_policymakers": ("Row 2 · Policymaker engagement",
                             "FY22/23: engaged law enforcement · "
                             "FY24: engaged legislators on minimizing law enforcement"),
    "1d_4_2_prevent_crim": ("Row 2 · Implementation",
                             "FY22/23: reverse existing · "
                             "FY24: implemented laws minimizing LE for basic life functions"),
    "1d_4_3_policymakers": ("Row 3 · Policymaker engagement",
                             "FY22/23: engaged business leaders · "
                             "FY24: engaged legislators on avoiding criminal sanctions"),
    "1d_4_3_prevent_crim": ("Row 3 · Implementation",
                             "FY22/23: reverse existing · "
                             "FY24: implemented laws avoiding criminal sanctions"),
}


def to_num(v):
    if v in ("", None): return None
    try:
        return float(v)
    except (ValueError, TypeError):
        return None


def load() -> pd.DataFrame:
    df = pd.read_excel(ANALYSIS_XLSX, sheet_name="unbalanced")
    iv = pd.read_excel(ANALYSIS_XLSX, sheet_name="iv_leadership")
    df = df.merge(iv[["coc_id", "nonprofit_led"]], on="coc_id", how="left")
    df["year"] = df["year"].astype(int)
    df["crim_activity_index"] = pd.to_numeric(df["crim_activity_index"], errors="coerce")
    df["nonprofit_led"] = pd.to_numeric(df["nonprofit_led"], errors="coerce")
    return df


def stats(vals):
    v = [x for x in vals if x is not None and not pd.isna(x)]
    if not v:
        return {"n": 0}
    v = np.array(v, dtype=float)
    q = np.quantile(v, [0.25, 0.5, 0.75])
    return {
        "n": int(len(v)),
        "mean": round(float(v.mean()), 4),
        "sd": round(float(v.std(ddof=1)), 4) if len(v) > 1 else 0,
        "se": round(float(v.std(ddof=1) / np.sqrt(len(v))), 4) if len(v) > 1 else 0,
        "min": round(float(v.min()), 4),
        "q25": round(float(q[0]), 4),
        "median": round(float(q[1]), 4),
        "q75": round(float(q[2]), 4),
        "max": round(float(v.max()), 4),
        "at_zero": int((v == 0).sum()),
        "at_one": int((v == 1).sum()),
        "hist_counts": np.histogram(v, bins=np.linspace(0, 1, 8))[0].tolist(),
    }


def yes_rate(series):
    s = series.astype(str).str.strip().str.lower()
    total = s.isin(["yes", "no", "nonexistent"]).sum()
    if total == 0:
        return None
    return round(float((s == "yes").sum()) / total, 4)


def main():
    df = load()

    # 1. Sample composition by year
    sample = {}
    for y in (2022, 2023, 2024):
        sub = df[df["year"] == y]
        sample[str(y)] = {
            "n_records": int(len(sub)),
            "n_cocs": int(sub["coc_id"].nunique()),
            "coded_iv": int(sub["nonprofit_led"].notna().sum()),
            "nonprofit": int((sub["nonprofit_led"] == 1).sum()),
            "government": int((sub["nonprofit_led"] == 0).sum()),
            "pct_nonprofit": round(float((sub["nonprofit_led"] == 1).mean() * 100), 1),
            "with_dv": int(sub["crim_activity_index"].notna().sum()),
        }

    # 2. Activity index descriptives
    activity = {}
    for y in (2022, 2023, 2024):
        sub = df[df["year"] == y]
        activity[str(y)] = {
            "overall": stats(sub["crim_activity_index"].tolist()),
            "nonprofit": stats(
                sub.loc[sub["nonprofit_led"] == 1, "crim_activity_index"].tolist()),
            "government": stats(
                sub.loc[sub["nonprofit_led"] == 0, "crim_activity_index"].tolist()),
        }

    # 3. Cell-level Yes rates (6 cells × 3 years)
    cell_rates = []
    for fid, (label, sub_label) in CELL_LABELS.items():
        row = {"field": fid, "label": label, "sublabel": sub_label, "years": {}}
        for y in (2022, 2023, 2024):
            sub = df[df["year"] == y]
            row["years"][str(y)] = {
                "overall": yes_rate(sub[fid]) if fid in sub.columns else None,
                "nonprofit": yes_rate(sub.loc[sub["nonprofit_led"] == 1, fid]) if fid in sub.columns else None,
                "government": yes_rate(sub.loc[sub["nonprofit_led"] == 0, fid]) if fid in sub.columns else None,
            }
        cell_rates.append(row)

    # 4. Δ table — simple between-year differences
    deltas = {
        "overall": {
            "FY22_FY23": round(activity["2023"]["overall"]["mean"] - activity["2022"]["overall"]["mean"], 4),
            "FY23_FY24": round(activity["2024"]["overall"]["mean"] - activity["2023"]["overall"]["mean"], 4),
            "FY22_FY24": round(activity["2024"]["overall"]["mean"] - activity["2022"]["overall"]["mean"], 4),
        },
        "nonprofit": {
            "FY22_FY23": round(activity["2023"]["nonprofit"]["mean"] - activity["2022"]["nonprofit"]["mean"], 4),
            "FY23_FY24": round(activity["2024"]["nonprofit"]["mean"] - activity["2023"]["nonprofit"]["mean"], 4),
            "FY22_FY24": round(activity["2024"]["nonprofit"]["mean"] - activity["2022"]["nonprofit"]["mean"], 4),
        },
        "government": {
            "FY22_FY23": round(activity["2023"]["government"]["mean"] - activity["2022"]["government"]["mean"], 4),
            "FY23_FY24": round(activity["2024"]["government"]["mean"] - activity["2023"]["government"]["mean"], 4),
            "FY22_FY24": round(activity["2024"]["government"]["mean"] - activity["2022"]["government"]["mean"], 4),
        },
    }

    # 5. Paired sample (CoCs present in all 3 years)
    years_per_coc = df.groupby("coc_id")["year"].nunique()
    balanced = years_per_coc[years_per_coc == 3].index.tolist()
    df_bal = df[df["coc_id"].isin(balanced)]
    balanced_stats = {}
    for y in (2022, 2023, 2024):
        sub = df_bal[df_bal["year"] == y]
        balanced_stats[str(y)] = stats(sub["crim_activity_index"].tolist())
    # Paired Δ
    pivot = df_bal.pivot(index="coc_id", columns="year", values="crim_activity_index")
    pivot = pivot.dropna()
    if len(pivot) > 0:
        paired_deltas = {
            "n_paired": int(len(pivot)),
            "mean_FY22": round(float(pivot[2022].mean()), 4),
            "mean_FY23": round(float(pivot[2023].mean()), 4),
            "mean_FY24": round(float(pivot[2024].mean()), 4),
            "mean_delta_23_24": round(float((pivot[2024] - pivot[2023]).mean()), 4),
            "sd_delta_23_24": round(float((pivot[2024] - pivot[2023]).std()), 4),
            "share_increased": round(float((pivot[2024] > pivot[2023]).mean()), 4),
            "share_decreased": round(float((pivot[2024] < pivot[2023]).mean()), 4),
            "share_unchanged": round(float((pivot[2024] == pivot[2023]).mean()), 4),
        }
    else:
        paired_deltas = None

    out = {
        "generated_at": pd.Timestamp.now().isoformat(timespec="seconds"),
        "sample": sample,
        "activity_index": activity,
        "cell_rates": cell_rates,
        "deltas": deltas,
        "balanced_panel": {
            "n_cocs": len(balanced),
            "year_stats": balanced_stats,
            "paired": paired_deltas,
        },
    }
    OUT.write_text(json.dumps(out, indent=2))
    print(f"wrote {OUT}")

    # Pretty console preview
    print("\n=== Sample ===")
    for y, s in sample.items():
        print(f"  FY{y}: {s['n_records']} records, {s['coded_iv']} IV-coded, "
              f"{s['pct_nonprofit']}% nonprofit")
    print("\n=== Activity index (overall) ===")
    for y in ("2022", "2023", "2024"):
        a = activity[y]["overall"]
        print(f"  FY{y}: n={a['n']}  mean={a['mean']}  median={a['median']}  SD={a['sd']}  "
              f"at-0={a['at_zero']}  at-1={a['at_one']}")
    print("\n=== Year-to-year Δ ===")
    for g, d in deltas.items():
        print(f"  {g}: FY22→23 {d['FY22_FY23']:+.4f}  |  FY23→24 {d['FY23_FY24']:+.4f}  "
              f"|  FY22→24 {d['FY22_FY24']:+.4f}")
    print("\n=== Cell-level Yes rates (overall) ===")
    for r in cell_rates:
        row = [r["years"][y]["overall"] for y in ("2022", "2023", "2024")]
        print(f"  {r['field']}:  FY22={row[0]}  FY23={row[1]}  FY24={row[2]}")
    if paired_deltas:
        print("\n=== Balanced paired sample (same CoCs across 3 years) ===")
        print(f"  N paired CoCs: {paired_deltas['n_paired']}")
        print(f"  mean FY22={paired_deltas['mean_FY22']}, FY23={paired_deltas['mean_FY23']}, "
              f"FY24={paired_deltas['mean_FY24']}")
        print(f"  paired Δ(FY24-FY23) mean = {paired_deltas['mean_delta_23_24']:+.4f} "
              f"(SD {paired_deltas['sd_delta_23_24']:.4f})")
        print(f"  % CoCs increased FY23→FY24: {paired_deltas['share_increased']*100:.1f}%")


if __name__ == "__main__":
    main()
