from src.analysis.clustering import cluster_regions
from src.analysis.helpers import RESIDENCE_METRICS
from src.analysis.data import load_raw_datasets
from src.analysis.nonmarital_birth_share import nonmarital_birth_share
from src.analysis.plotting import plot_results
from src.analysis.correlations import lag_correlations_period, regional_lag_matrix
from src.analysis.classes import AnalysisResults, RawDatasets
from src.analysis.sets_builder import build_national_datasets, build_regional_datasets


def run_analysis_pipeline(
    raw_datasets: RawDatasets,
    metric="total",
) -> AnalysisResults:
    if metric not in RESIDENCE_METRICS:
        raise ValueError(f"Unsupported metric: {metric}")

    national = build_national_datasets(raw_datasets, metric)
    regional = build_regional_datasets(raw_datasets, metric)

    cluster_features, cluster_diagnostics = cluster_regions(regional)

    return AnalysisResults(
        metric=metric,
        national_sets=national,
        regional_sets=regional,
        lags=lag_correlations_period(national, 2010, 2025),
        regional_lags=regional_lag_matrix(regional),
        nonmarital_share=nonmarital_birth_share(
            raw_datasets.marital,
            raw_datasets.nonmarital,
            metric,
        ),
        clusters={"kmeans": cluster_features},
        inertia={"kmeans": cluster_diagnostics},
    )


def build_analysis_results():
    raw_datasets = load_raw_datasets()

    results = []

    for metric in RESIDENCE_METRICS:
        curr_results = run_analysis_pipeline(raw_datasets, metric)
        results.append(curr_results)

    return results


def plot_analysis_results(results):
    for result in results:
        plot_results(result)


def run_analysis():
    results = build_analysis_results()
    plot_analysis_results(results)
