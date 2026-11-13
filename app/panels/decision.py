"""Decision panel, page 1 (slice 5, R-5.12). Every number comes from
inference_labs.lenses.decision.page_panel (gate G-8)."""
from inference_labs.lenses import decision

ORDER = 5
SOURCE = decision.page_panel


def render(st, walk) -> None:
    shown = SOURCE(walk)
    st.subheader(shown["heading"])
    st.markdown(shown["costs"])
    st.markdown(shown["evacuation"])
