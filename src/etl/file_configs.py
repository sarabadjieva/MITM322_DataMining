from dataclasses import dataclass
from enum import Enum
from pathlib import Path

SRC_DIR = Path(__file__).resolve().parent.parent
RAW_DIR = SRC_DIR.parent / "data"
ETL_OUTPUT_DIR = SRC_DIR / "output"
ETL_OUTPUT_DIR.mkdir(exist_ok=True)

METRIC_SEQUENCE = ["total", "urban", "rural"]
REQUIRED_OUTPUT_COLUMNS = {"year", "territory_raw", "territory_level", "metric", "value"}

class ParseMode(Enum):
    MARRIAGES = 0
    BIRTHS = 1


@dataclass(frozen=True)
class FileConfig:
    dataset: str
    mode: ParseMode
    clean_municipality: bool = False


FILE_CONFIGS = {
    "Pop_1.2.2._birth_DR.xlsx": FileConfig(
        dataset="births_marital_status_residence",
        mode=ParseMode.BIRTHS,
        clean_municipality=True,
    ),
    "Pop_4.1.1._Marriages_DR.xlsx": FileConfig(
        dataset="marriages_by_residence",
        mode=ParseMode.MARRIAGES,
    ),
    "Pop_6.1.5_Pop_DR.xlsx": FileConfig(
        dataset="population_by_residence",
        mode=ParseMode.MARRIAGES,
        clean_municipality=True,
    ),
}