# Reproducibility README

## Environment

The upgraded benchmark was run in the project virtual environment with CELLxGENE Census release `2025-11-08`. Required Python packages are listed in `requirements.txt`.

Install or refresh dependencies:

```bash
.venv/bin/python -m pip install -r requirements.txt
```

## Main commands

Run the metadata audit and figure generation:

```bash
make audit
```

Run the upgraded 30-seed blood T-cell benchmark:

```bash
make upgrade
```

Build the Word manuscript:

```bash
make manuscript
```

Render the Word manuscript for visual QA:

```bash
make render
```

## Fixed analysis settings

- Census release: `2025-11-08`.
- Empirical stratum: blood T cells.
- Young/old rule: numeric age `<=40` versus `>=60`; middle-aged donors excluded.
- Repeated benchmark seeds: `1301` through `1330`.
- Main split families: random cell split, donor holdout, grouped dataset holdout, disease-free versions, label-shuffled controls, and leave-one-dataset-out diagnostics.
- Hosted embeddings: scVI and TranscriptFormer TF-Sapiens as exposed through CELLxGENE Census hosted embedding metadata.

## Output locations

- Metadata audit outputs: `analysis/outputs/`.
- Original pilot benchmark outputs: `analysis/benchmark_outputs/`.
- Upgraded benchmark outputs: `analysis/upgrade_outputs/`.
- Upgraded figures: `outputs/upgrade_figures/`.
- Manuscript output: `outputs/donor_disease_aware_sc_aging_submission_ready_v2.docx`.

## Known limitations

- TranscriptFormer embedding extraction is slow from the hosted TileDB object. The upgrade script caches full and chunked embedding arrays under `analysis/upgrade_outputs/embedding_cache/`.
- The 16-cell donor-depth sensitivity point is capped by the existing eight-cell-per-donor benchmark sample and is therefore identical to the eight-cell point.
- Additional non-blood-T-cell strata require further harmonization and embedding extraction before they can be reported as completed benchmarks.
