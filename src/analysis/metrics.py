import pandas as pd

from src.analysis.constants import COUNTRY_LEVEL, RESIDENCE_METRICS
from src.analysis.result import TrendDatasets



def filter_metric(df, metric, level):
    return df[(df["metric"] == metric) & (df["territory_level"] == level)].copy()


def nonmarital_birth_share(births_marital, births_nonmarital, metric, level=COUNTRY_LEVEL):
    marital = filter_metric(births_marital, metric, level).rename(
        columns={"value": "value_marital"}
    )
    nonmarital = filter_metric(births_nonmarital, metric, level).rename(
        columns={"value": "value_nonmarital"}
    )

    share = pd.merge(
        marital[["year", "value_marital"]],
        nonmarital[["year", "value_nonmarital"]],
        on="year",
    ).sort_values("year")

    share["metric"] = metric
    share["value_total"] = share["value_marital"] + share["value_nonmarital"]
    share["nonmarital_share"] = (share["value_nonmarital"] / share["value_total"]) * 100
    share["share_change_pp"] = share["nonmarital_share"].diff()
    share["share_change_pct"] = share["nonmarital_share"].pct_change() * 100
    share["period_change_pp"] = share["nonmarital_share"] - share["nonmarital_share"].iloc[0]

    return share.reset_index(drop=True)


def nonmarital_birth_share_by_metric(
    births_marital,
    births_nonmarital,
    metrics=RESIDENCE_METRICS,
    level=COUNTRY_LEVEL,
):
    return pd.concat(
        [
            nonmarital_birth_share(
                births_marital,
                births_nonmarital,
                metric,
                level=level,
            )
            for metric in metrics
        ],
        ignore_index=True,
    )


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
