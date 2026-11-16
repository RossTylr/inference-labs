"""Reinforcement learning panel, page 1 (slice 9, R-9.12). Every number comes from
inference_labs.lenses.reinforcement.page_panel (gate G-8)."""
from inference_labs.lenses import reinforcement

ORDER = 9
SOURCE = reinforcement.page_panel


def render(st, walk) -> None:
    shown = SOURCE(walk)
    st.subheader(shown["heading"])
    st.markdown(shown["route"])
    st.markdown(shown["rule"])
    st.markdown(shown["treatment"])
