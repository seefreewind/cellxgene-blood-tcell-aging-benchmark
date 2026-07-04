# Stage upgrade summary

## Completed upgrades

- Created `CURRENT_UPGRADE_AUDIT.md` documenting the previous 5-seed pilot baseline and upgrade gaps.
- Added `analysis/upgrade_blood_tcell_benchmark.py` and completed a 30-seed blood T-cell benchmark using fixed seeds 1301-1330.
- Generated mean, SD, and 95% CI summaries for AUROC, AUPRC, and balanced accuracy.
- Added paired model comparisons, leakage diagnostics, LODO diagnostics, confounding source tables, metadata-only coefficients, PCA source tables, and sampling-depth sensitivity.
- Cached hosted scVI and TranscriptFormer embeddings under `analysis/upgrade_outputs/embedding_cache/`.
- Created `EXTRA_STRATUM_FEASIBILITY.md` and `analysis/upgrade_outputs/extra_stratum_numeric_age_feasibility.tsv` for non-blood-T-cell expansion planning.
- Added reproducibility files: `requirements.txt`, `Makefile`, `REPRODUCIBILITY_README.md`, `OUTPUT_MANIFEST.tsv`, and `PROJECT_MANUSCRIPT_RULES.md`.
- Built the upgraded Word manuscript: `outputs/donor_disease_aware_sc_aging_submission_ready_v2.docx`.
- Rendered the Word manuscript for visual QA: `outputs/rendered_submission_ready_v2/`.

## Key result changes

- Random-cell AUROC remained high for metadata alone: 0.769 (95% CI 0.762-0.776).
- Random-cell AUROC was 0.749 (95% CI 0.744-0.754) for TranscriptFormer and 0.707 (95% CI 0.699-0.716) for scVI.
- Dataset-holdout performance was lower and more variable: 0.366 for metadata, 0.445 for TranscriptFormer, and 0.501 for scVI.
- Disease-free donor-holdout performance was stronger for donor-mean embeddings: 0.905 for TranscriptFormer and 0.802 for scVI.
- LODO evaluation was feasible for only one held-out dataset; 12 datasets were excluded for insufficient young/old balance.
- Sampling-depth sensitivity showed monotonic improvement from 1 to 8 cells per donor; the requested 16-cell point was capped by the eight-cell sample.

## Remaining limitations

- The completed empirical benchmark is still limited to blood T cells.
- Age is inferred from public development_stage labels rather than a harmonized donor-age field.
- Geneformer, scGPT, and other single-cell models were not directly run.
- Secondary fibroblast and macrophage strata require a second empirical extraction and 30-seed evaluation before performance can be reported.
- References remain intentionally conservative and should be expanded and verified before journal submission.
- Public GitHub/Zenodo archiving and DOI assignment remain to be done before external submission.

## Target journal positioning

- The manuscript is now closer to a completed benchmark research article than a Stage 1 protocol.
- The strongest near-term fit is a methods-oriented or data-resource-aware computational biology journal that accepts a carefully scoped public-data benchmark.
- A high-impact submission would require secondary-stratum replication, fuller reference expansion, and public repository archiving.

## Next-step checklist

- Run a second empirical benchmark for eye fibroblasts or lung/eye macrophages if remote embedding time is acceptable.
- Expand and verify the reference list toward approximately 45-60 references.
- Add author names, affiliations, funding, author contributions, and competing-interest declarations.
- Deposit scripts, summary tables, figure source data, and manuscript source files to GitHub and Zenodo.
- Replace placeholder repository language in Data Availability with a permanent URL and DOI.
