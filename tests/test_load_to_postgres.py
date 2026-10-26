
import pandas as pd
import pytest

from src import load_to_postgres as loader


class FakeCursor:
    def __init__(self, counts):
        self.counts = iter(counts)
        self.executed = []
        self.inserted_rows = []

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        return False

    def execute(self, query):
        self.executed.append(query)

    def fetchone(self):
        return (next(self.counts),)

    def executemany(self, query, rows):
        self.inserted_rows = list(rows)


class FakeConnection:
    def __init__(self, cursor):
        self.fake_cursor = cursor

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        return False

    def cursor(self):
        return self.fake_cursor


@pytest.fixture
def sample_data():
    return pd.DataFrame({
        "observation_id": ["obs_001", "obs_002"],
        "dataset_id": ["worldbank-npl", "worldbank-npl"],
        "indicator_id": ["gdp_per_capita_usd", "life_expectancy_at_birth"],
        "place_id": ["pl_001", "pl_001"],
        "period_start": pd.to_datetime(["2020-01-01", "2021-01-01"]),
        "period_end": pd.to_datetime(["2020-12-31", "2021-12-31"]),
        "period_type": ["year", "year"],
        "value_numeric": [100.5, float("nan")],
        "value_text": [None, None],
        "unit_id": ["usd", "years"],
        "status": ["actual", "actual"],
        "dimension_key": [None, None],
    })


def configure_loader(monkeypatch, tmp_path, sample_data, counts):
    data_path = tmp_path / "observations_clean.parquet"
    data_path.touch()

    monkeypatch.setattr(loader, "DATA_PATH", data_path)
    monkeypatch.setattr(
        loader.pd, "read_parquet", lambda path: sample_data.copy()
    )
    monkeypatch.setattr(
        loader.getpass, "getpass", lambda prompt: "test-password"
    )

    cursor = FakeCursor(counts)
    connection = FakeConnection(cursor)

    monkeypatch.setattr(
        loader.psycopg, "connect", lambda **kwargs: connection
    )

    return cursor


def test_missing_cleaned_file_fails(monkeypatch, tmp_path):
    missing_path = tmp_path / "missing.parquet"
    monkeypatch.setattr(loader, "DATA_PATH", missing_path)

    with pytest.raises(FileNotFoundError, match="Cleaned dataset not found"):
        loader.load_data()


def test_successful_loading(monkeypatch, tmp_path, sample_data, capsys):
    cursor = configure_loader(
        monkeypatch, tmp_path, sample_data, counts=[0, 2]
    )

    loader.load_data()

    assert len(cursor.inserted_rows) == 2
    assert cursor.inserted_rows[0][0] == "obs_001"
    assert cursor.inserted_rows[1][0] == "obs_002"
    assert cursor.inserted_rows[0][7] == 100.5
    assert cursor.inserted_rows[1][7] is None
    assert "Rows in PostgreSQL: 2" in capsys.readouterr().out


def test_existing_data_prevents_duplicate_loading(
    monkeypatch, tmp_path, sample_data
):
    cursor = configure_loader(
        monkeypatch, tmp_path, sample_data, counts=[100]
    )

    with pytest.raises(RuntimeError, match="already contains 100 rows"):
        loader.load_data()

    assert cursor.inserted_rows == []


def test_row_count_mismatch_fails(
    monkeypatch, tmp_path, sample_data
):
    configure_loader(
        monkeypatch, tmp_path, sample_data, counts=[0, 1]
    )

    with pytest.raises(RuntimeError, match="Row count mismatch"):
        loader.load_data()
