from src.text_utils import normalize_text
from src.territory_utils import canonical_area_name, is_total_row
from src.const_vals import AREA_LABELS

def keep_only_districts(data_df):
    keep_rows = []
    seen_districts = set()
    current_district = None

    for idx, row in data_df.iterrows():
        name = normalize_text(row.iloc[0])
        if not name:
            continue

        if is_total_row(name):
            keep_rows.append(idx)
            current_district = None
            continue

        canon = canonical_area_name(name)
        if canon in AREA_LABELS and canon not in seen_districts:
            keep_rows.append(idx)
            seen_districts.add(canon)
            current_district = canon
            continue

        if current_district and canon == current_district:
            continue

    return data_df.loc[keep_rows].copy()