# Statistical Pipeline Audit

## Code Findings

- Standardization and logistic-regression fitting are implemented inside scikit-learn pipelines, so fitted transformations are learned from training folds.
- Metadata-only models use a ColumnTransformer/OneHotEncoder pipeline with `handle_unknown='ignore'`, preserving consistent train/test handling.
- Donor-holdout splitting groups all cells from one donor into a single partition.
- Grouped dataset-holdout uses dataset IDs as the grouping unit.
- No hyperparameter tuning uses the final test set.
- Label-shuffling permutes training labels while preserving the test labels and the split structure.
- Cell counts are reported separately from donor counts, and the manuscript avoids treating cells as independent donors.
- Thirty seeds are described as split-seed variability, not as 30 external cohorts.

## Metrics Available

AUROC, AUPRC, balanced accuracy, seed-matched paired differences, LODO diagnostics, and sampling-depth sensitivity are available in existing result files.

## Metrics Not Added

Brier score, calibration error, donor-level bootstrap, paired bootstrap, and donor-level permutation tests were not added because prediction-level probabilities were not stored in the current result package. Adding them requires rerunning the benchmark with prediction output retention.
