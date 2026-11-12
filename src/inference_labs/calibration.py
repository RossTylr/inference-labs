"""How each parameter in params.yaml is measured on the generator (gate G-4).

Every parameter has one measurement here. `calibration_table` samples the generator at n = 100,000 with
seed 42, measures each parameter, and compares it with its value within its tolerance. The same table is the
calibration table in the slice 0 report.

The MPTT-24 is applied here only to measure the physiology, and under every reading still open under O-1
(step order, and whether each threshold is inclusive). If the readings disagree on any casualty, the triage
figures are reported as missing and the gate fails. The rule itself is coded in slice 2.
"""
from __future__ import annotations

import itertools
import math
from functools import partial
from typing import Any, Callable

import numpy as np
import pandas as pd

N = 100_000
SEED = 42
SITES = ("truncal", "junctional", "extremity")
E22_BANDS = {"up_to_1h": (0.0, 60.0), "from_1h_to_3h": (60.0, 180.0), "over_3h": (180.0, math.inf)}  # E-22


# ------------------------------------------------------------------------------------------------ MPTT-24 readings

def priority_one(obs: pd.DataFrame, thresholds: dict, hr_inclusive: bool = True, rr_inclusive: bool = True,
                 catastrophic_first: bool = True) -> np.ndarray:
    hr, rr = obs["heart_rate"].to_numpy(), obs["respiratory_rate"].to_numpy()
    hr_abn = hr >= thresholds["heart_rate_at_or_above"] if hr_inclusive else hr > thresholds["heart_rate_at_or_above"]
    rr_hi = (rr >= thresholds["respiratory_rate_at_or_above"] if rr_inclusive
             else rr > thresholds["respiratory_rate_at_or_above"])
    signs = hr_abn | rr_hi | (rr < thresholds["respiratory_rate_below"]) | (obs["avpu"].to_numpy() != "A")
    walking, cat = obs["walking"].to_numpy(), obs["catastrophic_haemorrhage"].to_numpy()
    if catastrophic_first:
        return cat | (~walking & signs)
    return ~walking & (cat | signs)


def _readings_agree(obs: pd.DataFrame, thresholds: dict) -> tuple[bool, np.ndarray]:
    readings = [priority_one(obs, thresholds, *flags) for flags in itertools.product([True, False], repeat=3)]
    return all(np.array_equal(readings[0], r) for r in readings[1:]), readings[0]


# ------------------------------------------------------------------------------------------------ measurements

def _shares(series: pd.Series, keys) -> dict:
    counts = series.value_counts(normalize=True)
    return {k: float(counts.get(k, 0.0)) for k in keys}


def _mean(series: pd.Series) -> float:
    return float(series.astype(float).mean())


def _triage(o, t, v):
    agree, p1 = _readings_agree(o, v["mptt24_thresholds"])
    if not agree:
        return {"sensitivity": math.nan, "specificity": math.nan}
    lsi = t["needs_lsi"].to_numpy()
    return {"sensitivity": float(p1[lsi].mean()), "specificity": float((~p1[~lsi]).mean())}


def _thresholds(o, t, v):
    agree, _ = _readings_agree(o, v["mptt24_thresholds"])
    return dict(v["mptt24_thresholds"]) if agree else {k: math.nan for k in v["mptt24_thresholds"]}


def _p1(o, v):
    return priority_one(o, v["mptt24_thresholds"])


def _abnormal_signs(o, v):
    th = v["mptt24_thresholds"]
    rr = o["respiratory_rate"]
    return {
        "heart_rate": o["heart_rate"] >= th["heart_rate_at_or_above"],
        "respiratory_rate": (rr < th["respiratory_rate_below"]) | (rr >= th["respiratory_rate_at_or_above"]),
        "avpu": o["avpu"] != "A",
    }


def _range(series: pd.Series) -> list:
    return [int(series.min()), int(series.max())] if len(series) else [math.nan, math.nan]


def _heart_rate_ranges(o, th):
    hr = o["heart_rate"]
    cut = th["heart_rate_at_or_above"]
    return {"normal": _range(hr[hr < cut]), "abnormal": _range(hr[hr > cut])}


def _respiratory_rate_ranges(o, th):
    rr = o["respiratory_rate"]
    low, high = th["respiratory_rate_below"], th["respiratory_rate_at_or_above"]
    return {"normal": _range(rr[(rr >= low) & (rr < high)]), "low": _range(rr[rr < low]),
            "high": _range(rr[rr >= high])}


def _scan(o, t):
    battle = o["stream"] == "battle"
    out = {}
    for finding, truth_col, scan_col in (("free_fluid", "free_fluid", "scan_free_fluid"),
                                         ("pneumothorax", "pneumothorax", "scan_pneumothorax")):
        truth = t.loc[battle, truth_col].to_numpy(bool)
        result = o.loc[battle, scan_col].to_numpy(bool)
        out[finding] = {"sensitivity": float(result[truth].mean()), "specificity": float((~result[~truth]).mean())}
    return out


def _observed_risk(o, t):
    return np.where(o["txa"], t["p_death_treated"], t["p_death_untreated"])


def _lethal_sites(o, t, v):
    risk = pd.Series(_observed_risk(o, t), index=o.index)[t["bleeding"]]
    by_site = risk.groupby(t.loc[t["bleeding"], "site"]).sum()
    return {s: float(by_site.get(s, 0.0) / by_site.sum()) for s in SITES}


def _hazard(o, t, v):
    b = t["bleeding"]
    times = np.where(t.loc[b, "died_if_untreated"], t.loc[b, "t_death_potential_h"], np.inf)
    out = {}
    for key, hour in (("h_1h", 1.0), ("h_6h", 6.0), ("h_9h", 9.0)):
        at_risk = (times >= hour - 0.5).sum()
        deaths = ((times >= hour - 0.5) & (times < hour + 0.5)).sum()
        out[key] = float(deaths / at_risk) if at_risk else math.nan
    return out


def _severity_slope(o, t, v):
    m = t["bleeding"] & (t["site"] == "truncal")
    p = t.loc[m, "p_death_untreated"].to_numpy()
    return float(np.polyfit(t.loc[m, "severity"], np.log(p / (1 - p)), 1)[0])


def _benefit_line(o, t):
    m = (o["stream"] == "battle") & (t["txa_delay_min"] <= 180)
    slope, intercept = np.polyfit(t.loc[m, "txa_delay_min"], 1 - t.loc[m, "txa_rr"], 1)
    return float(slope), float(intercept)


def _benefit_decay(o, t, v):
    slope, intercept = _benefit_line(o, t)
    return {"decline_per_15min": -15 * slope / intercept, "none_after_h": -intercept / slope / 60}


def _rr_bands(o, t, v):
    b = t["bleeding"]
    delay, p0, p1 = t.loc[b, "txa_delay_min"], t.loc[b, "p_death_untreated"], t.loc[b, "p_death_treated"]
    out = {}
    for key, (lo, hi) in E22_BANDS.items():
        m = (delay > lo) & (delay <= hi)
        out[key] = float(p1[m].sum() / p0[m].sum()) if p0[m].sum() > 0 else math.nan
    return out


def _sbp_bleeding(o, t, v):
    m = t["bleeding"]
    x, y = t.loc[m, "severity"].to_numpy(), o.loc[m, "sbp"].to_numpy(float)
    slope, intercept = np.polyfit(x, y, 1)
    return {"mean": float(intercept), "severity_slope": float(slope),
            "residual_sd": float(np.std(y - (intercept + slope * x), ddof=2))}


def _lognormal(series: pd.Series) -> dict:
    return {"median": float(series.median()), "log_sd": float(np.log(series).std(ddof=1))}


# parameter id -> (which run: default, by_cohort or by_setting; measurement(observed, truth, values))
MEASURES: dict[str, tuple[str, Callable]] = {
    "stream_shares": ("default", lambda o, t, v: _shares(o["stream"], v["stream_shares"])),
    "battle_mechanism": ("default", lambda o, t, v: _shares(o.loc[o["stream"] == "battle", "mechanism"],
                                                            v["battle_mechanism"])),
    "non_battle_mechanism": ("default", lambda o, t, v: _shares(o.loc[o["stream"] == "non_battle", "mechanism"],
                                                                v["non_battle_mechanism"])),
    "battle_patient_type": ("default", lambda o, t, v: _shares(t.loc[o["stream"] == "battle", "patient_type"],
                                                               v["battle_patient_type"])),
    "significant_bleeding_given_haemorrhage": ("default", lambda o, t, v: _mean(
        t.loc[t["patient_type"] == "haemorrhage", "bleeding"])),
    "site_given_mechanism": ("default", lambda o, t, v: {
        m: _shares(t.loc[(t["patient_type"] == "haemorrhage") & (o["mechanism"] == m), "site"], SITES)
        for m in v["site_given_mechanism"]}),
    "pneumothorax_given_chest": ("default", lambda o, t, v: _mean(t.loc[t["patient_type"] == "chest", "pneumothorax"])),
    "tension_given_pneumothorax": ("default", lambda o, t, v: _mean(t.loc[t["pneumothorax"], "tension_pneumothorax"])),
    "severe_given_head": ("default", lambda o, t, v: _mean(t.loc[t["patient_type"] == "head", "head_severe"])),
    "sepsis_given_disease": ("default", lambda o, t, v: _mean(t.loc[o["stream"] == "disease", "sepsis"])),
    "septic_shock_given_sepsis": ("default", lambda o, t, v: _mean(t.loc[t["sepsis"], "septic_shock"])),
    "triage_accuracy_military": ("by_cohort", _triage),
    "triage_accuracy_civilian": ("by_cohort", _triage),
    "mptt24_thresholds": ("default", _thresholds),
    "walking_given_not_priority_one": ("default", lambda o, t, v: _mean(o.loc[~_p1(o, v), "walking"])),
    "catastrophic_haemorrhage_share": ("default", lambda o, t, v: _mean(o.loc[
        _p1(o, v) & t["bleeding"] & t["site"].isin(["junctional", "extremity"]), "catastrophic_haemorrhage"])),
    "abnormal_sign_weights": ("default", lambda o, t, v: {
        k: _mean(flag[_p1(o, v)]) for k, flag in _abnormal_signs(o, v).items()}),
    "heart_rate_ranges": ("default", lambda o, t, v: _heart_rate_ranges(o, v["mptt24_thresholds"])),
    "respiratory_rate_ranges": ("default", lambda o, t, v: _respiratory_rate_ranges(o, v["mptt24_thresholds"])),
    "respiratory_rate_low_share": ("default", lambda o, t, v: _mean(
        (o["respiratory_rate"] < 12)[_abnormal_signs(o, v)["respiratory_rate"]])),
    "avpu_abnormal_shares": ("default", lambda o, t, v: _shares(o.loc[o["avpu"] != "A", "avpu"], ("V", "P", "U"))),
    "sbp_not_bleeding": ("default", lambda o, t, v: {
        "mean": _mean(o.loc[~t["bleeding"], "sbp"]), "sd": float(o.loc[~t["bleeding"], "sbp"].std(ddof=1))}),
    "sbp_bleeding": ("default", _sbp_bleeding),
    "scan_accuracy_in_hospital": ("by_setting", lambda o, t, v: _scan(o, t)),
    "scan_accuracy_pre_hospital": ("by_setting", lambda o, t, v: _scan(o, t)),
    "time_to_phec_min": ("default", lambda o, t, v: _lognormal(o["t_phec_min"])),
    "phec_to_role2_min": ("default", lambda o, t, v: _lognormal(o["t_role2_min"] - o["t_phec_min"])),
    "lethal_haemorrhage_site": ("default", _lethal_sites),
    "bleeding_death_hazard": ("default", _hazard),
    "bleeding_death_severity_log_odds": ("default", _severity_slope),
    "txa_allocation": ("default", lambda o, t, v: _mean(o.loc[o["stream"] == "battle", "txa"])),
    "txa_benefit_at_zero_delay": ("default", lambda o, t, v: _benefit_line(o, t)[1]),
    "txa_rr_by_delay": ("default", _rr_bands),
    "txa_benefit_decay": ("default", _benefit_decay),
}


# ------------------------------------------------------------------------------------------------ comparison

def _normalise(value: Any) -> Any:
    if isinstance(value, dict):
        if value and all(isinstance(x, (int, float)) and not isinstance(x, bool) for x in value.values()):
            total = float(sum(value.values()))
            return {k: float(x) / total for k, x in value.items()}
        return {k: _normalise(x) for k, x in value.items()}
    return value


def _leaves(value: Any, path: tuple = ()) -> list[tuple[tuple, Any]]:
    if isinstance(value, dict):
        return [leaf for k, x in value.items() for leaf in _leaves(x, path + (str(k),))]
    if isinstance(value, list):
        return [leaf for i, x in enumerate(value) for leaf in _leaves(x, path + (str(i),))]
    return [(path, value)]


def _lookup(spec: Any, path: tuple, default: Any) -> Any:
    """Walk a per-key specification (tolerance or comparison) along a leaf's path."""
    for key in path:
        if not isinstance(spec, dict):
            break
        if key in spec:
            spec = spec[key]
    return default if isinstance(spec, dict) or spec is None else spec


def _get(value: Any, path: tuple) -> Any:
    for key in path:
        if isinstance(value, dict):
            value = value.get(key, math.nan)
        elif isinstance(value, list):
            value = value[int(key)] if int(key) < len(value) else math.nan
        else:
            return math.nan
    return value


def _run_kwargs(kind: str, param: dict, defaults: dict) -> dict:
    kwargs = dict(defaults)
    if kind == "by_cohort":
        kwargs["cohort"] = param["cohort"]
    elif kind == "by_setting":
        kwargs["setting"] = param["setting"]
    return kwargs


def calibration_table(params_doc: dict, sampler: Callable | None = None, measures: dict | None = None,
                      n: int = N, seed: int = SEED) -> list[dict]:
    """One row per figure: parameter, key, target, achieved, tolerance, pass."""
    if sampler is None:
        from inference_labs.generator import sample
        sampler = partial(sample, params=params_doc)
    measures = MEASURES if measures is None else measures
    params = params_doc.get("parameters") or {}
    values = {pid: p.get("value") for pid, p in params.items()}
    defaults = params_doc.get("defaults") or {}

    runs: dict[tuple, tuple] = {}
    rows = []
    for pid, p in params.items():
        target = _normalise(p["value"]) if p.get("normalise") else p["value"]
        if pid not in measures:
            for path, t in _leaves(target):
                rows.append({"parameter": pid, "key": ".".join(path), "target": t, "achieved": "no measurement",
                             "tolerance": _lookup(p.get("tolerance"), path, 0), "pass": False})
            continue
        kind, fn = measures[pid]
        kwargs = _run_kwargs(kind, p, defaults)
        key = tuple(sorted(kwargs.items()))
        if key not in runs:
            runs[key] = sampler(n, seed, return_truth=True, **kwargs)
        obs, truth = runs[key]
        achieved = fn(obs, truth, values)
        for path, t in _leaves(target):
            a = _get(achieved, path)
            tol = float(_lookup(p.get("tolerance"), path, 0))
            how = _lookup(p.get("comparison"), path, "within")
            ok = isinstance(a, (int, float)) and not math.isnan(a) and (
                a <= t + tol if how == "at_most" else abs(a - t) <= tol + 1e-12)
            rows.append({"parameter": pid, "key": ".".join(path), "target": t,
                         "achieved": round(a, 4) if isinstance(a, float) else a, "tolerance": tol,
                         "comparison": how, "pass": bool(ok)})
    return rows
