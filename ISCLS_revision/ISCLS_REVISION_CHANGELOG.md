# ISCLS Revision Changelog

## Title Decision

Three candidate titles were considered:

1. A leakage-aware computational benchmark of hosted single-cell representations for blood T-cell aging prediction
2. Donor- and dataset-aware evaluation of hosted single-cell representations using blood T-cell aging prediction
3. A public-data audit framework for leakage and dataset shift in single-cell age prediction

Selected title: **A leakage-aware computational benchmark of hosted single-cell representations for blood T-cell aging prediction**.

## Major Changes

- Reframed the paper from a direct scVI-vs-TranscriptFormer comparison to a leakage-aware public-data audit framework.
- Rewrote the Abstract to emphasize random-cell inflation, metadata-only performance, donor-aware evaluation, dataset-transfer constraints, and the non-clinical benchmark scope.
- Rewrote the Introduction as a compact gap-focused rationale centered on public single-cell resources, hosted embeddings, leakage, metadata confounding, and validation design.
- Added a new Methods subsection and Table 1: leakage and confounding risk-control framework.
- Reordered Results around feasibility, random-cell optimism, donor-aware evaluation, metadata structure, disease-free/negative-control diagnostics, LODO feasibility, and sampling depth.
- Rewrote the Discussion to compare findings with prior validation, batch-effect, dataset-shift, and benchmark literature while preserving conservative study boundaries.
- Added a raw-expression baseline feasibility report rather than fabricating unsupported expression-baseline results.
- Created independent blinded manuscript, title page, supplementary information, cover letter, and audit reports for ISCLS submission preparation.
