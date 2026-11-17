"""Notebook 11, hybrids: prediction sets by split conformal prediction (PRD section 6.11; background/11-hybrids.md).

A model that gives one answer hides its doubt. Split conformal prediction (E-112) wraps any trained model so that it
gives a set of answers instead, chosen so that the set holds the true answer at a rate the user sets. Here the answer
is whether a casualty needs a life-saving intervention, so a set is {need}, {no need} or both.

    diagnosis   two models are wrapped: the MPTT-24 under the figure reading, whose probability for a casualty is the
                share in need at that casualty's priority on lens 02's training sample, and lens 04's single tree.
                Each is calibrated on 1,000 further synthetic casualties (seed 11) to hold the true label for at least
                90% of casualties, on average over casualties like them, and scored on the evaluation sample of 100,000
                (seed 42), which neither the models nor the calibration saw.
    treatment   a weak fit: the join of a test into a rule. The ABC score counts a positive scan as one of its four
                items (E-31). Lens 03's belief after that scan is much lower before hospital than in hospital; the
                score counts the item the same either way.

The method
- A label's nonconformity for a casualty is one minus the model's probability of that label.
- The threshold is the ceil((n + 1) x level)-th smallest nonconformity of the true labels of the n calibration
  casualties. With n = 1,000 and a level of 0.90 that is the 901st.
- A casualty's set holds every label whose nonconformity is at or below the threshold, compared at full precision.
- The rate is an average over casualties exchangeable with the calibration ones. It says nothing about any subgroup,
  or about casualties drawn from a different mix. That condition is general knowledge about the method; it is not
  taken from E-112's register entry.

Assumptions
- The level, 0.90, the calibration size, 1,000, and the shifted mixes are choices made here.
- Significant bleeding stands in for the need for transfusion, and small arms injuries count as penetrating, as in
  lens 01.
- The prior of 0.20 behind the belief after a positive scan is the assumed one of notebook 03.

Every result computed here on the generator is a mechanism, not evidence (D-8).
"""
from __future__ import annotations

import math
from dataclasses import dataclass
from functools import lru_cache
from typing import Any, Mapping

import numpy as np
import pandas as pd

from inference_labs import baseline, generator
from inference_labs.interface import ScorecardRow
from inference_labs.lenses import bayesian, decision, frequentist, rules, trees

LENS_NAME = "Hybrids: prediction sets"
LEVEL = 0.90                         # the share of casualties whose set should hold the true label (a choice)
CAL_N, CAL_SEED = 1_000, 11          # the calibration casualties: neither the models' training sample nor the evaluation
CAL_SEED_OFFSET = 1_000              # the spread: calibration seed s + 1,000 beside evaluation seed s
NEED, NO_NEED = "need", "no need"
RULE, TREE = "MPTT-24 (figure)", "single tree"
MODELS = (RULE, TREE)
SETTINGS = baseline.SETTINGS
SETTING_NAMES = baseline.SETTING_NAMES
PRIOR = 0.20                         # notebook 03's assumed prior, for the belief behind a positive scan
SHIFTED = {"disease": 0.10, "battle": 0.80, "non_battle": 0.10}    # an assumed mix heavy in battle casualties
BATTLE_SHARES = (0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0)          # mixes for the shift curve (assumptions)
LEVELS = (0.80, 0.85, 0.90, 0.95, 0.99)
HAND_CAL, HAND_NEW = 20, 10

# E-74, as published (abstract): STAAMP, 903 patients, 30-day mortality hazard ratio 0.81 (0.59-1.11), and the
# posterior ratio under three priors.
STAAMP = {"patients": 903, "hazard ratio": (0.81, 0.59, 1.11)}
STAAMP_POSTERIORS = (("non-informative prior", 0.82, 0.52, 1.23), ("PATCH-Trauma prior", 0.80, 0.65, 0.97),
                     ("CRASH-2 prior", 0.91, 0.85, 0.97))


# ------------------------------------------------------------------------------------------------ the two models

@lru_cache(maxsize=1)
def rule_shares() -> dict[str, float]:
    """The MPTT-24's probability: the share in need of a life-saving intervention at each priority under the figure
    reading, on lens 02's training sample of 100,000 synthetic casualties (mechanism)."""
    observed, truth = trees.training()
    priority = baseline.triage_table(observed, baseline.DEFAULT_READING)["priority"].to_numpy()
    need = truth["needs_lsi"].to_numpy(bool)
    return {str(p): float(need[priority == p].mean()) for p in pd.unique(priority)}


def rule_probability(observed: pd.DataFrame) -> np.ndarray:
    shares = rule_shares()
    priority = baseline.triage_table(observed, baseline.DEFAULT_READING)["priority"].to_numpy()
    return np.array([shares[str(p)] for p in priority], dtype=float)


def tree_probability(observed: pd.DataFrame) -> np.ndarray:
    return trees.probabilities(observed)["single tree"]


def probability(model: str, observed: pd.DataFrame) -> np.ndarray:
    if model == RULE:
        return rule_probability(observed)
    if model == TREE:
        return tree_probability(observed)
    raise ValueError(f"model must be one of {MODELS}")


# ------------------------------------------------------------------------------------------------ the method

def nonconformity(p, need) -> np.ndarray:
    """One minus the model's probability of the label: 1 - p for a casualty in need, p for one not in need."""
    p, need = np.asarray(p, float), np.asarray(need, bool)
    return np.where(need, 1 - p, p)


def rank_for(n: int, level: float = LEVEL) -> int:
    """Which smallest calibration score is the threshold: ceil((n + 1) x level). Above n, no finite threshold will do."""
    return math.ceil((n + 1) * level - 1e-9)


def threshold_from(scores, level: float = LEVEL) -> float:
    """The threshold read off the calibration casualties' scores. Where the rank exceeds their number, every label
    is kept, and the threshold is infinite."""
    s = np.sort(np.asarray(scores, float))
    k = rank_for(s.size, level)
    return float("inf") if k > s.size else float(s[k - 1])


def holds(p, q: float) -> tuple[np.ndarray, np.ndarray]:
    """Whether each casualty's set holds need, and whether it holds no need, at threshold q (full precision)."""
    p = np.asarray(p, float)
    return (1 - p) <= q, p <= q


def set_words(has_need: bool, has_no: bool) -> str:
    if has_need and has_no:
        return f"{NEED} or {NO_NEED}"
    return NEED if has_need else (NO_NEED if has_no else "empty")


@lru_cache(maxsize=None)
def calibration_sample(n: int = CAL_N, seed: int = CAL_SEED, mix_key: tuple | None = None):
    return generator.sample(n, seed, mix=dict(mix_key) if mix_key else None, return_truth=True)


@lru_cache(maxsize=None)
def threshold(model: str, level: float = LEVEL, n: int = CAL_N, seed: int = CAL_SEED) -> float:
    """The model's threshold from the calibration casualties (mechanism)."""
    observed, truth = calibration_sample(n, seed)
    return threshold_from(nonconformity(probability(model, observed), truth["needs_lsi"].to_numpy(bool)), level)


def measure(p, need, q: float) -> dict:
    """Sets at threshold q scored against the truth: coverage, the share holding both labels, the share empty, the
    mean set size, and the sensitivity and specificity of flagging a casualty whose set holds need."""
    need = np.asarray(need, bool)
    has_need, has_no = holds(p, q)
    covered = np.where(need, has_need, has_no)
    return {"casualties": int(need.size), "coverage": float(covered.mean()),
            "both": float((has_need & has_no).mean()), "empty": float((~has_need & ~has_no).mean()),
            "size": float((has_need.astype(int) + has_no.astype(int)).mean()),
            "sensitivity": float(has_need[need].mean()), "specificity": float((~has_need[~need]).mean())}


@lru_cache(maxsize=None)
def diagnosis_results(setting: str = "pre_hospital", level: float = LEVEL) -> dict:
    """Both models' sets on the evaluation sample, every stream and the battle casualties alone (mechanism). The
    setting changes only the scan, which neither model reads."""
    observed, truth = baseline.generator_sample(setting)
    need = truth["needs_lsi"].to_numpy(bool)
    battle = (observed["stream"] == "battle").to_numpy()
    out = {}
    for model in MODELS:
        p, q = probability(model, observed), threshold(model, level)
        out[model] = {"threshold": q, "all": measure(p, need, q), "battle": measure(p[battle], need[battle], q),
                      "brier": float(np.mean((p - need) ** 2)), "calibration": float(p.mean() - need.mean())}
    return out


def flags(model: str, observed: pd.DataFrame, level: float = LEVEL) -> np.ndarray:
    """True where the casualty's set holds need: the set read as a flag for the scorecard's axes 1 and 7."""
    return holds(probability(model, observed), threshold(model, level))[0]


# ------------------------------------------------------------------------------------------------ the spread

@lru_cache(maxsize=None)
def spread(level: float = LEVEL) -> pd.DataFrame:
    """On 20 further samples of 100,000 (seeds 43 to 62), each calibrated afresh on 1,000 casualties of seed s + 1,000:
    for each model, coverage on every stream, among the battle casualties alone and on a sample of the shifted mix;
    the share of sets holding both labels; sensitivity and specificity of the flag; net benefit at 0.10 on every
    stream and among the battle casualties alone; with the MPTT-24's own figures beside them (mechanism)."""
    t = decision.threshold()

    def one(seed: int) -> dict:
        observed, truth = generator.sample(baseline.EVAL_N, seed, return_truth=True)
        shifted_obs, shifted_truth = generator.sample(baseline.EVAL_N, seed, mix=SHIFTED, return_truth=True)
        cal_obs, cal_truth = generator.sample(CAL_N, seed + CAL_SEED_OFFSET, return_truth=True)
        need = truth["needs_lsi"].to_numpy(bool)
        battle = (observed["stream"] == "battle").to_numpy()
        row = {"net benefit: flag every casualty": 100 * decision.flag_all(need, t),
               "net benefit, battle: flag every casualty": 100 * decision.flag_all(need[battle], t)}
        for reading in baseline.READINGS:
            flag = baseline.priority_one(observed, reading)
            m = baseline.flag_metrics(flag, need)
            row[f"correct: {reading}"] = 1 - m["brier"]
            row[f"sensitivity: {reading}"], row[f"specificity: {reading}"] = m["sensitivity"], m["specificity"]
            row[f"net benefit: {reading}"] = 100 * decision.net_benefit(flag, need, t)
            row[f"net benefit, battle: {reading}"] = 100 * decision.net_benefit(flag[battle], need[battle], t)
        for model in MODELS:
            q = threshold_from(nonconformity(probability(model, cal_obs), cal_truth["needs_lsi"].to_numpy(bool)),
                               level)
            p = probability(model, observed)
            every, alone = measure(p, need, q), measure(p[battle], need[battle], q)
            moved = measure(probability(model, shifted_obs), shifted_truth["needs_lsi"].to_numpy(bool), q)
            flag = holds(p, q)[0]
            row.update({f"threshold: {model}": q, f"coverage: {model}": every["coverage"],
                        f"coverage, battle: {model}": alone["coverage"], f"coverage, shifted: {model}": moved["coverage"],
                        f"both: {model}": every["both"], f"sensitivity: {model}": every["sensitivity"],
                        f"specificity: {model}": every["specificity"],
                        f"net benefit: {model}": 100 * decision.net_benefit(flag, need, t),
                        f"net benefit, battle: {model}": 100 * decision.net_benefit(flag[battle], need[battle], t)})
        return row

    return decision.across_seeds(one)


def spread_range(column: str, places: int = 3, scale: float = 1.0) -> str:
    s = scale * spread()[column]
    return f"from {s.min():.{places}f} to {s.max():.{places}f} across {s.size} seeds"


def spread_words(differences, places: int = 1, unit: str = " points", lower: str = "lower",
                 higher: str = "higher") -> str:
    return decision.spread_words(np.asarray(differences, float), unit, places, lower, higher)


# ------------------------------------------------------------------------------------------------ by hand

@lru_cache(maxsize=1)
def by_hand() -> dict:
    """Twenty calibration casualties and ten new ones, the first of the calibration sample and of the evaluation
    sample; the MPTT-24's probability for each, the threshold and the ten sets (mechanism)."""
    cal_obs, cal_truth = calibration_sample()
    new_obs, new_truth = baseline.generator_sample()

    def table(observed, truth, n):
        o, need = observed.head(n), truth["needs_lsi"].head(n).to_numpy(bool)
        priority = baseline.triage_table(o, baseline.DEFAULT_READING)["priority"].to_numpy()
        p = rule_probability(o)
        return pd.DataFrame({"id": o["id"].to_numpy(), "stream": o["stream"].to_numpy(), "priority": priority,
                             "probability of need": p, "needs an intervention": need})

    cal = table(cal_obs, cal_truth, HAND_CAL)
    cal["score of the true label"] = nonconformity(cal["probability of need"], cal["needs an intervention"])
    q = threshold_from(cal["score of the true label"])
    new = table(new_obs, new_truth, HAND_NEW)
    has_need, has_no = holds(new["probability of need"], q)
    new["set"] = [set_words(a, b) for a, b in zip(has_need, has_no)]
    new["holds the truth"] = np.where(new["needs an intervention"], has_need, has_no)
    return {"calibration": cal, "rank": rank_for(HAND_CAL), "threshold": q, "new": new}


# ------------------------------------------------------------------------------------------------ the envelopes

@lru_cache(maxsize=None)
def envelopes(level: float = LEVEL, n: int = 100) -> dict:
    """A hundred battle casualties of the evaluation sample, with lens 04's tree's probability and each one's set at
    the level given (mechanism). Battle casualties are used because the walk-through follows them."""
    observed, truth = baseline.generator_sample()
    battle = np.flatnonzero((observed["stream"] == "battle").to_numpy())[:n]
    o = observed.iloc[battle]
    need = truth["needs_lsi"].to_numpy(bool)[battle]
    p = tree_probability(o)
    q = threshold(TREE, level)
    has_need, has_no = holds(p, q)
    covered = np.where(need, has_need, has_no)
    return {"probability": p, "need": need, "has_need": has_need, "has_no": has_no, "threshold": q,
            "both": int((has_need & has_no).sum()), "empty": int((~has_need & ~has_no).sum()),
            "missed": int((~covered).sum()), "n": int(len(battle)),
            "lower": 1 - q, "upper": q}


@lru_cache(maxsize=None)
def level_table() -> pd.DataFrame:
    """Each model at several levels on the evaluation sample: threshold, coverage, share holding both labels, every
    stream and among the battle casualties alone (mechanism)."""
    rows = []
    for level in LEVELS:
        r = diagnosis_results("pre_hospital", level)
        for model in MODELS:
            rows.append({"level": level, "model": model, "threshold": r[model]["threshold"],
                         "coverage": r[model]["all"]["coverage"], "coverage, battle": r[model]["battle"]["coverage"],
                         "holding both labels": r[model]["all"]["both"]})
    return pd.DataFrame(rows)


# ------------------------------------------------------------------------------------------------ failures

@lru_cache(maxsize=None)
def shift_curve(level: float = LEVEL) -> pd.DataFrame:
    """Coverage of each model's sets, calibrated on the default mix, on 100,000 casualties (seed 42) drawn from mixes
    with a rising share of battle casualties, the rest split between disease and non-battle injury as in the default
    mix. Each mix is an assumption (mechanism)."""
    v = generator.load_params()["parameters"]["stream_shares"]["value"]
    other = float(v["disease"]) + float(v["non_battle"])
    rows = []
    for share in BATTLE_SHARES:
        mix = {"battle": share, "disease": (1 - share) * float(v["disease"]) / other,
               "non_battle": (1 - share) * float(v["non_battle"]) / other}
        observed, truth = generator.sample(baseline.EVAL_N, baseline.EVAL_SEED, mix=mix, return_truth=True)
        need = truth["needs_lsi"].to_numpy(bool)
        for model in MODELS:
            m = measure(probability(model, observed), need, threshold(model, level))
            rows.append({"battle share": share, "share in need": float(need.mean()), "model": model,
                         "coverage": m["coverage"], "holding both labels": m["both"]})
    return pd.DataFrame(rows)


@lru_cache(maxsize=1)
def every_label() -> dict:
    """The set that always holds both labels: it covers every casualty and says nothing. Read as a flag it flags every
    casualty, so its net benefit at 0.10 is that of flagging every casualty (mechanism)."""
    observed, truth = baseline.generator_sample()
    need = truth["needs_lsi"].to_numpy(bool)
    t = decision.threshold()
    has_need = has_no = np.ones_like(need)
    flag = has_need
    return {"coverage": float(np.where(need, has_need, has_no).mean()), "both": float((has_need & has_no).mean()),
            "size": 2.0,
            "net benefit": 100 * decision.net_benefit(flag, need, t), "flag every casualty": 100 * decision.flag_all(need, t),
            "sets": {m: diagnosis_results()[m]["all"] for m in MODELS}}


@lru_cache(maxsize=1)
def point_across_join(prior: float = PRIOR) -> dict:
    """Lens 03's belief after a positive scan before hospital (mechanism; scan accuracy from E-16's counts), passed on
    as its mean against a decision at one half, beside its draws."""
    belief = bayesian.belief_after_scan(prior, "pre_hospital", positive=True)
    lo, hi = belief.interval()
    return {"prior": prior, "mean": belief.mean(), "interval": (lo, hi), "draws": belief.draws,
            "above half": belief.prob(lambda d: d > bayesian.EVACUATE_ABOVE),
            "below half": belief.prob(lambda d: d <= bayesian.EVACUATE_ABOVE), "line": bayesian.EVACUATE_ABOVE}


# ------------------------------------------------------------------------------------------------ the joins in treatment

@lru_cache(maxsize=1)
def scan_into_rule(prior: float = PRIOR) -> pd.DataFrame:
    """A test feeding a rule: in each setting, lens 03's belief after a positive scan, which the ABC score counts as
    one item (E-31), and the score's sensitivity and specificity against significant bleeding on the generator's
    battle casualties (mechanism)."""
    rows = []
    for setting in SETTINGS:
        belief = bayesian.belief_after_scan(prior, setting, positive=True)
        lo, hi = belief.interval()
        abc = rules.treatment_results(setting)["abc"]
        rows.append({"setting": SETTING_NAMES[setting], "belief after a positive scan": belief.mean(),
                     "interval low": lo, "interval high": hi, "what the score counts": "one item",
                     "ABC score sensitivity": abc["sensitivity"], "ABC score specificity": abc["specificity"]})
    return pd.DataFrame(rows)


# ------------------------------------------------------------------------------------------------ the scorecard

def _pct(x: float, places: int = 1) -> str:
    return f"{100 * x:.{places}f}%"


METRICS = (("coverage", "coverage, the share whose set holds the true label"),
           ("both", "share of sets holding both labels"),
           ("sensitivity", "sensitivity, flagged where the set holds need"),
           ("specificity", "specificity, flagged where the set holds need"))
TREATMENT_METRICS = (("belief", "mean belief that the casualty bleeds into the abdomen after a positive scan, which "
                                "the ABC score counts as one item"),
                     ("sensitivity", "sensitivity, ABC score 2 or more against significant bleeding"),
                     ("specificity", "specificity, ABC score 2 or more against significant bleeding"))


def diagnosis_metric(name: str, model: str, setting: str) -> str:
    return (f"{name}, prediction sets on the {model} at a level of {LEVEL:.2f}, against need for a life-saving "
            f"intervention, {SETTING_NAMES[setting]}")


def treatment_metric(name: str, setting: str) -> str:
    return f"{name}, battle casualties, {SETTING_NAMES[setting]}"


def _baseline_value(key: str, setting: str) -> float:
    """The MPTT-24 (figure) as a single label: the share it classifies correctly stands beside coverage, and a single
    label never holds both."""
    r = baseline.diagnosis_results(setting)
    if key == "coverage":
        return 1 - r["brier"]
    if key == "both":
        return 0.0
    return r[key]


def seven_axes() -> pd.DataFrame:
    """The scorecard on the seven axes of D-21, with the baseline under both readings (D-24). Axes 1, 2 and 6 are
    computed on the generator (mechanism); 3, 4 and 5 are stated; axis 7 is net benefit at 0.10 (D-26), flagging a
    casualty whose set holds need. Across 20 further samples, each calibrated afresh (lesson 12), the spread is given
    of each model's coverage less the level, its coverage among the battle casualties alone less its coverage on every
    stream, the tree's coverage less the rule's, and each flag's net benefit less the MPTT-24's (figure)."""
    sp = spread()
    pre, inside = diagnosis_results("pre_hospital"), diagnosis_results("in_hospital")
    observed, truth = baseline.generator_sample()
    need = truth["needs_lsi"].to_numpy(bool)
    battle = (observed["stream"] == "battle").to_numpy()
    fig, txt = (baseline.diagnosis_results("pre_hospital", r) for r in baseline.READINGS)
    treat = scan_into_rule()
    battle_obs, battle_truth = rules.battle_sample("pre_hospital")
    bleed = battle_truth["bleeding"].to_numpy(bool)
    activated = (rules.abc_table(battle_obs)["score"] >= rules.ABC_ACTIVATES_AT).to_numpy()
    abc_pre = rules.treatment_results("pre_hospital")["abc"]

    def same_as_rule(model, measure):
        return bool(np.allclose(sp[f"{measure}: {model}"], sp[f"{measure}: figure"], rtol=0, atol=1e-12))

    def disc(model):
        r = pre[model]
        against = ("is identical to the MPTT-24's (figure) on every one of the 20 samples"
                   if same_as_rule(model, "sensitivity") else
                   f"less the MPTT-24's (figure) is "
                   f"{spread_words(100 * (sp[f'sensitivity: {model}'] - sp['sensitivity: figure']))}")
        return (f"sensitivity {_pct(r['all']['sensitivity'])}, specificity {_pct(r['all']['specificity'])}, flagging a "
                f"casualty whose set holds need; coverage {_pct(r['all']['coverage'])} at a level of {_pct(LEVEL, 0)}, "
                f"{_pct(r['all']['both'])} of sets holding both labels; all 100,000 synthetic casualties of the "
                f"military cohort, disease included. Across 20 further samples, each calibrated afresh, coverage runs "
                f"{spread_range(f'coverage: {model}', 1, 100).replace(' across', ' per cent across')}; its sensitivity "
                f"{against}")

    def cal(model):
        r = pre[model]
        return (f"Coverage {_pct(r['all']['coverage'])} against a level of {_pct(LEVEL, 0)} on every stream; among the "
                f"battle casualties alone {_pct(r['battle']['coverage'])}, below the level: across 20 further samples "
                f"their coverage less that on every stream is "
                f"{spread_words(100 * (sp[f'coverage, battle: {model}'] - sp[f'coverage: {model}']))}. Mean set size "
                f"{r['all']['size']:.3f} labels. The model beneath: Brier {r['brier']:.3f}, where lower is better; mean "
                f"probability minus share in need {r['calibration']:+.3f}")

    def rule_disc(r):
        return f"sensitivity {_pct(r['sensitivity'])}, specificity {_pct(r['specificity'])}"

    def rule_cal(r):
        return (f"A single label, right for {_pct(1 - r['brier'])} of casualties (Brier {r['brier']:.3f}, the share "
                f"misclassified, where lower is better); share flagged minus share in need {r['calibration']:+.3f}")

    def nb_rows(model):
        text = decision.decision_value(flags(model, observed), need, battle=battle)
        if same_as_rule(model, "net benefit") and same_as_rule(model, "net benefit, battle"):
            return text + (". Its net benefit is identical to the MPTT-24's (figure) on every one of the 20 further "
                           "samples, on every stream and among the battle casualties alone")
        return (text + ". On every stream, "
                + decision.versus(sp[f"net benefit: {model}"] - sp["net benefit: figure"], "the MPTT-24 (figure)")
                + "; among the battle casualties alone, "
                + decision.versus(sp[f"net benefit, battle: {model}"] - sp["net benefit, battle: figure"],
                                  "the MPTT-24 (figure)"))

    belief = {r["setting"]: r for _, r in treat.iterrows()}
    b_pre, b_in = belief[SETTING_NAMES["pre_hospital"]], belief[SETTING_NAMES["in_hospital"]]
    rows = [
        ("1 Discrimination (mechanism)",
         disc(RULE) + ". The flag is the MPTT-24's Priority 1 itself: only a Priority 1 casualty's set holds need",
         disc(TREE) + f"; its coverage less the rule's is "
         f"{spread_words(100 * (sp[f'coverage: {TREE}'] - sp[f'coverage: {RULE}']))}",
         rule_disc(fig) + ". " + rules.d23_sentence(), rule_disc(txt),
         f"ABC score: {rule_disc(abc_pre)} against significant bleeding, battle casualties, scan before hospital, the "
         f"positive scan behind its item a belief of {_pct(b_pre['belief after a positive scan'])} from a prior of "
         f"{PRIOR:.2f}"),
        ("2 Calibration (mechanism)", cal(RULE), cal(TREE), rule_cal(fig), rule_cal(txt),
         f"The score gives no probability: Brier {baseline.flag_metrics(activated, bleed)['brier']:.3f}, the share "
         f"misclassified, where lower is better"),
        ("3 Uncertainty expressed",
         "A set of one label or two, holding the true label for at least the level on average over casualties like "
         "the calibration ones", "The same, from the tree's probability", "None: a priority", "None: a priority",
         "None: a count of items; the belief behind the scan item is dropped"),
        ("4 What it needed",
         f"The rule, the share in need at each priority from {frequentist.TRAIN_N:,} labelled synthetic "
         f"casualties, and {CAL_N:,} more labelled casualties to calibrate (mechanism)",
         f"The tree, fitted on {frequentist.TRAIN_N:,} labelled synthetic casualties, and {CAL_N:,} more to "
         f"calibrate (mechanism)",
         "Rules only at the point of use (E-08)", "Rules only at the point of use (E-08)",
         "Rules and a scan at the point of use (E-31)"),
        ("5 Readability",
         "A medic reads the MPTT-24 as published, with Priority 1 read as 'need or no need: look again' and Priority 2 "
         "or 3 as 'no need'", "A three-question tree and two cut-offs on its leaf's share: a medic can follow it on a "
         "card", "Six yes-or-no steps, one observation each", "Six yes-or-no steps, one observation each",
         "Four yes-or-no items, counted"),
        ("6 Robustness, setting changed (mechanism)",
         f"Scan in hospital: coverage {_pct(inside[RULE]['all']['coverage'])}, unchanged, because neither model reads "
         f"the scan. Mix changed instead, to {_pct(SHIFTED['battle'], 0)} battle casualties (an assumption): across 20 "
         f"samples coverage runs {spread_range(f'coverage, shifted: {RULE}', 1, 100).replace(' across', ' per cent across')}, "
         f"below the level",
         f"Scan in hospital: coverage {_pct(inside[TREE]['all']['coverage'])}, unchanged for the same reason. Mix "
         f"changed to {_pct(SHIFTED['battle'], 0)} battle casualties: across 20 samples coverage runs "
         f"{spread_range(f'coverage, shifted: {TREE}', 1, 100).replace(' across', ' per cent across')}, below the level",
         "Unchanged", "Unchanged",
         f"Scan in hospital: the belief behind a positive scan is {_pct(b_in['belief after a positive scan'])} against "
         f"{_pct(b_pre['belief after a positive scan'])}, and the score's sensitivity "
         f"{_pct(b_in['ABC score sensitivity'])} against {_pct(b_pre['ABC score sensitivity'])}; the score counts the "
         f"item the same in both"),
        ("7 Decision value", nb_rows(RULE), nb_rows(TREE),
         decision.decision_value(baseline.priority_one(observed, "figure"), need, battle=battle),
         decision.decision_value(baseline.priority_one(observed, "text"), need, battle=battle),
         decision.decision_value(activated, bleed) + ", against significant bleeding, battle casualties, scan before "
                                                      "hospital"),
    ]
    return pd.DataFrame(rows, columns=["axis", f"diagnosis: sets on the {RULE}", f"diagnosis: sets on the {TREE}",
                                       "baseline: MPTT-24, figure (as published)",
                                       "baseline: MPTT-24, text (as validated)",
                                       "treatment: the ABC score fed by the scan (a join)"]).set_index("axis")


# ------------------------------------------------------------------------------------------------ the lens

@dataclass(frozen=True)
class SetAnswer:
    """One casualty's prediction set from each model, with the model's probability and threshold."""

    sets: dict
    probabilities: dict
    thresholds: dict


@dataclass(frozen=True)
class JoinAnswer:
    """The ABC score's items for one casualty, and the belief a positive scan stands for in its setting."""

    items: dict
    score: int
    scan_positive: bool | None
    belief_if_positive: float
    setting: str


class HybridsLens:
    name = LENS_NAME

    def diagnose(self, casualty: Mapping[str, Any]) -> SetAnswer:
        frame = pd.DataFrame([dict(casualty)])
        sets, probs, qs = {}, {}, {}
        for model in MODELS:
            p, q = float(probability(model, frame)[0]), threshold(model)
            a, b = holds(p, q)
            sets[model], probs[model], qs[model] = set_words(bool(a), bool(b)), p, q
        return SetAnswer(sets, probs, qs)

    def treat(self, casualty: Mapping[str, Any]) -> JoinAnswer:
        setting = casualty.get("setting", "pre_hospital")
        scan = casualty.get("scan_free_fluid")
        return JoinAnswer(rules.abc_items(casualty), rules.abc_score(casualty),
                          None if scan is None or pd.isna(scan) else bool(scan),
                          bayesian.belief_after_scan(PRIOR, setting, positive=True).mean(), setting)

    def scorecard(self) -> list[ScorecardRow]:
        rows = []
        for setting in SETTINGS:
            r = diagnosis_results(setting)
            for model in MODELS:
                for key, name in METRICS:
                    rows.append(ScorecardRow(LENS_NAME, "diagnosis", diagnosis_metric(name, model, setting),
                                             round(r[model]["all"][key], 4), round(_baseline_value(key, setting), 4),
                                             "mechanism", "native", "generator"))
        treat = scan_into_rule().set_index("setting")
        for setting in SETTINGS:
            t = treat.loc[SETTING_NAMES[setting]]
            mptt = rules.treatment_results(setting)["mptt24"]
            values = {"belief": (t["belief after a positive scan"], float("nan")),
                      "sensitivity": (t["ABC score sensitivity"], mptt["sensitivity"]),
                      "specificity": (t["ABC score specificity"], mptt["specificity"])}
            for key, name in TREATMENT_METRICS:
                value, base = values[key]
                rows.append(ScorecardRow(LENS_NAME, "treatment", treatment_metric(name, setting), round(float(value), 4),
                                         round(float(base), 4) if not math.isnan(base) else base,
                                         "mechanism", "weak", "generator"))
        return rows


LENS = HybridsLens()
