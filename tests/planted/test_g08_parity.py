"""Planted defects for G-8: a numerical import under app/, a number the app computes for itself, and a stray
number in the page's text."""
from harness.gates import g08_parity

GOOD = '''import streamlit as st
p = st.slider("Prior", 0.01, 0.99, 0.2, 0.01, key="prior")
st.metric("Start", f"{100 * p:.0f}%")
st.caption("Teaching material. Not for clinical use.")
'''
CASES = [{"prior": None}, {"prior": 0.5}]


def _expected(inputs):
    p = 0.2 if inputs["prior"] is None else inputs["prior"]
    return {"metrics": {"Start": f"{100 * p:.0f}%"}}


def _check(tmp_path, source):
    app = tmp_path / "app" / "streamlit_app.py"
    app.parent.mkdir(exist_ok=True)
    app.write_text(source)
    return g08_parity.check(tmp_path, 1, app=app, cases=CASES, expected=_expected)


def test_a_page_showing_only_library_values_passes(tmp_path):
    result = _check(tmp_path, GOOD)
    assert result.passed, result.reason


def test_a_numerical_import_fails(tmp_path):
    result = _check(tmp_path, "import numpy as np\n" + GOOD)
    assert not result.passed and "numpy" in result.reason


def test_a_number_the_app_computes_for_itself_fails(tmp_path):
    result = _check(tmp_path, GOOD.replace("f\"{100 * p:.0f}%\"", "f\"{100 * p + 1:.0f}%\""))
    assert not result.passed and "metrics" in result.reason


def test_a_stray_number_in_the_text_fails(tmp_path):
    result = _check(tmp_path, GOOD + 'st.markdown("Ten casualties in a row: 10")\n')
    assert not result.passed and "10" in result.reason


PANEL = '''ORDER = 1
SOURCE = {source}


def render(st, walk):
    st.markdown("panel")
'''


def test_a_panel_whose_numbers_do_not_come_from_the_library_fails(tmp_path):
    panels = tmp_path / "app" / "panels"
    panels.mkdir(parents=True)
    (panels / "own.py").write_text(PANEL.format(source="lambda walk: {'value': 0.5}"))
    assert any("not from inference_labs" in p for p in g08_parity.panel_problems(tmp_path))
    (panels / "own.py").write_text(PANEL.format(source="__import__('inference_labs.lenses.bayesian', fromlist=['x']).page_panel"))
    assert not g08_parity.panel_problems(tmp_path)


def test_a_panel_without_its_source_fails(tmp_path):
    panels = tmp_path / "app" / "panels"
    panels.mkdir(parents=True)
    (panels / "bare.py").write_text("ORDER = 1\n\ndef render(st, walk):\n    pass\n")
    assert any("has no SOURCE" in p for p in g08_parity.panel_problems(tmp_path))


# A further page (slice 11): its numbers must be ones its SOURCE returned for the case checked.
PAGE = '''import streamlit as st

from inference_labs.lenses import decision

SOURCE = decision.threshold
CASES = ({{}},)


def render():
    st.markdown(f"Threshold {{SOURCE()}}")
    st.markdown({extra!r})


if __name__ == "__main__":
    render()
'''


def _page(tmp_path, extra, source=None):
    pages = tmp_path / "app" / "pages"
    pages.mkdir(parents=True, exist_ok=True)
    text = PAGE.format(extra=extra)
    if source is not None:
        text = text.replace("SOURCE = decision.threshold", f"SOURCE = {source}")
    (pages / "2_Page.py").write_text(text)
    return g08_parity.check(tmp_path, 1, app=_app(tmp_path), cases=CASES, expected=_expected)


def _app(tmp_path):
    app = tmp_path / "app" / "streamlit_app.py"
    app.parent.mkdir(parents=True, exist_ok=True)
    app.write_text(GOOD)
    return app


def test_a_further_page_showing_only_library_values_passes(tmp_path):
    result = _page(tmp_path, "No other number here.")
    assert result.passed, result.reason


def test_a_further_page_showing_a_number_its_source_did_not_return_fails(tmp_path):
    result = _page(tmp_path, "Nine in ten: 0.90")
    assert not result.passed and "2_Page.py" in result.reason and "0.90" in result.reason


def test_a_further_page_whose_numbers_do_not_come_from_the_library_fails(tmp_path):
    result = _page(tmp_path, "No other number here.", source="lambda: 0.1")
    assert not result.passed and "not from inference_labs" in result.reason
