import json
from pathlib import Path

import pandas as pd

try:
    from .utils import parse_date_columns
except ImportError:
    from utils import parse_date_columns


PROJECT_ROOT = Path(__file__).resolve().parent.parent
RAW_PATH = PROJECT_ROOT / "data" / "raw" / "observations.parquet"
OUTPUT_PATH = PROJECT_ROOT / "data" / "processed" / "data_quality_report.json"


def generate_report():
    if not RAW_PATH.exists():
        raise FileNotFoundError(f"Dataset not found: {RAW_PATH}")

    df = pd.read_parquet(RAW_PATH)

    parsed = parse_date_columns(df, errors="coerce")
    date_start = parsed["period_start"]
    date_end = parsed["period_end"]

    report = {
        "project": "Nepal Public Data Pipeline",
        "source_file": str(RAW_PATH.relative_to(PROJECT_ROOT)),
        "total_rows": int(len(df)),
        "total_columns": int(len(df.columns)),
        "columns": list(df.columns),
        "duplicate_rows": int(df.duplicated().sum()),
        "duplicate_observation_ids": int(
            df["observation_id"].duplicated().sum()
        ),
        "missing_values_by_column": {
            column: int(count)
            for column, count in df.isna().sum().items()
        },
        "dataset_counts": {
            str(key): int(value)
            for key, value in df["dataset_id"].value_counts().items()
        },
        "status_counts": {
            str(key): int(value)
            for key, value in df["status"].value_counts().items()
        },
        "unique_indicators": int(df["indicator_id"].nunique()),
        "unique_places": int(df["place_id"].nunique()),
        "invalid_start_dates": int(date_start.isna().sum()),
        "invalid_end_dates": int(date_end.isna().sum()),
        "period_end_before_start": int(
            (date_end.notna() & date_start.notna() & (date_end < date_start)).sum()
        ),
        "numeric_value_summary": {
            "count": int(df["value_numeric"].count()),
            "minimum": (
                float(df["value_numeric"].min())
                if df["value_numeric"].notna().any()
                else None
            ),
            "maximum": (
                float(df["value_numeric"].max())
                if df["value_numeric"].notna().any()
                else None
            ),
            "negative_values": int((df["value_numeric"] < 0).sum()),
        },
    }

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)

    with OUTPUT_PATH.open("w", encoding="utf-8") as file:
        json.dump(report, file, indent=4, ensure_ascii=False)

    print("Data quality report generated successfully!")
    print(f"Total rows: {report['total_rows']:,}")
    print(f"Total columns: {report['total_columns']}")
    print(f"Duplicate rows: {report['duplicate_rows']}")
    print(
        "Duplicate observation IDs: "
        f"{report['duplicate_observation_ids']}"
    )
    print(f"Unique indicators: {report['unique_indicators']}")
    print(f"Unique places: {report['unique_places']}")
    print(f"Report saved to: {OUTPUT_PATH.relative_to(PROJECT_ROOT)}")


if __name__ == "__main__":
    generate_report()