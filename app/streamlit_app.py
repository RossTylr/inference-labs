"""inference-labs, page one: the casualty walk-through, with the Bayesian panel (R-1.9).

    streamlit run app/streamlit_app.py

The page computes nothing. Every number it shows comes from inference_labs (D-14; gate G-8), and every casualty
comes from the synthetic generator inside the package (D-7; gate G-9).
"""
import streamlit as st

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

shown = bayesian.walkthrough(patient_type, setting, prior, int(casualty)).display()

st.subheader("Bayesian panel: is this casualty bleeding into the abdomen?")
for column, (label, value) in zip(st.columns(len(shown["metrics"])), shown["metrics"].items()):
    column.metric(label, value)

BAND = {
    "height": 300,
    "encoding": {"x": {"field": "step", "type": "ordinal", "sort": {"field": "order"}, "title": None,
                       "axis": {"labelAngle": 0}}},
    "layer": [
        {"mark": {"type": "area", "color": "#08306b", "opacity": 0.25},
         "encoding": {"y": {"field": "lo", "type": "quantitative", "scale": {"domain": [0, 1]},
                            "title": "Belief: bleeding into the abdomen"},
                      "y2": {"field": "hi"}}},
        {"mark": {"type": "line", "color": "#08306b", "point": True},
         "encoding": {"y": {"field": "mean", "type": "quantitative"}}},
        {"mark": {"type": "rule", "strokeDash": [4, 4], "color": "black"},
         "encoding": {"y": {"datum": bayesian.EVACUATE_ABOVE}}},
    ],
}
st.vega_lite_chart(shown["band"], BAND, width="stretch")
st.caption("The band holds the middle of the draws at each step; the dotted line is one half. Treatment and "
           "evacuation use the belief without changing it.")

st.table(shown["table"])
st.markdown(shown["findings"])
st.markdown(f"**{shown['truth']}**")
st.markdown(shown["baseline"])
st.caption("Every figure on this page is a mechanism: computed on synthetic casualties, it can only confirm the "
           "model that made them. Scan accuracy before hospital comes from the published counts (E-16); in hospital "
           "it is an assumption centred on pooled figures (E-14). Both studies are civilian. The triage reading is "
           "systolic pressure at or below the ABC score's threshold (E-31).")
