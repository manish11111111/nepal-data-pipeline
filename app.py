"""Nepal Public Data Pipeline — landing page.

Designed and built by Manish Chapagain.
"""

from pathlib import Path

import pandas as pd
import streamlit as st

from src.ui import (
    apply_theme,
    chart_layout,
    footer,
    hero,
    sidebar_brand,
    sidebar_footer,
    sidebar_status,
)


PROJECT_ROOT = Path(__file__).resolve().parent
CLEAN_PATH = PROJECT_ROOT / "data" / "processed" / "observations_clean.parquet"
RAW_PATH = PROJECT_ROOT / "data" / "raw" / "observations.parquet"
ANOMALY_PATH = PROJECT_ROOT / "data" / "processed" / "anomalies.parquet"

st.set_page_config(
    page_title="Nepal Public Data Pipeline · Manish Chapagain",
    page_icon="◈",
    layout="wide",
    initial_sidebar_state="expanded",
)
apply_theme()


@st.cache_data
def load_clean() -> pd.DataFrame:
    return pd.read_parquet(CLEAN_PATH)


@st.cache_data
def load_anomalies():
    if not ANOMALY_PATH.exists():
        return None
    return pd.read_parquet(ANOMALY_PATH)


sidebar_brand()
sidebar_status(
    [
        ("Raw dataset", RAW_PATH),
        ("Cleaned dataset", CLEAN_PATH),
        ("Anomalies", ANOMALY_PATH),
    ]
)
sidebar_footer()

if not CLEAN_PATH.exists():
    st.error(
        "Cleaned dataset not found. Run the pipeline first:\n\n"
        "```\npython -m src.pipeline\n```"
    )
    st.stop()

df = load_clean()

hero(
    "Data engineering · Nepal",
    "Public data, made reliable.",
    "A reproducible pipeline that ingests, validates, transforms, "
    "summarises, and stores public observations about Nepal — from raw "
    "Parquet to PostgreSQL, with automated tests at every stage.",
)

c1, c2, c3, c4 = st.columns(4)
c1.metric("Observations", f"{len(df):,}")
c2.metric("Columns", f"{len(df.columns)}")
c3.metric("Indicators", f"{df['indicator_id'].nunique():,}")
c4.metric("Places", f"{df['place_id'].nunique():,}")

st.markdown("<div style='height:0.6rem'></div>", unsafe_allow_html=True)

c5, c6, c7, c8 = st.columns(4)
c5.metric("Datasets", f"{df['dataset_id'].nunique()}")
c6.metric("Duplicate IDs", f"{df['observation_id'].duplicated().sum()}")
c7.metric("Missing values", f"{int(df.isna().sum().sum()):,}")
c8.metric(
    "Date range",
    f"{df['period_start'].min().year}–{df['period_end'].max().year}",
)

st.markdown('<div class="section-rule"></div>', unsafe_allow_html=True)

anomalies = load_anomalies()
if anomalies is not None:
    n_anom = int(anomalies["is_anomaly"].sum())
    st.markdown("### Anomaly detection")
    st.info(
        f"**{n_anom:,}** observations flagged as anomalies by Isolation "
        "Forest (per-indicator). See the **Quality** page for details."
    )

st.markdown("### Navigate")
st.markdown(
    "Use the sidebar to open **Dataset**, **Indicators**, **Explore**, "
    "**Quality**, and **About**."
)

footer()