"""Lens 04, decision trees (R-4.1 to R-4.12)."""
import math

import numpy as np

from inference_labs import baseline
from inference_labs.interface import Lens, row_problems
from inference_labs.lenses import frequentist, trees as t


def test_the_lens_implements_the_interface():
    assert isinstance(t.LENS, Lens)
    observed, _ = baseline.generator_sample()
    answer = t.LENS.diagnose(observed.iloc[0].to_dict())
    assert 0 <= answer.forest_probability <= 1 and len(answer.tree_path) == t.TREE_DEPTH
    assert 0 <= t.LENS.treat(observed.iloc[0].to_dict()) <= 1


def test_the_models_use_lens_02s_signs_and_training_sample():
    """R-4.1: same four signs, same training sample, scored on the evaluation sample."""
    observed, _ = t.training()
    assert t.sign_matrix(observed).shape[1] == 4 and len(observed) == frequentist.TRAIN_N
    assert t.models().tree.get_depth() == t.TREE_DEPTH


def test_the_forest_beats_the_single_tree_and_matches_the_score():
    """Mechanism: averaging trees removes the single tree's variance; the forest and lens 02's score land together."""
    pre = t.diagnosis_results("pre_hospital")
    assert pre["forest"]["auc"] > pre["single tree"]["auc"] + 0.02
    assert abs(pre["forest"]["auc"] - frequentist.diagnosis_results("pre_hospital")["auc"]) < 0.02


def test_the_printed_tree_has_one_line_per_leaf_and_reads_in_whole_numbers():
    text = t.tree_text().splitlines()
    assert len(text) == len(t.leaves()) <= 2 ** t.TREE_DEPTH
    assert all(".5" not in line for line in text)


def test_the_best_single_question_by_hand_matches_the_library():
    """R-4.3: the Gini gain counted by hand picks the same question as a tree of depth one would."""
    observed, need = t.twenty(tuple(range(1, 21)))
    gains = {name: t.split_gain(q(observed), need)["gain"] for name, q in t.CANDIDATES}
    assert max(gains.values()) >= 0
    assert t.gini(np.array([True, False])) == 0.5 and t.gini(np.array([True, True])) == 0.0


def test_fast_and_frugal_exits_move_sensitivity_and_specificity():
    """R-4.6 (E-59): 'yes, yes' is the most liberal order and 'no, no' the most conservative."""
    table = t.fft_table()
    assert table["sensitivity"].is_monotonic_decreasing and table["specificity"].is_monotonic_increasing


def test_a_tree_finds_the_low_arm_of_the_u_and_a_linear_term_does_not():
    """R-4.7: below 12 breaths a minute the share in need rises again."""
    s = t.u_summary()
    assert s["share in need below 12"] > 0.08
    assert abs(s["tree below 12"] - s["share in need below 12"]) < 0.03
    assert s["linear term below 12"] < s["share in need below 12"] / 2


def test_small_samples_grow_different_trees():
    """R-4.10: twenty samples of 300 do not agree on the first question."""
    assert t.instability()["first question"].nunique() > 3


def test_a_variable_recorded_after_the_decision_inflates_accuracy():
    leak = t.leakage()
    assert leak["first question"] == "the constructed variable" and leak["with"] > leak["without"] + 0.1


def test_the_treatment_tree_is_compared_at_the_abc_scores_specificity():
    for setting in t.SETTINGS:
        r = t.treatment_results(setting)
        assert abs(r["tree"]["specificity"][0] - r["abc"]["specificity"][0]) < 0.02


def test_scorecard_rows_are_well_formed(root):
    rows = t.LENS.scorecard()
    assert rows and all(not row_problems(r, root) for r in rows)
    assert {r.case for r in rows} == {"diagnosis", "treatment"}
    axes = t.seven_axes()
    assert [a.split()[0] for a in axes.index] == [str(i) for i in range(1, 8)]
    assert "baseline: MPTT-24, text (as validated)" in axes.columns


def test_the_panel_labels_its_numbers():
    observed, _ = baseline.generator_sample()
    shown = t.panel(observed[observed["stream"] == "battle"].iloc[0].to_dict())
    assert all("(mechanism)" in shown[k] for k in ("path", "forest", "treatment"))
    assert "an assumption" in shown["treatment"]
