"""inference-labs, page one: the casualty walk-through. Each lens's panel is a file under app/panels/, found and
shown in slice order (D-27), so adding a lens does not change this file.

    streamlit run app/streamlit_app.py

The page computes nothing. Every number it shows comes from inference_labs (D-14; gate G-8), and every casualty
comes from the synthetic generator inside the package (D-7; gate G-9).
"""
import streamlit as st

import panels
from inference_labs import NOT_FOR_CLINICAL_USE
from inference_labs.lenses import bayesian

st.set_page_config(page_title="inference-labs: casualty walk-through", layout="wide")
st.title("Casualty walk-through")
st.caption(NOT_FOR_CLINICAL_USE)

with st.sidebar:
    st.header("Controls")
    patient_type = st.selectbox("Patient type", bayesian.PATIENT_TYPES, format_func=str.capitalize, key="patient_type")
    setting = st.radio("Where the scan is done", bayesian.SETTINGS, format_func=bayesian.SETTING_NAMES.get, key="setting")
    prior = st.slider("Prior: belief before any finding", min_value=0.01, max_value=0.99,
                      value=bayesian.default_prior(), step=0.01, key="prior")
    casualty = st.number_input("Casualty", min_value=1, max_value=bayesian.casualties_available(patient_type, setting),
                               value=1, step=1, key="casualty")
    st.caption("The prior starts at the share of the generator's battle casualties bleeding into the abdomen. "
               "Moving it recomputes every draw.")

walk = bayesian.walkthrough(patient_type, setting, prior, int(casualty))
for panel in panels.discovered():
    panel.render(st, walk)

st.caption("Every figure on this page is a mechanism, computed on synthetic casualties, which can only confirm the "
           "model that made them, except the published figures, each given with its evidence id. Scan accuracy before hospital comes from the "
           "published counts (E-16); in hospital it is an assumption centred on pooled figures (E-14). "
           f"{bayesian.SCAN_SOURCES} The Bayesian triage reading is systolic pressure at or below the ABC score's "
           "threshold (E-31). The MPTT-24 is coded from the published flowchart (E-08).")
