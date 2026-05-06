ROAD SAFETY EXPLORER — TEAM WORKSPACE

Course: Data Mining 10672349, An-Najah
Deadline: May 13, 2026
Presentation: May 14 or 18

GROUP LEADER: [Basmala Shtayeh]

TEAM ROLES:
- Person 1 — Clustering owner — [Basmala Shtayeh]
- Person 2 — PCA + Anomaly owner — [Osama]
- Person 3 — Time Series owner — [Omar]


WHAT WE ARE BUILDING

A Streamlit web app that analyzes road safety patterns across ~170
countries using WHO + IHME data, with Palestine as the spotlight country.
Four data mining techniques: clustering, PCA, time-series forecasting,
anomaly detection.


HOW THIS WORKSPACE IS ORGANIZED

data/raw/         The original WHO Excel + IHME CSV. NEVER edit these.
data/processed/   Cleaned outputs from notebooks. Read by other notebooks.
notebooks/        One notebook per person. Each owns theirs.
docs/             This file + meeting notes + slide drafts.


HOW TO START: YOU ALL SHOULD 

1. Open Google Drive → road-safety-explorer
2. Open notebooks/00_setup_check.ipynb
3. Run all cells. If everything prints success, you are ready.
4. Open YOUR notebook (the one with your role number).


NOTEBOOK OWNERSHIP RULE

- You only EDIT your own notebook.
- You can READ anyone else's anytime.
- Handoffs between teammates go through data/processed/ as CSV files.
  Person 1 saves a file there, Person 2 reads it. No live variable sharing.


WHAT EACH PERSON DOES

Person 1 (Clustering owner) — 01_data_cleaning.ipynb
- Clean the WHO Excel file
- Normalize country names (Palestine has multiple variants)
- Build country_features.csv → save to data/processed/
- Run K-Means, justify k via elbow method
- Document every cleaning decision in markdown cells

Person 2 (PCA + Anomaly owner) — 02_clustering_pca_anomaly.ipynb
- Read country_features.csv from data/processed/
- Standardize features
- Run PCA, report explained variance
- Run Isolation Forest for outlier countries
- Save country_pca.csv + country_anomalies.csv to data/processed/

Person 3 (Time Series owner) — 03_timeseries_forecast.ipynb
- Read output.csv from data/raw/
- Build per-country time series, decide raw deaths vs per-100k
- Try ARIMA and Holt-Winters, validate, pick one with justification
- Forecast 3 years ahead with confidence intervals
- Detect anomaly years via residuals (>2 sigma)
- Save country_forecasts.csv + country_year_anomalies.csv to data/processed/


CHECK-IN SCHEDULE

Day 1 evening: everyone has opened their notebook and loaded data
Day 3 evening: each person presents preliminary results to the others
Day 5 evening: all data/processed/ files final. Streamlit work begins.
Day 7: polish, slides, demo video, README.


GROUND RULES

- Comment every non-obvious decision in markdown cells.
- If you change someone else's file in data/processed/, tell them.
- All meetings logged below under MEETING NOTES.
- If stuck for more than 2 hours, message the group.


AI USAGE LOG (required by the brief)

The professor requires us to declare any AI used. Add an entry every
time you use AI assistance, like:
  - 2026-05-07, [name]: Used Claude to debug pandas merge error
  - 2026-05-08, [name]: Used Claude to draft README structure
We compile this into the AI Disclosure section of the final README.


MEETING NOTES

[fill in as we go]
