"""Connectionist panel, page 1 (slice 10, R-10.12). Every number comes from
inference_labs.lenses.connectionist.page_panel (gate G-8)."""
from inference_labs.lenses import connectionist

ORDER = 10
SOURCE = connectionist.page_panel


def render(st, walk) -> None:
    shown = SOURCE(walk)
    st.subheader(shown["heading"])
    st.markdown(shown["signs"])
    st.markdown(shown["battle"])
    st.markdown(shown["images"])
    st.markdown(shown["maps"])
