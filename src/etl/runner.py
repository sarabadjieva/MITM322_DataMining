from src.etl.export import export_output, normalize_output_dataframe, export_manifest, export_multiple_outputs
from src.etl.parsers.births_parser import parse_births
from src.etl.parsers.marriages_parser import parse_marriages
from src.etl.validation import validate_output_dataframe
from src.etl.file_configs import ParseMode, FILE_CONFIGS, RAW_DIR
from pathlib import Path


def clean_output(df, dataset):
    return validate_output_dataframe(normalize_output_dataframe(df), dataset)


def normalize_and_validate(result, dataset: str):
    if isinstance(result, dict):
        return {key: clean_output(df, dataset) for key, df in result.items()}

    return clean_output(result, dataset)


def run_etl_for_file(path: Path, config):
    match config.mode:
        case ParseMode.MARRIAGES:
            result = parse_marriages(path)

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

        manifest_entry = {
            "file": filename,
            "dataset": config.dataset,
            "clean_municipality": config.clean_municipality,
        }

        if isinstance(result, dict):
            exported = export_multiple_outputs(result, config.dataset)
            manifest_entry["outputs"] = {
                key: {"output_file": path.name, "rows": int(len(result[key]))}
                for key, path in exported.items()
            }
        else:
            exported_path = export_output(result, config.dataset)
            manifest_entry.update(
                rows=int(len(result)),
                output_file=exported_path.name,
            )

        manifest.append(manifest_entry)

    export_manifest(manifest)
    return manifest
