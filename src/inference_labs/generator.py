"""The casualty generator (design section 5; R-0.3 to R-0.6).

A directed acyclic graph, sampled forward with a fixed seed:

    mix ──> stream ──> mechanism ──> injury site ──> bleeding ──┬──> physiology ──> MPTT-24 priority
                                                               ├──> scan result  <── setting
                                                               └──> outcome      <── treatment, delay
    setting ──> scan accuracy, time to each echelon

Every number is read from params.yaml, where each carries its evidence id or is labelled an assumption.
Synthetic data drawn here can only confirm the model that made them: every result on them is a mechanism,
not evidence (D-8).

How the evidence enters
- Stream shares and mechanisms are the UK admissions figures (E-34 to E-36).
- Bleeding deaths follow an hourly hazard fitted exactly to the three points of E-85 (log-quadratic in time).
  E-85 is measured from hospital admission; here it runs from injury, which is an assumption. A constant
  hazard, fitted to the same median time to death, exists only for the failure demonstration in lens 05.
- Each bleeding site's death probability is set so that deaths from bleeding split by site as in E-41.
- Tranexamic acid lowers the probability of bleeding death by a benefit that falls linearly to none at
  3 hours (E-24); after 3 hours it raises it by the E-22 relative risk. The benefit at zero delay and the
  delay distribution are assumptions chosen so the generator reproduces the E-22 bands. The treatment acts
  on the probability of bleeding death, not on its timing.
- Physiology is drawn so that the MPTT-24 reproduces the cohort's sensitivity and specificity (E-09).
  No generated value sits where the readings still open under O-1 would disagree.
- Scan accuracy is a table keyed by setting (E-14 in hospital, E-16 before hospital, both provisional
  until O-6 is closed); triage accuracy is a table keyed by cohort (D-13).
"""
from __future__ import annotations

import math
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path

import numpy as np
import pandas as pd
import yaml
from scipy.optimize import brentq
from scipy.special import expit

PARAMS_PATH = Path(__file__).resolve().parents[2] / "params.yaml"

STREAMS = ("disease", "battle", "non_battle")
SITES = ("truncal", "junctional", "extremity")
EXTERNAL_SITES = ("junctional", "extremity")
SIGNS = ("heart_rate", "respiratory_rate", "avpu")
AVPU_ABNORMAL = ("V", "P", "U")
HAZARDS = ("time_varying", "constant")

LATE_BAND_MIN = 180.0    # E-22: the band "over 3 hours"
HORIZON_H = 24.0         # numerical horizon of the hazard integral; under E-85 later deaths are negligible
GRID_STEP_H = 1.0 / 60   # one-minute grid for the inverse-CDF draw of death times

# Every random quantity is drawn for every casualty, in this order, whatever the arguments. Changing the
# setting or cohort therefore changes only what depends on it, not the casualties themselves.
UNIFORMS = (
    "stream", "mechanism", "patient_type", "site", "bleeding", "pneumothorax", "tension", "head", "sepsis",
    "shock", "triage", "walking", "catastrophic", "sign", "heart_rate", "rr_side", "respiratory_rate", "avpu",
    "txa", "scan_free_fluid", "scan_pneumothorax", "death", "death_time",
)
NORMALS = ("severity", "sbp", "t_phec", "t_role2")


# ------------------------------------------------------------------------------------------------ parameters

@lru_cache(maxsize=4)
def _read(path: str) -> dict:
    with open(path, encoding="utf-8") as fh:
        return yaml.safe_load(fh)


def load_params(params: dict | None = None) -> dict:
    """The parameters document: params.yaml unless another document is passed."""
    return _read(str(PARAMS_PATH)) if params is None else params


def _normalised(mapping: dict) -> dict:
    total = float(sum(mapping.values()))
    if total <= 0 or any(float(x) < 0 for x in mapping.values()):
        raise ValueError(f"shares must be non-negative and not all zero: {mapping}")
    return {k: float(x) / total for k, x in mapping.items()}


@dataclass(frozen=True)
class Derived:
    """Quantities computed from the parameters, not chosen: the fitted hazard and the site calibration."""

    hazard_coef: tuple[float, float, float]
    grid_h: np.ndarray
    death_time_cdf: np.ndarray
    death_fraction: float
    median_death_h: float
    constant_rate: float
    site_mix: dict
    site_death_prob: dict
    site_alpha: dict
    triage: dict
    scan: dict


def _fit_hazard(h: dict) -> tuple[float, float, float]:
    """log h(t) = a + b t + c t^2 through the three points of E-85, t in hours."""
    t = np.array([1.0, 6.0, 9.0])
    y = np.log([h["h_1h"], h["h_6h"], h["h_9h"]])
    coef = np.linalg.solve(np.vstack([np.ones(3), t, t**2]).T, y)
    return tuple(float(c) for c in coef)


def _derive(doc: dict) -> Derived:
    v = {pid: p["value"] for pid, p in doc["parameters"].items()}
    coef = _fit_hazard(v["bleeding_death_hazard"])
    grid = np.arange(0.0, HORIZON_H + GRID_STEP_H / 2, GRID_STEP_H)
    h = np.exp(coef[0] + coef[1] * grid + coef[2] * grid**2)
    cum = np.concatenate([[0.0], np.cumsum((h[1:] + h[:-1]) / 2 * np.diff(grid))])
    surv = np.exp(-cum)
    death_fraction = float(1 - surv[-1])
    cdf = (1 - surv) / death_fraction
    median = float(np.interp(0.5, cdf, grid))

    mech = _normalised(v["battle_mechanism"])
    site_mix = {s: sum(mech[m] * _normalised(v["site_given_mechanism"][m])[s] for m in mech) for s in SITES}
    target = _normalised(v["lethal_haemorrhage_site"])
    site_death_prob = {s: death_fraction * target[s] / site_mix[s] for s in SITES}
    if any(p >= 1 for p in site_death_prob.values()):
        raise ValueError(f"the site mix cannot meet E-41: death probabilities {site_death_prob}")

    beta = float(v["bleeding_death_severity_log_odds"])
    x, w = np.polynomial.hermite_e.hermegauss(80)
    w = w / w.sum()
    site_alpha = {
        s: float(brentq(lambda a, p=p: float((expit(a + beta * x) * w).sum()) - p, -30.0, 30.0))
        for s, p in site_death_prob.items()
    }

    triage, scan = {}, {}
    for pid, p in doc["parameters"].items():
        if pid.startswith("triage_accuracy_"):
            triage[p["cohort"]] = (float(p["value"]["sensitivity"]), float(p["value"]["specificity"]))
        if pid.startswith("scan_accuracy_"):
            scan[p["setting"]] = {f: (float(a["sensitivity"]), float(a["specificity"])) for f, a in p["value"].items()}

    return Derived(coef, grid, cdf, death_fraction, median, math.log(2) / median, site_mix, site_death_prob,
                   site_alpha, triage, scan)


@lru_cache(maxsize=4)
def _derived_default() -> Derived:
    return _derive(load_params())


def derived(params: dict | None = None) -> Derived:
    return _derived_default() if params is None else _derive(params)


def bleeding_hazard(t_h, params: dict | None = None) -> np.ndarray:
    """Hourly hazard of death from bleeding at `t_h` hours, without tranexamic acid (fitted to E-85)."""
    a, b, c = derived(params).hazard_coef
    t = np.asarray(t_h, dtype=float)
    return np.exp(a + b * t + c * t**2)


def txa_relative_risk(delay_min, params: dict | None = None) -> np.ndarray:
    """Relative risk of bleeding death with tranexamic acid given `delay_min` minutes after injury."""
    v = {pid: p["value"] for pid, p in load_params(params)["parameters"].items()}
    delay = np.asarray(delay_min, dtype=float)
    none_after = float(v["txa_benefit_decay"]["none_after_h"]) * 60
    benefit = float(v["txa_benefit_at_zero_delay"]) * np.clip(1 - delay / none_after, 0, None)
    return np.where(delay > LATE_BAND_MIN, float(v["txa_rr_by_delay"]["over_3h"]), 1 - benefit)


# ------------------------------------------------------------------------------------------------ sampling

def _categorical(u: np.ndarray, labels, probs) -> np.ndarray:
    p = np.asarray(probs, dtype=float)
    idx = np.searchsorted(np.cumsum(p / p.sum())[:-1], u, side="right")
    return np.asarray(labels, dtype=object)[idx]


def _uniform_int(u: np.ndarray, lo: int, hi: int) -> np.ndarray:
    return (lo + np.floor(u * (hi - lo + 1))).astype(int)


def sample(n: int, seed: int, mix: dict | None = None, setting: str | None = None, return_truth: bool = False,
           *, cohort: str | None = None, hazard: str = "time_varying", params: dict | None = None):
    """Sample `n` casualties forward through the graph.

    mix      stream shares {disease, battle, non_battle}; scaled to sum to one. Default: E-34 to E-36.
    setting  where the scan is done: "pre_hospital" (default) or "in_hospital". Selects the scan accuracy
             row and the time of the scan.
    cohort   whose triage accuracy the physiology reproduces: "military" (default, E-09 registry row) or
             "civilian".
    hazard   "time_varying" (default, fitted to E-85) or "constant" (lens 05 failure demonstration only).

    Returns the observed table; with return_truth=True, a pair (observed, truth) where truth holds the latent
    nodes and both potential outcomes of tranexamic acid.
    """
    doc = load_params(params)
    v = {pid: p["value"] for pid, p in doc["parameters"].items()}
    d = derived(params)
    defaults = doc.get("defaults") or {}
    setting = setting or defaults.get("setting", "pre_hospital")
    cohort = cohort or defaults.get("cohort", "military")
    if setting not in d.scan:
        raise ValueError(f"setting must be one of {sorted(d.scan)}")
    if cohort not in d.triage:
        raise ValueError(f"cohort must be one of {sorted(d.triage)}")
    if hazard not in HAZARDS:
        raise ValueError(f"hazard must be one of {HAZARDS}")
    mix = _normalised(dict(mix if mix is not None else v["stream_shares"]))
    if set(mix) - set(STREAMS):
        raise ValueError(f"mix keys must be among {STREAMS}")

    rng = np.random.default_rng(seed)
    U = {name: rng.random(n) for name in UNIFORMS}
    Z = {name: rng.standard_normal(n) for name in NORMALS}

    # mix -> stream -> mechanism -> patient type and injury site -> bleeding
    stream = _categorical(U["stream"], STREAMS, [mix.get(s, 0.0) for s in STREAMS])
    battle = stream == "battle"
    mechanism = np.full(n, "none", dtype=object)
    for name, key in (("battle", "battle_mechanism"), ("non_battle", "non_battle_mechanism")):
        m = stream == name
        mechanism[m] = _categorical(U["mechanism"][m], list(v[key]), list(v[key].values()))

    patient_type = np.full(n, "dnbi", dtype=object)
    patient_type[battle] = _categorical(U["patient_type"][battle], list(v["battle_patient_type"]),
                                        list(v["battle_patient_type"].values()))
    haem = patient_type == "haemorrhage"
    site = np.full(n, "none", dtype=object)
    for mech, shares in v["site_given_mechanism"].items():
        m = haem & (mechanism == mech)
        site[m] = _categorical(U["site"][m], SITES, [shares[s] for s in SITES])

    bleeding = haem & (U["bleeding"] < v["significant_bleeding_given_haemorrhage"])
    free_fluid = bleeding & (site == "truncal")
    pneumothorax = (patient_type == "chest") & (U["pneumothorax"] < v["pneumothorax_given_chest"])
    tension = pneumothorax & (U["tension"] < v["tension_given_pneumothorax"])
    head_severe = (patient_type == "head") & (U["head"] < v["severe_given_head"])
    sepsis = (stream == "disease") & (U["sepsis"] < v["sepsis_given_disease"])
    septic_shock = sepsis & (U["shock"] < v["septic_shock_given_sepsis"])
    needs_lsi = bleeding | tension | head_severe | septic_shock

    # physiology -> MPTT-24 priority, drawn so the rule reproduces the cohort's accuracy (E-09)
    sens, spec = d.triage[cohort]
    priority_one = np.where(needs_lsi, U["triage"] < sens, U["triage"] < 1 - spec)
    walking = ~priority_one & (U["walking"] < v["walking_given_not_priority_one"])
    catastrophic = priority_one & bleeding & np.isin(site, EXTERNAL_SITES) & (
        U["catastrophic"] < v["catastrophic_haemorrhage_share"])
    sign = np.where(priority_one, _categorical(U["sign"], SIGNS, [v["abnormal_sign_weights"][s] for s in SIGNS]), "none")

    hr_r = v["heart_rate_ranges"]
    heart_rate = np.where(sign == "heart_rate", _uniform_int(U["heart_rate"], *hr_r["abnormal"]),
                          _uniform_int(U["heart_rate"], *hr_r["normal"]))
    rr_r = v["respiratory_rate_ranges"]
    rr_abnormal = sign == "respiratory_rate"
    rr_low = U["rr_side"] < v["respiratory_rate_low_share"]
    respiratory_rate = np.where(
        rr_abnormal & rr_low, _uniform_int(U["respiratory_rate"], *rr_r["low"]),
        np.where(rr_abnormal, _uniform_int(U["respiratory_rate"], *rr_r["high"]),
                 _uniform_int(U["respiratory_rate"], *rr_r["normal"])))
    avpu = np.where(sign == "avpu",
                    _categorical(U["avpu"], AVPU_ABNORMAL, [v["avpu_abnormal_shares"][k] for k in AVPU_ABNORMAL]), "A")

    severity = Z["severity"]
    sb, snb = v["sbp_bleeding"], v["sbp_not_bleeding"]
    sbp = np.where(bleeding, sb["mean"] + sb["severity_slope"] * severity + sb["residual_sd"] * Z["sbp"],
                   snb["mean"] + snb["sd"] * Z["sbp"])
    sbp = np.rint(sbp).astype(int)

    # setting -> time to each echelon, and when the scan is done
    tp, tr = v["time_to_phec_min"], v["phec_to_role2_min"]
    t_phec = np.round(np.exp(math.log(tp["median"]) + tp["log_sd"] * Z["t_phec"]), 1)
    t_role2 = np.round(t_phec + np.exp(math.log(tr["median"]) + tr["log_sd"] * Z["t_role2"]), 1)
    t_scan = t_phec if setting == "pre_hospital" else t_role2

    # bleeding -> scan result <- setting (battle casualties are scanned)
    def scan(truth_flag, finding, u):
        se, sp = d.scan[setting][finding]
        result = np.where(truth_flag, u < se, u < 1 - sp)
        return pd.array(np.where(battle, result, None), dtype="boolean")

    scan_ff = scan(free_fluid, "free_fluid", U["scan_free_fluid"])
    scan_ptx = scan(pneumothorax, "pneumothorax", U["scan_pneumothorax"])

    # bleeding -> outcome <- treatment, delay
    txa = battle & (U["txa"] < v["txa_allocation"])
    delay = np.where(battle, t_phec, np.nan)
    rr = np.where(battle, txa_relative_risk(np.nan_to_num(delay), params), np.nan)
    alpha = np.array([d.site_alpha.get(s, 0.0) for s in site])
    beta = float(v["bleeding_death_severity_log_odds"])
    p0 = np.where(bleeding, expit(alpha + beta * severity), 0.0)
    p1 = np.where(bleeding, np.minimum(1.0, p0 * np.nan_to_num(rr, nan=1.0)), 0.0)
    died_untreated = bleeding & (U["death"] < p0)
    died_treated = bleeding & (U["death"] < p1)
    if hazard == "time_varying":
        t_any = np.interp(U["death_time"], d.death_time_cdf, d.grid_h)
    else:
        t_any = -np.log1p(-U["death_time"]) / d.constant_rate
    t_any = np.round(t_any, 4)
    t_potential = np.where(died_untreated | died_treated, t_any, np.nan)
    died = np.where(txa, died_treated, died_untreated)

    ids = np.arange(1, n + 1)
    observed = pd.DataFrame({
        "id": ids,
        "cohort": cohort,
        "setting": setting,
        "stream": stream,
        "mechanism": mechanism,
        "walking": walking,
        "catastrophic_haemorrhage": catastrophic,
        "respiratory_rate": respiratory_rate,
        "heart_rate": heart_rate,
        "avpu": avpu,
        "sbp": sbp,
        "t_phec_min": t_phec,
        "t_role2_min": t_role2,
        "t_scan_min": t_scan,
        "scan_free_fluid": scan_ff,
        "scan_pneumothorax": scan_ptx,
        "txa": txa,
        "txa_delay_min": np.where(txa, delay, np.nan),
        "died": died,
        "t_death_h": np.where(died, t_any, np.nan),
    })
    if not return_truth:
        return observed
    truth = pd.DataFrame({
        "id": ids,
        "patient_type": patient_type,
        "site": site,
        "bleeding": bleeding,
        "severity": np.where(bleeding, severity, np.nan),
        "free_fluid": free_fluid,
        "pneumothorax": pneumothorax,
        "tension_pneumothorax": tension,
        "head_severe": head_severe,
        "sepsis": sepsis,
        "septic_shock": septic_shock,
        "needs_lsi": needs_lsi,
        "txa_delay_min": delay,
        "txa_rr": rr,
        "p_death_untreated": p0,
        "p_death_treated": p1,
        "died_if_untreated": died_untreated,
        "died_if_treated": died_treated,
        "t_death_potential_h": t_potential,
    })
    return observed, truth
