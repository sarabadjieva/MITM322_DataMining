import pandas as pd

from src.etl.file_configs import METRIC_SEQUENCE
from src.etl.helpers.const_vals import TOTAL_LABELS
from src.etl.helpers.text_utils import find_years_in_row, to_number, normalize_text


def find_year_row(df: pd.DataFrame, max_rows: int = 10) -> tuple[int, dict[int, int]]:
    for i in range(min(max_rows, len(df))):
        years = find_years_in_row(df.iloc[i].tolist())
        if len(years) >= 3:
            return i, years
    raise ValueError("Cannot find year row")


def iter_year_blocks(row, ordered_years, block_size):
    for col_idx, year in ordered_years:
        values = row[col_idx : col_idx + block_size]
        if len(values) < block_size:
            continue

        numbers = [to_number(v) for v in values]
        if all(pd.isna(v) for v in numbers):
            continue

        yield year, numbers


def extract_metric_records(row, ordered_years):
    block_size = len(METRIC_SEQUENCE)
    for year, numbers in iter_year_blocks(row, ordered_years, block_size):
        for metric_name, value in zip(METRIC_SEQUENCE, numbers):
            yield year, metric_name, value



def find_data_start_by_country(df, year_row_idx, max_search=50):
    for i in range(year_row_idx + 1, min(year_row_idx + 1 + max_search, len(df))):
        name = normalize_text(df.iloc[i, 0])
        if name in TOTAL_LABELS:
            return i
    return year_row_idx + 3


