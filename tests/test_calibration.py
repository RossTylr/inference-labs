import yaml

from inference_labs import calibration


def test_every_parameter_has_a_measurement(root):
    params = yaml.safe_load((root / "params.yaml").read_text())["parameters"]
    assert set(params) == set(calibration.MEASURES)


def test_comparison_helpers():
    assert calibration._normalise({"a": 1, "b": 3}) == {"a": 0.25, "b": 0.75}
    assert calibration._normalise({"x": {"a": 2, "b": 2}}) == {"x": {"a": 0.5, "b": 0.5}}
    tol = {"sensitivity": 0.025, "specificity": 0.01}
    assert calibration._lookup(tol, ("free_fluid", "sensitivity"), 0) == 0.025
    assert calibration._lookup({"other": 0.05}, ("other", "truncal"), 0) == 0.05
    assert calibration._lookup(0.01, ("a",), 0) == 0.01
    assert calibration._leaves({"n": [1, 2]}) == [(("n", "0"), 1), (("n", "1"), 2)]


def test_triage_accuracy_is_measured_with_the_coded_rule_under_the_text_reading():
    """The emergent triage rows are measured by baseline.py's MPTT-24 under the text reading (R-2.3)."""
    from inference_labs import baseline

    observed, truth = baseline.generator_sample()
    expected = baseline.flag_metrics(baseline.priority_one(observed, "text"), truth["needs_lsi"].to_numpy(bool))
    assert calibration._triage(observed, truth, None) == {k: expected[k] for k in ("sensitivity", "specificity")}
    assert baseline.CALIBRATION_READING == "text"


def test_only_the_triage_rows_are_emergent(root):
    params = yaml.safe_load((root / "params.yaml").read_text())["parameters"]
    emergent = {pid for pid, p in params.items() if p.get("emergent")}
    assert emergent == {"triage_accuracy_military", "triage_accuracy_civilian"}
    assert all(params[pid]["tolerance"] == 0.05 and params[pid]["source"] == ["E-09"] for pid in emergent)
