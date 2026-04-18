"""Multilevel DiD: state-level + county-within-state political environment.

Addresses collinearity between state-level and county-level political
measures by decomposing county Biden share into between-state and
within-state components (Mundlak-style at the multilevel structure).

  state_mean_biden   = mean Biden share of counties in the state
  biden_within_state = county_biden - state_mean_biden

This makes `blue_state` (state-level) and `biden_within_state` (pure
within-state county variation) statistically orthogonal, so both can
enter the same regression without collinearity washing out the
coefficients.

Model:
  crim_activity_index_it =
      β1 · nonprofit_led_i + β2 · blue_state_i + β3 · biden_within_i
    + β4 · post_t
    + β5 · nonprofit × post        ← nonprofit DiD
    + β6 · blue_state × post       ← state-level political DiD
    + β7 · biden_within × post     ← within-state county DiD
    + Mundlak-adjusted controls + ε_it

Estimator: Papke-Wooldridge fractional logit, state-level cluster-
robust SE. Run on both unbalanced (651 obs) and balanced (375 obs)
panels.

Outputs
-------
multilevel_results.md
multilevel_coefs.csv
multilevel_quadrant_means.csv  — for 2x2 grouping visualization
"""
from __future__ import annotations

import warnings
import numpy as np
import pandas as pd
import statsmodels.api as sm

warnings.filterwarnings("ignore")

from pipeline_utils import PIPELINE_DIR

ANALYSIS_XLSX = PIPELINE_DIR / "coc_analysis_ready.xlsx"
OUT_MD = PIPELINE_DIR / "multilevel_results.md"
OUT_CSV = PIPELINE_DIR / "multilevel_coefs.csv"
OUT_QUAD = PIPELINE_DIR / "multilevel_quadrant_means.csv"

N_BOOT = 999

BLUE_STATES = {
    "AZ","CA","CO","CT","DE","DC","GA","HI","IL","ME","MD","MA","MI","MN",
    "NV","NH","NJ","NM","NY","OR","PA","RI","VT","VA","WA","WI",
}
RED_STATES = {
    "AL","AK","AR","FL","ID","IN","IA","KS","KY","LA","MS","MO","MT","NE",
    "NC","ND","OH","OK","SC","SD","TN","TX","UT","WV","WY",
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
    df["state"] = df["coc_id"].str.split("-").str[0].str.upper()
    df["blue_state"] = df["state"].apply(
        lambda s: 1.0 if s in BLUE_STATES else (0.0 if s in RED_STATES else np.nan)
    )

    # Mundlak decomposition of county Biden at state level
    df["state_mean_biden"] = df.groupby("state")["biden_share"].transform("mean")
    df["biden_within_state"] = df["biden_share"] - df["state_mean_biden"]

    # Interactions
    df["did_np"] = df["nonprofit_led"] * df["post"]
    df["did_blue"] = df["blue_state"] * df["post"]
    df["did_within"] = df["biden_within_state"] * df["post"]

    # DV
    df["crim_activity_index"] = pd.to_numeric(df["crim_activity_index"], errors="coerce")

    # Controls
    df["hf_pct"] = pd.to_numeric(df["1d_2_3"], errors="coerce")
    df.loc[df["hf_pct"] > 1.5, "hf_pct"] = df["hf_pct"] / 100
    df["hmis_cov"] = pd.to_numeric(df["2a_5_1_coverage"], errors="coerce")
    df.loc[df["hmis_cov"] > 1.5, "hmis_cov"] = df["hmis_cov"] / 100
    df["hmis_cov"] = df["hmis_cov"].clip(0, 1)
    df["ple_ces_bin"] = (df["1b_1_6_ces"].astype(str).str.strip().str.lower() == "yes").astype(float)
    bed_cols = [c for c in (f"2a_5_{i}_non_vsp" for i in range(1, 7)) if c in df.columns]
    bed_sum = pd.DataFrame({c: pd.to_numeric(df[c], errors="coerce") for c in bed_cols}).sum(axis=1, min_count=1)
    df["log_beds"] = np.log1p(bed_sum.clip(upper=bed_sum.quantile(0.99)))
    for c in ("hf_pct", "hmis_cov", "log_beds", "ple_ces_bin"):
        df[c + "_bar"] = df.groupby("coc_id")[c].transform("mean")
    return df


def frac_logit(df, rhs, dv="crim_activity_index", cluster="state"):
    sub = df.dropna(subset=[dv] + list(rhs) + [cluster]).copy()
    y = sub[dv].astype(float).clip(0, 1)
    X = sub[list(rhs)].astype(float)
    X = sm.add_constant(X, has_constant="add")
    mod = sm.GLM(y, X, family=sm.families.Binomial())
    res = mod.fit(cov_type="cluster", cov_kwds={"groups": sub[cluster].values})
    return res, len(sub), sub


def wild_cluster_bootstrap(df, rhs, target, dv="crim_activity_index",
                           cluster="state", n=N_BOOT, seed=42):
    sub = df.dropna(subset=[dv] + list(rhs) + [cluster]).copy()
    y = sub[dv].astype(float).values
    X = sub[list(rhs)].astype(float)
    X = sm.add_constant(X, has_constant="add").values
    clusters = sub[cluster].values
    res_obs = sm.OLS(y, X).fit(
        cov_type="cluster", cov_kwds={"groups": clusters}
    )
    tidx = list(sub[list(rhs)].columns).index(target) + 1
    t_obs = res_obs.params[tidx] / res_obs.bse[tidx]
    Xr = np.delete(X, tidx, axis=1)
    res_r = sm.OLS(y, Xr).fit()
    resid = y - Xr @ res_r.params
    yhat = Xr @ res_r.params
    rng = np.random.default_rng(seed)
    uc = np.unique(clusters)
    ext = 0
    for _ in range(n):
        w = rng.choice([-1.0, 1.0], size=len(uc))
        wm = dict(zip(uc, w))
        wf = np.array([wm[c] for c in clusters])
        yb = yhat + resid * wf
        try:
            rb = sm.OLS(yb, X).fit(cov_type="cluster", cov_kwds={"groups": clusters})
            tb = rb.params[tidx] / rb.bse[tidx]
        except Exception:
            continue
        if abs(tb) >= abs(t_obs):
            ext += 1
    return (ext + 1) / (n + 1), t_obs


def star(p):
    if p is None or pd.isna(p): return ""
    if p < 0.01: return "***"
    if p < 0.05: return "**"
    if p < 0.10: return "*"
    return ""


def fmt(res, v):
    if v not in res.params.index or pd.isna(res.params[v]):
        return "—"
    return f"{res.params[v]:+.3f}{star(res.pvalues[v] if v in res.pvalues else None)}<br><span class='hint'>({res.bse[v]:.3f})</span>"


def quadrant_means(df):
    """Compute activity index means by 4 quadrants × year."""
    sub = df.dropna(subset=["blue_state", "biden_share", "crim_activity_index"]).copy()
    sub["blue_county_cat"] = (sub["biden_share"] > 0.5).astype(int)
    sub["quadrant"] = sub.apply(
        lambda r: ("Blue state × Blue county" if r["blue_state"] == 1 and r["blue_county_cat"] == 1
                   else "Blue state × Red county" if r["blue_state"] == 1 and r["blue_county_cat"] == 0
                   else "Red state × Blue county" if r["blue_state"] == 0 and r["blue_county_cat"] == 1
                   else "Red state × Red county"),
        axis=1,
    )
    out = (sub.groupby(["quadrant", "year"])["crim_activity_index"]
           .agg(["count", "mean", "std"])
           .reset_index())
    out["se"] = out["std"] / np.sqrt(out["count"])
    return out


def main():
    print("=" * 76)
    print("MULTILEVEL DIFFERENCE-IN-DIFFERENCES")
    print("=" * 76)

    rhs_base = [
        "nonprofit_led", "blue_state", "biden_within_state", "post",
        "did_np", "did_blue", "did_within",
        "hf_pct", "hmis_cov", "log_beds", "ple_ces_bin",
        "hf_pct_bar", "hmis_cov_bar", "log_beds_bar", "ple_ces_bin_bar",
    ]

    # Panels
    results = {}
    for balanced in [False, True]:
        df = load(balanced=balanced)
        n_states = df.dropna(subset=["blue_state"])["state"].nunique()
        tag = "balanced" if balanced else "unbalanced"
        print(f"\n[{tag}] N CoCs = {df.coc_id.nunique()}, N states = {n_states}")

        # Main spec
        res, n, sub = frac_logit(df, rhs_base, cluster="state")
        results[tag] = (res, n, df)

        # Bootstrap each of the three DiD terms
        print(f"  Running wild-cluster bootstrap (state-level, N={N_BOOT})...")
        p_np, _ = wild_cluster_bootstrap(df, rhs_base, "did_np")
        p_blue, _ = wild_cluster_bootstrap(df, rhs_base, "did_blue")
        p_within, _ = wild_cluster_bootstrap(df, rhs_base, "did_within")
        results[tag + "_boot"] = {"did_np": p_np, "did_blue": p_blue, "did_within": p_within}
        print(f"    bootstrap p: did_np={p_np:.3f}, did_blue={p_blue:.3f}, did_within={p_within:.3f}")

    # Quadrant means — using unbalanced panel for maximal N
    quad = quadrant_means(load(balanced=False))
    quad.to_csv(OUT_QUAD, index=False)
    print("\nQuadrant means by year (unbalanced):")
    print(quad.pivot(index="year", columns="quadrant", values="mean").round(3))

    # Build MD report
    label_map = {
        "nonprofit_led": "Nonprofit-led (IV₁)",
        "blue_state": "Blue state (IV₂, state-level)",
        "biden_within_state": "Biden-within-state (IV₃, county − state mean)",
        "post": "Post-Grants Pass",
        "did_np": "Nonprofit × Post",
        "did_blue": "<strong>Blue state × Post (state DiD)</strong>",
        "did_within": "<strong>Biden-within × Post (within-state county DiD)</strong>",
        "hf_pct": "Housing First adoption",
        "hmis_cov": "HMIS ES coverage",
        "log_beds": "log(total beds + 1)",
        "ple_ces_bin": "PLE in CES",
        "hf_pct_bar": "[Mundlak] HF mean",
        "hmis_cov_bar": "[Mundlak] HMIS mean",
        "log_beds_bar": "[Mundlak] log beds mean",
        "ple_ces_bin_bar": "[Mundlak] PLE mean",
        "const": "(Intercept)",
    }
    all_vars = list(label_map.keys())

    r_u, n_u, _ = results["unbalanced"]
    r_b, n_b, _ = results["balanced"]
    boot_u = results["unbalanced_boot"]
    boot_b = results["balanced_boot"]

    header = "| Variable | Unbalanced (n=" + str(n_u) + ") | Balanced (n=" + str(n_b) + ") |"
    sep = "|---|---|---|"
    rows = []
    for v in all_vars:
        rows.append(f"| {label_map[v]} | {fmt(r_u, v)} | {fmt(r_b, v)} |")

    md = [
        "# Multilevel DiD — State + County (within-state) Political Environment",
        "",
        f"_Generated: {pd.Timestamp.now().isoformat(timespec='seconds')}_",
        "",
        "## Why multilevel",
        "",
        "`blue_state` (state-level 2020 winner) and `biden_share` (county-level",
        "continuous) are highly correlated — putting both in the same model",
        "directly produces collinearity. We apply a Mundlak-style decomposition",
        "at the multilevel structure to separate them:",
        "",
        "```",
        "state_mean_biden   = average Biden share of counties in state",
        "biden_within_state = county_biden_share − state_mean_biden",
        "```",
        "",
        "After this decomposition:",
        "- `blue_state × Post` captures the **state-level** DiD",
        "  (political environment of the state you're in).",
        "- `biden_within_state × Post` captures the **within-state county** DiD",
        "  (how much bluer your county is than the rest of your state).",
        "",
        "These two are statistically orthogonal, so we can estimate both",
        "simultaneously. We also keep `nonprofit_led × Post` for completeness.",
        "",
        "## Estimator",
        "",
        "- Fractional logit (Papke-Wooldridge) for bounded [0, 1] DV",
        "- **State-level cluster-robust SE** (higher level in hierarchy)",
        "- Wild-cluster bootstrap p-values (Rademacher, state-clustered, 999 reps)",
        "- Mundlak-adjusted time-varying controls",
        "- Estimated on both unbalanced (651 obs) and balanced (375 obs) panels",
        "",
        "## Coefficient table",
        "",
        header, sep, *rows,
        "",
        "Cluster-robust SE at the state level in parentheses · `*** p<0.01, ** p<0.05, * p<0.10`.",
        "",
        "## Wild-cluster bootstrap p-values (state-clustered, 999 reps)",
        "",
        "| DiD term | Unbalanced | Balanced |",
        "|---|---|---|",
        f"| Nonprofit × Post | {boot_u['did_np']:.3f} | {boot_b['did_np']:.3f} |",
        f"| **Blue state × Post** | **{boot_u['did_blue']:.3f}** | **{boot_b['did_blue']:.3f}** |",
        f"| **Biden-within × Post** | **{boot_u['did_within']:.3f}** | **{boot_b['did_within']:.3f}** |",
        "",
        "## 2×2 Quadrant means (unbalanced sample)",
        "",
        "| Year | Red state × Red county | Red state × Blue county | Blue state × Red county | Blue state × Blue county |",
        "|---|---|---|---|---|",
    ]
    pivot = quad.pivot(index="year", columns="quadrant", values="mean")
    # Order columns properly
    cols = ["Red state × Red county", "Red state × Blue county",
            "Blue state × Red county", "Blue state × Blue county"]
    for yr in sorted(pivot.index):
        vals = []
        for c in cols:
            if c in pivot.columns:
                v = pivot.loc[yr, c]
                vals.append(f"{v:.3f}" if not pd.isna(v) else "—")
            else:
                vals.append("—")
        md.append(f"| FY{yr} | " + " | ".join(vals) + " |")
    md.append("")

    # Interpretation
    def beta_p(res, v, boots):
        if v not in res.params.index or pd.isna(res.params[v]):
            return "(n/a)"
        b = res.params[v]
        s = res.bse[v]
        p_c = res.pvalues[v] if v in res.pvalues else None
        p_b = boots.get(v, None)
        star_s = star(p_c)
        return f"β = {b:+.3f}{star_s} (cluster p = {p_c:.3f}, bootstrap p = {p_b:.3f})"

    md += [
        "## Key findings",
        "",
        "### Both political dimensions, **same model**, unbalanced:",
        f"- Nonprofit × Post: {beta_p(r_u, 'did_np', boot_u)}",
        f"- Blue state × Post: {beta_p(r_u, 'did_blue', boot_u)}",
        f"- Biden-within × Post: {beta_p(r_u, 'did_within', boot_u)}",
        "",
        "### Balanced panel (clean DiD contrast):",
        f"- Nonprofit × Post: {beta_p(r_b, 'did_np', boot_b)}",
        f"- Blue state × Post: {beta_p(r_b, 'did_blue', boot_b)}",
        f"- Biden-within × Post: {beta_p(r_b, 'did_within', boot_b)}",
        "",
    ]

    # Auto-generate narrative about which dimension dominates
    md.append("## Which level matters — automated diagnosis")
    md.append("")
    for tag, res, boots in [("Unbalanced", r_u, boot_u), ("Balanced", r_b, boot_b)]:
        md.append(f"### {tag}")
        bs = res.params.get("did_blue")
        bp = boots["did_blue"]
        ws = res.params.get("did_within")
        wp = boots["did_within"]
        if bs is None or ws is None:
            continue
        blue_sig = bp < 0.10
        within_sig = wp < 0.10
        if blue_sig and within_sig:
            md.append(f"- **Both levels matter** (blue state bootstrap p={bp:.3f}, "
                      f"within-state bootstrap p={wp:.3f}). Independent effects from "
                      "state politics AND county-level deviation.")
        elif blue_sig and not within_sig:
            md.append(f"- **State level dominates** (blue state bootstrap p={bp:.3f}, "
                      f"within-state n.s. at p={wp:.3f}). State-level political "
                      "environment is the channel; county-level adds little.")
        elif within_sig and not blue_sig:
            md.append(f"- **County level dominates** (within-state bootstrap p={wp:.3f}, "
                      f"blue state n.s. at p={bp:.3f}). Hyperlocal partisan variation "
                      "matters more than state-level.")
        else:
            md.append(f"- **Neither significant** after joint estimation (blue state "
                      f"bootstrap p={bp:.3f}, within-state p={wp:.3f}). Either the "
                      "political-environment effect is absorbed by the joint specification, "
                      "or the sample is underpowered for the multilevel decomposition.")
        md.append("")

    md += [
        "## Quadrant trajectory reading",
        "",
        "The 2×2 panel mean table above shows FY-by-FY activity index for each",
        "state × county political combination. Compare FY2023 → FY2024 differences:",
        "",
        "- If Blue state × Blue county jumps most → both state AND county matter",
        "- If Blue state × Red county ≈ Blue state × Blue county → state dominates",
        "- If Red state × Blue county ≈ Blue state × Blue county → county dominates",
        "",
    ]

    OUT_MD.write_text("\n".join(md))
    print(f"\nwrote {OUT_MD}")

    # CSV
    import csv
    with OUT_CSV.open("w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["panel", "variable", "coef", "se", "pvalue", "bootstrap_p", "n"])
        for tag, (res, n, _) in ((k, v) for k, v in results.items() if not k.endswith("_boot")):
            boots = results.get(tag + "_boot", {})
            for v in res.params.index:
                try:
                    w.writerow([
                        tag, v,
                        round(float(res.params[v]), 5),
                        round(float(res.bse[v]), 5),
                        round(float(res.pvalues[v]), 5) if v in res.pvalues else "",
                        round(boots.get(v, float("nan")), 5) if v in boots else "",
                        n,
                    ])
                except (ValueError, TypeError):
                    continue
    print(f"wrote {OUT_CSV}")

    # Console summary
    print("\n" + "=" * 76)
    print("COEFFICIENT TABLE (both panels, joint multilevel)")
    print("=" * 76)
    for line in [header, sep] + rows:
        print(line.replace("<br>", " ").replace("<span class='hint'>", "")
              .replace("</span>", "").replace("**", ""))


if __name__ == "__main__":
    main()
