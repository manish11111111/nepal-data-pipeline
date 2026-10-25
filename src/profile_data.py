
from pathlib import Path
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_PATH = PROJECT_ROOT / "data" / "raw" / "observations.parquet"


def main():
    df = pd.read_parquet(DATA_PATH)

    print("\n--- DATASET IDENTIFIERS ---")
    print(df["dataset_id"].value_counts(dropna=False).to_string())

    print("\n--- TOP 15 INDICATORS ---")
    print(df["indicator_id"].value_counts().head(15).to_string())

    print("\n--- OBSERVATIONS BY STATUS ---")
    print(df["status"].value_counts(dropna=False).to_string())

    print("\n--- OBSERVATIONS BY PERIOD TYPE ---")
    print(df["period_type"].value_counts(dropna=False).to_string())

    print("\n--- OBSERVATIONS BY UNIT ---")
    print(df["unit_id"].value_counts(dropna=False).head(20).to_string())

    print("\n--- UNIQUE ENTITY COUNTS ---")
    for column in [
        "dataset_id",
        "indicator_id",
        "place_id",
        "period_type",
        "unit_id",
    ]:
        print(f"{column}: {df[column].nunique(dropna=False)}")

    print("\n--- DATE VALIDATION ---")
    for column in ["period_start", "period_end"]:
        dates = pd.to_datetime(df[column], errors="coerce")
        print(f"{column}: invalid dates = {dates.isna().sum()}")

    start = pd.to_datetime(df["period_start"], errors="coerce")
    end = pd.to_datetime(df["period_end"], errors="coerce")
    print("End before start:", (end < start).sum())

    print("\n--- NUMERIC VALUE PROFILE ---")
    print(df["value_numeric"].describe().to_string())
    print("Negative numeric values:", (df["value_numeric"] < 0).sum())

    print("\n--- IDENTIFIER CHECKS ---")
    print("Null observation IDs:", df["observation_id"].isna().sum())
    print("Duplicate observation IDs:", df["observation_id"].duplicated().sum())

    business_key = [
        "dataset_id",
        "indicator_id",
        "place_id",
        "period_start",
        "period_end",
        "dimension_key",
    ]
    print(
        "Repeated business-key combinations:",
        df.duplicated(subset=business_key).sum(),
    )


if __name__ == "__main__":
    main()
