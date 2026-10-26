
from pathlib import Path

import pandas as pd
import streamlit as st


PROJECT_ROOT = Path(__file__).resolve().parent
DATA_PATH = PROJECT_ROOT / "data" / "processed" / "observations_clean.parquet"
SOURCE_URL = "https://datanepal.org/data/observations.parquet"

st.set_page_config(
    page_title="Nepal Public Data Explorer",
    page_icon="🇳🇵",
    layout="wide",
    initial_sidebar_state="expanded",
)


@st.cache_data
def load_data():
    if not DATA_PATH.exists():
        raise FileNotFoundError(
            "Processed data was not found. Run "
            "'.venv\\Scripts\\python.exe -m src.pipeline' first."
        )

    df = pd.read_parquet(DATA_PATH)

    for column in df.columns:
        if any(word in column.lower() for word in ("date", "time")):
            try:
                df[column] = pd.to_datetime(df[column], errors="ignore")
            except (TypeError, ValueError):
                pass

    return df


def find_column(df, candidates):
    lookup = {column.lower(): column for column in df.columns}

    for candidate in candidates:
        if candidate in lookup:
            return lookup[candidate]

    for column in df.columns:
        lowered = column.lower()
        if any(candidate in lowered for candidate in candidates):
            return column

    return None


def unique_count(df, column):
    if column is None or column not in df.columns:
        return None
    return int(df[column].nunique(dropna=True))


def display_value(value):
    if value is None:
        return "N/A"
    return f"{value:,}"


st.title("🇳🇵 Nepal Public Data Explorer")
st.caption(
    "Explore public observations through a reproducible data pipeline "
    "built with Python, pandas, Parquet and PostgreSQL."
)

try:
    data = load_data()
except Exception as exc:
    st.error(f"Unable to load the processed dataset: {exc}")
    st.info(
        "From the project root, run: "
        "`.venv\\Scripts\\python.exe -m src.pipeline`"
    )
    st.stop()

if data.empty:
    st.warning("The processed dataset contains no observations.")
    st.stop()

df = data.copy()

dataset_col = find_column(df, ["dataset_name", "dataset", "source_name"])
indicator_col = find_column(df, ["indicator_name", "indicator", "indicator_id"])
place_col = find_column(df, ["place_name", "location_name", "place", "location"])
status_col = find_column(df, ["status", "observation_status"])
date_col = find_column(df, ["observation_date", "date", "period", "year"])
value_col = find_column(df, ["value_numeric", "numeric_value", "value"])

with st.sidebar:
    st.header("Explore the data")
    st.caption(f"Available records: {len(df):,}")

    pages = [
        "Overview",
        "Data Explorer",
        "Data Quality",
        "About the Pipeline",
    ]
    page = st.radio("Navigate", pages)

    filtered = df.copy()

    if dataset_col:
        options = sorted(
            filtered[dataset_col].dropna().astype(str).unique().tolist()
        )
        selected = st.multiselect("Dataset", options, default=options)
        filtered = filtered[
            filtered[dataset_col].astype(str).isin(selected)
        ]

    if status_col:
        options = sorted(
            filtered[status_col].dropna().astype(str).unique().tolist()
        )
        selected = st.multiselect("Status", options, default=options)
        filtered = filtered[
            filtered[status_col].astype(str).isin(selected)
        ]

    if indicator_col:
        options = sorted(
            filtered[indicator_col].dropna().astype(str).unique().tolist()
        )
        selected = st.multiselect(
            "Indicator",
            options,
            default=[],
            help="Leave empty to include every indicator.",
        )
        if selected:
            filtered = filtered[
                filtered[indicator_col].astype(str).isin(selected)
            ]

st.caption(f"Showing {len(filtered):,} of {len(df):,} observations")

if page == "Overview":
    st.subheader("National data overview")

    col1, col2, col3, col4 = st.columns(4)

    col1.metric("Observations", f"{len(filtered):,}")
    col2.metric("Datasets", display_value(unique_count(filtered, dataset_col)))
    col3.metric(
        "Indicators",
        display_value(unique_count(filtered, indicator_col)),
    )
    col4.metric("Places", display_value(unique_count(filtered, place_col)))

    st.divider()
    st.subheader("Dataset distribution")

    left, right = st.columns(2)

    with left:
        if dataset_col and not filtered.empty:
            counts = (
                filtered[dataset_col]
                .fillna("Unknown")
                .astype(str)
                .value_counts()
                .rename_axis("Dataset")
                .rename("Observations")
            )
            st.bar_chart(counts)
        else:
            st.info("No dataset column was detected.")

    with right:
        if status_col and not filtered.empty:
            counts = (
                filtered[status_col]
                .fillna("Unknown")
                .astype(str)
                .value_counts()
                .rename_axis("Status")
                .rename("Observations")
            )
            st.bar_chart(counts)
        elif value_col and not filtered.empty:
            values = pd.to_numeric(filtered[value_col], errors="coerce")
            st.metric("Numeric values available", f"{values.notna().sum():,}")
            st.caption("Count of observations with a parseable numeric value.")
        else:
            st.info("No status or numeric value column was detected.")

    if date_col and not filtered.empty:
        st.subheader("Observations over time")
        dates = pd.to_datetime(filtered[date_col], errors="coerce")
        time_data = pd.DataFrame({"Date": dates}).dropna()

        if not time_data.empty:
            time_data["Period"] = time_data["Date"].dt.to_period("Y").astype(str)
            yearly = time_data.groupby("Period").size()
            st.bar_chart(yearly)
        else:
            st.info("The detected date column has no parseable dates.")

    st.subheader("Preview")
    st.dataframe(filtered.head(10), use_container_width=True, hide_index=True)

elif page == "Data Explorer":
    st.subheader("Search and inspect observations")

    search = st.text_input(
        "Search all text columns",
        placeholder="Enter a dataset, indicator, place, or keyword...",
    )

    result = filtered.copy()

    if search.strip():
        text_columns = result.select_dtypes(
            include=["object", "string", "category"]
        ).columns

        if len(text_columns):
            mask = result[text_columns].astype(str).apply(
                lambda column: column.str.contains(
                    search.strip(),
                    case=False,
                    na=False,
                    regex=False,
                )
            ).any(axis=1)
            result = result[mask]
        else:
            result = result.iloc[0:0]

    st.write(f"**{len(result):,}** matching observations")
    st.dataframe(result, use_container_width=True, hide_index=True)

    csv_data = result.to_csv(index=False).encode("utf-8")
    st.download_button(
        "Download filtered data as CSV",
        data=csv_data,
        file_name="nepal_observations.csv",
        mime="text/csv",
    )

elif page == "Data Quality":
    st.subheader("Data quality checks")
    st.caption("These checks describe the processed file; they do not replace the pipeline's validation rules.")

    total_rows = len(df)
    total_columns = len(df.columns)

    c1, c2, c3 = st.columns(3)
    c1.metric("Rows", f"{total_rows:,}")
    c2.metric("Columns", f"{total_columns:,}")
    c3.metric("Missing cells", f"{int(df.isna().sum().sum()):,}")

    quality_rows = []

    for column in df.columns:
        missing = int(df[column].isna().sum())
        quality_rows.append(
            {
                "Column": column,
                "Data type": str(df[column].dtype),
                "Missing values": missing,
                "Missing (%)": round(
                    missing / total_rows * 100, 2
                ) if total_rows else 0,
                "Unique values": int(df[column].nunique(dropna=True)),
            }
        )

    st.subheader("Column-level quality")
    quality = pd.DataFrame(quality_rows)
    st.dataframe(quality, use_container_width=True, hide_index=True)

    if "observation_id" in df.columns:
        duplicates = int(df["observation_id"].duplicated().sum())
        st.metric("Duplicate observation IDs", f"{duplicates:,}")
    else:
        st.info("No observation_id column was detected for duplicate checking.")

    if value_col:
        numeric = pd.to_numeric(df[value_col], errors="coerce")
        st.metric("Values not parseable as numbers", f"{int(numeric.isna().sum()):,}")
    else:
        st.info("No numeric value column was detected.")

    if date_col:
        parsed_dates = pd.to_datetime(df[date_col], errors="coerce")
        valid_dates = parsed_dates.dropna()

        if not valid_dates.empty:
            left, right = st.columns(2)
            left.metric("Earliest date", valid_dates.min().strftime("%Y-%m-%d"))
            right.metric("Latest date", valid_dates.max().strftime("%Y-%m-%d"))

        st.metric("Unparseable or missing dates", f"{int(parsed_dates.isna().sum()):,}")

elif page == "About the Pipeline":
    st.subheader("How the pipeline works")

    st.markdown(
        """
        This project turns public observations into structured data that
        can be explored and queried.

        **1. Ingestion**  
        Retrieves the upstream observations dataset.

        **2. Validation**  
        Checks the structure and consistency of the incoming data.

        **3. Transformation**  
        Produces cleaned Parquet data and summary reports.

        **4. Storage**  
        Uses Parquet for analytical files and PostgreSQL for relational
        persistence when the database-loading step is run.

        **5. Exploration**  
        This dashboard provides interactive views of the processed
        observations and basic data-quality checks.
        """
    )

    st.markdown("**Technologies**")
    st.write("Python · pandas · Parquet · PostgreSQL · pytest · Streamlit")

    st.markdown(f"**Upstream source:** [DataNepal observations dataset]({SOURCE_URL})")

    st.warning(
        "The dashboard reads the local processed Parquet file. "
        "It does not automatically ingest new data or write to PostgreSQL."
    )

st.divider()
st.caption("Nepal Public Data Explorer · Built with Streamlit")
