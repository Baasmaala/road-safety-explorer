"""
Page 4 — Trends
Per-country fatality time series 1990–2019 with 3-year projection
(with likely-range band) and unusual years flagged.

Story: each country has its own fatality trajectory. Some climb, some fall,
some swing wildly. The model fits each country's series and projects 3
years ahead. Years that deviate sharply from the country's own trend
are flagged automatically.

Inputs:
    data/processed/country_forecasts.csv        (Entity, Code, Year, Deaths,
                                                 Historical_Population, DeathRate,
                                                 Type, HW_Forecast, HW_CI_Lower/Upper, ...)
    data/processed/country_year_anomalies.csv   (Entity, Code, Year, DeathRate,
                                                 Fitted, Residual, Z_Score, Direction)
"""

import sys
from pathlib import Path

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

# Make utils.* importable when running via `streamlit run app/app.py`
APP_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(APP_DIR))
from utils.theme import COLORS, CLUSTER_COLORS, CLUSTER_NAMES, FONTS, apply_plotly_theme
from utils.layout import render_sidebar

# ============================================================
# PAGE CONFIG
# ============================================================
st.set_page_config(
    page_title="Trends — Road Safety Explorer",
    page_icon="◯",
    layout="wide",
    initial_sidebar_state="collapsed",
)

apply_plotly_theme()
render_sidebar()

# ============================================================
# STYLES — match the other pages
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

    .stRadio > label, .stSelectbox > label, .stMultiSelect > label {{
        font-family: {FONTS['mono']} !important;
        font-size: 10px !important; letter-spacing: 0.15em !important;
        text-transform: uppercase !important; color: {COLORS['ink_mute']} !important;
    }}
    [data-baseweb="select"] > div {{
        background: {COLORS['cream']} !important;
        border: 1.5px solid {COLORS['ink']} !important;
        border-radius: 0 !important;
    }}

    .sub-eyebrow {{
        font-family: {FONTS['mono']}; font-size: 10px;
        letter-spacing: 0.15em; text-transform: uppercase;
        color: {COLORS['ink_mute']};
        margin: 28px 0 10px;
    }}

    .stat-strip {{
        display: grid; grid-template-columns: repeat(4, 1fr);
        gap: 0;
        border-top: 1.5px solid {COLORS['ink']};
        border-bottom: 1.5px solid {COLORS['ink']};
        margin: 16px 0 32px;
    }}
    .stat-cell {{
        padding: 22px 24px 22px 0;
        border-right: 1px solid {COLORS['rule']};
    }}
    .stat-cell:first-child {{ padding-left: 0; }}
    .stat-cell:not(:first-child) {{ padding-left: 24px; }}
    .stat-cell:last-child {{ border-right: none; }}
    .stat-num {{
        font-family: {FONTS['display']};
        font-size: 32px; font-weight: 500;
        letter-spacing: -0.02em; color: {COLORS['ink']};
    }}
    .stat-label {{
        font-family: {FONTS['mono']}; font-size: 10px;
        letter-spacing: 0.12em; text-transform: uppercase;
        color: {COLORS['ink_mute']}; margin-top: 8px;
    }}

    .anomaly-row {{
        display: flex; justify-content: space-between; align-items: center;
        padding: 10px 16px;
        border: 1px solid {COLORS['rule']};
        background: {COLORS['cream_deep']};
        margin-bottom: 6px;
        font-family: {FONTS['mono']};
        font-size: 11px;
    }}
    .anomaly-row .year {{
        font-family: {FONTS['display']}; font-size: 18px; font-weight: 500;
        color: {COLORS['ink']};
    }}
    .anomaly-row .dir {{
        padding: 3px 9px;
        font-size: 9px;
        letter-spacing: 0.12em;
        text-transform: uppercase;
    }}
    .anomaly-row .dir.above {{
        background: {COLORS['lime']}; color: {COLORS['ink']};
    }}
    .anomaly-row .dir.below {{
        background: {COLORS['ink']}; color: {COLORS['lime']};
    }}
    .anomaly-row .meta {{
        color: {COLORS['ink_mute']};
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
    fc_path = DATA_DIR / "country_forecasts.csv"
    an_path = DATA_DIR / "country_year_anomalies.csv"

    if not fc_path.exists():
        st.error(f"Missing file: {fc_path}")
        st.stop()
    if not an_path.exists():
        st.error(f"Missing file: {an_path}")
        st.stop()

    fc = pd.read_csv(fc_path)
    an = pd.read_csv(an_path)

    # Type lowercase for safety
    fc["Type"] = fc["Type"].astype(str).str.lower()

    return fc, an


fc_df, anom_df = load_data()

# ============================================================
# HEADER
# ============================================================
st.markdown(
    """
    <div class="eyebrow"><span class="marker"></span><span>04 / Trends</span></div>
    <h1 class="page-title">Three decades, <span class="accent">projected ahead.</span></h1>
    <p class="page-lede">
        Per-country road-fatality trajectories from 1990 to 2019, with a
        3-year projection based on past trend and a likely-range band.
        Years where deaths spiked or dropped unusually compared to the
        country's own trend are flagged automatically.
    </p>
    """,
    unsafe_allow_html=True,
)

# ============================================================
# CONTROLS
# ============================================================
country_list = sorted(fc_df["Entity"].dropna().unique().tolist())
default_country = "Palestine" if "Palestine" in country_list else country_list[0]

col_a, col_b, col_c = st.columns([2, 3, 1])

with col_a:
    main_country = st.selectbox(
        "Anchor country",
        options=country_list,
        index=country_list.index(default_country),
    )

with col_b:
    peer_options = [c for c in country_list if c != main_country]
    peers = st.multiselect(
        "Overlay peers (up to 3)",
        options=peer_options,
        default=[],
        max_selections=3,
    )

with col_c:
    metric = st.radio(
        "Metric",
        options=["Per 100k", "Absolute"],
        index=0,
        horizontal=False,
    )

# ============================================================
# DATA HELPERS
# ============================================================
def get_country_series(country: str, metric: str) -> dict:
    """
    Pull a country's observed history + 3-year projection + likely range.
    Returns dict with x_obs, y_obs, x_fc, y_fc, ci_lo, ci_hi (or None if missing).
    """
    sub = fc_df[fc_df["Entity"] == country].sort_values("Year")
    if sub.empty:
        return None

    obs = sub[sub["Type"] == "observed"]
    fcr = sub[sub["Type"] == "forecast"]

    if metric == "Per 100k":
        y_obs = obs["DeathRate"].values
        y_fc = fcr["HW_Forecast"].values
        ci_lo = fcr["HW_CI_Lower"].values
        ci_hi = fcr["HW_CI_Upper"].values
        unit = "deaths per 100k"
    else:  # Absolute
        y_obs = obs["Deaths"].values
        # Estimate absolute projection: rate per 100k * last known population / 100k
        # using the final observed Historical_Population as the population baseline.
        pop_last = obs["Historical_Population"].dropna().iloc[-1] if not obs["Historical_Population"].dropna().empty else None
        if pop_last and pd.notna(pop_last):
            y_fc = fcr["HW_Forecast"].values * pop_last / 100000.0
            ci_lo = fcr["HW_CI_Lower"].values * pop_last / 100000.0
            ci_hi = fcr["HW_CI_Upper"].values * pop_last / 100000.0
        else:
            y_fc = ci_lo = ci_hi = None
        unit = "deaths"

    return {
        "x_obs": obs["Year"].values,
        "y_obs": y_obs,
        "x_fc": fcr["Year"].values,
        "y_fc": y_fc,
        "ci_lo": ci_lo,
        "ci_hi": ci_hi,
        "unit": unit,
    }


def get_anomalies(country: str) -> pd.DataFrame:
    """Pull the country's flagged unusual years."""
    return anom_df[anom_df["Entity"] == country].sort_values("Year")


# ============================================================
# BUILD THE MAIN CHART
# ============================================================
fig = go.Figure()

# Peer countries first (so they sit beneath the anchor visually)
PEER_PALETTE = [
    COLORS["ink_mute"],
    "#7a6d5c",
    "#3a3a38",
]

for i, peer in enumerate(peers):
    series = get_country_series(peer, metric)
    if series is None:
        continue
    line_color = PEER_PALETTE[i % len(PEER_PALETTE)]

    # observed
    fig.add_trace(
        go.Scatter(
            x=series["x_obs"],
            y=series["y_obs"],
            mode="lines",
            name=peer,
            line=dict(color=line_color, width=1.5),
            opacity=0.75,
            hovertemplate=f"<b>{peer}</b><br>Year %{{x}}<br>%{{y:,.2f}}<extra></extra>",
        )
    )
    # projection (dashed, same color)
    if series["y_fc"] is not None and len(series["y_fc"]) > 0:
        fig.add_trace(
            go.Scatter(
                x=series["x_fc"],
                y=series["y_fc"],
                mode="lines",
                name=f"{peer} projection",
                line=dict(color=line_color, width=1.5, dash="dot"),
                opacity=0.7,
                showlegend=False,
                hovertemplate=f"<b>{peer} (projection)</b><br>Year %{{x}}<br>%{{y:,.2f}}<extra></extra>",
            )
        )

# Anchor country — full treatment
anchor = get_country_series(main_country, metric)
if anchor is None:
    st.error(f"No data for {main_country}")
    st.stop()

# Likely-range band first so it sits behind the line
if anchor["ci_lo"] is not None and len(anchor["ci_lo"]) > 0:
    fig.add_trace(
        go.Scatter(
            x=list(anchor["x_fc"]) + list(anchor["x_fc"])[::-1],
            y=list(anchor["ci_hi"]) + list(anchor["ci_lo"])[::-1],
            fill="toself",
            fillcolor="rgba(198, 255, 61, 0.22)",  # lime translucent
            line=dict(color="rgba(0,0,0,0)"),
            name=f"{main_country} likely range",
            showlegend=True,
            hoverinfo="skip",
        )
    )

# Observed line
fig.add_trace(
    go.Scatter(
        x=anchor["x_obs"],
        y=anchor["y_obs"],
        mode="lines+markers",
        name=f"{main_country} observed",
        line=dict(color=COLORS["ink"], width=2.5),
        marker=dict(size=5, color=COLORS["ink"], line=dict(color=COLORS["cream"], width=0.5)),
        hovertemplate=f"<b>{main_country}</b><br>Year %{{x}}<br>%{{y:,.2f}}<extra></extra>",
    )
)

# Projection line — dashed lime
if anchor["y_fc"] is not None and len(anchor["y_fc"]) > 0:
    # Connect last observed to first projection so there's no visual gap
    x_bridge = [anchor["x_obs"][-1]] + list(anchor["x_fc"])
    y_bridge = [anchor["y_obs"][-1]] + list(anchor["y_fc"])
    fig.add_trace(
        go.Scatter(
            x=x_bridge,
            y=y_bridge,
            mode="lines+markers",
            name=f"{main_country} projection",
            line=dict(color=COLORS["lime"], width=2.8, dash="dot"),
            marker=dict(
                size=8, color=COLORS["lime"], symbol="diamond",
                line=dict(color=COLORS["ink"], width=1.2),
            ),
            hovertemplate=f"<b>{main_country} (projection)</b><br>Year %{{x}}<br>%{{y:,.2f}}<extra></extra>",
        )
    )

# Unusual-year markers on the anchor country
anchor_anoms = get_anomalies(main_country)
if not anchor_anoms.empty:
    # we want to plot at the actual observed value for that year
    obs_lookup = dict(zip(anchor["x_obs"], anchor["y_obs"]))
    anom_x, anom_y, anom_text, anom_color = [], [], [], []
    for _, ar in anchor_anoms.iterrows():
        yr = int(ar["Year"])
        if yr in obs_lookup:
            anom_x.append(yr)
            anom_y.append(obs_lookup[yr])
            direction = str(ar["Direction"])
            # Plain-English direction label
            dir_label = "spike above trend" if direction == "above_trend" else "drop below trend"
            anom_text.append(f"{yr} &middot; {dir_label}")
            # color matches direction
            anom_color.append(
                COLORS["lime"] if direction == "above_trend" else COLORS["ink"]
            )
    if anom_x:
        fig.add_trace(
            go.Scatter(
                x=anom_x,
                y=anom_y,
                mode="markers",
                name=f"{main_country} unusual years",
                marker=dict(
                    size=14,
                    color=anom_color,
                    symbol="circle-open",
                    line=dict(color=COLORS["lime"], width=2.5),
                ),
                text=anom_text,
                hovertemplate="<b>%{text}</b><extra></extra>",
            )
        )

# Vertical line at end of observed period
last_obs_year = int(max(anchor["x_obs"]))
fig.add_vline(
    x=last_obs_year,
    line=dict(color=COLORS["ink_mute"], width=1, dash="dash"),
    annotation_text=f"projection →",
    annotation_position="top",
    annotation=dict(
        font=dict(family=FONTS["mono"], size=10, color=COLORS["ink_mute"]),
    ),
)

fig.update_layout(
    paper_bgcolor=COLORS["cream_deep"],
    plot_bgcolor=COLORS["cream_deep"],
    xaxis=dict(
        title=dict(text="Year", font=dict(family=FONTS["mono"], size=11, color=COLORS["ink_mute"])),
        gridcolor=COLORS["rule"], zerolinecolor=COLORS["rule"],
        tickfont=dict(family=FONTS["mono"], size=10, color=COLORS["ink_mute"]),
        showline=True, linecolor=COLORS["ink"], linewidth=1,
        dtick=5,
    ),
    yaxis=dict(
        title=dict(
            text=anchor["unit"],
            font=dict(family=FONTS["mono"], size=11, color=COLORS["ink_mute"]),
        ),
        gridcolor=COLORS["rule"], zerolinecolor=COLORS["rule"],
        tickfont=dict(family=FONTS["mono"], size=10, color=COLORS["ink_mute"]),
        showline=True, linecolor=COLORS["ink"], linewidth=1,
    ),
    margin=dict(l=20, r=20, t=30, b=20),
    height=540,
    legend=dict(
        orientation="h",
        yanchor="bottom", y=-0.22,
        xanchor="left", x=0,
        font=dict(family=FONTS["mono"], size=10, color=COLORS["ink_mute"]),
        bgcolor="rgba(0,0,0,0)",
    ),
    hovermode="x unified",
)

st.plotly_chart(fig, use_container_width=True, config={"displaylogo": False})

# ============================================================
# AT-A-GLANCE STATS for the anchor country
# ============================================================
obs_y = anchor["y_obs"]
first_val = float(obs_y[0]) if len(obs_y) else None
last_val = float(obs_y[-1]) if len(obs_y) else None
peak_val = float(max(obs_y)) if len(obs_y) else None
peak_year = int(anchor["x_obs"][obs_y.argmax()]) if len(obs_y) else None
fc_y = anchor["y_fc"]
fc_last = float(fc_y[-1]) if (fc_y is not None and len(fc_y)) else None

if first_val is not None and last_val is not None and first_val != 0:
    change_pct = (last_val - first_val) / first_val * 100
    change_str = f"{change_pct:+.1f}%"
else:
    change_str = "—"

if last_val is not None and fc_last is not None and last_val != 0:
    proj_pct = (fc_last - last_val) / last_val * 100
    proj_str = f"{proj_pct:+.1f}%"
else:
    proj_str = "—"

unit_label = "deaths" if metric == "Absolute" else "/100k"

st.markdown(
    f"""
    <div class="stat-strip">
        <div class="stat-cell">
            <div class="stat-num">{first_val:,.1f}<span style="font-size:14px; color:{COLORS['ink_mute']}; margin-left:6px;">{unit_label}</span></div>
            <div class="stat-label">1990 baseline</div>
        </div>
        <div class="stat-cell">
            <div class="stat-num">{last_val:,.1f}<span style="font-size:14px; color:{COLORS['ink_mute']}; margin-left:6px;">{unit_label}</span></div>
            <div class="stat-label">{last_obs_year} latest observed</div>
        </div>
        <div class="stat-cell">
            <div class="stat-num">{change_str}</div>
            <div class="stat-label">Change since 1990</div>
        </div>
        <div class="stat-cell">
            <div class="stat-num">{proj_str}</div>
            <div class="stat-label">3-yr projected change</div>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

# ============================================================
# UNUSUAL YEARS for the anchor country
# ============================================================
st.markdown(
    '<div class="eyebrow"><span class="marker"></span><span>Unusual years</span></div>',
    unsafe_allow_html=True,
)

if anchor_anoms.empty:
    st.markdown(
        f'<div class="sub-eyebrow">No unusual years flagged for {main_country}.</div>',
        unsafe_allow_html=True,
    )
else:
    st.markdown(
        f'<div class="sub-eyebrow">{len(anchor_anoms)} year(s) flagged &middot; '
        'sorted by how far they deviated from the country\'s own trend (most extreme first)</div>',
        unsafe_allow_html=True,
    )

    sorted_anoms = anchor_anoms.assign(abs_z=anchor_anoms["Z_Score"].abs()) \
        .sort_values("abs_z", ascending=False)

    rows_html = []
    for _, ar in sorted_anoms.iterrows():
        direction = str(ar["Direction"])
        dir_class = "above" if direction == "above_trend" else "below"
        dir_label = "spike above trend" if direction == "above_trend" else "drop below trend"
        rows_html.append(
            f"""
            <div class="anomaly-row">
                <span class="year">{int(ar['Year'])}</span>
                <span class="dir {dir_class}">{dir_label}</span>
                <span class="meta">observed {ar['DeathRate']:.2f}/100k &middot; trend {ar['Fitted']:.2f} &middot; deviation {ar['Z_Score']:+.2f}σ</span>
            </div>
            """
        )
    st.markdown("".join(rows_html), unsafe_allow_html=True)

# ============================================================
# FOOTER NOTE — technical methodology stays here only
# ============================================================
st.markdown(
    f"""
    <div style="margin-top:60px; padding-top:24px; border-top:1px solid {COLORS['rule']};
                font-family:{FONTS['mono']}; font-size:10px; letter-spacing:0.12em;
                text-transform:uppercase; color:{COLORS['ink_mute']};">
        IHME Global Burden of Disease &middot; 1990&ndash;{last_obs_year} observed &middot;
        Holt-Winters 3-year forecast &middot; Z-score anomaly detection
    </div>
    """,
    unsafe_allow_html=True,
)