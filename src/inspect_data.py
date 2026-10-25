
from pathlib import Path
import pandas as pd

file_path = Path("data/raw/observations.parquet")

df = pd.read_parquet(file_path)

print("\n--- DATASET OVERVIEW ---")
print(f"Rows: {df.shape[0]:,}")
print(f"Columns: {df.shape[1]}")

print("\n--- COLUMN NAMES ---")
print(df.columns.tolist())

print("\n--- FIRST FIVE ROWS ---")
print(df.head().to_string())

print("\n--- DATA TYPES ---")
print(df.dtypes.to_string())

print("\n--- MISSING VALUES ---")
print(df.isnull().sum().to_string())

print("\n--- DUPLICATE ROWS ---")
print(df.duplicated().sum())
