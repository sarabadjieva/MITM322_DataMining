import pandas as pd

from src.etl.file_configs import REQUIRED_OUTPUT_COLUMNS


def validate_output_dataframe(df: pd.DataFrame, dataset: str) -> pd.DataFrame:
    expected = REQUIRED_OUTPUT_COLUMNS
    if expected and not expected.issubset(df.columns):
        missing = expected - set(df.columns)
        raise ValueError(f"{dataset}: missing columns {missing}")

    if "year" in df.columns:
        df["year"] = pd.to_numeric(df["year"], errors="coerce")
        if df["year"].isna().any():
            raise ValueError(f"{dataset}: invalid year values found")

    if "value" in df.columns:
        df["value"] = pd.to_numeric(df["value"], errors="coerce")

    return df