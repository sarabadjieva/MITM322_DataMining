import pandas as pd

from src.analysis.classes import TrendDatasets
from src.analysis.helpers import COUNTRY_LEVEL


def nonmarital_birth_share(trend_data: TrendDatasets, level=COUNTRY_LEVEL):
    marital_df = trend_data.marital.rename(columns={"births": "marital_births"})
    nonmarital_df = trend_data.nonmarital.rename(columns={"births": "nonmarital_births"})

    join_cols = ["year"] if level is COUNTRY_LEVEL else ["year", "territory_raw"]
    share = pd.merge(
        marital_df[join_cols + ["marital_births"]],
        nonmarital_df[join_cols + ["nonmarital_births"]],
        on=join_cols,
        how="inner",
    )

    share["total_births"] = share["marital_births"] + share["nonmarital_births"]
    share["nonmarital_share"] = (share["nonmarital_births"] / share["total_births"] * 100)

    return share.reset_index(drop=True)