# Current project status

Date: 2026-07-01  
Project: single-cell aging benchmark manuscript  
Workspace: `/Users/zy/Documents/New project 5`

## One-line status

The project has advanced from a feasibility/protocol-style draft to a complete first empirical manuscript draft centered on a 30-seed blood T-cell benchmark of CELLxGENE-hosted scVI and TranscriptFormer embeddings, with leakage-aware diagnostics, confounding analyses, reproducibility files, and a rendered Word draft.

## Main manuscript output

- Current Word draft: `outputs/donor_disease_aware_sc_aging_submission_ready_v2.docx`
- Rendered QA PDF: `outputs/rendered_submission_ready_v2/donor_disease_aware_sc_aging_submission_ready_v2.pdf`
- Rendered page images: `outputs/rendered_submission_ready_v2/page-*.png`
- Manuscript builder: `manuscript/build_submission_ready_benchmark_v2.py`

The Word draft has been rendered and visually spot-checked. No obvious missing figures, table overflow, or text overlap was observed. Some figure-heavy pages still have generous white space, but the file is usable as a first complete internal-review draft.

## What has been completed

### 1. Metadata feasibility audit

The Phase 0 audit has been completed using CELLxGENE Census release `2025-11-08`.

Key outputs:

- `analysis/outputs/metadata_audit_summary.json`
- `analysis/outputs/metadata_feasibility_map.tsv`
- `analysis/outputs/cell_system_feasibility_with_ci.tsv`
- `analysis/outputs/threshold_sensitivity.tsv`
- `analysis/outputs/metadata_screening_flow.tsv`
- Figures in `outputs/figures_v2/`

Main finding: public CELLxGENE metadata support selected benchmark strata, but pan-tissue benchmarking should not be assumed without stratum-level donor, disease, age-label, and dataset checks.

### 2. Blood T-cell empirical benchmark

The blood T-cell benchmark has been upgraded from 5 seeds to 30 seeds.

Key settings:

- Census release: `2025-11-08`
- Stratum: blood T cells
- Young/old rule: numeric age `<=40` versus `>=60`
- Donors: 140 balanced donors in the full sample
- Disease-free subset: 140 balanced donors
- Seeds: `1301` through `1330`
- Hosted embeddings: scVI and TranscriptFormer TF-Sapiens

Key outputs:

- `analysis/upgrade_outputs/blood_tcell_30seed_results_long.tsv`
- `analysis/upgrade_outputs/blood_tcell_30seed_results_summary.tsv`
- `analysis/upgrade_outputs/paired_model_comparisons.tsv`
- `analysis/upgrade_outputs/blood_tcell_30seed_leakage_diagnostics.tsv`
- `outputs/upgrade_figures/figure4_blood_tcell_30seed_performance.png`
- `outputs/upgrade_figures/figure5_30seed_leakage_diagnostics.png`

Main result pattern:

- Random-cell AUROC remains high for metadata alone.
- Dataset-holdout AUROC is lower and highly variable.
- Disease-free donor-holdout performance is strongest for donor-mean embeddings.
- Donor-level aggregation improves performance relative to cell-level embeddings.

### 3. Dataset-level and confounding diagnostics

Leave-one-dataset-out diagnostics were added.

Key outputs:

- `analysis/upgrade_outputs/lodo_dataset_holdout_metrics.tsv`
- `analysis/upgrade_outputs/lodo_dataset_exclusions.tsv`
- `outputs/upgrade_figures/figure7_lodo_dataset_holdout.png`

Main finding: only one dataset met the strict LODO requirement of having both young and old donors in the held-out set. Most datasets were excluded because age classes were too imbalanced.

Confounding diagnostics were also added.

Key outputs:

- `analysis/upgrade_outputs/confounding_age_by_dataset_id.tsv`
- `analysis/upgrade_outputs/confounding_age_by_disease.tsv`
- `analysis/upgrade_outputs/confounding_age_by_assay.tsv`
- `analysis/upgrade_outputs/confounding_age_by_sex.tsv`
- `analysis/upgrade_outputs/metadata_only_coefficients.tsv`
- `analysis/upgrade_outputs/scvi_pca_source.tsv`
- `analysis/upgrade_outputs/transcriptformer_pca_source.tsv`
- `outputs/upgrade_figures/figure6_age_label_confounding_structure.png`
- `outputs/upgrade_figures/figure6b_metadata_coefficients.png`
- `outputs/upgrade_figures/figure6c_scvi_pca_confounding.png`
- `outputs/upgrade_figures/figure6c_transcriptformer_pca_confounding.png`

Main finding: age labels are visibly structured by dataset, assay, disease, and sex. This supports keeping the metadata-only baseline as a central benchmark comparator.

### 4. Sampling-depth sensitivity

Sampling-depth sensitivity was completed for donor-mean embeddings.

Key outputs:

- `analysis/upgrade_outputs/sampling_depth_sensitivity.tsv`
- `analysis/upgrade_outputs/sampling_depth_sensitivity_summary.tsv`
- `outputs/upgrade_figures/figure8_sampling_depth_sensitivity.png`

Main finding: performance improves from 1 to 8 cells per donor. The requested 16-cell point is capped by the existing eight-cell-per-donor benchmark sample and is therefore not a true deeper-sampling condition.

### 5. Extra-stratum feasibility

Non-blood-T-cell strata were audited for possible expansion.

Key outputs:

- `EXTRA_STRATUM_FEASIBILITY.md`
- `analysis/upgrade_outputs/extra_stratum_numeric_age_feasibility.tsv`

Current interpretation: several candidate strata exist, especially eye fibroblasts and lung/eye macrophages, but they have not yet been benchmarked with hosted embeddings. Their performance should not be reported until a second empirical extraction and 30-seed evaluation are completed.

### 6. Reproducibility package

The project now includes a basic reproducibility package.

Key files:

- `requirements.txt`
- `Makefile`
- `REPRODUCIBILITY_README.md`
- `OUTPUT_MANIFEST.tsv`
- `PROJECT_MANUSCRIPT_RULES.md`
- `CURRENT_UPGRADE_AUDIT.md`
- `STAGE_UPGRADE_SUMMARY.md`

Embedding arrays are cached under:

- `analysis/upgrade_outputs/embedding_cache/`

This cache is important because TranscriptFormer hosted embedding extraction is slow.

## Current manuscript framing

The manuscript is currently framed as:

> A donor-, disease-, and study-aware benchmark of CELLxGENE-hosted single-cell representations for human cellular aging.

Important wording choices:

- Use "CELLxGENE-hosted single-cell representations" or "hosted embeddings".
- Do not imply that Geneformer, scGPT, or all foundation models were directly benchmarked.
- Treat scVI and TranscriptFormer as the directly evaluated hosted representations.
- Treat blood T cells as the completed empirical benchmark stratum.
- Treat fibroblast/macrophage expansion as future work unless additional empirical runs are completed.

## Key limitations to keep visible

1. The completed empirical benchmark is limited to blood T cells.
2. Age is inferred from public `development_stage` labels, not a harmonized donor-age field.
3. Dataset-holdout and LODO are constrained by strong age-class imbalance across datasets.
4. Geneformer, scGPT, and other single-cell models were not directly run.
5. The 16-cell sampling-depth condition is capped by the existing eight-cell-per-donor sample.
6. The reference list is still short for submission.
7. GitHub/Zenodo archiving and DOI assignment have not yet been completed.

## Recommended next step

The highest-value next step is reference expansion and citation verification, followed by targeted Introduction and Discussion revision.

Suggested order:

1. Expand references from the current short list toward approximately 45-60 verified references.
2. Add sentence-level citations to Background and Discussion claims.
3. Keep Abstract citation-free.
4. Avoid adding unnecessary citations to Methods and Results.
5. Revise Introduction to be compact and gap-focused.
6. Revise Discussion to compare directly with prior work, while keeping claims conservative.

Secondary empirical option:

- Choose one additional stratum, preferably eye fibroblast or lung/eye macrophage, and run a second hosted-embedding benchmark only if time and remote embedding extraction are acceptable.

## Files to open first in the next working session

Recommended reading order:

1. `STAGE_UPGRADE_SUMMARY.md`
2. `CURRENT_PROJECT_STATUS.md`
3. `outputs/donor_disease_aware_sc_aging_submission_ready_v2.docx`
4. `analysis/upgrade_outputs/blood_tcell_30seed_results_summary.tsv`
5. `EXTRA_STRATUM_FEASIBILITY.md`
6. `PROJECT_MANUSCRIPT_RULES.md`

