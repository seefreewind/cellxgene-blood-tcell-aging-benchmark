# Stage 24 submission-readiness changelog

Date: 2026-07-04

## Manuscript framing

- Revised the title to: "Leakage-aware evaluation of CELLxGENE-hosted single-cell embeddings for blood T-cell aging prediction".
- Sharpened the manuscript as a leakage-aware computational benchmark rather than a clinical aging-clock model.
- Maintained cautious interpretation and avoided new numerical claims beyond existing result files.

## Abstract and results interpretation

- Strengthened the Abstract to emphasize that random-cell evaluation can overestimate generalizable performance.
- Added the main metadata-only finding: metadata-only random-cell AUROC exceeded or matched the hosted embedding models under the easiest split.
- Added explicit interpretation that donor-, disease-, and dataset-aware diagnostics are necessary for public single-cell prediction benchmarks.

## Methods cleanup

- Removed duplicated overview text about LODO and sampling-depth sensitivity from the benchmark section.
- Kept a concise benchmark overview and a detailed diagnostic-analysis description.
- Retained the statement that repeated-seed confidence intervals quantify split variability rather than independent external-cohort uncertainty.

## Discussion revisions

- Replaced defensive phrasing with clearer study-boundary statements.
- Expanded interpretation of metadata-only baselines as evidence of source-variable predictability.
- Added that LODO feasibility is itself a diagnostic result showing limited cross-study validation capacity in public metadata.
- Added a paragraph clarifying that high disease-free donor-holdout AUROC does not remove residual dataset, assay, recruitment, cohort, or metadata-completeness effects.

## Figures and declarations

- Revised captions for Figures 1, 5, 6, 7, 9, and 10 to be more self-contained.
- Inserted author names, affiliations, correspondence email, and ORCID.
- Flagged unresolved placeholders for acknowledgements, author contributions, funding, GitHub URL, Zenodo DOI, and competing interests.

## Outputs

- Clean Word manuscript: `outputs/donor_disease_aware_sc_aging_submission_ready_v2.docx`
- Rendered QA PDF: `outputs/rendered_submission_ready_v2/donor_disease_aware_sc_aging_submission_ready_v2.pdf`
- Manuscript builder: `manuscript/build_submission_ready_benchmark_v2.py`
