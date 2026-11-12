"""Planted defect for G-3: a sampler that draws from an unseeded source."""
import numpy as np
import pandas as pd

from harness.gates import g03_determinism


def _seeded(n, seed, return_truth=False):
    rng = np.random.default_rng(seed)
    frame = pd.DataFrame({"x": rng.random(10)})
    return frame, frame.copy()


def _unseeded(n, seed, return_truth=False):
    frame = pd.DataFrame({"x": np.random.default_rng().random(10)})
    return frame, frame.copy()


def test_seeded_sampler_passes(tmp_path):
    assert g03_determinism.check(tmp_path, 0, sampler=_seeded).passed


def test_unseeded_sampler_fails(tmp_path):
    result = g03_determinism.check(tmp_path, 0, sampler=_unseeded)
    assert not result.passed and "differ" in result.reason
