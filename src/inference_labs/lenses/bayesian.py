"""Lens 03, Bayesian inference (slice 1; PRD section 5; docs/background/03-bayesian.md).

Evidence moves a belief; where you end depends on where you began.

Diagnosis. The belief that a battle casualty is bleeding into the abdomen, which is what the scan looks for
(free fluid). It is carried as an `RV` (D-19) along the belief line (D-17; design section 12.4):

    start       prior from the casualty mix
    triage      updated on the physiology: a systolic pressure of 90 mm Hg or less
    scan        updated on the scan result, by an amount that depends on the setting
    treatment   carried unchanged
    evacuation  carried unchanged

Treatment. A trial re-read with a prior: a summary of the trial's likelihood and a prior on the log relative
risk give the posterior for the relative risk and the probability of benefit (R-1.4).

Where the numbers come from
- Scan accuracy before hospital: sensitivity Beta(21, 63) and specificity Beta(257, 9), the two-by-two counts
  in E-16 (21 true positives, 63 false negatives, 257 true negatives, 9 false positives).
- Scan accuracy in hospital: Beta(74, 26) and Beta(294, 6). E-14 is pooled,
  so these shapes are an assumption centred on its 74% and 98%.
- The 90 mm Hg threshold is the systolic item of the ABC transfusion score (E-31). How often that reading is
  present with and without abdominal bleeding is counted on the generator, so it is a mechanism, not evidence.
- The prior from the mix is counted on the generator: a mechanism.
- Relative risk of bleeding death with tranexamic acid by delay band: CRASH-2 (E-22). CRASH-2 is civilian, so
  using its figures for a military casualty is an assumption. The log-normal shape fitted to each interval is an
  assumption.
- Trial summaries for the treatment case: CRASH-3 head injury-related death (E-27) and its mild to moderate
  subgroup (E-28); CRASH-2 all-cause death (E-20); death within 3 hours in RePHILL (E-77).
  The sceptical, enthusiastic and minimally informative priors are assumptions.

Every result computed on the generator or the fixtures carries the mechanism label (D-8). A result on a real
trial file, read from a local path outside the repository, carries the evidence label.

The baseline column of the scorecard is the MPTT-24 under its default reading (baseline.py), scored on the same
casualties against the same target: its Priority 1 counted as a flag for abdominal bleeding. The rule was written
to find casualties who need a life-saving intervention, not abdominal bleeding. It states no probability that a
treatment works, so the treatment row has no baseline figure and holds NaN.
"""
from __future__ import annotations

import math
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
from typing import Any, Mapping

import numpy as np
import pandas as pd
from scipy.stats import norm

from inference_labs import baseline, generator
from inference_labs.belief import RV
from inference_labs.interface import ScorecardRow, is_real_data_path
from inference_labs.lenses import rules

REPO_ROOT = Path(__file__).resolve().parents[3]
FIXTURE_CRASH3 = REPO_ROOT / "tests" / "fixtures" / "crash3.csv"

LENS_NAME = "Bayesian"
NO_BASELINE = float("nan")           # the MPTT-24 states no probability that a treatment works (R-2.11)

N_DRAWS = 4000
SEED = 42
TRAIN_N, TRAIN_SEED = 20_000, 1      # the synthetic casualties the triage reading is counted on
EVAL_N, EVAL_SEED = 30_000, 42       # the synthetic casualties the scorecard is measured on
WALK_N = 3_000                       # the synthetic casualties the walk-through draws from

EVACUATE_ABOVE = 0.5                 # the explainer's rule: evacuate first if the belief is above one half (assumption)
TRIAGE_SBP_AT_OR_BELOW = 90          # mm Hg, the systolic item of the ABC score (E-31)
Z95 = float(norm.ppf(0.975))

SETTINGS = ("pre_hospital", "in_hospital")
SETTING_NAMES = {"pre_hospital": "before hospital", "in_hospital": "in hospital"}
PATIENT_TYPES = ("haemorrhage", "chest", "head")   # the battle patient types; the generator scans battle casualties only
STEPS = ("start", "triage", "scan", "treatment", "evacuation")
STEP_NAMES = {"start": "Start", "triage": "Triage", "scan": "Scan", "treatment": "Treatment", "evacuation": "Evacuation"}

SCAN_ACCURACY = {
    "pre_hospital": {
        "sensitivity": (21, 63), "specificity": (257, 9), "source": "E-16",
        "basis": "the two-by-two counts of one civilian helicopter service",
    },
    "in_hospital": {
        "sensitivity": (74, 26), "specificity": (294, 6), "source": "E-14",
        "basis": "an assumption centred on the pooled 74% and 98%",
    },
}
E14_STUDIES = 75        # E-14: a pooled analysis of 75 studies
SCAN_SOURCES = (f"The pre-hospital study is civilian (E-16); the in-hospital figure is from a pooled analysis of "
                f"{E14_STUDIES} studies (E-14).")

# E-22: relative risk of death from bleeding with tranexamic acid, by time to treatment, in CRASH-2,
# a civilian trial. Using these figures for a military casualty is an assumption.
TXA_RR_BANDS = (
    ("up to 1 hour", 60.0, (0.68, 0.57, 0.82)),
    ("1 to 3 hours", 180.0, (0.79, 0.64, 0.97)),
    ("over 3 hours", math.inf, (1.44, 1.12, 1.84)),
)
# E-22: deaths from bleeding when treated within an hour, placebo (E-19) against tranexamic acid, per cent.
TXA_FIRST_HOUR_DEATHS = (7.7, 5.3)
TXA_FIRST_HOUR_POINTS = round(TXA_FIRST_HOUR_DEATHS[0] - TXA_FIRST_HOUR_DEATHS[1], 1)   # absolute reduction


# ------------------------------------------------------------------------------------------------ updating

def constant(value: float, n: int = N_DRAWS) -> RV:
    """A known number as an RV: the same value at every draw."""
    return RV(np.full(n, float(value)))


def update(belief: RV | float, sensitivity: RV | float, specificity: RV | float, positive: bool | None) -> RV | float:
    """Bayes' rule for one yes-or-no finding. A missing finding (None) leaves the belief unchanged."""
    if positive is None:
        return belief
    if positive:
        hit = belief * sensitivity
        return hit / (hit + (1 - belief) * (1 - specificity))
    miss = belief * (1 - sensitivity)
    return miss / (miss + (1 - belief) * specificity)


@lru_cache(maxsize=None)
def scan_accuracy(setting: str, n: int = N_DRAWS, seed: int = SEED) -> tuple[RV, RV]:
    """Sensitivity and specificity of the scan for free fluid in `setting`, as draws (sensitivity drawn first)."""
    if setting not in SCAN_ACCURACY:
        raise ValueError(f"setting must be one of {SETTINGS}")
    acc = SCAN_ACCURACY[setting]
    rng = np.random.default_rng(seed)
    return RV(rng.beta(*acc["sensitivity"], n)), RV(rng.beta(*acc["specificity"], n))


def belief_after_scan(prior: float, setting: str, positive: bool = True, n: int = N_DRAWS, seed: int = SEED) -> RV:
    """The belief after one scan result, starting from `prior` (the calculation in R-1.3)."""
    sens, spec = scan_accuracy(setting, n, seed)
    return update(constant(prior, n), sens, spec, positive)


# ------------------------------------------------------------------------------------------------ the generator

def _battle(observed: pd.DataFrame, truth: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    keep = (observed["stream"] == "battle").to_numpy()
    return observed[keep].reset_index(drop=True), truth[keep].reset_index(drop=True)


def triage_reading(casualty: Mapping[str, Any]) -> bool:
    """The physiology used at triage: systolic pressure of 90 mm Hg or less (E-31's threshold)."""
    return bool(casualty["sbp"] <= TRIAGE_SBP_AT_OR_BELOW)


@lru_cache(maxsize=None)
def training_counts() -> dict:
    """Battle casualties from the generator, counted by abdominal bleeding and the triage reading (mechanism)."""
    observed, truth = _battle(*generator.sample(TRAIN_N, TRAIN_SEED, return_truth=True))
    target = truth["free_fluid"].to_numpy(bool)
    reading = (observed["sbp"] <= TRIAGE_SBP_AT_OR_BELOW).to_numpy(bool)
    return {
        "casualties": int(target.size),
        "bleeding": int(target.sum()),
        "true_positive": int((reading & target).sum()),
        "false_negative": int((~reading & target).sum()),
        "false_positive": int((reading & ~target).sum()),
        "true_negative": int((~reading & ~target).sum()),
    }


def prior_from_mix() -> float:
    """Share of battle casualties bleeding into the abdomen under the generator's default mix (mechanism)."""
    c = training_counts()
    return c["bleeding"] / c["casualties"]


def default_prior() -> float:
    """The prior the walk-through starts from: the share from the mix, to two decimal places."""
    return round(prior_from_mix(), 2)


@lru_cache(maxsize=None)
def triage_accuracy(n: int = N_DRAWS, seed: int = SEED + 1) -> tuple[RV, RV]:
    """How often the triage reading is present with and without abdominal bleeding, as draws.

    Beta(1 + hits, 1 + misses) from the generator's counts, the 1s being a flat starting point (assumption).
    """
    c = training_counts()
    rng = np.random.default_rng(seed)
    sens = RV(rng.beta(1 + c["true_positive"], 1 + c["false_negative"], n))
    spec = RV(rng.beta(1 + c["true_negative"], 1 + c["false_positive"], n))
    return sens, spec


# ------------------------------------------------------------------------------------------------ the belief line

def start(prior: float, n: int = N_DRAWS) -> RV:
    """Start of the line: the prior, the same at every draw."""
    return constant(prior, n)


def after_triage(belief: RV, casualty: Mapping[str, Any]) -> RV:
    """Updated on the physiology at triage."""
    sens, spec = triage_accuracy(len(belief))
    return update(belief, sens, spec, triage_reading(casualty))


def scan_result(casualty: Mapping[str, Any]) -> bool | None:
    value = casualty.get("scan_free_fluid")
    if value is None or value is pd.NA or (isinstance(value, float) and math.isnan(value)):
        return None
    return bool(value)


def after_scan(belief: RV, casualty: Mapping[str, Any]) -> RV:
    """Updated on the scan, with the accuracy for the setting the scan was done in. No scan, no change."""
    sens, spec = scan_accuracy(casualty["setting"], len(belief))
    return update(belief, sens, spec, scan_result(casualty))


def to_treatment(belief: RV) -> RV:
    """Carried unchanged: the treatment step uses the belief; it does not update it."""
    return belief


def to_evacuation(belief: RV) -> RV:
    """Carried unchanged: the evacuation step uses the belief; it does not update it."""
    return belief


def belief_line(casualty: Mapping[str, Any], prior: float | None = None, n: int = N_DRAWS) -> dict[str, RV]:
    """The belief at each of the five steps for one casualty (R-1.2)."""
    line = {"start": start(default_prior() if prior is None else prior, n)}
    line["triage"] = after_triage(line["start"], casualty)
    line["scan"] = after_scan(line["triage"], casualty)
    line["treatment"] = to_treatment(line["scan"])
    line["evacuation"] = to_evacuation(line["treatment"])
    return line


# ------------------------------------------------------------------------------------------------ treatment

def delay_band(delay_min: float) -> tuple[str, tuple[float, float, float]]:
    for name, upper, rr in TXA_RR_BANDS:
        if delay_min <= upper:
            return name, rr
    raise ValueError(f"no band for a delay of {delay_min}")


@dataclass(frozen=True)
class LogNormalSummary:
    """A relative risk summarised as a normal distribution on the log scale: mean and standard deviation."""

    mean: float
    sd: float

    @classmethod
    def from_interval(cls, rr: float, lo: float, hi: float) -> "LogNormalSummary":
        """From a published relative risk and its 95% interval."""
        return cls(math.log(rr), (math.log(hi) - math.log(lo)) / (2 * Z95))

    @property
    def relative_risk(self) -> float:
        return math.exp(self.mean)

    def interval(self) -> tuple[float, float]:
        return math.exp(self.mean - Z95 * self.sd), math.exp(self.mean + Z95 * self.sd)

    def draws(self, n: int = N_DRAWS, seed: int = SEED) -> RV:
        return RV(np.exp(np.random.default_rng(seed).normal(self.mean, self.sd, n)))


@lru_cache(maxsize=None)
def relative_risk_draws(band: str, n: int = N_DRAWS, seed: int = SEED + 2) -> RV:
    """E-22's relative risk for one delay band, as draws from a log-normal fitted to its interval (shape assumed)."""
    rr = dict((name, value) for name, _, value in TXA_RR_BANDS)[band]
    return LogNormalSummary.from_interval(*rr).draws(n, seed)


def weighted_reduction(belief: RV, delay_min: float) -> RV:
    """Belief times the relative reduction in bleeding death for the delay: a population average applied to one
    casualty's belief, so a mechanism (design section 12.4)."""
    band, _ = delay_band(delay_min)
    return belief * (1 - relative_risk_draws(band, len(belief)))


def summary_from_counts(events_treated: int, n_treated: int, events_control: int, n_control: int) -> LogNormalSummary:
    """Log relative risk and its standard error from a two-by-two table."""
    if min(events_treated, events_control) == 0:
        raise ValueError("a zero count leaves the log relative risk undefined")
    log_rr = math.log((events_treated / n_treated) / (events_control / n_control))
    se = math.sqrt(1 / events_treated - 1 / n_treated + 1 / events_control - 1 / n_control)
    return LogNormalSummary(log_rr, se)


def summary_from_file(path: str | Path, arm: str = "treatment", treated: str = "TXA", event: str = "headinjurydeath") -> LogNormalSummary:
    """The likelihood summary of a CRASH-3-style file: one row per patient, an arm column and a 0/1 event column.

    The column names follow the fixture and are unconfirmed against the real files until O-2 is closed.
    """
    frame = pd.read_csv(path)
    is_treated = frame[arm] == treated
    events = frame[event].astype(int)
    return summary_from_counts(int(events[is_treated].sum()), int(is_treated.sum()),
                               int(events[~is_treated].sum()), int((~is_treated).sum()))


@dataclass(frozen=True)
class TrialPosterior:
    prior: LogNormalSummary
    likelihood: LogNormalSummary
    posterior: LogNormalSummary
    relative_risk: RV

    def prob_benefit(self) -> float:
        """Probability that the relative risk is below one, exact from the normal posterior."""
        return self.prob_below(1.0)

    def prob_below(self, threshold: float) -> float:
        """Probability that the relative risk is below `threshold`, exact from the normal posterior. The draws in
        `relative_risk` are for carrying the effect into later arithmetic, not for this summary."""
        return float(norm.cdf((math.log(threshold) - self.posterior.mean) / self.posterior.sd))


def reread_trial(likelihood: LogNormalSummary, prior: LogNormalSummary, n: int = N_DRAWS, seed: int = SEED + 3) -> TrialPosterior:
    """Combine a trial's likelihood summary with a prior on the log relative risk (normal with normal)."""
    w_prior, w_data = 1 / prior.sd ** 2, 1 / likelihood.sd ** 2
    sd = math.sqrt(1 / (w_prior + w_data))
    mean = (prior.mean * w_prior + likelihood.mean * w_data) / (w_prior + w_data)
    post = LogNormalSummary(mean, sd)
    return TrialPosterior(prior, likelihood, post, post.draws(n, seed))


SCEPTICAL_SD = math.log(1 / 0.8) / float(norm.ppf(0.95))   # 5% prior probability of a 20% reduction or more (assumption)
CRASH3_HEAD_INJURY_DEATH = LogNormalSummary.from_interval(0.94, 0.86, 1.02)     # E-27
CRASH3_MILD_TO_MODERATE = LogNormalSummary.from_interval(0.78, 0.64, 0.95)      # E-28
CRASH2_ALL_CAUSE_DEATH = LogNormalSummary.from_interval(0.91, 0.85, 0.97)       # E-20
REPHILL_DEATH_3H = LogNormalSummary.from_interval(0.75, 0.50, 1.13)             # E-77
PRIORS = {
    "minimally informative": LogNormalSummary(0.0, 10.0),                         # assumption
    "sceptical": LogNormalSummary(0.0, SCEPTICAL_SD),                            # assumption
    "enthusiastic": LogNormalSummary(math.log(0.8), SCEPTICAL_SD),               # assumption
    "CRASH-2": CRASH2_ALL_CAUSE_DEATH,                                           # E-20
}


# ------------------------------------------------------------------------------------------------ scorecard

def beliefs(observed: pd.DataFrame, prior: float) -> np.ndarray:
    """Mean belief after the scan for every casualty, computed once per combination of findings."""
    keys = list(zip(observed["sbp"] <= TRIAGE_SBP_AT_OR_BELOW, observed["scan_free_fluid"].astype(object), observed["setting"]))
    cache: dict = {}
    out = np.empty(len(keys))
    for i, (reading, scan, setting) in enumerate(keys):
        key = (bool(reading), None if scan is pd.NA or scan is None else bool(scan), setting)
        if key not in cache:
            sbp = TRIAGE_SBP_AT_OR_BELOW if key[0] else TRIAGE_SBP_AT_OR_BELOW + 1
            casualty = {"sbp": sbp, "scan_free_fluid": key[1], "setting": setting}
            cache[key] = belief_line(casualty, prior)["scan"].mean()
        out[i] = cache[key]
    return out


@lru_cache(maxsize=None)
def evaluate(setting: str, prior: float | None = None) -> dict:
    """The lens on the generator's battle casualties in one setting (mechanism)."""
    observed, truth = _battle(*generator.sample(EVAL_N, EVAL_SEED, setting=setting, return_truth=True))
    target = truth["free_fluid"].to_numpy(bool)
    belief = beliefs(observed, prior_from_mix() if prior is None else prior)
    flagged = belief > EVACUATE_ABOVE
    return {
        "casualties": int(target.size),
        "sensitivity": float(flagged[target].mean()),
        "specificity": float((~flagged[~target]).mean()),
        "brier": float(np.mean((belief - target) ** 2)),
        "calibration": float(belief.mean() - target.mean()),
        "baseline": baseline.flag_metrics(baseline.priority_one(observed), target),
    }


DIAGNOSIS_METRICS = (
    ("sensitivity", "sensitivity, belief above one half"),
    ("specificity", "specificity, belief above one half"),
    ("brier", "Brier score"),
    ("calibration", "mean belief minus observed share"),
)


class BayesianLens:
    """Lens 03 behind the Lens interface (R-1.1)."""

    name = LENS_NAME

    def __init__(self, prior: float | None = None, crash3_path: str | Path | None = None) -> None:
        self.prior = prior
        self.crash3_path = None if crash3_path in (None, "") else str(crash3_path)

    def diagnose(self, casualty: Mapping[str, Any]) -> RV:
        """The belief that the casualty is bleeding into the abdomen, after triage and the scan."""
        return belief_line(casualty, self.prior)["scan"]

    def treat(self, casualty: Mapping[str, Any]) -> RV:
        """The belief handed to the treatment step, unchanged. This lens's treatment case is `reread_trial`."""
        return belief_line(casualty, self.prior)["treatment"]

    def scorecard(self) -> list[ScorecardRow]:
        rows = []
        for setting in SETTINGS:
            result = evaluate(setting, self.prior)
            for key, metric in DIAGNOSIS_METRICS:
                rows.append(ScorecardRow(LENS_NAME, "diagnosis", f"{metric}, {SETTING_NAMES[setting]}",
                                         round(result[key], 4), round(result["baseline"][key], 4), "mechanism",
                                         "native", "generator"))
        metric = "probability tranexamic acid reduces head injury death, CRASH-2 prior"
        fixture = reread_trial(summary_from_file(FIXTURE_CRASH3), PRIORS["CRASH-2"])
        rows.append(ScorecardRow(LENS_NAME, "treatment", metric, round(fixture.prob_benefit(), 4), NO_BASELINE,
                                 "mechanism", "weak", f"fixture:{FIXTURE_CRASH3.name}"))
        if self.crash3_path is not None:
            if not is_real_data_path(self.crash3_path, REPO_ROOT):
                raise ValueError("a real-data path must be an absolute path outside the repository")
            real = reread_trial(summary_from_file(self.crash3_path), PRIORS["CRASH-2"])
            rows.append(ScorecardRow(LENS_NAME, "treatment", metric, round(real.prob_benefit(), 4), NO_BASELINE,
                                     "evidence", "weak", self.crash3_path))
        return rows


LENS = BayesianLens()


# ------------------------------------------------------------------------------------------------ app page 1

def percent(x: float) -> str:
    return f"{100 * x:.0f}%"


def interval_text(rv: RV) -> str:
    lo, hi = rv.interval()
    return f"{percent(lo)} to {percent(hi)}"


@lru_cache(maxsize=None)
def _walk_sample(setting: str) -> tuple[pd.DataFrame, pd.DataFrame]:
    return _battle(*generator.sample(WALK_N, SEED, setting=setting, return_truth=True))


def casualties_available(patient_type: str, setting: str = "pre_hospital") -> int:
    _, truth = _walk_sample(setting)
    return int((truth["patient_type"] == patient_type).sum())


@dataclass(frozen=True)
class Walkthrough:
    patient_type: str
    setting: str
    prior: float
    casualty: int
    record: dict
    bleeding: bool
    line: dict
    reduction: RV
    band_name: str
    needs_lsi: bool = False
    significant_bleeding: bool = False

    def band(self) -> list[dict]:
        """The belief line as a band: mean and 95% interval at each step."""
        rows = []
        for order, step in enumerate(STEPS, start=1):
            rv = self.line[step]
            lo, hi = rv.interval()
            rows.append({"order": order, "step": STEP_NAMES[step], "mean": round(rv.mean(), 4),
                         "lo": round(lo, 4), "hi": round(hi, 4)})
        return rows

    def display(self) -> dict:
        """Every number the app shows for this casualty, already formatted (gate G-8 compares against it)."""
        scan = scan_result(self.record)
        scan_text = "not done" if scan is None else ("free fluid seen" if scan else "no free fluid seen")
        final = self.line["evacuation"]
        lo, hi = self.reduction.interval()
        before, after = TXA_FIRST_HOUR_DEATHS
        return {
            "metrics": {
                "Belief before any finding": percent(self.line["start"].mean()),
                "Belief after the scan": percent(final.mean()),
                "Chance the belief is above one half": percent(final.prob(lambda d: d > EVACUATE_ABOVE)),
                "Belief times relative reduction (mechanism)": f"{self.reduction.mean():.2f}",
                "CRASH-2 absolute reduction, within an hour (E-22)": f"{TXA_FIRST_HOUR_POINTS:.1f} points",
            },
            "treatment": (
                "Belief times relative reduction is the belief that this casualty is bleeding, multiplied by the "
                "relative reduction in death from bleeding for the delay, one minus the relative risk CRASH-2 found "
                "(E-22). This step applies "
                "a population average to one casualty's belief, so it is a modelling step and carries the mechanism "
                "label. It is a diagnosis result put to use, not a treatment result, and it is not a change in this "
                "casualty's risk of death. For scale, in CRASH-2 deaths from bleeding among those treated within an "
                f"hour were {before:.1f}% with placebo and {after:.1f}% with tranexamic acid, an absolute "
                f"reduction of {TXA_FIRST_HOUR_POINTS:.1f} points (E-19, E-22). CRASH-2 is civilian, so using its figures "
                "for a military casualty is an assumption."
            ),
            "table": [
                {"Step": STEP_NAMES[step], "Belief": percent(self.line[step].mean()),
                 "95% interval": interval_text(self.line[step]),
                 "Above one half": percent(self.line[step].prob(lambda d: d > EVACUATE_ABOVE))}
                for step in STEPS
            ],
            "findings": (
                f"Systolic pressure {int(self.record['sbp'])} mm Hg "
                f"({'at or below' if triage_reading(self.record) else 'above'} {TRIAGE_SBP_AT_OR_BELOW}). "
                f"Scan {SETTING_NAMES[self.setting]}: {scan_text}. "
                f"Time to pre-hospital care {self.record['t_phec_min']:.0f} minutes, so the tranexamic acid band is "
                f"{self.band_name}; belief times relative reduction is {self.reduction.mean():.2f} "
                f"({lo:.2f} to {hi:.2f}), a mechanism figure."
                + (" Below zero means harm: in this band CRASH-2 found more deaths from bleeding with tranexamic "
                   "acid, not fewer (E-22)." if self.reduction.mean() < 0 else "")
            ),
            "truth": ("In the generator this casualty is bleeding into the abdomen."
                      if self.bleeding else "In the generator this casualty is not bleeding into the abdomen."),
            "baseline": rules.panel(self.record, self.needs_lsi, self.significant_bleeding, percent(final.mean())),
            "scan_sources": SCAN_SOURCES,
            "band": self.band(),
        }


def walkthrough(patient_type: str = "haemorrhage", setting: str = "pre_hospital", prior: float | None = None,
                casualty: int = 1) -> Walkthrough:
    """One synthetic battle casualty of `patient_type`, followed along the belief line (app page 1, R-1.9)."""
    if patient_type not in PATIENT_TYPES:
        raise ValueError(f"patient type must be one of {PATIENT_TYPES}")
    observed, truth = _walk_sample(setting)
    rows = np.flatnonzero((truth["patient_type"] == patient_type).to_numpy())
    if not 1 <= casualty <= rows.size:
        raise ValueError(f"casualty must lie between 1 and {rows.size}")
    i = int(rows[casualty - 1])
    record = observed.iloc[i].to_dict()
    prior = default_prior() if prior is None else float(prior)
    line = belief_line(record, prior)
    band_name, _ = delay_band(float(record["t_phec_min"]))
    return Walkthrough(patient_type, setting, prior, casualty, record, bool(truth["free_fluid"].iloc[i]), line,
                       weighted_reduction(line["treatment"], float(record["t_phec_min"])), band_name,
                       bool(truth["needs_lsi"].iloc[i]), bool(truth["bleeding"].iloc[i]))
