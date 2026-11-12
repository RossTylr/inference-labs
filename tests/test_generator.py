import numpy as np
import pandas as pd
import pytest

from inference_labs import generator
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


def test_cohort_changes_triage_physiology_not_the_casualties():
    mil, t_mil = sample(5000, 12, cohort="military", return_truth=True)
    civ, t_civ = sample(5000, 12, cohort="civilian", return_truth=True)
    pd.testing.assert_frame_equal(t_mil, t_civ)
    assert (mil["stream"] == civ["stream"]).all()
    assert not mil["walking"].equals(civ["walking"])


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


def test_physiology_avoids_the_thresholds_open_under_o1(small_sample):
    obs, _ = small_sample
    assert not (obs["heart_rate"] == 100).any()
    assert not obs["respiratory_rate"].between(22, 24).any()
