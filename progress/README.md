---
title: Building a Research-Grade Dataset from 677 HUD Documents — Process Log
project: CoC Criminalization / PLE Engagement (Lee & Kim, UCF)
audience: public / coauthors / future replicators
status: living document — updated as the pipeline evolves
last_updated: 2026-04-17
---

# Building a Research-Grade Dataset from 677 HUD Documents

This is an open process log for the data-construction effort behind our
study of *how Continuum of Care (CoC) governance shapes engagement with
people with lived experience (PLE) of homelessness and the use of punitive
responses to homelessness*.

Rather than publish only the finished dataset and a terse Methods section,
we are documenting the build as it happens — the choices, the dead ends,
the moment automation caught manual errors — so that the methodology is
transparent, reusable, and credible to reviewers and coauthors.

## Why this log exists

Three audiences, one document set:

1. **Coauthors and RAs** — concrete protocol; who does what and why.
2. **Reviewers of the eventual paper** — evidence the dataset is reproducible.
3. **Other researchers** — a worked example of combining classical content
   analysis (Krippendorff, 2018; Neuendorf, 2017), text-as-data methods
   (Grimmer & Stewart, 2013; Grimmer, Roberts, & Stewart, 2022), and modern
   LLM-assisted annotation (Gilardi, Alizadeh, & Kubli, 2023; Ziems et al.,
   2024) on a policy-document corpus.

## Reading order

| # | Page | What it covers |
|---|---|---|
| 1 | [[01-data-audit]] | What the 677-file corpus actually looks like — years, formats, scans, duplicates, naming anomalies |
| 2 | [[02-methodology-design]] | The three-stage extraction pipeline, the four variable classes, and the 98% convergence target |
| 3 | [[03-schema-and-crosswalk]] | Building the codebook (331 variables) and the year-to-year crosswalk |
| 4 | [[04-first-extractor]] | The first working extractor (1A + 1B-1), its design choices, and iteration 0 |
| 5 | [[05-debugging-and-iteration]] | Iteration 1 — a real extractor bug, a fix, and three manual-coder errors surfaced by automation |
| 6 | [[06-findings-so-far]] | Numbers, implications, and what's next |
| 7 | [[07-extending-coverage]] | Iteration 3 — adding 1C/1D sections including the criminalization-strategies chart |
| 8 | [[08-corpus-scale-run]] | Iteration 4 — full 2024 corpus (292 CoCs, 69k comparisons); 98.25% adjusted agreement achieved |
| 9 | [[09-closure-and-handoff]] | Session-close snapshot — what shipped, what's open, where to start next |

## Status at a glance (2026-04-17, after iteration 4)

- **Files indexed:** 677 across FY2022–FY2024, including 8 DOCX and 19 scanned PDFs
- **Canonical schema:** 331 variables (FY2024), first-pass codebook drafted
- **Crosswalk:** 113 canonical families mapped across 3 years; 34 flagged for PI review
- **Extractor coverage:** 242 variables per CoC (~73% of schema, all structured classes)
- **Corpus run:** **292 CoCs × 242 fields = 69,361 comparisons**, run in ~55 seconds
- **Weighted agreement:** **96.65%** (raw)
- **Adjusted agreement:** **98.25%** — **98% target met** ✅
- **Manual gaps filled by automation:** ~1,131 cells
- **Criminalization variables (`1d_4_*`):** full 3×2 chart covered for every extractable CoC

## Related internal documents

- [[data_construction_methodology]] — formal Methods document with citations
- [[codebook]] — per-variable definitions, value domains, missing conventions
- [[pilot_findings]] — snapshot of the first two iterations
- [[KL_From_Inclusion_to_Influence]] — project concept note and research questions
- [[2025_ARNOVA_KL]] — conference presentation of preliminary findings
