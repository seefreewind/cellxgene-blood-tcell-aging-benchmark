# Stage 20 reference expansion and manuscript revision report

Date: 2026-07-01

## Scope

This stage revised the current manuscript builder:

- `manuscript/build_submission_ready_benchmark_v2.py`

and regenerated:

- `outputs/donor_disease_aware_sc_aging_submission_ready_v2.docx`
- `outputs/rendered_submission_ready_v2/donor_disease_aware_sc_aging_submission_ready_v2.pdf`
- `outputs/rendered_submission_ready_v2/page-*.png`

## Reference count

- Before Stage 20: 12 references.
- After Stage 20: 49 references.

The expanded reference list now covers:

- DNA methylation and molecular aging clocks.
- Single-cell aging atlases and aging resources.
- Human Cell Atlas, Human Cell Landscape, Tabula Sapiens, and CZ CELLxGENE Discover.
- scVI and scvi-tools.
- TranscriptFormer and related transcriptomic representation models.
- Single-cell preprocessing, batch correction, and atlas-level integration benchmarks.
- Reproducibility, prediction-model reporting, small-sample validation, and dataset-shift literature.

## Citation verification status

Automated `cite-verify` was attempted on 50 candidate references, but the local tool initially reported `network_unavailable` for Crossref lookup. One candidate without a DOI-backed traceable record was removed. A follow-up Stage 21 Crossref audit verified all 47 DOI-backed references and manually verified the two stable non-DOI venue references against JMLR and PMLR pages.

The two stable non-DOI venue references are:

- Scikit-learn in Journal of Machine Learning Research.
- WILDS in Proceedings of Machine Learning Research.

Remaining pre-submission action: optional reference-manager export QA before journal submission, mainly for style consistency rather than source existence.

## Claim audit

The Background and Discussion were audited for claims requiring citation support. Citation support was added for:

- Molecular clocks and aging-resource rationale.
- Single-cell aging atlas motivation.
- Public atlas and CELLxGENE infrastructure.
- Hosted and transferable single-cell representations.
- Batch effects, dataset structure, and integration artifacts.
- Dataset shift, small-sample validation, leakage, and biomedical machine-learning reporting.
- Reproducibility and sample-size transparency.

The Abstract remains citation-free. Methods and Results remain largely citation-free, except for the manuscript-level reference list supporting software, hosted data, and methodological context elsewhere.

## Introduction changes

The Introduction was rewritten to be more compact and gap-focused. The revised version now:

- Starts from molecular aging clocks and single-cell aging atlases.
- Moves quickly to the specific public-atlas benchmarking problem.
- Names the exact evaluated hosted representations: scVI and TranscriptFormer.
- Explicitly states that Geneformer, scGPT, scFoundation, GeneCompass, and related models are background only, not directly benchmarked.
- Motivates metadata-only baselines, donor-aware splitting, disease-free analysis, dataset-holdout evaluation, and confounding diagnostics.
- Frames the contribution as a completed blood T-cell empirical benchmark after a metadata feasibility audit.

## Discussion changes

The Discussion was revised to compare the results more directly with prior work. The revised version now emphasizes:

- Random-cell performance can be inflated by metadata and dataset structure.
- Dataset-holdout and LODO results are constrained by age-class imbalance across datasets.
- Donor-mean aggregation improved stability but does not prove a biological mechanism.
- Hosted embeddings are useful but require donor-aware, disease-aware, and study-aware evaluation.
- Public CELLxGENE metadata support selected benchmark strata but should not be assumed sufficient for pan-tissue aging benchmarks.
- The work should be interpreted as a completed blood T-cell benchmark, not a pan-tissue or all-model foundation-model comparison.

## Claims softened or removed

- Removed broad implication that all foundation models were evaluated.
- Replaced broad "foundation model benchmark" phrasing with "CELLxGENE-hosted scVI and TranscriptFormer representations."
- Kept Geneformer, scGPT, scFoundation, and GeneCompass only as related-work context.
- Softened donor-mean aggregation interpretation from biological mechanism to possible noise reduction and label-unit alignment.
- Preserved LODO as a constrained diagnostic rather than a strong cross-study validation result.

## Preserved limitations

The revised Discussion explicitly preserves the required limitations:

- The completed empirical benchmark is limited to blood T cells.
- Age is inferred from public `development_stage` labels rather than a harmonized donor-age field.
- Dataset-holdout and LODO are constrained by strong age-class imbalance.
- Geneformer, scGPT, scFoundation, GeneCompass, and other models were not directly run.
- The 16-cell sampling-depth condition is capped by the existing eight-cell-per-donor sample.
- GitHub/Zenodo DOI archiving is not yet complete.

## Render QA

The revised Word manuscript was rebuilt and rendered with the current bundled document renderer.

Rendered output:

- 20 PNG pages.
- PDF generated successfully.

Spot-checked pages:

- Page 1: title and Abstract.
- Page 3: revised Background with expanded citations.
- Page 17: declarations and data availability.
- Page 20: expanded References list.

No obvious missing figures, text overlap, or reference-list overflow was observed.

## Final output paths

- Word: `outputs/donor_disease_aware_sc_aging_submission_ready_v2.docx`
- PDF: `outputs/rendered_submission_ready_v2/donor_disease_aware_sc_aging_submission_ready_v2.pdf`
- Rendered pages: `outputs/rendered_submission_ready_v2/page-*.png`
- Updated builder: `manuscript/build_submission_ready_benchmark_v2.py`
- Stage report: `STAGE20_REFERENCE_REVISION_REPORT.md`
