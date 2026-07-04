from __future__ import annotations

import json
import math
import re
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import scanpy as sc
import seaborn as sns
from scipy import sparse
from sklearn.decomposition import PCA, TruncatedSVD
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import average_precision_score, balanced_accuracy_score, roc_auc_score
from sklearn.model_selection import GroupShuffleSplit, train_test_split
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

import cellxgene_census
from cellxgene_census import experimental as census_exp


CENSUS_VERSION = "2025-11-08"
OUT = Path("analysis/benchmark_outputs")
FIG = Path("outputs/benchmark_figures")
OUT.mkdir(parents=True, exist_ok=True)
FIG.mkdir(parents=True, exist_ok=True)


def parse_numeric_age(stage: object) -> float | None:
    text = str(stage).lower()
    match = re.search(r"(\d+)-year-old", text)
    if match:
        return float(match.group(1))
    decade_midpoints = {
        "first decade": 5,
        "second decade": 15,
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


def disease_free_label(value: object) -> bool:
    return str(value).lower() in {"normal", "healthy"}


def sample_cells(meta: pd.DataFrame, disease_free_only: bool, seed: int = 13) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    df = meta.copy()
    if disease_free_only:
        df = df[df["is_disease_free"]].copy()
    df = df[df["age_group"].isin(["young", "old"])].copy()

    donor_table = df.groupby(["donor_id", "age_group"], observed=True).size().reset_index(name="cell_n")
    young = donor_table[donor_table["age_group"] == "young"]["donor_id"].unique()
    old = donor_table[donor_table["age_group"] == "old"]["donor_id"].unique()
    n = min(60, len(young), len(old))
    if n < 20:
        raise RuntimeError(f"Not enough donors after filtering: young={len(young)}, old={len(old)}")
    chosen = set(rng.choice(young, size=n, replace=False)) | set(rng.choice(old, size=n, replace=False))
    df = df[df["donor_id"].isin(chosen)].copy()

    sampled = []
    for _, block in df.groupby("donor_id", observed=True):
        take = min(10, len(block))
        sampled.append(block.sample(n=take, random_state=seed))
    out = pd.concat(sampled, ignore_index=True)
    out["y"] = out["age_group"].map({"young": 0, "old": 1}).astype(int)
    return out


def valid_binary(y: np.ndarray) -> bool:
    return len(np.unique(y)) == 2 and min(np.bincount(y.astype(int))) > 0


def metric_row(y_true: np.ndarray, scores: np.ndarray, pred: np.ndarray) -> dict[str, float]:
    if not valid_binary(y_true):
        return {"auroc": np.nan, "auprc": np.nan, "balanced_accuracy": np.nan}
    return {
        "auroc": roc_auc_score(y_true, scores),
        "auprc": average_precision_score(y_true, scores),
        "balanced_accuracy": balanced_accuracy_score(y_true, pred),
    }


def fit_eval(X_train, y_train, X_test, y_test) -> dict[str, float]:
    clf = make_pipeline(
        StandardScaler(with_mean=not sparse.issparse(X_train)),
        LogisticRegression(max_iter=2000, class_weight="balanced", solver="liblinear"),
    )
    clf.fit(X_train, y_train)
    scores = clf.predict_proba(X_test)[:, 1]
    pred = (scores >= 0.5).astype(int)
    return metric_row(y_test, scores, pred)


def split_random(y: np.ndarray, seed: int):
    return train_test_split(np.arange(len(y)), test_size=0.3, random_state=seed, stratify=y)


def split_group(y: np.ndarray, groups: np.ndarray, seed: int):
    for offset in range(80):
        splitter = GroupShuffleSplit(n_splits=1, test_size=0.3, random_state=seed + offset)
        train, test = next(splitter.split(np.arange(len(y)), y, groups))
        if valid_binary(y[train]) and valid_binary(y[test]):
            return train, test
    raise RuntimeError("Could not produce a valid grouped split")


def reduce_expression(ad):
    sc.pp.normalize_total(ad, target_sum=1e4)
    sc.pp.log1p(ad)
    sc.pp.highly_variable_genes(ad, n_top_genes=1000, flavor="seurat")
    hvg_mask = ad.var["highly_variable"].to_numpy()
    X = ad[:, hvg_mask].X
    if not sparse.issparse(X):
        X = sparse.csr_matrix(X)
    svd = TruncatedSVD(n_components=30, random_state=13)
    X_pca = svd.fit_transform(X)
    X_hvg200 = X[:, : min(200, X.shape[1])].toarray()
    return X_hvg200, X_pca


def pseudobulk_matrix(X_hvg200: np.ndarray, sample_meta: pd.DataFrame):
    blocks = []
    ys = []
    donors = []
    datasets = []
    for donor, idx in sample_meta.groupby("donor_id", observed=True).indices.items():
        block = X_hvg200[list(idx)]
        blocks.append(block.mean(axis=0))
        donor_rows = sample_meta.iloc[list(idx)]
        ys.append(int(donor_rows["y"].iloc[0]))
        donors.append(donor)
        datasets.append(str(donor_rows["dataset_id"].mode().iloc[0]))
    return np.vstack(blocks), np.array(ys), np.array(donors), np.array(datasets)


def run_feature_set(name: str, X: np.ndarray, meta: pd.DataFrame, repeats: int, label_shuffle: bool = False):
    rows = []
    y = meta["y"].to_numpy()
    donors = meta["donor_id"].astype(str).to_numpy()
    datasets = meta["dataset_id"].astype(str).to_numpy()
    splits = {
        "random_cell": lambda seed: split_random(y, seed),
        "donor_holdout": lambda seed: split_group(y, donors, seed),
        "dataset_holdout": lambda seed: split_group(y, datasets, seed),
    }
    for split_name, splitter in splits.items():
        for seed in range(13, 13 + repeats):
            train, test = splitter(seed)
            y_train = y[train].copy()
            if label_shuffle:
                rng = np.random.default_rng(seed)
                y_train = rng.permutation(y_train)
                model_name = f"{name}_label_shuffled"
            else:
                model_name = name
            try:
                metrics = fit_eval(X[train], y_train, X[test], y[test])
            except Exception as exc:
                metrics = {"auroc": np.nan, "auprc": np.nan, "balanced_accuracy": np.nan, "error": str(exc)}
            rows.append({"model": model_name, "split": split_name, "repeat": seed, **metrics})
    return rows


def run_pseudobulk(name: str, X: np.ndarray, meta: pd.DataFrame, repeats: int):
    rows = []
    Xb, y, donors, datasets = pseudobulk_matrix(X, meta)
    for split_name, groups in {"donor_holdout": donors, "dataset_holdout": datasets}.items():
        for seed in range(13, 13 + repeats):
            train, test = split_group(y, groups, seed)
            metrics = fit_eval(Xb[train], y[train], Xb[test], y[test])
            rows.append({"model": name, "split": split_name, "repeat": seed, **metrics})
    return rows


def main():
    with cellxgene_census.open_soma(census_version=CENSUS_VERSION) as census:
        obs = census["census_data"]["homo_sapiens"].obs
        value_filter = "is_primary_data == True and tissue_general == 'blood' and cell_type == 'T cell'"
        meta = obs.read(
            value_filter=value_filter,
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
    meta["is_disease_free"] = meta["disease"].map(disease_free_label)
    meta.to_csv(OUT / "blood_tcell_full_metadata.tsv", sep="\t", index=False)

    sample_all = sample_cells(meta, disease_free_only=False, seed=13)
    sample_df = sample_cells(meta, disease_free_only=True, seed=17)
    sample_all.to_csv(OUT / "blood_tcell_sample_all.tsv", sep="\t", index=False)
    sample_df.to_csv(OUT / "blood_tcell_sample_disease_free.tsv", sep="\t", index=False)

    all_ids = sample_all["soma_joinid"].to_numpy(dtype=np.int64)
    df_ids = sample_df["soma_joinid"].to_numpy(dtype=np.int64)

    with cellxgene_census.open_soma(census_version=CENSUS_VERSION) as census:
        ad_all = cellxgene_census.get_anndata(
            census,
            organism="homo_sapiens",
            obs_coords=all_ids,
            obs_column_names=["soma_joinid"],
            var_column_names=["feature_id", "feature_name"],
        )
        ad_df = cellxgene_census.get_anndata(
            census,
            organism="homo_sapiens",
            obs_coords=df_ids,
            obs_column_names=["soma_joinid"],
            var_column_names=["feature_id", "feature_name"],
        )

    X_hvg_all, X_pca_all = reduce_expression(ad_all)
    X_hvg_df, X_pca_df = reduce_expression(ad_df)

    emb_meta = {}
    for emb_name in ["scvi", "tf-sapiens"]:
        m = census_exp.get_embedding_metadata_by_name(emb_name, "homo_sapiens", CENSUS_VERSION)
        uri = "s3://cellxgene-contrib-public" + m["relative_uri"]
        emb_meta[emb_name] = {
            "uri": uri,
            "n_features": m["n_features"],
            "title": m["title"],
            "doi": m.get("DOI", ""),
        }

    X_scvi_all = census_exp.get_embedding(CENSUS_VERSION, emb_meta["scvi"]["uri"], all_ids)
    X_tf_all = census_exp.get_embedding(CENSUS_VERSION, emb_meta["tf-sapiens"]["uri"], all_ids)
    X_scvi_df = census_exp.get_embedding(CENSUS_VERSION, emb_meta["scvi"]["uri"], df_ids)
    X_tf_df = census_exp.get_embedding(CENSUS_VERSION, emb_meta["tf-sapiens"]["uri"], df_ids)

    features_all = {
        "HVG200_logistic": X_hvg_all,
        "expression_PCA_logistic": X_pca_all,
        "scVI_embedding_logistic": X_scvi_all,
        "TranscriptFormer_embedding_logistic": X_tf_all,
    }
    features_df = {
        "HVG200_logistic": X_hvg_df,
        "expression_PCA_logistic": X_pca_df,
        "scVI_embedding_logistic": X_scvi_df,
        "TranscriptFormer_embedding_logistic": X_tf_df,
    }

    rows = []
    for name, X in features_all.items():
        rows.extend(run_feature_set(name, X, sample_all, repeats=5, label_shuffle=False))
        rows.extend(run_feature_set(name, X, sample_all, repeats=5, label_shuffle=True))
    rows.extend(run_pseudobulk("pseudobulk_HVG200_logistic", X_hvg_all, sample_all, repeats=5))

    for name, X in features_df.items():
        disease_rows = run_feature_set(name, X, sample_df, repeats=5, label_shuffle=False)
        for row in disease_rows:
            row["split"] = "disease_free_" + row["split"]
        rows.extend(disease_rows)
    rows.extend(
        {**row, "split": "disease_free_" + row["split"]}
        for row in run_pseudobulk("pseudobulk_HVG200_logistic", X_hvg_df, sample_df, repeats=5)
    )

    results = pd.DataFrame(rows)
    results.to_csv(OUT / "blood_tcell_benchmark_results_long.tsv", sep="\t", index=False)
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
    summary.to_csv(OUT / "blood_tcell_benchmark_results_summary.tsv", sep="\t", index=False)

    audit = {
        "census_version": CENSUS_VERSION,
        "full_blood_t_cells": int(len(meta)),
        "numeric_age_cells": int(meta["age_group"].isin(["young", "old", "middle"]).sum()),
        "young_old_cells": int(meta["age_group"].isin(["young", "old"]).sum()),
        "sample_all_cells": int(len(sample_all)),
        "sample_all_donors": int(sample_all["donor_id"].nunique()),
        "sample_disease_free_cells": int(len(sample_df)),
        "sample_disease_free_donors": int(sample_df["donor_id"].nunique()),
        "sample_all_young_donors": int(sample_all[sample_all["y"] == 0]["donor_id"].nunique()),
        "sample_all_old_donors": int(sample_all[sample_all["y"] == 1]["donor_id"].nunique()),
        "embedding_metadata": emb_meta,
    }
    (OUT / "blood_tcell_benchmark_audit.json").write_text(json.dumps(audit, indent=2), encoding="utf-8")

    sns.set_theme(style="whitegrid", context="paper")
    plot = summary[
        ~summary["model"].str.contains("label_shuffled")
        & summary["split"].isin(["random_cell", "donor_holdout", "dataset_holdout", "disease_free_donor_holdout"])
    ].copy()
    plot["model"] = plot["model"].str.replace("_logistic", "", regex=False).str.replace("_embedding", "", regex=False)
    fig, ax = plt.subplots(figsize=(9.2, 4.8), constrained_layout=True)
    sns.barplot(data=plot, x="model", y="auroc_mean", hue="split", ax=ax)
    ax.axhline(0.5, color="#555555", linestyle="--", linewidth=1)
    ax.set_ylim(0.35, 1.0)
    ax.set_xlabel("")
    ax.set_ylabel("AUROC")
    ax.set_title("Blood T cell age-group prediction under increasingly strict splits")
    ax.tick_params(axis="x", rotation=20)
    fig.savefig(FIG / "figure_benchmark_performance_collapse.png", dpi=300)
    plt.close(fig)

    random_true = summary[summary["split"].eq("random_cell") & ~summary["model"].str.contains("label_shuffled")]
    random_perm = summary[summary["split"].eq("random_cell") & summary["model"].str.contains("label_shuffled")].copy()
    random_perm["base_model"] = random_perm["model"].str.replace("_label_shuffled", "", regex=False)
    gap = random_true.merge(random_perm, left_on="model", right_on="base_model", suffixes=("_true", "_shuffled"))
    gap["permutation_gap_auroc"] = gap["auroc_mean_true"] - gap["auroc_mean_shuffled"]
    donor = summary[summary["split"].eq("donor_holdout") & ~summary["model"].str.contains("label_shuffled")]
    drop = random_true.merge(donor, on="model", suffixes=("_random", "_donor"))
    drop["generalization_drop_auroc"] = drop["auroc_mean_random"] - drop["auroc_mean_donor"]
    diagnostics = gap[["model", "permutation_gap_auroc"]].merge(drop[["model", "generalization_drop_auroc"]], on="model", how="outer")
    diagnostics.to_csv(OUT / "blood_tcell_leakage_diagnostics.tsv", sep="\t", index=False)

    diag_long = diagnostics.melt(id_vars="model", var_name="diagnostic", value_name="auroc_delta")
    diag_long["model"] = diag_long["model"].str.replace("_logistic", "", regex=False).str.replace("_embedding", "", regex=False)
    fig, ax = plt.subplots(figsize=(8.2, 4.2), constrained_layout=True)
    sns.barplot(data=diag_long, x="model", y="auroc_delta", hue="diagnostic", ax=ax)
    ax.axhline(0, color="#555555", linewidth=1)
    ax.set_xlabel("")
    ax.set_ylabel("AUROC difference")
    ax.set_title("Permutation gap and donor-holdout generalization drop")
    ax.tick_params(axis="x", rotation=20)
    fig.savefig(FIG / "figure_leakage_diagnostics.png", dpi=300)
    plt.close(fig)

    print(json.dumps(audit, indent=2))
    print(summary.to_string(index=False))


if __name__ == "__main__":
    main()
