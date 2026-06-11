import re
import pandas as pd
import numpy as np
import const_vals as cvals
from typing import Any

WHITESPACE_RE = re.compile(r"\s+")
YEAR_RE = re.compile(r"(19|20)\d{2}")

def extract_year(value):
    match = YEAR_RE.search(str(value))
    return int(match.group()) if match else None

def is_missing_text(value):
    if isinstance(value, (pd.Series, list, tuple, np.ndarray)):
        return True
    if pd.isna(value):
        return True
    return False

def normalize_text(v: Any) -> str | None:
    if is_missing_text(v):
        return None
    s = str(v).replace('\xa0', ' ').strip()
    if s in cvals.NULL_MARKERS:
        return None
    s = WHITESPACE_RE.sub(' ', s)
    return s

def to_number(v: Any) -> float:
    s = normalize_text(v)
    if s is None:
        return np.nan
    s = s.replace(',', '')
    try:
        return float(s)
    except ValueError:
        return np.nan

def find_years_in_row(row: list[Any]) -> dict[int, int]:
    years_by_column = {}

    for col_idx, value in enumerate(row):
        text = normalize_text(value)

        if text and YEAR_RE.fullmatch(text):
            years_by_column[col_idx] = int(text)

    return years_by_column