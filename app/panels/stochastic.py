"""Stochastic panel, page 1 (slice 6, R-6.12). Every number comes from
inference_labs.lenses.stochastic.page_panel (gate G-8)."""
from inference_labs.lenses import stochastic

ORDER = 6
SOURCE = stochastic.page_panel


def render(st, walk) -> None:
    shown = SOURCE(walk)
    st.subheader(shown["heading"])
    st.markdown(shown["clock"])
    st.markdown(shown["risk"])
    st.markdown(shown["treatment"])
    st.markdown(f"**{shown['truth']}**")
