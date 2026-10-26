# Nepal Public Data Pipeline

A reproducible data engineering project that validates, transforms, and stores public data about Nepal using Python, Parquet, and PostgreSQL. The project includes automated testing, data quality reporting, execution logging, Docker Compose, and continuous integration with GitHub Actions.

## Overview

The pipeline processes a Parquet dataset containing public observations about Nepal. It validates data integrity, standardizes date fields, generates cleaned data, and loads the results into PostgreSQL for downstream analysis.

The project demonstrates core data engineering practices, including reliable transformations, data validation, duplicate protection, containerization, and automated testing.

## Features

- Read and process Parquet data using pandas and PyArrow
- Validate required columns and mandatory identifiers
- Detect duplicate observation IDs and invalid data
- Validate dates and observation periods
- Generate cleaned Parquet output
- Generate data quality reports and transformation summaries
- Record pipeline execution logs
- Load processed observations into PostgreSQL
- Prevent accidental duplicate database loads
- Run the pipeline and database using Docker Compose
- Automate testing with pytest and GitHub Actions

## Dataset Summary

| Metric | Result |
|---|---:|
| Observations | 27,182 |
| Columns | 12 |
| Unique indicators | 36 |
| Unique places | 838 |
| Duplicate observation IDs | 0 |
| Duplicate rows | 0 |

### Dataset Distribution

| Dataset ID | Observations |
|---|---:|
| `nso-nphc-2021` | 21,258 |
| `cod-ps-npl` | 4,590 |
| `worldbank-npl` | 1,213 |
| `ecn-hor-2026` | 121 |
| **Total** | **27,182** |

These figures describe the dataset currently processed by the project. Refer to the original providers for definitions, source metadata, update frequency, and licensing terms.

## Technology Stack

- **Language:** Python
- **Data Processing:** pandas, PyArrow, Parquet
- **Database:** PostgreSQL
- **Containerization:** Docker, Docker Compose
- **Testing:** pytest
- **Continuous Integration:** GitHub Actions
- **Version Control:** Git and GitHub

## Project Structure

```text
nepal-data-pipeline/
â”œâ”€â”€ .github/
â”‚   â””â”€â”€ workflows/
â”œâ”€â”€ data/
â”‚   â”œâ”€â”€ raw/
â”‚   â””â”€â”€ processed/
â”œâ”€â”€ logs/
â”œâ”€â”€ src/
â”‚   â”œâ”€â”€ pipeline.py
â”‚   â”œâ”€â”€ transform_data.py
â”‚   â”œâ”€â”€ validate_data.py
â”‚   â”œâ”€â”€ inspect_data.py
â”‚   â”œâ”€â”€ profile_data.py
â”‚   â”œâ”€â”€ data_quality_report.py
â”‚   â”œâ”€â”€ load_to_postgres.py
â”‚   â””â”€â”€ check_postgres_connection.py
â”œâ”€â”€ tests/
â”‚   â”œâ”€â”€ test_pipeline.py
â”‚   â”œâ”€â”€ test_transform_data.py
â”‚   â””â”€â”€ test_load_to_postgres.py
â”œâ”€â”€ .dockerignore
â”œâ”€â”€ .gitignore
â”œâ”€â”€ Dockerfile
â”œâ”€â”€ compose.yaml
â”œâ”€â”€ requirements.txt
â””â”€â”€ README.md
```

## Prerequisites

- Python
- Git
- Docker Desktop with Docker Compose
- The source Parquet dataset

## Getting Started

### 1. Clone the Repository

```bash
git clone https://github.com/manish11111111/nepal-data-pipeline.git
cd nepal-data-pipeline
```

### 2. Prepare the Dataset

Download the observations dataset from [DataNepal's dataset catalogue](https://www.datanepal.org/datasets/).

Place the downloaded Parquet file at:

`data/raw/observations.parquet`

The project expects this file as its raw input. Raw and processed data files are excluded from version control, so each user must obtain the dataset separately.

The dataset currently used for development contains 27,182 observations across 12 columns and four dataset IDs. These counts describe the downloaded snapshot and may change when the upstream dataset is updated.

**Data attribution and licensing:** DataNepal aggregates information from multiple providers. Refer to the dataset catalogue for the original publishers, source-specific licences, attribution requirements, retrieval dates, and methodological caveats. Do not assume that every source uses the same licence.

### 3. Install Dependencies

Create and activate a virtual environment.

**Windows PowerShell**

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

## Run Locally

Run the data processing pipeline:

```powershell
python -m src.pipeline
```

Generate the data quality report:

```powershell
python -m src.data_quality_report
```

Run the transformation workflow:

```powershell
python -m src.transform_data
```

The transformation workflow requires its configured input data to be available.

## PostgreSQL Integration

The project includes a loader that writes cleaned observations to PostgreSQL.

Configure the connection using these environment variables when required:

- `DB_HOST`
- `DB_PORT`
- `DB_NAME`
- `DB_USER`
- `DB_PASSWORD`

Without these variables, the loader uses its local connection defaults and prompts for a password if one is not supplied.

Run the loader after generating the cleaned Parquet file:

```powershell
python -m src.load_to_postgres
```

The loader creates the `observations` table if necessary and stops when the table already contains records to prevent accidental duplicate loading.

## Run with Docker Compose

### 1. Configure the Database Password

Create a `.env` file in the project root:

```dotenv
POSTGRES_PASSWORD=replace_with_your_own_strong_password
```

Replace the placeholder with a strong password. Do not commit or share this file.

### 2. Start PostgreSQL

```powershell
docker compose up -d db
```

PostgreSQL is available on host port `5433` and container port `5432`.

### 3. Run the Pipeline

```powershell
docker compose run --rm pipeline
```

### 4. Load Data into PostgreSQL

```powershell
docker compose run --rm --no-deps --entrypoint python pipeline src/load_to_postgres.py
```

Run the initial load only once for a fresh database. The loader intentionally stops if records already exist.

### 5. Verify the Database

Check the total number of observations:

```powershell
docker compose exec db psql -U pipeline_user -d nepal_data -c "SELECT COUNT(*) AS total_rows FROM observations;"
```

Inspect observations by dataset:

```powershell
docker compose exec db psql -U pipeline_user -d nepal_data -c "SELECT dataset_id, COUNT(*) AS row_count FROM observations GROUP BY dataset_id ORDER BY row_count DESC;"
```

Stop the containers:

```powershell
docker compose down
```

This stops and removes the containers while preserving the named database volume. Avoid `docker compose down -v` unless you intentionally want to delete the persisted Docker database.

## Testing

Run the automated test suite:

```powershell
python -m pytest -v
```

The test suite contains 15 tests covering pipeline validation, data transformations, missing files, database loading behavior, duplicate-load protection, and row-count checks.

**Latest verified local result:** 15 tests passed.

## Outputs

Depending on the workflow executed, generated artifacts include:

- `data/processed/observations_clean.parquet`
- `data/processed/data_quality_report.json`
- Transformation summary files under `data/processed/`
- `logs/pipeline.log`

Generated data and logs are excluded from version control.

## Continuous Integration

GitHub Actions runs automated checks on repository changes to help detect regressions and maintain code reliability.

## Future Improvements

- Add configurable data quality thresholds
- Record source metadata and data provenance
- Add scheduled ingestion and refresh workflows
- Improve database schema management and incremental loading
- Add a dashboard for exploring dataset quality
- Document source licensing and update frequency

## Data and Licensing

The dataset contains observations from multiple providers. Review the original providers' licensing conditions and attribution requirements before redistributing source data.

Validation checks establish whether data meets defined technical rules; they do not independently establish the accuracy or meaning of every observation.

