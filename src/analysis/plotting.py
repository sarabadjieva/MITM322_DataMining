import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

from sklearn.preprocessing import StandardScaler
from src.analysis.helpers import BIRTH_TYPES
from src.analysis.classes import AnalysisResults, TrendDatasets


def metric_title(metric):
    return metric.capitalize()


def show_plot():
    plt.tight_layout()
    plt.show()


def first_frame(dataframes):
    return next(iter(dataframes.values()))


def plot_national_trend(trend_dict: TrendDatasets, metric):
    marital = trend_dict.marital.sort_values("year")
    nonmarital = trend_dict.nonmarital.sort_values("year")
    shared = trend_dict.total.sort_values("year")

    fig, ax = plt.subplots(figsize=(12, 6))

    ax.plot(marital["year"], marital["marriages"], marker="o", linewidth=2, label="Marriages")
    ax.plot(marital["year"], marital["births"], marker="o", linewidth=2, label="Marital births")
    ax.plot(nonmarital["year"], nonmarital["births"], marker="o", linewidth=2, label="Nonmarital births")
    ax.plot(shared["year"], shared["births"], marker="o", linewidth=2, label="Total births")

    ax.set_title(f"{metric_title(metric)} Marriages and Births Over Time")
    ax.set_xlabel("Year")
    ax.set_ylabel("Count")
    ax.grid(True, alpha=0.3)
    ax.legend()
    show_plot()


def plot_lag_analysis(lag_dict, metric):
    fig, axes = plt.subplots(1, len(BIRTH_TYPES), figsize=(14, 5), sharey=True)

    for ax, birth_type in zip(axes, BIRTH_TYPES):
        lag_df = lag_dict[birth_type]
        ax.bar(lag_df["lag"], lag_df["correlation"])
        ax.set_title(f"{metric_title(metric)} Lag: {birth_type.capitalize()} Births")
        ax.set_xlabel("Lag (years)")
        ax.set_ylabel("Correlation")

    show_plot()

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

        ax.set_title(f"{metric_title(metric)} Regional Lag: {birth_type.capitalize()} Births")
        ax.set_xlabel("Lag (years)")
        ax.set_ylabel("Regions")

    show_plot()


def plot_nonmarital_share(share, metric):
    fig, ax = plt.subplots(figsize=(12, 6))

    ax.plot(share["year"], share["nonmarital_share"], marker="o", linewidth=2)
    ax.set_title(f"{metric_title(metric)} Share of Non-Marital Births")
    ax.set_xlabel("Year")
    ax.set_ylabel("%")
    ax.grid(True, alpha=0.3)

    show_plot()


def plot_elbow(inertia_dict, metric):
    diagnostics = first_frame(inertia_dict)
    if diagnostics.empty:
        return

    fig, ax = plt.subplots(figsize=(8, 5))
    ax.plot(diagnostics["k"], diagnostics["inertia"], marker="o")
    ax.set_title(f"{metric_title(metric)} Elbow Method - Choose Number of Clusters")
    ax.set_xlabel("Number of Clusters")
    ax.set_ylabel("Inertia")
    ax.set_xticks(diagnostics["k"])
    ax.grid(True, alpha=0.3)

    show_plot()


def plot_clusters(clusters_dict, metric):
    features = first_frame(clusters_dict).copy()

    x = "mean_marriages"
    y = "percent_nonmarital_births"
    size_col = "mean_nonmarital_births"

    # scale bubble sizes
    size = features[size_col]
    size_scaled = 80 + 320 * (size - size.min()) / (size.max() - size.min() + 1e-9)

    fig, ax = plt.subplots(figsize=(10, 8))

    scatter = ax.scatter(
        features[x],
        features[y],
        c=features["cluster"],
        s=size_scaled,
        cmap="tab10",
        alpha=0.7,
        edgecolors="black",
        linewidths=0.5,
    )

    # label only notable points: top/bottom or outliers
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

    ax.set_title(f"{metric_title(metric)} Regional Clusters")
    ax.set_xlabel("Mean Marriages")
    ax.set_ylabel("% Non-Marital Births")
    ax.grid(alpha=0.25)

    legend1 = ax.legend(*scatter.legend_elements(), title="Cluster", loc="upper right")
    ax.add_artist(legend1)

    show_plot()


def plot_results(results: AnalysisResults):
    # plot_national_trend(results.national_sets, results.metric)
    # plot_lag_analysis(results.lags, results.metric)
    # plot_regional_lag_analysis(results.regional_lags, results.metric)
    # plot_nonmarital_share(results.nonmarital_share, results.metric)
    # plot_elbow(results.inertia, results.metric)
    plot_clusters(results.clusters, results.metric)
    plot_clusters_heatmap(results.clusters, results.metric)
    plot_cluster_profiles(results.clusters, results.metric)


def plot_clusters_heatmap(clusters_dict, metric):
    features = first_frame(clusters_dict).copy()

    feature_cols = [
        "mean_marriages",
        "mean_marital_births",
        "mean_nonmarital_births",
        "percent_nonmarital_births",
        "marriages_trend",
        "marital_births_trend",
        "nonmarital_births_trend",
    ]

    plot_df = features[feature_cols + ["cluster"]].copy()
    plot_df = plot_df.sort_values(["cluster"])

    scaler = StandardScaler()
    scaled_values = scaler.fit_transform(plot_df[feature_cols])

    scaled_df = pd.DataFrame(
        scaled_values,
        index=plot_df.index,
        columns=feature_cols,
    )

    plt.figure(figsize=(12, 10))
    sns.heatmap(
        scaled_df,
        cmap="coolwarm",
        center=0,
        linewidths=0.4,
        linecolor="white",
        cbar_kws={"label": "Standardized value"},
    )

    plt.title(f"{metric_title(metric)} Regional Feature Heatmap")
    plt.xlabel("Features")
    plt.ylabel("Regions")
    plt.tight_layout()
    show_plot()


def plot_cluster_profiles(clusters_dict, metric):
    features = first_frame(clusters_dict).copy()

    feature_cols = [
        "mean_marriages",
        "mean_marital_births",
        "mean_nonmarital_births",
        "percent_nonmarital_births",
        "marriages_trend",
        "marital_births_trend",
        "nonmarital_births_trend",
    ]

    profile = features.groupby("cluster")[feature_cols].mean()

    # standardize across clusters for easier comparison
    scaler = StandardScaler()
    profile_scaled = pd.DataFrame(
        scaler.fit_transform(profile),
        index=profile.index,
        columns=profile.columns,
    )

    profile_scaled.T.plot(
        kind="bar",
        figsize=(14, 7),
        colormap="tab10",
        alpha=0.85,
    )

    plt.title(f"{metric_title(metric)} Cluster Profiles")
    plt.xlabel("Features")
    plt.ylabel("Standardized cluster mean")
    plt.xticks(rotation=45, ha="right")
    plt.legend(title="Cluster")
    plt.grid(axis="y", alpha=0.25)
    plt.tight_layout()
    show_plot()