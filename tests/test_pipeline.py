
from pathlib import Path

import pandas as pd
import pytest

import src.pipeline as pipeline
from src.pipeline import validate_data


@pytest.fixture
def valid_data():
    return pd.DataFrame(
        {
            "observation_id": ["obs-1", "obs-2"],
            "dataset_id": ["dataset-1", "dataset-1"],
            "indicator_id": ["indicator-1", "indicator-2"],
            "place_id": ["place-1", "place-2"],
            "period_start": ["2025-01-01", "2025-01-01"],
            "period_end": ["2025-12-31", "2025-12-31"],
            "period_type": ["year", "year"],
            "value_numeric": [10.0, 20.0],
            "value_text": [None, None],
            "unit_id": ["count", "count"],
            "status": ["active", "active"],
            "source_url": [
                "https://example.com/data1",
                "https://example.com/data2",
            ],
        }
    )


def test_valid_data_passes(valid_data):
    validate_data(valid_data)


def test_duplicate_observation_id_fails(valid_data):
    valid_data.loc[1, "observation_id"] = valid_data.loc[0, "observation_id"]

    with pytest.raises(ValueError, match="Duplicate observation IDs"):
        validate_data(valid_data)


def test_missing_required_value_fails(valid_data):
    valid_data.loc[0, "dataset_id"] = None

    with pytest.raises(ValueError, match="dataset_id"):
        validate_data(valid_data)


def test_invalid_date_fails(valid_data):
    valid_data.loc[0, "period_start"] = "not-a-date"

    with pytest.raises(ValueError, match="invalid dates"):
        validate_data(valid_data)


def test_negative_inflation_is_allowed(valid_data):
    valid_data.loc[0, "value_numeric"] = -2.5

    validate_data(valid_data)


def test_pipeline_fails_when_raw_file_missing(tmp_path, monkeypatch):
    raw_path = tmp_path / "missing.parquet"
    output_path = tmp_path / "processed" / "observations_clean.parquet"

    monkeypatch.setattr(pipeline, "RAW_PATH", raw_path)
    monkeypatch.setattr(pipeline, "OUTPUT_PATH", output_path)
    monkeypatch.setattr(pipeline, "LOG_PATH", tmp_path / "pipeline.log")

    with pytest.raises(FileNotFoundError, match="Raw dataset not found"):
        pipeline.run_pipeline(build_summaries=False)

    assert not output_path.exists()


def test_pipeline_ingests_when_raw_file_missing(
    tmp_path, monkeypatch, valid_data
):
    raw_path = tmp_path / "observations.parquet"
    output_path = tmp_path / "processed" / "observations_clean.parquet"

    monkeypatch.setattr(pipeline, "RAW_PATH", raw_path)
    monkeypatch.setattr(pipeline, "OUTPUT_PATH", output_path)
    monkeypatch.setattr(pipeline, "LOG_PATH", tmp_path / "pipeline.log")

    def fake_download_dataset(destination):
        destination = Path(destination)
        destination.parent.mkdir(parents=True, exist_ok=True)
        valid_data.to_parquet(destination, index=False)
        return destination

    import src.ingest_data as ingest_module

    monkeypatch.setattr(
        ingest_module,
        "download_dataset",
        fake_download_dataset,
    )

    pipeline.run_pipeline(
        download_if_missing=True,
        build_summaries=False,
    )

    assert raw_path.exists()
    assert output_path.exists()

    result = pd.read_parquet(output_path)
    assert len(result) == len(valid_data)


def test_pipeline_skips_ingestion_when_raw_file_exists(
    tmp_path, monkeypatch, valid_data
):
    raw_path = tmp_path / "observations.parquet"
    output_path = tmp_path / "processed" / "observations_clean.parquet"

    valid_data.to_parquet(raw_path, index=False)

    monkeypatch.setattr(pipeline, "RAW_PATH", raw_path)
    monkeypatch.setattr(pipeline, "OUTPUT_PATH", output_path)
    monkeypatch.setattr(pipeline, "LOG_PATH", tmp_path / "pipeline.log")

    import src.ingest_data as ingest_module

    def fail_if_downloaded(*args, **kwargs):
        raise AssertionError("Ingestion should not run when raw data exists")

    monkeypatch.setattr(
        ingest_module,
        "download_dataset",
        fail_if_downloaded,
    )

    pipeline.run_pipeline(
        download_if_missing=True,
        build_summaries=False,
    )

    assert output_path.exists()


def test_pipeline_can_skip_summaries(
    tmp_path, monkeypatch, valid_data
):
    raw_path = tmp_path / "observations.parquet"
    output_path = tmp_path / "processed" / "observations_clean.parquet"

    valid_data.to_parquet(raw_path, index=False)

    monkeypatch.setattr(pipeline, "RAW_PATH", raw_path)
    monkeypatch.setattr(pipeline, "OUTPUT_PATH", output_path)
    monkeypatch.setattr(pipeline, "LOG_PATH", tmp_path / "pipeline.log")

    import src.transform_data as transform_module

    def fail_if_transformed(*args, **kwargs):
        raise AssertionError("Summary generation should have been skipped")

    monkeypatch.setattr(
        transform_module,
        "transform_data",
        fail_if_transformed,
    )

    pipeline.run_pipeline(build_summaries=False)

    assert output_path.exists()


def test_pipeline_uses_custom_input_and_output_paths(
    tmp_path, monkeypatch, valid_data
):
    raw_path = tmp_path / "custom_input.parquet"
    output_path = (
        tmp_path / "custom_output" / "observations_clean.parquet"
    )

    valid_data.to_parquet(raw_path, index=False)

    monkeypatch.setattr(
        pipeline,
        "LOG_PATH",
        tmp_path / "pipeline.log",
    )

    pipeline.run_pipeline(
        input_path=raw_path,
        output_path=output_path,
        build_summaries=False,
    )

    assert raw_path.exists()
    assert output_path.exists()

    result = pd.read_parquet(output_path)

    assert len(result) == len(valid_data)
    assert result["observation_id"].tolist() == (
        valid_data["observation_id"].tolist()
    )
