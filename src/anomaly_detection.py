from pathlib import Path

import pandas as pd
from sklearn.ensemble import IsolationForest


PROJECT_ROOT = Path(__file__).resolve().parent.parent
INPUT_PATH = PROJECT_ROOT / "data" / "processed" / "observations_clean.parquet"
OUTPUT_PATH = PROJECT_ROOT / "data" / "processed" / "anomalies.parquet"


def detect_anomalies(
    input_path: Path = INPUT_PATH,
    output_path: Path = OUTPUT_PATH,
    contamination: float = 0.05,
) -> pd.DataFrame:
    """Detect anomalies in value_numeric per indicator.

    Args:
        input_path: Cleaned Parquet dataset.
        output_path: Where to write the anomaly-tagged dataset.
        contamination: Expected proportion of outliers.

    Returns:
        DataFrame with an added `is_anomaly` boolean column.
    """
    if not input_path.exists():
        raise FileNotFoundError(
            f"Cleaned dataset not found: {input_path}. "
            "Run src/pipeline.py first."
        )

    df = pd.read_parquet(input_path)
    df["is_anomaly"] = False

    numeric = df["value_numeric"].notna()
    if numeric.sum() < 10:
        df.to_parquet(output_path, index=False)
        return df

    # Fit per indicator when there are enough rows; otherwise fit globally.
    indicator_counts = df.loc[numeric, "indicator_id"].value_counts()

    for indicator_id, count in indicator_counts.items():
        if count < 20:
            continue

        mask = numeric & (df["indicator_id"] == indicator_id)
        values = df.loc[mask, ["value_numeric"]]

        model = IsolationForest(
            contamination=contamination,
            random_state=42,
        )
        predictions = model.fit_predict(values)
        df.loc[mask, "is_anomaly"] = predictions == -1

    # Global fallback for indicators with too few rows.
    small_indicators = indicator_counts[indicator_counts < 20].index
    if len(small_indicators) > 0:
        mask = numeric & df["indicator_id"].isin(small_indicators)
        if mask.sum() >= 10:
            values = df.loc[mask, ["value_numeric"]]
            model = IsolationForest(
                contamination=contamination,
                random_state=42,
            )
            predictions = model.fit_predict(values)
            df.loc[mask, "is_anomaly"] = predictions == -1

    output_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_parquet(output_path, index=False)

    print("Anomaly detection completed.")
    print(f"Rows scanned: {len(df):,}")
    print(f"Anomalies flagged: {int(df['is_anomaly'].sum()):,}")
    print(f"Saved: {output_path}")

    return df


if __name__ == "__main__":
    detect_anomalies()