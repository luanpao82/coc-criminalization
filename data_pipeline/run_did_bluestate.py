"""Difference-in-Differences with BLUE-STATE vs RED-STATE treatment.

Alternative to the nonprofit-vs-government DiD — uses the political
environment of each CoC's state as the treatment indicator. Theoretical
motivation: blue-state CoCs may face stronger local pressure to resist
criminalization after the Grants Pass ruling opened the door to
anti-camping enforcement.

Classification: state voted for Biden in the 2020 presidential election →
blue (treatment = 1); Trump → red (treatment = 0). Territories (PR/VI/GU)
are excluded because they have no Electoral College vote. DC is classified
as blue.

DV set:
  DV1: crim_activity_index (full 6-cell composite, instrument-affected)
  DV2: engagement-only sub-measure (3 col-1 cells, wording-stable)
  DV3: implemented_anticrim_practice (binary)

Specs:
  B1  OLS-FE + CoC FE with blue × post interaction
  B2  OLS-FE + CoC + Year FE
  B3  Pooled fractional logit with Mundlak means (primary)
  B4  Event study (pre-trend placebo on FY2023)
  B5  B3 but on DV2 (wording-stable)
  B6  B3 but on DV3 (binary)

Plus: wild-cluster bootstrap p-value for the primary DiD coefficient.

Outputs
-------
  did_bluestate_results.md
  did_bluestate_coefs.csv
  did_bluestate_trends.csv
"""
from __future__ import annotations

import warnings
import numpy as np
import pandas as pd
import statsmodels.api as sm
from linearmodels.panel import PanelOLS

warnings.filterwarnings("ignore")

from pipeline_utils import PIPELINE_DIR

ANALYSIS_XLSX = PIPELINE_DIR / "coc_analysis_ready.xlsx"
OUT_MD = PIPELINE_DIR / "did_bluestate_results.md"
OUT_CSV = PIPELINE_DIR / "did_bluestate_coefs.csv"
OUT_TRENDS = PIPELINE_DIR / "did_bluestate_trends.csv"

# 2020 presidential election — Biden winning states
BLUE_STATES = {
    "AZ", "CA", "CO", "CT", "DE", "DC", "GA", "HI", "IL", "ME", "MD",
    "MA", "MI", "MN", "NV", "NH", "NJ", "NM", "NY", "OR", "PA", "RI",
    "VT", "VA", "WA", "WI",
}
RED_STATES = {
    "AL", "AK", "AR", "FL", "ID", "IN", "IA", "KS", "KY", "LA", "MS",
    "MO", "MT", "NE", "NC", "ND", "OH", "OK", "SC", "SD", "TN", "TX",
    "UT", "WV", "WY",
}
# Territories excluded: PR, VI, GU


N_BOOT = 999


def classify_state(coc_id: str) -> float:
    st = coc_id.split("-")[0].upper()
    if st in BLUE_STATES:
        return 1.0
    if st in RED_STATES:
        return 0.0
    return np.nan


def yn(s):
    s = str(s).strip().lower()
    return 1.0 if s == "yes" else (0.0 if s in ("no", "nonexistent") else np.nan)


def load():
    df = pd.read_excel(ANALYSIS_XLSX, sheet_name="unbalanced")
    df["year"] = df["year"].astype(int)
    df["post"] = (df["year"] == 2024).astype(int)
    df["post_2023"] = (df["year"] == 2023).astype(int)

    # Blue state classification
    df["blue_state"] = df["coc_id"].apply(classify_state)
    df["state"] = df["coc_id"].str.split("-").str[0]
    df["did_blue"] = df["blue_state"] * df["post"]
    df["did_blue_placebo_2023"] = df["blue_state"] * df["post_2023"]

    # Convert cells
    df["crim_activity_index"] = pd.to_numeric(df["crim_activity_index"], errors="coerce")
    df["implemented_anticrim_practice"] = pd.to_numeric(df["implemented_anticrim_practice"], errors="coerce")
    for f in [f"1d_4_{r}_policymakers" for r in (1, 2, 3)]:
        if f in df.columns:
            df[f + "__bin"] = df[f].map(yn)
    eng_cells = [f + "__bin" for f in
                 ["1d_4_1_policymakers", "1d_4_2_policymakers", "1d_4_3_policymakers"]]
    df["DV2_engagement"] = df[eng_cells].mean(axis=1, skipna=True)
    df["DV3_implemented"] = df["implemented_anticrim_practice"]

    # Controls
    df["ple_dm_log"] = np.log1p(pd.to_numeric(df["1d_10a_1_years"], errors="coerce").clip(lower=0))
    df["ple_ces_bin"] = (df["1b_1_6_ces"].astype(str).str.strip().str.lower() == "yes").astype(float)
    df["hf_pct"] = pd.to_numeric(df["1d_2_3"], errors="coerce")
    df.loc[df["hf_pct"] > 1.5, "hf_pct"] = df["hf_pct"] / 100
    df["hmis_cov"] = pd.to_numeric(df["2a_5_1_coverage"], errors="coerce")
    df.loc[df["hmis_cov"] > 1.5, "hmis_cov"] = df["hmis_cov"] / 100
    df["hmis_cov"] = df["hmis_cov"].clip(0, 1)
    bed_cols = [c for c in (f"2a_5_{i}_non_vsp" for i in range(1, 7)) if c in df.columns]
    bed_sum = pd.DataFrame({c: pd.to_numeric(df[c], errors="coerce") for c in bed_cols}).sum(axis=1, min_count=1)
    df["log_beds"] = np.log1p(bed_sum.clip(upper=bed_sum.quantile(0.99)))

    return df


def mundlak(df, cols):
    df = df.copy()
    for c in cols:
        df[c + "_bar"] = df.groupby("coc_id")[c].transform("mean")
    return df


def fit_fe(df, rhs, dv, entity=True, time=False):
    sub = df.dropna(subset=[dv] + list(rhs) + ["blue_state"]).copy()
    sub = sub.set_index(["coc_id", "year"])
    y = sub[dv].astype(float)
    X = sub[list(rhs)].astype(float)
    X = sm.add_constant(X, has_constant="add")
    mod = PanelOLS(y, X, entity_effects=entity, time_effects=time, drop_absorbed=True)
    return mod.fit(cov_type="clustered", cluster_entity=True), len(sub)


def fit_fl(df, rhs, dv, year_dummies=True):
    sub = df.dropna(subset=[dv] + list(rhs) + ["coc_id", "blue_state"]).copy()
    y = sub[dv].astype(float).clip(0, 1)
    X = sub[list(rhs)].astype(float)
    X = sm.add_constant(X, has_constant="add")
    if year_dummies and sub["year"].nunique() > 1:
        yd = pd.get_dummies(sub["year"], prefix="yr", drop_first=True).astype(float)
        X = pd.concat([X, yd], axis=1)
    mod = sm.GLM(y, X, family=sm.families.Binomial())
    return mod.fit(cov_type="cluster", cov_kwds={"groups": sub["coc_id"].values}), len(sub)


def wcb_pvalue(df, rhs, dv, target="did_blue", n=N_BOOT, seed=42):
    sub = df.dropna(subset=[dv] + list(rhs) + ["coc_id", "blue_state"]).copy()
    y = sub[dv].astype(float).values
    X = sub[list(rhs)].astype(float)
    X = sm.add_constant(X, has_constant="add").values
    clusters = sub["coc_id"].values
    res_obs = sm.OLS(y, X).fit(cov_type="cluster", cov_kwds={"groups": clusters})
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


def fmt(res, v, panel=False):
    p = res.params; s = res.std_errors if panel else res.bse; pv = res.pvalues
    if v not in p.index or pd.isna(p[v]):
        return "—"
    return f"{p[v]:+.3f}{star(pv[v] if v in pv else None)}<br><span class='hint'>({s[v]:.3f})</span>"


def safe_b(res, v, panel=False):
    p = res.params; s = res.std_errors if panel else res.bse; pv = res.pvalues
    if v not in p.index or pd.isna(p[v]):
        return None
    return (float(p[v]), float(s[v]), float(pv[v]) if v in pv else None)


def main():
    df = load()
    coded = df.dropna(subset=["blue_state"])
    print(f"Rows: {len(df)}; classified: {len(coded)} "
          f"(blue={int((coded.blue_state==1).sum())}, "
          f"red={int((coded.blue_state==0).sum())}, "
          f"excluded: {len(df) - len(coded)} [territories])")

    mund_vars = ["ple_dm_log", "ple_ces_bin", "hf_pct", "hmis_cov", "log_beds"]
    df = mundlak(df, mund_vars)

    # Parallel trends
    pt = (coded.dropna(subset=["crim_activity_index"])
          .groupby(["blue_state", "year"])["crim_activity_index"]
          .agg(["mean", "count", "std"]).reset_index())
    pt["group"] = pt["blue_state"].map({0: "red", 1: "blue"})
    pt["se"] = pt["std"] / pt["count"] ** 0.5
    pt[["group", "year", "mean", "se", "count"]].to_csv(OUT_TRENDS, index=False)
    print("\nGroup × year means:")
    print(pt.pivot(index="year", columns="group", values="mean").round(3))

    # Specifications
    results = []

    # B1: DV1 OLS + CoC FE
    rhs_fe = ["post", "did_blue", "hf_pct", "hmis_cov", "log_beds", "ple_ces_bin"]
    r, n = fit_fe(df, rhs_fe, "crim_activity_index", entity=True, time=False)
    results.append(("B1·DV1 OLS+CoC FE", r, n, True))

    # B2: + Year FE
    rhs_fe2 = ["did_blue", "hf_pct", "hmis_cov", "log_beds", "ple_ces_bin"]
    r, n = fit_fe(df, rhs_fe2, "crim_activity_index", entity=True, time=True)
    results.append(("B2·DV1 OLS+CoC+Year FE", r, n, True))

    # B3: primary — pooled fractional logit + Mundlak
    rhs_fl = ["blue_state", "post", "did_blue",
              "hf_pct", "hmis_cov", "log_beds", "ple_ces_bin",
              "hf_pct_bar", "hmis_cov_bar", "log_beds_bar", "ple_ces_bin_bar"]
    r, n = fit_fl(df, rhs_fl, "crim_activity_index", year_dummies=False)
    results.append(("B3·DV1 frac-logit + Mundlak", r, n, False))

    # B4: event study — add placebo did_blue_2023
    rhs_event = ["blue_state", "post_2023", "post", "did_blue_placebo_2023", "did_blue",
                 "hf_pct", "hmis_cov", "log_beds", "ple_ces_bin",
                 "hf_pct_bar", "hmis_cov_bar", "log_beds_bar", "ple_ces_bin_bar"]
    r, n = fit_fl(df, rhs_event, "crim_activity_index", year_dummies=False)
    results.append(("B4·DV1 event study (pre-trend placebo)", r, n, False))

    # B5: DV2 engagement-only + Mundlak
    r, n = fit_fl(df, rhs_fl, "DV2_engagement", year_dummies=False)
    results.append(("B5·DV2 engagement-only", r, n, False))

    # B6: DV3 binary implemented
    r, n = fit_fl(df, rhs_fl, "DV3_implemented", year_dummies=False)
    results.append(("B6·DV3 binary (implemented)", r, n, False))

    # Wild-cluster bootstrap on primary DiD (B3)
    print("\nRunning wild-cluster bootstrap for primary DiD...")
    p_boot, t_obs = wcb_pvalue(df, rhs_fl, "crim_activity_index", target="did_blue")
    print(f"  observed t = {t_obs:.3f}; bootstrap p = {p_boot:.3f}")

    # State-level composition diagnostics
    st_blue_share = int((coded.blue_state == 1).sum())
    st_red_share = int((coded.blue_state == 0).sum())
    coc_blue = sorted(coded.loc[coded.blue_state == 1, "state"].unique())
    coc_red = sorted(coded.loc[coded.blue_state == 0, "state"].unique())

    # Build MD report
    def show(res, v, panel=False):
        c = safe_b(res, v, panel)
        if c is None: return "(absorbed / n/a)"
        b, s, p = c
        star_s = star(p)
        return f"β = {b:.3f}{star_s} (SE {s:.3f}, p = {p:.3f})"

    b3_did = safe_b(results[2][1], "did_blue", results[2][3])
    b4_placebo = safe_b(results[3][1], "did_blue_placebo_2023", results[3][3])
    b5_did = safe_b(results[4][1], "did_blue", results[4][3])
    b6_did = safe_b(results[5][1], "did_blue", results[5][3])

    md = [
        "# Blue-State vs Red-State DiD (Grants Pass)",
        "",
        f"_Generated: {pd.Timestamp.now().isoformat(timespec='seconds')}_",
        "",
        "## Design",
        "",
        "Alternative treatment definition: **political environment of the CoC's state**",
        "rather than lead-agency type. CoCs in states that voted Biden in the 2020",
        "presidential election (Electoral College) are treated; Trump-voting states",
        "are the control. Territories (PR/VI/GU) are excluded from this DiD.",
        "",
        "- **Treatment (blue):** {0} CoC-years across {1} states".format(
            st_blue_share, len(coc_blue)),
        "- **Control (red):** {0} CoC-years across {1} states".format(
            st_red_share, len(coc_red)),
        "- **Pre period:** FY2022, FY2023 (before June 2024 ruling)",
        "- **Post period:** FY2024 (applications submitted Oct 30, 2024)",
        "",
        "### Theoretical expectation",
        "",
        "Blue-state CoCs face stronger progressive pressure against",
        "criminalization, so should differentially expand reported anti-crim",
        "activity in FY2024 (β_DiD > 0). Alternative null: blue-state CoCs were",
        "already high pre-Grants Pass, leaving little room to respond — or the",
        "ruling uniformly affected reporting across political contexts.",
        "",
        "### Parallel-trends check",
        "",
        "| Year | Red | Blue | Δ (Blue − Red) |",
        "|---|---|---|---|",
    ]
    pt_wide = pt.pivot(index="year", columns="group", values="mean").round(3)
    for yr in sorted(pt_wide.index):
        r = pt_wide.loc[yr, "red"]; b = pt_wide.loc[yr, "blue"]
        md.append(f"| {yr} | {r:.3f} | {b:.3f} | {b-r:+.3f} |")
    md.append("")
    md.append(
        f"FY22→FY23 pre-trend: red {pt_wide.loc[2023,'red']-pt_wide.loc[2022,'red']:+.3f}, "
        f"blue {pt_wide.loc[2023,'blue']-pt_wide.loc[2022,'blue']:+.3f}."
    )
    md.append(
        f"FY23→FY24 post-shock: red {pt_wide.loc[2024,'red']-pt_wide.loc[2023,'red']:+.3f}, "
        f"blue {pt_wide.loc[2024,'blue']-pt_wide.loc[2023,'blue']:+.3f}."
    )
    md.append("")

    # Table
    all_vars = ["blue_state", "post_2023", "post", "did_blue_placebo_2023", "did_blue",
                "hf_pct", "hmis_cov", "log_beds", "ple_ces_bin", "const"]
    label_map = {
        "blue_state": "Blue state (treatment)",
        "post_2023": "FY2023 indicator",
        "post": "Post-Grants Pass (FY2024)",
        "did_blue_placebo_2023": "Blue × FY2023 (placebo)",
        "did_blue": "<strong>Blue × Post ← β_DiD</strong>",
        "hf_pct": "Housing First adoption",
        "hmis_cov": "HMIS ES coverage",
        "log_beds": "log(total beds + 1)",
        "ple_ces_bin": "PLE in CES (binary)",
        "const": "(Intercept)",
    }

    header = "| Variable | " + " | ".join(m[0] for m in results) + " |"
    sep = "|---|" + "|".join(["---"] * len(results)) + "|"
    rows = []
    for v in all_vars:
        row = [label_map.get(v, v)]
        for _, res, _, panel in results:
            row.append(fmt(res, v, panel))
        rows.append("| " + " | ".join(row) + " |")
    rows.append("| **N** | " + " | ".join(str(n) for _, _, n, _ in results) + " |")

    md += [
        "## Coefficient table",
        "",
        header, sep, *rows,
        "",
        "Cluster-robust SEs at the CoC level in parentheses · `*** p<0.01, ** p<0.05, * p<0.10`.",
        "",
        "## Key estimates",
        "",
        f"- **Primary β_DiD (B3 DV1 frac-logit + Mundlak):** {show(results[2][1], 'did_blue')}",
        f"- **Wild-cluster bootstrap p:** {p_boot:.3f} (based on 999 Rademacher replicates)",
        f"- **Pre-trend placebo (B4):** {show(results[3][1], 'did_blue_placebo_2023')}",
        f"- **DV2 engagement-only (B5):** {show(results[4][1], 'did_blue')}",
        f"- **DV3 implemented-binary (B6):** {show(results[5][1], 'did_blue')}",
        "",
        "## Interpretation",
        "",
    ]

    if b3_did:
        b, s, p = b3_did
        dir_word = "larger" if b > 0 else "smaller"
        sig = ("statistically significant at p < .05" if p < 0.05
               else ("borderline at p < .10" if p < 0.10
                     else "not statistically significant"))
        md.append(f"- Blue-state CoCs showed a {abs(b):.3f} logit-point {dir_word} "
                  f"differential change from pre to post than red-state CoCs; this is {sig}.")
    if b4_placebo and b4_placebo[2] is not None:
        _, _, pvp = b4_placebo
        if pvp < 0.10:
            md.append(f"- ⚠ The FY2023 placebo is significant (p = {pvp:.3f}); parallel-trends assumption is shaky.")
        else:
            md.append(f"- The FY2023 placebo is not significant (p ≈ {pvp:.2f}); parallel-trends assumption is plausible.")

    md += [
        "",
        "## Caveats",
        "",
        "1. **State-level treatment is coarse.** A CoC in a blue-state red county",
        "   (e.g., rural Pennsylvania) is treated identically to a CoC in a blue-state",
        "   blue county (e.g., Philadelphia). Local political environment likely matters",
        "   more than state-level. A future version could use county partisan vote share.",
        "2. **2020 classification is static.** Some 2020 blue states (Georgia, Arizona)",
        "   are highly competitive; some 2020 red states (North Carolina) nearly flipped.",
        "3. **Selection into lead-agency.** Blue states may have more nonprofit-led CoCs.",
        "   The blue-state effect and the nonprofit effect could be correlated — a joint",
        "   specification would disentangle them (add both variables + interaction).",
        "4. **Grants Pass exposure.** The ruling affects all states equally, but local",
        "   political will to enact or resist anti-camping ordinances varies. The DiD",
        "   captures *reporting differential*, not behavioral differential.",
    ]

    OUT_MD.write_text("\n".join(md))
    print(f"\nwrote {OUT_MD}")

    # CSV
    import csv
    with OUT_CSV.open("w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["spec", "variable", "coef", "se", "pvalue", "n"])
        for label, res, n, panel in results:
            ses = res.std_errors if panel else res.bse
            for v in res.params.index:
                try:
                    w.writerow([label, v,
                                round(float(res.params[v]), 5),
                                round(float(ses[v]), 5),
                                round(float(res.pvalues[v]), 5) if v in res.pvalues.index else "",
                                n])
                except (ValueError, TypeError):
                    continue
        w.writerow(["B3·DV1 frac-logit + Mundlak", "did_blue_bootstrap_p", "", "", p_boot, ""])
    print(f"wrote {OUT_CSV}")

    # Console summary
    print()
    for line in [header, sep] + rows:
        print(line.replace("<br>", " ").replace("<span class='hint'>", "").replace("</span>", "").replace("<strong>", "").replace("</strong>", ""))


if __name__ == "__main__":
    main()
