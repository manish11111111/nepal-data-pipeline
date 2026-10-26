"""Indicator summary page. Designed and built by Manish Chapagain."""

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
INDICATOR_SUMMARY_PATH = PROJECT_ROOT / "data" / "processed" / "indicator_summary.csv"

st.set_page_config(page_title="Indicators · Nepal Pipeline", page_icon="📊", layout="wide")
apply_theme()


@st.cache_data
def load():
    return pd.read_csv(INDICATOR_SUMMARY_PATH)


sidebar_brand()
sidebar_status([("Indicator summary", INDICATOR_SUMMARY_PATH)])
sidebar_footer()

page_header(
    "Analytics · Indicators",
    "Indicator summary",
    "Indicator-level aggregates with observation counts and value statistics.",
)

if not INDICATOR_SUMMARY_PATH.exists():
    st.error("indicator_summary.csv not found. Run `python -m src.pipeline`.")
    st.stop()

ind = load()

datasets = ["All datasets"] + sorted(ind["dataset_id"].dropna().unique().tolist())
selected = st.selectbox("Filter by dataset", datasets)
view = ind if selected == "All datasets" else ind[ind["dataset_id"] == selected]

st.dataframe(view, use_container_width=True, hide_index=True)

st.markdown('<div class="section-rule"></div>', unsafe_allow_html=True)

col1, col2 = st.columns(2)

with col1:
    st.subheader("Top 15 indicators by observation count")
    top = view.sort_values("observation_count", ascending=False).head(15)
    fig = px.bar(
        top, x="observation_count", y="indicator_id", orientation="h",
        template="plotly_dark", color_discrete_sequence=["#6366f1"],
    )
    fig.update_layout(yaxis=dict(autorange="reversed"))
    st.plotly_chart(chart_layout(fig), use_container_width=True)

with col2:
    st.subheader("Top 15 indicators by mean value")
    mean_view = (
        view.dropna(subset=["mean_value"])
        .sort_values("mean_value", ascending=False)
        .head(15)
    )
    fig = px.bar(
        mean_view, x="mean_value", y="indicator_id", orientation="h",
        template="plotly_dark", color_discrete_sequence=["#ec4899"],
    )
    fig.update_layout(yaxis=dict(autorange="reversed"))
    st.plotly_chart(chart_layout(fig), use_container_width=True)

footer()