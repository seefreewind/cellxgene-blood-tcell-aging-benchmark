from __future__ import annotations

import json
import math
import re
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from sklearn.compose import ColumnTransformer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import average_precision_score, balanced_accuracy_score, roc_auc_score
from sklearn.model_selection import GroupShuffleSplit, train_test_split
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

import cellxgene_census
from cellxgene_census import experimental as census_exp


CENSUS_VERSION = "2025-11-08"
OUT = Path("analysis/benchmark_outputs")
FIG = Path("outputs/benchmark_figures")
OUT.mkdir(parents=True, exist_ok=True)
FIG.mkdir(parents=True, exist_ok=True)


def parse_numeric_age(stage: object) -> float | None:
    text = str(stage).lower()
    m = re.search(r"(\d+)-year-old", text)
    if m:
        return float(m.group(1))
    decade_midpoints = {
        "third decade": 25,
        "fourth decade": 35,
        "fifth decade": 45,
        "sixth decade": 55,
        "seventh decade": 65,
        "eighth decade": 75,
        "ninth decade": 85,
        "tenth decade": 95,
    }
    for token, value in decade_midpoints.items():
        if token in text:
            return float(value)
    return None


def age_group(age: float | None) -> str:
    if age is None or math.isnan(age):
        return "exclude"
    if age <= 40:
        return "young"
    if age >= 60:
        return "old"
    return "middle"


def sample_cells(meta: pd.DataFrame, disease_free_only: bool, seed: int) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    df = meta[meta["age_group"].isin(["young", "old"])].copy()
    if disease_free_only:
        df = df[df["is_disease_free"]].copy()
    donors = df.groupby(["donor_id", "age_group"], observed=True).size().reset_index(name="cell_n")
    young = donors[donors["age_group"] == "young"]["donor_id"].unique()
    old = donors[donors["age_group"] == "old"]["donor_id"].unique()
    n = min(70, len(young), len(old))
    if n < 20:
        raise RuntimeError(f"Too few donors: young={len(young)}, old={len(old)}")
    chosen = set(rng.choice(young, n, replace=False)) | set(rng.choice(old, n, replace=False))
    df = df[df["donor_id"].isin(chosen)].copy()
    chunks = []
    for _, block in df.groupby("donor_id", observed=True):
        chunks.append(block.sample(n=min(8, len(block)), random_state=seed))
    out = pd.concat(chunks, ignore_index=True)
    out["y"] = out["age_group"].map({"young": 0, "old": 1}).astype(int)
    return out


def get_embedding(name: str, ids: np.ndarray) -> tuple[np.ndarray, dict]:
    meta = census_exp.get_embedding_metadata_by_name(name, "homo_sapiens", CENSUS_VERSION)
    uri = "s3://cellxgene-contrib-public" + meta["relative_uri"]
    return census_exp.get_embedding(CENSUS_VERSION, uri, ids), {
        "name": name,
        "title": meta["title"],
        "doi": meta.get("DOI", ""),
        "n_features": meta["n_features"],
        "uri": uri,
    }


def valid(y: np.ndarray) -> bool:
    return len(np.unique(y)) == 2


def metrics(y_true: np.ndarray, score: np.ndarray) -> dict[str, float]:
    pred = (score >= 0.5).astype(int)
    return {
        "auroc": roc_auc_score(y_true, score) if valid(y_true) else np.nan,
        "auprc": average_precision_score(y_true, score) if valid(y_true) else np.nan,
        "balanced_accuracy": balanced_accuracy_score(y_true, pred) if valid(y_true) else np.nan,
    }


def split_random(y: np.ndarray, seed: int):
    return train_test_split(np.arange(len(y)), test_size=0.3, random_state=seed, stratify=y)


def split_group(y: np.ndarray, groups: np.ndarray, seed: int):
    for offset in range(120):
        splitter = GroupShuffleSplit(n_splits=1, test_size=0.3, random_state=seed + offset)
        train, test = next(splitter.split(np.arange(len(y)), y, groups))
        if valid(y[train]) and valid(y[test]):
            return train, test
    raise RuntimeError("No valid group split found")


def fit_numeric(X_train, y_train, X_test) -> np.ndarray:
    clf = make_pipeline(
        StandardScaler(),
        LogisticRegression(max_iter=2000, class_weight="balanced", solver="liblinear"),
    )
    clf.fit(X_train, y_train)
    return clf.predict_proba(X_test)[:, 1]


def fit_metadata(train: pd.DataFrame, y_train: np.ndarray, test: pd.DataFrame) -> np.ndarray:
    cols = ["dataset_id", "assay", "disease", "sex"]
    pre = ColumnTransformer([("cat", OneHotEncoder(handle_unknown="ignore"), cols)])
    clf = make_pipeline(pre, LogisticRegression(max_iter=2000, class_weight="balanced", solver="liblinear"))
    clf.fit(train[cols], y_train)
    return clf.predict_proba(test[cols])[:, 1]


def aggregate_by_donor(X: np.ndarray, meta: pd.DataFrame):
    rows, y, donors, datasets = [], [], [], []
    for donor, idx in meta.groupby("donor_id", observed=True).indices.items():
        ids = list(idx)
        rows.append(X[ids].mean(axis=0))
        block = meta.iloc[ids]
        y.append(int(block["y"].iloc[0]))
        donors.append(donor)
        datasets.append(str(block["dataset_id"].mode().iloc[0]))
    return np.vstack(rows), np.array(y), np.array(donors), np.array(datasets)


def eval_cell_model(model_name: str, X: np.ndarray | None, meta: pd.DataFrame, repeats: int, shuffled: bool = False):
    y = meta["y"].to_numpy()
    donors = meta["donor_id"].astype(str).to_numpy()
    datasets = meta["dataset_id"].astype(str).to_numpy()
    splitters = {
        "random_cell": lambda seed: split_random(y, seed),
        "donor_holdout": lambda seed: split_group(y, donors, seed),
        "dataset_holdout": lambda seed: split_group(y, datasets, seed),
    }
    rows = []
    for split, fn in splitters.items():
        for seed in range(13, 13 + repeats):
            train, test = fn(seed)
            y_train = y[train].copy()
            if shuffled:
                y_train = np.random.default_rng(seed).permutation(y_train)
                out_model = model_name + "_label_shuffled"
            else:
                out_model = model_name
            if X is None:
                score = fit_metadata(meta.iloc[train], y_train, meta.iloc[test])
            else:
                score = fit_numeric(X[train], y_train, X[test])
            rows.append({"model": out_model, "split": split, "repeat": seed, **metrics(y[test], score)})
    return rows


def eval_pseudobulk(model_name: str, X: np.ndarray, meta: pd.DataFrame, repeats: int):
    Xb, y, donors, datasets = aggregate_by_donor(X, meta)
    rows = []
    for split, groups in {"donor_holdout": donors, "dataset_holdout": datasets}.items():
        for seed in range(13, 13 + repeats):
            train, test = split_group(y, groups, seed)
            score = fit_numeric(Xb[train], y[train], Xb[test])
            rows.append({"model": model_name, "split": split, "repeat": seed, **metrics(y[test], score)})
    return rows


def main():
    with cellxgene_census.open_soma(census_version=CENSUS_VERSION) as census:
        obs = census["census_data"]["homo_sapiens"].obs
        meta = obs.read(
            value_filter="is_primary_data == True and tissue_general == 'blood' and cell_type == 'T cell'",
            column_names=[
                "soma_joinid",
                "donor_id",
                "dataset_id",
                "assay",
                "disease",
                "sex",
                "development_stage",
            ],
        ).concat().to_pandas()

    meta["numeric_age"] = meta["development_stage"].map(parse_numeric_age)
    meta["age_group"] = meta["numeric_age"].map(age_group)
    meta["is_disease_free"] = meta["disease"].astype(str).str.lower().isin(["normal", "healthy"])

    sample_all = sample_cells(meta, disease_free_only=False, seed=13)
    sample_df = sample_cells(meta, disease_free_only=True, seed=17)
    sample_all.to_csv(OUT / "blood_tcell_embedding_sample_all.tsv", sep="\t", index=False)
    sample_df.to_csv(OUT / "blood_tcell_embedding_sample_disease_free.tsv", sep="\t", index=False)

    ids_all = sample_all["soma_joinid"].to_numpy(dtype=np.int64)
    ids_df = sample_df["soma_joinid"].to_numpy(dtype=np.int64)
    X_scvi, scvi_meta = get_embedding("scvi", ids_all)
    X_tf, tf_meta = get_embedding("tf-sapiens", ids_all)
    X_scvi_df, _ = get_embedding("scvi", ids_df)
    X_tf_df, _ = get_embedding("tf-sapiens", ids_df)

    rows = []
    for name, X in [
        ("metadata_confounder_logistic", None),
        ("scVI_embedding_logistic", X_scvi),
        ("TranscriptFormer_embedding_logistic", X_tf),
    ]:
        rows.extend(eval_cell_model(name, X, sample_all, repeats=5, shuffled=False))
        rows.extend(eval_cell_model(name, X, sample_all, repeats=5, shuffled=True))
    rows.extend(eval_pseudobulk("scVI_mean_embedding_pseudobulk", X_scvi, sample_all, repeats=5))
    rows.extend(eval_pseudobulk("TranscriptFormer_mean_embedding_pseudobulk", X_tf, sample_all, repeats=5))

    for name, X in [
        ("metadata_confounder_logistic", None),
        ("scVI_embedding_logistic", X_scvi_df),
        ("TranscriptFormer_embedding_logistic", X_tf_df),
    ]:
        for row in eval_cell_model(name, X, sample_df, repeats=5, shuffled=False):
            row["split"] = "disease_free_" + row["split"]
            rows.append(row)
    for row in eval_pseudobulk("scVI_mean_embedding_pseudobulk", X_scvi_df, sample_df, repeats=5):
        row["split"] = "disease_free_" + row["split"]
        rows.append(row)
    for row in eval_pseudobulk("TranscriptFormer_mean_embedding_pseudobulk", X_tf_df, sample_df, repeats=5):
        row["split"] = "disease_free_" + row["split"]
        rows.append(row)

    results = pd.DataFrame(rows)
    results.to_csv(OUT / "blood_tcell_embedding_benchmark_results_long.tsv", sep="\t", index=False)
    summary = (
        results.groupby(["model", "split"], dropna=False)
        .agg(
            auroc_mean=("auroc", "mean"),
            auroc_sd=("auroc", "std"),
            auprc_mean=("auprc", "mean"),
            balanced_accuracy_mean=("balanced_accuracy", "mean"),
            n=("auroc", "count"),
        )
        .reset_index()
    )
    summary.to_csv(OUT / "blood_tcell_embedding_benchmark_results_summary.tsv", sep="\t", index=False)

    random_true = summary[summary["split"].eq("random_cell") & ~summary["model"].str.contains("label_shuffled")]
    donor = summary[summary["split"].eq("donor_holdout") & ~summary["model"].str.contains("label_shuffled")]
    shuffled = summary[summary["split"].eq("random_cell") & summary["model"].str.contains("label_shuffled")].copy()
    shuffled["base_model"] = shuffled["model"].str.replace("_label_shuffled", "", regex=False)
    diagnostics = random_true[["model", "auroc_mean"]].merge(donor[["model", "auroc_mean"]], on="model", suffixes=("_random", "_donor"))
    diagnostics["generalization_drop_auroc"] = diagnostics["auroc_mean_random"] - diagnostics["auroc_mean_donor"]
    diagnostics = diagnostics.merge(shuffled[["base_model", "auroc_mean"]], left_on="model", right_on="base_model", how="left")
    diagnostics["permutation_gap_auroc"] = diagnostics["auroc_mean_random"] - diagnostics["auroc_mean"]
    diagnostics = diagnostics.drop(columns=["base_model", "auroc_mean"])
    diagnostics.to_csv(OUT / "blood_tcell_embedding_leakage_diagnostics.tsv", sep="\t", index=False)

    audit = {
        "census_version": CENSUS_VERSION,
        "full_blood_t_cell_metadata_rows": int(len(meta)),
        "numeric_young_old_metadata_rows": int(meta["age_group"].isin(["young", "old"]).sum()),
        "sample_all_cells": int(len(sample_all)),
        "sample_all_donors": int(sample_all["donor_id"].nunique()),
        "sample_all_young_donors": int(sample_all[sample_all["y"] == 0]["donor_id"].nunique()),
        "sample_all_old_donors": int(sample_all[sample_all["y"] == 1]["donor_id"].nunique()),
        "sample_disease_free_cells": int(len(sample_df)),
        "sample_disease_free_donors": int(sample_df["donor_id"].nunique()),
        "sample_disease_free_young_donors": int(sample_df[sample_df["y"] == 0]["donor_id"].nunique()),
        "sample_disease_free_old_donors": int(sample_df[sample_df["y"] == 1]["donor_id"].nunique()),
        "embeddings": [scvi_meta, tf_meta],
    }
    (OUT / "blood_tcell_embedding_benchmark_audit.json").write_text(json.dumps(audit, indent=2), encoding="utf-8")

    sns.set_theme(style="whitegrid", context="paper")
    plot = summary[
        ~summary["model"].str.contains("label_shuffled")
        & summary["split"].isin(["random_cell", "donor_holdout", "dataset_holdout", "disease_free_donor_holdout"])
    ].copy()
    plot["model_short"] = (
        plot["model"]
        .str.replace("_logistic", "", regex=False)
        .str.replace("_embedding", "", regex=False)
        .str.replace("_pseudobulk", " pseudobulk", regex=False)
        .str.replace("metadata_confounder", "metadata", regex=False)
        .str.replace("TranscriptFormer", "TF", regex=False)
    )
    fig, ax = plt.subplots(figsize=(9.8, 4.8), constrained_layout=True)
    sns.barplot(data=plot, x="model_short", y="auroc_mean", hue="split", ax=ax)
    ax.axhline(0.5, color="#555555", linestyle="--", linewidth=1)
    ax.set_ylim(0.35, 1.0)
    ax.set_xlabel("")
    ax.set_ylabel("AUROC")
    ax.set_title("Blood T cell young-old prediction under leakage-aware splits")
    ax.tick_params(axis="x", rotation=22)
    fig.savefig(FIG / "figure_blood_tcell_embedding_performance.png", dpi=300)
    plt.close(fig)

    diag_long = diagnostics.melt(
        id_vars=["model", "auroc_mean_random", "auroc_mean_donor"],
        value_vars=["generalization_drop_auroc", "permutation_gap_auroc"],
        var_name="diagnostic",
        value_name="auroc_delta",
    )
    diag_long["model_short"] = (
        diag_long["model"]
        .str.replace("_logistic", "", regex=False)
        .str.replace("_embedding", "", regex=False)
        .str.replace("_pseudobulk", " pseudobulk", regex=False)
        .str.replace("metadata_confounder", "metadata", regex=False)
        .str.replace("TranscriptFormer", "TF", regex=False)
    )
    fig, ax = plt.subplots(figsize=(8.8, 4.2), constrained_layout=True)
    sns.barplot(data=diag_long, x="model_short", y="auroc_delta", hue="diagnostic", ax=ax)
    ax.axhline(0, color="#555555", linewidth=1)
    ax.set_xlabel("")
    ax.set_ylabel("AUROC difference")
    ax.set_title("Generalization drop and permutation gap")
    ax.tick_params(axis="x", rotation=22)
    fig.savefig(FIG / "figure_blood_tcell_embedding_diagnostics.png", dpi=300)
    plt.close(fig)

    print(json.dumps(audit, indent=2))
    print(summary.to_string(index=False))
    print(diagnostics.to_string(index=False))


if __name__ == "__main__":
    main()

