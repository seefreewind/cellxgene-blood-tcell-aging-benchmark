# CELLxGENE-hosted blood T-cell aging benchmark

This repository contains the manuscript, analysis scripts, benchmark outputs, figures, and reproducibility materials for a leakage-aware evaluation of CELLxGENE-hosted scVI and TranscriptFormer embeddings for blood T-cell aging prediction.

The completed empirical benchmark is limited to blood T cells and evaluates public metadata-derived young-versus-old labels under random-cell, donor-holdout, grouped dataset-holdout, disease-free, label-shuffling, leave-one-dataset-out, confounding, and sampling-depth diagnostics.

The project does not directly benchmark Geneformer, scGPT, scFoundation, GeneCompass, or all single-cell foundation models. The outputs are not a clinically validated aging clock.

Archived record: https://doi.org/10.5281/zenodo.21188101

## Key files

- `manuscript/build_submission_ready_benchmark_v2.py`: builds the current Word manuscript.
- `outputs/donor_disease_aware_sc_aging_submission_ready_v2.docx`: clean revised Word manuscript.
- `outputs/rendered_submission_ready_v2/donor_disease_aware_sc_aging_submission_ready_v2.pdf`: rendered QA PDF.
- `analysis/upgrade_outputs/blood_tcell_30seed_results_summary.tsv`: 30-seed benchmark summary.
- `analysis/upgrade_outputs/lodo_dataset_exclusions.tsv`: LODO eligibility and exclusion diagnostics.
- `REPRODUCIBILITY_README.md`: reproducibility notes.
- `OUTPUT_MANIFEST.tsv`: output manifest.

## Rebuild

```bash
python manuscript/build_submission_ready_benchmark_v2.py
```

The manuscript uses existing result files in `analysis/outputs`, `analysis/benchmark_outputs`, and `analysis/upgrade_outputs`.
