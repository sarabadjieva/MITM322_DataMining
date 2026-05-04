from pathlib import Path
import re
import json
import unicodedata
import pandas as pd
import numpy as np
import openpyxl as pyxl

BASE_DIR = Path('.')
OUTPUT_DIR = Path('output')
OUTPUT_DIR.mkdir(exist_ok=True)

FILE_CONFIGS = {
    'Pop_1.2.1._birth_DR.xlsx': {
        'dataset': 'births_by_sex',
        'mode': 'wide_years_triplets',
        'entity_col': 'territory'
    },
    'Pop_1.2.2._birth_DR.xlsx': {
        'dataset': 'births_marital_status_residence',
        'mode': 'sheet_per_year_blocks',
        'entity_col': 'territory'
    },
    'Pop_1.2.3._birth_DR.xlsx': {
        'dataset': 'births_by_mother_age',
        'mode': 'sheet_per_year_blocks',
        'entity_col': 'territory'
    },
    'Pop_4.1.1._Marriages_DR.xlsx': {
        'dataset': 'marriages_by_residence',
        'mode': 'wide_years_triplets',
        'entity_col': 'territory'
    },
    'Pop_4.1.2._Marriages_DR.xlsx': {
        'dataset': 'marriages_age_matrix',
        'mode': 'sheet_per_year_matrix',
        'entity_col': 'female_age_group'
    },
    'Pop_4.1.5._Marriages_DR.xlsx': {
        'dataset': 'marriages_by_age_sex',
        'mode': 'wide_years_pairs',
        'entity_col': 'age_group'
    },
    'Pop_4.2.1._Divorces_DR.xlsx': {
        'dataset': 'divorces_by_residence',
        'mode': 'wide_years_triplets',
        'entity_col': 'territory'
    },
    'Pop_4.2.2._Divorces_DR.xlsx': {
        'dataset': 'divorces_age_matrix',
        'mode': 'sheet_per_year_matrix',
        'entity_col': 'female_age_group'
    },
    'Pop_4.2.5._Divorces_DR.xlsx': {
        'dataset': 'divorces_by_age_sex',
        'mode': 'wide_years_pairs',
        'entity_col': 'age_group'
    },
}

NULL_MARKERS = {'-', '..', '…', '...', '—', '', 'nan', 'None', None}
AREA_TOTAL_LABELS = {'Общо за страната', 'България'}
AREA_MAJOR_HINTS = {
    'София (столица)', 'София', 'Благоевград', 'Бургас', 'Варна', 'Велико Търново', 'Видин', 'Враца',
    'Габрово', 'Добрич', 'Кърджали', 'Кюстендил', 'Ловеч', 'Монтана', 'Пазарджик', 'Перник', 'Плевен',
    'Пловдив', 'Разград', 'Русе', 'Силистра', 'Сливен', 'Смолян', 'София', 'Стара Загора', 'Търговище',
    'Хасково', 'Шумен', 'Ямбол'
}


def normalize_text(v):
    if isinstance(v, (pd.Series, list, tuple, np.ndarray)):
        return None
    if pd.isna(v):
        return None
    s = str(v).replace('\xa0', ' ').strip()
    if s in NULL_MARKERS:
        return None
    s = re.sub(r'\s+', ' ', s)
    return s


def slugify(text):
    text = normalize_text(text) or 'value'
    text = unicodedata.normalize('NFKD', text)
    text = ''.join(ch for ch in text if not unicodedata.combining(ch))
    text = text.lower()
    text = re.sub(r'[^a-zA-Z0-9а-яА-Я]+', '_', text, flags=re.UNICODE)
    text = re.sub(r'_+', '_', text).strip('_')
    return text or 'value'


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


def classify_territory(name, current_oblast=None):
    name = normalize_text(name)
    if not name:
        return None, current_oblast, None
    if name in AREA_TOTAL_LABELS:
        return 'country', None, None
    if name in AREA_MAJOR_HINTS or name == 'София (столица)':
        return 'oblast', name, None
    if current_oblast:
        return 'municipality', current_oblast, name
    return 'unknown', None, name


def read_excel_raw(path, sheet_name=0):
    return pd.read_excel(path, sheet_name=sheet_name, header=None, dtype=object)


def parse_wide_years_triplets(path, dataset):
    df = read_excel_raw(path)
    year_row_idx = None
    years = None
    for i in range(min(10, len(df))):
        yrs = find_years_in_row(df.iloc[i].tolist())
        if len(yrs) >= 3:
            year_row_idx = i
            years = yrs
            break
    if year_row_idx is None:
        raise ValueError(f'Не може да се намери ред с години в {path.name}')

    data_start = year_row_idx + 3
    records = []
    current_oblast = None

    ordered = sorted(years.items(), key=lambda x: x[0])
    for r in range(data_start, len(df)):
        row = df.iloc[r].tolist()
        name = normalize_text(row[0])
        if not name:
            continue
        territory_level, oblast, municipality = classify_territory(name, current_oblast)
        if territory_level == 'oblast':
            current_oblast = oblast
        elif territory_level == 'country':
            current_oblast = None
        elif territory_level == 'unknown' and current_oblast is None:
            continue

        for col_idx, year in ordered:
            vals = row[col_idx:col_idx+3]
            if len(vals) < 3:
                continue
            total, v2, v3 = [to_number(x) for x in vals]
            if pd.isna(total) and pd.isna(v2) and pd.isna(v3):
                continue
            if dataset == 'births_by_sex':
                measures = [('total', total), ('male', v2), ('female', v3)]
            elif dataset == 'marriages_by_residence' or dataset == 'divorces_by_residence':
                measures = [('total', total), ('urban', v2), ('rural', v3)]
            else:
                measures = [('value1', total), ('value2', v2), ('value3', v3)]
            for metric, value in measures:
                records.append({
                    'dataset': dataset,
                    'year': year,
                    'territory_raw': name,
                    'territory_level': territory_level,
                    'oblast': oblast,
                    'municipality': municipality,
                    'metric': metric,
                    'value': value,
                    'source_file': path.name,
                })
    return pd.DataFrame(records)


def parse_wide_years_pairs(path, dataset):
    df = read_excel_raw(path)
    year_row_idx = None
    years = None
    for i in range(min(10, len(df))):
        yrs = find_years_in_row(df.iloc[i].tolist())
        if len(yrs) >= 3:
            year_row_idx = i
            years = yrs
            break
    if year_row_idx is None:
        raise ValueError(f'Не може да се намери ред с години в {path.name}')

    data_start = year_row_idx + 3
    ordered = sorted(years.items(), key=lambda x: x[0])
    records = []
    current_group = None

    for r in range(data_start, len(df)):
        row = df.iloc[r].tolist()
        label = normalize_text(row[0])
        if not label:
            continue
        if label in AREA_TOTAL_LABELS or label in AREA_MAJOR_HINTS or label == 'Общо за страната':
            current_group = label
            continue

        for col_idx, year in ordered:
            vals = row[col_idx:col_idx+2]
            if len(vals) < 2:
                continue
            male, female = [to_number(x) for x in vals]
            if pd.isna(male) and pd.isna(female):
                continue
            records.append({
                'dataset': dataset,
                'group_name': current_group,
                'age_group': label,
                'year': year,
                'metric': 'male',
                'value': male,
                'source_file': path.name,
            })
            records.append({
                'dataset': dataset,
                'group_name': current_group,
                'age_group': label,
                'year': year,
                'metric': 'female',
                'value': female,
                'source_file': path.name,
            })
    return pd.DataFrame(records)


def parse_sheet_per_year_blocks(path, dataset):
    xls = pd.ExcelFile(path)
    records = []
    for sheet in xls.sheet_names:
        year_match = re.search(r'(19|20)\d{2}', str(sheet))
        year = int(year_match.group()) if year_match else None
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
        current_oblast = None

        for _, row in data.iterrows():
            name = normalize_text(row[first_col])
            if not name:
                continue
            territory_level, oblast, municipality = classify_territory(name, current_oblast)
            if territory_level == 'oblast':
                current_oblast = oblast
            elif territory_level == 'country':
                current_oblast = None
            elif territory_level == 'unknown' and current_oblast is None:
                continue

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
                    'territory_level': territory_level,
                    'oblast': oblast,
                    'municipality': municipality,
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
        year_match = re.search(r'(19|20)\d{2}', str(sheet))
        year = int(year_match.group()) if year_match else None
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


def clean_dataframe(df):
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


def main():
    manifest = []
    #combined = []

    for filename, cfg in FILE_CONFIGS.items():
        path = BASE_DIR / filename
        if not path.exists():
            manifest.append({'file': filename, 'status': 'missing'})
            continue

        mode = cfg['mode']
        dataset = cfg['dataset']

        if mode == 'wide_years_triplets':
            df = parse_wide_years_triplets(path, dataset)
        elif mode == 'wide_years_pairs':
            df = parse_wide_years_pairs(path, dataset)
        elif mode == 'sheet_per_year_blocks':
            df = parse_sheet_per_year_blocks(path, dataset)
        elif mode == 'sheet_per_year_matrix':
            df = parse_sheet_per_year_matrix(path, dataset)
        else:
            raise ValueError(f'Непознат режим: {mode}')

        df = clean_dataframe(df)
        out = export_outputs(df, dataset)

        manifest.append({
            'file': filename,
            'dataset': dataset,
            'mode': mode,
            'rows': int(len(df)),
            'output_csv': str(out)
        })

        #if not df.empty:
        #    tmp = df.copy()
        #    tmp['dataset_name'] = dataset
        #    combined.append(tmp)

    manifest_path = OUTPUT_DIR / 'etl_manifest.json'
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding='utf-8')

    #if combined:
    #    combined_df = pd.concat(combined, ignore_index=True, sort=False)
    #    combined_df.to_csv(OUTPUT_DIR / 'demography_master.csv', index=False, encoding='utf-8-sig')


if __name__ == '__main__':
    main()