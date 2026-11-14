"""Lens 07, causal inference (R-7.1 to R-7.12)."""
import ast
from pathlib import Path

import numpy as np
import pytest

from inference_labs.interface import Lens, row_problems
from inference_labs.lenses import bayesian
from inference_labs.lenses import causal as c

MODULE = Path(c.__file__)
ROOT = Path(__file__).resolve().parents[1]


def test_the_lens_implements_the_interface():
    assert isinstance(c.LENS, Lens)
    record = {"t_phec_min": 45.0, "setting": "pre_hospital", "scan_free_fluid": True}
    reading = c.LENS.diagnose(record)
    assert reading.result is True and set(reading.accuracy) == set(c.SELECTIONS)
    effect = c.LENS.treat(record)
    assert effect.band == "up to 1 hour" and effect.casualties > 0
    assert c.LENS.treat({"t_phec_min": 200.0}).band == "over 3 hours"


def test_strength_zero_is_a_coin():
    """R-7.5: cutting the arrow leaves a chance of one half for everyone."""
    observed, truth = c.at_care()
    assert np.allclose(c.chance_of_treatment(observed, truth, 0.0), 0.5)
    assert c.chance_of_treatment(observed, truth, 1.0).std() > 0.1


def test_the_outcome_is_read_from_the_two_potential_outcomes():
    observed, truth = c.at_care()
    treated = c.allocate(observed, truth)
    died = c.outcome(truth, treated)
    assert (died[treated] == truth["died_if_treated"].to_numpy(bool)[treated]).all()
    assert (died[~treated] == truth["died_if_untreated"].to_numpy(bool)[~treated]).all()


def test_the_naive_estimate_is_wrong_and_full_adjustment_ties_with_the_truth():
    """R-7.7 and R-7.9 across 20 seeds: naive and signs-alone readings sit above the truth on every seed; the reading
    adjusted for every variable the allocation uses straddles it."""
    for name in c.ESTIMATORS[:3:2]:
        assert (c.spread_of(c.ALL, name) > 0).all()
    adjusted = c.spread_of(c.ALL, c.ESTIMATORS[1])
    assert adjusted.min() < 0 < adjusted.max()
    assert len(adjusted) == c.SEEDS


def test_cutting_the_arrow_brings_the_naive_estimate_to_the_truth():
    curve = c.strength_curve()
    gap = (curve["naive"] - curve["true value"]).abs()
    assert gap.loc[0.0] < 0.5 < gap.loc[c.DEFAULT_STRENGTH]
    assert np.allclose(curve["true value"], curve["true value"].iloc[0])


def test_the_hand_count_agrees_with_the_library():
    """R-7.4: the coin gives each side the same mix; given only to those alive at one hour, the drug looks protective."""
    table = c.hand_twelve()
    assert len(table) == 12
    coin, alive = c.hand_counts(table, "coin"), c.hand_counts(table, "alive at 1 hour")
    assert coin == {"given": 6, "given, died": 4, "not given": 6, "not given, died": 4}
    assert alive == {"given": 4, "given, died": 2, "not given": 8, "not given, died": 6}


def test_the_constructed_table_reverses_when_combined():
    shares = c.simpson_shares()
    for stratum in ("signs normal", "signs abnormal"):
        assert shares.loc[stratum, "given, %"] < shares.loc[stratum, "not given, %"]
    assert shares.loc["combined", "given, %"] > shares.loc["combined", "not given, %"]


def test_selection_moves_what_it_should():
    """R-7.6: scanning only Priority 1 leaves sensitivity and specificity tied and moves the predictive values;
    partial confirmation moves sensitivity and specificity."""
    spread = c.scan_spread()
    every, p1, conf = c.SELECTIONS
    for m in ("sensitivity", "specificity"):
        d = spread[f"{p1}: {m}"] - spread[f"{every}: {m}"]
        assert d.min() < 0 < d.max()
    assert (spread[f"{p1}: positive predictive value"] > spread[f"{every}: positive predictive value"]).all()
    assert (spread[f"{conf}: sensitivity"] > spread[f"{every}: sensitivity"] + 0.2).all()
    assert (spread[f"{conf}: specificity"] < spread[f"{every}: specificity"]).all()


def test_survival_bias_makes_a_drug_with_no_effect_look_protective():
    """R-7.8: naive relative risk below one on every seed; aligned at a common start, a tie."""
    spread = c.survival_spread()
    assert (spread["naive relative risk"] < 0.8).all()
    assert spread["aligned difference"].min() < 0 < spread["aligned difference"].max()


def test_faster_evacuation_moves_deaths_without_changing_them():
    spread = c.reaching_spread()
    assert (spread["died, as drawn"] == spread["died, faster"]).all()
    assert (spread["before, faster"] < spread["before, as drawn"]).all()
    assert (spread["after, faster"] > spread["after, as drawn"]).all()


def test_scorecard_rows_are_labelled():
    rows = c.LENS.scorecard()
    assert rows and all(not row_problems(r, ROOT) for r in rows)
    assert {r.case for r in rows} == {"diagnosis", "treatment"}
    assert all(r.fit == "weak" for r in rows if r.case == "diagnosis")


def test_seven_axes_and_harm_in_words():
    axes = c.seven_axes()
    assert len(axes) == 7 and axes.shape[1] == 4
    assert "more deaths" in c.Estimate(5.0, 3.0).direction() and "fewer deaths" in c.Estimate(3.0, 5.0).direction()


def test_the_panel_reads_from_the_library():
    shown = c.page_panel(bayesian.walkthrough("haemorrhage", "pre_hospital", None, 1))
    assert set(shown) == {"heading", "allocation", "effect", "spread", "scan"}
    assert "civilian" in shown["scan"]


def test_no_path_outside_the_repository_is_read():
    """R-7.11: the lens reads no file."""
    tree = ast.parse(MODULE.read_text(encoding="utf-8"))
    calls = {getattr(n.func, "attr", getattr(n.func, "id", "")) for n in ast.walk(tree) if isinstance(n, ast.Call)}
    assert not calls & {"open", "read_csv", "read_text", "load"}
