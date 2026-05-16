"""
Page 1 — Atlas
Global choropleth: every country colored by cluster (default) or a selected
indicator (toggle mode).

Story: the map shows the four K-Means clusters across the world. Below,
pick any country to see its cluster, who else is in that cluster, and how
its 27 indicators compare to the cluster average — so a viewer can see
*why* each country is in its group.

Inputs:
    data/processed/country_clusters.csv         (ISO, Cluster, Cluster_name)
    data/processed/country_features_display.csv (ISO + 27 original-unit indicators)
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
    page_title="Atlas — Road Safety Explorer",
    page_icon="◯",
    layout="wide",
    initial_sidebar_state="collapsed",
)


apply_plotly_theme()
render_sidebar()


# ============================================================
# ISO3 → COUNTRY NAME LOOKUP


# ============================================================
# ISO3 → COUNTRY NAME LOOKUP
# Embedded so we never depend on the CSVs having a name column.
# Covers every UN country + WHO-reported territory.
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
    """Return the country's display name, falling back to the ISO code itself."""
    return ISO3_TO_NAME.get(iso3, iso3)


# ============================================================
# STYLES — keep the homepage's bold modernist feel
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
    
    /* eyebrow + heading typography */
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

    /* Streamlit widget styling — match the brand */
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

    /* detail card */
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
        padding: 5px 11px; display: inline-block; margin-bottom: 0;
    }}

    /* country chips — for "other countries in this cluster" */
    .chip-row {{
        display: flex; flex-wrap: wrap; gap: 8px;
        margin: 14px 0 6px;
    }}
    .chip {{
        font-family: {FONTS['mono']}; font-size: 11px;
        letter-spacing: 0.04em;
        padding: 6px 12px;
        border: 1px solid {COLORS['ink']};
        background: {COLORS['cream']};
        color: {COLORS['ink']};
    }}
    .chip.self {{
        background: {COLORS['ink']}; color: {COLORS['lime']};
    }}

    /* small subheading */
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

    # normalize the ISO column name across both files
    def find_iso_col(df):
        for c in ["ISO", "iso", "iso3", "Code", "code", "Country code"]:
            if c in df.columns:
                return c
        return df.columns[0]

    clusters = clusters.rename(columns={find_iso_col(clusters): "ISO"})
    features = features.rename(columns={find_iso_col(features): "ISO"})

    # ensure Cluster_name exists (fallback to CLUSTER_NAMES dict if missing)
    if "Cluster_name" not in clusters.columns and "Cluster" in clusters.columns:
        clusters["Cluster_name"] = clusters["Cluster"].map(CLUSTER_NAMES)

    return clusters, features


clusters_df, features_df = load_data()

# Merge so we have everything in one place keyed by ISO
df = clusters_df.merge(features_df, on="ISO", how="left")

# Attach the country name from our embedded dict — overrides anything in the CSVs
df["Country"] = df["ISO"].map(name_of)

# Identify the indicator columns (numeric, not metadata)
NON_INDICATOR = {"ISO", "Cluster", "Cluster_name", "Country", "Country name", "Entity", "Name"}
indicator_cols = [c for c in df.columns if c not in NON_INDICATOR and pd.api.types.is_numeric_dtype(df[c])]

# ============================================================
# HEADER
# ============================================================
st.markdown(
    """
    <div class="eyebrow"><span class="marker"></span><span>01 / Atlas</span></div>
    <h1 class="page-title">Every country, <span class="accent">on a map.</span></h1>
    <p class="page-lede">
        171 countries grouped by their road-safety profile. Switch between cluster
        view and any single indicator. Below the map, pick a country to see who
        else is in its cluster and how its numbers compare to the cluster average.
    </p>
    """,
    unsafe_allow_html=True,
)

# ============================================================
# CONTROLS
# ============================================================
col_a, col_b = st.columns([1, 2])

with col_a:
    mode = st.radio(
        "Color mode",
        options=["Cluster", "Indicator"],
        index=0,
        horizontal=True,
    )

with col_b:
    if mode == "Indicator":
        selected_indicator = st.selectbox(
            "Pick an indicator",
            options=indicator_cols,
            index=0,
        )
    else:
        selected_indicator = None

# ============================================================
# BUILD THE CHOROPLETH
# ============================================================
fig = go.Figure()

if mode == "Cluster":
    for cluster_id in sorted(df["Cluster"].dropna().unique()):
        sub = df[df["Cluster"] == cluster_id]
        cluster_label = CLUSTER_NAMES.get(int(cluster_id), f"Cluster {int(cluster_id)}")
        fig.add_trace(
            go.Choropleth(
                locations=sub["ISO"],
                z=[1] * len(sub),
                locationmode="ISO-3",
                colorscale=[[0, CLUSTER_COLORS[int(cluster_id)]],
                            [1, CLUSTER_COLORS[int(cluster_id)]]],
                showscale=False,
                name=f"{int(cluster_id)} / {cluster_label}",
                showlegend=True,
                marker_line_color=COLORS["ink"],
                marker_line_width=0.4,
                hovertemplate=(
                    "<b>%{customdata[0]}</b><br>"
                    "Cluster " + str(int(cluster_id)) + " / " + cluster_label +
                    "<extra></extra>"
                ),
                customdata=sub[["Country"]].values,
            )
        )

else:
    valid = df.dropna(subset=[selected_indicator])
    fig.add_trace(
        go.Choropleth(
            locations=valid["ISO"],
            z=valid[selected_indicator],
            locationmode="ISO-3",
            colorscale=[
                [0.0, COLORS["cream_deep"]],
                [0.5, COLORS["lime"]],
                [1.0, COLORS["ink"]],
            ],
            marker_line_color=COLORS["ink"],
            marker_line_width=0.3,
            colorbar=dict(
                title=dict(
                    text=selected_indicator[:40] + ("…" if len(selected_indicator) > 40 else ""),
                    font=dict(family=FONTS["mono"], size=10, color=COLORS["ink_mute"]),
                ),
                tickfont=dict(family=FONTS["mono"], size=9, color=COLORS["ink_mute"]),
                outlinecolor=COLORS["ink"],
                outlinewidth=1,
                thickness=14,
                len=0.6,
            ),
            customdata=valid[["Country", "Cluster_name"]].values,
            hovertemplate=(
                "<b>%{customdata[0]}</b><br>"
                + selected_indicator + ": %{z:,.2f}<br>"
                "%{customdata[1]}"
                "<extra></extra>"
            ),
        )
    )

fig.update_layout(
    geo=dict(
        showframe=False,
        showcoastlines=False,
        showcountries=True,
        countrycolor=COLORS["ink"],
        landcolor=COLORS["land_nodata"] if "land_nodata" in COLORS else "#DDD8CC",
        bgcolor=COLORS["cream_deep"],
        projection_type="natural earth",
        showocean=False,
    ),
    paper_bgcolor=COLORS["cream_deep"],
    plot_bgcolor=COLORS["cream_deep"],
    margin=dict(l=0, r=0, t=0, b=0),
    height=560,
    legend=dict(
        orientation="h",
        yanchor="bottom", y=-0.08,
        xanchor="left", x=0,
        font=dict(family=FONTS["mono"], size=10, color=COLORS["ink_mute"]),
        bgcolor="rgba(0,0,0,0)",
    ),
    dragmode="pan",
)

st.plotly_chart(
    fig,
    use_container_width=True,
    config={
        "scrollZoom": True,
        "displayModeBar": True,
        "displaylogo": False,
        "modeBarButtonsToRemove": ["lasso2d", "select2d"],
    },
)

# ============================================================
# COUNTRY DETAIL — redesigned
#   1. Pick a country (full name dropdown)
#   2. Country name + cluster tag
#   3. Other countries in the same cluster (chips)
#   4. Indicator-by-indicator comparison: this country vs. cluster average
# ============================================================
st.markdown("<br>", unsafe_allow_html=True)
st.markdown(
    '<div class="eyebrow"><span class="marker"></span><span>Country detail</span></div>',
    unsafe_allow_html=True,
)

# Build the dropdown list — sorted alphabetically by full name
country_list = (
    df[["ISO", "Country"]]
    .dropna()
    .sort_values("Country")
    ["Country"]
    .tolist()
)

selected_country = st.selectbox(
    "Pick a country to inspect",
    options=country_list,
    index=0,
)

# Look up the row and basic metadata
row = df[df["Country"] == selected_country].iloc[0]
iso = row["ISO"]
cluster_id = int(row["Cluster"]) if pd.notna(row["Cluster"]) else None
cluster_name = row.get("Cluster_name", "—")

# --- 1. Country card ---
st.markdown(
    f"""
    <div class="detail-card">
        <h3>{selected_country}</h3>
        <span class="sub">Cluster {cluster_id} / {cluster_name}</span>
    </div>
    """,
    unsafe_allow_html=True,
)

# --- 2. Other countries in the same cluster (chips) ---
peers = df[df["Cluster"] == cluster_id].sort_values("Country")
peer_names = peers["Country"].tolist()

st.markdown(
    f'<div class="sub-eyebrow">Other countries in this cluster ({len(peer_names)} total)</div>',
    unsafe_allow_html=True,
)
chips_html = '<div class="chip-row">'
for nm in peer_names:
    cls = "chip self" if nm == selected_country else "chip"
    chips_html += f'<span class="{cls}">{nm}</span>'
chips_html += "</div>"
st.markdown(chips_html, unsafe_allow_html=True)

# --- 3. This country vs cluster average — full 27-indicator comparison ---
st.markdown(
    '<div class="sub-eyebrow">How this country compares to its cluster average</div>',
    unsafe_allow_html=True,
)

cluster_members = df[df["Cluster"] == cluster_id]
comparison_rows = []
for ind in indicator_cols:
    country_val = row.get(ind)
    cluster_avg = cluster_members[ind].mean(skipna=True)
    if pd.notna(country_val) and pd.notna(cluster_avg) and cluster_avg != 0:
        diff_pct = ((country_val - cluster_avg) / abs(cluster_avg)) * 100
        diff_str = f"{diff_pct:+.1f}%"
    else:
        diff_str = "—"
    comparison_rows.append({
        "Indicator": ind,
        f"{selected_country}": f"{country_val:,.2f}" if pd.notna(country_val) else "—",
        "Cluster average": f"{cluster_avg:,.2f}" if pd.notna(cluster_avg) else "—",
        "Difference": diff_str,
    })

comparison_df = pd.DataFrame(comparison_rows)
st.dataframe(comparison_df, use_container_width=True, hide_index=True, height=460)

# ============================================================
# FOOTER NOTE
# ============================================================
st.markdown(
    f"""
    <div style="margin-top:60px; padding-top:24px; border-top:1px solid {COLORS['rule']};
                font-family:{FONTS['mono']}; font-size:10px; letter-spacing:0.12em;
                text-transform:uppercase; color:{COLORS['ink_mute']};">
        WHO Global Status Report 2023 &middot; 171 countries &middot; 27 indicators &middot; K-Means K=4
    </div>
    """,
    unsafe_allow_html=True,
)