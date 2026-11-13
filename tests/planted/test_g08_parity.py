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
