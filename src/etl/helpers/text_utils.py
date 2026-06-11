import re
from typing import Any

import numpy as np
import pandas as pd

from src.etl.helpers.const_vals import NULL_MARKERS

YEAR_RE = re.compile(r"\b(?:19|20)\d{2}\b")


def extract_year(value: Any) -> int | None:
    if match := YEAR_RE.search(str(value)):
        return int(match.group())
    return None


def normalize_text(value: Any) -> str | None:
    if isinstance(value, (pd.Series, list, tuple, np.ndarray)):
        return None

    if pd.isna(value):
        return None

    text = str(value).replace("\xa0", " ").strip()
    if text in NULL_MARKERS:
        return None

    return " ".join(text.split())


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