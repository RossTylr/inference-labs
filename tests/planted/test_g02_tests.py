"""Planted defects for G-2: a failing test, and a test skipped without a reason."""
from pathlib import Path

from harness.gates import g02_tests


def _repo(tmp_path: Path, body: str) -> Path:
    (tmp_path / "test_sample.py").write_text(body)
    return tmp_path


def test_passing_suite_passes(tmp_path):
    assert g02_tests.check(_repo(tmp_path, "def test_ok():\n    assert True\n"), 0).passed


def test_failing_test_fails(tmp_path):
    result = g02_tests.check(_repo(tmp_path, "def test_bad():\n    assert 1 == 2\n"), 0)
    assert not result.passed and "failing" in result.reason


def test_skip_without_reason_fails(tmp_path):
    body = "import pytest\n\n@pytest.mark.skip\ndef test_skipped():\n    pass\n"
    result = g02_tests.check(_repo(tmp_path, body), 0)
    assert not result.passed and "without a reason" in result.reason


def test_skip_with_reason_passes(tmp_path):
    body = "import pytest\n\n@pytest.mark.skip(reason='needs a local data path')\ndef test_skipped():\n    pass\n"
    assert g02_tests.check(_repo(tmp_path, body), 0).passed
