import pandas as pd

from src.etl.export import export_output, normalize_output_dataframe, export_manifest
from src.etl.parsers.sheet_parser import parse_sheet_per_year_blocks
from src.etl.parsers.triplet_parser import parse_wide_years_triplets
from src.etl.validation import validate_output_dataframe
from src.file_configs import ParseMode, FILE_CONFIGS
from pathlib import Path


PARSERS = {
    ParseMode.WIDE_YEARS_TRIPLETS: parse_wide_years_triplets,
    ParseMode.SHEET_PER_YEAR_BLOCKS: parse_sheet_per_year_blocks,
}

SRC_DIR = Path(__file__).resolve().parent.parent
RAW_DIR = SRC_DIR.parent / "data"


def run_etl_for_file(path: Path, config) -> pd.DataFrame:
    parser = PARSERS[config.mode]
    df = parser(path, config.dataset, filter_districts=config.clean_municipality)
    df = normalize_output_dataframe(df)
    return validate_output_dataframe(df, config.dataset)


def run_all(file_configs=FILE_CONFIGS, raw_dir: Path = RAW_DIR):
    manifest = []

    for filename, config in file_configs.items():
        path = raw_dir / filename
        if not path.exists():
            manifest.append({"file": filename, "status": "missing"})
            continue

        df = run_etl_for_file(path, config)
        export_output(df, config.dataset)

        manifest.append(
            {
                "file": filename,
                "dataset": config.dataset,
                "mode": config.mode.value,
                "rows": int(len(df)),
                "clean_municipality": config.clean_municipality,
            }
        )

        export_manifest(manifest)

    return manifest