import matplotlib.pyplot as plt

from src.analysis.result import AnalysisResults, TrendDatasets


# def plot_national_trend(trend_dict):
#     fig, axes = plt.subplots(1, 3, figsize=(16, 6), sharey=True)
#
#     for ax, (birth_type, trend) in zip(axes, trend_dict.items()):
#         ax.plot(trend["year"], trend["marriages"], marker="o", label="Marriages")
#         ax.plot(trend["year"], trend["births"], marker="o", label=f"{birth_type.capitalize()} births")
#         ax.set_title(f"Marriages vs {birth_type.capitalize()} Births")
#         ax.set_xlabel("Year")
#         ax.set_ylabel("Count")
#         ax.grid(True)
#         ax.legend()
#
#     plt.tight_layout()
#     plt.show()

def plot_national_trend(trend_dict: TrendDatasets):
    marital = trend_dict.marital.sort_values("year")
    nonmarital = trend_dict.nonmarital.sort_values("year")
    shared = trend_dict.total.sort_values("year")

    fig, ax = plt.subplots(figsize=(12, 6))

    ax.plot(marital["year"],marital["marriages"],marker="o",linewidth=2,label="Marriages")
    ax.plot(marital["year"],marital["births"],marker="o",linewidth=2,label="Marital births")
    ax.plot(nonmarital["year"],nonmarital["births"],marker="o",linewidth=2,label="Nonmarital births")
    ax.plot(shared["year"],shared["births"],marker="o",linewidth=2,label="Total births")

    ax.set_title("Marriages and Births Over Time")
    ax.set_xlabel("Year")
    ax.set_ylabel("Count")
    ax.grid(True, alpha=0.3)
    ax.legend()
    plt.tight_layout()
    plt.show()


def plot_lag_analysis(lag_dict):
    fig, axes = plt.subplots(1, 3, figsize=(14, 5), sharey=True)

    for ax, (birth_type, lag_df) in zip(axes, lag_dict.items()):
        ax.bar(lag_df["lag"], lag_df["correlation"])
        ax.set_title(f"Lag Analysis: {birth_type.capitalize()} Births")
        ax.set_xlabel("Lag (years)")
        ax.set_ylabel("Correlation")

    plt.tight_layout()
    plt.show()


def plot_lag_pre_post(lags_pre, lags_post):
    import matplotlib.pyplot as plt

    fig, axes = plt.subplots(2, 3, figsize=(14, 10), sharey=True)

    birth_types = ["marital", "nonmarital"]
    titles = {
        "marital": "Marital Births",
        "nonmarital": "Nonmarital Births",
    }

    for row, birth_type in enumerate(birth_types):
        pre_df = lags_pre[birth_type]
        post_df = lags_post[birth_type]

        axes[row, 0].bar(pre_df["lag"], pre_df["correlation"], color="steelblue")
        axes[row, 0].set_title(f"{titles[birth_type]} — Pre-COVID (2010–2019)")
        axes[row, 0].set_xlabel("Lag (years)")
        axes[row, 0].set_ylabel("Correlation")

        axes[row, 1].bar(post_df["lag"], post_df["correlation"], color="darkorange")
        axes[row, 1].set_title(f"{titles[birth_type]} — Post-COVID (2020–2025)")
        axes[row, 1].set_xlabel("Lag (years)")

    plt.tight_layout()
    plt.show()


def plot_top_regions(corr_dict, top_n=15):
    fig, axes = plt.subplots(1, 3, figsize=(16, 8), sharex=True)

    for ax, (birth_type, corr_df) in zip(axes, corr_dict.items()):
        top = corr_df.head(top_n).sort_values("correlation")
        ax.barh(top["region"], top["correlation"])
        ax.set_title(f"Top Regions: {birth_type.capitalize()} Births")
        ax.set_xlabel("Correlation")

    plt.tight_layout()
    plt.show()


def plot_outside_share(share):
    plt.figure(figsize=(12, 6))
    plt.plot(share["year"], share["outside_share"], marker="o")
    plt.title("Share of Births Outside Marriage")
    plt.xlabel("Year")
    plt.ylabel("%")
    plt.grid(True)
    plt.tight_layout()
    plt.show()


def plot_elbow(inertia_dict):
    fig, axes = plt.subplots(1, 3, figsize=(14, 5), sharey=True)

    for ax, (birth_type, inertia_df) in zip(axes, inertia_dict.items()):
        ax.plot(inertia_df["k"], inertia_df["inertia"], marker="o")
        ax.set_title(f"Elbow Method: {birth_type.capitalize()} Births")
        ax.set_xlabel("Number of Clusters")
        ax.set_ylabel("Inertia")

    plt.tight_layout()
    plt.show()


def plot_clusters(clusters_dict):
    fig, axes = plt.subplots(1, 3, figsize=(16, 8), sharex=False, sharey=False)

    for ax, (birth_type, features) in zip(axes, clusters_dict.items()):
        ax.scatter(features["marriages_mean"], features["births_mean"], c=features["cluster"])

        for region in features.index:
            ax.annotate(
                region,
                (features.loc[region, "marriages_mean"], features.loc[region, "births_mean"]),
                fontsize=8,
            )

        ax.set_title(f"Regional Clusters: {birth_type.capitalize()} Births")
        ax.set_xlabel("Average Marriages")
        ax.set_ylabel(f"Average {birth_type.capitalize()} Births")


        #ax.set_xscale("log")
        #ax.set_yscale("log")

    plt.tight_layout()
    plt.show()

def plot_results(results: AnalysisResults):
    plot_national_trend(results.trend)
    plot_lag_analysis(results.lags)
    plot_lag_pre_post(results.pre_covid_lags, results.post_covid_lags)
    plot_top_regions(results.correlations)
    plot_outside_share(results.outside_share)
    plot_elbow(results.inertia)
    plot_clusters(results.clusters)