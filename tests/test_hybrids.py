"""Notebook 11, prediction sets by split conformal prediction (R-11.5 to R-11.11)."""
import math

import numpy as np
import pandas as pd

from inference_labs import baseline
from inference_labs.interface import Lens, row_problems
from inference_labs.lenses import decision, hybrids as h


def test_the_lens_implements_the_interface(root):
    assert isinstance(h.LENS, Lens)
    observed, _ = baseline.generator_sample()
    record = observed[observed["stream"] == "battle"].iloc[0].to_dict()
    answer = h.LENS.diagnose(record)
    assert set(answer.sets) == set(h.MODELS)
    assert all(s in ("need", "no need", "need or no need", "empty") for s in answer.sets.values())
    join = h.LENS.treat(record)
    assert 0 <= join.score <= 4 and 0 < join.belief_if_positive < 1
    rows = h.LENS.scorecard()
    assert rows and all(not row_problems(r, root) for r in rows)
    assert {r.fit for r in rows if r.case == "diagnosis"} == {"native"}
    assert {r.fit for r in rows if r.case == "treatment"} == {"weak"}


def test_the_threshold_is_the_ceil_n_plus_one_place():
    assert h.rank_for(20) == 19 and h.rank_for(1_000) == 901
    assert h.threshold_from(np.arange(20) / 20) == 18 / 20
    assert math.isinf(h.threshold_from([0.1, 0.2, 0.3, 0.4, 0.5]))      # 6th of 5: keep every label


def test_labels_are_kept_at_the_threshold_at_full_precision():
    q = 0.6406010649937997
    has_need, has_no = h.holds(np.array([1 - q, 0.2]), q)
    assert has_need.tolist() == [True, False] and has_no.tolist() == [True, True]


def test_the_sets_by_hand_agree_with_plain_python():
    """R-11.7: twenty to calibrate, ten to predict."""
    hand = h.by_hand()
    cal = hand["calibration"]
    scores = [1 - p if y else p for p, y in zip(cal["probability of need"], cal["needs an intervention"])]
    q = sorted(scores)[math.ceil(21 * 0.9) - 1]
    assert q == hand["threshold"] and hand["rank"] == 19
    sets = [" or ".join(n for n, keep in (("need", 1 - p <= q), ("no need", p <= q)) if keep)
            for p in hand["new"]["probability of need"]]
    assert sets == list(hand["new"]["set"])


def test_the_rule_probability_is_the_share_in_need_at_each_priority():
    shares = h.rule_shares()
    assert set(shares) == {baseline.P1, baseline.P2, baseline.P3}
    assert shares[baseline.P1] > shares[baseline.P2] > 0


def test_coverage_holds_on_every_stream_and_falls_among_battle_casualties():
    """R-11.5: at least the level on the held-out casualties; below it among battle casualties alone."""
    r = h.diagnosis_results()
    for model in h.MODELS:
        assert r[model]["all"]["coverage"] >= h.LEVEL
        assert r[model]["battle"]["coverage"] < h.LEVEL
        assert r[model]["all"]["empty"] == 0


def test_the_rule_set_holds_need_exactly_for_priority_one():
    observed, _ = baseline.generator_sample()
    assert np.array_equal(h.flags(h.RULE, observed), baseline.priority_one(observed, "figure"))


def test_coverage_falls_below_the_level_when_the_mix_shifts():
    """R-11.10: across 20 seeds, every shifted sample is below the level, for both models."""
    sp = h.spread()
    assert len(sp) == decision.SEEDS
    for model in h.MODELS:
        assert sp[f"coverage, shifted: {model}"].max() < h.LEVEL
        assert sp[f"coverage, battle: {model}"].max() < h.LEVEL
    curve = h.shift_curve()
    for model in h.MODELS:
        c = curve[curve["model"] == model]["coverage"].to_numpy()
        assert (np.diff(c) < 0).all()


def test_the_set_of_every_label_covers_all_and_scores_as_flagging_every_casualty():
    every = h.every_label()
    assert every["coverage"] == 1.0 and every["both"] == 1.0
    assert math.isclose(every["net benefit"], every["flag every casualty"], abs_tol=1e-9)


def test_the_point_estimate_hides_draws_below_one_half():
    """R-11.10: lens 03's belief after a positive scan before hospital, as in R-1.3."""
    point = h.point_across_join()
    assert abs(point["mean"] - 0.65) < 0.01 and 0.02 < point["below half"] < 0.07
    assert math.isclose(point["above half"] + point["below half"], 1.0)


def test_the_score_counts_two_different_beliefs_as_one_item():
    joins = h.scan_into_rule().set_index("setting")
    pre, inside = (joins.loc[h.SETTING_NAMES[s]] for s in h.SETTINGS)
    assert abs(pre["belief after a positive scan"] - 0.65) < 0.01
    assert abs(inside["belief after a positive scan"] - 0.90) < 0.01
    assert inside["ABC score sensitivity"] > pre["ABC score sensitivity"]


def test_the_seven_axes_are_all_present():
    axes = h.seven_axes()
    assert len(axes) == 7 and axes.shape[1] == 5
    assert "D-23" in axes.iloc[0, 2] and "0.10" in axes.iloc[6, 0]
    assert isinstance(axes, pd.DataFrame)
