import pandas as pd
from scipy.cluster.hierarchy import linkage, fcluster

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


def cluster_regions(regional, n_clusters=4):
    features = build_correlation_cluster_features(regional)
    x_scaled = StandardScaler().fit_transform(features)

    linkage_matrix = linkage(x_scaled, method="ward")

    result = features.copy()
    result["cluster"] = fcluster(
        linkage_matrix,
        t=n_clusters,
        criterion="maxclust",
    )

    return result, linkage_matrix
