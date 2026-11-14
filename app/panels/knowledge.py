"""Knowledge graph panel, page 1 (slice 8, R-8.12). Every number comes from
inference_labs.lenses.knowledge.page_panel (gate G-8)."""
from inference_labs.lenses import knowledge

ORDER = 8
SOURCE = knowledge.page_panel


def render(st, walk) -> None:
    shown = SOURCE(walk)
    st.subheader(shown["heading"])
    st.markdown(shown["findings"])
    st.markdown(shown["candidates"])
    st.markdown(shown["chain"])
    st.markdown(shown["note"])
