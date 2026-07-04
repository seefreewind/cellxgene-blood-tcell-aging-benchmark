# Stage 23 revision changelog for Computational Biology and Chemistry

Date: 2026-07-04

## Scope tightening

- Reframed the manuscript as a reproducible computational benchmark rather than a broad biological discovery or pan-tissue aging study.
- Revised the title to: "Leakage-aware benchmarking of hosted single-cell representations for blood T-cell aging-related prediction".
- Kept blood T cells as the only completed empirical benchmark stratum.
- Preserved conservative wording that the study evaluates CELLxGENE-hosted scVI and TranscriptFormer representations, not Geneformer, scGPT, scFoundation, GeneCompass, or all single-cell foundation models.
- Removed or softened wording that could imply a pan-tissue aging predictor, clinical validation, biological mechanism discovery, or broad model comparison.

## Computational biology positioning

- Rewrote the Abstract to open with the computational validation problem: random-cell splits can inflate apparent performance when labels are structured by donor identity, disease status, assay, or study origin.
- Revised the Background to focus on public atlas reuse, hosted embeddings, metadata-derived age labels, donor-aware validation, disease-aware evaluation, and dataset-shift diagnostics.
- Reorganized Results around computational questions: eligible public benchmark strata, random-cell signal, donor-aware and dataset-aware evaluation, metadata-only baselines, LODO feasibility, and sampling-depth sensitivity.
- Rewrote the Discussion to interpret results as benchmark behavior under validation design choices rather than biological aging discovery.

## Reproducibility improvements

- Added a benchmark-design schematic as the new Figure 1.
- Added an explicit Methods subsection mapping benchmark risks to diagnostic controls.
- Clarified that repeated-seed confidence intervals summarize variation across split seeds and should not be interpreted as independent external-cohort uncertainty.
- Updated Supplementary Information to include:
  - Supplementary Table S1: benchmark risks and diagnostic controls.
  - Supplementary Table S2: LODO eligibility and exclusion summary.
  - Supplementary Checklist S1: mapping of diagnostic controls to leakage or confounding risks.
- Updated Data Availability wording to specify the reproducibility package contents and to retain honest placeholders for GitHub and Zenodo links.

## Leakage/confounding diagnostics

- Made metadata-only prediction a central control rather than a secondary result.
- Explicitly connected random-cell, donor-holdout, grouped dataset-holdout, disease-free, label-shuffling, LODO, and sampling-depth analyses to their intended diagnostic roles.
- Emphasized that random-cell performance can reflect metadata and source structure.
- Emphasized that grouped dataset-holdout and LODO analyses diagnose study-level transfer and age-class imbalance.
- Clarified that donor-mean aggregation is a computational observation about label unit and sampling depth, not evidence of a validated biological mechanism.

## Limitations and cautious interpretation

- Preserved the major limitations requested by the user:
  - The completed empirical benchmark is restricted to blood T cells.
  - Age is inferred from public `development_stage` labels rather than a harmonized donor-age field.
  - Dataset-holdout and LODO analyses are constrained by strong age-class imbalance.
  - Geneformer, scGPT, scFoundation, GeneCompass, and other models were not directly run.
  - No raw-expression benchmark or manual external metadata harmonization was added.
  - GitHub and Zenodo archival links remain to be finalized before submission.
- Kept claims conservative and avoided new empirical claims beyond completed project outputs.
- Maintained 49 verified references and reduced over-dense citation ranges in the revised Introduction and Discussion.

## Remaining author actions before submission

- Complete author names, affiliations, correspondence details, funding, acknowledgements, and author-contribution statements.
- Replace `[GitHub repository URL to be inserted before submission]` and `[Zenodo DOI to be inserted before submission]` with final archival links.
- Confirm whether Computational Biology and Chemistry requires a specific title page, graphical abstract, highlights, conflict-of-interest declaration format, or data/code availability template.
- Decide whether to keep the current Word-first submission file or convert the manuscript into a journal-specific LaTeX/PDF package later.

## Final outputs from this stage

- Word manuscript: `outputs/donor_disease_aware_sc_aging_submission_ready_v2.docx`
- Rendered PDF: `outputs/rendered_submission_ready_v2/donor_disease_aware_sc_aging_submission_ready_v2.pdf`
- Rendered page images: `outputs/rendered_submission_ready_v2/page-*.png`
- New schematic figure: `outputs/upgrade_figures/figure0_benchmark_design_schematic.png`
- Updated manuscript builder: `manuscript/build_submission_ready_benchmark_v2.py`
