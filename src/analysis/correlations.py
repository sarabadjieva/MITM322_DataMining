import pandas as pd

from src.analysis.classes import TrendDatasets


def lag_correlations_period(trend_dict: TrendDatasets, start_year, end_year, max_lag=5):
    result = {}

    for birth_type, trend in trend_dict.items():
        sub = trend[(trend["year"] >= start_year) & (trend["year"] <= end_year)].copy()

        rows = []
        for lag in range(max_lag + 1):
            corr = sub["marriages"].corr(sub["births"].shift(-lag))
            rows.append({"lag": lag, "correlation": corr})

        result[birth_type] = pd.DataFrame(rows)

    return result

def regional_correlations(regional_dict: TrendDatasets):
    result = {}

    for birth_type, trend in regional_dict.items():
        rows = []
        for region, group in trend.groupby("territory_raw"):
            rows.append(
                {
                    "region": region,
                    "correlation": group["marriages"].corr(group["births"]),
                }
            )
        result[birth_type] = pd.DataFrame(rows).sort_values("correlation", ascending=False)

    return result
