"""Data quality + anomaly page. Designed and built by Manish Chapagain."""

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
ANOMALY_PATH = PROJECT_ROOT / "data" / "processed" / "anomalies.parquet"

st.set_page_config(page_title="Quality · Nepal Pipeline", page_icon="✅", layout="wide")
apply_theme()


@st.cache_data
def load():
    return pd.read_parquet(CLEAN_PATH)


@st.cache_data
def load_anomalies():
    if not ANOMALY_PATH.exists():
        return None
    return pd.read_parquet(ANOMALY_PATH)


sidebar_brand()
sidebar_status(
    [
        ("Cleaned dataset", CLEAN_PATH),
        ("Anomalies", ANOMALY_PATH),
    ]
)
sidebar_footer()

page_header(
    "Monitoring · Quality",
    "Data quality",
    "Automated checks and anomaly detection over the cleaned dataset.",
)

if not CLEAN_PATH.exists():
    st.error("Cleaned dataset not found. Run `python -m src.pipeline`.")
    st.stop()

df = load()

checks = {
    "Duplicate observation IDs": int(df["observation_id"].duplicated().sum()),
    "Rows missing both numeric and text values": int(
        (df["value_numeric"].isna() & df["value_text"].isna()).sum()
    ),
    "Invalid period_start dates": int(
        pd.to_datetime(df["period_start"], errors="coerce").isna().sum()
    ),
    "Invalid period_end dates": int(
        pd.to_datetime(df["period_end"], errors="coerce").isna().sum()
    ),
    "period_end before period_start": int(
        (
            df["period_end"].notna()
            & df["period_start"].notna()
            & (df["period_end"] < df["period_start"])
        ).sum()
    ),
}

cols = st.columns(5)
for col, (label, value) in zip(cols, checks.items()):
    with col:
        if value == 0:
            st.success(f"{label}\n\n**{value}**")
        else:
            st.warning(f"{label}\n\n**{value}**")

st.markdown('<div class="section-rule"></div>', unsafe_allow_html=True)

st.subheader("Missing values by column")
missing = df.isna().sum().sort_values(ascending=False)
st.dataframe(missing.to_frame("missing_count"), use_container_width=True)

st.subheader("Column data types")
st.dataframe(df.dtypes.astype(str).to_frame("dtype"), use_container_width=True)

st.markdown('<div class="section-rule"></div>', unsafe_allow_html=True)
st.subheader("Anomaly detection (Isolation Forest)")

anomalies = load_anomalies()
if anomalies is None:
    st.info("No anomaly file found. Run `python -m src.anomaly_detection`.")
else:
    n_anom = int(anomalies["is_anomaly"].sum())
    st.metric("Flagged anomalies", f"{n_anom:,}")

    flagged = anomalies[anomalies["is_anomaly"]]
    if not flagged.empty:
        top_indicators = flagged["indicator_id"].value_counts().head(15).reset_index()
        top_indicators.columns = ["indicator_id", "anomalies"]
        fig = px.bar(
            top_indicators, x="anomalies", y="indicator_id", orientation="h",
            template="plotly_dark", color_discrete_sequence=["#f59e0b"],
        )
        fig.update_layout(yaxis=dict(autorange="reversed"))
        st.plotly_chart(chart_layout(fig), use_container_width=True)

        st.dataframe(
            flagged[
                ["observation_id", "dataset_id", "indicator_id",
                 "value_numeric", "period_start"]
            ].head(200),
            use_container_width=True,
            hide_index=True,
        )

footer()