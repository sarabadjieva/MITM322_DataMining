BIRTH_TYPES = ("marital", "nonmarital", "total")
RESIDENCE_METRICS = ("total", "rural", "urban")
# RESIDENCE_METRICS = {"total"}

COUNTRY_LEVEL = "country"
REGION_LEVEL = "district"

def filter_metric(df, metric, level):
    return df[(df["metric"] == metric) & (df["territory_level"] == level)].copy()

