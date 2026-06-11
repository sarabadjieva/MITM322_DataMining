from pathlib import Path
from text_utils import normalize_text, to_number, extract_year
from territory_utils import classify_territory
from file_configs import ParseMode, TRIPLET_METRICS, FILE_CONFIGS
from territory_filters import keep_only_districts
from parser_utils import find_header_row, find_year_row, find_data_start_by_country, extract_metric_records, \
    make_unique_columns
import json
import pandas as pd
import records as recs

CURRENT_DIR = Path(__file__).resolve().parent
RAW_DIR = CURRENT_DIR.parent / "data"
OUTPUT_DIR = CURRENT_DIR / "output"
OUTPUT_DIR.mkdir(exist_ok=True)

def read_excel_raw(path, sheet_name=0):
    return pd.read_excel(path, sheet_name=sheet_name, header=None, dtype=object)

def parse_wide_years_triplets(
        path: Path,
        dataset: str,
        filter_districts: bool = False
) -> pd.DataFrame:

    df = read_excel_raw(path)

    year_row_idx, years = find_year_row(df)

    data_start = find_data_start_by_country(
        df,
        year_row_idx
    )

    if filter_districts:
        header = df.iloc[:data_start]

        data = df.iloc[data_start:]

        data = keep_only_districts(data)

        df = pd.concat([header, data])

    ordered = sorted(
        years.items(),
        key=lambda x: x[0]
    )

    metrics = TRIPLET_METRICS.get(
        dataset,
        TRIPLET_METRICS["_default"]
    )

    records = []

    for r in range(data_start, len(df)):
        row = df.iloc[r].tolist()

        name = normalize_text(row[0])

        if not name:
            continue

        for year, metric_name, value in extract_metric_records(
                row,
                ordered,
                metrics):

            records.append(
                recs.make_territory_metric_record(
                    year=year,
                    territory_raw=name,
                    territory_level=classify_territory(name).level,
                    metric=metric_name,
                    value=value,
                )
            )

    return pd.DataFrame(
        [r.to_dict() for r in records]
    )

def parse_sheet_per_year_blocks(path, dataset, filter_districts=False):
    xls = pd.ExcelFile(path)
    records = []
    for sheet in xls.sheet_names:
        year = extract_year(sheet)
        df = read_excel_raw(path, sheet)
        header_row = find_header_row(
            df,
            [
                lambda x: "Области" in x,
                lambda x: "Общини" in x,
                lambda x: "Възраст на майката" in x,
            ]
        )

        h1 = [normalize_text(x) for x in df.iloc[header_row].tolist()]
        h2 = [normalize_text(x) for x in df.iloc[header_row + 1].tolist()] if header_row + 1 < len(df) else [None] * len(h1)

        raw_cols = []

        for a, b in zip(h1, h2):
            parts = [p for p in (a, b) if p]

            raw_cols.append(
                " | ".join(parts)
                if parts
                else None
            )

        cols = make_unique_columns(raw_cols)

        data = df.iloc[header_row + 2:].copy()
        data.columns = cols
        data = data.dropna(how='all')

        if filter_districts:
            data = keep_only_districts(data)

        first_col = data.columns[0]

        for _, row in data.iterrows():
            name = normalize_text(row[first_col])
            if not name:
                continue
            t = classify_territory(name)

            for col in data.columns[1:]:
                if not col:
                    continue
                value = to_number(row[col])
                if pd.isna(value):
                    continue
                records.append(
                    recs.make_territory_measure_record(
                        year=year,
                        territory_raw=name,
                        territory_level=t.level,
                        measure=col,
                        value=value
                    )
                )

    return pd.DataFrame(
        [r.to_dict() for r in records]
    )

def normalize_output_dataframe(df):
    if df.empty:
        return df
    for col in df.columns:
        if df[col].dtype == object:
            df[col] = df[col].map(lambda x: normalize_text(x) if isinstance(x, str) or x is None else x)
    if 'value' in df.columns:
        df['value'] = pd.to_numeric(df['value'], errors='coerce')
    return df

PARSERS = {
    ParseMode.WIDE_YEARS_TRIPLETS: parse_wide_years_triplets,
    ParseMode.SHEET_PER_YEAR_BLOCKS: parse_sheet_per_year_blocks,
}

def validate_output_dataframe(df: pd.DataFrame, dataset: str) -> pd.DataFrame:
    required = {
        "births_by_mother_age": {"year", "territory_raw", "territory_level", "measure", "value"},
        "marriages_by_age_sex": {"group_name", "age_group", "year", "metric", "value"},
        "births_by_sex": {"year", "territory_raw", "territory_level", "metric", "value"},
        "marriages_by_residence": {"year", "territory_raw", "territory_level", "metric", "value"},
    }

    expected = required.get(dataset)
    if expected and not expected.issubset(df.columns):
        missing = expected - set(df.columns)
        raise ValueError(f"{dataset}: missing columns {missing}")

    if "year" in df.columns:
        df["year"] = pd.to_numeric(df["year"], errors="coerce")
        if df["year"].isna().any():
            raise ValueError(f"{dataset}: invalid year values found")

    if "value" in df.columns:
        df["value"] = pd.to_numeric(df["value"], errors="coerce")

    if "territory_raw" in df.columns:
        df["territory_raw"] = df["territory_raw"].replace({
            "Общо за страната": "България"
        })

    return df

def run_etl_for_file(path: Path, cfg) -> pd.DataFrame:
    parser = PARSERS[cfg.mode]

    if cfg.mode in {
        ParseMode.WIDE_YEARS_TRIPLETS,
        ParseMode.SHEET_PER_YEAR_BLOCKS,
    }:
        df = parser(
            path,
            cfg.dataset,
            filter_districts=cfg.clean_municipality
        )
    else:
        df = parser(
            path,
            cfg.dataset
        )
    return validate_output_dataframe(normalize_output_dataframe(df), cfg.dataset)

def export_outputs(df, dataset):
    csv_path = OUTPUT_DIR / f'{dataset}_clean.csv'
    df.to_csv(csv_path, index=False, encoding='utf-8-sig')
    return csv_path

def main():
    manifest = []

    for filename, cfg in FILE_CONFIGS.items():
        path = RAW_DIR / filename
        if not path.exists():
            manifest.append({"file": filename, "status": "missing"})
            continue

        dataset = cfg.dataset

        df_all = run_etl_for_file(
            path,
            cfg
        )

        export_outputs(df_all, dataset)

        manifest.append({
            "file": filename,
            "dataset": cfg.dataset,
            "mode": cfg.mode.value,
            "rows": int(len(df_all)),
            "clean_municipality": cfg.clean_municipality,
        })

    manifest_path = OUTPUT_DIR / "etl_manifest.json"
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")

if __name__ == '__main__':
    main()