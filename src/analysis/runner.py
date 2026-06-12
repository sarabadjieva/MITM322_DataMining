from src.analysis.clustering import cluster_regions
from src.analysis.constants import RESIDENCE_METRICS
from src.analysis.data import load_raw_datasets
from src.analysis.plotting import plot_nonmarital_share_by_metric, plot_results
from src.analysis.metrics import (
    lag_correlations_period,
    nonmarital_birth_share,
    nonmarital_birth_share_by_metric,
    regional_correlations,
)
from src.analysis.result import AnalysisResults, MultiMetricAnalysisResults, RawDatasets
from src.analysis.trends import build_national_datasets, build_regional_datasets


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
        nonmarital_share=nonmarital_birth_share(
            raw_datasets.marital,
            raw_datasets.nonmarital,
            metric,
        ),
        clusters=clusters,
        inertia=inertia,
    )


def build_analysis_results(metrics=RESIDENCE_METRICS):
    raw_datasets = load_raw_datasets()

    nonmarital_share_by_metric = nonmarital_birth_share_by_metric(
        raw_datasets.marital,
        raw_datasets.nonmarital,
        metrics=metrics,
    )

    results_by_metric = {}
    for metric in metrics:
        results = run_analysis_pipeline(raw_datasets, metric)
        results_by_metric[metric] = results

    return MultiMetricAnalysisResults(
        by_metric=results_by_metric,
        nonmarital_share_by_metric=nonmarital_share_by_metric,
    )


def plot_analysis_results(results: MultiMetricAnalysisResults):
    plot_nonmarital_share_by_metric(results.nonmarital_share_by_metric)

    for result in results.by_metric.values():
        plot_results(result)


def run_analysis(metrics=RESIDENCE_METRICS):
    results = build_analysis_results(metrics)
    plot_analysis_results(results)
    return results
