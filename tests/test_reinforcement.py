"""Lens 09, reinforcement learning (R-9.1 to R-9.12)."""
import ast
from pathlib import Path

import numpy as np
import pandas as pd

from inference_labs import baseline, generator
from inference_labs.interface import Lens, row_problems
from inference_labs.lenses import bayesian, decision
from inference_labs.lenses import reinforcement as rl

ROOT = Path(__file__).resolve().parents[1]


def test_the_lens_implements_the_interface():
    assert isinstance(rl.LENS, Lens)
    record = {"catastrophic_haemorrhage": False, "walking": False, "avpu": "A", "respiratory_rate": 16,
              "heart_rate": 80}
    route = rl.LENS.diagnose(record)
    assert route.decision in (rl.FLAG, rl.NO_FLAG) and route.questions >= 1
    advice = rl.LENS.treat({"step": 0, "severity": 5})
    assert advice.dose in rl.DOSES and 0 < advice.state_value < 1


def test_the_four_state_world_matches_the_hand_count():
    """R-9.3: two steps of the Bellman equation, as worked on paper."""
    v = rl.toy_values().set_index(["steps left", "state"])
    assert v.loc[(1, "critical"), "value"] == 3 / 4 and v.loc[(1, "unwell"), "value"] == 1.0
    assert v.loc[(2, "critical"), "value"] == 11 / 16 and v.loc[(2, "unwell"), "value"] == 15 / 16
    assert v.loc[(2, "critical"), "value if wait"] == 3 / 8
    assert (v.xs("critical", level="state")["best"] == "treat").all()
    assert (v.xs("unwell", level="state")["best"] == "wait").all()


def test_the_process_tables_are_chances():
    P = rl.transitions()
    assert (P >= 0).all() and np.allclose(P.sum(-1), 1)
    assert np.isclose(sum(rl.START), 1) and np.allclose(np.sum(rl.CLINICIANS, axis=1), 1)
    # the clinicians always give a dose at severity 3 and above
    assert all(rl.CLINICIANS[s][0] == 0 for s in range(2, rl.S))


def test_running_the_process_agrees_with_its_tables():
    """R-9.6: the true value from the tables is what running the process gives, within sampling error."""
    for policy in (rl.clinicians(), rl.do_nothing(), rl.seed_results()["learned"].policy):
        _, reward = rl.run(policy, 100_000, 7)
        assert abs(reward.mean() - rl.true_value(policy)) < 0.005
    leaky = rl.seed_results()["leaky"].policy
    _, reward = rl.run(leaky, 100_000, 7)
    assert abs(reward.mean() - rl.true_value(leaky)) < 0.005


def test_the_best_policy_is_best():
    ref = rl.reference_values()
    assert ref["best"] >= max(ref["clinicians"], ref["do nothing"], ref["random"])
    for seed in decision.SPREAD_SEEDS[:5]:
        assert rl.seed_results(seed)["true"]["learned"] <= ref["best"] + 1e-12


def test_the_clinicians_estimate_from_logs_is_the_share_surviving():
    record, reward = rl.logs()
    est = rl.naive_estimate(record, reward, rl.fixed(rl.estimated_clinicians(record)))
    assert np.isclose(est.value, reward.mean()) and np.isclose(est.ess, len(reward))


def test_the_learner_uses_only_doses_the_logs_hold():
    """R-9.6: learned from logs, not free interaction: no dose given fewer than MIN_RECORDS times at a severity."""
    record, reward = rl.logs()
    counts = pd.crosstab(record["severity"], record["dose"]).reindex(index=range(rl.S), columns=range(rl.A),
                                                                     fill_value=0).to_numpy()
    table = rl.learn(record, reward).table
    for s in range(rl.S):
        assert (counts[s, table[:, s]] >= rl.MIN_RECORDS).all()
    assert (counts[2:, 0] == 0).all()        # no record of an untreated patient at severity 3 and above


def test_doing_nothing_wins_from_the_logs_and_loses_in_truth():
    """R-9.7 across 20 sets of logs."""
    ts = rl.treatment_spread()
    assert len(ts) == rl.SEEDS
    assert (ts["naive: do nothing"] > ts["naive: clinicians"]).all()
    assert (ts["true: do nothing"] < ts["true: clinicians"]).all()
    carry = rl.who_carries()
    assert carry.loc[[3, 4, 5], "share of the weight"].sum() == 0
    assert np.isclose(carry["share of the weight"].sum(), 1)


def test_reading_the_response_raises_the_estimate_and_not_the_truth():
    """R-9.8 across 20 sets of logs."""
    ts = rl.treatment_spread()
    assert (ts["naive: learned, reading the response"] > ts["naive: learned"]).all()
    gap = ts["true: learned, reading the response"] - ts["true: learned"]
    assert gap.min() < 0.005 and gap.mean() <= 0


def test_the_question_policy_beats_the_rule_on_its_own_cost_on_the_training_sample():
    """R-9.5: the Bellman solution costs no more, decision plus questions, than the MPTT-24 asking the same questions
    in its fixed order, on the casualties it was solved on."""
    observed, truth = generator.sample(rl.TRAIN_N, rl.TRAIN_SEED, return_truth=True)
    need = truth["needs_lsi"].to_numpy(bool)
    out = rl.policy_output(observed)
    policy_cost = decision.expected_cost(out["flag"], need) / 100 + rl.QUESTION_COST * out["questions"].mean()
    rule = baseline.priority_one(observed, "figure")
    rule_cost = decision.expected_cost(rule, need) / 100 + rl.QUESTION_COST * rl.rule_questions(observed).mean()
    assert policy_cost <= rule_cost


def test_the_policy_flags_at_the_threshold():
    out = rl.policy_output(baseline.generator_sample()[0])
    assert (out["flag"] == (out["probability"] >= decision.threshold())).all()
    walker = {"catastrophic_haemorrhage": False, "walking": False, "avpu": "A", "respiratory_rate": 16,
              "heart_rate": 80}
    route = rl.LENS.diagnose(walker)
    assert route.asked == (("walking", "no"),) and route.decision == rl.FLAG


def test_the_diagnosis_spread_covers_twenty_seeds_and_the_battle_reversal():
    sp = rl.diagnosis_spread()
    assert len(sp) == rl.SEEDS
    assert (rl.less(sp, "brier", rl.FIGURE) < 0).all()
    assert (rl.less(sp, "brier", rl.FIGURE, ", battle") > 0).all()


def test_scorecard_rows_are_well_formed():
    rows = rl.LENS.scorecard()
    assert rows and all(not row_problems(r, ROOT) for r in rows)
    assert {r.fit for r in rows if r.case == "diagnosis"} == {"weak"}
    assert {r.label for r in rows} == {"mechanism"}
    axes = rl.seven_axes()
    assert len(axes) == 7 and axes.shape[1] == 4


def test_the_panel_draws_on_the_library_only():
    shown = rl.page_panel(bayesian.walkthrough())
    assert {"heading", "route", "rule", "treatment"} <= set(shown)
    assert "constructed" in shown["treatment"]
    tree = ast.parse((ROOT / "app" / "panels" / "reinforcement.py").read_text(encoding="utf-8"))
    imported = {a.name.split(".")[0] for n in ast.walk(tree) if isinstance(n, ast.Import) for a in n.names}
    imported |= {(n.module or "").split(".")[0] for n in ast.walk(tree) if isinstance(n, ast.ImportFrom)}
    assert imported <= {"inference_labs"}
