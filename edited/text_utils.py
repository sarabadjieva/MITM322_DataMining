import re
import pandas as pd
import numpy as np
import const_vals as cvals

def normalize_text(v):
    if isinstance(v, (pd.Series, list, tuple, np.ndarray)):
        return None
    if pd.isna(v):
        return None
    s = str(v).replace('\xa0', ' ').strip()
    if s in cvals.NULL_MARKERS:
        return None
    s = re.sub(r'\s+', ' ', s)
    return s

def to_number(v):
    s = normalize_text(v)
    if s is None:
        return np.nan
    s = s.replace(',', '')
    try:
        return float(s)
    except Exception:
        return np.nan

def find_years_in_row(row):
    years = {}
    for idx, val in enumerate(row):
        s = normalize_text(val)
        if s and re.fullmatch(r'(19|20)\d{2}', s):
            years[idx] = int(s)
    return years