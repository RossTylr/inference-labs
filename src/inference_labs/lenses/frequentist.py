"""Lens 02, frequentist inference and signal detection (PRD section 6.3; background/02-frequentist.md).

A test makes two kinds of error, and where the line sits between them is a choice. A trial reports what would
happen under repetition: an estimate and an interval, not a verdict on the treatment.

    diagnosis   a logistic score: the probability that a casualty needs a life-saving intervention, from four of the
                signs the MPTT-24 reads (walking, conscious level, respiratory rate, heart rate), fitted on one
                generator sample and scored on another. Its operating threshold is where its specificity on the
                training sample equals the MPTT-24's under the figure reading, so the two can be compared at the
                same rate of false alarms.
    treatment   a trial read as an estimate and an interval. Published results are quoted with their evidence ids;
                an interval is recomputed here only where the register holds the counts. The scorecard's treatment
                row runs on the CRASH-2 fixture, synthetic rows with no trial records, because the real file is not
                read while O-2 is open.

Assumptions
- The respiratory rate enters the score with a squared term, because the generator draws it two-sided, an
  assumption made there.
- Wilson score intervals for proportions, and the usual normal approximations on the log scale for a relative
  risk and on the natural scale for a risk difference, are the methods chosen here.

Every result computed here on the generator or a fixture is a mechanism, not evidence (D-8).
"""
from __future__ import annotations

import math
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
from typing import Any, Mapping

import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score, roc_curve
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

from inference_labs import baseline, generator
from inference_labs.interface import ScorecardRow

NAME = "Frequentist"
TRAIN_N, TRAIN_SEED = 100_000, 7            # the score is fitted here, not on the casualties it is scored on
Z95 = 1.959963984540054
SETTINGS = baseline.SETTINGS
SETTING_NAMES = baseline.SETTING_NAMES
BASTION_N = 357                             # E-07: the prospective cohort
RESAMPLES, RESAMPLE_SEED = 2_000, 357
REPO_ROOT = Path(__file__).resolve().parents[3]
FIXTURE_CRASH2 = REPO_ROOT / "tests" / "fixtures" / "crash2.csv"


# ------------------------------------------------------------------------------------------------ published

@dataclass(frozen=True)
class Published:
    """A published operating point, with its source, its population and its interval where the row gives one."""

    rule: str
    cohort: str
    sensitivity: float
    specificity: float
    source: str
    sensitivity_ci: tuple | None = None
    specificity_ci: tuple | None = None


PUBLISHED = (
    Published("MPTT", "military registry (JTTR), derivation", 0.699, 0.653, "E-03", (0.677, 0.720), (0.632, 0.675)),
    Published("MPTT", "civilian registry (TARN)", 0.576, 0.715, "E-05", (0.569, 0.582), (0.712, 0.718)),
    Published("MPTT", "Camp Bastion, prospective, 357 patients", 0.836, 0.510, "E-07", (0.780, 0.883), (0.426, 0.595)),
    Published("MPTT-24", "military registry (JTTR)", 0.667, 0.699, "E-09", (0.645, 0.689), (0.678, 0.719)),
    Published("MPTT-24", "civilian registry (TARN)", 0.535, 0.748, "E-09", (0.529, 0.541), (0.746, 0.751)),
)
BASTION = PUBLISHED[2]

# E-88: one protocol, in the study's own terms: under-triage and over-triage, per cent, with intervals.
PROTOCOL_PRACTICE = {
    "the protocol alone": {"under": (63.8, 59.2, 68.1), "over": (7.4, 6.7, 8.2)},
    "in practice": {"under": (21.6, 18.0, 25.7), "over": (30.6, 29.3, 32.0)},
}
SCAN_SETTINGS = {                           # free fluid, sensitivity and specificity
    "in hospital, pooled (E-14)": (0.74, 0.98),
    "before hospital, one civilian helicopter service (E-16)": (0.25, 0.96),
}


@dataclass(frozen=True)
class TrialResult:
    """One comparison from a trial: treated against control, as the register gives it or as recomputed here."""

    trial: str
    outcome: str
    treated: str
    control: str
    source: str
    treated_pct: float
    control_pct: float
    difference: tuple | None = None         # points, (estimate, low, high)
    relative_risk: tuple | None = None      # (estimate, low, high)
    p_value: str = ""
    recomputed: bool = False
    note: str = ""


def wilson(k: int, n: int, z: float = Z95) -> tuple[float, float, float]:
    """A proportion and its Wilson score interval."""
    if n == 0:
        return math.nan, math.nan, math.nan
    p = k / n
    centre = (p + z * z / (2 * n)) / (1 + z * z / n)
    half = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / (1 + z * z / n)
    return p, centre - half, centre + half


def risk_difference(k1: int, n1: int, k0: int, n0: int, z: float = Z95) -> tuple[float, float, float]:
    """Treated minus control, in percentage points, with a normal-approximation interval."""
    p1, p0 = k1 / n1, k0 / n0
    se = math.sqrt(p1 * (1 - p1) / n1 + p0 * (1 - p0) / n0)
    d = p1 - p0
    return 100 * d, 100 * (d - z * se), 100 * (d + z * se)


def relative_risk(k1: int, n1: int, k0: int, n0: int, z: float = Z95) -> tuple[float, float, float]:
    """Treated over control, with an interval on the log scale."""
    rr = (k1 / n1) / (k0 / n0)
    se = math.sqrt(1 / k1 - 1 / n1 + 1 / k0 - 1 / n0)
    return rr, rr * math.exp(-z * se), rr * math.exp(z * se)


# E-19 gives the analysed denominators; E-20 and E-21 give the deaths.
CRASH2_ANALYSED = (10_060, 10_067)          # tranexamic acid, placebo (E-19)
CRASH2_ALL_CAUSE = (1_463, 1_613)           # E-20
CRASH2_BLEEDING = (489, 574)                # E-21
REPHILL_COMPOSITE = ((128, 199), (136, 210))   # red cells and plasma, saline (E-77)


@lru_cache(maxsize=None)
def trials() -> tuple[TrialResult, ...]:
    """The treatment case: PROPPR beside CRASH-2 and RePHILL. Recomputed only where the register holds counts."""
    (n1, n0), (a1, a0), (b1, b0) = CRASH2_ANALYSED, CRASH2_ALL_CAUSE, CRASH2_BLEEDING
    (r1, rn1), (r0, rn0) = REPHILL_COMPOSITE
    return (
        TrialResult("PROPPR", "death within 24 hours", "1:1:1", "1:1:2", "E-72", 12.7, 17.0,
                    difference=(-4.2, -9.6, 1.1), p_value="P=.12",
                    note="680 patients; quoted, because the register gives no death counts"),
        TrialResult("CRASH-2", "death from any cause", "tranexamic acid", "placebo", "E-19, E-20",
                    100 * a1 / n1, 100 * a0 / n0, difference=risk_difference(a1, n1, a0, n0),
                    relative_risk=relative_risk(a1, n1, a0, n0), p_value="p = 0.0035", recomputed=True,
                    note="recomputed from the counts; the trial reports 0.91 (0.85 to 0.97)"),
        TrialResult("CRASH-2", "death from bleeding", "tranexamic acid", "placebo", "E-19, E-21",
                    100 * b1 / n1, 100 * b0 / n0, difference=risk_difference(b1, n1, b0, n0),
                    relative_risk=relative_risk(b1, n1, b0, n0), p_value="p = 0.0077", recomputed=True,
                    note="recomputed from the counts; the trial reports 0.85 (0.76 to 0.96)"),
        TrialResult("RePHILL", "death or failure to clear lactate", "red cells and plasma", "saline", "E-77",
                    100 * r1 / rn1, 100 * r0 / rn0, difference=risk_difference(r1, rn1, r0, rn0),
                    p_value="p=0.996", recomputed=True,
                    note="recomputed from the counts without adjustment; the trial's adjusted interval runs from "
                         "-9.0 to 9.0 points"),
        TrialResult("RePHILL", "death within 3 hours", "red cells and plasma", "saline", "E-77", 16.0, 22.0,
                    relative_risk=(0.75, 0.50, 1.13), note="quoted"),
    )


# E-20: CRASH-2 all-cause death by time from injury, relative risk with its 99% interval.
CRASH2_TIME_SUBGROUPS = (
    ("within 1 hour", (0.87, 0.75, 1.00)),
    ("1 to 3 hours", (0.87, 0.75, 1.00)),
    ("after 3 hours", (1.00, 0.86, 1.17)),
)
CRASH2_HETEROGENEITY_P, CRASH2_PRESPECIFIED_THRESHOLD = 0.11, 0.001     # E-20
E79_THRESHOLDS = {"benefit": 0.10, "harm": 0.025}                       # E-79


# ------------------------------------------------------------------------------------------------ the score

def sign_matrix(observed: pd.DataFrame) -> np.ndarray:
    """Walking; conscious level, one column for each level below alert; respiratory rate and its square; heart
    rate."""
    avpu = observed["avpu"].to_numpy(object)
    rr = observed["respiratory_rate"].to_numpy(float)
    return np.column_stack([observed["walking"].to_numpy(float), avpu == "V", avpu == "P", avpu == "U",
                            rr, rr ** 2, observed["heart_rate"].to_numpy(float)]).astype(float)


@dataclass(frozen=True)
class Score:
    model: Any
    threshold: float
    matched_specificity: float      # the MPTT-24's specificity, figure reading, on the training sample


@lru_cache(maxsize=1)
def fitted_score() -> Score:
    """The logistic score, fitted on the training sample, with its threshold set at the MPTT-24's specificity."""
    observed, truth = generator.sample(TRAIN_N, TRAIN_SEED, return_truth=True)
    need = truth["needs_lsi"].to_numpy(bool)
    model = make_pipeline(StandardScaler(), LogisticRegression(max_iter=1000)).fit(sign_matrix(observed), need)
    p = model.predict_proba(sign_matrix(observed))[:, 1]
    flag = baseline.priority_one(observed, "figure")
    spec = float((~flag[~need]).mean())
    return Score(model, float(np.quantile(p[~need], spec)), spec)


def probability(observed: pd.DataFrame) -> np.ndarray:
    return fitted_score().model.predict_proba(sign_matrix(observed))[:, 1]


def probability_one(casualty: Mapping[str, Any]) -> float:
    return float(probability(pd.DataFrame([dict(casualty)]))[0])


def coefficients() -> pd.Series:
    """The fitted weights on the standardised signs, so a reader can see what the score leans on."""
    names = ["walking", "responds to voice", "responds to pain", "unresponsive", "respiratory rate",
             "respiratory rate squared", "heart rate"]
    return pd.Series(fitted_score().model[-1].coef_[0], index=names).round(3)


# ------------------------------------------------------------------------------------------------ accuracy

def accuracy(flag: np.ndarray, need: np.ndarray) -> dict:
    """Sensitivity and specificity with Wilson intervals, and the counts behind them."""
    flag, need = np.asarray(flag, bool), np.asarray(need, bool)
    tp, fn = int((flag & need).sum()), int((~flag & need).sum())
    tn, fp = int((~flag & ~need).sum()), int((flag & ~need).sum())
    return {"casualties": int(need.size), "in need": int(need.sum()), "hits": tp, "misses": fn,
            "false alarms": fp, "correct rejections": tn,
            "sensitivity": wilson(tp, tp + fn), "specificity": wilson(tn, tn + fp)}


COHORT_VIEWS = (
    ("military", "military, every stream", None),
    ("military", "military, injured only", "injured"),
    ("civilian", "civilian, injured civilians", None),
)
METHODS = (("MPTT-24, figure (as published)", "figure"), ("MPTT-24, text (as validated)", "text"),
           ("logistic score", "score"))


def _flags(observed: pd.DataFrame, method: str) -> np.ndarray:
    if method == "score":
        return probability(observed) >= fitted_score().threshold
    return baseline.priority_one(observed, method)


@lru_cache(maxsize=None)
def accuracy_table() -> pd.DataFrame:
    """Sensitivity and specificity with 95% intervals, by cohort and setting, for both readings of the rule and
    for the score, on 100,000 synthetic casualties a cohort (mechanism)."""
    rows = []
    for cohort, label, subset in COHORT_VIEWS:
        for setting in SETTINGS:
            observed, truth = baseline.generator_sample(setting, cohort)
            m = baseline.calibration_cohort(observed) if subset == "injured" else np.ones(len(observed), bool)
            need = truth["needs_lsi"].to_numpy(bool)[m]
            for name, method in METHODS:
                a = accuracy(_flags(observed, method)[m], need)
                rows.append({"cohort": label, "scan": SETTING_NAMES[setting], "method": name,
                             "casualties": a["casualties"], "share in need": round(a["in need"] / a["casualties"], 3),
                             "sensitivity": round(a["sensitivity"][0], 3),
                             "sensitivity 95% interval": _interval(a["sensitivity"]),
                             "specificity": round(a["specificity"][0], 3),
                             "specificity 95% interval": _interval(a["specificity"])})
    return pd.DataFrame(rows)


def _interval(x: tuple) -> str:
    return f"{x[1]:.3f} to {x[2]:.3f}"


@lru_cache(maxsize=None)
def roc(cohort: str = "military") -> dict:
    """The score's receiver operating curve on the cohort's 100,000 evaluation casualties, with the rule's points
    under both readings and the score's own operating point."""
    observed, truth = baseline.generator_sample("pre_hospital", cohort)
    need = truth["needs_lsi"].to_numpy(bool)
    p = probability(observed)
    fpr, tpr, _ = roc_curve(need, p)
    points = {name: accuracy(_flags(observed, method), need) for name, method in METHODS}
    return {"fpr": fpr, "tpr": tpr, "auc": float(roc_auc_score(need, p)), "points": points,
            "share in need": float(need.mean())}


def hundred(start: int = 0) -> pd.DataFrame:
    """A hundred synthetic casualties from the military evaluation sample, with need and the MPTT-24's flag."""
    observed, truth = baseline.generator_sample()
    o, t = observed.iloc[start:start + 100], truth.iloc[start:start + 100]
    return pd.DataFrame({"id": o["id"].to_numpy(), "needs": t["needs_lsi"].to_numpy(bool),
                         "MPTT-24 Priority 1": baseline.priority_one(o, "figure")})


def expected_counts(sensitivity: float, specificity: float, in_need: int, total: int = 100) -> dict:
    """What a published operating point would do to a hundred with a given number in need, as expected counts."""
    not_need = total - in_need
    return {"hits": in_need * sensitivity, "misses": in_need * (1 - sensitivity),
            "false alarms": not_need * (1 - specificity), "correct rejections": not_need * specificity}


@lru_cache(maxsize=None)
def resampled_sensitivity(size: int = BASTION_N, resamples: int = RESAMPLES, seed: int = RESAMPLE_SEED) -> dict:
    """The MPTT-24's sensitivity (figure reading) estimated again and again on samples of `size` drawn from the
    military cohort's injured, with the long-run value on all of them. Sample size on synthetic data only."""
    observed, truth = baseline.generator_sample()
    m = baseline.calibration_cohort(observed)
    flag = baseline.priority_one(observed, "figure")[m]
    need = truth["needs_lsi"].to_numpy(bool)[m]
    rng = np.random.default_rng(seed)
    estimates = np.empty(resamples)
    in_need = np.empty(resamples, int)
    for i in range(resamples):
        idx = rng.choice(need.size, size, replace=False)
        estimates[i] = flag[idx][need[idx]].mean()
        in_need[i] = int(need[idx].sum())
    long_run = float(flag[need].mean())
    lo, hi = np.quantile(estimates, [0.025, 0.975])
    return {"estimates": estimates, "in need": in_need, "long run": long_run, "middle 95%": (float(lo), float(hi)),
            "share at or above E-07": float((estimates >= BASTION.sensitivity).mean())}


# ------------------------------------------------------------------------------------------------ treatment

@lru_cache(maxsize=None)
def fixture_reading(path: str = str(FIXTURE_CRASH2)) -> dict:
    """Death with tranexamic acid against placebo on the CRASH-2 fixture: 200 synthetic rows with no trial
    records, a stand-in while O-2 is open. Mechanism only."""
    data = pd.read_csv(path)
    treated = data["treatment"] == "TXA"
    dead = data["condition"] == "dead"
    k1, n1, k0, n0 = int(dead[treated].sum()), int(treated.sum()), int(dead[~treated].sum()), int((~treated).sum())
    return {"treated": (k1, n1), "control": (k0, n0), "difference": risk_difference(k1, n1, k0, n0)}


# ------------------------------------------------------------------------------------------------ scoring

def _calibration(p: np.ndarray, need: np.ndarray) -> dict:
    return {"brier": float(np.mean((p - need) ** 2)), "calibration": float(p.mean() - need.mean())}


@lru_cache(maxsize=None)
def diagnosis_results(setting: str) -> dict:
    """The score on every synthetic casualty in one setting, against need for a life-saving intervention."""
    observed, truth = baseline.generator_sample(setting)
    need = truth["needs_lsi"].to_numpy(bool)
    p = probability(observed)
    a = accuracy(p >= fitted_score().threshold, need)
    return {"sensitivity": a["sensitivity"], "specificity": a["specificity"], **_calibration(p, need),
            "auc": float(roc_auc_score(need, p))}


DIAGNOSIS_METRICS = (("sensitivity", "sensitivity"), ("specificity", "specificity"), ("brier", "Brier score"),
                     ("calibration", "mean probability minus share in need"))


def diagnosis_metric(name: str, setting: str) -> str:
    return (f"{name}, logistic score against need for a life-saving intervention, "
            f"{SETTING_NAMES[setting]}")


class FrequentistLens:
    """The lens behind the Lens interface (R-0.8, R-3.1)."""

    name = NAME

    def diagnose(self, casualty: Mapping[str, Any]) -> float:
        """The score's probability that the casualty needs a life-saving intervention (mechanism)."""
        return probability_one(casualty)

    def treat(self, casualty: Mapping[str, Any]) -> TrialResult:
        """The lens does not choose for one casualty. It returns a trial read as an estimate and an interval: CRASH-2,
        death from bleeding (E-19, E-21)."""
        return trials()[2]

    def scorecard(self) -> list[ScorecardRow]:
        rows = []
        for setting in SETTINGS:
            score = diagnosis_results(setting)
            rule = baseline.diagnosis_results(setting, "figure")
            for key, name in DIAGNOSIS_METRICS:
                value = score[key][0] if isinstance(score[key], tuple) else score[key]
                rows.append(ScorecardRow(NAME, "diagnosis", diagnosis_metric(name, setting), round(value, 4),
                                         round(rule[key], 4), "mechanism", "native", "generator"))
        d = fixture_reading()["difference"][0]
        rows.append(ScorecardRow(NAME, "treatment", "difference in death, tranexamic acid minus placebo, points, "
                                 "CRASH-2 fixture (synthetic rows)", round(d, 2), math.nan, "mechanism", "weak",
                                 f"fixture:{FIXTURE_CRASH2.name}"))
        return rows


LENS = FrequentistLens()


# ------------------------------------------------------------------------------------------------ seven axes

def _pct(x: float) -> str:
    return f"{100 * x:.1f}%"


def _ci(x: tuple) -> str:
    return f"{_pct(x[0])} ({_pct(x[1])} to {_pct(x[2])})"


def difference_words(d: tuple, what: str = "deaths") -> str:
    """A difference in points, treated minus control, said in words: fewer or more, with its interval."""
    def side(x: float) -> str:
        return f"{abs(x):.1f} {'fewer' if x < 0 else 'more'}"
    return f"{side(d[0])} {what} in every 100 with the treatment (from {side(d[1])} to {side(d[2])})"


def seven_axes() -> pd.DataFrame:
    """The scorecard on the seven axes of D-21, with the baseline under both readings (D-24). Axes 1, 2 and 6 are
    computed on the generator or the fixture (mechanism); 3, 4 and 5 are stated; axis 7 waits for lens 10."""
    pre, inside = diagnosis_results("pre_hospital"), diagnosis_results("in_hospital")
    fig, txt = (baseline.diagnosis_results("pre_hospital", r) for r in ("figure", "text"))
    civ = roc("civilian")["points"]
    fx = fixture_reading()
    (k1, n1), (k0, n0), d = fx["treated"], fx["control"], fx["difference"]

    def rule_disc(r):
        return f"sensitivity {_pct(r['sensitivity'])}, specificity {_pct(r['specificity'])}"

    def rule_cal(r):
        gap = r["calibration"]
        side = "more" if gap > 0 else "fewer"
        return f"Brier {r['brier']:.3f}; it flags {100 * abs(gap):.1f} points {side} than are in need"

    rows = [
        ("1 Discrimination (mechanism)",
         f"sensitivity {_ci(pre['sensitivity'])}, specificity {_ci(pre['specificity'])}; area under the curve "
         f"{pre['auc']:.3f}; all 100,000 synthetic casualties of the military cohort, disease included",
         rule_disc(fig), rule_disc(txt),
         f"Not a classifier. On the CRASH-2 fixture, {k1} of {n1} died with tranexamic acid and {k0} of {n0} with "
         f"placebo: {difference_words(d)}; synthetic rows, not trial data"),
        ("2 Calibration (mechanism)",
         f"Brier {pre['brier']:.3f}; mean probability minus share in need {pre['calibration']:+.3f}",
         rule_cal(fig) + ". A rule gives no probability, so the Brier score is the share misclassified",
         rule_cal(txt), "Not applicable"),
        ("3 Uncertainty expressed", "An interval on every rate",
         "None: a priority", "None: a priority", "An interval on the difference"),
        ("4 What it needed",
         f"Labelled cases: {TRAIN_N:,} synthetic casualties to fit seven weights (mechanism)",
         "Rules only at the point of use (E-08)", "Rules only at the point of use (E-08)",
         "A randomised trial: deaths counted in each arm"),
        ("5 Readability",
         "A weighted sum of terms in four signs: a medic needs the weights or a device; the decision is one comparison",
         "Six yes-or-no steps, one observation each", "Six yes-or-no steps, one observation each",
         "Two percentages, their difference and its interval"),
        ("6 Robustness, setting and cohort changed (mechanism)",
         f"Scan in hospital: sensitivity {_pct(inside['sensitivity'][0])}, specificity "
         f"{_pct(inside['specificity'][0])}, unchanged because in the generator the setting changes only the scan. Civilian cohort: "
         f"sensitivity {_pct(civ['logistic score']['sensitivity'][0])}, specificity "
         f"{_pct(civ['logistic score']['specificity'][0])}",
         f"Civilian cohort: sensitivity {_pct(civ['MPTT-24, figure (as published)']['sensitivity'][0])}, "
         f"specificity {_pct(civ['MPTT-24, figure (as published)']['specificity'][0])}",
         f"Civilian cohort: sensitivity {_pct(civ['MPTT-24, text (as validated)']['sensitivity'][0])}, "
         f"specificity {_pct(civ['MPTT-24, text (as validated)']['specificity'][0])}",
         "Not applicable: the setting does not enter"),
        ("7 Decision value", "Pending until lens 10", "Pending until lens 10", "Pending until lens 10",
         "Pending until lens 10"),
    ]
    return pd.DataFrame(rows, columns=["axis", "diagnosis: logistic score", "baseline: MPTT-24, figure (as published)",
                                       "baseline: MPTT-24, text (as validated)", "treatment: trial reading"]
                        ).set_index("axis")


# ------------------------------------------------------------------------------------------------ app page 1

def panel(record: Mapping[str, Any]) -> dict:
    """The frequentist panel for one synthetic casualty on app page 1. Every number is formatted here, so the page
    shows only what the library computed (gate G-8)."""
    score = fitted_score()
    p = probability_one(record)
    pre = diagnosis_results("pre_hospital")
    rule = baseline.diagnosis_results("pre_hospital", "figure")
    crash2 = trials()[2]
    rr, d = crash2.relative_risk, crash2.difference
    return {
        "heading": "Frequentist panel: a score, its two error rates, and a trial read as an interval",
        "score": (f"Logistic score from walking, conscious level, respiratory rate and heart rate: probability "
                  f"{p:.2f} that this casualty needs a life-saving intervention (mechanism). The threshold is "
                  f"{score.threshold:.2f}, so the score {'flags' if p >= score.threshold else 'does not flag'} "
                  f"this casualty."),
        "errors": (f"At that threshold, on all 100,000 synthetic casualties of the military cohort, disease included "
                   f"(mechanism): sensitivity {_ci(pre['sensitivity'])}, "
                   f"specificity {_ci(pre['specificity'])}. The MPTT-24 as published, on the same casualties: "
                   f"sensitivity {_pct(rule['sensitivity'])}, specificity {_pct(rule['specificity'])} "
                   f"(mechanism)."),
        "trial": (f"CRASH-2, death from bleeding: {crash2.treated_pct:.1f}% with tranexamic acid against "
                  f"{crash2.control_pct:.1f}% with placebo: {difference_words(d)}, a relative risk of {rr[0]:.2f} "
                  f"({rr[1]:.2f} to {rr[2]:.2f}), recomputed from the counts (E-19, E-21). CRASH-2 is civilian, so using it for a military casualty is an "
                  f"assumption."),
    }
