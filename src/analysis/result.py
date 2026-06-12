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


@dataclass
class AnalysisResults:
    trend: TrendDatasets
    lags: dict[str, pd.DataFrame]
    pre_covid_lags: dict[str, pd.DataFrame]
    post_covid_lags: dict[str, pd.DataFrame]
    regional: dict[str, pd.DataFrame]
    correlations: dict[str, pd.DataFrame]
    outside_share: pd.DataFrame
    clusters: dict[str, pd.DataFrame]
    inertia: dict[str, pd.DataFrame]