# Project-Level Manuscript Rules and Audit Checklist

Project: Donor- and disease-aware benchmarking of single-cell foundation models for human cellular aging

## Manuscript Format

- Default format: BMC Genomics-style Research Article unless a target journal is later specified.
- Required order: Title, Abstract, Keywords, Background, Methods, Results, Discussion, Conclusions, Supplementary Information, Acknowledgements, Authors' contributions, Funding, Availability of data and materials, Ethics approval and consent to participate, Consent for publication, Competing interests, References.
- Use in-text numbered reference markers in the main text.
- Do not invent analyses, sample sizes, model results, validation results, statistics, or references.
- Keep causal and clinical wording conservative. Public-data and machine-learning findings should be described as associations, signals, or benchmark results unless independently validated.

## Citation Rules

- Cite background, rationale, prior-work comparison, interpretation, and limitation claims sentence by sentence.
- Do not place literature citations in Methods or Results unless needed to identify a public resource, software framework, or benchmark source.
- Use approximately 50 references for a full research manuscript after final literature search, unless journal limits differ.

## Data Feasibility Rules

The first analytical stage is a metadata feasibility audit. The manuscript must not assume that pan-tissue benchmarking is possible until the audit supports it.

### Required CELLxGENE Census Metadata Fields

- donor_id
- dataset_id
- collection_id
- tissue
- cell_type
- disease
- assay
- sex
- development_stage or age-related field
- organism
- suspension_type
- is_primary_data

### Feasibility Tiers

Level A: Pan-tissue benchmark is allowed only if at least six tissues each contain at least two major cell types, each tissue-cell type stratum has at least 30 donors, young and old groups each include at least 10 donors, at least two independent datasets are represented, and a disease-free subset retains at least 50% of donors.

Level B: Three-system benchmark is allowed if at least two of immune, endothelial, and fibroblast/stromal systems satisfy donor and study criteria.

Level C: Immune-aging benchmark is allowed if immune cells are the only system with adequate donor, age, disease, and study metadata.

No-go: If donor, age, disease, or dataset metadata are insufficient, the study must be reframed as a data-availability audit or redirected to additional data sources.

## Benchmark Rules

- Required baseline models: pseudobulk ridge regression, pseudobulk elastic net, cell-level logistic regression, PCA plus linear model, and HVG mean-expression baseline.
- Foundation-model inference should use hosted or released embeddings by default. Full-scale de novo inference is optional and should be justified by a pilot.
- Required splits: random cell split, donor-holdout, dataset/study-holdout, disease-free or disease-stratified split, and label-shuffling/permutation baseline.
- Required metrics: MAE and Spearman correlation for age regression; AUROC, AUPRC, and balanced accuracy for young-old classification; generalization drop; permutation gap.

## Biological Interpretation Rules

Interpret only programs that remain stable across donor-holdout, study-holdout, and disease-free analyses.

A robust aging program should meet as many as possible of the following criteria:

- Same direction in at least two datasets.
- Same direction in at least two tissues or cell systems.
- Preserved in disease-free analyses.
- Overlap with HCATA, Aging Atlas, SenNet, or established senescence/aging signatures.

