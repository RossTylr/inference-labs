"""Lens 05, stochastic processes (R-6.1 to R-6.12)."""
import ast
import math
from pathlib import Path

import numpy as np
import pytest

from inference_labs import generator
from inference_labs.interface import Lens, row_problems
from inference_labs.lenses import bayesian
from inference_labs.lenses import stochastic as s

MODULE = Path(s.__file__)


def test_the_lens_implements_the_interface():
    assert isinstance(s.LENS, Lens)
    record = {"t_phec_min": 45.0}
    clock = s.LENS.diagnose(record)
    assert 0 < clock.next_hour < 1 and clock.minutes_since_injury == 45.0
    assert len(s.LENS.treat(record)) == s.DRAWS


def test_the_hazard_passes_through_the_three_published_rates():
    """R-6.5: the time-varying hazard is the generator's, fitted to E-85's hourly rates."""
    rates = generator.load_params()["parameters"]["bleeding_death_hazard"]["value"]
    for hour, key in ((1, "h_1h"), (6, "h_6h"), (9, "h_9h")):
        assert float(s.hourly_rate(hour)) == pytest.approx(rates[key], rel=1e-6)
    assert s.E85_MEDIAN_H[0] <= s.median_death_h() <= s.E85_MEDIAN_H[1]


def test_the_fixed_rate_chain_has_the_same_median_and_misses_the_tail():
    """R-6.11: the constant chain matches the median by construction and holds the 9-hour rate far above E-85's."""
    assert float(s.deaths_by(s.median_death_h(), "constant")) == pytest.approx(0.5, abs=1e-6)
    assert float(s.hourly_rate(9.0, "constant")) > 4 * float(s.hourly_rate(9.0))
    assert s.rate_falls_to(0.001, "constant") > s.rate_falls_to(0.001) + 4


def test_alive_and_the_hazard_agree():
    """The share alive is the exponential of minus the integrated hazard."""
    grid = np.linspace(0, 12, 1201)
    integrated = np.concatenate([[0], np.cumsum((s.hourly_rate(grid)[1:] + s.hourly_rate(grid)[:-1]) / 2 * np.diff(grid))])
    assert np.allclose(s.alive(grid), np.exp(-integrated), atol=2e-4)


def test_a_chance_of_death_is_conditional_on_being_alive_now():
    """Lesson 13: the chance between two times divides by the share alive at the first."""
    q = s.death_chance()
    expected = q * (s.deaths_by(2.0) - s.deaths_by(1.0)) / (1 - q * s.deaths_by(1.0))
    assert float(s.chance_between(1.0, 2.0)) == pytest.approx(float(expected))
    assert float(s.next_hour(60.0)) == pytest.approx(float(expected))


def test_the_hand_chain_agrees_with_plain_python_and_the_matrix():
    """R-6.3: the library's steps agree with a hand rule; the matrix's rows sum to one."""
    table = s.rolls()
    states = s.run_chain(table)
    for i, row in table.iterrows():
        state = "bleeding"
        for k in (1, 2, 3):
            coin, die = row[f"hour {k} coin"], row[f"hour {k} die"]
            if state == "bleeding" and coin == "T":
                state = "dead" if die == 1 else "stopped" if die in (2, 3) else "bleeding"
            assert states.loc[i, f"after hour {k}"] == state
    assert np.allclose(s.CHAIN.sum(axis=1), 1)
    shares = s.expected_shares()
    assert shares.loc["after hour 3", "bleeding"] == pytest.approx(0.75 ** 3)


def test_lives_change_only_their_evacuation_clock():
    """R-6.4: the same lives under a faster evacuation die at the same times; deaths move from before Role 2 to
    after it and the total is unchanged."""
    a, b = s.lives(evacuation=1.0), s.lives(evacuation=0.5)
    assert np.array_equal(np.isnan(a["t_death_h"]), np.isnan(b["t_death_h"]))
    assert np.allclose(b["t_role2_h"], 0.5 * a["t_role2_h"])
    slow, fast = s.where_deaths_fall(1.0), s.where_deaths_fall(0.5)
    assert slow["died"] == fast["died"]
    assert fast["died before reaching Role 2"] < slow["died before reaching Role 2"]
    counts = s.state_counts(a, [0, 2, 24])
    assert (counts.sum(axis=1) == len(a)).all()


def test_the_decline_matches_the_first_band_and_reaches_none_at_three_hours():
    """R-6.8: the line's average over the first band is E-22's first band draw by draw; none at 3 hours; harm after."""
    check = s.band_check()
    assert check.loc["up to 1 hour", "lens, mean of draws"] == pytest.approx(0.68, abs=0.01)
    assert s.relative_reduction(180.0).mean() == pytest.approx(0.0)
    assert s.relative_reduction(200.0).mean() < 0
    draws = s.band_draws()
    assert abs(np.corrcoef(draws["up to 1 hour"].draws, draws["over 3 hours"].draws)[0, 1]) < 0.1


def test_the_lens_and_the_generator_agree_on_deaths_averted():
    """R-6.8: on the generator, the lens's expected deaths averted sit close to the generator's own count."""
    r = s.treatment_results()
    assert abs(r["own delay"].mean() - r["generator count"]) < 0.5
    assert r["30 minutes later"].mean() < r["own delay"].mean()


def test_later_deaths_dilute_the_relative_risk():
    """R-6.9: with no later deaths the 30-day relative risk is the 3-hour one; with them it moves towards one."""
    none, some = s.early_late(43, 0.0, 100_000), s.early_late(43, 0.3, 100_000)
    assert some["30 days"]["relative risk"] > none["30 days"]["relative risk"]
    assert some["3 hours"] == none["3 hours"]


def test_rounding_moves_the_bands_towards_no_effect():
    """R-6.10: recorded to the half hour, both bands within 3 hours move towards one."""
    r = s.rounding()
    assert s.recorded([14.9, 15.0, 44.9, 45.0]).tolist() == [0.0, 30.0, 30.0, 60.0]
    assert r["recorded"]["up to 1 hour"] > r["exact"]["up to 1 hour"]
    assert r["recorded"]["1 to 3 hours"] > r["exact"]["1 to 3 hours"]
    assert r["exact"]["none after, hours"] == pytest.approx(3.0, abs=1e-6)


def test_only_the_failure_calls_the_constant_hazard_option():
    """R-6.1: the generator's constant-hazard option is called by the failure and nowhere else."""
    tree = ast.parse(MODULE.read_text(encoding="utf-8"))
    callers = set()
    for fn in [n for n in ast.walk(tree) if isinstance(n, ast.FunctionDef)]:
        for node in ast.walk(fn):
            if (isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute) and node.func.attr == "sample"
                    and any(k.arg == "hazard" for k in node.keywords)):
                callers.add(fn.name)
    assert callers == {"failure_rates"}


def test_the_scorecard_rows_are_labelled():
    rows = s.LENS.scorecard()
    assert rows and all(not row_problems(r, Path(__file__).resolve().parents[1]) for r in rows)
    treatment = [r for r in rows if r.case == "treatment"]
    assert all(r.fit == "native" and math.isnan(r.baseline) for r in treatment)


def test_the_seven_axes_report_both_readings_and_axis_7():
    table = s.seven_axes()
    assert len(table) == 7
    assert "0.10" in table.loc["7 Decision value"].iloc[0]
    assert "baseline: MPTT-24, text (as validated)" in table.columns


@pytest.mark.parametrize("patient_type,setting,casualty", [("haemorrhage", "pre_hospital", 1), ("chest", "in_hospital", 2)])
def test_the_panel_names_its_sources(patient_type, setting, casualty):
    shown = s.page_panel(bayesian.walkthrough(patient_type, setting, None, casualty))
    assert "civilian" in shown["treatment"] and "E-22" in shown["treatment"]
    assert "from injury" in shown["risk"] and "admission" in shown["risk"]
