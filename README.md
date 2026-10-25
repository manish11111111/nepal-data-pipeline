# Nepal Public Data Pipeline

A Python-based data engineering project that processes and validates public data about Nepal from a Parquet dataset.

## Project Overview

This project demonstrates a basic, reproducible data pipeline with automated data validation, quality reporting, and execution logging.

The pipeline reads the raw dataset, checks required fields and data integrity, standardizes date columns, and writes a processed Parquet file without modifying the original input.

## Features

- Reads Parquet data using pandas and PyArrow
- Validates required columns and mandatory identifiers
- Detects duplicate observation IDs
- Checks missing values and invalid dates
- Validates period start and end dates
- Writes processed data in Parquet format
- Generates a JSON data quality report
- Records pipeline execution logs
- Includes automated tests using pytest

## Dataset Summary

| Metric | Result |
|---|---:|
| Records inspected | 27,182 |
| Columns | 12 |
| Unique indicators | 36 |
| Unique places | 838 |
| Duplicate observation IDs | 0 |
| Duplicate rows | 0 |

The dataset contains observations from multiple sources. Consult the dataset provider's documentation for source details, definitions, and licensing terms.

## Technology Stack

- Python
- pandas
- PyArrow
- pytest
- Parquet
- JSON
- Git and GitHub

## Project Structure

```text
nepal-data-pipeline/
├── data/
│   ├── raw/
│   └── processed/
├── logs/
├── src/
│   ├── inspect_data.py
│   ├── profile_data.py
│   ├── validate_data.py
│   ├── pipeline.py
│   └── data_quality_report.py
├── tests/
│   └── test_pipeline.py
├── requirements.txt
├── .gitignore
└── README.md
```

## Setup

Create and activate a virtual environment, then install the dependencies.

```bash
python -m venv .venv
```

Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

## Run the Pipeline

```bash
python -m src.pipeline
```

## Generate a Data Quality Report

```bash
python -m src.data_quality_report
```

The report is written to:

`data/processed/data_quality_report.json`

## Run Automated Tests

```bash
python -m pytest -v
```

The current test suite contains five tests covering valid data, duplicate IDs, missing values, invalid dates, and negative numeric values.

## Outputs

- `data/processed/observations_clean.parquet`
- `data/processed/data_quality_report.json`
- `logs/pipeline.log`

## Future Improvements

- Add structured data quality thresholds
- Add source metadata and data provenance
- Automate pipeline execution and tests with GitHub Actions
- Add a dashboard for exploring dataset quality
- Document dataset licensing and update frequency

## Data and Licensing

Before redistributing the raw dataset, review the original provider's licensing terms and attribution requirements. This project should distinguish validation results from assumptions about the meaning or quality of individual observations.
