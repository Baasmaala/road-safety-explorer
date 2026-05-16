"""
generate_home_map.py
====================
One-shot script: read country_clusters.csv, render the world map colored by
cluster (Palestine starred in lime), save as a static SVG + PNG.

Run once locally, then commit the SVG to the repo. The home page embeds it.

Usage (from project root, with .venv active):
    python generate_home_map.py

Output files (overwrites existing):
    app/assets/home_map.svg     <- vector, used on home page
    app/assets/home_map.png     <- raster fallback (rarely needed)

Requirements: plotly + kaleido + Chrome. If kaleido complains, run once:
    plotly_get_chrome
"""

from pathlib import Path
import pandas as pd
import plotly.graph_objects as go

# ---- paths ------------------------------------------------------------
HERE = Path(__file__).parent
CLUSTERS_CSV = HERE / "data" / "processed" / "country_clusters.csv"
OUT_DIR = HERE / "app" / "assets"
OUT_DIR.mkdir(parents=True, exist_ok=True)

# ---- palette (mirrors utils/theme.py CLUSTER_COLORS) ------------------
CLUSTER_COLORS = {
    0: "#4A4A48",   # developing road profile
    1: "#0A0A0A",   # rich car culture
    2: "#C6FF3D",   # Palestine's cluster
    3: "#8A8880",   # atypical reporting
}
CREAM_DEEP = "#ECE7DC"
LAND_NO_DATA = "#DDD8CC"
INK = "#0A0A0A"
LIME = "#C6FF3D"

# ---- read clusters ----------------------------------------------------
df = pd.read_csv(CLUSTERS_CSV)
if "ISO_3 country name" in df.columns:
    df = df.rename(columns={"ISO_3 country name": "ISO"})

print(f"Loaded {len(df)} countries from {CLUSTERS_CSV.name}")

# ---- build figure -----------------------------------------------------
fig = go.Figure()

for cid in sorted(df["Cluster"].unique()):
    sub = df[df["Cluster"] == cid]
    color = CLUSTER_COLORS[int(cid)]
    fig.add_trace(go.Choropleth(
        locations=sub["ISO"],
        z=[1] * len(sub),
        colorscale=[[0, color], [1, color]],
        showscale=False,
        marker=dict(line=dict(color=INK, width=0.3)),
        hoverinfo="skip",
        name=f"Cluster {cid}",
    ))

pse = df[df["ISO"] == "PSE"]
if len(pse):
    fig.add_trace(go.Choropleth(
        locations=pse["ISO"],
        z=[1],
        colorscale=[[0, LIME], [1, LIME]],
        showscale=False,
        marker=dict(line=dict(color=INK, width=2.2)),
        hoverinfo="skip",
        name="Palestine",
    ))
else:
    print("WARN: no Palestine row found (ISO == 'PSE')")

fig.update_layout(
    geo=dict(
        bgcolor=CREAM_DEEP,
        landcolor=LAND_NO_DATA,
        lakecolor=CREAM_DEEP,
        oceancolor=CREAM_DEEP,
        coastlinecolor=INK,
        coastlinewidth=0.4,
        countrycolor=INK,
        showframe=False,
        showcoastlines=True,
        showcountries=False,
        showocean=True,
        showland=True,
        projection=dict(type="natural earth"),
    ),
    paper_bgcolor=CREAM_DEEP,
    plot_bgcolor=CREAM_DEEP,
    margin=dict(l=0, r=0, t=0, b=0),
    showlegend=False,
    width=1600,
    height=800,
)

# ---- export -----------------------------------------------------------
svg_path = OUT_DIR / "home_map.svg"
png_path = OUT_DIR / "home_map.png"

try:
    fig.write_image(str(svg_path), format="svg", width=1600, height=800)
    print(f"Wrote {svg_path}")
except Exception as e:
    print(f"SVG export failed: {e}")
    print("If this is the first run, install Chrome for kaleido:")
    print("    plotly_get_chrome")
    raise

try:
    fig.write_image(str(png_path), format="png", width=1600, height=800, scale=2)
    print(f"Wrote {png_path}")
except Exception as e:
    print(f"PNG export skipped: {e}")

print("Done.")