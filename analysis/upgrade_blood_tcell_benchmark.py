from __future__ import annotations

import json
import math
import re
import hashlib
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from scipy import stats
from sklearn.compose import ColumnTransformer
from sklearn.decomposition import PCA
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import average_precision_score, balanced_accuracy_score, roc_auc_score
from sklearn.model_selection import GroupShuffleSplit, StratifiedShuffleSplit, train_test_split
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

from cellxgene_census import experimental as census_exp


CENSUS_VERSION = "2025-11-08"
ROOT = Path(".")
OLD = ROOT / "analysis" / "benchmark_outputs"
OUT = ROOT / "analysis" / "upgrade_outputs"
FIG = ROOT / "outputs" / "upgrade_figures"
CACHE = OUT / "embedding_cache"
SEEDS = list(range(1301, 1331))
META_COLS = ["dataset_id", "assay", "disease", "sex"]
EMBEDDINGS = {
    "scVI": "scvi",
    "TranscriptFormer": "tf-sapiens",
}

for directory in [OUT, FIG, CACHE]:
    directory.mkdir(parents=True, exist_ok=True)


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


def embedding_metadata(name: str) -> dict:
    meta = census_exp.get_embedding_metadata_by_name(name, "homo_sapiens", CENSUS_VERSION)
    return {
        "name": name,
        "title": meta["title"],
        "doi": meta.get("DOI", ""),
        "n_features": int(meta["n_features"]),
        "uri": "s3://cellxgene-contrib-public" + meta["relative_uri"],
    }


def load_embedding(label: str, ids: np.ndarray) -> tuple[np.ndarray, dict]:
    name = EMBEDDINGS[label]
    meta = embedding_metadata(name)
    ids = ids.astype(np.int64)
    digest = hashlib.md5(ids.astype(np.int64).tobytes()).hexdigest()[:16]
    cache_file = CACHE / f"{label.lower()}_{len(ids)}_{digest}.npz"
    if cache_file.exists():
        print(f"Using cached {label} embedding: {cache_file}", flush=True)
        arr = np.load(cache_file)["X"]
        return arr, meta
    print(f"Fetching {label} embedding for {len(ids)} cells from {meta['uri']}", flush=True)
    if label != "TranscriptFormer":
        arr = census_exp.get_embedding(CENSUS_VERSION, meta["uri"], ids)
        np.savez_compressed(cache_file, X=arr)
        print(f"Cached {label} embedding: {cache_file}", flush=True)
        return arr, meta

    chunk_size = 50
    chunks = []
    chunk_dir = CACHE / f"{label.lower()}_{len(ids)}_{digest}_chunks"
    chunk_dir.mkdir(parents=True, exist_ok=True)
    for start in range(0, len(ids), chunk_size):
        stop = min(start + chunk_size, len(ids))
        chunk_file = chunk_dir / f"chunk_{start:05d}_{stop:05d}.npz"
        if chunk_file.exists():
            chunk = np.load(chunk_file)["X"]
            print(f"  {label}: using cached rows {start + 1}-{stop} / {len(ids)}", flush=True)
        else:
            print(f"  {label}: fetching rows {start + 1}-{stop} / {len(ids)}", flush=True)
            chunk = census_exp.get_embedding(CENSUS_VERSION, meta["uri"], ids[start:stop])
            np.savez_compressed(chunk_file, X=chunk)
        chunks.append(chunk)
    arr = np.vstack(chunks)
    np.savez_compressed(cache_file, X=arr)
    print(f"Cached {label} embedding: {cache_file}", flush=True)
    return arr, meta


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
    for offset in range(200):
        splitter = GroupShuffleSplit(n_splits=1, test_size=0.3, random_state=seed + offset)
        train, test = next(splitter.split(np.arange(len(y)), y, groups))
        if valid(y[train]) and valid(y[test]):
            return train, test
    raise RuntimeError("No valid grouped split found")


def fit_numeric(X_train, y_train, X_test) -> np.ndarray:
    clf = make_pipeline(
        StandardScaler(),
        LogisticRegression(max_iter=3000, class_weight="balanced", solver="liblinear"),
    )
    clf.fit(X_train, y_train)
    return clf.predict_proba(X_test)[:, 1]


def fit_metadata(train: pd.DataFrame, y_train: np.ndarray, test: pd.DataFrame) -> np.ndarray:
    pre = ColumnTransformer([("cat", OneHotEncoder(handle_unknown="ignore"), META_COLS)])
    clf = make_pipeline(pre, LogisticRegression(max_iter=3000, class_weight="balanced", solver="liblinear"))
    clf.fit(train[META_COLS], y_train)
    return clf.predict_proba(test[META_COLS])[:, 1]


def aggregate_by_donor(X: np.ndarray, meta: pd.DataFrame):
    rows, y, donors, datasets = [], [], [], []
    for donor, idx in meta.groupby("donor_id", observed=True).indices.items():
        ids = list(idx)
        block = meta.iloc[ids]
        rows.append(X[ids].mean(axis=0))
        y.append(int(block["y"].iloc[0]))
        donors.append(str(donor))
        datasets.append(str(block["dataset_id"].mode().iloc[0]))
    return np.vstack(rows), np.array(y), np.array(donors), np.array(datasets)


def eval_cell_model(model_name: str, X: np.ndarray | None, meta: pd.DataFrame, split_prefix: str = "", shuffled: bool = False):
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
        for seed in SEEDS:
            train, test = fn(seed)
            y_train = y[train].copy()
            out_model = model_name
            if shuffled:
                y_train = np.random.default_rng(seed).permutation(y_train)
                out_model = model_name + "_label_shuffled"
            score = fit_metadata(meta.iloc[train], y_train, meta.iloc[test]) if X is None else fit_numeric(X[train], y_train, X[test])
            rows.append({"model": out_model, "split": split_prefix + split, "seed": seed, **metrics(y[test], score)})
    return rows


def eval_pseudobulk(model_name: str, X: np.ndarray, meta: pd.DataFrame, split_prefix: str = ""):
    Xb, y, donors, datasets = aggregate_by_donor(X, meta)
    rows = []
    for split, groups in {"donor_holdout": donors, "dataset_holdout": datasets}.items():
        for seed in SEEDS:
            train, test = split_group(y, groups, seed)
            score = fit_numeric(Xb[train], y[train], Xb[test])
            rows.append({"model": model_name, "split": split_prefix + split, "seed": seed, **metrics(y[test], score)})
    return rows


def summarize(results: pd.DataFrame) -> pd.DataFrame:
    grouped = results.groupby(["model", "split"], dropna=False)
    rows = []
    for (model, split), g in grouped:
        row = {"model": model, "split": split, "n": int(g["auroc"].notna().sum())}
        for metric in ["auroc", "auprc", "balanced_accuracy"]:
            vals = g[metric].dropna().to_numpy()
            mean = float(np.mean(vals)) if len(vals) else np.nan
            sd = float(np.std(vals, ddof=1)) if len(vals) > 1 else np.nan
            ci = 1.96 * sd / math.sqrt(len(vals)) if len(vals) > 1 else np.nan
            row[f"{metric}_mean"] = mean
            row[f"{metric}_sd"] = sd
            row[f"{metric}_ci95_low"] = mean - ci if not math.isnan(ci) else np.nan
            row[f"{metric}_ci95_high"] = mean + ci if not math.isnan(ci) else np.nan
        rows.append(row)
    return pd.DataFrame(rows).sort_values(["split", "model"])


def paired_comparisons(results: pd.DataFrame) -> pd.DataFrame:
    models = [
        "metadata_confounder_logistic",
        "scVI_embedding_logistic",
        "TranscriptFormer_embedding_logistic",
        "scVI_mean_embedding_pseudobulk",
        "TranscriptFormer_mean_embedding_pseudobulk",
    ]
    pairs = [
        ("TranscriptFormer_embedding_logistic", "scVI_embedding_logistic"),
        ("TranscriptFormer_embedding_logistic", "metadata_confounder_logistic"),
        ("scVI_embedding_logistic", "metadata_confounder_logistic"),
        ("TranscriptFormer_mean_embedding_pseudobulk", "scVI_mean_embedding_pseudobulk"),
    ]
    base = results[results["model"].isin(models)].copy()
    rows = []
    for split, block in base.groupby("split"):
        wide = block.pivot_table(index="seed", columns="model", values="auroc")
        for a, b in pairs:
            if a not in wide.columns or b not in wide.columns:
                continue
            diff = (wide[a] - wide[b]).dropna()
            if len(diff) < 2:
                continue
            sd = float(diff.std(ddof=1))
            ci = 1.96 * sd / math.sqrt(len(diff))
            t = stats.ttest_rel(wide[a].dropna(), wide[b].dropna(), nan_policy="omit")
            rows.append({
                "split": split,
                "model_a": a,
                "model_b": b,
                "n_pairs": int(len(diff)),
                "mean_auroc_difference_a_minus_b": float(diff.mean()),
                "sd_difference": sd,
                "ci95_low": float(diff.mean() - ci),
                "ci95_high": float(diff.mean() + ci),
                "paired_t_pvalue": float(t.pvalue),
            })
    return pd.DataFrame(rows)


def leakage_diagnostics(summary: pd.DataFrame) -> pd.DataFrame:
    true = summary[~summary["model"].str.contains("label_shuffled", regex=False)].copy()
    random_true = true[true["split"].eq("random_cell")]
    donor = true[true["split"].eq("donor_holdout")]
    shuffled = summary[summary["split"].eq("random_cell") & summary["model"].str.contains("label_shuffled", regex=False)].copy()
    shuffled["base_model"] = shuffled["model"].str.replace("_label_shuffled", "", regex=False)
    out = random_true[["model", "auroc_mean"]].merge(donor[["model", "auroc_mean"]], on="model", suffixes=("_random", "_donor"))
    out["generalization_drop_auroc"] = out["auroc_mean_random"] - out["auroc_mean_donor"]
    out = out.merge(shuffled[["base_model", "auroc_mean"]], left_on="model", right_on="base_model", how="left")
    out["permutation_gap_auroc"] = out["auroc_mean_random"] - out["auroc_mean"]
    return out.drop(columns=["base_model", "auroc_mean"])


def composition_counts(values: pd.Series) -> str:
    counts = values.astype(str).value_counts().head(6)
    return "; ".join(f"{k}={v}" for k, v in counts.items())


def lodo_dataset_holdout(meta: pd.DataFrame, embeddings: dict[str, np.ndarray]):
    donor_level = meta.drop_duplicates("donor_id").copy()
    rows, exclusions = [], []
    datasets = sorted(meta["dataset_id"].astype(str).unique())
    y_all = meta["y"].to_numpy()
    for dataset in datasets:
        test_mask = meta["dataset_id"].astype(str).eq(dataset).to_numpy()
        train_mask = ~test_mask
        test_donors = donor_level[donor_level["dataset_id"].astype(str).eq(dataset)]
        young = int(test_donors[test_donors["y"] == 0]["donor_id"].nunique())
        old = int(test_donors[test_donors["y"] == 1]["donor_id"].nunique())
        reason = []
        if young < 2 or old < 2:
            reason.append("held-out dataset has fewer than two donors in at least one age class")
        if not valid(y_all[test_mask]) or not valid(y_all[train_mask]):
            reason.append("train or test set lacks both age classes")
        if reason:
            exclusions.append({
                "dataset_id": dataset,
                "heldout_donors": int(test_donors["donor_id"].nunique()),
                "heldout_cells": int(test_mask.sum()),
                "young_donors": young,
                "old_donors": old,
                "exclusion_reason": "; ".join(reason),
            })
            continue
        for model_name, X in [("metadata_confounder_logistic", None), *[(f"{label}_embedding_logistic", arr) for label, arr in embeddings.items()]]:
            score = fit_metadata(meta.loc[train_mask], y_all[train_mask], meta.loc[test_mask]) if X is None else fit_numeric(X[train_mask], y_all[train_mask], X[test_mask])
            rows.append({
                "dataset_id": dataset,
                "model": model_name,
                "heldout_donors": int(test_donors["donor_id"].nunique()),
                "heldout_cells": int(test_mask.sum()),
                "young_donors": young,
                "old_donors": old,
                "disease_composition": composition_counts(meta.loc[test_mask, "disease"]),
                "assay_composition": composition_counts(meta.loc[test_mask, "assay"]),
                "sex_composition": composition_counts(meta.loc[test_mask, "sex"]),
                **metrics(y_all[test_mask], score),
            })
    return pd.DataFrame(rows), pd.DataFrame(exclusions)


def metadata_coefficients(meta: pd.DataFrame) -> pd.DataFrame:
    y = meta["y"].to_numpy()
    pre = ColumnTransformer([("cat", OneHotEncoder(handle_unknown="ignore"), META_COLS)])
    clf = make_pipeline(pre, LogisticRegression(max_iter=3000, class_weight="balanced", solver="liblinear"))
    clf.fit(meta[META_COLS], y)
    encoder = clf.named_steps["columntransformer"].named_transformers_["cat"]
    names = encoder.get_feature_names_out(META_COLS)
    coefs = clf.named_steps["logisticregression"].coef_[0]
    return pd.DataFrame({"feature": names, "coefficient_old_vs_young": coefs, "abs_coefficient": np.abs(coefs)}).sort_values("abs_coefficient", ascending=False)


def confounding_tables_and_figure(meta: pd.DataFrame, embeddings: dict[str, np.ndarray]) -> None:
    donor = meta.sort_values("soma_joinid").drop_duplicates("donor_id").copy()
    for col in ["dataset_id", "disease", "assay", "sex"]:
        tab = donor.groupby([col, "age_group"], observed=True)["donor_id"].nunique().reset_index(name="donor_n")
        tab.to_csv(OUT / f"confounding_age_by_{col}.tsv", sep="\t", index=False)
    metadata_coefficients(meta).to_csv(OUT / "metadata_only_coefficients.tsv", sep="\t", index=False)

    sns.set_theme(style="whitegrid", context="paper")
    fig, axes = plt.subplots(2, 2, figsize=(11.5, 8.2), constrained_layout=True)
    for ax, col, title in [
        (axes[0, 0], "dataset_id", "Dataset"),
        (axes[0, 1], "disease", "Disease"),
        (axes[1, 0], "assay", "Assay"),
        (axes[1, 1], "sex", "Sex"),
    ]:
        tab = donor.groupby([col, "age_group"], observed=True)["donor_id"].nunique().reset_index(name="donor_n")
        top = donor[col].astype(str).value_counts().head(10).index
        tab = tab[tab[col].astype(str).isin(top)]
        sns.barplot(data=tab, x=col, y="donor_n", hue="age_group", ax=ax)
        ax.set_title(f"Age labels by {title.lower()}")
        ax.set_xlabel("")
        ax.set_ylabel("Unique donors")
        ax.tick_params(axis="x", rotation=65, labelsize=7)
    fig.savefig(FIG / "figure6_age_label_confounding_structure.png", dpi=300)
    plt.close(fig)

    coef = metadata_coefficients(meta).head(20).iloc[::-1]
    fig, ax = plt.subplots(figsize=(7.2, 5.8), constrained_layout=True)
    ax.barh(coef["feature"], coef["coefficient_old_vs_young"], color="#4C78A8")
    ax.axvline(0, color="#555555", linewidth=1)
    ax.set_xlabel("Metadata-only coefficient for old class")
    ax.set_title("Largest metadata-only age coefficients")
    fig.savefig(FIG / "figure6b_metadata_coefficients.png", dpi=300)
    plt.close(fig)

    for label, X in embeddings.items():
        pcs = PCA(n_components=2, random_state=13).fit_transform(StandardScaler().fit_transform(X))
        pc = pd.DataFrame({"PC1": pcs[:, 0], "PC2": pcs[:, 1], "age_group": meta["age_group"], "disease": meta["disease"], "dataset_id": meta["dataset_id"]})
        pc.to_csv(OUT / f"{label.lower()}_pca_source.tsv", sep="\t", index=False)
        fig, axes = plt.subplots(1, 3, figsize=(12.5, 3.7), constrained_layout=True)
        for ax, hue in zip(axes, ["age_group", "disease", "dataset_id"]):
            sns.scatterplot(data=pc, x="PC1", y="PC2", hue=hue, s=10, linewidth=0, ax=ax, legend=False)
            ax.set_title(f"{label} PCA by {hue}")
        fig.savefig(FIG / f"figure6c_{label.lower()}_pca_confounding.png", dpi=300)
        plt.close(fig)


def sampling_depth_sensitivity(meta: pd.DataFrame, embeddings: dict[str, np.ndarray], disease_free: bool = False) -> pd.DataFrame:
    rows = []
    depths = [1, 2, 4, 8, 16]
    base_meta = meta[meta["is_disease_free"]].copy() if disease_free else meta.copy()
    prefix = "disease_free_" if disease_free else ""
    for depth in depths:
        for seed in SEEDS:
            chosen = []
            for _, block in base_meta.groupby("donor_id", observed=True):
                chosen.extend(block.sample(n=min(depth, len(block)), random_state=seed).index.tolist())
            sub_meta = base_meta.loc[chosen].reset_index(drop=True)
            source_idx = base_meta.index.get_indexer(base_meta.loc[chosen].index)
            for label, Xfull in embeddings.items():
                Xbase = Xfull[base_meta.index.to_numpy()]
                Xsub = Xbase[source_idx]
                Xb, y, donors, _ = aggregate_by_donor(Xsub, sub_meta)
                train, test = split_group(y, donors, seed)
                score = fit_numeric(Xb[train], y[train], Xb[test])
                rows.append({
                    "model": f"{label}_mean_embedding_pseudobulk",
                    "split": prefix + "donor_holdout",
                    "seed": seed,
                    "requested_cells_per_donor": depth,
                    "median_effective_cells_per_donor": float(sub_meta.groupby("donor_id").size().median()),
                    "max_effective_cells_per_donor": int(sub_meta.groupby("donor_id").size().max()),
                    "note": "Requested depth 16 is capped by the existing eight-cell-per-donor benchmark sample." if depth == 16 else "",
                    **metrics(y[test], score),
                })
    return pd.DataFrame(rows)


def extra_stratum_feasibility() -> None:
    donor = pd.read_csv(ROOT / "analysis" / "outputs" / "donor_level_metadata_summary.tsv", sep="\t")
    donor["numeric_age"] = donor["development_stage"].map(parse_numeric_age)
    donor["numeric_age_group"] = donor["numeric_age"].map(age_group)
    donor["is_disease_free"] = donor["disease"].astype(str).str.lower().isin(["normal", "healthy"])
    rows = []
    for (tissue, cell_type), block in donor.groupby(["tissue_general", "cell_type"], observed=True):
        if tissue == "blood" and cell_type == "T cell":
            continue
        numeric = block[block["numeric_age_group"].isin(["young", "old"])]
        dfree = numeric[numeric["is_disease_free"]]
        rows.append({
            "tissue_general": tissue,
            "cell_type": cell_type,
            "numeric_young_donors": int(numeric[numeric["numeric_age_group"] == "young"]["donor_id"].nunique()),
            "numeric_old_donors": int(numeric[numeric["numeric_age_group"] == "old"]["donor_id"].nunique()),
            "disease_free_numeric_young_donors": int(dfree[dfree["numeric_age_group"] == "young"]["donor_id"].nunique()),
            "disease_free_numeric_old_donors": int(dfree[dfree["numeric_age_group"] == "old"]["donor_id"].nunique()),
            "dataset_n": int(block["dataset_id"].nunique()),
            "cell_n": int(block["cell_n"].sum()),
        })
    out = pd.DataFrame(rows).sort_values(["disease_free_numeric_young_donors", "disease_free_numeric_old_donors"], ascending=False)
    out.to_csv(OUT / "extra_stratum_numeric_age_feasibility.tsv", sep="\t", index=False)
    top = out.head(20)
    lines = [
        "# Extra stratum feasibility",
        "",
        "This audit tested whether any non-blood-T-cell stratum had enough numeric young and old donor labels, disease-free retention, and dataset diversity to support the same leakage-aware benchmark without changing the study design.",
        "",
        "## Main conclusion",
        "",
        "No additional stratum was promoted to a full empirical benchmark in this upgrade. The Phase 0 metadata map contains several apparently eligible strata when broad development-stage proxies are used, but the stricter numeric-age requirement needed for young-versus-old classification sharply reduces usable donor counts, especially after disease-free filtering.",
        "",
        "## Top non-blood-T-cell numeric-age candidates",
        "",
        "| tissue | cell type | numeric young | numeric old | disease-free numeric young | disease-free numeric old | datasets | cells |",
        "|---|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for _, r in top.iterrows():
        lines.append(
            f"| {r['tissue_general']} | {r['cell_type']} | {int(r['numeric_young_donors'])} | {int(r['numeric_old_donors'])} | "
            f"{int(r['disease_free_numeric_young_donors'])} | {int(r['disease_free_numeric_old_donors'])} | {int(r['dataset_n'])} | {int(r['cell_n'])} |"
        )
    lines.extend([
        "",
        "## Interpretation",
        "",
        "Fibroblast and macrophage strata remain the priority for future expansion, but the available public metadata do not yet support a matched 30-seed, donor-aware, disease-free benchmark under the same numeric-age rule used for blood T cells. The manuscript should therefore describe expansion as a near-term requirement rather than report unsupported secondary-stratum performance.",
    ])
    (ROOT / "EXTRA_STRATUM_FEASIBILITY.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def make_main_figures(summary: pd.DataFrame, diagnostics: pd.DataFrame, lodo: pd.DataFrame, depth: pd.DataFrame) -> None:
    sns.set_theme(style="whitegrid", context="paper")
    plot = summary[
        ~summary["model"].str.contains("label_shuffled", regex=False)
        & summary["split"].isin(["random_cell", "donor_holdout", "dataset_holdout", "disease_free_donor_holdout"])
    ].copy()
    plot["model_short"] = (
        plot["model"].str.replace("_logistic", "", regex=False)
        .str.replace("_embedding", "", regex=False)
        .str.replace("_pseudobulk", " mean", regex=False)
        .str.replace("metadata_confounder", "metadata", regex=False)
        .str.replace("TranscriptFormer", "TF", regex=False)
    )
    fig, ax = plt.subplots(figsize=(10.8, 4.8), constrained_layout=True)
    sns.barplot(data=plot, x="model_short", y="auroc_mean", hue="split", ax=ax)
    for _, r in plot.iterrows():
        xlabels = [t.get_text() for t in ax.get_xticklabels()]
    ax.axhline(0.5, color="#555555", linestyle="--", linewidth=1)
    ax.set_ylim(0.25, 1.0)
    ax.set_xlabel("")
    ax.set_ylabel("Mean AUROC across 30 seeds")
    ax.set_title("Blood T cell benchmark with leakage-aware splits")
    ax.tick_params(axis="x", rotation=25)
    fig.savefig(FIG / "figure4_blood_tcell_30seed_performance.png", dpi=300)
    plt.close(fig)

    diag_long = diagnostics.melt(
        id_vars=["model", "auroc_mean_random", "auroc_mean_donor"],
        value_vars=["generalization_drop_auroc", "permutation_gap_auroc"],
        var_name="diagnostic",
        value_name="auroc_delta",
    )
    diag_long["model_short"] = diag_long["model"].str.replace("_embedding_logistic", "", regex=False).str.replace("metadata_confounder_logistic", "metadata", regex=False).str.replace("TranscriptFormer", "TF", regex=False)
    fig, ax = plt.subplots(figsize=(8.6, 4.2), constrained_layout=True)
    sns.barplot(data=diag_long, x="model_short", y="auroc_delta", hue="diagnostic", ax=ax)
    ax.axhline(0, color="#555555", linewidth=1)
    ax.set_xlabel("")
    ax.set_ylabel("AUROC difference")
    ax.set_title("Generalization drop and permutation gap")
    fig.savefig(FIG / "figure5_30seed_leakage_diagnostics.png", dpi=300)
    plt.close(fig)

    if not lodo.empty:
        fig, ax = plt.subplots(figsize=(9.5, 4.5), constrained_layout=True)
        sns.barplot(data=lodo, x="dataset_id", y="auroc", hue="model", ax=ax)
        ax.axhline(0.5, color="#555555", linestyle="--", linewidth=1)
        ax.set_xlabel("Held-out dataset")
        ax.set_ylabel("AUROC")
        ax.set_title("Leave-one-dataset-out blood T cell benchmark")
        ax.tick_params(axis="x", rotation=65, labelsize=7)
        fig.savefig(FIG / "figure7_lodo_dataset_holdout.png", dpi=300)
        plt.close(fig)

    if not depth.empty:
        depth_summary = summarize(depth.rename(columns={"requested_cells_per_donor": "depth"}))
        depth.groupby(["model", "split", "requested_cells_per_donor"], observed=True).agg(
            auroc_mean=("auroc", "mean"),
            auroc_sd=("auroc", "std"),
            n=("auroc", "count"),
        ).reset_index().to_csv(OUT / "sampling_depth_sensitivity_summary.tsv", sep="\t", index=False)
        fig, ax = plt.subplots(figsize=(8.8, 4.4), constrained_layout=True)
        sns.lineplot(data=depth, x="requested_cells_per_donor", y="auroc", hue="model", style="split", marker="o", errorbar=("ci", 95), ax=ax)
        ax.axhline(0.5, color="#555555", linestyle="--", linewidth=1)
        ax.set_xlabel("Requested cells per donor")
        ax.set_ylabel("AUROC")
        ax.set_title("Sampling-depth sensitivity for donor-mean embeddings")
        fig.savefig(FIG / "figure8_sampling_depth_sensitivity.png", dpi=300)
        plt.close(fig)


def main() -> None:
    sample_all = pd.read_csv(OLD / "blood_tcell_embedding_sample_all.tsv", sep="\t")
    sample_df = pd.read_csv(OLD / "blood_tcell_embedding_sample_disease_free.tsv", sep="\t")
    for frame in [sample_all, sample_df]:
        frame["dataset_id"] = frame["dataset_id"].astype(str)
        frame["donor_id"] = frame["donor_id"].astype(str)
        frame["y"] = frame["y"].astype(int)
        frame["is_disease_free"] = frame["is_disease_free"].astype(bool)

    X_scvi, scvi_meta = load_embedding("scVI", sample_all["soma_joinid"].to_numpy(dtype=np.int64))
    X_tf, tf_meta = load_embedding("TranscriptFormer", sample_all["soma_joinid"].to_numpy(dtype=np.int64))
    X_scvi_df, _ = load_embedding("scVI", sample_df["soma_joinid"].to_numpy(dtype=np.int64))
    X_tf_df, _ = load_embedding("TranscriptFormer", sample_df["soma_joinid"].to_numpy(dtype=np.int64))
    embeddings = {"scVI": X_scvi, "TranscriptFormer": X_tf}
    embeddings_df = {"scVI": X_scvi_df, "TranscriptFormer": X_tf_df}

    rows = []
    for name, X in [
        ("metadata_confounder_logistic", None),
        ("scVI_embedding_logistic", X_scvi),
        ("TranscriptFormer_embedding_logistic", X_tf),
    ]:
        rows.extend(eval_cell_model(name, X, sample_all))
        rows.extend(eval_cell_model(name, X, sample_all, shuffled=True))
    rows.extend(eval_pseudobulk("scVI_mean_embedding_pseudobulk", X_scvi, sample_all))
    rows.extend(eval_pseudobulk("TranscriptFormer_mean_embedding_pseudobulk", X_tf, sample_all))

    for name, X in [
        ("metadata_confounder_logistic", None),
        ("scVI_embedding_logistic", X_scvi_df),
        ("TranscriptFormer_embedding_logistic", X_tf_df),
    ]:
        rows.extend(eval_cell_model(name, X, sample_df, split_prefix="disease_free_"))
    rows.extend(eval_pseudobulk("scVI_mean_embedding_pseudobulk", X_scvi_df, sample_df, split_prefix="disease_free_"))
    rows.extend(eval_pseudobulk("TranscriptFormer_mean_embedding_pseudobulk", X_tf_df, sample_df, split_prefix="disease_free_"))

    results = pd.DataFrame(rows)
    summary = summarize(results)
    pairs = paired_comparisons(results)
    diagnostics = leakage_diagnostics(summary)
    lodo, exclusions = lodo_dataset_holdout(sample_all, embeddings)
    confounding_tables_and_figure(sample_all, embeddings)
    depth = pd.concat([
        sampling_depth_sensitivity(sample_all, embeddings, disease_free=False),
        sampling_depth_sensitivity(sample_all, embeddings, disease_free=True),
    ], ignore_index=True)
    extra_stratum_feasibility()
    make_main_figures(summary, diagnostics, lodo, depth)

    results.to_csv(OUT / "blood_tcell_30seed_results_long.tsv", sep="\t", index=False)
    summary.to_csv(OUT / "blood_tcell_30seed_results_summary.tsv", sep="\t", index=False)
    pairs.to_csv(OUT / "paired_model_comparisons.tsv", sep="\t", index=False)
    diagnostics.to_csv(OUT / "blood_tcell_30seed_leakage_diagnostics.tsv", sep="\t", index=False)
    lodo.to_csv(OUT / "lodo_dataset_holdout_metrics.tsv", sep="\t", index=False)
    exclusions.to_csv(OUT / "lodo_dataset_exclusions.tsv", sep="\t", index=False)
    depth.to_csv(OUT / "sampling_depth_sensitivity.tsv", sep="\t", index=False)

    audit = {
        "census_version": CENSUS_VERSION,
        "seeds": SEEDS,
        "sample_all_cells": int(len(sample_all)),
        "sample_all_donors": int(sample_all["donor_id"].nunique()),
        "sample_disease_free_cells": int(len(sample_df)),
        "sample_disease_free_donors": int(sample_df["donor_id"].nunique()),
        "embeddings": [scvi_meta, tf_meta],
        "outputs": {
            "results_long": "analysis/upgrade_outputs/blood_tcell_30seed_results_long.tsv",
            "results_summary": "analysis/upgrade_outputs/blood_tcell_30seed_results_summary.tsv",
            "lodo": "analysis/upgrade_outputs/lodo_dataset_holdout_metrics.tsv",
            "confounding": "outputs/upgrade_figures/figure6_age_label_confounding_structure.png",
            "depth": "analysis/upgrade_outputs/sampling_depth_sensitivity.tsv",
        },
        "limitations": [
            "The 16-cell sampling depth is capped by the existing eight-cell-per-donor benchmark sample.",
            "Additional strata were not benchmarked because numeric-age disease-free donor balance was insufficient under the same design.",
        ],
    }
    (OUT / "upgrade_audit.json").write_text(json.dumps(audit, indent=2), encoding="utf-8")
    print(json.dumps(audit, indent=2))
    print(summary.to_string(index=False))


if __name__ == "__main__":
    main()
