# Nepal Public Data Pipeline

A reproducible data engineering project that ingests, validates, transforms, and stores public data about Nepal using Python, Parquet, and PostgreSQL. The project demonstrates data quality checks, automated testing, execution logging, containerization, and continuous integration with GitHub Actions.

## Overview

This project processes public observations about Nepal from a Parquet dataset. It supports downloading the source dataset when needed, validating its structure and data integrity, standardizing date fields, generating cleaned Parquet output, producing summary reports, and loading processed observations into PostgreSQL.

The pipeline is designed around reproducibility and data integrity. It includes automated tests for validation, ingestion behavior, transformation outputs, and database loading safeguards.

## Features

- **Data ingestion:** Download the source Parquet dataset when the raw input is missing and ingestion is explicitly enabled.
- **Data validation:** Check required columns, mandatory identifiers, duplicate observation IDs, date validity, and observation periods.
- **Data cleaning:** Standardize date fields and write validated observations to Parquet.
- **Data transformation:** Generate indicator-level and dataset-level summary reports.
- **Data quality reporting:** Produce a structured data quality report.
- **Execution logging:** Record pipeline progress and errors.
- **PostgreSQL integration:** Load cleaned observations into a relational database.
- **Duplicate-load protection:** Prevent accidental repeat loading into a populated table.
- **Containerization:** Run PostgreSQL and pipeline workflows using Docker Compose.
- **Automated testing:** Test ingestion, validation, transformations, and database-loading behavior with pytest.
- **Continuous integration:** Run automated checks through GitHub Actions.

## Dataset Summary

The development dataset currently processed by this project contains the following snapshot:

| Metric | Result |
|---|---:|
| Observations | 27,182 |
| Columns | 12 |
| Unique indicators | 36 |
| Unique places | 838 |
| Duplicate observation IDs | 0 |
| Duplicate rows | 0 |

### Dataset distribution

| Dataset ID | Observations |
|---|---:|
| `nso-nphc-2021` | 21,258 |
| `cod-ps-npl` | 4,590 |
| `worldbank-npl` | 1,213 |
| `ecn-hor-2026` | 121 |
| **Total** | **27,182** |

These figures describe the development snapshot and may change when the upstream dataset is updated. The transformation workflow currently generates 37 rows in the indicator summary and 4 rows in the dataset summary; summary rows are not necessarily the same as the number of unique indicator IDs.

## Technology Stack

- **Language:** Python
- **Data processing:** pandas, PyArrow, Parquet
- **Database:** PostgreSQL
- **Containerization:** Docker, Docker Compose
- **Testing:** pytest
- **Version control:** Git and GitHub
- **Continuous integration:** GitHub Actions

## Project Structure

```text
nepal-data-pipeline/
├── .github/
│   └── workflows/
├── data/
│   ├── raw/
│   └── processed/
├── logs/
├── src/
│   ├── __init__.py
│   ├── ingest_data.py
│   ├── pipeline.py
│   ├── transform_data.py
│   ├── validate_data.py
│   ├── inspect_data.py
│   ├── profile_data.py
│   ├── data_quality_report.py
│   ├── load_to_postgres.py
│   └── check_postgres_connection.py
├── tests/
│   ├── test_pipeline.py
│   ├── test_transform_data.py
│   └── test_load_to_postgres.py
├── .dockerignore
├── .gitignore
├── Dockerfile
├── compose.yaml
├── requirements.txt
└── README.md
```

Generated data files, logs, virtual environments, and environment configuration files are excluded from version control. The exact repository structure may include additional configuration or support files.

## Prerequisites

- Python installed on your system
- Git
- Docker Desktop with Docker Compose, for containerized workflows
- Internet access when downloading the source dataset

## Getting Started

### 1. Clone the repository

```bash
git clone https://github.com/manish11111111/nepal-data-pipeline.git
cd nepal-data-pipeline
```

### 2. Create and activate a virtual environment

**Windows PowerShell**

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

### 3. Obtain the source dataset

The pipeline uses the following source file:

```text
data/raw/observations.parquet
```

You can obtain the dataset from the [DataNepal dataset catalogue](https://www.datanepal.org/datasets/).

Alternatively, if the raw file is missing, run the pipeline with the `--ingest` option to request the project's configured download workflow.

Raw and processed data files are excluded from version control, so a fresh clone may not include the dataset.

**Data attribution and licensing:** DataNepal aggregates information from multiple providers. Check the catalogue and original publishers for source metadata, licensing terms, attribution requirements, retrieval dates, and methodological caveats. Do not assume that all sources use the same licence.

## Run the Pipeline

Run the pipeline using the available raw dataset:

```powershell
python -m src.pipeline
```

If the raw dataset is missing and you want the pipeline to attempt ingestion:

```powershell
python -m src.pipeline --ingest
```

The `--ingest` option enables the download workflow when the expected raw file is missing. It does not mean that every normal run downloads a fresh copy.

To run the pipeline without generating transformation summaries:

```powershell
python -m src.pipeline --no-summaries
```

The pipeline validates the input, writes the cleaned Parquet output, and generates summary reports by default.

### Generated outputs

The principal output files include:

```text
data/processed/observations_clean.parquet
data/processed/indicator_summary.csv
data/processed/dataset_summary.csv
data/processed/data_quality_report.json
logs/pipeline.log
```

Individual outputs are generated by their corresponding workflows. For example, the data quality report is produced by the data quality reporting script rather than necessarily by every pipeline run.

To run the transformation workflow separately:

```powershell
python -m src.transform_data
```

To generate the data quality report:

```powershell
python -m src.data_quality_report
```

These commands require their configured input data to be available.

## PostgreSQL Integration

The project includes a loader that writes cleaned observations to PostgreSQL.

Configure the following environment variables as required by your database setup:

- `DB_HOST`
- `DB_PORT`
- `DB_NAME`
- `DB_USER`
- `DB_PASSWORD`

The loader may use configured local defaults when environment variables are absent. Consult the database configuration in the source code before running it.

Run the loader after generating the cleaned Parquet file:

```powershell
python -m src.load_to_postgres
```

The loader creates the `observations` table when necessary and checks for existing records before loading data. If the table already contains records, the loader stops rather than accidentally inserting a duplicate full dataset.

For a populated database, do not clear the table or delete the database volume merely to rerun the loader. Follow the project's database safeguards.

## Run with Docker Compose

Docker Compose provides a containerized workflow for PostgreSQL and the pipeline.

### 1. Configure the database password

Create a `.env` file in the project root if required by your Compose configuration:

```dotenv
POSTGRES_PASSWORD=replace_with_your_own_strong_password
```

Replace the placeholder with a strong password. Never commit or share the `.env` file.

### 2. Start PostgreSQL

```powershell
docker compose up -d db
```

In the current local setup, PostgreSQL is exposed on host port `5433` and listens on container port `5432`.

### 3. Run the pipeline

```powershell
docker compose run --rm pipeline
```

Ensure the input dataset is available to the container. For a fresh setup, review the Compose volume and data-mount configuration before running the pipeline.

### 4. Load data into PostgreSQL

```powershell
docker compose run --rm --no-deps --entrypoint python pipeline src/load_to_postgres.py
```

Run the initial load only once for a fresh database. The loader intentionally stops if records already exist.

### 5. Verify the database

Check the number of observations:

```powershell
docker compose exec db psql -U pipeline_user -d nepal_data -c "SELECT COUNT(*) AS total_rows FROM observations;"
```

Inspect records by dataset:

```powershell
docker compose exec db psql -U pipeline_user -d nepal_data -c "SELECT dataset_id, COUNT(*) AS row_count FROM observations GROUP BY dataset_id ORDER BY row_count DESC;"
```

### 6. Stop the containers

```powershell
docker compose down
```

This stops and removes the containers while preserving the named database volume. Avoid `docker compose down -v` unless you intentionally want to delete the persisted Docker database.

## Testing

Run the automated test suite:

```powershell
python -m pytest -v
```

**Latest verified local result: 19 tests passed.**

The test suite covers:

- Required-column and data-integrity validation
- Duplicate observation ID detection
- Invalid dates and missing values
- Negative inflation values
- Missing raw-file behavior
- Optional ingestion behavior
- Summary-generation options
- Transformation output schemas and row counts
- Missing cleaned-file handling
- Database loading safeguards and row-count verification

The reported result is from the local test run; it should not be interpreted as a claim that every possible input or deployment configuration has been tested.

## Continuous Integration

GitHub Actions runs automated checks on repository changes to help detect regressions and maintain code reliability.

## Future Improvements

- Add configurable data quality thresholds.
- Record source metadata, retrieval timestamps, and data provenance.
- Add scheduled ingestion and refresh workflows.
- Introduce incremental loading and explicit database schema migrations.
- Add stronger integration tests using an isolated PostgreSQL instance.
- Build a dashboard for exploring dataset quality and summary statistics.
- Document source licensing, update frequency, and known data limitations.
- Add pipeline metrics and monitoring for production-style observability.

## Data Quality and Licensing Notes

Validation checks establish whether the dataset meets defined technical rules. They do not independently establish the accuracy, completeness, or interpretation of every observation.

Before redistributing source data, review the relevant original providers' licensing conditions and attribution requirements.
