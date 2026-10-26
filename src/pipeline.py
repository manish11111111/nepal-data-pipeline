
import argparse
import logging
import sys
from pathlib import Path

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parent.parent

RAW_PATH = PROJECT_ROOT / "data" / "raw" / "observations.parquet"
OUTPUT_PATH = (
    PROJECT_ROOT / "data" / "processed" / "observations_clean.parquet"
)
LOG_PATH = PROJECT_ROOT / "logs" / "pipeline.log"

REQUIRED_COLUMNS = [
    "observation_id",
    "dataset_id",
    "indicator_id",
    "place_id",
    "period_start",
    "period_end",
    "period_type",
    "value_numeric",
    "status",
]


def configure_logging():
    LOG_PATH.parent.mkdir(parents=True, exist_ok=True)

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(message)s",
        handlers=[
            logging.FileHandler(LOG_PATH, encoding="utf-8"),
            logging.StreamHandler(),
        ],
        force=True,
    )

    return logging.getLogger(__name__)


def validate_data(df: pd.DataFrame) -> None:
    errors = []

    missing_columns = [
        column
        for column in REQUIRED_COLUMNS
        if column not in df.columns
    ]

    if missing_columns:
        raise ValueError(
            "Missing required columns: " + ", ".join(missing_columns)
        )

    required_non_null_columns = [
        "observation_id",
        "dataset_id",
        "indicator_id",
        "place_id",
        "period_type",
        "status",
    ]

    for column in required_non_null_columns:
        if df[column].isna().any():
            errors.append(f"{column} contains missing values")

    if df["observation_id"].duplicated().any():
        errors.append("Duplicate observation IDs found")

    if "value_text" in df.columns:
        missing_values = (
            df["value_numeric"].isna() & df["value_text"].isna()
        )
    else:
        missing_values = df["value_numeric"].isna()

    if missing_values.any():
        errors.append(
            f"{int(missing_values.sum())} rows have neither "
            "numeric nor text values"
        )

    parsed_dates = {}

    for column in ("period_start", "period_end"):
        parsed = pd.to_datetime(
            df[column],
            errors="coerce",
            format="mixed",
        )

        parsed_dates[column] = parsed

        invalid_count = int(parsed.isna().sum())

        if invalid_count:
            errors.append(
                f"{column} contains {invalid_count} invalid dates"
            )

    start = parsed_dates["period_start"]
    end = parsed_dates["period_end"]

    valid_dates = start.notna() & end.notna()

    if (end[valid_dates] < start[valid_dates]).any():
        errors.append("Some period_end dates are before period_start")

    if errors:
        raise ValueError(
            "DATA VALIDATION FAILED:\n- " + "\n- ".join(errors)
        )


def run_pipeline(
    download_if_missing=False,
    build_summaries=True,
):
    logger = configure_logging()

    logger.info("Starting Nepal public data pipeline")

    try:
        if not RAW_PATH.exists():
            if not download_if_missing:
                raise FileNotFoundError(
                    f"Raw dataset not found: {RAW_PATH}. "
                    "Run with --ingest to download it."
                )

            logger.info("Raw dataset missing; starting ingestion")

            try:
                from .ingest_data import download_dataset
            except ImportError:
                from ingest_data import download_dataset

            download_dataset(RAW_PATH)

            if not RAW_PATH.exists():
                raise FileNotFoundError(
                    "Ingestion completed without creating the raw dataset: "
                    f"{RAW_PATH}"
                )

        logger.info("Reading raw dataset")

        df = pd.read_parquet(RAW_PATH)

        logger.info("Loaded %s rows", f"{len(df):,}")

        validate_data(df)

        logger.info("Data validation passed")

        df["period_start"] = pd.to_datetime(
            df["period_start"],
            errors="raise",
            format="mixed",
        )

        df["period_end"] = pd.to_datetime(
            df["period_end"],
            errors="raise",
            format="mixed",
        )

        OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)

        df.to_parquet(OUTPUT_PATH, index=False)

        try:
            display_path = OUTPUT_PATH.relative_to(PROJECT_ROOT)
        except ValueError:
            display_path = OUTPUT_PATH

        logger.info("Output saved to %s", display_path)
        logger.info("Rows written: %s", f"{len(df):,}")
        logger.info("Columns written: %s", len(df.columns))

        if build_summaries:
            logger.info("Generating summary reports")

            try:
                from .transform_data import transform_data
            except ImportError:
                from transform_data import transform_data

            transform_data(OUTPUT_PATH, OUTPUT_PATH.parent)

            logger.info("Summary reports generated")

        logger.info("Pipeline completed successfully")

    except Exception:
        logger.exception("Pipeline failed")
        raise


def main():
    parser = argparse.ArgumentParser(
        description="Run the Nepal public data pipeline."
    )

    parser.add_argument(
        "--ingest",
        action="store_true",
        help="Download the raw dataset only if it is missing.",
    )

    parser.add_argument(
        "--no-summaries",
        action="store_true",
        help="Skip summary CSV generation.",
    )

    args = parser.parse_args()

    sys.path.insert(0, str(Path(__file__).resolve().parent))

    run_pipeline(
        download_if_missing=args.ingest,
        build_summaries=not args.no_summaries,
    )


if __name__ == "__main__":
    main()
