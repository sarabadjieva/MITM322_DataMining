import matplotlib.pyplot as plt

from src.analysis.constants import BIRTH_TYPES
from src.analysis.result import AnalysisResults, TrendDatasets


def metric_title(metric):
    return metric.capitalize()


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
    plt.tight_layout()
    plt.show()


def plot_lag_analysis(lag_dict, metric):
    fig, axes = plt.subplots(1, len(BIRTH_TYPES), figsize=(14, 5), sharey=True)

    for ax, birth_type in zip(axes, BIRTH_TYPES):
        lag_df = lag_dict[birth_type]
        ax.bar(lag_df["lag"], lag_df["correlation"])
        ax.set_title(f"{metric_title(metric)} Lag: {birth_type.capitalize()} Births")
        ax.set_xlabel("Lag (years)")
        ax.set_ylabel("Correlation")

    plt.tight_layout()
    plt.show()


def plot_lag_pre_post(lags_pre, lags_post, metric):
    fig, axes = plt.subplots(len(BIRTH_TYPES), 2, figsize=(12, 12), sharey=True)

    for row, birth_type in enumerate(BIRTH_TYPES):
        title = f"{metric_title(metric)} {birth_type.capitalize()} Births"

        axes[row, 0].bar(lags_pre[birth_type]["lag"], lags_pre[birth_type]["correlation"], color="steelblue")
        axes[row, 0].set_title(f"{title} - Pre-COVID (2010-2019)")
        axes[row, 0].set_xlabel("Lag (years)")
        axes[row, 0].set_ylabel("Correlation")

        axes[row, 1].bar(lags_post[birth_type]["lag"], lags_post[birth_type]["correlation"], color="darkorange")
        axes[row, 1].set_title(f"{title} - Post-COVID (2019-2025)")
        axes[row, 1].set_xlabel("Lag (years)")

    plt.tight_layout()
    plt.show()


def plot_top_regions(corr_dict, metric, top_n=15):
    fig, axes = plt.subplots(1, len(BIRTH_TYPES), figsize=(16, 8), sharex=True)

    for ax, birth_type in zip(axes, BIRTH_TYPES):
        top = corr_dict[birth_type].head(top_n).sort_values("correlation")
        ax.barh(top["region"], top["correlation"])
        ax.set_title(f"{metric_title(metric)} Top Regions: {birth_type.capitalize()} Births")
        ax.set_xlabel("Correlation")

    plt.tight_layout()
    plt.show()


def plot_nonmarital_share_by_metric(share_by_metric):
    fig, ax = plt.subplots(figsize=(12, 6))

    for metric, group in share_by_metric.groupby("metric"):
        group = group.sort_values("year")
        ax.plot(
            group["year"],
            group["nonmarital_share"],
            marker="o",
            linewidth=2,
            label=metric.capitalize(),
        )

    ax.set_title("Share of Births Outside Marriage by Residence")
    ax.set_xlabel("Year")
    ax.set_ylabel("%")
    ax.grid(True, alpha=0.3)
    ax.legend()
    plt.tight_layout()
    plt.show()


def plot_elbow(inertia_dict, metric):
    fig, axes = plt.subplots(1, len(BIRTH_TYPES), figsize=(14, 5), sharey=True)

    for ax, birth_type in zip(axes, BIRTH_TYPES):
        inertia_df = inertia_dict[birth_type]
        ax.plot(inertia_df["k"], inertia_df["inertia"], marker="o")
        ax.set_title(f"{metric_title(metric)} Elbow: {birth_type.capitalize()} Births")
        ax.set_xlabel("Number of Clusters")
        ax.set_ylabel("Inertia")

    plt.tight_layout()
    plt.show()


def plot_clusters(clusters_dict, metric):
    fig, axes = plt.subplots(1, len(BIRTH_TYPES), figsize=(16, 8), sharex=False, sharey=False)

    for ax, birth_type in zip(axes, BIRTH_TYPES):
        features = clusters_dict[birth_type]
        ax.scatter(features["marriages_mean"], features["births_mean"], c=features["cluster"])

        for region in features.index:
            ax.annotate(
                region,
                (features.loc[region, "marriages_mean"], features.loc[region, "births_mean"]),
                fontsize=8,
            )

        ax.set_title(f"{metric_title(metric)} Regional Clusters: {birth_type.capitalize()} Births")
        ax.set_xlabel("Average Marriages")
        ax.set_ylabel(f"Average {birth_type.capitalize()} Births")

    plt.tight_layout()
    plt.show()


def plot_results(results: AnalysisResults):
    plot_national_trend(results.trend, results.metric)
    plot_lag_analysis(results.lags, results.metric)
    plot_lag_pre_post(results.pre_covid_lags, results.post_covid_lags, results.metric)
    plot_top_regions(results.correlations, results.metric)
    plot_elbow(results.inertia, results.metric)
    plot_clusters(results.clusters, results.metric)
