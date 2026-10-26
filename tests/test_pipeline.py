
import pandas as pd
import pytest

from src import pipeline
from src.pipeline import validate_data


@pytest.fixture
def valid_data():
    return pd.DataFrame({
        "observation_id": ["obs_001", "obs_002"],
        "dataset_id": ["worldbank-npl", "worldbank-npl"],
        "indicator_id": [
            "cpi_inflation_annual",
            "cpi_inflation_annual",
        ],
        "place_id": ["place_001", "place_001"],
        "period_start": ["1971-01-01", "1972-01-01"],
        "period_end": ["1971-12-31", "1972-12-31"],
        "period_type": ["year", "year"],
        "value_numeric": [-2.0, 5.0],
        "value_text": [None, None],
        "unit_id": ["percent", "percent"],
        "status": ["actual", "actual"],
        "dimension_key": ["none", "none"],
    })


def test_valid_data_passes(valid_data):
    validate_data(valid_data)


def test_duplicate_observation_id_fails(valid_data):
    valid_data.loc[1, "observation_id"] = "obs_001"

    with pytest.raises(ValueError, match="Duplicate observation IDs"):
        validate_data(valid_data)


def test_missing_required_value_fails(valid_data):
    valid_data.loc[0, "value_numeric"] = float("nan")
    valid_data.loc[0, "value_text"] = None

    with pytest.raises(ValueError, match="neither numeric nor text values"):
        validate_data(valid_data)


def test_invalid_date_fails(valid_data):
    valid_data.loc[0, "period_start"] = "not-a-date"

    with pytest.raises(ValueError, match="invalid dates"):
        validate_data(valid_data)


def test_negative_inflation_is_allowed(valid_data):
    validate_data(valid_data)
    assert valid_data.loc[0, "value_numeric"] < 0


def test_pipeline_fails_when_raw_file_missing(monkeypatch, tmp_path):
    monkeypatch.setattr(pipeline, "RAW_PATH", tmp_path / "missing.parquet")
    monkeypatch.setattr(pipeline, "OUTPUT_PATH", tmp_path / "clean.parquet")
    monkeypatch.setattr(pipeline, "LOG_PATH", tmp_path / "pipeline.log")

    with pytest.raises(FileNotFoundError, match="Raw dataset not found"):
        pipeline.run_pipeline()


def test_pipeline_ingests_when_raw_file_missing(
    monkeypatch, tmp_path, valid_data
):
    raw_path = tmp_path / "raw" / "observations.parquet"
    output_path = tmp_path / "processed" / "clean.parquet"

    monkeypatch.setattr(pipeline, "RAW_PATH", raw_path)
    monkeypatch.setattr(pipeline, "OUTPUT_PATH", output_path)
    monkeypatch.setattr(pipeline, "LOG_PATH", tmp_path / "pipeline.log")

    def fake_download(path):
        path.parent.mkdir(parents=True, exist_ok=True)
        valid_data.to_parquet(path, index=False)

    def fake_transform(input_path, output_dir):
        assert input_path == output_path
        assert output_dir == output_path.parent

    monkeypatch.setattr(
        "src.ingest_data.download_dataset", fake_download
    )
    monkeypatch.setattr(
        "src.transform_data.transform_data", fake_transform
    )

    pipeline.run_pipeline(download_if_missing=True)

    assert raw_path.exists()
    assert output_path.exists()

    cleaned = pd.read_parquet(output_path)
    assert len(cleaned) == len(valid_data)


def test_pipeline_skips_ingestion_when_raw_file_exists(
    monkeypatch, tmp_path, valid_data
):
    raw_path = tmp_path / "observations.parquet"
    output_path = tmp_path / "clean.parquet"

    valid_data.to_parquet(raw_path, index=False)

    monkeypatch.setattr(pipeline, "RAW_PATH", raw_path)
    monkeypatch.setattr(pipeline, "OUTPUT_PATH", output_path)
    monkeypatch.setattr(pipeline, "LOG_PATH", tmp_path / "pipeline.log")

    def unexpected_download(*args, **kwargs):
        pytest.fail("Ingestion should not run when raw data already exists")

    def fake_transform(input_path, output_dir):
        assert input_path == output_path

    monkeypatch.setattr(
        "src.ingest_data.download_dataset", unexpected_download
    )
    monkeypatch.setattr(
        "src.transform_data.transform_data", fake_transform
    )

    pipeline.run_pipeline(download_if_missing=True)

    assert output_path.exists()


def test_pipeline_can_skip_summaries(monkeypatch, tmp_path, valid_data):
    raw_path = tmp_path / "observations.parquet"
    output_path = tmp_path / "clean.parquet"

    valid_data.to_parquet(raw_path, index=False)

    monkeypatch.setattr(pipeline, "RAW_PATH", raw_path)
    monkeypatch.setattr(pipeline, "OUTPUT_PATH", output_path)
    monkeypatch.setattr(pipeline, "LOG_PATH", tmp_path / "pipeline.log")

    def unexpected_transform(*args, **kwargs):
        pytest.fail("Summary generation should have been skipped")

    monkeypatch.setattr(
        "src.transform_data.transform_data", unexpected_transform
    )

    pipeline.run_pipeline(build_summaries=False)

    assert output_path.exists()
