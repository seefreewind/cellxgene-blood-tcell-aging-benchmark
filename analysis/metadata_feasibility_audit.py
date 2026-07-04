from __future__ import annotations

import argparse
import json
from pathlib import Path

import pandas as pd


REQUIRED_COLUMNS = [
    "soma_joinid",
    "dataset_id",
    "assay",
    "tissue",
    "tissue_general",
    "cell_type",
    "cell_type_ontology_term_id",
    "disease",
    "disease_ontology_term_id",
    "sex",
    "development_stage",
    "development_stage_ontology_term_id",
    "donor_id",
    "suspension_type",
    "is_primary_data",
]

TARGET_CELL_TYPES = [
    "T cell",
    "monocyte",
    "macrophage",
    "endothelial cell",
    "fibroblast",
]


def classify_age_label(value: object) -> str:
    text = str(value).lower()
    if not text or text == "nan":
        return "unknown"
    young_tokens = ["young", "adult stage", "20", "30", "40"]
    old_tokens = ["old", "elderly", "60", "70", "80", "90", "100"]
    if any(token in text for token in young_tokens):
        return "young_or_adult"
    if any(token in text for token in old_tokens):
        return "old_or_elderly"
    return "annotated_other"


def assign_feasibility(row: pd.Series) -> str:
    donors = row["donor_n"]
    young = row["young_or_adult_donor_n"]
    old = row["old_or_elderly_donor_n"]
    datasets = row["dataset_n"]
    disease_free_fraction = row["disease_free_donor_fraction"]

    if donors >= 30 and young >= 10 and old >= 10 and datasets >= 2 and disease_free_fraction >= 0.5:
        return "eligible_stratum"
    if donors >= 15 and datasets >= 2 and disease_free_fraction >= 0.3:
        return "pilot_candidate"
    if donors >= 10:
        return "metadata_limited"
    return "not_recommended"


def add_age_counts(base: pd.DataFrame, donor_level: pd.DataFrame, keys: list[str]) -> pd.DataFrame:
    age_counts = (
        donor_level.groupby(keys + ["age_group_proxy"], dropna=False, observed=True)["donor_id"]
        .nunique()
        .unstack(fill_value=0)
        .reset_index()
    )
    for col in ["young_or_adult", "old_or_elderly", "annotated_other", "unknown"]:
        if col not in age_counts.columns:
            age_counts[col] = 0
        age_counts[f"{col}_donor_n"] = age_counts[col]
    keep = keys + [
        "young_or_adult_donor_n",
        "old_or_elderly_donor_n",
        "annotated_other_donor_n",
        "unknown_donor_n",
    ]
    return base.merge(age_counts[keep], on=keys, how="left")


def add_disease_free_counts(base: pd.DataFrame, donor_level: pd.DataFrame, keys: list[str]) -> pd.DataFrame:
    disease_free = (
        donor_level[
            donor_level["disease"].astype(str).str.lower().isin(["normal", "healthy"])
        ]
        .groupby(keys, dropna=False, observed=True)["donor_id"]
        .nunique()
        .reset_index(name="disease_free_donor_n")
    )
    out = base.merge(disease_free, on=keys, how="left")
    out["disease_free_donor_fraction"] = (
        out["disease_free_donor_n"].fillna(0) / out["donor_n"].replace(0, pd.NA)
    ).fillna(0)
    return out


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", default="analysis/outputs")
    parser.add_argument("--census-version", default="2025-11-08")
    parser.add_argument("--target-cell-types", nargs="*", default=TARGET_CELL_TYPES)
    args = parser.parse_args()

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    try:
        import cellxgene_census
    except ImportError as exc:
        raise SystemExit("cellxgene_census is not installed in this environment") from exc

    with cellxgene_census.open_soma(census_version=args.census_version) as census:
        summary_cell_counts = (
            census["census_info"]["summary_cell_counts"].read().concat().to_pandas()
        )
        datasets = census["census_info"]["datasets"].read().concat().to_pandas()
        obs = census["census_data"]["homo_sapiens"].obs
        columns = [column for column in REQUIRED_COLUMNS if column in obs.schema.names]
        cell_filter = " or ".join([f"cell_type == '{label}'" for label in args.target_cell_types])
        value_filter = f"is_primary_data == True and ({cell_filter})"
        metadata = obs.read(value_filter=value_filter, column_names=columns).concat().to_pandas()

    metadata = metadata.merge(
        datasets[["dataset_id", "collection_id", "collection_name", "dataset_title"]],
        on="dataset_id",
        how="left",
    )
    metadata["age_group_proxy"] = metadata["development_stage"].map(classify_age_label)

    donor_level = (
        metadata.groupby(
            [
                "tissue_general",
                "cell_type",
                "donor_id",
                "dataset_id",
                "collection_id",
                "assay",
                "disease",
                "sex",
                "development_stage",
                "age_group_proxy",
            ],
            dropna=False,
            observed=True,
        )
        .size()
        .reset_index(name="cell_n")
    )

    tissue_cell = (
        donor_level.groupby(["tissue_general", "cell_type"], dropna=False, observed=True)
        .agg(
            donor_n=("donor_id", "nunique"),
            cell_n=("cell_n", "sum"),
            dataset_n=("dataset_id", "nunique"),
            collection_n=("collection_id", "nunique"),
            assay_n=("assay", "nunique"),
            disease_n=("disease", "nunique"),
        )
        .reset_index()
    )
    tissue_cell = add_age_counts(tissue_cell, donor_level, ["tissue_general", "cell_type"])
    tissue_cell = add_disease_free_counts(tissue_cell, donor_level, ["tissue_general", "cell_type"])
    tissue_cell["feasibility_status"] = tissue_cell.apply(assign_feasibility, axis=1)
    tissue_cell = tissue_cell.sort_values(
        ["feasibility_status", "donor_n", "dataset_n", "cell_n"],
        ascending=[True, False, False, False],
    )

    cell_system = (
        donor_level.groupby("cell_type", dropna=False, observed=True)
        .agg(
            donor_n=("donor_id", "nunique"),
            cell_n=("cell_n", "sum"),
            tissue_n=("tissue_general", "nunique"),
            dataset_n=("dataset_id", "nunique"),
            collection_n=("collection_id", "nunique"),
            assay_n=("assay", "nunique"),
            disease_n=("disease", "nunique"),
        )
        .reset_index()
    )
    cell_system = add_age_counts(cell_system, donor_level, ["cell_type"])
    cell_system = add_disease_free_counts(cell_system, donor_level, ["cell_type"])
    cell_system["feasibility_status"] = cell_system.apply(assign_feasibility, axis=1)

    global_counts = summary_cell_counts[
        summary_cell_counts["organism"].astype(str).eq("homo_sapiens")
    ].copy()
    target_cell_counts = (
        global_counts[
            (global_counts["category"].astype(str).eq("cell_type"))
            & (global_counts["label"].isin(args.target_cell_types))
        ]
        .sort_values("total_cell_count", ascending=False)
    )

    summary = {
        "census_version": args.census_version,
        "target_cell_types": args.target_cell_types,
        "target_primary_cell_rows": int(len(metadata)),
        "unique_donors": int(metadata["donor_id"].nunique(dropna=True)),
        "unique_datasets": int(metadata["dataset_id"].nunique(dropna=True)),
        "unique_collections": int(metadata["collection_id"].nunique(dropna=True)),
        "unique_tissues": int(metadata["tissue_general"].nunique(dropna=True)),
        "unique_cell_types": int(metadata["cell_type"].nunique(dropna=True)),
    }

    global_counts.to_csv(output_dir / "census_global_summary_cell_counts.tsv", sep="\t", index=False)
    target_cell_counts.to_csv(output_dir / "target_cell_type_global_counts.tsv", sep="\t", index=False)
    tissue_cell.to_csv(output_dir / "metadata_feasibility_map.tsv", sep="\t", index=False)
    cell_system.to_csv(output_dir / "cell_system_feasibility_map.tsv", sep="\t", index=False)
    donor_level.to_csv(output_dir / "donor_level_metadata_summary.tsv", sep="\t", index=False)
    metadata.head(5000).to_csv(output_dir / "metadata_sample.tsv", sep="\t", index=False)
    (output_dir / "metadata_audit_summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")

    print(json.dumps(summary, indent=2))
    print("\nCell-system feasibility")
    print(cell_system.sort_values("donor_n", ascending=False).to_string(index=False))
    print("\nTissue-cell feasibility")
    print(tissue_cell.head(20).to_string(index=False))


if __name__ == "__main__":
    main()
