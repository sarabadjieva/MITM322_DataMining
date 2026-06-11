from dataclasses import dataclass
import pandas as pd


@dataclass
class AnalysisResults:
    trend: dict[str, pd.DataFrame]
    lags: dict[str, pd.DataFrame]
    pre_covid_lags: dict[str, pd.DataFrame]
    post_covid_lags: dict[str, pd.DataFrame]
    regional: dict[str, pd.DataFrame]
    correlations: dict[str, pd.DataFrame]
    outside_share: pd.DataFrame
    clusters: dict[str, pd.DataFrame]
    inertia: dict[str, pd.DataFrame]