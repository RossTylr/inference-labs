"""Planted defects for G-9: the app opens a real-data file, reads one with pandas, passes the lens a path, and
imports the file system."""
from harness.gates import g09_synthetic_app

CLEAN = '''import streamlit as st
from inference_labs.lenses import bayesian
shown = bayesian.walkthrough("haemorrhage", "pre_hospital", 0.2, 1).display()
st.metric("Belief", shown["metrics"]["Belief after the scan"])
'''


def _check(tmp_path, source):
    app = tmp_path / "streamlit_app.py"
    app.write_text(source)
    return g09_synthetic_app.check(tmp_path, 1, app_files=[app])


def test_a_page_on_the_generator_passes(tmp_path):
    result = _check(tmp_path, CLEAN)
    assert result.passed, result.reason


def test_opening_a_real_data_file_fails(tmp_path):
    result = _check(tmp_path, CLEAN + 'rows = open("/Users/someone/data/real/crash3.csv").read()\n')
    assert not result.passed and "open" in result.reason


def test_reading_with_pandas_fails(tmp_path):
    result = _check(tmp_path, CLEAN + 'import inference_labs as il\nframe = il.pd.read_csv(shown["path"])\n')
    assert not result.passed and "read_csv" in result.reason


def test_passing_the_lens_a_data_path_fails(tmp_path):
    result = _check(tmp_path, CLEAN + 'lens = bayesian.BayesianLens(crash3_path=st.text_input("File"))\n')
    assert not result.passed and "crash3_path" in result.reason


def test_importing_the_file_system_fails(tmp_path):
    result = _check(tmp_path, "import os\n" + CLEAN)
    assert not result.passed and "os" in result.reason
