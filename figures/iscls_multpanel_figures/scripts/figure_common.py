from __future__ import annotations

from pathlib import Path

import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[3]
FIG_ROOT = ROOT / "figures" / "iscls_multpanel_figures"
ANALYSIS = ROOT / "analysis"
UPGRADE = ANALYSIS / "upgrade_outputs"
BENCH = ANALYSIS / "benchmark_outputs"


COLORS = {
    "young": "#4C78A8",
    "old": "#E45756",
    "train": "#72B7B2",
    "test": "#F58518",
    "metadata": "#6B6B6B",
    "scvi": "#54A24B",
    "tf": "#B279A2",
    "raw": "#BAB0AC",
    "risk": "#D65F5F",
    "neutral": "#F4F6F8",
    "ink": "#263238",
    "line": "#61717A",
}

MODEL_LABELS = {
    "metadata_confounder_logistic": "Metadata-only",
    "scVI_embedding_logistic": "scVI",
    "TranscriptFormer_embedding_logistic": "TranscriptFormer",
    "scVI_mean_embedding_pseudobulk": "scVI donor mean",
    "TranscriptFormer_mean_embedding_pseudobulk": "TranscriptFormer donor mean",
}

MODEL_COLORS = {
    "Metadata-only": COLORS["metadata"],
    "scVI": COLORS["scvi"],
    "TranscriptFormer": COLORS["tf"],
    "scVI donor mean": "#7BC67E",
    "TranscriptFormer donor mean": "#C99BC0",
}


def set_style() -> None:
    mpl.rcParams.update(
        {
            "font.family": "sans-serif",
            "font.sans-serif": ["Arial", "Helvetica", "Liberation Sans", "DejaVu Sans"],
            "font.size": 7.2,
            "axes.titlesize": 8.2,
            "axes.labelsize": 7.2,
            "xtick.labelsize": 6.5,
            "ytick.labelsize": 6.5,
            "legend.fontsize": 6.5,
            "svg.fonttype": "none",
            "pdf.fonttype": 42,
            "ps.fonttype": 42,
            "axes.linewidth": 0.6,
            "lines.linewidth": 1.0,
        }
    )


def mm_to_in(width_mm: float, height_mm: float) -> tuple[float, float]:
    return width_mm / 25.4, height_mm / 25.4


def load_core():
    sample = pd.read_csv(BENCH / "blood_tcell_embedding_sample_all.tsv", sep="\t")
    summary = pd.read_csv(UPGRADE / "blood_tcell_30seed_results_summary.tsv", sep="\t")
    long = pd.read_csv(UPGRADE / "blood_tcell_30seed_results_long.tsv", sep="\t")
    paired = pd.read_csv(UPGRADE / "paired_model_comparisons.tsv", sep="\t")
    lodo = pd.read_csv(UPGRADE / "lodo_dataset_holdout_metrics.tsv", sep="\t")
    depth = pd.read_csv(UPGRADE / "sampling_depth_sensitivity_summary.tsv", sep="\t")
    return sample, summary, long, paired, lodo, depth


def rounded_panel(ax, label: str, title: str | None = None) -> None:
    ax.set_facecolor("white")
    for spine in ax.spines.values():
        spine.set_visible(False)
    ax.set_xticks([])
    ax.set_yticks([])
    ax.text(
        -0.04,
        1.04,
        label,
        transform=ax.transAxes,
        ha="left",
        va="bottom",
        fontsize=10,
        fontweight="bold",
        color=COLORS["ink"],
    )
    if title:
        ax.text(
            0.08,
            1.02,
            title,
            transform=ax.transAxes,
            ha="left",
            va="bottom",
            fontsize=8.2,
            fontweight="bold",
            color=COLORS["ink"],
        )


def save_figure(fig, stem: str) -> None:
    FIG_ROOT.mkdir(parents=True, exist_ok=True)
    fig.savefig(FIG_ROOT / f"{stem}.svg", bbox_inches="tight", pad_inches=0.03)
    fig.savefig(FIG_ROOT / f"{stem}.pdf", bbox_inches="tight", pad_inches=0.03)
    fig.savefig(FIG_ROOT / f"{stem}_600dpi.png", dpi=600, bbox_inches="tight", pad_inches=0.03)


def add_provenance(rows: list[dict], figure: str, panel: str, displayed_value: str, source_file: str, source_column: str, calculation: str, script: str, notes: str = "") -> None:
    rows.append(
        {
            "figure": figure,
            "panel": panel,
            "displayed_value": displayed_value,
            "source_file": source_file,
            "source_column": source_column,
            "calculation": calculation,
            "script": script,
            "notes": notes,
        }
    )


def mean_ci(summary: pd.DataFrame, model: str, split: str) -> tuple[float, float, float]:
    row = summary[(summary["model"] == model) & (summary["split"] == split)]
    if row.empty:
        return np.nan, np.nan, np.nan
    r = row.iloc[0]
    return float(r.auroc_mean), float(r.auroc_ci95_low), float(r.auroc_ci95_high)
