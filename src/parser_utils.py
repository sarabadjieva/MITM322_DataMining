from src.const_vals import TOTAL_LABELS
from src.text_utils import find_years_in_row, normalize_text, to_number
import pandas as pd

def find_header_row(df, predicates, max_rows=8):
    for i in range(min(max_rows, len(df))):
        text = row_to_text(df.iloc[i])

        if any(predicate(text) for predicate in predicates):
            return i

    return None

def row_to_text(row):
    return " | ".join(
        str(x)
        for x in row.tolist()
        if pd.notna(x)
    )

def find_year_row(df: pd.DataFrame, max_rows: int = 10) -> tuple[int, dict[int, int]]:
    for i in range(min(max_rows, len(df))):
        yrs = find_years_in_row(df.iloc[i].tolist())
        if len(yrs) >= 3:
            return i, yrs
    raise ValueError("Cannot find year row")

def find_data_start_by_country(df, year_row_idx, max_search=50):
    # търсим в следващите N реда след реда с годините
    for i in range(year_row_idx + 1, min(year_row_idx + 1 + max_search, len(df))):
        name = normalize_text(df.iloc[i, 0])
        if name in TOTAL_LABELS:  # "Общо за страната", "България", "Общо"
            return i
    # fallback – ако не намерим, пазим старото поведение
    return year_row_idx + 3

def make_unique_columns(columns):
    seen = {}
    result = []

    for col in columns:
        key = col or "unnamed"

        seen[key] = seen.get(key, 0) + 1

        result.append(
            f"{key}__{seen[key]}"
            if seen[key] > 1
            else key
        )

    return result

def iter_year_blocks(
    row,
    ordered_years,
    block_size
):
    for col_idx, year in ordered_years:
        values = row[col_idx:col_idx + block_size]

        if len(values) < block_size:
            continue

        numbers = [to_number(v) for v in values]

        if all(pd.isna(v) for v in numbers):
            continue

        yield year, numbers

def extract_metric_records(
        row,
        ordered_years,
        metrics):
    """
    Yields:
        (year, metric_name, value)

    Example:
        (2020, "male", 51)
        (2020, "female", 49)
        (2021, "male", 57)
        (2021, "female", 53)
    """

    block_size = len(metrics)

    for year, numbers in iter_year_blocks(
            row,
            ordered_years,
            block_size):

        for metric_name, value in zip(
                metrics,
                numbers):
            yield year, metric_name, value
