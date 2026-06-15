import pandas as pd

from pathlib import Path
from src.analysis.classes import RawDatasets


SRC_DIR = Path(__file__).resolve().parent.parent
OUTPUT_DIR = SRC_DIR / "output"


def load_raw_datasets() -> RawDatasets:
    return RawDatasets(
        marriages=pd.read_csv(OUTPUT_DIR / "marriages_by_residence_clean.csv"),
        marital=pd.read_csv(OUTPUT_DIR / "births_marital_status_residence_marital_clean.csv"),
        nonmarital=pd.read_csv(OUTPUT_DIR / "births_marital_status_residence_nonmarital_clean.csv"),
        all_births=pd.read_csv(OUTPUT_DIR / "births_marital_status_residence_all_clean.csv"),
        population=pd.read_csv(OUTPUT_DIR / "population_by_residence_clean.csv")
    )
