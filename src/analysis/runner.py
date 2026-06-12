import pandas as pd
from pathlib import Path

from src.analysis.clustering import cluster_regions
from src.analysis.plotting import plot_results
from src.analysis.metrics import (
    lag_correlations_period,
    outside_marriage_share,
    regional_correlations,
)
from src.analysis.result import AnalysisResults, RawDatasets, RESIDENCE_METRICS
from src.analysis.trends import build_national_datasets, build_regional_datasets

SRC_DIR = Path(__file__).resolve().parent.parent
OUTPUT_DIR = SRC_DIR / "output"


def load_data(output_dir=OUTPUT_DIR):
    return {
        "marriages": pd.read_csv(f"{output_dir}/marriages_by_residence_clean.csv"),
        "births_marital": pd.read_csv(
            f"{output_dir}/births_marital_status_residence_marital_clean.csv"
        ),
        "births_nonmarital": pd.read_csv(
            f"{output_dir}/births_marital_status_residence_nonmarital_clean.csv"
        ),
        "births_all": pd.read_csv(
            f"{output_dir}/births_marital_status_residence_all_clean.csv"
        ),
    }


def run_analysis_pipeline(raw_datasets, metric="total") -> AnalysisResults:
    if metric not in RESIDENCE_METRICS:
        raise ValueError(f"Unsupported metric: {metric}")

    trend = build_national_datasets(raw_datasets, metric)
    regional = build_regional_datasets(raw_datasets, metric)

    clusters = {}
    inertia = {}

    for birth_type, regional_df in regional.items():
        features, inertia_df = cluster_regions(regional_df)
        clusters[birth_type] = features
        inertia[birth_type] = inertia_df

    return AnalysisResults(
        metric=metric,
        trend=trend,
        lags=lag_correlations_period(trend, 2010, 2025),
        pre_covid_lags=lag_correlations_period(trend, 2010, 2019),
        post_covid_lags=lag_correlations_period(trend, 2019, 2025),
        regional=regional,
        correlations=regional_correlations(regional),
        outside_share=outside_marriage_share(
            raw_datasets.marital,
            raw_datasets.nonmarital,
            metric,
        ),
        clusters=clusters,
        inertia=inertia,
    )


def run_analysis(metrics=RESIDENCE_METRICS):
    data = load_data()

    raw_datasets = RawDatasets(
        data["marriages"],
        data["births_marital"],
        data["births_nonmarital"],
        data["births_all"],
    )

    results_by_metric = {}
    for metric in metrics:
        results = run_analysis_pipeline(raw_datasets, metric)
        results_by_metric[metric] = results
        plot_results(results)

    return results_by_metric
