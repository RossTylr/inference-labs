"""Frequentist panel, page 1 (slice 3, R-3.12). Every number comes from
inference_labs.lenses.frequentist.page_panel (gate G-8)."""
from inference_labs.lenses import frequentist

ORDER = 3
SOURCE = frequentist.page_panel


def render(st, walk) -> None:
    shown = SOURCE(walk)
    st.subheader(shown["heading"])
    st.markdown(shown["score"])
    st.markdown(shown["errors"])
    st.markdown(shown["trial"])
