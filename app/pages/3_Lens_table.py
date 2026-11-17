"""App page 3: the lens table (slice 11). Every lens's scorecard rows, generated from the scorecards, with a diagnosis
and treatment toggle. Every number comes from inference_labs.pages.lens_table (gate G-8)."""
import streamlit as st

from inference_labs import pages

SOURCE = pages.lens_table
CASES = ({"case": "diagnosis"}, {"case": "treatment"})


def render() -> None:
    st.set_page_config(page_title="inference-labs: lens table", layout="wide")
    with st.sidebar:
        case = st.radio("Case", pages.CASES, format_func=pages.CASE_NAMES.get, key="case")
    shown = SOURCE(case)
    st.title(shown["title"])
    st.caption(shown["caption"])
    st.subheader(shown["heading"])
    st.markdown(shown["about"])
    st.dataframe(shown["table"], hide_index=True, width="stretch")
    st.caption(shown["rule"])
    st.subheader(shown["summary heading"])
    st.dataframe(shown["summary"], hide_index=True, width="stretch")
    st.caption(shown["note"])


if __name__ == "__main__":
    render()
