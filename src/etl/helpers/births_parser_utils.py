from src.etl.helpers.text_utils import normalize_text


def find_header_row(df, max_rows=8):
    for i in range(min(max_rows, len(df))):
        text = " ".join(map(str, df.iloc[i].dropna()))

        if "Области" in text or "Общини" in text:
            return i

    return None


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
