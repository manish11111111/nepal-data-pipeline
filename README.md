# Nepal Data Pipeline

**Live Dashboard:** [nepal-data-pipeline.streamlit.app](https://nepal-data-pipeline.streamlit.app/)

A modular data engineering project for ingesting, validating, transforming, profiling, and analysing Nepal-related indicator observations. The pipeline produces structured analytical datasets, generates data quality reports, detects potential anomalies, and supports PostgreSQL integration. An interactive Streamlit dashboard makes the processed data and quality results accessible for exploration.

## Project Overview

This project demonstrates an end-to-end data processing workflow, from raw observations to cleaned datasets and analytical outputs. Its design separates ingestion, validation, transformation, anomaly detection, database loading, and presentation into distinct components.

The project focuses on data reliability, reproducible processing, automated testing, and the practical integration of data engineering with analytical applications.

## Key Features

- **Data ingestion:** Loads raw observations into the processing workflow.
- **Data validation:** Checks required columns, missing values, observation identifiers, date consistency, and other data integrity rules.
- **Data transformation:** Produces cleaned datasets and indicator-level and dataset-level summaries.
- **Data profiling:** Supports inspection and profiling of the available observations.
- **Data quality reporting:** Generates a structured report of data quality findings.
- **Anomaly detection:** Flags potentially unusual observations for further investigation.
- **PostgreSQL integration:** Supports loading processed observations with checks for duplicate loading and row-count consistency.
- **Interactive dashboard:** Provides dedicated pages for datasets, indicators, exploration, data quality, and project information.
- **Automated testing:** Uses pytest to verify processing logic, validation rules, output consistency, anomaly detection, and database-loading behaviour.
- **Deployment:** Makes the dashboard available through Streamlit Community Cloud.

## Live Dashboard

Explore the deployed application:

**[Open Nepal Data Pipeline](https://nepal-data-pipeline.streamlit.app/)**

The dashboard contains the following pages:

| Page | Description |
|---|---|
| Home | Introduces the project and provides an overview of the data. |
| Dataset | Presents dataset-level information and summaries. |
| Indicators | Provides indicator-level summary information. |
| Explore | Supports exploration of processed observations. |
| Quality | Presents data quality and anomaly-related information. |
| About | Provides project information. |

## Pipeline Workflow

The pipeline follows a modular sequence of processing stages:

1. **Ingestion:** Loads raw observations from the input dataset.
2. **Validation:** Evaluates data structure, required values, identifiers, and date consistency.
3. **Transformation:** Creates cleaned observations and analytical summaries.
4. **Profiling and quality analysis:** Supports data inspection and produces quality-related outputs.
5. **Anomaly detection:** Identifies observations that may warrant further investigation.
6. **Database integration:** Supports loading processed observations into PostgreSQL.
7. **Presentation:** Exposes processed data and summary information through the Streamlit dashboard.

This separation makes individual stages easier to test, maintain, and extend.

## Technology Stack

| Technology | Purpose |
|---|---|
| Python | Pipeline implementation |
| Pandas | Data processing and transformation |
| Parquet | Structured data storage |
| CSV | Analytical summary outputs |
| JSON | Structured data quality reporting |
| PostgreSQL | Relational database integration |
| Streamlit | Interactive dashboard |
| pytest | Automated testing |
| Docker Compose | Container orchestration configuration |
| Git and GitHub | Version control and repository hosting |
| Streamlit Community Cloud | Dashboard deployment |

## Verified Results

The following results were confirmed through local execution of the automated tests and anomaly detection module.

| Metric | Result |
|---|---:|
| Automated tests passed | 27 |
| Observations processed | 27,182 |
| Indicator summary records | 37 |
| Dataset summary records | 4 |
| Anomalies flagged | 1,370 |
| Observations not flagged | 25,812 |

All 27 automated tests passed in the recorded test run. The anomaly detection module scanned 27,182 observations and saved the results to `data/processed/anomalies.parquet`.

An anomaly flag indicates a potentially unusual observation according to the implemented detection method; it does not automatically mean that the observation is erroneous.

## Project Structure

```text
nepal-data-pipeline/
├── app.py
├── pages/
│   ├── 1_Dataset.py
│   ├── 2_Indicators.py
│   ├── 3_Explore.py
│   ├── 4_Quality.py
│   └── 5_About.py
├── src/
│   ├── anomaly_detection.py
│   ├── check_postgres_connection.py
│   ├── data_quality_report.py
│   ├── ingest_data.py
│   ├── inspect_data.py
│   ├── load_to_postgres.py
│   ├── pipeline.py
│   ├── profile_data.py
│   ├── transform_data.py
│   ├── ui.py
│   ├── utils.py
│   ├── validate_data.py
│   └── _init_.py
├── data/
│   ├── raw/
│   │   └── observations.parquet
│   └── processed/
│       ├── observations_clean.parquet
│       ├── anomalies.parquet
│       ├── indicator_summary.csv
│       ├── dataset_summary.csv
│       └── data_quality_report.json
├── logs/
│   └── pipeline.log
├── tests/
│   ├── test_anamoly_detection.py
│   ├── test_load_to_postgres.py
│   ├── test_pipeline.py
│   └── test_transform_data.py
└── docs/
```

## Data Outputs

| File | Purpose |
|---|---|
| `observations_clean.parquet` | Cleaned observations for downstream analysis |
| `anomalies.parquet` | Observations with anomaly detection results |
| `indicator_summary.csv` | Indicator-level analytical summaries |
| `dataset_summary.csv` | Dataset-level summaries |
| `data_quality_report.json` | Structured data quality findings |

The raw dataset is stored separately from the processed outputs, supporting a clear distinction between input data and derived results.

## Getting Started

### Prerequisites

- Python
- Git
- Project dependencies listed in `requirements.txt`
- PostgreSQL, when running database integration

### 1. Clone the repository

```bash
git clone https://github.com/manish11111111/nepal-data-pipeline.git
cd nepal-data-pipeline
```

### 2. Create a virtual environment

```bash
python -m venv .venv
```

On Windows PowerShell, activate it with:

```powershell
.\.venv\Scripts\Activate.ps1
```

### 3. Install dependencies

```bash
python -m pip install -r requirements.txt
```

### 4. Run the dashboard

```bash
streamlit run app.py
```

Streamlit will display a local URL where the dashboard can be opened in a browser.

## Running Pipeline Components

Run anomaly detection from the repository root:

```bash
python -m src.anomaly_detection
```

The module scans the processed observations and writes its results to `data/processed/anomalies.parquet`.

The remaining pipeline components are organised under `src/`, including ingestion, validation, transformation, profiling, quality reporting, and PostgreSQL integration.

## Running Tests

Run the test suite from the repository root:

```bash
python -m pytest -v
```

The verified test run completed with **27 passed**. Coverage includes validation rules, missing and invalid input handling, duplicate identifiers, date consistency, transformation outputs, summary consistency, anomaly detection, and PostgreSQL loading behaviour.

## Engineering Considerations

The project emphasises modular processing, data integrity, automated verification, and separation between processing logic and presentation. Validation rules help identify structural and consistency issues before downstream use. Summary outputs support analysis at both indicator and dataset levels, while anomaly detection highlights records for closer examination.

PostgreSQL integration adds a relational storage component, and automated tests help verify expected behaviour across key processing stages.

## Scope and Limitations

- The deployed dashboard is intended for data exploration and reporting rather than editing the underlying dataset.
- Anomaly detection identifies potentially unusual observations; flagged records require interpretation in context.
- The reported test results and processing counts reflect the verified local execution.
- PostgreSQL functionality requires an appropriately configured database environment.

## Author

**Manish Chapagain**

Computer Engineering graduate with interests in data engineering, data quality, analytical systems, and artificial intelligence.

- **GitHub:** [manish11111111](https://github.com/manish11111111)
- **Live Dashboard:** [Nepal Data Pipeline](https://nepal-data-pipeline.streamlit.app/)