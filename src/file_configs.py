from enum import Enum
from dataclasses import dataclass

class ParseMode(str, Enum):
    WIDE_YEARS_TRIPLETS = "wide_years_triplets"
    WIDE_YEARS_PAIRS = "wide_years_pairs"
    SHEET_PER_YEAR_BLOCKS = "sheet_per_year_blocks"
    SHEET_PER_YEAR_MATRIX = "sheet_per_year_matrix"

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

PAIR_METRICS = {
    "marriages_by_age_sex": ["male", "female"],
    "divorces_by_age_sex": ["male", "female"],
    "_default": ["value1", "value2"],
}

FILE_CONFIGS = {
    #'Birth/Pop_1.2.3._birth_DR.xlsx': FileConfig(
    #    dataset='births_by_mother_age',
    #    mode=ParseMode.SHEET_PER_YEAR_BLOCKS,
    #    clean_municipality=True
    #),
    #"Marriages/Pop_4.1.5._Marriages_DR.xlsx": FileConfig(
    #    dataset="marriages_by_age_sex",
    #    mode=ParseMode.WIDE_YEARS_PAIRS
    #),
    #"Divorces/Pop_4.2.5._Divorces_DR.xlsx": FileConfig(
    #    dataset="divorces_by_age_sex",
    #    mode=ParseMode.WIDE_YEARS_PAIRS
    #),
    'Birth/Pop_1.2.1._birth_DR.xlsx': FileConfig(
        dataset='births_by_sex',
        mode=ParseMode.WIDE_YEARS_TRIPLETS,
        clean_municipality=True
    ),
    #'Pop_1.2.2._birth_DR.xlsx': {
    #    'dataset': 'births_marital_status_residence',
    #    'mode': 'sheet_per_year_blocks',
    #    'clean_municipality': 'true'
    #},
    "Marriages/Pop_4.1.1._Marriages_DR.xlsx": FileConfig(
        dataset='marriages_by_residence',
        mode=ParseMode.WIDE_YEARS_TRIPLETS
    ),
    #'Pop_4.1.2._Marriages_DR.xlsx': {
    #    'dataset': 'marriages_age_matrix',
    #    'mode': 'sheet_per_year_matrix'
    #},
    #'Pop_4.2.1._Divorces_DR.xlsx': {
    #    'dataset': 'divorces_by_residence',
    #    'mode': 'wide_years_triplets'
    #},
    #'Pop_4.2.2._Divorces_DR.xlsx': {
    #    'dataset': 'divorces_age_matrix',
    #    'mode': 'sheet_per_year_matrix'
    #},
}
