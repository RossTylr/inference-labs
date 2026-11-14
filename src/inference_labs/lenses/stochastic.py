"""Lens 05, stochastic processes (PRD section 6.6; docs/background/05-stochastic.md).

One casualty's course cannot be predicted; a thousand casualties' can. The lens describes the dice, not the roll:
how the chance of dying from bleeding changes with time since injury, and how the benefit of tranexamic acid falls
with delay.

    diagnosis   for a casualty alive at pre-hospital care, the chance of dying from bleeding in the next hour if
                bleeding significantly, conditional on being alive then, under the generator's hazard
    treatment   the relative reduction in death from bleeding left at the casualty's delay to tranexamic acid, as
                draws

Where the numbers come from
- The hazard of death from bleeding is the generator's: log-quadratic in time since injury, through E-85's three
  hourly rates (about 4.6% at 1 hour, about 1% at 6 hours, under 0.1% by 9 hours, the last taken as 0.1%). E-85 was
  measured from hospital admission, in 4,064 haemorrhaging patients from five prospective studies at civilian
  centres. The generator runs it from injury, an assumption, and so does this lens.
- The chance that a casualty bleeding significantly dies from bleeding, on average over site and severity, is the
  generator's: the share of them dead by 24 hours under that hazard. The generator sets each site's chance so that
  the average over sites equals it.
- The fixed-rate chain is the generator's constant-hazard option: whether a casualty dies is decided as before, and
  the time of death is drawn at a fixed hourly rate, ln 2 over the time-varying hazard's median time to death. This
  module calls that option only in the failure (`failure_*`).
- Tranexamic acid: E-22's relative risks of death from bleeding by time to treatment, from an exploratory analysis
  (E-23) of CRASH-2, a civilian trial, each drawn from a log-normal fitted to its 95% interval (the shape an
  assumption) with a seed of its own. The relative reduction falls in a straight line to none at 3 hours, where
  E-24 puts the end of the benefit; the straight line is an assumption, a fall of 8.3% of the reduction at zero
  delay for each 15 minutes, against E-24's "about 10%". E-24 pooled CRASH-2 with a trial in postpartum
  haemorrhage, half its patients (E-26). The line's height is set, draw by draw, so that its average over the
  first band matches E-22's first band; the spread of delays within the band is the generator's, an assumption.
  After 3 hours the lens uses E-22's band over 3 hours, in which there were more deaths from bleeding with the drug.
- The dice of the by-hand chain, the lives of the central figure and the later deaths of the early-against-late
  comparison are constructed here and are labelled so. The generator holds one death time per casualty and no
  repeated observations.

Every result computed on the generator is a mechanism, not evidence (D-8).
"""
from __future__ import annotations

import math
from dataclasses import dataclass
from functools import lru_cache
from typing import Any, Mapping

import numpy as np
import pandas as pd
from scipy.stats import lognorm

from inference_labs import baseline, generator
from inference_labs.belief import RV
from inference_labs.interface import ScorecardRow
from inference_labs.lenses import decision, rules
from inference_labs.lenses.bayesian import LogNormalSummary

NAME = "Stochastic processes"
NO_BASELINE = float("nan")         # the MPTT-24 states no benefit of a treatment
SETTINGS = baseline.SETTINGS
SETTING_NAMES = baseline.SETTING_NAMES
EVAL_N, EVAL_SEED = baseline.EVAL_N, baseline.EVAL_SEED     # 100,000 synthetic casualties, seed 42
SEEDS = 20                         # further samples behind every spread, seeds 43 onward
SPREAD_N = 400_000                 # synthetic casualties in each further sample where events are rare
WINDOW_MIN = 60.0                  # the diagnosis looks one hour ahead of pre-hospital care
HOURS = (1.0, 6.0, 9.0)            # E-85's three hourly rates

# E-85: five prospective studies, 4,064 haemorrhaging patients, timed from hospital admission.
E85_PATIENTS, E85_STUDIES = 4064, 5
E85_MEDIAN_H = (2.0, 2.6)
E85_WITHIN_6H = 0.85
E85_SOURCE = ("E-85: 4,064 haemorrhaging patients in five prospective studies at civilian centres, timed from "
              "hospital admission")
E85_CLOCK = ("E-85 was measured from hospital admission; it is run here from injury, which is an assumption")
# E-25: in the trials pooled by E-24, half of whose patients were obstetric (E-26).
E25_DEATHS, E25_WITHIN_12H = 1408, 884
# E-127: a US registry, 2012 to 2014.
E127 = {"patients": 42_135, "mortality": 0.079, "median_min": 37, "penetrating_min": 28, "blunt_min": 40}
# E-81: 21,089 US casualties, Afghanistan, 2001 to 2014.
E81 = {"casualties": 21_089, "kia_before": (386, 2_411, 0.160), "kia_after": (964, 9_755, 0.099),
       "dow_before": 0.041, "dow_after": 0.043, "dow_p": 0.71, "detailed": 4_542, "transport_before_min": 90,
       "transport_after_min": 43, "matched": 0.373}
# E-22: relative risk of death from bleeding by time to treatment, CRASH-2 (civilian), with deaths from bleeding
# per cent, tranexamic acid against placebo.
E22_BANDS = (
    ("up to 1 hour", 0.0, 60.0, (0.68, 0.57, 0.82), (5.3, 7.7)),
    ("1 to 3 hours", 60.0, 180.0, (0.79, 0.64, 0.97), (4.8, 6.1)),
    ("over 3 hours", 180.0, math.inf, (1.44, 1.12, 1.84), (4.4, 3.1)),
)
E24 = {"patients": 40_138, "trauma": 20_127, "obstetric": 20_011, "immediate_or": (1.72, 1.42, 2.10),
       "decline_per_15min": 0.10, "none_after_h": 3.0}
NONE_AFTER_MIN = 60 * E24["none_after_h"]      # E-24: no benefit after about 3 hours
LINE_DECLINE_PER_15MIN = 15 / NONE_AFTER_MIN   # the straight line's fall, as a share of the reduction at zero delay
# E-77: 432 randomised by four English prehospital critical care services; red cells and plasma against saline.
E77 = {"randomised": 432, "early": (0.16, 0.22, (0.75, 0.50, 1.13)), "death": (0.43, 0.45, (0.97, 0.78, 1.20))}
DRAWS, DRAW_SEED = 4000, 50
TIMELINES_MIN = (10, 60, 120)                  # E-42: the planning timelines
HALF_HOUR = 30.0


def _pct(x: float, places: int = 1) -> str:
    return f"{100 * x:.{places}f}%"


def spread_words(differences, places: int = 2, unit: str = "") -> str:
    """A difference reported with its spread across seeds, to `places` decimals: a tie where the spread covers no
    difference (as decision.spread_words, with the precision a small quantity needs)."""
    d = np.asarray(differences, float)
    lo, hi = float(d.min()), float(d.max())
    span = f"from {lo:+.{places}f} to {hi:+.{places}f}{unit} across {d.size} seeds"
    if lo <= 0 <= hi:
        return f"a tie: no detectable difference (the difference runs {span})"
    return f"{'lower' if hi < 0 else 'higher'}: the difference runs {span}"


# ------------------------------------------------------------------------------------------------ the chains

def death_chance() -> float:
    """The generator's chance that a casualty bleeding significantly dies from bleeding, on average over site and
    severity: the share of them dead by 24 hours under its hazard."""
    return float(generator.derived().death_fraction)


def constant_rate() -> float:
    """The fixed-rate chain's hourly rate for a casualty who will die: ln 2 over the median time to death."""
    return float(generator.derived().constant_rate)


def median_death_h() -> float:
    """Median time from injury to death among bleeding deaths under the time-varying hazard. The fixed-rate chain
    has the same median by construction."""
    return float(generator.derived().median_death_h)


def deaths_by(t_h, hazard: str = "time_varying") -> np.ndarray:
    """The share of bleeding deaths that have happened by `t_h` hours after injury."""
    t = np.asarray(t_h, dtype=float)
    if hazard == "time_varying":
        d = generator.derived()
        return np.interp(t, d.grid_h, d.death_time_cdf)
    if hazard == "constant":
        return 1 - np.exp(-constant_rate() * t)
    raise ValueError(f"hazard must be one of {generator.HAZARDS}")


def alive(t_h, hazard: str = "time_varying") -> np.ndarray:
    """The share of casualties bleeding significantly still alive `t_h` hours after injury."""
    return 1 - death_chance() * deaths_by(t_h, hazard)


def hourly_rate(t_h, hazard: str = "time_varying") -> np.ndarray:
    """Deaths from bleeding per hour among casualties bleeding significantly and still alive at `t_h` hours: the
    quantity E-85 reports at 1, 6 and 9 hours. Under the fixed-rate chain it falls only because the casualties who
    will not die make up more of those alive."""
    t = np.asarray(t_h, dtype=float)
    if hazard == "time_varying":
        return generator.bleeding_hazard(t)
    lam = constant_rate()
    return death_chance() * lam * np.exp(-lam * t) / alive(t, "constant")


def chance_between(now_h, then_h, hazard: str = "time_varying") -> np.ndarray:
    """The chance that a casualty bleeding significantly and alive `now_h` hours after injury dies from bleeding by
    `then_h`, without tranexamic acid. Conditional on being alive now."""
    q = death_chance()
    before, by_then = deaths_by(now_h, hazard), deaths_by(then_h, hazard)
    return q * (by_then - before) / (1 - q * before)


def next_hour(minutes_since_injury) -> np.ndarray:
    """The lens's diagnosis: the chance of dying from bleeding in the next hour, if bleeding significantly and alive
    now, under the time-varying hazard."""
    m = np.asarray(minutes_since_injury, dtype=float)
    return chance_between(m / 60, (m + WINDOW_MIN) / 60)


def chance_after(minutes_since_injury, hazard: str = "time_varying") -> np.ndarray:
    """The chance of dying from bleeding at any later time, if bleeding significantly and alive now, without
    tranexamic acid."""
    m = np.asarray(minutes_since_injury, dtype=float)
    return chance_between(m / 60, np.inf, hazard)


def rate_falls_to(level: float, hazard: str = "time_varying") -> float:
    """Hours after injury at which the hourly rate among those alive first falls to `level`, after its peak."""
    grid = np.arange(0.0, 24.0 + 1e-9, 1 / 60)
    rate = hourly_rate(grid, hazard)
    below = np.flatnonzero((rate <= level) & (grid >= grid[int(np.argmax(rate))]))
    return float(grid[below[0]]) if below.size else math.inf


def e85_check() -> pd.DataFrame:
    """Each chain against E-85's figures, and against E-25's share within 12 hours. The chains are computed from the
    hazard, not drawn; the time-varying hazard was fitted to the three hourly rates."""
    rates = generator.load_params()["parameters"]["bleeding_death_hazard"]["value"]
    published = {1.0: f"about {_pct(rates['h_1h'])}", 6.0: f"about {_pct(rates['h_6h'], 0)}",
                 9.0: f"under {_pct(rates['h_9h'])}"}
    rows = []
    for h in HOURS:
        rows.append((f"hourly death rate among those alive at {h:g} hours", published[h], "E-85",
                     float(hourly_rate(h, "constant")), float(hourly_rate(h))))
    rows.append(("median time to death among bleeding deaths, hours",
                 f"{E85_MEDIAN_H[0]:.1f} to {E85_MEDIAN_H[1]:.1f}", "E-85", median_death_h(), median_death_h()))
    rows.append(("share of bleeding deaths within 6 hours", f"about {_pct(E85_WITHIN_6H, 0)}", "E-85",
                 float(deaths_by(6.0, "constant")), float(deaths_by(6.0))))
    rows.append(("share of bleeding deaths within 12 hours", f"{E25_WITHIN_12H:,} of {E25_DEATHS:,} "
                 f"({_pct(E25_WITHIN_12H / E25_DEATHS, 0)}), from onset", "E-25",
                 float(deaths_by(12.0, "constant")), float(deaths_by(12.0))))
    return pd.DataFrame(rows, columns=["figure", "published", "source", "fixed-rate chain", "time-varying hazard"]
                        ).set_index("figure")


# ------------------------------------------------------------------------------------------------ by hand

CHAIN_STATES = ("bleeding", "stopped", "dead")
# One hour of the hand chain, for a casualty still bleeding: toss a coin; heads, nothing changes this hour. Tails,
# roll a die: 1, dead; 2 or 3, the bleeding stops; 4 to 6, still bleeding. The dice are constructed for counting.
CHAIN = np.array([[3 / 4, 1 / 6, 1 / 12],
                  [0.0, 1.0, 0.0],
                  [0.0, 0.0, 1.0]])
HAND_N, HAND_STEPS, HAND_SEED = 10, 3, 11


def rolls(n: int = HAND_N, steps: int = HAND_STEPS, seed: int = HAND_SEED) -> pd.DataFrame:
    """A coin and a die for each casualty in each hour, rolled whether or not they are used."""
    rng = np.random.default_rng(seed)
    coins = rng.choice(["H", "T"], size=(n, steps))
    dice = rng.integers(1, 7, size=(n, steps))
    cols = {}
    for k in range(steps):
        cols[f"hour {k + 1} coin"] = coins[:, k]
        cols[f"hour {k + 1} die"] = dice[:, k]
    return pd.DataFrame(cols, index=pd.RangeIndex(1, n + 1, name="casualty"))


def step(state: str, coin: str, die: int) -> str:
    """One hour of the hand chain."""
    if state != "bleeding" or coin == "H":
        return state
    if die == 1:
        return "dead"
    if die in (2, 3):
        return "stopped"
    return "bleeding"


def run_chain(table: pd.DataFrame, steps: int = HAND_STEPS) -> pd.DataFrame:
    """Every casualty's state at the start and after each hour."""
    out = {"start": ["bleeding"] * len(table)}
    state = list(out["start"])
    for k in range(1, steps + 1):
        state = [step(s, c, int(d)) for s, c, d in zip(state, table[f"hour {k} coin"], table[f"hour {k} die"])]
        out[f"after hour {k}"] = state
    return pd.DataFrame(out, index=table.index)


def expected_shares(steps: int = HAND_STEPS) -> pd.DataFrame:
    """The share in each state after each hour, from the transition matrix: the start row times the matrix to the
    power of the number of hours."""
    start = np.array([1.0, 0.0, 0.0])
    rows = {f"after hour {k}": start @ np.linalg.matrix_power(CHAIN, k) for k in range(steps + 1)}
    rows["start"] = rows.pop("after hour 0")
    order = ["start"] + [f"after hour {k}" for k in range(1, steps + 1)]
    return pd.DataFrame(rows, index=list(CHAIN_STATES)).T.loc[order]


# ------------------------------------------------------------------------------------------------ many lives

LIFE_STATES = ("alive, before Role 2", "alive, at Role 2", "died before reaching Role 2", "died after reaching Role 2")
LIVES_N, LIVES_SEED = 100, 3
MANY_LIVES = 10_000


def lives(n: int = LIVES_N, seed: int = LIVES_SEED, evacuation: float = 1.0) -> pd.DataFrame:
    """`n` constructed lives of one kind of casualty, bleeding significantly from the moment of wounding: each dies
    from bleeding with the generator's average chance, at a time drawn from its time-varying hazard, and reaches Role
    2 at a time drawn from the generator's assumed times to pre-hospital care and on to Role 2, both multiplied by
    `evacuation`. The draws are made in the same order whatever `evacuation` is, so changing it changes only the
    clock of evacuation. Constructed, not data: the generator holds no repeated observations."""
    d = generator.derived()
    v = {pid: p["value"] for pid, p in generator.load_params()["parameters"].items()}
    rng = np.random.default_rng(seed)
    u, z1, z2 = rng.random(n), rng.standard_normal(n), rng.standard_normal(n)
    q = d.death_fraction
    t_death = np.where(u < q, np.interp(u / q, d.death_time_cdf, d.grid_h), np.nan)
    tp, tr = v["time_to_phec_min"], v["phec_to_role2_min"]
    to_care = np.exp(math.log(tp["median"]) + tp["log_sd"] * z1)
    on_to_role2 = np.exp(math.log(tr["median"]) + tr["log_sd"] * z2)
    return pd.DataFrame({"t_role2_h": evacuation * (to_care + on_to_role2) / 60, "t_death_h": t_death},
                        index=pd.RangeIndex(1, n + 1, name="life"))


def state_counts(table: pd.DataFrame, grid_h) -> pd.DataFrame:
    """How many of the lives are in each state at each time."""
    t = np.asarray(grid_h, dtype=float)[:, None]
    death, arrive = table["t_death_h"].to_numpy()[None, :], table["t_role2_h"].to_numpy()[None, :]
    dead = ~np.isnan(death) & (death <= t)
    before = death < arrive
    counts = {
        "alive, before Role 2": (~dead & (t < arrive)).sum(axis=1),
        "alive, at Role 2": (~dead & (t >= arrive)).sum(axis=1),
        "died before reaching Role 2": (dead & before).sum(axis=1),
        "died after reaching Role 2": (dead & ~before).sum(axis=1),
    }
    return pd.DataFrame(counts, index=pd.Index(np.asarray(grid_h, float), name="hours since injury"))


def where_deaths_fall(evacuation: float, n: int = MANY_LIVES, seed: int = LIVES_SEED) -> dict:
    """Of `n` constructed lives, how many die from bleeding before reaching Role 2 and how many after."""
    table = lives(n, seed, evacuation)
    death, arrive = table["t_death_h"].to_numpy(), table["t_role2_h"].to_numpy()
    died = ~np.isnan(death)
    return {"lives": n, "died before reaching Role 2": int((died & (death < arrive)).sum()),
            "died after reaching Role 2": int((died & (death >= arrive)).sum()), "died": int(died.sum())}


@lru_cache(maxsize=None)
def evacuation_spread(faster: float = 0.5) -> pd.DataFrame:
    """Deaths before reaching Role 2 per 1,000 constructed lives, at the generator's evacuation times and with them
    multiplied by `faster`, on SEEDS sets of lives."""
    rows = {}
    for k in range(SEEDS):
        seed = LIVES_SEED + 1 + k
        a, b = where_deaths_fall(1.0, seed=seed), where_deaths_fall(faster, seed=seed)
        rows[seed] = {"before Role 2, as drawn": 1000 * a["died before reaching Role 2"] / a["lives"],
                      "before Role 2, faster": 1000 * b["died before reaching Role 2"] / b["lives"],
                      "after reaching Role 2, as drawn": 1000 * a["died after reaching Role 2"] / a["lives"],
                      "after reaching Role 2, faster": 1000 * b["died after reaching Role 2"] / b["lives"]}
    return pd.DataFrame.from_dict(rows, orient="index").rename_axis("seed of the lives")


# ------------------------------------------------------------------------------------------------ the generator

def _bleeding_battle(observed: pd.DataFrame, truth: pd.DataFrame) -> np.ndarray:
    return (observed["stream"] == "battle").to_numpy() & truth["bleeding"].to_numpy(bool)


def at_care(observed: pd.DataFrame, truth: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    """The battle casualties bleeding significantly and alive at pre-hospital care, judged by the generator's
    outcome without tranexamic acid: those whose bleeding death falls at or before that time are not there."""
    keep = _bleeding_battle(observed, truth) & decision.alive_at_triage(observed, truth)
    return observed[keep].reset_index(drop=True), truth[keep].reset_index(drop=True)


@lru_cache(maxsize=2 * SEEDS + 4)
def _sample(seed: int, n: int, setting: str = "pre_hospital") -> tuple[pd.DataFrame, pd.DataFrame]:
    """The battle casualties bleeding significantly and alive at pre-hospital care in one generator sample."""
    if seed == EVAL_SEED and n == EVAL_N:
        return at_care(*baseline.generator_sample(setting))
    return at_care(*generator.sample(n, seed, setting=setting, return_truth=True))


def where_bleeding_deaths_fall(setting: str = "pre_hospital") -> pd.Series:
    """The evaluation sample's battle casualties bleeding significantly, from injury, by where their bleeding death
    without tranexamic acid falls (mechanism)."""
    observed, truth = baseline.generator_sample(setting)
    m = _bleeding_battle(observed, truth)
    died = truth["died_if_untreated"].to_numpy(bool)[m]
    t = 60 * truth["t_death_potential_h"].to_numpy(float)[m]
    care, role2 = observed["t_phec_min"].to_numpy(float)[m], observed["t_role2_min"].to_numpy(float)[m]
    return pd.Series({
        "bleeding significantly": int(m.sum()),
        "died before pre-hospital care": int((died & (t <= care)).sum()),
        "died between pre-hospital care and Role 2": int((died & (t > care) & (t <= role2)).sum()),
        "died after reaching Role 2": int((died & (t > role2)).sum()),
        "did not die from bleeding": int((~died).sum()),
    }, name="synthetic battle casualties")


def next_hour_target(observed: pd.DataFrame, truth: pd.DataFrame) -> np.ndarray:
    """Died from bleeding, without tranexamic acid, within the hour after pre-hospital care."""
    t = 60 * truth["t_death_potential_h"].to_numpy(float)
    care = observed["t_phec_min"].to_numpy(float)
    return truth["died_if_untreated"].to_numpy(bool) & (t > care) & (t <= care + WINDOW_MIN)


def _brier(p: np.ndarray, target: np.ndarray) -> float:
    return float(np.mean((np.asarray(p, float) - target) ** 2))


@lru_cache(maxsize=None)
def diagnosis_results(setting: str = "pre_hospital", seed: int = EVAL_SEED, n: int = EVAL_N) -> dict:
    """The lens's chance and the MPTT-24's Priority 1 against death from bleeding in the next hour, on the battle
    casualties bleeding significantly and alive at pre-hospital care (mechanism)."""
    observed, truth = _sample(seed, n, setting)
    target = next_hour_target(observed, truth)
    p = next_hour(observed["t_phec_min"].to_numpy(float))
    t = decision.threshold()
    out = {"casualties": int(target.size), "died in the next hour": int(target.sum()), "chance": p,
           "minutes": observed["t_phec_min"].to_numpy(float),
           "target": target, "highest chance": float(p.max()), "mean chance": float(p.mean()),
           "lens": {**baseline.flag_metrics(p >= t, target), "brier": _brier(p, target),
                    "calibration": float(p.mean() - target.mean())}}
    for reading in baseline.READINGS:
        out[reading] = baseline.flag_metrics(baseline.priority_one(observed, reading), target)
        out[f"{reading} flag"] = baseline.priority_one(observed, reading)
    return out


def axis7(flag_or_p, target, words: str = "") -> str:
    """Net benefit per 100 at the common threshold, 0.10 (D-26), with treat all and treat none, in words."""
    t = decision.threshold()
    arr = np.asarray(flag_or_p)
    flag = arr if arr.dtype == bool else arr >= t
    target = np.asarray(target, bool)
    nb, everyone = 100 * decision.net_benefit(flag, target, t), 100 * decision.treat_all(target, t)
    if not flag.any():
        how = "it flags no casualty at this threshold, so it scores exactly as treating none"
    elif flag.all():
        how = "it flags every casualty at this threshold, so it scores exactly as treating all"
    elif nb < 0:
        how = "worse than treating none"
    elif nb < everyone:
        how = "below treating all"
    else:
        how = "above treating none, and at or above treating all" if nb > 0 else "no better than treating none"
    all_words = "worse than treating none" if everyone < 0 else "better than treating none"
    return (f"Net benefit {nb:.1f} per 100 at a threshold of {t:.2f} ({how}), with a miss weighed "
            f"{decision.DEFAULT_COSTS['miss'] / decision.DEFAULT_COSTS['false alarm']:g} times a false alarm (an "
            f"assumption); treat all {everyone:.1f} ({all_words}), treat none 0 (mechanism){words}")


# ------------------------------------------------------------------------------------------------ treatment

def _delay_distribution():
    tp = generator.load_params()["parameters"]["time_to_phec_min"]["value"]
    return lognorm(s=float(tp["log_sd"]), scale=float(tp["median"]))


def line_weight(lo_min: float, hi_min: float) -> float:
    """The average of the straight line's share of the reduction at zero delay, 1 - delay / 180, over the generator's
    delays between `lo_min` and `hi_min` (an assumption standing in for the trial's spread within the band)."""
    dist = _delay_distribution()
    hi = min(hi_min, NONE_AFTER_MIN)
    grid = np.linspace(lo_min, hi, 4001)
    w = dist.pdf(grid)
    share = np.clip(1 - grid / NONE_AFTER_MIN, 0, None)
    return float(np.trapezoid(w * share, grid) / (dist.cdf(hi_min) - dist.cdf(lo_min)))


@lru_cache(maxsize=None)
def band_draws(n: int = DRAWS, seed: int = DRAW_SEED) -> dict[str, RV]:
    """E-22's relative risk of death from bleeding in each band, as draws from a log-normal fitted to its interval,
    each band with a seed of its own (the shape an assumption)."""
    return {name: LogNormalSummary.from_interval(*rr).draws(n, seed + k)
            for k, (name, _, _, rr, _) in enumerate(E22_BANDS)}


def zero_delay_reduction(n: int = DRAWS, seed: int = DRAW_SEED) -> RV:
    """The relative reduction at zero delay, draw by draw, set so that the line's average over the first band
    matches E-22's first band."""
    return (1 - band_draws(n, seed)["up to 1 hour"]) / line_weight(0.0, 60.0)


def band_index(delay_min) -> np.ndarray:
    """Which of E-22's bands a delay falls in: 0 up to 1 hour, 1 from 1 to 3 hours, 2 over 3 hours."""
    d = np.asarray(delay_min, dtype=float)
    return np.select([d <= E22_BANDS[0][2], d <= E22_BANDS[1][2]], [0, 1], 2)


def benefit_left(delay_min: float) -> float:
    """The share of the reduction at zero delay still left at `delay_min` minutes, on the straight line."""
    return float(max(0.0, 1 - float(delay_min) / NONE_AFTER_MIN))


def relative_reduction(delay_min: float, n: int = DRAWS, seed: int = DRAW_SEED) -> RV:
    """The lens's treatment answer: the relative reduction in death from bleeding with tranexamic acid given
    `delay_min` minutes after injury, as draws. After 3 hours it is one minus E-22's band over 3 hours, below zero:
    harm."""
    if float(delay_min) > NONE_AFTER_MIN:
        return 1 - band_draws(n, seed)["over 3 hours"]
    return zero_delay_reduction(n, seed) * benefit_left(delay_min)


def decline_curve(delays_min=tuple(range(0, 241, 5)), n: int = DRAWS, seed: int = DRAW_SEED) -> pd.DataFrame:
    """The relative reduction by delay: the mean of the draws and their central 95%."""
    rows = []
    for d in delays_min:
        rv = relative_reduction(d, n, seed)
        lo, hi = rv.interval()
        rows.append({"minutes": d, "mean": rv.mean(), "lo": lo, "hi": hi, "share left": benefit_left(d)})
    return pd.DataFrame(rows).set_index("minutes")


def band_check(setting: str = "pre_hospital") -> pd.DataFrame:
    """E-22's relative risk in each band, beside the lens's line averaged over the band and the generator's own
    (sum of chances with the drug over sum without, on the battle casualties bleeding significantly and alive at
    pre-hospital care; mechanism). The first band and the band over 3 hours match E-22 by construction; the second
    is a check."""
    observed, truth = _sample(EVAL_SEED, EVAL_N, setting)
    delay = observed["t_phec_min"].to_numpy(float)
    p0, p1 = truth["p_death_untreated"].to_numpy(float), truth["p_death_treated"].to_numpy(float)
    b0 = zero_delay_reduction()
    rows = []
    band = band_index(delay)
    for k, (name, lo, hi, (rr, rlo, rhi), _) in enumerate(E22_BANDS):
        if hi <= NONE_AFTER_MIN:
            lens = 1 - b0 * line_weight(lo, hi)
        else:
            lens = band_draws()[name]
        m = band == k
        llo, lhi = lens.interval()
        rows.append({"band": name, "E-22": rr, "E-22 interval": f"{rlo:.2f} to {rhi:.2f}",
                     "lens, mean of draws": lens.mean(), "lens interval": f"{llo:.2f} to {lhi:.2f}",
                     "generator": float(p1[m].sum() / p0[m].sum()), "casualties": int(m.sum())})
    return pd.DataFrame(rows).set_index("band")


def _averted_lens(observed: pd.DataFrame, extra_min: float = 0.0) -> RV:
    """Expected deaths from bleeding averted per 100 casualties alive at pre-hospital care, with the drug given
    `extra_min` minutes after that, on the lens's line. A casualty who dies in the extra minutes is not reached."""
    care = observed["t_phec_min"].to_numpy(float)
    given = care + extra_min
    q = death_chance()
    after = q * (1 - deaths_by(given / 60)) / (1 - q * deaths_by(care / 60))
    inside = given <= NONE_AFTER_MIN
    line = float((after * np.where(inside, 1 - given / NONE_AFTER_MIN, 0.0)).sum())
    late = float(after[~inside].sum())
    total = zero_delay_reduction() * line + (1 - band_draws()["over 3 hours"]) * late
    return total * (100 / len(care))


def _averted_count(observed: pd.DataFrame, truth: pd.DataFrame) -> float:
    """The generator's own count of deaths from bleeding averted per 100, from its two potential outcomes: deaths
    without the drug that do not happen with it, less deaths with it that do not happen without it, counted only
    after pre-hospital care."""
    du, dt = truth["died_if_untreated"].to_numpy(bool), truth["died_if_treated"].to_numpy(bool)
    after = 60 * truth["t_death_potential_h"].to_numpy(float) > observed["t_phec_min"].to_numpy(float)
    return float(100 * ((du & ~dt).sum() - (dt & ~du & after).sum()) / len(du))


@lru_cache(maxsize=None)
def treatment_results(setting: str = "pre_hospital") -> dict:
    """Deaths from bleeding averted by tranexamic acid per 100 battle casualties bleeding significantly and alive at
    pre-hospital care, given at their own delay and 30 minutes later, on the lens's line, and the generator's count
    at their own delay (mechanism)."""
    observed, truth = _sample(EVAL_SEED, EVAL_N, setting)
    delay = observed["t_phec_min"].to_numpy(float)
    return {"casualties": len(observed), "own delay": _averted_lens(observed), "30 minutes later":
            _averted_lens(observed, 30.0), "generator count": _averted_count(observed, truth),
            "median delay": float(np.median(delay)), "over 3 hours": int((delay > NONE_AFTER_MIN).sum())}


# ------------------------------------------------------------------------------------------------ early and late

EARLY_H = 3.0
LATER_SHARES = (0.0, 0.1, 0.2, 0.3, 0.4)    # assumption: share of the survivors of bleeding who die later
LATER_SEED = 1000


def _inside_three_hours(seed: int, n: int) -> tuple[pd.DataFrame, pd.DataFrame]:
    observed, truth = _sample(seed, n)
    keep = (observed["t_phec_min"].to_numpy(float) <= NONE_AFTER_MIN)
    return observed[keep].reset_index(drop=True), truth[keep].reset_index(drop=True)


def early_late(seed: int, later_share: float, n: int = SPREAD_N) -> dict:
    """On the battle casualties bleeding significantly, alive at pre-hospital care and given or denied tranexamic
    acid at random within 3 hours: deaths within 3 hours of injury, and deaths by 30 days once later deaths from
    other causes are constructed among those who survive their bleeding, a share `later_share` of them, the same in
    both arms (an assumption). The generator's bleeding deaths all fall within its 24-hour horizon."""
    observed, _ = _inside_three_hours(seed, n)
    txa = observed["txa"].to_numpy(bool)
    died = observed["died"].to_numpy(bool)
    early = died & (observed["t_death_h"].to_numpy(float) <= EARLY_H)
    u = np.random.default_rng(LATER_SEED + seed).random(len(observed))
    late = died | (~died & (u < later_share))
    out = {"casualties": len(observed), "given": int(txa.sum())}
    for name, x in (("3 hours", early), ("30 days", late)):
        a, b = float(x[txa].mean()), float(x[~txa].mean())
        out[name] = {"with": a, "without": b, "relative risk": a / b, "difference": a - b}
    return out


@lru_cache(maxsize=None)
def early_late_spread(n: int = SPREAD_N) -> pd.DataFrame:
    """early_late on SEEDS further samples (seeds 43 onward) for each assumed share of later deaths."""
    rows = []
    for k in range(SEEDS):
        seed = EVAL_SEED + 1 + k
        for share in LATER_SHARES:
            r = early_late(seed, share, n)
            rows.append({"seed": seed, "later share": share,
                         **{f"{w} {m}": r[w][m] for w in ("3 hours", "30 days")
                            for m in ("with", "without", "relative risk", "difference")}})
    return pd.DataFrame(rows)


def dilution_summary(n: int = SPREAD_N) -> pd.DataFrame:
    """For each assumed share of later deaths, the mean over seeds of each figure, and the 30-day relative risk less
    the 3-hour one, with its spread."""
    table = early_late_spread(n)
    rows = {}
    for share, g in table.groupby("later share"):
        rows[share] = {
            "3 hours: with, %": 100 * g["3 hours with"].mean(), "3 hours: without, %": 100 * g["3 hours without"].mean(),
            "3 hours: relative risk": g["3 hours relative risk"].mean(),
            "30 days: with, %": 100 * g["30 days with"].mean(), "30 days: without, %": 100 * g["30 days without"].mean(),
            "30 days: relative risk": g["30 days relative risk"].mean(),
            "30-day less 3-hour relative risk": spread_words(g["30 days relative risk"] - g["3 hours relative risk"]),
        }
    return pd.DataFrame.from_dict(rows, orient="index").rename_axis("share of survivors dying later (assumed)")


# ------------------------------------------------------------------------------------------------ rounding

def recorded(minutes) -> np.ndarray:
    """A time recorded to the nearest half hour, halves rounded up."""
    m = np.asarray(minutes, dtype=float)
    return HALF_HOUR * np.floor(m / HALF_HOUR + 0.5)


def _line(delay: np.ndarray, reduction: np.ndarray) -> dict:
    m = delay <= NONE_AFTER_MIN
    slope, intercept = np.polyfit(delay[m], reduction[m], 1)
    return {"reduction at zero delay": float(intercept), "none after, hours": float(-intercept / slope / 60),
            "fall per 15 minutes, share": float(-15 * slope / intercept)}


def rounding(seed: int = EVAL_SEED, n: int = EVAL_N) -> dict:
    """The decline as the generator holds it, read from exact and from recorded delays: a straight line fitted to
    each casualty's relative reduction, one minus its chance of a bleeding death with the drug over its chance
    without, against delay up to 3 hours; and the relative risk in each of E-22's bands, the sum of chances with the
    drug over the sum without. The battle casualties bleeding significantly and alive at pre-hospital care
    (mechanism). Fitting to the chances, which the generator holds and a trial does not, keeps chance deaths from
    hiding the change."""
    observed, truth = _sample(seed, n)
    exact = observed["t_phec_min"].to_numpy(float)
    rec = recorded(exact)
    p0, p1 = truth["p_death_untreated"].to_numpy(float), truth["p_death_treated"].to_numpy(float)
    out = {}
    for name, delay in (("exact", exact), ("recorded", rec)):
        out[name] = _line(delay, 1 - p1 / p0)
        band = band_index(delay)
        for k, (name_k, *_rest) in enumerate(E22_BANDS):
            m = band == k
            out[name][name_k] = float(p1[m].sum() / p0[m].sum())

    out["band changed"] = int((band_index(exact) != band_index(rec)).sum())
    out["casualties"] = len(exact)
    out["treated after 3 hours, recorded within"] = int(((exact > NONE_AFTER_MIN) & (rec <= NONE_AFTER_MIN)).sum())
    return out


@lru_cache(maxsize=None)
def rounding_spread() -> pd.DataFrame:
    """rounding on SEEDS further samples of 100,000 (seeds 43 onward): each figure exact and recorded."""
    rows = {}
    for k in range(SEEDS):
        seed = EVAL_SEED + 1 + k
        r = rounding(seed)
        rows[seed] = {f"{key}, {name}": r[name][key] for name in ("exact", "recorded") for key in r["exact"]}
        rows[seed]["band changed"] = r["band changed"]
    return pd.DataFrame.from_dict(rows, orient="index").rename_axis("sample seed")


def rounding_summary() -> pd.DataFrame:
    """For each figure, exact and recorded means over seeds, and recorded less exact with its spread."""
    table = rounding_spread()
    keys = {"reduction at zero delay": (3, ""), "none after, hours": (2, " hours"),
            "fall per 15 minutes, share": (3, ""), **{f"relative risk, {b[0]}": (3, "") for b in E22_BANDS}}
    rows = {}
    for key, (places, unit) in keys.items():
        col = key.removeprefix("relative risk, ")
        diff = table[f"{col}, recorded"] - table[f"{col}, exact"]
        rows[key] = {"exact": round(table[f"{col}, exact"].mean(), places),
                     "recorded": round(table[f"{col}, recorded"].mean(), places),
                     "recorded less exact": spread_words(diff, places, unit)}
    return pd.DataFrame.from_dict(rows, orient="index").rename_axis("figure, mean over seeds")


# ------------------------------------------------------------------------------------------------ the failure

def failure_rates(seed: int, n: int = SPREAD_N, hazard: str = "constant") -> dict:
    """The only caller of the generator's constant-hazard option. On the battle casualties bleeding significantly,
    from injury: deaths from bleeding without tranexamic acid per hour among those still alive, in the hour around
    1, 6, 9 and 12 hours, as the generator's calibration measures them, and the share of bleeding deaths after 6
    hours (mechanism)."""
    observed, truth = generator.sample(n, seed, return_truth=True, hazard=hazard)
    m = _bleeding_battle(observed, truth)
    times = np.where(truth["died_if_untreated"].to_numpy(bool)[m], truth["t_death_potential_h"].to_numpy(float)[m],
                     np.inf)
    out = {}
    for hour in HOURS + (12.0,):
        at_risk = (times >= hour - 0.5).sum()
        out[f"rate at {hour:g} hours"] = float(((times >= hour - 0.5) & (times < hour + 0.5)).sum() / at_risk)
    died = np.isfinite(times)
    out["share of deaths after 6 hours"] = float((times[died] > 6).mean())
    out["bleeding"] = int(m.sum())
    return out


@lru_cache(maxsize=None)
def failure_spread(n: int = SPREAD_N) -> pd.DataFrame:
    """failure_rates under both hazards on SEEDS samples (seeds 43 onward), the same casualties under each."""
    rows = []
    for k in range(SEEDS):
        seed = EVAL_SEED + 1 + k
        for hazard in generator.HAZARDS:
            rows.append({"seed": seed, "hazard": hazard, **failure_rates(seed, n, hazard)})
    return pd.DataFrame(rows)


def failure_summary(n: int = SPREAD_N) -> pd.DataFrame:
    """Means over seeds under each hazard, and the fixed-rate chain less the time-varying hazard with its spread."""
    table = failure_spread(n)
    keys = [c for c in table.columns if c.startswith("rate") or c.startswith("share")]
    tv = table[table["hazard"] == "time_varying"].set_index("seed")
    fixed = table[table["hazard"] == "constant"].set_index("seed")
    rows = {}
    for key in keys:
        places = 1 if key.startswith("share") else 3
        rows[f"{key}, %"] = {"time-varying hazard": round(100 * tv[key].mean(), places),
                             "fixed-rate chain": round(100 * fixed[key].mean(), places),
                             "fixed-rate less time-varying": spread_words(100 * (fixed[key] - tv[key]), places,
                                                                          " points")}
    return pd.DataFrame.from_dict(rows, orient="index").rename_axis("figure, mean over seeds")


# ------------------------------------------------------------------------------------------------ spread

@lru_cache(maxsize=None)
def scorecard_spread() -> pd.DataFrame:
    """The diagnosis comparison and the treatment check on SEEDS further samples of 100,000 (seeds 43 onward)."""
    rows = {}
    t = decision.threshold()
    for k in range(SEEDS):
        seed = EVAL_SEED + 1 + k
        r = diagnosis_results("pre_hospital", seed, EVAL_N)
        observed, truth = _sample(seed, EVAL_N)
        lens_nb = 100 * decision.net_benefit(r["chance"] >= t, r["target"], t)
        rule_nb = 100 * decision.net_benefit(r["figure flag"], r["target"], t)
        rows[seed] = {"lens Brier": r["lens"]["brier"], "rule Brier": r["figure"]["brier"],
                      "lens net benefit": lens_nb, "rule net benefit": rule_nb,
                      "lens calibration": r["lens"]["calibration"],
                      "averted, lens": _averted_lens(observed).mean(),
                      "averted 30 minutes later, lens": _averted_lens(observed, 30.0).mean(),
                      "averted, generator": _averted_count(observed, truth)}
    return pd.DataFrame.from_dict(rows, orient="index").rename_axis("sample seed")


# ------------------------------------------------------------------------------------------------ the lens

@dataclass(frozen=True)
class Clock:
    minutes_since_injury: float
    next_hour: float          # chance of dying from bleeding in the next hour, if bleeding and alive now
    hourly_rate: float        # deaths from bleeding per hour among those bleeding and alive now


DIAGNOSIS_METRICS = (("sensitivity", "sensitivity at 0.10"), ("specificity", "specificity at 0.10"),
                     ("brier", "Brier score"), ("calibration", "mean chance minus observed share"))


def diagnosis_metric(name: str, setting: str) -> str:
    return (f"{name}, chance of dying from bleeding in the next hour against death from bleeding within the hour "
            f"after pre-hospital care, battle casualties bleeding significantly and alive at pre-hospital care, "
            f"{SETTING_NAMES[setting]}")


class StochasticLens:
    """Lens 05 behind the Lens interface (R-0.8, R-6.1)."""

    name = NAME

    def diagnose(self, casualty: Mapping[str, Any]) -> Clock:
        m = float(casualty["t_phec_min"])
        return Clock(m, float(next_hour(m)), float(hourly_rate(m / 60)))

    def treat(self, casualty: Mapping[str, Any]) -> RV:
        return relative_reduction(float(casualty["t_phec_min"]))

    def scorecard(self) -> list[ScorecardRow]:
        rows = []
        for setting in SETTINGS:
            r = diagnosis_results(setting)
            for key, name in DIAGNOSIS_METRICS:
                rows.append(ScorecardRow(NAME, "diagnosis", diagnosis_metric(name, setting), round(r["lens"][key], 4),
                                         round(r["figure"][key], 4), "mechanism", "weak", "generator"))
        tx = treatment_results()
        group = "battle casualties bleeding significantly and alive at pre-hospital care"
        rows.append(ScorecardRow(NAME, "treatment", f"expected deaths from bleeding averted per 100 by tranexamic acid "
                                 f"at each casualty's own delay, lens's decline, mean of {DRAWS:,} draws, {group}",
                                 round(tx["own delay"].mean(), 4), NO_BASELINE, "mechanism", "native", "generator"))
        rows.append(ScorecardRow(NAME, "treatment", f"lens's expected deaths averted per 100 less the generator's own "
                                 f"count, {group}", round(tx["own delay"].mean() - tx["generator count"], 4),
                                 NO_BASELINE, "mechanism", "native", "generator"))
        return rows


LENS = StochasticLens()


def seven_axes() -> pd.DataFrame:
    """The scorecard on the seven axes of D-21, with the baseline under both readings (D-24) and axis 7 at 0.10
    (D-26)."""
    pre, inside = diagnosis_results("pre_hospital"), diagnosis_results("in_hospital")
    tx = treatment_results()
    spread = scorecard_spread()
    target = pre["target"]
    t = decision.threshold()
    group = (f"{pre['casualties']:,} synthetic battle casualties bleeding significantly and alive at pre-hospital "
             f"care, of whom {pre['died in the next hour']:,} die from bleeding within the hour")
    registry = rules.PUBLISHED["MPTT-24, military"].prevalence     # E-09: Priority 1 in the military registry

    def rule_disc(r):
        return f"sensitivity {_pct(r['sensitivity'])}, specificity {_pct(r['specificity'])}"

    def rule_cal(r):
        gap = r["calibration"]
        return (f"Brier {r['brier']:.3f}; it flags {100 * abs(gap):.1f} points {'more' if gap > 0 else 'fewer'} than "
                f"die within the hour. A rule gives no probability, so the Brier score is the share misclassified")

    own, later, count = tx["own delay"], tx["30 minutes later"], tx["generator count"]
    olo, ohi = own.interval()
    llo, lhi = later.interval()
    d23 = (f"Among the generator's injured in the military cohort, battle and non-battle injury together, "
           f"{_pct(baseline.calibration_need('military'))} need a life-saving intervention, against "
           f"{_pct(registry)} Priority 1 in the military registry (E-01, E-09), so the generator's injured are a milder "
           f"cohort than the one the rule was validated on (D-23)")
    rows = [
        ("1 Discrimination (mechanism)",
         f"It flags none at the threshold of {t:.2f}: the highest chance among them is "
         f"{decision.against_threshold(pre['highest chance'], t, places=4)}, so sensitivity "
         f"{_pct(pre['lens']['sensitivity'])}, specificity {_pct(pre['lens']['specificity'])}; {group}",
         f"{rule_disc(pre['figure'])}, against death within the hour, which the rule was not written for. {d23}",
         rule_disc(pre["text"]),
         f"Not a classifier: expected deaths from bleeding averted per 100 battle casualties bleeding significantly "
         f"and alive at pre-hospital care, with the drug at their own delay, {own.mean():.2f} ({olo:.2f} to "
         f"{ohi:.2f}); with every one of them reached 30 minutes later, {later.mean():.2f} ({llo:.2f} to {lhi:.2f}); "
         f"30 minutes later less their own delay, across {len(spread)} further samples, "
         f"{spread_words(spread['averted 30 minutes later, lens'] - spread['averted, lens'], 2, ' per 100')}; the "
         f"generator's own count on the same casualties at their own delay, {count:.2f}"),
        ("2 Calibration (mechanism)",
         f"Brier {pre['lens']['brier']:.4f}; mean chance minus observed share {pre['lens']['calibration']:+.4f}. The "
         f"lens's hazard is the generator's, so this holds by construction. The lens's Brier score less the rule's, "
         f"across {len(spread)} further samples: {spread_words(spread['lens Brier'] - spread['rule Brier'], 3)}",
         rule_cal(pre["figure"]), rule_cal(pre["text"]),
         f"The lens's expected deaths averted less the generator's count: {own.mean() - count:+.2f} per 100; across "
         f"{len(spread)} further samples, {spread_words(spread['averted, lens'] - spread['averted, generator'], 2, ' per 100')}. "
         f"The lens's line and the generator were both set from E-22 (CRASH-2, a civilian trial), so agreement is by "
         f"construction"),
        ("3 Uncertainty expressed", "None: one chance for each casualty", "None: a priority", "None: a priority",
         f"A distribution: E-22's bands carried as {DRAWS:,} draws"),
        ("4 What it needed",
         f"A hazard through three published hourly rates ({E85_SOURCE}, run here from injury and applied to battle "
         f"casualties, both assumptions), the time since injury, and who is bleeding significantly, which the generator supplies and no medic knows for "
         f"certain",
         "Rules only (E-08)", "Rules only (E-08)",
         "E-22's bands, from an exploratory analysis (E-23) of CRASH-2, a civilian trial; E-24's end of the benefit "
         "at about 3 hours, from pooled trials half of whose patients were obstetric (E-26); a straight line and the "
         "generator's spread of delays within the first band (assumptions)"),
        ("5 Readability", "One look-up: minutes since injury to a chance", "Six yes-or-no steps",
         "Six yes-or-no steps", "One line: the benefit falls to none at 3 hours"),
        ("6 Robustness, setting changed (mechanism)",
         f"Scan in hospital: sensitivity {_pct(inside['lens']['sensitivity'])}, specificity "
         f"{_pct(inside['lens']['specificity'])}, Brier {inside['lens']['brier']:.4f}, unchanged because in the "
         f"generator the setting changes only the scan, which this lens does not read",
         f"Scan in hospital: {rule_disc(inside['figure'])}, unchanged", f"Scan in hospital: "
         f"{rule_disc(inside['text'])}, unchanged",
         "Unchanged: the delay does not depend on where the scan is done"),
        ("7 Decision value",
         axis7(pre["chance"], target) + f". Across {len(spread)} further samples the lens's net benefit less the "
         f"rule's is {spread_words(spread['lens net benefit'] - spread['rule net benefit'], 1, ' per 100')}",
         axis7(pre["figure flag"], target), axis7(pre["text flag"], target),
         "Expected deaths averted are the decision value here: see axis 1"),
    ]
    return pd.DataFrame(rows, columns=["axis", "diagnosis: chance of death from bleeding in the next hour",
                                       "baseline: MPTT-24, figure (as published)",
                                       "baseline: MPTT-24, text (as validated)",
                                       "treatment: benefit of tranexamic acid left at the delay"]).set_index("axis")


# ------------------------------------------------------------------------------------------------ app page 1

def panel(record: Mapping[str, Any], bleeding: bool) -> dict:
    """The stochastic panel for one synthetic casualty on app page 1. Every number is formatted here, so the page
    shows only what the library computed (gate G-8)."""
    care, role2 = float(record["t_phec_min"]), float(record["t_role2_min"])
    clock = LENS.diagnose(record)
    rr = LENS.treat(record)
    lo, hi = rr.interval()
    without = float(chance_after(care))
    with_drug = without * (1 - rr.mean())
    late = care > NONE_AFTER_MIN
    if late:
        left = (f"Tranexamic acid at {care:.1f} minutes is after 3 hours, where the lens uses E-22's band over 3 hours "
                f"in CRASH-2, a civilian trial: a relative reduction of {rr.mean():.2f} ({lo:.2f} to {hi:.2f}), below "
                f"zero, which is harm: more deaths from bleeding with the drug, not fewer")
    else:
        left = (f"Tranexamic acid at {care:.1f} minutes: {_pct(benefit_left(care), 0)} of the reduction it would give "
                f"at the moment of wounding is left on the lens's line, a relative reduction in death from bleeding "
                f"of {rr.mean():.2f} ({lo:.2f} to {hi:.2f})")
    return {
        "heading": "Stochastic panel: how the risk runs with the clock, and how much of the drug's benefit is left",
        "clock": (f"Pre-hospital care at {care:.1f} minutes after injury and arrival at Role 2 at {role2:.1f} minutes: "
                  f"the generator's times, which are assumptions."),
        "risk": (f"If this casualty is bleeding significantly, the chance of dying from it in the hour after "
                 f"pre-hospital care, alive then, is {_pct(clock.next_hour)}, and the hourly death rate among those "
                 f"bleeding and alive at that time is {_pct(clock.hourly_rate, 2)} (mechanism). The rate comes from a "
                 f"hazard fitted to {E85_SOURCE}; it is run here from injury, and applied to a battle casualty, both "
                 f"assumptions."),
        "treatment": (f"{left} (mechanism). If bleeding significantly and alive now, the chance of dying from bleeding "
                      f"later is {_pct(without)} without the drug and {_pct(with_drug)} with it at this delay "
                      f"(mechanism). The line is set from E-22, an exploratory analysis (E-23) of CRASH-2, a civilian "
                      f"trial, and falls to none at about 3 hours as E-24 found in pooled trials half of whose "
                      f"patients were obstetric (E-26). Applying them to a battle casualty is an assumption."),
        "truth": ("In the generator this casualty is bleeding significantly." if bleeding else
                  "In the generator this casualty is not bleeding significantly."),
    }


def page_panel(walk: Any) -> dict:
    """The stochastic panel on app page 1 for one walk-through casualty, given lens 03's Walkthrough (D-27)."""
    return panel(walk.record, walk.significant_bleeding)
