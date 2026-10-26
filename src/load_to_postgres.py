
import getpass
import os
from pathlib import Path

import pandas as pd
import psycopg
from psycopg import sql

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_PATH = PROJECT_ROOT / "data" / "processed" / "observations_clean.parquet"


def load_data():
    if not DATA_PATH.exists():
        raise FileNotFoundError(
            f"Cleaned dataset not found: {DATA_PATH}. "
            "Run src/pipeline.py first."
        )

    df = pd.read_parquet(DATA_PATH)

    password = os.getenv("DB_PASSWORD")
    if not password:
        password = getpass.getpass("PostgreSQL password: ")

    host = os.getenv("DB_HOST", "localhost")
    port = int(os.getenv("DB_PORT", "5432"))
    dbname = os.getenv("DB_NAME", "nepal_data")
    user = os.getenv("DB_USER", "postgres")

    with psycopg.connect(
        host=host,
        port=port,
        dbname=dbname,
        user=user,
        password=password,
    ) as conn:
        with conn.cursor() as cur:
            cur.execute("""
                CREATE TABLE IF NOT EXISTS observations (
                    observation_id TEXT PRIMARY KEY,
                    dataset_id TEXT NOT NULL,
                    indicator_id TEXT NOT NULL,
                    place_id TEXT NOT NULL,
                    period_start DATE,
                    period_end DATE,
                    period_type TEXT,
                    value_numeric DOUBLE PRECISION,
                    value_text TEXT,
                    unit_id TEXT,
                    status TEXT NOT NULL,
                    dimension_key TEXT
                );
            """)

            cur.execute("SELECT COUNT(*) FROM observations;")
            existing_count = cur.fetchone()[0]

            if existing_count > 0:
                raise RuntimeError(
                    f"Table already contains {existing_count} rows. "
                    "Stopping to avoid accidental duplicate loading."
                )

            columns = list(df.columns)
            insert_query = sql.SQL(
                "INSERT INTO observations ({}) VALUES ({})"
            ).format(
                sql.SQL(", ").join(
                    sql.Identifier(column) for column in columns
                ),
                sql.SQL(", ").join(sql.Placeholder() for _ in columns),
            )

            rows = [
                tuple(
                    None if pd.isna(value) else value
                    for value in row
                )
                for row in df.itertuples(index=False, name=None)
            ]

            cur.executemany(insert_query, rows)

            cur.execute("SELECT COUNT(*) FROM observations;")
            loaded_count = cur.fetchone()[0]

            if loaded_count != len(df):
                raise RuntimeError(
                    f"Row count mismatch: expected {len(df)}, "
                    f"found {loaded_count}."
                )

    print("PostgreSQL data loading completed successfully!")
    print(f"Rows in source file: {len(df):,}")
    print(f"Rows in PostgreSQL: {loaded_count:,}")
    print("Table: observations")


if __name__ == "__main__":
    load_data()
