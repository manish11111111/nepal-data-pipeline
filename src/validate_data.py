
from pathlib import Path
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_PATH = PROJECT_ROOT / "data" / "raw" / "observations.parquet"


def main():
    df = pd.read_parquet(DATA_PATH)

    print("\n--- RECORDS BY DATASET AND STATUS ---")
    print(
        pd.crosstab(
            df["dataset_id"],
            df["status"],
            margins=True,
        ).to_string()
    )

    print("\n--- NEGATIVE VALUES ---")
    negative = df.loc[
        df["value_numeric"] < 0,
        [
            "observation_id",
            "dataset_id",
            "indicator_id",
            "place_id",
            "period_start",
            "value_numeric",
            "unit_id",
            "status",
        ],
    ]
    print(negative.to_string(index=False))

    print("\n--- MISSING VALUES BY DATASET ---")
    print(
        df.groupby("dataset_id")["value_text"]
        .apply(lambda column: column.isna().sum())
        .to_string()
    )

    print("\n--- PERIOD DISTRIBUTION BY DATASET ---")
    print(
        df.groupby(["dataset_id", "period_type"])
        .size()
        .to_string()
    )

    print("\n--- INDICATOR AND UNIT COMBINATIONS ---")
    print(
        df.groupby(["indicator_id", "unit_id"])
        .size()
        .sort_values(ascending=False)
        .head(30)
        .to_string()
    )

    print("\n--- VALIDATION SUMMARY ---")
    checks = {
        "Null observation IDs": df["observation_id"].isna().sum(),
        "Duplicate observation IDs": df["observation_id"].duplicated().sum(),
        "Null dataset IDs": df["dataset_id"].isna().sum(),
        "Null indicator IDs": df["indicator_id"].isna().sum(),
        "Null place IDs": df["place_id"].isna().sum(),
        "Null numeric and text values": (
            df["value_numeric"].isna() & df["value_text"].isna()
        ).sum(),
    }

    for check, count in checks.items():
        print(f"{check}: {count}")


if __name__ == "__main__":
    main()
