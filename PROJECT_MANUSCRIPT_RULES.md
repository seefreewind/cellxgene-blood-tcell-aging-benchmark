# Project manuscript rules

This file preserves the project-level manuscript standards applied to the single-cell aging benchmark draft.

## Scope and claims

- Report the work as a public-data benchmark of CELLxGENE-hosted single-cell representations.
- Do not claim that Geneformer, scGPT, or other models were benchmarked unless they are directly run.
- Use "hosted embeddings", "hosted representations", or model-specific names for scVI and TranscriptFormer.
- Treat blood T cells as the completed empirical benchmark stratum.
- Treat additional strata as feasibility-limited unless the same numeric-age, donor-aware, disease-aware workflow is completed.
- Avoid clinical utility, causal, diagnostic, therapeutic, or biological-mechanism claims beyond the benchmark data.

## Citation rules

- Do not include literature citations in the Abstract.
- Keep Methods and Results citation-free unless a method, software, dataset, or reporting standard explicitly requires a citation.
- Cite Background and Discussion claims with in-text markers.
- Use no more than three references for a single sentence.

## Benchmark reporting rules

- Report random-cell, donor-holdout, dataset-holdout, disease-free, label-shuffling, LODO, confounding, and sampling-depth diagnostics together.
- Report means, standard deviations, and 95% confidence intervals for repeated-seed metrics.
- Preserve failed or limited analyses, including LODO exclusions and extra-stratum feasibility limitations.
- Do not overwrite previous pilot outputs; write upgraded results under `analysis/upgrade_outputs/` and `outputs/upgrade_figures/`.

## Reproducibility rules

- Use CELLxGENE Census release `2025-11-08`.
- Use fixed seeds `1301` through `1330` for the 30-seed benchmark.
- Archive scripts, metric CSV/TSV files, figure source data, and generated figures before external submission.
