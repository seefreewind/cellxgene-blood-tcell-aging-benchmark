from __future__ import annotations

import math
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns


ANALYSIS = Path("analysis/outputs")
FIGS = Path("outputs/figures_v2")
FIGS.mkdir(parents=True, exist_ok=True)


def wilson_ci(successes: int, total: int, z: float = 1.96) -> tuple[float, float]:
    if total == 0:
        return (0.0, 0.0)
    p = successes / total
    denom = 1 + z**2 / total
    centre = (p + z**2 / (2 * total)) / denom
    margin = z * math.sqrt((p * (1 - p) + z**2 / (4 * total)) / total) / denom
    return max(0.0, centre - margin), min(1.0, centre + margin)


system = pd.read_csv(ANALYSIS / "cell_system_feasibility_map.tsv", sep="\t")
tissue = pd.read_csv(ANALYSIS / "metadata_feasibility_map.tsv", sep="\t")
donor = pd.read_csv(ANALYSIS / "donor_level_metadata_summary.tsv", sep="\t")
summary = pd.read_json(ANALYSIS / "metadata_audit_summary.json", typ="series")

system_ci = system.copy()
cis = [wilson_ci(int(r.disease_free_donor_n), int(r.donor_n)) for r in system_ci.itertuples()]
system_ci["disease_free_ci_low"] = [x[0] for x in cis]
system_ci["disease_free_ci_high"] = [x[1] for x in cis]
system_ci.to_csv(ANALYSIS / "cell_system_feasibility_with_ci.tsv", sep="\t", index=False)

age_by_system = (
    donor.groupby(["cell_type", "age_group_proxy"], observed=True)["donor_id"]
    .nunique()
    .reset_index(name="donor_n")
)
age_by_system.to_csv(ANALYSIS / "age_proxy_distribution_by_cell_system.tsv", sep="\t", index=False)

sex_by_system = (
    donor.groupby(["cell_type", "sex"], observed=True)["donor_id"]
    .nunique()
    .reset_index(name="donor_n")
)
sex_by_system.to_csv(ANALYSIS / "sex_distribution_by_cell_system.tsv", sep="\t", index=False)

rows = []
for donor_min in [20, 25, 30, 35, 40]:
    for age_min in [5, 10, 15]:
        for disease_min in [0.30, 0.40, 0.50, 0.60]:
            eligible = tissue[
                (tissue["donor_n"] >= donor_min)
                & (tissue["young_or_adult_donor_n"] >= age_min)
                & (tissue["old_or_elderly_donor_n"] >= age_min)
                & (tissue["dataset_n"] >= 2)
                & (tissue["disease_free_donor_fraction"] >= disease_min)
            ]
            rows.append(
                {
                    "donor_min": donor_min,
                    "age_group_min": age_min,
                    "disease_free_min": disease_min,
                    "eligible_strata_n": len(eligible),
                    "eligible_tissue_n": eligible["tissue_general"].nunique(),
                    "eligible_cell_type_n": eligible["cell_type"].nunique(),
                }
            )
sensitivity = pd.DataFrame(rows)
sensitivity.to_csv(ANALYSIS / "threshold_sensitivity.tsv", sep="\t", index=False)

flow = pd.DataFrame(
    [
        {"step": "Target primary-cell metadata rows", "count": int(summary["target_primary_cell_rows"])},
        {"step": "Unique donors", "count": int(summary["unique_donors"])},
        {"step": "Unique datasets", "count": int(summary["unique_datasets"])},
        {"step": "Tissue-cell strata assessed", "count": int(len(tissue))},
        {"step": "Eligible tissue-cell strata", "count": int((tissue["feasibility_status"] == "eligible_stratum").sum())},
        {"step": "Pilot-candidate tissue-cell strata", "count": int((tissue["feasibility_status"] == "pilot_candidate").sum())},
    ]
)
flow.to_csv(ANALYSIS / "metadata_screening_flow.tsv", sep="\t", index=False)

sns.set_theme(style="whitegrid", context="paper")

fig, ax = plt.subplots(figsize=(7.8, 4.2), constrained_layout=True)
y = list(range(len(flow)))[::-1]
for yi, (_, row) in zip(y, flow.iterrows()):
    ax.text(0.5, yi, f"{row['step']}\n{row['count']:,}", ha="center", va="center", fontsize=9,
            bbox=dict(boxstyle="round,pad=0.45", facecolor="#F7FAFC", edgecolor="#2B6CB0", linewidth=1.2))
    if yi > 0:
        ax.annotate("", xy=(0.5, yi - 0.38), xytext=(0.5, yi - 0.62),
                    arrowprops=dict(arrowstyle="->", color="#4A5568", lw=1))
ax.set_xlim(0, 1)
ax.set_ylim(-0.6, len(flow) - 0.4)
ax.axis("off")
ax.set_title("Metadata screening flow for the Phase 0 audit", pad=12)
fig.savefig(FIGS / "figure1_metadata_screening_flow.png", dpi=300)
plt.close(fig)

baseline = sensitivity[
    (sensitivity["age_group_min"] == 10) & (sensitivity["disease_free_min"].isin([0.3, 0.4, 0.5, 0.6]))
]
fig, ax = plt.subplots(figsize=(7.4, 4.2), constrained_layout=True)
sns.lineplot(
    data=baseline,
    x="donor_min",
    y="eligible_strata_n",
    hue="disease_free_min",
    marker="o",
    palette="viridis",
    ax=ax,
)
ax.set_xlabel("Minimum donors per tissue-cell stratum")
ax.set_ylabel("Eligible tissue-cell strata")
ax.set_title("Threshold sensitivity at >=10 donors per age proxy group")
ax.legend(title="Disease-free threshold", loc="upper right")
fig.savefig(FIGS / "figure3_threshold_sensitivity.png", dpi=300)
plt.close(fig)

plot = system_ci.sort_values("donor_n", ascending=True)
fig, ax = plt.subplots(figsize=(7.2, 4.0), constrained_layout=True)
ax.errorbar(
    plot["disease_free_donor_fraction"],
    plot["cell_type"],
    xerr=[
        plot["disease_free_donor_fraction"] - plot["disease_free_ci_low"],
        plot["disease_free_ci_high"] - plot["disease_free_donor_fraction"],
    ],
    fmt="o",
    color="#2C7A7B",
    ecolor="#718096",
    capsize=3,
)
ax.axvline(0.5, color="#4A5568", linestyle="--", linewidth=1)
ax.set_xlim(0, 0.75)
ax.set_xlabel("Disease-free donor fraction with 95% Wilson CI")
ax.set_ylabel("")
ax.set_title("Uncertainty around disease-free donor retention")
fig.savefig(FIGS / "figure4_disease_free_ci.png", dpi=300)
plt.close(fig)

age_pivot = age_by_system.pivot_table(index="cell_type", columns="age_group_proxy", values="donor_n", fill_value=0)
age_pivot = age_pivot[[c for c in ["young_or_adult", "old_or_elderly", "annotated_other", "unknown"] if c in age_pivot.columns]]
fig, ax = plt.subplots(figsize=(7.4, 4.2), constrained_layout=True)
age_pivot.loc[system.sort_values("donor_n", ascending=False)["cell_type"]].plot(kind="bar", stacked=True, ax=ax, colormap="tab20c")
ax.set_xlabel("Cell system")
ax.set_ylabel("Unique donors")
ax.set_title("Age-proxy composition by target cell system")
ax.tick_params(axis="x", rotation=25)
fig.savefig(FIGS / "figure5_age_proxy_distribution.png", dpi=300)
plt.close(fig)

