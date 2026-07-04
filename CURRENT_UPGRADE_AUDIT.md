# Current upgrade audit

## Project baseline

- Existing manuscript: `outputs/donor_disease_aware_sc_aging_completed_pilot_v1.docx`.
- Existing pilot benchmark outputs: `analysis/benchmark_outputs/`.
- CELLxGENE Census release used by the project: `2025-11-08`.
- Metadata audit scope: 7,149,649 primary-cell metadata rows, 7,255 donors, 360 datasets, 193 collections, and 68 tissues across the target cell systems.
- Current empirical benchmark stratum: blood T cells with numeric age labels, 140 donors balanced as 70 young and 70 old.
- Current hosted representations: CELLxGENE-hosted scVI embeddings and CELLxGENE-hosted TranscriptFormer TF-Sapiens embeddings.

## Strengths already present

- The manuscript no longer relies only on a feasibility audit; it contains an empirical blood T-cell pilot benchmark.
- The benchmark already includes donor-holdout, dataset-holdout, disease-free donor-holdout, metadata-confounder baseline, and label-shuffling controls.
- The Phase 0 metadata audit includes threshold sensitivity and disease-free retention summaries.
- The manuscript already uses a BMC-style article skeleton with declarations and data availability.

## Priority gaps before this upgrade

1. The blood T-cell benchmark used only five repeated seeds, leaving uncertainty estimates thin.
2. Dataset-holdout was implemented as repeated grouped random dataset splits, but not as explicit leave-one-dataset-out diagnostics.
3. The manuscript describes metadata confounding but lacks a dedicated confounding figure and source tables.
4. Donor-level mean embedding performance was not stress-tested for sampling depth.
5. Additional strata were not empirically benchmarked, and infeasibility reasons were not documented in a standalone file.
6. Reproducibility files were incomplete for an external reviewer: no run-all target, manifest, fixed-output map, or clear seed record.
7. Manuscript wording still risked overclaiming "foundation model" scope despite directly using hosted scVI and TranscriptFormer embeddings only.

## Upgrade target

The next manuscript version should be framed as a completed, conservative benchmark of CELLxGENE-hosted single-cell representations in one robust numeric-age stratum, with transparent evidence that extension beyond blood T cells is limited by public metadata structure rather than author choice.
