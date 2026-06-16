import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from scipy.cluster.hierarchy import dendrogram

from sklearn.preprocessing import StandardScaler
from src.analysis.helpers import BIRTH_TYPES, Features, CLUSTER_FEATURES
from src.analysis.classes import AnalysisResults, TrendDatasets


def finalize_plot():
    plt.tight_layout()
    plt.show()


def plot_national_trend(trend_dict: TrendDatasets, metric):
    marital = trend_dict.marital.sort_values("year")
    nonmarital = trend_dict.nonmarital.sort_values("year")
    shared = trend_dict.total.sort_values("year")

    fig, ax = plt.subplots(figsize=(12, 6))

    ax.plot(marital["year"], marital["marriages"], marker="o", linewidth=2, label="Marriages")
    ax.plot(marital["year"], marital["births"], marker="o", linewidth=2, label="Marital births")
    ax.plot(nonmarital["year"], nonmarital["births"], marker="o", linewidth=2, label="Nonmarital births")
    ax.plot(shared["year"], shared["births"], marker="o", linewidth=2, label="Total births")

    ax.set_title(f"{metric.capitalize()} Marriages and Births Over Time per 1000 people")
    ax.set_xlabel("Year")
    ax.set_ylabel("Rate per 1000")
    ax.grid(True, alpha=0.3)
    ax.legend()
    finalize_plot()


def plot_lag_analysis(lag_dict, metric):
    fig, axes = plt.subplots(1, len(BIRTH_TYPES), figsize=(14, 5), sharey=True)

    for ax, birth_type in zip(axes, BIRTH_TYPES):
        lag_df = lag_dict[birth_type]
        ax.bar(lag_df["lag"], lag_df["correlation"])
        ax.set_title(f"{metric.capitalize()} Lag: {birth_type.capitalize()} Births")
        ax.set_xlabel("Lag (years)")
        ax.set_ylabel("Correlation")

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

        ax.set_title(f"{metric.capitalize()} Regional Lag: {birth_type.capitalize()} Births")
        ax.set_xlabel("Lag (years)")
        ax.set_ylabel("Regions")

    finalize_plot()


def plot_nonmarital_share(share, metric):
    fig, ax = plt.subplots(figsize=(12, 6))

    ax.plot(share["year"], share["nonmarital_share"], marker="o", linewidth=2)
    ax.set_title(f"{metric.capitalize()} Share of Non-Marital Births")
    ax.set_xlabel("Year")
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

    plt.title(f"{metric.capitalize()} Hierarchical Clustering Dendrogram")
    plt.xlabel("Region")
    plt.ylabel("Ward Distance")

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

    for region in features.index:
        ax.annotate(
            region,
            (features.loc[region, x], features.loc[region, y]),
            fontsize=8,
            xytext=(4, 4),
            textcoords="offset points",
        )

    ax.set_title(f"{metric.capitalize()} Regional Clusters")
    ax.set_xlabel("Strongest marital correlation")
    ax.set_ylabel("Nonmarital birth share")

    ax.grid(alpha=0.25)

    legend = ax.legend(
        *scatter.legend_elements(),
        title="Cluster",
        loc="upper right",
    )

    ax.add_artist(legend)

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

    plt.title(f"{metric.capitalize()} Cluster Feature Heatmap")
    plt.xlabel("Features")
    plt.ylabel("Regions")

    plt.tight_layout()
    finalize_plot()


def plot_cluster_profiles(clusters_dict, metric):
    features = clusters_dict.copy()

    profile = features.groupby("cluster")[CLUSTER_FEATURES].mean()

    scaler = StandardScaler()

    profile_scaled = pd.DataFrame(
        scaler.fit_transform(profile),
        index=profile.index,
        columns=profile.columns,
    )

    plt.figure(figsize=(8, 5))

    sns.heatmap(
        profile_scaled,
        annot=True,
        cmap="coolwarm",
        center=0,
        fmt=".2f",
    )

    plt.title(f"{metric.capitalize()} Cluster Profiles")
    plt.ylabel("Cluster")
    plt.xlabel("Feature")

    plt.tight_layout()
    finalize_plot()


def plot_results(results: AnalysisResults):
    plot_national_trend(results.national_sets, results.metric)
    plot_lag_analysis(results.lags, results.metric)
    plot_regional_lag_analysis(results.regional_lags, results.metric)
    plot_nonmarital_share(results.nonmarital_share, results.metric)
    plot_dendrogram(results.clusters, results.linkage_matrix, results.metric)
    plot_clusters(results.clusters, results.metric)
    plot_clusters_heatmap(results.clusters, results.metric)
    plot_cluster_profiles(results.clusters, results.metric)
