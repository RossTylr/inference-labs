import copy
import inspect
import re

import numpy as np
import pandas as pd
import pytest

from inference_labs import baseline, calibration, generator
from inference_labs.generator import sample

SCAN_COLUMNS = ["setting", "t_scan_min", "scan_free_fluid", "scan_pneumothorax"]


def test_returns_observed_table_or_observed_and_truth():
    obs = sample(500, 1)
    assert isinstance(obs, pd.DataFrame) and len(obs) == 500
    obs2, truth = sample(500, 1, return_truth=True)
    pd.testing.assert_frame_equal(obs, obs2)
    assert (truth["id"] == obs["id"]).all()
    assert {"bleeding", "site", "patient_type", "needs_lsi", "p_death_untreated"} <= set(truth.columns)
    assert not {"bleeding", "site", "patient_type"} & set(obs.columns)


def test_same_seed_same_casualties_different_seed_different():
    pd.testing.assert_frame_equal(sample(2000, 7), sample(2000, 7))
    assert not sample(2000, 7).equals(sample(2000, 8))


def test_patient_types_and_sites(small_sample):
    obs, truth = small_sample
    assert set(truth["patient_type"]) == {"haemorrhage", "chest", "head", "dnbi"}
    assert set(truth.loc[truth["patient_type"] == "haemorrhage", "site"]) == {"truncal", "junctional", "extremity"}
    assert (truth.loc[obs["stream"] != "battle", "patient_type"] == "dnbi").all()
    assert not (truth["bleeding"] & ~truth["needs_lsi"]).any()
    assert (truth["free_fluid"] == (truth["bleeding"] & (truth["site"] == "truncal"))).all()


def test_mix_is_an_argument():
    obs = sample(3000, 3, mix={"battle": 1.0})
    assert (obs["stream"] == "battle").all()
    obs = sample(3000, 3, mix={"disease": 1, "battle": 1, "non_battle": 0})
    assert set(obs["stream"]) == {"disease", "battle"}
    with pytest.raises(ValueError):
        sample(10, 3, mix={"battle": -1, "disease": 2})


def test_setting_changes_only_the_scan():
    pre = sample(5000, 11, setting="pre_hospital")
    post = sample(5000, 11, setting="in_hospital")
    same = [c for c in pre.columns if c not in SCAN_COLUMNS]
    pd.testing.assert_frame_equal(pre[same], post[same])
    assert (post["t_scan_min"] == post["t_role2_min"]).all() and (pre["t_scan_min"] == pre["t_phec_min"]).all()


def test_the_civilian_cohort_is_injured_civilians_with_their_own_mix_and_physiology():
    """The civilian cohort is the non-battle injury stream only, with its own mechanisms and patient types; given
    the same casualties, its signs differ through the cohort-level parameters."""
    params = generator.load_params()["parameters"]
    civ, t_civ = sample(20_000, 12, cohort="civilian", return_truth=True)
    assert set(civ["stream"]) == {"non_battle"}
    types = t_civ["patient_type"].value_counts(normalize=True)
    for kind, share in params["cohort_patient_type_civilian"]["value"].items():
        assert abs(types[kind] - share) < 0.015
    mil_obs, mil_truth = sample(20_000, 12, return_truth=True)
    assert t_civ["needs_lsi"].any() and not mil_truth.loc[mil_obs["stream"] == "non_battle", "needs_lsi"].any()
    mix = {"battle": 1.0}                                  # battle casualties are drawn the same way in both cohorts
    mil, t_mil = sample(5000, 12, mix=mix, cohort="military", return_truth=True)
    civ_b, t_civ_b = sample(5000, 12, mix=mix, cohort="civilian", return_truth=True)
    pd.testing.assert_frame_equal(t_mil, t_civ_b)
    assert (mil["sbp"] == civ_b["sbp"]).all() and (mil["walking"] == civ_b["walking"]).all()
    assert civ_b["heart_rate"].mean() < mil["heart_rate"].mean()


def test_injury_raises_the_resting_rates(small_sample):
    """The resting mean is for a casualty with no injury and none of the conditions; injury adds its increment."""
    obs, truth = small_sample
    params = generator.load_params()["parameters"]
    calm = (obs["stream"] == "disease") & ~truth["sepsis"]
    hurt = (obs["stream"] == "non_battle")
    for sign in ("heart_rate", "respiratory_rate"):
        p = params[sign]["value"]
        assert abs(obs.loc[calm, sign].mean() - p["resting"]) < 0.6
        assert abs(obs.loc[hurt, sign].mean() - obs.loc[calm, sign].mean() - p["injury"]) < 0.8
    assert params["heart_rate"]["value"]["resting"] < 90


def test_bad_arguments_are_refused():
    for kwargs in ({"setting": "role_4"}, {"cohort": "naval"}, {"hazard": "weibull"}):
        with pytest.raises(ValueError):
            sample(10, 1, **kwargs)


def test_scan_is_missing_for_casualties_not_scanned(small_sample):
    obs, _ = small_sample
    battle = obs["stream"] == "battle"
    assert obs.loc[~battle, "scan_free_fluid"].isna().all()
    assert obs.loc[battle, "scan_free_fluid"].notna().all()


def test_hazard_passes_through_the_three_points_of_e85():
    assert generator.bleeding_hazard([1.0, 6.0, 9.0]) == pytest.approx([0.046, 0.010, 0.001], rel=1e-9)


def test_hazard_is_front_loaded():
    h = generator.bleeding_hazard(np.arange(1, 13))
    assert np.all(np.diff(h) < 0)


def test_constant_hazard_keeps_the_deaths_and_moves_the_tail():
    tv = sample(60_000, 5, return_truth=True)
    const = sample(60_000, 5, hazard="constant", return_truth=True)
    assert (tv[0]["died"] == const[0]["died"]).all()
    t_tv, t_c = tv[0]["t_death_h"].dropna(), const[0]["t_death_h"].dropna()
    assert abs(t_tv.median() - t_c.median()) < 0.3
    assert (t_c > 9).mean() > 5 * (t_tv > 9).mean()


def test_txa_relative_risk_follows_the_delay():
    rr = generator.txa_relative_risk([0.0, 90.0, 180.0, 181.0])
    assert rr == pytest.approx([1 - 0.41, 1 - 0.41 * 0.5, 1.0, 1.44])


def test_treatment_acts_only_on_bleeding_casualties(small_sample):
    obs, truth = small_sample
    assert not obs.loc[~truth["bleeding"], "died"].any()
    assert (truth.loc[~truth["bleeding"], "p_death_treated"] == 0).all()


def test_no_triage_priority_is_drawn_or_used(small_sample):
    """R-0.14: the MPTT-24's accuracy is a target the generator never reads. Changing it changes nothing."""
    doc = copy.deepcopy(generator.load_params())
    for pid in ("triage_accuracy_military", "triage_accuracy_civilian"):
        assert doc["parameters"][pid]["emergent"] is True
        doc["parameters"][pid]["value"] = {"sensitivity": 0.99, "specificity": 0.01}
    for cohort in ("military", "civilian"):
        a = sample(5000, 3, cohort=cohort, return_truth=True)
        b = sample(5000, 3, cohort=cohort, return_truth=True, params=doc)
        pd.testing.assert_frame_equal(a[0], b[0])
        pd.testing.assert_frame_equal(a[1], b[1])
    obs, truth = small_sample
    assert not [c for c in list(obs.columns) + list(truth.columns) if "priority" in c or "triage" in c]
    source = inspect.getsource(generator)
    assert "triage_accuracy" not in source
    assert not re.search(r"^\s*(from|import)\b.*\bbaseline\b", source, re.M)


def test_each_sign_is_drawn_from_the_latent_state(small_sample):
    """R-0.14: each sign moves with the condition that drives it, and varies within it."""
    obs, truth = small_sample
    battle = obs["stream"] == "battle"
    hr, rr = obs["heart_rate"], obs["respiratory_rate"]
    assert hr[truth["bleeding"]].mean() > hr[battle & ~truth["needs_lsi"]].mean() + 4
    assert hr[truth["tension_pneumothorax"]].mean() > hr[battle & ~truth["needs_lsi"]].mean() + 6
    assert hr[truth["septic_shock"]].mean() > hr[truth["sepsis"] & ~truth["septic_shock"]].mean() > (
        hr[(obs["stream"] == "disease") & ~truth["sepsis"]].mean())
    assert rr[truth["tension_pneumothorax"]].mean() > rr[battle & ~truth["needs_lsi"]].mean() + 2
    assert rr[truth["breathing_slowed"]].mean() < rr[truth["head_severe"] & ~truth["breathing_slowed"]].mean() - 5
    assert (obs.loc[truth["head_severe"], "avpu"] != "A").mean() > 0.5 > (obs.loc[~truth["head_severe"], "avpu"] != "A").mean()
    bled = truth["bleeding"]
    low, high = obs["sbp"] < 80, obs["sbp"] >= 110
    assert (obs.loc[bled & low, "avpu"] != "A").mean() > (obs.loc[bled & high, "avpu"] != "A").mean()
    assert obs.loc[~truth["needs_lsi"], "walking"].mean() > obs.loc[truth["needs_lsi"], "walking"].mean()
    assert not obs.loc[obs["avpu"].isin(["P", "U"]), "walking"].any()
    external = bled & truth["site"].isin(["junctional", "extremity"])
    assert obs.loc[external, "catastrophic_haemorrhage"].any() and not obs.loc[~external, "catastrophic_haemorrhage"].any()
    assert (hr[bled] < 100).mean() > 0.2                       # a share of bleeding casualties are not tachycardic
    mildest = bled & (truth["severity"] < truth.loc[bled, "severity"].quantile(0.2))
    assert hr[mildest].mean() > hr[battle & ~truth["needs_lsi"]].mean()     # bleeding never lowers the rate
    assert rr[mildest].mean() > rr[battle & ~truth["needs_lsi"]].mean()
    for group in (bled, ~truth["needs_lsi"]):
        assert hr[group].std() > 10 and rr[group].std() > 2


def test_upstream_draws_are_unchanged_from_version_one(small_sample):
    """Version 2 keeps version 1's order of draws, so the latent states, scans, times and deaths of each
    casualty are the same as before; only the signs differ. Spot values from version 1, n = 20,000, seed 42."""
    obs, truth = small_sample
    assert int(truth["bleeding"].sum()) == 2181 and int(obs["died"].sum()) == 339
    assert int(obs["scan_free_fluid"].sum()) == 397 and int(obs["sbp"].sum()) == 2_455_877


@pytest.mark.parametrize("reading", baseline.READINGS)
def test_the_signs_carry_information_beyond_the_rule(reading):
    """R-0.15, on the four signs the MPTT-24 reads after the haemorrhage check: walking, conscious level,
    respiratory rate and heart rate. n = 100,000, seed 42, every stream, military cohort."""
    observed, truth = baseline.generator_sample()
    result = calibration.sign_information(observed, truth, reading)
    assert result["casualties"] == 100_000
    assert result["regression"] >= max(result["priority"], result["priority_one"]) + calibration.SIGNS_GAIN
    assert all(a > calibration.SIGNS_WITHIN for a in result["within"].values()), result["within"]
    assert calibration.signs_inform(result)
