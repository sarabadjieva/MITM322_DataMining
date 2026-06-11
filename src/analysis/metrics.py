import pandas as pd

COUNTRY_LEVEL = "country"
REGION_LEVEL = "district"

def filter_metric(df, metric, level):
    return df[(df["metric"] == metric) & (df["territory_level"] == level)].copy()

def national_trend(marriages, births):
    bg_marriages = filter_metric(marriages, "total", COUNTRY_LEVEL)
    bg_births = filter_metric(births, "total", COUNTRY_LEVEL)

    return pd.merge(
        bg_marriages[["year", "value"]],
        bg_births[["year", "value"]],
        on="year",
        suffixes=("_marriages", "_births"),
    )


def regional_dataset(marriages, births):
    regional_marriages = filter_metric(marriages, "total", REGION_LEVEL).rename(
        columns={"value": "marriages"}
    )
    regional_births = filter_metric(births, "total", REGION_LEVEL).rename(
        columns={"value": "births"}
    )

    return pd.merge(
        regional_marriages[["year", "territory_raw", "marriages"]],
        regional_births[["year", "territory_raw", "births"]],
        on=["year", "territory_raw"],
    )


def outside_marriage_share(births_status):
    country_status = births_status[births_status["territory_level"] == COUNTRY_LEVEL].copy()

    total_births = country_status[country_status["measure"] == "Общо | всичко"][
        ["year", "value"]
    ].rename(columns={"value": "value_total"})

    outside_births = (
        country_status[country_status["measure"].str.contains("извън", case=False, na=False)]
        .groupby("year")["value"]
        .sum()
        .reset_index()
        .rename(columns={"value": "value_outside"})
    )

    share = pd.merge(total_births, outside_births, on="year")
    share["outside_share"] = (share["value_outside"] / share["value_total"]) * 100
    return share



def lag_correlations(trend, max_lag=5):
    rows = []
    for lag in range(max_lag + 1):
        corr = trend["value_marriages"].corr(trend["value_births"].shift(-lag))
        rows.append({"lag": lag, "correlation": corr})
    return pd.DataFrame(rows)


def regional_correlations(regional):
    rows = []
    for region, group in regional.groupby("territory_raw"):
        rows.append(
            {
                "region": region,
                "correlation": group["marriages"].corr(group["births"]),
            }
        )
    return pd.DataFrame(rows).sort_values("correlation", ascending=False)
