import pandas as pd
from pathlib import Path

from src.etl.file_configs import TRIPLET_METRICS
from src.etl.helpers.parser_utils import find_year_row, find_data_start_by_country, extract_metric_records
from src.etl.helpers.territory_filters import keep_only_districts
from src.etl.helpers.territory_utils import classify_territory
from src.etl.helpers.text_utils import normalize_text


def territory_metric_row(year, name, metric, value):
    return {
        "year": year,
        "territory_raw": name,
        "territory_level": classify_territory(name).level,
        "metric": metric,
        "value": value,
    }


def parse_marriages(path: Path, dataset: str, filter_districts: bool = False) -> pd.DataFrame:
    df = pd.read_excel(path, header=None, dtype=object)
    year_row_idx, years = find_year_row(df)
    data_start = find_data_start_by_country(df, year_row_idx)

    if filter_districts:
        header = df.iloc[:data_start]
        data = keep_only_districts(df.iloc[data_start:])
        df = pd.concat([header, data])

    ordered_years = sorted(years.items(), key=lambda item: item[0])
    metrics = TRIPLET_METRICS.get(dataset, TRIPLET_METRICS["_default"])
    rows = []

    for row_idx in range(data_start, len(df)):
        row = df.iloc[row_idx].tolist()
        name = normalize_text(row[0])
        if not name:
            continue

        for year, metric_name, value in extract_metric_records(row, ordered_years, metrics):
            rows.append(territory_metric_row(year, name, metric_name, value))

    return pd.DataFrame(rows)