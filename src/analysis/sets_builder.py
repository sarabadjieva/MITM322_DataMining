import pandas as pd

from src.analysis.helpers import COUNTRY_LEVEL, REGION_LEVEL, filter_metric
from src.analysis.classes import TrendDatasets, RawDatasets


def build_trend_dataset(raw_datasets: RawDatasets, metric, level, join_cols):
    marriages_df = filter_metric(raw_datasets.marriages, metric, level).rename(
        columns={"value": "marriages"}
    )

    def merge_births(births_df):
        births_df = filter_metric(births_df, metric, level).rename(
            columns={"value": "births"}
        )
        return pd.merge(
            marriages_df[join_cols + ["marriages"]],
            births_df[join_cols + ["births"]],
            on=join_cols,
        )

    return TrendDatasets(
        marital=merge_births(raw_datasets.marital),
        nonmarital=merge_births(raw_datasets.nonmarital),
        total=merge_births(raw_datasets.all_births),
    )


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
