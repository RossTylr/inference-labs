"""Lens 10, decision theory (R-5.1 to R-5.12)."""
import math

import numpy as np
import pytest

from inference_labs import baseline
from inference_labs.interface import Lens, row_problems
from inference_labs.lenses import decision as d


def test_the_lens_implements_the_interface():
    assert isinstance(d.LENS, Lens)
    observed, _ = baseline.generator_sample()
    answer = d.LENS.diagnose(observed.iloc[0].to_dict())
    assert answer.threshold == pytest.approx(0.1) and answer.act == (answer.probability >= answer.threshold)


def test_the_threshold_follows_the_costs_and_minimises_expected_cost():
    """R-5.1: flag when the probability is at least false-alarm cost over the sum; the cost curve agrees."""
    assert d.threshold({"miss": 9, "false alarm": 1}) == pytest.approx(0.1)
    assert d.threshold({"miss": 1, "false alarm": 1}) == pytest.approx(0.5)
    curve = d.cost_curve()
    assert abs(curve.idxmin() - d.threshold()) <= 0.02


def test_net_benefit_matches_its_definition():
    """E-93: true positives less false positives weighted by t over 1 - t, per casualty."""
    need = np.array([True, True, False, False])
    flag = np.array([True, False, True, False])
    assert d.net_benefit(flag, need, 0.2) == pytest.approx((1 - 1 * 0.25) / 4)
    assert d.treat_all(need, 0.2) == pytest.approx(0.5 - 0.5 * 0.25)
    table = d.net_benefit_table()
    assert (table["treat none"] == 0).all()
    assert table.loc[0.1, "logistic score (lens 02)"] > table.loc[0.1, "MPTT-24, figure (as published)"]


def test_by_hand_totals_match_the_library():
    table, totals = d.by_hand(tuple(range(1, 11)))
    for c, row in totals.iterrows():
        flag = table["probability"].to_numpy() >= c
        need = table["needs"].to_numpy(bool)
        assert row["total cost"] == 9 * (~flag & need).sum() + (flag & ~need).sum()


def test_published_operating_points_use_each_sources_definition():
    """R-5.6: under-triage 1 minus sensitivity, over-triage 1 minus PPV (E-12); E-88's figures as given."""
    points = d.operating_points()
    assert points.loc["MPTT-24, civilian registry", "over-triage"] == pytest.approx(0.66)
    assert points.loc["Dutch practice", "under-triage"] == pytest.approx(0.216)
    assert points.loc["Dutch practice", "over-triage defined as"] == "not given in the register"
    assert 0 < d.sieve_over_triage() < 0.5


def test_the_best_threshold_rises_as_capacity_tightens():
    """R-5.7: a mechanism demonstration on assumed costs."""
    shift = d.load_shift()
    assert shift["best threshold"].is_monotonic_increasing
    assert shift["best threshold"].iloc[-1] > shift["best threshold"].iloc[0]


def test_holding_a_casualty_raises_expected_bleeding_deaths():
    """R-5.8: each minute held adds to the expected bleeding deaths; the chance is the truncal site's."""
    curve = d.hold_curve(0.5, 30.0)
    assert curve.is_monotonic_increasing
    assert float(d.death_between(30, 30)) == 0 and 0 < float(d.death_between(30, 60)) < float(d.death_between(30, 240)) < 1
    assert float(d.death_between(30, 240)) > float(d.death_between(30, 240, "extremity"))


def test_the_chance_of_death_is_conditional_on_being_alive_at_the_decision():
    """Lesson 14: deaths before the decision are not counted, and the chance is that of a casualty alive now."""
    q = d.generator.derived().site_death_prob[d.BLEEDING_SITE]
    now, then = 40.0, 70.0
    before, by_then = float(d.share_dead_by(now)), float(d.share_dead_by(then))
    assert float(d.death_between(now, then)) == pytest.approx(q * (by_then - before) / (1 - q * before))
    assert float(d.death_between(now, then)) < q * by_then
    assert float(d.death_between(now, np.inf, chance=0.0)) == 0


def test_ordering_by_belief_and_clock_is_reported_with_its_spread_across_seeds():
    """Lesson 13: a difference smaller than its spread across seeds is a tie and is called one."""
    for setting in d.SETTINGS:
        table = d.aircraft_spread(setting)
        assert len(table) == d.SEEDS >= 20
        assert (table["knowing who is bleeding"] <= table["belief and clock"]).all()
    assert d.aircraft_summary("pre_hospital")["against the rule"].startswith("fewer")
    assert d.aircraft_policy()["pairs"] == d.PAIRS
    assert d.spread_words([-0.2, 0.1]).startswith("a tie: no detectable difference")
    assert d.spread_words([0.2, 0.4]).startswith("more")


def test_accuracy_loses_the_torso_bleeds():
    """R-5.9 (E-38, E-41): the accuracy-optimal cut misses more truncal bleeders and more expected deaths."""
    f = d.torso_failure()
    acc, cost = f["highest accuracy"], f["lowest cost, misses weighed by lethality"]
    assert acc["accuracy"] > cost["accuracy"]
    assert acc["by site"].loc["truncal", "expected deaths among the missed"] > \
        cost["by site"].loc["truncal", "expected deaths among the missed"]


def test_probabilities_and_thresholds_are_compared_at_full_precision_and_shown_alike():
    """Lesson 15."""
    assert d.against_threshold(0.0996, 0.1) == "at the threshold of 0.100 to 3 decimal places, and below it at full precision"
    assert d.against_threshold(0.1001, 0.1).endswith("at or above it at full precision")
    assert d.against_threshold(0.309, 0.1) == "0.309, at or above the threshold of 0.100"
    assert d.against_threshold(0.05, 0.1, show=False) == "below the threshold of 0.100"


def test_the_battle_casualties_alone_reverse_the_comparison_with_treating_all():
    """Lesson 16 and D-26: among battle casualties half need an intervention, and treating all beats every method."""
    table = d.battle_reversal()
    alone = table["battle casualties alone"]
    assert (alone.drop("treat all") < alone["treat all"]).all()
    assert table.loc["logistic score (lens 02)", "every stream"] > table.loc["treat all", "every stream"]
    assert d.battle_share_in_need()["battle casualties alone"] > 0.4
    flags_all = d.decision_value(np.ones(4, bool), np.array([True, False, True, False]))
    assert "flags every casualty" in flags_all


def test_the_torso_failure_holds_across_seeds():
    spread = d.torso_spread()
    assert len(spread) >= 20
    assert (spread["highest accuracy"] > spread["lowest cost, misses weighed by lethality"]).all()


def test_axis_seven_is_computed_for_every_built_lens():
    """R-5.10: no lens still reads pending."""
    from inference_labs.lenses import frequentist, rules, trees

    for module in (rules, frequentist, trees, d):
        row = module.seven_axes().iloc[6]
        assert not any("Pending" in str(v) for v in row)
    assert "Net benefit" in d.bayesian_decision_value("pre_hospital")["lens"]


def test_scorecard_rows_are_well_formed(root):
    rows = d.LENS.scorecard()
    assert rows and all(not row_problems(r, root) for r in rows)
    assert {r.case for r in rows} == {"diagnosis", "treatment"}
    assert "baseline: MPTT-24, text (as validated)" in d.seven_axes().columns


def test_the_panel_calls_every_cost_an_assumption():
    observed, _ = baseline.generator_sample()
    from inference_labs.lenses import bayesian

    record = observed[observed["stream"] == "battle"].iloc[0].to_dict()
    shown = d.panel(record, bayesian.belief_line(record))
    assert "an assumption" in shown["costs"] and "assumptions" in shown["evacuation"]
    assert "civilian centres" in shown["evacuation"] and "Alive now" in shown["evacuation"]
    assert "(mechanism)" in shown["costs"] and "(mechanism)" in shown["evacuation"]
    inside = d.panel({**record, "setting": "in_hospital"}, bayesian.belief_line({**record, "setting": "in_hospital"}))
    assert "after triage" in inside["evacuation"] and "after the scan" in shown["evacuation"]
