import numpy as np
import pandas as pd

from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler

from src.analysis.classes import TrendDatasets


# Compute the linear trend as the slope of the best-fit line (value vs. year).
# Positive slope = increasing over time, negative slope = decreasing, near 0 = stable.
def compute_trend(group: pd.DataFrame, value_col: str) -> float:
    series = group[["year", value_col]].dropna().sort_values("year")
    if len(series) < 2:
        return 0.0

    x = series["year"].to_numpy(dtype=float)
    y = series[value_col].to_numpy(dtype=float)

    slope = np.polyfit(x, y, 1)[0]
    return float(slope)


def build_regional_cluster_features(regional: TrendDatasets):
    marital = regional.marital.rename(columns={"births": "marital_births"})
    nonmarital = regional.nonmarital.rename(columns={"births": "nonmarital_births"})

    merged = pd.merge(
        marital[["year", "territory_raw", "marriages", "marital_births"]],
        nonmarital[["year", "territory_raw", "nonmarital_births"]],
        on=["year", "territory_raw"],
    )
    merged["total_births"] = regional.total["births"]
    merged["percent_nonmarital_births"] = (
        merged["nonmarital_births"] / merged["total_births"]
    ) * 100

    grouped = merged.groupby("territory_raw")
    features = pd.DataFrame(
        {
            "mean_marriages": grouped["marriages"].mean(),
            "mean_marital_births": grouped["marital_births"].mean(),
            "mean_nonmarital_births": grouped["nonmarital_births"].mean(),
            "percent_nonmarital_births": grouped["percent_nonmarital_births"].mean(),
        }
    )

    features["marriages_trend"] = grouped.apply(lambda g: compute_trend(g, "marriages"))
    features["marital_births_trend"] = grouped.apply(lambda g: compute_trend(g, "marital_births"))
    features["nonmarital_births_trend"] = grouped.apply(
        lambda g: compute_trend(g, "nonmarital_births")
    )

    return features


def build_elbow_diagnostics(x_scaled, max_k):
    rows = []
    for k in range(1, max_k + 1):
        model = KMeans(n_clusters=k, random_state=42, n_init=10)
        model.fit(x_scaled)
        rows.append({"k": k, "inertia": model.inertia_})

    return pd.DataFrame(rows)


def cluster_regions(regional, n_clusters=5, max_k=10):
    features = build_regional_cluster_features(regional)
    x_scaled = StandardScaler().fit_transform(features)

    max_k = min(max_k, len(features))
    elbow_diagnostics = build_elbow_diagnostics(x_scaled, max_k)

    model = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
    features = features.copy()
    features["cluster"] = model.fit_predict(x_scaled)

    return features, elbow_diagnostics
