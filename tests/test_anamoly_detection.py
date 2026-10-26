from pathlib import Path

import pandas as pd
import pytest

from src.anomaly_detection import detect_anomalies


@pytest.fixture
def sample_data(tmp_path):
    df = pd.DataFrame(
        {
            "observation_id": [f"obs-{i}" for i in range(60)],
            "dataset_id": ["test"] * 60,
            "indicator_id": ["indicator-a"] * 60,
            "place_id": ["place-1"] * 60,
            "period_start": pd.date_range("2020-01-01", periods=60, freq="D"),
            "period_end": pd.date_range("2020-12-31", periods=60, freq="D"),
            "period_type": ["day"] * 60,
            "value_numeric": [10.0] * 59 + [1000.0],
            "value_text": [None] * 60,
            "unit_id": ["count"] * 60,
            "status": ["actual"] * 60,
            "dimension_key": [None] * 60,
        }
    )
    input_path = tmp_path / "clean.parquet"
    df.to_parquet(input_path, index=False)
    return input_path, tmp_path / "anomalies.parquet"


def test_detects_outlier(sample_data):
    input_path, output_path = sample_data
    result = detect_anomalies(input_path, output_path)

    assert "is_anomaly" in result.columns
    assert output_path.exists()
    assert result["is_anomaly"].sum() >= 1


def test_missing_input_fails(tmp_path):
    with pytest.raises(FileNotFoundError, match="Cleaned dataset not found"):
        detect_anomalies(
            tmp_path / "missing.parquet",
            tmp_path / "out.parquet",
        )