"""Lens page: 07 Causal (slice 11). The notebook's general explainer and its central figure, as the notebook last
ran them, read by inference_labs.pages.lens_page; every number shown comes from it (gate G-8)."""
import streamlit as st

from inference_labs import pages

SOURCE = pages.lens_page
CASES = ({"lens": "07"},)


def render() -> None:
    shown = SOURCE(**CASES[0])
    st.set_page_config(page_title=f"inference-labs: {shown['title']}", layout="wide")
    st.title(shown["title"])
    st.caption(shown["caption"])
    st.info(shown["intro"])
    first, *rest = shown["explainer"] or [""]
    st.markdown(first)
    if shown["figure"]:
        st.image(shown["figure"], width="stretch")
        st.caption(shown["figure caption"])
    for text in rest:
        st.markdown(text)


if __name__ == "__main__":
    render()
