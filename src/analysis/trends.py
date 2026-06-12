import pandas as pd

from src.analysis.constants import COUNTRY_LEVEL, REGION_LEVEL
from src.analysis.metrics import filter_metric
from src.analysis.result import TrendDatasets, RawDatasets


def build_trend_dataset(raw_datasets: RawDatasets, metric, level, join_cols):
    marriages_df = filter_metric(raw_datasets.marriages, metric, level).rename(
        columns={"value": "marriages"}
    )

    births_marital_df = filter_metric(raw_datasets.marital, metric, level).rename(
        columns={"value": "births"}
    )

    births_nonmarital_df = filter_metric(raw_datasets.nonmarital, metric, level).rename(
        columns={"value": "births"}
    )

    births_all_df = filter_metric(raw_datasets.all_births, metric, level).rename(
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


def build_national_datasets(raw_datasets: RawDatasets, metric) -> TrendDatasets:
    return build_trend_dataset(
        raw_datasets,
        metric=metric,
        level=COUNTRY_LEVEL,
        join_cols=["year"],
    )


def build_regional_datasets(raw_datasets: RawDatasets, metric) -> TrendDatasets:
    return build_trend_dataset(
        raw_datasets,
        metric=metric,
        level=REGION_LEVEL,
        join_cols=["year", "territory_raw"],
    )
