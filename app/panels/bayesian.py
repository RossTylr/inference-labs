"""Bayesian panel, page 1 (slice 1, R-1.9): is this casualty bleeding into the abdomen? Every number comes from
inference_labs.lenses.bayesian.page_panel (gate G-8)."""
from inference_labs.lenses import bayesian

ORDER = 1
SOURCE = bayesian.page_panel

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


def render(st, walk) -> None:
    shown = SOURCE(walk)
    st.subheader("Bayesian panel: is this casualty bleeding into the abdomen?")
    for column, (label, value) in zip(st.columns(len(shown["metrics"])), shown["metrics"].items()):
        column.metric(label, value)
    st.caption(shown["scan_source"])
    st.caption(shown["treatment"])
    st.vega_lite_chart(shown["band"], BAND, width="stretch")
    st.caption("The band holds the middle of the draws at each step; the dotted line is one half. Treatment and "
               "evacuation use the belief without changing it.")
    st.table(shown["table"])
    st.markdown(shown["findings"])
    st.markdown(f"**{shown['truth']}**")
