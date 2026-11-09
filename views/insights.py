import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from core.charts import STATUS_COLORS, rate_bar, show, style
from core.data import load_applications, refusal_rate
from core.theme import CORAL, INK, money, number, page_head, pct

apps = load_applications()

LOAN_TYPES = ["All loans", "Cash loans", "Consumer loans", "Revolving loans"]
CLIENT_TYPES = ["All clients", "New", "Refreshed", "Repeater"]
AGE_RANGE = (int(apps["AGE_YEARS"].min()), int(apps["AGE_YEARS"].max()))
INCOME_RANGE = (25, 900)          # thousands of dollars; the top value means "900K and above"
MIN_RELIABLE = 500                # below this, rates are shown with a warning

DEFAULTS = {"f_loan": "All loans", "f_client": "All clients", "f_age": AGE_RANGE, "f_income": INCOME_RANGE}
for key, value in DEFAULTS.items():
    st.session_state.setdefault(key, value)


def reset_filters() -> None:
    for key, value in DEFAULTS.items():
        st.session_state[key] = value


# ---- Header ----------------------------------------------------------------
page_head("Refusals depend on the request more than on the client.",
          "What drives refusals across 329,163 past applications. Use the filters to see how "
          "each factor changes.",
          banner="assets/banner_insights_web.jpg")

# ---- Filters -----------------------------------------------------------------
f1, f2 = st.columns([1.2, 1], gap="large", vertical_alignment="bottom")
with f1:
    st.segmented_control("Loan type", LOAN_TYPES, key="f_loan")
with f2:
    st.segmented_control("Client type", CLIENT_TYPES, key="f_client")

f3, f4 = st.columns([1.2, 1], gap="large", vertical_alignment="bottom")
with f3:
    st.slider("Age", *AGE_RANGE, key="f_age")
with f4:
    st.slider("Income", *INCOME_RANGE, step=5, key="f_income", format="$%dK",
              help="The top of the range includes every income above $900K.")

loan_type = st.session_state.f_loan or "All loans"
client_type = st.session_state.f_client or "All clients"
age_lo, age_hi = st.session_state.f_age
inc_lo, inc_hi = st.session_state.f_income

df = apps
if loan_type != "All loans":
    df = df[df["NAME_CONTRACT_TYPE"] == loan_type]
if client_type != "All clients":
    df = df[df["NAME_CLIENT_TYPE"] == client_type]
df = df[df["AGE_YEARS"].between(age_lo, age_hi)]
income_k = df["AMT_INCOME_TOTAL"] / 1000
df = df[(income_k >= inc_lo) & ((income_k <= inc_hi) | (inc_hi == INCOME_RANGE[1]))]

# Summary of the active filters
parts = [p for p in (loan_type if loan_type != "All loans" else None,
                     f"{client_type} clients" if client_type != "All clients" else None) if p]
if (age_lo, age_hi) != AGE_RANGE:
    parts.append(f"Age {age_lo}–{age_hi}")
if (inc_lo, inc_hi) != INCOME_RANGE:
    top = f"${inc_hi}K" + ("+" if inc_hi == INCOME_RANGE[1] else "")
    parts.append(f"Income ${inc_lo}K–{top}")
summary = ", ".join(parts) if parts else "All applications"

s1, s2 = st.columns([1, 0.25], vertical_alignment="center")
s1.html(f'<div class="ll-filter-summary">{summary}</div>')
s2.button("Reset filters", icon=":material/restart_alt:", on_click=reset_filters, type="tertiary",
          disabled=not parts, width="stretch")

if df.empty:
    st.info("No applications match these filters. Widen the age or income range, or reset the filters.",
            icon=":material/filter_alt_off:")
    st.stop()

if len(df) < MIN_RELIABLE:
    st.warning(f"Only {number(len(df))} applications match these filters, so the rates below may not be "
               "reliable.", icon=":material/warning:")

# ---- Metric strip ---------------------------------------------------------
refused = df["REFUSED"].mean() * 100
med_app = df.loc[df["REFUSED"] == 0, "AMT_APPLICATION"].median()
med_ref = df.loc[df["REFUSED"] == 1, "AMT_APPLICATION"].median()


def fmt_money(v):
    return money(v) if pd.notna(v) else "–"


if client_type == "All clients":
    last_label = "New clients refused"
    v = df.loc[df["NAME_CLIENT_TYPE"] == "New", "REFUSED"].mean() * 100
    last_value = pct(v) if pd.notna(v) else "–"
else:
    last_label = "Median income"
    last_value = fmt_money(df["AMT_INCOME_TOTAL"].median())

st.html(
    f"""
    <div class="ll-strip">
      <div><div class="ll-label">Applications</div><div class="ll-mid">{number(len(df))}</div></div>
      <div><div class="ll-label">Refusal rate</div><div class="ll-mid">{pct(refused)}</div></div>
      <div><div class="ll-label">Median approved</div><div class="ll-mid">{fmt_money(med_app)}</div></div>
      <div><div class="ll-label">Median refused</div><div class="ll-mid" style="color:var(--coral)">{fmt_money(med_ref)}</div></div>
      <div><div class="ll-label">{last_label}</div><div class="ll-mid">{last_value}</div></div>
    </div>
    """
)

# ---- Card helpers ------------------------------------------------------------
CARD_HEIGHT = 440  # equal card height: title + two-line finding + chart


def card(title: str, finding: str):
    box = st.container(border=True, height=CARD_HEIGHT)
    box.html(f'<div class="ll-chart-title">{title}</div><div class="ll-finding">{finding}</div>')
    return box


def empty_card(title: str, message: str) -> None:
    with card(title, message):
        st.html('<div class="ll-empty">Not enough applications in this selection to draw the chart.</div>')


def quantile_groups(data: pd.DataFrame, col: str, label: str) -> pd.DataFrame:
    """Refusal rate by five equal-size groups of a money column."""
    q = data.assign(GROUP=pd.qcut(data[col], 5, duplicates="drop"))
    q["GROUP"] = q["GROUP"].map(lambda i: f"${i.left / 1000:,.0f}K–${i.right / 1000:,.0f}K")
    return refusal_rate(q, "GROUP").rename(columns={"GROUP": label})


# ---- The application ------------------------------------------------------
st.html('<div class="ll-section-title">The application</div>')
c1, c2 = st.columns(2, gap="medium")

with c1:
    # Always shows every loan type, so the selected one is seen in context
    ct = refusal_rate(apps, "NAME_CONTRACT_TYPE").sort_values("Refusal_Rate")
    cons = ct.loc[ct.NAME_CONTRACT_TYPE == "Consumer loans", "Refusal_Rate"].iloc[0]
    cash = ct.loc[ct.NAME_CONTRACT_TYPE == "Cash loans", "Refusal_Rate"].iloc[0]
    fig = rate_bar(ct, "NAME_CONTRACT_TYPE")
    if loan_type != "All loans":
        fig.data[0].marker.color = [CORAL if t == loan_type else "#C9D3DA" for t in ct.NAME_CONTRACT_TYPE]
    with card("Refusal rate by loan type (all applications)",
              f"Consumer loans are secured by the goods: {pct(cons)} refused vs {pct(cash)} for cash loans."):
        show(style(fig))

with c2:
    cl = refusal_rate(df, "NAME_CLIENT_TYPE").sort_values("Refusal_Rate")
    if client_type == "All clients" and len(cl) > 1:
        new = cl.loc[cl.NAME_CLIENT_TYPE == "New", "Refusal_Rate"]
        rep = cl.loc[cl.NAME_CLIENT_TYPE == "Repeater", "Refusal_Rate"]
        with card("Refusal rate by client type",
                  f"New clients are refused {pct(new.iloc[0]) if len(new) else '–'}, repeat clients "
                  f"{pct(rep.iloc[0]) if len(rep) else '–'}."):
            show(style(rate_bar(cl, "NAME_CLIENT_TYPE")))
    else:
        # One client type selected: compare requested amounts instead
        aq = quantile_groups(df, "AMT_APPLICATION", "Amount")
        if len(aq) > 1:
            with card("Refusal rate by requested amount",
                      f"Refusal ranges from {pct(aq['Refusal_Rate'].min())} to "
                      f"{pct(aq['Refusal_Rate'].max())} across amount groups."):
                show(style(rate_bar(aq, "Amount")))
        else:
            empty_card("Refusal rate by requested amount", "Too few applications to split by amount.")

c3, c4 = st.columns(2, gap="medium")

with c3:
    sample = df.sample(min(len(df), 6000), random_state=42)  # keeps the page light
    fig = go.Figure()
    for status in ["Approved", "Refused"]:
        s = sample[sample["NAME_CONTRACT_STATUS"] == status]
        fig.add_trace(go.Box(y=s["AMT_APPLICATION"], name=status, marker_color=STATUS_COLORS[status],
                             boxpoints=False, line_width=2, fillcolor="rgba(0,0,0,0)"))
    fig.update_yaxes(type="log", tickvals=[1e4, 3e4, 1e5, 3e5, 1e6, 3e6],
                     ticktext=["$10K", "$30K", "$100K", "$300K", "$1M", "$3M"])
    with card("Requested amount (log scale)",
              f"Median requested: {fmt_money(med_ref)} for refused vs {fmt_money(med_app)} for approved."):
        show(style(fig))

with c4:
    tg = refusal_rate(df, "TERM_GROUP", min_apps=200)
    tg = tg[tg["TERM_GROUP"] != "No term"]  # revolving loans have no fixed term
    if len(tg) > 1:
        fig = go.Figure(go.Scatter(x=tg["TERM_GROUP"].astype(str), y=tg["Refusal_Rate"], mode="lines+markers+text",
                                   text=[f"{v:.1f}%" for v in tg["Refusal_Rate"]], textposition="top center",
                                   cliponaxis=False, line=dict(color=INK, width=3), marker=dict(size=9),
                                   hovertemplate="%{x} months<br>%{y:.1f}% refused<extra></extra>"))
        fig.update_yaxes(ticksuffix="%", range=[0, tg["Refusal_Rate"].max() * 1.2])
        fig.update_xaxes(range=[-0.4, len(tg) - 0.6])
        with card("Refusal rate by loan term (months)",
                  f"Longer loans are refused more: {pct(tg['Refusal_Rate'].iloc[0])} for "
                  f"{tg['TERM_GROUP'].iloc[0]} months vs {pct(tg['Refusal_Rate'].iloc[-1])} for "
                  f"{tg['TERM_GROUP'].iloc[-1]}."):
            show(style(fig))
    else:
        bq = df.assign(BUREAU=pd.cut(df["TOTAL_BUREAU_REQ"], [-1, 0, 1, 2, 5, 1000],
                                     labels=["0", "1", "2", "3–5", "6+"]))
        bq = refusal_rate(bq, "BUREAU", min_apps=50)
        if len(bq) > 1:
            with card("Refusal rate by credit bureau inquiries",
                      "No fixed loan term in this selection, so inquiries to the credit bureau are shown."):
                show(style(rate_bar(bq, "BUREAU")))
        else:
            empty_card("Refusal rate by loan term", "No fixed loan term in this selection.")

# ---- The client ------------------------------------------------------------
st.html('<div class="ll-section-title">The client</div>')
c5, c6 = st.columns(2, gap="medium")

with c5:
    ag = refusal_rate(df, "AGE_GROUP", min_apps=200)
    if len(ag) > 2:
        fig = go.Figure(go.Scatter(x=ag["AGE_GROUP"], y=ag["Refusal_Rate"], mode="lines+markers",
                                   line=dict(color=INK, width=3), marker=dict(size=8),
                                   hovertemplate="Age %{x}<br>%{y:.1f}% refused<extra></extra>"))
        fig.update_yaxes(ticksuffix="%")
        lo, hi = ag["Refusal_Rate"].min(), ag["Refusal_Rate"].max()
        with card("Refusal rate by age", f"Between {pct(lo)} and {pct(hi)} across age groups."):
            show(style(fig))
    else:
        # Narrow age range: compare income levels instead
        iq = quantile_groups(df, "AMT_INCOME_TOTAL", "Income")
        if len(iq) > 1:
            with card("Refusal rate by income",
                      f"The age range is narrow, so income groups are shown: "
                      f"{pct(iq['Refusal_Rate'].min())} to {pct(iq['Refusal_Rate'].max())}."):
                show(style(rate_bar(iq, "Income")))
        else:
            empty_card("Refusal rate by age", "The age range is too narrow to compare groups.")

with c6:
    s = df.sample(min(len(df), 6000), random_state=7)
    m = df.groupby("NAME_CONTRACT_STATUS")["EXT_SOURCE_3"].mean()
    if s["EXT_SOURCE_3"].notna().sum() > 50 and len(m) == 2:
        fig = go.Figure()
        for status in ["Approved", "Refused"]:
            fig.add_trace(go.Histogram(x=s.loc[s["NAME_CONTRACT_STATUS"] == status, "EXT_SOURCE_3"], name=status,
                                       histnorm="percent", nbinsx=30, marker_color=STATUS_COLORS[status],
                                       opacity=0.6))
        fig.update_layout(barmode="overlay")
        fig.update_yaxes(ticksuffix="%")
        with card("Credit score distribution (EXT_SOURCE_3)",
                  f"Average score: {m['Refused']:.2f} for refused vs {m['Approved']:.2f} for approved."):
            show(style(fig, legend=True))
    else:
        empty_card("Credit score distribution (EXT_SOURCE_3)", "Too few scored applications in this selection.")

c7, c8 = st.columns(2, gap="medium")
with c7:
    short = {"Lower secondary": "Lower sec.", "Secondary / secondary special": "Secondary",
             "Incomplete higher": "Incomplete higher", "Higher education": "Higher",
             "Academic degree": "Academic"}
    ed = refusal_rate(df, "NAME_EDUCATION_TYPE", min_apps=200)
    if len(ed) > 1:
        ed["order"] = ed["NAME_EDUCATION_TYPE"].map(list(short).index)
        ed = ed.sort_values("order")
        ed["NAME_EDUCATION_TYPE"] = ed["NAME_EDUCATION_TYPE"].map(short)
        with card("Refusal rate by education",
                  f"Between {pct(ed['Refusal_Rate'].min())} and {pct(ed['Refusal_Rate'].max())} "
                  "across education levels."):
            show(style(rate_bar(ed, "NAME_EDUCATION_TYPE")))
    else:
        empty_card("Refusal rate by education", "Too few applications to compare education levels.")
with c8:
    it = refusal_rate(df, "NAME_INCOME_TYPE", min_apps=200).sort_values("Refusal_Rate")
    if len(it) > 1:
        with card("Refusal rate by income type",
                  f"Between {pct(it['Refusal_Rate'].min())} and {pct(it['Refusal_Rate'].max())} "
                  "across income types."):
            show(style(rate_bar(it, "NAME_INCOME_TYPE")))
    else:
        empty_card("Refusal rate by income type", "Too few applications to compare income types.")

st.caption("Box plots and histograms use a random sample of up to 6,000 applications; all rates and "
           "medians use every application in the selection. The loan-type chart always shows all "
           "applications. Groups with too few applications are hidden.")
