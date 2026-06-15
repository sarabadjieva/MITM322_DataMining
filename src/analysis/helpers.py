BIRTH_TYPES = ("marital", "nonmarital", "total")
RESIDENCE_METRICS = ("total", "rural", "urban")
# RESIDENCE_METRICS = {"total"}

COUNTRY_LEVEL = "country"
REGION_LEVEL = "district"

class Features:
    MARITAL_BEST_CORR = "marital_best_corr"
    MARITAL_BEST_LAG = "marital_best_lag"
    NONMARITAL_BEST_CORR = "nonmarital_best_corr"
    NONMARITAL_BEST_LAG = "nonmarital_best_lag"
    NONMARITAL_SHARE = "nonmarital_share"


CLUSTER_FEATURES = [
        Features.MARITAL_BEST_CORR,
        Features.MARITAL_BEST_LAG,
        Features.NONMARITAL_BEST_CORR,
        Features.NONMARITAL_BEST_LAG,
        Features.NONMARITAL_SHARE,
    ]

def filter_metric(df, metric, level):
    return df[(df["metric"] == metric) & (df["territory_level"] == level)].copy()

