import pandas as pd

from src.analysis.metrics import filter_metric
from src.analysis.result import TrendDatasets, RawDatasets

# promqna brok brakove prez godinite
# promqna na dql/procent na nonmarital
# districts s nai-burz rastej na nonmarital

COUNTRY_LEVEL = "country"
REGION_LEVEL = "district"

def build_trend_dataset(raw_datasets: RawDatasets, level, join_cols):
    marriages_df = filter_metric(raw_datasets.marriages, "total", level).rename(
        columns={"value": "marriages"}
    )

    births_marital_df = filter_metric(raw_datasets.marital, "total", level).rename(
        columns={"value": "births"}
    )

    births_nonmarital_df = filter_metric(raw_datasets.nonmarital, "total", level).rename(
        columns={"value": "births"}
    )

    births_all_df = filter_metric(raw_datasets.all_births, "total", level).rename(
        columns={"value": "births"}
    )

    trend_marital = pd.merge(
        marriages_df[join_cols + ["marriages"]],
        births_marital_df[join_cols + ["births"]],
        on=join_cols,
    )

    trend_nonmarital = pd.merge(
        marriages_df[join_cols + ["marriages"]],
        births_nonmarital_df[join_cols + ["births"]],
        on=join_cols,
    )

    trend_shared = pd.merge(
        marriages_df[join_cols + ["marriages"]],
        births_all_df[join_cols + ["births"]],
        on=join_cols,
    )

    return TrendDatasets(trend_marital, trend_nonmarital, trend_shared)


def build_national_datasets(raw_datasets: RawDatasets) -> TrendDatasets:
    return build_trend_dataset(
        raw_datasets,
        level=COUNTRY_LEVEL,
        join_cols=["year"],
    )


def build_regional_datasets(raw_datasets: RawDatasets) -> TrendDatasets:
    return build_trend_dataset(
        raw_datasets,
        level=REGION_LEVEL,
        join_cols=["year", "territory_raw"],
    )
