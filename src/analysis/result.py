from dataclasses import dataclass

import pandas as pd

@dataclass
class AnalysisResults:
    trend: pd.DataFrame
    lags: pd.DataFrame
    regional: pd.DataFrame
    correlations: pd.DataFrame
    outside_share: pd.DataFrame
    clusters: pd.DataFrame
    inertia: pd.DataFrame