"""App page 2: mix and setting (slice 11). Every method that flags need for a life-saving intervention, re-scored on
synthetic casualties of the mix and setting the reader chooses. Every number comes from
inference_labs.pages.mix_and_setting (gate G-8); the casualties come from the generator inside the package (gate G-9).
"""
import streamlit as st

from inference_labs import pages

SOURCE = pages.mix_and_setting
CASES = ({}, {"disease": 10, "battle": 80, "non_battle": 10, "setting": "in_hospital"})


def render() -> None:
    st.set_page_config(page_title="inference-labs: mix and setting", layout="wide")
    defaults = pages.mix_defaults()
    with st.sidebar:
        st.header("Mix and setting")
        disease = st.slider("Disease, per cent of admissions", 0, 100, defaults["disease"], key="disease")
        battle = st.slider("Battle injury, per cent of admissions", 0, 100, defaults["battle"], key="battle")
        non_battle = st.slider("Non-battle injury, per cent of admissions", 0, 100, defaults["non_battle"],
                               key="non_battle")
        setting = st.radio("Where the scan is done", pages.SETTINGS, format_func=pages.SETTING_NAMES.get,
                           key="setting")
    shown = SOURCE(disease, battle, non_battle, setting)
    st.title(shown["title"])
    st.caption(shown["caption"])
    if shown["status"]:
        st.warning(shown["status"])
        return
    st.markdown(shown["mix"])
    st.markdown(shown["need"])
    st.dataframe(shown["table"], hide_index=True, width="stretch")
    st.caption(shown["rule"])
    st.markdown(shown["not moved heading"])
    st.markdown("\n".join(f"- {line}" for line in shown["not moved"]))
    st.caption(shown["note"])


if __name__ == "__main__":
    render()
