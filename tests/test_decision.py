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
    assert float(d.death_by(0)) == 0 and 0 < float(d.death_by(60)) < float(d.death_by(240)) < 1
    assert float(d.death_by(240)) > float(d.death_by(240, "extremity"))


def test_ordering_by_belief_and_clock_does_no_worse_than_the_rule_or_chance():
    for setting in d.SETTINGS:
        r = d.aircraft_policy(setting)
        assert r["knowing who is bleeding"] <= r["belief and clock"] <= r["chance"]
        assert r["belief and clock"] <= r["MPTT-24 priority, then the longer wait"]


def test_accuracy_loses_the_torso_bleeds():
    """R-5.9 (E-38, E-41): the accuracy-optimal cut misses more truncal bleeders and more expected deaths."""
    f = d.torso_failure()
    acc, cost = f["highest accuracy"], f["lowest cost, misses weighed by lethality"]
    assert acc["accuracy"] > cost["accuracy"]
    assert acc["by site"].loc["truncal", "expected deaths among the missed"] > \
        cost["by site"].loc["truncal", "expected deaths among the missed"]


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
    assert "(mechanism)" in shown["costs"] and "(mechanism)" in shown["evacuation"]
    inside = d.panel({**record, "setting": "in_hospital"}, bayesian.belief_line({**record, "setting": "in_hospital"}))
    assert "after triage" in inside["evacuation"] and "after the scan" in shown["evacuation"]
