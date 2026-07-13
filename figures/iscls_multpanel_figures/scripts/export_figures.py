from __future__ import annotations

import json
import sys
from pathlib import Path

import pandas as pd

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from build_figure1 import build_figure1
from build_figure2 import build_figure2
from figure_common import BENCH, FIG_ROOT, ROOT, UPGRADE


def write_audit() -> None:
    sample = pd.read_csv(BENCH / "blood_tcell_embedding_sample_all.tsv", sep="\t")
    audit = json.loads((BENCH / "blood_tcell_embedding_benchmark_audit.json").read_text())
    scvi = UPGRADE / "embedding_cache" / "scvi_1075_a9ebd705da975e78.npz"
    tf = UPGRADE / "embedding_cache" / "transcriptformer_1075_a9ebd705da975e78.npz"
    rows = [
        ("Figure 1A", "Benchmark construction", "blood_tcell_embedding_benchmark_audit.json; blood_tcell_embedding_sample_all.tsv", "sample_all_cells, sample_all_donors, dataset_id, age_group, cell_type", f"{audit['sample_all_cells']} cells; {audit['sample_all_donors']} donors; {sample.dataset_id.nunique()} datasets", "Yes", "No major missing values for plotted fields", "No", "Low: descriptive counts only"),
        ("Figure 1B", "Representation/model schematic", "blood_tcell_embedding_benchmark_audit.json", "embeddings.name, embeddings.n_features", "scVI 50 features; TranscriptFormer 2048 features", "Yes", "Raw-expression baseline absent", "No", "Low: schematic only"),
        ("Figure 1C", "Risk map", "ISCLS manuscript audit framework", "risk/control descriptions", "10 risk classes mapped in manuscript", "Yes", "No quantitative input", "No", "Risk arrows labeled as potential pathways"),
        ("Figure 1D", "Validation strategies", "upgrade_audit.json; lodo_dataset_holdout_metrics.tsv", "seeds, dataset_id", "30 seeds; one eligible LODO dataset", "Yes", "LODO limited by class balance", "No", "Explicitly labels limited diagnostic"),
        ("Figure 1E", "Diagnostic controls", "results summary and audit reports", "available metrics and controls", "AUROC/AUPRC/balanced accuracy; metadata-only; disease-free; label shuffle; sampling depth", "Yes", "Brier/bootstrap/permutation absent", "No", "Absent analyses not displayed as completed"),
        ("Figure 1F", "Core AUROC summary", "blood_tcell_30seed_results_summary.tsv; lodo_dataset_holdout_metrics.tsv", "model, split, auroc_mean, ci columns", "30 seed summaries", "Yes", "Intervals are split variability", "No", "Does not call seeds external cohorts"),
        ("Figure 2A-C", "Embedding projection", "transcriptformer_1075_a9ebd705da975e78.npz; sample metadata", "X, cell_type, age_group, dataset_id", f"{scvi.exists()=}; {tf.exists()=}", "Yes", "T-cell subtype unavailable; PCA used instead of UMAP", "PCA computed for visualization", "Projection not used for model performance"),
        ("Figure 2D", "Donor metadata heatmap", "blood_tcell_embedding_sample_all.tsv", "donor_id, age_group, dataset_id, disease, sex, assay, soma_joinid", f"{sample.donor_id.nunique()} donors", "Yes", "Categorical encoding for visualization", "Donor-level aggregation", "No test-set information used"),
        ("Figure 2E", "Donor metadata composition", "blood_tcell_embedding_sample_all.tsv", "donor_id, age_group, disease, assay, sex", "Donor-level proportions", "Yes", "No T-cell subtype composition available", "Donor modes and proportions", "Avoids cell-weighting donors"),
        ("Figure 2F", "30-seed performance", "blood_tcell_30seed_results_long.tsv; summary.tsv", "auroc, model, split, seed", "30 seeds per displayed combination", "Yes", "Seed variability only", "No", "No independent cohort claim"),
        ("Figure 2G", "Paired differences", "paired_model_comparisons.tsv", "mean_auroc_difference_a_minus_b, ci95_low, ci95_high", "Seed-matched differences", "Yes", "Bootstrap/permutation not available", "No", "Zero-crossing intervals not called superiority"),
    ]
    out = ["# Figure Data Audit\n", "| Panel | Purpose | Data file(s) | Fields | Sample size/value | Directly drawable | Missingness/limits | Recalculation | Leakage concern |", "|---|---|---|---|---|---|---|---|---|"]
    for r in rows:
        out.append("| " + " | ".join(str(x) for x in r) + " |")
    (FIG_ROOT / "figure_data_audit.md").write_text("\n".join(out) + "\n", encoding="utf-8")
    # Uppercase compatibility path requested by user.
    (ROOT / "figures" / "FIGURE_DATA_AUDIT.md").write_text("\n".join(out) + "\n", encoding="utf-8")


def write_style_guide() -> None:
    (FIG_ROOT / "figure_style_guide.md").write_text(
        """# Figure Style Guide\n\n- Canvas: horizontal, journal-width multipanel figures, white background.\n- Font: sans-serif; SVG text is kept editable (`svg.fonttype = none`).\n- Minimum intended font size: approximately 6-7 pt for dense labels, with legends/captions carrying longer explanations.\n- Semantic colors: young = blue, old = red, scVI = green, TranscriptFormer = purple, metadata-only = gray, train = teal, test = orange, risk = muted red.\n- Figure 1 uses schematic modules and rounded boxes for workflow/risk-control logic.\n- Figure 2 uses data-derived plots from current metadata, hosted embeddings, and benchmark result tables.\n- No rainbow palettes, no official logos, no copied layouts, and no unsupported biological or clinical claims.\n""",
        encoding="utf-8",
    )


def main() -> None:
    FIG_ROOT.mkdir(parents=True, exist_ok=True)
    provenance = []
    provenance.extend(build_figure1())
    provenance.extend(build_figure2())
    pd.DataFrame(provenance).to_csv(FIG_ROOT / "figure_value_provenance.csv", index=False)
    write_audit()
    write_style_guide()


if __name__ == "__main__":
    main()
