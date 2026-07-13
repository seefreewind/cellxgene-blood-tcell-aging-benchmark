from __future__ import annotations

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib import patches
from matplotlib.gridspec import GridSpec
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler

from figure_common import (
    COLORS,
    FIG_ROOT,
    MODEL_COLORS,
    UPGRADE,
    add_provenance,
    load_core,
    mm_to_in,
    rounded_panel,
    save_figure,
    set_style,
)


SCRIPT = "figures/iscls_multpanel_figures/scripts/build_figure2.py"


def compute_projection(sample: pd.DataFrame) -> pd.DataFrame:
    x = np.load(UPGRADE / "embedding_cache" / "transcriptformer_1075_a9ebd705da975e78.npz")["X"]
    x = np.nan_to_num(x.astype(float), nan=0.0, posinf=0.0, neginf=0.0)
    z = StandardScaler().fit_transform(x)
    coords = PCA(n_components=2, svd_solver="full").fit_transform(z)
    out = sample.copy()
    out["PC1"] = coords[:, 0]
    out["PC2"] = coords[:, 1]
    return out


def scatter_panel(ax, df, color_col, palette, title, prov, panel, note=None):
    rounded_panel(ax, panel, title)
    vals = df[color_col].astype(str)
    for val in vals.unique():
        sub = df[vals == val]
        ax.scatter(sub["PC1"], sub["PC2"], s=5, alpha=0.72, lw=0, color=palette.get(val, "#9EA7AD"), label=val)
    ax.set_xlabel("TranscriptFormer PC1")
    ax.set_ylabel("TranscriptFormer PC2")
    ax.set_xticks([]); ax.set_yticks([])
    for spine in ax.spines.values():
        spine.set_visible(False)
    if len(vals.unique()) <= 6:
        ax.legend(frameon=False, loc="best", markerscale=1.8, handletextpad=0.2)
    if note:
        ax.text(0.02, 0.02, note, transform=ax.transAxes, fontsize=6.3, color=COLORS["ink"], ha="left", va="bottom")
    add_provenance(prov, "Figure 2", panel, f"{len(df)} cells projected", "analysis/upgrade_outputs/embedding_cache/transcriptformer_1075_a9ebd705da975e78.npz", "X", "standardize TranscriptFormer embedding then PCA(n=2)", SCRIPT)


def panel_d_heatmap(ax, sample, prov):
    rounded_panel(ax, "D", "Donor-level metadata structure")
    donor = sample.groupby("donor_id").agg(
        age_group=("age_group", lambda x: x.mode().iloc[0]),
        dataset_id=("dataset_id", lambda x: x.mode().iloc[0]),
        disease=("disease", lambda x: x.mode().iloc[0]),
        sex=("sex", lambda x: x.mode().iloc[0]),
        assay=("assay", lambda x: x.mode().iloc[0]),
        cell_count=("soma_joinid", "size"),
    ).reset_index()
    donor = donor.sort_values(["age_group", "dataset_id", "sex"]).reset_index(drop=True)
    cols = ["age_group", "dataset_id", "disease", "sex", "assay", "cell_count"]
    mat = []
    ylabels = ["age", "dataset", "disease", "sex", "assay", "cells"]
    for col in cols:
        if col == "cell_count":
            v = donor[col].astype(float)
            v = (v - v.min()) / max(1, (v.max() - v.min()))
        else:
            codes = pd.Categorical(donor[col]).codes.astype(float)
            v = codes / max(1, codes.max())
        mat.append(v)
    mat = np.vstack(mat)
    im = ax.imshow(mat, aspect="auto", cmap="viridis", interpolation="nearest", vmin=0, vmax=1)
    ax.set_yticks(range(len(ylabels)))
    ax.set_yticklabels(ylabels)
    ax.set_xticks([])
    ax.set_xlabel("Donors ordered by age group and dataset")
    ax.text(0.01, -0.18, f"{donor.shape[0]} donors; categorical variables encoded for structure display", transform=ax.transAxes, fontsize=6.1, color=COLORS["ink"])
    add_provenance(prov, "Figure 2", "D", f"{donor.shape[0]} donor columns", "analysis/benchmark_outputs/blood_tcell_embedding_sample_all.tsv", "donor_id", "groupby donor_id", SCRIPT)
    add_provenance(prov, "Figure 2", "D", "metadata heatmap variables: age,dataset,disease,sex,assay,cells", "analysis/benchmark_outputs/blood_tcell_embedding_sample_all.tsv", "age_group; dataset_id; disease; sex; assay; soma_joinid", "donor-level mode or count", SCRIPT)


def stacked_bar(ax, sample, prov):
    rounded_panel(ax, "E", "Donor-level metadata composition")
    donor = sample.groupby("donor_id").agg(
        age_group=("age_group", lambda x: x.mode().iloc[0]),
        disease=("disease", lambda x: x.mode().iloc[0]),
        assay=("assay", lambda x: x.mode().iloc[0]),
        sex=("sex", lambda x: x.mode().iloc[0]),
    ).reset_index()
    variables = ["disease", "assay", "sex"]
    x0 = np.arange(len(variables))
    width = 0.32
    colors = ["#4C78A8", "#F58518", "#54A24B", "#B279A2", "#9EA7AD"]
    for j, age in enumerate(["young", "old"]):
        sub = donor[donor["age_group"] == age]
        bottom = np.zeros(len(variables))
        for k in range(5):
            vals = []
            for var in variables:
                top = sub[var].value_counts(normalize=True).head(5)
                vals.append(top.iloc[k] if k < len(top) else 0)
            ax.bar(x0 + (j - 0.5) * width, vals, bottom=bottom, width=width, color=colors[k], edgecolor="white", lw=0.4)
            bottom += np.array(vals)
    ax.set_xticks(x0)
    ax.set_xticklabels(["disease", "assay", "sex"])
    ax.set_ylabel("Donor proportion")
    ax.set_ylim(0, 1.0)
    ax.legend(["rank 1", "rank 2", "rank 3", "rank 4", "rank 5"], frameon=False, loc="upper right", ncol=1, title="category rank")
    ax.text(0.05, -0.22, "Left bar: young; right bar: old. Proportions are donor-level, not cell-weighted.", transform=ax.transAxes, fontsize=6.1)
    for spine in ax.spines.values():
        spine.set_visible(False)
    ax.grid(axis="y", color="#E2E7EA", lw=0.5)
    add_provenance(prov, "Figure 2", "E", "donor-level disease/assay/sex proportions", "analysis/benchmark_outputs/blood_tcell_embedding_sample_all.tsv", "donor_id; age_group; disease; assay; sex", "mode per donor then proportions by age group", SCRIPT)


def performance_panel(ax, long, summary, prov):
    rounded_panel(ax, "F", "Performance across validation strategies")
    models = ["metadata_confounder_logistic", "scVI_embedding_logistic", "TranscriptFormer_embedding_logistic"]
    labels = ["Metadata-only", "scVI", "TranscriptFormer"]
    splits = ["random_cell", "donor_holdout", "dataset_holdout"]
    split_labels = ["Random", "Donor", "Dataset"]
    positions = np.arange(len(splits))
    offsets = [-0.22, 0, 0.22]
    for i, (model, lab) in enumerate(zip(models, labels)):
        for j, split in enumerate(splits):
            vals = long[(long["model"] == model) & (long["split"] == split)]["auroc"].values
            ax.scatter(np.full_like(vals, positions[j] + offsets[i], dtype=float), vals, s=7, alpha=0.20, color=MODEL_COLORS[lab], lw=0)
            row = summary[(summary["model"] == model) & (summary["split"] == split)].iloc[0]
            ax.errorbar(positions[j] + offsets[i], row.auroc_mean, yerr=[[row.auroc_mean-row.auroc_ci95_low], [row.auroc_ci95_high-row.auroc_mean]], fmt="o", color=MODEL_COLORS[lab], ms=3.2, capsize=2, lw=0.8)
            add_provenance(prov, "Figure 2", "F", f"{lab} {split} mean AUROC {row.auroc_mean:.3f}", "analysis/upgrade_outputs/blood_tcell_30seed_results_summary.tsv", "auroc_mean", "summary lookup", SCRIPT)
    ax.set_xticks(positions)
    ax.set_xticklabels(split_labels)
    ax.set_ylabel("AUROC")
    ax.set_ylim(0.15, 0.95)
    ax.grid(axis="y", color="#E2E7EA", lw=0.5)
    for spine in ax.spines.values():
        spine.set_visible(False)
    handles = [plt.Line2D([0], [0], marker="o", color="w", markerfacecolor=MODEL_COLORS[l], markersize=5, label=l) for l in labels]
    ax.legend(handles=handles, frameon=False, loc="lower left")


def paired_diff_panel(ax, paired, prov):
    rounded_panel(ax, "G", "Embedding AUROC minus metadata-only")
    rows = paired[
        paired["model_b"].eq("metadata_confounder_logistic")
        & paired["model_a"].isin(["scVI_embedding_logistic", "TranscriptFormer_embedding_logistic"])
        & paired["split"].isin(["random_cell", "donor_holdout", "dataset_holdout", "disease_free_donor_holdout"])
    ].copy()
    split_short = {
        "random_cell": "random",
        "donor_holdout": "donor",
        "dataset_holdout": "dataset",
        "disease_free_donor_holdout": "disease-free donor",
    }
    rows["label"] = rows["model_a"].map({"scVI_embedding_logistic": "scVI", "TranscriptFormer_embedding_logistic": "TF"}) + " | " + rows["split"].map(split_short)
    rows = rows.sort_values(["split", "model_a"])
    y = np.arange(rows.shape[0])
    for i, r in rows.reset_index(drop=True).iterrows():
        val = r["mean_auroc_difference_a_minus_b"]
        lo = r["ci95_low"]; hi = r["ci95_high"]
        color = MODEL_COLORS["TranscriptFormer"] if "TranscriptFormer" in r["label"] else MODEL_COLORS["scVI"]
        ax.errorbar(val, i, xerr=[[val - lo], [hi - val]], fmt="o", color=color, ms=3.2, capsize=2, lw=0.8)
        add_provenance(prov, "Figure 2", "G", f"{r['label']} AUROC difference {val:.3f}", "analysis/upgrade_outputs/paired_model_comparisons.tsv", "mean_auroc_difference_a_minus_b", "seed-matched model_a minus metadata-only", SCRIPT)
    ax.axvline(0, color="#333333", lw=0.7, ls="--")
    ax.set_yticks(y)
    ax.set_yticklabels(rows["label"].tolist(), fontsize=5.7)
    ax.set_xlabel("AUROC difference")
    ax.set_xlim(-0.18, 0.34)
    ax.grid(axis="x", color="#E2E7EA", lw=0.5)
    for spine in ax.spines.values():
        spine.set_visible(False)


def build_figure2() -> list[dict]:
    set_style()
    sample, summary, long, paired, lodo, depth = load_core()
    df = compute_projection(sample)
    prov: list[dict] = []
    fig = plt.figure(figsize=mm_to_in(190, 150), facecolor="white")
    ax_a = fig.add_axes([0.07, 0.68, 0.25, 0.22])
    ax_b = fig.add_axes([0.38, 0.68, 0.25, 0.22])
    ax_c = fig.add_axes([0.69, 0.68, 0.25, 0.22])
    ax_d = fig.add_axes([0.07, 0.39, 0.43, 0.19])
    ax_e = fig.add_axes([0.58, 0.39, 0.34, 0.19])
    ax_f = fig.add_axes([0.07, 0.08, 0.37, 0.22])
    ax_g = fig.add_axes([0.60, 0.08, 0.35, 0.22])
    scatter_panel(ax_a, df, "cell_type", {"T cell": "#61717A"}, "Embedding projection: cell annotation", prov, "A", "n = 1,075 cells; public label = T cell")
    scatter_panel(ax_b, df, "age_group", {"young": COLORS["young"], "old": COLORS["old"]}, "Donor-level age class", prov, "B", "Cells colored by donor-level age class")
    top = df["dataset_id"].value_counts().head(5).index
    df["dataset_group"] = np.where(df["dataset_id"].isin(top), "dataset " + (pd.Categorical(df["dataset_id"], categories=top).codes + 1).astype(str), "other")
    pal = {"dataset 1": "#4C78A8", "dataset 2": "#F58518", "dataset 3": "#54A24B", "dataset 4": "#B279A2", "dataset 5": "#72B7B2", "other": "#BAB0AC"}
    scatter_panel(ax_c, df, "dataset_group", pal, "Study-origin structure", prov, "C", "Top 5 datasets + other")
    panel_d_heatmap(ax_d, sample, prov)
    stacked_bar(ax_e, sample, prov)
    performance_panel(ax_f, long, summary, prov)
    paired_diff_panel(ax_g, paired, prov)
    fig.suptitle("Cellular landscape, cohort structure and sources of confounding", x=0.02, ha="left", fontsize=11, fontweight="bold", color=COLORS["ink"])
    save_figure(fig, "figure2_data_confounds")
    plt.close(fig)
    (FIG_ROOT / "figure2_legend.md").write_text(
        """# Figure 2. Cellular landscape, cohort structure and sources of confounding\n\n(A) Two-dimensional PCA projection of the cached TranscriptFormer hosted embedding for the 1,075-cell blood T-cell benchmark sample. The public metadata contains a single reported cell-type label, T cell; no T-cell subtype labels were available in the sampled metadata and none were inferred. (B) The same projection colored by donor-level age class. Cells inherit young or old labels from donor-level metadata. (C) The same projection colored by source dataset group, with the five largest datasets shown separately and remaining datasets grouped as other. (D) Donor-level metadata structure across age group, dataset, disease, sex, assay, and donor cell count. Categorical variables are encoded for structure display. (E) Donor-level metadata composition by age group for disease, assay, and sex; proportions are donor-level and not weighted by cell count. (F) AUROC across 30 repeated split seeds for metadata-only, scVI, and TranscriptFormer cell-level models under random-cell, donor-holdout, and grouped dataset-holdout validation. (G) Seed-matched AUROC differences for embedding models relative to metadata-only. Intervals crossing zero should be interpreted as compatible with limited incremental value rather than model superiority.\n""",
        encoding="utf-8",
    )
    return prov


if __name__ == "__main__":
    build_figure2()
