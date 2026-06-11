import matplotlib.pyplot as plt


def plot_national_trend(trend_dict):
    fig, axes = plt.subplots(1, 2, figsize=(16, 6), sharey=True)

    for ax, (birth_type, trend) in zip(axes, trend_dict.items()):
        ax.plot(trend["year"], trend["value_marriages"], marker="o", label="Marriages")
        ax.plot(trend["year"], trend["value_births"], marker="o", label=f"{birth_type.capitalize()} births")
        ax.set_title(f"Marriages vs {birth_type.capitalize()} Births")
        ax.set_xlabel("Year")
        ax.set_ylabel("Count")
        ax.grid(True)
        ax.legend()

    plt.tight_layout()
    plt.show()


def plot_lag_analysis(lag_dict):
    fig, axes = plt.subplots(1, 2, figsize=(14, 5), sharey=True)

    for ax, (birth_type, lag_df) in zip(axes, lag_dict.items()):
        ax.bar(lag_df["lag"], lag_df["correlation"])
        ax.set_title(f"Lag Analysis: {birth_type.capitalize()} Births")
        ax.set_xlabel("Lag (years)")
        ax.set_ylabel("Correlation")

    plt.tight_layout()
    plt.show()


def plot_top_regions(corr_dict, top_n=15):
    fig, axes = plt.subplots(1, 2, figsize=(16, 8), sharex=True)

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
    fig, axes = plt.subplots(1, 2, figsize=(14, 5), sharey=True)

    for ax, (birth_type, inertia_df) in zip(axes, inertia_dict.items()):
        ax.plot(inertia_df["k"], inertia_df["inertia"], marker="o")
        ax.set_title(f"Elbow Method: {birth_type.capitalize()} Births")
        ax.set_xlabel("Number of Clusters")
        ax.set_ylabel("Inertia")

    plt.tight_layout()
    plt.show()


def plot_clusters(clusters_dict):
    fig, axes = plt.subplots(1, 2, figsize=(16, 8), sharex=False, sharey=False)

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


        ax.set_xscale("log")
        ax.set_yscale("log")

    plt.tight_layout()
    plt.show()