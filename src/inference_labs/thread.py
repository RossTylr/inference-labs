"""Notebook 00, the casualty thread (PRD section 6.11; background/00-casualty-thread.md), and the lens table that sets
every lens's scorecard side by side.

The military record holds three kinds of question (E-117): what happened, who is at risk, and what would change it.
This module gives notebook 00 what it counts on the generator, and the table of every lens's scorecard rows that
notebook 11 and app page 3 show.

    by hand         a hundred synthetic admissions sorted by stream, then the battle-injured by mechanism, against the
                    generator's parameters, which carry E-34 to E-36 and E-35's row counts
    the route       the casualty's route from the point of injury to Role 2, with lens 08's graph placing the
                    interventions, and the generator's assumed times to each echelon
    common, lethal  the bleeding sites of the generator's battle casualties against the sites of its bleeding deaths;
                    the second is set to E-41 by construction
    the failure     a constructed before and after in which the mix and the treatment change at once
    the lens map    each lens's two cases sorted under the three questions; the sorting is this notebook's own, and
                    each lens's fit is read from its scorecard

Every result computed here on the generator is a mechanism, not evidence (D-8).
"""
from __future__ import annotations

import importlib
import math
import pkgutil
from functools import lru_cache

import numpy as np
import pandas as pd

from inference_labs import baseline, generator

STREAMS = generator.STREAMS
STREAM_NAMES = {"disease": "disease", "battle": "battle injury", "non_battle": "non-battle injury"}
MECHANISMS = ("explosion", "small_arms", "other")
MECHANISM_NAMES = {"explosion": "explosion", "small_arms": "small arms", "other": "other"}
HAND_N, HAND_SEED = 100, baseline.EVAL_SEED
SITES = generator.SITES
FOCUS_INJURY = "junctional haemorrhage"     # its chain on lens 08's graph reaches both tourniquet and blood

# The failure: a constructed after in which the battle share is halved, an assumption, and every battle casualty is
# given tranexamic acid.
AFTER_BATTLE_SHARE = 0.15

DESCRIPTION, PREDICTION, COUNTERFACTUAL = "description", "prediction", "counterfactual prediction"
QUESTIONS = (DESCRIPTION, PREDICTION, COUNTERFACTUAL)

# E-117's three tasks with the source's own example from health records, restated for the casualty.
THREE_QUESTIONS = (
    (DESCRIPTION, "How can women with a history of stroke be grouped?", "Who is injured, and how?"),
    (PREDICTION, "What is the probability of a stroke next year?", "Who will die of bleeding?"),
    (COUNTERFACTUAL, "Will starting a statin reduce the risk?", "Does tranexamic acid reduce those deaths?"),
)

# Each lens's two cases, as the notebooks build them, with the kind of question each asks. The sorting is this
# notebook's own reading, not a source's.
LENS_MAP = (
    ("01", "Rules", "rules", "MPTT-24 priority", PREDICTION,
     "ABC score: who is likely to need massive transfusion", PREDICTION),
    ("02", "Frequentist", "frequentist", "a test's error rates, by cohort and setting", DESCRIPTION,
     "a randomised trial read as a test and an interval", COUNTERFACTUAL),
    ("03", "Bayesian", "bayesian", "belief in bleeding into the abdomen after a scan", PREDICTION,
     "belief that tranexamic acid helps, from a trial and a prior", COUNTERFACTUAL),
    ("04", "Decision trees", "trees", "need for an intervention from four signs", PREDICTION,
     "who gets blood first: who is bleeding", PREDICTION),
    ("05", "Stochastic processes", "stochastic", "chance of dying from bleeding in the next hour", PREDICTION,
     "the benefit of tranexamic acid left at a delay", COUNTERFACTUAL),
    ("06", "Connectionist", "connectionist", "a constructed image: is the oval there?", PREDICTION,
     "need for an intervention from four signs", PREDICTION),
    ("07", "Causal", "causal", "who gets scanned, and how that biases measured accuracy", DESCRIPTION,
     "the effect of tranexamic acid, naive, adjusted and true", COUNTERFACTUAL),
    ("08", "Knowledge graph", "knowledge", "findings to candidate injuries, by traversal", PREDICTION,
     "injury to intervention to the echelon that holds it", DESCRIPTION),
    ("09", "Reinforcement learning", "reinforcement", "which question to ask next", PREDICTION,
     "a dosing policy's value, estimated from logs of another", COUNTERFACTUAL),
    ("10", "Decision theory", "decision", "where to set the triage threshold, given costs", PREDICTION,
     "treat here or evacuate; two casualties and one aircraft", COUNTERFACTUAL),
)


# ------------------------------------------------------------------------------------------------ by hand

def _params() -> dict:
    return {pid: p for pid, p in generator.load_params()["parameters"].items()}


def stream_shares() -> dict[str, float]:
    """The generator's default mix as params.yaml holds it (E-34 to E-36): rounded shares that sum to 1.01."""
    return {s: float(v) for s, v in _params()["stream_shares"]["value"].items()}


def mechanism_counts() -> dict[str, int]:
    """E-35's row counts for battle injuries, as params.yaml holds them."""
    return {m: int(v) for m, v in _params()["battle_mechanism"]["value"].items()}


@lru_cache(maxsize=1)
def hundred(seed: int = HAND_SEED) -> pd.DataFrame:
    """A hundred synthetic admissions of the military cohort (mechanism)."""
    return generator.sample(HAND_N, seed)[["id", "stream", "mechanism"]]


def counts_by_stream(table: pd.DataFrame) -> dict[str, int]:
    return {s: int((table["stream"] == s).sum()) for s in STREAMS}


def counts_by_mechanism(table: pd.DataFrame) -> dict[str, int]:
    battle = table[table["stream"] == "battle"]
    return {m: int((battle["mechanism"] == m).sum()) for m in MECHANISMS}


def expected_by_stream(n: int = HAND_N) -> dict[str, float]:
    """What the shares lead one to expect among n admissions. The generator scales them to sum to one; the shares as
    stated do not."""
    shares = stream_shares()
    total = sum(shares.values())
    return {s: n * shares[s] / total for s in STREAMS}


def expected_by_mechanism(n_battle: int) -> dict[str, float]:
    counts = mechanism_counts()
    total = sum(counts.values())
    return {m: n_battle * counts[m] / total for m in MECHANISMS}


# ------------------------------------------------------------------------------------------------ the route

@lru_cache(maxsize=1)
def route() -> dict:
    """The central figure's content: the route from lens 08's graph with E-42's timelines on its legs, where the graph
    places the tourniquet and blood for a junctional bleed, with each placement's edge label, and the generator's
    assumed times to pre-hospital care (standing for Role 1, as in lens 08) and to Role 2 (mechanism)."""
    from inference_labs.lenses import knowledge

    care = knowledge.map_of_care(FOCUS_INJURY)
    placed = {name: (echelon, label) for name, echelon, label in care["lit"]}
    observed, _ = baseline.generator_sample()
    t1, t2 = observed["t_phec_min"].to_numpy(float), observed["t_role2_min"].to_numpy(float)
    return {
        "route": care["route"][:3],
        "first response": care["first response"],
        "legs": [leg for leg in care["legs"] if leg[1] in care["route"][:3]],
        "tourniquet": (knowledge.TOURNIQUET, *placed[knowledge.TOURNIQUET]),
        "blood": (knowledge.BLOOD, *placed[knowledge.BLOOD]),
        "transport": "faster transport: the legs between echelons",
        "minutes": {knowledge.ROLE1: 60, knowledge.ROLE2: 120},
        "times": {knowledge.ROLE1: t1, knowledge.ROLE2: t2},
        "within": {knowledge.ROLE1: float((t1 <= 60).mean()), knowledge.ROLE2: float((t2 <= 120).mean())},
        "medians": {knowledge.ROLE1: float(np.median(t1)), knowledge.ROLE2: float(np.median(t2))},
        "casualties": int(len(observed)),
    }


def casualty_times(casualty: int = 1) -> dict:
    """One battle casualty of the evaluation sample (the casualty-th) and its assumed times (mechanism)."""
    observed, truth = baseline.generator_sample()
    rows = np.flatnonzero((observed["stream"] == "battle").to_numpy())
    i = int(rows[casualty - 1])
    return {"id": int(observed["id"].iloc[i]), "t_phec_min": float(observed["t_phec_min"].iloc[i]),
            "t_role2_min": float(observed["t_role2_min"].iloc[i]), "patient type": str(truth["patient_type"].iloc[i]),
            "site": str(truth["site"].iloc[i])}


# ------------------------------------------------------------------------------------------------ common and lethal

@lru_cache(maxsize=1)
def site_split() -> pd.DataFrame:
    """Among the evaluation sample's battle casualties bleeding significantly, the share at each site; among those who
    would die of bleeding without tranexamic acid, the share at each site; and E-41's split, to which the generator
    sets the second (mechanism, with E-41's figures as published)."""
    _, truth = baseline.generator_sample()
    bleeding = truth["bleeding"].to_numpy(bool)
    dead = truth["died_if_untreated"].to_numpy(bool)
    site = truth["site"].to_numpy()
    lethal = _params()["lethal_haemorrhage_site"]["value"]
    rows = []
    for s in SITES:
        rows.append({"site": s, "share of those bleeding": float((site[bleeding] == s).mean()),
                     "share of bleeding deaths": float((site[dead] == s).mean()), "E-41": float(lethal[s])})
    out = pd.DataFrame(rows).set_index("site")
    out.attrs["bleeding"], out.attrs["deaths"] = int(bleeding.sum()), int(dead.sum())
    return out


# ------------------------------------------------------------------------------------------------ the counterfactual

@lru_cache(maxsize=1)
def tranexamic_both_ways() -> dict:
    """On the evaluation sample's battle casualties alive at pre-hospital care, where the generator gives tranexamic
    acid, deaths from bleeding with every casualty given it and with none given it, from the generator's two potential
    outcomes, which only a generator can hold (mechanism). A casualty whose bleeding death without the drug falls at or
    before that time is left out: the drug is not yet given, and the generator acts on the probability of death, not
    on its timing, so counting them would credit the drug with deaths it could not reach."""
    observed, truth = baseline.generator_sample()
    battle = (observed["stream"] == "battle").to_numpy()
    before_care = baseline.died_before_care(observed, truth)
    keep = battle & ~before_care
    treated = truth["died_if_treated"].to_numpy(bool)[keep]
    untreated = truth["died_if_untreated"].to_numpy(bool)[keep]
    late = truth["txa_delay_min"].to_numpy(float)[keep] > generator.LATE_BAND_MIN
    return {"battle casualties": int(battle.sum()), "died before care": int((battle & before_care).sum()),
            "casualties": int(keep.sum()), "deaths if all treated": int(treated.sum()),
            "deaths if none treated": int(untreated.sum()),
            "per 100 if all treated": 100 * float(treated.mean()), "per 100 if none treated": 100 * float(untreated.mean()),
            "saved": int((untreated & ~treated).sum()), "harmed": int((treated & ~untreated).sum()),
            "harmed, given after 3 hours": int((treated & ~untreated & late).sum())}


def after_mix() -> dict[str, float]:
    """The constructed after's mix: the battle share halved, the rest split as in the default mix (assumption)."""
    shares = stream_shares()
    total = sum(shares.values())
    battle = AFTER_BATTLE_SHARE
    rest = (shares["disease"] + shares["non_battle"]) / total
    return {"battle": battle, "disease": (1 - battle) * shares["disease"] / total / rest,
            "non_battle": (1 - battle) * shares["non_battle"] / total / rest}


def before_after(seed: int = baseline.EVAL_SEED) -> dict:
    """The failure, constructed. Before: 100,000 casualties at the default mix, none given tranexamic acid. After:
    100,000 casualties of a different sample (seed + 100) at the after mix, every battle casualty given it at
    pre-hospital care. Deaths are from bleeding, per 100 casualties, counted from injury. A casualty whose bleeding death
    falls at or before pre-hospital care dies before the drug is given, so dies in the after cohort whether or not it
    was meant for them; the drug's true effect is read from both potential outcomes of the after casualties alive at
    care (mechanism)."""
    _, before = generator.sample(baseline.EVAL_N, seed, return_truth=True)
    after_observed, after = generator.sample(baseline.EVAL_N, seed + 100, mix=after_mix(), return_truth=True)
    before_care = baseline.died_before_care(after_observed, after)
    b = 100 * float(before["died_if_untreated"].mean())
    a_treated = 100 * float((before_care | after["died_if_treated"].to_numpy(bool)).mean())
    a_untreated = 100 * float(after["died_if_untreated"].mean())
    return {"before": b, "after": a_treated, "after, none treated": a_untreated,
            "fall": b - a_treated, "drug": a_untreated - a_treated, "mix": b - a_untreated}


@lru_cache(maxsize=1)
def before_after_spread() -> pd.DataFrame:
    """The before and after on 20 further seeds, 43 to 62, each after drawn at seed + 100 (mechanism)."""
    from inference_labs.lenses import decision

    return decision.across_seeds(before_after)


# ------------------------------------------------------------------------------------------------ the lenses

def lens_modules() -> dict[str, object]:
    """Every module with a LENS: the baseline and each module under inference_labs.lenses, in name order."""
    import inference_labs.lenses as pkg

    found = {"baseline": importlib.import_module("inference_labs.baseline")}
    for m in pkgutil.iter_modules(pkg.__path__):
        module = importlib.import_module(f"inference_labs.lenses.{m.name}")
        if hasattr(module, "LENS"):
            found[m.name] = module
    return found


@lru_cache(maxsize=1)
def scorecards() -> pd.DataFrame:
    """Every scorecard row of every lens, as the lens returns it. Nothing here is typed by hand."""
    rows = []
    for key, module in lens_modules().items():
        for row in module.LENS.scorecard():
            rows.append({"module": key, **vars(row)})
    return pd.DataFrame(rows)


def fits() -> dict[str, dict[str, str]]:
    """Each lens's fit for each case, read from its scorecard rows."""
    out: dict[str, dict[str, str]] = {}
    for (module, case), group in scorecards().groupby(["module", "case"]):
        out.setdefault(module, {})[case] = ", ".join(sorted(set(group["fit"])))
    return out


def lens_map() -> pd.DataFrame:
    """The ten lenses, each case with the kind of question it asks (this notebook's sorting) and the lens's fit for it,
    read from its scorecard."""
    f = fits()
    rows = []
    for number, name, module, dx, dx_q, tx, tx_q in LENS_MAP:
        rows.append({"lens": f"{number} {name}", "diagnosis case": dx, "diagnosis asks": dx_q,
                     "diagnosis fit": f.get(module, {}).get("diagnosis", "no row"), "treatment case": tx,
                     "treatment asks": tx_q, "treatment fit": f.get(module, {}).get("treatment", "no row")})
    return pd.DataFrame(rows).set_index("lens")


def _number(x) -> str:
    if x is None or (isinstance(x, float) and math.isnan(x)):
        return "none stated"
    return f"{x:.4f}"


def lens_table(case: str = "diagnosis") -> pd.DataFrame:
    """Every lens's scorecard rows for one case, as the lenses return them, with values and baselines to four places
    and no baseline shown as "none stated"."""
    if case not in ("diagnosis", "treatment"):
        raise ValueError("case must be diagnosis or treatment")
    card = scorecards()
    card = card[card["case"] == case]
    return pd.DataFrame({"lens": card["lens"].to_numpy(), "metric": card["metric"].to_numpy(),
                         "value": [_number(v) for v in card["value"]],
                         "baseline": [_number(v) for v in card["baseline"]],
                         "label": card["label"].to_numpy(), "fit": card["fit"].to_numpy(),
                         "data": card["data_source"].to_numpy()})


# The lenses whose baseline, in each case, is measured on battle casualties alone or a group within them, as each
# lens's notebook says; every other row's baseline is on every stream of the military cohort.
BATTLE_BASELINES = {"diagnosis": ("Bayesian", "Causal inference", "Stochastic processes"),
                    "treatment": ("Rules", "Hybrids: prediction sets", "Decision trees", "Decision theory")}


def _and(names) -> str:
    names = list(names)
    return names[0] if len(names) == 1 else f"{', '.join(names[:-1])} and {names[-1]}"


def lens_table_rule(cases=("diagnosis", "treatment"), subject: str = "The MPTT-24's figures in these tables are") -> str:
    """D-23's statement for the lens table (lesson 16), naming the casualties the MPTT-24's figures in it are on."""
    from inference_labs.lenses import rules

    rows = _and(f"the {case} rows of {_and(BATTLE_BASELINES[case])}" for case in cases)
    return rules.d23_sentence(scored=(f"every stream of the military cohort, disease included, except in {rows}, "
                                      f"where they are on battle casualties alone or a group within them"),
                              subject=subject)


def lens_summary() -> pd.DataFrame:
    """One row per lens: its rows for each case, their fit, labels and data sources (from the scorecards)."""
    rows = []
    for lens, group in scorecards().groupby("lens", sort=False):
        row = {"lens": lens}
        for case in ("diagnosis", "treatment"):
            g = group[group["case"] == case]
            row[f"{case} rows"] = int(len(g))
            row[f"{case} fit"] = ", ".join(sorted(set(g["fit"]))) or "no row"
        row["labels"] = ", ".join(sorted(set(group["label"])))
        row["data"] = ", ".join(sorted(set(group["data_source"])))
        rows.append(row)
    return pd.DataFrame(rows).set_index("lens")
