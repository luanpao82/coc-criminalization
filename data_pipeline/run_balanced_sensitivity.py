"""Sensitivity analysis: balanced 3-year panel vs. unbalanced panel.

All main DiD analyses to date used the unbalanced panel (651 CoC-years).
But 124 of 325 CoCs appear only once — they contribute to main effects but
not to the DiD contrast (no within-CoC pre-vs-post variation). This script
re-runs the key specifications on the **balanced 3-year panel** (125 CoCs ×
3 years = 375 rows, same CoCs each year) and compares the estimates.

Specifications (each in both unbalanced and balanced):
  N1  Nonprofit-led × Post (DiD)
  B1  Blue-state × Post (DiD)
  J2  Joint Nonprofit + County-Biden × Post

Outputs
-------
balanced_sensitivity_results.md
balanced_sensitivity_coefs.csv
"""
from __future__ import annotations

import warnings
import numpy as np
import pandas as pd
import statsmodels.api as sm

warnings.filterwarnings("ignore")

from pipeline_utils import PIPELINE_DIR

ANALYSIS_XLSX = PIPELINE_DIR / "coc_analysis_ready.xlsx"
OUT_MD = PIPELINE_DIR / "balanced_sensitivity_results.md"
OUT_CSV = PIPELINE_DIR / "balanced_sensitivity_coefs.csv"

BLUE_STATES = {
    "AZ","CA","CO","CT","DE","DC","GA","HI","IL","ME","MD","MA","MI","MN",
    "NV","NH","NJ","NM","NY","OR","PA","RI","VT","VA","WA","WI",
}


def load(balanced: bool):
    sheet = "balanced_panel" if balanced else "unbalanced"
    df = pd.read_excel(ANALYSIS_XLSX, sheet_name=sheet)
    iv_l = pd.read_excel(ANALYSIS_XLSX, sheet_name="iv_leadership")
    iv_c = pd.read_excel(ANALYSIS_XLSX, sheet_name="iv_county")
    df = df.merge(iv_l[["coc_id", "nonprofit_led"]], on="coc_id", how="left")
    df = df.merge(iv_c[["coc_id", "biden_share"]], on="coc_id", how="left")
    df["year"] = df["year"].astype(int)
    df["post"] = (df["year"] == 2024).astype(int)
    df["nonprofit_led"] = pd.to_numeric(df["nonprofit_led"], errors="coerce")
    df["biden_share"] = pd.to_numeric(df["biden_share"], errors="coerce")
    df["biden_c"] = df["biden_share"] - 0.5
    df["state"] = df["coc_id"].str.split("-").str[0].str.upper()
    df["blue_state"] = df["state"].apply(lambda s: 1.0 if s in BLUE_STATES else 0.0)
    df.loc[~df["state"].isin(BLUE_STATES | {"AL","AK","AR","FL","ID","IN","IA",
        "KS","KY","LA","MS","MO","MT","NE","NC","ND","OH","OK","SC","SD","TN",
        "TX","UT","WV","WY"}), "blue_state"] = np.nan

    df["crim_activity_index"] = pd.to_numeric(df["crim_activity_index"], errors="coerce")
    df["did_np"] = df["nonprofit_led"] * df["post"]
    df["did_blue"] = df["blue_state"] * df["post"]
    df["did_biden"] = df["biden_c"] * df["post"]

    # Controls
    df["ple_ces_bin"] = (df["1b_1_6_ces"].astype(str).str.strip().str.lower() == "yes").astype(float)
    df["hf_pct"] = pd.to_numeric(df["1d_2_3"], errors="coerce")
    df.loc[df["hf_pct"] > 1.5, "hf_pct"] = df["hf_pct"] / 100
    df["hmis_cov"] = pd.to_numeric(df["2a_5_1_coverage"], errors="coerce")
    df.loc[df["hmis_cov"] > 1.5, "hmis_cov"] = df["hmis_cov"] / 100
    df["hmis_cov"] = df["hmis_cov"].clip(0, 1)
    bed_cols = [c for c in (f"2a_5_{i}_non_vsp" for i in range(1, 7)) if c in df.columns]
    bed_sum = pd.DataFrame({c: pd.to_numeric(df[c], errors="coerce") for c in bed_cols}).sum(axis=1, min_count=1)
    df["log_beds"] = np.log1p(bed_sum.clip(upper=bed_sum.quantile(0.99)))
    # Mundlak
    for c in ("ple_ces_bin", "hf_pct", "hmis_cov", "log_beds"):
        df[c + "_bar"] = df.groupby("coc_id")[c].transform("mean")
    return df


def frac_logit(df, rhs, dv="crim_activity_index"):
    sub = df.dropna(subset=[dv] + list(rhs) + ["coc_id"]).copy()
    y = sub[dv].astype(float).clip(0, 1)
    X = sub[list(rhs)].astype(float)
    X = sm.add_constant(X, has_constant="add")
    mod = sm.GLM(y, X, family=sm.families.Binomial())
    return mod.fit(cov_type="cluster", cov_kwds={"groups": sub["coc_id"].values}), len(sub)


def star(p):
    if p is None or pd.isna(p): return ""
    if p < 0.01: return "***"
    if p < 0.05: return "**"
    if p < 0.10: return "*"
    return ""


def cell(res, v):
    if v not in res.params.index or pd.isna(res.params[v]):
        return "—"
    b = res.params[v]; s = res.bse[v]
    p = res.pvalues[v] if v in res.pvalues else None
    return f"{b:+.3f}{star(p)}<br><span class='hint'>({s:.3f})</span>"


def main():
    controls = ["hf_pct", "hmis_cov", "log_beds", "ple_ces_bin"]
    mund = [c + "_bar" for c in controls]

    df_u = load(balanced=False)
    df_b = load(balanced=True)
    print(f"Unbalanced: {len(df_u)} rows, {df_u.coc_id.nunique()} CoCs")
    print(f"Balanced:   {len(df_b)} rows, {df_b.coc_id.nunique()} CoCs")

    # Specs
    specs = {
        "N1 (Nonprofit × Post)": ["nonprofit_led", "post", "did_np"] + controls + mund,
        "B1 (Blue-state × Post)": ["blue_state", "post", "did_blue"] + controls + mund,
        "J2 (Joint NP + Biden × Post)": ["nonprofit_led", "biden_c", "post",
                                          "did_np", "did_biden"] + controls + mund,
    }

    target_vars = {
        "N1 (Nonprofit × Post)": "did_np",
        "B1 (Blue-state × Post)": "did_blue",
        "J2 (Joint NP + Biden × Post)": "did_biden",
    }

    all_results = {}
    for name, rhs in specs.items():
        r_u, n_u = frac_logit(df_u, rhs)
        r_b, n_b = frac_logit(df_b, rhs)
        all_results[name] = {"unbal": (r_u, n_u), "bal": (r_b, n_b)}

    # Build table
    md = [
        "# Balanced vs Unbalanced Panel — Sensitivity",
        "",
        f"_Generated: {pd.Timestamp.now().isoformat(timespec='seconds')}_",
        "",
        "## Why compare",
        "",
        f"The unbalanced panel has **{len(df_u)}** CoC-year rows across",
        f"**{df_u.coc_id.nunique()}** CoCs, but only **{(df_u.groupby('coc_id')['year'].nunique() == 3).sum()}**",
        "CoCs appear in all three fiscal years. The remaining CoCs contribute",
        "to main effects but add nothing to the within-CoC pre-vs-post",
        "contrast that drives DiD identification. This note re-estimates the",
        "main specifications on the **balanced 3-year panel** (same CoCs each",
        "year) as a sensitivity check.",
        "",
        "## Composition differences",
        "",
        "| | Unbalanced | Balanced |",
        "|---|---|---|",
        f"| CoCs | {df_u.coc_id.nunique()} | {df_b.coc_id.nunique()} |",
        f"| Observations | {len(df_u)} | {len(df_b)} |",
        f"| CoCs in all 3 years | {(df_u.groupby('coc_id')['year'].nunique() == 3).sum()} | "
        f"{df_b.coc_id.nunique()} (by construction) |",
        "",
        "## Side-by-side key DiD coefficients",
        "",
        "| Specification | Panel | Focal DiD coef | Cluster p | N |",
        "|---|---|---|---|---|",
    ]

    def beta_line(label, tag, res, n, v):
        b = res.params.get(v)
        s = res.bse.get(v)
        p = res.pvalues.get(v) if v in res.pvalues else None
        if b is None or pd.isna(b):
            return f"| {label} | {tag} | — | — | {n} |"
        return f"| {label} | {tag} | {b:+.3f}{star(p)} (SE {s:.3f}) | {p:.3f} | {n} |"

    for name, rhs in specs.items():
        v = target_vars[name]
        r_u, n_u = all_results[name]["unbal"]
        r_b, n_b = all_results[name]["bal"]
        md.append(beta_line(name, "Unbalanced", r_u, n_u, v))
        md.append(beta_line(name, "Balanced  ", r_b, n_b, v))

    md.append("")

    # Full table
    md += [
        "## Full coefficient table",
        "",
        "| Variable | N1 unbal | N1 bal | B1 unbal | B1 bal | J2 unbal | J2 bal |",
        "|---|---|---|---|---|---|---|",
    ]
    all_vars = ["nonprofit_led", "blue_state", "biden_c", "post",
                "did_np", "did_blue", "did_biden",
                "hf_pct", "hmis_cov", "log_beds", "ple_ces_bin", "const"]
    labels = {
        "nonprofit_led": "Nonprofit-led (IV)",
        "blue_state": "Blue state (IV)",
        "biden_c": "County Biden share (centered)",
        "post": "Post-Grants Pass",
        "did_np": "Nonprofit × Post",
        "did_blue": "Blue × Post / Biden × Post",
        "did_biden": "(continuous Biden × Post)",
        "hf_pct": "Housing First adoption",
        "hmis_cov": "HMIS ES coverage",
        "log_beds": "log(total beds + 1)",
        "ple_ces_bin": "PLE in CES",
        "const": "(Intercept)",
    }
    for v in all_vars:
        row = [labels.get(v, v)]
        for name in specs.keys():
            r_u, _ = all_results[name]["unbal"]
            r_b, _ = all_results[name]["bal"]
            row.append(cell(r_u, v))
            row.append(cell(r_b, v))
        md.append("| " + " | ".join(row) + " |")

    md.append("")
    md.append("Cluster-robust SEs at the CoC level in parentheses · `*** p<0.01, ** p<0.05, * p<0.10`.")
    md.append("")

    # Compare each DiD side-by-side verbally
    md.append("## Interpretation")
    md.append("")
    for name, rhs in specs.items():
        v = target_vars[name]
        r_u = all_results[name]["unbal"][0]
        r_b = all_results[name]["bal"][0]
        b_u = r_u.params.get(v)
        b_b = r_b.params.get(v)
        p_u = r_u.pvalues.get(v) if v in r_u.pvalues else None
        p_b = r_b.pvalues.get(v) if v in r_b.pvalues else None
        if b_u is None or b_b is None:
            continue
        diff = b_b - b_u
        md.append(f"### {name}")
        md.append(f"- **Unbalanced:** β = {b_u:+.3f}{star(p_u)} (p = {p_u:.3f})")
        md.append(f"- **Balanced:** β = {b_b:+.3f}{star(p_b)} (p = {p_b:.3f})")
        md.append(f"- Difference (bal − unbal): {diff:+.3f}")
        if (p_u is not None and p_b is not None):
            if (p_u < 0.10) != (p_b < 0.10):
                md.append("- ⚠ **Significance flips between panels** — interpret with caution.")
            elif p_u < 0.10 and p_b < 0.10:
                md.append("- ✅ Significant in both — robust to panel composition.")
            else:
                md.append("- Null in both — robust null.")
        md.append("")

    md += [
        "## Decision: which panel to use in the paper?",
        "",
        "### Arguments for unbalanced (current primary)",
        "- More observations → more statistical power (651 vs 375 rows).",
        "- FY2022 has 166 CoCs but FY2024 has 292; using all observations is",
        "  standard practice when missingness is not strongly selection-biased.",
        "- Frac-logit with CoC clusters handles unbalanced panels cleanly.",
        "- CoC fixed effects (implicit via Mundlak) identify only off multi-",
        "  year CoCs anyway, so single-year CoCs contribute to main effects.",
        "",
        "### Arguments for balanced (robustness)",
        "- **Same CoCs in pre and post** → cleanest DiD contrast.",
        "- Rules out **compositional changes** as an alternative explanation",
        "  (e.g., the FY2024 jump being driven by newly-added CoCs rather",
        "  than existing CoCs responding).",
        "- Parallel-trends assumption easier to defend when the comparison",
        "  is literally the same CoCs across years.",
        "- Pre-registered 'within-CoC' interpretation is more natural.",
        "",
        "### Recommendation",
        "",
        "**Report the unbalanced panel as primary** (more power; standard",
        "DiD econometric practice) and **the balanced panel as a",
        "robustness check** in the appendix. The balanced sensitivity above",
        "lets reviewers verify that sample composition is not driving the",
        "DiD estimates.",
    ]

    OUT_MD.write_text("\n".join(md))
    print(f"\nwrote {OUT_MD}")

    # CSV
    import csv
    with OUT_CSV.open("w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["spec", "panel", "variable", "coef", "se", "pvalue", "n"])
        for name, _ in specs.items():
            for tag, (res, n) in (("unbalanced", all_results[name]["unbal"]),
                                  ("balanced", all_results[name]["bal"])):
                for v in res.params.index:
                    try:
                        w.writerow([name, tag, v,
                                    round(float(res.params[v]), 5),
                                    round(float(res.bse[v]), 5),
                                    round(float(res.pvalues[v]), 5) if v in res.pvalues else "",
                                    n])
                    except (ValueError, TypeError):
                        continue
    print(f"wrote {OUT_CSV}")

    # Console summary
    print("\n=== Key DiD coefficients: unbalanced vs balanced ===")
    for name in specs.keys():
        v = target_vars[name]
        r_u = all_results[name]["unbal"][0]
        r_b = all_results[name]["bal"][0]
        print(f"\n{name} (target: {v})")
        print(f"  Unbalanced: β = {r_u.params.get(v):+.3f} (SE {r_u.bse.get(v):.3f}, p = {r_u.pvalues.get(v):.3f})")
        print(f"  Balanced:   β = {r_b.params.get(v):+.3f} (SE {r_b.bse.get(v):.3f}, p = {r_b.pvalues.get(v):.3f})")


if __name__ == "__main__":
    main()
