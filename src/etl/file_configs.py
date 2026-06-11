from dataclasses import dataclass
from enum import Enum


class ParseMode(str, Enum):
    MARRIAGES = "wide_years_triplets"
    BIRTHS = "sheet_per_year_blocks"


@dataclass(frozen=True)
class FileConfig:
    dataset: str
    mode: ParseMode
    clean_municipality: bool = False


METRIC_SEQUENCE = ["total", "urban", "rural"]


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
}