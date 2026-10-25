
import pandas as pd
import pytest

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
