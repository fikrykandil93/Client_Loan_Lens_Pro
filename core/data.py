"""Cached data loading and portfolio statistics."""
from pathlib import Path

import pandas as pd
import streamlit as st

ROOT = Path(__file__).resolve().parent.parent
DATA_FILE = ROOT / "Clients_LoanLens_clean.parquet"


@st.cache_data(show_spinner=False)
def load_clients() -> pd.DataFrame:
    return pd.read_parquet(DATA_FILE)


@st.cache_data(show_spinner=False)
def load_applications() -> pd.DataFrame:
    """Clients with a past application (Approved / Refused) + helper columns for Insights."""
    df = load_clients()
    df = df[df["NAME_CONTRACT_STATUS"].notna()].copy()
    df["REFUSED"] = (df["NAME_CONTRACT_STATUS"] == "Refused").astype(int)
    df["AGE_GROUP"] = pd.cut(df["AGE_YEARS"], bins=range(20, 75, 5), right=False).astype(str)
    df["AGE_GROUP"] = df["AGE_GROUP"].str.replace(r"\[(\d+), (\d+)\)", r"\1–\2", regex=True)
    df["TERM_GROUP"] = pd.cut(df["CNT_PAYMENT"], bins=[-1, 0, 6, 12, 24, 36, 60, 100],
                              labels=["No term", "1–6", "7–12", "13–24", "25–36", "37–60", "60+"])
    return df


def refusal_rate(df: pd.DataFrame, col: str, min_apps: int = 0) -> pd.DataFrame:
    """Applications and refusal rate (%) per category of a column."""
    out = (df.groupby(col, observed=True)["REFUSED"]
             .agg(Applications="size", Refusal_Rate="mean").reset_index())
    out["Refusal_Rate"] = out["Refusal_Rate"] * 100
    return out[out["Applications"] >= min_apps]


@st.cache_data(show_spinner=False)
def portfolio_kpis() -> dict:
    df = load_clients()
    status = df["NAME_CONTRACT_STATUS"]
    with_app = int(status.notna().sum())
    approved = int((status == "Approved").sum())
    refused = int((status == "Refused").sum())
    return {
        "clients": len(df),
        "with_application": with_app,
        "no_application": len(df) - with_app,
        "approved": approved,
        "refused": refused,
        "approved_pct": approved / with_app * 100,
        "refused_pct": refused / with_app * 100,
    }


@st.cache_data(show_spinner=False)
def client_segments() -> pd.Series:
    """Segment name of every client (KMeans pipeline from the segmentation notebook)."""
    from core.model_service import load_models

    *_, segment, segment_inputs, segment_names = load_models()
    df = load_clients()
    rows = df.assign(INCOME_PER_PERSON=df["AMT_INCOME_TOTAL"] / df["CNT_FAM_MEMBERS"])
    return pd.Series(segment.predict(rows[segment_inputs]), index=df.index).map(segment_names)


@st.cache_data(show_spinner=False)
def segment_summary() -> pd.DataFrame:
    """Profile of each segment + share of clients and refusal rate of past applications."""
    from core.model_service import load_segment_profile

    df = load_clients()
    seg = client_segments()
    status = df["NAME_CONTRACT_STATUS"]
    refused = (status[status.notna()] == "Refused").groupby(seg[status.notna()]).mean() * 100
    out = load_segment_profile().copy()
    out["Share"] = out["Clients"] / out["Clients"].sum() * 100
    out["Refusal_Rate"] = refused
    return out


@st.cache_data(show_spinner=False)
def feature_importance(top: int = 8) -> pd.Series:
    """XGBoost importance (%) summed into the same reader-friendly groups as the reasons."""
    from core.model_service import REASON_GROUPS, _column_owners, load_models

    approval, *_ = load_models()
    imp = pd.Series(approval.steps[-1][1].feature_importances_, index=_column_owners()).groupby(level=0).sum()
    group_of = {c: label for label, cols in REASON_GROUPS.items() for c in cols}
    grouped = imp.groupby(imp.index.map(lambda c: group_of.get(c, c))).sum() * 100
    return grouped.sort_values(ascending=False).head(top)


def find_client(client_id: int) -> pd.Series | None:
    """One client's record (index = SK_ID_CURR), or None if the ID is not in the data."""
    df = load_clients()
    return df.loc[client_id] if client_id in df.index else None
