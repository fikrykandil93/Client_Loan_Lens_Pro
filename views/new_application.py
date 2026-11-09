from datetime import date

import streamlit as st

import math

from core import form_rules as R
from core.data import find_client
from core.theme import money, page_head

page_head("New loan application",
          "Enter the client's details and the loan request. Fields adapt to each answer, and the "
          "check runs once every required field is complete.",
          banner="assets/banner_application_web.jpg")

# "Edit application" on the Client Form brings the last submitted values back
if st.session_state.pop("restore_form", False):
    for key, value in st.session_state.get("form_snapshot", {}).items():
        st.session_state[key] = value


# ---- Existing client: fill the form from the bank's records ---------------------------------
def clear_form() -> None:
    for key in [k for k in st.session_state if isinstance(k, str) and k.startswith("a_")]:
        del st.session_state[key]
    st.session_state.pop("client", None)


def clear_all() -> None:
    clear_form()
    st.session_state.pop("lookup_id", None)


def use_client(client_id: int) -> None:
    """Callback: copy one client's record into the form fields (runs before the widgets)."""
    r = find_client(client_id)
    clear_form()
    ss = st.session_state
    num = lambda v: None if v is None or (isinstance(v, float) and math.isnan(v)) else v  # noqa: E731
    ss.update({
        "a_name": f"Client {client_id}",
        "a_gender": "Female" if r.CODE_GENDER == "F" else "Male",
        "a_family": r.NAME_FAMILY_STATUS, "a_edu": r.NAME_EDUCATION_TYPE, "a_children": int(r.CNT_CHILDREN),
        "a_income": int(round(r.AMT_INCOME_TOTAL)), "a_income_type": r.NAME_INCOME_TYPE,
        "a_car": "Yes" if r.FLAG_OWN_CAR == "Y" else "No", "a_realty": "Yes" if r.FLAG_OWN_REALTY == "Y" else "No",
        "a_housing": r.NAME_HOUSING_TYPE, "a_region": int(r.REGION_RATING_CLIENT_W_CITY),
        "a_other_region": bool(r.LIVE_REGION_NOT_WORK_REGION),
        "a_ext2": num(r.EXT_SOURCE_2), "a_ext3": num(r.EXT_SOURCE_3),
        "a_no_ext1": num(r.EXT_SOURCE_1) is None, "a_has_bureau": bool(r.HAS_BUREAU_RECORD),
        **{f"a_doc_{d}": bool(r[f"FLAG_DOCUMENT_{d}"]) for d in R.MAIN_DOCS},
        # Only the number of other documents is known: the first ones in the list are ticked
        "a_other_docs": [f"Doc {d}" for d in R.OTHER_DOCS[:int(r.OTHER_DOCUMENTS)]],
    })
    if r.FLAG_OWN_CAR == "Y":
        ss["a_car_age"] = int(r.OWN_CAR_AGE)
    if num(r.EXT_SOURCE_1) is not None:
        ss["a_ext1"] = float(r.EXT_SOURCE_1)
    if r.HAS_BUREAU_RECORD:
        ss["a_bureau"] = int(r.TOTAL_BUREAU_REQ)
    if r.NAME_INCOME_TYPE not in R.NOT_WORKING:
        if r.OCCUPATION_TYPE in R.OCCUPATIONS:
            ss["a_occ"] = r.OCCUPATION_TYPE
        elif not isinstance(r.OCCUPATION_TYPE, str):
            ss["a_occ"] = "Other"
        if r.ORGANIZATION_TYPE in R.ORGANIZATIONS:
            ss["a_org"] = r.ORGANIZATION_TYPE
        ss["a_months"] = int(r.MONTH_EMPLOYED)
    last = None
    if isinstance(r.NAME_CONTRACT_STATUS, str):     # the client's last application → the loan request
        ss["a_contract"] = r.NAME_CONTRACT_TYPE
        if r.NAME_CLIENT_TYPE in R.CLIENT_TYPES:
            ss["a_client_type"] = r.NAME_CLIENT_TYPE
        ss["a_amount"] = int(round(r.AMT_APPLICATION))
        if r.NAME_CONTRACT_TYPE != "Revolving loans":
            ss["a_term"] = int(r.CNT_PAYMENT)
        if r.NAME_CONTRACT_TYPE == "Consumer loans":
            ss["a_down"] = int(round(r.AMT_DOWN_PAYMENT))
        last = {"status": r.NAME_CONTRACT_STATUS, "contract_type": r.NAME_CONTRACT_TYPE,
                "client_type": r.NAME_CLIENT_TYPE, "amount": float(ss["a_amount"]),
                "term": int(ss.get("a_term", 0)), "down_payment": float(ss.get("a_down", 0))}
    ss["client"] = {"id": client_id, "last": last, "age": int(r.AGE_YEARS), "region_population": float(r.REGION_POPULATION_RELATIVE),
                    "emp_phone": int(r.FLAG_EMP_PHONE)}



# Opened from the Clients page: load that client straight away
if (opened := st.session_state.pop("open_client", None)) is not None:
    use_client(opened)
    st.session_state["lookup_id"] = str(opened)

client = st.session_state.get("client")
with st.container(border=True):
    a, b, c = st.columns([1.3, 0.6, 2.2], vertical_alignment="bottom")
    lookup = a.text_input("Find an existing client", key="lookup_id", placeholder="Client ID, for example 100002")
    b.button("Find", icon=":material/search:", width="stretch")   # Enter in the box does the same
    shown = lookup.strip()
    if client:
        c.html(f'<div class="ll-found ok"><b>Client {client["id"]}</b> loaded from the bank\'s records. '
               'Review the fields and change the loan request if needed.</div>')
        c.button("Clear form", icon=":material/close:", type="tertiary", on_click=clear_all)
    elif shown:
        cid = int(shown) if shown.strip().isdigit() else None
        r = find_client(cid) if cid is not None else None
        if r is None:
            c.html(f'<div class="ll-found">No client with ID <b>{shown}</b>. IDs run from 100001 to 456255.</div>')
        else:
            last = (f'Last request: {money(r.AMT_APPLICATION)} {r.NAME_CONTRACT_TYPE.lower()[:-1]}, '
                    f'<b class="{"coral" if r.NAME_CONTRACT_STATUS == "Refused" else "teal"}">'
                    f'{r.NAME_CONTRACT_STATUS.lower()}</b> by the bank.'
                    if isinstance(r.NAME_CONTRACT_STATUS, str) else "No previous application.")
            c.html(f'<div class="ll-found"><b>Client {cid}</b> · {"Female" if r.CODE_GENDER == "F" else "Male"}, '
                   f'{r.AGE_YEARS} · {money(r.AMT_INCOME_TOTAL)} a year<br>{last}</div>')
            c.button("Use this client", icon=":material/person_add:", type="primary", on_click=use_client,
                     args=(cid,))

errors: list[str] = []
warnings: list[str] = []
progress: dict[int, tuple[int, int]] = {}   # section → (filled, required)
SELECT = "Select…"


def note(where, result) -> None:
    """Show a validator result right under its field and collect it for the summary."""
    if not result:
        return
    level, message = result
    (errors if level == "error" else warnings).append(message)
    where.html(f'<div class="ll-{"err" if level == "error" else "warn"}">{message}</div>')


def filled(v) -> bool:
    return v is not None and v != ""


class Section:
    """Bordered section whose header shows how many required fields are complete."""

    def __init__(self, n: int, title: str, hint: str):
        self.n, self.title, self.hint = n, title, hint
        self.box = st.container(border=True)
        self.header = self.box.empty()
        self.required: list = []

    def need(self, *values) -> None:
        self.required.extend(values)

    def close(self) -> None:
        done, total = sum(filled(v) for v in self.required), len(self.required)
        progress[self.n] = (done, total)
        status = ('<span class="ll-status ok">✓ Complete</span>' if done == total
                  else f'<span class="ll-status">{done} of {total}</span>')
        self.header.html(f'<div class="ll-sec"><span class="n">{self.n}</span><div class="tt">'
                         f'<div class="t">{self.title}</div><div class="h">{self.hint}</div></div>{status}</div>')


form, side = st.columns([2.1, 1], gap="large")

with form:
    # ---- 1. Personal ----------------------------------------------------------
    s1 = Section(1, "Personal details", "Who the client is.")
    with s1.box:
        a, b = st.columns(2)
        name = a.text_input("Client name", key="a_name", placeholder="Full name").strip()
        national_id = b.text_input("National ID" + (" (optional)" if client else ""), key="a_nid",
                                    placeholder="14 digits", max_chars=14).strip()
        if national_id or not client:
            note(b, R.v_national_id(national_id))
        a, b = st.columns(2)
        dob = a.date_input("Date of birth", value=None, min_value=date(1900, 1, 1), max_value=date.today(),
                           format="DD/MM/YYYY", key="a_dob")
        age = R.age_from_dob(dob) if dob else None
        if age is not None:
            a.caption(f"Age: **{age}** (calculated)")
            note(a, R.v_age(age))
        if client:   # the records have the age, not the date of birth
            a.html(f'<div class="ll-hint">Age at the last application: <b>{client["age"]}</b>. '
                   'The date of birth must give this age or more.</div>')
            if age is not None and age < client["age"]:
                note(a, ("error", f"Younger than at the last application ({client['age']}). Check the date of birth."))
        gender = b.segmented_control("Gender", list(R.GENDERS), default=None, key="a_gender")
        a, b = st.columns(2)
        family_status = a.selectbox("Marital status", R.FAMILY_STATUS, index=None, placeholder=SELECT,
                                    key="a_family")
        education = b.selectbox("Education", R.EDUCATION, index=None, placeholder=SELECT, key="a_edu")
        a, b = st.columns(2)
        children = a.number_input("Children", min_value=0, max_value=30, value=None, step=1,
                                  placeholder="0 if none", key="a_children")
        note(a, R.v_children(children) if children is not None else None)
        family = R.family_members(family_status, children) if family_status and children is not None else None
        if family is not None:
            b.html(f'<div class="ll-calc">Family members<b>{family}</b><span>calculated</span></div>')
        # National ID is optional for a client loaded from the records (the data has no IDs)
        nid_ok = national_id if len(national_id) == 14 else ("loaded" if client and not national_id else None)
        s1.need(name, nid_ok, dob, gender, family_status, education, children)
    s1.close()

    # ---- 2. Work ----------------------------------------------------------------
    s2 = Section(2, "Work and income", "Income is yearly, in US dollars.")
    with s2.box:
        a, b = st.columns(2)
        income = a.number_input("Yearly income ($)", min_value=0, value=None, step=5_000,
                                placeholder="For example 150000", key="a_income")
        if income is not None:
            a.caption(f"= {money(income)} per year")
            note(a, R.v_income(income))
        income_type = b.selectbox("Income type", R.INCOME_TYPES, index=None, placeholder=SELECT,
                                  key="a_income_type")
        s2.need(income, income_type)
        working = income_type is not None and income_type not in R.NOT_WORKING
        occupation = organization = months_employed = None
        if income_type in R.NOT_WORKING:
            occupation = organization = "Not Working"
            months_employed = 0
            st.caption(f"{income_type}: occupation, employer and employment length are not needed.")
        elif working:
            a, b = st.columns(2)
            occupation = a.selectbox("Occupation", R.OCCUPATIONS, index=None, placeholder=SELECT, key="a_occ")
            organization = b.selectbox("Employer type", R.ORGANIZATIONS, index=None, placeholder=SELECT,
                                       key="a_org")
            months_employed = a.number_input("Months with current employer", min_value=0, value=None, step=1,
                                             placeholder="For example 24", key="a_months")
            if months_employed is not None and age is not None:
                note(a, R.v_months(months_employed, age))
            s2.need(occupation, organization, months_employed)
    s2.close()

    # ---- 3. Assets and home -----------------------------------------------------------
    s3 = Section(3, "Assets and home", "What the client owns and where they live.")
    with s3.box:
        a, b = st.columns(2)
        car = a.segmented_control("Owns a car", ["Yes", "No"], default=None, key="a_car")
        realty = b.segmented_control("Owns property", ["Yes", "No"], default=None, key="a_realty")
        s3.need(car, realty)
        car_age = 0 if car == "No" else None
        if car == "Yes":
            car_age = a.number_input("Car age (years)", min_value=0, max_value=100, value=None, step=1,
                                     placeholder="For example 5", key="a_car_age")
            if car_age is not None:
                note(a, R.v_car_age(car_age))
            s3.need(car_age)
        a, b = st.columns(2)
        housing = a.selectbox("Housing", R.HOUSING, index=None, placeholder=SELECT, key="a_housing")
        region_rating = b.segmented_control("Region rating", [1, 2, 3], default=None, key="a_region",
                                            help="1 = best-rated region, 3 = lowest-rated.")
        s3.need(housing, region_rating)
        works_other_region = st.checkbox("Works in a different region from where they live", key="a_other_region")
    s3.close()

    # ---- 4. Credit check ----------------------------------------------------------------
    s4 = Section(4, "Credit check", "Scores from external credit sources, from 0 (worst) to 1 (best).")
    with s4.box:
        a, b, c = st.columns(3)
        ext2 = a.number_input("Score 2", min_value=0.0, max_value=1.0, value=None, step=0.01,
                              placeholder="0.00 – 1.00", key="a_ext2")
        ext3 = b.number_input("Score 3", min_value=0.0, max_value=1.0, value=None, step=0.01,
                              placeholder="0.00 – 1.00", key="a_ext3")
        s4.need(ext2, ext3)
        no_ext1 = c.checkbox("Score 1 not available", value=True, key="a_no_ext1",
                             help="Missing for more than half of clients.")
        ext1 = None
        if not no_ext1:
            ext1 = c.number_input("Score 1", min_value=0.0, max_value=1.0, value=None, step=0.01,
                                  placeholder="0.00 – 1.00", key="a_ext1")
            s4.need(ext1)
        a, b = st.columns(2)
        has_bureau = a.checkbox("Has a credit bureau record", value=True, key="a_has_bureau")
        bureau_req = 0
        if has_bureau:
            bureau_req = b.number_input("Credit bureau inquiries (last year)", min_value=0, max_value=100,
                                        value=None, step=1, placeholder="0 if none", key="a_bureau")
            if bureau_req is not None:
                note(b, R.v_bureau(bureau_req))
            s4.need(bureau_req)
    s4.close()

    # ---- 5. Loan request ---------------------------------------------------------------
    s5 = Section(5, "Loan request and documents", "What the client is asking for.")
    with s5.box:
        contract_type = st.segmented_control("Loan type", R.CONTRACT_TYPES, default=None, key="a_contract")
        client_type = st.segmented_control("Client type", R.CLIENT_TYPES, default=None, key="a_client_type",
                                           help="New: first loan with the bank. Refreshed: returning after "
                                                "a long gap. Repeater: regular client.")
        a, b = st.columns(2)
        amount = a.number_input("Requested amount ($)", min_value=0, value=None, step=5_000,
                                placeholder="For example 200000", key="a_amount")
        if amount is not None:
            a.caption(f"= {money(amount)}")
            note(a, R.v_amount(amount))
        s5.need(contract_type, client_type, amount)
        term, down_payment = 0, 0
        if contract_type == "Revolving loans":
            b.caption("Revolving loans (credit cards) have no fixed term or down payment.")
        elif contract_type is not None:
            terms = sorted(set(R.TERMS) | {st.session_state.get("a_term")} - {None})  # keeps a loaded client's term
            term = b.selectbox("Term (months)", terms, index=None, placeholder=SELECT, key="a_term")
            s5.need(term)
            if contract_type == "Consumer loans":
                down_payment = a.number_input("Down payment ($)", min_value=0, value=None, step=1_000,
                                              placeholder="0 if none", key="a_down")
                if down_payment is not None and amount is not None:
                    note(a, R.v_down(down_payment, amount))
                s5.need(down_payment)
            else:
                b.caption("Cash loans have no down payment.")

        st.html('<div class="ll-sub">Required documents</div>')
        cols = st.columns(4)
        docs = {d: cols[i].checkbox(f"Document {d}", key=f"a_doc_{d}") for i, d in enumerate(R.MAIN_DOCS)}
        other_docs = st.pills("Other documents provided", [f"Doc {d}" for d in R.OTHER_DOCS],
                              selection_mode="multi", key="a_other_docs")
    s5.close()

# ---- Side panel: progress, live summary, check button --------------------------------
done = sum(p[0] for p in progress.values())
total = sum(p[1] for p in progress.values())
complete = done == total

with side:
    st.html('<span class="ll-sticky-marker"></span>')
    pct_done = done / total * 100 if total else 0
    steps = "".join(
        f'<span class="{"ok" if progress[n][0] == progress[n][1] else ""}">{n}</span>' for n in sorted(progress)
    )
    ratio = amount / income if amount and income else None
    monthly = amount / term if amount and term else None
    rows = [
        ("Client", name or "–"),
        ("Loan", f"{contract_type}, {client_type.lower()}" if contract_type and client_type else "–"),
        ("Requested", money(amount) if amount else "–"),
        ("Term", "No fixed term" if contract_type == "Revolving loans" else (f"{term} months" if term else "–")),
        ("Monthly payment, before interest", money(monthly) if monthly else "–"),
        ("Amount vs yearly income", f"{ratio:.1f}×" if ratio else "–"),
        ("Family members", str(family) if family is not None else "–"),
    ]
    items = "".join(f'<div class="r"><span>{k}</span><b>{v}</b></div>' for k, v in rows)
    st.html(
        f'<div class="ll-summary"><div class="ll-chart-title">Application summary</div>'
        f'<div class="ll-progress"><div class="lbl"><span>{done} of {total} fields complete</span>'
        f'<span class="steps">{steps}</span></div>'
        f'<div class="bar"><div style="width:{pct_done:.0f}%"></div></div></div>{items}</div>'
    )

    if errors:
        msgs = "".join(f"<li>{m}</li>" for m in errors)
        st.html(f'<div class="ll-err-box"><b>Fix before checking</b><ul>{msgs}</ul></div>')
    if warnings:
        msgs = "".join(f"<li>{m}</li>" for m in warnings)
        st.html(f'<div class="ll-warn-box"><b>Check these values</b><ul>{msgs}</ul></div>')

    ready = complete and not errors
    if st.button("Check application", type="primary", icon=":material/fact_check:",
                 disabled=not ready, width="stretch"):
        st.session_state["application"] = dict(
            name=name, national_id=national_id, dob=dob, gender=R.GENDERS[gender], age=age,
            family_status=family_status, children=int(children), family_members=family, education=education,
            income=float(income), income_type=income_type, working=working, occupation=occupation,
            organization=organization, months_employed=int(months_employed),
            own_car=car == "Yes", car_age=int(car_age), own_realty=realty == "Yes", housing=housing,
            region_rating=int(region_rating), works_other_region=works_other_region,
            ext1=ext1, ext2=float(ext2), ext3=float(ext3), has_bureau=has_bureau, bureau_req=int(bureau_req),
            contract_type=contract_type, client_type=client_type, amount=float(amount), term=int(term),
            down_payment=float(down_payment), doc_3=docs[3], doc_5=docs[5], doc_6=docs[6], doc_8=docs[8],
            other_docs=other_docs or [],
        )
        if client:   # bank-record values the officer can't enter, and the bank's real decision
            st.session_state["application"].update(
                client_id=client["id"], last_request=client["last"],
                region_population=client["region_population"], emp_phone=client["emp_phone"])
        st.session_state["form_snapshot"] = {k: v for k, v in st.session_state.items()
                                             if isinstance(k, str) and k.startswith("a_")}
        st.session_state.pop("assessment", None)
        st.switch_page("views/client_form.py")
    if not complete:
        st.caption("Complete every section to check the application.")
    st.caption("The result supports the loan officer. The final decision is always made by a person.")
