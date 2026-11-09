import streamlit as st

from core.data import portfolio_kpis
from core.theme import number, page_background, pct

page_background("assets/hero_web.jpg")

k = portfolio_kpis()

# ---- Hero ---------------------------------------------------------------
left, right = st.columns([1.15, 1], gap="large", vertical_alignment="center")

with left:
    st.html(
        """
        <div class="ll-hero">
          <h1>See the whole loan decision.</h1>
          <p>LoanLens predicts whether an application will be approved, estimates the highest
          amount the client could get, and places the client in a customer segment, so the
          loan officer decides with the full picture.</p>
        </div>
        """
    )
    st.write("")
    if st.button("Start a new application", type="primary", icon=":material/add:"):
        st.switch_page("views/new_application.py")

with right:
    st.html(
        f"""
        <div class="ll-panel">
          <div class="ll-label">Clients in the portfolio</div>
          <div class="ll-big">{number(k['clients'])}</div>
          <div class="ll-note" style="margin-top:0.4rem">
            {number(k['with_application'])} with a past loan application,
            {number(k['no_application'])} without one.
          </div>

          <div class="ll-split" role="img"
               aria-label="Approved {pct(k['approved_pct'])}, refused {pct(k['refused_pct'])}">
            <div class="a" style="width:{k['approved_pct']:.2f}%"></div>
            <div class="r" style="width:{k['refused_pct']:.2f}%"></div>
          </div>

          <div class="ll-legend">
            <div>
              <div class="ll-label"><span class="dot" style="background:var(--teal)"></span>Approved</div>
              <div class="ll-mid">{number(k['approved'])}</div>
              <div class="ll-note">{pct(k['approved_pct'])} of applications</div>
            </div>
            <div>
              <div class="ll-label"><span class="dot" style="background:var(--coral)"></span>Refused</div>
              <div class="ll-mid">{number(k['refused'])}</div>
              <div class="ll-note">{pct(k['refused_pct'])} of applications</div>
            </div>
          </div>
        </div>
        """
    )

# ---- How it works (a real sequence) ---------------------------------------
st.html('<div class="ll-section-title">How an application is checked</div>')
st.html(
    """
    <div class="ll-steps">
      <div class="ll-step"><div class="n">1</div>
        <h4>Enter the client's details</h4>
        <p>Personal, work, assets, credit check and the loan request, with fields that adapt
        to each answer.</p></div>
      <div class="ll-step"><div class="n">2</div>
        <h4>Get the decision support</h4>
        <p>Approval prediction with the refusal probability, and the highest amount the
        client could be approved for.</p></div>
      <div class="ll-step"><div class="n">3</div>
        <h4>Review and print the client form</h4>
        <p>The client's segment, all details and the result in one form, ready to download
        as a PDF.</p></div>
    </div>
    """
)

st.write("")
st.caption("Data: [Home Credit Default Risk](https://www.kaggle.com/competitions/home-credit-default-risk) on Kaggle: "
           "clients and their latest previous loan application. "
           "Approval model: XGBoost (F1 47%, Precision 34%, Recall 75%). "
           "Results support the loan officer; the final decision is always made by a person.")
