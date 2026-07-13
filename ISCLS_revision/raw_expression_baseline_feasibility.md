# Raw Expression Baseline Feasibility

A traditional raw-expression baseline was **not added** to the ISCLS revision.

## Reason

The current reproducibility package contains metadata tables, hosted scVI and TranscriptFormer embedding caches, split-level result tables, and figures, but it does not package the exact raw expression matrix for the sampled CELLxGENE cells. A valid baseline would need the same cells, donors, labels, and splits used for the hosted-embedding benchmark.

## Required Train-Fold-Safe Workflow

1. Retrieve raw counts for the exact sampled cells.
2. Keep the same donor IDs, dataset IDs, age labels, and train/test splits.
3. Fit normalization, HVG selection, PCA, and logistic regression only within each training fold.
4. Evaluate cell-level and donor-level predictions with AUROC, AUPRC, and balanced accuracy.
5. Store prediction-level outputs to support donor bootstrap, permutation tests, Brier score, and calibration.

## Current Manuscript Treatment

The missing raw-expression baseline is listed in Table 2 as not available in the current release and is discussed as a major limitation. No expression-baseline performance was fabricated or inferred.
