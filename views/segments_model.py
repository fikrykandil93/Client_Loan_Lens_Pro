import plotly.graph_objects as go
import streamlit as st

from core.charts import show, style
from core.data import feature_importance, load_clients, segment_summary
from core.model_card import ALGORITHMS, FINAL_MODEL, SEGMENT_ORDER, SEGMENT_TEXT, SILHOUETTE
from core.model_service import THRESHOLD
from core.theme import CORAL, INK, money, number, page_head, pct

page_head("Customer segments and the models",
          "Who the bank's clients are, and how the approval model makes its recommendation.",
          banner="assets/banner_segments_web.jpg")

CARD_HEIGHT = 440


def card(title: str, finding: str):
    box = st.container(border=True, height=CARD_HEIGHT)
    box.html(f'<div class="ll-chart-title">{title}</div><div class="ll-finding">{finding}</div>')
    return box


def hbar(labels, values, text, highlight=None) -> go.Figure:
    """Horizontal bars, largest on top; the highlighted bar is coral."""
    colors = [CORAL if lab == highlight else INK for lab in labels]
    fig = go.Figure(go.Bar(x=values, y=labels, orientation="h", marker_color=colors, marker_cornerradius=6,
                           text=text, textposition="outside", cliponaxis=False,
                           hovertemplate="%{y}: %{text}<extra></extra>"))
    fig = style(fig)
    fig.update_yaxes(autorange="reversed", gridcolor="rgba(0,0,0,0)", tickfont=dict(color=INK))
    fig.update_xaxes(showticklabels=False, range=[0, max(values) * 1.25])
    fig.update_layout(margin=dict(l=8, r=8, t=10, b=8), bargap=0.4)
    return fig


segments_tab, model_tab = st.tabs(["Customer segments", "Approval model"])

# =========================================================================================
with segments_tab:
    seg = segment_summary().loc[SEGMENT_ORDER]
    st.html(f'<p class="ll-note" style="margin:.4rem 0 1rem">{number(len(load_clients()))} clients grouped into '
            'five segments by KMeans on income per person, age, region rating, credit score 2, car and education.</p>')

    tier_class = {"Prime": "prime", "Near-Prime": "near", "Subprime": "sub"}
    cards = ""
    for name, r in seg.iterrows():
        tier, short = name.split(" – ")
        cards += f"""
        <div class="ll-segcard">
          <span class="ll-tier {tier_class[tier]}">{tier}</span>
          <div class="ll-segcard-name">{short}</div>
          <div class="ll-segcard-share"><b>{pct(r['Share'], 0)}</b> of clients · {number(r['Clients'])}</div>
          <p>{SEGMENT_TEXT[name]}</p>
          <div class="r"><span>Income / person</span><b>{money(r['Income_Person'])}</b></div>
          <div class="r"><span>Average age</span><b>{r['Age']:.0f}</b></div>
          <div class="r"><span>Credit score 2</span><b>{r['Credit_Score']:.2f}</b></div>
          <div class="r"><span>Refusal rate</span><b>{pct(r['Refusal_Rate'])}</b></div>
        </div>"""
    st.html(f'<div class="ll-segcards">{cards}</div>')

    c1, c2 = st.columns([1.5, 1], gap="medium")
    metrics = {   # pill label → (column, value format, chart title)
        "Income": ("Income_Person", money, "Income per person"),
        "Age": ("Age", lambda v: f"{v:.0f}", "Average age"),
        "Credit score": ("Credit_Score", lambda v: f"{v:.2f}", "Credit score 2"),
        "Car": ("Has_Car", lambda v: pct(v, 0), "Clients who own a car"),
        "Education": ("Higher_Edu", lambda v: pct(v, 0), "Clients with higher education"),
        "Refusals": ("Refusal_Rate", pct, "Refusal rate"),
    }
    with c1:
        choice = st.segmented_control("Compare segments by", list(metrics), default="Income",
                                      key="seg_metric", label_visibility="collapsed") or "Income"
        col, fmt, title = metrics[choice]
        values = seg[col]
        top = values.idxmax()
        with card(f"{title} by segment", f"Highest: {top} with {fmt(values[top])}; lowest: "
                                          f"{values.idxmin()} with {fmt(values.min())}."):
            show(hbar(list(values.index), list(values), [fmt(v) for v in values], highlight=top))
    with c2:
        low, high = seg["Refusal_Rate"].min(), seg["Refusal_Rate"].max()
        st.html(f"""
        <div class="ll-panel ll-read">
          <div class="ll-chart-title">What the segments tell us</div>
          <ul>
            <li><b>Credit quality splits the portfolio.</b> Credit score 2 runs from
              {seg['Credit_Score'].min():.2f} (Subprime – Young) to {seg['Credit_Score'].max():.2f} (Prime – Mass Affluent).</li>
            <li><b>Refusals barely change by segment</b> ({pct(low)} to {pct(high)}). What the client asks for
              (loan type, client type) matters more than who the client is.</li>
            <li><b>Use segments to describe, not to decide.</b> Clients form a continuum rather than separate
              groups (silhouette {SILHOUETTE}), so a segment is a profile for the officer, not a verdict.</li>
          </ul>
        </div>""")

# =========================================================================================
with model_tab:
    st.html(f"""
    <div class="ll-strip" style="margin-top:.4rem">
      <div><div class="ll-label">Algorithm</div><div class="ll-mid">{FINAL_MODEL['name']}</div></div>
      <div><div class="ll-label">F1 score</div><div class="ll-mid">{pct(FINAL_MODEL['F1'])}</div></div>
      <div><div class="ll-label">Precision</div><div class="ll-mid">{pct(FINAL_MODEL['Precision'])}</div></div>
      <div><div class="ll-label">Recall</div><div class="ll-mid">{pct(FINAL_MODEL['Recall'])}</div></div>
      <div><div class="ll-label">Decision limit</div><div class="ll-mid">{pct(THRESHOLD * 100, 0)}</div></div>
    </div>""")
    st.caption("Scores from 5-fold cross-validation after tuning. Accuracy is not shown: with only 15.4% of "
               "applications refused, predicting “Approved” for everyone already scores 85%.")

    c1, c2 = st.columns(2, gap="medium")
    with c1:
        metric = st.segmented_control("Compare algorithms by", ["F1", "Precision", "Recall"], default="F1",
                                      key="algo_metric", label_visibility="collapsed") or "F1"
        algos = sorted(ALGORITHMS, key=lambda a: ALGORITHMS[a][metric], reverse=True)
        vals = [ALGORITHMS[a][metric] for a in algos]
        findings = {
            "F1": "XGBoost gives the best balance between catching refusals and avoiding false alarms.",
            "Precision": "Random Forest is the most precise, but it misses more than half of the refusals.",
            "Recall": "Naive Bayes catches the most refusals, but most of its alarms are false.",
        }
        with card(f"{metric} by algorithm (before tuning)", findings[metric]):
            show(hbar(algos, vals, [pct(v) for v in vals], highlight="XGBoost"))
    with c2:
        st.html('<div style="height:2.55rem"></div>')  # lines the card up with the left one
        imp = feature_importance()
        with card("What drives the model",
                  f"Loan type alone carries {pct(imp.iloc[0], 0)} of the model's importance, client type "
                  f"{pct(imp.iloc[1], 0)}."):
            show(hbar(list(imp.index), list(imp), [pct(v) for v in imp], highlight=imp.index[0]))

    st.html(f"""
    <div class="ll-section-title">How to read the result</div>
    <div class="ll-steps ll-steps-plain">
      <div class="ll-step"><h4>Refused at {pct(THRESHOLD * 100, 0)} or more</h4>
        <p>The model gives every application a refusal probability. At {pct(THRESHOLD * 100, 0)} or above
        the recommendation is Refused.</p></div>
      <div class="ll-step"><h4>Recall {pct(FINAL_MODEL['Recall'], 0)}</h4>
        <p>It flags about 3 of every 4 applications the bank refused, so few risky requests pass unseen.</p></div>
      <div class="ll-step"><h4>Precision {pct(FINAL_MODEL['Precision'], 0)}</h4>
        <p>About 1 in 3 flagged applications was really refused. That is why the loan officer reviews
        every flag and makes the final decision.</p></div>
    </div>

    <div class="ll-section-title">How it was built</div>
    <div class="ll-steps ll-steps-4">
      <div class="ll-step"><div class="n">1</div><h4>Data</h4>
        <p>{number(len(load_clients()))} clients and 38 columns, joined from the application, previous
        application and credit bureau tables.</p></div>
      <div class="ll-step"><div class="n">2</div><h4>Features</h4>
        <p>Three new ratios: loan to income, down payment ratio and payment to income. Columns known only
        after the decision were removed to avoid leakage.</p></div>
      <div class="ll-step"><div class="n">3</div><h4>Approval model</h4>
        <p>Five algorithms with class weights for the imbalance, then GridSearchCV on Logistic Regression
        and XGBoost, chosen by F1.</p></div>
      <div class="ll-step"><div class="n">4</div><h4>Segments</h4>
        <p>KMeans on six client features, scaled in one pipeline; k = 5 picked with the elbow method
        and silhouette score.</p></div>
    </div>
    """)
