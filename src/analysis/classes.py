from dataclasses import dataclass
import pandas as pd


@dataclass
class RawDatasets:
    marriages: pd.DataFrame
    marital: pd.DataFrame
    nonmarital: pd.DataFrame
    all_births: pd.DataFrame
    population: pd.DataFrame


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
    national_sets: TrendDatasets
    regional_sets: TrendDatasets
    lags: dict[str, pd.DataFrame]
    regional_lags: dict[str, pd.DataFrame]
    nonmarital_share: pd.DataFrame
    clusters: dict[str, pd.DataFrame]
    inertia: dict[str, pd.DataFrame]