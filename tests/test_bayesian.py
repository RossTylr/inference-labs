import math

import numpy as np
import pytest

from inference_labs.belief import RV
from inference_labs.interface import Lens, row_problems
from inference_labs.lenses import bayesian as b

POINT = 0.01   # R-1.3: tolerance of one percentage point


def _casualty(sbp=120, scan=True, setting="pre_hospital"):
    return {"sbp": sbp, "scan_free_fluid": scan, "setting": setting, "t_phec_min": 45.0}


def test_the_lens_implements_the_interface_and_diagnose_returns_an_rv():
    assert isinstance(b.LENS, Lens)
    assert isinstance(b.LENS.diagnose(_casualty()), RV)


def test_every_step_of_the_belief_line_takes_and_returns_an_rv():
    casualty = _casualty(sbp=85, scan=True)
    belief = b.start(0.2)
    for step in (lambda r: b.after_triage(r, casualty), lambda r: b.after_scan(r, casualty), b.to_treatment, b.to_evacuation):
        belief = step(belief)
        assert isinstance(belief, RV) and len(belief) == b.N_DRAWS


def test_findings_move_the_belief_and_later_steps_carry_it_unchanged():
    line = b.belief_line(_casualty(sbp=85, scan=True), prior=0.2)
    assert line["start"].mean() == pytest.approx(0.2)
    assert line["triage"].mean() > line["start"].mean()       # a low pressure raises the belief
    assert line["scan"].mean() > line["triage"].mean()         # so does a positive scan
    assert line["treatment"] is line["scan"] and line["evacuation"] is line["scan"]
    cleared = b.belief_line(_casualty(sbp=120, scan=False), prior=0.2)
    assert cleared["scan"].mean() < cleared["start"].mean()


def test_no_scan_leaves_the_belief_unchanged():
    line = b.belief_line(_casualty(scan=None), prior=0.2)
    assert line["scan"] is line["triage"]


def test_belief_after_a_positive_scan_matches_r_1_3():
    pre = b.belief_after_scan(0.20, "pre_hospital")
    lo, hi = pre.interval()
    assert pre.mean() == pytest.approx(0.65, abs=POINT)
    assert (lo, hi) == pytest.approx((0.48, 0.82), abs=POINT)
    assert pre.prob(lambda d: d > 0.5) == pytest.approx(0.96, abs=POINT)
    inside = b.belief_after_scan(0.20, "in_hospital")
    assert inside.mean() == pytest.approx(0.90, abs=POINT)
    assert inside.interval() == pytest.approx((0.83, 0.96), abs=POINT)


def test_scan_accuracy_draws_are_the_stated_betas():
    sens, spec = b.scan_accuracy("pre_hospital")
    rng = np.random.default_rng(42)
    assert np.array_equal(sens.draws, rng.beta(21, 63, 4000))
    assert np.array_equal(spec.draws, rng.beta(257, 9, 4000))


def test_shuffling_or_sorting_one_of_two_paired_quantities_changes_the_answer():
    sens, _ = b.scan_accuracy("pre_hospital")
    miss = 1 - sens
    assert np.allclose((sens + miss).draws, 1.0)
    shuffled = sens + RV(np.random.default_rng(0).permutation(miss.draws))
    lo, hi = shuffled.interval()
    assert lo < 0.9 and hi > 1.1                                  # scans catching more than 100% of bleeds
    assert not np.allclose((sens + RV(np.sort(miss.draws))).draws, 1.0)


def test_trial_reread_is_the_normal_normal_posterior():
    prior, data = b.LogNormalSummary(0.0, 0.2), b.LogNormalSummary(math.log(0.8), 0.1)
    post = b.reread_trial(data, prior)
    w0, w1 = 1 / 0.04, 1 / 0.01
    assert post.posterior.mean == pytest.approx(math.log(0.8) * w1 / (w0 + w1))
    assert post.posterior.sd == pytest.approx(math.sqrt(1 / (w0 + w1)))
    assert post.prob_benefit() == pytest.approx(0.5 + 0.5 * math.erf(-post.posterior.mean / post.posterior.sd / math.sqrt(2)))
    assert post.relative_risk.prob(lambda d: d < 1) == pytest.approx(post.prob_benefit(), abs=0.02)


def test_published_summaries_round_trip_to_their_intervals():
    s = b.CRASH3_HEAD_INJURY_DEATH
    assert s.relative_risk == pytest.approx(0.94)
    assert s.interval() == pytest.approx((0.86, 1.02), abs=0.005)


def test_a_flat_prior_leaves_the_trial_as_it_was_and_crash2_tightens_it():
    flat = b.reread_trial(b.CRASH3_HEAD_INJURY_DEATH, b.PRIORS["minimally informative"])
    assert flat.posterior.mean == pytest.approx(b.CRASH3_HEAD_INJURY_DEATH.mean, abs=1e-4)
    borrowed = b.reread_trial(b.CRASH3_HEAD_INJURY_DEATH, b.PRIORS["CRASH-2"])
    assert borrowed.posterior.sd < flat.posterior.sd
    assert borrowed.prob_benefit() > flat.prob_benefit()


def test_trial_reread_runs_on_the_fixture():
    summary = b.summary_from_file(b.FIXTURE_CRASH3)
    assert math.isfinite(summary.mean) and summary.sd > 0
    assert 0 <= b.reread_trial(summary, b.PRIORS["sceptical"]).prob_benefit() <= 1


def test_real_data_rows_are_labelled_evidence_and_need_a_path_outside_the_repository(tmp_path):
    path = tmp_path / "crash3.csv"
    path.write_text(b.FIXTURE_CRASH3.read_text())
    rows = b.BayesianLens(crash3_path=str(path)).scorecard()
    real = [r for r in rows if r.data_source == str(path)]
    assert len(real) == 1 and real[0].label == "evidence"
    with pytest.raises(ValueError):
        b.BayesianLens(crash3_path=str(b.FIXTURE_CRASH3)).scorecard()


def test_scorecard_rows_are_well_formed_and_the_baseline_is_pending(root):
    rows = b.LENS.scorecard()
    assert rows and all(not row_problems(r, root) for r in rows)
    assert all(r.baseline == "pending slice 2" for r in rows)
    assert {r.case for r in rows} == {"diagnosis", "treatment"}
    assert all(r.label == "mechanism" for r in rows)


def test_the_lens_is_calibrated_on_the_generator_that_made_the_data():
    for setting in b.SETTINGS:
        assert abs(b.evaluate(setting)["calibration"]) < 0.01


def test_in_hospital_accuracy_applied_before_hospital_overstates_the_belief():
    """R-1.5: the wrong population's accuracy, beside the right one."""
    right = b.belief_after_scan(0.20, "pre_hospital")
    wrong = b.belief_after_scan(0.20, "in_hospital")
    assert wrong.mean() - right.mean() > 0.2
    assert wrong.prob(lambda d: d > 0.5) == 1.0 > right.prob(lambda d: d > 0.5)


def test_walkthrough_display_is_built_from_the_belief_line():
    w = b.walkthrough("haemorrhage", "pre_hospital", 0.2, 1)
    shown = w.display()
    assert shown["metrics"]["Belief before any finding"] == "20%"
    assert shown["metrics"]["Belief after the scan"] == b.percent(w.line["evacuation"].mean())
    assert [r["Step"] for r in shown["table"]] == ["Start", "Triage", "Scan", "Treatment", "Evacuation"]
    assert [r["mean"] for r in shown["band"]] == [round(w.line[s].mean(), 4) for s in b.STEPS]
    with pytest.raises(ValueError):
        b.walkthrough("dnbi")


def test_the_belief_weighted_reduction_is_shown_with_its_scale_and_population():
    """The app's tranexamic acid figures come from the library, labelled as a mechanism on civilian data (E-22)."""
    w = b.walkthrough("haemorrhage", "pre_hospital", None, 39)
    shown = w.display()
    assert shown["metrics"]["Belief times relative reduction (mechanism)"] == f"{w.reduction.mean():.2f}"
    assert b.TXA_FIRST_HOUR_DEATHS == (7.7, 5.3) and b.TXA_FIRST_HOUR_POINTS == 2.4
    assert shown["metrics"]["CRASH-2 absolute reduction, within an hour (E-22)"] == "2.4 points"
    note = shown["treatment"]
    for words in ("not a treatment result", "not a change in this casualty's risk of death", "7.7% with placebo",
                  "5.3% with tranexamic acid", "CRASH-2 is civilian", "for a military casualty is an assumption"):
        assert words in note
    assert "a mechanism figure" in shown["findings"]


def test_the_same_casualty_is_drawn_in_either_setting():
    pre, inside = b.walkthrough(setting="pre_hospital"), b.walkthrough(setting="in_hospital")
    assert pre.record["sbp"] == inside.record["sbp"] and pre.bleeding == inside.bleeding


def test_rephill_with_a_flat_prior_gives_about_92_percent():
    """The figure the background file derives from E-77's interval: calculated, not reported by the trial."""
    flat = b.reread_trial(b.REPHILL_DEATH_3H, b.PRIORS["minimally informative"])
    assert flat.prob_benefit() == pytest.approx(0.92, abs=POINT)
