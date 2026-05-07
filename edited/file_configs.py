TRIPLET_METRICS = {
    "births_by_sex":        ["total", "male", "female"],
    "marriages_by_residence": ["total", "urban", "rural"],
    "divorces_by_residence":  ["total", "urban", "rural"],
    "_default":            ["value1", "value2", "value3"],
}

PAIR_METRICS = {
    "marriages_by_age_sex": ["male", "female"],
    "divorces_by_age_sex":  ["male", "female"],
    "_default":             ["value1", "value2"],
}

FILE_CONFIGS = {
    'Pop_1.2.1._birth_DR.xlsx': {
        'dataset': 'births_by_sex',
        'mode': 'wide_years_triplets',
        'clean_municipality': 'true'
    },
    'Pop_1.2.2._birth_DR.xlsx': {
        'dataset': 'births_marital_status_residence',
        'mode': 'sheet_per_year_blocks',
        'clean_municipality': 'true'
    },
    'Pop_1.2.3._birth_DR.xlsx': {
        'dataset': 'births_by_mother_age',
        'mode': 'sheet_per_year_blocks',
        'clean_municipality': 'true'
    },
    'Pop_4.1.1._Marriages_DR.xlsx': {
        'dataset': 'marriages_by_residence',
        'mode': 'wide_years_triplets'
    },
    'Pop_4.1.2._Marriages_DR.xlsx': {
        'dataset': 'marriages_age_matrix',
        'mode': 'sheet_per_year_matrix'
    },
    'Pop_4.1.5._Marriages_DR.xlsx': {
        'dataset': 'marriages_by_age_sex',
        'mode': 'wide_years_pairs'
    },
    'Pop_4.2.1._Divorces_DR.xlsx': {
        'dataset': 'divorces_by_residence',
        'mode': 'wide_years_triplets'
    },
    'Pop_4.2.2._Divorces_DR.xlsx': {
        'dataset': 'divorces_age_matrix',
        'mode': 'sheet_per_year_matrix'
    },
    'Pop_4.2.5._Divorces_DR.xlsx': {
        'dataset': 'divorces_by_age_sex',
        'mode': 'wide_years_pairs'
    },
}