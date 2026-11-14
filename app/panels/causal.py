"""Causal panel, page 1 (slice 7, R-7.12). Every number comes from
inference_labs.lenses.causal.page_panel (gate G-8)."""
from inference_labs.lenses import causal

ORDER = 7
SOURCE = causal.page_panel


def render(st, walk) -> None:
    shown = SOURCE(walk)
    st.subheader(shown["heading"])
    st.markdown(shown["allocation"])
    st.markdown(shown["effect"])
    st.markdown(shown["spread"])
    st.markdown(shown["scan"])
