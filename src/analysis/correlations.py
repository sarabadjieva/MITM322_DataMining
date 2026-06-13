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


def regional_lag_matrix(regional_dict: TrendDatasets, max_lag=5):
    result = {}

    for birth_type, trend in regional_dict.items():
        rows = []
        for region, group in trend.groupby("territory_raw"):
            group_sorted = group.sort_values("year")
            row = {"region": region}
            for lag in range(max_lag + 1):
                corr = group_sorted["marriages"].corr(group_sorted["births"].shift(-lag))
                row[f"{lag}"] = corr
            rows.append(row)

        df = pd.DataFrame(rows).set_index("region")
        result[birth_type] = df

    return result
