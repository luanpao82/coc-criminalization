# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project

Research codebase for Lee & Kim (UCF) — a multilevel difference-in-differences
study of how 325 U.S. Continuums of Care (CoCs) responded to *Grants Pass v.
Johnson* (SCOTUS, June 28, 2024), built from 677 HUD CoC Consolidated
Application documents (FY2022–FY2024). Primary specification is a
Papke-Wooldridge fractional logit with Mundlak within-CoC means,
state-clustered SEs, and wild-cluster bootstrap p-values.

## Key commands

The full pipeline lives in `data_pipeline/`. All scripts are run with
`python3` from that directory. Outputs land back in `data_pipeline/` by
default.

**Dataset construction** (one-time or after raw-source updates):

```bash
cd data_pipeline
python3 build_file_inventory.py          # scan DATA_DIR → file_inventory.csv
python3 router.py                         # dispatch extractors → extracted/*.json
python3 build_panel.py                   # per-year + long/wide panels
python3 build_harmonized_dv.py           # crim_activity_index across 3 years
python3 build_analysis_ready.py          # unbalanced/balanced/fy2024_only sheets
python3 code_iv_leadership.py            # nonprofit vs government classification
python3 build_coc_county.py              # CoC → county Biden vote merge
```

**Primary analysis** (reproduces the published results):

```bash
python3 run_multilevel.py                # primary multilevel DiD + wild-cluster bootstrap
python3 run_balanced_sensitivity.py      # Appendix A — balanced-panel robustness
python3 run_dv_robustness.py             # Appendix B — alternative DV definitions
```

**Quality assurance:**

```bash
python3 corpus_diff.py                   # extractor vs manual xlsx diff → review queue
python3 build_review_ui.py               # renders review_ui.html for human adjudication
```

**Coauthor-facing site:**

```bash
python3 build_site.py                    # regenerate docs/ + copy downloads/
python3 build_map.py                     # interactive CoC map (docs/map.html)
git push                                 # → GitHub Pages rebuilds in ~1–2 min
```

## Architecture

### Two data roots

`pipeline_utils.py` defines two Path constants that everything else imports:

- `DATA_DIR` — OneDrive location of the raw HUD source documents and the
  manual reference xlsx (`coc_apps_all_info.xlsx`). **Not in the repo.**
- `PIPELINE_DIR` — `data_pipeline/` in this repo. All derived artifacts live
  here: extracted JSONs, panel CSVs/XLSXs, result CSVs, markdown writeups.

Scripts read from `DATA_DIR` and write to `PIPELINE_DIR`. No script should
write into `DATA_DIR`. The `extracted/` and `drafts/` subdirectories of
`PIPELINE_DIR` are gitignored (bulk intermediate JSON outputs, ~74 MB).

### Extraction — format-aware with a router

`router.py` reads `file_inventory.csv` and dispatches each (coc_id, year) to
a format-specific adapter:

- `extract_pdf_native.py` — native PDFs via `pdftotext -layout`
- `extract_docx.py` — DOCX via `python-docx` structural walk
- `extract_narrative.py` — LLM Stage-2 coding for open-ended narrative fields
  (requires `ANTHROPIC_API_KEY` env var)

Nine FY2024 PDFs are flagged as scanned with no DOCX alternative; a dedicated
OCR adapter is not yet wired up.

All adapters implement the same record schema: `{coc_id, year, field_id,
value, raw_text, source_page, extractor, confidence, needs_review}`.
Every extracted cell carries provenance.

### Anchor-then-parse principle

Extractors locate each HUD question by its `1B-1.` / `1D-4.`-style anchor
and parse only the local block that follows. A parse failure in one
question's block must not contaminate neighboring variables. This is
enforced at the adapter level, not by post-processing.

### DV harmonization is load-bearing

HUD reworded the 1D-4 criminalization question between FY2023 and FY2024.
`build_harmonized_dv.py` produces three comparable DVs by mapping the
extractor's per-year field IDs to a common schema; `dv_harmonization_strategies.md`
documents the reasoning. Two non-obvious decisions:

1. **Only rows 1–3 of the 1D-4 chart are kept in every year.** FY2022/23
   had 4 rows, FY2024 has 3. Including row 4 for some years would make
   the activity index incomparable.
2. **The *column* means different things per year.** The FY2024 "column 2"
   reword ("Implemented Laws/Policies…") is mechanically easier to check
   Yes than the FY2022/23 "Reverse existing" wording. Year fixed effects
   absorb the common shift; DiD interactions identify differential response.

### Multilevel Mundlak decomposition

`run_multilevel.py` orthogonalizes county Biden vote share into:

```
state_mean_biden   = mean Biden share of counties in the state
biden_within_state = county_biden − state_mean_biden
```

so that `blue_state` (H2a, between-state) and `biden_within_state` (H2b,
within-state county deviation) can both enter the same regression without
collinearity. Time-varying controls get Mundlak within-CoC means added,
which preserves identification of the DiD coefficients without CoC fixed
effects absorbing the time-invariant IVs.

### Inference

State-level clustering with ≈50 clusters (many singletons) over-rejects under
asymptotic cluster SEs. `run_multilevel.py` therefore reports **wild-cluster
bootstrap p-values** (Rademacher weights, 999 reps, clustered at state).
This is not optional — do not substitute asymptotic cluster SEs in downstream
writeups.

### Site — builds to `docs/`, not `site/`

`build_site.py` writes HTML into `docs/` (set by `SITE_DIR = PIPELINE_DIR.parent / "docs"`).
GitHub Pages only accepts `/` or `/docs` as source path. A parallel
`docs/downloads/` directory is auto-populated by `copy_downloads()`; the
`DOWNLOADS` list at the top of `build_site.py` is the registry of which
files to stage for coauthor download. To add a new file, append a tuple to
that list and rebuild.

Site structure is five top-level pages. This is intentional — earlier
versions had 8–19 pages and were explicitly cut down. Prefer inline
appendix sections over new pages when adding analytical variants.

### Reference-standard reconciliation

`corpus_diff.py` compares every extracted CoC against the manual reference
xlsx and writes `corpus_diffs.csv` (the review queue) plus
`corpus_agreement.md` (per-category rates). The pipeline never auto-patches
the manual file; every disagreement is surfaced for human review. When
extractor and manual disagree, the extractor cites a specific PDF page —
if it matches the source, the manual entry is the one to correct.

## Deployment

- Public GitHub repo: `luanpao82/coc-criminalization` (already pushed).
- Live site: https://luanpao82.github.io/coc-criminalization/ — serves from
  `main` branch, `/docs` path. Pushing to `main` triggers a rebuild.
- `gh` CLI is authenticated as `luanpao82`.
- Never commit files under `data_pipeline/extracted/` or
  `data_pipeline/drafts/` — both are gitignored for size + derivability.

## Methodology references

- `data_construction_methodology.md` — full pipeline protocol with citations
  (Krippendorff, Cohen, Gilardi et al., Ziems et al.).
- `codebook.md` — 331 canonical variables with controlled vocabularies.
- `main_variables.md` — operationalization notes for regression variables.
- `multilevel_results.md` — human-readable writeup of the primary spec.
