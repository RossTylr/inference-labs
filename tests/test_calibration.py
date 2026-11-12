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


def test_every_reading_of_the_mptt24_agrees_on_the_generator(root, small_sample):
    obs, _ = small_sample
    thresholds = yaml.safe_load((root / "params.yaml").read_text())["parameters"]["mptt24_thresholds"]["value"]
    agree, _ = calibration._readings_agree(obs, thresholds)
    assert agree


def test_readings_disagree_when_a_value_sits_on_a_threshold(small_sample):
    obs, _ = small_sample
    obs = obs.copy()
    obs.loc[obs.index[0], ["walking", "catastrophic_haemorrhage", "heart_rate"]] = [False, False, 100]
    obs.loc[obs.index[0], ["respiratory_rate", "avpu"]] = [16, "A"]
    thresholds = {"respiratory_rate_below": 12, "respiratory_rate_at_or_above": 24, "heart_rate_at_or_above": 100}
    agree, _ = calibration._readings_agree(obs, thresholds)
    assert not agree
