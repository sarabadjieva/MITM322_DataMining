import pandas as pd
from pathlib import Path

from src.parser_utils import make_unique_columns, find_header_row
from src.territory_filters import keep_only_districts
from src.territory_utils import classify_territory
from src.text_utils import normalize_text, extract_year, to_number

HEADER_PREDICATES = (
    lambda text: "Области" in text,
    lambda text: "Общини" in text,
    lambda text: "Възраст на майката" in text,
)


def territory_measure_row(year, name, measure, value):
    return {
        "year": year,
        "territory_raw": name,
        "territory_level": classify_territory(name).level,
        "measure": measure,
        "value": value,
    }


def build_sheet_columns(df, header_row):
    header_1 = [normalize_text(x) for x in df.iloc[header_row].tolist()]
    header_2 = (
        [normalize_text(x) for x in df.iloc[header_row + 1].tolist()]
        if header_row + 1 < len(df)
        else [None] * len(header_1)
    )

    raw_columns = []
    for left, right in zip(header_1, header_2):
        parts = [part for part in (left, right) if part]
        raw_columns.append(" | ".join(parts) if parts else None)

    return make_unique_columns(raw_columns)


def parse_sheet_per_year_blocks(path: Path, dataset: str, filter_districts: bool = False) -> pd.DataFrame:
    xls = pd.ExcelFile(path)
    rows = []

    for sheet_name in xls.sheet_names:
        year = extract_year(sheet_name)
        df = pd.read_excel(path, sheet_name=sheet_name, header=None, dtype=object)
        header_row = find_header_row(df, HEADER_PREDICATES)
        if header_row is None or year is None:
            continue

        data = df.iloc[header_row + 2 :].copy()
        data.columns = build_sheet_columns(df, header_row)
        data = data.dropna(how="all")

        if filter_districts:
            data = keep_only_districts(data)

        first_col = data.columns[0]

        for _, row in data.iterrows():
            name = normalize_text(row[first_col])
            if not name:
                continue

            for col in data.columns[1:]:
                if not col:
                    continue
                value = to_number(row[col])
                if pd.isna(value):
                    continue
                rows.append(territory_measure_row(year, name, col, value))

    return pd.DataFrame(rows)
