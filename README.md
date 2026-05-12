# Road-Safety-Explorer
## Data Sources

This project uses two real, publicly available datasets. Both are committed to the repo at `data/raw/` so the analysis runs without any external downloads.

### 1. WHO Global Status Report on Road Safety 2023

**Source:** World Health Organization
**Direct link:** [WHO road safety indicators (XLSX)](https://cdn.who.int/media/docs/default-source/documents/health-topics/road-traffic-injuries/gsrrs23-indicators-for-participating-countries-or-territories.xlsx?sfvrsn=88035adb_3)
**File in repo:** `data/raw/gsrrs23-indicators-for-participating-countries-or-territories.xlsx`
**Format:** Excel spreadsheet, 173 rows × 228 columns
**License:** CC BY-NC-SA 3.0 IGO

**What it contains:**
The WHO Global Status Report on Road Safety is published every few years and is the most comprehensive country-level road safety dataset available. The 2023 edition covers 171 participating countries and territories across 228 indicators including:

- Reported and WHO-estimated road traffic fatalities
- Fatality breakdowns by gender and road user type (pedestrians, cyclists, 2-wheeler riders, drivers)
- Vehicle counts (cars, motorbikes, heavy trucks, buses)
- Road infrastructure (total paved kilometres)
- Legislation scores (speed limits, drink driving, helmet laws, seat belt laws, child restraint laws)
- WHO regional and World Bank income group classifications

**How we use it:**
This dataset drives the clustering, PCA, and spatial anomaly detection pages of the app. Each country becomes a single point in a high-dimensional space defined by its road safety profile, and K-Means groups countries with similar profiles together.

### 2. Road Traffic Deaths 1990–2019 (IHME)

**Source:** Institute for Health Metrics and Evaluation (IHME), Global Burden of Disease study, accessed via Kaggle
**File in repo:** `data/raw/output.csv`
**Format:** CSV, 8,010 rows × 6 columns
**Columns:** `Entity, Code, Year, Deaths, Sidedness, Historical_Population`

**What it contains:**
Annual road traffic death counts for every country from 1990 through 2019, along with the historical population for the same year. This allows us to compute deaths per 100,000 people without needing a separate population dataset.

**How we use it:**
This dataset drives the time series and temporal anomaly detection pages of the app. We fit ARIMA and Holt-Winters models to each country's 30-year death trend, forecast three years forward, and flag years where deaths deviate sharply from the trend.

### Why these two datasets together

The WHO dataset is rich (228 indicators) but cross-sectional — it captures a snapshot of where each country stands today. The IHME dataset is narrow (one indicator) but longitudinal — it shows how road safety has changed over three decades. Combining them lets the app answer both *"who is similar to Palestine right now?"* (clustering, PCA on WHO data) and *"how has Palestine's road safety changed over time, and what should we expect next?"* (forecasting on IHME data).

### A note on Palestine

Palestine appears under different names across these datasets. The WHO file labels it as *"occupied Palestinian territory, including east Jerusalem"*, while the IHME file simply uses *"Palestine"*. To allow the two datasets to be joined and compared, we normalize all variants to a single name (`"Palestine"`) using the `COUNTRY_NAME_MAP` dictionary defined in notebook 01. The ISO 3-letter code `PSE` is preserved throughout.

### Data limitations

Honest disclosure of what these datasets do and do not capture:

- **WHO data relies on country self-reports.** Quality and reporting practices vary significantly between countries. Some Palestinian indicators are marked "no data" in the source.
- **IHME data ends in 2019.** The COVID-19 pandemic substantially changed road usage and fatality patterns globally. Post-2019 patterns are not captured in our forecasts.
- **Forecasts are statistical projections, not predictions.** They assume past trends continue and do not account for policy changes, conflicts, or other interventions.
- **Cluster labels are data-driven, not policy assessments.** Two countries sharing a cluster have similar indicator profiles — this is not an endorsement or criticism of either country's road safety policy.
## AI Tool Usage Disclosure

This project was developed with assistance from AI tools. In accordance with the
course requirements, this section documents where and how AI assistance was used.

### Tools used
- **Claude (Anthropic)** 
- **Chat gpt**
 used by team members during planning

### Where AI was used

**Project planning & decisions (Basmala)**
- Brainstormed and evaluated ~15 candidate project ideas before settling on the final one
- Verified dataset availability and structure before committing to the topic
- Drafted the initial project plan, branch strategy, and team handoff structure

**Notebook 01 — Data Cleaning & Clustering (Basmala)**
- Discussed the choice between mean vs median imputation
- Discussed how to handle skewed count columns (drop raw fatality counts vs log-transform vehicle counts)

**Notebook 02 — PCA & Anomaly Detection (Osama)**


**Notebook 03 — Time Series & Forecasting (Omar)**


**Streamlit app**



