# Submission Readiness Report

## Structure Diagnosis

- Abstract word count: 220
- Introduction word count: 535
- Discussion word count: 1107
- Discussion-to-Introduction ratio: 2.07
- Total reference count: 49
- Introduction citation count: 4
- Discussion citation count: 3

## Major Introduction Changes

The Introduction was compacted into four focused paragraphs: public single-cell resources; hosted representations and validation risk; donor/dataset/disease/metadata confounding; and the present leakage-aware benchmark contribution.

## Major Discussion Changes

The Discussion now centers on methodological interpretation: random-cell optimism, metadata-only performance, donor-level aggregation, limited dataset-transfer capacity, residual cohort effects after disease exclusion, and future benchmark requirements.

## Claims Softened or Removed

- Removed framing as a clinical aging-clock model.
- Avoided mechanism-discovery claims.
- Avoided pan-tissue validation claims.
- Avoided claims that Geneformer, scGPT, scFoundation, GeneCompass, or all foundation models were benchmarked.
- Recast LODO as a limited dataset-transfer diagnostic rather than external multicohort validation.

## Remaining Manual Checks

- Verify funding and author-contribution statements with all authors.
- Confirm whether ISCLS permits public repository and Zenodo details on the separate title page during double-blind review.
- Inspect Word document metadata in Microsoft Word before upload.
- Decide whether Figure 7 should remain in the main manuscript or move to supplementary material if the journal prefers 5-6 main figures.

## Render and Upload Package QA

- Blinded main manuscript PDF rendered successfully with 16 pages.
- Visual spot-checks of page 1 and page 16 showed no obvious blank page, truncation, or author-identifying information.
- Automated scan found no author names, correspondence email, GitHub username, Zenodo string, or DOI identifier in the blinded main manuscript or supplementary information.
- Optional/supplementary upload package created: `ISCLS_revision/ISCLS_optional_and_supplementary_files.zip`.

## Final Output Paths

- `ISCLS_revision/blinded_main_manuscript.docx`
- `ISCLS_revision/blinded_main_manuscript.pdf` (rendered after DOCX generation)
- `ISCLS_revision/title_page_with_author_details.docx`
- `ISCLS_revision/supplementary_information.docx`
- `ISCLS_revision/cover_letter.docx`
- `ISCLS_revision/journal_compliance_checklist.md`
- `ISCLS_revision/anonymization_audit.md`
- `ISCLS_revision/statistical_pipeline_audit.md`
- `ISCLS_revision/raw_expression_baseline_feasibility.md`
- `ISCLS_revision/figure_table_cross_reference_audit.md`
- `ISCLS_revision/reference_verification_report.md`
- `ISCLS_revision/ISCLS_REVISION_CHANGELOG.md`
- `ISCLS_revision/submission_readiness_report.md`

## Readiness Judgment

**READY WITH MINOR MANUAL CHECKS.** The scientific framing, double-blind files, title page, cover letter, and audit reports are prepared. Manual confirmation is still needed for funding, author contributions, local ethics policy, and whether repository/DOI disclosure should remain only on the title page during double-blind review.


## Figure Integration Update

New multipanel Figure 1 and Figure 2 from `figures/iscls_multpanel_figures/` were inserted into the blinded main manuscript. The previous detailed performance, metadata, LODO and sampling-depth figures were moved to the supplementary information as Supplementary Figures S1-S5.
