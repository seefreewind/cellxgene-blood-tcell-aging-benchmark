# Figure Generation Report

- figure1_study_design.svg: OK
- figure1_study_design.pdf: OK
- figure1_study_design_600dpi.png: OK
- figure1_legend.md: OK
- figure2_data_confounds.svg: OK
- figure2_data_confounds.pdf: OK
- figure2_data_confounds_600dpi.png: OK
- figure2_legend.md: OK
- figure_style_guide.md: OK
- figure_data_audit.md: OK
- figure_value_provenance.csv: OK
- SVG parse figure1_study_design.svg: OK
- SVG parse figure2_data_confounds.svg: OK
- PNG DPI figure1_study_design_600dpi.png: OK ((599.9988, 599.9988), (4366, 3210))
- PNG DPI figure2_data_confounds_600dpi.png: OK ((599.9988, 599.9988), (4359, 3330))
- Provenance table: OK (48 rows)

## Completed Panels
- Figure 1A-F: study design, representations, leakage/confounding map, validation strategies, diagnostics, and key AUROC findings.
- Figure 2A-G: embedding PCA projection by annotation/age/dataset, donor metadata heatmap, donor composition, 30-seed performance, and paired AUROC differences.

## Unable or Deliberately Not Completed
- UMAP was not generated because umap-learn installation was interrupted after a long dependency download; Figure 2 uses PCA of the hosted TranscriptFormer embedding and labels it as PCA.
- T-cell subtype panels were not generated because the sampled metadata contains only one `cell_type` label: T cell.
- Raw-expression/PCA baseline performance, Brier score, calibration, donor bootstrap, and permutation tests were not plotted because existing result files do not contain those analyses or prediction-level probabilities.

## Scientific Authenticity Check
- No new sample sizes, performance metrics, subtype labels, external validation claims, or model-superiority claims were invented.
- 30 seeds are labeled as split-seed variability, not independent cohorts.
- LODO is labeled as a limited diagnostic with one eligible held-out dataset.

## Recommendation
- Recommended for manuscript use after optional manual spacing/typography refinement in Illustrator or Inkscape.

Final validation status: PASS
