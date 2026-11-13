"""Decision trees panel, page 1 (slice 4, R-4.12). Every number comes from
inference_labs.lenses.trees.page_panel (gate G-8)."""
from inference_labs.lenses import trees

ORDER = 4
SOURCE = trees.page_panel


def render(st, walk) -> None:
    shown = SOURCE(walk)
    st.subheader(shown["heading"])
    st.markdown(shown["path"])
    st.markdown(shown["forest"])
    st.markdown(shown["treatment"])
