from src.etl.export import export_output, normalize_output_dataframe, export_manifest, export_multiple_outputs
from src.etl.parsers.births_parser import parse_births
from src.etl.parsers.marriages_parser import parse_marriages
from src.etl.validation import validate_output_dataframe
from src.etl.file_configs import ParseMode, FILE_CONFIGS, RAW_DIR
from pathlib import Path


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
    match config.mode:
        case ParseMode.MARRIAGES:
            result = parse_marriages(path, config.clean_municipality)

        case ParseMode.BIRTHS:
            result = parse_births(path, config.clean_municipality)

        case _:
            raise ValueError(f"Unsupported mode: {config.mode}")

    return normalize_and_validate(result, config.dataset)


def run_all():
    manifest = []

    for filename, config in FILE_CONFIGS.items():
        path = RAW_DIR / filename
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
                    "outputs": {
                        key: {
                            "output_file": exported_path.name,
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
                    "rows": int(len(result)),
                    "output_file": exported_path.name,
                    "clean_municipality": config.clean_municipality,
                }
            )

    export_manifest(manifest)
    return manifest