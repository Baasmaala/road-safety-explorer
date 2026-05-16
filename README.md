# Global Road Safety Explorer

A Streamlit web application that analyzes road safety patterns across 171 countries using WHO and IHME data, with Palestine as the spotlight country. The app applies four data mining techniques — K-Means clustering, PCA, time-series forecasting, and anomaly detection — and lets the user explore them through five interactive pages.

**Course:** Data Mining 10672349, An-Najah National University — Dr.-Ing. Ahmed Abualia
**Team:** Basmala Shtayeh (lead), Omar, Osama

---

## Quick start

```bash
git clone https://github.com/Baasmaala/road-safety-explorer.git
cd road-safety-explorer
pip install -r requirements.txt
streamlit run app/app.py
```

Then open the local URL Streamlit prints (usually `http://localhost:8501`).

**Requirements:** Python 3.10 or newer. No internet access is needed after installation — the WHO and IHME files are already in `data/raw/` and all processed outputs are in `data/processed/`.

---

## What the app does

The app is organized as a homepage plus five pages, each driven by a specific data mining technique:

| Page | Technique | What it shows |
|---|---|---|
| **Atlas** | K-Means clustering | World choropleth, every country colored by its cluster, with a country-detail panel comparing its 27 indicators to the cluster average |
| **Compare** | (clustering output) | Radar chart of Palestine vs up to 4 peer countries across 6 thematic indicator groups, normalized 0–1 globally |
| **Landscape** | PCA + Isolation Forest | 2D landscape of all 171 countries colored by cluster, anomaly countries flagged distinctly, Palestine starred |
| **Trends** | ARIMA / Holt-Winters + z-score anomalies | Per-country 1990–2019 fatality time series, 3-year forecast with 95% confidence band, anomaly years circled |
| **Upload** | Full pipeline | User uploads any country-level CSV; the app auto-detects the format, runs cleaning, clustering, PCA, and shows the same visuals |

---

## Datasets

Two real, publicly available datasets, both committed to the repo at `data/raw/`.

### 1. WHO Global Status Report on Road Safety 2023

- **Source:** World Health Organization
- **File:** `data/raw/gsrrs23-indicators-for-participating-countries-or-territories.xlsx`
- **Shape:** 173 rows × 228 columns (171 countries used after cleaning)
- **License:** CC BY-NC-SA 3.0 IGO
- **Direct link:** [WHO road safety indicators (XLSX)](https://cdn.who.int/media/docs/default-source/documents/health-topics/road-traffic-injuries/gsrrs23-indicators-for-participating-countries-or-territories.xlsx?sfvrsn=88035adb_3)

A cross-sectional snapshot of road safety indicators for every reporting country: fatality counts and rates, vehicle counts by category, legislation scores (speed, drink driving, helmet, seat belt, child restraint), infrastructure, and WHO region / income group classification. This is the input for clustering, PCA, and country-level anomaly detection.

### 2. IHME Road Traffic Deaths 1990–2019

- **Source:** Institute for Health Metrics and Evaluation, Global Burden of Disease study (accessed via Kaggle)
- **File:** `data/raw/output.csv`
- **Shape:** 8,010 rows × 6 columns (`Entity, Code, Year, Deaths, Sidedness, Historical_Population`)

A longitudinal series of annual road traffic deaths per country from 1990 through 2019, plus the matching population for each year (so we can compute deaths per 100,000 directly). This is the input for time-series forecasting and temporal anomaly detection.

### Why both

WHO is rich (228 indicators) but cross-sectional. IHME is narrow (one indicator) but covers 30 years. Together they let the app answer both *"who is similar to Palestine right now?"* (clustering, PCA on WHO) and *"how has Palestine's road safety changed, and what's the projection?"* (forecasting on IHME).

### Palestine name normalization

Palestine appears under different names across these sources. A single mapping is applied across every notebook and the app's upload mode:

```python
COUNTRY_NAME_MAP = {
    "occupied Palestinian territory, including east Jerusalem": "Palestine",
    "occupied Palestinian territory": "Palestine",
    "State of Palestine": "Palestine",
    "Palestinian Territory": "Palestine",
    "West Bank and Gaza Strip": "Palestine",
}
```

The IHME file already labels it "Palestine"; the WHO file uses the long form. The ISO 3-letter code `PSE` is preserved throughout.

---

## Methodology

The three notebooks in `notebooks/` produce the processed files that the app reads. Each notebook is owned by a different team member.

### Notebook 01 — Data cleaning + K-Means clustering (Basmala)

Cleans the WHO XLSX file, normalizes country names, and groups countries into 4 clusters based on their road safety profile.

- **Cleaning:** dropped columns with more than 50% missing values; dropped raw fatality counts (they correlate strongly with population, not safety); log-transformed vehicle counts to reduce skew; standardized all features with `StandardScaler`.
- **Final feature set:** 27 indicators after cleaning (down from 228 raw columns).
- **K selection:** tested k = 2 through 8 using both elbow (inertia) and silhouette scores. The elbow curve is smooth with no clear bend, and silhouette scores hover between 0.12–0.17 across all k. This means country road safety profiles form a gradient rather than crisp groups. We chose **k = 4** because it gives the four most interpretable, reasonably-sized clusters (k = 8 produced clusters with only 3–4 countries, which are too small to describe meaningfully).
- **Anchor-based label remap:** K-Means assigns cluster IDs arbitrarily, so we lock the IDs to fixed anchor countries (`PSE → 2`, `DEU → 1`, `IND → 0`). The remaining cluster gets ID 3. This keeps cluster meanings stable across re-runs and across teammates' notebooks.

**Final cluster identities:**

| ID | Name | Size | Profile |
|---|---|---|---|
| 0 | Developing-country road profile | 85 | Lower motorization, higher death rates per 100k, mixed reporting quality |
| 1 | Rich-country car culture | 53 | High motorization, strong reporting, lower fatality rate per vehicle |
| 2 | Low-motorization mixed | 25 | **Palestine's cluster** — small island states, smaller African countries, low vehicle ownership |
| 3 | Atypical reporting | 8 | Statistical outliers, often with unusual indicator patterns |

### Notebook 02 — PCA + spatial anomaly detection (Omar)

Reads the cleaned feature matrix from Notebook 01 and produces a 2D landscape plus per-country anomaly flags.

- **PCA:** standardized features → 2D projection (PC1, PC2) for visualization. PCA is used only for plotting here; the clusters themselves were already fit in Notebook 01.
- **Isolation Forest:** fit on the standardized features with `contamination = 0.05`, meaning roughly 5% of countries are expected to be flagged as anomalous. The model produces an anomaly score per country; the most extreme 9 countries are flagged.
- **Outputs:** `country_pca.csv` (all 171 countries with PC1, PC2, cluster, anomaly flag), `country_anomalies.csv` (the flagged subset).

### Notebook 03 — Time-series forecasting + temporal anomalies (Osama)

Reads the IHME yearly deaths file and produces per-country 30-year trends plus 3-year forecasts.

- **Series construction:** for each country, build a yearly series of deaths per 100,000 population from 1990 through 2019.
- **Models:** fit both ARIMA(1,1,1) and Holt-Winters (additive trend, no seasonality — yearly data) for every country. The app's Trends page displays Holt-Winters because it produced more stable forecasts across the range of country trajectories.
- **Forecast horizon:** 3 years (2020–2022), with 95% confidence intervals.
- **Temporal anomalies:** z-score on the model residuals. Years where the absolute z-score exceeds 2 are flagged as anomalies and tagged as either "above trend" or "below trend".
- **Outputs:** `country_forecasts.csv` (observed + forecast for every country-year), `country_year_anomalies.csv` (the flagged subset).

### Integration

The four techniques are not parallel branches — they feed each other:

- Clustering output (cluster ID per country) is consumed by PCA, the Atlas, Compare, and Landscape pages.
- PCA output and Isolation Forest output share the Landscape scatter, with cluster colors and anomaly markers overlaid.
- Time-series forecasts and temporal anomalies drive the Trends page, with cluster context available from the clustering output.
- The Upload page wraps Notebook 01's cleaning function so user-supplied CSVs go through the same pipeline.

---

## Repository structure

```
road-safety-explorer/
├── app/                              # the Streamlit application
│   ├── .streamlit/config.toml
│   ├── assets/                       # global CSS, homepage map
│   ├── data/                         # processed CSVs the app reads
│   ├── pages/
│   │   ├── 0_Upload.py
│   │   ├── 1_Atlas.py
│   │   ├── 2_Compare.py
│   │   ├── 3_Landscape.py
│   │   └── 4_Trends.py
│   ├── utils/                        # theme, layout, data, upload pipeline
│   └── app.py                        # homepage
├── data/
│   ├── raw/                          # WHO XLSX + IHME CSV (DO NOT EDIT)
│   └── processed/                    # outputs from the three notebooks
├── docs/                             # team workspace, screenshots
├── notebooks/
│   ├── 00_setup_check.ipynb
│   ├── 01_data_cleaningclustering.ipynb
│   ├── 02_pca_anomaly_ipynb.ipynb
│   └── 03_timeseries_forecast.ipynb
├── scripts/
├── LICENSE
├── README.md
└── requirements.txt
```

### Branching strategy

- `main` — clean, working version, updated via Pull Request.
- `basmala`, `omar`, `osama` — personal branches, one per teammate.

Each person edits only their own notebook on their own branch. Notebooks live in separate files so merges are conflict-free.

---

## Screenshots

Screenshots of the five pages live in `docs/screenshots/`:

- `docs/screenshots/01_homepage.png` — typing animation, stat strip, page cards
- `docs/screenshots/02_atlas.png` — global choropleth, cluster legend, country detail
- `docs/screenshots/03_compare.png` — radar chart, Palestine vs peers
- `docs/screenshots/04_landscape.png` — PCA scatter, anomalies flagged
- `docs/screenshots/05_trends.png` — Palestine 1990–2019 with forecast band
- `docs/screenshots/06_upload.png` — upload page with results


## Demo

A 90-second demo video walking through all five pages is available at:

`docs/demo.mp4` *(to be added)*

The narration script is in `docs/demo_script.md`.

---

## Limitations, assumptions, and weaknesses

Honest disclosure of where this system is and is not reliable.

**Data limitations**

- **WHO data relies on country self-reports.** Quality and reporting practices vary significantly between countries — what looks like a "data" difference between two countries may partly reflect how diligently each reports, not how safe its roads actually are. Some Palestinian indicators are marked "no data" in the source.
- **IHME data ends in 2019.** The COVID-19 pandemic substantially changed road usage and fatality patterns globally. Post-2019 patterns are not captured.
- **IHME deaths are modelled estimates, not direct counts.** They carry their own uncertainty band that is not displayed in the app.

**Methodology limitations**

- **Clustering structure is weak.** Silhouette scores across k = 2–8 sit in the 0.12–0.17 range, well below the 0.5 threshold considered "clear structure." The four clusters are real and interpretable, but countries near cluster boundaries could reasonably belong to either side. The clusters are descriptive groupings, not crisp categories.
- **Three of the 27 clustering features are weakly informative.** "Year reported fatalities," "Year total paved kilometres," and "Year total registered vehicles" capture *when* data was reported rather than its content. They have low variance after scaling so they don't dominate, but they should ideally be excluded from a future re-run.
- **PCA explained variance is modest.** The 2D landscape on the Landscape page is a useful visual approximation but does not capture the full 27-dimensional structure.
- **Forecasts are statistical projections, not predictions.** They assume past trends continue. They do not account for policy changes, conflict, or post-pandemic shifts. Wording in the app uses "forecast" and "projection," never "prediction."
- **ARIMA order is fixed at (1, 1, 1).** A per-country auto-ARIMA search could improve fit for some countries; we did not run it because the consistency of (1, 1, 1) across all 210 countries made the Trends page comparable.
- **Anomalies are statistical, not normative.** A country flagged as a spatial anomaly has an unusual indicator pattern compared to the global dataset — this is not an assessment that its roads are unsafe.

**Scope limitations**

- The app does not model causation. It shows similarities and changes, not why they exist.
- Cluster labels (e.g. "Developing-country road profile") are short descriptive tags chosen to be readable, not policy assessments. Countries within a cluster are not endorsed or criticized by being grouped together.
- The Upload mode works on any country-level dataset that has a country name column, but if a user uploads data with a very different feature set, the resulting clusters won't be directly comparable to the ones from the WHO data. The app surfaces this by labeling user-clusters as "Group N" rather than using the four WHO-derived names.

---

## AI tool usage disclosure

As required by the course, this section documents where and how AI assistance was used.

### Tools used

- **Claude (Anthropic)**
- **ChatGPT (OpenAI)**

### Where AI was used

Across all three notebooks and the Streamlit app, AI tools were used to help understand concepts, fix bugs, and debug specific code cells.

**Project planning and decisions (Basmala)**

- Brainstormed and evaluated around 15 candidate project ideas before settling on this one.
- Verified dataset availability and structure before committing to the topic.
- Drafted the initial project plan, branch strategy, and team handoff structure.

**Notebook 01 — Data cleaning and clustering (Basmala)**

- Discussed mean vs median imputation trade-offs.
- Discussed how to handle skewed count columns: drop raw fatality counts, log-transform vehicle counts.
- Audit of the notebook's narrative claims against the actual computed outputs.

**Notebook 02 — PCA and anomaly detection (Omar)**

- Help writing and debugging specific code cells.
- Explanation of how PCA and Isolation Forest work conceptually.

**Notebook 03 — Time series forecasting (Osama)**

- Help writing and debugging specific code cells.
- Explanation of how ARIMA and Holt-Winters models work conceptually.

**Streamlit app (Basmala)**

- Built collaboratively. Basmala directed the structure and design; Claude helped implement specific features and design elements. Many decisions came from back-and-forth discussion — Claude reminded Basmala of earlier decisions and the two iterated together on visual layout, page flow, and integration of teammates' outputs.

All AI assistance was reviewed by the team. Code was not accepted blindly — every notebook and every page was tested and verified to produce sensible output. The cluster identities, methodology choices, and final results are owned by the team.

---

## Ethical considerations

- The two datasets used (WHO and IHME) are globally trusted, publicly available, and ethically sourced.
- The framing is public-health analytics, not political. Palestine is included because it is part of both source datasets and because the team wanted to contextualize Palestinian road safety against global peers.
- Cluster labels are data-driven, descriptive groupings, not policy assessments or rankings.
- Forecasts are described as "projections" or "forecasts under stable conditions," never "predictions."
- No personally identifying information is used. All data is at the country level.

---

## License

This project is released under the MIT License — see [LICENSE](LICENSE) for details.

The underlying datasets retain their original licenses:
- WHO Global Status Report on Road Safety 2023: CC BY-NC-SA 3.0 IGO
- IHME Global Burden of Disease: see IHME terms of use

---

## Acknowledgments

- World Health Organization for the Global Status Report on Road Safety 2023.
- Institute for Health Metrics and Evaluation for the Global Burden of Disease data.
- Dr.-Ing. Ahmed Abualia for the course and project guidance.

