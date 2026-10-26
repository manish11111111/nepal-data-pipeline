
import pandas as pd

from src.transform_data import (
    INPUT_PATH,
    OUTPUT_DIR,
    transform_data,
)


def test_transform_creates_summary_files():
    transform_data()

    assert (OUTPUT_DIR / "indicator_summary.csv").exists()
    assert (OUTPUT_DIR / "dataset_summary.csv").exists()


def test_indicator_summary_has_required_columns():
    transform_data()

    summary = pd.read_csv(OUTPUT_DIR / "indicator_summary.csv")

    expected_columns = {
        "dataset_id",
        "indicator_id",
        "unit_id",
        "observation_count",
        "unique_places",
        "unique_periods",
        "numeric_value_count",
        "mean_value",
        "minimum_value",
        "maximum_value",
    }

    assert expected_columns.issubset(summary.columns)


def test_dataset_summary_counts_match_cleaned_data():
    transform_data()

    source = pd.read_parquet(INPUT_PATH)
    summary = pd.read_csv(OUTPUT_DIR / "dataset_summary.csv")

    assert summary["observation_count"].sum() == len(source)


def test_indicator_summary_counts_match_cleaned_data():
    transform_data()

    source = pd.read_parquet(INPUT_PATH)
    summary = pd.read_csv(OUTPUT_DIR / "indicator_summary.csv")

    assert summary["observation_count"].sum() == len(source)


def test_summary_observation_counts_are_positive():
    transform_data()

    indicator_summary = pd.read_csv(
        OUTPUT_DIR / "indicator_summary.csv"
    )
    dataset_summary = pd.read_csv(
        OUTPUT_DIR / "dataset_summary.csv"
    )

    assert (indicator_summary["observation_count"] > 0).all()
    assert (dataset_summary["observation_count"] > 0).all()
