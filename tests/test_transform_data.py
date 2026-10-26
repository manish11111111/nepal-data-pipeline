
import pandas as pd
import pytest

from src.transform_data import transform_data


@pytest.fixture
def sample_data(tmp_path):
    source = pd.DataFrame(
        {
            "observation_id": ["obs1", "obs2", "obs3", "obs4"],
            "dataset_id": ["dataset_a", "dataset_a", "dataset_a", "dataset_b"],
            "indicator_id": ["indicator_x", "indicator_x", "indicator_y", "indicator_z"],
            "unit_id": ["people", "people", "percent", "index"],
            "place_id": ["place_1", "place_2", "place_1", "place_3"],
            "period_start": pd.to_datetime(
                ["2021-01-01", "2022-01-01", "2021-01-01", "2023-01-01"]
            ),
            "period_end": pd.to_datetime(
                ["2021-12-31", "2022-12-31", "2021-12-31", "2023-12-31"]
            ),
            "value_numeric": [100.0, 200.0, 25.5, 99.0],
            "status": ["observed", "observed", "observed", "projected"],
            "period_type": ["yearly", "yearly", "yearly", "yearly"],
        }
    )

    input_path = tmp_path / "observations_clean.parquet"
    output_dir = tmp_path / "processed"

    source.to_parquet(input_path, index=False)

    return input_path, output_dir, source


def test_transform_creates_summary_files(sample_data):
    input_path, output_dir, _ = sample_data

    transform_data(input_path, output_dir)

    assert (output_dir / "indicator_summary.csv").exists()
    assert (output_dir / "dataset_summary.csv").exists()


def test_indicator_summary_has_required_columns(sample_data):
    input_path, output_dir, _ = sample_data

    transform_data(input_path, output_dir)

    summary = pd.read_csv(output_dir / "indicator_summary.csv")

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


def test_dataset_summary_counts_match_cleaned_data(sample_data):
    input_path, output_dir, source = sample_data

    transform_data(input_path, output_dir)

    summary = pd.read_csv(output_dir / "dataset_summary.csv")

    assert summary["observation_count"].sum() == len(source)


def test_indicator_summary_counts_match_cleaned_data(sample_data):
    input_path, output_dir, source = sample_data

    transform_data(input_path, output_dir)

    summary = pd.read_csv(output_dir / "indicator_summary.csv")

    assert summary["observation_count"].sum() == len(source)


def test_summary_observation_counts_are_positive(sample_data):
    input_path, output_dir, _ = sample_data

    transform_data(input_path, output_dir)

    indicator_summary = pd.read_csv(
        output_dir / "indicator_summary.csv"
    )
    dataset_summary = pd.read_csv(
        output_dir / "dataset_summary.csv"
    )

    assert (indicator_summary["observation_count"] > 0).all()
    assert (dataset_summary["observation_count"] > 0).all()


def test_missing_input_file_fails(tmp_path):
    missing_path = tmp_path / "missing.parquet"
    output_dir = tmp_path / "processed"

    with pytest.raises(FileNotFoundError, match="Cleaned dataset not found"):
        transform_data(missing_path, output_dir)
