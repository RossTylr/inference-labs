"""The MPTT-24, the rule-based baseline every lens is compared against (D-9; PRD R-2.1 to R-2.3).

Coded from the published flowchart as the register records it (E-08, Figure 2 of the corrected version of
record), six steps in this order and with these thresholds and no others:

    step 1  catastrophic haemorrhage    yes: Priority 1 (apply tourniquet or haemostatic dressing)
    step 2  walking                     yes: Priority 3
    step 3  breathing                   no:  Dead
    step 4  responds to voice           no:  Priority 1 (recovery position)
    step 5  respiratory rate 12 to 23   no:  Priority 1
    step 6  heart rate below 100        yes: Priority 2; no: Priority 1

The voice step is read two ways, because the paper's text and its figure differ for one group (E-08). The text
says 'responds to voice' replaces 'GCS below 14', the alert and voice boundary sitting at a median GCS of 13: on
that reading anything below alert leaves for Priority 1. Read literally, the figure lets a casualty who responds
only to voice go on to the next step.

    figure  the default. Only a casualty who does not respond to voice (P or U on the AVPU scale) leaves here.
    text    anything below alert (V, P or U) leaves here.

E-09's accuracy was measured on first recorded hospital respiratory rate and registry GCS, not on AVPU at the
scene (E-09, E-11). A GCS below 14 corresponds to the text reading, so the calibration check against E-09 is run
under that reading (R-2.3). It is a check that the generator's physiology is consistent with E-09, not evidence
about the rule.

The generator records no breathing check. A casualty without a `breathing` entry is taken as breathing: an
assumption.

Every result computed here on the generator is a mechanism, not evidence (D-8).
"""
from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache
from typing import Any, Mapping

import numpy as np
import pandas as pd

from inference_labs import generator
from inference_labs.interface import ScorecardRow

NAME = "MPTT-24"

P1, P2, P3, DEAD = "Priority 1", "Priority 2", "Priority 3", "Dead"
PRIORITIES = (P1, P2, P3, DEAD)

READINGS = ("figure", "text")
DEFAULT_READING = "figure"
CALIBRATION_READING = "text"         # the reading that matches the GCS below 14 on which E-09 was measured
READING_NAMES = {
    "figure": "the published figure: only a casualty who does not respond to voice is Priority 1 here",
    "text": "the paper's text: anything below alert is Priority 1 here",
}
VOICE_EXITS = {"figure": ("P", "U"), "text": ("V", "P", "U")}   # AVPU levels that leave at the voice step

RR_FROM, RR_TO = 12, 23              # E-08: respiratory rate 12 to 23 passes
HR_BELOW = 100                       # E-08: heart rate below 100 gives Priority 2

STEPS = (
    "catastrophic haemorrhage",
    "walking",
    "breathing",
    "responds to voice",
    f"respiratory rate {RR_FROM} to {RR_TO}",
    f"heart rate below {HR_BELOW}",
)
ACTIONS = {1: "apply a tourniquet or haemostatic dressing", 4: "recovery position"}   # E-08

EVAL_N, EVAL_SEED = 100_000, 42      # the synthetic casualties the scorecard and the calibration check use
SETTINGS = ("pre_hospital", "in_hospital")
SETTING_NAMES = {"pre_hospital": "scan before hospital", "in_hospital": "scan in hospital"}
COHORTS = ("military", "civilian")


def _check_reading(reading: str) -> None:
    if reading not in READINGS:
        raise ValueError(f"reading must be one of {READINGS}")


# ------------------------------------------------------------------------------------------------ the rule

@dataclass(frozen=True)
class Triage:
    """The rule's answer for one casualty: the priority, the step at which the casualty left, and the
    flowchart's instruction at that exit (empty where there is none)."""

    priority: str
    step: int
    action: str
    reading: str


def triage(casualty: Mapping[str, Any], reading: str = DEFAULT_READING) -> Triage:
    """One casualty through the six steps, in order. The first step that gives an answer ends the triage."""
    _check_reading(reading)

    def leave(priority: str, step: int) -> Triage:
        return Triage(priority, step, ACTIONS.get(step, "") if priority == P1 else "", reading)

    if bool(casualty["catastrophic_haemorrhage"]):
        return leave(P1, 1)
    if bool(casualty["walking"]):
        return leave(P3, 2)
    if not bool(casualty.get("breathing", True)):          # the generator records no breathing check: assumption
        return leave(DEAD, 3)
    if casualty["avpu"] in VOICE_EXITS[reading]:
        return leave(P1, 4)
    if not RR_FROM <= casualty["respiratory_rate"] <= RR_TO:
        return leave(P1, 5)
    if casualty["heart_rate"] < HR_BELOW:
        return leave(P2, 6)
    return leave(P1, 6)


def triage_table(observed: pd.DataFrame, reading: str = DEFAULT_READING) -> pd.DataFrame:
    """The same six steps for every row of a table of casualties at once: columns `priority` and `step`."""
    _check_reading(reading)
    n = len(observed)
    catastrophic = observed["catastrophic_haemorrhage"].to_numpy(bool)
    walking = observed["walking"].to_numpy(bool)
    breathing = observed["breathing"].to_numpy(bool) if "breathing" in observed else np.ones(n, bool)
    voice = np.isin(observed["avpu"].to_numpy(object), VOICE_EXITS[reading])
    rr = observed["respiratory_rate"].to_numpy(float)
    rr_passes = (rr >= RR_FROM) & (rr <= RR_TO)
    hr_passes = observed["heart_rate"].to_numpy(float) < HR_BELOW

    exits = [catastrophic, walking, ~breathing, voice, ~rr_passes]
    step = np.select(exits, [1, 2, 3, 4, 5], 6)
    priority = np.select(exits + [hr_passes], [P1, P3, DEAD, P1, P1, P2], P1)
    return pd.DataFrame({"priority": priority, "step": step}, index=observed.index)


def priority_one(observed: pd.DataFrame, reading: str = DEFAULT_READING) -> np.ndarray:
    """True where the rule gives Priority 1."""
    return (triage_table(observed, reading)["priority"] == P1).to_numpy()


def reading_changes(observed: pd.DataFrame) -> pd.DataFrame:
    """The casualties whose priority differs between the two readings of the voice step."""
    figure, text = triage_table(observed, "figure"), triage_table(observed, "text")
    differ = (figure["priority"] != text["priority"]).to_numpy()
    return pd.DataFrame({"figure": figure["priority"][differ], "text": text["priority"][differ]})


# ------------------------------------------------------------------------------------------------ measuring it

def flag_metrics(flag: np.ndarray, target: np.ndarray) -> dict:
    """A yes-or-no flag against a yes-or-no truth. A rule gives no probability, so its prediction is the flag
    itself: the Brier score is then the share misclassified, and calibration is the share flagged minus the
    share with the condition."""
    flag, target = np.asarray(flag, bool), np.asarray(target, bool)
    return {
        "casualties": int(target.size),
        "sensitivity": float(flag[target].mean()),
        "specificity": float((~flag[~target]).mean()),
        "brier": float(np.mean((flag.astype(float) - target) ** 2)),
        "calibration": float(flag.mean() - target.mean()),
    }


@lru_cache(maxsize=None)
def generator_sample(setting: str = "pre_hospital", cohort: str = "military") -> tuple[pd.DataFrame, pd.DataFrame]:
    """The synthetic casualties the lens is measured on: n = 100,000, seed 42, every stream (mechanism)."""
    return generator.sample(EVAL_N, EVAL_SEED, setting=setting, cohort=cohort, return_truth=True)


def calibration_check(cohort: str = "military") -> pd.DataFrame:
    """The coded rule against E-09 on the generator (R-2.3), under both readings. Only the text reading is held
    to E-09; the figure reading is shown beside it."""
    observed, truth = generator_sample("pre_hospital", cohort)
    param = generator.load_params()["parameters"][f"triage_accuracy_{cohort}"]
    rows = []
    for reading in READINGS:
        achieved = flag_metrics(priority_one(observed, reading), truth["needs_lsi"].to_numpy(bool))
        for key in ("sensitivity", "specificity"):
            tol = param["tolerance"][key] if isinstance(param["tolerance"], dict) else param["tolerance"]
            target, tol = float(param["value"][key]), float(tol)
            rows.append({"reading": reading, "measure": key, "E-09": target, "achieved": round(achieved[key], 4),
                         "tolerance": tol, "held to E-09": reading == CALIBRATION_READING,
                         "within tolerance": abs(achieved[key] - target) <= tol})
    return pd.DataFrame(rows)


DIAGNOSIS_METRICS = (
    ("sensitivity", "sensitivity"),
    ("specificity", "specificity"),
    ("brier", "Brier score"),
    ("calibration", "share flagged minus share in need"),
)


def diagnosis_metric(name: str, setting: str) -> str:
    return (f"{name}, Priority 1 against need for a life-saving intervention, generator physiology tuned to "
            f"accuracy measured on hospital observations, {SETTING_NAMES[setting]}")


@lru_cache(maxsize=None)
def diagnosis_results(setting: str, reading: str = DEFAULT_READING, cohort: str = "military") -> dict:
    """The rule on every synthetic casualty in one setting: Priority 1 against need for a life-saving
    intervention (mechanism). The generator draws the same physiology in either setting."""
    observed, truth = generator_sample(setting, cohort)
    return flag_metrics(priority_one(observed, reading), truth["needs_lsi"].to_numpy(bool))


def diagnosis_rows(lens: str = NAME, reading: str = DEFAULT_READING) -> list[ScorecardRow]:
    """Axes 1, 2 and 6 of D-21 for the rule's diagnosis case. The rule is its own baseline, so the baseline
    column repeats the value."""
    rows = []
    for setting in SETTINGS:
        result = diagnosis_results(setting, reading)
        for key, name in DIAGNOSIS_METRICS:
            value = round(result[key], 4)
            rows.append(ScorecardRow(lens, "diagnosis", diagnosis_metric(name, setting), value, value,
                                     "mechanism", "native", "generator"))
    return rows


# ------------------------------------------------------------------------------------------------ the lens

class MPTT24:
    """The MPTT-24 behind the Lens interface (R-0.8, R-2.1)."""

    name = NAME

    def __init__(self, reading: str = DEFAULT_READING) -> None:
        _check_reading(reading)
        self.reading = reading

    def diagnose(self, casualty: Mapping[str, Any]) -> Triage:
        """The priority, and the step at which the casualty left."""
        return triage(casualty, self.reading)

    def treat(self, casualty: Mapping[str, Any]) -> str:
        """The flowchart's own instruction at the casualty's exit, or an empty string where it gives none."""
        return triage(casualty, self.reading).action

    def scorecard(self) -> list[ScorecardRow]:
        return diagnosis_rows(NAME, self.reading)


LENS = MPTT24()
