import pandas as pd

from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler

def cluster_regions(regional, n_clusters=3, max_k=9):
    features = regional.groupby("territory_raw")[["marriages", "births"]].mean()

    scaler = StandardScaler()
    x_scaled = scaler.fit_transform(features)

    inertia = []
    for k in range(1, max_k + 1):
        model = KMeans(n_clusters=k, random_state=42, n_init=10)
        model.fit(x_scaled)
        inertia.append({"k": k, "inertia": model.inertia_})

    final_model = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
    features = features.copy()
    features["cluster"] = final_model.fit_predict(x_scaled)

    return features, pd.DataFrame(inertia)