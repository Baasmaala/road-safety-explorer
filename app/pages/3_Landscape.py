"""
Page 3 — Landscape
PCA scatter of all countries colored by cluster, with anomalies styled
distinctly (diamond + lime ring) and Palestine starred.

Story: clustering groups countries into 4 profiles; PCA flattens the
27-feature space into 2D so we can see the shape of those groups. Isolation
Forest then flags ~5% of countries as anomalous — countries whose indicator
patterns don't fit any cluster cleanly. Pick any country below to see
exactly where it sits.

Inputs:
    data/processed/country_pca.csv        (full 171 countries, PCA + cluster)
    data/processed/country_anomalies.csv  (subset: flagged anomalies)
"""

import sys
from pathlib import Path

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

# Make utils.* importable when running via `streamlit run app/app.py`
APP_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(APP_DIR))
from utils.theme import (
    COLORS,
    CLUSTER_COLORS,
    CLUSTER_NAMES,
    FONTS,
    apply_plotly_theme,
)
from utils.layout import render_sidebar

# ============================================================
# PAGE CONFIG
# ============================================================
st.set_page_config(
    page_title="Landscape — Road Safety Explorer",
    page_icon="◯",
    layout="wide",
    initial_sidebar_state="collapsed",
)

apply_plotly_theme()
render_sidebar()

# ============================================================
# STYLES — match Atlas
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
        max-width: 640px; margin-bottom: 36px;
    }}

    .stRadio > label, .stSelectbox > label {{
        font-family: {FONTS['mono']} !important;
        font-size: 10px !important; letter-spacing: 0.15em !important;
        text-transform: uppercase !important; color: {COLORS['ink_mute']} !important;
    }}
    [data-baseweb="select"] > div {{
        background: {COLORS['cream']} !important;
        border: 1.5px solid {COLORS['ink']} !important;
        border-radius: 0 !important;
    }}

    /* detail card for the selected country */
    .detail-card {{
        background: {COLORS['cream_deep']};
        border: 1.5px solid {COLORS['ink']};
        padding: 28px 32px; margin-top: 20px;
    }}
    .detail-card h3 {{
        font-family: {FONTS['display']}; font-size: 32px; font-weight: 500;
        letter-spacing: -0.02em; margin: 0 0 8px 0; color: {COLORS['ink']};
    }}
    .detail-card .sub {{
        font-family: {FONTS['mono']}; font-size: 10px;
        letter-spacing: 0.15em; text-transform: uppercase;
        color: {COLORS['lime']}; background: {COLORS['ink']};
        padding: 5px 11px; display: inline-block;
    }}
    .detail-card .sub.anomaly {{
        color: {COLORS['ink']}; background: {COLORS['lime']};
    }}
    .detail-card .meta {{
        font-family: {FONTS['mono']}; font-size: 11px;
        color: {COLORS['ink_mute']}; margin-top: 18px;
        line-height: 1.7;
    }}
    .detail-card .meta strong {{
        color: {COLORS['ink']}; font-weight: 500;
    }}

    .sub-eyebrow {{
        font-family: {FONTS['mono']}; font-size: 10px;
        letter-spacing: 0.15em; text-transform: uppercase;
        color: {COLORS['ink_mute']};
        margin: 28px 0 10px;
    }}

    /* anomaly list */
    .anomaly-row {{
        display: flex; justify-content: space-between; align-items: center;
        padding: 12px 18px;
        border: 1px solid {COLORS['rule']};
        background: {COLORS['cream_deep']};
        margin-bottom: 6px;
        font-family: {FONTS['mono']};
        font-size: 12px;
    }}
    .anomaly-row .name {{
        font-family: {FONTS['display']}; font-size: 15px; font-weight: 500;
        color: {COLORS['ink']};
    }}
    .anomaly-row .score {{
        color: {COLORS['ink_mute']};
    }}
    .anomaly-row .region {{
        color: {COLORS['ink_mute']}; font-size: 10px;
        letter-spacing: 0.1em; text-transform: uppercase;
    }}
    </style>
    """,
    unsafe_allow_html=True,
)

# ============================================================
# DATA LOADING
# ============================================================
DATA_DIR = APP_DIR.parent / "data" / "processed"


@st.cache_data
def load_data():
    pca_path = DATA_DIR / "country_pca.csv"
    anom_path = DATA_DIR / "country_anomalies.csv"

    if not pca_path.exists():
        st.error(f"Missing file: {pca_path}")
        st.stop()
    if not anom_path.exists():
        st.error(f"Missing file: {anom_path}")
        st.stop()

    pca = pd.read_csv(pca_path)
    anom = pd.read_csv(anom_path)

    # Standardize the ISO column name (handle the "ISO_3 country name" header)
    for df in (pca, anom):
        rename_map = {}
        for c in df.columns:
            cl = c.lower().strip()
            if "iso" in cl:
                rename_map[c] = "ISO"
            elif cl == "country name":
                rename_map[c] = "Country"
        df.rename(columns=rename_map, inplace=True)

    return pca, anom


pca_df, anom_df = load_data()

# Mark which countries are anomalies in the master frame
pca_df["is_anomaly"] = pca_df["is_anomaly"].astype(bool)

# ============================================================
# HEADER
# ============================================================
st.markdown(
    """
    <div class="eyebrow"><span class="marker"></span><span>03 / Landscape</span></div>
    <h1 class="page-title">The space of <span class="accent">countries.</span></h1>
    <p class="page-lede">
        PCA flattens 27 road-safety indicators into two dimensions. Each dot
        is a country, colored by its cluster. Diamonds with a lime ring are
        anomalies — countries that don't fit cleanly into any group. Palestine
        is starred.
    </p>
    """,
    unsafe_allow_html=True,
)

# ============================================================
# SCATTER PLOT
# ============================================================
fig = go.Figure()

# One trace per cluster — only NON-anomalies, as circles
for cluster_id in sorted(pca_df["Cluster"].dropna().unique()):
    cid = int(cluster_id)
    sub = pca_df[(pca_df["Cluster"] == cid) & (~pca_df["is_anomaly"])]
    sub = sub[sub["Country"] != "Palestine"]  # Palestine drawn separately
    cluster_label = CLUSTER_NAMES.get(cid, f"Cluster {cid}")

    fig.add_trace(
        go.Scatter(
            x=sub["PC1"],
            y=sub["PC2"],
            mode="markers",
            name=f"{cid} / {cluster_label}",
            marker=dict(
                size=11,
                color=CLUSTER_COLORS.get(cid, COLORS["ink_mute"]),
                symbol="circle",
                line=dict(color=COLORS["ink"], width=0.8),
                opacity=0.92,
            ),
            customdata=sub[["Country", "Cluster_name"]].values,
            hovertemplate=(
                "<b>%{customdata[0]}</b><br>"
                "%{customdata[1]}<br>"
                "PC1: %{x:.2f}  &middot;  PC2: %{y:.2f}"
                "<extra></extra>"
            ),
        )
    )

# Anomaly trace — diamonds with lime ring, all clusters merged into one legend entry
anom_in_pca = pca_df[pca_df["is_anomaly"] & (pca_df["Country"] != "Palestine")]
if not anom_in_pca.empty:
    # color fill by their cluster, but with a lime ring
    fill_colors = [
        CLUSTER_COLORS.get(int(c), COLORS["ink_mute"])
        for c in anom_in_pca["Cluster"]
    ]
    fig.add_trace(
        go.Scatter(
            x=anom_in_pca["PC1"],
            y=anom_in_pca["PC2"],
            mode="markers",
            name="Anomaly",
            marker=dict(
                size=15,
                color=fill_colors,
                symbol="diamond",
                line=dict(color=COLORS["lime"], width=2.5),
            ),
            customdata=anom_in_pca[["Country", "Cluster_name", "anomaly_score"]].values,
            hovertemplate=(
                "<b>%{customdata[0]}</b><br>"
                "%{customdata[1]}<br>"
                "PC1: %{x:.2f}  &middot;  PC2: %{y:.2f}<br>"
                "Anomaly score: %{customdata[2]:.3f}"
                "<extra>Anomaly</extra>"
            ),
        )
    )

# Palestine — starred
pal = pca_df[pca_df["Country"] == "Palestine"]
if not pal.empty:
    fig.add_trace(
        go.Scatter(
            x=pal["PC1"],
            y=pal["PC2"],
            mode="markers+text",
            name="Palestine",
            marker=dict(
                size=22,
                color=COLORS["lime"],
                symbol="star",
                line=dict(color=COLORS["ink"], width=1.8),
            ),
            text=["Palestine"],
            textposition="top center",
            textfont=dict(family=FONTS["mono"], size=11, color=COLORS["ink"]),
            customdata=pal[["Cluster_name"]].values,
            hovertemplate=(
                "<b>Palestine</b><br>"
                "%{customdata[0]}<br>"
                "PC1: %{x:.2f}  &middot;  PC2: %{y:.2f}"
                "<extra></extra>"
            ),
        )
    )

fig.update_layout(
    paper_bgcolor=COLORS["cream_deep"],
    plot_bgcolor=COLORS["cream_deep"],
    xaxis=dict(
        title=dict(text="PC1", font=dict(family=FONTS["mono"], size=11, color=COLORS["ink_mute"])),
        gridcolor=COLORS["rule"],
        zerolinecolor=COLORS["rule"],
        tickfont=dict(family=FONTS["mono"], size=10, color=COLORS["ink_mute"]),
        showline=True, linecolor=COLORS["ink"], linewidth=1,
    ),
    yaxis=dict(
        title=dict(text="PC2", font=dict(family=FONTS["mono"], size=11, color=COLORS["ink_mute"])),
        gridcolor=COLORS["rule"],
        zerolinecolor=COLORS["rule"],
        tickfont=dict(family=FONTS["mono"], size=10, color=COLORS["ink_mute"]),
        showline=True, linecolor=COLORS["ink"], linewidth=1,
    ),
    margin=dict(l=20, r=20, t=20, b=20),
    height=580,
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
# COUNTRY PICKER + DETAIL CARD
# ============================================================
st.markdown(
    '<div class="eyebrow"><span class="marker"></span><span>Inspect a country</span></div>',
    unsafe_allow_html=True,
)

country_list = sorted(pca_df["Country"].dropna().unique().tolist())
# Default to Palestine if available
default_idx = country_list.index("Palestine") if "Palestine" in country_list else 0

selected = st.selectbox(
    "Pick a country",
    options=country_list,
    index=default_idx,
)

row = pca_df[pca_df["Country"] == selected].iloc[0]
sel_iso = row.get("ISO", "—")
sel_cluster = int(row["Cluster"]) if pd.notna(row["Cluster"]) else None
sel_cluster_name = row.get("Cluster_name", "—")
sel_is_anom = bool(row["is_anomaly"])
sel_pc1 = float(row["PC1"])
sel_pc2 = float(row["PC2"])
sel_score = float(row["anomaly_score"])
sel_income = row.get("Income group", "—")
sel_region = row.get("WHO Region", "—")

# Re-draw the scatter with the selected country highlighted (small inset)
fig_inset = go.Figure()

# Faded background — all countries as small grey dots
fig_inset.add_trace(
    go.Scatter(
        x=pca_df["PC1"],
        y=pca_df["PC2"],
        mode="markers",
        marker=dict(
            size=6,
            color=COLORS["ink_faint"] if "ink_faint" in COLORS else "#8A8880",
            opacity=0.35,
        ),
        showlegend=False,
        hoverinfo="skip",
    )
)

# Same-cluster peers — colored
peers = pca_df[(pca_df["Cluster"] == sel_cluster) & (pca_df["Country"] != selected)]
fig_inset.add_trace(
    go.Scatter(
        x=peers["PC1"],
        y=peers["PC2"],
        mode="markers",
        name=f"Same cluster ({sel_cluster_name})",
        marker=dict(
            size=10,
            color=CLUSTER_COLORS.get(sel_cluster, COLORS["ink_mute"]),
            line=dict(color=COLORS["ink"], width=0.6),
            opacity=0.85,
        ),
        customdata=peers[["Country"]].values,
        hovertemplate="<b>%{customdata[0]}</b><extra></extra>",
    )
)

# The selected country itself — big lime marker
fig_inset.add_trace(
    go.Scatter(
        x=[sel_pc1],
        y=[sel_pc2],
        mode="markers+text",
        name=selected,
        marker=dict(
            size=24,
            color=COLORS["lime"],
            symbol="star" if selected == "Palestine" else ("diamond" if sel_is_anom else "circle"),
            line=dict(color=COLORS["ink"], width=2),
        ),
        text=[selected],
        textposition="top center",
        textfont=dict(family=FONTS["mono"], size=11, color=COLORS["ink"]),
        hoverinfo="skip",
    )
)

fig_inset.update_layout(
    paper_bgcolor=COLORS["cream_deep"],
    plot_bgcolor=COLORS["cream_deep"],
    xaxis=dict(
        title=dict(text="PC1", font=dict(family=FONTS["mono"], size=10, color=COLORS["ink_mute"])),
        gridcolor=COLORS["rule"], zerolinecolor=COLORS["rule"],
        tickfont=dict(family=FONTS["mono"], size=9, color=COLORS["ink_mute"]),
        showline=True, linecolor=COLORS["ink"], linewidth=1,
    ),
    yaxis=dict(
        title=dict(text="PC2", font=dict(family=FONTS["mono"], size=10, color=COLORS["ink_mute"])),
        gridcolor=COLORS["rule"], zerolinecolor=COLORS["rule"],
        tickfont=dict(family=FONTS["mono"], size=9, color=COLORS["ink_mute"]),
        showline=True, linecolor=COLORS["ink"], linewidth=1,
    ),
    margin=dict(l=20, r=20, t=20, b=20),
    height=420,
    legend=dict(
        orientation="h", yanchor="bottom", y=-0.22, xanchor="left", x=0,
        font=dict(family=FONTS["mono"], size=10, color=COLORS["ink_mute"]),
        bgcolor="rgba(0,0,0,0)",
    ),
)

col_chart, col_card = st.columns([3, 2])

with col_chart:
    st.plotly_chart(fig_inset, use_container_width=True, config={"displaylogo": False})

with col_card:
    tag_class = "sub anomaly" if sel_is_anom else "sub"
    tag_text = "Anomaly" if sel_is_anom else f"Cluster {sel_cluster} / {sel_cluster_name}"

    st.markdown(
        f"""
        <div class="detail-card">
            <h3>{selected}</h3>
            <span class="{tag_class}">{tag_text}</span>
            <div class="meta">
                <strong>ISO:</strong> {sel_iso}<br>
                <strong>Cluster:</strong> {sel_cluster} &mdash; {sel_cluster_name}<br>
                <strong>WHO region:</strong> {sel_region}<br>
                <strong>Income group:</strong> {sel_income}<br>
                <strong>PC1:</strong> {sel_pc1:+.2f}  &middot;  <strong>PC2:</strong> {sel_pc2:+.2f}<br>
                <strong>Anomaly score:</strong> {sel_score:+.3f}
                ({"flagged" if sel_is_anom else "not flagged"})
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

# ============================================================
# FULL ANOMALY LIST
# ============================================================
st.markdown(
    '<div class="eyebrow" style="margin-top:36px;"><span class="marker"></span><span>All anomalies</span></div>',
    unsafe_allow_html=True,
)
st.markdown(
    f'<div class="sub-eyebrow">{len(anom_df)} countries flagged by Isolation Forest &middot; '
    'sorted by anomaly score (most anomalous first)</div>',
    unsafe_allow_html=True,
)

# Sort: more positive score = more anomalous (sklearn convention varies, but in
# this file the flagged rows tend to have higher scores)
anom_sorted = anom_df.sort_values("anomaly_score", ascending=False)

rows_html = []
for _, ar in anom_sorted.iterrows():
    rows_html.append(
        f"""
        <div class="anomaly-row">
            <span class="name">{ar['Country']}</span>
            <span class="region">{ar.get('WHO Region', '')}</span>
            <span class="score">score {ar['anomaly_score']:+.3f}</span>
        </div>
        """
    )
st.markdown("".join(rows_html), unsafe_allow_html=True)

# ============================================================
# FOOTER NOTE
# ============================================================
st.markdown(
    f"""
    <div style="margin-top:60px; padding-top:24px; border-top:1px solid {COLORS['rule']};
                font-family:{FONTS['mono']}; font-size:10px; letter-spacing:0.12em;
                text-transform:uppercase; color:{COLORS['ink_mute']};">
        PCA &middot; 27 indicators &rarr; 2D &middot; Isolation Forest anomaly detection &middot; K-Means K=4
    </div>
    """,
    unsafe_allow_html=True,
)