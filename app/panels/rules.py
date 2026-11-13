"""Rules panel, page 1 (slice 2, R-2.12): the MPTT-24, the baseline. Every number comes from
inference_labs.lenses.rules.page_panel (gate G-8)."""
from inference_labs.lenses import rules

ORDER = 2
SOURCE = rules.page_panel


def render(st, walk) -> None:
    shown = SOURCE(walk)
    st.subheader(shown["heading"])
    st.markdown(shown["priority"])
    st.markdown("\n".join(f"- {step}" for step in shown["steps"]))
    if shown["action"]:
        st.markdown(shown["action"])
    st.markdown(f"**{shown['truth']}**")
    st.markdown(shown["transfusion"])
    st.markdown(f"**{shown['bleeding']}**")
    st.markdown(shown["txa"])
    st.caption(shown["published"])
