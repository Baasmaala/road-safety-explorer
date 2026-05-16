"""
Page 0 — Upload
Drop any country-level CSV. The pipeline detects whether it matches the WHO
format (and uses the same group identities as the rest of the app) or
treats it as a generic dataset (runs Basmala's notebook function from
scratch, labels as Group 1–4).
Outputs: cleaning summary, group sizes, 2D landscape, results table,
download button.
"""

import io
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

APP_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(APP_DIR))

from utils.theme import COLORS, CLUSTER_COLORS, CLUSTER_NAMES, FONTS, apply_plotly_theme
from utils.layout import render_sidebar
from utils.upload_pipeline import (
    clean_country_dataset,
    cluster_who_mode,
    detect_format,
    project_to_2d,
)

# ============================================================
# PAGE CONFIG
# ============================================================
st.set_page_config(
    page_title="Upload — Road Safety Explorer",
    page_icon="◯",
    layout="wide",
    initial_sidebar_state="collapsed",
)

apply_plotly_theme()
render_sidebar()

# ============================================================
# STYLES
# ============================================================
st.markdown(
    f"""
    <style>
    .block-container {{
        padding: 32px 56px 80px !important;
        max-width: 1280px !important;
    }}
    [data-testid="stAppViewContainer"] {{ background: {COLORS['cream']} !important; }}
    [data-testid="stHeader"] {{ display: none !important; }}
    footer {{ display: none !important; }}

    .eyebrow {{
        font-family: {FONTS['mono']};
        font-size: 11px; letter-spacing: 0.15em; text-transform: uppercase;
        color: {COLORS['ink_mute']};
        display: flex; align-items: center; gap: 12px; margin-bottom: 18px;
    }}
    .eyebrow .marker {{
        width: 8px; height: 8px; background: {COLORS['lime']};
        box-shadow: 0 0 0 2px {COLORS['ink']};
    }}
    .page-title {{
        font-family: {FONTS['display']};
        font-size: clamp(36px, 4.5vw, 56px);
        font-weight: 500; line-height: 0.98; letter-spacing: -0.025em;
        color: {COLORS['ink']}; margin-bottom: 14px;
    }}
    .page-title .accent {{
        font-family: {FONTS['serif']}; font-style: italic; font-weight: 400;
    }}
    .page-lede {{
        font-family: {FONTS['body']};
        font-size: 17px; line-height: 1.55; color: {COLORS['ink_mute']};
        max-width: 640px; margin-bottom: 28px;
    }}

    [data-testid="stFileUploaderDropzone"] {{
        background: {COLORS['cream_deep']} !important;
        border: 1.5px dashed {COLORS['ink']} !important;
        border-radius: 0 !important;
        padding: 28px !important;
        min-height: 120px !important;
    }}
    [data-testid="stFileUploaderDropzone"] section span,
    [data-testid="stFileUploaderDropzone"] section small {{
        font-family: {FONTS['mono']} !important;
        color: {COLORS['ink_mute']} !important;
    }}
    [data-testid="stFileUploaderDropzone"] button {{
        background: {COLORS['ink']} !important;
        color: {COLORS['cream']} !important;
        border: 1.5px solid {COLORS['ink']} !important;
        border-radius: 0 !important;
        font-family: {FONTS['body']} !important;
        font-size: 13px !important;
        font-weight: 500 !important;
        padding: 10px 20px !important;
    }}
    [data-testid="stFileUploaderDropzone"] button:hover {{
        background: {COLORS['lime']} !important;
        color: {COLORS['ink']} !important;
    }}

    .info-card {{
        background: {COLORS['cream_deep']};
        border: 1.5px solid {COLORS['ink']};
        padding: 20px 24px;
    }}
    .info-card .label {{
        font-family: {FONTS['mono']}; font-size: 10px;
        letter-spacing: 0.15em; text-transform: uppercase;
        color: {COLORS['ink_mute']}; margin-bottom: 4px;
    }}
    .info-card .value {{
        font-family: {FONTS['display']}; font-size: 28px;
        font-weight: 500; color: {COLORS['ink']};
        letter-spacing: -0.02em;
    }}

    .sub-eyebrow {{
        font-family: {FONTS['mono']}; font-size: 10px;
        letter-spacing: 0.15em; text-transform: uppercase;
        color: {COLORS['ink_mute']};
        margin: 28px 0 10px;
    }}

    .instruction-box {{
        background: {COLORS['cream_deep']};
        border-left: 3px solid {COLORS['lime']};
        padding: 18px 22px;
        margin: 20px 0 36px;
        font-family: {FONTS['body']};
        font-size: 14px; line-height: 1.6; color: {COLORS['ink_mute']};
    }}
    .instruction-box strong {{ color: {COLORS['ink']}; font-weight: 500; }}
    .instruction-box code {{
        font-family: {FONTS['mono']}; font-size: 12px;
        background: {COLORS['cream']}; padding: 2px 6px;
        border: 1px solid {COLORS['rule']};
    }}
    .instruction-box ul {{ margin: 10px 0 0 18px; }}
    .instruction-box li {{ margin-bottom: 4px; }}

    .mode-tag {{
        display: inline-block;
        font-family: {FONTS['mono']}; font-size: 10px;
        letter-spacing: 0.15em; text-transform: uppercase;
        padding: 5px 11px;
        background: {COLORS['ink']}; color: {COLORS['lime']};
        margin-bottom: 12px;
    }}

    .stDownloadButton button {{
        background: {COLORS['ink']} !important;
        color: {COLORS['cream']} !important;
        border: 1.5px solid {COLORS['ink']} !important;
        border-radius: 0 !important;
        font-family: {FONTS['body']} !important;
        font-size: 13px !important;
        font-weight: 500 !important;
        padding: 12px 22px !important;
    }}
    .stDownloadButton button:hover {{
        background: {COLORS['lime']} !important;
        color: {COLORS['ink']} !important;
    }}
    </style>
    """,
    unsafe_allow_html=True,
)

# ============================================================
# HEADER
# ============================================================
st.markdown(
    """
    <div class="eyebrow"><span class="marker"></span><span>00 / Upload</span></div>
    <h1 class="page-title">Bring your own <span class="accent">data.</span></h1>
    <p class="page-lede">
        Drop any country-level CSV. If it matches the WHO format, it gets
        labelled against the same four road-safety profile groups as the
        rest of the atlas. Otherwise, the same grouping pipeline runs
        from scratch on whatever measurements you supply, sorting your
        countries into four data-driven groups.
    </p>
    """,
    unsafe_allow_html=True,
)

# ============================================================
# INSTRUCTIONS
# ============================================================
st.markdown(
    """
    <div class="instruction-box">
        <strong>What your file needs:</strong>
        <ul>
            <li>One row per country, in CSV format.</li>
            <li>A column holding country names. Common headers work
                automatically: <code>Country</code>, <code>Country name</code>,
                <code>Entity</code>, or <code>Name</code>.</li>
            <li>The rest of the columns should be numeric measurements.
                Non-numeric columns are dropped during cleaning.</li>
            <li>Columns with more than 50% missing values are dropped;
                remaining gaps are filled with the column median. Constant
                columns (no variation) and severely skewed columns are
                also removed.</li>
            <li>Palestine listed under any WHO/UN variant
                (e.g. "occupied Palestinian territory") is normalized to
                "Palestine" automatically.</li>
        </ul>
    </div>
    """,
    unsafe_allow_html=True,
)

# ============================================================
# FILE UPLOADER
# ============================================================
uploaded = st.file_uploader(
    "Drop a CSV here",
    type=["csv"],
    label_visibility="collapsed",
)

if uploaded is None:
    st.markdown(
        f"""
        <div style="margin-top:60px; padding-top:24px; border-top:1px solid {COLORS['rule']};
                    font-family:{FONTS['mono']}; font-size:10px; letter-spacing:0.12em;
                    text-transform:uppercase; color:{COLORS['ink_mute']};">
            Waiting for upload &middot; Country-level CSV &middot; K-Means K=4 &middot; PCA 2D
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.stop()

# ============================================================
# READ THE FILE
# ============================================================
try:
    raw = pd.read_csv(uploaded)
except Exception as e:
    st.error(f"Couldn't read this file as CSV: {e}")
    st.stop()

# ============================================================
# DETECT FORMAT + RUN THE PIPELINE
# ============================================================
WHO_REF_PATH = APP_DIR.parent / "data" / "processed" / "country_features.csv"
format_mode = detect_format(raw, WHO_REF_PATH) if WHO_REF_PATH.exists() else "generic"

try:
    if format_mode == "who":
        out = cluster_who_mode(raw, WHO_REF_PATH)
    else:
        out = clean_country_dataset(raw)
except ValueError as e:
    st.error(str(e))
    st.stop()

labels_df = out["labels_df"]
features = out["features"]
country_col = out["country_col"]

# 2D projection for the landscape scatter
pca_out = project_to_2d(features)
ev1, ev2 = pca_out["explained_variance"]

# Build a unified `results` frame indexed by country name
results = labels_df.copy()
if country_col and country_col in results.columns:
    results = results.set_index(country_col)
results["PC1"] = pca_out["PC1"]
results["PC2"] = pca_out["PC2"]
results.index.name = "Country"

# Group sizes
sizes = {int(c): int((labels_df["Cluster"] == c).sum()) for c in sorted(labels_df["Cluster"].unique())}

# ============================================================
# CLEANING SUMMARY
# ============================================================
st.markdown(
    '<div class="eyebrow"><span class="marker"></span><span>Cleaning summary</span></div>',
    unsafe_allow_html=True,
)

c1, c2, c3, c4 = st.columns(4)
with c1:
    st.markdown(
        f"""<div class="info-card">
            <div class="label">Country column</div>
            <div class="value">{country_col or '—'}</div>
        </div>""",
        unsafe_allow_html=True,
    )
with c2:
    st.markdown(
        f"""<div class="info-card">
            <div class="label">Rows kept</div>
            <div class="value">{len(labels_df)}</div>
        </div>""",
        unsafe_allow_html=True,
    )
with c3:
    st.markdown(
        f"""<div class="info-card">
            <div class="label">Measurements kept</div>
            <div class="value">{features.shape[1]}</div>
        </div>""",
        unsafe_allow_html=True,
    )
with c4:
    palestine_present = "Palestine" in results.index
    st.markdown(
        f"""<div class="info-card">
            <div class="label">Palestine found</div>
            <div class="value">{'Yes' if palestine_present else 'No'}</div>
        </div>""",
        unsafe_allow_html=True,
    )

# What was dropped
dropped_cols = out.get("dropped_cols", [])
constant_cols = out.get("constant_cols", [])
outlier_cols = out.get("outlier_cols", [])
if dropped_cols or constant_cols or outlier_cols:
    with st.expander("What was dropped during cleaning"):
        if dropped_cols:
            st.markdown(f"**Sparse columns dropped** ({len(dropped_cols)} — >50% missing): "
                        + ", ".join(f"`{c}`" for c in dropped_cols))
        if constant_cols:
            st.markdown(f"**Constant columns dropped** ({len(constant_cols)} — no variation): "
                        + ", ".join(f"`{c}`" for c in constant_cols))
        if outlier_cols:
            st.markdown(f"**Skewed columns dropped** ({len(outlier_cols)} — extremely uneven distribution): "
                        + ", ".join(f"`{c}`" for c in outlier_cols))

# ============================================================
# MODE TAG
# ============================================================
if format_mode == "who":
    mode_label = "WHO format detected — using shared group profiles"
else:
    mode_label = "Generic format — groups built from scratch on your data"

st.markdown(
    f'<span class="mode-tag">{mode_label}</span>',
    unsafe_allow_html=True,
)

# ============================================================
# GROUP LANDSCAPE
# ============================================================
st.markdown(
    '<div class="eyebrow" style="margin-top:12px;"><span class="marker"></span><span>Group landscape</span></div>',
    unsafe_allow_html=True,
)
st.markdown(
    f'<div class="sub-eyebrow">All countries placed on a single chart &middot; '
    f'captures {ev1 + ev2:.1%} of the variation in your data</div>',
    unsafe_allow_html=True,
)

fig = go.Figure()

for cid in sorted(results["Cluster"].unique()):
    sub = results[results["Cluster"] == int(cid)]
    cname = sub["Cluster_name"].iloc[0]
    fig.add_trace(
        go.Scatter(
            x=sub["PC1"],
            y=sub["PC2"],
            mode="markers",
            name=f"{int(cid)} — {cname}",
            marker=dict(
                size=10,
                color=CLUSTER_COLORS.get(int(cid), COLORS["ink_mute"]),
                line=dict(color=COLORS["ink"], width=0.8),
            ),
            customdata=np.array(sub.index.tolist()).reshape(-1, 1),
            hovertemplate=(
                "<b>%{customdata[0]}</b><br>"
                f"{cname}<br>"
                "Position: %{x:.2f}, %{y:.2f}"
                "<extra></extra>"
            ),
        )
    )

if "Palestine" in results.index:
    pal = results.loc[["Palestine"]]
    fig.add_trace(
        go.Scatter(
            x=pal["PC1"], y=pal["PC2"],
            mode="markers+text",
            name="Palestine",
            marker=dict(
                size=22, color=COLORS["lime"], symbol="star",
                line=dict(color=COLORS["ink"], width=1.8),
            ),
            text=["Palestine"], textposition="top center",
            textfont=dict(family=FONTS["mono"], size=11, color=COLORS["ink"]),
            hovertemplate="<b>Palestine</b><br>Position: %{x:.2f}, %{y:.2f}<extra></extra>",
        )
    )

fig.update_layout(
    paper_bgcolor=COLORS["cream_deep"],
    plot_bgcolor=COLORS["cream_deep"],
    xaxis=dict(
        title=dict(text="Horizontal axis", font=dict(family=FONTS["mono"], size=11, color=COLORS["ink_mute"])),
        gridcolor=COLORS["rule"], zerolinecolor=COLORS["rule"],
        tickfont=dict(family=FONTS["mono"], size=10, color=COLORS["ink_mute"]),
        showline=True, linecolor=COLORS["ink"], linewidth=1,
    ),
    yaxis=dict(
        title=dict(text="Vertical axis", font=dict(family=FONTS["mono"], size=11, color=COLORS["ink_mute"])),
        gridcolor=COLORS["rule"], zerolinecolor=COLORS["rule"],
        tickfont=dict(family=FONTS["mono"], size=10, color=COLORS["ink_mute"]),
        showline=True, linecolor=COLORS["ink"], linewidth=1,
    ),
    margin=dict(l=20, r=20, t=10, b=20),
    height=520,
    legend=dict(
        orientation="h",
        yanchor="bottom", y=-0.20,
        xanchor="left", x=0,
        font=dict(family=FONTS["mono"], size=10, color=COLORS["ink_mute"]),
        bgcolor="rgba(0,0,0,0)",
    ),
)
st.plotly_chart(fig, use_container_width=True, config={"displaylogo": False})

# ============================================================
# GROUP SUMMARY (sizes + sample members)
# ============================================================
st.markdown(
    '<div class="eyebrow" style="margin-top:36px;"><span class="marker"></span><span>Group breakdown</span></div>',
    unsafe_allow_html=True,
)

size_cols = st.columns(len(sizes))
for i, cid in enumerate(sorted(sizes.keys())):
    members = results[results["Cluster"] == cid].index.tolist()
    sample = ", ".join(members[:4]) + (f" + {len(members) - 4} more" if len(members) > 4 else "")
    cname = results[results["Cluster"] == cid]["Cluster_name"].iloc[0] if sizes[cid] > 0 else f"Group {cid + 1}"

    with size_cols[i]:
        st.markdown(
            f"""<div class="info-card" style="border-left:3px solid {CLUSTER_COLORS.get(cid, COLORS['ink'])};">
                <div class="label">{cname}</div>
                <div class="value">{sizes[cid]}</div>
                <div style="font-family:{FONTS['mono']}; font-size:10px;
                            color:{COLORS['ink_mute']}; margin-top:10px; line-height:1.5;">
                    {sample if members else '—'}
                </div>
            </div>""",
            unsafe_allow_html=True,
        )

# ============================================================
# RESULTS TABLE + DOWNLOAD
# ============================================================
st.markdown(
    '<div class="eyebrow" style="margin-top:36px;"><span class="marker"></span><span>All countries</span></div>',
    unsafe_allow_html=True,
)

display_table = results.reset_index()
if "Country" not in display_table.columns:
    display_table = display_table.rename(columns={display_table.columns[0]: "Country"})
display_table["PC1"] = display_table["PC1"].round(3)
display_table["PC2"] = display_table["PC2"].round(3)
display_table = display_table[["Country", "Cluster_name", "Cluster", "PC1", "PC2"]]
display_table = display_table.rename(columns={
    "Cluster_name": "Group name",
    "Cluster": "Group",
    "PC1": "Horizontal",
    "PC2": "Vertical",
})

st.dataframe(display_table, use_container_width=True, hide_index=True)

# Download button — results as CSV
csv_buf = io.StringIO()
display_table.to_csv(csv_buf, index=False)
st.download_button(
    label="Download results as CSV",
    data=csv_buf.getvalue(),
    file_name="upload_results.csv",
    mime="text/csv",
)

# ============================================================
# FOOTER NOTE — technical methodology stays here only
# ============================================================
st.markdown(
    f"""
    <div style="margin-top:60px; padding-top:24px; border-top:1px solid {COLORS['rule']};
                font-family:{FONTS['mono']}; font-size:10px; letter-spacing:0.12em;
                text-transform:uppercase; color:{COLORS['ink_mute']};">
        Format: {format_mode.upper()} &middot; K-Means K=4 &middot; PCA 2D &middot;
        {len(labels_df)} countries &middot; {features.shape[1]} indicators
    </div>
    """,
    unsafe_allow_html=True,
)