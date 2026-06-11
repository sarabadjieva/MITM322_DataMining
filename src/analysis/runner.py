import pandas as pd
from pathlib import Path

from src.analysis.clustering import cluster_regions
from src.analysis.plotting import (
    plot_national_trend,
    plot_lag_analysis,
    plot_top_regions,
    plot_outside_share,
    plot_elbow,
    plot_clusters,
)
from src.analysis.metrics import (
    national_trend,
    regional_dataset,
    outside_marriage_share,
    lag_correlations,
    regional_correlations,
)
from src.analysis.result import AnalysisResults

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
    }


def run_analysis_pipeline(
    marriages: pd.DataFrame,
    births_marital: pd.DataFrame,
    births_nonmarital: pd.DataFrame,
) -> AnalysisResults:
    trend = national_trend(marriages, births_marital, births_nonmarital)
    regional = regional_dataset(marriages, births_marital, births_nonmarital)

    clusters = {}
    inertia = {}
    for birth_type, regional_df in regional.items():
        features, inertia_df = cluster_regions(regional_df)
        clusters[birth_type] = features
        inertia[birth_type] = inertia_df

    return AnalysisResults(
        trend=trend,
        lags=lag_correlations(trend),
        regional=regional,
        correlations=regional_correlations(regional),
        outside_share=outside_marriage_share(births_marital, births_nonmarital),
        clusters=clusters,
        inertia=inertia,
    )


def run_analysis():
    data = load_data()

    results = run_analysis_pipeline(
        marriages=data["marriages"],
        births_marital=data["births_marital"],
        births_nonmarital=data["births_nonmarital"],
    )

    plot_national_trend(results.trend)
    plot_lag_analysis(results.lags)
    plot_top_regions(results.correlations)
    plot_outside_share(results.outside_share)
    plot_elbow(results.inertia)
    plot_clusters(results.clusters)