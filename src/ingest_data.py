
import argparse
import os
import shutil
import tempfile
from pathlib import Path
from urllib.request import Request, urlopen

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parent.parent

SOURCE_URL = "https://datanepal.org/data/observations.parquet"
DEFAULT_OUTPUT = PROJECT_ROOT / "data" / "raw" / "observations.parquet"

REQUIRED_COLUMNS = {
    "observation_id",
    "dataset_id",
    "indicator_id",
    "place_id",
    "period_start",
    "period_end",
    "period_type",
    "value_numeric",
    "status",
}

EXPECTED_DATASETS = {
    "nso-nphc-2021",
    "cod-ps-npl",
    "worldbank-npl",
    "ecn-hor-2026",
}


def validate_download(path: Path) -> pd.DataFrame:
    df = pd.read_parquet(path)

    missing = REQUIRED_COLUMNS - set(df.columns)
    if missing:
        raise ValueError(
            f"Downloaded dataset is missing columns: {sorted(missing)}"
        )

    if df.empty:
        raise ValueError("Downloaded dataset is empty")

    for column in ("observation_id", "dataset_id"):
        if df[column].isna().any():
            raise ValueError(f"{column} contains missing values")

    if df["observation_id"].duplicated().any():
        raise ValueError("Duplicate observation IDs found")

    actual_datasets = set(df["dataset_id"].unique())
    missing_datasets = EXPECTED_DATASETS - actual_datasets

    if missing_datasets:
        raise ValueError(
            "Expected dataset IDs were not found: "
            f"{sorted(missing_datasets)}"
        )

    return df


def download_dataset(output_path: Path, force: bool = False) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)

    if output_path.exists() and not force:
        print(f"Output already exists; leaving it unchanged: {output_path}")
        print("Use --force only if you intend to replace this file.")
        return

    temp_path = None

    try:
        with tempfile.NamedTemporaryFile(
            dir=output_path.parent,
            suffix=".parquet",
            delete=False,
        ) as temp_file:
            temp_path = Path(temp_file.name)

            request = Request(
                SOURCE_URL,
                headers={"User-Agent": "NepalDataPipeline/1.0"},
            )

            print(f"Downloading dataset from {SOURCE_URL}")

            with urlopen(request, timeout=60) as response:
                shutil.copyfileobj(response, temp_file)

        df = validate_download(temp_path)

        os.replace(temp_path, output_path)
        temp_path = None

        print("Ingestion completed successfully.")
        print(f"Rows: {len(df):,}")
        print(f"Columns: {len(df.columns)}")
        print("Dataset counts:")
        print(df["dataset_id"].value_counts().to_string())
        print(f"Saved to: {output_path}")

    finally:
        if temp_path is not None:
            temp_path.unlink(missing_ok=True)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Download and validate DataNepal observations."
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=DEFAULT_OUTPUT,
        help="Output Parquet path (default: data/raw/observations.parquet)",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Replace the output file after a successful validation.",
    )
    args = parser.parse_args()

    download_dataset(args.output.resolve(), force=args.force)


if __name__ == "__main__":
    main()
