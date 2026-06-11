import pandas as pd

from src.etl.export import export_output, normalize_output_dataframe, export_manifest, export_multiple_outputs
from src.etl.parsers.births_parser import parse_births
from src.etl.parsers.marriages_parser import parse_marriages
from src.etl.validation import validate_output_dataframe
from src.etl.file_configs import ParseMode, FILE_CONFIGS
from pathlib import Path


PARSERS = {
    ParseMode.MARRIAGES: parse_marriages,
    ParseMode.BIRTHS: parse_births,
}

SRC_DIR = Path(__file__).resolve().parent.parent
RAW_DIR = SRC_DIR.parent / "data"


def normalize_and_validate(result, dataset: str):
    if isinstance(result, dict):
        cleaned = {}
        for key, df in result.items():
            df = normalize_output_dataframe(df)
            df = validate_output_dataframe(df, dataset)
            cleaned[key] = df
        return cleaned

    result = normalize_output_dataframe(result)
    return validate_output_dataframe(result, dataset)


def run_etl_for_file(path: Path, config):
    parser = PARSERS[config.mode]
    result = parser(path, config.dataset, filter_districts=config.clean_municipality)
    return normalize_and_validate(result, config.dataset)


def run_all(file_configs=FILE_CONFIGS, raw_dir: Path = RAW_DIR):
    manifest = []

    for filename, config in file_configs.items():
        path = raw_dir / filename
        if not path.exists():
            manifest.append({"file": filename, "status": "missing"})
            continue

        result = run_etl_for_file(path, config)

        if isinstance(result, dict):
            exported = export_multiple_outputs(result, config.dataset)
            manifest.append(
                {
                    "file": filename,
                    "dataset": config.dataset,
                    "mode": config.mode.value,
                    "outputs": {
                        key: {
                            "filename": exported_path.name,
                            "rows": int(len(result[key])),
                        }
                        for key, exported_path in exported.items()
                    },
                    "clean_municipality": config.clean_municipality,
                }
            )
        else:
            exported_path = export_output(result, config.dataset)
            manifest.append(
                {
                    "file": filename,
                    "dataset": config.dataset,
                    "mode": config.mode.value,
                    "rows": int(len(result)),
                    "output_file": exported_path.name,
                    "clean_municipality": config.clean_municipality,
                }
            )

    export_manifest(manifest)
    return manifest