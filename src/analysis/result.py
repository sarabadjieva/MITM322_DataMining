from dataclasses import dataclass
import pandas as pd


@dataclass
class RawDatasets:
    marriages: pd.DataFrame
    marital: pd.DataFrame
    nonmarital: pd.DataFrame
    all_births: pd.DataFrame


@dataclass
class TrendDatasets:
    marital: pd.DataFrame
    nonmarital: pd.DataFrame
    total: pd.DataFrame

    def items(self):
        return (
            ("marital", self.marital),
            ("nonmarital", self.nonmarital),
            ("total", self.total),
        )


@dataclass
class AnalysisResults:
    metric: str
    trend: TrendDatasets
    lags: dict[str, pd.DataFrame]
    pre_covid_lags: dict[str, pd.DataFrame]
    post_covid_lags: dict[str, pd.DataFrame]
    regional: TrendDatasets
    correlations: dict[str, pd.DataFrame]
    nonmarital_share: pd.DataFrame
    clusters: dict[str, pd.DataFrame]
    inertia: dict[str, pd.DataFrame]


@dataclass
class MultiMetricAnalysisResults:
    by_metric: dict[str, AnalysisResults]
    nonmarital_share_by_metric: pd.DataFrame
