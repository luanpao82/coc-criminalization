"""Generate a coauthor-friendly HTML site for the CoC extraction project.

The goal is narrative clarity — coauthors, not engineers, should be able
to understand what the pipeline did, why each methodological choice was
made, and how to use the resulting dataset.

Pages
-----
  index.html        — The project: what we built and why
  approach.html     — How we built it (methodology, plain language)
  variables.html    — What's in the dataset (searchable variable table)
  dv_story.html     — The DV harmonization problem (deep narrative)
  examples.html     — Real extracted records (AL-500, CA-500, FL-501, NY-600, TX-600)
  using.html        — How to use the data (code recipes)
  data.html         — Data downloads
  limits.html       — What's still missing
  review.html       — Adjudication queue for the PI team

Every page is self-contained HTML + Plotly from CDN. No build step.
Re-run this script after any pipeline change.
"""
from __future__ import annotations

import csv
import datetime as dt
import html
import json
from collections import Counter, defaultdict
from pathlib import Path

import shutil

from pipeline_utils import DATA_DIR, PIPELINE_DIR

SITE_DIR = PIPELINE_DIR.parent / "docs"
SITE_DIR.mkdir(parents=True, exist_ok=True)
DOWNLOADS_DIR = SITE_DIR / "downloads"


# ---------------------------------------------------------------------------
# Downloads — files coauthors can pull from the site
# ---------------------------------------------------------------------------
# (source_path, group, title, description)
DOWNLOADS = [
    # --- Primary analysis dataset ---
    (PIPELINE_DIR / "coc_analysis_ready.xlsx", "primary",
     "coc_analysis_ready.xlsx",
     "Primary analysis file — 4 sheets: balanced_panel (125 CoCs × 3 years), "
     "unbalanced, fy2024_only, variables. Start here."),
    (PIPELINE_DIR / "coc_analysis_ready.csv", "primary",
     "coc_analysis_ready.csv",
     "Same data in long-form CSV — easy to load with pandas/readr."),
    (PIPELINE_DIR / "coc_panel_wide.xlsx", "primary",
     "coc_panel_wide.xlsx",
     "Full wide panel (243 variables × 3 years). Sheets: panel_safe, "
     "full_wide, fy2022, fy2023, fy2024, plus dv_harmonized and narrative_codes."),
    (PIPELINE_DIR / "coc_panel_long.csv", "primary",
     "coc_panel_long.csv",
     "Long form — one row per (CoC, year, field, value). ~164k rows."),
    (PIPELINE_DIR / "harmonized_dv.xlsx", "primary",
     "harmonized_dv.xlsx",
     "Harmonized DV workbook — crim_activity_index, implemented_anticrim_practice, "
     "cell-level 1D-4 indicators across all three years."),

    # --- Data provenance ---
    (PIPELINE_DIR / "file_inventory.csv", "provenance",
     "file_inventory.csv",
     "Source-document index (677 files) with normalized CoC IDs, format, and scan flags."),
    (PIPELINE_DIR / "coc_raw_data.xlsx", "provenance",
     "coc_raw_data.xlsx",
     "Comprehensive raw data file — 677 rows × 331 canonical HUD variables + 3 PLE narrative texts. "
     "Mirrors the manual coc_apps_all_info.xlsx schema but covers all three years, with a schema sheet "
     "showing which variables still need extraction work."),
    (PIPELINE_DIR / "coc_raw_for_coding.xlsx", "provenance",
     "coc_raw_for_coding.xlsx",
     "Coding workbook — 677 CoC-years with 3 PLE narratives + atomic code columns "
     "(bool indicators) + auto-computed composite indices. 18 CoC-years coded in the pilot; "
     "remainder awaiting coauthor review + further coding."),
    (PIPELINE_DIR / "coc_panel_wide_with_ple.xlsx", "primary",
     "coc_panel_wide_with_ple.xlsx",
     "Analytical panel — coc_panel_wide.xlsx + PLE institution indices merged onto the 651 "
     "analytic CoC-years (currently 18 with PLE codes; NaN elsewhere until coding expands)."),
    (PIPELINE_DIR / "panel_field_map.csv", "provenance",
     "panel_field_map.csv",
     "Per-variable panel-safety category (panel_safe / mostly_panel / year_specific / sparse)."),
    (PIPELINE_DIR / "crosswalk.csv", "provenance",
     "crosswalk.csv",
     "FY2024 canonical field ↔ FY2022/FY2023 question-ID mapping."),
    (PIPELINE_DIR / "corpus_diffs.csv", "provenance",
     "corpus_diffs.csv",
     "Review queue — automation vs manual spreadsheet diffs with PDF page citations."),
    (PIPELINE_DIR / "iterations.csv", "provenance",
     "iterations.csv",
     "Extractor iteration ledger — per-iter agreement, top error, fix applied."),
    (PIPELINE_DIR / "extraction_summary.csv", "provenance",
     "extraction_summary.csv",
     "Per-field extraction coverage and validity rates."),

    # --- Independent-variable coding ---
    (PIPELINE_DIR / "iv_leadership.csv", "ivs",
     "iv_leadership.csv",
     "Nonprofit vs government classification per CoC (hand-coded from 1a_2 "
     "Collaborative Applicant Name, 99% coverage)."),
    (PIPELINE_DIR / "iv_county.csv", "ivs",
     "iv_county.csv",
     "CoC → county presidential-vote merge (MIT/tonmcg 2020 county data), "
     "population-weighted to a CoC-level Biden share."),

    # --- Results tables ---
    (PIPELINE_DIR / "multilevel_coefs.csv", "results",
     "multilevel_coefs.csv",
     "Primary spec — multilevel fractional-logit DiD coefficients, "
     "state-clustered SEs, wild-cluster bootstrap p-values."),
    (PIPELINE_DIR / "multilevel_quadrant_means.csv", "results",
     "multilevel_quadrant_means.csv",
     "Four-quadrant (state × county politics) pre/post means used in the trajectory figure."),
    (PIPELINE_DIR / "balanced_sensitivity_coefs.csv", "results",
     "balanced_sensitivity_coefs.csv",
     "Appendix A — balanced-panel sensitivity coefficients (unbalanced vs balanced)."),
    (PIPELINE_DIR / "dv_robustness_coefs.csv", "results",
     "dv_robustness_coefs.csv",
     "Appendix B — alternative DV definitions (full / engagement-only / pre-shock only)."),

    # --- Documentation ---
    (PIPELINE_DIR.parent / "codebook.md", "docs",
     "codebook.md",
     "Variable codebook — 331 canonical fields, controlled vocabulary, observed value domains."),
    (PIPELINE_DIR.parent / "data_construction_methodology.md", "docs",
     "data_construction_methodology.md",
     "Methods-ready protocol (Krippendorff, Cohen, Gilardi et al., Ziems et al. citations)."),
    (PIPELINE_DIR / "multilevel_results.md", "docs",
     "multilevel_results.md",
     "Human-readable writeup of the primary multilevel DiD results."),
    (PIPELINE_DIR / "corpus_agreement.md", "docs",
     "corpus_agreement.md",
     "Extractor vs manual agreement audit — per-category rates and failure modes."),
    (PIPELINE_DIR / "pilot_diff_report.md", "docs",
     "pilot_diff_report.md",
     "Five-CoC pilot iteration trajectory (convergence to ≥98% weighted agreement)."),
    (PIPELINE_DIR.parent / "main_variables.md", "docs",
     "main_variables.md",
     "Operationalization notes for the primary variables used in the regression."),
]


def _human_size(n: int) -> str:
    for unit in ("B", "KB", "MB", "GB"):
        if n < 1024 or unit == "GB":
            return f"{n:.0f} {unit}" if unit == "B" else f"{n:.1f} {unit}"
        n /= 1024
    return f"{n} B"


def copy_downloads() -> list[dict]:
    """Copy every available DOWNLOADS file into site/downloads/ and return metadata."""
    DOWNLOADS_DIR.mkdir(parents=True, exist_ok=True)
    records = []
    for src, group, title, desc in DOWNLOADS:
        if not src.exists():
            continue
        dest = DOWNLOADS_DIR / title
        shutil.copy2(src, dest)
        records.append({
            "href":        f"downloads/{title}",
            "group":       group,
            "title":       title,
            "description": desc,
            "size":        _human_size(dest.stat().st_size),
        })
    return records

# ---------------------------------------------------------------------------
# Shared style + navigation
# ---------------------------------------------------------------------------
STYLE = """
:root {
  --bg: #ffffff; --fg: #1a1a1a; --muted: #666; --accent: #0366d6;
  --line: #e5e5e5; --hi: #f7f7f7; --good: #17813c; --bad: #c53030;
  --warn: #b68400; --panel: #f0f6ff; --callout: #fff9e6;
}
* { box-sizing: border-box; }
body { font-family: Georgia, "Times New Roman", serif;
       max-width: 860px; margin: 0 auto; padding: 2em 1.2em 4em;
       color: var(--fg); background: var(--bg); line-height: 1.7; font-size: 17px; }
header { border-bottom: 2px solid var(--line); padding-bottom: 1.2em; margin-bottom: 2em; }
header .proj { color: var(--muted); font-size: 0.85em; letter-spacing: 0.04em; text-transform: uppercase; }
h1 { margin: 0.3em 0 0.2em; font-size: 2em; letter-spacing: -0.01em; line-height: 1.25; }
h2 { margin-top: 2.5em; padding-bottom: 0.2em; border-bottom: 1px solid var(--line); font-size: 1.5em; }
h3 { margin-top: 2em; font-size: 1.2em; color: #222; }
h4 { margin-top: 1.5em; font-size: 1.02em; color: #333; }
p, li { line-height: 1.7; }
.lead { color: var(--muted); font-size: 1.05em; font-style: italic; }
nav.main { display: flex; gap: 1.2em; margin: 0.6em 0 0; flex-wrap: wrap;
           font-family: -apple-system, system-ui, sans-serif; font-size: 0.92em; }
nav.main a { color: var(--accent); text-decoration: none; }
nav.main a.active { color: var(--fg); font-weight: 600; }
nav.main a:hover { text-decoration: underline; }
table { width: 100%; border-collapse: collapse; margin: 1.2em 0; font-size: 0.93em;
        font-family: -apple-system, system-ui, sans-serif; }
th, td { padding: 7px 11px; border-bottom: 1px solid var(--line); text-align: left; vertical-align: top; }
th { background: var(--hi); font-weight: 600; }
tr:hover { background: #fafafa; }
.num { text-align: right; font-variant-numeric: tabular-nums; }
table.downloads td:first-child { white-space: nowrap; width: 1%; }
table.downloads td:first-child a { font-weight: 500; }
table.downloads td:nth-child(2) { white-space: nowrap; width: 1%; color: var(--muted); }
table.downloads td:last-child { color: var(--muted); }
.badge { display: inline-block; padding: 1px 8px; border-radius: 10px;
         font-size: 0.8em; background: var(--hi); color: var(--muted);
         font-family: -apple-system, system-ui, sans-serif; }
.badge.good { background: #eafaef; color: var(--good); }
.badge.warn { background: #fff7e0; color: var(--warn); }
.badge.bad { background: #fde8e8; color: var(--bad); }
.stat { display: inline-block; background: var(--hi); padding: 0.9em 1.3em;
        border-radius: 6px; margin: 0.3em 0.3em 0.3em 0; min-width: 200px;
        font-family: -apple-system, system-ui, sans-serif; }
.stat .label { color: var(--muted); font-size: 0.82em; margin-bottom: 0.3em; }
.stat .value { font-size: 1.7em; font-weight: 600; color: var(--fg); }
code { background: #f2f2f2; padding: 1px 5px; border-radius: 3px;
       font-family: "SF Mono", Menlo, Consolas, monospace; font-size: 0.88em; }
pre { background: #f5f7fa; padding: 1.2em; border-radius: 6px; overflow-x: auto;
      font-size: 0.87em; line-height: 1.55;
      font-family: "SF Mono", Menlo, Consolas, monospace;
      border-left: 3px solid var(--accent); }
pre code { background: none; padding: 0; }
blockquote { background: var(--callout); border-left: 4px solid #c8a030;
             padding: 0.8em 1.2em; margin: 1.4em 0; border-radius: 0 6px 6px 0; }
blockquote p:first-child { margin-top: 0; }
blockquote p:last-child { margin-bottom: 0; }
.callout { background: var(--panel); border-left: 4px solid var(--accent);
           padding: 0.8em 1.2em; margin: 1.4em 0; border-radius: 0 6px 6px 0; }
.callout-title { font-weight: 600; color: var(--accent); margin-bottom: 0.4em;
                 font-family: -apple-system, system-ui, sans-serif; font-size: 0.95em; }
footer { margin-top: 5em; padding-top: 1.4em; border-top: 1px solid var(--line);
         color: var(--muted); font-size: 0.85em;
         font-family: -apple-system, system-ui, sans-serif; }
.card-row { display: flex; gap: 1em; flex-wrap: wrap; margin: 1em 0;
            font-family: -apple-system, system-ui, sans-serif; }
.card { flex: 1; min-width: 260px; background: var(--hi); padding: 1.2em;
        border-radius: 6px; border: 1px solid var(--line); }
.card h3 { margin: 0 0 0.4em; font-family: Georgia, serif; }
.breadcrumb { font-size: 0.8em; color: var(--muted); margin-bottom: 0.5em;
              font-family: -apple-system, system-ui, sans-serif; }
.breadcrumb a { color: var(--muted); text-decoration: none; }
.breadcrumb a:hover { color: var(--accent); text-decoration: underline; }
.hub-card { display: block; background: white; border: 1px solid var(--line);
            border-radius: 8px; padding: 1.3em 1.4em; text-decoration: none;
            color: inherit; transition: all 0.2s ease; margin-bottom: 0.8em; }
.hub-card:hover { border-color: var(--accent); box-shadow: 0 2px 10px rgba(3,102,214,0.08);
                  transform: translateY(-1px); }
.hub-card h3 { margin: 0 0 0.4em; color: var(--accent); font-family: Georgia, serif; font-size: 1.15em; }
.hub-card p { margin: 0.3em 0 0; color: var(--fg); font-size: 0.95em; line-height: 1.55; }
.hub-card .meta { color: var(--muted); font-size: 0.82em; margin-top: 0.5em;
                  font-family: -apple-system, system-ui, sans-serif; }
.hub-card .num-tag { display: inline-block; width: 1.5em; height: 1.5em;
                     background: var(--accent); color: white; border-radius: 50%;
                     text-align: center; line-height: 1.5em; font-weight: 700;
                     font-size: 0.75em; margin-right: 0.4em;
                     font-family: -apple-system, sans-serif; vertical-align: 2px; }
.hub-grid { display: grid; gap: 0.9em; grid-template-columns: 1fr;
            margin: 1em 0 2em; }
@media (min-width: 700px) { .hub-grid { grid-template-columns: 1fr 1fr; } }
.track { background: var(--hi); border-radius: 8px; padding: 1.1em 1.3em; margin: 0.7em 0; }
.track h3 { margin-top: 0; color: var(--accent); font-family: Georgia, serif; }
.track ol { margin: 0.5em 0; padding-left: 1.3em; }
.findings-box { background: #f0faf3; border-left: 4px solid var(--good);
                padding: 1em 1.3em; border-radius: 0 8px 8px 0; margin: 1.3em 0; }
.findings-box h3 { margin-top: 0; color: var(--good); font-family: Georgia, serif; }
.findings-box ul { margin: 0.4em 0 0; padding-left: 1.3em; }
.card p { font-size: 0.95em; }
.filterbox { margin: 0.8em 0; font-family: -apple-system, system-ui, sans-serif; }
.filterbox input, .filterbox select { padding: 7px 11px; border: 1px solid var(--line);
                                       border-radius: 4px; font-size: 0.95em; }
.filterbox input { width: 360px; }
details > summary { cursor: pointer; color: var(--accent); margin: 0.5em 0;
                    font-family: -apple-system, system-ui, sans-serif; font-size: 0.95em; }
.hint { font-size: 0.88em; color: var(--muted); font-style: italic; }
.quote { background: #f9f6f0; border-left: 3px solid #d6c389;
         padding: 0.7em 1em; margin: 0.8em 0; font-style: italic;
         font-size: 0.93em; border-radius: 0 3px 3px 0; }
.step-list { list-style: none; padding-left: 0; counter-reset: step; }
.step-list > li { counter-increment: step; position: relative; padding: 0.6em 0 0.6em 3em; }
.step-list > li::before { content: counter(step); position: absolute; left: 0; top: 0.7em;
                          width: 2em; height: 2em; border-radius: 50%;
                          background: var(--accent); color: white;
                          text-align: center; line-height: 2em; font-weight: 600;
                          font-family: -apple-system, sans-serif; font-size: 0.9em; }
"""

NAV_ITEMS = [
    ("Overview",                         "index.html"),
    ("Data collection and coding",       "data.html"),
    ("Research design and measurement",  "design.html"),
    ("Descriptive stats",                "descriptive.html"),
    ("Analysis results",                 "results.html"),
]

PAGE_PARENTS: dict = {}


def nav(active: str) -> str:
    links = "".join(
        f'<a class="{"active" if a[1] == active else ""}" href="{a[1]}">{a[0]}</a>'
        for a in NAV_ITEMS
    )
    return f'<nav class="main">{links}</nav>'


def breadcrumb(active: str) -> str:
    return ""


def wrap(title: str, active: str, body: str, subtitle: str = "") -> str:
    head_subtitle = f'<p class="lead">{subtitle}</p>' if subtitle else ""
    return f"""<!DOCTYPE html>
<html lang="en"><head><meta charset="utf-8">
<title>{html.escape(title)} · CoC Criminalization Project</title>
<style>{STYLE}</style>
<script src="https://cdn.plot.ly/plotly-2.35.2.min.js"></script>
</head><body>
<header>
  <div class="proj">CoC Criminalization &amp; PLE Engagement · Lee &amp; Kim, UCF</div>
  {breadcrumb(active)}
  <h1>{html.escape(title)}</h1>
  {head_subtitle}
  {nav(active)}
</header>
{body}
<footer>
  <strong>This site regenerates from the same files the analysis runs on.</strong>
  Last generated {dt.datetime.now().isoformat(timespec='seconds')}.
  Source: <code>data_pipeline/build_site.py</code>. ·
  Authors: Kyungmin Lee &amp; Hanvit Kim (University of Central Florida).
</footer>
</body></html>"""


# ---------------------------------------------------------------------------
# Data loaders
# ---------------------------------------------------------------------------
def load_csv(path: Path) -> list[dict]:
    if not path.exists():
        return []
    with path.open() as f:
        return list(csv.DictReader(f))


def load_inventory():
    return load_csv(PIPELINE_DIR / "file_inventory.csv")


def load_iterations():
    return load_csv(PIPELINE_DIR / "iterations.csv")


def load_field_map():
    return load_csv(PIPELINE_DIR / "panel_field_map.csv")


def load_harmonized():
    return load_csv(PIPELINE_DIR / "harmonized_dv.csv")


def load_corpus_diffs():
    return load_csv(PIPELINE_DIR / "corpus_diffs.csv")


def load_stage1_flagged():
    return load_csv(PIPELINE_DIR / "stage1_flagged.csv")


def load_extraction_summary():
    return load_csv(PIPELINE_DIR / "extraction_summary.csv")


# ---------------------------------------------------------------------------
# Pages
# ---------------------------------------------------------------------------
def page_index():
    inv = load_inventory()
    fm = load_field_map()
    harm = load_harmonized()
    panel_safe_n = sum(1 for r in fm if r["category"] == "panel_safe")

    body = f"""
    <p class="lead">How 325 U.S. Continuums of Care responded to the June
    2024 Supreme Court ruling in <em>Grants Pass v. Johnson</em> — a
    multilevel difference-in-differences built from 677 HUD application
    documents (FY2022–FY2024).</p>

    <div class="findings-box">
      <h3>Headline finding</h3>
      <p style="font-size: 1.05em; margin: 0.3em 0 0.6em;">
      <strong>Local political environment — not CoC governance structure —
      filters federal legal shocks on homelessness criminalization.</strong>
      </p>
      <ul>
        <li><strong>Organizational form doesn't matter.</strong> Nonprofit-led
        vs. government-led CoCs responded identically
        (β = +0.09, wild-cluster bootstrap p = 0.80).</li>
        <li><strong>State political environment does.</strong> Blue-state
        CoCs raised reported anti-criminalization activity more than
        red-state CoCs (β = +0.57, p = 0.095). Within-state county
        variation adds no independent effect.</li>
        <li><strong>The pattern is asymmetric.</strong> Only fully red-state
        × red-county CoCs stayed flat (Δ ≈ −0.03). All three other
        political combinations rose in parallel by +0.11 to +0.14.</li>
      </ul>
    </div>

    <h2>The five sections</h2>
    <div class="hub-grid">
      <a class="hub-card" href="data.html">
        <h3>1 · Data development and cleaning</h3>
        <p>How the 677-document corpus became a three-year CoC panel.
        Extraction pipeline, agreement metrics, and the review queue.</p>
      </a>
      <a class="hub-card" href="design.html">
        <h3>2 · Research design and measurement</h3>
        <p>The multilevel DiD specification, H1 (organizational form) vs
        H2 (political environment) hypotheses, variable construction, and
        the DV measurement-invariance story.</p>
      </a>
      <a class="hub-card" href="descriptive.html">
        <h3>3 · Descriptive stats</h3>
        <p>Grants Pass as the policy shock, year-by-year distributions of
        the anti-criminalization activity index, and which cells of the
        HUD 1D-4 form drove the FY2024 shift.</p>
      </a>
      <a class="hub-card" href="results.html" style="background: #f0faf3; border-color: #17813c;">
        <h3>4 · Analysis results</h3>
        <p>The primary multilevel fractional-logit DiD, the four-quadrant
        political-geography figure, balanced-panel sensitivity, DV
        robustness, and limitations.</p>
      </a>
    </div>

    <h2>Dataset at a glance</h2>
    <div class="card-row">
      <div class="stat"><div class="label">Source documents</div><div class="value">{len(inv)}</div></div>
      <div class="stat"><div class="label">CoC × year records</div><div class="value">{len(harm)}</div></div>
      <div class="stat"><div class="label">Panel-safe variables</div><div class="value">{panel_safe_n}</div></div>
      <div class="stat"><div class="label">Unique CoCs</div><div class="value">325</div></div>
    </div>
    """
    return wrap("CoC responses to Grants Pass v. Johnson",
                "index.html", body,
                "Lee &amp; Kim (UCF) · Multilevel DiD across 325 Continuums of Care, FY2022–FY2024.")


def page_descriptive():
    stats_path = PIPELINE_DIR / "descriptive_stats.json"
    if not stats_path.exists():
        return wrap("Descriptives", "descriptive.html",
                    "<p><em>Run <code>build_descriptive.py</code> first.</em></p>", "")
    stats = json.loads(stats_path.read_text())

    sample = stats["sample"]
    act = stats["activity_index"]
    deltas = stats["deltas"]
    cells = stats["cell_rates"]
    bal = stats["balanced_panel"]

    # Time-series mean line with SE band
    years = ["2022", "2023", "2024"]
    mean_line = {
        "type": "scatter", "mode": "lines+markers+text",
        "x": [f"FY{y}" for y in years],
        "y": [act[y]["overall"]["mean"] for y in years],
        "text": [f"{act[y]['overall']['mean']:.3f}" for y in years],
        "textposition": "top center",
        "name": "Mean", "line": {"width": 3, "color": "#0366d6"},
        "marker": {"size": 10, "color": "#0366d6"},
        "error_y": {
            "type": "data", "visible": True,
            "array": [act[y]["overall"]["se"] * 1.96 for y in years],
            "thickness": 1.5,
        },
    }
    np_line = {
        "type": "scatter", "mode": "lines+markers",
        "x": [f"FY{y}" for y in years],
        "y": [act[y]["nonprofit"]["mean"] for y in years],
        "name": "Nonprofit-led",
        "line": {"width": 2.5, "color": "#17813c", "dash": "solid"},
        "marker": {"size": 9, "color": "#17813c"},
        "error_y": {
            "type": "data", "visible": True,
            "array": [act[y]["nonprofit"]["se"] * 1.96 for y in years],
            "thickness": 1, "color": "#17813c",
        },
    }
    gv_line = {
        "type": "scatter", "mode": "lines+markers",
        "x": [f"FY{y}" for y in years],
        "y": [act[y]["government"]["mean"] for y in years],
        "name": "Government-led",
        "line": {"width": 2.5, "color": "#c53030", "dash": "solid"},
        "marker": {"size": 9, "color": "#c53030"},
        "error_y": {
            "type": "data", "visible": True,
            "array": [act[y]["government"]["se"] * 1.96 for y in years],
            "thickness": 1, "color": "#c53030",
        },
    }
    ts_layout = {
        "title": "Anti-criminalization activity index — yearly means (±1.96·SE)",
        "xaxis": {"title": "Fiscal year"},
        "yaxis": {"title": "Mean index (0–1)", "range": [0.60, 0.90]},
        "height": 420,
        "legend": {"orientation": "h", "y": -0.2},
        "shapes": [{
            "type": "rect", "xref": "x", "yref": "paper",
            "x0": 1.5, "x1": 2.5, "y0": 0, "y1": 1,
            "fillcolor": "#fff4cc", "opacity": 0.35, "line": {"width": 0},
            "layer": "below",
        }],
        "annotations": [{
            "x": 2, "y": 0.96, "xref": "x", "yref": "paper",
            "showarrow": False,
            "text": "Post-Grants Pass · HUD 1D-4 redesign",
            "font": {"color": "#8a6d1f", "size": 11},
        }],
    }

    # Distribution shift — bar chart of FY22 vs FY23 vs FY24
    buckets = ["0.00", "0.17", "0.33", "0.50", "0.67", "0.83", "1.00"]
    # Use activity hist_counts (7 bins from 0 to 1)
    def hist_normalized(year):
        h = act[year]["overall"]["hist_counts"]
        total = sum(h) or 1
        return [round(x / total * 100, 1) for x in h]
    dist_data = [
        {"type": "bar", "name": f"FY{y} (n={act[y]['overall']['n']})",
         "x": buckets, "y": hist_normalized(y),
         "text": [f"{v}%" for v in hist_normalized(y)],
         "textposition": "outside",
         "marker": {"color": {"2022": "#c9c9c9", "2023": "#7fbfff", "2024": "#0366d6"}[y]}}
        for y in years
    ]
    dist_layout = {
        "title": "Distribution of activity index by year (% of CoCs in each bucket)",
        "xaxis": {"title": "Activity index bucket"},
        "yaxis": {"title": "Share of CoCs in that year (%)", "range": [0, 65]},
        "barmode": "group",
        "height": 400,
        "legend": {"orientation": "h", "y": -0.15},
    }

    # Cell heatmap
    heat_rows = []
    heat_z = []
    for cell in cells:
        label = cell["label"]
        heat_rows.append(label)
        row_z = []
        for y in years:
            v = cell["years"][y]["overall"]
            row_z.append(round((v or 0) * 100, 1))
        heat_z.append(row_z)
    heat_data = [{
        "type": "heatmap",
        "z": heat_z,
        "x": [f"FY{y}" for y in years],
        "y": heat_rows,
        "colorscale": [[0, "#fee5d9"], [0.5, "#fcbba1"], [1, "#a50f15"]],
        "zmin": 40, "zmax": 100,
        "text": [[f"{v:.0f}%" for v in row] for row in heat_z],
        "texttemplate": "%{text}",
        "textfont": {"color": "#111"},
        "colorbar": {"title": "Yes %", "thickness": 10, "len": 0.7},
    }]
    heat_layout = {
        "title": "Cell-level Yes rates — which 1D-4 cells drove the FY2024 jump?",
        "xaxis": {"side": "top"},
        "yaxis": {"autorange": "reversed"},
        "height": 360,
        "margin": {"t": 60, "l": 260, "r": 20, "b": 20},
    }

    # Δ bar chart (by leadership × period)
    periods = ["FY22_FY23", "FY23_FY24"]
    delta_data = [
        {"type": "bar", "name": "Nonprofit-led",
         "x": ["FY22 → FY23 (pre-period)", "FY23 → FY24 (post-Grants Pass)"],
         "y": [deltas["nonprofit"][p] for p in periods],
         "text": [f"+{deltas['nonprofit'][p]:.3f}" for p in periods],
         "textposition": "outside",
         "marker": {"color": "#17813c"}},
        {"type": "bar", "name": "Government-led",
         "x": ["FY22 → FY23 (pre-period)", "FY23 → FY24 (post-Grants Pass)"],
         "y": [deltas["government"][p] for p in periods],
         "text": [f"+{deltas['government'][p]:.3f}" for p in periods],
         "textposition": "outside",
         "marker": {"color": "#c53030"}},
    ]
    delta_layout = {
        "title": "Year-over-year change by lead-agency type",
        "yaxis": {"title": "Δ mean activity index", "range": [-0.02, 0.12]},
        "barmode": "group",
        "height": 380,
        "legend": {"orientation": "h", "y": -0.15},
    }

    # Build tables
    def stat_row(label, s):
        if s.get("n", 0) == 0:
            return f"<tr><td>{label}</td>" + "<td class='num'>—</td>" * 7 + "</tr>"
        return (
            f"<tr><td>{label}</td>"
            f"<td class='num'>{s['n']}</td>"
            f"<td class='num'>{s['mean']:.3f}</td>"
            f"<td class='num'>{s['median']:.3f}</td>"
            f"<td class='num'>{s['sd']:.3f}</td>"
            f"<td class='num'>{s['min']:.2f}</td>"
            f"<td class='num'>{s['max']:.2f}</td>"
            f"<td class='num'>{s['at_one']} ({s['at_one']/max(s['n'],1)*100:.0f}%)</td>"
            f"</tr>"
        )

    activity_table = "<table><thead><tr><th>Group / Year</th><th class='num'>N</th><th class='num'>Mean</th><th class='num'>Median</th><th class='num'>SD</th><th class='num'>Min</th><th class='num'>Max</th><th class='num'>At 1.0</th></tr></thead><tbody>"
    for y in years:
        activity_table += f"<tr style='background:#eef4fb'><td colspan='8'><strong>FY{y}</strong></td></tr>"
        activity_table += stat_row("  Overall", act[y]["overall"])
        activity_table += stat_row("  Nonprofit-led", act[y]["nonprofit"])
        activity_table += stat_row("  Government-led", act[y]["government"])
    activity_table += "</tbody></table>"

    # Sample table
    sample_table = """<table><thead><tr><th>Fiscal year</th><th class='num'>Records</th><th class='num'>Unique CoCs</th><th class='num'>IV-coded</th><th class='num'>Nonprofit</th><th class='num'>Government</th><th class='num'>% Nonprofit</th><th class='num'>With DV</th></tr></thead><tbody>"""
    for y in years:
        s = sample[y]
        sample_table += (
            f"<tr><td>FY{y}</td>"
            f"<td class='num'>{s['n_records']}</td>"
            f"<td class='num'>{s['n_cocs']}</td>"
            f"<td class='num'>{s['coded_iv']}</td>"
            f"<td class='num'>{s['nonprofit']}</td>"
            f"<td class='num'>{s['government']}</td>"
            f"<td class='num'>{s['pct_nonprofit']}%</td>"
            f"<td class='num'>{s['with_dv']}</td></tr>"
        )
    sample_table += "</tbody></table>"

    # Delta table
    delta_table = """<table><thead><tr><th>Group</th><th class='num'>FY22 → FY23 (pre)</th><th class='num'>FY23 → FY24 (post-Grants Pass)</th><th class='num'>FY22 → FY24 (total)</th></tr></thead><tbody>"""
    for g in ["overall", "nonprofit", "government"]:
        gl = {"overall": "Overall", "nonprofit": "Nonprofit-led", "government": "Government-led"}[g]
        delta_table += (
            f"<tr><td>{gl}</td>"
            f"<td class='num'>{deltas[g]['FY22_FY23']:+.4f}</td>"
            f"<td class='num'><strong>{deltas[g]['FY23_FY24']:+.4f}</strong></td>"
            f"<td class='num'>{deltas[g]['FY22_FY24']:+.4f}</td></tr>"
        )
    delta_table += "</tbody></table>"

    # Balanced paired sample
    paired = bal["paired"]
    balanced_info = ""
    if paired:
        balanced_info = f"""
    <h2>Paired (within-CoC) changes</h2>
    <p>Restricting to the {paired['n_paired']} CoCs observed in all 3 years —
    the cleanest look at <em>within-CoC</em> change:</p>
    <table>
      <thead><tr><th></th><th class='num'>Mean</th></tr></thead>
      <tbody>
        <tr><td>FY2022 (pre)</td><td class='num'>{paired['mean_FY22']:.3f}</td></tr>
        <tr><td>FY2023 (pre)</td><td class='num'>{paired['mean_FY23']:.3f}</td></tr>
        <tr><td>FY2024 (post-Grants Pass)</td><td class='num'>{paired['mean_FY24']:.3f}</td></tr>
        <tr><td><strong>Mean paired Δ (FY24 − FY23)</strong></td>
            <td class='num'><strong>+{paired['mean_delta_23_24']:.3f}</strong> (SD {paired['sd_delta_23_24']:.3f})</td></tr>
        <tr><td>Share of CoCs that increased</td>
            <td class='num'>{paired['share_increased']*100:.0f}%</td></tr>
        <tr><td>Share that decreased</td>
            <td class='num'>{paired['share_decreased']*100:.0f}%</td></tr>
        <tr><td>Share unchanged</td>
            <td class='num'>{paired['share_unchanged']*100:.0f}%</td></tr>
      </tbody>
    </table>
    <p class="hint">Only {paired['share_increased']*100:.0f}% of CoCs actually
    raised their score FY23→FY24. The +{paired['mean_delta_23_24']:.3f} mean increase
    is driven by a subset making large jumps while {paired['share_unchanged']*100:.0f}%
    stayed exactly the same — a signature consistent with the HUD 1D-4 form
    redesign producing a step-function shift for CoCs that updated their reporting
    practices, rather than a gradual substantive behavior change.</p>
    """

    body = f"""
    <p class="lead">Descriptive statistics for the anti-criminalization
    activity index (<code>crim_activity_index</code>) across FY2022, FY2023,
    and FY2024 — with an explicit view into <em>what</em> shifted after the
    June 2024 Supreme Court ruling in <em>City of Grants Pass v. Johnson</em>.</p>

    <h2>Grants Pass as the policy shock</h2>
    <div class="callout">
      <p><strong><em>City of Grants Pass v. Johnson</em></strong> (603 U.S. ___,
      decided June 28, 2024) held 6–3 that enforcing public-camping ordinances
      against people experiencing homelessness <em>does not</em> constitute
      cruel and unusual punishment under the Eighth Amendment. The decision
      overruled the Ninth Circuit's <em>Martin v. Boise</em> (2019) framework
      that had effectively blocked anti-camping enforcement in nine western
      states when shelter space was unavailable.</p>
      <p>The FY2024 HUD CoC Application deadline was <strong>October 30, 2024</strong> —
      four months after the ruling. FY2024 reports therefore capture CoCs'
      first documented anti-criminalization posture after the legal landscape
      shifted. The design exploits this timing as a quasi-exogenous shock.</p>
    </div>

    <h2>Sample</h2>
    {sample_table}
    <p class="hint">FY2024 is the largest because HUD folded YHDP recipients
    into the main competition that year. Nonprofit/government shares are
    remarkably stable (49% → 50% → 52% nonprofit).</p>

    <h2>Activity index — means over time</h2>
    <div id="ts_chart" style="width:100%"></div>
    <p>The yellow band marks the post-Grants Pass period. Both groups show
    essentially <strong>parallel pre-trends</strong> (FY22 → FY23) followed by
    a <strong>sharp, nearly identical jump</strong> in FY2024.</p>

    <h2>Descriptive table</h2>
    {activity_table}
    <p class="hint">Note the dramatic rise in the "at 1.0" count (all-Yes CoCs):
    55 (39%) in FY2022 → 80 (43%) in FY2023 → <strong>166 (58%)</strong> in FY2024.</p>

    <h2>Year-over-year changes (Δ mean)</h2>
    {delta_table}
    <div id="delta_chart" style="width:100%"></div>
    <p>The pre-period change (FY22 → FY23) was near zero for government-led CoCs
    (+0.003) and modest for nonprofit-led (+0.028). The post-shock change
    (FY23 → FY24) is <strong>nearly identical for both groups</strong>
    (nonprofit +0.085, government +0.082). The difference-in-differences is
    +0.004 — statistically indistinguishable from zero (wild-cluster bootstrap
    p = 0.819). <em>See <a href="results.html">Analysis results</a>
    for the full multilevel DiD.</em></p>

    <h2>Distribution shift</h2>
    <div id="dist_chart" style="width:100%"></div>
    <p>Each bar shows the share of CoCs landing in each discrete value of the
    activity index within a given year. Two things are visible:</p>
    <ul>
      <li>The <strong>0.50 bucket shrinks</strong> in FY2024 (FY22 38% →
      FY23 39% → FY24 15%): fewer CoCs end up at the "half-yes" level.</li>
      <li>The <strong>1.00 (all-Yes) bucket balloons</strong> in FY2024
      (FY22 39% → FY23 43% → FY24 58%): more CoCs report maximal
      anti-criminalization activity.</li>
    </ul>
    <p>This is a <em>bimodal shift</em> — CoCs aren't incrementally adding one
    more Yes; they're jumping from "half" to "all". Consistent with an
    instrument-change story (new FY24 form items are easier to check "Yes" to)
    layered on top of whatever substantive post-Grants Pass response
    exists.</p>

    <h2>Which cells drove the change?</h2>
    <div id="heat_chart" style="width:100%"></div>
    <p>This heatmap reveals the <strong>single most important descriptive
    finding of the paper</strong>: the FY2024 jump in the activity index is
    <strong>almost entirely produced by the three "Implementation" cells</strong>
    (rows 1–3 × column 2), not the "Policymaker engagement" cells.</p>
    <table style="font-size: 0.92em;">
      <thead><tr><th>Cell</th><th class='num'>FY2022</th><th class='num'>FY2023</th><th class='num'>FY2024</th><th class='num'>Δ FY23→24</th></tr></thead>
      <tbody>
        <tr><td>Row 1 · Policymaker engagement</td><td class='num'>97%</td><td class='num'>97%</td><td class='num'>94%</td><td class='num'>−3 pt</td></tr>
        <tr><td>Row 1 · <strong>Implementation</strong></td><td class='num'>47%</td><td class='num'>53%</td><td class='num'><strong>76%</strong></td><td class='num'><strong>+23 pt</strong></td></tr>
        <tr><td>Row 2 · Policymaker engagement</td><td class='num'>96%</td><td class='num'>96%</td><td class='num'>94%</td><td class='num'>−2 pt</td></tr>
        <tr><td>Row 2 · <strong>Implementation</strong></td><td class='num'>50%</td><td class='num'>52%</td><td class='num'><strong>67%</strong></td><td class='num'><strong>+15 pt</strong></td></tr>
        <tr><td>Row 3 · Policymaker engagement</td><td class='num'>91%</td><td class='num'>93%</td><td class='num'>93%</td><td class='num'>0 pt</td></tr>
        <tr><td>Row 3 · <strong>Implementation</strong></td><td class='num'>46%</td><td class='num'>46%</td><td class='num'><strong>64%</strong></td><td class='num'><strong>+18 pt</strong></td></tr>
      </tbody>
    </table>
    <p><strong>Why this matters for interpretation:</strong> the
    "Implementation" column was labeled differently in each form:</p>
    <ul>
      <li>FY2022/23: "Reverse existing criminalization policies" (what you must <em>have undone</em>)</li>
      <li>FY2024: "Implemented Laws/Policies/Practices that Prevent Criminalization" (what you have <em>implemented</em>)</li>
    </ul>
    <p>FY2024's wording is substantially easier to check "Yes" to — any
    adopted policy, even one existing for years, qualifies. FY2022/23's
    wording required evidence that an <em>existing criminalization policy was
    reversed</em>, which is much more stringent. This is why the jump is
    concentrated entirely in column 2 and why we reach this conclusion:</p>

    <div class="callout">
      <div class="callout-title">What we're actually observing</div>
      <p>The +0.083 FY23→FY24 jump in the overall activity index is
      <strong>partly an instrument artifact</strong>, <strong>partly a real
      response</strong> to Grants Pass, and in any case
      <strong>affects nonprofit-led and government-led CoCs equivalently</strong>.
      The "Policymaker engagement" column — which asked essentially the same
      question across all three years — actually <em>declined slightly</em>
      in FY2024 (~3-point drop). The increase is concentrated in the
      "Implementation" column, whose wording changed in ways that mechanically
      make "Yes" easier to report.</p>
      <p>This is why the paper should:</p>
      <ol>
        <li>Report cell-level descriptives to make the instrument effect transparent;</li>
        <li>Rely on DiD (which differences out common shifts) rather than raw year-on-year comparisons;</li>
        <li>Treat the DiD null as the primary finding — <em>both groups moved identically</em>,
        so even after the instrument change, leadership type does not predict differential response.</li>
      </ol>
    </div>

    {balanced_info}

    <h2>Bottom line</h2>
    <ul>
      <li><strong>Pre-period (FY22 → FY23):</strong> roughly stable activity index, with nearly
      parallel trajectories for nonprofit and government CoCs.</li>
      <li><strong>Post-Grants Pass (FY23 → FY24):</strong> both groups jump by
      ~0.08 points. The jump is <em>concentrated in the "Implementation" cells</em>
      whose wording changed to be easier to check Yes.</li>
      <li><strong>No differential response</strong> by lead-agency type
      (DiD ≈ 0, p<sub>boot</sub> = 0.819). The theoretical prediction that
      nonprofit-led CoCs should more aggressively reject criminalization is
      not supported.</li>
      <li><strong>The descriptive story is consistent with — but does not
      prove — an instrument-change interpretation.</strong> External behavioral
      data (NLHR ordinance counts, FBI UCR vagrancy arrests) are the next step
      to validate whether the FY2024 jump reflects real behavior change.</li>
    </ul>

    <script>
    Plotly.newPlot("ts_chart", {json.dumps([mean_line, np_line, gv_line])},
                   {json.dumps(ts_layout)}, {{responsive: true}});
    Plotly.newPlot("dist_chart", {json.dumps(dist_data)},
                   {json.dumps(dist_layout)}, {{responsive: true}});
    Plotly.newPlot("delta_chart", {json.dumps(delta_data)},
                   {json.dumps(delta_layout)}, {{responsive: true}});
    Plotly.newPlot("heat_chart", {json.dumps(heat_data)},
                   {json.dumps(heat_layout)}, {{responsive: true}});
    </script>
    """
    return wrap("Descriptives & Grants Pass", "descriptive.html", body,
                "How the anti-criminalization index moved year-to-year, and what that tells us about the 2024 Supreme Court ruling.")


def page_main_results():
    """Primary multilevel DiD page with 4-quadrant key figure."""
    coefs = load_csv(PIPELINE_DIR / "multilevel_coefs.csv")
    quad = load_csv(PIPELINE_DIR / "multilevel_quadrant_means.csv")
    if not coefs or not quad:
        return wrap("Main results", "main_results.html",
                    "<p><em>Run <code>run_multilevel.py</code> first.</em></p>", "")

    def to_float(x):
        try: return float(x)
        except (ValueError, TypeError): return None

    # --- Quadrant trajectory data ---
    quadrants = [
        "Red state × Red county",
        "Red state × Blue county",
        "Blue state × Red county",
        "Blue state × Blue county",
    ]
    colors = {
        "Red state × Red county": "#c53030",
        "Red state × Blue county": "#d69e2e",
        "Blue state × Red county": "#3182ce",
        "Blue state × Blue county": "#17813c",
    }
    trajectory_traces = []
    for q in quadrants:
        xs, ys, ses, ns = [], [], [], []
        for yr in (2022, 2023, 2024):
            row = next((r for r in quad if r["quadrant"] == q and int(r["year"]) == yr), None)
            if row:
                xs.append(f"FY{yr}")
                ys.append(to_float(row["mean"]))
                ses.append(to_float(row["se"]))
                ns.append(int(float(row["count"])))
        is_red_red = (q == "Red state × Red county")
        trajectory_traces.append({
            "type": "scatter", "mode": "lines+markers+text",
            "name": f"{q} (n≈{ns[-1] if ns else '?'})",
            "x": xs, "y": ys,
            "error_y": {"type": "data", "array": [s * 1.96 for s in ses], "visible": True},
            "text": [f"{v:.3f}" for v in ys], "textposition": "top center",
            "marker": {"size": 11, "color": colors[q],
                       "symbol": "diamond" if is_red_red else "circle"},
            "line": {"width": 4 if is_red_red else 2.5,
                     "color": colors[q],
                     "dash": "solid"},
        })
    trajectory_layout = {
        "title": "Anti-criminalization activity index by 2×2 political quadrant (mean ± 1.96·SE)",
        "xaxis": {"title": "Fiscal year",
                  "categoryorder": "array",
                  "categoryarray": ["FY2022", "FY2023", "FY2024"]},
        "yaxis": {"title": "Mean activity index (0–1)", "range": [0.55, 0.92]},
        "height": 500,
        "shapes": [{
            "type": "rect", "xref": "x", "yref": "paper",
            "x0": 1.5, "x1": 2.5, "y0": 0, "y1": 1,
            "fillcolor": "#fff4cc", "opacity": 0.35, "line": {"width": 0},
            "layer": "below",
        }],
        "annotations": [
            {"x": 2, "y": 0.89, "xref": "x", "yref": "paper",
             "showarrow": False,
             "text": "Post-Grants Pass (June 2024)",
             "font": {"color": "#8a6d1f", "size": 12}},
            {"x": "FY2024", "y": 0.751, "xref": "x", "yref": "y",
             "showarrow": True, "arrowhead": 2, "arrowcolor": "#c53030",
             "ax": 60, "ay": 40,
             "text": "<b>Only Red×Red stays flat</b><br>(Δ = −0.031)",
             "font": {"color": "#c53030", "size": 11},
             "bgcolor": "rgba(255,255,255,0.9)",
             "bordercolor": "#c53030"},
        ],
        "legend": {"orientation": "h", "y": -0.2},
    }

    # --- Coefficient table ---
    from collections import defaultdict
    by_panel = defaultdict(dict)
    for r in coefs:
        b = to_float(r["coef"]); s = to_float(r["se"])
        p = to_float(r["pvalue"]); p_boot = to_float(r["bootstrap_p"])
        if b is None: continue
        by_panel[r["panel"]][r["variable"]] = (b, s, p, p_boot)

    label_map = {
        "nonprofit_led": "Nonprofit-led (IV)",
        "blue_state": "Blue state",
        "biden_within_state": "Biden-within-state (county − state mean)",
        "post": "Post-Grants Pass",
        "did_np": "Nonprofit × Post",
        "did_blue": "<strong>Blue state × Post</strong>",
        "did_within": "Biden-within × Post",
        "hf_pct": "Housing First adoption",
        "hmis_cov": "HMIS ES coverage",
        "log_beds": "log(total beds + 1)",
        "ple_ces_bin": "PLE in CES (binary)",
        "hf_pct_bar": "[Mundlak] HF mean",
        "hmis_cov_bar": "[Mundlak] HMIS mean",
        "log_beds_bar": "[Mundlak] log beds mean",
        "ple_ces_bin_bar": "[Mundlak] PLE mean",
        "const": "(Intercept)",
    }
    # Order: key variables first
    all_vars = [
        "nonprofit_led", "blue_state", "biden_within_state",
        "post", "did_np", "did_blue", "did_within",
        "hf_pct", "hmis_cov", "log_beds", "ple_ces_bin",
        "hf_pct_bar", "hmis_cov_bar", "log_beds_bar", "ple_ces_bin_bar",
        "const",
    ]

    def _is_valid(x):
        return x is not None and not (isinstance(x, float) and x != x)  # not None and not NaN

    def cell(panel, v):
        d = by_panel.get(panel, {}).get(v)
        if not d: return "—"
        b, s, p, p_b = d
        star = ""
        if v.startswith("did_") and _is_valid(p_b):
            if p_b < 0.01: star = "***"
            elif p_b < 0.05: star = "**"
            elif p_b < 0.10: star = "*"
        elif _is_valid(p):
            if p < 0.01: star = "***"
            elif p < 0.05: star = "**"
            elif p < 0.10: star = "*"
        cell_str = f"{b:+.3f}{star}"
        if s: cell_str += f"<br><span class='hint'>({s:.3f})</span>"
        if v.startswith("did_") and _is_valid(p_b):
            cell_str += f"<br><span class='hint'>p_boot = {p_b:.3f}</span>"
        return cell_str

    rows_html = []
    for v in all_vars:
        tds = [label_map.get(v, v), cell("unbalanced", v), cell("balanced", v)]
        rows_html.append("<tr>" + "".join(f"<td>{x}</td>" for x in tds) + "</tr>")
    coef_table = (
        "<table style='font-size: 0.9em'>"
        "<thead><tr><th>Variable</th>"
        "<th>Unbalanced (n=594)</th><th>Balanced (n=341)</th></tr></thead>"
        f"<tbody>{''.join(rows_html)}</tbody></table>"
    )

    # --- Quadrant Δ bar chart ---
    quad_deltas = []
    for q in quadrants:
        fy23 = next((r for r in quad if r["quadrant"] == q and int(r["year"]) == 2023), None)
        fy24 = next((r for r in quad if r["quadrant"] == q and int(r["year"]) == 2024), None)
        if fy23 and fy24:
            delta = to_float(fy24["mean"]) - to_float(fy23["mean"])
            quad_deltas.append({"q": q, "d": delta, "n24": int(float(fy24["count"]))})
    delta_data = [{
        "type": "bar",
        "x": [d["q"] for d in quad_deltas],
        "y": [d["d"] for d in quad_deltas],
        "marker": {"color": [colors[d["q"]] for d in quad_deltas]},
        "text": [f"{d['d']:+.3f}<br>(n={d['n24']})" for d in quad_deltas],
        "textposition": "outside",
    }]
    delta_layout = {
        "title": "FY2023 → FY2024 change (Δ) by quadrant",
        "yaxis": {"title": "Δ mean activity index", "range": [-0.06, 0.18]},
        "xaxis": {"title": ""},
        "height": 360,
        "showlegend": False,
        "shapes": [{"type": "line", "xref": "paper", "yref": "y",
                    "x0": 0, "x1": 1, "y0": 0, "y1": 0,
                    "line": {"color": "#666", "width": 1, "dash": "dot"}}],
    }

    # --- Forest plot: DiD terms across panels ---
    did_terms = [
        ("did_np", "Nonprofit × Post"),
        ("did_blue", "Blue state × Post"),
        ("did_within", "Biden-within × Post"),
    ]
    forest_traces = []
    for label_panel in ("unbalanced", "balanced"):
        xs, ys, errs, texts = [], [], [], []
        for vid, lbl in did_terms:
            d = by_panel.get(label_panel, {}).get(vid)
            if d:
                b, s, _, p_b = d
                xs.append(b); ys.append(lbl); errs.append(1.96 * s)
                texts.append(f"p_boot={p_b:.3f}" if p_b else "")
        forest_traces.append({
            "type": "scatter", "mode": "markers+text",
            "name": label_panel.capitalize(),
            "x": xs, "y": ys,
            "error_x": {"type": "data", "array": errs, "visible": True, "thickness": 1.5},
            "text": texts, "textposition": "top right", "textfont": {"size": 9},
            "marker": {"size": 12},
        })
    forest_layout = {
        "title": "DiD coefficients across panels (95% CI)",
        "xaxis": {"title": "Coefficient (logit scale)",
                  "zeroline": True, "zerolinecolor": "#c53030", "zerolinewidth": 2},
        "yaxis": {"autorange": "reversed"},
        "height": 300,
        "margin": {"l": 180, "r": 30, "t": 50, "b": 40},
        "legend": {"orientation": "h", "y": -0.25},
    }

    # --- Narrative ---
    np_est = by_panel.get("unbalanced", {}).get("did_np")
    blue_est = by_panel.get("unbalanced", {}).get("did_blue")
    within_est = by_panel.get("unbalanced", {}).get("did_within")

    def tell(c, use_boot=True):
        if not c: return "(n/a)"
        b, s, p, pb = c
        p_ref = pb if (use_boot and pb is not None) else p
        star = ""
        if p_ref is not None:
            if p_ref < 0.01: star = "***"
            elif p_ref < 0.05: star = "**"
            elif p_ref < 0.10: star = "*"
        return f"β = {b:+.3f}{star} (bootstrap p = {pb:.3f})" if pb else f"β = {b:+.3f}{star}"

    body = f"""
    <p class="lead">The primary specification for the paper — a multilevel
    difference-in-differences that decomposes political environment into
    state-level and within-state county components, estimated jointly with
    the governance treatment.</p>

    <h2>The key figure</h2>
    <div id="trajectory" style="width:100%"></div>
    <p class="hint">CoCs are grouped into 2×2 quadrants based on their state's
    2020 presidential winner and whether their county's Biden share exceeds 50%.
    Three of four quadrants rose in parallel after <em>Grants Pass v. Johnson</em>;
    only the red-state × red-county group stayed flat.</p>

    <div class="findings-box">
      <h3>What this shows in one sentence</h3>
      <p style="font-size: 1.05em;">
      <strong>Only CoCs embedded in fully red-leaning political environments
      (state AND county) did not expand their reported anti-criminalization
      activity after Grants Pass.</strong> All three other political
      combinations rose by +0.11 to +0.14 points, converging to a similar
      FY2024 level (0.75–0.87).
      </p>
    </div>

    <h2>Model specification</h2>

    <h3>Why multilevel</h3>
    <p>Two political measures — state-level binary (Biden won 2020) and
    county-level Biden share — are highly correlated because a county
    tends to be blue partly because its state is. Putting both in the
    same model directly produces collinearity. We apply a
    Mundlak-style decomposition at the multilevel structure:</p>
    <pre><code>state_mean_biden   = mean Biden share of counties in the state
biden_within_state = county_biden_share − state_mean_biden</code></pre>
    <p>After this decomposition, <code>blue_state</code> captures the
    state-level political environment and <code>biden_within_state</code>
    captures <em>purely</em> within-state county deviation. They are
    statistically orthogonal, so we can estimate both effects in the same
    regression.</p>

    <h3>Primary specification</h3>
    <pre><code>crim_activity_index<sub>it</sub> =
      β₁ · Nonprofit<sub>i</sub>
    + β₂ · Blue_state<sub>i</sub>
    + β₃ · Biden_within_state<sub>i</sub>
    + β₄ · Post<sub>t</sub>
    + β₅ · Nonprofit × Post                ← governance DiD
    + β₆ · Blue_state × Post               ← state-level political DiD
    + β₇ · Biden_within_state × Post       ← within-state county DiD
    + γ · Controls<sub>it</sub> (Mundlak-adjusted)
    + ε<sub>it</sub></code></pre>

    <p><strong>Estimator:</strong> Papke-Wooldridge fractional logit for the
    bounded DV [0,1]. <strong>Standard errors:</strong> state-level
    cluster-robust, reinforced with wild-cluster bootstrap (Rademacher
    weights, state-clustered, 999 replicates). <strong>Sample:</strong>
    unbalanced panel as primary (preserves 651 CoC-years across 51 states),
    balanced 3-year panel as robustness.</p>

    <h2>Coefficient table</h2>
    {coef_table}
    <p class="hint">Cluster-robust SE at the state level in parentheses.
    Significance stars on DiD terms use wild-cluster bootstrap p-values;
    on main effects use cluster-robust p. <code>*** p&lt;0.01, ** p&lt;0.05,
    * p&lt;0.10</code>.</p>

    <h2>Forest plot — DiD terms</h2>
    <div id="forest" style="width:100%"></div>
    <p class="hint">The three DiD coefficients (governance, state political
    environment, within-state county deviation) side by side on both
    panels. Whiskers cross zero for Nonprofit × Post and Biden-within × Post;
    only Blue-state × Post approaches significance.</p>

    <h2>Quadrant Δ (FY2023 → FY2024)</h2>
    <div id="delta_bar" style="width:100%"></div>

    <h2>Reading the results</h2>

    <h3>1. Governance does not matter</h3>
    <p>Nonprofit × Post: {tell(np_est)}. Across both panels the nonprofit
    coefficient is indistinguishable from zero. The theoretical prediction
    that nonprofit-led CoCs should be more rights-responsive is not
    supported.</p>

    <h3>2. State-level political environment matters (marginally)</h3>
    <p>Blue-state × Post: {tell(blue_est)}. Significant at the 10%
    level in the unbalanced panel, weaker in the balanced sample.
    <strong>This is the paper's key positive finding, subject to the
    balanced-panel caveat.</strong></p>

    <h3>3. Within-state county variation adds nothing</h3>
    <p>Biden-within × Post: {tell(within_est)}. Once state-level
    environment is controlled, the additional county deviation does not
    explain response. <strong>The earlier county-level finding (β = +1.95
    in isolation) was primarily picking up between-state variation, not
    within-state.</strong></p>

    <h3>4. The asymmetric quadrant pattern</h3>
    <p>The quadrant decomposition reveals the <em>shape</em> of the
    political-environment effect. It is not simply "blue areas respond
    more" — it is "<strong>red-state × red-county is the outlier that
    doesn't respond, while all other political combinations respond
    similarly</strong>". This OR-shaped pattern is more consistent with
    a threshold story than a linear dose-response.</p>

    <h2>Interpretation — what does "red-state × red-county doesn't respond" mean?</h2>

    <div class="callout">
      <div class="callout-title">A nuance worth spelling out</div>
      <p><strong>"Not responding"</strong> here means the activity index
      did not rise FY23 → FY24 (actually declined slightly). It does
      <em>not</em> mean red-state × red-county CoCs have low activity
      overall — they were at 0.782 in FY2023, the highest of any
      quadrant at that point. After Grants Pass they held steady at
      0.751 while the three other quadrants converged upward to
      0.75–0.87.</p>
      <p>Three candidate mechanisms, all consistent with the data:</p>
      <ul>
        <li><strong>Ceiling:</strong> Red-red CoCs were already at a high
        baseline; limited room to expand.</li>
        <li><strong>Political demand:</strong> Fully red environments
        provide no constituency-level pressure to reframe toward
        rights-responsive anti-criminalization; the Grants Pass ruling
        signals "the law is on our side" and requires no defensive
        repositioning.</li>
        <li><strong>Reporting strategy:</strong> CoCs in red environments
        may deliberately avoid foregrounding anti-criminalization framing
        in the new FY2024 form language.</li>
      </ul>
    </div>

    <h2>Sample sizes by quadrant (FY2024)</h2>
    <table>
      <thead><tr><th>Quadrant</th><th class='num'>n</th></tr></thead>
      <tbody>
        <tr><td>Blue state × Blue county</td><td class='num'>131</td></tr>
        <tr><td>Red state × Red county</td><td class='num'>75</td></tr>
        <tr><td>Blue state × Red county</td><td class='num'>50</td></tr>
        <tr><td>Red state × Blue county</td><td class='num'>26</td></tr>
      </tbody>
    </table>
    <p class="hint">The smallest cell (red state × blue county, n = 26)
    has wide confidence intervals. Interpret the quadrant effect sizes
    with this power constraint in mind.</p>

    <h2>Limitations of this primary specification</h2>
    <ol>
      <li><strong>Marginal significance.</strong> The state-level DiD is
      at bootstrap p ≈ 0.095 — meets a 10% threshold, not 5%. External
      behavioral data would strengthen the inference.</li>
      <li><strong>Balanced-panel weakening.</strong> See
      <a href="balanced.html">Balanced vs Unbalanced</a>. Balanced-panel
      results are weaker; the unbalanced-panel significance may reflect
      sample composition (FY2024 adds ~126 YHDP CoCs potentially
      concentrated in blue states).</li>
      <li><strong>DV self-report.</strong> The DV is a CoC's own
      reporting on HUD Form 1D-4, not an external behavioral measure.
      See <a href="dv_story.html">The DV story</a> and
      <a href="dv_robust.html">DV robustness</a>.</li>
      <li><strong>Short post-period.</strong> FY2024 applications were
      submitted four months after the Supreme Court ruling; longer-run
      behavior may differ.</li>
      <li><strong>Quadrant sample imbalance.</strong> Red state × Blue
      county has only 26 observations in FY2024, limiting the precision
      of that cell's estimate.</li>
    </ol>

    <h2>Reproduce</h2>
    <pre><code>cd data_pipeline
python3 code_iv_leadership.py         # nonprofit_led classification
python3 build_coc_county.py           # CoC → county Biden share
python3 run_multilevel.py             # primary specification + bootstrap
python3 build_site.py                 # regenerate this page</code></pre>

    <script>
    Plotly.newPlot("trajectory", {json.dumps(trajectory_traces)},
                   {json.dumps(trajectory_layout)}, {{responsive:true}});
    Plotly.newPlot("forest", {json.dumps(forest_traces)},
                   {json.dumps(forest_layout)}, {{responsive:true}});
    Plotly.newPlot("delta_bar", {json.dumps(delta_data)},
                   {json.dumps(delta_layout)}, {{responsive:true}});
    </script>
    """
    return wrap("Main results — Multilevel DiD", "main_results.html", body,
                "The paper's primary specification: multilevel fractional-logit DiD with state-clustered SEs.")


# ---------------------------------------------------------------------------
# Consolidated top-level pages (5-section structure)
# ---------------------------------------------------------------------------
def page_data_development(download_records=None):
    inv = load_inventory()
    iters = load_iterations()
    fm = load_field_map()
    harm = load_harmonized()
    diffs = load_corpus_diffs()
    stage1_flagged = load_stage1_flagged()
    download_records = download_records or []

    by_year = Counter(r["year"] for r in inv)
    panel_safe_n = sum(1 for r in fm if r["category"] == "panel_safe")
    last_iter = iters[-1] if iters else {}
    wacc = float(last_iter.get("weighted_acc", 0) or 0)
    aacc = float(last_iter.get("adjusted_acc", 0) or 0) if last_iter.get("adjusted_acc") else None

    # Pipeline coverage stats computed live
    raw_path = PIPELINE_DIR / "coc_raw_data.xlsx"
    coding_path = PIPELINE_DIR / "coc_raw_for_coding.xlsx"
    panel_path = PIPELINE_DIR / "coc_panel_wide_with_ple.xlsx"
    codes_jsonl = PIPELINE_DIR / "drafts" / "pilot_ple_codes.jsonl"
    n_coded = 0
    if codes_jsonl.exists():
        codes_keys = set()
        for line in codes_jsonl.open():
            try:
                r = json.loads(line)
                codes_keys.add((r["coc_id"], int(r["year"])))
            except Exception:
                continue
        n_coded = len(codes_keys)

    mismatches = [d for d in diffs if d.get("manual_value") and d.get("auto_value")]
    autofills  = [d for d in diffs if not d.get("manual_value") and d.get("auto_value")]
    downloads_html = _downloads_block(download_records)

    body = f"""
    <p class="lead">This page walks coauthors through the four stages of
    data construction for this study: from the 677 HUD CoC Consolidated
    Application documents, to a comprehensive raw-data file, to the
    narrative-coding workbook, to the analytical panel used in the
    regressions.</p>

    <div style="background:#f6f8fa;border-left:4px solid #4c5fd5;padding:1em 1.2em;margin:1em 0;">
      <strong>Pipeline at a glance.</strong>
      <pre style="background:transparent;padding:0;margin:0.6em 0 0 0;font-size:0.9em;line-height:1.5;">
<b>Stage 1.</b> 677 source PDFs/DOCX            →  <b>coc_raw_data.xlsx</b>
              (all HUD form fields as columns; structured data filled)

<b>Stage 2.</b> + text slicing of 3 PLE narratives
              (research-used variables; embedded in raw file)

<b>Stage 3.</b> coc_raw_data → <b>coc_raw_for_coding.xlsx</b>
              (Claude reads narratives → atomic codes → composite indices)
              <span style="color:#b7791f">↳ awaiting coauthor review (18 CoC-years coded)</span>

<b>Stage 4.</b> raw + coded indices → <b>coc_panel_wide_with_ple.xlsx</b>
              (651 CoC-years × variables needed for the regression)</pre>
    </div>

    <h2>1 · Source corpus</h2>
    <div class="card-row">
      <div class="stat"><div class="label">FY2022 applications</div><div class="value">{by_year.get("2022", 0)}</div></div>
      <div class="stat"><div class="label">FY2023 applications</div><div class="value">{by_year.get("2023", 0)}</div></div>
      <div class="stat"><div class="label">FY2024 applications</div><div class="value">{by_year.get("2024", 0)}</div></div>
      <div class="stat"><div class="label">Total documents</div><div class="value">{len(inv)}</div></div>
    </div>
    <p class="hint">FY2024 is the largest year because HUD folded the
    Youth Homeless Demonstration Program (YHDP) into the main competition.
    Eight CoCs submit DOCX instead of PDF; a handful require OCR and are
    flagged rather than silently dropped.</p>

    <h2 id="stage1">Stage 1 · Automated PDF → comprehensive raw data file</h2>
    <p><strong>Goal:</strong> produce a single data file that mirrors the
    manually-coded <code>coc_apps_all_info.xlsx</code> but extends coverage
    from FY2024-only (hand-coded by the RA team) to all three years, and
    captures <em>every</em> HUD CoC Application field as a column — even
    the ones this study does not yet use.</p>

    <p><strong>Output:</strong>
    <a href="downloads/coc_raw_data.xlsx" download><code>coc_raw_data.xlsx</code></a>
    (677 rows × 348 columns; ~2&nbsp;MB).</p>

    <ul>
      <li><strong>Row universe:</strong> one row per source document in
      <code>file_inventory.csv</code> — every PDF or DOCX that a CoC
      submitted across FY2022, FY2023, and FY2024.</li>
      <li><strong>Column schema:</strong> the 331 canonical HUD variables
      from <code>codebook.md</code>, in PDF question order
      (1A → 1B → 1C → 1D → 1E → 2A → 2B → 2C → 3A → 3B → 4A), plus 9
      meta columns and 8 completeness/PLE-status columns.</li>
      <li><strong>Extractor:</strong> format-aware adapters
      (<code>extract_pdf_native.py</code>, <code>extract_docx.py</code>)
      with an <em>anchor-then-parse</em> rule — every question is located
      by its <code>1B-1.</code>/<code>1D-4.</code>-style anchor, and only
      the local block is parsed. A failure in one block cannot corrupt
      neighboring variables. Categorical outputs are validated against
      the codebook's controlled vocabularies; out-of-vocab values are
      flagged rather than coerced.</li>
      <li><strong>Cross-year harmonization:</strong> FY2024 field IDs are
      canonical. FY2022/23 content is crosswalked into the same columns
      where the construct is equivalent (see <code>crosswalk.csv</code>
      and <code>panel_field_map.csv</code>).</li>
    </ul>

    <div class="card-row">
      <div class="stat"><div class="label">Canonical variables</div><div class="value">331</div></div>
      <div class="stat"><div class="label">Weighted agreement vs manual</div><div class="value">{wacc:.1%}</div></div>
      {f'<div class="stat"><div class="label">Adjusted (manual-error removed)</div><div class="value">{aacc:.1%}</div></div>' if aacc else ""}
      <div class="stat"><div class="label">Panel-safe variables</div><div class="value">{panel_safe_n}</div></div>
    </div>

    <p><strong>Reviewer guide:</strong> open the workbook and start with
    the <code>schema</code> sheet. Green rows are PLE-relevant fields
    with text populated. Red rows are canonical variables whose columns
    are present but not yet filled — they define the roadmap for future
    extraction waves. Each row reports <code>n_populated</code> and
    <code>pct_populated</code> across the 677-document corpus so you can
    see at a glance which fields need work next.</p>

    {_stage1_flagged_block(stage1_flagged)}

    <h2 id="stage2">Stage 2 · Text extraction for research-used variables</h2>
    <p><strong>Goal:</strong> populate free-text narrative cells for the
    variables this study measures. Doing Stage-2 narrative coding for
    all 24 narrative variables in the codebook is a large undertaking;
    we scoped text extraction to the three People with Lived Experience
    (PLE) engagement questions because they are the study's primary IV.</p>

    <p><strong>Fields extracted:</strong></p>
    <ul>
      <li><code>1d_10</code> — <em>Involving PLE in Service Delivery
      and Decisionmaking</em> (FY2024 anchor; FY2022/23 equivalent at
      <code>1d_11</code>, crosswalked in)</li>
      <li><code>1d_10b</code> — <em>Professional Development and
      Employment Opportunities for PLE</em></li>
      <li><code>1d_10c</code> — <em>Routinely Gathering Feedback and
      Addressing Challenges of PLE</em></li>
    </ul>

    <p><strong>Method:</strong> year-branched regex anchors
    (<code>anchors_by_year</code> in <code>extract_narrative.py</code>)
    with a 1E-1 backstop that guarantees every slice is bounded. Every
    extracted text cell carries a <code>*_source_page</code> and
    <code>*_status</code> annotation so reviewers can cross-reference
    the original PDF.</p>

    <div class="card-row">
      <div class="stat"><div class="label">FY2022 ok</div><div class="value">143 / 172</div></div>
      <div class="stat"><div class="label">FY2023 ok</div><div class="value">190 / 197</div></div>
      <div class="stat"><div class="label">FY2024 ok</div><div class="value">289 / 308</div></div>
      <div class="stat"><div class="label">3-year ok CoC-years</div><div class="value">622</div></div>
    </div>

    <p>Other narrative columns (<code>1b_1a</code>, <code>1b_3</code>,
    <code>1c_4a</code>, <code>1d_11</code> racial-equity, etc.) remain
    as empty columns in the raw file — the schema is ready, only the
    extraction pass is pending.</p>

    <h2 id="stage3">Stage 3 · Narrative coding into structured variables</h2>

    <p><strong>Goal:</strong> turn each PLE narrative into a small set of
    machine-readable atomic codes that can enter a regression, while
    keeping every code defensible against its source text.</p>

    <p><strong>Output:</strong>
    <a href="downloads/coc_raw_for_coding.xlsx" download><code>coc_raw_for_coding.xlsx</code></a>
    (677 rows × 41 columns; ~1&nbsp;MB). One sheet, one row per CoC-year.</p>

    <h3>The coding protocol</h3>
    <ol>
      <li><strong>Atomic-code schema</strong> — 15 boolean indicators +
      one free-form frequency string across the 3 fields. Codes are
      grounded in Arnstein's (1969) participation ladder: representation
      (ladder top), compensation (tokenism defense), feedback loop
      (delegated power).
      <ul>
        <li><code>ple_umbrella</code> (6): <code>on_board</code>,
        <code>on_committees</code>, <code>compensated</code>,
        <code>hiring_advertised</code>, <code>formal_policy</code>,
        <code>decisionmaking</code></li>
        <li><code>ple_prof_dev</code> (5): <code>paid_positions</code>,
        <code>comp_policy_formal</code>, <code>training_pipeline</code>,
        <code>career_advancement</code>, <code>scope_beyond_tokenism</code></li>
        <li><code>ple_feedback</code> (4 + freq): <code>mechanism_formal</code>,
        <code>acts_on_feedback</code>, <code>addresses_barriers</code>,
        <code>closes_the_loop</code>, <code>frequency</code></li>
      </ul></li>

      <li><strong>Claude Code reads each narrative</strong> and returns a
      JSON object with every code plus a one-sentence <code>summary</code>
      and a list of <code>evidence</code>: up to three
      <em>verbatim quotations</em> from the source text that justify the
      coded values. If a field is not discussed in the narrative, the
      code is <code>null</code>; the model is instructed never to
      fabricate.</li>

      <li><strong>Scoring rule</strong> (Krippendorff 2018 §4.3, direct
      inference): <code>True → 1</code>, <code>False → 0</code>,
      <code>null → 0</code>. Rationale: HUD's instrument directly
      elicits the practice, so a CoC's non-mention is substantive evidence
      of absence, not of uncertainty. A robustness column pair
      (<code>*_availcase</code>) computes the available-case mean that
      skips nulls, for sensitivity checks.</li>

      <li><strong>Composite indices</strong> are computed per CoC-year
      (range 0 → 1):
      <ul>
        <li><code>ple_representation</code> = mean(on_board,
        on_committees, formal_policy, decisionmaking)</li>
        <li><code>ple_compensation</code> = mean(compensated,
        paid_positions, comp_policy_formal)</li>
        <li><code>ple_feedback_loop</code> = mean(mechanism_formal,
        acts_on_feedback, addresses_barriers, closes_the_loop)</li>
        <li><code>ple_institution</code> = mean of the three
        sub-indices — the headline IV</li>
      </ul></li>
    </ol>

    <h3 style="color:#b7791f">Coauthor review requested</h3>
    <div style="background:#fffbeb;border-left:4px solid #b7791f;padding:1em 1.2em;">
      <p style="margin-top:0">{n_coded} CoC-years are currently fully
      coded (the pilot batch). Before scaling coding to the remaining
      ~600 CoC-years, we need coauthor sign-off on three things:</p>

      <ol>
        <li><strong>Evidence ↔ code fidelity.</strong> Open
        <code>coc_raw_for_coding.xlsx</code>, sort by <code>coc_id</code>
        and <code>year</code>, and for each coded row check that the
        quotations in the three <code>*_evidence</code> columns actually
        support the 0/1 values in the atomic-code columns. If any code
        is not supported by its evidence, flip it in the cell and note
        the issue in <code>reviewer_notes</code>.</li>

        <li><strong>Schema validity.</strong> Are the 15 atomic indicators
        the right operationalization of institutionalized PLE engagement?
        Should any be added (e.g., youth-specific representation) or
        dropped (e.g., <code>hiring_advertised</code> if too weak)?
        Composite-index formulas are reported above and can be adjusted.</li>

        <li><strong>Scoring convention.</strong> We score
        <code>null → 0</code> (absent mention = absent practice). If
        coauthors prefer the available-case convention (skip nulls
        entirely) as the primary, say so — both columns already exist
        in <code>pilot_ple_variables.csv</code>.</li>
      </ol>

      <p>Once items 2 and 3 are confirmed, the pilot's 18 × 3 = 54
      narrative codings scale to ~1,800 across the full corpus.
      Iterating the schema after full coding is expensive; now is the
      right moment to weigh in.</p>
    </div>

    <h2 id="stage4">Stage 4 · Analytical panel for the regression</h2>
    <p><strong>Goal:</strong> select from the comprehensive raw file only
    the variables the primary multilevel DiD specification needs, and
    join in the PLE composite indices. This is the file the analysis
    scripts read.</p>

    <p><strong>Output:</strong>
    <a href="downloads/coc_panel_wide_with_ple.xlsx" download><code>coc_panel_wide_with_ple.xlsx</code></a>
    (651 CoC-years × 264 columns). Built by <code>merge_ple_variables.py</code>
    from the existing <code>coc_panel_wide.xlsx</code> plus
    <code>drafts/pilot_ple_variables.csv</code>.</p>

    <ul>
      <li><strong>Row scope:</strong> 651 = 172 (FY2022) + 195 (FY2023)
      + 284 (FY2024), after excluding Special-NOFO submissions that do
      not carry the DV. Balanced subset (125 CoCs observed in all three
      years) is a sheet within <code>coc_analysis_ready.xlsx</code>.</li>
      <li><strong>Carried-in variables</strong> from
      <code>coc_panel_wide.xlsx</code>: all 245 structured variables used
      for the DV construction, political geography, organizational
      controls, and the Mundlak within-CoC means.</li>
      <li><strong>New PLE columns</strong> (from
      <code>pilot_ple_variables.csv</code>): the four composite indices
      plus 15 atomic bool indicators. Currently non-null for the
      {n_coded} pilot-coded CoC-years; NaN elsewhere until Stage 3
      coding is expanded.</li>
      <li><strong>Used by:</strong> <code>run_multilevel.py</code>
      (primary DiD), <code>run_balanced_sensitivity.py</code>,
      <code>run_dv_robustness.py</code>. The existing specifications run
      unchanged; PLE variables enter as new regressors in the extended
      spec.</li>
    </ul>

    <h2>Reproducing the pipeline end-to-end</h2>
    <pre><code>cd data_pipeline
python3 build_file_inventory.py    # Stage 1 prerequisite
python3 router.py                  # Stage 1 — structured extraction
python3 build_raw_data.py          # Stage 1+2 consolidated raw file
python3 build_coding_file.py       # Stage 3 — coding workbook
# [Stage 3 coding runs inline or via the Claude API]
python3 merge_ple_variables.py     # Stage 4 — analytical panel
python3 run_multilevel.py          # Primary regression</code></pre>

    <h2>Downloads — the three files from this pipeline</h2>
    <p class="hint">Just the files produced by the four stages above.
    Open them in Excel or Numbers. Each link downloads the current build.</p>
    <table class="downloads"><thead><tr>
      <th>File</th><th>Stage</th><th>What it is</th>
    </tr></thead><tbody>
      <tr>
        <td><a href="downloads/coc_raw_data.xlsx" download><code>coc_raw_data.xlsx</code></a></td>
        <td>Stage 1 + 2</td>
        <td>Comprehensive raw data — 677 rows × 331 HUD variables + meta
        + 3 PLE narratives. <em>Open the <code>schema</code> sheet to see
        which variables are populated vs. awaiting extraction.</em></td>
      </tr>
      <tr>
        <td><a href="downloads/coc_raw_for_coding.xlsx" download><code>coc_raw_for_coding.xlsx</code></a></td>
        <td>Stage 3</td>
        <td>Coding workbook — 3 PLE narratives + 15 atomic code columns
        + 4 composite indices per CoC-year. {n_coded} CoC-years coded
        (pilot). <strong>This is the file to review.</strong></td>
      </tr>
      <tr>
        <td><a href="downloads/coc_panel_wide_with_ple.xlsx" download><code>coc_panel_wide_with_ple.xlsx</code></a></td>
        <td>Stage 4</td>
        <td>Analytical panel — 651 CoC-years × 264 columns. Feeds the
        regression in <code>run_multilevel.py</code>.</td>
      </tr>
    </tbody></table>
    """
    return wrap("Data collection and coding", "data.html", body,
                "Four-stage pipeline: automated digitization → text extraction → narrative coding → analytical panel. Coauthor review requested at Stage 3.")


def _stage1_flagged_block(rows: list[dict]) -> str:
    """Render the Stage 1 'files that need attention' section.

    Groups 677-file failures by status_code, shows summary counts, then
    lists every flagged file with its action for coauthor follow-up."""
    if not rows:
        return ("<p class='hint'><em>stage1_flagged.csv not found — "
                "run <code>python3 build_raw_data.py</code> to regenerate.</em></p>")

    # Count per status_code
    counts = Counter(r["status_code"] for r in rows)
    # Suppress NOT_PDF and OUT_OF_SCOPE — those are inventory-level, not
    # data-quality issues the coauthors need to act on.
    actionable_codes = [c for c in counts if c not in ("NOT_PDF", "OUT_OF_SCOPE")]
    actionable_rows = [r for r in rows if r["status_code"] in actionable_codes]
    n_total = len(actionable_rows)

    # Summary cards ordered by urgency
    CATEGORY_ORDER = [
        ("MIS_FILED_PROJECT_APP", "Mis-filed — wrong HUD form",         "bad"),
        ("SCANNED",               "Scanned PDFs — need OCR",            "warn"),
        ("ANCHOR_NOT_FOUND",      "Non-standard template — review",     "warn"),
        ("PLE_BLOCK_ABSENT",      "Incomplete — PLE block missing",     "warn"),
        ("LOW_TEXT",              "Low text — likely scanned/corrupt",  "warn"),
        ("UNKNOWN_FORMAT",        "Unknown format",                     "warn"),
        ("SPECIAL_NOFO_INSTRUMENT", "Special NOFO — excluded by design","good"),
    ]
    cards = []
    for code, label, badge in CATEGORY_ORDER:
        n = counts.get(code, 0)
        if n == 0:
            continue
        cards.append(
            f'<div class="stat"><div class="label">{html.escape(label)}</div>'
            f'<div class="value">{n}</div></div>'
        )
    cards_html = '<div class="card-row">' + "\n".join(cards) + "</div>"

    # Full table of flagged files — sorted by urgency then year/coc_id
    url_order = {c: i for i, (c, _, _) in enumerate(CATEGORY_ORDER)}
    actionable_rows.sort(key=lambda r: (url_order.get(r["status_code"], 99),
                                         r["year"], r["coc_id"]))

    LABEL_MAP = {c: label for c, label, _ in CATEGORY_ORDER}
    BADGE_MAP = {c: badge for c, _, badge in CATEGORY_ORDER}
    table_rows = []
    for r in actionable_rows:
        code = r["status_code"]
        badge = BADGE_MAP.get(code, "warn")
        label = LABEL_MAP.get(code, code)
        table_rows.append(
            f"<tr>"
            f"<td><code>{html.escape(r['original_filename'])}</code></td>"
            f"<td>{html.escape(r['coc_id'])}</td>"
            f"<td class='num'>{html.escape(str(r['year']))}</td>"
            f"<td><span class='badge {badge}'>{html.escape(label)}</span></td>"
            f"<td>{html.escape(r['action_needed'])}</td>"
            f"</tr>"
        )
    table_html = (
        "<table class='downloads'><thead><tr>"
        "<th>Source file</th><th>CoC</th><th>Year</th>"
        "<th>Category</th><th>What to do</th>"
        "</tr></thead><tbody>" + "\n".join(table_rows) + "</tbody></table>"
    )

    return f"""
    <h3 id="stage1-flagged" style="color:#b7791f">Files that need attention ({n_total})</h3>
    <p>Of the 677 source documents, <strong>{n_total}</strong> did not
    pass Stage 1 extraction cleanly. The categories below are in priority
    order for coauthor follow-up. Each row names the exact file
    (look it up in the OneDrive <code>Data/</code> folder) and what
    action would unblock it.</p>

    {cards_html}

    <details open><summary><strong>Show all {n_total} files</strong>
    &nbsp;<span class='hint'>(sorted by category, then year, then CoC)</span></summary>
    {table_html}
    </details>

    <p class='hint' style='margin-top:0.5em;'>
    The <strong>Special NOFO</strong> files are a design-level exclusion
    (different HUD form, no 1D PLE section) rather than a bug — they are
    listed so the exclusion is transparent, but no action is needed.
    Everything else is a genuine gap.
    </p>
    """


def _downloads_block(records: list[dict]) -> str:
    if not records:
        return "<p><em>(No downloadable files were found. Run the pipeline first.)</em></p>"
    groups = [
        ("primary",    "Primary analysis dataset",
         "Load these for the main regression."),
        ("provenance", "Data provenance &amp; review",
         "Source-document index, panel-safety map, crosswalk, and the manual-vs-extractor review queue."),
        ("ivs",        "Independent-variable coding",
         "Hand-coded nonprofit/government classification and the CoC → county political-geography merge."),
        ("results",    "Results tables (CSV)",
         "Coefficient tables behind the figures on the Results page."),
        ("docs",       "Documentation (Markdown)",
         "Codebook, methodology, and human-readable results writeups."),
    ]
    out = []
    for key, heading, lede in groups:
        subset = [r for r in records if r["group"] == key]
        if not subset:
            continue
        out.append(f"<h3>{heading}</h3>")
        out.append(f"<p class='hint'>{lede}</p>")
        out.append("<table class='downloads'><thead><tr>"
                   "<th>File</th><th>Size</th><th>Description</th>"
                   "</tr></thead><tbody>")
        for r in subset:
            out.append(
                f"<tr>"
                f"<td><a href='{r['href']}' download><code>{r['title']}</code></a></td>"
                f"<td class='num'>{r['size']}</td>"
                f"<td>{r['description']}</td>"
                f"</tr>"
            )
        out.append("</tbody></table>")
    return "\n".join(out)


def page_design():
    body = """
    <p class="lead">How <em>Grants Pass v. Johnson</em> becomes an
    identification strategy: two competing hypotheses, a multilevel
    decomposition of political environment, and an honest account of
    the DV's measurement-invariance issue.</p>

    <h2>Theory — two competing hypotheses</h2>
    <div class="callout">
      <div class="callout-title">H1 · Organizational form</div>
      <p>Nonprofit-led CoCs — more insulated from electoral pressure and
      with closer ties to service providers and advocates — should respond
      to a federal legal shock enabling criminalization (<em>Grants
      Pass</em>) by <em>raising</em> their anti-criminalization posture
      relative to government-led CoCs.</p>
    </div>
    <div class="callout">
      <div class="callout-title">H2 · Local political environment</div>
      <p>CoCs embedded in Democratic-leaning political environments —
      whether at the state level (H2a) or in terms of county-within-state
      deviation (H2b) — should raise their anti-criminalization posture
      relative to Republican-leaning environments. Governance structure
      is irrelevant in this story; politics filters the shock.</p>
    </div>

    <h2>Multilevel decomposition of political environment</h2>
    <p>Because CoCs are nested (CoCs ⊂ counties ⊂ states), and because
    state and county politics are highly correlated, we decompose county
    Biden vote share into two <em>orthogonal</em> components:</p>
    <pre><code>county_biden_share = state_mean_share      ← H2a (between-state)
                   + biden_within_state    ← H2b (within-state)</code></pre>
    <p>The between-state component is summarized as a binary
    <code>blue_state</code> indicator (Biden won the state's EC vote in
    2020). The within-state component is continuous and mean-zero by
    construction. Both enter the regression together without collinearity.</p>

    <h2>Model diagram</h2>
    <div style="text-align:center; margin: 1.5em 0;">
    <svg viewBox="0 0 860 420" width="100%" style="max-width:860px; font-family: -apple-system, sans-serif;">
      <defs>
        <marker id="arr" markerWidth="10" markerHeight="10" refX="9" refY="3" orient="auto">
          <path d="M0,0 L0,6 L9,3 z" fill="#0366d6"/>
        </marker>
        <marker id="arr-n" markerWidth="10" markerHeight="10" refX="9" refY="3" orient="auto">
          <path d="M0,0 L0,6 L9,3 z" fill="#c53030"/>
        </marker>
      </defs>

      <rect x="30" y="50" width="200" height="70" rx="8" fill="#fdf2f2" stroke="#c53030" stroke-width="2"/>
      <text x="130" y="78" text-anchor="middle" font-weight="600" font-size="13">H1 · Organizational form</text>
      <text x="130" y="98" text-anchor="middle" font-size="11" fill="#555">Nonprofit-led (vs Government-led)</text>
      <text x="130" y="112" text-anchor="middle" font-size="11" fill="#555">coded from 1a_2 Collaborative Applicant</text>

      <rect x="30" y="180" width="200" height="50" rx="8" fill="#eef4fb" stroke="#0366d6" stroke-width="2"/>
      <text x="130" y="202" text-anchor="middle" font-weight="600" font-size="13">H2a · State-level politics</text>
      <text x="130" y="220" text-anchor="middle" font-size="11" fill="#555">Blue state (Biden 2020 winner)</text>

      <rect x="30" y="260" width="200" height="50" rx="8" fill="#eef4fb" stroke="#0366d6" stroke-width="2" stroke-dasharray="4,2"/>
      <text x="130" y="280" text-anchor="middle" font-weight="600" font-size="13">H2b · County-within-state</text>
      <text x="130" y="298" text-anchor="middle" font-size="11" fill="#555">Biden share − state mean</text>

      <rect x="310" y="165" width="210" height="80" rx="8" fill="#fff4cc" stroke="#8a6d1f" stroke-width="2"/>
      <text x="415" y="193" text-anchor="middle" font-weight="600" font-size="14">Grants Pass shock</text>
      <text x="415" y="213" text-anchor="middle" font-size="11" fill="#555">SCOTUS ruling · June 28, 2024</text>
      <text x="415" y="229" text-anchor="middle" font-size="11" fill="#555">FY2024 = Post indicator</text>

      <rect x="620" y="165" width="200" height="80" rx="8" fill="#f0faf3" stroke="#17813c" stroke-width="2"/>
      <text x="720" y="193" text-anchor="middle" font-weight="600" font-size="14">Anti-crim activity</text>
      <text x="720" y="213" text-anchor="middle" font-size="11" fill="#555">crim_activity_index ∈ [0,1]</text>
      <text x="720" y="229" text-anchor="middle" font-size="11" fill="#555">share of 1D-4 cells = Yes</text>

      <rect x="310" y="310" width="210" height="90" rx="8" fill="#fafafa" stroke="#888" stroke-width="1.5" stroke-dasharray="4,3"/>
      <text x="415" y="333" text-anchor="middle" font-weight="600" font-size="13" fill="#444">Controls</text>
      <text x="415" y="351" text-anchor="middle" font-size="11" fill="#555">Housing First · HMIS coverage</text>
      <text x="415" y="366" text-anchor="middle" font-size="11" fill="#555">log(total beds, winsorized)</text>
      <text x="415" y="381" text-anchor="middle" font-size="11" fill="#555">PLE participation · Mundlak means</text>

      <path d="M 230 85 Q 280 125 310 180" fill="none" stroke="#c53030" stroke-width="2.5" marker-end="url(#arr-n)"/>
      <text x="244" y="145" font-size="11" fill="#c53030">H1: × Post</text>
      <path d="M 230 205 L 310 205" fill="none" stroke="#0366d6" stroke-width="2.5" marker-end="url(#arr)"/>
      <text x="250" y="200" font-size="11" fill="#0366d6">H2a: × Post</text>
      <path d="M 230 285 Q 270 260 310 225" fill="none" stroke="#0366d6" stroke-width="2" stroke-dasharray="4,2" marker-end="url(#arr)"/>
      <text x="240" y="260" font-size="11" fill="#0366d6">H2b: × Post</text>
      <path d="M 520 205 L 620 205" fill="none" stroke="#17813c" stroke-width="3" marker-end="url(#arr)"/>
      <path d="M 520 345 Q 580 290 620 230" fill="none" stroke="#888" stroke-width="1.5" marker-end="url(#arr)"/>
    </svg>
    </div>
    <p class="hint">Red arrow = H1 prediction. Blue arrows = H2
    predictions. Each IV's interaction with Post is its DiD estimand.</p>

    <h2>Operationalization</h2>
    <table>
      <thead><tr><th>Construct</th><th>Variable</th><th>Type</th><th>Source</th></tr></thead>
      <tbody>
        <tr><td><strong>IV₁ · Organizational form</strong></td>
            <td><code>nonprofit_led</code></td>
            <td>binary</td>
            <td>Hand-coded from <code>1a_2</code> Collaborative Applicant Name (99% coverage)</td></tr>
        <tr><td><strong>IV₂ · State-level politics</strong></td>
            <td><code>blue_state</code></td>
            <td>binary</td>
            <td>2020 presidential EC winner (Biden=1, Trump=0; DC blue; territories excluded)</td></tr>
        <tr><td><strong>IV₃ · Within-state county politics</strong></td>
            <td><code>biden_within_state</code></td>
            <td>continuous</td>
            <td>County Biden share − state-level mean (MIT/tonmcg 2020 county data)</td></tr>
        <tr><td><strong>Shock</strong></td>
            <td><code>post</code></td>
            <td>binary (FY2024 = 1)</td>
            <td><em>Grants Pass v. Johnson</em> (SCOTUS, June 28, 2024)</td></tr>
        <tr><td><strong>DV</strong></td>
            <td><code>crim_activity_index</code></td>
            <td>fraction [0, 1]</td>
            <td>Share of 6 HUD 1D-4 cells answered "Yes"</td></tr>
        <tr><td>Control · service orientation</td>
            <td><code>hf_pct</code></td>
            <td>fraction</td>
            <td>Housing First adoption, HUD 1D-2</td></tr>
        <tr><td>Control · CoC maturity</td>
            <td><code>hmis_cov</code></td>
            <td>fraction</td>
            <td>HMIS ES bed coverage, HUD 2A-5</td></tr>
        <tr><td>Control · size</td>
            <td><code>log_beds</code></td>
            <td>continuous</td>
            <td>log(total beds + 1), winsorized at 99th pct</td></tr>
        <tr><td>Control · PLE participation</td>
            <td><code>ple_ces_bin</code></td>
            <td>binary</td>
            <td>HUD 1B-1 row 6 in CES</td></tr>
      </tbody>
    </table>

    <h2>Primary specification</h2>
    <pre><code>crim_activity_index<sub>it</sub> =
    β₁ · Nonprofit<sub>i</sub>
  + β₂ · Blue_state<sub>i</sub>
  + β₃ · Biden_within_state<sub>i</sub>
  + β₄ · Post<sub>t</sub>
  + β₅ · Nonprofit × Post                 ← H1 test
  + β₆ · Blue_state × Post                ← H2a test
  + β₇ · Biden_within × Post              ← H2b test
  + γ · Controls<sub>it</sub> (Mundlak-adjusted)
  + ε<sub>it</sub></code></pre>
    <ul>
      <li><strong>Estimator:</strong> Papke-Wooldridge fractional logit
      (bounded [0, 1] DV with mass at 0 and 1).</li>
      <li><strong>Standard errors:</strong> state-level cluster-robust,
      reinforced with wild-cluster bootstrap (Rademacher weights,
      999 replicates). Addresses small-cluster over-rejection per
      Bertrand, Duflo &amp; Mullainathan (2004).</li>
      <li><strong>Sample:</strong> unbalanced panel (651 obs) for primary
      power; balanced three-year panel (375 obs) reported as sensitivity.</li>
      <li><strong>Mundlak means:</strong> adding CoC-level means of
      time-varying controls preserves identification of the DiD coefficients
      without absorbing the time-invariant IVs, which within-CoC fixed
      effects would otherwise do.</li>
    </ul>

    <h2>DV measurement invariance — the load-bearing caveat</h2>
    <p>The outcome comes from HUD's 1D-4 question, which was reworded in
    FY2024:</p>
    <table>
      <thead><tr><th>Column</th><th>FY2022 / FY2023 wording</th><th>FY2024 wording</th></tr></thead>
      <tbody>
        <tr><td>1 · Policymaker engagement</td>
            <td>"Engaged local policymakers to prevent criminalization"</td>
            <td>"Engaged legislators on co-responder responses"</td></tr>
        <tr><td>2 · Implementation</td>
            <td>"Reverse existing criminalization policies"</td>
            <td>"Implemented Laws/Policies/Practices that Prevent Criminalization"</td></tr>
      </tbody>
    </table>
    <p>The column-2 reword is mechanically easier to check Yes — any
    existing policy qualifies, not just a reversal. Descriptives show
    the FY2024 jump is concentrated in column 2, consistent with at
    least <em>some</em> of the level shift being an instrument effect.</p>
    <p>Three design choices handle this:</p>
    <ol>
      <li><strong>Year fixed effect</strong> (the <code>post</code>
      indicator) absorbs the common instrument-change shift.</li>
      <li><strong>DiD interactions</strong> identify <em>differential</em>
      response — the instrument change cancels out of any contrast
      between CoCs facing the same reworded form.</li>
      <li><strong>Engagement-only DV</strong> (<code>results.html</code>
      robustness) restricts to the column-1 cells whose wording was
      nearly identical across years.</li>
    </ol>

    <p>Next: <a href="descriptive.html">descriptive patterns</a> →
    <a href="results.html">analysis results</a>.</p>
    """
    return wrap("Research design and measurement", "design.html", body,
                "Two competing hypotheses, a multilevel decomposition of political environment, and the DV measurement story.")


def page_results():
    bal = load_csv(PIPELINE_DIR / "balanced_sensitivity_coefs.csv")
    dvr = load_csv(PIPELINE_DIR / "dv_robustness_coefs.csv")
    main_body_html = page_main_results()

    import re
    match = re.search(r"<header>.*?</header>\s*(.*)<footer>", main_body_html, re.S)
    if match:
        core = match.group(1)
    else:
        core = "<p><em>Main results body could not be extracted.</em></p>"

    core = core.replace('href="balanced.html"',     'href="#balanced"')
    core = core.replace('href="dv_story.html"',     'href="design.html#dv-story"')
    core = core.replace('href="dv_robust.html"',    'href="#dv-robust"')
    core = core.replace('href="descriptive.html"',  'href="descriptive.html"')

    def bal_row(rows, spec):
        u = next((r for r in rows if r.get("spec") == spec and r.get("panel") == "unbalanced"), {})
        b = next((r for r in rows if r.get("spec") == spec and r.get("panel") == "balanced"), {})
        def cell(r):
            if not r:
                return "<td class='num'>—</td><td class='num'>—</td>"
            coef = r.get("coef", "")
            p    = r.get("p_boot", "") or r.get("p", "")
            return f"<td class='num'>{coef}</td><td class='num'>{p}</td>"
        return f"<tr><td><strong>{spec}</strong></td>{cell(u)}{cell(b)}</tr>"

    balanced_table = ""
    if bal:
        balanced_table = (
            "<table><thead><tr>"
            "<th>Term</th>"
            "<th class='num'>β (unbalanced)</th><th class='num'>p<sub>boot</sub></th>"
            "<th class='num'>β (balanced)</th><th class='num'>p<sub>boot</sub></th>"
            "</tr></thead><tbody>"
            + bal_row(bal, "Nonprofit × Post")
            + bal_row(bal, "Blue × Post")
            + bal_row(bal, "Biden_within × Post")
            + "</tbody></table>"
        )

    def dvr_rows(rows):
        out = []
        for r in rows:
            out.append(
                f"<tr><td>{r.get('dv','')}</td>"
                f"<td>{r.get('term','')}</td>"
                f"<td class='num'>{r.get('coef','')}</td>"
                f"<td class='num'>{r.get('p_boot', r.get('p',''))}</td>"
                f"<td class='num'>{r.get('n','')}</td></tr>"
            )
        return "".join(out)

    dvr_table = ""
    if dvr:
        dvr_table = (
            "<table><thead><tr>"
            "<th>DV</th><th>Term</th>"
            "<th class='num'>β</th><th class='num'>p<sub>boot</sub></th><th class='num'>n</th>"
            "</tr></thead><tbody>" + dvr_rows(dvr) + "</tbody></table>"
        )

    appendix = f"""
    <hr>
    <h2 id="balanced">Appendix A · Balanced-panel sensitivity</h2>
    <p>The primary spec uses the unbalanced panel (651 obs) for power.
    The balanced subset keeps only the 125 CoCs observed in all three
    years (375 obs). If the pattern reflects political geography rather
    than selection, the within-state county pull should survive balancing;
    the binary state-level effect may weaken because composition drives
    much of it.</p>
    {balanced_table or '<p><em>(Run <code>run_balanced_sensitivity.py</code> to populate this table.)</em></p>'}
    <p><strong>Reading:</strong> Blue × Post weakens sharply under
    balancing (β = +0.57 → near zero), consistent with the unbalanced
    effect being partly a composition artifact; the within-state county
    pull is stable to strengthening. Political geography, not which CoCs
    HUD happened to add in FY2024, carries the story.</p>

    <h2 id="dv-robust">Appendix B · Alternative DV definitions</h2>
    <p>Three DV variants probe measurement sensitivity:</p>
    <ol>
      <li><strong>DV1 · Full six-cell activity index</strong> — the primary
      DV reported above.</li>
      <li><strong>DV2 · Engagement-only</strong> — the three 1D-4
      "policymaker engagement" cells whose wording was nearly identical
      across FY2022/23 and FY2024. This DV is immune to the FY2024
      column-2 reword discussed on the <a href="design.html">design</a>
      page.</li>
      <li><strong>DV3 · FY2022 + FY2023 only</strong> — pre-shock,
      identical instrument across both years. Used as a placebo:
      political-geography effects should <em>not</em> appear here.</li>
    </ol>
    {dvr_table or '<p><em>(Run <code>run_dv_robustness.py</code> to populate this table.)</em></p>'}
    <p><strong>Reading:</strong> the political-geography pattern survives
    DV2 (engagement-only cells), so the effect is not an artifact of the
    column-2 wording change. DV3 (pre-shock only) shows no differential
    pattern, consistent with a genuine post-shock divergence rather than
    a long-run red/blue gap in CoC reporting style.</p>

    <h2 id="limits">Limitations</h2>
    <ol>
      <li><strong>Marginal state-level significance.</strong> The binary
      Blue × Post coefficient is at bootstrap p ≈ 0.095 in the primary
      specification and loses significance under balancing. Reported as
      suggestive, not definitive.</li>
      <li><strong>Self-report DV.</strong> The outcome is what CoCs
      <em>say</em> they do on HUD Form 1D-4. External behavioral
      triangulation (PIT outflow rates, state legislation trackers) is
      a needed next step.</li>
      <li><strong>Short post-period.</strong> FY2024 applications were
      submitted four months after the Supreme Court ruling. Medium-term
      persistence cannot be assessed until FY2025 data are available.</li>
      <li><strong>State cluster count.</strong> ~50 state clusters with
      many singletons force wild-cluster bootstrap inference; asymptotic
      cluster SEs would over-reject.</li>
      <li><strong>Quadrant cell imbalance.</strong> Red-state × Blue-county
      has only 26 FY2024 observations, limiting precision in that cell.</li>
    </ol>

    <h2>Reproduce</h2>
    <pre><code>cd data_pipeline
python3 run_multilevel.py            # primary specification + bootstrap
python3 run_balanced_sensitivity.py  # Appendix A
python3 run_dv_robustness.py         # Appendix B
python3 build_site.py                # regenerate this page</code></pre>
    """

    combined = core + appendix
    return wrap("Analysis results", "results.html", combined,
                "Multilevel fractional-logit DiD with state-clustered wild-cluster bootstrap — plus balanced-panel and DV-robustness appendices.")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main():
    records = copy_downloads()
    pages = {
        "index.html":       page_index(),
        "data.html":        page_data_development(records),
        "design.html":      page_design(),
        "descriptive.html": page_descriptive(),
        "results.html":     page_results(),
    }
    for name, html_text in pages.items():
        (SITE_DIR / name).write_text(html_text)
        print(f"wrote {name}")
    print(f"staged {len(records)} downloads under {DOWNLOADS_DIR}")
    print(f"\nOpen: file://{SITE_DIR}/index.html")


if __name__ == "__main__":
    main()
