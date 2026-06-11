from enum import Enum
from dataclasses import dataclass

class ParseMode(str, Enum):
    WIDE_YEARS_TRIPLETS = "wide_years_triplets"
    SHEET_PER_YEAR_BLOCKS = "sheet_per_year_blocks"

@dataclass(frozen=True)
class FileConfig:
    dataset: str
    mode: ParseMode
    clean_municipality: bool = False

TRIPLET_METRICS = {
    "births_by_sex": ["total", "male", "female"],
    "marriages_by_residence":["total", "urban", "rural"],
    "divorces_by_residence": ["total", "urban", "rural"],
    "_default": ["value1", "value2", "value3"],
}

FILE_CONFIGS = {
    'Pop_1.2.1._birth_DR.xlsx': FileConfig(
        dataset='births_by_sex',
        mode=ParseMode.WIDE_YEARS_TRIPLETS,
        clean_municipality=True
    ),
    'Pop_1.2.2._birth_DR.xlsx': FileConfig(
        dataset='births_marital_status_residence',
        mode=ParseMode.SHEET_PER_YEAR_BLOCKS,
        clean_municipality=True
    ),
    "Pop_4.1.1._Marriages_DR.xlsx": FileConfig(
        dataset='marriages_by_residence',
        mode=ParseMode.WIDE_YEARS_TRIPLETS
    )
}
