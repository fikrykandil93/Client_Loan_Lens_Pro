"""LoanLens: internal loan decision support app.

Run:  streamlit run app.py
"""
import streamlit as st

from core.theme import apply_theme

st.set_page_config(page_title="LoanLens", page_icon="assets/icon.png", layout="wide")
apply_theme()
st.logo("assets/logo.svg", size="large")

home = st.Page("views/home.py", title="Home", icon=":material/home:", default=True)
insights = st.Page("views/insights.py", title="Insights", icon=":material/insights:")
new_app = st.Page("views/new_application.py", title="New Application", icon=":material/edit_document:")
# Hidden from the menu: opened only from New Application with st.switch_page
client_form = st.Page("views/client_form.py", title="Credit Approval Form", icon=":material/description:",
                      visibility="hidden")
clients = st.Page("views/clients.py", title="Clients", icon=":material/group:")
segments = st.Page("views/segments_model.py", title="Segments & Model", icon=":material/donut_small:")

nav = st.navigation([home, insights, clients, new_app, client_form, segments], position="top")
nav.run()
