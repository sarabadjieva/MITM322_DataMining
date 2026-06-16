BIRTH_TYPES = ("marital", "nonmarital", "total")
RESIDENCE_METRICS = ("total", "rural", "urban")
# RESIDENCE_METRICS = {"total"}

COUNTRY_LEVEL = "country"
REGION_LEVEL = "district"

def birth_type_title(birth_type):
    if birth_type == "marital":
        return "брачни"
    if birth_type == "nonmarital":
        return "извънбрачни"
    if birth_type == "total":
        return "всички"

    return birth_type


def metric_title(metric):
    if metric == "total":
        return "Общо"
    if metric == "urban":
        return "Градове"
    if metric == "rural":
        return "Села"

    return metric


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
        Features.NONMARITAL_SHARE
    ]


FEATURE_LABELS = {
    Features.MARITAL_BEST_CORR: "Най-силна корелация\n с брачни раждания",
    Features.MARITAL_BEST_LAG: "Лаг на най-силната\n корелация (брачни)",
    Features.NONMARITAL_BEST_CORR: "Най-силна корелация\n с извънбрачни раждания",
    Features.NONMARITAL_BEST_LAG: "Лаг на най-силната\n корелация (извънбрачни)",
    Features.NONMARITAL_SHARE: "Дял извънбрачни\n раждания (%)",
}


def filter_metric(df, metric, level):
    return df[(df["metric"] == metric) & (df["territory_level"] == level)].copy()

