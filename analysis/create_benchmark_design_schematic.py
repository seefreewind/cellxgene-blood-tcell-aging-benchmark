from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch


OUT = Path("outputs/upgrade_figures")
OUT.mkdir(parents=True, exist_ok=True)


def box(ax, xy, text, width=2.6, height=0.78, fc="#F3F6FA", ec="#4C78A8"):
    patch = FancyBboxPatch(
        xy,
        width,
        height,
        boxstyle="round,pad=0.04,rounding_size=0.06",
        linewidth=1.2,
        facecolor=fc,
        edgecolor=ec,
    )
    ax.add_patch(patch)
    ax.text(xy[0] + width / 2, xy[1] + height / 2, text, ha="center", va="center", fontsize=8.5)


def arrow(ax, start, end):
    ax.annotate("", xy=end, xytext=start, arrowprops=dict(arrowstyle="->", lw=1.1, color="#444444"))


def main() -> None:
    fig, ax = plt.subplots(figsize=(10.5, 5.8))
    ax.set_xlim(0, 10.5)
    ax.set_ylim(0, 5.8)
    ax.axis("off")

    box(ax, (0.35, 4.55), "CELLxGENE Census\npublic metadata", width=2.2)
    box(ax, (0.35, 3.35), "Blood T-cell\nnumeric-age stratum", width=2.2)
    box(ax, (0.35, 2.15), "Hosted embeddings\nscVI + TranscriptFormer", width=2.2)

    box(ax, (3.25, 4.55), "Random-cell split\napparent signal", width=2.25)
    box(ax, (3.25, 3.35), "Donor-holdout\ncontrols donor overlap", width=2.25)
    box(ax, (3.25, 2.15), "Grouped dataset-holdout\nstudy-shift diagnostic", width=2.25)
    box(ax, (3.25, 0.95), "Disease-free analysis\ndisease confounding check", width=2.25)

    box(ax, (6.2, 4.55), "Metadata-only baseline\nsource predictability", width=2.3, fc="#FFF7E6", ec="#C47F2C")
    box(ax, (6.2, 3.35), "Label shuffling\nspurious label control", width=2.3, fc="#FFF7E6", ec="#C47F2C")
    box(ax, (6.2, 2.15), "LODO feasibility\ncross-study balance check", width=2.3, fc="#FFF7E6", ec="#C47F2C")
    box(ax, (6.2, 0.95), "Sampling depth\ndonor-mean sensitivity", width=2.3, fc="#FFF7E6", ec="#C47F2C")

    box(ax, (8.95, 2.75), "Leakage-aware\nbenchmark readout", width=1.35, height=1.0, fc="#EAF4EA", ec="#4C8A4C")

    for y in [4.94, 3.74, 2.54]:
        arrow(ax, (2.55, y), (3.25, y))
    for y in [4.94, 3.74, 2.54, 1.34]:
        arrow(ax, (5.5, y), (6.2, y))
        arrow(ax, (8.5, y), (8.95, 3.25))
    arrow(ax, (1.45, 4.55), (1.45, 4.13))
    arrow(ax, (1.45, 3.35), (1.45, 2.93))
    arrow(ax, (2.55, 2.54), (3.25, 1.34))

    ax.text(
        0.35,
        0.35,
        "Each diagnostic asks whether prediction behavior persists after controlling for donor overlap, disease composition, study origin, metadata predictability, or sampling depth.",
        fontsize=8.5,
        color="#333333",
    )
    fig.savefig(OUT / "figure0_benchmark_design_schematic.png", dpi=300, bbox_inches="tight")
    plt.close(fig)


if __name__ == "__main__":
    main()
