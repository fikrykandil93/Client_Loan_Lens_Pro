import pandas as pd
import streamlit as st

from core.data import client_segments, load_clients
from core.model_card import SEGMENT_ORDER
from core.theme import number, page_head

page_head("Clients",
          "Find a client in the bank's records, browse a range of client IDs, and open one in a new application.",
          banner="assets/banner_clients_web.jpg")

MAX_ROWS = 1_000
FIRST_ID, LAST_ID = 100_001, 456_255


@st.cache_data(show_spinner=False)
def directory() -> pd.DataFrame:
    """One row per client with the columns the officer needs to recognise them."""
    df = load_clients()
    out = pd.DataFrame({
        "Client ID": df.index,
        "Gender": df["CODE_GENDER"].map({"F": "Female", "M": "Male"}).values,
        "Age": df["AGE_YEARS"].values,
        "Yearly income": df["AMT_INCOME_TOTAL"].values,
        "Segment": client_segments().values,
        "Last loan type": df["NAME_CONTRACT_TYPE"].fillna("–").values,
        "Last amount": df["AMT_APPLICATION"].values,
        "Bank decision": df["NAME_CONTRACT_STATUS"].fillna("No application").values,
    })
    return out


def reset_filters() -> None:
    """Callback: every filter back to its starting value (set, not deleted, so the widgets update)."""
    st.session_state.update(c_from=FIRST_ID, c_to=FIRST_ID + 199, c_one="", c_decision=[], c_segment=[])
    st.session_state.pop("c_table", None)


data = directory()

# ---- Filters -------------------------------------------------------------------------------
with st.container(border=True):
    a, b, c = st.columns([1, 1, 1.2])
    id_from = a.number_input("From client ID", min_value=FIRST_ID, max_value=LAST_ID, value=FIRST_ID, step=1,
                             key="c_from")
    id_to = b.number_input("To client ID", min_value=FIRST_ID, max_value=LAST_ID, value=FIRST_ID + 199, step=1,
                           key="c_to")
    one = c.text_input("Or find one client", placeholder="Client ID, for example 100002", key="c_one").strip()
    a, b = st.columns([1, 1.6])
    decision = a.pills("Bank decision", ["Approved", "Refused", "No application"],
                       selection_mode="multi", key="c_decision")
    segments = b.pills("Segment", SEGMENT_ORDER, selection_mode="multi", key="c_segment")
    st.button("Reset filters", icon=":material/restart_alt:", type="tertiary", on_click=reset_filters)

if one:
    if not one.isdigit():
        st.html('<div class="ll-empty">A client ID is a number, for example 100002.</div>')
        st.stop()
    view = data[data["Client ID"] == int(one)]
    scope = f"Client {one}"
else:
    lo, hi = min(id_from, id_to), max(id_from, id_to)
    view = data[data["Client ID"].between(lo, hi)]
    scope = f"Client IDs {lo} to {hi}"
if decision:
    view = view[view["Bank decision"].isin(decision)]
if segments:
    view = view[view["Segment"].isin(segments)]

total = len(view)
shown = view.head(MAX_ROWS)
note = f" Showing the first {number(MAX_ROWS)}; narrow the range to see the rest." if total > MAX_ROWS else ""
st.html(f'<div class="ll-filter-summary"><b>{number(total)}</b> clients · {scope}.{note}</div>')

if total == 0:
    st.html('<div class="ll-empty">No client matches these filters. IDs run from '
            f'{FIRST_ID} to {LAST_ID}, and not every number is used.</div>')
    st.stop()

# ---- Table + open -----------------------------------------------------------------------------
event = st.dataframe(
    shown, hide_index=True, width="stretch", height=min(38 + 35 * len(shown), 460),
    on_select="rerun", selection_mode="single-row", key="c_table",
    column_config={
        "Client ID": st.column_config.NumberColumn(format="%d"),
        "Yearly income": st.column_config.NumberColumn(format="$%,.0f"),
        "Last amount": st.column_config.NumberColumn(format="$%,.0f"),
    },
)
rows = event.selection.rows
picked = int(shown.iloc[rows[0]]["Client ID"]) if rows else (int(view.iloc[0]["Client ID"]) if total == 1 else None)

a, b = st.columns([1, 2.4], vertical_alignment="center")
if a.button("Open in New Application", type="primary", icon=":material/edit_document:", disabled=picked is None,
            width="stretch"):
    st.session_state["open_client"] = picked
    st.switch_page("views/new_application.py")
b.caption(f"Client {picked} selected." if picked else "Select a client in the table (click the box at the start "
          "of a row) to open it.")
