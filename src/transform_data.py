
from pathlib import Path

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parent.parent
INPUT_PATH = PROJECT_ROOT / "data" / "processed" / "observations_clean.parquet"
OUTPUT_DIR = PROJECT_ROOT / "data" / "processed"


def transform_data(input_path=INPUT_PATH, output_dir=OUTPUT_DIR):
    input_path = Path(input_path)
    output_dir = Path(output_dir)

    if not input_path.exists():
        raise FileNotFoundError(
            f"Cleaned dataset not found: {input_path}. "
            "Run src/pipeline.py first."
        )

    df = pd.read_parquet(input_path)

    df["value_numeric"] = pd.to_numeric(
        df["value_numeric"], errors="raise"
    )

    indicator_summary = (
        df.groupby(
            ["dataset_id", "indicator_id", "unit_id"],
            dropna=False,
        )
        .agg(
            observation_count=("observation_id", "count"),
            unique_places=("place_id", "nunique"),
            unique_periods=("period_start", "nunique"),
            first_period=("period_start", "min"),
            last_period=("period_end", "max"),
            numeric_value_count=("value_numeric", "count"),
            mean_value=("value_numeric", "mean"),
            minimum_value=("value_numeric", "min"),
            maximum_value=("value_numeric", "max"),
        )
        .reset_index()
        .sort_values(
            ["dataset_id", "indicator_id"],
            ignore_index=True,
        )
    )

    dataset_summary = (
        df.groupby(
            ["dataset_id", "status", "period_type"],
            dropna=False,
        )
        .agg(
            observation_count=("observation_id", "count"),
            unique_indicators=("indicator_id", "nunique"),
            unique_places=("place_id", "nunique"),
            first_period=("period_start", "min"),
            last_period=("period_end", "max"),
        )
        .reset_index()
        .sort_values(
            ["dataset_id", "status", "period_type"],
            ignore_index=True,
        )
    )

    output_dir.mkdir(parents=True, exist_ok=True)

    indicator_path = output_dir / "indicator_summary.csv"
    dataset_path = output_dir / "dataset_summary.csv"

    indicator_summary.to_csv(indicator_path, index=False)
    dataset_summary.to_csv(dataset_path, index=False)

    print("Data transformation completed successfully!")
    print(f"Input observations: {len(df):,}")
    print(f"Indicator summary rows: {len(indicator_summary):,}")
    print(f"Dataset summary rows: {len(dataset_summary):,}")
    print(f"Saved: {indicator_path}")
    print(f"Saved: {dataset_path}")


if __name__ == "__main__":
    transform_data()
