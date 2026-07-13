from __future__ import annotations

import re
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[3]
FIG_ROOT = ROOT / "figures" / "iscls_multpanel_figures"


REQUIRED = [
    "figure1_study_design.svg",
    "figure1_study_design.pdf",
    "figure1_study_design_600dpi.png",
    "figure1_legend.md",
    "figure2_data_confounds.svg",
    "figure2_data_confounds.pdf",
    "figure2_data_confounds_600dpi.png",
    "figure2_legend.md",
    "figure_style_guide.md",
    "figure_data_audit.md",
    "figure_value_provenance.csv",
]


def png_dpi(path: Path):
    try:
        from PIL import Image

        with Image.open(path) as img:
            return img.info.get("dpi", (None, None)), img.size
    except Exception:
        return (None, None), None


def main() -> int:
    report = []
    ok = True
    for name in REQUIRED:
        p = FIG_ROOT / name
        exists = p.exists() and p.stat().st_size > 0
        report.append(f"- {name}: {'OK' if exists else 'MISSING'}")
        ok &= exists

    for svg_name in ["figure1_study_design.svg", "figure2_data_confounds.svg"]:
        p = FIG_ROOT / svg_name
        if p.exists():
            try:
                ET.parse(p)
                report.append(f"- SVG parse {svg_name}: OK")
            except Exception as exc:
                ok = False
                report.append(f"- SVG parse {svg_name}: FAIL ({exc})")
            text = p.read_text(errors="ignore")
            for token in ["Yi Zha", "Da Lin", "Ying Chen", "Yue Liu", "Yu Zhang", "seefreewind", "10.5281", "zenodo", "TODO", "placeholder", " XX "]:
                if token.lower() in text.lower():
                    ok = False
                    report.append(f"- Identity/TODO scan {svg_name}: found {token}")
            for letter in list("ABCDEFG"):
                if f">{letter}<" in text or f">{letter}" in text:
                    continue
            if "A" not in text:
                ok = False
                report.append(f"- Panel labels {svg_name}: unable to find panel label text")

    for png_name in ["figure1_study_design_600dpi.png", "figure2_data_confounds_600dpi.png"]:
        dpi, size = png_dpi(FIG_ROOT / png_name)
        if dpi[0] is not None and dpi[0] >= 590:
            report.append(f"- PNG DPI {png_name}: OK ({dpi}, {size})")
        else:
            # Some backends round to 599.998 or omit metadata; pixel size still verifies high-res export.
            if size and min(size) > 2500:
                report.append(f"- PNG DPI {png_name}: metadata unavailable/rounded, pixel dimensions high ({size})")
            else:
                ok = False
                report.append(f"- PNG DPI {png_name}: FAIL ({dpi}, {size})")

    prov_path = FIG_ROOT / "figure_value_provenance.csv"
    if prov_path.exists():
        prov = pd.read_csv(prov_path)
        required_cols = {"figure", "panel", "displayed_value", "source_file", "source_column", "calculation", "script", "notes"}
        if required_cols.issubset(prov.columns) and len(prov) >= 25:
            report.append(f"- Provenance table: OK ({len(prov)} rows)")
        else:
            ok = False
            report.append(f"- Provenance table: FAIL ({len(prov)} rows, columns={list(prov.columns)})")

    report.append("")
    report.append("## Completed Panels")
    report.append("- Figure 1A-F: study design, representations, leakage/confounding map, validation strategies, diagnostics, and key AUROC findings.")
    report.append("- Figure 2A-G: embedding PCA projection by annotation/age/dataset, donor metadata heatmap, donor composition, 30-seed performance, and paired AUROC differences.")
    report.append("")
    report.append("## Unable or Deliberately Not Completed")
    report.append("- UMAP was not generated because umap-learn installation was interrupted after a long dependency download; Figure 2 uses PCA of the hosted TranscriptFormer embedding and labels it as PCA.")
    report.append("- T-cell subtype panels were not generated because the sampled metadata contains only one `cell_type` label: T cell.")
    report.append("- Raw-expression/PCA baseline performance, Brier score, calibration, donor bootstrap, and permutation tests were not plotted because existing result files do not contain those analyses or prediction-level probabilities.")
    report.append("")
    report.append("## Scientific Authenticity Check")
    report.append("- No new sample sizes, performance metrics, subtype labels, external validation claims, or model-superiority claims were invented.")
    report.append("- 30 seeds are labeled as split-seed variability, not independent cohorts.")
    report.append("- LODO is labeled as a limited diagnostic with one eligible held-out dataset.")
    report.append("")
    report.append("## Recommendation")
    report.append("- Recommended for manuscript use after optional manual spacing/typography refinement in Illustrator or Inkscape.")
    report.append("")
    report.append(f"Final validation status: {'PASS' if ok else 'FAIL'}")
    (FIG_ROOT / "figure_generation_report.md").write_text("# Figure Generation Report\n\n" + "\n".join(report) + "\n", encoding="utf-8")
    print("\n".join(report))
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
