import pandas as pd
from pathlib import Path
from collections import defaultdict

from src.etl.file_configs import METRIC_SEQUENCE
from src.etl.helpers.parser_utils import find_header_row
from src.etl.helpers.territory_filters import keep_only_districts
from src.etl.helpers.territory_utils import territory_metric_row
from src.etl.helpers.text_utils import normalize_text, extract_year, to_number

HEADER_PREDICATES = (
    lambda text: "Области" in text,
    lambda text: "Общини" in text,
)


def build_sheet_labels(df, header_row):
    header_1 = [normalize_text(x) for x in df.iloc[header_row].tolist()]
    header_2 = (
        [normalize_text(x) for x in df.iloc[header_row + 1].tolist()]
        if header_row + 1 < len(df)
        else [None] * len(header_1)
    )

    labels = []
    for left, right in zip(header_1, header_2):
        parts = [part for part in (left, right) if part]
        labels.append(" | ".join(parts) if parts else None)

    return labels


def base_measure_name(label: str) -> str | None:
    label = normalize_text(label)
    if not label:
        return None

    if label.startswith("брачни"):
        return "брачни"

    if label.startswith("извънбрачни") or label.startswith("извън-брачни"):
        return "извънбрачни"

    return None


def resolve_birth_column_mapping(labels: list[str]) -> dict[int, tuple[str, str]]:
    counters = defaultdict(int)
    resolved = {}

    for col_idx, label in enumerate(labels[1:], start=1):
        base_name = base_measure_name(label)
        if base_name is None:
            continue

        group = "marital" if base_name == "брачни" else "nonmarital"
        occurrence_idx = counters[group]
        counters[group] += 1

        if occurrence_idx >= len(METRIC_SEQUENCE):
            continue

        metric = METRIC_SEQUENCE[occurrence_idx]
        resolved[col_idx] = (group, metric)

    return resolved


def parse_births(path: Path, dataset: str, filter_districts: bool = False) -> dict[str, pd.DataFrame]:
    xls = pd.ExcelFile(path)
    buckets = {
        "marital": [],
        "nonmarital": [],
    }

    for sheet_name in xls.sheet_names:
        year = extract_year(sheet_name)
        df = pd.read_excel(path, sheet_name=sheet_name, header=None, dtype=object)
        header_row = find_header_row(df, HEADER_PREDICATES)
        if header_row is None or year is None:
            continue

        labels = build_sheet_labels(df, header_row)
        data = df.iloc[header_row + 2 :].copy()
        data = data.dropna(how="all")

        if filter_districts:
            data = keep_only_districts(data)

        metric_mapping = resolve_birth_column_mapping(labels)
        first_col_idx = 0

        for _, row in data.iterrows():
            name = normalize_text(row.iloc[first_col_idx])
            if not name:
                continue

            for col_idx, (birth_group, metric) in metric_mapping.items():
                value = to_number(row.iloc[col_idx])
                if pd.isna(value):
                    continue

                buckets[birth_group].append(
                    territory_metric_row(year, name, metric, value)
                )

    return {key: pd.DataFrame(rows) for key, rows in buckets.items()}