import pandas as pd

from src.analysis.result import TrendDatasets

COUNTRY_LEVEL = "country"
REGION_LEVEL = "district"


def filter_metric(df, metric, level):
    return df[(df["metric"] == metric) & (df["territory_level"] == level)].copy()


def outside_marriage_share(births_marital, births_nonmarital):
    country_marital = filter_metric(births_marital, "total", COUNTRY_LEVEL).rename(
        columns={"value": "value_marital"}
    )
    country_nonmarital = filter_metric(births_nonmarital, "total", COUNTRY_LEVEL).rename(
        columns={"value": "value_nonmarital"}
    )

    share = pd.merge(
        country_marital[["year", "value_marital"]],
        country_nonmarital[["year", "value_nonmarital"]],
        on="year",
    )

    share["value_total"] = share["value_marital"] + share["value_nonmarital"]
    share["outside_share"] = (share["value_nonmarital"] / share["value_total"]) * 100

    return share.sort_values("year").reset_index(drop=True)

def lag_correlations_period(trend_dict: TrendDatasets, start_year, end_year, max_lag=5):
    result = {}

    for birth_type, trend in {
        "marital": trend_dict.marital,
        "nonmarital": trend_dict.nonmarital,
        "total": trend_dict.total,
    }.items():
        sub = trend[(trend["year"] >= start_year) & (trend["year"] <= end_year)].copy()

        rows = []
        for lag in range(max_lag + 1):
            corr = sub["marriages"].corr(sub["births"].shift(-lag))
            rows.append({"lag": lag, "correlation": corr})

        result[birth_type] = pd.DataFrame(rows)

    return result

def regional_correlations(regional_dict: TrendDatasets):
    result = {}

    for birth_type, trend in {
        "marital": regional_dict.marital,
        "nonmarital": regional_dict.nonmarital,
        "total": regional_dict.total,
    }.items():
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