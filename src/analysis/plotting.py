import matplotlib.pyplot as plt

def plot_national_trend(trend):
    plt.figure(figsize=(12, 6))
    plt.plot(trend["year"], trend["value_marriages"], marker="o", label="Marriages")
    plt.plot(trend["year"], trend["value_births"], marker="o", label="Births")
    plt.title("Births vs Marriages in Bulgaria")
    plt.xlabel("Year")
    plt.ylabel("Count")
    plt.legend()
    plt.grid(True)
    plt.show()


def plot_lag_analysis(lag_df):
    plt.figure(figsize=(8, 5))
    plt.bar(lag_df["lag"], lag_df["correlation"])
    plt.xlabel("Lag (years)")
    plt.ylabel("Correlation")
    plt.title("Marriage-Birth Lag Analysis")
    plt.show()


def plot_top_regions(corr_df, top_n=15):
    top = corr_df.head(top_n)
    plt.figure(figsize=(10, 8))
    plt.barh(top["region"], top["correlation"])
    plt.title("Top Regions by Correlation")
    plt.show()


def plot_outside_share(share):
    plt.figure(figsize=(12, 6))
    plt.plot(share["year"], share["outside_share"], marker="o")
    plt.title("Share of Births Outside Marriage")
    plt.xlabel("Year")
    plt.ylabel("%")
    plt.grid(True)
    plt.show()


def plot_elbow(inertia_df):
    plt.figure(figsize=(8, 5))
    plt.plot(inertia_df["k"], inertia_df["inertia"], marker="o")
    plt.title("Elbow Method")
    plt.xlabel("Number of Clusters")
    plt.ylabel("Inertia")
    plt.show()


def plot_clusters(features):
    plt.figure(figsize=(10, 8))
    plt.scatter(features["marriages"], features["births"], c=features["cluster"])

    for region in features.index:
        plt.annotate(
            region,
            (features.loc[region, "marriages"], features.loc[region, "births"]),
            fontsize=8,
        )

    plt.title("Regional Clusters")
    plt.xlabel("Average Marriages")
    plt.ylabel("Average Births")
    plt.show()
