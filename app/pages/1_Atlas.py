"""
Page 1 — Atlas
Global choropleth: every country colored by its road-safety group (default)
or a selected measurement (toggle mode).

Story: the map shows four road-safety groups across the world. Below,
pick any country to see its group, who else is in that group, and how
its 27 road-safety measurements compare to the group average — so a viewer
can see *why* each country is in its group.

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

    /* country chips — for "other countries in this group" */
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

    /* Country brief block — visually distinct "report" output */
    .brief-block {{
        background: {COLORS['cream']};
        border: 1.5px solid {COLORS['ink']};
        border-left: 6px solid {COLORS['lime']};
        padding: 28px 32px 24px;
        margin-top: 18px;
    }}
    .brief-eyebrow {{
        font-family: {FONTS['mono']}; font-size: 10px;
        letter-spacing: 0.18em; text-transform: uppercase;
        color: {COLORS['ink_mute']};
        margin: 0 0 18px 0;
        display: flex; align-items: center; gap: 10px;
    }}
    .brief-eyebrow .dot {{
        width: 6px; height: 6px; background: {COLORS['lime']};
        box-shadow: 0 0 0 1.5px {COLORS['ink']};
    }}
    .brief-section-title {{
        font-family: {FONTS['mono']}; font-size: 10px;
        letter-spacing: 0.15em; text-transform: uppercase;
        color: {COLORS['ink']}; font-weight: 500;
        margin: 18px 0 12px 0;
        padding-bottom: 6px;
        border-bottom: 1px solid {COLORS['rule']};
    }}
    .brief-section-title:first-child {{ margin-top: 0; }}
    .brief-row {{
        font-family: {FONTS['body']}; font-size: 15px;
        line-height: 1.55; color: {COLORS['ink']};
        margin: 6px 0;
        padding-left: 18px;
        position: relative;
    }}
    .brief-row::before {{
        content: "—";
        position: absolute; left: 0; top: 0;
        color: {COLORS['ink_mute']};
        font-family: {FONTS['mono']};
    }}
    .brief-row strong {{
        font-weight: 600;
    }}
    .brief-row .num {{
        font-family: {FONTS['mono']};
        font-weight: 500;
        color: {COLORS['ink']};
    }}
    .brief-row .num.up {{ color: #C13D3D; }}
    .brief-row .num.down {{ color: #2E6B3A; }}
    .brief-note {{
        font-family: {FONTS['mono']}; font-size: 9px;
        letter-spacing: 0.12em; text-transform: uppercase;
        color: {COLORS['ink_faint'] if 'ink_faint' in COLORS else COLORS['ink_mute']};
        margin-top: 18px; padding-top: 14px;
        border-top: 1px solid {COLORS['rule']};
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


@st.cache_data
def load_trend_data():
    """Load IHME forecasts + temporal anomalies for the Country Brief block.

    Both files are optional — if they're missing the brief just hides the
    trend / forecast lines instead of erroring out.
    """
    forecasts_path = DATA_DIR / "country_forecasts.csv"
    anomalies_path = DATA_DIR / "country_year_anomalies.csv"

    forecasts = pd.read_csv(forecasts_path) if forecasts_path.exists() else None
    anomalies = pd.read_csv(anomalies_path) if anomalies_path.exists() else None

    return forecasts, anomalies


clusters_df, features_df = load_data()
forecasts_df, year_anomalies_df = load_trend_data()

# Merge so we have everything in one place keyed by ISO
df = clusters_df.merge(features_df, on="ISO", how="left")

# Attach the country name from our embedded dict — overrides anything in the CSVs
df["Country"] = df["ISO"].map(name_of)

# Identify the indicator columns (numeric, not metadata)
NON_INDICATOR = {"ISO", "Cluster", "Cluster_name", "Country", "Country name", "Entity", "Name"}
indicator_cols = [c for c in df.columns if c not in NON_INDICATOR and pd.api.types.is_numeric_dtype(df[c])]


# ============================================================
# COUNTRY BRIEF — helpers
# Same 6 themes used on the Compare page, so the recommendation logic
# stays consistent between pages.
# ============================================================
THEME_KEYWORDS = {
    "Legislation": ["law", "legislation", "limit", "bac", "speed limit",
                    "helmet", "seatbelt", "seat-belt", "child restraint",
                    "drink", "drink-driving", "drunk", "mobile phone"],
    "Enforcement": ["enforcement", "enforced", "perceived enforcement"],
    "Infrastructure": ["infrastructure", "road design", "audit", "star rating",
                       "irap", "safe system", "pedestrian", "cycl"],
    "Vehicle safety": ["vehicle", "inspection", "standards", "ncap",
                       "abs", "airbag", "electronic stability"],
    "Post-crash care": ["emergency", "ems", "trauma", "post-crash", "post crash",
                        "ambulance", "hospital", "rehabilitation"],
    "Data quality": ["registration", "vital", "reporting", "completeness",
                     "death registration", "icd", "data quality"],
}


def _classify_indicator(col_name: str):
    """Map an indicator column to one of the six themes, or None."""
    lower = col_name.lower()
    for theme, kws in THEME_KEYWORDS.items():
        for kw in kws:
            if kw in lower:
                return theme
    return None


def _theme_gaps(country_row, cluster_members, indicator_cols):
    """
    For each theme, compute the average pct-gap of the country vs the group
    average. Returns a list of (theme, gap_pct, n_indicators) sorted with
    the most under-performing theme first.

    Positive gap = country is above group average (over-performing).
    Negative gap = country is below group average (under-performing).
    For death-rate-style indicators this convention is inverted in the
    interpretation, but for the brief we use the raw signed gap and
    let the verbal description handle the framing.
    """
    theme_gaps = {}
    for ind in indicator_cols:
        theme = _classify_indicator(ind)
        if theme is None:
            continue
        cval = country_row.get(ind)
        cavg = cluster_members[ind].mean(skipna=True)
        if pd.notna(cval) and pd.notna(cavg) and cavg != 0:
            gap_pct = ((cval - cavg) / abs(cavg)) * 100
            theme_gaps.setdefault(theme, []).append(gap_pct)

    out = []
    for theme, gaps in theme_gaps.items():
        if gaps:
            out.append((theme, sum(gaps) / len(gaps), len(gaps)))
    # Sort by gap ascending (most negative = most under-performing first)
    out.sort(key=lambda t: t[1])
    return out


def _country_trend_summary(iso_code, country_display_name, forecasts_df, anomalies_df):
    """
    Returns a dict with trend / forecast info for a country, or None if no
    matching rows exist. We match on either the ISO code (preferred) or
    the country display name as a fallback.
    """
    if forecasts_df is None:
        return None

    # Try ISO match first, then name match
    fc = forecasts_df[forecasts_df["Code"] == iso_code]
    if fc.empty:
        fc = forecasts_df[forecasts_df["Entity"] == country_display_name]
    if fc.empty:
        return None

    obs = fc[fc["Type"] == "observed"].sort_values("Year")
    fut = fc[fc["Type"] == "forecast"].sort_values("Year")
    if obs.empty:
        return None

    # Pick the rate column (DeathRate) over absolute deaths — comparable across countries
    first_year = int(obs["Year"].iloc[0])
    last_year = int(obs["Year"].iloc[-1])
    first_val = float(obs["DeathRate"].iloc[0])
    last_val = float(obs["DeathRate"].iloc[-1])
    change_pct = ((last_val - first_val) / first_val * 100) if first_val else None

    # Forecast horizon (3 years)
    fc_last_year = int(fut["Year"].iloc[-1]) if not fut.empty else None
    fc_last_val = float(fut["HW_Forecast"].iloc[-1]) if not fut.empty else None
    fc_change_pct = (
        ((fc_last_val - last_val) / last_val * 100)
        if (fc_last_val is not None and last_val)
        else None
    )
    ci_lo = float(fut["HW_CI_Lower"].iloc[-1]) if not fut.empty else None
    ci_hi = float(fut["HW_CI_Upper"].iloc[-1]) if not fut.empty else None

    # Temporal anomalies
    anom_count = 0
    if anomalies_df is not None:
        am = anomalies_df[anomalies_df["Code"] == iso_code]
        if am.empty:
            am = anomalies_df[anomalies_df["Entity"] == country_display_name]
        anom_count = len(am)

    return {
        "first_year": first_year,
        "last_year": last_year,
        "first_val": first_val,
        "last_val": last_val,
        "change_pct": change_pct,
        "fc_last_year": fc_last_year,
        "fc_last_val": fc_last_val,
        "fc_change_pct": fc_change_pct,
        "ci_lo": ci_lo,
        "ci_hi": ci_hi,
        "anom_count": anom_count,
    }


def _fmt_signed_pct(val):
    """Return '<span class='num up/down'>+X.X%</span>' for use inside the HTML."""
    if val is None or pd.isna(val):
        return '<span class="num">—</span>'
    cls = "up" if val > 0 else ("down" if val < 0 else "")
    return f'<span class="num {cls}">{val:+.1f}%</span>'


def _trend_direction_word(change_pct):
    if change_pct is None:
        return "unchanged"
    if change_pct < -10:
        return "fell substantially"
    if change_pct < -3:
        return "declined"
    if change_pct > 10:
        return "rose substantially"
    if change_pct > 3:
        return "rose"
    return "was roughly flat"


# ============================================================
# HEADER
# ============================================================
st.markdown(
    """
    <div class="eyebrow"><span class="marker"></span><span>01 / Atlas</span></div>
    <h1 class="page-title">Every country, <span class="accent">on a map.</span></h1>
    <p class="page-lede">
        171 countries grouped by their road-safety profile. Switch between the
        group view and any single road-safety measurement. Below the map, pick
        a country to see who else is in its group and how its numbers compare
        to the group average.
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
        options=["By group", "By measurement"],
        index=0,
        horizontal=True,
    )

with col_b:
    if mode == "By measurement":
        selected_indicator = st.selectbox(
            "Pick a road-safety measurement",
            options=indicator_cols,
            index=0,
        )
    else:
        selected_indicator = None

# ============================================================
# BUILD THE CHOROPLETH
# ============================================================
fig = go.Figure()

if mode == "By group":
    for cluster_id in sorted(df["Cluster"].dropna().unique()):
        sub = df[df["Cluster"] == cluster_id]
        cluster_label = CLUSTER_NAMES.get(int(cluster_id), f"Group {int(cluster_id)}")
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
                    "Group " + str(int(cluster_id)) + " — " + cluster_label +
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
#   2. Country name + group tag
#   3. Country brief — auto-generated report + recommendations
#   4. Other countries in the same group (chips)
#   5. Measurement-by-measurement comparison: this country vs. group average
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
        <span class="sub">Group {cluster_id} — {cluster_name}</span>
    </div>
    """,
    unsafe_allow_html=True,
)

# --- 2. Country Brief — auto-generated report + recommendations ---
# This block produces the "report" and "recommendations" outputs the brief
# requires, built entirely from data already on disk. Same logic runs for
# every country so Palestine and any other selection get equal treatment.

cluster_members_for_brief = df[df["Cluster"] == cluster_id]
gaps = _theme_gaps(row, cluster_members_for_brief, indicator_cols)

# Headline death-rate value (WHO-estimated rate per 100 000)
DEATH_RATE_COL = "WHO-estimated rate per 100 000 population"
death_rate_val = row.get(DEATH_RATE_COL)
death_rate_cluster_avg = cluster_members_for_brief[DEATH_RATE_COL].mean(skipna=True) \
    if DEATH_RATE_COL in cluster_members_for_brief.columns else None

# Vehicle ownership headline
VEH_RATE_COL = "Total registered vehicles rate per 100 000 pop"
veh_val = row.get(VEH_RATE_COL) if VEH_RATE_COL in row.index else None

# Pull trend / forecast info from IHME data (separate dataset)
trend = _country_trend_summary(iso, selected_country, forecasts_df, year_anomalies_df)

# Build the REPORT lines
report_lines = []

# Line 1 — group membership
report_lines.append(
    f"Belongs to the <strong>{cluster_name}</strong> profile alongside "
    f"{len(cluster_members_for_brief) - 1} other countries."
)

# Line 2 — death rate vs group average
if pd.notna(death_rate_val) and pd.notna(death_rate_cluster_avg) and death_rate_cluster_avg != 0:
    death_gap = ((death_rate_val - death_rate_cluster_avg) / death_rate_cluster_avg) * 100
    direction = "above" if death_gap > 0 else "below"
    report_lines.append(
        f"WHO-estimated death rate: <span class='num'>{death_rate_val:.1f}</span> per 100k "
        f"&mdash; {_fmt_signed_pct(death_gap)} {direction} the group average of "
        f"<span class='num'>{death_rate_cluster_avg:.1f}</span>."
    )
elif pd.notna(death_rate_val):
    report_lines.append(
        f"WHO-estimated death rate: <span class='num'>{death_rate_val:.1f}</span> per 100k population."
    )

# Line 3 — vehicle ownership context
if pd.notna(veh_val):
    report_lines.append(
        f"Vehicle ownership: <span class='num'>{veh_val:,.0f}</span> registered vehicles per 100k people."
    )

# Line 4 — historical trend (IHME)
if trend is not None and trend["change_pct"] is not None:
    trend_word = _trend_direction_word(trend["change_pct"])
    report_lines.append(
        f"From {trend['first_year']} to {trend['last_year']}, the death rate "
        f"{trend_word} ({_fmt_signed_pct(trend['change_pct'])} over 30 years)."
    )
    if trend["anom_count"] > 0:
        report_lines.append(
            f"<span class='num'>{trend['anom_count']}</span> year(s) where deaths "
            f"spiked or dropped unusually compared to the country's own trend."
        )

# Line 5 — 3-year projection
if trend is not None and trend["fc_change_pct"] is not None:
    fc_word = "rise" if trend["fc_change_pct"] > 1 else ("fall" if trend["fc_change_pct"] < -1 else "stay roughly flat")
    report_lines.append(
        f"3-year projection: expected to {fc_word} to "
        f"<span class='num'>{trend['fc_last_val']:.1f}</span> per 100k by "
        f"{trend['fc_last_year']} ({_fmt_signed_pct(trend['fc_change_pct'])} from latest observed, "
        f"likely range <span class='num'>{trend['ci_lo']:.1f}&ndash;{trend['ci_hi']:.1f}</span>)."
    )

# Build the RECOMMENDATIONS lines
recommendation_lines = []

if gaps:
    # Worst-performing theme (most negative gap = country is below group avg)
    worst_theme, worst_gap, worst_n = gaps[0]
    if worst_gap < 0:
        recommendation_lines.append(
            f"<strong>Priority focus: {worst_theme}.</strong> Across {worst_n} measurement(s) in this theme, "
            f"{selected_country} averages {_fmt_signed_pct(worst_gap)} relative to its group &mdash; "
            f"the largest shortfall vs. peers. Strengthening this area would bring the country "
            f"closest to its peer group."
        )

    # Second-worst, if also negative and meaningfully different
    if len(gaps) > 1:
        second_theme, second_gap, second_n = gaps[1]
        if second_gap < -2 and second_theme != worst_theme:
            recommendation_lines.append(
                f"<strong>Secondary focus: {second_theme}.</strong> Also under-performs "
                f"the group average ({_fmt_signed_pct(second_gap)} across {second_n} measurement(s))."
            )

    # Strongest theme — what to maintain
    best_theme, best_gap, best_n = gaps[-1]
    if best_gap > 2:
        recommendation_lines.append(
            f"<strong>Maintain strength: {best_theme}.</strong> Out-performs the group average "
            f"by {_fmt_signed_pct(best_gap)} &mdash; this is a relative strength worth preserving."
        )

# Forecast-driven recommendation
if trend is not None and trend["fc_change_pct"] is not None:
    if trend["fc_change_pct"] > 3:
        recommendation_lines.append(
            f"<strong>Watch the trend.</strong> The 3-year projection points upward "
            f"({_fmt_signed_pct(trend['fc_change_pct'])}). If recent policy efforts exist, "
            f"their effect should appear in the next observed years; otherwise corrective "
            f"interventions are indicated."
        )
    elif trend["fc_change_pct"] < -3:
        recommendation_lines.append(
            f"<strong>Build on momentum.</strong> The 3-year projection continues a downward trend "
            f"({_fmt_signed_pct(trend['fc_change_pct'])}). Sustaining recent interventions should "
            f"consolidate the gains."
        )

# Peer-based recommendation: pick the best-performing peer in the group
if pd.notna(death_rate_val) and DEATH_RATE_COL in cluster_members_for_brief.columns:
    peers_only = cluster_members_for_brief[cluster_members_for_brief["Country"] != selected_country]
    if not peers_only.empty and peers_only[DEATH_RATE_COL].notna().any():
        best_peer_idx = peers_only[DEATH_RATE_COL].idxmin()
        best_peer_name = peers_only.loc[best_peer_idx, "Country"]
        best_peer_val = peers_only.loc[best_peer_idx, DEATH_RATE_COL]
        if pd.notna(best_peer_val) and best_peer_val < death_rate_val:
            recommendation_lines.append(
                f"<strong>Peer benchmark.</strong> Within the same group, "
                f"<strong>{best_peer_name}</strong> reports the lowest death rate "
                f"(<span class='num'>{best_peer_val:.1f}</span> per 100k vs "
                f"<span class='num'>{death_rate_val:.1f}</span> here). Comparing legislation "
                f"and enforcement scores with this peer may surface concrete differences worth examining."
            )

# Fallback if recommendations is empty (e.g. country has no usable theme data)
if not recommendation_lines:
    recommendation_lines.append(
        "Not enough comparable measurement data is available to generate targeted recommendations "
        "for this country. The general profile of the group is the best available context."
    )

# Render the brief block
brief_html = '<div class="brief-block">'
brief_html += (
    '<div class="brief-eyebrow"><span class="dot"></span>'
    f'<span>Country brief &middot; auto-generated from group + trend data</span></div>'
)

brief_html += '<div class="brief-section-title">Report</div>'
for line in report_lines:
    brief_html += f'<div class="brief-row">{line}</div>'

brief_html += '<div class="brief-section-title">Recommendations</div>'
for line in recommendation_lines:
    brief_html += f'<div class="brief-row">{line}</div>'

brief_html += (
    '<div class="brief-note">'
    'Synthesized from group profile &middot; WHO measurements &middot; '
    '30-year death-rate trend &middot; 3-year projection'
    '</div>'
)
brief_html += '</div>'

st.markdown(brief_html, unsafe_allow_html=True)

# --- 3. Other countries in the same group (chips) ---
peers = df[df["Cluster"] == cluster_id].sort_values("Country")
peer_names = peers["Country"].tolist()

st.markdown(
    f'<div class="sub-eyebrow">Other countries in this group ({len(peer_names)} total)</div>',
    unsafe_allow_html=True,
)
chips_html = '<div class="chip-row">'
for nm in peer_names:
    cls = "chip self" if nm == selected_country else "chip"
    chips_html += f'<span class="{cls}">{nm}</span>'
chips_html += "</div>"
st.markdown(chips_html, unsafe_allow_html=True)

# --- 4. This country vs group average — full 27-measurement comparison ---
st.markdown(
    '<div class="sub-eyebrow">How this country compares to its group average</div>',
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
        "Measurement": ind,
        f"{selected_country}": f"{country_val:,.2f}" if pd.notna(country_val) else "—",
        "Group average": f"{cluster_avg:,.2f}" if pd.notna(cluster_avg) else "—",
        "Difference": diff_str,
    })

comparison_df = pd.DataFrame(comparison_rows)
st.dataframe(comparison_df, use_container_width=True, hide_index=True, height=460)

# ============================================================
# FOOTER NOTE — technical methodology stays here only
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