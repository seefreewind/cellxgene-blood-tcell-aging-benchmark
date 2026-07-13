from __future__ import annotations

import json
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib import patches
from matplotlib.gridspec import GridSpec

from figure_common import (
    ANALYSIS,
    BENCH,
    COLORS,
    FIG_ROOT,
    MODEL_COLORS,
    add_provenance,
    load_core,
    mean_ci,
    mm_to_in,
    rounded_panel,
    save_figure,
    set_style,
)


SCRIPT = "figures/iscls_multpanel_figures/scripts/build_figure1.py"


def box(ax, xy, w, h, text, fc="#F4F6F8", ec="#B8C2C8", lw=0.8, fs=6.8, bold=False):
    patch = patches.FancyBboxPatch(
        xy,
        w,
        h,
        boxstyle="round,pad=0.012,rounding_size=0.025",
        fc=fc,
        ec=ec,
        lw=lw,
    )
    ax.add_patch(patch)
    ax.text(
        xy[0] + w / 2,
        xy[1] + h / 2,
        text,
        ha="center",
        va="center",
        fontsize=fs,
        fontweight="bold" if bold else "normal",
        color=COLORS["ink"],
        wrap=True,
    )
    return patch


def arrow(ax, start, end, color=None, dashed=False, lw=1.0):
    ax.annotate(
        "",
        xy=end,
        xytext=start,
        arrowprops=dict(
            arrowstyle="-|>",
            lw=lw,
            color=color or COLORS["line"],
            linestyle="--" if dashed else "-",
            shrinkA=2,
            shrinkB=2,
        ),
    )


def panel_a(ax, sample, audit, prov):
    rounded_panel(ax, "A", "Data source and benchmark construction")
    ax.set_xlim(0, 1); ax.set_ylim(0, 1)
    steps = [
        ("CELLxGENE\nCensus\n2025-11-08", 0.02, 0.61, 0.16, 0.22),
        ("Human blood\nmetadata", 0.22, 0.61, 0.15, 0.22),
        ("T-cell\nextraction", 0.42, 0.61, 0.14, 0.22),
        ("Donor-level\nfiltering", 0.61, 0.61, 0.14, 0.22),
        ("Young vs old\nage labels", 0.80, 0.61, 0.16, 0.22),
    ]
    for text, x, y, w, h in steps:
        box(ax, (x, y), w, h, text, fc="#EEF3F8", bold=x in (0.02, 0.80))
    for i in range(len(steps) - 1):
        _, x, y, w, h = steps[i]
        _, nx, ny, nw, nh = steps[i + 1]
        arrow(ax, (x + w, y + h / 2), (nx, ny + nh / 2))

    n_cells = int(audit["sample_all_cells"])
    n_donors = int(audit["sample_all_donors"])
    n_datasets = int(sample["dataset_id"].nunique())
    young = int(audit["sample_all_young_donors"])
    old = int(audit["sample_all_old_donors"])
    subtype = sample["cell_type"].nunique()
    box(
        ax,
        (0.13, 0.12),
        0.74,
        0.27,
        f"Final benchmark stratum\n{n_cells:,} cells | {n_donors} donors | {n_datasets} datasets\nAge groups: {young} young donors, {old} old donors\nCell annotation: T cell ({subtype} reported cell-type label)",
        fc="#FFF8E7",
        ec="#E8C878",
        fs=7.0,
        bold=True,
    )
    add_provenance(prov, "Figure 1", "A", f"{n_cells} cells", "analysis/benchmark_outputs/blood_tcell_embedding_benchmark_audit.json", "sample_all_cells", "read from audit JSON", SCRIPT)
    add_provenance(prov, "Figure 1", "A", f"{n_donors} donors", "analysis/benchmark_outputs/blood_tcell_embedding_benchmark_audit.json", "sample_all_donors", "read from audit JSON", SCRIPT)
    add_provenance(prov, "Figure 1", "A", f"{n_datasets} datasets", "analysis/benchmark_outputs/blood_tcell_embedding_sample_all.tsv", "dataset_id", "nunique", SCRIPT)
    add_provenance(prov, "Figure 1", "A", f"{young} young / {old} old donors", "analysis/benchmark_outputs/blood_tcell_embedding_benchmark_audit.json", "sample_all_young_donors; sample_all_old_donors", "read from audit JSON", SCRIPT)


def panel_b(ax, audit, prov):
    rounded_panel(ax, "B", "Representations and prediction models")
    ax.set_xlim(0, 1); ax.set_ylim(0, 1)
    box(ax, (0.04, 0.42), 0.18, 0.22, "Same cells\nsame donors\nsame labels", fc="#F4F6F8", bold=True)
    reps = [
        ("scVI\n50 features", COLORS["scvi"], 0.35, 0.73),
        ("TranscriptFormer\n2,048 features", COLORS["tf"], 0.35, 0.45),
        ("Metadata-only\nbaseline", COLORS["metadata"], 0.35, 0.17),
    ]
    for label, color, x, y in reps:
        box(ax, (x, y), 0.22, 0.17, label, fc=color + "22", ec=color, bold=True)
        arrow(ax, (0.22, 0.53), (x, y + 0.085), color=color)
        box(ax, (0.70, y), 0.21, 0.17, "Logistic\nregression", fc="#FFFFFF", ec=color)
        arrow(ax, (x + 0.22, y + 0.085), (0.70, y + 0.085), color=color)
    box(ax, (0.36, 0.00), 0.53, 0.10, "Cell-level prediction + donor-mean aggregation", fc="#EEF7F4", ec="#9BC7BD", fs=6.5)
    add_provenance(prov, "Figure 1", "B", "scVI 50 features", "analysis/benchmark_outputs/blood_tcell_embedding_benchmark_audit.json", "embeddings.n_features", "read scVI embedding dimension", SCRIPT)
    add_provenance(prov, "Figure 1", "B", "TranscriptFormer 2048 features", "analysis/benchmark_outputs/blood_tcell_embedding_benchmark_audit.json", "embeddings.n_features", "read tf-sapiens embedding dimension", SCRIPT)
    add_provenance(prov, "Figure 1", "B", "raw-expression baseline not shown", "ISCLS_revision/raw_expression_baseline_feasibility.md", "not applicable", "baseline absent in current release", SCRIPT)


def panel_c(ax, prov):
    rounded_panel(ax, "C", "Potential leakage/confounding pathway")
    ax.set_xlim(0, 1); ax.set_ylim(0, 1)
    nodes = {
        "Donor identity": (0.10, 0.72, "#EAF2FD"),
        "Repeated cells": (0.36, 0.72, "#EAF2FD"),
        "Random-cell overlap": (0.66, 0.72, "#FCEDEE"),
        "Dataset origin": (0.10, 0.46, "#EDF7EF"),
        "Assay / cohort": (0.36, 0.46, "#EDF7EF"),
        "Embedding structure": (0.66, 0.46, "#F6EFF8"),
        "Disease / sex": (0.10, 0.20, "#FFF4E5"),
        "Metadata labels": (0.36, 0.20, "#FFF4E5"),
        "Apparent age prediction": (0.66, 0.20, "#FCEDEE"),
    }
    for label, (x, y, c) in nodes.items():
        box(ax, (x, y), 0.20, 0.12, label, fc=c, fs=6.4, bold=label in ["Random-cell overlap", "Apparent age prediction"])
    arrows = [
        ("Donor identity", "Repeated cells", False),
        ("Repeated cells", "Random-cell overlap", True),
        ("Dataset origin", "Assay / cohort", False),
        ("Assay / cohort", "Embedding structure", True),
        ("Embedding structure", "Apparent age prediction", True),
        ("Disease / sex", "Metadata labels", False),
        ("Metadata labels", "Apparent age prediction", True),
    ]
    for a, b, dashed in arrows:
        x, y, _ = nodes[a]; nx, ny, _ = nodes[b]
        arrow(ax, (x + 0.20, y + 0.06), (nx, ny + 0.06), color=COLORS["risk"], dashed=dashed)
    ax.text(0.02, 0.02, "Dashed arrows mark audit targets, not proven causal mechanisms.", fontsize=6.2, color=COLORS["risk"])
    add_provenance(prov, "Figure 1", "C", "10 risk classes summarized", "ISCLS_revision/statistical_pipeline_audit.md", "narrative", "risk map derived from manuscript audit framework", SCRIPT)


def split_diagram(ax, x, title, warn=False):
    ax.text(x, 0.86, title, ha="center", va="top", fontsize=6.7, fontweight="bold", color=COLORS["ink"])
    for i in range(3):
        y = 0.65 - i * 0.16
        c_train = COLORS["train"] if not (warn and i == 1) else COLORS["train"]
        c_test = COLORS["test"]
        ax.add_patch(patches.Circle((x - 0.055, y), 0.025, fc=c_train, ec="white", lw=0.4))
        ax.add_patch(patches.Circle((x + 0.000, y + (0.025 if warn and i == 1 else 0)), 0.025, fc=c_test if warn and i == 1 else c_train, ec="white", lw=0.4))
        ax.add_patch(patches.Circle((x + 0.055, y), 0.025, fc=c_test if (i == 2 or title.startswith("Dataset") or title.startswith("LODO")) else c_train, ec="white", lw=0.4))
    ax.text(x - 0.065, 0.08, "train", color=COLORS["train"], ha="center", fontsize=6.0)
    ax.text(x + 0.065, 0.08, "test", color=COLORS["test"], ha="center", fontsize=6.0)
    if warn:
        ax.text(x, 0.17, "identity\nrisk", ha="center", va="center", fontsize=6.0, color=COLORS["risk"])


def panel_d(ax, prov):
    rounded_panel(ax, "D", "Validation strategies")
    ax.set_xlim(0, 1); ax.set_ylim(0, 1)
    split_diagram(ax, 0.13, "Random-cell", warn=True)
    split_diagram(ax, 0.38, "Donor-holdout")
    split_diagram(ax, 0.63, "Dataset-holdout")
    split_diagram(ax, 0.87, "LODO\nlimited diagnostic")
    add_provenance(prov, "Figure 1", "D", "30 repeated seeds", "analysis/upgrade_outputs/upgrade_audit.json", "seeds", "count seeds", SCRIPT)
    add_provenance(prov, "Figure 1", "D", "limited LODO diagnostic", "analysis/upgrade_outputs/lodo_dataset_holdout_metrics.tsv", "dataset_id", "one eligible held-out dataset", SCRIPT)


def panel_e(ax, prov):
    rounded_panel(ax, "E", "Diagnostic controls and metrics")
    ax.set_xlim(0, 1); ax.set_ylim(0, 1)
    rows = [
        ("Donor leakage", "Donor-holdout", "AUROC/AUPRC/BA"),
        ("Metadata confounding", "Metadata-only", "Incremental value"),
        ("Disease confounding", "Disease-free", "Sensitivity"),
        ("Label leakage", "Label shuffling", "Negative control"),
        ("Cells per donor", "Sampling depth", "Stability"),
        ("Split instability", "30 seeds", "Paired difference"),
    ]
    for i, (risk, control, metric) in enumerate(rows):
        y = 0.84 - i * 0.135
        box(ax, (0.03, y - 0.04), 0.26, 0.08, risk, fc="#FCEDEE", ec="#F1B7B7", fs=6.3)
        arrow(ax, (0.30, y), (0.39, y), color=COLORS["line"])
        box(ax, (0.40, y - 0.04), 0.25, 0.08, control, fc="#EEF3F8", ec="#B8C2C8", fs=6.3, bold=True)
        arrow(ax, (0.66, y), (0.74, y), color=COLORS["line"])
        box(ax, (0.75, y - 0.04), 0.21, 0.08, metric, fc="#EEF7F4", ec="#B8D8C8", fs=6.1)
    add_provenance(prov, "Figure 1", "E", "AUROC, AUPRC, balanced accuracy", "analysis/upgrade_outputs/blood_tcell_30seed_results_summary.tsv", "auroc_mean; auprc_mean; balanced_accuracy_mean", "available metrics", SCRIPT)
    add_provenance(prov, "Figure 1", "E", "Brier/calibration not displayed", "ISCLS_revision/statistical_pipeline_audit.md", "not applicable", "prediction-level scores unavailable", SCRIPT)


def panel_f(ax, summary, lodo, prov):
    rounded_panel(ax, "F", "Key benchmark findings")
    splits = ["random_cell", "donor_holdout", "dataset_holdout", "disease_free_donor_holdout"]
    split_labels = ["Random-cell", "Donor", "Dataset", "Disease-free"]
    models = [
        ("metadata_confounder_logistic", "Metadata-only"),
        ("scVI_embedding_logistic", "scVI"),
        ("TranscriptFormer_embedding_logistic", "TranscriptFormer"),
    ]
    y_positions = np.arange(len(splits))[::-1]
    offsets = [-0.16, 0.0, 0.16]
    for m_i, (model, label) in enumerate(models):
        vals = []
        lows = []
        highs = []
        for split in splits:
            v, lo, hi = mean_ci(summary, model, split)
            vals.append(v); lows.append(lo); highs.append(hi)
            add_provenance(prov, "Figure 1", "F", f"{label} {split} AUROC {v:.3f}", "analysis/upgrade_outputs/blood_tcell_30seed_results_summary.tsv", "auroc_mean", "model/split lookup", SCRIPT)
        y = y_positions + offsets[m_i]
        xerr = [np.array(vals) - np.array(lows), np.array(highs) - np.array(vals)]
        ax.errorbar(vals, y, xerr=xerr, fmt="o", ms=3.2, lw=0.8, capsize=1.8, label=label, color=MODEL_COLORS[label])
    ax.set_yticks(y_positions)
    ax.set_yticklabels(split_labels)
    ax.set_xlabel("AUROC")
    ax.set_xlim(0.20, 0.86)
    ax.grid(axis="x", color="#E2E7EA", lw=0.5)
    for spine in ax.spines.values():
        spine.set_visible(False)
    ax.legend(frameon=False, loc="upper center", bbox_to_anchor=(0.55, -0.08), ncol=3, handletextpad=0.4, columnspacing=0.9)
    notes = "Key patterns:\n• random-cell optimistic\n• metadata structure predictive\n• donor/dataset-aware estimates changed"
    ax.text(0.02, 0.02, notes, transform=ax.transAxes, fontsize=5.8, color=COLORS["ink"], ha="left", va="bottom")
    lodo_n = lodo["dataset_id"].nunique()
    add_provenance(prov, "Figure 1", "F", f"{lodo_n} eligible LODO dataset", "analysis/upgrade_outputs/lodo_dataset_holdout_metrics.tsv", "dataset_id", "nunique", SCRIPT)


def build_figure1() -> list[dict]:
    set_style()
    sample, summary, long, paired, lodo, depth = load_core()
    audit = json.loads((BENCH / "blood_tcell_embedding_benchmark_audit.json").read_text())
    prov: list[dict] = []

    fig = plt.figure(figsize=mm_to_in(190, 138), facecolor="white")
    gs = GridSpec(3, 6, figure=fig, height_ratios=[1.0, 1.0, 1.05], hspace=0.55, wspace=0.48, left=0.045, right=0.985, top=0.91, bottom=0.06)
    axes = [
        fig.add_subplot(gs[0, 0:3]),
        fig.add_subplot(gs[0, 3:6]),
        fig.add_subplot(gs[1, 0:3]),
        fig.add_subplot(gs[1, 3:6]),
        fig.add_subplot(gs[2, 0:3]),
        fig.add_subplot(gs[2, 3:6]),
    ]
    panel_a(axes[0], sample, audit, prov)
    panel_b(axes[1], audit, prov)
    panel_c(axes[2], prov)
    panel_d(axes[3], prov)
    panel_e(axes[4], prov)
    panel_f(axes[5], summary, lodo, prov)
    fig.suptitle("Study design and leakage-aware evaluation framework", x=0.02, ha="left", fontsize=11, fontweight="bold", color=COLORS["ink"])
    save_figure(fig, "figure1_study_design")
    plt.close(fig)

    legend = FIG_ROOT / "figure1_legend.md"
    legend.write_text(
        """# Figure 1. Study design and leakage-aware evaluation framework\n\n(A) Construction of the blood T-cell benchmark stratum from public CELLxGENE metadata and hosted embeddings. The final sample contains 1,075 cells from 140 donors and 13 datasets, with 70 young and 70 old donors. The public metadata contains a single reported cell-type label, T cell, for the benchmark stratum. (B) Fixed hosted representations and the metadata-only baseline evaluated with logistic regression at cell level and with donor-mean aggregation. scVI has 50 features and TranscriptFormer has 2,048 features in the cached embeddings. No raw-expression baseline was available in the current release. (C) Potential leakage and confounding pathways considered in the audit. Dashed arrows mark diagnostic targets, not proven causal mechanisms. (D) Validation strategies used to contrast random-cell, donor-holdout, grouped dataset-holdout, and limited LODO diagnostics. (E) Diagnostic controls and metrics mapped to benchmark risks. (F) Core AUROC estimates across validation designs for metadata-only, scVI, and TranscriptFormer models. Intervals describe 30 split-seed variability, not independent-cohort uncertainty.\n""",
        encoding="utf-8",
    )
    return prov


if __name__ == "__main__":
    build_figure1()
