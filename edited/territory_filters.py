from text_utils import normalize_text
from territory_utils import canonical_area_name, is_total_row
import const_vals as cvals

def keep_only_oblasti(data_df):
    keep_rows = []

    seen_oblasti = set()
    current_oblast = None

    for idx, row in data_df.iterrows():
        name = normalize_text(row.iloc[0])

        if not name:
            continue

        # Country total
        if is_total_row(name):
            keep_rows.append(idx)
            current_oblast = None
            continue

        canon = canonical_area_name(name)

        # First oblast row
        if canon in cvals.AREA_LABELS and canon not in seen_oblasti:
            keep_rows.append(idx)

            seen_oblasti.add(canon)
            current_oblast = canon
            continue

        # Municipality total with same name as oblast
        if current_oblast and canon == current_oblast:
            continue

        # Municipality/detail row
        continue

    return data_df.loc[keep_rows].copy()