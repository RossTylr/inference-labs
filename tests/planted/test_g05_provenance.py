"""Planted defects for G-5: an id that does not resolve, a missing label, a CARRIED source not marked
provisional, and a stale assumptions register."""
import copy
from pathlib import Path

import yaml

from harness.gates import g05_provenance
from inference_labs.graph import provenance

EVIDENCE = """| Id | Claim | Verified value | Source | Status |
|---|---|---|---|---|
| E-01 | A read claim | 1 | `a` | READ |
| E-02 | A carried claim | 2 | `b` | CARRIED |
"""

PARAMS = {
    "version": 1,
    "valid_from": "2026-11-12",
    "parameters": {
        "read_param": {"description": "x", "value": 0.5, "unit": "p", "tolerance": 0.01, "source": ["E-01"],
                       "label": "registry evidence", "population": "people"},
        "carried_param": {"description": "y", "value": 0.2, "unit": "p", "tolerance": 0.01, "source": ["E-02"],
                          "label": "registry evidence", "provisional": True, "population": "people"},
        "assumed_param": {"description": "z", "value": 3, "unit": "n", "tolerance": 0, "source": "assumption",
                          "label": "assumption", "population": "synthetic casualties"},
    },
}


def _repo(tmp_path: Path, params: dict, register_from: dict | None = None) -> Path:
    (tmp_path / "docs").mkdir()
    (tmp_path / "docs" / "EVIDENCE.md").write_text(EVIDENCE)
    (tmp_path / "params.yaml").write_text(yaml.safe_dump(params, sort_keys=False))
    graph = provenance.build_provenance(register_from or params)
    (tmp_path / "docs" / "ASSUMPTIONS.md").write_text(provenance.register_markdown(graph))
    return tmp_path


def test_clean_parameters_pass(tmp_path):
    result = g05_provenance.check(_repo(tmp_path, PARAMS), 0)
    assert result.passed, result.reason


def test_unresolved_id_fails(tmp_path):
    params = copy.deepcopy(PARAMS)
    params["parameters"]["read_param"]["source"] = ["E-99"]
    result = g05_provenance.check(_repo(tmp_path, params), 0)
    assert not result.passed and "E-99" in result.reason


def test_missing_label_fails(tmp_path):
    params = copy.deepcopy(PARAMS)
    del params["parameters"]["read_param"]["label"]
    result = g05_provenance.check(_repo(tmp_path, params, register_from=PARAMS), 0)
    assert not result.passed and "label" in result.reason


def test_carried_not_provisional_fails(tmp_path):
    params = copy.deepcopy(PARAMS)
    del params["parameters"]["carried_param"]["provisional"]
    result = g05_provenance.check(_repo(tmp_path, params), 0)
    assert not result.passed and "provisional" in result.reason


def test_stale_register_fails(tmp_path):
    params = copy.deepcopy(PARAMS)
    params["parameters"]["assumed_param"]["value"] = 4
    result = g05_provenance.check(_repo(tmp_path, params, register_from=PARAMS), 0)
    assert not result.passed and "stale" in result.reason
