"""Planted defects for G-12: a gate with no planted test, and a gate that passes its own defect."""
from pathlib import Path

from harness.gates import g12_planted

GATE = "def check(value):\n    return value > 0\n"
GOOD_TEST = "from gate_under_test import check\n\n\ndef test_defect_caught():\n    assert not check(-1)\n"
WEAK_TEST = "from gate_under_test import check\n\n\ndef test_defect_caught():\n    assert not check(1)\n"


def _repo(tmp_path: Path, planted_body: str | None) -> Path:
    gates = tmp_path / "harness" / "gates"
    gates.mkdir(parents=True)
    (gates / "g01_example.py").write_text(GATE)
    planted = tmp_path / "tests" / "planted"
    planted.mkdir(parents=True)
    (planted / "conftest.py").write_text(
        "import sys, pathlib\nsys.path.insert(0, str(pathlib.Path(__file__).parents[2] / 'harness' / 'gates'))\n"
        "import importlib.util\n"
        "spec = importlib.util.spec_from_file_location('gate_under_test', "
        "pathlib.Path(__file__).parents[2] / 'harness' / 'gates' / 'g01_example.py')\n"
        "mod = importlib.util.module_from_spec(spec); spec.loader.exec_module(mod)\n"
        "sys.modules['gate_under_test'] = mod\n"
    )
    if planted_body is not None:
        (planted / "test_g01_example.py").write_text(planted_body)
    return tmp_path


def test_covered_gate_passes(tmp_path):
    result = g12_planted.check(_repo(tmp_path, GOOD_TEST), 0)
    assert result.passed, result.reason


def test_gate_without_planted_test_fails(tmp_path):
    result = g12_planted.check(_repo(tmp_path, None), 0)
    assert not result.passed and "G-1" in result.reason


def test_gate_passing_its_own_defect_fails(tmp_path):
    result = g12_planted.check(_repo(tmp_path, WEAK_TEST), 0)
    assert not result.passed and "passed its own defect" in result.reason
