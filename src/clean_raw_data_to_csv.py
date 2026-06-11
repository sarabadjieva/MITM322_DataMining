from pathlib import Path
from text_utils import normalize_text, to_number, extract_year
from territory_utils import classify_territory
from file_configs import ParseMode, TRIPLET_METRICS, PAIR_METRICS, FILE_CONFIGS
from territory_filters import keep_only_oblasti
from parser_utils import find_header_row, find_year_row, find_data_start_by_country, extract_metric_records, \
    make_unique_columns
import json
import pandas as pd
import const_vals as c_vals
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
        filter_oblasti: bool = False
) -> pd.DataFrame:

    df = read_excel_raw(path)

    year_row_idx, years = find_year_row(df)

    data_start = find_data_start_by_country(
        df,
        year_row_idx
    )

    if filter_oblasti:
        header = df.iloc[:data_start]

        data = df.iloc[data_start:]

        data = keep_only_oblasti(data)

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

def parse_wide_years_pairs(
        path: Path,
        dataset: str
) -> pd.DataFrame:

    df = read_excel_raw(path)

    year_row_idx, years = find_year_row(df)

    data_start = year_row_idx + 3

    ordered = sorted(
        years.items(),
        key=lambda x: x[0]
    )

    metrics = PAIR_METRICS.get(
        dataset,
        PAIR_METRICS["_default"]
    )

    current_group = None

    records = []

    for r in range(data_start - 1, len(df)):
        row = df.iloc[r].tolist()

        label = normalize_text(row[0])

        if not label:
            continue

        if (
            label in c_vals.TOTAL_LABELS
            or label in c_vals.AREA_LABELS
            or label.isupper()
        ):
            current_group = label
            continue

        for year, metric_name, value in extract_metric_records(
                row,
                ordered,
                metrics):
            records.append(
                recs.make_age_metric_record(
                    group_name=current_group,
                    age_group=label,
                    year=year,
                    metric=metric_name,
                    value=value,
                )
            )

    return pd.DataFrame(
        [r.to_dict() for r in records]
    )

def parse_sheet_per_year_blocks(path, dataset, filter_oblasti=False):
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

        if filter_oblasti:
            data = keep_only_oblasti(data)

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

def parse_sheet_per_year_matrix(path, dataset):
    xls = pd.ExcelFile(path)
    records = []

    for sheet in xls.sheet_names:
        year = extract_year(sheet)
        df = read_excel_raw(path, sheet)

        if dataset == 'divorces_age_matrix':
            a4 = normalize_text(df.iloc[3, 0])  # A4
            a5 = normalize_text(df.iloc[4, 0])  # A5
            if a4 and a5:
                merged_a4_a5 = f"{a4} / {a5}"
            else:
                merged_a4_a5 = a4 or a5

            df.iloc[3, 0] = merged_a4_a5
            df.iloc[4, 0] = None

        header_row = find_header_row(
            df,
            [
                lambda x: "Общо" in x,
                lambda x: "Възраст на жените" in x,
            ]
        )

        colnames = [normalize_text(x)
                    for x in df.iloc[header_row + 1].tolist()]

        colnames = make_unique_columns(colnames)

        colnames[0] = 'female_age_group'
        if len(colnames) > 1:
            colnames[1] = 'total'

        data = df.iloc[header_row + 2:].copy()
        data.columns = colnames[:len(data.columns)]
        data = data.dropna(how='all')
        current_residence = 'Общо за страната'

        for _, row in data.iterrows():
            female_age = normalize_text(row['female_age_group'])
            if not female_age:
                continue
            if female_age in {'Общо за страната', 'В градовете', 'В селата'}:
                current_residence = female_age
                continue
            for col in data.columns[1:]:
                value = to_number(row[col])
                if pd.isna(value):
                    continue
                male_age = col
                records.append(
                    recs.make_age_matrix_record(
                        year=year,
                        residence_group=current_residence,
                        female_age_group=female_age,
                        male_age_group=male_age,
                        value=value,
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
    ParseMode.WIDE_YEARS_PAIRS: parse_wide_years_pairs,
    ParseMode.SHEET_PER_YEAR_BLOCKS: parse_sheet_per_year_blocks,
    ParseMode.SHEET_PER_YEAR_MATRIX: parse_sheet_per_year_matrix,
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
            filter_oblasti=cfg.clean_municipality
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