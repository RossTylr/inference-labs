"""Lens 01, rules (PRD section 6.2; docs/background/01-rules.md).

A rule is a decision made in advance. What matters is where it came from, who it was written for, and what it
throws away.

Diagnosis. The MPTT-24, coded in `baseline.py` from E-08, with both readings of its voice step. The Military
Sieve is not coded: the register holds its performance (E-10), not its algorithm, so it appears here only as a
published operating point.

Treatment.
- The ABC score (E-31): four unweighted yes-or-no items, penetrating mechanism, positive scan, systolic pressure
  90 mm Hg or less, heart rate 120 or more. A score of 2 or more activates transfusion.
- US military resuscitation doctrine (E-86): three of four of systolic pressure under 100, heart rate over 100,
  haematocrit under 32% and pH under 7.25 predicts about a 70% risk of massive transfusion. Two of the four need a
  laboratory, so at the point of injury only the two bedside items can be read and the rule cannot be met.
- Tranexamic acid only if started within 3 hours of injury (E-86). CRASH-2's analysis by time to treatment (E-22)
  was exploratory (E-23), and CRASH-2 is civilian.

Failure. A rule meeting a population it was not written for: a needle of about 5 cm against a mean chest wall of
5.36 cm in 100 male military cases (E-104), and the field record (E-106); the MPTT-24 in a civilian registry
(E-09); the ABC score in a later cohort (E-90).

Assumptions, stated where used
- The generator does not record whether a wound is penetrating. Small arms injuries are counted as penetrating;
  explosion and other mechanisms are not.
- The generator has no node for massive transfusion. Significant bleeding stands in for the need for transfusion.
- The scan item of the ABC score is the generator's scan for free fluid, read in the setting where it was done.
- Chest wall thickness is taken as normally distributed with E-104's mean and standard deviation. The shape is an
  assumption, checked against E-104's 99% for an 8 cm catheter. A needle is taken to reach when it is longer than
  the chest wall is thick, ignoring angle and hub.

Every result on the generator carries the mechanism label (D-8). A published figure is given with its evidence
id and the population it was measured in; it describes the rule in that population, not the rule.
"""
from __future__ import annotations

import math
from dataclasses import dataclass
from functools import lru_cache
from typing import Any, Mapping

import numpy as np
import pandas as pd
from scipy.stats import norm

from inference_labs import baseline
from inference_labs.baseline import DEFAULT_READING, SETTING_NAMES, SETTINGS
from inference_labs.interface import ScorecardRow

LENS_NAME = "Rules"

# ------------------------------------------------------------------------------------------------ the ABC score (E-31)

ABC_SBP_AT_OR_BELOW = 90
ABC_HR_AT_OR_ABOVE = 120
ABC_ACTIVATES_AT = 2
PENETRATING = ("small_arms",)        # assumption: the generator does not record penetration
ABC_ITEMS = ("penetrating mechanism", "positive scan", f"systolic pressure {ABC_SBP_AT_OR_BELOW} mm Hg or less",
             f"heart rate {ABC_HR_AT_OR_ABOVE} or more")


def _scan_positive(value: Any) -> bool:
    """A missing scan is not a positive one."""
    if value is None or value is pd.NA or (isinstance(value, float) and math.isnan(value)):
        return False
    return bool(value)


def abc_items(casualty: Mapping[str, Any]) -> dict[str, bool]:
    """The four items of the ABC score for one casualty."""
    return {
        ABC_ITEMS[0]: casualty["mechanism"] in PENETRATING,
        ABC_ITEMS[1]: _scan_positive(casualty.get("scan_free_fluid")),
        ABC_ITEMS[2]: casualty["sbp"] <= ABC_SBP_AT_OR_BELOW,
        ABC_ITEMS[3]: casualty["heart_rate"] >= ABC_HR_AT_OR_ABOVE,
    }


def abc_score(casualty: Mapping[str, Any]) -> int:
    return int(sum(abc_items(casualty).values()))


def abc_table(observed: pd.DataFrame) -> pd.DataFrame:
    """The four items and the score for every row of a table of casualties at once."""
    items = pd.DataFrame({
        ABC_ITEMS[0]: observed["mechanism"].isin(PENETRATING).to_numpy(),
        ABC_ITEMS[1]: observed["scan_free_fluid"].astype("boolean").fillna(False).to_numpy(bool),
        ABC_ITEMS[2]: (observed["sbp"] <= ABC_SBP_AT_OR_BELOW).to_numpy(),
        ABC_ITEMS[3]: (observed["heart_rate"] >= ABC_HR_AT_OR_ABOVE).to_numpy(),
    }, index=observed.index)
    items["score"] = items[list(ABC_ITEMS)].sum(axis=1).astype(int)
    return items


# ------------------------------------------------------------------------------------------------ doctrine (E-86)

DOCTRINE_SBP_BELOW = 100
DOCTRINE_HR_ABOVE = 100
DOCTRINE_LABORATORY_ITEMS = ("haematocrit under 32%", "pH under 7.25")
DOCTRINE_NEEDS = 3                   # three of four predicts about a 70% risk of massive transfusion
TXA_WITHIN_MIN = 180                 # tranexamic acid only if started within 3 hours of injury


def doctrine_bedside_items(casualty: Mapping[str, Any]) -> int:
    """How many of the doctrine rule's two bedside items are present. The other two need a laboratory."""
    return int(casualty["sbp"] < DOCTRINE_SBP_BELOW) + int(casualty["heart_rate"] > DOCTRINE_HR_ABOVE)


def doctrine_bedside_table(observed: pd.DataFrame) -> pd.Series:
    return ((observed["sbp"] < DOCTRINE_SBP_BELOW).astype(int) + (observed["heart_rate"] > DOCTRINE_HR_ABOVE).astype(int))


def txa_inside(minutes_from_injury: float) -> bool:
    """The doctrine's three-hour rule: give tranexamic acid only if it can be started within 3 hours of injury."""
    return bool(minutes_from_injury <= TXA_WITHIN_MIN)


# E-22: deaths from bleeding in CRASH-2 by time from injury to treatment, tranexamic acid against placebo, per
# cent, with the relative risk and its interval. An exploratory analysis (E-23) of a civilian trial.
E22_BANDS = (
    {"band": "up to 1 hour", "tranexamic acid": 5.3, "placebo": 7.7, "rr": (0.68, 0.57, 0.82)},
    {"band": "1 to 3 hours", "tranexamic acid": 4.8, "placebo": 6.1, "rr": (0.79, 0.64, 0.97)},
    {"band": "over 3 hours", "tranexamic acid": 4.4, "placebo": 3.1, "rr": (1.44, 1.12, 1.84)},
)


# ------------------------------------------------------------------------------------------------ published figures

@dataclass(frozen=True)
class OperatingPoint:
    """A published sensitivity and specificity, with the population it was measured in."""

    rule: str
    population: str
    sensitivity: float
    specificity: float
    source: str
    prevalence: float | None = None
    ppv: float | None = None


JTTR = "UK military registry (JTTR), 3,654 adults, 2006 to 2013"
TARN = "civilian registry (TARN), 127,233 patients"
PUBLISHED = {
    "MPTT-24, military": OperatingPoint("MPTT-24", JTTR, 0.667, 0.699, "E-09", prevalence=0.476, ppv=0.670),
    "MPTT-24, civilian": OperatingPoint("MPTT-24", TARN, 0.535, 0.748, "E-09", prevalence=0.195, ppv=0.340),
    "Military Sieve, military": OperatingPoint("Military Sieve", JTTR, 0.432, 0.937, "E-10"),
    "Military Sieve, civilian": OperatingPoint("Military Sieve", TARN, 0.280, 0.941, "E-10"),
    "ABC score, 596 patients": OperatingPoint("ABC score", "596 patients, 12.4% massively transfused", 0.75, 0.86, "E-31",
                                          prevalence=0.124),
    "ABC score, 2,438 patients": OperatingPoint("ABC score", "2,438 patients, 4.9% massively transfused", 0.36, 0.80, "E-90",
                                       prevalence=0.049),
}
HOSPITAL_OBSERVATIONS = ("measured on first recorded hospital observations and registry GCS, not at the point of "
                         "injury (E-09, E-11)")


def ppv(sensitivity: float, specificity: float, prevalence: float) -> float:
    """Positive predictive value from accuracy and the share with the condition (Bayes' rule)."""
    hit = sensitivity * prevalence
    return hit / (hit + (1 - specificity) * (1 - prevalence))


# ------------------------------------------------------------------------------------------------ the needle (E-104, E-106)

CHEST_WALL_MEAN_CM, CHEST_WALL_SD_CM = 5.36, 1.19   # E-104: CT of 100 male military cases
NEEDLE_CM = 5.0                                       # E-104: a recommended needle of about 5 cm
CATHETER_CM = 8.0                                     # E-104
CATHETER_REACH_PUBLISHED = 0.99                       # E-104: an 8 cm catheter would reach in 99%
FIELD_DECOMPRESSIONS = 111                            # E-106, 1997 to 2012
FIELD_AT_POINT_OF_INJURY = 0.79                       # E-106
FIELD_THEN_CHEST_TUBE = 0.32                          # E-106: a chest tube then placed in the field


def needle_reaches(length_cm: float) -> float:
    """Share of chest walls thinner than the needle is long, under the assumed normal shape."""
    return float(norm.cdf((length_cm - CHEST_WALL_MEAN_CM) / CHEST_WALL_SD_CM))


def chest_walls(n: int = 100, seed: int = 42) -> np.ndarray:
    """`n` chest wall thicknesses in cm drawn from the assumed normal shape (synthetic)."""
    return np.random.default_rng(seed).normal(CHEST_WALL_MEAN_CM, CHEST_WALL_SD_CM, n)


# ------------------------------------------------------------------------------------------------ the generator

def _battle(observed: pd.DataFrame, truth: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    keep = (observed["stream"] == "battle").to_numpy()
    return observed[keep].reset_index(drop=True), truth[keep].reset_index(drop=True)


@lru_cache(maxsize=None)
def battle_sample(setting: str = "pre_hospital", cohort: str = "military") -> tuple[pd.DataFrame, pd.DataFrame]:
    """The battle casualties among the generator's 100,000 (seed 42); only they are scanned."""
    return _battle(*baseline.generator_sample(setting, cohort))


@lru_cache(maxsize=None)
def treatment_results(setting: str, reading: str = DEFAULT_READING) -> dict:
    """The ABC score on the generator's battle casualties, against significant bleeding (mechanism), with the
    MPTT-24's Priority 1 scored against the same target as the baseline."""
    observed, truth = battle_sample(setting)
    target = truth["bleeding"].to_numpy(bool)
    activated = (abc_table(observed)["score"] >= ABC_ACTIVATES_AT).to_numpy()
    return {"abc": baseline.flag_metrics(activated, target),
            "mptt24": baseline.flag_metrics(baseline.priority_one(observed, reading), target)}


TREATMENT_METRICS = baseline.DIAGNOSIS_METRICS


def treatment_metric(name: str, setting: str) -> str:
    return f"{name}, ABC score 2 or more against significant bleeding, battle casualties, {SETTING_NAMES[setting]}"


# ------------------------------------------------------------------------------------------------ the lens

@dataclass(frozen=True)
class Treatment:
    """What the treatment rules say for one casualty.

    tranexamic_acid_time_condition_met, when true: inside 3 hours, so the time limit in the guideline (E-86) is met.
    The limit is a condition for giving tranexamic acid, not an instruction to give it.
    """

    abc_score: int
    transfusion: bool
    doctrine_bedside_items: int
    tranexamic_acid_time_condition_met: bool


class RulesLens:
    """Lens 01 behind the Lens interface: the MPTT-24 for diagnosis, the ABC score and the doctrine's three-hour
    rule for treatment."""

    name = LENS_NAME

    def __init__(self, reading: str = DEFAULT_READING) -> None:
        self.reading = reading

    def diagnose(self, casualty: Mapping[str, Any]) -> baseline.Triage:
        return baseline.triage(casualty, self.reading)

    def treat(self, casualty: Mapping[str, Any]) -> Treatment:
        score = abc_score(casualty)
        return Treatment(score, score >= ABC_ACTIVATES_AT, doctrine_bedside_items(casualty),
                         txa_inside(float(casualty["t_phec_min"])))

    def scorecard(self) -> list[ScorecardRow]:
        rows = baseline.diagnosis_rows(LENS_NAME, self.reading)
        for setting in SETTINGS:
            result = treatment_results(setting, self.reading)
            for key, name in TREATMENT_METRICS:
                rows.append(ScorecardRow(LENS_NAME, "treatment", treatment_metric(name, setting),
                                         round(result["abc"][key], 4), round(result["mptt24"][key], 4),
                                         "mechanism", "native", "generator"))
        return rows


LENS = RulesLens()


def _pct(x: float) -> str:
    return f"{100 * x:.1f}%"


def seven_axes(reading: str = DEFAULT_READING) -> pd.DataFrame:
    """The scorecard on the seven axes of D-21. Axes 1, 2 and 6 are computed on the generator (mechanism); axes 3,
    4 and 5 are stated; axis 7 is net benefit at the threshold lens 10's default costs set (mechanism)."""
    from inference_labs.lenses import decision

    pre_dx, in_dx = (baseline.diagnosis_results(s, reading) for s in SETTINGS)
    observed, truth = baseline.generator_sample()
    battle_obs, battle_truth = battle_sample("pre_hospital")
    pre_tx, in_tx = (treatment_results(s, reading)["abc"] for s in SETTINGS)

    def disc(r):
        return f"sensitivity {_pct(r['sensitivity'])}, specificity {_pct(r['specificity'])}"

    def cal(r):
        gap = r["calibration"]
        side = "more" if gap > 0 else "fewer"
        return (f"Brier {r['brier']:.3f}; it flags {100 * abs(gap):.1f} points {side} of the casualties than are in "
                f"need (share flagged minus share in need {gap:+.3f})")

    rows = [
        ("1 Discrimination (mechanism)",
         f"{disc(pre_dx)}: Priority 1 against need for a life-saving intervention, all 100,000 synthetic casualties, "
         "disease included",
         f"{disc(pre_tx)}: score 2 or more against significant bleeding, battle casualties, scan before hospital"),
        ("2 Calibration (mechanism)",
         f"{cal(pre_dx)}. A rule gives no probability, so the Brier score is the share misclassified",
         f"{cal(pre_tx)}"),
        ("3 Uncertainty expressed", "None: a priority, not a probability or an interval",
         "None: activate or not"),
        ("4 What it needed",
         "Rules only at the point of use. Its thresholds descend from the MPTT, derived by logistic regression on "
         "3,654 patients with complete data (E-01, E-02, E-08)",
         "Rules only at the point of use. Its published accuracy, 75% sensitive and 86% specific at a score of 2 "
         "or more, comes from 596 patients (E-31)"),
        ("5 Readability", "A medic can follow it at the point of care: six yes-or-no steps, one observation each",
         "A medic can follow it: four yes-or-no items, counted"),
        ("6 Robustness, setting changed (mechanism)",
         f"With the scan in hospital: {disc(in_dx)}; {cal(in_dx)}. Unchanged, because the generator draws the same "
         "physiology in either setting, so this axis cannot show what moving from hospital observations to the "
         "point of injury would do (E-11)",
         f"With the scan in hospital: {disc(in_tx)}; {cal(in_tx)}. The scan item is more often right in hospital"),
        ("7 Decision value", decision.decision_value(baseline.priority_one(observed, reading), truth["needs_lsi"],
                                                     battle=(observed["stream"] == "battle").to_numpy()),
         decision.decision_value(abc_table(battle_obs)["score"].to_numpy() >= ABC_ACTIVATES_AT, battle_truth["bleeding"]) +
         ", against significant bleeding, battle casualties, scan before hospital"),
    ]
    return pd.DataFrame(rows, columns=["axis", "diagnosis: MPTT-24", "treatment: ABC score"]).set_index("axis")


# ------------------------------------------------------------------------------------------------ app page 1

def _yes(flag: bool) -> str:
    return "yes" if flag else "no"


def panel(record: Mapping[str, Any], needs_lsi: bool, significant_bleeding: bool, belief_after_scan: str) -> dict:
    """The rules panel for one synthetic casualty on app page 1. Every number is formatted here, so the page shows
    only what the library computed (gate G-8)."""
    figure = baseline.triage(record, "figure")
    text = baseline.triage(record, "text")
    steps = [
        f"Step 1, catastrophic haemorrhage: {_yes(bool(record['catastrophic_haemorrhage']))}.",
        f"Step 2, walking: {_yes(bool(record['walking']))}.",
        "Step 3, breathing: yes, taken as breathing because the generator records no breathing check (an assumption).",
        f"Step 4, responds to voice: AVPU level {record['avpu']}.",
        f"Step 5, respiratory rate {baseline.RR_FROM} to {baseline.RR_TO}: {int(record['respiratory_rate'])} breaths "
        f"a minute, {_yes(baseline.RR_FROM <= record['respiratory_rate'] <= baseline.RR_TO)}.",
        f"Step 6, heart rate below {baseline.HR_BELOW}: {int(record['heart_rate'])} beats a minute, "
        f"{_yes(record['heart_rate'] < baseline.HR_BELOW)}.",
    ][:figure.step]
    priority = (f"MPTT-24, reading the published figure (the default): {figure.priority}, at step {figure.step}. "
                f"Reading the paper's text, where anything below alert is Priority 1: {text.priority}, at step "
                f"{text.step}.")
    if figure.priority != text.priority:
        priority += " The two readings disagree for this casualty."
    action = f"The flowchart's instruction at this exit: {figure.action}." if figure.action else ""

    items = abc_items(record)
    score = sum(items.values())
    setting = SETTING_NAMES[record["setting"]]
    transfusion = (
        f"Transfusion, ABC score (E-31): penetrating mechanism {_yes(items[ABC_ITEMS[0]])} (small arms counted as "
        f"penetrating, an assumption); positive {setting} {_yes(items[ABC_ITEMS[1]])}; systolic pressure "
        f"{int(record['sbp'])} mm Hg, {ABC_SBP_AT_OR_BELOW} or less {_yes(items[ABC_ITEMS[2]])}; heart rate "
        f"{int(record['heart_rate'])}, {ABC_HR_AT_OR_ABOVE} or more {_yes(items[ABC_ITEMS[3]])}. Score {score} of 4: "
        f"{'activates' if score >= ABC_ACTIVATES_AT else 'does not activate'} transfusion, which needs "
        f"{ABC_ACTIVATES_AT} or more. The score's published accuracy, 75% sensitive and 86% specific at a score of 2 "
        f"or more, comes from 596 patients (E-31). The register does not describe them as military, so applying the "
        f"score to a military casualty is an assumption. The score "
        f"counts a positive scan as one point and a clear or missing scan as none, whatever the belief after it; the "
        f"Bayesian panel's belief after the scan is {belief_after_scan}."
    )
    bleeding = ("In the generator this casualty is bleeding significantly, the stand-in here for needing "
                "transfusion (an assumption)." if significant_bleeding else
                "In the generator this casualty is not bleeding significantly, the stand-in here for needing "
                "transfusion (an assumption).")
    minutes = float(record["t_phec_min"])
    condition = (". Inside 3 hours, so the time limit in the guideline (E-86) is met. The limit is a condition for "
                 "giving tranexamic acid, not an instruction to give it."
                 if txa_inside(minutes) else ": outside 3 hours, so the rule withholds it.")
    txa = (
        f"Tranexamic acid, US military resuscitation doctrine (E-86): given only if started within 3 hours of "
        f"injury. Time to pre-hospital care {minutes:.0f} minutes{condition}"
    )
    mil, civ, sieve = PUBLISHED["MPTT-24, military"], PUBLISHED["MPTT-24, civilian"], PUBLISHED["Military Sieve, military"]
    published = (
        f"Published accuracy, {HOSPITAL_OBSERVATIONS}. In the {JTTR}, the MPTT-24 had sensitivity "
        f"{_pct(mil.sensitivity)} and specificity {_pct(mil.specificity)} for Priority 1, and the Military Sieve "
        f"{_pct(sieve.sensitivity)} and {_pct(sieve.specificity)} (E-10). In the {TARN}, the MPTT-24 had "
        f"{_pct(civ.sensitivity)} and {_pct(civ.specificity)}. Each figure belongs to its registry, not to the rule."
    )
    return {
        "heading": "Rules panel, the baseline: which priority, and which treatment rules fire?",
        "priority": priority,
        "steps": steps,
        "action": action,
        "truth": ("In the generator this casualty needs a life-saving intervention." if needs_lsi else
                  "In the generator this casualty does not need a life-saving intervention."),
        "transfusion": transfusion,
        "bleeding": bleeding,
        "txa": txa,
        "published": published,
    }


def page_panel(walk: Any) -> dict:
    """The rules panel on app page 1 for one walk-through casualty, given lens 03's Walkthrough (D-27): every
    number already formatted, so the page shows only what the library computed (gate G-8)."""
    from inference_labs.lenses.bayesian import percent

    return panel(walk.record, walk.needs_lsi, walk.significant_bleeding, percent(walk.line["evacuation"].mean()))
