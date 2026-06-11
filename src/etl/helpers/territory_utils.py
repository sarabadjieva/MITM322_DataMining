from functools import cache

from src.etl.helpers.text_utils import normalize_text
from src.etl.helpers.const_vals import TOTAL_LABELS, AREA_LABELS


def keep_only_districts(data_df):
    keep_rows = []
    seen_districts = set()
    current_district = None

    for idx, row in data_df.iterrows():
        name = normalize_text(row.iloc[0])
        if not name:
            continue

        if name and name in TOTAL_LABELS:
            keep_rows.append(idx)
            current_district = None
            continue

        if name in AREA_LABELS and name not in seen_districts:
            keep_rows.append(idx)
            seen_districts.add(name)
            current_district = name
            continue

        if current_district and name == current_district:
            continue

    return data_df.loc[keep_rows].copy()


@cache
def get_territory_level(name, current_district=None) -> str|None:
    name = normalize_text(name)

    if not name:
        return None

    if name in TOTAL_LABELS:
        return "country"

    if current_district is None and name in AREA_LABELS:
        return "district"

    if current_district is not None and name in AREA_LABELS:
        return "municipality"

    if current_district:
        return "municipality"

    return "unknown"


def territory_metric_row(year, name, metric, value):
    return {
        "year": year,
        "territory_raw": name,
        "territory_level": get_territory_level(name),
        "metric": metric,
        "value": value,
    }
