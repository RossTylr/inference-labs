"""Planted defect for R-0.15: a generator built the version 1 way fails the check on the signs.

Version 1 drew the MPTT-24 priority first, as a noisy copy of need for a life-saving intervention set to
E-09's sensitivity and specificity, and then filled in walking, conscious level, respiratory rate and heart
rate to fit that priority. Its signs carry nothing beyond the priority it drew, so a regression on them cannot
beat the rule, and within Priority 1 and Priority 3 it cannot tell need from no need. Under the figure reading
a casualty drawn into Priority 1 on responding to voice alone falls to Priority 2, where conscious level still
separates need, so the test asks only that some priority stay at or below the bar. The construction below is
version 1's, with its parameter values, applied to the latent states of the current generator. Its draws use
their own seed, so that they do not repeat the generator's.
"""
import numpy as np
import pandas as pd

from inference_labs import calibration
from inference_labs.generator import sample

N, SEED = 100_000, 42
SENSITIVITY, SPECIFICITY = 0.667, 0.699                     # E-09, military
WALKING, CATASTROPHIC = 0.6, 0.5
SIGN_WEIGHTS = {"heart_rate": 0.5, "respiratory_rate": 0.3, "avpu": 0.2}
HR_NORMAL, HR_ABNORMAL = (60, 99), (101, 150)
RR_NORMAL, RR_LOW, RR_HIGH, RR_LOW_SHARE = (12, 21), (6, 10), (25, 40), 0.2
AVPU_ABNORMAL = {"V": 0.5, "P": 0.3, "U": 0.2}


def _uniform_int(rng, n, lo, hi):
    return rng.integers(lo, hi + 1, n)


def version_one(observed: pd.DataFrame, truth: pd.DataFrame, seed: int = SEED + 1) -> pd.DataFrame:
    """The signs redrawn the version 1 way: priority first, then signs to fit it."""
    rng = np.random.default_rng(seed)
    n = len(observed)
    need = truth["needs_lsi"].to_numpy(bool)
    u = rng.random(n)
    priority_one = np.where(need, u < SENSITIVITY, u < 1 - SPECIFICITY)
    external = truth["bleeding"].to_numpy(bool) & truth["site"].isin(["junctional", "extremity"]).to_numpy()
    sign = np.where(priority_one, rng.choice(list(SIGN_WEIGHTS), n, p=list(SIGN_WEIGHTS.values())), "none")
    low = rng.random(n) < RR_LOW_SHARE
    out = observed.copy()
    out["walking"] = ~priority_one & (rng.random(n) < WALKING)
    out["catastrophic_haemorrhage"] = priority_one & external & (rng.random(n) < CATASTROPHIC)
    out["heart_rate"] = np.where(sign == "heart_rate", _uniform_int(rng, n, *HR_ABNORMAL), _uniform_int(rng, n, *HR_NORMAL))
    out["respiratory_rate"] = np.where(
        (sign == "respiratory_rate") & low, _uniform_int(rng, n, *RR_LOW),
        np.where(sign == "respiratory_rate", _uniform_int(rng, n, *RR_HIGH), _uniform_int(rng, n, *RR_NORMAL)))
    out["avpu"] = np.where(sign == "avpu", rng.choice(list(AVPU_ABNORMAL), n, p=list(AVPU_ABNORMAL.values())), "A")
    return out


def test_the_current_generator_passes():
    observed, truth = sample(N, SEED, return_truth=True)
    assert calibration.signs_inform(calibration.sign_information(observed, truth))


def test_a_generator_built_the_version_one_way_fails():
    observed, truth = sample(N, SEED, return_truth=True)
    planted = version_one(observed, truth)
    for reading in ("figure", "text"):
        result = calibration.sign_information(planted, truth, reading)
        assert not calibration.signs_inform(result)
        assert result["regression"] < max(result["priority"], result["priority_one"]) + calibration.SIGNS_GAIN
        assert min(result["within"].values()) <= calibration.SIGNS_WITHIN
