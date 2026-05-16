"""
upload_pipeline.py — Process any user-uploaded country CSV.

Two routes auto-detected from the file's columns:

1. WHO-format: the upload's columns substantially overlap the WHO 2023
   feature set. We re-fit Basmala's model on the original WHO data
   (with the same random_state) and use it to label the uploaded
   countries — so cluster IDs match the rest of the app (Atlas / Compare /
   Landscape).

2. Generic: any country-level CSV. We call `clean_country_dataset`
   (copied verbatim from Notebook 01) with K forced to 4 so the UI
   stays consistent.

A separate `project_to_2d` runs PCA(2) for the cluster-landscape scatter
the Upload page draws.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
from scipy import stats
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
from sklearn.metrics import silhouette_score
from sklearn.preprocessing import StandardScaler


# Same map used everywhere — apply defensively to any uploaded file
COUNTRY_NAME_MAP = {
    "occupied Palestinian territory, including east Jerusalem": "Palestine",
    "occupied Palestinian territory": "Palestine",
    "State of Palestine": "Palestine",
    "Palestinian Territory": "Palestine",
    "West Bank and Gaza Strip": "Palestine",
}

K_CLUSTERS = 4
RANDOM_STATE = 42


# ============================================================
# clean_country_dataset — COPIED VERBATIM FROM NOTEBOOK 01
# (with K=4 forced by default for Upload-page consistency)
# ============================================================
def clean_country_dataset(raw_df, country_col=None, missing_threshold=0.5, k=K_CLUSTERS):
    """
    Run the same cleaning pipeline used on the WHO data on any uploaded
    country-level dataframe.

    Parameters
    ----------
    raw_df : pandas DataFrame
        The user's uploaded data.
    country_col : str or None
        Name of the column that holds the country name. If None, the function
        tries common names ('Country', 'Entity', etc.) and falls back to the
        first non-numeric column.
    missing_threshold : float
        Drop any column with more than this fraction of missing values.
    k : int or None
        Number of clusters. If None, the function picks the k with the
        highest silhouette score. Defaults to 4 to match the rest of the app.

    Returns
    -------
    dict with keys: features, labels_df, cluster_labels, k_used,
                    scaler, dropped_cols, constant_cols, outlier_cols
    """
    df_work = raw_df.copy()

    # auto-detect the country column if not provided
    if country_col is None:
        candidates = ['Country name', 'Country', 'country', 'Entity', 'entity', 'Name', 'name']
        for cand in candidates:
            if cand in df_work.columns:
                country_col = cand
                break
        if country_col is None:
            non_num = df_work.select_dtypes(exclude='number').columns
            if len(non_num) > 0:
                country_col = non_num[0]
            else:
                raise ValueError("No country column found in uploaded data")

    # 1. normalize country names if our map applies
    if country_col in df_work.columns:
        df_work[country_col] = df_work[country_col].replace(COUNTRY_NAME_MAP)

    # 2. drop mostly-empty columns
    miss_share = df_work.isna().mean()
    dropped = miss_share[miss_share > missing_threshold].index.tolist()
    df_work = df_work.drop(columns=dropped)

    # 3. pick numeric features, fill missing with median
    num = df_work.select_dtypes(include='number').copy()
    num = num.fillna(num.median(numeric_only=True))

    # 4. drop constant columns (zero variance)
    constant = [c for c in num.columns if num[c].nunique() <= 1]
    num = num.drop(columns=constant)

    # 5. drop columns with extreme skewness (severe outlier drivers)
    if len(num.columns) > 0:
        skew_vals = num.apply(lambda x: stats.skew(x.dropna()) if x.notna().any() else 0)
        outlier_cols = skew_vals[skew_vals > 5].index.tolist()
        num = num.drop(columns=outlier_cols)
    else:
        outlier_cols = []

    # 6. scale
    scl = StandardScaler()
    X = scl.fit_transform(num)

    # 7. pick k by silhouette if not given
    if k is None and len(X) >= 4:
        best_k, best_score = 2, -1
        for trial_k in range(2, min(9, len(X))):
            km = KMeans(n_clusters=trial_k, random_state=42, n_init=10)
            lbl = km.fit_predict(X)
            score = silhouette_score(X, lbl)
            if score > best_score:
                best_k, best_score = trial_k, score
        k = best_k

    # 8. fit final
    final_km = KMeans(n_clusters=k, random_state=42, n_init=10)
    final_labels = final_km.fit_predict(X)

    # 9. build labels frame (whatever non-numeric cols are available)
    label_cols_available = [c for c in df_work.columns if c not in num.columns]
    labels_df = df_work[label_cols_available].copy()
    labels_df['Cluster'] = final_labels
    # Generic readable name — uploaded data has no domain meaning, so we just
    # number the groups starting from 1 for the UI.
    labels_df['Cluster_name'] = labels_df['Cluster'].apply(lambda x: f'Group {x + 1}')

    return {
        'features': pd.DataFrame(X, columns=num.columns),
        'labels_df': labels_df,
        'cluster_labels': final_labels,
        'k_used': k,
        'scaler': scl,
        'dropped_cols': dropped,
        'constant_cols': constant,
        'outlier_cols': outlier_cols,
        'country_col': country_col,
    }


# ============================================================
# project_to_2d — PCA(2) on the cleaned features
# ============================================================
def project_to_2d(features: pd.DataFrame) -> dict:
    """Run PCA(2) on the scaled feature matrix. Returns coords + variance."""
    pca = PCA(n_components=2, random_state=RANDOM_STATE)
    coords = pca.fit_transform(features.values)
    return {
        'PC1': coords[:, 0],
        'PC2': coords[:, 1],
        'explained_variance': (
            float(pca.explained_variance_ratio_[0]),
            float(pca.explained_variance_ratio_[1]),
        ),
    }


# ============================================================
# detect_format — decide WHO vs generic
# ============================================================
def detect_format(raw_df: pd.DataFrame, who_features_path) -> str:
    """WHO-format = >=70% of WHO's feature columns are present in the upload."""
    try:
        who = pd.read_csv(who_features_path, nrows=2)
    except Exception:
        return "generic"

    who_cols = {c for c in who.columns if c.upper() not in {"ISO", "CODE"}}
    if not who_cols:
        return "generic"

    overlap = who_cols.intersection(set(raw_df.columns))
    return "who" if (len(overlap) / len(who_cols)) >= 0.70 else "generic"


# ============================================================
# WHO-mode: re-fit Basmala's model on her WHO data, predict on upload
# ============================================================
def cluster_who_mode(raw_df: pd.DataFrame, who_features_path) -> dict:
    """
    Uploaded file is WHO-format. Re-fit on Basmala's full WHO dataset
    (deterministic with fixed random_state) so the uploaded countries
    get labelled against the SAME four clusters as Atlas / Compare /
    Landscape.

    Returns a dict shaped like clean_country_dataset's so the Upload
    page can treat both modes uniformly.
    """
    who = pd.read_csv(who_features_path)

    # Normalize the WHO file's ISO column name
    iso_col = None
    for c in ["ISO", "iso", "Code", "code"]:
        if c in who.columns:
            iso_col = c
            break
    if iso_col is None:
        iso_col = who.columns[0]
    who = who.rename(columns={iso_col: "ISO"})

    # Detect upload's country column
    country_col = None
    candidates = ['Country name', 'Country', 'country', 'Entity', 'entity', 'Name', 'name']
    for cand in candidates:
        if cand in raw_df.columns:
            country_col = cand
            break
    if country_col is None:
        non_num = raw_df.select_dtypes(exclude='number').columns
        country_col = non_num[0] if len(non_num) > 0 else None

    upload = raw_df.copy()
    if country_col and country_col in upload.columns:
        upload[country_col] = upload[country_col].replace(COUNTRY_NAME_MAP)

    # Keep only columns that exist in BOTH files
    shared = [c for c in who.columns if c in upload.columns and c != "ISO"]
    if not shared:
        # Fall back to generic if WHO data and upload don't share columns
        return clean_country_dataset(raw_df)

    X_who = who[shared].fillna(who[shared].median(numeric_only=True)).values
    X_upload = upload[shared].fillna(upload[shared].median(numeric_only=True)).values

    scaler = StandardScaler().fit(X_who)
    X_who_s = scaler.transform(X_who)
    X_upload_s = scaler.transform(X_upload)

    km = KMeans(n_clusters=K_CLUSTERS, n_init=10, random_state=RANDOM_STATE)
    km.fit(X_who_s)
    upload_clusters = km.predict(X_upload_s)

    # Names used elsewhere in the app
    CLUSTER_NAMES = {
        0: "Developing-country road profile",
        1: "Rich-country car culture",
        2: "Low-motorization mixed",
        3: "Atypical reporting",
    }

    labels_df = upload[[country_col] if country_col else []].copy()
    labels_df['Cluster'] = upload_clusters
    labels_df['Cluster_name'] = [CLUSTER_NAMES.get(int(c), f"Cluster {c}") for c in upload_clusters]

    features_df = pd.DataFrame(X_upload_s, columns=shared)

    return {
        'features': features_df,
        'labels_df': labels_df,
        'cluster_labels': upload_clusters,
        'k_used': K_CLUSTERS,
        'scaler': scaler,
        'dropped_cols': [c for c in upload.columns if c not in shared and c != country_col],
        'constant_cols': [],
        'outlier_cols': [],
        'country_col': country_col,
    }