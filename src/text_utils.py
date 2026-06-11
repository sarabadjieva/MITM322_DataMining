import re
from typing import Any

import numpy as np
import pandas as pd

from src.const_vals import NULL_MARKERS

WHITESPACE_RE = re.compile(r"\s+")
YEAR_RE = re.compile(r"(19|20)\d{2}")


def extract_year(value: Any) -> int | None:
    match = YEAR_RE.search(str(value))
    return int(match.group()) if match else None


def is_missing_text(value: Any) -> bool:
    if isinstance(value, (pd.Series, list, tuple, np.ndarray)):
        return True
    return pd.isna(value)


def normalize_text(value: Any) -> str | None:
    if is_missing_text(value):
        return None
    text = str(value).replace("\xa0", " ").strip()
    if text in NULL_MARKERS:
        return None
    return WHITESPACE_RE.sub(" ", text)


def to_number(value: Any) -> float:
    text = normalize_text(value)
    if text is None:
        return np.nan
    try:
        return float(text.replace(",", ""))
    except ValueError:
        return np.nan


def find_years_in_row(row: list[Any]) -> dict[int, int]:
    years = {}
    for col_idx, value in enumerate(row):
        text = normalize_text(value)
        if text and YEAR_RE.fullmatch(text):
            years[col_idx] = int(text)
    return years