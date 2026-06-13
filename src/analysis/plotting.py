import matplotlib.pyplot as plt

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

    show_plot()


def plot_top_regions(corr_dict, metric, top_n=15):
    fig, axes = plt.subplots(1, len(BIRTH_TYPES), figsize=(16, 8), sharex=True)

    for ax, birth_type in zip(axes, BIRTH_TYPES):
        top = corr_dict[birth_type].head(top_n).sort_values("correlation")
        ax.barh(top["region"], top["correlation"])
        ax.set_title(f"{metric_title(metric)} Top Regions: {birth_type.capitalize()} Births")
        ax.set_xlabel("Correlation")

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
    features = first_frame(clusters_dict)
    fig, ax = plt.subplots(figsize=(10, 8))

    ax.scatter(
        features["mean_marriages"],
        features["percent_nonmarital_births"],
        c=features["cluster"],
    )

    for region in features.index:
        ax.annotate(
            region,
            (
                features.loc[region, "mean_marriages"],
                features.loc[region, "percent_nonmarital_births"],
            ),
            fontsize=8,
        )

    ax.set_title(f"{metric_title(metric)} Regional Clusters")
    ax.set_xlabel("Mean Marriages")
    ax.set_ylabel("% Non-Marital Births")

    show_plot()


def plot_anomalies(anomalies, metric):
    fig, ax = plt.subplots(figsize=(10, 8))

    normal = anomalies[~anomalies["is_anomaly"]]
    outliers = anomalies[anomalies["is_anomaly"]]

    ax.scatter(
        normal["mean_marriages"],
        normal["percent_nonmarital_births"],
        c=normal["cluster"],
        alpha=0.7,
        label="Normal",
    )
    ax.scatter(
        outliers["mean_marriages"],
        outliers["percent_nonmarital_births"],
        color="red",
        edgecolor="black",
        label="Anomaly",
    )

    for region in outliers.index:
        ax.annotate(
            region,
            (
                outliers.loc[region, "mean_marriages"],
                outliers.loc[region, "percent_nonmarital_births"],
            ),
            fontsize=8,
        )

    ax.set_title(f"{metric_title(metric)} Regional Anomalies")
    ax.set_xlabel("Mean Marriages")
    ax.set_ylabel("% Non-Marital Births")
    ax.legend()
    show_plot()


def plot_results(results: AnalysisResults):
    # plot_national_trend(results.national_sets, results.metric)
    # plot_lag_analysis(results.lags, results.metric)
    # plot_lag_pre_post(results.pre_covid_lags, results.post_covid_lags, results.metric)
    # plot_top_regions(results.correlations, results.metric)
    plot_nonmarital_share(results.nonmarital_share, results.metric)
    # plot_elbow(results.inertia, results.metric)
    # plot_clusters(results.clusters, results.metric)
    # plot_anomalies(results.anomalies, results.metric)
