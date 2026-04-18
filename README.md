# CoC Criminalization & PLE Engagement

Longitudinal study of how 325 U.S. Continuums of Care responded to the
June 2024 Supreme Court ruling in *Grants Pass v. Johnson* — built from
677 HUD CoC Consolidated Application documents (FY2022–FY2024).

**Authors:** Kyungmin Lee & Hanvit Kim, University of Central Florida.

## Headline finding

Local political environment — not CoC governance structure — filters
federal legal shocks on homelessness criminalization. Nonprofit-led vs
government-led CoCs responded identically (β = +0.09,
p<sub>boot</sub> = 0.80); state political composition predicts
differential post-shock response (β = +0.57, p<sub>boot</sub> = 0.095),
with the effect concentrated at the state level rather than within-state
county variation.

## Repository layout

```
├── data_pipeline/        # extraction pipeline + analysis scripts
│   ├── build_*.py        # dataset construction
│   ├── run_multilevel.py # primary multilevel DiD specification
│   ├── run_balanced_sensitivity.py
│   ├── run_dv_robustness.py
│   └── *.csv / *.xlsx    # analysis-ready outputs
├── site/                 # generated static website
│   ├── index.html        # 5-section overview + results
│   └── downloads/        # coauthor-accessible dataset copies
├── codebook.md
├── data_construction_methodology.md
└── main_variables.md
```

## Data availability

The raw HUD CoC application PDFs are **not** included in this repository
(they are publicly available from HUD; contact the authors for the
curated local mirror). Derived artifacts are committed:

- `data_pipeline/coc_analysis_ready.{xlsx,csv}` — primary three-year panel
- `data_pipeline/coc_panel_wide.xlsx` — full 243-variable wide panel
- `data_pipeline/coc_panel_long.csv` — long form
- `data_pipeline/harmonized_dv.xlsx` — harmonized outcomes
- Results CSVs: `multilevel_coefs.csv`, `balanced_sensitivity_coefs.csv`,
  `dv_robustness_coefs.csv`, etc.

## Reproduce the primary analysis

```bash
cd data_pipeline
python3 run_multilevel.py            # primary multilevel DiD + wild-cluster bootstrap
python3 run_balanced_sensitivity.py  # Appendix A
python3 run_dv_robustness.py         # Appendix B
python3 build_site.py                # regenerate the static site
```

## Primary specification

Papke-Wooldridge fractional logit with Mundlak within-CoC means,
state-clustered standard errors reinforced by wild-cluster bootstrap
(Rademacher weights, 999 replicates):

```
crim_activity_index = β₁·Nonprofit + β₂·BlueState + β₃·BidenWithin + β₄·Post
                    + β₅·Nonprofit × Post      ← H1 test
                    + β₆·BlueState × Post      ← H2a test
                    + β₇·BidenWithin × Post    ← H2b test
                    + γ·Controls (Mundlak-adjusted) + ε
```

See `data_construction_methodology.md` and `site/design.html` for the
full methodological discussion.
