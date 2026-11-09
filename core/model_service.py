"""Model loading, feature building, prediction and the highest approvable amount."""
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
import streamlit as st

ROOT = Path(__file__).resolve().parent.parent
REGION_POPULATION_MEDIAN = 0.01885   # not known by the loan officer → training median (or the client's own value)
THRESHOLD = 0.5                      # refusal probability at or above this → "Refused"
MIN_AMOUNT = 10_000


@st.cache_resource(show_spinner=False)
def load_models():
    approval = joblib.load(ROOT / "XGBoost_Approval_Pipeline.pkl")
    inputs = joblib.load(ROOT / "Inputs.pkl")
    segment = joblib.load(ROOT / "KMeans_Segment_Pipeline.pkl")
    segment_inputs = joblib.load(ROOT / "Segment_Inputs.pkl")
    segment_names = joblib.load(ROOT / "Segment_Names.pkl")
    return approval, inputs, segment, segment_inputs, segment_names


@st.cache_data(show_spinner=False)
def load_segment_profile() -> pd.DataFrame:
    return pd.read_csv(ROOT / "Segment_Profile.csv").set_index("Segment_Name")


def add_ratios(row: dict) -> dict:
    """The three engineered features, exactly as in the model notebook."""
    amount, income, term = row["AMT_APPLICATION"], row["AMT_INCOME_TOTAL"], row["CNT_PAYMENT"]
    row["LOAN_TO_INCOME"] = amount / income
    row["DOWN_PAYMENT_RATIO"] = row["AMT_DOWN_PAYMENT"] / amount
    row["PAYMENT_TO_INCOME"] = (amount / term) / income if term > 0 else 0.0
    return row


def build_row(app: dict) -> dict:
    """Model input row (37 columns) from the form values."""
    row = {
        "CODE_GENDER": app["gender"],
        "NAME_FAMILY_STATUS": app["family_status"],
        "CNT_CHILDREN": app["children"],
        "CNT_FAM_MEMBERS": app["family_members"],
        "NAME_EDUCATION_TYPE": app["education"],
        "AMT_INCOME_TOTAL": float(app["income"]),
        "NAME_INCOME_TYPE": app["income_type"],
        "OCCUPATION_TYPE": app["occupation"],
        "ORGANIZATION_TYPE": app["organization"],
        "FLAG_OWN_CAR": "Y" if app["own_car"] else "N",
        "OWN_CAR_AGE": float(app["car_age"]),
        "FLAG_OWN_REALTY": "Y" if app["own_realty"] else "N",
        "NAME_HOUSING_TYPE": app["housing"],
        "REGION_POPULATION_RELATIVE": app.get("region_population", REGION_POPULATION_MEDIAN),
        "REGION_RATING_CLIENT_W_CITY": app["region_rating"],
        "LIVE_REGION_NOT_WORK_REGION": int(app["works_other_region"]),
        "EXT_SOURCE_1": app["ext1"] if app["ext1"] is not None else np.nan,
        "EXT_SOURCE_2": app["ext2"],
        "EXT_SOURCE_3": app["ext3"],
        "FLAG_DOCUMENT_3": int(app["doc_3"]),
        "FLAG_DOCUMENT_5": int(app["doc_5"]),
        "FLAG_DOCUMENT_6": int(app["doc_6"]),
        "FLAG_DOCUMENT_8": int(app["doc_8"]),
        "FLAG_EMP_PHONE": int(app.get("emp_phone", app["working"])),
        "AMT_APPLICATION": float(app["amount"]),
        "CNT_PAYMENT": float(app["term"]),
        "AMT_DOWN_PAYMENT": float(app["down_payment"]),
        "NAME_CONTRACT_TYPE": app["contract_type"],
        "NAME_CLIENT_TYPE": app["client_type"],
        "OTHER_DOCUMENTS": len(app["other_docs"]),
        "HAS_BUREAU_RECORD": int(app["has_bureau"]),
        "TOTAL_BUREAU_REQ": app["bureau_req"],
        "MONTH_EMPLOYED": app["months_employed"],
        "AGE_YEARS": app["age"],
    }
    return add_ratios(row)


def refusal_probability(rows: list[dict]) -> np.ndarray:
    approval, inputs, *_ = load_models()
    X = pd.DataFrame(rows)[inputs]
    return approval.predict_proba(X)[:, 1]


def highest_approvable(row: dict, steps: int = 80) -> float | None:
    """Largest amount at or below the request that the model would approve.

    Every amount from the request down to $10,000 (geometric steps) is scored with the
    amount-based features recalculated; the largest approved one is returned.
    """
    requested = row["AMT_APPLICATION"]
    if requested <= MIN_AMOUNT:
        return None
    amounts = np.unique(np.geomspace(MIN_AMOUNT, requested, steps).round(-3))
    amounts = amounts[amounts > row["AMT_DOWN_PAYMENT"]]  # down payment must stay below the amount
    if len(amounts) == 0:
        return None
    rows = [add_ratios({**row, "AMT_APPLICATION": float(a)}) for a in amounts]
    probs = refusal_probability(rows)
    ok = amounts[probs < THRESHOLD]
    return float(ok.max()) if len(ok) else None


def predict_segment(row: dict) -> tuple[int, str]:
    *_, segment, segment_inputs, segment_names = load_models()
    seg_row = {**row, "INCOME_PER_PERSON": row["AMT_INCOME_TOTAL"] / row["CNT_FAM_MEMBERS"]}
    label = int(segment.predict(pd.DataFrame([seg_row])[segment_inputs])[0])
    return label, segment_names[label]


def assess(app: dict) -> dict:
    """Full result for the Client Form."""
    row = build_row(app)
    p = float(refusal_probability([row])[0])
    refused = p >= THRESHOLD
    seg_id, seg_name = predict_segment(row)
    return {
        "row": row,
        "refusal_probability": p,
        "decision": "Refused" if refused else "Approved",
        "max_amount": highest_approvable(row) if refused else row["AMT_APPLICATION"],
        "segment_id": seg_id,
        "segment": seg_name,
    }


# ---- Why the model decided ----------------------------------------------------------------
# Raw model columns grouped into reasons a loan officer can read.
REASON_GROUPS = {
    "Loan type": ["NAME_CONTRACT_TYPE"],
    "Client type": ["NAME_CLIENT_TYPE"],
    "Loan size": ["AMT_APPLICATION", "LOAN_TO_INCOME", "PAYMENT_TO_INCOME"],
    "Loan term": ["CNT_PAYMENT"],
    "Down payment": ["AMT_DOWN_PAYMENT", "DOWN_PAYMENT_RATIO"],
    "Yearly income": ["AMT_INCOME_TOTAL"],
    "Credit score 1": ["EXT_SOURCE_1"],
    "Credit score 2": ["EXT_SOURCE_2"],
    "Credit score 3": ["EXT_SOURCE_3"],
    "Credit bureau": ["HAS_BUREAU_RECORD", "TOTAL_BUREAU_REQ"],
    "Age": ["AGE_YEARS"],
    "Gender": ["CODE_GENDER"],
    "Marital status": ["NAME_FAMILY_STATUS"],
    "Family size": ["CNT_CHILDREN", "CNT_FAM_MEMBERS"],
    "Education": ["NAME_EDUCATION_TYPE"],
    "Income type": ["NAME_INCOME_TYPE", "FLAG_EMP_PHONE"],
    "Occupation": ["OCCUPATION_TYPE"],
    "Employer type": ["ORGANIZATION_TYPE"],
    "Time with employer": ["MONTH_EMPLOYED"],
    "Car": ["FLAG_OWN_CAR", "OWN_CAR_AGE"],
    "Property": ["FLAG_OWN_REALTY"],
    "Housing": ["NAME_HOUSING_TYPE"],
    "Region rating": ["REGION_RATING_CLIENT_W_CITY"],
    "Works in another region": ["LIVE_REGION_NOT_WORK_REGION"],
    "Documents": ["FLAG_DOCUMENT_3", "FLAG_DOCUMENT_5", "FLAG_DOCUMENT_6", "FLAG_DOCUMENT_8", "OTHER_DOCUMENTS"],
}
# REGION_POPULATION_RELATIVE is filled with the training median, so it is never a reason.


@st.cache_resource(show_spinner=False)
def _column_owners() -> list[str]:
    """Original input column behind every column the preprocessing step outputs."""
    approval, *_ = load_models()
    pre = approval.named_steps["Preprocessing"]
    owners = []
    for name, _tr, cols in pre.transformers_:
        if name == "drop" or not len(cols):
            continue
        outputs = [n.split("__", 1)[1] for n in pre.get_feature_names_out() if n.startswith(f"{name}__")]
        for out in outputs:
            if name == "Binary Pipeline":          # BinaryEncoder names columns 0_0, 0_1 … 1_5
                owners.append(cols[int(out.split("_")[0])])
            else:                                  # one-to-one, or OHE "COLUMN_value"
                owners.append(max((c for c in cols if out == c or out.startswith(f"{c}_")), key=len))
    return owners


def explain(row: dict, top: int = 3) -> list[dict]:
    """Top reasons behind this client's refusal probability (XGBoost feature contributions).

    Each contribution is in log-odds: positive pushes towards refusal, negative towards approval.
    """
    import xgboost as xgb

    approval, inputs, *_ = load_models()
    Xt = approval.named_steps["Preprocessing"].transform(pd.DataFrame([row])[inputs])
    booster = approval.steps[-1][1].get_booster()
    contribs = booster.predict(xgb.DMatrix(np.asarray(Xt, dtype=float), feature_names=booster.feature_names),
                               pred_contribs=True)[0][:-1]          # last value is the bias
    by_column = pd.Series(contribs, index=_column_owners()).groupby(level=0).sum()
    reasons = [{"reason": label, "effect": float(by_column.reindex(cols).fillna(0).sum())}
               for label, cols in REASON_GROUPS.items()]
    reasons.sort(key=lambda r: abs(r["effect"]), reverse=True)
    return reasons[:top]
