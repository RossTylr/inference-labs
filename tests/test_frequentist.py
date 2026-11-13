"""Lens 02, frequentist inference and signal detection (R-3.1 to R-3.12)."""
import math

import numpy as np
import pytest

from inference_labs import baseline
from inference_labs.interface import Lens, row_problems
from inference_labs.lenses import frequentist as f


def test_the_lens_implements_the_interface():
    assert isinstance(f.LENS, Lens)
    observed, _ = baseline.generator_sample()
    p = f.LENS.diagnose(observed.iloc[0].to_dict())
    assert 0 <= p <= 1
    assert f.LENS.treat(observed.iloc[0].to_dict()).source == "E-19, E-21"


def test_the_score_is_fitted_away_from_the_casualties_it_is_scored_on():
    """R-3.1: training sample and evaluation sample differ; the threshold matches the rule's specificity."""
    assert (f.TRAIN_N, f.TRAIN_SEED) != (baseline.EVAL_N, baseline.EVAL_SEED)
    score = f.fitted_score()
    observed, truth = baseline.generator_sample()
    need = truth["needs_lsi"].to_numpy(bool)
    spec = float((f.probability(observed)[~need] < score.threshold).mean())
    assert abs(spec - score.matched_specificity) < 0.01


def test_the_score_finds_more_than_the_rule_at_the_same_specificity():
    """Mechanism: the signs carry more than the rule's thresholds keep (R-0.15)."""
    score, rule = f.diagnosis_results("pre_hospital"), baseline.diagnosis_results("pre_hospital", "figure")
    assert abs(score["specificity"][0] - rule["specificity"]) < 0.01
    assert score["sensitivity"][0] > rule["sensitivity"] + 0.03
    assert f.roc()["auc"] > 0.75


def test_wilson_interval_matches_the_formula_and_contains_the_estimate():
    p, lo, hi = f.wilson(83, 100)
    assert p == 0.83 and lo < p < hi
    assert (round(lo, 3), round(hi, 3)) == (0.745, 0.891)
    assert all(math.isnan(x) for x in f.wilson(0, 0))


def test_crash2_intervals_recomputed_from_the_counts_match_the_published_ones():
    """R-3.9: recomputed only where the register holds counts (E-19 denominators, E-20 and E-21 deaths)."""
    all_cause, bleeding = f.trials()[1], f.trials()[2]
    assert [round(x, 2) for x in all_cause.relative_risk] == [0.91, 0.85, 0.97]       # E-20
    assert [round(x, 2) for x in bleeding.relative_risk] == [0.85, 0.76, 0.96]        # E-21
    assert round(bleeding.treated_pct, 1) == 4.9 and round(bleeding.control_pct, 1) == 5.7
    proppr = f.trials()[0]
    assert not proppr.recomputed and proppr.difference == (-4.2, -9.6, 1.1)           # E-72, quoted
    rephill = f.trials()[3]
    assert rephill.recomputed and rephill.difference[1] < 0 < rephill.difference[2]


def test_the_accuracy_table_covers_both_cohorts_both_settings_and_three_methods():
    """R-3.5: the setting changes only the scan, so the signs' accuracy is the same in either setting."""
    table = f.accuracy_table()
    assert len(table) == len(f.COHORT_VIEWS) * len(f.SETTINGS) * len(f.METHODS)
    for (cohort, method), group in table.groupby(["cohort", "method"]):
        assert group["sensitivity"].nunique() == 1 and group["specificity"].nunique() == 1
    injured = table[(table["cohort"] == "military, injured only") & (table["method"].str.contains("text"))]
    assert abs(injured["share in need"].iloc[0] - 0.265) < 0.002                       # D-23


def test_samples_of_357_scatter_widely_around_the_long_run_value():
    """R-3.8: sample size on synthetic data; it does not explain E-07."""
    r = f.resampled_sensitivity()
    lo, hi = r["middle 95%"]
    assert lo < r["long run"] < hi and hi - lo > 0.15
    assert r["share at or above E-07"] < 0.01


def test_published_points_are_labelled_by_source():
    assert {p.source for p in f.PUBLISHED} == {"E-03", "E-05", "E-07", "E-09"}
    assert f.BASTION.sensitivity == 0.836 and f.BASTION.specificity == 0.510


def test_a_negative_difference_is_said_in_words():
    words = f.difference_words((-0.84, -1.46, -0.22))
    assert "0.8 fewer deaths" in words and "-" not in words
    assert "more" in f.difference_words((-1.9, -12.9, 9.1))


def test_scorecard_rows_are_well_formed(root):
    rows = f.LENS.scorecard()
    assert rows and all(not row_problems(r, root) for r in rows)
    assert {r.case for r in rows} == {"diagnosis", "treatment"}
    treatment = [r for r in rows if r.case == "treatment"]
    assert len(treatment) == 1 and treatment[0].data_source == "fixture:crash2.csv" and math.isnan(treatment[0].baseline)
    axes = f.seven_axes()
    assert [a.split()[0] for a in axes.index] == [str(i) for i in range(1, 8)]
    assert "baseline: MPTT-24, text (as validated)" in axes.columns                      # D-24


def test_the_panel_says_what_every_number_is():
    observed, _ = baseline.generator_sample()
    shown = f.panel(observed.iloc[0].to_dict())
    assert "(mechanism)" in shown["score"] and "(E-19, E-21)" in shown["trial"]
    assert "CRASH-2 is civilian" in shown["trial"] and "fewer deaths" in shown["trial"]
