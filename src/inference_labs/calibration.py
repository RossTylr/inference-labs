"""How each parameter in params.yaml is measured on the generator (gate G-4), and whether the signs carry
information beyond the rule (R-0.15).

Every parameter has one measurement here. `calibration_table` samples the generator at n = 100,000 with
seed 42, measures each parameter, and compares it with its value within its tolerance. The same table is the
calibration table in the slice 0 report.

A parameter marked `emergent: true` is not used by the generator. The two triage rows are of that kind: they
are measured by applying the coded MPTT-24 (baseline.py) to the generated signs, under the text reading, the
one that matches the GCS below 14 on which E-09 was measured, and on the injured only, the disease stream left
out: E-09's military figures come from a trauma registry (E-01).
"""
from __future__ import annotations

import math
from functools import partial
from typing import Any, Callable

import numpy as np
import pandas as pd
from scipy.optimize import minimize
from scipy.special import expit, ndtr

N = 100_000
SEED = 42
SITES = ("truncal", "junctional", "extremity")
STREAMS = ("disease", "battle", "non_battle")
INJURY_STREAMS = ("battle", "non_battle")
AVPU_LEVELS = ("A", "V", "P", "U")
E22_BANDS = {"up_to_1h": (0.0, 60.0), "from_1h_to_3h": (60.0, 180.0), "over_3h": (180.0, math.inf)}  # E-22


# ------------------------------------------------------------------------------------------------ measurements

def _shares(series: pd.Series, keys) -> dict:
    counts = series.value_counts(normalize=True)
    return {k: float(counts.get(k, 0.0)) for k in keys}


def _mean(series: pd.Series) -> float:
    return float(series.astype(float).mean())


def _triage(o, t, v):
    """The coded MPTT-24, under the text reading, against need for a life-saving intervention, on the cohort's
    calibration streams: the injured, as in the trauma registries where E-09 was measured."""
    from inference_labs import baseline

    m = baseline.calibration_cohort(o)
    p1 = baseline.priority_one(o, baseline.CALIBRATION_READING)[m]
    lsi = t["needs_lsi"].to_numpy(bool)[m]
    return {"sensitivity": float(p1[lsi].mean()), "specificity": float((~p1[~lsi]).mean())}


def _states(t: pd.DataFrame) -> dict:
    """The latent conditions each rate responds to, as numbers: one or zero, and where bleeding the centile of
    its severity, from 0 to 1."""
    return {
        "bleeding": t["bleeding"].to_numpy(float),
        "bleeding_by_severity_centile": np.where(t["bleeding"], ndtr(np.nan_to_num(t["severity"].to_numpy(float))), 0.0),
        "tension_pneumothorax": t["tension_pneumothorax"].to_numpy(float),
        "sepsis": t["sepsis"].to_numpy(float),
        "septic_shock": t["septic_shock"].to_numpy(float),
    }


def _rate_model(o, t, column: str, mask=None) -> dict:
    """Least squares of a rate on injury and the latent conditions: the resting mean, the injury increment, the
    effect of each condition, and the residual standard deviation. A term that does not vary in the casualties
    measured (for example sepsis where there is no disease stream, or injury where every casualty is injured) is
    left out and reported as missing; the resting mean then absorbs the injury increment."""
    m = np.ones(len(o), bool) if mask is None else np.asarray(mask, bool)
    injured = o["stream"].isin(INJURY_STREAMS).to_numpy(float)[m]
    columns = {"resting": np.ones(int(m.sum())), "injury": injured}
    columns.update({f"effect:{k}": x[m] for k, x in _states(t).items()})
    kept = {k: x for k, x in columns.items() if k == "resting" or np.ptp(x) > 0}
    X = np.column_stack(list(kept.values()))
    y = o[column].to_numpy(float)[m]
    coef, *_ = np.linalg.lstsq(X, y, rcond=None)
    resid = y - X @ coef
    fitted = dict(zip(kept, (float(c) for c in coef)))
    out: dict = {"resting": fitted["resting"], "injury": fitted.get("injury", math.nan),
                 "effect": {k: fitted.get(f"effect:{k}", math.nan) for k in _states(t)},
                 "residual_sd": float(np.sqrt(resid @ resid / (len(y) - X.shape[1])))}
    return out


def _not_slowed(t):
    return ~t["breathing_slowed"].to_numpy(bool)


def _breathing_slowed(o, t, v):
    head = t["head_severe"].to_numpy(bool)
    slowed = t["breathing_slowed"].to_numpy(bool)
    rr = o["respiratory_rate"].to_numpy(float)
    return {"share_slowed": float(slowed[head].mean()),
            "factor": float(rr[head & slowed].mean() / rr[head & ~slowed].mean())}


def _avpu_bleeding(o, t, v):
    """Maximum likelihood fit of the pressure-driven chance of not being alert in significant bleeding, with the
    base chance taken as stated."""
    m = t["bleeding"].to_numpy(bool)
    x = o.loc[m, "sbp"].to_numpy(float)
    y = (o.loc[m, "avpu"] != "A").to_numpy(float)
    base = float(v["avpu_not_alert_base"])

    def nll(theta):
        even, slope = theta
        p = 1 - (1 - base) * (1 - expit(slope * (x - even) / 10))
        p = np.clip(p, 1e-12, 1 - 1e-12)
        return -float(np.sum(y * np.log(p) + (1 - y) * np.log(1 - p)))

    fit = minimize(nll, x0=[80.0, -1.0], method="Nelder-Mead", options={"xatol": 1e-4, "fatol": 1e-6, "maxiter": 2000})
    return {"even_odds_at_sbp": float(fit.x[0]), "log_odds_per_10_mmhg": float(fit.x[1])}


def _walking(o, t, v):
    can = o["avpu"].isin(["A", "V"]).to_numpy()
    lsi = t["needs_lsi"].to_numpy(bool)
    walking = o["walking"].to_numpy(bool)
    return {"no_intervention": float(walking[can & ~lsi].mean()), "needs_intervention": float(walking[can & lsi].mean())}


def _cohort_physiology(o, t, v):
    """The civilian cohort's heart rate shift and response scale, read against the reference parameters. Every
    civilian is injured and none has sepsis, so the shift is read from the injured mean, and the scale from the
    effects of the conditions that occur (bleeding and tension pneumothorax)."""
    hr = _rate_model(o, t, "heart_rate")
    rr = _rate_model(o, t, "respiratory_rate", _not_slowed(t))
    ref_hr, ref_rr = v["heart_rate"], v["respiratory_rate"]
    injured_mean = hr["resting"] + (0.0 if math.isnan(hr["injury"]) else hr["injury"])
    shift = injured_mean - float(ref_hr["resting"]) - float(ref_hr["injury"])
    pairs = [(hr["effect"][k], float(x)) for k, x in ref_hr["effect"].items() if not math.isnan(hr["effect"][k])]
    pairs += [(rr["effect"][k], float(x)) for k, x in ref_rr["effect"].items() if not math.isnan(rr["effect"][k])]
    fitted, reference = np.array([a for a, _ in pairs]), np.array([b for _, b in pairs])
    return {"heart_rate_shift": float(shift), "response_scale": float(fitted @ reference / (reference @ reference))}


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
    "heart_rate": ("default", lambda o, t, v: _rate_model(o, t, "heart_rate")),
    "respiratory_rate": ("default", lambda o, t, v: _rate_model(o, t, "respiratory_rate", _not_slowed(t))),
    "respiratory_rate_severe_head_injury": ("default", _breathing_slowed),
    "avpu_severe_head_injury": ("default", lambda o, t, v: _shares(o.loc[t["head_severe"], "avpu"], AVPU_LEVELS)),
    "avpu_not_alert_base": ("default", lambda o, t, v: _mean(
        o.loc[~t["bleeding"] & ~t["head_severe"], "avpu"] != "A")),
    "avpu_bleeding": ("default", _avpu_bleeding),
    "avpu_levels_not_alert": ("default", lambda o, t, v: _shares(
        o.loc[~t["head_severe"] & (o["avpu"] != "A"), "avpu"], ("V", "P", "U"))),
    "walking": ("default", _walking),
    "catastrophic_haemorrhage_share": ("default", lambda o, t, v: _mean(o.loc[
        t["bleeding"] & t["site"].isin(["junctional", "extremity"]), "catastrophic_haemorrhage"])),
    "cohort_physiology_civilian": ("by_cohort", _cohort_physiology),
    "cohort_mix_civilian": ("by_cohort", lambda o, t, v: _shares(o["stream"], v["cohort_mix_civilian"])),
    "cohort_mechanism_civilian": ("by_cohort", lambda o, t, v: _shares(
        o.loc[o["stream"] == "non_battle", "mechanism"], v["cohort_mechanism_civilian"])),
    "cohort_patient_type_civilian": ("by_cohort", lambda o, t, v: _shares(
        t.loc[o["stream"] == "non_battle", "patient_type"], v["cohort_patient_type_civilian"])),
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


# ------------------------------------------------------------------------------------------------ R-0.15

SIGNS_GAIN = 0.03           # R-0.15: the regression's area under the curve must exceed the rule's by this much
SIGNS_WITHIN = 0.55         # R-0.15: and must exceed this within every priority
SIGN_FOLDS = 5


def _sign_matrix(observed: pd.DataFrame) -> np.ndarray:
    """The four signs the MPTT-24 reads after the haemorrhage check: walking; conscious level, as one column for
    each level below alert; respiratory rate and its square, since its relation to need runs both ways; and
    heart rate."""
    avpu = observed["avpu"].to_numpy(object)
    rr = observed["respiratory_rate"].to_numpy(float)
    return np.column_stack([observed["walking"].to_numpy(float), avpu == "V", avpu == "P", avpu == "U",
                            rr, rr ** 2, observed["heart_rate"].to_numpy(float)]).astype(float)


def sign_information(observed: pd.DataFrame, truth: pd.DataFrame, reading: str | None = None) -> dict:
    """R-0.15: how much the signs say about need for a life-saving intervention beyond the MPTT-24's answer.

    A logistic regression of need on the four signs is scored out of fold (five folds), so no casualty is
    scored by a model fitted to it. Its area under the curve is set beside the priority's own, with the
    priorities ranked 1 above 2 above 3, and beside the Priority 1 flag alone; then it is computed again within
    each priority, where the rule can no longer tell the casualties apart."""
    from sklearn.linear_model import LogisticRegression
    from sklearn.metrics import roc_auc_score
    from sklearn.model_selection import cross_val_predict
    from sklearn.pipeline import make_pipeline
    from sklearn.preprocessing import StandardScaler

    from inference_labs import baseline

    reading = reading or baseline.DEFAULT_READING
    need = truth["needs_lsi"].to_numpy(bool)
    model = make_pipeline(StandardScaler(), LogisticRegression(max_iter=1000))
    score = cross_val_predict(model, _sign_matrix(observed), need, cv=SIGN_FOLDS, method="predict_proba")[:, 1]
    priority = baseline.triage_table(observed, reading)["priority"].to_numpy(object)
    rank = np.select([priority == baseline.P1, priority == baseline.P2, priority == baseline.P3], [3, 2, 1], 0)
    within = {}
    for p in (baseline.P1, baseline.P2, baseline.P3):
        m = priority == p
        within[p] = float(roc_auc_score(need[m], score[m])) if m.any() and 0 < need[m].mean() < 1 else math.nan
    return {
        "reading": reading,
        "casualties": int(need.size),
        "regression": float(roc_auc_score(need, score)),
        "priority": float(roc_auc_score(need, rank)),
        "priority_one": float(roc_auc_score(need, priority == baseline.P1)),
        "within": within,
    }


def signs_inform(result: dict) -> bool:
    """True when a `sign_information` result meets R-0.15."""
    rule = max(result["priority"], result["priority_one"])
    within = list(result["within"].values())
    return result["regression"] >= rule + SIGNS_GAIN and all(not math.isnan(a) and a > SIGNS_WITHIN for a in within)
