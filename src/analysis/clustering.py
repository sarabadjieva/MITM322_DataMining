import pandas as pd
from scipy.cluster.hierarchy import linkage, fcluster
from sklearn.metrics import silhouette_score

from sklearn.preprocessing import StandardScaler

from src.analysis.correlations import regional_lag_matrix
from src.analysis.helpers import REGION_LEVEL, Features
from src.analysis.nonmarital_birth_share import nonmarital_birth_share


def build_correlation_cluster_features(regional, max_lag=5):
    correlations = regional_lag_matrix(regional, max_lag=max_lag)

    marital = correlations["marital"]
    nonmarital = correlations["nonmarital"]

    features = pd.DataFrame(index=marital.index)

    abs_marital = marital.abs()

    features[Features.MARITAL_BEST_LAG] = abs_marital.idxmax(axis=1).astype(int)
    features[Features.MARITAL_BEST_CORR] = marital.apply(
        lambda row: row.loc[row.abs().idxmax()],
        axis=1
    )

    abs_nonmarital = nonmarital.abs()

    features[Features.NONMARITAL_BEST_LAG] = abs_nonmarital.idxmax(axis=1).astype(int)
    features[Features.NONMARITAL_BEST_CORR] = nonmarital.apply(
        lambda row: row.loc[row.abs().idxmax()],
        axis=1
    )

    share = nonmarital_birth_share(regional, REGION_LEVEL)
    share = share.groupby("territory_raw")[Features.NONMARITAL_SHARE].mean()
    features = features.join(share)

    return features.fillna(features.mean())


def cluster_regions(regional, min_clusters=3, max_clusters=5):
    features = build_correlation_cluster_features(regional)

    x_scaled = StandardScaler().fit_transform(features)

    linkage_matrix = linkage(x_scaled, method="ward")

    best_score = -1
    best_labels = None

    max_clusters = min(max_clusters, len(features) - 1)
    for k in range(min_clusters, max_clusters + 1):
        labels = fcluster(
            linkage_matrix,
            t=k,
            criterion="maxclust",
        )

        score = silhouette_score(x_scaled, labels)

        if score > best_score:
            best_score = score
            best_labels = labels

    result = features.copy()
    result["cluster"] = best_labels

    return result, linkage_matrix