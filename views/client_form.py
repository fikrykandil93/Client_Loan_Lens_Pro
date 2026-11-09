import hashlib
from datetime import date

import streamlit as st

from core.model_card import SEGMENT_TEXT
from core.model_service import THRESHOLD, assess, explain, load_segment_profile
from core.report import build_pdf, detail_groups, reason_value
from core.theme import money, pct


app = st.session_state.get("application")

# ---- Empty state ------------------------------------------------------------
if not app:
    st.html('<div class="ll-page-head"><h1>Credit Approval Form</h1>'
            '<p>The form appears after an application is checked.</p></div>')
    if st.button("Start a new application", type="primary", icon=":material/add:"):
        st.switch_page("views/new_application.py")
    st.stop()

# ---- Result (computed once per submitted application) -----------------------
if "assessment" not in st.session_state:
    res = assess(app)
    seed = f"{app['national_id']}{app['amount']}{app['contract_type']}".encode()
    res["reference"] = f"LL-{date.today():%Y%m%d}-{int(hashlib.sha1(seed).hexdigest(), 16) % 10000:04d}"
    res["date"] = date.today()
    st.session_state["assessment"] = res
res = st.session_state["assessment"]
if "reasons" not in res:
    res["reasons"] = explain(res["row"])

refused = res["decision"] == "Refused"
p = res["refusal_probability"]
nid = app["national_id"]
id_parts = []
if app.get("client_id"):
    id_parts.append(f"Client ID {app['client_id']}")
if nid:
    id_parts.append(f"National ID {nid[:7]}•••••{nid[-2:]}")
id_line = " · ".join(id_parts)

# ---- Header -------------------------------------------------------------------
st.html(
    f"""
    <div class="ll-doc-head">
      <div>
        <div class="ll-form-title">Credit Approval Form</div>
        <h1>{app['name']}</h1>
        <div class="ll-note">{id_line} · Age {app['age']}</div>
      </div>
      <div class="ll-doc-meta">
        <div><span>Reference</span><b>{res['reference']}</b></div>
        <div><span>Date</span><b>{res['date']:%d/%m/%Y}</b></div>
      </div>
    </div>
    """
)

# ---- Decision card (the one bold element of the page) --------------------------
state = "refused" if refused else "approved"
icon = "✕" if refused else "✓"
st.html(
    f"""
    <div class="ll-decision {state}">
      <div class="ll-decision-main">
        <span class="ll-decision-icon" aria-hidden="true">{icon}</span>
        <div>
          <div class="ll-decision-word">{res['decision']}</div>
          <div class="ll-decision-sub">Model recommendation for a {app['contract_type'].lower()[:-1]} of
          {money(app['amount'])}{f" over {app['term']} months" if app['term'] else ""}.</div>
        </div>
      </div>
      <div class="ll-prob">
        <div class="ll-prob-top"><span>Refusal probability</span><b>{pct(p * 100, 0)}</b></div>
        <div class="ll-prob-track" role="img" aria-label="Refusal probability {pct(p * 100, 0)}, limit {pct(THRESHOLD * 100, 0)}">
          <div class="fill" style="width:{p * 100:.1f}%"></div>
          <div class="limit" style="left:{THRESHOLD * 100:.0f}%"><span>Limit {pct(THRESHOLD * 100, 0)}</span></div>
        </div>
      </div>
    </div>
    """
)

# ---- The bank's real decision (client loaded from the records) ----------------------------
if app.get("client_id"):
    last = app.get("last_request")
    if not last:
        line = "No previous application in the bank's records."
    else:
        same = all(app[k] == last[k] for k in ("contract_type", "client_type", "amount", "term", "down_payment"))
        css = "coral" if last["status"] == "Refused" else "teal"
        what = ("this same request" if same else
                f"the client's last request ({money(last['amount'])} {last['contract_type'].lower()[:-1]})")
        line = f'The bank\'s actual decision on {what}: <b class="{css}">{last["status"]}</b>.'
    st.html(f'<div class="ll-bank">{line}</div>')

# ---- Why the model decided --------------------------------------------------------------
biggest = max(abs(r["effect"]) for r in res["reasons"]) or 1
items = ""
for r in res["reasons"]:
    up = r["effect"] > 0
    items += (
        f'<div class="ll-reason {"up" if up else "down"}">'
        f'<span class="ll-reason-arrow" aria-hidden="true">{"▲" if up else "▼"}</span>'
        f'<div class="ll-reason-text"><b>{r["reason"]}</b><span>{reason_value(app, r["reason"])}</span></div>'
        f'<div class="ll-reason-effect"><div class="ll-reason-bar"><div style="width:{abs(r["effect"]) / biggest * 100:.0f}%"></div></div>'
        f'<span>{"Raises" if up else "Lowers"} refusal risk</span></div></div>'
    )
st.html(
    f'<div class="ll-reasons"><div class="ll-chart-title">Why the model decided</div>'
    f'<p class="ll-note">The three details that moved this client\'s refusal probability the most.</p>'
    f'{items}</div>'
)

# ---- Amount + segment ------------------------------------------------------------
left, right = st.columns(2, gap="medium")

with left:
    requested, best = app["amount"], res["max_amount"]
    if not refused:
        body = (f'<div class="ll-amount-row"><span>Requested</span><b>{money(requested)}</b></div>'
                '<div class="ll-amount-bar"><div class="ok" style="width:100%"></div></div>'
                '<p class="ll-note">Approved for the full amount requested.</p>')
    elif best:
        share = best / requested * 100
        body = (f'<div class="ll-amount-row"><span>Requested</span><b>{money(requested)}</b></div>'
                f'<div class="ll-amount-row"><span>Highest approvable</span><b class="teal">{money(best)}</b></div>'
                f'<div class="ll-amount-bar"><div class="ok" style="width:{share:.1f}%"></div></div>'
                f'<p class="ll-note">With every other detail unchanged, the model would approve up to '
                f'{money(best)} ({share:.0f}% of the request).</p>')
    else:
        body = (f'<div class="ll-amount-row"><span>Requested</span><b>{money(requested)}</b></div>'
                f'<div class="ll-amount-row"><span>Highest approvable</span><b class="coral">None found</b></div>'
                '<div class="ll-amount-bar"><div class="none"></div></div>'
                '<p class="ll-note">Lowering the amount alone does not change the decision, even at $10,000. '
                'Other details (loan type, client history, credit scores) drive this result.</p>')
    with st.container(border=True, height=330):
        st.html(f'<div class="ll-chart-title">Highest approvable amount</div>{body}')

with right:
    seg = res["segment"]
    prof = load_segment_profile().loc[seg]
    income_pp = app["income"] / app["family_members"]
    rows = [
        ("Income per person", money(income_pp), money(prof["Income_Person"])),
        ("Age", str(app["age"]), f"{prof['Age']:.0f}"),
        ("Credit score 2", f"{app['ext2']:.2f}", f"{prof['Credit_Score']:.2f}"),
    ]
    table = "".join(f"<tr><td>{a}</td><td>{b}</td><td>{c}</td></tr>" for a, b, c in rows)
    with st.container(border=True, height=330):
        st.html(
            f'<div class="ll-chart-title">Client segment</div>'
            f'<div class="ll-seg-name">{seg}</div><p class="ll-note">{SEGMENT_TEXT.get(seg, "")}</p>'
            f'<table class="ll-seg-table"><tr><th></th><th>Client</th><th>Segment average</th></tr>{table}</table>'
        )

# ---- Client details ------------------------------------------------------------------
groups = detail_groups(app)
st.html('<div class="ll-section-title">Client details</div>')
cards = "".join(
    f'<div class="ll-dl"><div class="ll-dl-title">{g}</div>'
    + "".join(f'<div class="r"><span>{k}</span><b>{v}</b></div>' for k, v in items) + "</div>"
    for g, items in groups.items()
)
st.html(f'<div class="ll-dl-grid">{cards}</div>')

# ---- Officer decision -----------------------------------------------------------------
st.html('<div class="ll-section-title">Officer decision</div>')
with st.container(border=True):
    st.html('<p class="ll-note" style="margin:0">The model supports the decision; the loan officer makes it. '
            'Record the final decision before printing the form.</p>')
    a, b = st.columns([1, 1.4], gap="large")
    officer = a.segmented_control("Final decision", ["Approve", "Refuse", "Refer for review"],
                                  default=None, key="officer_decision")
    officer_name = a.text_input("Loan officer", key="officer_name", placeholder="Full name")
    officer_notes = b.text_area("Notes", key="officer_notes", height=120,
                                placeholder="Reason for the decision, conditions, or documents still needed")

# ---- Actions ----------------------------------------------------------------------------
st.write("")
c1, c2, c3, _ = st.columns([1, 1, 1, 1.2])
pdf = build_pdf(app, res, SEGMENT_TEXT.get(seg, ""), prof,
                {"decision": officer, "name": officer_name.strip(), "notes": officer_notes.strip()})
c1.download_button("Download PDF", data=pdf, file_name=f"{res['reference']}.pdf", mime="application/pdf",
                   type="primary", icon=":material/download:", width="stretch",
                   help="Includes the officer decision, name and notes entered above.")
if c2.button("Edit application", icon=":material/edit:", width="stretch"):
    st.session_state["restore_form"] = True
    st.switch_page("views/new_application.py")
if c3.button("New application", icon=":material/add:", width="stretch"):
    for key in [k for k in st.session_state if isinstance(k, str) and k.startswith(("a_", "officer_"))]:
        del st.session_state[key]
    for key in ("application", "assessment", "form_snapshot", "client", "lookup_id"):
        st.session_state.pop(key, None)
    st.switch_page("views/new_application.py")
