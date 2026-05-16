"""
Data loading utilities. Centralized so every page reads from the same place
and the cache is shared across pages.
"""
from pathlib import Path
import pandas as pd
import streamlit as st

DATA_DIR = Path(__file__).parent.parent / "data"


@st.cache_data(show_spinner=False)
def load_clusters() -> pd.DataFrame:
    """Country -> cluster mapping with both numeric Cluster and Cluster_name."""
    return pd.read_csv(DATA_DIR / "country_clusters.csv")


@st.cache_data(show_spinner=False)
def load_features() -> pd.DataFrame:
    """Model-ready features (log-transformed). Use for math and radar charts."""
    return pd.read_csv(DATA_DIR / "country_features.csv")


@st.cache_data(show_spinner=False)
def load_display_features() -> pd.DataFrame:
    """Original-unit features. Use for tables, tooltips, and stat cards."""
    return pd.read_csv(DATA_DIR / "country_features_display.csv")


@st.cache_data(show_spinner=False)
def get_cluster_summary(clusters_df: pd.DataFrame, display_df: pd.DataFrame) -> dict:
    """Top-level summary stats for the landing page."""
    merged = clusters_df.merge(
        display_df[["ISO_3 country name"]
                   + [c for c in display_df.columns
                      if "WHO-estimated road traffic fatalities" in c
                      and "rate" not in c.lower()
                      and "Lower" not in c
                      and "Upper" not in c
                      and "2010" not in c
                      and "2016" not in c]],
        on="ISO_3 country name",
        how="left",
    )
    # the main estimated fatalities column
    fatality_col = next(
        (c for c in merged.columns
         if "WHO-estimated road traffic fatalities" in c
         and "rate" not in c.lower()),
        None,
    )
    total = int(merged[fatality_col].sum()) if fatality_col else 1_190_000
    return {
        "total_deaths_est": total,
        "num_countries": len(clusters_df),
        "num_clusters": clusters_df["Cluster"].nunique(),
    }


@st.cache_data(show_spinner=False)
def get_country_record(iso: str) -> dict:
    """Everything we know about one country, merged across the three CSVs."""
    clusters = load_clusters()
    display = load_display_features()
    row_c = clusters[clusters["ISO_3 country name"] == iso]
    row_d = display[display["ISO_3 country name"] == iso]
    if row_c.empty:
        return {}
    return {
        "name": row_c["Country name"].iloc[0],
        "iso": iso,
        "income": row_c["Income group"].iloc[0],
        "region": row_c["WHO Region"].iloc[0],
        "cluster": int(row_c["Cluster"].iloc[0]),
        "cluster_name": row_c["Cluster_name"].iloc[0],
        "features": row_d.iloc[0].to_dict() if not row_d.empty else {},
    }


CLUSTER_COLORS = {
    0: "#6BB6FF",  # developing
    1: "#A78BFA",  # rich europe
    2: "#FF6B6B",  # palestine's cluster
    3: "#FBBF24",  # atypical
}

CLUSTER_DESCRIPTIONS = {
    0: "Developing-country road profile — 85 countries with higher fatality rates, lower motorization, and a higher share of pedestrian deaths.",
    1: "Rich-country car culture — 53 countries (most of Europe) with high vehicle ownership but low fatality rates due to mature road safety systems.",
    2: "Low-motorization mixed — 25 countries including small island states and Palestine. Lowest vehicle ownership of any cluster.",
    3: "Atypical reporting — 8 countries with unusual demographic patterns in their fatality data.",
}