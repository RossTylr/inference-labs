"""Lens 04, decision trees (PRD section 6.4; background/04-decision-trees.md).

A tree asks the single question that splits the casualties most cleanly, then asks again inside each part. One tree
is readable and changes with the sample; many trees averaged are steadier and cannot be read.

    diagnosis   a single tree of depth three and a random forest, predicting need for a life-saving intervention from
                the same four of the MPTT-24's signs as lens 02's score (walking, conscious level, respiratory rate,
                heart rate), fitted on lens 02's training sample and scored on the evaluation sample. Each operating
                threshold is set where the model's specificity on the training sample is closest to the MPTT-24's
                under the figure reading.
    treatment   who gets blood first: a tree on the ABC score's bedside items (penetrating mechanism, a positive scan,
                systolic pressure, heart rate) predicting significant bleeding in battle casualties, the stand-in
                for transfusion used in lens 01, beside the ABC score.

Assumptions
- Conscious level enters as an ordered number: alert 0, voice 1, pain 2, unresponsive 3.
- The tree's depth, its smallest leaf, the forest's size and the resampling sizes are choices made here.
- Small arms injuries count as penetrating and significant bleeding stands in for the need for transfusion, as in
  lens 01.
- The variable recorded after the decision in the failure case is constructed here from the generator's truth. It is
  not a generator variable and stands for nothing measured.

Every result computed here on the generator is a mechanism, not evidence (D-8).
"""
from __future__ import annotations

import math
from dataclasses import dataclass
from functools import lru_cache
from typing import Any, Mapping

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score
from sklearn.tree import DecisionTreeClassifier

from inference_labs import baseline, generator
from inference_labs.interface import ScorecardRow
from inference_labs.lenses import frequentist, rules

NAME = "Decision trees"
FEATURES = ("walking", "conscious level", "respiratory rate", "heart rate")
AVPU_ORDER = {"A": 0, "V": 1, "P": 2, "U": 3}
TREE_DEPTH, TREE_LEAF = 3, 200
FOREST_TREES, FOREST_LEAF, MODEL_SEED = 100, 50, 0
SMALL_N, RESAMPLES, RESAMPLE_SEED = 300, 20, 20
U_DEPTH, U_LEAF = 5, 100
TX_FEATURES = ("penetrating mechanism", "positive scan", "systolic pressure", "heart rate")
SETTINGS = baseline.SETTINGS
SETTING_NAMES = baseline.SETTING_NAMES
LEAK_SEED = 99


# ------------------------------------------------------------------------------------------------ the signs

def sign_matrix(observed: pd.DataFrame) -> np.ndarray:
    return np.column_stack([observed["walking"].to_numpy(float),
                            observed["avpu"].map(AVPU_ORDER).to_numpy(float),
                            observed["respiratory_rate"].to_numpy(float),
                            observed["heart_rate"].to_numpy(float)])


@lru_cache(maxsize=1)
def training() -> tuple[pd.DataFrame, pd.DataFrame]:
    """Lens 02's training sample: the same 100,000 synthetic casualties, so the models are compared fairly."""
    return generator.sample(frequentist.TRAIN_N, frequentist.TRAIN_SEED, return_truth=True)


def _matched_threshold(p: np.ndarray, need: np.ndarray, specificity: float) -> float:
    """The threshold whose specificity on the training sample is closest to the target."""
    candidates = np.unique(np.quantile(p[~need], np.linspace(0, 1, 401)))
    specs = np.array([(p[~need] < c).mean() for c in candidates])
    return float(candidates[np.argmin(np.abs(specs - specificity))])


@dataclass(frozen=True)
class Models:
    tree: Any
    forest: Any
    tree_threshold: float
    forest_threshold: float
    target_specificity: float


@lru_cache(maxsize=1)
def models() -> Models:
    observed, truth = training()
    need = truth["needs_lsi"].to_numpy(bool)
    X = sign_matrix(observed)
    tree = DecisionTreeClassifier(max_depth=TREE_DEPTH, min_samples_leaf=TREE_LEAF, random_state=MODEL_SEED).fit(X, need)
    forest = RandomForestClassifier(n_estimators=FOREST_TREES, min_samples_leaf=FOREST_LEAF, n_jobs=-1,
                                    random_state=MODEL_SEED).fit(X, need)
    target = frequentist.fitted_score().matched_specificity
    return Models(tree, forest, _matched_threshold(tree.predict_proba(X)[:, 1], need, target),
                  _matched_threshold(forest.predict_proba(X)[:, 1], need, target), target)


def probabilities(observed: pd.DataFrame) -> dict[str, np.ndarray]:
    m, X = models(), sign_matrix(observed)
    return {"single tree": m.tree.predict_proba(X)[:, 1], "forest": m.forest.predict_proba(X)[:, 1]}


# ------------------------------------------------------------------------------------------------ reading a tree

def _question(feature: int, threshold: float, left: bool) -> str:
    """A split in words. Every sign is a whole number, so a threshold of 22.5 means 22 or less, or 23 or more."""
    name = FEATURES[feature]
    if name == "walking":
        return "not walking" if left else "walking"
    if name == "conscious level":
        levels = [k for k, v in AVPU_ORDER.items() if (v <= threshold) == left]
        return "alert" if levels == ["A"] else ("not alert" if levels == ["V", "P", "U"] else
                                                f"conscious level {', '.join(levels)}")
    cut = math.floor(threshold)
    return f"{name} {cut} or less" if left else f"{name} {cut + 1} or more"


def leaves(tree: Any | None = None) -> list[dict]:
    """Every leaf of the single tree: the questions on the way to it, the casualties in it on the training sample,
    and the share of them in need."""
    tree = models().tree if tree is None else tree
    t = tree.tree_
    out = []

    def walk(node: int, path: list[str]) -> None:
        if t.children_left[node] == -1:
            counts = t.value[node][0]
            share = float(counts[1] / counts.sum()) if counts.sum() else math.nan
            out.append({"path": path, "casualties": int(t.n_node_samples[node]), "share in need": share,
                        "node": node})
            return
        f, th = int(t.feature[node]), float(t.threshold[node])
        walk(t.children_left[node], path + [_question(f, th, True)])
        walk(t.children_right[node], path + [_question(f, th, False)])

    walk(0, [])
    return out


def tree_text(tree: Any | None = None) -> str:
    """The single tree as a list a reader can follow, one line per leaf."""
    lines = []
    for leaf in leaves(tree):
        lines.append(f"If {', and '.join(leaf['path'])}: {leaf['share in need']:.0%} need an intervention "
                     f"({leaf['casualties']:,} training casualties)")
    return "\n".join(lines)


def path(casualty: Mapping[str, Any]) -> dict:
    """The single tree's questions for one casualty, and the leaf it lands in."""
    m = models()
    x = sign_matrix(pd.DataFrame([dict(casualty)]))
    node = int(m.tree.apply(x)[0])
    for leaf in leaves():
        if leaf["node"] == node:
            return leaf
    raise ValueError("leaf not found")


# ------------------------------------------------------------------------------------------------ scoring

def _metrics(p: np.ndarray, need: np.ndarray, threshold: float) -> dict:
    a = frequentist.accuracy(p >= threshold, need)
    return {"sensitivity": a["sensitivity"], "specificity": a["specificity"],
            "brier": float(np.mean((p - need) ** 2)), "calibration": float(p.mean() - need.mean()),
            "auc": float(roc_auc_score(need, p))}


@lru_cache(maxsize=None)
def diagnosis_results(setting: str) -> dict:
    observed, truth = baseline.generator_sample(setting)
    need = truth["needs_lsi"].to_numpy(bool)
    p, m = probabilities(observed), models()
    return {"single tree": _metrics(p["single tree"], need, m.tree_threshold),
            "forest": _metrics(p["forest"], need, m.forest_threshold)}


@lru_cache(maxsize=None)
def comparison() -> pd.DataFrame:
    """The rule under both readings, lens 02's score, the single tree and the forest, on the same 100,000 synthetic
    casualties of the military cohort, every stream (mechanism)."""
    rows = []
    for reading, name in (("figure", "MPTT-24, figure (as published)"), ("text", "MPTT-24, text (as validated)")):
        r = baseline.diagnosis_results("pre_hospital", reading)
        rows.append({"method": name, "area under the curve": math.nan, "sensitivity": r["sensitivity"],
                     "specificity": r["specificity"], "Brier score": r["brier"], "calibration": r["calibration"]})
    score = frequentist.diagnosis_results("pre_hospital")
    rows.append({"method": "logistic score (lens 02)", "area under the curve": score["auc"],
                 "sensitivity": score["sensitivity"][0], "specificity": score["specificity"][0],
                 "Brier score": score["brier"], "calibration": score["calibration"]})
    for name, r in diagnosis_results("pre_hospital").items():
        rows.append({"method": name, "area under the curve": r["auc"], "sensitivity": r["sensitivity"][0],
                     "specificity": r["specificity"][0], "Brier score": r["brier"], "calibration": r["calibration"]})
    return pd.DataFrame(rows).set_index("method").round(3)


# ------------------------------------------------------------------------------------------------ by hand

CANDIDATES = (
    ("not walking", lambda o: ~o["walking"].to_numpy(bool)),
    ("not alert", lambda o: (o["avpu"] != "A").to_numpy()),
    ("respiratory rate outside 12 to 23", lambda o: ~o["respiratory_rate"].between(12, 23).to_numpy()),
    ("heart rate 100 or more", lambda o: (o["heart_rate"] >= 100).to_numpy()),
)


def gini(need: np.ndarray) -> float:
    if need.size == 0:
        return 0.0
    q = float(np.mean(need))
    return 2 * q * (1 - q)


def split_gain(question: np.ndarray, need: np.ndarray) -> dict:
    """How much one yes-or-no question lowers the Gini impurity, weighted by the size of each side."""
    yes, no = need[question], need[~question]
    after = (yes.size * gini(yes) + no.size * gini(no)) / need.size
    return {"yes": int(yes.size), "yes in need": int(yes.sum()), "no": int(no.size), "no in need": int(no.sum()),
            "impurity before": gini(need), "impurity after": after, "gain": gini(need) - after}


def twenty(ids: tuple[int, ...]) -> tuple[pd.DataFrame, np.ndarray]:
    observed, truth = baseline.generator_sample()
    m = observed["id"].isin(ids).to_numpy()
    return observed[m], truth["needs_lsi"].to_numpy(bool)[m]


# ------------------------------------------------------------------------------------------------ the carving

CARVING_FEATURES = ("respiratory rate", "heart rate")


@lru_cache(maxsize=None)
def carving_tree(depth: int):
    """A tree on two signs only, for the central figure."""
    observed, truth = training()
    X = observed[["respiratory_rate", "heart_rate"]].to_numpy(float)
    return DecisionTreeClassifier(max_depth=depth, min_samples_leaf=TREE_LEAF, random_state=MODEL_SEED).fit(
        X, truth["needs_lsi"].to_numpy(bool))


# ------------------------------------------------------------------------------------------------ fast and frugal

FFT_CUES = (
    ("not walking", lambda o: ~o["walking"].to_numpy(bool)),
    ("heart rate 100 or more", lambda o: (o["heart_rate"] >= baseline.HR_BELOW).to_numpy()),
    (f"respiratory rate outside {baseline.RR_FROM} to {baseline.RR_TO}",
     lambda o: ~o["respiratory_rate"].between(baseline.RR_FROM, baseline.RR_TO).to_numpy()),
)


def fast_frugal(observed: pd.DataFrame, exits: tuple[str, str]) -> np.ndarray:
    """Three cues asked in order. The first two cues each have one exit, 'yes' (flag) or 'no' (clear); the last
    cue decides whatever is left."""
    flag = np.zeros(len(observed), bool)
    open_ = np.ones(len(observed), bool)
    for (_, cue), exit_ in zip(FFT_CUES[:2], exits):
        c = cue(observed)
        leave = open_ & (c if exit_ == "yes" else ~c)
        flag[leave] = exit_ == "yes"
        open_ &= ~leave
    flag[open_] = FFT_CUES[2][1](observed)[open_]
    return flag


@lru_cache(maxsize=None)
def fft_table() -> pd.DataFrame:
    observed, truth = baseline.generator_sample()
    need = truth["needs_lsi"].to_numpy(bool)
    rows = []
    for exits in (("yes", "yes"), ("yes", "no"), ("no", "yes"), ("no", "no")):
        a = frequentist.accuracy(fast_frugal(observed, exits), need)
        rows.append({"exits of the first two cues": f"{exits[0]}, {exits[1]}",
                     "sensitivity": round(a["sensitivity"][0], 3), "specificity": round(a["specificity"][0], 3)})
    return pd.DataFrame(rows).set_index("exits of the first two cues")


# ------------------------------------------------------------------------------------------------ the U shape

@lru_cache(maxsize=None)
def u_shape() -> pd.DataFrame:
    """Respiratory rate alone: the share in need at each rate on the evaluation sample, beside a single linear term
    and a tree, both fitted on the training sample."""
    observed, truth = training()
    x, y = observed[["respiratory_rate"]].to_numpy(float), truth["needs_lsi"].to_numpy(bool)
    linear = LogisticRegression().fit(x, y)
    tree = DecisionTreeClassifier(max_depth=U_DEPTH, min_samples_leaf=U_LEAF, random_state=MODEL_SEED).fit(x, y)
    eo, et = baseline.generator_sample()
    rr = eo["respiratory_rate"].to_numpy(float)
    need = et["needs_lsi"].to_numpy(bool)
    grid = np.arange(int(rr.min()), int(rr.max()) + 1)
    counts = pd.Series(need).groupby(rr).agg(["mean", "size"])
    return pd.DataFrame({"respiratory rate": grid,
                         "casualties": [int(counts["size"].get(g, 0)) for g in grid],
                         "share in need": [float(counts["mean"].get(g, math.nan)) for g in grid],
                         "linear term": linear.predict_proba(grid[:, None].astype(float))[:, 1],
                         "tree": tree.predict_proba(grid[:, None].astype(float))[:, 1]})


def u_summary() -> dict:
    """The low end, where the linear term and the tree part company."""
    eo, et = baseline.generator_sample()
    rr = eo["respiratory_rate"].to_numpy(float)
    need = et["needs_lsi"].to_numpy(bool)
    u = u_shape().set_index("respiratory rate")
    low = rr < baseline.RR_FROM
    return {"casualties below 12": int(low.sum()), "share in need below 12": float(need[low].mean()),
            "linear term below 12": float(u.loc[rr[low], "linear term"].mean()),
            "tree below 12": float(u.loc[rr[low], "tree"].mean())}


# ------------------------------------------------------------------------------------------------ the failure

@lru_cache(maxsize=None)
def instability(n: int = SMALL_N, resamples: int = RESAMPLES, seed: int = RESAMPLE_SEED) -> pd.DataFrame:
    """Trees of depth two grown on `resamples` samples of `n` training casualties each: which question each asks
    first, and at what cut."""
    observed, truth = training()
    X, need = sign_matrix(observed), truth["needs_lsi"].to_numpy(bool)
    rng = np.random.default_rng(seed)
    rows = []
    for i in range(resamples):
        idx = rng.choice(need.size, n, replace=False)
        t = DecisionTreeClassifier(max_depth=2, random_state=MODEL_SEED).fit(X[idx], need[idx]).tree_
        first = _question(int(t.feature[0]), float(t.threshold[0]), False)
        seconds = [_question(int(t.feature[c]), float(t.threshold[c]), False) for c in (t.children_left[0],
                   t.children_right[0]) if t.children_left[c] != -1]
        rows.append({"sample": i + 1, "first question": first, "second questions": "; ".join(seconds)})
    return pd.DataFrame(rows).set_index("sample")


def stable_root() -> str:
    t = models().tree.tree_
    return _question(int(t.feature[0]), float(t.threshold[0]), False)


def recorded_after(truth: pd.DataFrame, seed: int = LEAK_SEED) -> np.ndarray:
    """A constructed variable that stands for something recorded after the decision, for example what an operation
    found. It is built from the generator's truth plus noise, so it leaks the answer. It is not a generator variable
    and measures nothing."""
    rng = np.random.default_rng(seed)
    return truth["needs_lsi"].to_numpy(float) * 2 + rng.standard_normal(len(truth))


@lru_cache(maxsize=None)
def leakage() -> dict:
    """The single tree with and without the constructed variable, on the evaluation sample."""
    to, tt = training()
    eo, et = baseline.generator_sample()
    need_t, need_e = tt["needs_lsi"].to_numpy(bool), et["needs_lsi"].to_numpy(bool)
    Xt = np.column_stack([sign_matrix(to), recorded_after(tt)])
    Xe = np.column_stack([sign_matrix(eo), recorded_after(et, LEAK_SEED + 1)])
    leaky = DecisionTreeClassifier(max_depth=TREE_DEPTH, min_samples_leaf=TREE_LEAF, random_state=MODEL_SEED).fit(Xt, need_t)
    root = "the constructed variable" if leaky.tree_.feature[0] == 4 else FEATURES[int(leaky.tree_.feature[0])]
    return {"without": float(roc_auc_score(need_e, models().tree.predict_proba(sign_matrix(eo))[:, 1])),
            "with": float(roc_auc_score(need_e, leaky.predict_proba(Xe)[:, 1])), "first question": root}


# ------------------------------------------------------------------------------------------------ treatment

def tx_matrix(observed: pd.DataFrame) -> np.ndarray:
    scan = observed["scan_free_fluid"].astype("boolean").fillna(False).to_numpy(bool)
    return np.column_stack([observed["mechanism"].isin(rules.PENETRATING).to_numpy(float), scan.astype(float),
                            observed["sbp"].to_numpy(float), observed["heart_rate"].to_numpy(float)])


@lru_cache(maxsize=None)
def treatment_tree(setting: str):
    """A tree on the ABC score's bedside items predicting significant bleeding, fitted on the training sample's
    battle casualties with the scan done in `setting`."""
    observed, truth = generator.sample(frequentist.TRAIN_N, frequentist.TRAIN_SEED, setting=setting, return_truth=True)
    battle = (observed["stream"] == "battle").to_numpy()
    return DecisionTreeClassifier(max_depth=TREE_DEPTH, min_samples_leaf=TREE_LEAF, random_state=MODEL_SEED).fit(
        tx_matrix(observed[battle]), truth["bleeding"].to_numpy(bool)[battle])


@lru_cache(maxsize=None)
def treatment_results(setting: str) -> dict:
    """On the evaluation sample's battle casualties: the ABC score at 2 or more, the treatment tree at the specificity
    closest to the ABC score's, and the MPTT-24's Priority 1, each against significant bleeding (mechanism)."""
    observed, truth = rules.battle_sample(setting)
    bleed = truth["bleeding"].to_numpy(bool)
    abc = rules.abc_table(observed)["score"].to_numpy() >= rules.ABC_ACTIVATES_AT
    p = treatment_tree(setting).predict_proba(tx_matrix(observed))[:, 1]
    abc_spec = float((~abc[~bleed]).mean())
    threshold = _matched_threshold(p, bleed, abc_spec)
    rule = rules.treatment_results(setting)["mptt24"]
    return {"tree": _metrics(p, bleed, threshold), "threshold": threshold,
            "abc": frequentist.accuracy(abc, bleed), "mptt24": rule,
            "doctrine bedside items": rules.doctrine_bedside_table(observed)}


# ------------------------------------------------------------------------------------------------ the lens

@dataclass(frozen=True)
class TreeAnswer:
    forest_probability: float
    tree_share: float
    tree_path: tuple[str, ...]


DIAGNOSIS_METRICS = (("sensitivity", "sensitivity"), ("specificity", "specificity"), ("brier", "Brier score"),
                     ("calibration", "mean probability minus share in need"))


class TreesLens:
    """The lens behind the Lens interface (R-0.8, R-4.1)."""

    name = NAME

    def diagnose(self, casualty: Mapping[str, Any]) -> TreeAnswer:
        p = probabilities(pd.DataFrame([dict(casualty)]))["forest"][0]
        leaf = path(casualty)
        return TreeAnswer(float(p), leaf["share in need"], tuple(leaf["path"]))

    def treat(self, casualty: Mapping[str, Any]) -> float:
        """The treatment tree's probability that the casualty is bleeding significantly (mechanism)."""
        setting = casualty.get("setting", "pre_hospital")
        return float(treatment_tree(setting).predict_proba(tx_matrix(pd.DataFrame([dict(casualty)])))[0, 1])

    def scorecard(self) -> list[ScorecardRow]:
        rows = []
        for setting in SETTINGS:
            rule = baseline.diagnosis_results(setting, "figure")
            for model, r in diagnosis_results(setting).items():
                for key, name in DIAGNOSIS_METRICS:
                    v = r[key][0] if isinstance(r[key], tuple) else r[key]
                    rows.append(ScorecardRow(NAME, "diagnosis", f"{name}, {model} against need for a life-saving "
                                             f"intervention, {SETTING_NAMES[setting]}", round(v, 4), round(rule[key], 4),
                                             "mechanism", "native", "generator"))
        for setting in SETTINGS:
            r = treatment_results(setting)
            for key, name in DIAGNOSIS_METRICS:
                v = r["tree"][key][0] if isinstance(r["tree"][key], tuple) else r["tree"][key]
                rows.append(ScorecardRow(NAME, "treatment", f"{name}, treatment tree against significant bleeding, "
                                         f"battle casualties, {SETTING_NAMES[setting]}", round(v, 4),
                                         round(r["mptt24"][key], 4), "mechanism", "native", "generator"))
        return rows


LENS = TreesLens()


# ------------------------------------------------------------------------------------------------ seven axes

def _pct(x: float) -> str:
    return f"{100 * x:.1f}%"


def seven_axes() -> pd.DataFrame:
    """The scorecard on the seven axes of D-21, with the baseline under both readings (D-24). Axes 1, 2 and 6 are
    computed on the generator (mechanism); 3, 4 and 5 are stated; axis 7 is net benefit at the threshold lens 10's
    default costs set (mechanism)."""
    from inference_labs.lenses import decision

    pre, inside = diagnosis_results("pre_hospital"), diagnosis_results("in_hospital")
    observed, truth = baseline.generator_sample()
    need = truth["needs_lsi"].to_numpy(bool)
    battle = (observed["stream"] == "battle").to_numpy()
    p_all = probabilities(observed)
    battle_obs, battle_truth = rules.battle_sample("pre_hospital")
    fig, txt = (baseline.diagnosis_results("pre_hospital", r) for r in ("figure", "text"))
    tx_pre, tx_in = treatment_results("pre_hospital"), treatment_results("in_hospital")
    n_leaves = len(leaves())

    def disc(r):
        return (f"sensitivity {_pct(r['sensitivity'][0])}, specificity {_pct(r['specificity'][0])}, area under the "
                f"curve {r['auc']:.3f}")

    def cal(r):
        return f"Brier {r['brier']:.3f}; mean probability minus share in need {r['calibration']:+.3f}"

    def rule_disc(r):
        return f"sensitivity {_pct(r['sensitivity'])}, specificity {_pct(r['specificity'])}"

    def rule_cal(r):
        gap = r["calibration"]
        return f"Brier {r['brier']:.3f}; it flags {100 * abs(gap):.1f} points {'more' if gap > 0 else 'fewer'} than are in need"

    group = "all 100,000 synthetic casualties of the military cohort, disease included"
    rows = [
        ("1 Discrimination (mechanism)", f"{disc(pre['single tree'])}; {group}", f"{disc(pre['forest'])}; {group}",
         rule_disc(fig), rule_disc(txt),
         f"{disc(tx_pre['tree'])}; significant bleeding, battle casualties, scan before hospital. ABC score: "
         f"{rule_disc({k: tx_pre['abc'][k][0] for k in ('sensitivity', 'specificity')})}"),
        ("2 Calibration (mechanism)", cal(pre["single tree"]), cal(pre["forest"]),
         rule_cal(fig) + ". A rule gives no probability, so the Brier score is the share misclassified",
         rule_cal(txt), cal(tx_pre["tree"])),
        ("3 Uncertainty expressed", "A share in need for each leaf", "A probability, the average over the trees",
         "None: a priority", "None: a priority", "A share bleeding for each leaf"),
        ("4 What it needed", f"Labelled cases: {frequentist.TRAIN_N:,} synthetic casualties (mechanism)",
         f"Labelled cases: {frequentist.TRAIN_N:,} synthetic casualties, {FOREST_TREES} trees (mechanism)",
         "Rules only at the point of use (E-08)", "Rules only at the point of use (E-08)",
         f"Labelled cases: the battle casualties among {frequentist.TRAIN_N:,} synthetic casualties (mechanism)"),
        ("5 Readability", f"Three questions deep, {n_leaves} leaves: a medic can follow it on a card",
         f"{FOREST_TREES} trees averaged: it cannot be followed by hand",
         "Six yes-or-no steps, one observation each", "Six yes-or-no steps, one observation each",
         "Three questions deep: a medic can follow it on a card"),
        ("6 Robustness, setting changed (mechanism)",
         f"Scan in hospital: {disc(inside['single tree'])}, unchanged because in the generator the setting changes "
         f"only the scan", f"Scan in hospital: {disc(inside['forest'])}, unchanged for the same reason",
         "Unchanged", "Unchanged",
         f"Scan in hospital: {disc(tx_in['tree'])}. The scan item is more often right in hospital"),
        ("7 Decision value", decision.decision_value(p_all["single tree"], need, battle=battle),
         decision.decision_value(p_all["forest"], need, battle=battle),
         decision.decision_value(baseline.priority_one(observed, "figure"), need, battle=battle),
         decision.decision_value(baseline.priority_one(observed, "text"), need, battle=battle),
         decision.decision_value(treatment_tree("pre_hospital").predict_proba(tx_matrix(battle_obs))[:, 1],
                                 battle_truth["bleeding"]) + ", against significant bleeding, battle casualties, scan before hospital"),
    ]
    return pd.DataFrame(rows, columns=["axis", "diagnosis: single tree", "diagnosis: forest",
                                       "baseline: MPTT-24, figure (as published)",
                                       "baseline: MPTT-24, text (as validated)", "treatment: tree for bleeding"]
                        ).set_index("axis")


# ------------------------------------------------------------------------------------------------ app page 1

@lru_cache(maxsize=None)
def battle_calibration() -> dict:
    """On the evaluation sample's battle casualties, the only casualties app page 1 shows: the share in need, the
    mean probability from the forest and the single tree, and the share in need in each leaf. The models were fitted
    on every stream, so on battle casualties they run low (mechanism)."""
    observed, truth = baseline.generator_sample()
    battle = (observed["stream"] == "battle").to_numpy()
    need = truth["needs_lsi"].to_numpy(bool)[battle]
    p = probabilities(observed[battle])
    node = models().tree.apply(sign_matrix(observed[battle]))
    by_leaf = pd.Series(need).groupby(node).mean().to_dict()
    return {"share in need": float(need.mean()), "forest": float(p["forest"].mean()),
            "single tree": float(p["single tree"].mean()), "leaf": {int(k): float(v) for k, v in by_leaf.items()}}


def panel(record: Mapping[str, Any]) -> dict:
    """The trees panel for one synthetic casualty on app page 1. Every number is formatted here, so the page shows
    only what the library computed (gate G-8)."""
    from inference_labs.lenses import decision

    answer = LENS.diagnose(record)
    m = models()
    cal = battle_calibration()
    leaf_node = path(record)["node"]
    setting = record.get("setting", "pre_hospital")
    bleed_p = LENS.treat(record)
    tx = treatment_results(setting)
    abc = rules.abc_score(record)
    return {
        "heading": "Decision trees panel: one tree you can read, and a forest you cannot",
        "path": ("Single tree, three questions: " + "; ".join(answer.tree_path) + f". In that leaf, "
                 f"{_pct(answer.tree_share)} of the training casualties need a life-saving intervention, so the tree "
                 f"{'flags' if answer.tree_share >= m.tree_threshold else 'does not flag'} this casualty: it flags a "
                 f"leaf where {_pct(m.tree_threshold)} or more need one (mechanism). "
                 f"Among the battle casualties in that leaf, {_pct(cal['leaf'][leaf_node])} need one (mechanism)."),
        "forest": (f"Forest of {FOREST_TREES} trees: probability {answer.forest_probability:.4f} that this casualty "
                   f"needs a life-saving intervention, "
                   f"{decision.against_threshold(answer.forest_probability, m.forest_threshold, places=4, show=False,
                                               name="the forest's own threshold")}"
                   f", so it "
                   f"{'flags' if answer.forest_probability >= m.forest_threshold else 'does not flag'} this casualty "
                   f"(mechanism). Both were fitted on the whole military cohort, disease admissions and non-battle "
                   f"injuries included; on its battle casualties the forest's mean probability is {cal['forest']:.2f} "
                   f"and the single tree's {cal['single tree']:.2f} where {_pct(cal['share in need'])} need an "
                   f"intervention (mechanism), so for a battle casualty both run low."),
        "treatment": (f"Treatment tree on penetrating mechanism (small arms counted as penetrating, an assumption), a "
                      f"positive scan, systolic pressure and heart rate: "
                      f"probability {bleed_p:.2f} that this casualty is "
                      f"bleeding significantly (mechanism), the stand-in for needing transfusion (an assumption). The ABC score "
                      f"for this casualty is {abc} of its 4 items (E-31). On the synthetic battle casualties, at the specificity "
                      f"closest to the ABC score's, the "
                      f"tree finds {_pct(tx['tree']['sensitivity'][0])} of those bleeding against the score's "
                      f"{_pct(tx['abc']['sensitivity'][0])} (mechanism)."),
    }


def page_panel(walk: Any) -> dict:
    """The decision trees panel on app page 1 for one walk-through casualty, given lens 03's Walkthrough (D-27): every
    number already formatted, so the page shows only what the library computed (gate G-8)."""
    return panel(walk.record)
