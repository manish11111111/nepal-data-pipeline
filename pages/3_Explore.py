"""Observation explorer. Designed and built by Manish Chapagain."""

from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st

from src.ui import (
    apply_theme,
    chart_layout,
    footer,
    page_header,
    sidebar_brand,
    sidebar_footer,
    sidebar_status,
)


PROJECT_ROOT = Path(__file__).resolve().parent.parent
CLEAN_PATH = PROJECT_ROOT / "data" / "processed" / "observations_clean.parquet"

st.set_page_config(page_title="Explore · Nepal Pipeline", page_icon="🔍", layout="wide")
apply_theme()


@st.cache_data
def load():
    return pd.read_parquet(CLEAN_PATH)


sidebar_brand()
sidebar_status([("Cleaned dataset", CLEAN_PATH)])
sidebar_footer()

page_header(
    "Exploration · Observations",
    "Explore observations",
    "Filter, inspect, and download cleaned observations.",
)

if not CLEAN_PATH.exists():
    st.error("Cleaned dataset not found. Run `python -m src.pipeline`.")
    st.stop()

df = load()

a, b = st.columns(2)
with a:
    dataset_choices = sorted(df["dataset_id"].dropna().unique().tolist())
    selected_datasets = st.multiselect("Dataset", dataset_choices, default=dataset_choices)
    status_choices = sorted(df["status"].dropna().unique().tolist())
    selected_status = st.multiselect("Status", status_choices, default=status_choices)

with b:
    indicator_choices = sorted(df["indicator_id"].dropna().unique().tolist())
    selected_indicators = st.multiselect(
        "Indicator (leave empty for all)", indicator_choices, default=[]
    )
    min_year = int(df["period_start"].min().year)
    max_year = int(df["period_end"].max().year)
    year_range = st.slider("Year range", min_year, max_year, (min_year, max_year))

filtered = df[
    df["dataset_id"].isin(selected_datasets)
    & df["status"].isin(selected_status)
    & (df["period_start"].dt.year >= year_range[0])
    & (df["period_end"].dt.year <= year_range[1])
]
if selected_indicators:
    filtered = filtered[filtered["indicator_id"].isin(selected_indicators)]

st.markdown(
    f"<div style='font-size:0.9rem;color:#94a3b8;margin:0.5rem 0 1rem 0;'>"
    f"<strong style='color:#a5b4fc;'>{len(filtered):,}</strong> observations match.</div>",
    unsafe_allow_html=True,
)

st.dataframe(filtered.head(500), use_container_width=True, hide_index=True)

if not filtered.empty:
    numeric = filtered["value_numeric"].dropna()
    if not numeric.empty:
        st.markdown('<div class="section-rule"></div>', unsafe_allow_html=True)
        st.subheader("Numeric value distribution")
        fig = px.histogram(
            numeric, nbins=30, template="plotly_dark",
            color_discrete_sequence=["#6366f1"],
        )
        st.plotly_chart(chart_layout(fig), use_container_width=True)

st.download_button(
    "Download filtered data as CSV",
    data=filtered.to_csv(index=False).encode("utf-8"),
    file_name="filtered_observations.csv",
    mime="text/csv",
)

footer()