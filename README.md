
# Nepal Public Data Engineering Pipeline

A reproducible data engineering project that ingests, validates, transforms, and stores public datasets about Nepal. The pipeline uses Python and Pandas for data processing, Parquet for analytical storage, PostgreSQL for structured data storage, Docker for environment setup, and pytest for automated testing.

The project demonstrates practical data engineering concepts, including data ingestion, schema validation, data quality checks, transformation, aggregation, database loading, logging, and pipeline orchestration.

## Project Objectives

- Ingest public data related to Nepal from a published Parquet dataset.
- Validate schemas, identifiers, values, and observation periods.
- Transform raw observations into a cleaned analytical dataset.
- Generate indicator-level and dataset-level summary reports.
- Load processed observations into PostgreSQL.
- Automate pipeline execution and verify functionality through tests.
- Provide a reproducible development environment using Docker.

## Architecture

```text
Public Nepal Dataset
        |
        v
   Data Ingestion
        |
        v
     Raw Parquet
        |
        v
  Data Validation
        |
        v
  Data Transformation
        |
        +----------------------+
        |                      |
        v                      v
 Cleaned Parquet        Summary Reports
        |               - Indicator summary
        |               - Dataset summary
        v
   PostgreSQL
        |
        v
  Analytical Queries
```

The pipeline is orchestrated through `src/pipeline.py`. PostgreSQL loading is available as a separate step so that data processing and database operations can be managed independently.

## Technology Stack

| Technology | Purpose |
|---|---|
| Python | Pipeline orchestration and data processing |
| Pandas | Data cleaning, validation support, and aggregation |
| PyArrow | Parquet file processing |
| PostgreSQL | Relational data storage |
| Docker Compose | Local database and container orchestration |
| pytest | Automated testing |
| GitHub Actions | Continuous integration |
| Git | Version control |

## Repository Structure

```text
nepal-data-pipeline/
├── data/
│   ├── raw/
│   └── processed/
├── logs/
├── src/
│   ├── check_postgres_connection.py
│   ├── data_quality_report.py
│   ├── ingest_data.py
│   ├── inspect_data.py
│   ├── load_to_postgres.py
│   ├── pipeline.py
│   ├── profile_data.py
│   ├── transform_data.py
│   └── validate_data.py
├── tests/
├── .github/
│   └── workflows/
├── docker-compose.yml
├── Dockerfile
├── requirements.txt
├── .gitignore
└── README.md
```

Generated data files and local environment files are excluded from version control where configured in `.gitignore`.

## Data Source

The pipeline uses the published DataNepal observations dataset:

- Source: https://datanepal.org/data/observations.parquet
- Format: Apache Parquet
- Content: Structured observations from multiple datasets related to Nepal

The dataset contains observations from sources represented by identifiers such as:

- `nso-nphc-2021`
- `cod-ps-npl`
- `worldbank-npl`
- `ecn-hor-2026`

The pipeline validates the downloaded dataset before accepting it as a raw input. Existing raw data is not overwritten unless the ingestion script is explicitly instructed to do so.

## Dataset Snapshot

The following figures are from the locally verified dataset used during development.

| Metric | Result |
|---|---:|
| Total observations | 27,182 |
| Columns | 12 |
| Unique indicators | 36 |
| Unique places | 838 |
| Duplicate observation IDs | 0 |
| Duplicate rows | 0 |

### Observations by dataset

| Dataset ID | Observations |
|---|---:|
| `nso-nphc-2021` | 21,258 |
| `cod-ps-npl` | 4,590 |
| `worldbank-npl` | 1,213 |
| `ecn-hor-2026` | 121 |
| **Total** | **27,182** |

These are development-time results, not guaranteed permanent counts. The upstream dataset may change.

## Getting Started

### Prerequisites

Install the following tools:

- Python 3.12 or another compatible Python version
- Git
- Docker Desktop, if you want to run PostgreSQL through Docker
- PowerShell on Windows, or an equivalent terminal

### 1. Clone the repository

```powershell
git clone https://github.com/manish11111111/nepal-data-pipeline.git
cd nepal-data-pipeline
```

### 2. Create a virtual environment

On Windows PowerShell:

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
```

If Python 3.12 is unavailable, use an installed compatible Python version.

### 3. Install dependencies

```powershell
python -m pip install --upgrade pip
pip install -r requirements.txt
```

## Running the Pipeline

### Run the default pipeline

```powershell
python .\src\pipeline.py
```

The pipeline uses the project's default raw and processed data paths. If the default raw dataset is missing, use the ingestion option to download it automatically.

```powershell
python .\src\pipeline.py --ingest
```

### Run with a custom input and output path

The pipeline accepts optional input and output paths. This allows you to validate and process a separate dataset without overwriting the default cleaned dataset.

```powershell
python .\src\pipeline.py `
  --input .\data\raw\observations_e2e_test.parquet `
  --output .\data\processed\e2e_test\observations_clean.parquet
```

When summary generation is enabled, the indicator and dataset summary CSV files are written to the same directory as the specified output Parquet file.

To skip summary generation:

```powershell
python .\src\pipeline.py `
  --input .\data\raw\observations_e2e_test.parquet `
  --output .\data\processed\e2e_test\observations_clean.parquet `
  --no-summaries
```

If `--input` or `--output` is omitted, the pipeline uses the corresponding default project path. The `--ingest` option downloads data when the selected input path does not exist.

### Pipeline stages

The orchestrated workflow performs the following operations:

1. Reads the selected raw Parquet dataset.
2. Validates the required schema and observation records.
3. Checks identifiers, missing values, and observation periods.
4. Converts date fields into appropriate datetime types.
5. Writes the cleaned Parquet dataset.
6. Generates indicator-level and dataset-level summary reports, unless disabled.
7. Logs pipeline progress and completion.

## Data Validation

The validation logic checks important data integrity conditions, including:

- Required columns are present.
- Observation and dataset identifiers are populated.
- Required status and period fields are available.
- Observation IDs are unique.
- Each record contains a numeric or textual value.
- Observation dates can be parsed.
- Observation end dates are not earlier than their start dates.

The ingestion stage also checks the downloaded dataset before replacing the target raw file.

These checks help detect malformed or inconsistent data before it proceeds through the pipeline.

## Data Transformation

The transformation module generates aggregated CSV reports from the cleaned observations.

### Indicator summary

The indicator summary groups observations by dataset, indicator, and unit. It provides a compact view of the available indicators and their associated data.

### Dataset summary

The dataset summary groups observations by dataset, status, and period type. It provides a high-level view of the records available from each source.

### Generated outputs

```text
data/processed/
├── observations_clean.parquet
├── indicator_summary.csv
├── dataset_summary.csv
├── data_quality_report.json
└── dataset_summary.csv
```

The files shown represent the types of processed artifacts generated or maintained by the project. Exact outputs depend on which scripts have been executed and the selected output directory.

## Data Quality and Profiling

The repository includes scripts for inspecting, profiling, validating, and reporting on the data:

```powershell
python .\src\inspect_data.py
python .\src\profile_data.py
python .\src\validate_data.py
python .\src\data_quality_report.py
```

These scripts support inspection of the source data, validation of data assumptions, and production of data quality information.

Run each script from the repository root. Its precise inputs and outputs depend on the paths configured in the script.

## PostgreSQL Setup with Docker

PostgreSQL can be started locally using Docker Compose.

### 1. Configure environment variables

Create a local `.env` file containing the database credentials expected by your Compose configuration. For example:

```dotenv
POSTGRES_DB=nepal_data
POSTGRES_USER=postgres
POSTGRES_PASSWORD=replace_with_a_local_password
```

Use the variable names expected by your actual `docker-compose.yml` and application configuration. Keep real credentials private and never commit `.env` to Git.

### 2. Start PostgreSQL

```powershell
docker compose up -d db
```

The local PostgreSQL service is configured to use host port `5433`, mapped to container port `5432`.

### 3. Check the connection

```powershell
python .\src\check_postgres_connection.py
```

Ensure your local environment variables and database connection settings match the Compose configuration.

### 4. Load the processed data

```powershell
python .\src\load_to_postgres.py
```

**Important:** The loader checks whether the destination `observations` table already contains records and refuses to load if it is populated. This prevents accidental duplicate loading. Inspect the database and the loader's behavior before attempting another load.

Do not remove the PostgreSQL Docker volume to resolve a loading issue; doing so can delete stored database data.

### 5. Run the containerized pipeline

The pipeline service is configured behind the `pipeline` Compose profile:

```powershell
docker compose --profile pipeline run --rm pipeline
```

This command runs the pipeline service using the default paths available inside its container. Ensure the required raw data is available through the configured volumes or that ingestion is configured appropriately for your environment.

## Automated Testing

The project uses `pytest` to verify data validation and pipeline behavior.

Run the test suite:

```powershell
python -m pytest -v
```

Compile the main pipeline modules:

```powershell
python -m py_compile .\src\pipeline.py
python -m py_compile .\src\ingest_data.py
python -m py_compile .\src\transform_data.py
```

The tests cover validation behavior and pipeline scenarios, including missing raw files, ingestion behavior, and skipping summary generation.

### Verified local results

The following results were observed during local development:

- **19 automated tests passed** before the latest custom-path changes were fully documented.
- End-to-end pipeline execution completed successfully using a separate test input and output directory.
- Cleaned dataset contained 27,182 rows and 12 columns.
- Indicator summary contained 37 rows.
- Dataset summary contained 4 rows.
- All 27,182 observation IDs were unique.
- Duplicate observation IDs: 0.

Test counts can change as new regression tests are added. Run the test suite to obtain the current result for your checkout.

## Logging

Pipeline progress and errors are recorded in the project log directory.

```text
logs/
└── pipeline.log
```

Logs help trace ingestion, validation, transformation, output creation, and pipeline completion.

## Continuous Integration

GitHub Actions is configured to run automated tests using Python 3.12.

The CI workflow helps catch regressions and verify that the test suite runs in a clean environment. Check the repository's Actions tab for the latest workflow status:

https://github.com/manish11111111/nepal-data-pipeline/actions

## Design Considerations

Several implementation choices are intended to improve reliability:

- **Validation before processing:** Invalid records are detected before downstream transformations.
- **Safe ingestion:** Downloaded data is validated before replacing the target raw file.
- **Separate stages:** Ingestion, validation, transformation, and database loading have distinct responsibilities.
- **Reproducible environment:** Dependencies and container configuration are version-controlled.
- **Automated tests:** Core behavior is checked through repeatable test cases.
- **Database safeguards:** The loader avoids silently loading into an already populated observations table.
- **Configurable paths:** The orchestrator supports custom input and output paths for isolated processing and testing.

## Future Improvements

Potential next steps include:

- Add stronger schema contracts and explicit data type checks.
- Add configurable retry and timeout policies for ingestion.
- Track source dataset versions and ingestion timestamps.
- Improve incremental ingestion and change detection.
- Add more database integration tests.
- Add data freshness and quality metrics.
- Expand CI to test the Dockerized workflow.
- Add reproducible sample data and a documented end-to-end demonstration.
- Explore orchestration tools and scheduling for larger workflows.
- Add a dashboard for exploring indicators and datasets.

## Limitations

- The pipeline depends on the availability and structure of the upstream dataset.
- Summary counts may change when the source data changes.
- The current database loader is intentionally cautious about loading into a populated table.
- Local execution, Docker execution, and CI execution can differ depending on configuration and environment.
- The project is a portfolio and learning project, not an official Nepal government data service.

## License and Data Attribution

This repository uses a public dataset published by DataNepal. Review the upstream dataset's license and terms before redistributing the data.

Unless a license file is present in this repository, do not assume that the project code or source data has a particular open-source license. Add an explicit `LICENSE` file if you intend to publish the code under a specific license.

## Author

**Manish Chapagain**

Computer Engineering graduate interested in data engineering, artificial intelligence, and data-driven applications.

- GitHub: https://github.com/manish11111111
- Project repository: https://github.com/manish11111111/nepal-data-pipeline

# Nepal Public Data Engineering Pipeline

A reproducible data engineering project that ingests, validates, transforms, and stores public datasets about Nepal. The pipeline uses Python and Pandas for data processing, Parquet for analytical storage, PostgreSQL for structured data storage, Docker for environment setup, and pytest for automated testing.

The project demonstrates practical data engineering concepts, including data ingestion, schema validation, data quality checks, transformation, aggregation, database loading, logging, and pipeline orchestration.

## Project Objectives

- Ingest public data related to Nepal from a published Parquet dataset.
- Validate schemas, identifiers, values, and observation periods.
- Transform raw observations into a cleaned analytical dataset.
- Generate indicator-level and dataset-level summary reports.
- Load processed observations into PostgreSQL.
- Automate pipeline execution and verify functionality through tests.
- Provide a reproducible development environment using Docker.

## Architecture

```text
Public Nepal Dataset
        |
        v
   Data Ingestion
        |
        v
     Raw Parquet
        |
        v
  Data Validation
        |
        v
  Data Transformation
        |
        +----------------------+
        |                      |
        v                      v
 Cleaned Parquet        Summary Reports
        |               - Indicator summary
        |               - Dataset summary
        v
   PostgreSQL
        |
        v
  Analytical Queries
```

The pipeline is orchestrated through `src/pipeline.py`. PostgreSQL loading is available as a separate step so that data processing and database operations can be managed independently.

## Technology Stack

| Technology | Purpose |
|---|---|
| Python | Pipeline orchestration and data processing |
| Pandas | Data cleaning, validation support, and aggregation |
| PyArrow | Parquet file processing |
| PostgreSQL | Relational data storage |
| Docker Compose | Local database and container orchestration |
| pytest | Automated testing |
| GitHub Actions | Continuous integration |
| Git | Version control |

## Repository Structure

```text
nepal-data-pipeline/
├── data/
│   ├── raw/
│   └── processed/
├── logs/
├── src/
│   ├── check_postgres_connection.py
│   ├── data_quality_report.py
│   ├── ingest_data.py
│   ├── inspect_data.py
│   ├── load_to_postgres.py
│   ├── pipeline.py
│   ├── profile_data.py
│   ├── transform_data.py
│   └── validate_data.py
├── tests/
├── .github/
│   └── workflows/
├── docker-compose.yml
├── Dockerfile
├── requirements.txt
├── .gitignore
└── README.md
```

Generated data files and local environment files are excluded from version control where configured in `.gitignore`.

## Data Source

The pipeline uses the published DataNepal observations dataset:

- Source: https://datanepal.org/data/observations.parquet
- Format: Apache Parquet
- Content: Structured observations from multiple datasets related to Nepal

The dataset contains observations from sources represented by identifiers such as:

- `nso-nphc-2021`
- `cod-ps-npl`
- `worldbank-npl`
- `ecn-hor-2026`

The pipeline validates the downloaded dataset before accepting it as a raw input. Existing raw data is not overwritten unless the ingestion script is explicitly instructed to do so.

## Dataset Snapshot

The following figures are from the locally verified dataset used during development.

| Metric | Result |
|---|---:|
| Total observations | 27,182 |
| Columns | 12 |
| Unique indicators | 36 |
| Unique places | 838 |
| Duplicate observation IDs | 0 |
| Duplicate rows | 0 |

### Observations by dataset

| Dataset ID | Observations |
|---|---:|
| `nso-nphc-2021` | 21,258 |
| `cod-ps-npl` | 4,590 |
| `worldbank-npl` | 1,213 |
| `ecn-hor-2026` | 121 |
| **Total** | **27,182** |

These are development-time results, not guaranteed permanent counts. The upstream dataset may change.

## Getting Started

### Prerequisites

Install the following tools:

- Python 3.12 or another compatible Python version
- Git
- Docker Desktop, if you want to run PostgreSQL through Docker
- PowerShell on Windows, or an equivalent terminal

### 1. Clone the repository

```powershell
git clone https://github.com/manish11111111/nepal-data-pipeline.git
cd nepal-data-pipeline
```

### 2. Create a virtual environment

On Windows PowerShell:

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
```

If Python 3.12 is unavailable, use an installed compatible Python version.

### 3. Install dependencies

```powershell
python -m pip install --upgrade pip
pip install -r requirements.txt
```

## Running the Pipeline

### Run the default pipeline

```powershell
python .\src\pipeline.py
```

The pipeline uses the project's default raw and processed data paths. If the default raw dataset is missing, use the ingestion option to download it automatically.

```powershell
python .\src\pipeline.py --ingest
```

### Run with a custom input and output path

The pipeline accepts optional input and output paths. This allows you to validate and process a separate dataset without overwriting the default cleaned dataset.

```powershell
python .\src\pipeline.py `
  --input .\data\raw\observations_e2e_test.parquet `
  --output .\data\processed\e2e_test\observations_clean.parquet
```

When summary generation is enabled, the indicator and dataset summary CSV files are written to the same directory as the specified output Parquet file.

To skip summary generation:

```powershell
python .\src\pipeline.py `
  --input .\data\raw\observations_e2e_test.parquet `
  --output .\data\processed\e2e_test\observations_clean.parquet `
  --no-summaries
```

If `--input` or `--output` is omitted, the pipeline uses the corresponding default project path. The `--ingest` option downloads data when the selected input path does not exist.

### Pipeline stages

The orchestrated workflow performs the following operations:

1. Reads the selected raw Parquet dataset.
2. Validates the required schema and observation records.
3. Checks identifiers, missing values, and observation periods.
4. Converts date fields into appropriate datetime types.
5. Writes the cleaned Parquet dataset.
6. Generates indicator-level and dataset-level summary reports, unless disabled.
7. Logs pipeline progress and completion.

## Data Validation

The validation logic checks important data integrity conditions, including:

- Required columns are present.
- Observation and dataset identifiers are populated.
- Required status and period fields are available.
- Observation IDs are unique.
- Each record contains a numeric or textual value.
- Observation dates can be parsed.
- Observation end dates are not earlier than their start dates.

The ingestion stage also checks the downloaded dataset before replacing the target raw file.

These checks help detect malformed or inconsistent data before it proceeds through the pipeline.

## Data Transformation

The transformation module generates aggregated CSV reports from the cleaned observations.

### Indicator summary

The indicator summary groups observations by dataset, indicator, and unit. It provides a compact view of the available indicators and their associated data.

### Dataset summary

The dataset summary groups observations by dataset, status, and period type. It provides a high-level view of the records available from each source.

### Generated outputs

```text
data/processed/
├── observations_clean.parquet
├── indicator_summary.csv
├── dataset_summary.csv
├── data_quality_report.json
└── dataset_summary.csv
```

The files shown represent the types of processed artifacts generated or maintained by the project. Exact outputs depend on which scripts have been executed and the selected output directory.

## Data Quality and Profiling

The repository includes scripts for inspecting, profiling, validating, and reporting on the data:

```powershell
python .\src\inspect_data.py
python .\src\profile_data.py
python .\src\validate_data.py
python .\src\data_quality_report.py
```

These scripts support inspection of the source data, validation of data assumptions, and production of data quality information.

Run each script from the repository root. Its precise inputs and outputs depend on the paths configured in the script.

## PostgreSQL Setup with Docker

PostgreSQL can be started locally using Docker Compose.

### 1. Configure environment variables

Create a local `.env` file containing the database credentials expected by your Compose configuration. For example:

```dotenv
POSTGRES_DB=nepal_data
POSTGRES_USER=postgres
POSTGRES_PASSWORD=replace_with_a_local_password
```

Use the variable names expected by your actual `docker-compose.yml` and application configuration. Keep real credentials private and never commit `.env` to Git.

### 2. Start PostgreSQL

```powershell
docker compose up -d db
```

The local PostgreSQL service is configured to use host port `5433`, mapped to container port `5432`.

### 3. Check the connection

```powershell
python .\src\check_postgres_connection.py
```

Ensure your local environment variables and database connection settings match the Compose configuration.

### 4. Load the processed data

```powershell
python .\src\load_to_postgres.py
```

**Important:** The loader checks whether the destination `observations` table already contains records and refuses to load if it is populated. This prevents accidental duplicate loading. Inspect the database and the loader's behavior before attempting another load.

Do not remove the PostgreSQL Docker volume to resolve a loading issue; doing so can delete stored database data.

### 5. Run the containerized pipeline

The pipeline service is configured behind the `pipeline` Compose profile:

```powershell
docker compose --profile pipeline run --rm pipeline
```

This command runs the pipeline service using the default paths available inside its container. Ensure the required raw data is available through the configured volumes or that ingestion is configured appropriately for your environment.

## Automated Testing

The project uses `pytest` to verify data validation and pipeline behavior.

Run the test suite:

```powershell
python -m pytest -v
```

Compile the main pipeline modules:

```powershell
python -m py_compile .\src\pipeline.py
python -m py_compile .\src\ingest_data.py
python -m py_compile .\src\transform_data.py
```

The tests cover validation behavior and pipeline scenarios, including missing raw files, ingestion behavior, and skipping summary generation.

### Verified local results

The following results were observed during local development:

- **19 automated tests passed** before the latest custom-path changes were fully documented.
- End-to-end pipeline execution completed successfully using a separate test input and output directory.
- Cleaned dataset contained 27,182 rows and 12 columns.
- Indicator summary contained 37 rows.
- Dataset summary contained 4 rows.
- All 27,182 observation IDs were unique.
- Duplicate observation IDs: 0.

Test counts can change as new regression tests are added. Run the test suite to obtain the current result for your checkout.

## Logging

Pipeline progress and errors are recorded in the project log directory.

```text
logs/
└── pipeline.log
```

Logs help trace ingestion, validation, transformation, output creation, and pipeline completion.

## Continuous Integration

GitHub Actions is configured to run automated tests using Python 3.12.

The CI workflow helps catch regressions and verify that the test suite runs in a clean environment. Check the repository's Actions tab for the latest workflow status:

https://github.com/manish11111111/nepal-data-pipeline/actions

## Design Considerations

Several implementation choices are intended to improve reliability:

- **Validation before processing:** Invalid records are detected before downstream transformations.
- **Safe ingestion:** Downloaded data is validated before replacing the target raw file.
- **Separate stages:** Ingestion, validation, transformation, and database loading have distinct responsibilities.
- **Reproducible environment:** Dependencies and container configuration are version-controlled.
- **Automated tests:** Core behavior is checked through repeatable test cases.
- **Database safeguards:** The loader avoids silently loading into an already populated observations table.
- **Configurable paths:** The orchestrator supports custom input and output paths for isolated processing and testing.

## Future Improvements

Potential next steps include:

- Add stronger schema contracts and explicit data type checks.
- Add configurable retry and timeout policies for ingestion.
- Track source dataset versions and ingestion timestamps.
- Improve incremental ingestion and change detection.
- Add more database integration tests.
- Add data freshness and quality metrics.
- Expand CI to test the Dockerized workflow.
- Add reproducible sample data and a documented end-to-end demonstration.
- Explore orchestration tools and scheduling for larger workflows.
- Add a dashboard for exploring indicators and datasets.

## Limitations

- The pipeline depends on the availability and structure of the upstream dataset.
- Summary counts may change when the source data changes.
- The current database loader is intentionally cautious about loading into a populated table.
- Local execution, Docker execution, and CI execution can differ depending on configuration and environment.
- The project is a portfolio and learning project, not an official Nepal government data service.

## License and Data Attribution

This repository uses a public dataset published by DataNepal. Review the upstream dataset's license and terms before redistributing the data.

Unless a license file is present in this repository, do not assume that the project code or source data has a particular open-source license. Add an explicit `LICENSE` file if you intend to publish the code under a specific license.

## Author

**Manish Chapagain**

Computer Engineering graduate interested in data engineering, artificial intelligence, and data-driven applications.

- GitHub: https://github.com/manish11111111
- Project repository: https://github.com/manish11111111/nepal-data-pipeline
