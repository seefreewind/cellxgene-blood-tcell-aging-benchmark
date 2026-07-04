# Stage 25 humanized polishing and DOI update changelog

Date: 2026-07-04

## DOI update

- Added the Zenodo DOI to the manuscript Data Availability section: `https://doi.org/10.5281/zenodo.21188101`.
- Added the same Zenodo record to `README.md`.

## Language polishing

- Applied a humanizing pass to reduce formulaic phrasing, repetitive signposting, and defensive wording.
- Applied academic polishing to the Abstract, Background, Methods, Results, Discussion, Conclusions, and Data Availability sections.
- Shortened several overloaded sentences while preserving all numerical results.
- Kept terminology consistent: CELLxGENE Census, hosted embeddings, scVI, TranscriptFormer TF-Sapiens, metadata-only baseline, random-cell, donor-holdout, grouped dataset-holdout, LODO, and disease-free donor-holdout.

## Interpretation boundaries

- Preserved the benchmark framing and avoided clinical aging-clock claims.
- Retained the blood T-cell-only empirical scope.
- Kept Geneformer, scGPT, scFoundation, and GeneCompass as background context rather than directly benchmarked comparators.
- Maintained explicit limitations around public `development_stage` labels, LODO imbalance, lack of raw-expression benchmarking, and absence of manual external metadata harmonization.

## QA

- Rebuilt the Word manuscript.
- Rendered the DOCX to PDF and page PNGs.
- Checked the title page and Data Availability pages visually.
- Confirmed the Zenodo DOI appears in the rendered manuscript.
