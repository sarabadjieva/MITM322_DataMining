import json
import pandas as pd
from src.etl.helpers.text_utils import normalize_text
from pathlib import Path


SRC_DIR = Path(__file__).resolve().parent.parent
OUTPUT_DIR = SRC_DIR / "output"
OUTPUT_DIR.mkdir(exist_ok=True)

def normalize_output_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty:
        return df

    df = df.copy()
    for col in df.columns:
        if df[col].dtype == object:
            df[col] = df[col].map(
                lambda x: normalize_text(x) if isinstance(x, str) or x is None else x
            )

    if "value" in df.columns:
        df["value"] = pd.to_numeric(df["value"], errors="coerce")

    if "territory_raw" in df.columns:
        df["territory_raw"] = df["territory_raw"].replace({"Общо за страната": "България"})

    return df


def export_multiple_outputs(dfs: dict[str, pd.DataFrame], dataset: str) -> dict[str, Path]:
    exported = {}

    for suffix, df in dfs.items():
        csv_path = OUTPUT_DIR / f"{dataset}_{suffix}_clean.csv"
        df.to_csv(csv_path, index=False, encoding="utf-8-sig")
        exported[suffix] = csv_path

    return exported


def export_output(df: pd.DataFrame, dataset: str) -> Path:
    csv_path = OUTPUT_DIR / f"{dataset}_clean.csv"
    df.to_csv(csv_path, index=False, encoding="utf-8-sig")
    return csv_path

def export_manifest(manifest: list[str]):
    manifest_path = OUTPUT_DIR / "etl_manifest.json"
    manifest_path.write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2),
        encoding="utf-8"
    )