"""Interactive CoC map — v2 (visualization-focused redesign).

Improvements over v1
--------------------
* Variable picker is a horizontal row of pill buttons (all visible at once,
  each shows a color-scale preview).
* Year picker is a separate pill row (segmented control).
* Color range is **fixed per variable** across years, so the same color
  means the same value in FY22 and FY24 — allowing meaningful temporal
  comparison.
* Marker size encodes CoC size (log total beds) when the coloring variable
  is not itself size — so big CoCs like NYC are visible.
* Categorical variables (`nonprofit_led`) use two distinct colors and a
  proper legend, not a gradient colorbar.
* Right-side summary panel updates with the selection: n, mean, median,
  range, and a mini inline histogram.
* Hover shows multi-variable context for each CoC-year.
* Clean typography, bordered pill buttons, active-state styling.
"""
from __future__ import annotations

import hashlib
import html
import json
from pathlib import Path

import numpy as np
import pandas as pd

from pipeline_utils import PIPELINE_DIR

OUT_HTML = PIPELINE_DIR.parent / "docs" / "map.html"
ANALYSIS_XLSX = PIPELINE_DIR / "coc_analysis_ready.xlsx"

STATE_CENTROIDS = {
    "AK": (64.2, -149.5), "AL": (32.8, -86.8), "AR": (34.9, -92.4),
    "AZ": (34.3, -111.7), "CA": (36.8, -119.4), "CO": (39.0, -105.5),
    "CT": (41.6, -72.7),  "DC": (38.9, -77.0),  "DE": (39.0, -75.5),
    "FL": (27.8, -82.6),  "GA": (32.7, -83.4),  "GU": (13.4, 144.7),
    "HI": (20.9, -156.5), "IA": (42.1, -93.5),  "ID": (44.2, -114.5),
    "IL": (40.1, -89.2),  "IN": (39.9, -86.3),  "KS": (38.6, -98.4),
    "KY": (37.6, -85.3),  "LA": (31.2, -92.0),  "MA": (42.2, -71.5),
    "MD": (39.1, -76.8),  "ME": (45.4, -69.2),  "MI": (43.3, -84.5),
    "MN": (45.7, -93.9),  "MO": (38.6, -92.2),  "MS": (32.7, -89.7),
    "MT": (46.9, -110.4), "NC": (35.6, -79.4),  "ND": (47.5, -99.8),
    "NE": (41.5, -99.8),  "NH": (43.4, -71.6),  "NJ": (40.3, -74.5),
    "NM": (34.8, -106.2), "NV": (38.3, -117.0), "NY": (42.9, -75.5),
    "OH": (40.3, -82.8),  "OK": (35.5, -97.5),  "OR": (44.6, -122.1),
    "PA": (40.6, -77.2),  "PR": (18.2, -66.5),  "RI": (41.7, -71.5),
    "SC": (33.9, -80.9),  "SD": (44.3, -99.4),  "TN": (35.7, -86.7),
    "TX": (31.0, -97.6),  "UT": (40.2, -111.9), "VA": (37.8, -78.2),
    "VI": (18.3, -64.9),  "VT": (44.0, -72.7),  "WA": (47.4, -121.5),
    "WI": (44.3, -89.6),  "WV": (38.5, -80.9),  "WY": (42.8, -107.3),
}


def jitter_for(coc_id: str, scale: float = 2.2) -> tuple[float, float]:
    h = hashlib.md5(coc_id.encode()).digest()
    return ((h[0] / 255 - 0.5) * scale, (h[1] / 255 - 0.5) * scale)


def coordinate(coc_id: str):
    state = coc_id.split("-")[0]
    if state not in STATE_CENTROIDS:
        return None, None
    lat0, lon0 = STATE_CENTROIDS[state]
    dl, dn = jitter_for(coc_id)
    return lat0 + dl, lon0 + dn


def build_dataset() -> pd.DataFrame:
    df = pd.read_excel(ANALYSIS_XLSX, sheet_name="unbalanced")
    iv = pd.read_excel(ANALYSIS_XLSX, sheet_name="iv_leadership")
    df = df.merge(iv[["coc_id", "lead_agency_type", "nonprofit_led"]],
                  on="coc_id", how="left")
    df["year"] = df["year"].astype(int)
    coords = df["coc_id"].apply(coordinate)
    df["lat"] = [c[0] for c in coords]
    df["lon"] = [c[1] for c in coords]
    df["crim_activity_index"] = pd.to_numeric(df["crim_activity_index"], errors="coerce")
    df["implemented_anticrim_practice"] = pd.to_numeric(
        df["implemented_anticrim_practice"], errors="coerce"
    )
    df["ple_dm_count"] = pd.to_numeric(df["1d_10a_1_years"], errors="coerce")
    df["hf_pct"] = pd.to_numeric(df["1d_2_3"], errors="coerce")
    df.loc[df["hf_pct"] > 1.5, "hf_pct"] = df["hf_pct"] / 100
    df["hmis_cov"] = pd.to_numeric(df["2a_5_1_coverage"], errors="coerce")
    df.loc[df["hmis_cov"] > 1.5, "hmis_cov"] = df["hmis_cov"] / 100
    df["hmis_cov"] = df["hmis_cov"].clip(0, 1)
    bed_cols = [c for c in (f"2a_5_{i}_non_vsp" for i in range(1, 7)) if c in df.columns]
    bed_sum = pd.DataFrame({c: pd.to_numeric(df[c], errors="coerce") for c in bed_cols}).sum(axis=1, min_count=1)
    df["total_beds"] = bed_sum
    df["log_beds"] = np.log1p(bed_sum)
    df["leadership_label"] = df["nonprofit_led"].map({1: "Nonprofit", 0: "Government"}).fillna("Unclassified")
    df["coc_name"] = df["1a_1b"].fillna("").astype(str)
    return df.dropna(subset=["lat", "lon"])


# Variable specifications
# kind: "continuous" | "categorical" | "binary"
# cmin/cmax: fixed color range across years (None = auto)
VARIABLES = [
    {"id": "crim_activity_index", "label": "Anti-crim activity index",
     "sub": "Primary DV · share of 1D-4 cells = Yes",
     "kind": "continuous", "cmin": 0.0, "cmax": 1.0,
     "colorscale": "RdYlGn", "preview": ["#c53030", "#ffef8a", "#17813c"]},
    {"id": "implemented_anticrim_practice", "label": "Implemented anti-crim",
     "sub": "Binary · Yes in any 1D-4 implementation cell",
     "kind": "binary", "cmin": 0.0, "cmax": 1.0,
     "colorscale": "RdYlGn", "preview": ["#c53030", "#17813c"]},
    {"id": "nonprofit_led", "label": "Lead-agency type",
     "sub": "Green = nonprofit · Red = government",
     "kind": "categorical", "cmin": 0.0, "cmax": 1.0,
     "colorscale": None, "preview": ["#c53030", "#999", "#17813c"]},
    {"id": "ple_dm_count", "label": "PLE in decisionmaking",
     "sub": "# people with lived experience · log-scaled colors",
     "kind": "continuous", "cmin": 0.0, "cmax": 4.5,
     "colorscale": "Viridis", "preview": ["#440154", "#21908C", "#FDE725"],
     "transform": "log1p"},
    {"id": "hf_pct", "label": "Housing First adoption",
     "sub": "Share of CoC projects adopting Housing First (0-1)",
     "kind": "continuous", "cmin": 0.0, "cmax": 1.0,
     "colorscale": "Blues", "preview": ["#f7fbff", "#6baed6", "#08306b"]},
    {"id": "hmis_cov", "label": "HMIS ES coverage",
     "sub": "Share of Emergency Shelter beds in HMIS (0-1)",
     "kind": "continuous", "cmin": 0.0, "cmax": 1.0,
     "colorscale": "Blues", "preview": ["#f7fbff", "#6baed6", "#08306b"]},
    {"id": "log_beds", "label": "CoC size (log beds)",
     "sub": "log(total beds + 1) — proxy for CoC size",
     "kind": "continuous", "cmin": 0.0, "cmax": 12.0,
     "colorscale": "Plasma", "preview": ["#0d0887", "#cc4778", "#f0f921"]},
    # ---------- Composite research-model view ----------
    {"id": "research_model", "label": "★ Research model (IV · M · DV)",
     "sub": "Color = DV (activity) · Size = Mediator (PLE) · Ring color = IV (leadership)",
     "kind": "composite_model", "cmin": 0.0, "cmax": 1.0,
     "colorscale": "RdYlGn", "preview": ["#c53030", "#ffef8a", "#17813c"]},
    # ---------- Change map ----------
    {"id": "activity_change", "label": "★ Change FY23 → FY24",
     "sub": "Post-Grants Pass shift in activity index · divergent (red = decrease, green = increase)",
     "kind": "composite_change", "cmin": -0.4, "cmax": 0.4,
     "colorscale": "RdBu", "preview": ["#c53030", "#f5f5f5", "#17813c"]},
]
YEARS = [2022, 2023, 2024]


def build_all():
    df = build_dataset()

    traces = []   # list of Plotly trace dicts
    stats = []    # parallel list of {n, mean, median, min, max, hist_x, hist_y}

    for spec in VARIABLES:
        for y in YEARS:
            sub = df[df["year"] == y].copy()

            # ---------- Composite: research model view ----------
            if spec["kind"] == "composite_model":
                sub = sub.dropna(subset=["crim_activity_index", "ple_dm_count",
                                         "nonprofit_led", "lat", "lon"]).copy()
                # Size from log1p(PLE count), mapped to 8–22 px
                ple_log = np.log1p(sub["ple_dm_count"].clip(lower=0))
                sizes = (ple_log / max(ple_log.max(), 1) * 14 + 8).tolist()
                # Ring color by leadership
                ring_colors = np.where(sub["nonprofit_led"] == 1, "#17813c", "#c53030").tolist()
                customdata = np.stack([
                    sub["coc_id"].values,
                    sub["coc_name"].values,
                    sub["leadership_label"].values,
                    sub["crim_activity_index"].round(3).fillna(0).values,
                    sub["ple_dm_count"].fillna(0).astype(int).values,
                    sub["total_beds"].fillna(0).astype(int).values,
                    sub["hf_pct"].round(3).fillna(-1).values,
                ], axis=-1)
                hover = (
                    "<b>%{customdata[0]}</b> · %{customdata[1]}<br>"
                    f"FY{y}<br>"
                    "<b>IV</b> Lead agency: %{customdata[2]}<br>"
                    "<b>M</b> PLE in decisionmaking: %{customdata[4]}<br>"
                    "<b>Y</b> Anti-crim activity index: %{customdata[3]}<br>"
                    "—<br>"
                    "CoC total beds: %{customdata[5]}<br>"
                    "Housing First %: %{customdata[6]}"
                    "<extra></extra>"
                )
                trace = {
                    "type": "scattergeo", "mode": "markers",
                    "lat": sub["lat"].tolist(), "lon": sub["lon"].tolist(),
                    "marker": {
                        "size": sizes,
                        "color": sub["crim_activity_index"].tolist(),
                        "colorscale": spec["colorscale"],
                        "cmin": spec["cmin"], "cmax": spec["cmax"],
                        "showscale": True,
                        "colorbar": {
                            "title": {"text": "Anti-crim activity (DV)", "font": {"size": 11}},
                            "thickness": 10, "len": 0.55, "x": 1.0,
                            "tickfont": {"size": 10},
                        },
                        "line": {"width": 2.0, "color": ring_colors},
                        "opacity": 0.9,
                    },
                    "customdata": customdata.tolist(),
                    "hovertemplate": hover,
                    "name": f"{spec['id']}·{y}", "visible": False, "showlegend": False,
                }
                # Summary: show n, correlation between PLE count and activity, mean activity
                act = sub["crim_activity_index"].values
                ple_v = ple_log.values
                if len(act) > 1 and np.std(ple_v) > 0:
                    corr = float(np.corrcoef(ple_v, act)[0, 1])
                else:
                    corr = None
                summary = {
                    "n": len(sub),
                    "nonprofit_n": int((sub["nonprofit_led"] == 1).sum()),
                    "govt_n": int((sub["nonprofit_led"] == 0).sum()),
                    "mean_activity_nonprofit": round(float(sub.loc[sub["nonprofit_led"] == 1, "crim_activity_index"].mean()), 3)
                        if (sub["nonprofit_led"] == 1).any() else None,
                    "mean_activity_govt": round(float(sub.loc[sub["nonprofit_led"] == 0, "crim_activity_index"].mean()), 3)
                        if (sub["nonprofit_led"] == 0).any() else None,
                    "corr_ple_activity": round(corr, 3) if corr is not None else None,
                }
                traces.append(trace)
                stats.append({
                    "variable": spec["id"], "year": y,
                    "label": spec["label"], "sub": spec["sub"],
                    "kind": spec["kind"], "summary": summary,
                })
                continue

            # ---------- Composite: change FY23 → FY24 ----------
            if spec["kind"] == "composite_change":
                if y != 2024:
                    # Only meaningful for 2024; emit empty trace for 2022/2023 slots
                    traces.append({
                        "type": "scattergeo", "mode": "markers",
                        "lat": [], "lon": [], "name": f"{spec['id']}·{y}",
                        "visible": False, "showlegend": False,
                        "hoverinfo": "skip",
                    })
                    stats.append({
                        "variable": spec["id"], "year": y,
                        "label": spec["label"], "sub": spec["sub"],
                        "kind": spec["kind"],
                        "summary": {"n": 0, "note": "Change view is FY2024-only — switch year to FY2024."},
                    })
                    continue
                # Compute Δ per CoC (2024 - 2023)
                a23 = df[df["year"] == 2023][["coc_id", "crim_activity_index"]].rename(
                    columns={"crim_activity_index": "act23"})
                a24 = df[df["year"] == 2024][["coc_id", "crim_activity_index", "lat", "lon",
                                              "coc_name", "leadership_label", "nonprofit_led",
                                              "total_beds"]].rename(
                    columns={"crim_activity_index": "act24"})
                sub_c = a24.merge(a23, on="coc_id", how="inner").dropna(subset=["act24", "act23"])
                sub_c["delta"] = sub_c["act24"] - sub_c["act23"]
                ring_colors = np.where(sub_c["nonprofit_led"] == 1, "#17813c", "#c53030").tolist()
                sizes = (10 + np.log1p(sub_c["total_beds"].fillna(0)).clip(0, 12) / 2).tolist()
                customdata = np.stack([
                    sub_c["coc_id"].values,
                    sub_c["coc_name"].fillna("").values,
                    sub_c["leadership_label"].values,
                    sub_c["act23"].round(3).fillna(0).values,
                    sub_c["act24"].round(3).fillna(0).values,
                    sub_c["delta"].round(3).fillna(0).values,
                ], axis=-1)
                hover = (
                    "<b>%{customdata[0]}</b> · %{customdata[1]}<br>"
                    "Lead agency: %{customdata[2]}<br>"
                    "FY2023 activity: %{customdata[3]}<br>"
                    "FY2024 activity: %{customdata[4]}<br>"
                    "<b>Δ (FY24 − FY23): %{customdata[5]}</b>"
                    "<extra></extra>"
                )
                trace = {
                    "type": "scattergeo", "mode": "markers",
                    "lat": sub_c["lat"].tolist(), "lon": sub_c["lon"].tolist(),
                    "marker": {
                        "size": sizes,
                        "color": sub_c["delta"].tolist(),
                        "colorscale": spec["colorscale"],
                        "cmin": spec["cmin"], "cmax": spec["cmax"],
                        "showscale": True,
                        "colorbar": {
                            "title": {"text": "Δ activity (FY24 − FY23)", "font": {"size": 11}},
                            "thickness": 10, "len": 0.55, "x": 1.0,
                            "tickfont": {"size": 10},
                        },
                        "line": {"width": 1.8, "color": ring_colors},
                        "opacity": 0.9,
                    },
                    "customdata": customdata.tolist(),
                    "hovertemplate": hover,
                    "name": f"{spec['id']}·{y}", "visible": False, "showlegend": False,
                }
                d = sub_c["delta"].values
                summary = {
                    "n": len(sub_c),
                    "mean": round(float(np.mean(d)), 3) if len(d) else None,
                    "median": round(float(np.median(d)), 3) if len(d) else None,
                    "pos_count": int((d > 0).sum()),
                    "neg_count": int((d < 0).sum()),
                    "zero_count": int((d == 0).sum()),
                    "mean_np": round(float(np.mean(d[sub_c["nonprofit_led"].values == 1])), 3)
                        if (sub_c["nonprofit_led"] == 1).any() else None,
                    "mean_gov": round(float(np.mean(d[sub_c["nonprofit_led"].values == 0])), 3)
                        if (sub_c["nonprofit_led"] == 0).any() else None,
                }
                # Mini hist
                bins = np.linspace(spec["cmin"], spec["cmax"], 11)
                counts, _ = np.histogram(d, bins=bins)
                summary["hist_x"] = [round(0.5 * (bins[i] + bins[i + 1]), 2) for i in range(len(bins) - 1)]
                summary["hist_y"] = counts.tolist()
                traces.append(trace)
                stats.append({
                    "variable": spec["id"], "year": y,
                    "label": spec["label"], "sub": spec["sub"],
                    "kind": spec["kind"], "summary": summary,
                })
                continue

            # ---------- Standard single-variable trace ----------
            if spec.get("transform") == "log1p":
                sub["val"] = np.log1p(sub[spec["id"]].clip(lower=0))
            else:
                sub["val"] = sub[spec["id"]]

            sub = sub.dropna(subset=["val"])

            # marker size — log_beds for non-size variables; fixed for size itself
            if spec["id"] == "log_beds":
                sizes = [8] * len(sub)
            else:
                # Map log_beds in [0, 12] to marker size in [6, 18]
                lb = sub["log_beds"].fillna(sub["log_beds"].median())
                sizes = ((lb - 4).clip(lower=0) / 8 * 12 + 6).tolist()

            customdata = np.stack([
                sub["coc_id"].values,
                sub["coc_name"].values,
                sub["leadership_label"].values,
                sub["val"].round(3).fillna(0).values,
                sub[spec["id"]].fillna(0).values,
                sub["total_beds"].fillna(0).astype(int).values,
                sub["crim_activity_index"].round(3).fillna(-1).values,
                sub["hf_pct"].round(3).fillna(-1).values,
            ], axis=-1)

            hover_val_name = spec["label"]
            hover = (
                "<b>%{customdata[0]}</b> · %{customdata[1]}<br>"
                f"FY{y}<br>"
                "Lead agency: <b>%{customdata[2]}</b><br>"
                f"<b>{hover_val_name}</b>: %{{customdata[4]}}<br>"
                "—<br>"
                "CoC total beds: %{customdata[5]}<br>"
                "Activity index: %{customdata[6]}<br>"
                "Housing First %: %{customdata[7]}"
                "<extra></extra>"
            )

            # Trace construction depends on variable kind
            if spec["kind"] == "categorical":
                # Emit a compound trace (two sub-traces? or single with explicit colors)
                # Simpler: one trace with discrete colors, no colorbar.
                color_map = {1: "#17813c", 0: "#c53030"}
                colors = [color_map.get(int(v), "#bbbbbb") if pd.notna(v) else "#bbbbbb"
                          for v in sub["val"]]
                trace = {
                    "type": "scattergeo", "mode": "markers",
                    "lat": sub["lat"].tolist(), "lon": sub["lon"].tolist(),
                    "marker": {
                        "size": sizes, "color": colors,
                        "line": {"width": 0.8, "color": "white"},
                        "opacity": 0.85,
                    },
                    "customdata": customdata.tolist(),
                    "hovertemplate": hover,
                    "name": f"{spec['id']}·{y}",
                    "visible": False,
                    "showlegend": False,
                }
            else:
                trace = {
                    "type": "scattergeo", "mode": "markers",
                    "lat": sub["lat"].tolist(), "lon": sub["lon"].tolist(),
                    "marker": {
                        "size": sizes,
                        "color": sub["val"].tolist(),
                        "colorscale": spec["colorscale"],
                        "cmin": spec["cmin"], "cmax": spec["cmax"],
                        "showscale": True,
                        "colorbar": {
                            "title": {"text": spec["label"], "font": {"size": 11}},
                            "thickness": 10, "len": 0.55, "x": 1.0,
                            "tickfont": {"size": 10},
                        },
                        "line": {"width": 0.6, "color": "white"},
                        "opacity": 0.85,
                    },
                    "customdata": customdata.tolist(),
                    "hovertemplate": hover,
                    "name": f"{spec['id']}·{y}",
                    "visible": False,
                    "showlegend": False,
                }

            # Summary stats for this (variable, year)
            values = sub[spec["id"]].dropna().tolist()
            if spec["kind"] == "categorical":
                from collections import Counter
                cnt = Counter(int(v) for v in values if pd.notna(v))
                summary = {
                    "n": len(values),
                    "counts": {"Nonprofit": cnt.get(1, 0), "Government": cnt.get(0, 0)},
                }
            else:
                if values:
                    summary = {
                        "n": len(values),
                        "mean": round(np.mean(values), 3),
                        "median": round(float(np.median(values)), 3),
                        "min": round(min(values), 3),
                        "max": round(max(values), 3),
                        "std": round(float(np.std(values)), 3),
                    }
                else:
                    summary = {"n": 0}
                # Inline histogram (10 bins)
                if values:
                    lo, hi = spec["cmin"], spec["cmax"]
                    bins = np.linspace(lo, hi, 11)
                    plot_vals = (np.log1p(np.clip(values, 0, None))
                                 if spec.get("transform") == "log1p" else values)
                    counts, _ = np.histogram(plot_vals, bins=bins)
                    summary["hist_y"] = counts.tolist()
                    summary["hist_x"] = [round(0.5 * (bins[i] + bins[i + 1]), 2)
                                         for i in range(len(bins) - 1)]

            traces.append(trace)
            stats.append({
                "variable": spec["id"], "year": y,
                "label": spec["label"], "sub": spec["sub"],
                "kind": spec["kind"],
                "summary": summary,
            })

    # Mark the default view visible
    default_idx = 0  # crim_activity_index · 2024
    for i, s in enumerate(stats):
        if s["variable"] == "crim_activity_index" and s["year"] == 2024:
            default_idx = i
            break
    traces[default_idx]["visible"] = True

    layout = {
        "geo": {
            "scope": "usa",
            "projection": {"type": "albers usa"},
            "showland": True, "landcolor": "#fafafa",
            "showsubunits": True, "subunitcolor": "#d6d6d6",
            "subunitwidth": 0.7,
            "showlakes": True, "lakecolor": "#e8f4f8",
            "showframe": False, "bgcolor": "white",
            "resolution": 50,
        },
        "height": 560,
        "margin": {"t": 20, "b": 10, "l": 10, "r": 10},
        "showlegend": False,
        "paper_bgcolor": "white",
    }

    return df, traces, stats, layout, default_idx


def render(df, traces, stats, layout, default_idx):
    n_records = len(df)
    n_coc = df["coc_id"].nunique()
    coded_records = df["nonprofit_led"].notna().sum()
    pct_coded = 100 * coded_records / n_records

    # Pill buttons for variables
    var_pills = []
    for i, spec in enumerate(VARIABLES):
        # preview gradient
        colors = spec["preview"]
        if len(colors) == 2:
            grad = f"linear-gradient(90deg, {colors[0]} 0%, {colors[0]} 50%, {colors[1]} 50%, {colors[1]} 100%)"
        else:
            stops = ", ".join(
                f"{c} {int(100*k/(len(colors)-1))}%" for k, c in enumerate(colors)
            )
            grad = f"linear-gradient(90deg, {stops})"
        var_pills.append(
            f'<button class="pill var-pill" data-var="{spec["id"]}" data-idx="{i}">'
            f'<span class="swatch" style="background: {grad}"></span>'
            f'<span class="pill-label">{html.escape(spec["label"])}</span>'
            f'</button>'
        )

    year_pills = []
    for y in YEARS:
        year_pills.append(
            f'<button class="pill year-pill" data-year="{y}">FY{y}</button>'
        )

    html_out = f"""<!DOCTYPE html>
<html lang="en"><head><meta charset="utf-8">
<title>Interactive CoC Map · CoC Criminalization Project</title>
<style>
:root {{
  --fg: #1a1a1a; --muted: #666; --line: #e5e5e5; --hi: #f7f7f7;
  --accent: #0366d6; --green: #17813c; --red: #c53030;
}}
* {{ box-sizing: border-box; }}
body {{ font-family: -apple-system, system-ui, "Helvetica Neue", sans-serif;
       max-width: 1400px; margin: 0 auto; padding: 1.5em 1.2em 3em;
       color: var(--fg); background: #fafbfc; line-height: 1.55; }}
header.site {{ border-bottom: 1px solid var(--line); padding-bottom: 1em; margin-bottom: 1.2em; }}
header.site .proj {{ color: var(--muted); font-size: 0.82em; letter-spacing: 0.04em; text-transform: uppercase; }}
header.site h1 {{ margin: 0.2em 0; font-size: 1.6em; letter-spacing: -0.01em; }}
nav.site {{ display: flex; gap: 1em; margin-top: 0.4em; flex-wrap: wrap; font-size: 0.92em; }}
nav.site a {{ color: var(--accent); text-decoration: none; }}
nav.site a:hover {{ text-decoration: underline; }}

.map-shell {{ display: grid; grid-template-columns: 1fr 320px; gap: 1.2em; margin-top: 1em; }}
@media (max-width: 900px) {{ .map-shell {{ grid-template-columns: 1fr; }} }}

.controls {{ background: white; border: 1px solid var(--line); border-radius: 10px;
             padding: 1em 1.1em; margin-bottom: 1em; }}
.controls-row {{ display: flex; gap: 0.55em; flex-wrap: wrap; align-items: center;
                 margin-bottom: 0.7em; }}
.controls-row:last-child {{ margin-bottom: 0; }}
.controls-row .label {{ color: var(--muted); font-size: 0.85em; font-weight: 600;
                        letter-spacing: 0.03em; text-transform: uppercase;
                        min-width: 80px; }}
.pill {{ background: white; border: 1px solid var(--line); border-radius: 999px;
         padding: 6px 14px; font-size: 0.92em; font-family: inherit;
         cursor: pointer; display: inline-flex; align-items: center; gap: 7px;
         transition: all 0.15s ease; color: var(--fg); }}
.pill:hover {{ border-color: var(--accent); background: #f5f9ff; }}
.pill.active {{ background: var(--accent); color: white; border-color: var(--accent);
                box-shadow: 0 1px 3px rgba(3,102,214,0.25); }}
.pill.active .swatch {{ border: 1.5px solid rgba(255,255,255,0.6); }}
.pill .swatch {{ display: inline-block; width: 32px; height: 10px; border-radius: 3px;
                 border: 1px solid rgba(0,0,0,0.08); }}
.pill .pill-label {{ white-space: nowrap; }}
.year-pill {{ font-variant-numeric: tabular-nums; font-weight: 500; min-width: 64px;
              justify-content: center; }}

.map-panel {{ background: white; border: 1px solid var(--line); border-radius: 10px;
              padding: 0.6em; }}
.map-title {{ font-size: 1.05em; font-weight: 600; padding: 0.4em 0.6em 0.6em; }}
.map-title .sub {{ display: block; color: var(--muted); font-size: 0.85em; font-weight: 400;
                   margin-top: 2px; }}

.sidebar {{ background: white; border: 1px solid var(--line); border-radius: 10px;
            padding: 1.2em; align-self: start; position: sticky; top: 1em; }}
.sidebar h3 {{ margin: 0 0 0.4em; font-size: 0.85em; color: var(--muted);
               text-transform: uppercase; letter-spacing: 0.05em; font-weight: 600; }}
.sidebar .stats {{ font-variant-numeric: tabular-nums; }}
.sidebar .stats dl {{ display: grid; grid-template-columns: auto 1fr; gap: 0.25em 1em;
                      margin: 0.6em 0; }}
.sidebar .stats dt {{ color: var(--muted); font-size: 0.88em; }}
.sidebar .stats dd {{ margin: 0; font-weight: 600; }}
.sidebar .bigstat {{ font-size: 1.9em; font-weight: 600; line-height: 1; color: var(--fg); }}
.sidebar .bigstat .sub {{ display: block; font-size: 0.55em; color: var(--muted);
                          font-weight: 400; margin-top: 5px; letter-spacing: 0.02em; }}
.mini-hist {{ margin-top: 0.9em; }}
.mini-hist svg {{ width: 100%; height: 70px; }}

.legend-cat {{ display: flex; gap: 1em; margin: 0.6em 0; font-size: 0.9em; }}
.legend-cat .swatch-dot {{ display: inline-block; width: 12px; height: 12px; border-radius: 50%;
                           margin-right: 6px; vertical-align: -2px; }}

.info-footer {{ color: var(--muted); font-size: 0.82em; margin-top: 1em; padding-top: 1em;
                border-top: 1px solid var(--line); }}
</style>
<script src="https://cdn.plot.ly/plotly-2.35.2.min.js"></script>
</head>
<body>

<header class="site">
  <div class="proj">CoC Criminalization &amp; PLE Engagement · Lee &amp; Kim, UCF</div>
  <h1>Interactive CoC map</h1>
  <p style="color: var(--muted); margin: 0.3em 0 0.4em;">
    {n_coc} Continuums of Care · {n_records} CoC-year records · {pct_coded:.0f}% with coded leadership IV
  </p>
  <nav class="site">
    <a href="index.html">← Overview</a>
    <a href="data.html">Data development</a>
    <a href="design.html">Research design</a>
    <a href="results.html">Results</a>
    <a href="descriptive.html">Descriptives</a>
  </nav>
</header>

<div class="controls">
  <div class="controls-row">
    <span class="label">Variable</span>
    {"".join(var_pills)}
  </div>
  <div class="controls-row">
    <span class="label">Year</span>
    {"".join(year_pills)}
  </div>
</div>

<div class="map-shell">
  <div class="map-panel">
    <div class="map-title" id="mapTitle"></div>
    <div id="map" style="width:100%"></div>
  </div>

  <aside class="sidebar">
    <h3>Current view</h3>
    <div class="bigstat" id="bigstat">—<span class="sub"></span></div>
    <div class="stats" id="statsBox"></div>
    <div class="mini-hist" id="miniHist"></div>
    <div id="catLegend"></div>

    <h3 style="margin-top: 1.4em">How to read the map</h3>
    <p style="font-size: 0.88em; color: var(--muted); margin: 0.5em 0;">
      Each dot is a Continuum of Care at its state's centroid plus a stable
      deterministic jitter. <strong>Marker size</strong> encodes CoC size
      (log total beds); <strong>color</strong> encodes the selected variable.
      Color ranges are <em>fixed across years</em>, so the same color means
      the same value in FY22 and FY24.
    </p>

    <div class="info-footer">
      Positions are for visual overview only — not a GIS-accurate CoC boundary map.
      Hover any dot for CoC identifier, leadership, and multi-variable context.
    </div>
  </aside>
</div>

<script>
const VARS = {json.dumps([dict(v, preview=v["preview"]) for v in VARIABLES])};
const YEARS = {json.dumps(YEARS)};
const traces = {json.dumps(traces)};
const stats = {json.dumps(stats)};
const defaultIdx = {default_idx};

let activeVar = VARS[0].id;
let activeYear = 2024;

function indexOf(varId, year) {{
  return stats.findIndex(s => s.variable === varId && s.year === year);
}}

function updateUI(idx) {{
  // Plotly visibility
  const vis = traces.map((_, i) => i === idx);
  Plotly.restyle("map", {{"visible": vis}});

  const s = stats[idx];
  document.getElementById("mapTitle").innerHTML =
    '<strong>' + s.label + '</strong>'
    + ' · FY' + s.year
    + '<span class="sub">' + s.sub + '</span>';

  // Stats box
  const box = document.getElementById("statsBox");
  const big = document.getElementById("bigstat");
  const catLeg = document.getElementById("catLegend");
  catLeg.innerHTML = "";

  // Disable year pills for change view (FY2024 only)
  document.querySelectorAll(".year-pill").forEach(b => {{
    b.disabled = (s.kind === "composite_change" && +b.dataset.year !== 2024);
    b.style.opacity = b.disabled ? 0.35 : 1;
    b.style.cursor = b.disabled ? "not-allowed" : "pointer";
  }});

  if (s.kind === "composite_model") {{
    const su = s.summary;
    big.innerHTML = (su.corr_ple_activity != null ? su.corr_ple_activity.toFixed(3) : "—")
                    + '<span class="sub">corr(PLE, activity) · n = ' + su.n + '</span>';
    box.innerHTML =
      '<dl>' +
      '<dt>Nonprofit CoCs</dt><dd>' + su.nonprofit_n + ' (mean act. ' + (su.mean_activity_nonprofit ?? '—') + ')</dd>' +
      '<dt>Government CoCs</dt><dd>' + su.govt_n + ' (mean act. ' + (su.mean_activity_govt ?? '—') + ')</dd>' +
      '<dt>Δ (NP − Gov)</dt><dd>' + (su.mean_activity_nonprofit != null && su.mean_activity_govt != null
          ? (su.mean_activity_nonprofit - su.mean_activity_govt).toFixed(3) : '—') + '</dd>' +
      '</dl>';
    catLeg.innerHTML =
      '<div style="font-size: 0.88em; color: var(--muted); margin-bottom: 0.3em; font-weight: 600;">Ring color</div>' +
      '<div class="legend-cat">' +
        '<span><span class="swatch-dot" style="background: white; border: 3px solid #17813c; box-sizing: border-box;"></span>Nonprofit-led</span>' +
        '<span><span class="swatch-dot" style="background: white; border: 3px solid #c53030; box-sizing: border-box;"></span>Government-led</span>' +
      '</div>' +
      '<div style="font-size: 0.85em; color: var(--muted); margin-top: 0.8em;">' +
        '<b>Dot size</b> = # PLE in decisionmaking (log-scaled)<br>' +
        '<b>Fill color</b> = anti-crim activity index (red 0 → green 1)' +
      '</div>';
    document.getElementById("miniHist").innerHTML = "";
  }} else if (s.kind === "composite_change") {{
    const su = s.summary;
    if (su.n === 0) {{
      big.innerHTML = '—<span class="sub">' + (su.note || 'no data') + '</span>';
      box.innerHTML = "";
      document.getElementById("miniHist").innerHTML = "";
    }} else {{
      big.innerHTML = (su.mean >= 0 ? '+' : '') + su.mean.toFixed(3)
                      + '<span class="sub">mean Δ · n = ' + su.n + '</span>';
      box.innerHTML =
        '<dl>' +
        '<dt>Median Δ</dt><dd>' + su.median + '</dd>' +
        '<dt>Nonprofit Δ</dt><dd>' + (su.mean_np ?? '—') + '</dd>' +
        '<dt>Government Δ</dt><dd>' + (su.mean_gov ?? '—') + '</dd>' +
        '<dt>DiD (NP − Gov)</dt><dd>' + (su.mean_np != null && su.mean_gov != null
            ? (su.mean_np - su.mean_gov).toFixed(3) : '—') + '</dd>' +
        '<dt>CoCs ↑ / ↓ / =</dt><dd>' + su.pos_count + ' / ' + su.neg_count + ' / ' + su.zero_count + '</dd>' +
        '</dl>';
      renderHist(su.hist_x || [], su.hist_y || []);
    }}
    catLeg.innerHTML =
      '<div style="font-size: 0.88em; color: var(--muted); margin-bottom: 0.3em; font-weight: 600;">Ring color</div>' +
      '<div class="legend-cat">' +
        '<span><span class="swatch-dot" style="background: white; border: 3px solid #17813c; box-sizing: border-box;"></span>Nonprofit</span>' +
        '<span><span class="swatch-dot" style="background: white; border: 3px solid #c53030; box-sizing: border-box;"></span>Government</span>' +
      '</div>';
  }} else if (s.kind === "categorical") {{
    big.innerHTML = s.summary.n + '<span class="sub">CoCs · FY' + s.year + '</span>';
    box.innerHTML =
      '<dl>' +
      '<dt>Nonprofit</dt><dd>' + s.summary.counts.Nonprofit + '</dd>' +
      '<dt>Government</dt><dd>' + s.summary.counts.Government + '</dd>' +
      '</dl>';
    catLeg.innerHTML =
      '<div class="legend-cat">' +
        '<span><span class="swatch-dot" style="background:#17813c"></span>Nonprofit-led</span>' +
        '<span><span class="swatch-dot" style="background:#c53030"></span>Government-led</span>' +
      '</div>';
    document.getElementById("miniHist").innerHTML = "";
  }} else {{
    big.innerHTML = (s.summary.mean != null ? s.summary.mean.toFixed(3) : "—")
                    + '<span class="sub">mean · n = ' + s.summary.n + '</span>';
    box.innerHTML =
      '<dl>' +
      '<dt>Median</dt><dd>' + (s.summary.median ?? '—') + '</dd>' +
      '<dt>SD</dt><dd>' + (s.summary.std ?? '—') + '</dd>' +
      '<dt>Range</dt><dd>' + (s.summary.min ?? '—') + ' — ' + (s.summary.max ?? '—') + '</dd>' +
      '</dl>';
    renderHist(s.summary.hist_x || [], s.summary.hist_y || []);
  }}

  // Active pill state
  document.querySelectorAll(".var-pill").forEach(b => {{
    b.classList.toggle("active", b.dataset.var === s.variable);
  }});
  document.querySelectorAll(".year-pill").forEach(b => {{
    b.classList.toggle("active", +b.dataset.year === s.year);
  }});
}}

function renderHist(xs, ys) {{
  const el = document.getElementById("miniHist");
  if (!ys.length) {{ el.innerHTML = ""; return; }}
  const maxY = Math.max(...ys);
  const w = 280, h = 70, pad = 4;
  const bw = (w - pad * 2) / ys.length;
  let bars = "";
  for (let i = 0; i < ys.length; i++) {{
    const bh = maxY ? (ys[i] / maxY) * (h - 18) : 0;
    const x = pad + i * bw;
    const y = h - bh - 14;
    bars += '<rect x="' + (x + 1) + '" y="' + y + '" width="' + (bw - 2)
            + '" height="' + bh + '" fill="#0366d6" opacity="0.75"></rect>';
  }}
  const xmin = xs[0], xmax = xs[xs.length - 1];
  el.innerHTML =
    '<div style="font-size: 0.78em; color: var(--muted); margin-bottom: 3px;">Distribution</div>' +
    '<svg viewBox="0 0 ' + w + ' ' + h + '" preserveAspectRatio="none">' + bars +
    '<text x="' + pad + '" y="' + (h - 2) + '" font-size="9" fill="#999">' + xmin + '</text>' +
    '<text x="' + (w - pad) + '" y="' + (h - 2) + '" text-anchor="end" font-size="9" fill="#999">' + xmax + '</text>' +
    '</svg>';
}}

document.querySelectorAll(".year-pill").forEach(btn => {{
  btn.addEventListener("click", () => {{
    if (btn.disabled) return;
    activeYear = +btn.dataset.year;
    const idx = indexOf(activeVar, activeYear);
    if (idx >= 0) updateUI(idx);
  }});
}});

// Composite pill: if user clicks "change" view, snap to FY2024 automatically
document.querySelectorAll(".var-pill").forEach(btn => {{
  btn.addEventListener("click", () => {{
    const vid = btn.dataset.var;
    const spec = VARS.find(v => v.id === vid);
    if (spec && spec.kind === "composite_change" && activeYear !== 2024) {{
      activeYear = 2024;
    }}
    activeVar = vid;
    const idx = indexOf(activeVar, activeYear);
    if (idx >= 0) updateUI(idx);
  }});
}}, {{ once: false }});

// Initial render
Plotly.newPlot("map", traces, {json.dumps(layout)}, {{responsive: true, displayModeBar: false}});
const s0 = stats[defaultIdx];
activeVar = s0.variable;
activeYear = s0.year;
updateUI(defaultIdx);
</script>
</body></html>
"""
    OUT_HTML.write_text(html_out)


def main():
    df, traces, stats, layout, default_idx = build_all()
    render(df, traces, stats, layout, default_idx)
    n = df["coc_id"].nunique()
    print(f"wrote {OUT_HTML} ({n} unique CoCs, {len(traces)} traces)")


if __name__ == "__main__":
    main()
