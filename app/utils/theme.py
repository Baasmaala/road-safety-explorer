"""
theme.py — Single source of truth for visual styling across the app.

Keeps the homepage's bold modernist palette consistent on every page:
    ink  #0A0A0A   ·   cream  #F4F1EA   ·   lime  #C6FF3D

Usage in any page (1Atlas.py, 2Compare.py, etc.):

    from utils.theme import (
        COLORS,
        FONTS,
        CLUSTER_COLORS,
        apply_plotly_theme,
        style_figure,
    )

    apply_plotly_theme()   # call once at top of page

    fig = px.scatter(...)
    fig = style_figure(fig, title="Cluster landscape")
    st.plotly_chart(fig, use_container_width=True)
"""

from __future__ import annotations
import plotly.graph_objects as go
import plotly.io as pio


# ============================================================
# 1. PALETTE — must match assets/style.css exactly
# ============================================================
COLORS = {
    # Core neutrals
    "ink":          "#0A0A0A",   # primary text, axes, strong lines
    "ink_soft":     "#1A1A1A",
    "ink_mute":     "#4A4A48",   # secondary text, light axis labels
    "ink_faint":    "#8A8880",   # tertiary text, grid lines
    "cream":        "#F4F1EA",   # page background
    "cream_deep":   "#ECE7DC",   # alt surface
    "land_nodata":  "#DDD8CC",   # land fill for countries with no data
    "paper":        "#FFFFFF",   # cards, popovers
    "rule":         "rgba(10,10,10,0.12)",   # hairline borders
    "rule_strong":  "rgba(10,10,10,0.85)",

    # Accent
    "lime":         "#C6FF3D",   # the one accent — use sparingly
    "lime_deep":    "#A8E020",

    # Semantic
    "spotlight":    "#C6FF3D",   # Palestine highlight everywhere
    "spotlight_ink":"#0A0A0A",
}


# ============================================================
# 2. CLUSTER PALETTE — 4 stable colors aligned with notebook 01
#     Cluster identities (anchored in clustering code):
#       0 = Developing-country road profile   (85 countries)
#       1 = Rich-country car culture          (53 countries)
#       2 = Low-motorization mixed            (25 countries — PSE)
#       3 = Atypical reporting                ( 8 countries)
# ============================================================
CLUSTER_COLORS = {
    0: "#4A4A48",   # ink_mute — developing profile (largest group, neutral)
    1: "#0A0A0A",   # ink     — rich car culture (strong, dominant)
    2: "#C6FF3D",   # lime    — Palestine's cluster (the spotlight)
    3: "#8A8880",   # ink_faint — atypical reporting (background-ish)
}

CLUSTER_NAMES = {
    0: "Developing road profile",
    1: "Rich car culture",
    2: "Low-motorization mixed",
    3: "Atypical reporting",
}

# Ordered list for legends / Plotly color sequences
CLUSTER_SEQUENCE = [CLUSTER_COLORS[i] for i in range(4)]


# ============================================================
# 3. CONTINUOUS COLORSCALES — for choropleths, heatmaps, etc.
# ============================================================
# Cream → lime → ink (sequential, dramatic)
COLORSCALE_SEQUENTIAL = [
    [0.00, "#F4F1EA"],
    [0.35, "#E8EDB8"],
    [0.60, "#C6FF3D"],
    [0.85, "#5A5A2A"],
    [1.00, "#0A0A0A"],
]

# Diverging: ink ← cream → lime (for above/below average style maps)
COLORSCALE_DIVERGING = [
    [0.00, "#0A0A0A"],
    [0.25, "#4A4A48"],
    [0.50, "#F4F1EA"],
    [0.75, "#C6FF3D"],
    [1.00, "#A8E020"],
]


# ============================================================
# 4. FONTS — must be loaded by style.css via @import for these
#    to actually render in Plotly (Plotly uses the same CSS context)
# ============================================================
FONTS = {
    "display": "Space Grotesk, -apple-system, sans-serif",
    "body":    "Inter, -apple-system, sans-serif",
    "mono":    "JetBrains Mono, SF Mono, monospace",
    "serif":   "Instrument Serif, Georgia, serif",
}

# ============================================================
# 5. PLOTLY TEMPLATE — flat, modernist, no gridline noise
# ============================================================
def _build_template() -> go.layout.Template:
    """Construct the shared Plotly template once."""
    t = go.layout.Template()

    t.layout = go.Layout(
        font=dict(
            family=FONTS["body"],
            size=13,
            color=COLORS["ink"],
        ),
        title=dict(
            font=dict(
                family=FONTS["display"],
                size=22,
                color=COLORS["ink"],
            ),
            x=0,
            xanchor="left",
            pad=dict(t=8, b=20, l=0),
        ),
        paper_bgcolor=COLORS["cream"],
        plot_bgcolor=COLORS["cream"],
        colorway=CLUSTER_SEQUENCE,
        margin=dict(l=60, r=30, t=70, b=60),
        hovermode="closest",
        hoverlabel=dict(
            bgcolor=COLORS["ink"],
            bordercolor=COLORS["ink"],
            font=dict(
                family=FONTS["mono"],
                size=12,
                color=COLORS["cream"],
            ),
        ),
        xaxis=dict(
            showgrid=False,
            showline=True,
            linecolor=COLORS["ink"],
            linewidth=1.2,
            ticks="outside",
            tickcolor=COLORS["ink"],
            ticklen=5,
            tickfont=dict(family=FONTS["mono"], size=11, color=COLORS["ink_mute"]),
            title=dict(font=dict(family=FONTS["body"], size=13, color=COLORS["ink_mute"])),
            zeroline=False,
        ),
        yaxis=dict(
            showgrid=True,
            gridcolor=COLORS["rule"],
            gridwidth=0.5,
            showline=True,
            linecolor=COLORS["ink"],
            linewidth=1.2,
            ticks="outside",
            tickcolor=COLORS["ink"],
            ticklen=5,
            tickfont=dict(family=FONTS["mono"], size=11, color=COLORS["ink_mute"]),
            title=dict(font=dict(family=FONTS["body"], size=13, color=COLORS["ink_mute"])),
            zeroline=False,
        ),
        legend=dict(
            font=dict(family=FONTS["mono"], size=11, color=COLORS["ink"]),
            bgcolor="rgba(0,0,0,0)",
            bordercolor=COLORS["rule"],
            borderwidth=0,
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="left",
            x=0,
        ),
        geo=dict(
            bgcolor=COLORS["cream"],
            landcolor=COLORS["cream_deep"],
            lakecolor=COLORS["cream"],
            coastlinecolor=COLORS["ink_mute"],
            countrycolor=COLORS["ink_mute"],
            showframe=False,
            showcoastlines=True,
            projection=dict(type="natural earth"),
        ),
    )
    return t


PLOTLY_TEMPLATE = _build_template()


def apply_plotly_theme() -> None:
    """
    Register and activate the shared Plotly template.
    Call once at the top of every page.
    """
    pio.templates["road_safety"] = PLOTLY_TEMPLATE
    pio.templates.default = "road_safety"


# ============================================================
# 6. FIGURE HELPERS — small utilities used across pages
# ============================================================
def style_figure(
    fig: go.Figure,
    title: str | None = None,
    subtitle: str | None = None,
    height: int = 520,
    show_legend: bool = True,
) -> go.Figure:
    """
    Apply consistent finishing touches to a figure after building it.
    """
    layout_update = dict(height=height, showlegend=show_legend)

    if title is not None:
        if subtitle:
            layout_update["title"] = dict(
                text=(
                    f"{title}"
                    f"<br><span style='font-family:{FONTS['mono']}; "
                    f"font-size:11px; letter-spacing:0.1em; "
                    f"color:{COLORS['ink_mute']}; "
                    f"text-transform:uppercase;'>{subtitle}</span>"
                )
            )
        else:
            layout_update["title"] = dict(text=title)

    fig.update_layout(**layout_update)
    return fig


def highlight_palestine_trace(
    fig: go.Figure,
    palestine_indices: list[int] | None = None,
) -> go.Figure:
    """
    Make Palestine markers visually dominant: lime fill, ink border, larger size.
    Pass the row indices of Palestine in the plotted data; if None, looks for
    a trace named 'Palestine' or 'PSE'.
    """
    for trace in fig.data:
        name = getattr(trace, "name", "") or ""
        if name.lower() in ("palestine", "pse"):
            trace.marker = dict(
                color=COLORS["lime"],
                size=16,
                line=dict(color=COLORS["ink"], width=2),
                symbol="star",
            )
    return fig


def section_label(text: str) -> str:
    """
    Return an HTML span styled as a monospace section eyebrow.
    Use inside st.markdown(..., unsafe_allow_html=True).

        st.markdown(section_label("01 / Overview"), unsafe_allow_html=True)
    """
    return (
        f"<div style='font-family:{FONTS['mono']}; font-size:11px; "
        f"letter-spacing:0.15em; text-transform:uppercase; "
        f"color:{COLORS['ink_mute']}; margin: 0 0 8px;'>"
        f"<span style='display:inline-block; width:8px; height:8px; "
        f"background:{COLORS['ink']}; margin-right:10px; vertical-align:1px;'></span>"
        f"{text}</div>"
    )


def display_heading(text: str, size: int = 44) -> str:
    """
    Return an HTML h2 styled in the Space Grotesk display face.
    """
    return (
        f"<h2 style='font-family:{FONTS['display']}; "
        f"font-size:{size}px; font-weight:500; "
        f"letter-spacing:-0.025em; line-height:0.98; "
        f"color:{COLORS['ink']}; margin: 0 0 24px;'>{text}</h2>"
    )


# ============================================================
# 7. STREAMLIT METRIC CARD (replaces st.metric, which looks generic)
# ============================================================
def metric_card_html(label: str, value: str, sub: str | None = None) -> str:
    """
    Render a single bold-modernist stat card. Use 3-4 in a row via
    st.columns to build a stat strip on any page.
    """
    sub_html = (
        f"<div style='font-family:{FONTS['mono']}; font-size:10px; "
        f"letter-spacing:0.12em; text-transform:uppercase; "
        f"color:{COLORS['ink_mute']}; margin-top:10px;'>{sub}</div>"
        if sub else ""
    )
    return (
        f"<div style='padding: 24px 0; border-top: 1.5px solid {COLORS['ink']}; "
        f"border-bottom: 1px solid {COLORS['rule']};'>"
        f"<div style='font-family:{FONTS['mono']}; font-size:10px; "
        f"letter-spacing:0.15em; text-transform:uppercase; "
        f"color:{COLORS['ink_mute']}; margin-bottom:14px;'>{label}</div>"
        f"<div style='font-family:{FONTS['display']}; font-size:44px; "
        f"font-weight:500; letter-spacing:-0.025em; line-height:1; "
        f"color:{COLORS['ink']};'>{value}</div>"
        f"{sub_html}"
        f"</div>"
    )