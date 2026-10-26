# Nepal Public Data Pipeline

A reproducible data engineering project that ingests, validates, transforms, and stores public data about Nepal using Python, Parquet, and PostgreSQL. The project demonstrates data quality validation, automated testing, execution logging, containerization, and continuous integration with GitHub Actions.

## Overview

This project processes public observations about Nepal from a Parquet dataset published through DataNepal. It supports downloading the source dataset when required, validating data integrity, standardizing date fields, generating cleaned Parquet output, producing summary reports, and loading processed observations into PostgreSQL.

The pipeline is designed around reproducibility and data integrity. Automated tests cover pipeline behavior, ingestion, transformations, and database-loading safeguards.

## Features

- **Data ingestion:** Download and validate the source dataset when the raw input is missing.
- **Data validation:** Check required columns, missing identifiers, duplicate observation IDs, date validity, and observation periods.
- **Data cleaning:** Standardize date fields and write validated observations to Parquet.
- **Data transformation:** Generate indicator-level and dataset-level summary reports.
- **Data quality reporting:** Generate a structured data quality report.
- **Execution logging:** Record pipeline progress and errors.
- **PostgreSQL integration:** Load cleaned observations into a relational database.
- **Duplicate-load protection:** Stop loading when the destination table already contains records.
- **Containerization:** Run PostgreSQL and pipeline workflows using Docker Compose.
- **Automated testing:** Use pytest to test pipeline functionality.
- **Continuous integration:** Run automated tests through GitHub Actions.

## Dataset Summary

The current development dataset contains the following snapshot:

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

These figures describe the development snapshot and may change when the upstream dataset is updated.

The transformation workflow currently generates 37 rows in the indicator summary and 4 rows in the dataset summary. Summary row counts do not necessarily equal the number of unique indicator IDs.

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
│       └── tests.yml
├── data/
│   ├── raw/
│   └── processed/
├── logs/
├── src/
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
├── .dockerignore
├── .gitignore
├── Dockerfile
├── compose.yaml
├── requirements.txt
└── README.md
```

Generated data files, logs, virtual environments, and environment configuration files are excluded from version control.

## Prerequisites

- Python 3.12 or a compatible Python version
- Git
- Docker Desktop with Docker Compose, for containerized workflows
- Internet access when downloading the source dataset

Python 3.12 is the version configured in the Docker image and GitHub Actions workflow.

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

The pipeline expects the raw dataset at:

```text
data/raw/observations.parquet
```

The configured source URL is:

https://datanepal.org/data/observations.parquet

To download and validate the dataset directly:

```powershell
python .\src\ingest_data.py
```

The ingestion script validates the downloaded Parquet file before replacing the destination. If the destination already exists, it leaves that file unchanged unless `--force` is explicitly supplied.

Alternatively, run the pipeline with `--ingest` to download the dataset if the expected raw file is missing.

Raw and processed data files are excluded from version control, so a fresh clone may not include the dataset.

**Data attribution and licensing:** DataNepal aggregates information from multiple providers. Consult the DataNepal catalogue and original publishers for source metadata, licensing terms, attribution requirements, retrieval dates, and methodological caveats. Do not assume all sources use the same licence.

## Run the Pipeline

### Run with an existing raw dataset

```powershell
python .\src\pipeline.py
```

### Download the dataset if it is missing

```powershell
python .\src\pipeline.py --ingest
```

The `--ingest` option enables downloading only when the expected raw dataset is missing. It does not force a fresh download on every run.

### Skip summary generation

```powershell
python .\src\pipeline.py --no-summaries
```

The pipeline validates the input, standardizes date fields, writes the cleaned Parquet output, and generates summary reports by default.

### Generated outputs

The principal output files are:

```text
data/processed/observations_clean.parquet
data/processed/indicator_summary.csv
data/processed/dataset_summary.csv
data/processed/data_quality_report.json
logs/pipeline.log
```

The cleaned Parquet file, summary CSVs, and pipeline log are produced by the main pipeline workflow. The data quality report is generated by its dedicated reporting script rather than necessarily by every pipeline run.

## PostgreSQL Integration

The project includes a loader that writes cleaned observations to PostgreSQL.

The loader reads the following environment variables:

| Variable | Purpose |
|---|---|
| `DB_HOST` | Database host |
| `DB_PORT` | Database port |
| `DB_NAME` | Database name |
| `DB_USER` | Database username |
| `DB_PASSWORD` | Database password |

When variables are not provided, the loader uses its configured defaults and may prompt for the password.

Run the loader after generating the cleaned Parquet file:

```powershell
python .\src\load_to_postgres.py
```

The loader creates the `observations` table if necessary and checks whether it already contains records. If the table is populated, the loader stops instead of inserting the entire dataset again.

**Important:** The development database already contains 27,182 observations. Do not rerun the loader against that populated table, or delete the database volume just to repeat the initial load.

## Run with Docker Compose

### 1. Configure the database password

Create a `.env` file in the project root:

```dotenv
POSTGRES_PASSWORD=replace_with_your_own_strong_password
```

Replace the placeholder with your own strong password. Never commit or share the `.env` file.

### 2. Start PostgreSQL

```powershell
docker compose up -d db
```

The current configuration exposes PostgreSQL on host port `5433`, mapped to container port `5432`.

### 3. Run the pipeline container

The pipeline service uses the `pipeline` Compose profile:

```powershell
docker compose --profile pipeline run --rm pipeline
```

The container runs `python src/pipeline.py`. Ensure the raw dataset exists in `data/raw/observations.parquet` before running this command, unless you explicitly override the command to enable ingestion.

### 4. Load the data into PostgreSQL

For a fresh database with an empty `observations` table, run:

```powershell
docker compose --profile pipeline run --rm --no-deps --entrypoint python pipeline src/load_to_postgres.py
```

Run the initial load only once. The loader intentionally stops if records already exist.

### 5. Verify the database

Check the total number of observations:

```powershell
docker compose exec db psql -U pipeline_user -d nepal_data -c "SELECT COUNT(*) AS total_rows FROM observations;"
```

Inspect the distribution by dataset:

```powershell
docker compose exec db psql -U pipeline_user -d nepal_data -c "SELECT dataset_id, COUNT(*) AS row_count FROM observations GROUP BY dataset_id ORDER BY row_count DESC;"
```

### 6. Stop the containers

```powershell
docker compose down
```

This stops and removes the containers while preserving the named database volume. Avoid `docker compose down -v` unless you intentionally want to delete the persisted database volume.

## Testing

Run the automated test suite:

```powershell
python -m pytest -v
```

**Latest verified local result: 19 tests passed.**

The test suite covers pipeline validation, missing input handling, ingestion behavior, optional summary generation, transformation outputs, and database-loading safeguards.

This result reflects the recorded local test run; it does not imply that every possible input or deployment configuration has been tested.

## Continuous Integration

GitHub Actions runs the automated test suite on pushes and pull requests targeting the `main` branch.

The workflow is defined in `.github/workflows/tests.yml` and uses Python 3.12 to install the project dependencies and run:

```bash
python -m pytest -v
```

## Future Improvements

- Add configurable data quality thresholds.
- Record source metadata, retrieval timestamps, and data provenance.
- Introduce scheduled ingestion and refresh workflows.
- Implement incremental loading and explicit database schema migrations.
- Add integration tests using an isolated PostgreSQL instance.
- Build a dashboard for exploring dataset quality and summary statistics.
- Document source licensing, update frequency, and known data limitations.
- Add pipeline metrics and monitoring for production-style observability.

## Data Quality and Licensing Notes

Validation checks establish whether a dataset meets defined technical rules. They do not independently establish the accuracy, completeness, or interpretation of every observation.

Before redistributing source data, review the relevant original providers' licensing conditions and attribution requirements.
