"""App page: the visual gallery (slice 11). The figures of the executed notebooks, as each last ran, read by
inference_labs.pages.gallery; every number shown comes from it (gate G-8)."""
import streamlit as st

from inference_labs import pages

SOURCE = pages.gallery
CASES = ({"notebook": "central"}, {"notebook": "05_stochastic"})


def render() -> None:
    st.set_page_config(page_title="inference-labs: gallery", layout="wide")
    with st.sidebar:
        notebook = st.selectbox("Show", pages.gallery_choices(), format_func=pages.gallery_name, key="notebook")
    shown = SOURCE(notebook)
    st.title(shown["title"])
    st.caption(shown["caption"])
    st.markdown(shown["about"])
    columns = st.columns(2)
    for k, item in enumerate(shown["items"]):
        columns[k % 2].image(item["image"], caption=item["caption"], width="stretch")


if __name__ == "__main__":
    render()
