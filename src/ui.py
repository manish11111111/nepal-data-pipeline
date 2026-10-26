"""Shared UI components for the Nepal Public Data Pipeline dashboard.

Designed and built by Manish Chapagain.
"""

from pathlib import Path

import streamlit as st


AUTHOR = "Manish Chapagain"
PROJECT_NAME = "Nepal Public Data Pipeline"

PROJECT_ROOT = Path(__file__).resolve().parent.parent


GLOBAL_CSS = """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
/* Hide the green success checkmark in the page header */
[data-testid="stStatusWidget"] {
    display: none !important;
}
    .stApp {
        background:
            radial-gradient(circle at 15% 0%, rgba(99,102,241,0.10), transparent 45%),
            radial-gradient(circle at 85% 100%, rgba(236,72,153,0.07), transparent 45%),
            #0a0a0f;
        color: #e5e7eb;
    }
    #MainMenu, footer, header { visibility: hidden; }
    .block-container { padding-top: 2rem; padding-bottom: 3rem; max-width: 1400px; }

    h1, h2, h3 { font-family: 'Inter', sans-serif; letter-spacing: -0.02em; color: #f9fafb; }
    h1 { font-weight: 700; font-size: 2.6rem; line-height: 1.1; }
    h2 { font-weight: 600; font-size: 1.45rem; margin-top: 1.75rem; }
    h3 { font-weight: 600; font-size: 1.1rem; }
    p, span, div { color: #cbd5e1; }

    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0f0f17 0%, #0a0a0f 100%);
        border-right: 1px solid rgba(255,255,255,0.06);
    }
    section[data-testid="stSidebar"] .block-container { padding-top: 1.75rem; }

    div[data-testid="stMetric"] {
        background: linear-gradient(145deg, rgba(255,255,255,0.04), rgba(255,255,255,0.01));
        border: 1px solid rgba(255,255,255,0.08);
        border-radius: 14px;
        padding: 1rem 1.15rem;
        transition: border-color 0.2s ease, transform 0.2s ease;
    }
    div[data-testid="stMetric"]:hover {
        border-color: rgba(99,102,241,0.5);
        transform: translateY(-2px);
    }
    div[data-testid="stMetricLabel"] {
        font-size: 0.7rem !important; text-transform: uppercase;
        letter-spacing: 0.08em; color: #94a3b8 !important; font-weight: 500;
    }
    div[data-testid="stMetricValue"] {
        font-family: 'JetBrains Mono', monospace;
        font-size: 1.75rem !important; font-weight: 500; color: #f9fafb !important;
    }

    .stTabs [data-baseweb="tab-list"] {
        gap: 0.4rem; background: transparent;
        border-bottom: 1px solid rgba(255,255,255,0.08);
    }
    .stTabs [data-baseweb="tab"] {
        background: transparent; border-radius: 8px 8px 0 0;
        padding: 0.55rem 1rem; color: #94a3b8; font-weight: 500;
        font-size: 0.88rem; border: none;
    }
    .stTabs [aria-selected="true"] {
        background: rgba(99,102,241,0.12); color: #a5b4fc;
        border-bottom: 2px solid #6366f1;
    }

    div[data-testid="stDataFrame"] {
        border: 1px solid rgba(255,255,255,0.06);
        border-radius: 12px; overflow: hidden;
    }

    .stButton > button, .stDownloadButton > button {
        background: #6366f1; color: #ffffff; border: none;
        border-radius: 9px; padding: 0.5rem 1.1rem;
        font-weight: 500; font-size: 0.86rem;
        transition: background 0.15s ease;
    }
    .stButton > button:hover, .stDownloadButton > button:hover { background: #4f46e5; }

    .stAlert { border-radius: 10px; border: 1px solid rgba(255,255,255,0.08); }

    .brand-block { padding: 0.25rem 0 1.1rem 0; }
    .brand-mark { font-size: 1.5rem; color: #6366f1; margin-right: 0.5rem; }
    .brand-name { font-size: 1.02rem; font-weight: 600; color: #f9fafb; }
    .brand-role {
        font-size: 0.7rem; color: #64748b; text-transform: uppercase;
        letter-spacing: 0.1em; margin-top: 0.2rem;
    }

    .status-row {
        display: flex; justify-content: space-between; align-items: center;
        padding: 0.4rem 0; font-size: 0.8rem;
        border-bottom: 1px solid rgba(255,255,255,0.04);
    }
    .status-label { color: #94a3b8; }
    .status-ok { color: #34d399; font-family: 'JetBrains Mono', monospace; font-size: 0.76rem; }
    .status-miss { color: #f87171; font-family: 'JetBrains Mono', monospace; font-size: 0.76rem; }

    .hero-eyebrow {
        font-size: 0.72rem; text-transform: uppercase; letter-spacing: 0.16em;
        color: #818cf8; font-weight: 500; margin-bottom: 0.5rem;
    }
    .hero-title { font-size: 2.4rem; font-weight: 700; color: #f9fafb; line-height: 1.1; }
    .hero-sub {
        font-size: 1rem; color: #94a3b8; max-width: 760px;
        line-height: 1.6; margin-top: 0.75rem;
    }

    .section-rule {
        height: 1px; background: linear-gradient(90deg, rgba(99,102,241,0.4), transparent);
        margin: 1.75rem 0 1.25rem 0;
    }

    .page-eyebrow {
        font-size: 0.7rem; text-transform: uppercase; letter-spacing: 0.14em;
        color: #818cf8; font-weight: 500; margin-bottom: 0.35rem;
    }
    .page-title { font-size: 1.9rem; font-weight: 700; color: #f9fafb; }
    .page-caption { font-size: 0.92rem; color: #94a3b8; margin-top: 0.3rem; }

    .credit {
        text-align: center; margin-top: 3rem; padding-top: 1.25rem;
        border-top: 1px solid rgba(255,255,255,0.06);
        font-size: 0.76rem; color: #64748b; letter-spacing: 0.03em;
    }
    .credit strong { color: #a5b4fc; font-weight: 600; }
</style>
"""


def apply_theme() -> None:
    """Inject global CSS and page config."""
    st.markdown(GLOBAL_CSS, unsafe_allow_html=True)


def page_header(eyebrow: str, title: str, caption: str) -> None:
    """Consistent page header across all pages."""
    st.markdown(f'<div class="page-eyebrow">{eyebrow}</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="page-title">{title}</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="page-caption">{caption}</div>', unsafe_allow_html=True)


def hero(eyebrow: str, title: str, subtitle: str) -> None:
    st.markdown(f'<div class="hero-eyebrow">{eyebrow}</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="hero-title">{title}</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="hero-sub">{subtitle}</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-rule"></div>', unsafe_allow_html=True)


def sidebar_brand() -> None:
    with st.sidebar:
        st.markdown(
            '<div class="brand-block">'
            '<span class="brand-mark">◈</span>'
            '<span class="brand-name">Nepal Data Pipeline</span>'
            '<div class="brand-role">by Manish Chapagain</div>'
            '</div>',
            unsafe_allow_html=True,
        )


def sidebar_status(items: list) -> None:
    """Render a list of (label, Path) status rows in the sidebar."""
    with st.sidebar:
        st.markdown(
            '<div style="font-size:0.68rem;text-transform:uppercase;'
            'letter-spacing:0.12em;color:#64748b;margin-bottom:0.5rem;">'
            'Artifacts</div>',
            unsafe_allow_html=True,
        )
        for label, path in items:
            if path.exists():
                size_mb = path.stat().st_size / (1024 * 1024)
                cls, text = "status-ok", f"{size_mb:.2f} MB"
            else:
                cls, text = "status-miss", "missing"
            st.markdown(
                f'<div class="status-row">'
                f'<span class="status-label">{label}</span>'
                f'<span class="{cls}">{text}</span>'
                f'</div>',
                unsafe_allow_html=True,
            )


def sidebar_footer() -> None:
    with st.sidebar:
        st.markdown("<div style='height:1.25rem'></div>", unsafe_allow_html=True)
        st.markdown(
            '<div style="font-size:0.68rem;text-transform:uppercase;'
            'letter-spacing:0.12em;color:#64748b;margin-bottom:0.5rem;">'
            'Stack</div>',
            unsafe_allow_html=True,
        )
        st.markdown(
            '<div style="font-size:0.8rem;color:#94a3b8;line-height:1.7;">'
            'pandas · PyArrow · PostgreSQL<br>'
            'Docker · pytest · Streamlit · Plotly'
            '</div>',
            unsafe_allow_html=True,
        )


def footer() -> None:
    st.markdown(
        f'<div class="credit">Designed and built by '
        f'<strong>{AUTHOR}</strong> · {PROJECT_NAME}</div>',
        unsafe_allow_html=True,
    )


def chart_layout(fig, height: int = 340):
    """Apply the shared Plotly layout to a figure."""
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#cbd5e1", family="Inter"),
        margin=dict(l=10, r=10, t=10, b=10),
        height=height,
        showlegend=False,
    )
    return fig