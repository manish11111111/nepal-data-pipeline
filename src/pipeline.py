
import logging
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
        column for column in REQUIRED_COLUMNS
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

    for column in ["period_start", "period_end"]:
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


def run_pipeline():
    logger = configure_logging()
    logger.info("Starting Nepal public data pipeline")

    try:
        if not RAW_PATH.exists():
            raise FileNotFoundError(
                f"Raw dataset not found: {RAW_PATH}"
            )

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

        logger.info("Output saved to %s", OUTPUT_PATH.relative_to(PROJECT_ROOT))
        logger.info("Rows written: %s", f"{len(df):,}")
        logger.info("Columns written: %s", len(df.columns))
        logger.info("Pipeline completed successfully")

    except Exception:
        logger.exception("Pipeline failed")
        raise


if __name__ == "__main__":
    run_pipeline()
