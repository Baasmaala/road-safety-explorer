"""
Global Road Safety Explorer — Homepage
Bold modernist design: near-black + cream + electric lime
Team: Basmala (lead) · Omar · Osama
Course: Data Mining 10672349, An-Najah · Dr.-Ing. Ahmed Abualia
"""

import json
import sys
from pathlib import Path

import streamlit as st
import streamlit.components.v1 as components

# Make utils.* importable when running via `streamlit run app/app.py`
sys.path.insert(0, str(Path(__file__).parent))
from utils.map_data import CLUSTERS, ISO_NUM_TO_ALPHA3

# ============================================================
# PAGE CONFIG
# ============================================================
st.set_page_config(
    page_title="Global Road Safety Explorer",
    page_icon="◼",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# Kill Streamlit chrome so the iframe sits flush against the page
st.markdown(
    """
    <style>
    .block-container { padding: 0 !important; max-width: 100% !important; }
    [data-testid="stAppViewContainer"] { background: #F4F1EA !important; }
    footer { display: none !important; }
    iframe { border: none !important; }
    section[data-testid="stSidebar"] { background: #0A0A0A !important; }
    section[data-testid="stSidebar"] * { color: #F4F1EA !important; }
    </style>
    """,
    unsafe_allow_html=True,
)

# ============================================================


# ============================================================
# Serialize cluster data + ISO lookup as JS literals for the iframe
# ============================================================
CLUSTERS_JS = json.dumps(CLUSTERS, separators=(",", ":"))
ISO_NUM_JS = json.dumps(ISO_NUM_TO_ALPHA3, separators=(",", ":"))

# ============================================================
# HOMEPAGE BODY
# ============================================================
HOMEPAGE_HTML = r"""
<!DOCTYPE html>
<html lang="en">
<head>
    <base target="_top">
<meta charset="UTF-8">
<link href="https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;500;700&family=Inter:wght@400;500;600&family=Instrument+Serif:ital@0;1&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet">
<style>
:root {
    --ink: #0A0A0A;
    --ink-mute: #4A4A48;
    --ink-faint: #8A8880;
    --cream: #F4F1EA;
    --cream-deep: #ECE7DC;
    --land-nodata: #DDD8CC;
    --lime: #C6FF3D;
    --rule: rgba(10, 10, 10, 0.12);
    --font-display: 'Space Grotesk', -apple-system, sans-serif;
    --font-serif: 'Instrument Serif', Georgia, serif;
    --font-body: 'Inter', -apple-system, sans-serif;
    --font-mono: 'JetBrains Mono', 'SF Mono', monospace;
}

* { box-sizing: border-box; margin: 0; padding: 0; }

html, body {
    background: var(--cream);
    color: var(--ink);
    font-family: var(--font-body);
    -webkit-font-smoothing: antialiased;
}

.wrap { max-width: 1240px; margin: 0 auto; padding: 0 56px 80px; }
@media (max-width: 768px) { .wrap { padding: 0 24px 60px; } }

::selection { background: var(--lime); color: var(--ink); }

.topbar {
    display: flex; justify-content: space-between; align-items: center;
    padding: 18px 0; border-bottom: 1px solid var(--rule);
    font-family: var(--font-mono); font-size: 11px;
    letter-spacing: 0.12em; text-transform: uppercase; color: var(--ink-mute);
}
.topbar .brand { display: flex; align-items: center; gap: 10px; color: var(--ink); font-weight: 500; }
.topbar .brand .dot { width: 10px; height: 10px; background: var(--lime); border: 1.5px solid var(--ink); }

.eyebrow {
    font-family: var(--font-mono); font-size: 11px;
    letter-spacing: 0.15em; text-transform: uppercase; color: var(--ink-mute);
    display: flex; align-items: center; gap: 12px;
}
.eyebrow .marker { width: 8px; height: 8px; background: var(--lime); box-shadow: 0 0 0 2px var(--ink); }

.display-xl {
    font-family: var(--font-display); font-size: clamp(48px, 7vw, 88px);
    font-weight: 500; line-height: 0.95; letter-spacing: -0.035em; color: var(--ink);
}
.display-xl .accent { font-family: var(--font-serif); font-style: italic; font-weight: 400; letter-spacing: -0.02em; }

.display-lg {
    font-family: var(--font-display); font-size: clamp(36px, 4.5vw, 56px);
    font-weight: 500; line-height: 0.98; letter-spacing: -0.025em;
}

.lede { font-size: clamp(16px, 1.4vw, 19px); line-height: 1.55; color: var(--ink-mute); max-width: 600px; }

.hero { padding: 80px 0 72px; border-bottom: 1px solid var(--rule); }
.hero .lede { margin-top: 32px; }
.hero .cta-row { display: flex; gap: 14px; margin-top: 44px; flex-wrap: wrap; }

.cta-primary, .cta-secondary {
    padding: 16px 26px; font-family: var(--font-body); font-size: 14px; font-weight: 500;
    text-decoration: none; display: inline-flex; align-items: center; gap: 10px;
    cursor: pointer; transition: all 0.25s ease; border: 1.5px solid var(--ink);
    position: relative; overflow: hidden;
}
.cta-primary { background: var(--ink); color: var(--cream); }
.cta-primary::before {
    content: ''; position: absolute; inset: 0; background: var(--lime);
    transform: translateX(-100%); transition: transform 0.35s ease; z-index: 0;
}
.cta-primary > * { position: relative; z-index: 1; }
.cta-primary:hover { color: var(--ink); }
.cta-primary:hover::before { transform: translateX(0); }
.cta-primary .arrow { font-family: var(--font-mono); transition: transform 0.25s ease; }
.cta-primary:hover .arrow { transform: translateX(4px); }

.cta-secondary { background: transparent; color: var(--ink); }
.cta-secondary:hover { background: var(--ink); color: var(--cream); }

.cursor {
    display: inline-block; width: 0.55em; height: 0.85em;
    background: var(--lime); vertical-align: -0.05em; margin-left: 0.05em;
    animation: blink 0.9s steps(2) infinite;
}
@keyframes blink { 0%, 50% { opacity: 1; } 51%, 100% { opacity: 0; } }

.fade-up {
    opacity: 0; transform: translateY(20px);
    transition: opacity 0.7s ease, transform 0.7s ease;
}
.fade-up.in { opacity: 1; transform: translateY(0); }

/* ============================================================
   MAP PREVIEW — interactive D3 + TopoJSON, CDN-loaded
   ============================================================ */
.map-preview { padding: 72px 0 64px; border-bottom: 1px solid var(--rule); }
.map-meta {
    display: flex; justify-content: space-between; align-items: flex-end;
    flex-wrap: wrap; gap: 24px; margin-bottom: 32px;
}
.map-meta-right {
    font-family: var(--font-mono); font-size: 11px;
    letter-spacing: 0.12em; text-transform: uppercase; color: var(--ink-mute);
}
.map-accent {
    font-family: var(--font-serif); font-style: italic; font-weight: 400;
    letter-spacing: -0.02em;
}
.map-frame {
    position: relative; width: 100%; aspect-ratio: 2 / 1;
    background: var(--cream-deep); border: 1.5px solid var(--ink); overflow: hidden;
}
#map-svg { width: 100%; height: 100%; display: block; cursor: crosshair; }
.country {
    stroke: var(--ink); stroke-width: 0.25;
    transition: filter 0.1s ease, stroke-width 0.1s ease;
}
.country.no-data { fill: var(--land-nodata); }
.country.palestine { stroke-width: 1.8; }
.country:hover { stroke-width: 1.2; filter: brightness(1.1); cursor: pointer; }

#hover-card {
    position: absolute; pointer-events: none;
    background: var(--ink); color: var(--cream);
    padding: 12px 16px; font-family: var(--font-mono);
    font-size: 11px; letter-spacing: 0.05em; line-height: 1.5;
    opacity: 0; transition: opacity 0.12s ease;
    z-index: 10; min-width: 180px; max-width: 260px;
    border: 1.5px solid var(--ink);
}
#hover-card.show { opacity: 1; }
#hover-card .h-name {
    font-family: var(--font-display); font-size: 16px; font-weight: 500;
    letter-spacing: -0.01em; text-transform: none; margin-bottom: 8px;
    color: var(--cream);
}
#hover-card .h-cluster {
    color: var(--lime); text-transform: uppercase;
    font-size: 10px; letter-spacing: 0.12em;
}
#hover-card .h-cluster.muted { color: var(--ink-faint); }

.map-cta {
    position: absolute; bottom: 18px; right: 18px;
    background: var(--ink); color: var(--cream);
    padding: 12px 18px; font-family: var(--font-mono); font-size: 11px;
    letter-spacing: 0.1em; text-transform: uppercase; text-decoration: none;
    display: inline-flex; align-items: center; gap: 8px;
    border: 1.5px solid var(--ink); transition: all 0.25s ease;
    z-index: 5; cursor: pointer;
}
.map-cta:hover { background: var(--lime); color: var(--ink); }
.map-cta .arr { transition: transform 0.25s ease; }
.map-cta:hover .arr { transform: translateX(3px); }

#map-loading, #map-error {
    position: absolute; inset: 0;
    display: flex; flex-direction: column; align-items: center; justify-content: center;
    font-family: var(--font-mono); font-size: 11px;
    letter-spacing: 0.12em; text-transform: uppercase; color: var(--ink-mute);
    background: var(--cream-deep); gap: 12px;
}
#map-error { display: none; }
.loading-dot {
    width: 10px; height: 10px; background: var(--lime);
    border: 1.5px solid var(--ink); animation: pulse 1.2s ease-in-out infinite;
}
@keyframes pulse {
    0%, 100% { opacity: 0.4; transform: scale(0.85); }
    50% { opacity: 1; transform: scale(1.1); }
}

.map-legend {
    display: flex; gap: 28px; margin-top: 24px; flex-wrap: wrap;
    font-family: var(--font-mono); font-size: 10px;
    letter-spacing: 0.1em; text-transform: uppercase; color: var(--ink-mute);
}
.legend-item { display: flex; align-items: center; gap: 10px; }
.legend-swatch { width: 14px; height: 14px; border: 1px solid var(--ink); }
@media (max-width: 768px) {
    .map-legend { gap: 14px; font-size: 9px; }
    .map-cta { padding: 9px 13px; font-size: 10px; bottom: 12px; right: 12px; }
}

.stat-strip {
    display: grid; grid-template-columns: repeat(4, 1fr); border-bottom: 1px solid var(--rule);
}
.stat-cell { padding: 36px 24px 36px 0; border-right: 1px solid var(--rule); }
.stat-cell:first-child { padding-left: 0; }
.stat-cell:last-child { border-right: none; padding-right: 0; }
.stat-cell:not(:first-child) { padding-left: 28px; }
.stat-num {
    font-family: var(--font-display); font-size: clamp(40px, 4.5vw, 56px);
    font-weight: 500; line-height: 1; letter-spacing: -0.025em;
}
.stat-num .unit { font-size: 0.5em; color: var(--ink-faint); margin-left: 2px; font-weight: 400; }
.stat-label {
    font-family: var(--font-mono); font-size: 10px;
    letter-spacing: 0.12em; text-transform: uppercase; color: var(--ink-mute); margin-top: 12px;
}
@media (max-width: 768px) {
    .stat-strip { grid-template-columns: repeat(2, 1fr); }
    .stat-cell:nth-child(2) { border-right: none; padding-right: 0; }
    .stat-cell:nth-child(3) { padding-left: 0; }
    .stat-cell:nth-child(1), .stat-cell:nth-child(2) { border-bottom: 1px solid var(--rule); }
}

.section-head {
    padding: 80px 0 48px; display: flex; align-items: baseline;
    justify-content: space-between; flex-wrap: wrap; gap: 24px;
}
.section-head .index {
    font-family: var(--font-mono); font-size: 11px;
    letter-spacing: 0.15em; text-transform: uppercase; color: var(--ink-mute);
}

.ways-grid {
    display: grid; grid-template-columns: 1fr 1fr;
    border-top: 1.5px solid var(--ink); border-left: 1.5px solid var(--ink);
}
@media (max-width: 768px) { .ways-grid { grid-template-columns: 1fr; } }

.way-card {
    position: relative; padding: 40px 36px;
    border-right: 1.5px solid var(--ink); border-bottom: 1.5px solid var(--ink);
    cursor: pointer; overflow: hidden; min-height: 280px;
    display: flex; flex-direction: column; justify-content: space-between;
    background: var(--cream); text-decoration: none; color: var(--ink);
    transition: color 0.35s ease;
}
.way-card::before {
    content: ''; position: absolute; inset: 0; background: var(--lime);
    transform: translateX(-101%); transition: transform 0.45s cubic-bezier(0.65, 0, 0.35, 1); z-index: 0;
}
.way-card > * { position: relative; z-index: 1; }
.way-card:hover::before { transform: translateX(0); }
.way-card:hover .card-num { transform: scale(1.15); }
.way-card:hover .card-arrow { transform: translateX(6px); }
.way-card:hover .card-shape { transform: rotate(45deg) scale(1.1); }

.card-top { display: flex; justify-content: space-between; align-items: flex-start; }
.card-num {
    font-family: var(--font-display); font-size: 64px;
    font-weight: 500; line-height: 0.9; letter-spacing: -0.04em;
    transition: transform 0.35s ease; transform-origin: bottom left;
}
.card-shape { width: 22px; height: 22px; transition: transform 0.4s ease; }
.card-shape svg { width: 100%; height: 100%; fill: none; stroke: var(--ink); stroke-width: 1.5; }
.card-shape.filled svg { fill: var(--ink); }
.card-body { margin-top: auto; padding-top: 40px; }
.card-label {
    font-family: var(--font-mono); font-size: 10px;
    letter-spacing: 0.18em; text-transform: uppercase; color: var(--ink-mute); margin-bottom: 14px;
}
.card-title {
    font-family: var(--font-display); font-size: 28px;
    font-weight: 500; letter-spacing: -0.02em; line-height: 1.08; margin-bottom: 12px;
}
.card-desc { font-size: 14px; line-height: 1.55; color: var(--ink-mute); margin-bottom: 22px; max-width: 420px; }
.card-arrow {
    font-family: var(--font-mono); font-size: 12px; font-weight: 500;
    letter-spacing: 0.05em; display: inline-flex; align-items: center; gap: 8px;
    transition: transform 0.3s ease;
}

.method-row {
    padding: 36px 0; border-top: 1px solid var(--rule); margin-top: 80px;
    display: flex; justify-content: space-between; align-items: center;
    flex-wrap: wrap; gap: 24px;
}
.method-title { display: flex; align-items: center; gap: 16px; }
.method-title .square { width: 12px; height: 12px; background: var(--ink); }
.method-title .label { font-family: var(--font-display); font-size: 20px; font-weight: 500; letter-spacing: -0.015em; }
.method-title .sub { font-size: 15px; color: var(--ink-mute); }

.footer-strip {
    margin-top: 80px; padding: 32px 0; border-top: 1.5px solid var(--ink);
    display: flex; justify-content: space-between; align-items: center;
    flex-wrap: wrap; gap: 16px; font-family: var(--font-mono);
    font-size: 10px; letter-spacing: 0.12em; text-transform: uppercase; color: var(--ink-mute);
}
.footer-strip .team { color: var(--ink); font-weight: 500; }
</style>
</head>
<body>
<div class="wrap">

<div class="topbar">
    <div class="brand">
        <span class="dot"></span>
        <span>Global Road Safety Explorer</span>
    </div>
    <span>WHO &middot; IHME / 1990 &mdash; 2023</span>
</div>

<section class="hero">
    <div class="eyebrow fade-up" id="rev-eyebrow">
        <span class="marker"></span>
        <span>DIVE IN </span>
    </div>

    <h1 class="display-xl" style="margin-top: 36px;">
        <span><span id="typed-1"></span><span id="cur-1" class="cursor"></span></span><br/>
        <span><span id="typed-2"></span><span id="cur-2" class="cursor" style="display:none;"></span></span><br/>
        <span class="accent"><span id="typed-3"></span><span id="cur-3" class="cursor" style="display:none;"></span></span>
    </h1>

    <p class="lede fade-up" id="rev-lede">
        An interactive atlas of fatality patterns across 171 countries &mdash; built on the WHO 2023 Global
        Status Report and three decades of IHME mortality data.
    </p>

    <div class="cta-row fade-up" id="rev-cta">
        <a class="cta-primary" href="#" onclick="goTo('Atlas'); return false;">
            <span>Open the atlas</span>
            <span class="arrow">&rarr;</span>
        </a>
        <a class="cta-secondary" href="#" onclick="goTo('Upload'); return false;">
            <span>Upload your data</span>
        </a>
    </div>
</section>

<section class="map-preview fade-up">
    <div class="map-meta">
        <div>
            <div class="eyebrow"><span class="marker"></span><span>Preview &middot; the atlas</span></div>
            <h2 class="display-lg" style="margin-top:18px;">171 countries, <span class="map-accent">grouped.</span></h2>
        </div>
        <div class="map-meta-right"></div>
    </div>

    <div class="map-frame">
        <svg id="map-svg" viewBox="0 0 1000 500" preserveAspectRatio="xMidYMid meet"></svg>
        <div id="hover-card"></div>
        <div id="map-loading"><div class="loading-dot"></div><span>Loading the world&hellip;</span></div>
        <div id="map-error"><span>Preview unavailable &mdash;</span><span style="color:var(--ink); font-weight:500;">open the full atlas below.</span></div>
        <a class="map-cta" href="#" onclick="goTo('Atlas'); return false;">Open full atlas <span class="arr">&rarr;</span></a>
    </div>

    <div class="map-legend">
        <div class="legend-item"><span class="legend-swatch" style="background:#4A4A48;"></span><span>0 / Developing road profile</span></div>
        <div class="legend-item"><span class="legend-swatch" style="background:#0A0A0A;"></span><span>1 / Rich car culture</span></div>
        <div class="legend-item"><span class="legend-swatch" style="background:#C6FF3D;"></span><span>2 / Low-motorization mixed &mdash; Palestine</span></div>
        <div class="legend-item"><span class="legend-swatch" style="background:#8A8880;"></span><span>3 / Atypical reporting</span></div>
        <div class="legend-item"><span class="legend-swatch" style="background:#DDD8CC;"></span><span>No data</span></div>
    </div>
</section>

<div class="stat-strip">
    <div class="stat-cell fade-up" data-delay="0"><div class="stat-num">171</div><div class="stat-label">Countries</div></div>
    <div class="stat-cell fade-up" data-delay="80"><div class="stat-num">27</div><div class="stat-label">Indicators</div></div>
    <div class="stat-cell fade-up" data-delay="160"><div class="stat-num">4</div><div class="stat-label">Clusters found</div></div>
    <div class="stat-cell fade-up" data-delay="240"><div class="stat-num">30<span class="unit">yr</span></div><div class="stat-label">Time horizon</div></div>
</div>

<div class="section-head">
    <h2 class="display-lg"><span id="typed-sec"></span></h2>
    <span class="index">01 &mdash; 04</span>
</div>

<div class="ways-grid">

    <a class="way-card" href="#" onclick="goTo('Atlas'); return false;">
        <div class="card-top">
            <div class="card-num">01</div>
            <div class="card-shape"><svg viewBox="0 0 24 24"><circle cx="12" cy="12" r="10"/><circle cx="12" cy="12" r="3" fill="#0A0A0A"/></svg></div>
        </div>
        <div class="card-body">
            <div class="card-label">Atlas / World map</div>
            <h3 class="card-title">Every country, on a map</h3>
            <p class="card-desc">Colored by cluster. Hover for the country brief. Palestine starred.</p>
            <span class="card-arrow">Open <span>&rarr;</span></span>
        </div>
    </a>

    <a class="way-card" href="#" onclick="goTo('Compare'); return false;">
        <div class="card-top">
            <div class="card-num">02</div>
            <div class="card-shape filled"><svg viewBox="0 0 24 24"><rect x="2" y="2" width="20" height="20"/><rect x="9" y="9" width="6" height="6" fill="#F4F1EA" stroke="none"/></svg></div>
        </div>
        <div class="card-body">
            <div class="card-label">Compare / Radar</div>
            <h3 class="card-title">Palestine vs. its peers</h3>
            <p class="card-desc">Overlay up to four countries on a radar across all 27 indicators.</p>
            <span class="card-arrow">Open <span>&rarr;</span></span>
        </div>
    </a>

    <a class="way-card" href="#" onclick="goTo('Landscape'); return false;">
        <div class="card-top">
            <div class="card-num">03</div>
            <div class="card-shape"><svg viewBox="0 0 24 24"><polygon points="12,3 21,21 3,21"/><circle cx="12" cy="16" r="2.5" fill="#0A0A0A"/></svg></div>
        </div>
        <div class="card-body">
            <div class="card-label">Landscape / PCA</div>
            <h3 class="card-title">171 countries, one plane</h3>
            <p class="card-desc">PCA scatter compressing every indicator to two dimensions. Outliers flagged automatically.</p>
            <span class="card-arrow">Open <span>&rarr;</span></span>
        </div>
    </a>

    <a class="way-card" href="#" onclick="goTo('Trends'); return false;">
        <div class="card-top">
            <div class="card-num">04</div>
            <div class="card-shape"><svg viewBox="0 0 24 24"><line x1="3" y1="21" x2="21" y2="3"/><circle cx="21" cy="3" r="3" fill="#0A0A0A"/></svg></div>
        </div>
        <div class="card-body">
            <div class="card-label">Trends / Forecast</div>
            <h3 class="card-title">Three decades, forecast ahead</h3>
            <p class="card-desc">Per-country fatality trends 1990 &ndash; 2019 with a short forward projection.</p>
            <span class="card-arrow">Open <span>&rarr;</span></span>
        </div>
    </a>

</div>

<div class="method-row"
     onclick="openReadme()"
     style="cursor: pointer;">
    <div class="method-title">
        <span class="square"></span>
        <span class="label">Methodology</span>
        <span class="sub">&mdash; how this was built.</span>
    </div>
    <span style="font-family: 'JetBrains Mono', monospace; font-size: 11px; letter-spacing: 0.1em; text-transform: uppercase; color: #4A4A48;">Read &rarr;</span>
</div>
<div class="footer-strip">
    <span>Data Mining 10672349 / An-Najah / Dr. Abualia</span>
    <span class="team"></span>
    <span>v 1.0 / May 2026</span>
</div>

</div>

<!-- D3 + TopoJSON from jsdelivr -->
<script src="https://cdn.jsdelivr.net/npm/d3@7/dist/d3.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/topojson-client@3/dist/topojson-client.min.js"></script>

<script>
// Robust nav helper — works inside Streamlit's iframe in every deployment.
// Streamlit serves multipage routes at /PageName (the filename minus the
// numeric prefix and underscore). Filenames are 0_Upload.py, 1_Atlas.py, etc.
function goTo(page) {
    try {
        var origin = window.top.location.origin;
        window.top.location.href = origin + '/' + page;
    } catch (e) {
        // Cross-origin fallback (rare on local, possible on some hosts)
        window.location.href = '/' + page;
    }
}

function openReadme() {
    var url = 'https://github.com/Baasmaala/road-safety-explorer#readme';
    var win = window.open(url, '_blank', 'noopener,noreferrer');
    if (!win) {
        try { window.top.location.href = url; }
        catch (e) { window.location.href = url; }
    }
}
// Embedded data (populated by Python)
var CLUSTERS = __CLUSTERS_JSON__;
var NUM_TO_A3 = __NUM_JSON__;

var CLUSTER_COLORS = {
    0: '#4A4A48',
    1: '#0A0A0A',
    2: '#C6FF3D',
    3: '#8A8880'
};
var NO_DATA_FILL = '#DDD8CC';
var LIME = '#C6FF3D';
var INK = '#0A0A0A';

function showMapError() {
    var loading = document.getElementById('map-loading');
    var err = document.getElementById('map-error');
    if (loading) loading.style.display = 'none';
    if (err) err.style.display = 'flex';
}

function initMap() {
    if (typeof d3 === 'undefined' || typeof topojson === 'undefined') {
        showMapError();
        return;
    }

    var svg = d3.select('#map-svg');
    var stage = document.querySelector('.map-frame');
    var hoverCard = document.getElementById('hover-card');
    var loading = document.getElementById('map-loading');

    var projection = d3.geoNaturalEarth1().scale(180).translate([500, 250]);
    var path = d3.geoPath(projection);

    d3.json('https://cdn.jsdelivr.net/npm/world-atlas@2/countries-110m.json')
      .then(function(world) {
          if (loading) loading.style.display = 'none';
          var countries = topojson.feature(world, world.objects.countries).features;

          var g = svg.append('g');
          var palestinePath = null;

          g.selectAll('path')
            .data(countries)
            .join('path')
            .attr('class', function(d) {
                var num = String(d.id).padStart(3, '0');
                var iso3 = NUM_TO_A3[num];
                var cls = 'country';
                if (iso3 === 'PSE') cls += ' palestine';
                if (!iso3 || !CLUSTERS[iso3]) cls += ' no-data';
                return cls;
            })
            .attr('fill', function(d) {
                var num = String(d.id).padStart(3, '0');
                var iso3 = NUM_TO_A3[num];
                if (iso3 && CLUSTERS[iso3]) {
                    return CLUSTER_COLORS[CLUSTERS[iso3].c];
                }
                return NO_DATA_FILL;
            })
            .attr('d', path)
            .each(function(d) {
                var num = String(d.id).padStart(3, '0');
                if (NUM_TO_A3[num] === 'PSE') palestinePath = this;
            })
            .on('mousemove', function(event, d) {
                var num = String(d.id).padStart(3, '0');
                var iso3 = NUM_TO_A3[num];
                var info = iso3 ? CLUSTERS[iso3] : null;
                var rect = stage.getBoundingClientRect();
                var x = event.clientX - rect.left;
                var y = event.clientY - rect.top;
                var name = (d.properties && d.properties.name) ? d.properties.name : 'Unknown';
                if (info) {
                    hoverCard.innerHTML =
                        '<div class="h-name">' + info.n + '</div>' +
                        '<div class="h-cluster">Cluster ' + info.c + ' / ' + info.cn + '</div>';
                } else {
                    hoverCard.innerHTML =
                        '<div class="h-name">' + name + '</div>' +
                        '<div class="h-cluster muted">No data</div>';
                }
                var cardW = 220, cardH = 70;
                hoverCard.style.left = Math.min(Math.max(x + 14, 8), rect.width - cardW - 8) + 'px';
                hoverCard.style.top = Math.min(Math.max(y + 14, 8), rect.height - cardH - 8) + 'px';
                hoverCard.classList.add('show');
            })
            .on('mouseleave', function() {
                hoverCard.classList.remove('show');
            })
            .on('click', function(event, d) {
                goTo('Atlas');
            });

          // Re-append Palestine so its thick border sits on top of neighbors
          if (palestinePath) g.node().appendChild(palestinePath);
      })
      .catch(function(err) {
          console.error('Map load failed:', err);
          showMapError();
      });
}

// Wait for both libs; bail after 6 seconds
var attempts = 0;
var checkLibs = setInterval(function() {
    attempts++;
    if (typeof d3 !== 'undefined' && typeof topojson !== 'undefined') {
        clearInterval(checkLibs);
        initMap();
    } else if (attempts > 30) {
        clearInterval(checkLibs);
        showMapError();
    }
}, 200);
</script>

<script>
(function () {
    var lines = [
        { id: 'typed-1', cursor: 'cur-1', text: "Reading the world's", speed: 38 },
        { id: 'typed-2', cursor: 'cur-2', text: "road-safety record,", speed: 38 },
        { id: 'typed-3', cursor: 'cur-3', text: "one country at a time.", speed: 42 }
    ];

    function typeLine(i) {
        if (i >= lines.length) {
            ['rev-eyebrow', 'rev-lede', 'rev-cta'].forEach(function (id, idx) {
                setTimeout(function () {
                    var el = document.getElementById(id);
                    if (el) el.classList.add('in');
                }, idx * 180);
            });
            return;
        }
        var line = lines[i];
        var target = document.getElementById(line.id);
        var cursor = document.getElementById(line.cursor);
        if (!target) { typeLine(i + 1); return; }
        if (i > 0) {
            var prev = document.getElementById(lines[i - 1].cursor);
            if (prev) prev.style.display = 'none';
        }
        if (cursor) cursor.style.display = 'inline-block';
        var idx = 0;
        var interval = setInterval(function () {
            target.textContent = line.text.slice(0, idx + 1);
            idx++;
            if (idx >= line.text.length) {
                clearInterval(interval);
                setTimeout(function () { typeLine(i + 1); }, 240);
            }
        }, line.speed);
    }

    function typeSection(target, text, speed) {
        target.textContent = '';
        var idx = 0;
        var interval = setInterval(function () {
            target.textContent = text.slice(0, idx + 1);
            idx++;
            if (idx >= text.length) clearInterval(interval);
        }, speed);
    }

    function init() {
        typeLine(0);

        var io = new IntersectionObserver(function (entries) {
            entries.forEach(function (entry) {
                if (entry.isIntersecting) {
                    var el = entry.target;
                    var delay = parseInt(el.dataset.delay || '0', 10);
                    setTimeout(function () { el.classList.add('in'); }, delay);

                    if (el.classList.contains('section-head')) {
                        var sec = document.getElementById('typed-sec');
                        if (sec && !sec.dataset.done) {
                            sec.dataset.done = '1';
                            typeSection(sec, 'Four ways in.', 42);
                        }
                    }
                    io.unobserve(el);
                }
            });
        }, { threshold: 0.2 });

        document.querySelectorAll('.fade-up, .section-head').forEach(function (el) {
            io.observe(el);
        });
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }
})();
</script>

</body>
</html>
"""

# Inject the data into the HTML (replace placeholders to avoid f-string brace hell)
HOMEPAGE_HTML = HOMEPAGE_HTML.replace("__CLUSTERS_JSON__", CLUSTERS_JS)
HOMEPAGE_HTML = HOMEPAGE_HTML.replace("__NUM_JSON__", ISO_NUM_JS)

# Render inside an iframe — required for HTML this size to work in Streamlit
components.html(HOMEPAGE_HTML, height=2500, scrolling=True)