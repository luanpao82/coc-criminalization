"""Run the panel regression described in the research model.

DV    : crim_activity_index (fraction 0–1; OLS-FE + fractional logit)
IV    : nonprofit_led (1 = nonprofit-led CoC, 0 = government-led)
MED   : log1p(1d_10a_1_years) + 1b_1_6_voted + 1b_1_6_ces
CTRL  : 1d_2_3 (Housing First %),
        2a_5_1_coverage (HMIS ES coverage),
        log1p(total_beds = sum of 2a_5_*_non_vsp)
FE    : CoC fixed effects, year fixed effects (two-way)

Models estimated
---------------
 M1  OLS-FE   direct effect (IV only, + controls + FE)
 M2  OLS-FE   with mediators (IV, MED, controls, FE)
 M3  OLS-FE   FY24 cross-section (full mediator set, no CoC FE since 1 year)
 M4  Frac.logit, pooled with CoC-clustered SEs (handles censoring at 0/1)

Outputs
-------
 panel_regression_results.md   — human-readable results
 panel_regression_coefs.csv    — every coefficient table flat-pasted
"""
from __future__ import annotations

import math
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from linearmodels.panel import PanelOLS
import statsmodels.api as sm
import statsmodels.formula.api as smf

from pipeline_utils import PIPELINE_DIR

ANALYSIS_XLSX = PIPELINE_DIR / "coc_analysis_ready.xlsx"
OUT_MD = PIPELINE_DIR / "panel_regression_results.md"
OUT_CSV = PIPELINE_DIR / "panel_regression_coefs.csv"


def load_panel() -> pd.DataFrame:
    # Unbalanced panel (all observed CoC-years)
    df = pd.read_excel(ANALYSIS_XLSX, sheet_name="unbalanced")
    iv = pd.read_excel(ANALYSIS_XLSX, sheet_name="iv_leadership")
    iv = iv[["coc_id", "lead_agency_type", "nonprofit_led"]]
    df = df.merge(iv, on="coc_id", how="left")

    # Types
    df["year"] = df["year"].astype(int)

    # --- Transformations -----------------------------------------------------
    # DV stays in [0,1] fraction
    df["crim_activity_index"] = pd.to_numeric(df["crim_activity_index"], errors="coerce")

    # Binary mediators
    for col in ("1b_1_6_voted", "1b_1_6_ces", "1b_1_6_meetings"):
        s = df[col].astype(str).str.strip().str.lower()
        df[col + "_bin"] = (s == "yes").astype(float)
        df.loc[~s.isin(["yes", "no", "nonexistent"]), col + "_bin"] = np.nan

    # Count mediators — log1p
    for col in ("1d_10a_1_years", "1d_10a_1_unsheltered",
                "1d_10a_2_years", "1d_10a_3_years"):
        v = pd.to_numeric(df[col], errors="coerce")
        df["log_" + col] = np.log1p(v.where(v >= 0))

    # Controls
    df["hf_pct"] = pd.to_numeric(df["1d_2_3"], errors="coerce")
    # Housing First stored inconsistently (some 0–1, some 0–100) — normalize
    df.loc[df["hf_pct"] > 1.5, "hf_pct"] = df["hf_pct"] / 100

    df["hmis_es_cov"] = pd.to_numeric(df["2a_5_1_coverage"], errors="coerce")
    df.loc[df["hmis_es_cov"] > 1.5, "hmis_es_cov"] = df["hmis_es_cov"] / 100
    # Clip above 1 (a handful of coder typos pushed above 1)
    df.loc[df["hmis_es_cov"] > 1.0, "hmis_es_cov"] = 1.0

    # Total beds = sum of non_vsp across project types that are present
    bed_cols = [c for c in (f"2a_5_{i}_non_vsp" for i in range(1, 7)) if c in df.columns]
    bed_sum = pd.DataFrame({c: pd.to_numeric(df[c], errors="coerce") for c in bed_cols}).sum(axis=1, min_count=1)
    df["log_total_beds"] = np.log1p(bed_sum)

    df["nonprofit_led"] = pd.to_numeric(df["nonprofit_led"], errors="coerce")

    return df


def fit_ols_fe(df, formula_vars, label, include_coc_fe=True, include_year_fe=True):
    """Run a two-way FE panel OLS with CoC-clustered SEs."""
    sub = df.dropna(subset=["crim_activity_index"] + formula_vars).copy()
    if include_coc_fe:
        sub = sub.set_index(["coc_id", "year"])
    else:
        sub = sub.reset_index(drop=True)

    y = sub["crim_activity_index"].astype(float)
    X = sub[formula_vars].astype(float)
    X = sm.add_constant(X, has_constant="add")
    if include_coc_fe:
        mod = PanelOLS(y, X, entity_effects=True, time_effects=include_year_fe,
                       drop_absorbed=True)
        res = mod.fit(cov_type="clustered", cluster_entity=True)
    else:
        # Cross-section (no fixed effects; robust SE)
        mod = sm.OLS(y, X, missing="drop")
        res = mod.fit(cov_type="HC3")
    return res, sub


def fit_frac_logit(df, formula_vars, label):
    """Pooled fractional logit with CoC-clustered SEs (robust alternative to OLS)."""
    sub = df.dropna(subset=["crim_activity_index"] + formula_vars + ["coc_id"]).copy()
    y = sub["crim_activity_index"].astype(float)
    X = sub[formula_vars].astype(float)
    X = sm.add_constant(X, has_constant="add")
    # Year dummies (drop first)
    year_dummies = pd.get_dummies(sub["year"], prefix="year", drop_first=True).astype(float)
    X = pd.concat([X, year_dummies], axis=1)
    mod = sm.GLM(y, X, family=sm.families.Binomial())
    res = mod.fit(cov_type="cluster", cov_kwds={"groups": sub["coc_id"].values})
    return res, sub


# ---------------------------------------------------------------------------
# Report helpers
# ---------------------------------------------------------------------------
def fmt_coef(v, se=None, pvalue=None):
    if v is None or pd.isna(v):
        return "—"
    star = ""
    if pvalue is not None and not pd.isna(pvalue):
        if pvalue < 0.01:
            star = "***"
        elif pvalue < 0.05:
            star = "**"
        elif pvalue < 0.1:
            star = "*"
    if se is None or pd.isna(se):
        return f"{v:.3f}{star}"
    return f"{v:.3f}{star}<br><span class='hint'>({se:.3f})</span>"


def linearmodels_coefs(res):
    p = res.params; se = res.std_errors; pv = res.pvalues
    out = {}
    for n in p.index:
        out[n] = (p[n], se[n], pv[n])
    return out


def sm_coefs(res):
    p = res.params; se = res.bse; pv = res.pvalues
    out = {}
    for n in p.index:
        out[n] = (p[n], se[n], pv[n])
    return out


def main():
    df = load_panel()
    print(f"Loaded {len(df)} rows. Nonprofit_led coded: {df['nonprofit_led'].notna().sum()} "
          f"(nonprofit={int((df['nonprofit_led']==1).sum())}, gov={int((df['nonprofit_led']==0).sum())})")

    base_controls = ["hf_pct", "hmis_es_cov", "log_total_beds"]

    # M1: Direct effect, OLS-FE
    vars_m1 = ["nonprofit_led"] + base_controls
    res_m1, sub1 = fit_ols_fe(df, vars_m1, "M1")
    # M2: Add mediators
    vars_m2 = ["nonprofit_led",
               "log_1d_10a_1_years", "1b_1_6_voted_bin", "1b_1_6_ces_bin"] + base_controls
    res_m2, sub2 = fit_ols_fe(df, vars_m2, "M2")
    # M3: FY24 cross-section (no CoC FE)
    df24 = df[df["year"] == 2024].copy()
    res_m3, sub3 = fit_ols_fe(df24, vars_m2, "M3", include_coc_fe=False, include_year_fe=False)
    # M4: Pooled fractional logit
    res_m4, sub4 = fit_frac_logit(df, vars_m2, "M4")

    # Build results table
    all_vars = ["nonprofit_led",
                "log_1d_10a_1_years", "1b_1_6_voted_bin", "1b_1_6_ces_bin",
                "hf_pct", "hmis_es_cov", "log_total_beds", "const"]
    label_map = {
        "nonprofit_led": "Nonprofit-led CoC (IV)",
        "log_1d_10a_1_years": "log(PLE in decisionmaking + 1)",
        "1b_1_6_voted_bin": "PLE voted in CoC (binary)",
        "1b_1_6_ces_bin": "PLE in CES (binary)",
        "hf_pct": "Housing First adoption (share)",
        "hmis_es_cov": "HMIS ES coverage (share)",
        "log_total_beds": "log(total beds + 1)",
        "const": "(Intercept)",
    }

    c1 = linearmodels_coefs(res_m1); c2 = linearmodels_coefs(res_m2)
    c3 = sm_coefs(res_m3); c4 = sm_coefs(res_m4)

    def r(v, table):
        return table.get(v, (None, None, None))

    header = [
        "| Variable | M1 (OLS-FE, direct) | M2 (OLS-FE + mediators) | M3 (FY24 cross-section) | M4 (Frac. logit, pooled) |",
        "|---|---|---|---|---|",
    ]
    rows = []
    for v in all_vars:
        row = [label_map.get(v, v)]
        for t in (c1, c2, c3, c4):
            p, se, pv = r(v, t)
            row.append(fmt_coef(p, se, pv))
        rows.append("| " + " | ".join(row) + " |")
    rows.append(
        "| **N (obs)** | "
        f"{int(res_m1.nobs)} | {int(res_m2.nobs)} | {int(res_m3.nobs)} | {int(res_m4.nobs)} |"
    )
    rows.append(
        "| **R² (within / pseudo)** | "
        f"{res_m1.rsquared_within:.3f} | {res_m2.rsquared_within:.3f} | "
        f"{res_m3.rsquared:.3f} | {1 - res_m4.deviance / res_m4.null_deviance:.3f} |"
    )

    md = [
        "# Panel Regression Results — Research Model v1",
        "",
        f"_Generated: {pd.Timestamp.now().isoformat(timespec='seconds')}_",
        "",
        "## Research model",
        "",
        "DV = `crim_activity_index` (fraction of 1D-4 cells = Yes, bounded [0, 1]).",
        "",
        "Four specifications:",
        "- **M1** — OLS with two-way (CoC + year) fixed effects; direct IV effect only, no mediators.",
        "- **M2** — Adds the PLE-engagement mediator set (log of decisionmaking PLE counts + two binary breadth indicators).",
        "- **M3** — FY2024 cross-section (no CoC FE, HC3 SEs); exploits richer FY2024 variables.",
        "- **M4** — Pooled fractional logit with CoC-clustered SEs; handles censoring at 0 and 1 in the DV.",
        "",
        "Significance: `*** p<0.01, ** p<0.05, * p<0.10` · cluster-robust SEs at the CoC level.",
        "",
        "## Coefficient table",
        "",
        *header, *rows,
        "",
    ]

    def beta(table, key):
        v = table.get(key, (None, None, None))[0]
        return f"{v:.3f}" if v is not None and not pd.isna(v) else "(absorbed by CoC FE)"

    # Interpretation
    md += [
        "## Interpretation highlights",
        "",
        "### The Nonprofit-led effect",
        f"- M1 (TWFE, direct): β = {beta(c1, 'nonprofit_led')}",
        f"- M2 (TWFE, with mediators): β = {beta(c2, 'nonprofit_led')}",
        f"- M3 (FY24 cross-section): β = {beta(c3, 'nonprofit_led')}",
        f"- M4 (pooled frac. logit): β = {beta(c4, 'nonprofit_led')}",
        "",
        "With CoC fixed effects absorbing time-invariant CoC characteristics (M1, M2, M4),",
        "the nonprofit-led dummy is identified only off CoCs that change leadership during the",
        "panel window — of which there are very few. The **FY2024 cross-section (M3)** is the",
        "cleaner identification for the Nonprofit-vs-government question.",
        "",
        "### PLE engagement (mediator path M → Y)",
        f"- log(PLE decisionmaking count): M2={beta(c2,'log_1d_10a_1_years')}, M3={beta(c3,'log_1d_10a_1_years')}",
        f"- PLE voted (binary): M2={beta(c2,'1b_1_6_voted_bin')}",
        f"- PLE in CES (binary): M2={beta(c2,'1b_1_6_ces_bin')}",
        "",
        "### Controls",
        f"- Housing First adoption: M2={beta(c2,'hf_pct')}",
        f"- HMIS ES coverage: M2={beta(c2,'hmis_es_cov')}",
        f"- log(total beds): M2={beta(c2,'log_total_beds')}",
        "",
        "## Caveats",
        "",
        "1. **IV coverage.** Rule-based coding of `1a_2` classified ~217 of 321 CoCs",
        "   (~68%). Unclassified CoCs drop from IV models; manual refinement of the",
        "   classifier would expand the sample.",
        "2. **DV instrument change.** M1–M3 use the harmonized `crim_activity_index`; M4",
        "   uses it with fractional-logit corrections for 0/1 censoring. See",
        "   `dv_harmonization_results.md`.",
        "3. **Absorbed variation.** TWFE absorbs ~all Nonprofit_led variation for",
        "   CoCs stable across years. Interpret M3 (cross-section) alongside M1/M2.",
    ]

    OUT_MD.write_text("\n".join(md))
    print(f"wrote {OUT_MD}")

    # Also save a flat CSV with every coef
    import csv as _csv
    with OUT_CSV.open("w", newline="") as f:
        w = _csv.writer(f)
        w.writerow(["model", "variable", "coef", "se", "pvalue"])
        for label, coefs in [("M1", c1), ("M2", c2), ("M3", c3), ("M4", c4)]:
            for v, (p, s, pv) in coefs.items():
                w.writerow([label, v, p, s, pv])
    print(f"wrote {OUT_CSV}")

    # Print the main table to console
    print()
    print("=" * 80)
    for line in header + rows:
        print(line.replace("<br>", " ").replace("<span class='hint'>", "").replace("</span>", ""))


if __name__ == "__main__":
    main()
