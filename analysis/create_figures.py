from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns


OUT = Path("outputs/figures")
OUT.mkdir(parents=True, exist_ok=True)

system = pd.read_csv("analysis/outputs/cell_system_feasibility_map.tsv", sep="\t")
tissue = pd.read_csv("analysis/outputs/metadata_feasibility_map.tsv", sep="\t")

sns.set_theme(style="whitegrid", context="paper")

fig, axes = plt.subplots(1, 2, figsize=(10, 4.2), constrained_layout=True)
system_plot = system.sort_values("donor_n", ascending=True)
colors = system_plot["feasibility_status"].map(
    {
        "eligible_stratum": "#2C7A7B",
        "pilot_candidate": "#D69E2E",
        "metadata_limited": "#718096",
        "not_recommended": "#A0AEC0",
    }
)
axes[0].barh(system_plot["cell_type"], system_plot["donor_n"], color=colors)
axes[0].set_xlabel("Unique donors")
axes[0].set_ylabel("")
axes[0].set_title("Donor coverage by target cell system")
for i, value in enumerate(system_plot["donor_n"]):
    axes[0].text(value + 40, i, f"{value:,}", va="center", fontsize=8)

axes[1].barh(system_plot["cell_type"], system_plot["disease_free_donor_fraction"], color=colors)
axes[1].axvline(0.5, color="#4A5568", linestyle="--", linewidth=1)
axes[1].set_xlim(0, 1)
axes[1].set_xlabel("Disease-free donor fraction")
axes[1].set_ylabel("")
axes[1].set_title("Disease-free donor retention")

fig.savefig(OUT / "figure1_cell_system_feasibility.png", dpi=300)
plt.close(fig)

eligible = tissue[tissue["feasibility_status"].eq("eligible_stratum")].head(18)
heat = eligible.pivot_table(
    index="tissue_general",
    columns="cell_type",
    values="donor_n",
    aggfunc="max",
    fill_value=0,
)
fig, ax = plt.subplots(figsize=(8.5, 5.5), constrained_layout=True)
sns.heatmap(
    heat,
    ax=ax,
    cmap="YlGnBu",
    annot=True,
    fmt=".0f",
    linewidths=0.4,
    linecolor="white",
    cbar_kws={"label": "Unique donors"},
)
ax.set_xlabel("Cell type")
ax.set_ylabel("Tissue")
ax.set_title("Top eligible tissue-cell strata in the metadata audit")
fig.savefig(OUT / "figure2_tissue_cell_feasibility_heatmap.png", dpi=300)
plt.close(fig)

