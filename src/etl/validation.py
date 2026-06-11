import pandas as pd


REQUIRED_COLUMNS = {
    "births_by_mother_age": {"year", "territory_raw", "territory_level", "metric", "value"},
    "births_marital_status_residence": {"year", "territory_raw", "territory_level", "metric", "value"},
    "marriages_by_age_sex": {"group_name", "age_group", "year", "metric", "value"},
    "births_by_sex": {"year", "territory_raw", "territory_level", "metric", "value"},
    "marriages_by_residence": {"year", "territory_raw", "territory_level", "metric", "value"},
}

def validate_output_dataframe(df: pd.DataFrame, dataset: str) -> pd.DataFrame:
    expected = REQUIRED_COLUMNS.get(dataset)
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