"""Lens 10, decision theory (PRD section 6.5; background/10-decision-theory.md).

A probability is not a decision. To act, each kind of mistake needs a cost, and the costs are a judgement that
someone owns. Every cost here is a named control with a default that is an assumption; no source states an exchange
rate between a miss and a false alarm, and none is implied.

    diagnosis   lens 02's probability that a casualty needs a life-saving intervention, turned into a decision at the
                threshold the costs set: flag when the probability is at least false-alarm cost over the sum of the
                two costs. Judged by expected cost and by net benefit (E-93) against the MPTT-24.
    treatment   one aircraft and two casualties. Each casualty's expected chance of dying from bleeding by the time
                they reach surgery is lens 03's belief that they are bleeding into the abdomen, times the generator's
                chance that a casualty bleeding into the trunk dies from bleeding by that time. The order with fewer
                expected deaths flies first.

Assumptions
- The default costs (a miss weighed nine times a false alarm), the cost of each casualty flagged beyond capacity, the
  flight time and the holding times are choices made here, for the reader to change.
- Surgery on arrival is taken to stop a bleeding death. The chance of dying before arrival is the generator's, without
  tranexamic acid, for a casualty still alive when the decision is made: the truncal site's chance of a bleeding death,
  set so that deaths from bleeding split by site as in E-41, applied to the share of bleeding deaths falling between
  the decision and arrival under the hazard fitted to the three hourly rates of E-85. E-85 was measured from hospital
  admission at civilian centres; running it from injury, for battle casualties, is an assumption, as in the generator.
- A comparison of expected deaths is reported with its spread across 20 seeds; where the spread covers no difference,
  it is called a tie.
- The aircraft takes the casualty to surgery. A scan in hospital is done on arrival, after the flight, so in that
  setting the choice of who flies first rests on the belief after triage.
- Under-triage is 1 minus sensitivity and over-triage 1 minus the positive predictive value, the MPTT-24 authors'
  definitions (E-12), wherever this module computes them.

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
from inference_labs.lenses import frequentist, rules, trees

NAME = "Decision theory"
DEFAULT_COSTS = {"miss": 9.0, "false alarm": 1.0}       # assumption: the reader's to set
OVERFLOW_COST = 3.0           # assumption: cost of each casualty flagged beyond capacity, per 100 casualties
FLIGHT_MIN = 30.0             # assumption: flight time to surgery
HOLD_MIN = 30.0               # assumption: the extra time held here in the panel's example
THRESHOLDS = np.round(np.arange(0.01, 0.61, 0.01), 2)
CAPACITIES = (60, 50, 40, 30, 25, 20, 15, 10)            # flagged casualties that can be handled, per 100
PAIRS, PAIR_SEED = 2_000, 10
SEEDS = 20                    # seeds behind every spread of a comparison of expected deaths
SETTINGS = baseline.SETTINGS
SETTING_NAMES = baseline.SETTING_NAMES


def threshold(costs: Mapping[str, float] = DEFAULT_COSTS) -> float:
    """The probability above which acting costs less, in expectation, than not acting."""
    return float(costs["false alarm"] / (costs["false alarm"] + costs["miss"]))


def against_threshold(p: float, t: float, places: int = 3, show: bool = True, name: str = "the threshold") -> str:
    """A probability against a threshold: compared at full precision, both shown to the same number of places. Where
    the two print alike, the text says so and states which side the probability falls. With show=False the
    probability itself is left to the caller; `name` says whose threshold it is."""
    shown, line = f"{p:.{places}f}", f"{t:.{places}f}"
    side = "at or above" if p >= t else "below"
    if shown == line:
        return f"at {name} of {line} to {places} decimal places, and {side} it at full precision"
    return f"{shown + ', ' if show else ''}{side} {name} of {line}"


def expected_cost(flag: np.ndarray, need: np.ndarray, costs: Mapping[str, float] = DEFAULT_COSTS) -> float:
    """Cost per 100 casualties: misses times their cost plus false alarms times theirs."""
    flag, need = np.asarray(flag, bool), np.asarray(need, bool)
    misses, alarms = (~flag & need).sum(), (flag & ~need).sum()
    return float(100 * (costs["miss"] * misses + costs["false alarm"] * alarms) / need.size)


def net_benefit(flag: np.ndarray, need: np.ndarray, t: float) -> float:
    """Net benefit at threshold probability t (E-93), computed here as true positives less false positives weighted by
    t over 1 - t, per casualty."""
    flag, need = np.asarray(flag, bool), np.asarray(need, bool)
    tp, fp = (flag & need).sum(), (flag & ~need).sum()
    return float((tp - fp * t / (1 - t)) / need.size)


def treat_all(need: np.ndarray, t: float) -> float:
    q = float(np.mean(need))
    return q - (1 - q) * t / (1 - t)


# ------------------------------------------------------------------------------------------------ diagnosis

@lru_cache(maxsize=None)
def diagnosis_inputs(setting: str = "pre_hospital") -> dict:
    """The military cohort's 100,000 evaluation casualties: need, the rule's two flags and three probabilities."""
    observed, truth = baseline.generator_sample(setting)
    p = trees.probabilities(observed)
    return {"need": truth["needs_lsi"].to_numpy(bool),
            "probabilities": {"logistic score (lens 02)": frequentist.probability(observed),
                              "single tree (lens 04)": p["single tree"], "forest (lens 04)": p["forest"]},
            "flags": {"MPTT-24, figure (as published)": baseline.priority_one(observed, "figure"),
                      "MPTT-24, text (as validated)": baseline.priority_one(observed, "text")}}


@lru_cache(maxsize=None)
def net_benefit_table() -> pd.DataFrame:
    """Net benefit per 100 casualties across thresholds for each method, treat all and treat none (mechanism)."""
    d = diagnosis_inputs()
    rows = {}
    for name, p in d["probabilities"].items():
        rows[name] = [100 * net_benefit(p >= t, d["need"], t) for t in THRESHOLDS]
    for name, flag in d["flags"].items():
        rows[name] = [100 * net_benefit(flag, d["need"], t) for t in THRESHOLDS]
    rows["treat all"] = [100 * treat_all(d["need"], t) for t in THRESHOLDS]
    rows["treat none"] = [0.0] * len(THRESHOLDS)
    return pd.DataFrame(rows, index=pd.Index(THRESHOLDS, name="threshold"))


def cost_curve(costs: Mapping[str, float] = DEFAULT_COSTS, method: str = "logistic score (lens 02)") -> pd.Series:
    d = diagnosis_inputs()
    p = d["probabilities"][method]
    return pd.Series([expected_cost(p >= t, d["need"], costs) for t in THRESHOLDS],
                     index=pd.Index(THRESHOLDS, name="threshold"), name="cost per 100")


def by_hand(ids: tuple[int, ...], cut_offs: tuple[float, ...] = (0.1, 0.3, 0.5),
            costs: Mapping[str, float] = DEFAULT_COSTS) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Ten casualties with lens 02's probability, and the total cost of flagging at each cut-off."""
    observed, truth = baseline.generator_sample()
    m = observed["id"].isin(ids).to_numpy()
    p = frequentist.probability(observed[m])
    need = truth["needs_lsi"].to_numpy(bool)[m]
    table = pd.DataFrame({"id": observed.loc[m, "id"].to_numpy(), "probability": p.round(3), "needs": need})
    totals = []
    for c in cut_offs:
        flag = p >= c
        misses, alarms = int((~flag & need).sum()), int((flag & ~need).sum())
        totals.append({"cut-off": c, "misses": misses, "false alarms": alarms,
                       "total cost": costs["miss"] * misses + costs["false alarm"] * alarms})
    return table, pd.DataFrame(totals).set_index("cut-off")


def under_over(flag: np.ndarray, need: np.ndarray) -> tuple[float, float]:
    """Under-triage as 1 minus sensitivity and over-triage as 1 minus the positive predictive value (E-12)."""
    flag, need = np.asarray(flag, bool), np.asarray(need, bool)
    return float(1 - flag[need].mean()), float(1 - need[flag].mean())


def sieve_over_triage() -> float:
    """The Military Sieve's over-triage in the military registry, calculated here from its published sensitivity and
    specificity (E-10) and the registry's share in Priority 1 (E-09), with E-12's definition."""
    s = rules.PUBLISHED["Military Sieve, military"]
    q = rules.PUBLISHED["MPTT-24, military"].prevalence
    ppv = s.sensitivity * q / (s.sensitivity * q + (1 - s.specificity) * (1 - q))
    return float(1 - ppv)


def operating_points(costs: Mapping[str, float] = DEFAULT_COSTS) -> pd.DataFrame:
    """Under-triage and over-triage for each published point, and the generator's points (mechanism)."""
    mil, civ = rules.PUBLISHED["MPTT-24, military"], rules.PUBLISHED["MPTT-24, civilian"]
    sieve = rules.PUBLISHED["Military Sieve, military"]
    d = diagnosis_inputs()
    rows = [
        ("MPTT-24, military registry", 1 - mil.sensitivity, 1 - mil.ppv, "E-09, E-12", "1 minus PPV (E-12)"),
        ("MPTT-24, civilian registry", 1 - civ.sensitivity, 1 - civ.ppv, "E-09, E-12", "1 minus PPV (E-12)"),
        ("Military Sieve, military registry", 1 - sieve.sensitivity, sieve_over_triage(), "E-09, E-10, E-12",
         "1 minus PPV, calculated here"),
        ("Dutch protocol alone", 0.638, 0.074, "E-88", "not given in the register"),
        ("Dutch practice", 0.216, 0.306, "E-88", "not given in the register"),
    ]
    for name, flag in d["flags"].items():
        u, o = under_over(flag, d["need"])
        rows.append((f"{name}, generator's military cohort", u, o, "mechanism", "1 minus PPV (E-12)"))
    u, o = under_over(d["probabilities"]["logistic score (lens 02)"] >= threshold(costs), d["need"])
    rows.append(("logistic score at the reader's costs, generator's military cohort", u, o, "mechanism",
                 "1 minus PPV (E-12)"))
    return pd.DataFrame(rows, columns=["point", "under-triage", "over-triage", "source", "over-triage defined as"]
                        ).set_index("point")


BENCHMARK = {"under-triage below": 0.05, "over-triage below": 0.50}      # E-87
LONDON = {"scene": 0.64, "ambulance staff and bystanders": 0.82, "mainly advanced prehospital teams": 0.33}   # E-126


@lru_cache(maxsize=None)
def load_shift(costs_key: tuple = tuple(DEFAULT_COSTS.items()), overflow: float = OVERFLOW_COST) -> pd.DataFrame:
    """The best threshold as capacity tightens. Each casualty flagged beyond capacity adds `overflow` to the cost,
    so a false alarm costs more when the system is full. A mechanism demonstration on assumed costs."""
    costs = dict(costs_key)
    d = diagnosis_inputs()
    p, need = d["probabilities"]["logistic score (lens 02)"], d["need"]
    rows = []
    for k in CAPACITIES:
        totals = []
        for t in THRESHOLDS:
            flag = p >= t
            beyond = max(0.0, 100 * flag.mean() - k)
            totals.append(expected_cost(flag, need, costs) + overflow * beyond)
        best = int(np.argmin(totals))
        rows.append({"capacity per 100": k, "best threshold": float(THRESHOLDS[best]),
                     "flagged per 100": float(100 * (p >= THRESHOLDS[best]).mean()), "cost per 100": totals[best]})
    return pd.DataFrame(rows).set_index("capacity per 100")


# ------------------------------------------------------------------------------------------------ treatment

BLEEDING_SITE = "truncal"     # in the generator, free fluid in the abdomen is significant bleeding in the trunk


def share_dead_by(minutes) -> np.ndarray:
    """The share of the generator's bleeding deaths that have happened by `minutes` after injury, from its hazard
    fitted to E-85 (measured from admission at civilian centres; run from injury, an assumption)."""
    d = generator.derived()
    return np.interp(np.asarray(minutes, float) / 60, d.grid_h, d.death_time_cdf)


def death_between(now_min, then_min, site: str = BLEEDING_SITE, chance=None) -> np.ndarray:
    """The generator's chance that a casualty bleeding significantly at `site`, alive `now_min` minutes after injury,
    dies from bleeding by `then_min`, without tranexamic acid. It is conditional on being alive when the decision is
    made: the chance of a bleeding death, `chance` or else the site's average over severity, times the share of
    bleeding deaths falling between the two times, over the chance of being alive now."""
    q = generator.derived().site_death_prob[site] if chance is None else np.asarray(chance, float)
    before, by_then = share_dead_by(now_min), share_dead_by(then_min)
    return q * (by_then - before) / (1 - q * before)


def expected_deaths(belief, now_min, then_min) -> Any:
    """The chance that a casualty alive now dies from bleeding into the abdomen before `then_min`, given lens 03's
    belief that they are bleeding there. Being alive now is itself evidence: it lowers both the chance of bleeding
    and, for a bleeder, the chance of dying, so both are conditioned on it."""
    q = generator.derived().site_death_prob[BLEEDING_SITE]
    before, by_then = share_dead_by(now_min), share_dead_by(then_min)
    return belief * q * (by_then - before) / (1 - belief * q * before)


def hold_curve(belief: float, now_min: float, flight_min: float = FLIGHT_MIN,
               holds: tuple[int, ...] = tuple(range(0, 121, 10))) -> pd.Series:
    """Expected bleeding deaths before surgery per 100 such casualties alive now, by minutes held here before the
    flight."""
    return pd.Series([100 * float(expected_deaths(belief, now_min, now_min + h + flight_min)) for h in holds],
                     index=pd.Index(holds, name="minutes held"), name="expected deaths per 100")


@dataclass(frozen=True)
class Casualty:
    label: str
    belief: Any          # lens 03's belief after the scan: an RV or a number
    now_min: float       # minutes since injury at the decision


def aircraft(a: Casualty, b: Casualty, flight_min: float = FLIGHT_MIN) -> dict:
    """One aircraft, two casualties: the second waits a round trip. Expected bleeding deaths for each order."""
    first_a = (expected_deaths(a.belief, a.now_min, a.now_min + flight_min)
               + expected_deaths(b.belief, b.now_min, b.now_min + 3 * flight_min))
    first_b = (expected_deaths(b.belief, b.now_min, b.now_min + flight_min)
               + expected_deaths(a.belief, a.now_min, a.now_min + 3 * flight_min))
    out = {f"{a.label} first": first_a, f"{b.label} first": first_b}
    if hasattr(first_a, "draws"):
        out["chance the first order is better"] = float(np.mean(first_a.draws < first_b.draws))
    return out


@lru_cache(maxsize=None)
def aircraft_policy(setting: str = "pre_hospital", flight_min: float = FLIGHT_MIN, seed: int = PAIR_SEED) -> dict:
    """Random pairs of the evaluation sample's battle casualties. Three ways to choose who flies first, scored by the
    expected bleeding deaths, before surgery, of those truly bleeding into the abdomen and alive at the decision, per
    100 pairs (mechanism). A scan in hospital comes after the flight, so in that setting the belief is the one after
    triage."""
    from inference_labs.lenses import bayesian

    observed, truth = rules.battle_sample(setting)
    alive = alive_at_triage(observed, truth)
    observed, truth = observed[alive].reset_index(drop=True), truth[alive].reset_index(drop=True)
    seen = observed if setting == "pre_hospital" else observed.assign(scan_free_fluid=pd.NA)
    belief = bayesian.beliefs(seen, bayesian.default_prior())
    bleeding = truth["free_fluid"].to_numpy(bool)
    now = observed["t_phec_min"].to_numpy(float)
    urgent = baseline.priority_one(observed, "figure")
    rng = np.random.default_rng(seed)
    i, j = rng.choice(len(observed), (2, PAIRS))
    keep = i != j
    i, j = i[keep], j[keep]

    def die(k, wait):
        return death_between(now[k], now[k] + wait)

    def deaths(first, second):
        return bleeding[first] * die(first, flight_min) + bleeding[second] * die(second, 3 * flight_min)

    def expected(k, wait):
        return expected_deaths(belief[k], now[k], now[k] + wait)

    by_belief = (expected(i, flight_min) + expected(j, 3 * flight_min) <=
                 expected(j, flight_min) + expected(i, 3 * flight_min))
    by_rule = np.where(urgent[i] == urgent[j], now[i] >= now[j], urgent[i])
    by_chance = rng.random(i.size) < 0.5
    result = {}
    for name, a_first in (("belief and clock", by_belief), ("MPTT-24 priority, then the longer wait", by_rule),
                          ("chance", by_chance)):
        d = np.where(a_first, deaths(i, j), deaths(j, i))
        result[name] = float(100 * d.mean())
    best = np.minimum(deaths(i, j), deaths(j, i))
    result["knowing who is bleeding"] = float(100 * best.mean())
    result["pairs"] = int(i.size)
    return result


@lru_cache(maxsize=None)
def aircraft_spread(setting: str = "pre_hospital") -> pd.DataFrame:
    """The four ways of choosing, each scored on SEEDS different draws of random pairs (mechanism)."""
    rows = {seed: {k: v for k, v in aircraft_policy(setting, seed=seed).items() if k != "pairs"}
            for seed in range(PAIR_SEED, PAIR_SEED + SEEDS)}
    return pd.DataFrame.from_dict(rows, orient="index").rename_axis("pair seed")


def spread_words(differences, unit: str = "") -> str:
    """A difference reported with its spread across seeds: a tie where the spread covers no difference."""
    d = np.asarray(differences, float)
    lo, hi = float(d.min()), float(d.max())
    span = f"from {lo:+.2f} to {hi:+.2f}{unit} across {d.size} seeds"
    if lo <= 0 <= hi:
        return f"a tie: no detectable difference (the difference runs {span})"
    return f"{'fewer' if hi < 0 else 'more'}: the difference runs {span}"


def aircraft_summary(setting: str = "pre_hospital") -> dict:
    """Mean expected bleeding deaths per 100 pairs for each way of choosing, and the belief-and-clock order against
    the MPTT-24's priority with its spread across seeds."""
    table = aircraft_spread(setting)
    diff = table["belief and clock"] - table["MPTT-24 priority, then the longer wait"]
    return {"mean": table.mean().to_dict(), "against the rule": spread_words(diff), "seeds": len(table),
            "pairs": aircraft_policy(setting)["pairs"]}


# ------------------------------------------------------------------------------------------------ the failure

@lru_cache(maxsize=None)
def torso_failure(setting: str = "pre_hospital", costs_key: tuple = tuple(DEFAULT_COSTS.items())) -> dict:
    """The treatment tree's probability of significant bleeding on the evaluation sample's battle casualties alive at
    triage, cut where
    overall accuracy is highest and where the cost is lowest once each missed bleeder is weighed by their chance, alive
    at triage, of a bleeding death after it. Misses and the expected deaths among them, by site (mechanism)."""
    costs = dict(costs_key)
    observed, truth = rules.battle_sample(setting)
    alive = alive_at_triage(observed, truth)
    observed, truth = observed[alive].reset_index(drop=True), truth[alive].reset_index(drop=True)
    p = trees.treatment_tree(setting).predict_proba(trees.tx_matrix(observed))[:, 1]
    bleed = truth["bleeding"].to_numpy(bool)
    lethal = lethal_after_triage(observed, truth)
    site = truth["site"].to_numpy(object)
    accuracy = [float(((p >= t) == bleed).mean()) for t in THRESHOLDS]
    weight = lethal / lethal[bleed].mean()
    weighted = [float(costs["miss"] * (weight * (~(p >= t) & bleed)).sum() + costs["false alarm"] * ((p >= t) & ~bleed).sum())
                for t in THRESHOLDS]
    out = {}
    for name, t in (("highest accuracy", float(THRESHOLDS[int(np.argmax(accuracy))])),
                    ("lowest cost, misses weighed by lethality", float(THRESHOLDS[int(np.argmin(weighted))]))):
        flag = p >= t
        rows = []
        for s in ("truncal", "junctional", "extremity"):
            m = bleed & (site == s)
            rows.append({"site": s, "bleeding": int(m.sum()), "missed": int((m & ~flag).sum()),
                         "expected deaths among the missed": float(lethal[m & ~flag].sum())})
        out[name] = {"threshold": t, "accuracy": float((flag == bleed).mean()),
                     "false alarms": int((flag & ~bleed).sum()), "by site": pd.DataFrame(rows).set_index("site")}
    return out


def alive_at_triage(observed: pd.DataFrame, truth: pd.DataFrame) -> np.ndarray:
    """False for a casualty whose bleeding death without tranexamic acid, in the generator, falls at or before the
    triage time; those casualties are not there to be triaged or flown."""
    died = truth["died_if_untreated"].to_numpy(bool)
    return ~(died & (60 * truth["t_death_potential_h"].to_numpy(float) <= observed["t_phec_min"].to_numpy(float)))


def lethal_after_triage(observed: pd.DataFrame, truth: pd.DataFrame) -> np.ndarray:
    """Each casualty's chance, alive at triage, of dying from bleeding after it without tranexamic acid: the
    generator's own chance of a bleeding death for them, conditioned on being alive at the triage time."""
    chance = np.nan_to_num(truth["p_death_untreated"].to_numpy(float))
    return death_between(observed["t_phec_min"].to_numpy(float), np.inf, chance=chance)


def torso_spread(setting: str = "pre_hospital") -> pd.DataFrame:
    """Expected deaths among the missed truncal bleeders at the two cuts of torso_failure, on SEEDS further samples of
    100,000 synthetic casualties (seeds 43 onward), battle casualties alive at triage only (mechanism)."""
    cuts = {name: r["threshold"] for name, r in torso_failure(setting).items()}
    tree = trees.treatment_tree(setting)
    rows = {}
    for seed in range(baseline.EVAL_SEED + 1, baseline.EVAL_SEED + 1 + SEEDS):
        observed, truth = generator.sample(baseline.EVAL_N, seed, setting=setting, return_truth=True)
        keep = (observed["stream"] == "battle").to_numpy() & alive_at_triage(observed, truth)
        observed, truth = observed[keep].reset_index(drop=True), truth[keep].reset_index(drop=True)
        p = tree.predict_proba(trees.tx_matrix(observed))[:, 1]
        truncal = truth["bleeding"].to_numpy(bool) & (truth["site"].to_numpy(object) == "truncal")
        lethal = lethal_after_triage(observed, truth)
        rows[seed] = {name: float(lethal[truncal & (p < t)].sum()) for name, t in cuts.items()}
    return pd.DataFrame.from_dict(rows, orient="index").rename_axis("sample seed")


# ------------------------------------------------------------------------------------------------ axis 7

def _worse(nb: float, all_: float, flags_all: bool) -> str:
    if flags_all:
        return " (it flags every casualty at this threshold, so it scores exactly as treating all)"
    return (" (worse than treating none)" if nb < 0 else " (below treating all)" if nb < all_ - 1e-9 else
            " (no better than treating all)" if nb <= all_ + 1e-9 else "")


def _nb_text(nb: float, all_: float, t: float, costs: Mapping[str, float], flags_all: bool = False) -> str:
    return (f"Net benefit {100 * nb:.1f} per 100 at a threshold of {t:.2f}{_worse(nb, all_, flags_all)}, with a miss "
            f"weighed {costs['miss'] / costs['false alarm']:g} times a false alarm (an assumption); treat all "
            f"{100 * all_:.1f}, treat none 0 (mechanism)")


def decision_value(flag_or_p: np.ndarray, target: np.ndarray, costs: Mapping[str, float] = DEFAULT_COSTS,
                   battle: np.ndarray | None = None) -> str:
    """Axis 7 of D-21 for one lens's output: net benefit at 0.10 for every lens (D-26), the threshold the default
    costs set. Given `battle`, the battle casualties alone are reported too, since there the comparison reverses."""
    t = threshold(costs)
    arr = np.asarray(flag_or_p)
    flag = arr if arr.dtype == bool else arr >= t
    target = np.asarray(target, bool)
    text = _nb_text(net_benefit(flag, target, t), treat_all(target, t), t, costs, bool(flag.all()))
    if battle is not None:
        b = np.asarray(battle, bool)
        nb, all_ = net_benefit(flag[b], target[b], t), treat_all(target[b], t)
        text += (f". Battle casualties alone, where a share of {target[b].mean():.3f} need it against a threshold of "
                 f"{t:.3f}: "
                 f"net benefit {100 * nb:.1f}{_worse(nb, all_, bool(flag[b].all()))}, treat all {100 * all_:.1f}")
    return text


@lru_cache(maxsize=None)
def battle_reversal() -> pd.DataFrame:
    """Net benefit per 100 at the cost threshold for every method, on all the military cohort's 100,000 synthetic
    casualties and on its battle casualties alone (mechanism)."""
    observed, _ = baseline.generator_sample()
    battle = (observed["stream"] == "battle").to_numpy()
    d, t = diagnosis_inputs(), threshold()
    flags = {**{k: p >= t for k, p in d["probabilities"].items()}, **d["flags"]}
    rows = {}
    for name, flag in flags.items():
        rows[name] = {"every stream": 100 * net_benefit(flag, d["need"], t),
                      "battle casualties alone": 100 * net_benefit(flag[battle], d["need"][battle], t)}
    rows["treat all"] = {"every stream": 100 * treat_all(d["need"], t),
                         "battle casualties alone": 100 * treat_all(d["need"][battle], t)}
    return pd.DataFrame.from_dict(rows, orient="index")


def unflagged_need() -> pd.Series:
    """Among the military cohort's battle casualties, the share needing a life-saving intervention among those each
    method does not flag at the cost threshold (mechanism). Flagging pays wherever this share exceeds the threshold."""
    observed, _ = baseline.generator_sample()
    battle = (observed["stream"] == "battle").to_numpy()
    d, t = diagnosis_inputs(), threshold()
    flags = {**{k: p >= t for k, p in d["probabilities"].items()}, **d["flags"]}
    return pd.Series({name: float(d["need"][battle & ~flag].mean()) for name, flag in flags.items()},
                     name="share in need among the battle casualties not flagged")


def battle_share_in_need() -> dict:
    """The share needing a life-saving intervention, every stream and battle casualties alone (mechanism)."""
    observed, _ = baseline.generator_sample()
    battle = (observed["stream"] == "battle").to_numpy()
    need = diagnosis_inputs()["need"]
    return {"every stream": float(need.mean()), "battle casualties alone": float(need[battle].mean())}


def bayesian_decision_value(setting: str) -> dict:
    """Axis 7 for lens 03: the belief after the scan, and the MPTT-24's Priority 1, against bleeding into the abdomen
    on the evaluation sample's battle casualties."""
    from inference_labs.lenses import bayesian

    observed, truth = rules.battle_sample(setting)
    target = truth["free_fluid"].to_numpy(bool)
    return {"lens": decision_value(bayesian.beliefs(observed, bayesian.default_prior()), target),
            "baseline": decision_value(baseline.priority_one(observed, "figure"), target)}


# ------------------------------------------------------------------------------------------------ the lens

@dataclass(frozen=True)
class Decision:
    probability: float
    threshold: float
    act: bool


class DecisionLens:
    """The lens behind the Lens interface (R-0.8, R-5.1)."""

    name = NAME

    def __init__(self, costs: Mapping[str, float] = DEFAULT_COSTS) -> None:
        self.costs = dict(costs)

    def diagnose(self, casualty: Mapping[str, Any]) -> Decision:
        p, t = frequentist.probability_one(casualty), threshold(self.costs)
        return Decision(p, t, p >= t)

    def treat(self, pair: tuple[Casualty, Casualty]) -> dict:
        return aircraft(*pair)

    def scorecard(self) -> list[ScorecardRow]:
        t = threshold(self.costs)
        rows = []
        for setting in SETTINGS:
            d = diagnosis_inputs(setting)
            flag = d["probabilities"]["logistic score (lens 02)"] >= t
            rule = d["flags"]["MPTT-24, figure (as published)"]
            for name, f in (("sensitivity", lambda x: float(x[d["need"]].mean())),
                            ("specificity", lambda x: float((~x[~d["need"]]).mean())),
                            ("expected cost per 100", lambda x: expected_cost(x, d["need"], self.costs)),
                            ("net benefit per 100", lambda x: 100 * net_benefit(x, d["need"], t))):
                rows.append(ScorecardRow(NAME, "diagnosis", f"{name}, lens 02's score at the cost threshold {t:.2f} "
                                         f"against need for a life-saving intervention, {SETTING_NAMES[setting]}",
                                         round(f(flag), 4), round(f(rule), 4), "mechanism", "weak", "generator"))
        for setting in SETTINGS:
            r = aircraft_summary(setting)
            after = "" if setting == "pre_hospital" else ", belief after triage as the scan comes after the flight"
            rows.append(ScorecardRow(NAME, "treatment", "expected deaths before surgery from bleeding into the abdomen "
                                     "per 100 pairs, one aircraft, belief and "
                                     f"clock against MPTT-24 priority, mean over {r['seeds']} draws of pairs, battle "
                                     f"casualties alive at the decision, assumed flight time, "
                                     f"{SETTING_NAMES[setting]}{after}; {r['against the rule']}",
                                     round(r["mean"]["belief and clock"], 4),
                                     round(r["mean"]["MPTT-24 priority, then the longer wait"], 4),
                                     "mechanism", "native", "generator"))
        return rows


LENS = DecisionLens()


def _pct(x: float) -> str:
    return f"{100 * x:.1f}%"


def seven_axes(costs: Mapping[str, float] = DEFAULT_COSTS) -> pd.DataFrame:
    """The scorecard on the seven axes of D-21, with the baseline under both readings (D-24)."""
    t = threshold(costs)
    d, d_in = diagnosis_inputs("pre_hospital"), diagnosis_inputs("in_hospital")
    p = d["probabilities"]["logistic score (lens 02)"]
    flag = p >= t
    fig, txt = d["flags"]["MPTT-24, figure (as published)"], d["flags"]["MPTT-24, text (as validated)"]
    pre, inside = aircraft_summary("pre_hospital"), aircraft_summary("in_hospital")
    m_pre, m_in = pre["mean"], inside["mean"]
    rule = "MPTT-24 priority, then the longer wait"
    need = d["need"]
    battle = (baseline.generator_sample()[0]["stream"] == "battle").to_numpy()

    def disc(f):
        return f"sensitivity {_pct(f[need].mean())}, specificity {_pct((~f[~need]).mean())}"

    def cost(f):
        return f"expected cost {expected_cost(f, need, costs):.1f} per 100 at the stated costs (assumptions)"

    group = "all 100,000 synthetic casualties of the military cohort, disease included"
    rows = [
        ("1 Discrimination (mechanism)", f"{disc(flag)} at the cost threshold {t:.2f}; {group}", disc(fig), disc(txt),
         f"Not a classifier: expected deaths before surgery from bleeding into the abdomen per 100 pairs of battle "
         f"casualties alive at the "
         f"decision, at an assumed flight time, mean over {pre['seeds']} draws of pairs: {m_pre['belief and clock']:.2f}, "
         f"against {m_pre[rule]:.2f} by the MPTT-24's priority, {pre['against the rule']}; {m_pre['chance']:.2f} by "
         f"chance; {m_pre['knowing who is bleeding']:.2f} if it were known who is bleeding; scan before hospital"),
        ("2 Calibration (mechanism)", f"{cost(flag)}; the probability it acts on has calibration "
         f"{frequentist.diagnosis_results('pre_hospital')['calibration']:+.3f}", cost(fig), cost(txt),
         "Not applicable"),
        ("3 Uncertainty expressed", "None in the decision; the costs are stated, not estimated", "None: a priority",
         "None: a priority", "The belief behind each casualty is a distribution (lens 03)"),
        ("4 What it needed", "Lens 02's probability and two stated costs (assumptions)", "Rules only (E-08)",
         "Rules only (E-08)", "Lens 03's belief, the generator's bleeding hazard (fitted to E-85, measured from "
         "admission at civilian centres; applied to battle casualties from injury, an assumption) and a stated flight "
         "time (an assumption)"),
        ("5 Readability", "One comparison: is the probability above the threshold the costs set?",
         "Six yes-or-no steps", "Six yes-or-no steps", "Two sums of two products, compared"),
        ("6 Robustness, setting changed (mechanism)",
         f"Scan in hospital: {disc(d_in['probabilities']['logistic score (lens 02)'] >= t)}, unchanged because in the "
         f"generator the setting changes only the scan", "Unchanged", "Unchanged",
         f"Scan in hospital: the scan comes after the flight, so the choice rests on the belief after triage: "
         f"{m_in['belief and clock']:.2f} against {m_in[rule]:.2f} per 100 pairs, {inside['against the rule']}"),
        ("7 Decision value", decision_value(p, need, costs, battle), decision_value(fig, need, costs, battle),
         decision_value(txt, need, costs, battle), "Expected deaths are the decision value here: see axis 1"),
    ]
    return pd.DataFrame(rows, columns=["axis", "diagnosis: decision on lens 02's score",
                                       "baseline: MPTT-24, figure (as published)",
                                       "baseline: MPTT-24, text (as validated)", "treatment: one aircraft, two casualties"]
                        ).set_index("axis")


# ------------------------------------------------------------------------------------------------ app page 1

@lru_cache(maxsize=None)
def battle_not_acted(costs_key: tuple = tuple(DEFAULT_COSTS.items())) -> tuple[float, float]:
    """Among the military evaluation sample's battle casualties, the only casualties app page 1 shows: the share whose
    lens 02 probability falls below the cost threshold, and the share of those who need an intervention (mechanism)."""
    costs = dict(costs_key)
    observed, truth = baseline.generator_sample()
    battle = (observed["stream"] == "battle").to_numpy()
    below = frequentist.probability(observed)[battle] < threshold(costs)
    need = truth["needs_lsi"].to_numpy(bool)[battle]
    return float(below.mean()), float(need[below].mean())


def panel(record: Mapping[str, Any], line: Mapping[str, Any]) -> dict:
    """The decision panel for one synthetic casualty on app page 1, given lens 03's belief line for them. Every number
    is formatted here, so the page shows only what the library computed (gate G-8). The costs are the defaults, each
    an assumption. A scan in hospital comes after the flight, so in that setting the belief used is the one after
    triage."""
    decision = LENS.diagnose(record)
    before = record["setting"] == "pre_hospital"
    belief = float(line["evacuation" if before else "triage"].mean())
    now = float(record["t_phec_min"])
    go = float(expected_deaths(belief, now, now + FLIGHT_MIN))
    wait = float(expected_deaths(belief, now, now + HOLD_MIN + FLIGHT_MIN))
    which = ("after the scan" if before else "after triage, since the scan in hospital comes after the flight")
    mean_p, share = frequentist.battle_calibration()
    below, below_need = battle_not_acted()
    cheaper = DEFAULT_COSTS["miss"] * below_need > DEFAULT_COSTS["false alarm"] * (1 - below_need)
    return {
        "heading": "Decision panel: a probability becomes a decision only once each mistake has a cost",
        "costs": (f"With a miss weighed {DEFAULT_COSTS['miss'] / DEFAULT_COSTS['false alarm']:g} times a false alarm "
                  f"(an assumption: no source states an exchange rate between a miss and a false alarm), the "
                  f"threshold is {decision.threshold:.3f}. Lens 02's probability for this casualty is "
                  f"{against_threshold(decision.probability, decision.threshold)}, so at these costs the decision is "
                  f"{'to act' if decision.act else 'not to act'} (mechanism). The probability was fitted on the whole "
                  f"military cohort, disease admissions included. On the battle casualties among that cohort's 100,000 "
                  f"synthetic casualties, the kind this page shows, it averages {mean_p:.3f} where {_pct(share)} "
                  f"need an intervention, so for a battle casualty it runs low and the decision errs towards not acting: {_pct(below)} of them are told not to act, and "
                  f"{_pct(below_need)} of those need an intervention"
                  + (", so at these costs acting on all of them would cost less (mechanism)." if cheaper else
                     " (mechanism).")),
        "evacuation": (f"Belief that this casualty is bleeding into the abdomen, {which}: {_pct(belief)} (lens 03). "
                       f"Alive now and flown now, {FLIGHT_MIN:.0f} minutes to surgery, the expected chance of dying "
                       f"from bleeding into the abdomen before arrival is {_pct(go)}; held {HOLD_MIN:.0f} minutes "
                       f"more, {_pct(wait)}. Being alive now counts as evidence on both the belief and the chance of "
                       f"dying. The times are assumptions, and surgery on arrival is taken to stop a "
                       f"bleeding death. The chance of a bleeding death is the generator's for bleeding into the "
                       f"trunk, without tranexamic acid, with its level set so that bleeding deaths split by site as in "
                       f"E-41 (lethal haemorrhage among the US battlefield deaths before a treatment facility judged "
                       f"potentially survivable, E-40), and its timing from a hazard fitted to E-85 (4,064 haemorrhaging patients in "
                       f"five prospective studies at civilian centres, timed from hospital admission). Applying it to "
                       f"a battle casualty, and from injury, is an assumption (mechanism)."),
    }


def page_panel(walk: Any) -> dict:
    """The decision panel on app page 1 for one walk-through casualty, given lens 03's Walkthrough (D-27): every
    number already formatted, so the page shows only what the library computed (gate G-8)."""
    return panel(walk.record, walk.line)
