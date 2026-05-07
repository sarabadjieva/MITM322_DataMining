from pathlib import Path
from text_utils import normalize_text, to_number, find_years_in_row
from territory_utils import classify_territory_t
import re
import json
import pandas as pd
import clean_workbook_municipality as clean_wb
import file_configs as fconfig
import const_vals as c_vals

BASE_DIR = Path('.')
OUTPUT_DIR = Path('output')
OUTPUT_DIR.mkdir(exist_ok=True)

def read_excel_raw(path, sheet_name=0):
    return pd.read_excel(path, sheet_name=sheet_name, header=None, dtype=object)

def find_year_row(df: pd.DataFrame, max_rows: int = 10) -> tuple[int, dict[int, int]]:
    year_row_idx, years = None, None
    for i in range(min(max_rows, len(df))):
        yrs = find_years_in_row(df.iloc[i].tolist())
        if len(yrs) >= 3:
            return i, yrs
    raise ValueError("Cannot find year row")

def extract_year(value):
    m = re.search(r"(19|20)\d{2}", str(value))
    return int(m.group()) if m else None

def find_data_start_by_country(df, year_row_idx, max_search=50):
    # търсим в следващите N реда след реда с годините
    for i in range(year_row_idx + 1, min(year_row_idx + 1 + max_search, len(df))):
        name = normalize_text(df.iloc[i, 0])
        if name in c_vals.TOTAL_LABELS:  # "Общо за страната", "България", "Общо"
            return i
    # fallback – ако не намерим, пазим старото поведение
    return year_row_idx + 3

def parse_wide_years_triplets(path: Path, dataset: str) -> pd.DataFrame:
    df = read_excel_raw(path)

    # find row with years
    year_row_idx, years = find_year_row(df)
    data_start = find_data_start_by_country(df, year_row_idx)
    records = []
    ordered = sorted(years.items(), key=lambda x: x[0])

    # get metric names for this dataset
    metrics = fconfig.TRIPLET_METRICS.get(dataset, fconfig.TRIPLET_METRICS["_default"])

    for r in range(data_start, len(df)):
        row = df.iloc[r].tolist()
        name = normalize_text(row[0])
        if not name:
            continue

        t = classify_territory_t(name)

        for col_idx, year in ordered:
            vals = row[col_idx:col_idx + 3]
            if len(vals) < 3:
                continue

            numbers = [to_number(x) for x in vals]
            if all(pd.isna(x) for x in numbers):
                continue

            for metric_name, value in zip(metrics, numbers):
                records.append({
                    "dataset": dataset,
                    "year": year,
                    "territory_raw": name,
                    "territory_level": t.level,
                    "metric": metric_name,
                    "value": value,
                    "source_file": path.name,
                })

    return pd.DataFrame(records)

def parse_wide_years_pairs(path: Path, dataset: str) -> pd.DataFrame:
    df = read_excel_raw(path)

    # find row with years
    year_row_idx, years = find_year_row(df)

    data_start = year_row_idx + 3
    ordered = sorted(years.items(), key=lambda x: x[0])
    records = []
    current_group = None

    metrics = fconfig.PAIR_METRICS.get(dataset, fconfig.PAIR_METRICS["_default"])

    for r in range(data_start - 1, len(df)):
        row = df.iloc[r].tolist()
        label = normalize_text(row[0])
        if not label:
            continue

        if (label in c_vals.TOTAL_LABELS
                or label in c_vals.AREA_LABELS
                or label.isupper()):
            current_group = label
            continue

        for col_idx, year in ordered:
            vals = row[col_idx:col_idx + 2]
            if len(vals) < 2:
                continue
            numbers = [to_number(x) for x in vals]
            if all(pd.isna(x) for x in numbers):
                continue

            for metric_name, value in zip(metrics, numbers):
                records.append({
                    "dataset": dataset,
                    "group_name": current_group,
                    "age_group": label,
                    "year": year,
                    "metric": metric_name,
                    "value": value,
                    "source_file": path.name,
                })

    return pd.DataFrame(records)

def parse_sheet_per_year_blocks(path, dataset):
    xls = pd.ExcelFile(path)
    records = []
    for sheet in xls.sheet_names:
        year = extract_year(sheet)
        df = read_excel_raw(path, sheet)
        header_row = None
        for i in range(min(8, len(df))):
            row_text = ' | '.join([str(x) for x in df.iloc[i].tolist() if pd.notna(x)])
            if 'Области' in row_text or 'Общини' in row_text or 'Възраст на майката' in row_text:
                header_row = i
                break
        if header_row is None:
            continue

        h1 = [normalize_text(x) for x in df.iloc[header_row].tolist()]
        h2 = [normalize_text(x) for x in df.iloc[header_row + 1].tolist()] if header_row + 1 < len(df) else [None] * len(h1)

        cols = []
        seen = {}
        for a, b in zip(h1, h2):
            parts = [p for p in [a, b] if p]
            col = ' | '.join(parts) if parts else None
            key = col or 'unnamed'
            seen[key] = seen.get(key, 0) + 1
            cols.append(f'{key}__{seen[key]}' if seen[key] > 1 else key)

        data = df.iloc[header_row + 2:].copy()
        data.columns = cols
        data = data.dropna(how='all')
        first_col = data.columns[0]

        for _, row in data.iterrows():
            name = normalize_text(row[first_col])
            if not name:
                continue
            t = classify_territory_t(name)

            for col in data.columns[1:]:
                if not col:
                    continue
                value = to_number(row[col])
                if pd.isna(value):
                    continue
                records.append({
                    'dataset': dataset,
                    'year': year,
                    'territory_raw': name,
                    'territory_level': t.level,
                    'measure': col,
                    'value': value,
                    'source_file': path.name,
                    'sheet_name': str(sheet),
                })
    return pd.DataFrame(records)


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

        header_row = None
        for i in range(min(8, len(df))):
            row_text = ' | '.join([str(x) for x in df.iloc[i].tolist() if pd.notna(x)])
            if 'Възраст на жените' in row_text and 'Общо' in row_text:
                header_row = i
                break
        if header_row is None:
            continue

        colnames = [normalize_text(x) for x in df.iloc[header_row + 1].tolist()]
        seen = {}
        newcols = []
        for c in colnames:
            key = c or 'unnamed'
            seen[key] = seen.get(key, 0) + 1
            newcols.append(f'{key}__{seen[key]}' if seen[key] > 1 else key)
        colnames = newcols

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
                records.append({
                    'dataset': dataset,
                    'year': year,
                    'residence_group': current_residence,
                    'female_age_group': female_age,
                    'male_age_group': male_age,
                    'value': value,
                    'source_file': path.name,
                    'sheet_name': str(sheet),
                })
    return pd.DataFrame(records)


def normalize_output_dataframe(df):
    if df.empty:
        return df
    for col in df.columns:
        if df[col].dtype == object:
            df[col] = df[col].map(lambda x: normalize_text(x) if isinstance(x, str) or x is None else x)
    if 'value' in df.columns:
        df['value'] = pd.to_numeric(df['value'], errors='coerce')
    return df


def export_outputs(df, dataset):
    csv_path = OUTPUT_DIR / f'{dataset}_clean.csv'
    df.to_csv(csv_path, index=False, encoding='utf-8-sig')
    return csv_path

PARSERS = {
    "wide_years_triplets": parse_wide_years_triplets,
    "wide_years_pairs": parse_wide_years_pairs,
    "sheet_per_year_blocks": parse_sheet_per_year_blocks,
    "sheet_per_year_matrix": parse_sheet_per_year_matrix,
}

def run_etl_for_file(path: Path, cfg: dict, keep_only_oblasti: bool) -> pd.DataFrame:
    mode = cfg["mode"]
    dataset = cfg["dataset"]
    parser = PARSERS[mode]

    if keep_only_oblasti:
        tmp_path = clean_wb.clean_workbook_keep_only_oblasti(path, inplace=True)
    else:
        tmp_path = path

    df = parser(tmp_path, dataset)
    df = normalize_output_dataframe(df)
    return df

def main():
    manifest = []

    for filename, cfg in fconfig.FILE_CONFIGS.items():
        path = BASE_DIR / filename
        if not path.exists():
            manifest.append({"file": filename, "status": "missing"})
            continue

        dataset = cfg["dataset"]
        mode = cfg["mode"]
        clean_muni_flag = cfg.get("clean_municipality", "false")

        if clean_muni_flag == "true":
            df_all = run_etl_for_file(path, cfg, keep_only_oblasti=True)
            df_all = df_all[df_all["territory_level"].isin(["country", "oblast"])]
        else:
            df_all = run_etl_for_file(path, cfg, keep_only_oblasti=False)

        df_all = normalize_output_dataframe(df_all)

        out = export_outputs(df_all, dataset)

        manifest.append({
            "file": filename,
            "dataset": dataset,
            "mode": mode,
            "rows": int(len(df_all)),
            "output_csv": str(out),
            "clean_municipality": clean_muni_flag,
        })

    manifest_path = OUTPUT_DIR / "etl_manifest.json"
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")

if __name__ == '__main__':
    main()