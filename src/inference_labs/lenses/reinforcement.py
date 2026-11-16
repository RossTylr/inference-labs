"""Lens 09, reinforcement learning (PRD section 6.9; docs/background/09-reinforcement-learning.md).

Learning a sequence of decisions from past records is possible in principle. The hard part is knowing whether the
learned policy is any good without trying it on patients.

    diagnosis   which question to ask next (weak fit). The MPTT-24's five bedside questions the generator records,
                asked in whatever order a policy chooses, stopping when a further question is not worth its cost. The
                policy solves the Bellman equation on counts from a training sample of the generator, and its flag is
                scored against need for a life-saving intervention beside the MPTT-24
    treatment   sequential resuscitation on a constructed decision process. A policy is learned from the logged
                episodes of a clinicians' policy, its value is estimated from those logs by weighted importance
                sampling, and its true value is then read from the process itself

The constructed process
- It is built here and is labelled constructed wherever it is shown. It is not ICU-Sepsis (E-49), whose figures are
  quoted only as published figures; PRD R-9.1 records which was done. It stands in for sepsis in intensive care,
  which stands in for prolonged casualty care. It says nothing about any patient.
- A patient has a severity from 1 (mildest) to 5 and is given one of three doses at each of up to 8 steps: none,
  moderate or intensive. At each step the patient moves one level milder, stays, moves one level worse or dies. A
  move milder from severity 1 is recovery and ends the episode; so does death. A patient alive after 8 steps counts
  as surviving. The reward is 1 for surviving and 0 for dying, so a policy's value is its share surviving.
- Every number in it is an assumption: the chances of each move, the effect of each dose (a dose cuts the chances of
  worsening and of death at the higher severities and raises them at the lowest, and raises the chance of moving
  milder at severity 3 and above), the starting severities, the clinicians' policy, the number of logged episodes and
  the reading of the response to a dose. The clinicians' policy depends on severity alone and always gives a dose at
  severity 3 and above.
- The response to a dose is read after the dose and filed against the step at which the dose was given. It reads 1
  when the patient stayed or moved milder, read right nine times in ten, and 0 when no dose was given.

How the lens learns and estimates
- The learner counts, in the logs, where each dose at each severity led, ignores any dose given fewer than 5 times at
  that severity, and solves the Bellman equation on those counts over the 8 steps.
- The clinicians' policy is estimated from the logs as the share of each dose given at each severity.
- Weighted importance sampling gives each logged episode a weight: the product, over its steps, of the chance the
  evaluated policy gives the dose that was given, over the estimated chance the clinicians gave it. The estimate is
  the weighted share surviving. The effective sample size is the square of the sum of the weights over the sum of
  their squares (E-119 asks how large it is).
- A policy's true value is computed from the process's own tables. Running the process forward gives the same value
  to within sampling error.

Every result here is a mechanism on synthetic data, not evidence (D-8).
"""
from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache
from typing import Any, Mapping

import numpy as np
import pandas as pd

from inference_labs import baseline, generator
from inference_labs.interface import ScorecardRow
from inference_labs.lenses import decision, frequentist, rules, stochastic

NAME = "Reinforcement learning"
NO_BASELINE = float("nan")          # the MPTT-24 states no treatment policy
SETTINGS = baseline.SETTINGS
SETTING_NAMES = baseline.SETTING_NAMES
EVAL_N, EVAL_SEED = baseline.EVAL_N, baseline.EVAL_SEED      # 100,000 synthetic casualties, seed 42
TRAIN_N, TRAIN_SEED = frequentist.TRAIN_N, frequentist.TRAIN_SEED   # the training sample lens 02 fits on
SEEDS = decision.SEEDS              # further samples behind every spread, seeds 43 onward
CONSTRUCTED = "constructed decision process"


def _pct(x: float, places: int = 1) -> str:
    return f"{100 * x:.{places}f}%"


def spread_words(differences, places: int = 3, unit: str = "") -> str:
    """A difference with its spread across seeds: a tie where the spread covers no difference (lesson 12)."""
    return decision.spread_words(differences, unit, places, "lower", "higher")


# ================================================================================================ by hand

TOY_STATES = ("critical", "unwell", "recovered", "dead")
TOY_ACTIONS = ("wait", "treat")
TOY_STEPS = 2
# The four-state, two-action world of the by-hand case, constructed. Recovered and dead end the episode; a patient
# alive at the end of the steps counts as surviving, as in the constructed process.
TOY = {
    "critical": {"wait": {"critical": 1 / 2, "dead": 1 / 2},
                 "treat": {"unwell": 1 / 2, "critical": 1 / 4, "dead": 1 / 4}},
    "unwell": {"wait": {"recovered": 1 / 2, "unwell": 1 / 4, "critical": 1 / 4},
               "treat": {"recovered": 1 / 2, "unwell": 1 / 4, "dead": 1 / 4}},
}
TOY_END = {"recovered": 1.0, "dead": 0.0}


def toy_values(steps: int = TOY_STEPS) -> pd.DataFrame:
    """The Bellman equation worked backwards on the four-state world: for each number of steps left and each state in
    play, the value of each action, the best action and the state's value."""
    value = {s: 1.0 for s in TOY}                 # no steps left: alive counts as surviving
    rows = []
    for left in range(1, steps + 1):
        new = {}
        for s, actions in TOY.items():
            q = {a: sum(p * TOY_END.get(nxt, value.get(nxt, 0.0)) for nxt, p in moves.items())
                 for a, moves in actions.items()}
            best = max(TOY_ACTIONS, key=lambda a: (q[a], -TOY_ACTIONS.index(a)))
            new[s] = q[best]
            rows.append({"steps left": left, "state": s, **{f"value if {a}": q[a] for a in TOY_ACTIONS},
                         "best": best, "value": q[best]})
        value = new
    return pd.DataFrame(rows)


# ================================================================================================ diagnosis

QUESTIONS = ("catastrophic haemorrhage", "walking", "conscious level", "respiratory rate 12 to 23",
             "heart rate below 100")
ANSWERS = (("no", "yes"), ("no", "yes"), ("alert", "responds to voice", "responds to pain or unresponsive"),
           ("no", "yes"), ("no", "yes"))
LEVELS = tuple(len(a) for a in ANSWERS)
UNKNOWN = -1
QUESTION_COST = 0.01                # assumption: one question costs a hundredth of a false alarm
COSTS = decision.DEFAULT_COSTS      # assumption, lens 10's default: a miss weighed nine times a false alarm
FLAG, NO_FLAG = "flag", "do not flag"


def answers(observed: pd.DataFrame) -> np.ndarray:
    """Each casualty's answer to the five questions, as codes: 0 for no or alert, 1 for yes or voice, 2 for pain or
    unresponsive. The generator records no breathing check, so the MPTT-24's breathing step is not among them."""
    avpu = observed["avpu"].to_numpy(object)
    rr = observed["respiratory_rate"].to_numpy(float)
    return np.column_stack([
        observed["catastrophic_haemorrhage"].to_numpy(int),
        observed["walking"].to_numpy(int),
        np.where(avpu == "A", 0, np.where(avpu == "V", 1, 2)),
        ((rr >= baseline.RR_FROM) & (rr <= baseline.RR_TO)).astype(int),
        (observed["heart_rate"].to_numpy(float) < baseline.HR_BELOW).astype(int),
    ])


@lru_cache(maxsize=1)
def answer_counts() -> np.ndarray:
    """Counts of the training sample's casualties by their five answers and by need for a life-saving intervention:
    100,000 synthetic casualties, seed 7, every stream, the sample lens 02's score is fitted on."""
    observed, truth = generator.sample(TRAIN_N, TRAIN_SEED, return_truth=True)
    counts = np.zeros(LEVELS + (2,))
    np.add.at(counts, tuple(answers(observed).T) + (truth["needs_lsi"].to_numpy(int),), 1)
    return counts


def _known(state: tuple) -> tuple:
    return tuple(slice(None) if v == UNKNOWN else v for v in state)


def share_in_need(state: tuple) -> float:
    """The share in need among the training casualties who gave the answers known so far."""
    m = answer_counts()[_known(state)].reshape(-1, 2).sum(0)
    return float(m[1] / m.sum())


def stop_value(p: float, costs: Mapping[str, float] = COSTS) -> tuple[float, str]:
    """Stop and decide: flag if the share in need is at or above the threshold the costs set, at full precision."""
    if p >= decision.threshold(costs):
        return -costs["false alarm"] * (1 - p), FLAG
    return -costs["miss"] * p, NO_FLAG


@lru_cache(maxsize=None)
def question_policy(cost: float = QUESTION_COST) -> dict:
    """The Bellman equation over every state of knowledge the training sample holds: for each set of answers known so
    far that some training casualty gave, the value of the best
    action and the action, which is to ask one of the questions not yet asked, or to stop and flag or not flag. The
    value of asking is minus the question's cost plus the expected value of the state the answer leads to; the value
    of stopping is minus the expected cost of the decision. A tie goes to stopping, then to the MPTT-24's order."""
    counts = answer_counts()
    policy: dict[tuple, tuple[float, Any]] = {}

    def solve(state: tuple) -> float:
        if state in policy:
            return policy[state][0]
        best = stop_value(share_in_need(state))
        for q, v in enumerate(state):
            if v != UNKNOWN:
                continue
            m = counts[_known(state)]
            unknown = [j for j, x in enumerate(state) if x == UNKNOWN]
            dist = np.moveaxis(m, unknown.index(q), 0).reshape(LEVELS[q], -1).sum(1)
            value = -cost
            for level in range(LEVELS[q]):
                if dist[level]:
                    nxt = state[:q] + (level,) + state[q + 1:]
                    value += dist[level] / dist.sum() * solve(nxt)
            if value > best[0] + 1e-12:
                best = (value, q)
        policy[state] = best
        return best[0]

    solve((UNKNOWN,) * len(QUESTIONS))
    return policy


@dataclass(frozen=True)
class Route:
    """The questions asked, in order, with the answers; the decision; and the share in need among the training
    casualties who gave those answers."""

    asked: tuple
    decision: str
    share: float

    @property
    def questions(self) -> int:
        return len(self.asked)

    def words(self) -> str:
        steps = "; ".join(f"{q}: {a}" for q, a in self.asked) or "no question asked"
        return f"{steps}; then {self.decision} ({self.share:.3f} in need among training casualties with these answers)"


def route(codes, cost: float = QUESTION_COST) -> Route:
    """One casualty through the policy: ask, read the answer, ask again, until the policy stops. An answer no training
    casualty gave at that point ends the route there, decided on the answers before it."""
    policy = question_policy(cost)
    state = [UNKNOWN] * len(QUESTIONS)
    asked = []
    while True:
        _, action = policy[tuple(state)]
        if action in (FLAG, NO_FLAG):
            return Route(tuple(asked), action, share_in_need(tuple(state)))
        nxt = state[:action] + [int(codes[action])] + state[action + 1:]
        if tuple(nxt) not in policy:
            p = share_in_need(tuple(state))
            return Route(tuple(asked), stop_value(p)[1], p)
        state = nxt
        asked.append((QUESTIONS[action], ANSWERS[action][int(codes[action])]))


def _combinations() -> np.ndarray:
    return np.array(list(np.ndindex(*LEVELS)))


@lru_cache(maxsize=None)
def route_table(cost: float = QUESTION_COST) -> pd.DataFrame:
    """Every combination of the five answers, with the route the policy takes for it."""
    rows = []
    for codes in _combinations():
        r = route(codes, cost)
        rows.append({"codes": tuple(int(c) for c in codes), "questions asked": r.questions,
                     "route": " > ".join(f"{q}: {a}" for q, a in r.asked) or "none", "decision": r.decision,
                     "share in need": r.share})
    return pd.DataFrame(rows)


def policy_output(observed: pd.DataFrame, cost: float = QUESTION_COST) -> dict:
    """For each casualty: the share in need where the policy stopped (its probability), its flag and the number of
    questions it asked."""
    table = route_table(cost)
    idx = np.ravel_multi_index(answers(observed).T, LEVELS)
    return {"probability": table["share in need"].to_numpy(float)[idx],
            "flag": (table["decision"] == FLAG).to_numpy()[idx],
            "questions": table["questions asked"].to_numpy(int)[idx]}


@lru_cache(maxsize=None)
def question_tree(cost: float = QUESTION_COST) -> pd.DataFrame:
    """The policy's distinct routes, each with the number of training casualties who take it, the share of them in
    need and the decision: the policy written out as a tree."""
    table = route_table(cost)
    counts = answer_counts().reshape(-1, 2)
    table = table.assign(casualties=counts.sum(1).astype(int), in_need=counts[:, 1].astype(int))
    tree = table.groupby(["route", "decision"], sort=False)[["casualties", "in_need"]].sum().reset_index()
    tree = tree[tree["casualties"] > 0].copy()
    tree["share in need"] = tree["in_need"] / tree["casualties"]
    return tree.drop(columns="in_need").sort_values("casualties", ascending=False).reset_index(drop=True)


def rule_questions(observed: pd.DataFrame, reading: str = baseline.DEFAULT_READING) -> np.ndarray:
    """How many of the five questions the MPTT-24 asks before a casualty leaves: the step it leaves at, with the
    breathing check, which the generator takes as yes for everyone, not counted."""
    step = baseline.triage_table(observed, reading)["step"].to_numpy(int)
    return step - (step > 3)


POLICY, FIGURE, TEXT = "question policy", "MPTT-24, figure (as published)", "MPTT-24, text (as validated)"


def _flag_measures(flag: np.ndarray, p: np.ndarray, need: np.ndarray) -> dict:
    t = decision.threshold()
    return {"sensitivity": float(flag[need].mean()), "specificity": float((~flag[~need]).mean()),
            "brier": float(np.mean((p - need) ** 2)), "calibration": float(p.mean() - need.mean()),
            "net benefit": 100 * decision.net_benefit(flag, need, t)}


def _methods(observed: pd.DataFrame, cost: float = QUESTION_COST) -> dict:
    out = policy_output(observed, cost)
    fig, txt = baseline.priority_one(observed, "figure"), baseline.priority_one(observed, "text")
    return {POLICY: (out["flag"], out["probability"], out["questions"]),
            FIGURE: (fig, fig.astype(float), rule_questions(observed, "figure")),
            TEXT: (txt, txt.astype(float), rule_questions(observed, "text"))}


def _measured(observed: pd.DataFrame, truth: pd.DataFrame, cost: float = QUESTION_COST) -> dict:
    need = truth["needs_lsi"].to_numpy(bool)
    battle = (observed["stream"] == "battle").to_numpy()
    out = {}
    for name, (flag, p, asked) in _methods(observed, cost).items():
        out[name] = {**_flag_measures(flag, p, need), "questions": float(asked.mean())}
        out[f"{name}, battle"] = {**_flag_measures(flag[battle], p[battle], need[battle]),
                                  "questions": float(asked[battle].mean())}
    return out


@lru_cache(maxsize=None)
def diagnosis_results(setting: str = "pre_hospital", cost: float = QUESTION_COST) -> dict:
    """The policy and both readings of the MPTT-24 on the evaluation sample: 100,000 synthetic casualties of the
    military cohort, seed 42, every stream, against need for a life-saving intervention, with the battle casualties
    alone beside them (mechanism). A rule gives no probability, so its Brier score is the share misclassified."""
    observed, truth = baseline.generator_sample(setting)
    out = policy_output(observed, cost)
    return {"measures": _measured(observed, truth, cost), "casualties": len(observed),
            "in need": int(truth["needs_lsi"].sum()), "probability": out["probability"], "flag": out["flag"],
            "questions": out["questions"], "need": truth["needs_lsi"].to_numpy(bool),
            "battle": (observed["stream"] == "battle").to_numpy(),
            "figure flag": baseline.priority_one(observed, "figure"),
            "text flag": baseline.priority_one(observed, "text"),
            "figure questions": rule_questions(observed, "figure")}


@lru_cache(maxsize=None)
def diagnosis_spread(cost: float = QUESTION_COST) -> pd.DataFrame:
    """Every measure of the policy and of both readings of the rule on 20 further samples of 100,000 synthetic
    casualties of the military cohort, seeds 43 onward, every stream and battle casualties alone (mechanism)."""
    def one(seed: int) -> dict:
        observed, truth = generator.sample(EVAL_N, seed, return_truth=True)
        return {f"{key}: {name}": v for name, m in _measured(observed, truth, cost).items() for key, v in m.items()}

    return decision.across_seeds(one)


def less(spread: pd.DataFrame, measure: str, other: str = FIGURE, group: str = "") -> np.ndarray:
    """The policy's measure less another method's, on each further sample."""
    return (spread[f"{measure}: {POLICY}{group}"] - spread[f"{measure}: {other}{group}"]).to_numpy()


COST_GRID = (0.0, 0.005, 0.01, 0.02, 0.05, 0.1, 0.2)


@lru_cache(maxsize=None)
def cost_curve(costs: tuple = COST_GRID) -> pd.DataFrame:
    """The policy's questions asked and net benefit at 0.10 as the cost of a question changes, on the evaluation
    sample (mechanism)."""
    rows = []
    for c in costs:
        m = diagnosis_results("pre_hospital", c)["measures"][POLICY]
        rows.append({"question cost": c, "questions asked": m["questions"], "net benefit": m["net benefit"],
                     "sensitivity": m["sensitivity"], "specificity": m["specificity"],
                     "first question": QUESTIONS[question_policy(c)[(UNKNOWN,) * len(QUESTIONS)][1]]
                     if isinstance(question_policy(c)[(UNKNOWN,) * len(QUESTIONS)][1], int) else "none"})
    return pd.DataFrame(rows).set_index("question cost")


# ================================================================================================ the constructed process

SEVERITIES = (1, 2, 3, 4, 5)
S = len(SEVERITIES)
STEPS = 8
DOSES = ("none", "moderate", "intensive")
A = len(DOSES)
DEAD, RECOVERED = S, S + 1          # the two ends, after the five severities
# Every number below is an assumption of the constructed process (severity 1 first).
BETTER = (0.35, 0.25, 0.18, 0.12, 0.08)       # chance per step of moving one level milder; from 1, recovery
WORSE = (0.10, 0.14, 0.18, 0.22, 0.00)        # chance per step of moving one level worse
DEATH = (0.00, 0.01, 0.03, 0.08, 0.22)        # chance per step of dying
CUT = {"moderate": (-0.10, 0.10, 0.25, 0.30, 0.30),      # relative cut in the chances of worsening and of dying;
       "intensive": (-0.40, -0.05, 0.30, 0.45, 0.50)}    # a negative cut raises them
GAIN = {"moderate": (1.0, 1.0, 1.1, 1.1, 1.1),           # multiplies the chance of moving milder
        "intensive": (1.0, 1.0, 1.2, 1.2, 1.2)}
START = (0.15, 0.30, 0.30, 0.18, 0.07)        # share starting at each severity
CLINICIANS = ((0.85, 0.12, 0.03), (0.55, 0.35, 0.10), (0.00, 0.60, 0.40), (0.00, 0.40, 0.60), (0.00, 0.25, 0.75))
READ_RIGHT = 0.9                    # the response to a dose is read right nine times in ten
LOGGED = 5_000                      # logged episodes in one set of logs
MIN_RECORDS = 5                     # a dose given fewer times than this at a severity is not considered
RUN_N = 100_000                     # episodes when the process is run forward
RUN_SEED = 1_000                    # added to a seed for the run that reveals a true value


@lru_cache(maxsize=1)
def transitions() -> np.ndarray:
    """The process's own table: for each severity and dose, the chance of each next severity, of death and of
    recovery."""
    P = np.zeros((S, A, S + 2))
    for s in range(S):
        for a, dose in enumerate(DOSES):
            cut = CUT[dose][s] if dose in CUT else 0.0
            gain = GAIN[dose][s] if dose in GAIN else 1.0
            better, worse, death = BETTER[s] * gain, WORSE[s] * (1 - cut), DEATH[s] * (1 - cut)
            P[s, a, RECOVERED if s == 0 else s - 1] += better
            P[s, a, s + 1 if s < S - 1 else DEAD] += worse
            P[s, a, DEAD] += death
            P[s, a, s] += 1 - better - worse - death
    return P


def process_table() -> pd.DataFrame:
    """The constructed process's numbers, every one an assumption: by severity, the chance per step of each move with
    no dose, the cut each dose makes in the chances of worsening and of dying (a negative cut raises them), the gain in
    the chance of moving milder, the share starting there and the clinicians' chance of each dose."""
    rows = {}
    for i, sev in enumerate(SEVERITIES):
        rows[sev] = {"milder": BETTER[i], "worse": WORSE[i], "dies": DEATH[i],
                     **{f"cut, {d}": CUT[d][i] for d in CUT}, **{f"gain, {d}": GAIN[d][i] for d in GAIN},
                     "starts here": START[i], **{f"clinicians give {d}": CLINICIANS[i][a] for a, d in enumerate(DOSES)}}
    return pd.DataFrame.from_dict(rows, orient="index").rename_axis("severity")


def _good(s: int, nxt: np.ndarray) -> np.ndarray:
    """Stayed or moved milder, recovery included; death and worsening are not."""
    nxt = np.asarray(nxt)
    return (nxt == RECOVERED) | ((nxt < S) & (nxt <= s))


# ------------------------------------------------------------------------------------------------ policies
# A policy is an array of shape (steps, severities, 2, doses): the chance of each dose at each step and severity,
# given the response the policy reads (0 or 1). A policy that does not read the response is the same in both.

def as_policy(table) -> np.ndarray:
    """A table of doses, by step and severity (and, optionally, by the response read), as a policy."""
    table = np.asarray(table, int)
    if table.ndim == 2:
        table = np.repeat(table[:, :, None], 2, axis=2)
    return np.eye(A)[table]


def fixed(chances) -> np.ndarray:
    """A policy giving the same chances of each dose at every step, by severity."""
    return np.broadcast_to(np.asarray(chances, float)[None, :, None, :], (STEPS, S, 2, A)).copy()


def do_nothing() -> np.ndarray:
    return as_policy(np.zeros((STEPS, S), int))


def clinicians() -> np.ndarray:
    return fixed(CLINICIANS)


def random_policy() -> np.ndarray:
    return fixed(np.full((S, A), 1 / A))


@lru_cache(maxsize=1)
def best() -> tuple[np.ndarray, float]:
    """The best policy, from the process's own tables: the Bellman equation solved exactly. Only a constructed
    process has these tables."""
    P = transitions()
    V = np.ones(S)
    table = np.zeros((STEPS, S), int)
    for t in range(STEPS - 1, -1, -1):
        Q = P[:, :, :S] @ V + P[:, :, RECOVERED]
        table[t], V = Q.argmax(1), Q.max(1)
    return table, float(np.asarray(START) @ V)


def _response_chance(s: int, a: int) -> np.ndarray:
    """Chance the response reads 1, for each next state, after dose a at severity s."""
    if a == 0:
        return np.zeros(S + 2)
    good = _good(s, np.arange(S + 2))
    return np.where(good, READ_RIGHT, 1 - READ_RIGHT)


def value_grid(policy: np.ndarray) -> np.ndarray:
    """The true value of being at each severity at each step under a policy, with no response yet read (the start)
    or the previous response read, from the process's own tables: shape (steps + 1, severities, 2)."""
    P = transitions()
    V = np.ones((STEPS + 1, S, 2))
    for t in range(STEPS - 1, -1, -1):
        for s in range(S):
            for l in range(2):
                total = 0.0
                for a in range(A):
                    chance = policy[t, s, l, a]
                    if chance == 0:
                        continue
                    r = _response_chance(s, a)
                    cont = r[:S] * V[t + 1, :, 1] + (1 - r[:S]) * V[t + 1, :, 0]
                    total += chance * (P[s, a, :S] @ cont + P[s, a, RECOVERED])
                V[t, s, l] = total
    return V


def true_value(policy: np.ndarray) -> float:
    """A policy's share surviving, from the process's own tables, every episode starting with no response read."""
    return float(np.asarray(START) @ value_grid(policy)[0, :, 0])


def run(policy: np.ndarray, n: int = RUN_N, seed: int = EVAL_SEED, start=START) -> tuple[pd.DataFrame, np.ndarray]:
    """Run the process forward for n episodes under a policy: the record of every step and each episode's reward. At
    each step the policy reads the previous response, which is what is known before the dose. `start` is the share
    starting at each severity."""
    rng = np.random.default_rng(seed)
    P = transitions()
    s = rng.choice(S, n, p=np.asarray(start, float))
    done = np.zeros(n, bool)
    reward = np.zeros(n)
    previous = np.zeros(n, int)
    rows = []
    for t in range(STEPS):
        idx = np.flatnonzero(~done)
        if idx.size == 0:
            break
        chances = policy[t, s[idx], previous[idx]]
        a = (rng.random(idx.size)[:, None] > chances.cumsum(1)).sum(1)
        a = np.minimum(a, A - 1)
        nxt = (rng.random(idx.size)[:, None] > P[s[idx], a].cumsum(1)).sum(1)
        nxt = np.minimum(nxt, S + 1)
        good = (nxt == RECOVERED) | ((nxt < S) & (nxt <= s[idx]))
        read = rng.random(idx.size) < READ_RIGHT
        response = np.where(a > 0, np.where(read, good, ~good), False).astype(int)
        rows.append(pd.DataFrame({"episode": idx, "step": t, "severity": s[idx], "dose": a, "next": nxt,
                                  "response": response, "previous response": previous[idx]}))
        previous[idx] = response
        end = (nxt == DEAD) | (nxt == RECOVERED)
        reward[idx[nxt == RECOVERED]] = 1.0
        done[idx[end]] = True
        s[idx[~end]] = nxt[~end]
    reward[~done] = 1.0
    return pd.concat(rows, ignore_index=True), reward


def readable(record: pd.DataFrame) -> pd.DataFrame:
    """A record with severities numbered 1 to 5, doses named, and the next state named where it is an end."""
    ends = {DEAD: "died", RECOVERED: "recovered"}
    return pd.DataFrame({
        "episode": record["episode"], "step": record["step"] + 1,
        "severity": [SEVERITIES[s] for s in record["severity"]], "dose": [DOSES[a] for a in record["dose"]],
        "next": [ends.get(int(x), str(SEVERITIES[int(x)]) if int(x) < S else "") for x in record["next"]],
        "response filed with the dose": record["response"]}, index=record.index)


@lru_cache(maxsize=2 * SEEDS + 4)
def logs(seed: int = EVAL_SEED, n: int = LOGGED) -> tuple[pd.DataFrame, np.ndarray]:
    """One set of logged episodes under the clinicians' policy: the record a learner is given."""
    return run(clinicians(), n, seed)


def estimated_clinicians(record: pd.DataFrame) -> np.ndarray:
    """The clinicians' policy estimated from the logs: the share of each dose given at each severity."""
    counts = np.zeros((S, A))
    np.add.at(counts, (record["severity"].to_numpy(), record["dose"].to_numpy()), 1)
    return counts / np.maximum(counts.sum(1, keepdims=True), 1)


# ------------------------------------------------------------------------------------------------ estimating from logs

@dataclass(frozen=True)
class Estimate:
    """A value estimated from logs by weighted importance sampling."""

    value: float
    ess: float                  # effective sample size
    counted: int                # logged episodes with a weight above zero
    episodes: int
    weights: np.ndarray

    def words(self) -> str:
        return (f"{self.value:.3f}, from {self.counted:,} of {self.episodes:,} logged episodes with any weight, an "
                f"effective sample of {self.ess:.1f}")


def naive_estimate(record: pd.DataFrame, reward: np.ndarray, policy: np.ndarray, reads: str = "previous response"
                   ) -> Estimate:
    """Weighted importance sampling from the logs, with the clinicians' policy estimated from the same logs. `reads`
    is the logged column the policy reads at each step: the previous response, or the response filed at the dose."""
    mu = estimated_clinicians(record)
    s, a = record["severity"].to_numpy(), record["dose"].to_numpy()
    ratio = policy[record["step"].to_numpy(), s, record[reads].to_numpy(), a] / mu[s, a]
    w = np.ones(len(reward))
    np.multiply.at(w, record["episode"].to_numpy(), ratio)
    total = w.sum()
    value = float((w * reward).sum() / total) if total > 0 else float("nan")
    ess = float(total ** 2 / (w ** 2).sum()) if total > 0 else 0.0
    return Estimate(value, ess, int((w > 0).sum()), len(reward), w)


@dataclass(frozen=True)
class Learned:
    """A policy learned from logs: its table of doses, the policy, and the learner's own estimate of its value from
    the counts it learned on."""

    table: np.ndarray
    policy: np.ndarray
    own_estimate: float
    reads_response: bool


def learn(record: pd.DataFrame, reward: np.ndarray, reads_response: bool = False) -> Learned:
    """Learn from logged episodes, not from free interaction: count where each dose at each severity led, set aside
    any dose given fewer than MIN_RECORDS times there, and solve the Bellman equation on the counts over the steps.
    With reads_response, the learner also reads the response filed at each dose, as if it were known before the dose.
    Where no dose is left at a state, the dose the clinicians gave most often there is taken."""
    s, a, nxt = record["severity"].to_numpy(), record["dose"].to_numpy(), record["next"].to_numpy()
    first = record[record["step"] == 0]
    start = np.bincount(first["severity"].to_numpy(), minlength=S) / len(first)
    usual = estimated_clinicians(record).argmax(1)
    if not reads_response:
        counts = np.zeros((S, A, S + 2))
        np.add.at(counts, (s, a, nxt), 1)
        n = counts.sum(-1)
        Ph = counts / np.maximum(n, 1)[..., None]
        V = np.ones(S)
        table = np.zeros((STEPS, S), int)
        for t in range(STEPS - 1, -1, -1):
            Q = Ph[:, :, :S] @ V + Ph[:, :, RECOVERED]
            Q[n < MIN_RECORDS] = -np.inf
            table[t] = np.where(np.isfinite(Q).any(1), Q.argmax(1), usual)
            V = np.take_along_axis(np.where(np.isfinite(Q), Q, 0.0), table[t][:, None], 1)[:, 0]
        return Learned(table, as_policy(table), float(start @ V), False)
    r = record["response"].to_numpy()
    counts = np.zeros((S, 2, A, S + 2))
    np.add.at(counts, (s, r, a, nxt), 1)
    n = counts.sum(-1)
    Ph = counts / np.maximum(n, 1)[..., None]
    seen = np.zeros((S, 2))
    np.add.at(seen, (s, r), 1)
    p_response = seen / np.maximum(seen.sum(1, keepdims=True), 1)
    V = np.ones((S, 2))
    table = np.zeros((STEPS, S, 2), int)
    for t in range(STEPS - 1, -1, -1):
        ahead = (p_response * V).sum(1)
        Q = Ph[..., :S] @ ahead + Ph[..., RECOVERED]
        Q[n < MIN_RECORDS] = -np.inf
        table[t] = np.where(np.isfinite(Q).any(-1), Q.argmax(-1), usual[:, None])
        V = np.take_along_axis(np.where(np.isfinite(Q), Q, 0.0), table[t][..., None], -1)[..., 0]
    return Learned(table, as_policy(table), float(start @ (p_response * V).sum(1)), True)


@lru_cache(maxsize=16)
def learned_from(n: int = LOGGED, seed: int = EVAL_SEED) -> Learned:
    """The policy learned from n logged episodes of one seed: the board's control is n."""
    return learn(*logs(seed, n))


POLICIES = ("clinicians", "do nothing", "learned", "learned, reading the response")


@lru_cache(maxsize=2 * SEEDS + 4)
def seed_results(seed: int = EVAL_SEED) -> dict:
    """One set of logs: every policy's naive estimate and true value, and what the learner learned."""
    record, reward = logs(seed)
    learned, leaky = learn(record, reward), learn(record, reward, reads_response=True)
    naive = {"clinicians": naive_estimate(record, reward, fixed(estimated_clinicians(record))),
             "do nothing": naive_estimate(record, reward, do_nothing()),
             "learned": naive_estimate(record, reward, learned.policy),
             "learned, reading the response": naive_estimate(record, reward, leaky.policy, "response")}
    true = {"clinicians": true_value(clinicians()), "do nothing": true_value(do_nothing()),
            "learned": true_value(learned.policy), "learned, reading the response": true_value(leaky.policy)}
    given = record["dose"].to_numpy()
    differs = learned.table[record["step"].to_numpy(), record["severity"].to_numpy()] != given
    return {"naive": naive, "true": true, "learned": learned, "leaky": leaky, "logged survival": float(reward.mean()),
            "departs": float(differs.mean()), "decisions": len(record), "episodes": len(reward)}


@lru_cache(maxsize=1)
def treatment_spread() -> pd.DataFrame:
    """Every policy's naive estimate, effective sample and true value on 20 further sets of logs, seeds 43 onward
    (mechanism)."""
    def one(seed: int) -> dict:
        r = seed_results(seed)
        row = {}
        for name in POLICIES:
            row[f"naive: {name}"] = r["naive"][name].value
            row[f"effective sample: {name}"] = r["naive"][name].ess
            row[f"true: {name}"] = r["true"][name]
        row["own estimate: learned"] = r["learned"].own_estimate
        row["own estimate: learned, reading the response"] = r["leaky"].own_estimate
        row["departs"] = r["departs"]
        return row

    return decision.across_seeds(one)


def reference_values() -> dict:
    """The true value of the clinicians', do-nothing, random and best policies, from the process's own tables."""
    return {"clinicians": true_value(clinicians()), "do nothing": true_value(do_nothing()),
            "random": true_value(random_policy()), "best": best()[1]}


def who_carries(seed: int = EVAL_SEED) -> pd.DataFrame:
    """The reason the do-nothing policy scores well, in its weights: the logged episodes by the worst severity each
    reached while in care, with how many there are, how many carry any weight, the share of the total weight they
    carry, and the share of them surviving."""
    record, reward = logs(seed)
    w = seed_results(seed)["naive"]["do nothing"].weights
    worst = record.groupby("episode")["severity"].max().reindex(range(len(reward))).to_numpy()
    rows = []
    for s in range(S):
        m = worst == s
        rows.append({"worst severity reached": SEVERITIES[s], "episodes": int(m.sum()),
                     "with any weight": int((w[m] > 0).sum()), "share of the weight": float(w[m].sum() / w.sum()),
                     "share surviving": float(reward[m].mean()) if m.any() else float("nan")})
    return pd.DataFrame(rows).set_index("worst severity reached")


def routes(policy: np.ndarray, start: int = 3, n: int = 6, seed: int = EVAL_SEED) -> list[dict]:
    """n patients run forward from one starting severity under a policy: the severities each passed through, the
    doses given and how the episode ended."""
    record, _ = run(policy, n, seed, start=[float(s == start) for s in SEVERITIES])
    out = []
    for e in range(n):
        steps = record[record["episode"] == e].sort_values("step")
        last = int(steps["next"].iloc[-1])
        end = "died" if last == DEAD else "recovered" if last == RECOVERED else "alive at the end"
        out.append({"severities": [SEVERITIES[s] for s in steps["severity"]],
                    "doses": [DOSES[a] for a in steps["dose"]], "end": end})
    return out


def dose_shares(seed: int = EVAL_SEED) -> pd.DataFrame:
    """How far the learned policy departs from the logged care: across the logged decisions, the share of each dose
    given and the share the learned policy would give at the same step and severity."""
    record, _ = logs(seed)
    table = seed_results(seed)["learned"].table
    learned = table[record["step"].to_numpy(), record["severity"].to_numpy()]
    given = record["dose"].to_numpy()
    return pd.DataFrame({"given in the logs": np.bincount(given, minlength=A) / len(given),
                         "learned policy": np.bincount(learned, minlength=A) / len(learned)},
                        index=pd.Index(DOSES, name="dose"))


# ================================================================================================ published figures

# E-120: the learned sepsis policy.
E120 = {"trained": 17_083, "tested": 79_073, "hospitals": 128, "variables": 48, "states": 750, "actions": 25,
        "learned": 84.5, "clinicians": 56.9, "vasopressor recommended": 30, "vasopressor given": 17}
# E-97: CLOVERS.
E97 = {"patients": 1_563, "centres": 60, "restrictive": 14.0, "liberal": 14.9, "difference": (-0.9, -4.4, 2.6),
       "p": 0.61, "less fluid ml": 2_134}
# E-94: hourly cost of delay.
E94 = {"patients": 49_331, "hospitals": 149, "bundle": (1.04, 1.02, 1.05), "antibiotics": (1.04, 1.03, 1.06),
       "bolus": (1.01, 0.99, 1.02)}
# E-49: ICU-Sepsis.
E49 = {"states": 716, "actions": 25, "random": 0.78, "clinician": 0.78, "optimal": 0.88, "dataset": 0.77}


def claim_and_trial() -> pd.DataFrame:
    """The learned policy's claim beside the trial of the same choice and the timing result for fluids, each as its
    register row gives it."""
    d = E97["difference"]
    return pd.DataFrame([
        {"source": "E-120", "what": "a policy learned from records, scored from records",
         "who": f"trained on {E120['trained']:,} admissions from one hospital's database, tested on "
                f"{E120['tested']:,} from {E120['hospitals']} hospitals",
         "result": f"estimated value {E120['learned']} for the learned policy against {E120['clinicians']} for "
                   f"clinicians; vasopressors recommended {E120['vasopressor recommended']}% of the time against "
                   f"{E120['vasopressor given']}% given",
         "how measured": "weighted importance sampling on records; the authors state it needs prospective evaluation"},
        {"source": "E-97", "what": "a trial of two fixed strategies: restrictive against liberal fluid",
         "who": f"{E97['patients']:,} patients, {E97['centres']} US centres",
         "result": f"death by 90 days {E97['restrictive']}% (restrictive) against {E97['liberal']}% (liberal); "
                   f"difference {d[0]} points ({d[1]} to {d[2]}), P=.{str(E97['p'])[2:]}; the restrictive group "
                   f"received a median {E97['less fluid ml']:,} mL less fluid",
         "how measured": "a trial"},
        {"source": "E-94", "what": "time to each treatment",
         "who": f"{E94['patients']:,} patients, {E94['hospitals']} New York hospitals",
         "result": f"odds ratio for death for each hour to antibiotics {E94['antibiotics'][0]} "
                   f"({E94['antibiotics'][1]}-{E94['antibiotics'][2]}); for each hour to the fluid bolus "
                   f"{E94['bolus'][0]} ({E94['bolus'][1]}-{E94['bolus'][2]}), not associated",
         "how measured": "observational"},
    ]).set_index("source")


# ================================================================================================ the lens

@dataclass(frozen=True)
class Advice:
    """The learned policy's dose for one state of the constructed process, with the policy's naive estimate and true
    value. The process is constructed; it is not the casualty."""

    step: int
    severity: int
    dose: str
    state_value: float
    naive: Estimate
    true: float


DIAGNOSIS_METRICS = (("sensitivity", "sensitivity"), ("specificity", "specificity"),
                     ("brier", "Brier score, where lower is better"), ("calibration", "share in need where it stopped "
                                                                          "minus share in need"))


def diagnosis_metric(name: str, setting: str) -> str:
    return (f"{name}, question policy's flag against need for a life-saving intervention, every stream, "
            f"{SETTING_NAMES[setting]}")


class ReinforcementLens:
    """Lens 09 behind the Lens interface (R-0.8, R-9.1)."""

    name = NAME

    def diagnose(self, casualty: Mapping[str, Any]) -> Route:
        """The questions the policy asks this casualty, in its order, and the decision (weak fit)."""
        return route(answers(pd.DataFrame([dict(casualty)]))[0])

    def treat(self, casualty: Mapping[str, Any]) -> Advice:
        """The learned policy's dose at a state of the constructed process, read from `step` and `severity` (by
        default the start, at severity 3). The process stands in for prolonged care; it is not the casualty."""
        step, severity = int(casualty.get("step", 0)), int(casualty.get("severity", 3))
        r = seed_results()
        table = r["learned"].table
        grid = value_grid(r["learned"].policy)
        return Advice(step, severity, DOSES[table[step, severity - 1]], float(grid[step, severity - 1, 0]),
                      r["naive"]["learned"], r["true"]["learned"])

    def scorecard(self) -> list[ScorecardRow]:
        rows = []
        for setting in SETTINGS:
            m = diagnosis_results(setting)["measures"]
            for key, name in DIAGNOSIS_METRICS:
                rows.append(ScorecardRow(NAME, "diagnosis", diagnosis_metric(name, setting), round(m[POLICY][key], 4),
                                         round(m[FIGURE][key], 4), "mechanism", "weak", "generator"))
        r = seed_results()
        where = f"{CONSTRUCTED}, {LOGGED:,} logged episodes, seed {EVAL_SEED}, share surviving"
        rows.append(ScorecardRow(NAME, "treatment", f"true value of the learned policy, {where}",
                                 round(r["true"]["learned"], 4), NO_BASELINE, "mechanism", "native", CONSTRUCTED))
        for name in ("learned", "do nothing", "learned, reading the response"):
            rows.append(ScorecardRow(NAME, "treatment", f"naive estimate less true value: {name}, {where}",
                                     round(r["naive"][name].value - r["true"][name], 4), NO_BASELINE, "mechanism",
                                     "native", CONSTRUCTED))
        return rows


LENS = ReinforcementLens()


# ================================================================================================ seven axes

HOSPITAL = ("The generator's physiology is an assumption, tuned until the rule landed within 0.05 of E-09's accuracy, "
            "which was measured on first recorded hospital respiratory rate and registry GCS, not at the point of "
            "injury")
COST_WORDS = (f"Its decisions rest on two assumptions: a miss weighed {COSTS['miss'] / COSTS['false alarm']:g} times a "
              f"false alarm, and a question costing {QUESTION_COST} of a false alarm")


def seven_axes() -> pd.DataFrame:
    """The scorecard on the seven axes of D-21, with the baseline under both readings (D-24) and axis 7 at 0.10
    (D-26). An axis that does not apply is answered in words."""
    pre = diagnosis_results("pre_hospital")
    m = pre["measures"]
    sp = diagnosis_spread()
    ts = treatment_spread()
    ref = reference_values()
    r = seed_results()
    d23 = rules.d23_sentence()
    tree = question_tree()

    def disc(x):
        return f"sensitivity {_pct(x['sensitivity'])}, specificity {_pct(x['specificity'])}"

    def rule_cal(x):
        gap = x["calibration"]
        return (f"Brier {x['brier']:.3f}, where lower is better; it flags {100 * abs(gap):.1f} points "
                f"{'more' if gap > 0 else 'fewer'} than are in need. A rule gives no probability, so the Brier score "
                f"is the share misclassified")

    def vs(measure, other, group="", places=3, unit=""):
        return spread_words(less(sp, measure, other, group), places, unit)

    def gap(name):
        return spread_words(ts[f"naive: {name}"] - ts[f"true: {name}"], 3)

    battle = m[f"{POLICY}, battle"]
    rows = [
        ("1 Discrimination (mechanism)",
         f"{disc(m[POLICY])} for need for a life-saving intervention, on {pre['casualties']:,} synthetic casualties, "
         f"{pre['in need']:,} in need. Sensitivity less the rule's (figure): {vs('sensitivity', FIGURE, places=3)}; "
         f"specificity less the rule's: {vs('specificity', FIGURE, places=3)}. {COST_WORDS}",
         f"{disc(m[FIGURE])}. {d23} {HOSPITAL}",
         disc(m[TEXT]),
         f"Not a classifier: the learned policy's true share surviving is {r['true']['learned']:.3f} on the logs "
         f"of seed {EVAL_SEED}, from {ts['true: learned'].min():.3f} to {ts['true: learned'].max():.3f} across "
         f"{len(ts)} further sets of logs; the clinicians' policy {ref['clinicians']:.3f}, doing nothing "
         f"{ref['do nothing']:.3f}, the best policy {ref['best']:.3f} ({CONSTRUCTED}). Learned less clinicians: "
         f"{spread_words(ts['true: learned'] - ref['clinicians'], 3)}. The process's record holds everything that "
         f"drives the clinicians' doses and the outcomes, by construction"),
        ("2 Calibration (mechanism)",
         f"Brier {m[POLICY]['brier']:.3f}, where lower is better; share in need where it stopped minus share in need "
         f"{m[POLICY]['calibration']:+.4f}. Its Brier score less the rule's (figure), every stream, is "
         f"{vs('brier', FIGURE)}. Among battle casualties alone this reverses: its Brier score is "
         f"{battle['brier']:.3f} against the rule's {m[FIGURE + ', battle']['brier']:.3f}, and the difference is "
         f"{vs('brier', FIGURE, ', battle')}. Its shares in need are counted on every stream of the training sample; "
         f"among battle casualties they fall {abs(battle['calibration']):.3f} below the share in need, where the "
         f"rule's share flagged falls {abs(m[FIGURE + ', battle']['calibration']):.3f} below it",
         rule_cal(m[FIGURE]), rule_cal(m[TEXT]),
         f"Of the value estimate from logs: naive estimate less true value across {len(ts)} further sets of logs. "
         f"Learned policy: {gap('learned')}. Doing nothing: {gap('do nothing')}. Learned while reading the response "
         f"to each dose: {gap('learned, reading the response')}"),
        ("3 Uncertainty expressed",
         "A share in need where it stops, counted on the training sample; no interval",
         "None: a priority", "None: a priority",
         f"One estimate from one set of logs, with its effective sample size: for the learned policy "
         f"{r['naive']['learned'].ess:.1f} of {LOGGED:,} episodes on seed {EVAL_SEED}, from "
         f"{ts['effective sample: learned'].min():.1f} to {ts['effective sample: learned'].max():.1f} across {len(ts)} "
         f"further sets of logs. No interval"),
        ("4 What it needed",
         f"Labelled cases: {TRAIN_N:,} synthetic training casualties with need known; two stated costs, both "
         f"assumptions",
         "Rules only (E-08)", "Rules only (E-08)",
         f"{LOGGED:,} logged episodes of the clinicians' policy, with every dose and the recorded severity; no free "
         f"interaction. The true value needs the process's own tables, which only a constructed process has"),
        ("5 Readability",
         f"A tree of {int((tree['casualties'] > 0).sum())} routes and at most "
         f"{int(route_table()['questions asked'].max())} questions; on average {m[POLICY]['questions']:.2f} questions "
         f"asked against the rule's {m[FIGURE]['questions']:.2f}; the policy's less the rule's is "
         f"{vs('questions', FIGURE, places=2)}. The rule's count leaves out the breathing check",
         "Six yes-or-no steps", "Six yes-or-no steps",
         f"A table of one dose for each of {STEPS} steps and {S} severities: the board"),
        ("6 Robustness, setting changed (mechanism)",
         "Unchanged: the questions do not include the scan, and the generator draws the same signs in either setting",
         "Unchanged: the setting changes only the scan", "Unchanged: the setting changes only the scan",
         "Does not apply: the constructed process has no care setting"),
        ("7 Decision value",
         stochastic.axis7(pre["flag"], pre["need"]) + ", against need for a life-saving intervention. Net benefit less "
         f"the rule's (figure) is {vs('net benefit', FIGURE, places=1, unit=' per 100')}; the policy is built to "
         f"minimise the expected cost that net benefit at 0.10 scores, so this is its own measure",
         stochastic.axis7(pre["figure flag"], pre["need"]) + ", against need",
         stochastic.axis7(pre["text flag"], pre["need"]) + ", against need",
         "Does not apply: net benefit scores a flag, not a policy. A policy's decision value is its share surviving, "
         "in axis 1"),
    ]
    return pd.DataFrame(rows, columns=["axis", "diagnosis: which question next (weak fit)",
                                       "baseline: MPTT-24, figure (as published)",
                                       "baseline: MPTT-24, text (as validated)",
                                       f"treatment: learned policy, {CONSTRUCTED}"]).set_index("axis")


# ================================================================================================ app page 1

def panel(record: Mapping[str, Any]) -> dict:
    """The reinforcement learning panel for one synthetic casualty on app page 1. Every number is formatted here, so
    the page shows only what the library computed (gate G-8)."""
    r = LENS.diagnose(record)
    fig = baseline.triage(record, "figure")
    txt = baseline.triage(record, "text")
    res = seed_results()
    learned, nothing = res["naive"]["learned"], res["naive"]["do nothing"]
    ts = treatment_spread()
    nothing_spread = spread_words(ts["naive: do nothing"] - ts["naive: clinicians"], 3)
    asked = "; ".join(f"{q}: {a}" for q, a in r.asked) or "no question"
    return {
        "heading": "Reinforcement learning panel: which question next, and a policy learned from logs",
        "route": (f"Questions asked by the policy, in its order: {asked}. It stops and decides: {r.decision}. Of the "
                  f"training casualties with these answers, {r.share:.3f} needed a life-saving intervention, "
                  f"{decision.against_threshold(r.share, decision.threshold(), 3, show=False, name='the threshold the costs set')} "
                  f"(mechanism, weak fit). {COST_WORDS}."),
        "rule": (f"MPTT-24 for this casualty: {fig.priority} under the published figure, leaving at step {fig.step}; "
                 f"{txt.priority} under the text, leaving at step {txt.step}."),
        "treatment": (f"The treatment case runs on a {CONSTRUCTED}, not on this casualty (mechanism). From "
                      f"{LOGGED:,} logged episodes of the clinicians' policy, the learned policy's estimate is "
                      f"{learned.value:.3f}, on an effective sample of {learned.ess:.1f}, and its true share surviving "
                      f"is {res['true']['learned']:.3f}. Doing nothing is estimated at {nothing.value:.3f} from the same "
                      f"logs, against the clinicians' {res['naive']['clinicians'].value:.3f}; its true share surviving "
                      f"is {res['true']['do nothing']:.3f}, against the clinicians' {res['true']['clinicians']:.3f}. "
                      f"Estimated from logs, doing nothing less the clinicians is {nothing_spread}."),
    }


def page_panel(walk: Any) -> dict:
    """The reinforcement learning panel on app page 1 for one walk-through casualty, given lens 03's Walkthrough
    (D-27)."""
    return panel(walk.record)
