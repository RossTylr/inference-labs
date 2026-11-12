"""Planted defects for G-4: a generator that drifts from a parameter, and a parameter with no measurement."""
import numpy as np
import pandas as pd

from harness.gates import g04_calibration

PARAMS = {
    "version": 1,
    "parameters": {
        "share_a": {"value": 0.3, "tolerance": 0.01, "source": "assumption", "label": "assumption"},
    },
}


def _sampler(share):
    def sample(n, seed, return_truth=False, **kwargs):
        rng = np.random.default_rng(seed)
        frame = pd.DataFrame({"a": rng.random(n) < share})
        return frame, frame.copy()
    return sample


MEASURES = {"share_a": ("default", lambda obs, truth, p: float(obs["a"].mean()))}


def test_faithful_sampler_passes(tmp_path):
    result = g04_calibration.check(tmp_path, 0, sampler=_sampler(0.3), params=PARAMS, measures=MEASURES)
    assert result.passed, result.reason


def test_drifted_sampler_fails(tmp_path):
    result = g04_calibration.check(tmp_path, 0, sampler=_sampler(0.36), params=PARAMS, measures=MEASURES)
    assert not result.passed and "share_a" in result.reason


def test_parameter_without_measurement_fails(tmp_path):
    result = g04_calibration.check(tmp_path, 0, sampler=_sampler(0.3), params=PARAMS, measures={})
    assert not result.passed and "share_a" in result.reason
