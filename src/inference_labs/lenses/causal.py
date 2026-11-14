"""Lens 07, causal inference (PRD section 6.7; docs/background/07-causal.md).

Seeing that treated casualties did better is not knowing that treatment made them better. The generator allocates
tranexamic acid by a coin and holds both of each casualty's outcomes, with and without the drug, so the true effect
is known here, and only because the generator was built with it. The lens builds an observational record from the
same casualties and asks how far each way of reading that record lands from the truth.

    diagnosis   the casualty's scan result for free fluid, with the scan's sensitivity and specificity as measured
                under two constructed selections and as they are on every casualty (weak fit)
    treatment   for a battle casualty's delay band, the effect of tranexamic acid on death from bleeding estimated
                naively and with adjustment, beside its true value

Where the numbers come from
- The casualties are the generator's battle casualties alive at pre-hospital care, judged by its outcome without
  tranexamic acid. Each one's outcome is read from the generator's two potential outcomes: death from bleeding with
  the drug if treated, without it if not. The true effect is the difference between the two, averaged over the same
  casualties.
- The constructed allocation is an assumption, labelled constructed. The chance of treatment rises with four
  recorded signs (heart rate 100 or more, systolic pressure 90 or less, below alert, catastrophic haemorrhage) and
  with one variable a record would not hold: how heavily the casualty is bleeding, the generator's severity centile
  for a casualty bleeding significantly and zero for one who is not. A strength multiplies every arrow into
  treatment; at strength zero the chance is one half for everyone, a coin, as in the generator's own allocation.
- Adjustment is inverse probability weighting: the chance of treatment fitted by logistic regression on the
  variables named, each arm weighted by one over its fitted chance, and the weighted shares compared.
- Survival bias, in the failure, reads each casualty's outcome as if untreated, so the drug has no effect. The
  generator's death times run from injury on a hazard fitted to E-85, measured from hospital admission: an
  assumption.
- Scan accuracy is the generator's: before hospital set from E-16, a civilian helicopter service; in hospital from
  E-14's pooled figures. Both are applied to battle casualties, an assumption. The two selections, who is scanned
  and whose true state is confirmed, are constructed and are assumptions.
- The twelve casualties counted by hand are the generator's; the stratified table beside them is constructed.

Every result computed on the generator is a mechanism, not evidence (D-8).
"""
from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache
from typing import Any, Mapping

import numpy as np
import pandas as pd
from scipy.special import expit, ndtr
from sklearn.linear_model import LogisticRegression

from inference_labs import baseline, generator
from inference_labs.interface import ScorecardRow
from inference_labs.lenses import decision, rules, stochastic

NAME = "Causal inference"
NO_BASELINE = float("nan")         # the MPTT-24 states no effect of a treatment
SETTINGS = baseline.SETTINGS
SETTING_NAMES = baseline.SETTING_NAMES
EVAL_N, EVAL_SEED = baseline.EVAL_N, baseline.EVAL_SEED     # 100,000 synthetic casualties, seed 42
SEEDS = 20                         # further samples behind every spread, seeds 43 onward
ALLOCATION_SEED = 1000             # the constructed allocation's coin for a sample is seeded with this plus its seed
VERIFY_SEED = 2000                 # the coin deciding which negative scans are confirmed, likewise
BANDS = tuple(b[0] for b in stochastic.E22_BANDS)      # up to 1 hour, 1 to 3 hours, over 3 hours
ALL = "every delay"

# ------------------------------------------------------------------------------------------------ published figures

# E-19, E-21: CRASH-2, a civilian trial.
CRASH2 = {"randomised": 20_211, "hospitals": 274, "countries": 40, "within_h": 8, "analysed": (10_060, 10_067),
          "bleeding_deaths": (489, 574), "shown": (4.9, 5.7), "rr": (0.85, 0.76, 0.96)}
# E-20: CRASH-2 all-cause mortality and blood products.
E20 = {"deaths": (1_463, 1_613), "shown": (14.5, 16.0), "rr": (0.91, 0.85, 0.97),
       "blood": (50.4, 51.3), "blood_rr": (0.98, 0.96, 1.01)}
# E-71: MATTERs, a Role 3 hospital in southern Afghanistan.
E71 = {"casualties": 896, "given": 293, "mortality": (17.4, 23.9), "iss": (25.2, 22.5), "massive": (14.4, 28.1),
       "or_survival": (7.228, 3.016, 17.322)}
# E-80: 134 massively transfused patients.
E80 = {"patients": 134, "fixed": (0.37, 0.22, 0.64), "changing": (0.84, 0.47, 1.50), "first_6h": 54}
# E-81: 21,089 US casualties, Afghanistan, 2001 to 2014.
E81 = {"casualties": 21_089, "kia_before": (386, 2_411, 16.0), "kia_after": (964, 9_755, 9.9),
       "dow": (4.1, 4.3), "dow_p": 0.71, "lives_saved": 359, "transfused": (40, 589, 6.8),
       "not_transfused": (249, 488, 51.0), "matched": 37.3}
# E-117: three tasks of data science, with its worked example from health records.
E117 = (("description", "How can women with a history of stroke be grouped?"),
        ("prediction", "What is the probability of a stroke next year?"),
        ("counterfactual prediction", "Will starting a statin reduce the risk?"))
# E-120: trained on one hospital's database, tested on 128 hospitals.
E120 = {"trained": 17_083, "tested": 79_073, "hospitals": 128}
# E-123: 4,542 US casualties, Afghanistan, 2001 to 2014; odds of being killed in action for military ISS of 25 or more.
E123 = {"casualties": 4_542, "trend": (0.99, 0.94, 1.03), "transfusion": (0.17, 0.06, 0.51),
        "surgical_team": (0.67, 0.58, 0.78), "transport": (0.61, 0.51, 0.74), "more_kia": (135, 105, 164),
        "rivals": 5}


def _pct(x: float, places: int = 1) -> str:
    return f"{100 * x:.{places}f}%"


def spread_words(differences, places: int = 2, unit: str = "") -> str:
    """A difference with its spread across seeds: a tie where the spread covers no difference."""
    return stochastic.spread_words(differences, places, unit)


# ------------------------------------------------------------------------------------------------ the casualties

@lru_cache(maxsize=2 * SEEDS + 4)
def _sample(seed: int = EVAL_SEED, n: int = EVAL_N, setting: str = "pre_hospital"):
    if seed == EVAL_SEED and n == EVAL_N:
        return baseline.generator_sample(setting)
    return generator.sample(n, seed, setting=setting, return_truth=True)


@lru_cache(maxsize=2 * SEEDS + 4)
def at_care(seed: int = EVAL_SEED, n: int = EVAL_N) -> tuple[pd.DataFrame, pd.DataFrame]:
    """The battle casualties alive at pre-hospital care, judged by the generator's outcome without tranexamic acid:
    those whose bleeding death falls at or before that time are not there to be treated."""
    observed, truth = _sample(seed, n)
    keep = (observed["stream"] == "battle").to_numpy() & decision.alive_at_triage(observed, truth)
    return observed[keep].reset_index(drop=True), truth[keep].reset_index(drop=True)


# ------------------------------------------------------------------------------------------------ the allocation

SIGNS = ("heart rate 100 or more", "systolic pressure 90 or less", "below alert", "catastrophic haemorrhage")
HIDDEN = "how heavily bleeding, as seen at the wound"
# The constructed allocation (an assumption): log odds of being given tranexamic acid, each term multiplied by the
# strength of the arrow into treatment.
ALLOCATION = {"intercept": -1.5, "heart rate 100 or more": 1.0, "systolic pressure 90 or less": 1.0,
              "below alert": 1.0, "catastrophic haemorrhage": 1.0, HIDDEN: 2.0}
DEFAULT_STRENGTH = 1.0
STRENGTHS = tuple(np.round(np.arange(0.0, 1.51, 0.25), 2))


def signs(observed: pd.DataFrame) -> pd.DataFrame:
    """The four recorded signs the constructed allocation reads, each as yes (1) or no (0)."""
    return pd.DataFrame({
        "heart rate 100 or more": (observed["heart_rate"] >= 100).to_numpy(float),
        "systolic pressure 90 or less": (observed["sbp"] <= 90).to_numpy(float),
        "below alert": (observed["avpu"] != "A").to_numpy(float),
        "catastrophic haemorrhage": observed["catastrophic_haemorrhage"].to_numpy(float),
    }, index=observed.index)


def hidden(truth: pd.DataFrame) -> np.ndarray:
    """The variable a record would not hold: the generator's severity centile for a casualty bleeding significantly,
    zero for one who is not."""
    bleeding = truth["bleeding"].to_numpy(bool)
    return np.where(bleeding, ndtr(np.nan_to_num(truth["severity"].to_numpy(float))), 0.0)


def chance_of_treatment(observed: pd.DataFrame, truth: pd.DataFrame, strength: float = DEFAULT_STRENGTH) -> np.ndarray:
    """Each casualty's chance of being given tranexamic acid under the constructed allocation. At strength zero it is
    one half for everyone."""
    x = signs(observed).to_numpy() @ np.array([ALLOCATION[s] for s in SIGNS])
    return expit(strength * (ALLOCATION["intercept"] + x + ALLOCATION[HIDDEN] * hidden(truth)))


def allocate(observed: pd.DataFrame, truth: pd.DataFrame, strength: float = DEFAULT_STRENGTH,
             seed: int = EVAL_SEED) -> np.ndarray:
    """Who is given the drug under the constructed allocation. The coin is the same whatever the strength, so changing
    the strength changes only the chances it is compared with."""
    u = np.random.default_rng(ALLOCATION_SEED + seed).random(len(observed))
    return u < chance_of_treatment(observed, truth, strength)


def outcome(truth: pd.DataFrame, treated: np.ndarray) -> np.ndarray:
    """Death from bleeding, read from the generator's two potential outcomes: with the drug if treated, without if
    not."""
    return np.where(treated, truth["died_if_treated"].to_numpy(bool), truth["died_if_untreated"].to_numpy(bool))


@dataclass(frozen=True)
class Estimate:
    """Deaths from bleeding per 100, with tranexamic acid and without it."""

    with_drug: float
    without: float

    @property
    def difference(self) -> float:
        """With less without, per 100: below zero, fewer deaths with the drug."""
        return self.with_drug - self.without

    @property
    def relative_risk(self) -> float:
        return self.with_drug / self.without if self.without > 0 else float("nan")

    def direction(self) -> str:
        """The difference in words, so that harm reads as more deaths with the drug and not as a sign."""
        d = self.difference
        if round(d, 2) == 0:
            return "no difference to two decimal places"
        return (f"{abs(d):.2f} more deaths per 100 with the drug" if d > 0 else
                f"{abs(d):.2f} fewer deaths per 100 with the drug")

    def words(self) -> str:
        rr = self.relative_risk
        ratio = "relative risk not defined" if np.isnan(rr) else f"relative risk {rr:.2f}"
        return (f"{self.with_drug:.2f} per 100 with the drug against {self.without:.2f} without: "
                f"{self.direction()} ({ratio})")


def true_effect(truth: pd.DataFrame, mask: np.ndarray) -> Estimate:
    """Both potential outcomes of the same casualties: what only the generator can give."""
    return Estimate(100 * float(truth["died_if_treated"].to_numpy(bool)[mask].mean()),
                    100 * float(truth["died_if_untreated"].to_numpy(bool)[mask].mean()))


def naive(treated: np.ndarray, died: np.ndarray, mask: np.ndarray) -> Estimate:
    """The share who died among those given the drug against the share among those not given it."""
    t, d = treated[mask], died[mask]
    return Estimate(100 * float(d[t].mean()), 100 * float(d[~t].mean()))


def fitted_chance(variables: np.ndarray, treated: np.ndarray) -> np.ndarray:
    """The chance of treatment fitted by logistic regression on the variables given, practically unpenalised."""
    model = LogisticRegression(C=1e6, max_iter=2000).fit(variables, treated)
    return model.predict_proba(variables)[:, 1]


def weighted(treated: np.ndarray, died: np.ndarray, chance: np.ndarray, mask: np.ndarray) -> Estimate:
    """Inverse probability weighting: each arm weighted by one over its chance of being in that arm."""
    t, d, e = treated[mask], died[mask].astype(float), chance[mask]
    w1, w0 = t / e, (~t) / (1 - e)
    return Estimate(100 * float((w1 * d).sum() / w1.sum()), 100 * float((w0 * d).sum() / w0.sum()))


def band_masks(observed: pd.DataFrame) -> dict[str, np.ndarray]:
    """Every delay, and each of E-22's three bands of time from injury to pre-hospital care, when the drug is given."""
    band = stochastic.band_index(observed["t_phec_min"].to_numpy(float))
    return {ALL: np.ones(len(observed), bool), **{name: band == k for k, name in enumerate(BANDS)}}


ESTIMATORS = ("naive", "adjusted for every variable the allocation uses", "adjusted on the recorded signs alone",
              "true value")


@lru_cache(maxsize=None)
def estimates(seed: int = EVAL_SEED, n: int = EVAL_N, strength: float = DEFAULT_STRENGTH) -> dict:
    """On the battle casualties alive at pre-hospital care under the constructed allocation: the effect of tranexamic
    acid on death from bleeding, for every delay and in each band, estimated naively, with adjustment for every
    variable the allocation uses, with adjustment on the recorded signs alone, and its true value (mechanism)."""
    observed, truth = at_care(seed, n)
    treated = allocate(observed, truth, strength, seed)
    died = outcome(truth, treated)
    recorded = signs(observed).to_numpy()
    full = fitted_chance(np.column_stack([recorded, hidden(truth)]), treated)
    partial = fitted_chance(recorded, treated)
    out = {"casualties": len(observed), "given": int(treated.sum()), "strength": strength}
    for name, mask in band_masks(observed).items():
        out[name] = {"casualties": int(mask.sum()), "given": int(treated[mask].sum()), "deaths": int(died[mask].sum()),
                     "naive": naive(treated, died, mask),
                     "adjusted for every variable the allocation uses": weighted(treated, died, full, mask),
                     "adjusted on the recorded signs alone": weighted(treated, died, partial, mask),
                     "true value": true_effect(truth, mask)}
    return out


@lru_cache(maxsize=None)
def estimate_spread(strength: float = DEFAULT_STRENGTH) -> pd.DataFrame:
    """estimates on SEEDS further samples of 100,000 (seeds 43 onward): each estimate's difference per 100, less the
    true value's, for every delay and each band."""
    rows = []
    for k in range(SEEDS):
        seed = EVAL_SEED + 1 + k
        r = estimates(seed, EVAL_N, strength)
        for band in (ALL,) + BANDS:
            truth = r[band]["true value"].difference
            for name in ESTIMATORS:
                rows.append({"seed": seed, "band": band, "estimator": name, "difference": r[band][name].difference,
                             "less true": r[band][name].difference - truth, "casualties": r[band]["casualties"]})
    return pd.DataFrame(rows)


def spread_of(band: str, estimator: str, strength: float = DEFAULT_STRENGTH) -> pd.Series:
    table = estimate_spread(strength)
    return table[(table["band"] == band) & (table["estimator"] == estimator)].set_index("seed")["less true"]


def estimate_table(band: str = ALL, strength: float = DEFAULT_STRENGTH) -> pd.DataFrame:
    """The four readings for one band in the evaluation sample, each with its distance from the true value across
    the further samples."""
    r = estimates(strength=strength)[band]
    rows = {}
    for name in ESTIMATORS:
        e = r[name]
        rows[name] = {"with the drug, per 100": round(e.with_drug, 2), "without, per 100": round(e.without, 2),
                      "difference, per 100": round(e.difference, 2), "relative risk": round(e.relative_risk, 2),
                      f"less the true value, across {SEEDS} further samples":
                          "the reference" if name == "true value" else
                          spread_words(spread_of(band, name, strength), 2, " per 100")}
    return pd.DataFrame.from_dict(rows, orient="index").rename_axis(f"{band} ({r['casualties']:,} casualties)")


@lru_cache(maxsize=None)
def strength_curve(strengths: tuple = STRENGTHS, seed: int = EVAL_SEED) -> pd.DataFrame:
    """Each reading's difference per 100, for every delay, as the strength of the arrow into treatment changes; the
    same casualties and the same coin at every strength."""
    rows = []
    for s in strengths:
        r = estimates(seed, EVAL_N, float(s))
        rows.append({"strength": float(s), "share given": r["given"] / r["casualties"],
                     **{name: r[ALL][name].difference for name in ESTIMATORS}})
    return pd.DataFrame(rows).set_index("strength")


def balance(strength: float = DEFAULT_STRENGTH) -> pd.DataFrame:
    """How the given and the not given differ under the constructed allocation, in the evaluation sample: the share
    with each recorded sign, the mean of the hidden variable, and the share bleeding significantly."""
    observed, truth = at_care()
    treated = allocate(observed, truth, strength)
    table = signs(observed).assign(**{HIDDEN: hidden(truth), "bleeding significantly": truth["bleeding"].to_numpy(float)})
    return pd.DataFrame({"given the drug": table[treated].mean(), "not given": table[~treated].mean()})


# ------------------------------------------------------------------------------------------------ by hand

HAND_PER_GROUP = 4
HAND_COIN_SEED = 6                 # a seed whose coin falls heads twice in each group of four
HAND_HOUR = 1.0
HAND_GROUPS = ("dies within the first hour", "dies after the first hour", "does not die from bleeding")


def hand_twelve() -> pd.DataFrame:
    """Twelve battle casualties bleeding significantly from the evaluation sample, from the moment of wounding, with
    their outcome as if untreated, so the drug has no effect here: the first four in sample order whose bleeding death
    comes within the first hour, the first four whose death comes after it, and the first four who do not die from
    bleeding. A coin is tossed for each, with a seed whose tosses fall heads twice and tails twice in each group of
    four, so that the coin alone gives the two sides the same mix."""
    observed, truth = _sample()
    m = (observed["stream"] == "battle").to_numpy() & truth["bleeding"].to_numpy(bool)
    died = truth["died_if_untreated"].to_numpy(bool)
    hours = truth["t_death_potential_h"].to_numpy(float)
    group = np.where(~died, HAND_GROUPS[2], np.where(hours <= HAND_HOUR, HAND_GROUPS[0], HAND_GROUPS[1]))
    picks = np.concatenate([np.flatnonzero(m & (group == g))[:HAND_PER_GROUP] for g in HAND_GROUPS])
    coin = np.random.default_rng(HAND_COIN_SEED).choice(["H", "T"], size=picks.size)
    return pd.DataFrame({"casualty": observed["id"].to_numpy()[picks], "group": group[picks], "coin": coin,
                         "dies from bleeding": died[picks],
                         "hours to death": np.where(died[picks], np.round(hours[picks], 2), np.nan)}
                        ).set_index("casualty")


def hand_given(table: pd.DataFrame, rule: str) -> np.ndarray:
    """Who is given the drug: by the coin alone, or by the coin only if still alive at the end of the first hour."""
    heads = (table["coin"] == "H").to_numpy()
    if rule == "coin":
        return heads
    if rule == "alive at 1 hour":
        dead_by = table["dies from bleeding"].to_numpy(bool) & (table["hours to death"].to_numpy(float) <= HAND_HOUR)
        return heads & ~dead_by
    raise ValueError("rule must be 'coin' or 'alive at 1 hour'")


def hand_counts(table: pd.DataFrame, rule: str) -> dict:
    """Given and not given, and how many of each die from bleeding."""
    given, died = hand_given(table, rule), table["dies from bleeding"].to_numpy(bool)
    return {"given": int(given.sum()), "given, died": int(died[given].sum()),
            "not given": int((~given).sum()), "not given, died": int(died[~given].sum())}


# A stratified two-by-two table, constructed for counting: not drawn from the generator.
SIMPSON = pd.DataFrame(
    [("signs normal", "given", 20, 1), ("signs normal", "not given", 80, 8),
     ("signs abnormal", "given", 80, 24), ("signs abnormal", "not given", 20, 8)],
    columns=["stratum", "drug", "casualties", "died"])


def simpson_shares(table: pd.DataFrame = SIMPSON) -> pd.DataFrame:
    """The share who died, given and not given, within each stratum and combined."""
    rows = {}
    for stratum, g in list(table.groupby("stratum", sort=False)) + [("combined", table)]:
        t = g.groupby("drug")[["casualties", "died"]].sum()
        rows[stratum] = {"given: died of": f"{t.loc['given', 'died']} of {t.loc['given', 'casualties']}",
                         "given, %": 100 * t.loc["given", "died"] / t.loc["given", "casualties"],
                         "not given: died of": f"{t.loc['not given', 'died']} of {t.loc['not given', 'casualties']}",
                         "not given, %": 100 * t.loc["not given", "died"] / t.loc["not given", "casualties"]}
    return pd.DataFrame.from_dict(rows, orient="index").rename_axis("constructed table")


# ------------------------------------------------------------------------------------------------ diagnosis

SELECTIONS = ("every casualty", "scanned only if Priority 1", "confirmed after every positive, one in five negatives")
CONFIRM_NEGATIVE = 0.2             # assumption: the share of negative scans whose true state is confirmed


def _accuracy(scan: np.ndarray, state: np.ndarray) -> dict:
    return {"scanned and confirmed": int(state.size), "with free fluid": int(state.sum()),
            "sensitivity": float(scan[state].mean()), "specificity": float((~scan[~state]).mean()),
            "positive predictive value": float(state[scan].mean()),
            "negative predictive value": float((~state[~scan]).mean())}


@lru_cache(maxsize=None)
def scan_accuracy(setting: str = "pre_hospital", seed: int = EVAL_SEED, n: int = EVAL_N) -> dict:
    """The scan for free fluid on the battle casualties, measured three ways (mechanism): against the true state of
    every casualty, which only the generator gives; scanning only those the MPTT-24 (figure reading) puts in
    Priority 1; and scanning everyone but confirming the true state after every positive scan and after one in five
    negative scans, chosen by a coin. Both selections are constructed and are assumptions."""
    observed, truth = _sample(seed, n, setting)
    b = (observed["stream"] == "battle").to_numpy()
    scan = observed["scan_free_fluid"].to_numpy(dtype=bool, na_value=False)[b]
    state = truth["free_fluid"].to_numpy(bool)[b]
    priority_one = baseline.priority_one(observed, "figure")[b]
    confirmed = scan | (np.random.default_rng(VERIFY_SEED + seed).random(state.size) < CONFIRM_NEGATIVE)
    out = {"battle casualties": int(b.sum()), "scan": scan, "state": state,
           SELECTIONS[0]: _accuracy(scan, state),
           SELECTIONS[1]: _accuracy(scan[priority_one], state[priority_one]),
           SELECTIONS[2]: _accuracy(scan[confirmed], state[confirmed])}
    for reading in baseline.READINGS:
        flag = baseline.priority_one(observed, reading)[b]
        out[reading] = baseline.flag_metrics(flag, state)
        out[f"{reading} flag"] = flag
    out["scan metrics"] = baseline.flag_metrics(scan, state)
    return out


MEASURES = ("sensitivity", "specificity", "positive predictive value", "negative predictive value")


@lru_cache(maxsize=None)
def scan_spread(setting: str = "pre_hospital") -> pd.DataFrame:
    """scan_accuracy on SEEDS further samples (seeds 43 onward): each measure under each selection, and the scan's
    and the rule's Brier score and net benefit at the common threshold, against free fluid."""
    t = decision.threshold()
    rows = {}
    for k in range(SEEDS):
        seed = EVAL_SEED + 1 + k
        r = scan_accuracy(setting, seed)
        row = {f"{sel}: {m}": r[sel][m] for sel in SELECTIONS for m in MEASURES}
        row.update({"scan Brier": r["scan metrics"]["brier"], "rule Brier": r["figure"]["brier"],
                    "scan net benefit": 100 * decision.net_benefit(r["scan"], r["state"], t),
                    "rule net benefit": 100 * decision.net_benefit(r["figure flag"], r["state"], t)})
        rows[seed] = row
    return pd.DataFrame.from_dict(rows, orient="index").rename_axis("sample seed")


def scan_table(setting: str = "pre_hospital") -> pd.DataFrame:
    """Each measure on every casualty and as measured under each selection, in the evaluation sample, with each
    selection's difference from every casualty across the further samples."""
    r, spread = scan_accuracy(setting), scan_spread(setting)
    rows = {}
    for m in MEASURES:
        row = {sel: round(100 * r[sel][m], 1) for sel in SELECTIONS}
        for sel in SELECTIONS[1:]:
            diff = 100 * (spread[f"{sel}: {m}"] - spread[f"{SELECTIONS[0]}: {m}"])
            row[f"{sel}, less every casualty"] = spread_words(diff, 1, " points")
        rows[f"{m}, %"] = row
    return pd.DataFrame.from_dict(rows, orient="index").rename_axis(f"{SETTING_NAMES[setting]}, battle casualties")


# ------------------------------------------------------------------------------------------------ the failure

def survival_bias(seed: int = EVAL_SEED, n: int = EVAL_N) -> dict:
    """On the battle casualties bleeding significantly, from the moment of wounding, each outcome read as if untreated,
    so the drug has no effect. The generator's own coin says who is meant to get the drug, at their time to
    pre-hospital care; it is given only to those still alive then. Naive: those given it against everyone else.
    Aligned at a common start: only those alive at the moment the drug would be given, those given it against those
    not meant to get it, both counted from then (mechanism)."""
    observed, truth = _sample(seed, n)
    m = (observed["stream"] == "battle").to_numpy() & truth["bleeding"].to_numpy(bool)
    died = truth["died_if_untreated"].to_numpy(bool)[m]
    minutes = 60 * truth["t_death_potential_h"].to_numpy(float)[m]
    delay = observed["t_phec_min"].to_numpy(float)[m]
    meant = observed["txa"].to_numpy(bool)[m]
    alive = ~(died & (minutes <= delay))
    given = meant & alive
    return {"casualties": int(m.sum()), "meant": int(meant.sum()), "given": int(given.sum()),
            "meant, died first": int((meant & ~alive).sum()),
            "naive": Estimate(100 * float(died[given].mean()), 100 * float(died[~given].mean())),
            "aligned": Estimate(100 * float(died[given].mean()), 100 * float(died[alive & ~meant].mean())),
            "aligned casualties": int(alive.sum())}


@lru_cache(maxsize=None)
def survival_spread() -> pd.DataFrame:
    rows = {}
    for k in range(SEEDS):
        seed = EVAL_SEED + 1 + k
        r = survival_bias(seed)
        rows[seed] = {"naive difference": r["naive"].difference, "naive relative risk": r["naive"].relative_risk,
                      "aligned difference": r["aligned"].difference, "aligned relative risk": r["aligned"].relative_risk}
    return pd.DataFrame.from_dict(rows, orient="index").rename_axis("sample seed")


FASTER = 0.5        # constructed: every time from injury to Role 2 halved


def reaching_care(seed: int = EVAL_SEED, n: int = EVAL_N, factor: float = 1.0) -> dict:
    """On the battle casualties bleeding significantly, each outcome read as if untreated: deaths from bleeding before
    reaching Role 2 per 100, and the share who die after reaching it among those who reach it alive, at the
    generator's times from injury to Role 2 multiplied by `factor`. In the generator reaching Role 2 saves no one, so
    the deaths are the same casualties at any factor (mechanism)."""
    observed, truth = _sample(seed, n)
    m = (observed["stream"] == "battle").to_numpy() & truth["bleeding"].to_numpy(bool)
    died = truth["died_if_untreated"].to_numpy(bool)[m]
    minutes = 60 * truth["t_death_potential_h"].to_numpy(float)[m]
    arrive = factor * observed["t_role2_min"].to_numpy(float)[m]
    before = died & (minutes < arrive)
    reached = ~before
    return {"casualties": int(m.sum()), "died": int(died.sum()), "before Role 2": int(before.sum()),
            "reached alive": int(reached.sum()), "died after reaching": int((died & reached).sum()),
            "before, per 100": 100 * float(before.mean()),
            "after, per 100 reaching": 100 * float(died[reached].mean())}


@lru_cache(maxsize=None)
def reaching_spread() -> pd.DataFrame:
    rows = {}
    for k in range(SEEDS):
        seed = EVAL_SEED + 1 + k
        a, b = reaching_care(seed), reaching_care(seed, factor=FASTER)
        rows[seed] = {"before, as drawn": a["before, per 100"], "before, faster": b["before, per 100"],
                      "after, as drawn": a["after, per 100 reaching"], "after, faster": b["after, per 100 reaching"],
                      "died, as drawn": a["died"], "died, faster": b["died"]}
    return pd.DataFrame.from_dict(rows, orient="index").rename_axis("sample seed")


# ------------------------------------------------------------------------------------------------ the lens

@dataclass(frozen=True)
class ScanReading:
    result: bool | None       # free fluid seen; None where the casualty was not scanned
    setting: str
    accuracy: dict            # selection -> (sensitivity, specificity), in the evaluation sample


@dataclass(frozen=True)
class Effect:
    band: str
    casualties: int
    deaths: int
    naive: Estimate
    adjusted: Estimate
    true: Estimate


def band_of(minutes: float) -> str:
    return BANDS[int(stochastic.band_index(float(minutes)))]


def scan_word(value: Any) -> bool | None:
    if value is None or value is pd.NA or (isinstance(value, float) and np.isnan(value)):
        return None
    return bool(value)


DIAGNOSIS_METRICS = (("sensitivity", "sensitivity"), ("specificity", "specificity"), ("brier", "Brier score"),
                     ("calibration", "share positive minus share with free fluid"))


def diagnosis_metric(name: str, setting: str) -> str:
    return (f"{name}, scan against free fluid, measured on every battle casualty against the true state, "
            f"{SETTING_NAMES[setting]}")


class CausalLens:
    """Lens 07 behind the Lens interface (R-0.8, R-7.1)."""

    name = NAME

    def diagnose(self, casualty: Mapping[str, Any]) -> ScanReading:
        setting = str(casualty.get("setting", "pre_hospital"))
        r = scan_accuracy(setting)
        return ScanReading(scan_word(casualty.get("scan_free_fluid")), setting,
                           {sel: (r[sel]["sensitivity"], r[sel]["specificity"]) for sel in SELECTIONS})

    def treat(self, casualty: Mapping[str, Any]) -> Effect:
        band = band_of(float(casualty["t_phec_min"]))
        r = estimates()[band]
        return Effect(band, r["casualties"], r["deaths"], r["naive"], r["adjusted for every variable the allocation uses"],
                      r["true value"])

    def scorecard(self) -> list[ScorecardRow]:
        rows = []
        for setting in SETTINGS:
            r = scan_accuracy(setting)
            for key, name in DIAGNOSIS_METRICS:
                rows.append(ScorecardRow(NAME, "diagnosis", diagnosis_metric(name, setting),
                                         round(r["scan metrics"][key], 4), round(r["figure"][key], 4), "mechanism",
                                         "weak", "generator"))
            for sel in SELECTIONS[1:]:
                for key in ("sensitivity", "specificity"):
                    rows.append(ScorecardRow(NAME, "diagnosis", f"{key} of the scan as measured when {sel}, less on "
                                             f"every battle casualty, {SETTING_NAMES[setting]}",
                                             round(r[sel][key] - r[SELECTIONS[0]][key], 4), NO_BASELINE, "mechanism",
                                             "weak", "generator"))
        e = estimates()[ALL]
        group = ("battle casualties alive at pre-hospital care, under the constructed allocation, deaths from bleeding "
                 "per 100")
        rows.append(ScorecardRow(NAME, "treatment", f"true effect of tranexamic acid, with less without, {group}",
                                 round(e["true value"].difference, 4), NO_BASELINE, "mechanism", "native", "generator"))
        for name in ESTIMATORS[:3]:
            rows.append(ScorecardRow(NAME, "treatment", f"estimate less the true effect: {name}, {group}",
                                     round(e[name].difference - e["true value"].difference, 4), NO_BASELINE,
                                     "mechanism", "native", "generator"))
        return rows


LENS = CausalLens()


def seven_axes() -> pd.DataFrame:
    """The scorecard on the seven axes of D-21, with the baseline under both readings (D-24) and axis 7 at 0.10
    (D-26)."""
    pre, inside = scan_accuracy("pre_hospital"), scan_accuracy("in_hospital")
    sp, si = scan_spread("pre_hospital"), scan_spread("in_hospital")
    e = estimates()[ALL]
    t = decision.threshold()
    registry = rules.PUBLISHED["MPTT-24, military"].prevalence     # E-09: Priority 1 in the military registry
    every, p1, conf = SELECTIONS
    group = (f"{pre['battle casualties']:,} synthetic battle casualties, {pre[every]['with free fluid']:,} with free "
             f"fluid")
    d23 = (f"Among the generator's injured in the military cohort, battle and non-battle injury together, "
           f"{_pct(baseline.calibration_need('military'))} need a life-saving intervention, against "
           f"{_pct(registry)} Priority 1 in the military registry (E-01, E-09), so the generator's injured are a milder "
           f"cohort than the one the rule was validated on (D-23)")

    def scan_disc(r):
        return (f"on every casualty sensitivity {_pct(r[every]['sensitivity'])}, specificity "
                f"{_pct(r[every]['specificity'])}; as measured when {p1}, {_pct(r[p1]['sensitivity'])} and "
                f"{_pct(r[p1]['specificity'])}; as measured when {conf}, {_pct(r[conf]['sensitivity'])} and "
                f"{_pct(r[conf]['specificity'])}")

    def rule_disc(r):
        return f"sensitivity {_pct(r['sensitivity'])}, specificity {_pct(r['specificity'])} for free fluid"

    def rule_cal(r):
        gap = r["calibration"]
        return (f"Brier {r['brier']:.3f}; it flags {100 * abs(gap):.1f} points {'more' if gap > 0 else 'fewer'} than "
                f"have free fluid. A rule gives no probability, so the Brier score is the share misclassified")

    def diff(name):
        return spread_words(spread_of(ALL, name), 2, " per 100")

    true = e["true value"]
    rows = [
        ("1 Discrimination (mechanism)",
         f"The scan, before hospital: {scan_disc(pre)}; {group}. Sensitivity as measured when {conf}, less on every "
         f"casualty, is {spread_words(100 * (sp[f'{conf}: sensitivity'] - sp[f'{every}: sensitivity']), 1, ' points')}; "
         f"as measured when {p1}, less on every casualty, it is "
         f"{spread_words(100 * (sp[f'{p1}: sensitivity'] - sp[f'{every}: sensitivity']), 1, ' points')}",
         f"{rule_disc(pre['figure'])}, which the rule was not written for. {d23}",
         rule_disc(pre["text"]),
         f"Not a classifier: the effect of tranexamic acid on death from bleeding among {e['casualties']:,} battle "
         f"casualties alive at pre-hospital care, under the constructed allocation. True value: {true.words()}. "
         f"Naive: {e['naive'].direction()}. Adjusted for every variable the allocation uses: "
         f"{e[ESTIMATORS[1]].direction()}. Adjusted on the recorded signs alone: {e[ESTIMATORS[2]].direction()}"),
        ("2 Calibration (mechanism)",
         f"Brier {pre['scan metrics']['brier']:.3f}; share positive minus share with free fluid "
         f"{pre['scan metrics']['calibration']:+.3f}, on every casualty. What a positive scan means moves with who is "
         f"scanned: positive predictive value {_pct(pre[every]['positive predictive value'])} on every casualty, "
         f"{_pct(pre[p1]['positive predictive value'])} when {p1}, which less every casualty is "
         f"{spread_words(100 * (sp[f'{p1}: positive predictive value'] - sp[f'{every}: positive predictive value']), 1, ' points')}. "
         f"The scan's Brier score less the rule's is {spread_words(sp['scan Brier'] - sp['rule Brier'], 3)}",
         rule_cal(pre["figure"]), rule_cal(pre["text"]),
         f"Each estimate less the true value, per 100, across {SEEDS} further samples. Naive: {diff(ESTIMATORS[0])}. "
         f"Adjusted for every variable the allocation uses: {diff(ESTIMATORS[1])}. Adjusted on the recorded signs "
         f"alone: {diff(ESTIMATORS[2])}"),
        ("3 Uncertainty expressed", "None: a yes or no", "None: a priority", "None: a priority",
         f"One estimate from one sample, with its distance from the true value across {SEEDS} further samples shown "
         f"beside it"),
        ("4 What it needed",
         "The true state on every battle casualty, which the generator supplies and a study rarely has; the scan's "
         "accuracy set from E-16 before hospital (a civilian helicopter service) and E-14 in hospital, applied to "
         "battle casualties (an assumption)",
         "Rules only (E-08)", "Rules only (E-08)",
         "A stated causal structure: every variable that drives who is given the drug, recorded. The allocation is "
         "constructed and is an assumption, and only the generator holds the true value"),
        ("5 Readability", "Two counts a reader can ask for: who was scanned, and whose true state was confirmed",
         "Six yes-or-no steps", "Six yes-or-no steps",
         "One diagram: the arrows into treatment, and whether each is recorded"),
        ("6 Robustness, setting changed (mechanism)",
         f"Scan in hospital: {scan_disc(inside)}. The scan's Brier score less the rule's, in hospital, is "
         f"{spread_words(si['scan Brier'] - si['rule Brier'], 3)}",
         f"Scan in hospital: {rule_disc(inside['figure'])}, unchanged because the setting changes only the scan",
         f"Scan in hospital: {rule_disc(inside['text'])}, unchanged",
         "Unchanged: the constructed allocation reads the signs and not the scan, and the generator draws the same "
         "signs and outcomes in either setting"),
        ("7 Decision value",
         stochastic.axis7(pre["scan"], pre["state"]) + f", against free fluid. Across {len(sp)} further samples the "
         f"scan's net benefit less the rule's is {spread_words(sp['scan net benefit'] - sp['rule net benefit'], 1, ' per 100')}",
         stochastic.axis7(pre["figure flag"], pre["state"]) + ", against free fluid",
         stochastic.axis7(pre["text flag"], pre["state"]) + ", against free fluid",
         "Net benefit scores a flag, not an effect estimate. What the decision needs is the effect's sign and size. "
         f"Read naively, the record shows {e['naive'].direction()}; the true value is {true.direction()}"),
    ]
    return pd.DataFrame(rows, columns=["axis", "diagnosis: the scan for free fluid, as measured and as it is",
                                       "baseline: MPTT-24, figure (as published)",
                                       "baseline: MPTT-24, text (as validated)",
                                       "treatment: effect of tranexamic acid, three ways"]).set_index("axis")


# ------------------------------------------------------------------------------------------------ app page 1

def panel(record: Mapping[str, Any]) -> dict:
    """The causal panel for one synthetic casualty on app page 1. Every number is formatted here, so the page shows
    only what the library computed (gate G-8)."""
    effect = LENS.treat(record)
    reading = LENS.diagnose(record)
    minutes = float(record["t_phec_min"])

    def spread(name):
        return spread_words(spread_of(effect.band, name), 2, " per 100")

    scan = {None: "was not scanned", True: "free fluid seen", False: "no free fluid seen"}[reading.result]
    r = scan_accuracy(reading.setting)
    every, p1, conf = SELECTIONS
    accuracy = "; ".join(f"{sel}, sensitivity {_pct(r[sel]['sensitivity'])} and specificity "
                         f"{_pct(r[sel]['specificity'])}" for sel in SELECTIONS)
    source = ("before hospital the generator's scan accuracy is set from E-16, a civilian helicopter service"
              if reading.setting == "pre_hospital" else
              "in hospital the generator's scan accuracy is set from E-14's pooled figures")
    return {
        "heading": "Causal panel: what a record would show, and what is true",
        "allocation": (f"Pre-hospital care at {minutes:.1f} minutes after injury puts this casualty in the band "
                       f"\"{effect.band}\", with {effect.casualties:,} of the battle casualties alive at pre-hospital "
                       f"care among the 100,000 synthetic casualties, of whom {effect.deaths:,} die from bleeding when "
                       f"the drug is given as in the constructed record. In that record, an assumption, the drug is "
                       f"given more often to those with abnormal signs and to those bleeding more heavily, a variable "
                       f"the record does not hold."),
        "effect": (f"Effect of tranexamic acid on death from bleeding in this band (mechanism). Read naively: "
                   f"{effect.naive.words()}. Adjusted for every variable the allocation uses: "
                   f"{effect.adjusted.words()}. True value, from both outcomes of the same casualties, which only the "
                   f"generator holds: {effect.true.words()}."),
        "spread": (f"Distance from the true value across {SEEDS} further samples: naive, {spread(ESTIMATORS[0])}; "
                   f"adjusted, {spread(ESTIMATORS[1])}."),
        "scan": (f"Scan for free fluid, {SETTING_NAMES[reading.setting]}: {scan}. The scan's accuracy on the battle "
                 f"casualties (mechanism): {accuracy}. Both selections are constructed, and {source}, applied to "
                 f"battle casualties as an assumption."),
    }


def page_panel(walk: Any) -> dict:
    """The causal panel on app page 1 for one walk-through casualty, given lens 03's Walkthrough (D-27)."""
    return panel(walk.record)
