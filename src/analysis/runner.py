import pandas as pd
from pathlib import Path

from src.analysis.clustering import cluster_regions
from src.analysis.plotting import plot_results
from src.analysis.metrics import (
    outside_marriage_share,
    regional_correlations, lag_correlations_period,
)
from src.analysis.result import AnalysisResults, RawDatasets
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


def run_analysis_pipeline(raw_datasets) -> AnalysisResults:
    trend = build_national_datasets(raw_datasets)
    regional = build_regional_datasets(raw_datasets)

    clusters = {}
    inertia = {}

    for birth_type, regional_df in {
        "marital": regional.marital,
        "nonmarital": regional.nonmarital,
        "total": regional.total,
    }.items():
        features, inertia_df = cluster_regions(regional_df)
        clusters[birth_type] = features
        inertia[birth_type] = inertia_df

    return AnalysisResults(
        trend=trend,
        lags=lag_correlations_period(trend, 2010, 2025),
        pre_covid_lags=lag_correlations_period(trend, 2010, 2019),
        post_covid_lags=lag_correlations_period(trend, 2019, 2025),
        regional=regional,
        correlations=regional_correlations(regional),
        outside_share=outside_marriage_share(raw_datasets.marital, raw_datasets.nonmarital),
        clusters=clusters,
        inertia=inertia,
    )


def run_analysis():
    data = load_data()

    raw_datasets = RawDatasets(data["marriages"],data["births_marital"],data["births_nonmarital"],data["births_all"])
    results = run_analysis_pipeline(raw_datasets)

    plot_results(results)