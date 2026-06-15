import pandas as pd
from src.analysis.helpers import filter_metric, COUNTRY_LEVEL


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
