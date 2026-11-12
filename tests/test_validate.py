import json

import yaml

from harness import validate
from harness.common import GateResult, unresolved_items

OK, BAD = GateResult(True, "ok"), GateResult(False, "bad")


def test_verdicts():
    assert validate.verdict_for({"G-1": OK, "G-2": OK}, []) == "BUILT"
    assert validate.verdict_for({"G-1": OK, "G-2": BAD}, []) == "REVISE"
    assert validate.verdict_for({"G-1": OK, "G-2": GateResult(False, "x", evaluable=False)}, []) == "BLOCKED"
    assert validate.verdict_for({"G-1": OK}, ["O-6"]) == "BLOCKED"
    assert validate.tally({"G-1": OK, "G-2": BAD}) == "1/2 pass"


def test_open_items_resolve_only_when_closed_or_waived_with_a_reason():
    manifest = {
        "open_items": {"O-1": "closed", "O-2": {"status": "waived", "reason": "teaching data only"},
                       "O-3": {"status": "waived"}, "O-6": {"status": "open", "reason": "x"}},
        "slices": {1: {"blocked_by": ["O-1", "O-2", "O-3", "O-6", "O-9"]}},
    }
    assert unresolved_items(manifest, 1) == ["O-3", "O-6", "O-9"]


def test_a_crashing_or_missing_gate_cannot_be_evaluated(tmp_path):
    def boom(root, slice_id):
        raise RuntimeError("no data")

    results = validate.run_gates(tmp_path, 0, ["G-1", "G-99"], registry={"G-1": boom})
    assert not results["G-1"].evaluable and "no data" in results["G-1"].reason
    assert not results["G-99"].evaluable


def test_record_writes_the_verdict_file_and_one_ledger_row_per_attempt(tmp_path):
    validate.record(tmp_path, 0, {"G-1": BAD}, [])
    payload = validate.record(tmp_path, 0, {"G-1": OK}, [])
    assert payload["attempt"] == 2 and payload["verdict"] == "BUILT"
    saved = json.loads((tmp_path / "reviews" / "slice-0.verdict.json").read_text())
    assert saved["tally"] == "1/1 pass"
    rows = [r for r in (tmp_path / "LEDGER.md").read_text().splitlines() if r.startswith("| 20")]
    assert len(rows) == 2 and "**REVISE**" in rows[0] and "**BUILT**" in rows[1]


def test_manifest_lists_every_slice_with_gates_dates_and_blocking_items(root):
    manifest = yaml.safe_load((root / "manifest.yaml").read_text())
    assert sorted(manifest["slices"]) == list(range(12))
    for sid, s in manifest["slices"].items():
        assert {"files", "gates", "approved", "blocked_by"} <= set(s)
        for item in s["blocked_by"]:
            assert item in manifest["open_items"]
    assert manifest["slices"][0]["approved"] and manifest["slices"][1]["approved"]
    assert manifest["slices"][1]["blocked_by"] == ["O-6"]
    for item, entry in manifest["open_items"].items():
        assert entry["status"] in ("open", "closed", "waived") and entry["reason"]
