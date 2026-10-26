# Nepal Public Data Pipeline

A reproducible data engineering pipeline for public observations about Nepal.

This project demonstrates an end-to-end data preparation workflow using Python, pandas, Apache Parquet, and PostgreSQL. It separates ingestion, validation, transformation, summarization, and database loading into distinct stages to make data processing easier to test and maintain.

## Table of Contents

- [Overview](#overview)
- [Key Features](#key-features)
- [Technology Stack](#technology-stack)
- [Architecture](#architecture)
- [Data Source](#data-source)
- [Project Structure](#project-structure)
- [Data Validation](#data-validation)
- [Generated Outputs](#generated-outputs)
- [Getting Started](#getting-started)
- [Running the Pipeline](#running-the-pipeline)
- [Running with Docker](#running-with-docker)
- [Loading Data into PostgreSQL](#loading-data-into-postgresql)
- [Testing and Continuous Integration](#testing-and-continuous-integration)
- [Verified Results](#verified-results)
- [Engineering Decisions](#engineering-decisions)
- [Limitations and Future Improvements](#limitations-and-future-improvements)
- [Data Attribution and Licensing](#data-attribution-and-licensing)
- [Author](#author)

---

## Overview

Public datasets become more useful when they can be processed consistently, validated before analysis, and stored in formats suitable for downstream applications.

The Nepal Public Data Pipeline processes public observations related to Nepal. It retrieves a source dataset in Parquet format, validates its structure and contents, transforms the observations, and generates analytical summary reports.

The processed data can also be loaded into PostgreSQL through a separate database-loading step.

The project focuses on practical data engineering concepts, including:

- Modular pipeline design
- Data quality validation
- Structured data transformation
- Analytical storage using Parquet
- Relational database loading
- Automated testing
- Containerized development
- Continuous integration

## Key Features

| Feature | Description |
|---|---|
| Data ingestion | Downloads the upstream observations dataset |
| Data validation | Checks required fields, identifiers, observation values, and date consistency |
| Data transformation | Produces a cleaned dataset for downstream analysis |
| Summary generation | Creates indicator-level and dataset-level CSV reports |
| Parquet storage | Stores raw and processed observations in a columnar format |
| PostgreSQL integration | Loads cleaned observations into a relational database |
| Loading safeguards | Protects against loading into an already populated target table |
| Docker Compose | Provides a containerized environment for the database and optional pipeline service |
| Automated tests | Uses pytest to verify important pipeline behaviors |
| Continuous integration | Uses GitHub Actions to run automated tests |

## Technology Stack

| Technology | Purpose |
|---|---|
| Python | Pipeline implementation |
| pandas | Data manipulation and transformation |
| Apache Parquet | Columnar data storage |
| PyArrow | Parquet support |
| PostgreSQL | Relational data storage |
| psycopg | PostgreSQL connectivity |
| Docker | Containerization |
| Docker Compose | Local service management |
| pytest | Automated testing |
| GitHub Actions | Continuous integration |

## Architecture

The architecture diagram below illustrates the pipeline stages, generated outputs, and separate PostgreSQL loading workflow.

<p align="center">
  <img src="docs/images/nepal-data-pipeline-architecture1.png" alt="Nepal Public Data Pipeline architecture showing ingestion, validation, transformation, analytical outputs, and PostgreSQL loading" width="900">
</p>

<p align="center">
  <a href="docs/images/nepal-data-pipeline-architecture1.svg">View the full-resolution architecture diagram (SVG)</a>
</p>

### Pipeline stages

1. **Ingestion:** Retrieves the public observations dataset.
2. **Validation:** Checks the input data for structural and consistency problems.
3. **Transformation:** Processes observation fields and produces a cleaned Parquet dataset.
4. **Summarization:** Generates indicator-level and dataset-level CSV reports.
5. **Database loading:** Loads the cleaned observations into PostgreSQL through a separate operation.
6. **Testing:** Verifies pipeline behavior using automated tests.

The standard pipeline prepares data and generates summaries. PostgreSQL loading is a separate operation rather than an automatic part of the default workflow.

## Data Source

The pipeline uses the public observations dataset published by [DataNepal](https://datanepal.org/).

- **Dataset:** [observations.parquet](https://datanepal.org/data/observations.parquet)
- **Format:** Apache Parquet
- **Content:** Structured observations from datasets related to Nepal

The ingestion workflow expects supported dataset identifiers, including:

- `nso-nphc-2021`
- `cod-ps-npl`
- `worldbank-npl`
- `ecn-hor-2026`

The source dataset may change over time. Therefore, row counts and summary statistics reported in this README describe the data snapshot used during development, not guaranteed permanent totals.

## Project Structure

```text
nepal-data-pipeline/
├── .github/
│   └── workflows/
│       └── tests.yml
├── data/
│   ├── raw/
│   │   └── observations.parquet
│   └── processed/
│       ├── observations_clean.parquet
│       ├── indicator_summary.csv
│       └── dataset_summary.csv
├── docs/
│   └── images/
│       ├── nepal-data-pipeline-architecture1.png
│       └── nepal-data-pipeline-architecture1.svg
├── logs/
│   └── pipeline.log
├── src/
│   ├── ingest_data.py
│   ├── pipeline.py
│   ├── transform_data.py
│   ├── load_to_postgres.py
│   └── check_postgres_connection.py
├── tests/
├── .gitignore
├── docker-compose.yml
├── requirements.txt
└── README.md
```

The `data/` and `logs/` directories contain generated artifacts and may not appear in a fresh clone if they are excluded by `.gitignore`. The structure above describes the intended project layout.

## Data Validation

Data validation helps detect malformed or inconsistent observations before downstream processing.

The pipeline checks include:

- Presence of required columns
- Missing required identifiers
- Duplicate observation identifiers
- Availability of numeric or textual observation values
- Date parsing and invalid dates
- Observation periods where the end date precedes the start date

These checks improve consistency but do not independently verify the real-world accuracy of every source observation.

## Generated Outputs

| Output path | Description |
|---|---|
| `data/raw/observations.parquet` | Downloaded raw observations |
| `data/processed/observations_clean.parquet` | Validated and transformed observations |
| `data/processed/indicator_summary.csv` | Indicator-level summary statistics |
| `data/processed/dataset_summary.csv` | Dataset-level summary statistics |
| `logs/pipeline.log` | Pipeline execution logs |

Generated datasets and logs are excluded from source control where configured by `.gitignore`. Run the ingestion and pipeline commands to recreate the required local outputs.

## Getting Started

### Prerequisites

- Python 3.12 or later
- Git
- Internet access to retrieve the source dataset
- Docker Desktop, if using the containerized database setup

### 1. Clone the repository

```bash
git clone https://github.com/manish11111111/nepal-data-pipeline.git
cd nepal-data-pipeline
```

### 2. Create a virtual environment

**Windows PowerShell**

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

If PowerShell prevents environment activation, use the virtual environment's Python executable directly.

**macOS or Linux**

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install dependencies

```bash
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

## Running the Pipeline

### Download the source dataset

Run the ingestion module:

```bash
python -m src.ingest_data
```

If you intentionally want to replace the existing ingestion output, use the supported force option:

```bash
python -m src.ingest_data --force
```

Use this option carefully because it replaces the existing ingestion output.

### Run the complete data preparation workflow

```bash
python -m src.pipeline
```

If the raw input file is missing and you want the pipeline to download it automatically, run:

```bash
python -m src.pipeline --ingest
```

The `--ingest` option downloads the source when the selected raw input is missing. It does not force-refresh an existing raw file.

### Pipeline options

| Option | Purpose |
|---|---|
| `--ingest` | Download the source if the raw input is missing |
| `--input PATH` | Specify a custom input path |
| `--output PATH` | Specify a custom cleaned output path |
| `--no-summaries` | Skip summary generation |

For example, to run the pipeline without generating summary reports:

```bash
python -m src.pipeline --no-summaries
```

## Running with Docker

Docker Compose provides a PostgreSQL service and an optional pipeline container.

### 1. Configure environment variables

Create a `.env` file in the project root and configure the database password expected by the Compose configuration.

```env
POSTGRES_PASSWORD=replace_with_a_strong_local_password
```

Use a suitable local password. Never commit `.env` files or expose database credentials in source control.

### 2. Start PostgreSQL

```bash
docker compose up -d db
docker compose ps
```

Check that the database service has started and is healthy before attempting to load data.

### 3. Build the pipeline container

```bash
docker compose --profile pipeline build pipeline
```

### 4. Run the pipeline container

```bash
docker compose --profile pipeline run --rm pipeline
```

The containerized pipeline uses the configured environment and mounted project data directories.

Running the standard pipeline does not automatically load observations into PostgreSQL.

## Loading Data into PostgreSQL

PostgreSQL loading is separate from the default data preparation workflow.

First, generate the cleaned Parquet output and start the database service. Then run the loader:

```bash
docker compose --profile pipeline run --rm --no-deps --entrypoint python pipeline src/load_to_postgres.py
```

The loader reads the cleaned observations and writes them to the PostgreSQL `observations` table.

### Safe-loading behavior

The loader refuses to write into a target table that already contains records. This protects against accidental duplicate loading during initial setup.

If loading is refused because the target table already contains records, inspect the database state before deciding how to proceed. Do not drop or truncate a populated table simply to rerun the loader.

Incremental loading, upserts, and automatic synchronization of changed source records are not currently implemented.

### Database connection checks

The repository also includes a PostgreSQL connection-check module:

```bash
python -m src.check_postgres_connection
```

Use the connection settings defined by the project configuration and Docker Compose environment.

## Testing and Continuous Integration

### Run the test suite

```bash
python -m pytest -v
```

On Windows, you can also use the virtual environment's Python executable directly:

```powershell
.\.venv\Scripts\python.exe -m pytest
```

The automated tests cover important ingestion, validation, transformation, and loading behaviors, including failure handling and duplicate-loading protection.

### GitHub Actions

The repository uses GitHub Actions to run the test suite on pushes and pull requests targeting `main`, with Python 3.12 configured in the workflow.

- [GitHub repository](https://github.com/manish11111111/nepal-data-pipeline)
- [GitHub Actions](https://github.com/manish11111111/nepal-data-pipeline/actions)

The CI workflow checks the behavior covered by its automated test run. It does not, by itself, establish that the project has been tested on every Python version or deployment environment.

## Verified Results

The following results were recorded during local development verification:

| Metric | Result |
|---|---:|
| Raw observations processed | 27,182 |
| Cleaned observations | 27,182 |
| Cleaned dataset columns | 12 |
| Duplicate observation IDs | 0 |
| Invalid observation-period ranges | 0 |
| Rows missing both numeric and textual values | 0 |
| Indicator summary rows | 37 |
| Dataset summary rows | 4 |
| Automated tests passed | 25 |
| PostgreSQL observations verified | 27,182 |

These figures describe the tested dataset snapshot and local test run. Results may differ if the upstream dataset or project code changes.

## Engineering Decisions

| Decision | Rationale |
|---|---|
| Modular pipeline stages | Makes ingestion, transformation, and loading easier to test independently |
| Validation before processing | Detects structural and consistency issues before generating analytical outputs |
| Parquet storage | Provides a columnar format for structured observation data |
| Separate database loading | Keeps data preparation independent from database writes |
| Safe initial loading | Helps prevent accidental duplicate writes to a populated table |
| Automated testing | Detects regressions in important pipeline behaviors |
| Docker Compose | Simplifies local database setup |
| GitHub Actions | Automates testing when the repository changes |

## Limitations and Future Improvements

This project is a data engineering portfolio project, not a production-scale orchestration platform.

Potential future improvements include:

- Stronger schema contracts and explicit data type checks
- Dataset version tracking and ingestion timestamps
- Incremental loading and change detection
- Upsert-based database synchronization
- Expanded database integration testing
- Docker-based CI verification
- Data freshness monitoring and quality metrics
- A small sample dataset for easier local development
- Scheduled execution and workflow orchestration
- An interactive dashboard for exploring datasets and indicators

These items are future improvements and should not be interpreted as completed features.

## Data Attribution and Licensing

The source data is obtained from [DataNepal](https://datanepal.org/).

- [DataNepal website](https://datanepal.org/)
- [Public observations dataset](https://datanepal.org/data/observations.parquet)

Review the upstream dataset's applicable terms, attribution requirements, and licensing conditions before redistributing source data.

A repository-level licence should be added explicitly if the project is intended to be distributed under a particular open-source licence. Without a licence file, users should not assume that the project code has been released under an open-source licence.

## Author

**Manish Chapagain**

Computer Engineering graduate interested in data engineering, artificial intelligence, and data-driven applications.

- [GitHub](https://github.com/manish11111111)
- [LinkedIn](https://linkedin.com/in/manish-chapagain-467451284)
