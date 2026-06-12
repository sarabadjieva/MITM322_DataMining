import numpy as np
import pandas as pd

from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler


def compute_trend(group: pd.DataFrame, value_col: str) -> float:
    series = group[["year", value_col]].dropna().sort_values("year")
    if len(series) < 2:
        return 0.0

    x = series["year"].to_numpy(dtype=float)
    y = series[value_col].to_numpy(dtype=float)

    slope = np.polyfit(x, y, 1)[0]
    return float(slope)


def cluster_regions(regional, n_clusters=9, max_k=20):
    grouped = regional.groupby("territory_raw")

    features = pd.DataFrame({
        "marriages_mean": grouped["marriages"].mean(),
        # marital and nonmarital
        "births_mean": grouped["births"].mean(),
        # percent nonmarital
    })

    features["marriages_trend"] = grouped.apply(
        lambda g: compute_trend(g, "marriages")
    )
    features["births_trend"] = grouped.apply(
        lambda g: compute_trend(g, "births")
    )

    scaler = StandardScaler()
    x_scaled = scaler.fit_transform(features)

    inertias = []
    K = range(1, max_k + 1)
    for k in K:
        model = KMeans(n_clusters=k, random_state=42, n_init=10)
        model.fit(x_scaled)
        inertias.append({"k": k, "inertia": model.inertia_})

    final_model = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
    features = features.copy()
    features["cluster"] = final_model.fit_predict(x_scaled)

    return features, pd.DataFrame(inertias)