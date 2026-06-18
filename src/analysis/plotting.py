import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from scipy.cluster.hierarchy import dendrogram

from sklearn.preprocessing import StandardScaler
from src.analysis.helpers import BIRTH_TYPES, Features, CLUSTER_FEATURES, FEATURE_LABELS, metric_title, \
    birth_type_title
from src.analysis.classes import AnalysisResults, TrendDatasets


def finalize_plot():
    plt.tight_layout()
    plt.show()


def plot_national_trend(trend_dict: TrendDatasets, metric):
    marital = trend_dict.marital.sort_values("year")
    nonmarital = trend_dict.nonmarital.sort_values("year")
    shared = trend_dict.total.sort_values("year")

    fig, ax = plt.subplots(figsize=(12, 6))

    ax.plot(marital["year"], marital["marriages"], marker="o", linewidth=2, label="Бракове")
    ax.plot(marital["year"], marital["births"], marker="o", linewidth=2, label="Брачни раждания")
    ax.plot(nonmarital["year"], nonmarital["births"], marker="o", linewidth=2, label="Извънбрачни раждания")
    ax.plot(shared["year"], shared["births"], marker="o", linewidth=2, label="Раждания")

    ax.set_title(f"{metric_title(metric)}: бракове и раждания на 1000 души")
    ax.set_xlabel("Година")
    ax.set_ylabel("Стойност за всеки 1000")
    ax.grid(True, alpha=0.3)
    ax.legend()
    finalize_plot()


def plot_lag_analysis(lag_dict, metric):
    fig, axes = plt.subplots(1, len(BIRTH_TYPES), figsize=(14, 5), sharey=True)

    for ax, birth_type in zip(axes, BIRTH_TYPES):
        lag_df = lag_dict[birth_type]
        ax.bar(lag_df["lag"], lag_df["correlation"])
        ax.set_title(f"{metric_title(metric)}: {birth_type_title(birth_type)} раждания")
        ax.set_xlabel("Изместване (години)")
        ax.set_ylabel("Корелация")

    finalize_plot()

def plot_regional_lag_analysis(lag_matrices, metric):

    fig, axes = plt.subplots(1, len(BIRTH_TYPES), figsize=(22, 12), sharey=True)

    for ax, birth_type in zip(axes, BIRTH_TYPES):
        df_heat = lag_matrices[birth_type]
        sns.heatmap(
            df_heat,
            annot=False,
            cmap="coolwarm",
            center=0,
            vmin=-1,
            vmax=1,
            ax=ax
        )

        ax.set_title(f"{metric_title(metric)}: {birth_type_title(birth_type)} раждания по области")
        ax.set_xlabel("Изместване (години)")
        ax.set_ylabel("Области")

    finalize_plot()


def plot_nonmarital_share(share, metric):
    fig, ax = plt.subplots(figsize=(12, 6))

    ax.plot(share["year"], share["nonmarital_share"], marker="o", linewidth=2)
    ax.set_title(f"{metric_title(metric)}: дял на извънбрачните раждания")
    ax.set_xlabel("Година")
    ax.set_ylabel("%")
    ax.grid(True, alpha=0.3)

    finalize_plot()


def plot_dendrogram(clusters, linkage_matrix, metric):
    plt.figure(figsize=(14, 7))

    dendrogram(
        linkage_matrix,
        labels=clusters.index,
        leaf_rotation=90,
        leaf_font_size=8,
    )

    plt.title(f"{metric_title(metric)}: йерархична клъстеризация на областите")
    plt.xlabel("Област")
    plt.ylabel("Разстояние (Ward)")

    plt.tight_layout()
    finalize_plot()


def plot_clusters(clusters, metric):
    features = clusters.copy()

    x = Features.MARITAL_BEST_CORR
    y = Features.NONMARITAL_SHARE
    size_col = Features.MARITAL_BEST_LAG

    size = features[size_col]
    den = size.max() - size.min()
    if den == 0:
        size_scaled = np.full(len(size), 200)
    else:
        size_scaled = 100 + 300 * (size - size.min()) / den

    fig, ax = plt.subplots(figsize=(10, 8))

    scatter = ax.scatter(
        features[x],
        features[y],
        c=features["cluster"],
        s=size_scaled,
        cmap="tab10",
        alpha=0.75,
        edgecolors="black",
        linewidths=0.5,
    )

    to_label = set()

    to_label.update(features.nlargest(3, x).index)
    to_label.update(features.nsmallest(3, x).index)

    to_label.update(features.nlargest(3, y).index)
    to_label.update(features.nsmallest(3, y).index)

    for region in to_label:
        ax.annotate(
            region,
            (features.loc[region, x], features.loc[region, y]),
            fontsize=8,
            xytext=(4, 4),
            textcoords="offset points",
        )

    ax.set_title(f"{metric_title(metric)}: клъстери на областите")
    ax.set_xlabel("Най-силна корелация с брачни раждания")
    ax.set_ylabel("Дял извънбрачни раждания (%)")

    ax.grid(alpha=0.25)

    finalize_plot()


def plot_clusters_heatmap(clusters_dict, metric):
    features = clusters_dict.copy()

    plot_df = features.sort_values("cluster")

    scaler = StandardScaler()

    scaled_df = pd.DataFrame(
        scaler.fit_transform(plot_df[CLUSTER_FEATURES]),
        index=plot_df.index,
        columns=CLUSTER_FEATURES,
    )

    scaled_df.columns = [
        FEATURE_LABELS.get(col, col)
        for col in scaled_df.columns
    ]

    plt.figure(figsize=(10, 10))

    sns.heatmap(
        scaled_df,
        cmap="coolwarm",
        center=0,
        linewidths=0.5,
        linecolor="white",
        cbar_kws={"label": "Standardized value"},
    )

    cluster_changes = np.where(
        plot_df["cluster"].values[:-1]
        != plot_df["cluster"].values[1:]
    )[0]

    for pos in cluster_changes:
        plt.axhline(pos + 1, color="black", linewidth=2)

    plt.title(f"{metric_title(metric)}: характеристики на областите")
    plt.xlabel("Показатели")
    plt.ylabel("Области")

    plt.tight_layout()
    finalize_plot()


def plot_cluster_profiles(clusters, metric):
    profile = (
        clusters.groupby("cluster")[CLUSTER_FEATURES]
        .mean()
        .round(2)
    )

    profile = profile.rename(columns=FEATURE_LABELS).T

    fig, ax = plt.subplots(figsize=(6, 3))
    ax.axis("off")

    table = ax.table(
        cellText=profile.values,
        rowLabels=profile.index,
        colLabels=[f"К{i}" for i in profile.columns],
        cellLoc="center",
        loc="center",
    )

    table.auto_set_font_size(False)
    table.set_fontsize(9)
    table.scale(1.2, 2)

    plt.suptitle(
        f"{metric_title(metric)}: средни характеристики на клъстерите",
    )

    finalize_plot()


def plot_cluster_members(clusters, metric):
    fig, ax = plt.subplots(figsize=(12, 3))
    ax.axis("off")

    lines = []

    for cluster, group in clusters.groupby("cluster"):
        regions = ", ".join(sorted(group.index))
        lines.append(f"Клъстер {cluster}:")
        lines.append(regions)
        lines.append("")

    text = "\n".join(lines)

    ax.text(
        0.02,
        0.98,
        text,
        va="top",
        fontsize=10,
        transform=ax.transAxes,
    )

    fig.suptitle(f"{metric_title(metric)}: клъстери")

    finalize_plot()


def plot_results(results: AnalysisResults):
    # plot_national_trend(results.national_sets, results.metric)
    # plot_lag_analysis(results.lags, results.metric)
    # plot_regional_lag_analysis(results.regional_lags, results.metric)
    # plot_nonmarital_share(results.nonmarital_share, results.metric)
    # plot_dendrogram(results.clusters, results.linkage_matrix, results.metric)
    plot_clusters(results.clusters, results.metric)
    plot_clusters_heatmap(results.clusters, results.metric)
    plot_cluster_profiles(results.clusters, results.metric)
    plot_cluster_members(results.clusters, results.metric)
