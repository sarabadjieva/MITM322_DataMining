import argparse

from src.analysis.runner import run_analysis
from src.etl.runner import run_all


def main():
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--mode",
        choices=["etl", "analysis", "all"],
        default="all",
    )

    args = parser.parse_args()

    if args.mode in {"etl", "all"}:
        run_all()

    if args.mode in {"analysis", "all"}:
       run_analysis()

if __name__ == "__main__":
    main()