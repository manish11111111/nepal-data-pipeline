"""About page. Designed and built by Manish Chapagain."""

from pathlib import Path

import streamlit as st

from src.ui import (
    apply_theme,
    footer,
    page_header,
    sidebar_brand,
    sidebar_footer,
)


PROJECT_ROOT = Path(__file__).resolve().parent.parent

st.set_page_config(page_title="About · Nepal Pipeline", page_icon="◈", layout="wide")
apply_theme()

sidebar_brand()
sidebar_footer()

page_header(
    "Project · Author",
    "About this project",
    "Context, pipeline stages, stack, and the person behind it.",
)

st.markdown(
    """
### What this is

A reproducible data engineering pipeline for public observations about Nepal.
It ingests a Parquet dataset from DataNepal, validates structure and consistency,
transforms dates, produces analytical summaries, and loads cleaned observations
into PostgreSQL.

### Pipeline stages

1. **Ingestion** — download + schema validation
2. **Validation** — required columns, duplicates, dates, values
3. **Transformation** — date parsing, cleaned Parquet
4. **Summarisation** — indicator-level and dataset-level CSVs
5. **Persistence** — PostgreSQL loader with duplicate protection
6. **Verification** — pytest + GitHub Actions

### Stack

pandas · PyArrow · PostgreSQL · Docker · pytest · Streamlit · Plotly · scikit-learn
"""
)

st.markdown('<div class="section-rule"></div>', unsafe_allow_html=True)

st.markdown("### Author")
st.markdown(
    "**Manish Chapagain** — Computer Engineering graduate interested in "
    "data engineering, AI, and data-driven applications.\n\n"
    "- GitHub: [manish11111111](https://github.com/manish11111111)\n"
    "- LinkedIn: [manish-chapagain-467451284](https://linkedin.com/in/manish-chapagain-467451284)"
)

footer()