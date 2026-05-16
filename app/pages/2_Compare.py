"""
Page 2 — Compare
Radar chart comparison: Palestine vs. up to 4 peer countries across 27
measurements, grouped into 6 readable themes.

Story: a 27-axis radar is unreadable, so we group the measurements into
six WHO-style themes (Legislation, Enforcement, Infrastructure, Vehicle
safety, Post-crash, Data quality). Each theme score is the mean of its
measurements, scored 0 to 1 across all 171 countries — so "1.0 on
Legislation" means strongest legislative coverage globally.

Inputs:
    data/processed/country_features_display.csv  (171 × 27, original units)
    data/processed/country_clusters.csv          (ISO, Cluster, Cluster_name)
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
    page_title="Compare — Road Safety Explorer",
    page_icon="◯",
    layout="wide",
    initial_sidebar_state="collapsed",
)

apply_plotly_theme()
render_sidebar()

# ============================================================
# ISO3 → NAME LOOKUP (same as Atlas — embedded so we never depend on CSVs)
# ============================================================
ISO3_TO_NAME = {
    "AFG": "Afghanistan", "ALB": "Albania", "DZA": "Algeria", "AND": "Andorra",
    "AGO": "Angola", "ATG": "Antigua and Barbuda", "ARG": "Argentina",
    "ARM": "Armenia", "AUS": "Australia", "AUT": "Austria", "AZE": "Azerbaijan",
    "BHS": "Bahamas", "BHR": "Bahrain", "BGD": "Bangladesh", "BRB": "Barbados",
    "BLR": "Belarus", "BEL": "Belgium", "BLZ": "Belize", "BEN": "Benin",
    "BTN": "Bhutan", "BOL": "Bolivia", "BIH": "Bosnia and Herzegovina",
    "BWA": "Botswana", "BRA": "Brazil", "BRN": "Brunei", "BGR": "Bulgaria",
    "BFA": "Burkina Faso", "BDI": "Burundi", "CPV": "Cabo Verde",
    "KHM": "Cambodia", "CMR": "Cameroon", "CAN": "Canada",
    "CAF": "Central African Republic", "TCD": "Chad", "CHL": "Chile",
    "CHN": "China", "COL": "Colombia", "COM": "Comoros", "COG": "Congo",
    "COD": "DR Congo", "CRI": "Costa Rica", "CIV": "Côte d'Ivoire",
    "HRV": "Croatia", "CUB": "Cuba", "CYP": "Cyprus", "CZE": "Czechia",
    "DNK": "Denmark", "DJI": "Djibouti", "DMA": "Dominica",
    "DOM": "Dominican Republic", "ECU": "Ecuador", "EGY": "Egypt",
    "SLV": "El Salvador", "GNQ": "Equatorial Guinea", "ERI": "Eritrea",
    "EST": "Estonia", "SWZ": "Eswatini", "ETH": "Ethiopia", "FJI": "Fiji",
    "FIN": "Finland", "FRA": "France", "GAB": "Gabon", "GMB": "Gambia",
    "GEO": "Georgia", "DEU": "Germany", "GHA": "Ghana", "GRC": "Greece",
    "GRD": "Grenada", "GTM": "Guatemala", "GIN": "Guinea",
    "GNB": "Guinea-Bissau", "GUY": "Guyana", "HTI": "Haiti", "HND": "Honduras",
    "HUN": "Hungary", "ISL": "Iceland", "IND": "India", "IDN": "Indonesia",
    "IRN": "Iran", "IRQ": "Iraq", "IRL": "Ireland", "ISR": "Israel",
    "ITA": "Italy", "JAM": "Jamaica", "JPN": "Japan", "JOR": "Jordan",
    "KAZ": "Kazakhstan", "KEN": "Kenya", "KIR": "Kiribati", "KWT": "Kuwait",
    "KGZ": "Kyrgyzstan", "LAO": "Laos", "LVA": "Latvia", "LBN": "Lebanon",
    "LSO": "Lesotho", "LBR": "Liberia", "LBY": "Libya", "LIE": "Liechtenstein",
    "LTU": "Lithuania", "LUX": "Luxembourg", "MDG": "Madagascar",
    "MWI": "Malawi", "MYS": "Malaysia", "MDV": "Maldives", "MLI": "Mali",
    "MLT": "Malta", "MHL": "Marshall Islands", "MRT": "Mauritania",
    "MUS": "Mauritius", "MEX": "Mexico", "FSM": "Micronesia", "MDA": "Moldova",
    "MCO": "Monaco", "MNG": "Mongolia", "MNE": "Montenegro", "MAR": "Morocco",
    "MOZ": "Mozambique", "MMR": "Myanmar", "NAM": "Namibia", "NRU": "Nauru",
    "NPL": "Nepal", "NLD": "Netherlands", "NZL": "New Zealand",
    "NIC": "Nicaragua", "NER": "Niger", "NGA": "Nigeria",
    "PRK": "North Korea", "MKD": "North Macedonia", "NOR": "Norway",
    "OMN": "Oman", "PAK": "Pakistan", "PLW": "Palau", "PSE": "Palestine",
    "PAN": "Panama", "PNG": "Papua New Guinea", "PRY": "Paraguay",
    "PER": "Peru", "PHL": "Philippines", "POL": "Poland", "PRT": "Portugal",
    "QAT": "Qatar", "ROU": "Romania", "RUS": "Russia", "RWA": "Rwanda",
    "KNA": "Saint Kitts and Nevis", "LCA": "Saint Lucia",
    "VCT": "Saint Vincent and the Grenadines", "WSM": "Samoa",
    "SMR": "San Marino", "STP": "São Tomé and Príncipe", "SAU": "Saudi Arabia",
    "SEN": "Senegal", "SRB": "Serbia", "SYC": "Seychelles",
    "SLE": "Sierra Leone", "SGP": "Singapore", "SVK": "Slovakia",
    "SVN": "Slovenia", "SLB": "Solomon Islands", "SOM": "Somalia",
    "ZAF": "South Africa", "KOR": "South Korea", "SSD": "South Sudan",
    "ESP": "Spain", "LKA": "Sri Lanka", "SDN": "Sudan", "SUR": "Suriname",
    "SWE": "Sweden", "CHE": "Switzerland", "SYR": "Syria", "TJK": "Tajikistan",
    "TZA": "Tanzania", "THA": "Thailand", "TLS": "Timor-Leste", "TGO": "Togo",
    "TON": "Tonga", "TTO": "Trinidad and Tobago", "TUN": "Tunisia",
    "TUR": "Türkiye", "TKM": "Turkmenistan", "TUV": "Tuvalu", "UGA": "Uganda",
    "UKR": "Ukraine", "ARE": "United Arab Emirates", "GBR": "United Kingdom",
    "USA": "United States", "URY": "Uruguay", "UZB": "Uzbekistan",
    "VUT": "Vanuatu", "VEN": "Venezuela", "VNM": "Vietnam", "YEM": "Yemen",
    "ZMB": "Zambia", "ZWE": "Zimbabwe", "TWN": "Taiwan", "HKG": "Hong Kong",
    "COK": "Cook Islands", "NIU": "Niue",
}


def name_of(iso3: str) -> str:
    return ISO3_TO_NAME.get(iso3, iso3)


# ============================================================
# THEME GROUPING — match measurement names by keyword
# Each theme's score is the mean of its matched measurements
# (after 0–1 scaling).
# ============================================================
THEME_KEYWORDS = {
    "Legislation": [
        "law", "legislation", "limit", "bac", "speed limit",
        "helmet", "seatbelt", "seat-belt", "child restraint",
        "drink", "drink-driving", "drunk", "mobile phone",
    ],
    "Enforcement": [
        "enforcement", "enforced", "perceived enforcement",
    ],
    "Infrastructure": [
        "infrastructure", "road design", "audit", "star rating",
        "irap", "safe system", "pedestrian", "cycl",
    ],
    "Vehicle safety": [
        "vehicle", "inspection", "standards", "ncap",
        "abs", "airbag", "electronic stability",
    ],
    "Post-crash care": [
        "emergency", "ems", "trauma", "post-crash", "post crash",
        "ambulance", "hospital", "rehabilitation",
    ],
    "Data quality": [
        "registration", "vital", "reporting", "completeness",
        "death registration", "icd", "data quality",
    ],
}


def classify_indicator(col_name: str) -> str | None:
    """Map a measurement column to one of the six themes, or None if unmatched."""
    lower = col_name.lower()
    for theme, kws in THEME_KEYWORDS.items():
        for kw in kws:
            if kw in lower:
                return theme
    return None


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

    .note-box {{
        background: {COLORS['cream_deep']};
        border-left: 3px solid {COLORS['lime']};
        padding: 14px 20px;
        margin: 16px 0 28px;
        font-family: {FONTS['body']};
        font-size: 13px;
        line-height: 1.55;
        color: {COLORS['ink_mute']};
    }}
    .note-box strong {{ color: {COLORS['ink']}; font-weight: 500; }}

    .country-tag {{
        display: inline-block;
        padding: 5px 11px;
        margin: 0 6px 6px 0;
        font-family: {FONTS['mono']};
        font-size: 11px;
        border: 1px solid {COLORS['ink']};
        background: {COLORS['cream']};
        color: {COLORS['ink']};
    }}
    .country-tag.palestine {{
        background: {COLORS['lime']}; color: {COLORS['ink']};
        border-color: {COLORS['ink']};
    }}

    .sub-eyebrow {{
        font-family: {FONTS['mono']}; font-size: 10px;
        letter-spacing: 0.15em; text-transform: uppercase;
        color: {COLORS['ink_mute']};
        margin: 28px 0 10px;
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
    clusters_path = DATA_DIR / "country_clusters.csv"
    features_path = DATA_DIR / "country_features_display.csv"

    if not clusters_path.exists():
        st.error(f"Missing file: {clusters_path}")
        st.stop()
    if not features_path.exists():
        st.error(f"Missing file: {features_path}")
        st.stop()

    clusters = pd.read_csv(clusters_path)
    features = pd.read_csv(features_path)

    def find_iso_col(df):
        for c in ["ISO", "iso", "iso3", "Code", "code", "Country code"]:
            if c in df.columns:
                return c
        return df.columns[0]

    clusters = clusters.rename(columns={find_iso_col(clusters): "ISO"})
    features = features.rename(columns={find_iso_col(features): "ISO"})

    if "Cluster_name" not in clusters.columns and "Cluster" in clusters.columns:
        clusters["Cluster_name"] = clusters["Cluster"].map(CLUSTER_NAMES)

    return clusters, features


clusters_df, features_df = load_data()
df = clusters_df.merge(features_df, on="ISO", how="left")
df["Country"] = df["ISO"].map(name_of)

# Identify measurement columns
NON_INDICATOR = {"ISO", "Cluster", "Cluster_name", "Country", "Country name", "Entity", "Name"}
indicator_cols = [
    c for c in df.columns
    if c not in NON_INDICATOR and pd.api.types.is_numeric_dtype(df[c])
]

# ============================================================
# BUILD THE THEME SCORES
# ============================================================
# 1. Scale each measurement to 0–1 across all 171 countries
normalized = df[indicator_cols].copy()
for col in indicator_cols:
    col_min = normalized[col].min(skipna=True)
    col_max = normalized[col].max(skipna=True)
    if pd.notna(col_min) and pd.notna(col_max) and col_max > col_min:
        normalized[col] = (normalized[col] - col_min) / (col_max - col_min)
    else:
        normalized[col] = 0.0

# 2. Classify each measurement into a theme
theme_to_indicators = {theme: [] for theme in THEME_KEYWORDS}
unclassified = []
for col in indicator_cols:
    theme = classify_indicator(col)
    if theme is not None:
        theme_to_indicators[theme].append(col)
    else:
        unclassified.append(col)

# 3. If a theme came up empty, drop it from the radar (keeps the chart honest)
theme_to_indicators = {t: cols for t, cols in theme_to_indicators.items() if cols}

# 4. Mean per theme per country (skipna so missing data doesn't sink the score)
theme_scores = pd.DataFrame(index=df.index)
theme_scores["Country"] = df["Country"]
theme_scores["ISO"] = df["ISO"]
theme_scores["Cluster"] = df["Cluster"]
theme_scores["Cluster_name"] = df["Cluster_name"]
for theme, cols in theme_to_indicators.items():
    theme_scores[theme] = normalized[cols].mean(axis=1, skipna=True)

# ============================================================
# HEADER
# ============================================================
st.markdown(
    """
    <div class="eyebrow"><span class="marker"></span><span>02 / Compare</span></div>
    <h1 class="page-title">Palestine, <span class="accent">in profile.</span></h1>
    <p class="page-lede">
        Compare any country's road-safety profile against up to four peers
        across six themes. Each axis is scored 0 (lowest globally) to 1
        (highest globally) — so a longer reach on an axis means stronger
        performance compared to every other country in the dataset.
    </p>
    """,
    unsafe_allow_html=True,
)

# ============================================================
# CONTROLS
# ============================================================
country_list = sorted(theme_scores["Country"].dropna().unique().tolist())

col_a, col_b = st.columns([1, 2])

with col_a:
    # Palestine is the anchor and can't be removed via the multiselect
    # (kept always-visible); the multiselect picks up to 4 peers
    anchor_options = country_list
    default_anchor = "Palestine" if "Palestine" in anchor_options else anchor_options[0]
    anchor = st.selectbox(
        "Anchor country",
        options=anchor_options,
        index=anchor_options.index(default_anchor),
    )

with col_b:
    peer_options = [c for c in country_list if c != anchor]
    peers = st.multiselect(
        "Compare against (up to 4 peers)",
        options=peer_options,
        default=[],
        max_selections=4,
    )

selected_countries = [anchor] + peers

# Show the selection as styled chips
tags_html = ""
for c in selected_countries:
    cls = "country-tag palestine" if c == anchor else "country-tag"
    tags_html += f'<span class="{cls}">{c}</span>'
st.markdown(
    f'<div style="margin-top:6px;">{tags_html}</div>',
    unsafe_allow_html=True,
)

# Note about scoring
st.markdown(
    """
    <div class="note-box">
        <strong>Reading the chart:</strong> each axis is the country's
        score on that theme — 0 means lowest globally, 1 means highest
        globally. Themes are averages of related road-safety measurements.
    </div>
    """,
    unsafe_allow_html=True,
)

# ============================================================
# BUILD THE RADAR
# ============================================================
theme_axes = list(theme_to_indicators.keys())

fig = go.Figure()

# Color logic: anchor = lime, peers = ink shades / group colors
PEER_PALETTE = [
    COLORS["ink"],
    COLORS["ink_mute"],
    "#7a6d5c",  # warm taupe
    "#3a3a38",  # near-ink
]

for i, country in enumerate(selected_countries):
    row = theme_scores[theme_scores["Country"] == country]
    if row.empty:
        continue
    row = row.iloc[0]

    values = [float(row[t]) if pd.notna(row[t]) else 0.0 for t in theme_axes]
    # close the polygon
    radar_vals = values + [values[0]]
    radar_axes = theme_axes + [theme_axes[0]]

    is_anchor = (country == anchor)
    line_color = COLORS["lime"] if is_anchor else PEER_PALETTE[(i - 1) % len(PEER_PALETTE)]
    fill_color = (
        "rgba(198, 255, 61, 0.25)"  # lime translucent
        if is_anchor
        else "rgba(10, 10, 10, 0.05)"
    )

    cluster_label = row.get("Cluster_name", "")

    fig.add_trace(
        go.Scatterpolar(
            r=radar_vals,
            theta=radar_axes,
            name=f"{country} — {cluster_label}" if cluster_label else country,
            mode="lines+markers",
            line=dict(color=line_color, width=2.5 if is_anchor else 1.8),
            marker=dict(color=line_color, size=7 if is_anchor else 5,
                        line=dict(color=COLORS["ink"], width=0.6)),
            fill="toself",
            fillcolor=fill_color,
            hovertemplate=(
                f"<b>{country}</b><br>"
                "%{theta}: %{r:.2f}"
                "<extra></extra>"
            ),
        )
    )

fig.update_layout(
    polar=dict(
        bgcolor=COLORS["cream_deep"],
        radialaxis=dict(
            visible=True,
            range=[0, 1],
            tickvals=[0.25, 0.5, 0.75, 1.0],
            ticktext=[".25", ".50", ".75", "1.0"],
            tickfont=dict(family=FONTS["mono"], size=9, color=COLORS["ink_mute"]),
            gridcolor=COLORS["rule"],
            linecolor=COLORS["rule"],
            angle=90,
        ),
        angularaxis=dict(
            tickfont=dict(family=FONTS["mono"], size=11, color=COLORS["ink"]),
            gridcolor=COLORS["rule"],
            linecolor=COLORS["ink"],
        ),
    ),
    paper_bgcolor=COLORS["cream"],
    plot_bgcolor=COLORS["cream"],
    height=600,
    margin=dict(l=60, r=60, t=40, b=80),
    showlegend=True,
    legend=dict(
        orientation="h",
        yanchor="bottom", y=-0.18,
        xanchor="center", x=0.5,
        font=dict(family=FONTS["mono"], size=10, color=COLORS["ink_mute"]),
        bgcolor="rgba(0,0,0,0)",
    ),
)

st.plotly_chart(fig, use_container_width=True, config={"displaylogo": False})

# ============================================================
# THEME SCORE TABLE
# ============================================================
st.markdown(
    '<div class="eyebrow"><span class="marker"></span><span>Theme scores</span></div>',
    unsafe_allow_html=True,
)
st.markdown(
    '<div class="sub-eyebrow">Scored 0 (lowest globally) to 1 (highest globally), across all 171 countries</div>',
    unsafe_allow_html=True,
)

table_rows = []
for country in selected_countries:
    row = theme_scores[theme_scores["Country"] == country]
    if row.empty:
        continue
    row = row.iloc[0]
    table_row = {"Country": country, "Group": row.get("Cluster_name", "—")}
    for t in theme_axes:
        v = row[t]
        table_row[t] = f"{v:.2f}" if pd.notna(v) else "—"
    table_rows.append(table_row)

st.dataframe(
    pd.DataFrame(table_rows),
    use_container_width=True,
    hide_index=True,
)

# ============================================================
# WHAT'S IN EACH THEME (expander)
# ============================================================
with st.expander("How themes are built (which measurements go into each)"):
    for theme, cols in theme_to_indicators.items():
        st.markdown(f"**{theme}** ({len(cols)} measurements)")
        for c in cols:
            st.markdown(f"- {c}")
    if unclassified:
        st.markdown("**Unclassified** (not included in any theme)")
        for c in unclassified:
            st.markdown(f"- {c}")

# ============================================================
# FOOTER NOTE — technical methodology stays here only
# ============================================================
st.markdown(
    f"""
    <div style="margin-top:60px; padding-top:24px; border-top:1px solid {COLORS['rule']};
                font-family:{FONTS['mono']}; font-size:10px; letter-spacing:0.12em;
                text-transform:uppercase; color:{COLORS['ink_mute']};">
        WHO Global Status Report 2023 &middot; 6 themes &middot; 27 min-max normalized indicators &middot; 171 countries
    </div>
    """,
    unsafe_allow_html=True,
)