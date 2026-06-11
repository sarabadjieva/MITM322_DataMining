import pandas as pd
from pathlib import Path

from src.etl.helpers.marriages_parser_utils import find_year_row, find_data_start_by_country, extract_metric_records
from src.etl.helpers.territory_utils import territory_metric_row
from src.etl.helpers.text_utils import normalize_text


def parse_marriages(path: Path) -> pd.DataFrame:
    df = pd.read_excel(path, header=None, dtype=object)
    year_row_idx, years = find_year_row(df)
    data_start = find_data_start_by_country(df, year_row_idx)

    ordered_years = sorted(years.items(), key=lambda item: item[0])
    rows = []

    for row_idx in range(data_start, len(df)):
        row = df.iloc[row_idx].tolist()
        name = normalize_text(row[0])
        if not name:
            continue

        for year, metric_name, value in extract_metric_records(row, ordered_years):
            rows.append(territory_metric_row(year, name, metric_name, value))

    return pd.DataFrame(rows)