"""App page 4: the graph explorer (slice 11). The capability chain for an injury, the provenance of every generator
parameter, and one edge read three ways. Every number comes from inference_labs.pages.graph_explorer (gate G-8)."""
import streamlit as st

from inference_labs import pages

SOURCE = pages.graph_explorer
CASES = ({}, {"injury": "tension pneumothorax", "start": "Role 1", "evidence": "E-41"})


def render() -> None:
    st.set_page_config(page_title="inference-labs: graph explorer", layout="wide")
    with st.sidebar:
        st.header("Graph explorer")
        injuries, starts, ids = pages.injuries(), pages.starts(), pages.evidence_ids()
        injury = st.selectbox("Injury", injuries, index=injuries.index(pages.DEFAULT_INJURY), key="injury")
        start = st.selectbox("Where the casualty lies", starts, index=starts.index(pages.DEFAULT_START), key="start")
        evidence = st.selectbox("Evidence id", ids, index=ids.index(pages.DEFAULT_EVIDENCE), key="evidence")
    shown = SOURCE(injury, start, evidence)
    st.title(shown["title"])
    st.caption(shown["caption"])
    st.subheader(shown["chain heading"])
    st.dataframe(shown["chain"], hide_index=True, width="stretch")
    st.caption(shown["chain note"])
    st.subheader(shown["edge heading"])
    edge = shown["edge"]
    st.markdown(edge["graph"])
    st.markdown(edge["probability"])
    st.markdown(edge["intervention"])
    st.dataframe(edge["table"], hide_index=True, width="stretch")
    st.subheader(shown["provenance heading"])
    st.dataframe(shown["provenance"], hide_index=True, width="stretch")
    st.caption(shown["provenance note"])
    st.subheader(shown["depends heading"])
    st.markdown(shown["depends"])


if __name__ == "__main__":
    render()
