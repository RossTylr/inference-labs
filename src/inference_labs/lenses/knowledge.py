"""Lens 08, knowledge graph (PRD section 6.8; docs/background/08-knowledge-graph.md).

Some knowledge is neither a rule nor a statistic but a maintained map of what connects to what. The lens holds one
hand-built graph in the package's store and answers by traversal. It retrieves what was put there and nothing more.

    diagnosis   the casualty's findings, coded from the record, to candidate injuries along the *suggests* edges,
                returned as a ranked list with the edges behind each candidate (native fit)
    treatment   an injury to intervention, competency, role and echelon, with the timelines on the edges between
                echelons (native fit)

Where the edges come from
- Echelons and timelines: AJP-4.10, NATO doctrine, Edition C Version 1, September 2019 (E-42 to E-44). Whether that
  edition is current was not checked, and every edge taken from it says so (D-28). The timelines are read as time from
  injury, an assumption. The point of injury, where the route starts, is the casualty thread's (D-4).
- Tranexamic acid and blood: the US military's resuscitation guideline (E-86), labelled US doctrine on every edge it
  supplies. It is not UK practice. The earlier tranexamic acid edge is the CRASH-2 regimen (E-19, E-20), a civilian
  trial: the register holds neither the guideline's earlier wording nor which of its updates set the dose.
- The needle: E-104 records a recommended needle of about 5 cm, and measured the chest wall on CT of 100 male military
  cases.
- The MPTT-24: its six steps as published (E-08).
- Every other edge is an assumption written for this lens and labelled so. That includes every *suggests* edge, each
  of which runs from a finding to a condition that, in the generator, makes that finding more likely; and the edges
  from interventions to competencies, roles and echelons that the register does not supply.

The ranking is the graph's own: each finding present adds one over the number of injuries it suggests, so a finding
that points to one injury counts for more than one that points to five. Candidates with equal scores are tied, and
are reported as tied.

Every result computed on the generator is a mechanism, not evidence (D-8).
"""
from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import date
from fractions import Fraction
from functools import lru_cache
from math import lcm
from typing import Any, Mapping

import numpy as np
import pandas as pd
import yaml

from inference_labs import baseline, generator
from inference_labs.graph import provenance
from inference_labs.graph.schema import EDGE_FIELDS, EDGE_LABELS
from inference_labs.graph.store import Edge, Graph, node_key
from inference_labs.interface import ScorecardRow
from inference_labs.lenses import decision, rules, stochastic

NAME = "Knowledge graph"
NO_BASELINE = float("nan")          # the MPTT-24 gives no list of candidates and no chain of care
SETTINGS = baseline.SETTINGS
SETTING_NAMES = baseline.SETTING_NAMES
EVAL_N, EVAL_SEED = baseline.EVAL_N, baseline.EVAL_SEED     # 100,000 synthetic casualties, seed 42
SEEDS = 20                          # further samples behind every spread, seeds 43 onward
TODAY = "2026-11-14"                # the date the graph was built and the default date of a date-aware query
ROOT = provenance.ROOT

# ------------------------------------------------------------------------------------------------ the store

# The package's schema has no edge between echelons. The lens adds one here, in its own module.
EXTRA_EDGE_TYPES = {"leads_to": ("echelon", "echelon")}


class CareGraph(Graph):
    """The package's graph store with one further edge type, from an echelon to the next on the route of care. Every
    edge, of whatever type, must carry label, source, version, valid_from and population."""

    def add_edge(self, src: str, dst: str, edge_type: str, **attrs: Any) -> Edge:
        if edge_type not in EXTRA_EDGE_TYPES:
            return super().add_edge(src, dst, edge_type, **attrs)
        for key in (src, dst):
            if not self.has_node(key):
                raise KeyError(f"no node '{key}'")
        want_src, want_dst = EXTRA_EDGE_TYPES[edge_type]
        if self.node(src)["type"] != want_src or self.node(dst)["type"] != want_dst:
            raise ValueError(f"a '{edge_type}' edge runs from {want_src} to {want_dst}")
        missing = [f for f in EDGE_FIELDS if attrs.get(f) in (None, "")]
        if missing:
            raise ValueError(f"edge {src} -> {dst} is missing {', '.join(missing)}")
        if attrs["label"] not in EDGE_LABELS:
            raise ValueError(f"edge label '{attrs['label']}' is not one of {sorted(EDGE_LABELS)}")
        core = {f: str(attrs.pop(f)) for f in EDGE_FIELDS}
        edge = Edge(src=src, dst=dst, type=edge_type, props=attrs, **core)
        self._edges.append(edge)
        return edge


def name_of(key: str) -> str:
    return key.split(":", 1)[1]


# ------------------------------------------------------------------------------------------------ edge provenance

# AJP-4.10, NATO doctrine, the edition read (E-44), currency not confirmed (D-28).
AJP = {"label": "doctrine", "version": "AJP-4.10 Edition C Version 1, September 2019 (E-44); currency not confirmed",
       "valid_from": "2019-09", "population": "allied joint medical support (NATO doctrine)"}
# E-86, US doctrine. The version read carries rapid updates of June and August 2023; the register does not say which
# update set the tranexamic acid dose, so the edge holds from the latest date in the version read.
US = {"label": "doctrine", "source": "E-86",
      "version": "US Joint Trauma System guideline, published 12 July 2019, with rapid updates in June and August 2023, "
                 "as read (E-86)",
      "valid_from": "2023-08", "population": "US military casualties (US doctrine, not UK practice)"}
# E-19, E-20: CRASH-2, a civilian trial.
CRASH2 = {"label": "trial evidence", "source": "E-19, E-20", "version": "CRASH-2 trial regimen (E-19), 2010",
          "valid_from": "2010",
          "population": "civilian trauma patients entered by clinical judgement within 8 hours of injury, 274 "
                        "hospitals in 40 countries (E-19, E-20)"}
# E-08: the MPTT-24 as published. Its accuracy was measured in two registries (E-09).
MPTT = {"label": "registry evidence", "source": "E-08",
        "version": "MPTT-24, Figure 2 of the corrected version of record (E-08)", "valid_from": "2017",
        "population": "as published; its accuracy was measured in a military and a civilian registry (E-09)"}
# Every edge the register does not supply.
ASSUMED = {"label": "assumption", "source": "assumption", "version": f"written for lens 08, {TODAY}",
           "valid_from": TODAY}
ON_GENERATOR = "the generator's synthetic casualties"
ON_THREAD = "the casualty thread of this repository (D-4)"

# ------------------------------------------------------------------------------------------------ findings and injuries

INJURY, ILLNESS = "presenting with injury", "presenting with illness"


@dataclass(frozen=True)
class Finding:
    name: str
    coded_from: str          # what in the record the finding is coded from
    threshold_from: str      # where its threshold comes from


FINDINGS = (
    Finding("catastrophic haemorrhage", "the record's catastrophic haemorrhage check", "E-08, the first step"),
    Finding("free fluid on the scan", "the scan for free fluid, where one was done", "the scan's own reading"),
    Finding("pneumothorax on the scan", "the scan for pneumothorax, where one was done", "the scan's own reading"),
    Finding("heart rate 100 or more", "heart rate", "E-08: below 100 gives Priority 2"),
    Finding("respiratory rate 24 or more", "respiratory rate", "E-08: 12 to 23 passes"),
    Finding("respiratory rate below 12", "respiratory rate", "E-08: 12 to 23 passes"),
    Finding("systolic pressure under 100", "systolic pressure", "E-86, US doctrine: a massive transfusion predictor"),
    Finding("below alert", "AVPU: responds to voice, to pain or not at all", "the AVPU scale"),
    Finding("not walking", "the record's walking check", "E-08, the second step"),
)
FINDING_NAMES = tuple(f.name for f in FINDINGS)
SBP_UNDER = 100                      # E-86: systolic pressure under 100, a massive transfusion predictor


def findings(observed: pd.DataFrame) -> pd.DataFrame:
    """Each casualty's findings, coded from the record as the terms the graph holds (one column per finding)."""
    def flag(col):
        return observed[col].astype("boolean").fillna(False).to_numpy(bool)

    return pd.DataFrame({
        "catastrophic haemorrhage": flag("catastrophic_haemorrhage"),
        "free fluid on the scan": flag("scan_free_fluid"),
        "pneumothorax on the scan": flag("scan_pneumothorax"),
        "heart rate 100 or more": (observed["heart_rate"] >= baseline.HR_BELOW).to_numpy(),
        "respiratory rate 24 or more": (observed["respiratory_rate"] > baseline.RR_TO).to_numpy(),
        "respiratory rate below 12": (observed["respiratory_rate"] < baseline.RR_FROM).to_numpy(),
        "systolic pressure under 100": (observed["sbp"] < SBP_UNDER).to_numpy(),
        "below alert": (observed["avpu"] != "A").to_numpy(),
        "not walking": ~flag("walking"),
    }, index=observed.index)[list(FINDING_NAMES)]


def context(observed: pd.DataFrame) -> np.ndarray:
    """Presenting with injury (the battle and non-battle injury streams) or with illness (the disease stream)."""
    return np.where(observed["stream"].to_numpy() == "disease", ILLNESS, INJURY)


def _frame(record: Mapping[str, Any]) -> pd.DataFrame:
    row = {k: record.get(k) for k in ("catastrophic_haemorrhage", "scan_free_fluid", "scan_pneumothorax",
                                       "heart_rate", "respiratory_rate", "sbp", "avpu", "walking", "stream")}
    for k in ("scan_free_fluid", "scan_pneumothorax"):
        v = row[k]
        row[k] = None if v is None or v is pd.NA or (isinstance(v, float) and np.isnan(v)) else bool(v)
    frame = pd.DataFrame([row])
    for k in ("scan_free_fluid", "scan_pneumothorax", "catastrophic_haemorrhage", "walking"):
        frame[k] = frame[k].astype("boolean")
    return frame


def findings_of(record: Mapping[str, Any]) -> tuple[str, ...]:
    row = findings(_frame(record)).iloc[0]
    return tuple(name for name in FINDING_NAMES if bool(row[name]))


INJURIES = ("extremity haemorrhage", "junctional haemorrhage", "truncal haemorrhage", "tension pneumothorax",
            "severe head injury", "septic shock")
HAEMORRHAGES = INJURIES[:3]


def true_condition(truth: pd.DataFrame) -> np.ndarray:
    """The condition each casualty has that needs a life-saving intervention, in the generator's truth, or "" for none.
    The four kinds of need in the generator are significant bleeding (at one of three sites), tension pneumothorax,
    severe head injury and septic shock, and a casualty has at most one."""
    site, bleeding = truth["site"].to_numpy(), truth["bleeding"].to_numpy(bool)
    out = np.full(len(truth), "", dtype=object)
    for s in ("extremity", "junctional", "truncal"):
        out[bleeding & (site == s)] = f"{s} haemorrhage"
    out[truth["tension_pneumothorax"].to_numpy(bool)] = "tension pneumothorax"
    out[truth["head_severe"].to_numpy(bool)] = "severe head injury"
    out[truth["septic_shock"].to_numpy(bool)] = "septic shock"
    return out


# Each edge runs from a finding to a condition that, in the generator, makes the finding more likely, and is followed
# only for a casualty presenting as the edge says. All are assumptions.
SUGGESTS = (
    ("catastrophic haemorrhage", "extremity haemorrhage", INJURY),
    ("catastrophic haemorrhage", "junctional haemorrhage", INJURY),
    ("free fluid on the scan", "truncal haemorrhage", INJURY),
    ("pneumothorax on the scan", "tension pneumothorax", INJURY),
    *(("heart rate 100 or more", i, INJURY) for i in HAEMORRHAGES + ("tension pneumothorax",)),
    ("heart rate 100 or more", "septic shock", ILLNESS),
    *(("respiratory rate 24 or more", i, INJURY) for i in HAEMORRHAGES + ("tension pneumothorax",)),
    ("respiratory rate 24 or more", "septic shock", ILLNESS),
    ("respiratory rate below 12", "severe head injury", INJURY),
    *(("systolic pressure under 100", i, INJURY) for i in HAEMORRHAGES),
    ("below alert", "severe head injury", INJURY),
    *(("below alert", i, INJURY) for i in HAEMORRHAGES),
    *(("not walking", i, INJURY) for i in INJURIES[:5]),
    ("not walking", "septic shock", ILLNESS),
)

# ------------------------------------------------------------------------------------------------ the capability chain

TOURNIQUET = "tourniquet or haemostatic dressing"
TXA = "tranexamic acid"
BLOOD = "blood: whole blood, otherwise components at about 1:1:1"
NEEDLE = "needle decompression"
SURGERY = "surgery"
AIRWAY = "airway management"
CT = "CT scan"
SEPSIS_CARE = "antibiotics and fluids"
INTERVENTIONS = (TOURNIQUET, TXA, BLOOD, NEEDLE, SURGERY, AIRWAY, CT, SEPSIS_CARE)

REQUIRES = {TOURNIQUET: "control of severe bleeding", TXA: "advanced resuscitation", BLOOD: "transfusion",
            NEEDLE: "chest decompression", SURGERY: "operating", AIRWAY: "airway, breathing and circulation",
            CT: "CT imaging", SEPSIS_CARE: "sepsis care"}
COMPETENCIES = tuple(dict.fromkeys(REQUIRES.values()))

SOLDIER, MEDIC, PHEC, RESUS, SURGEONS, RADIOLOGY = ("any trained soldier", "medic", "pre-hospital emergency care team",
                                                     "resuscitation team", "surgical team", "radiology team")
ROLES = (SOLDIER, MEDIC, PHEC, RESUS, SURGEONS, RADIOLOGY)
HELD_BY = {
    "control of severe bleeding": (SOLDIER, MEDIC, PHEC, SURGEONS),
    "airway, breathing and circulation": (SOLDIER, MEDIC, PHEC, RESUS),
    "advanced resuscitation": (PHEC, RESUS),
    "transfusion": (PHEC, RESUS),
    "chest decompression": (MEDIC, PHEC, RESUS),
    "operating": (SURGEONS,),
    "CT imaging": (RADIOLOGY,),
    "sepsis care": (RESUS,),
}

POINT, ROLE1, ROLE2, ROLE3, ROLE4 = "point of injury", "Role 1", "Role 2", "Role 3", "Role 4"
ECHELONS = (POINT, ROLE1, ROLE2, ROLE3, ROLE4)
ECHELON_WHAT = {
    POINT: "where the casualty lies, the start of the casualty thread (D-4)",
    ROLE1: "primary care, triage and pre-hospital emergency care (E-43)",
    ROLE2: "forward, basic and enhanced (E-43)",
    ROLE3: "deployed hospital with CT (E-43)",
    ROLE4: "definitive care at home (E-43)",
}
FIRST_RESPONSE = "10 minutes: life-saving first response (E-42)"
# E-42's timelines are read here as time from injury, an assumption.
FROM_INJURY = "each timeline read here as time from injury, an assumption"
# (from, to, minutes or None, the timeline as E-42 states it)
LEADS_TO = (
    (POINT, ROLE1, 60, "1 hour: advanced resuscitation and pre-hospital emergency care (E-42)"),
    (ROLE1, ROLE2, 120, "2 hours: life-, limb- and function-preserving surgery and resuscitation (E-42)"),
    (ROLE2, ROLE3, None, "no timeline in E-42"),
    (ROLE3, ROLE4, None, "no timeline in E-42"),
)
# (role, echelon, the edge's provenance)
AVAILABLE_AT = (
    (SOLDIER, POINT, None), (MEDIC, POINT, None), (MEDIC, ROLE1, None),
    (PHEC, ROLE1, "E-43"),
    (RESUS, ROLE2, None), (RESUS, ROLE3, None), (SURGEONS, ROLE2, None), (SURGEONS, ROLE3, None),
    (RADIOLOGY, ROLE3, "E-43"),
)

TXA_DOSES = {"CRASH-2": {"dose": "1 g over 10 minutes, then 1 g over 8 hours",
                         "condition": "within 8 hours of injury, on clinical judgement", "window_min": 480},
             "E-86": {"dose": "2 g", "condition": "only if started within 3 hours of injury", "window_min": 180}}
NEEDLE_CM, CATHETER_CM = rules.NEEDLE_CM, rules.CATHETER_CM     # E-104
NEEDLE_POPULATION = "not stated in the register"
CHEST_WALL_POPULATION = "male military personnel: CT of 100 male military cases (E-104)"


def _k(t: str, name: str) -> str:
    return node_key(t, name)


def _care_edges(g: CareGraph) -> None:
    for f in FINDINGS:
        g.add_node("finding", f.name, coded_from=f.coded_from, threshold_from=f.threshold_from)
    for i in INJURIES:
        g.add_node("injury", i)
    for v in INTERVENTIONS:
        g.add_node("intervention", v)
    for c in COMPETENCIES:
        g.add_node("competency", c)
    for r in ROLES:
        g.add_node("role", r)
    for e in ECHELONS:
        g.add_node("echelon", e, what=ECHELON_WHAT[e])
    g.node(_k("echelon", POINT))["timeline"] = FIRST_RESPONSE

    for f, i, when in SUGGESTS:
        g.add_edge(_k("finding", f), _k("injury", i), "suggests", population=ON_GENERATOR, when=when, **ASSUMED)

    def treated(injury, intervention, prov, **props):
        g.add_edge(_k("injury", injury), _k("intervention", intervention), "treated_by", **prov, **props)

    for i in ("extremity haemorrhage", "junctional haemorrhage"):
        treated(i, TOURNIQUET, {**ASSUMED, "population": ON_THREAD}, wording="E-08's instruction at its first step")
    for i in HAEMORRHAGES:                         # the earlier version is entered first, as a graph built then would be
        treated(i, TXA, CRASH2, **TXA_DOSES["CRASH-2"])
    for i in HAEMORRHAGES:
        treated(i, TXA, US, **TXA_DOSES["E-86"])
    for i in HAEMORRHAGES:
        treated(i, BLOOD, US)
    for i in ("junctional haemorrhage", "truncal haemorrhage"):
        treated(i, SURGERY, {**ASSUMED, "population": ON_THREAD})
    treated("tension pneumothorax", NEEDLE,
            {"label": "doctrine", "source": "E-104", "version": "the recommended length as E-104 records it (2007)",
             "valid_from": "2007", "population": NEEDLE_POPULATION}, length_cm=NEEDLE_CM, device="needle")
    treated("tension pneumothorax", NEEDLE,
            {"label": "registry evidence", "source": "E-104", "version": "E-104 (2007)", "valid_from": "2007",
             "population": CHEST_WALL_POPULATION}, length_cm=CATHETER_CM, device="catheter",
            reaches="99% of the 100 cases (E-104)")
    treated("severe head injury", AIRWAY, {**ASSUMED, "population": ON_THREAD})
    treated("severe head injury", CT, {**ASSUMED, "population": ON_THREAD})
    treated("septic shock", SEPSIS_CARE, {**ASSUMED, "population": ON_THREAD})

    for v, c in REQUIRES.items():
        g.add_edge(_k("intervention", v), _k("competency", c), "requires", population=ON_THREAD, **ASSUMED)
    for c, roles in HELD_BY.items():
        for r in roles:
            g.add_edge(_k("competency", c), _k("role", r), "held_by", population=ON_THREAD, **ASSUMED)
    for r, e, src in AVAILABLE_AT:
        prov = {**AJP, "source": src} if src else {**ASSUMED, "population": ON_THREAD}
        g.add_edge(_k("role", r), _k("echelon", e), "available_at", **prov)
    for a, b, minutes, words in LEADS_TO:
        g.add_edge(_k("echelon", a), _k("echelon", b), "leads_to", source="E-42, E-43", timeline=words,
                   minutes=minutes, **AJP)


# ------------------------------------------------------------------------------------------------ the rule as edges

# (step, observation, how it is tested, {answer: priority})
RULE_STEPS = (
    (1, "catastrophic haemorrhage", {"kind": "flag", "column": "catastrophic_haemorrhage"}, {"yes": baseline.P1}),
    (2, "walking", {"kind": "flag", "column": "walking"}, {"yes": baseline.P3}),
    (3, "breathing", {"kind": "flag", "column": "breathing", "absent": "yes"}, {"no": baseline.DEAD}),
    (4, "responds to voice", {"kind": "not in", "column": "avpu", "exits": dict(baseline.VOICE_EXITS)},
     {"no": baseline.P1}),
    (5, "respiratory rate", {"kind": "range", "column": "respiratory_rate", "from": baseline.RR_FROM,
                             "to": baseline.RR_TO}, {"no": baseline.P1}),
    (6, "heart rate", {"kind": "below", "column": "heart_rate", "value": baseline.HR_BELOW},
     {"yes": baseline.P2, "no": baseline.P1}),
)


def _rule_edges(g: CareGraph) -> None:
    for p in baseline.PRIORITIES:
        g.add_node("priority", p)
    for step, obs, test, assigns in RULE_STEPS:
        g.add_node("observation", obs)
        th = g.add_node("threshold", baseline.STEPS[step - 1], step=step)
        g.add_edge(th, _k("observation", obs), "tests", **MPTT, **test)
        for answer, priority in assigns.items():
            g.add_edge(th, _k("priority", priority), "assigns", when=answer, **MPTT)


@lru_cache(maxsize=1)
def care_graph() -> CareGraph:
    """The hand-built graph: the capability chain and the MPTT-24 as edges."""
    g = CareGraph()
    _care_edges(g)
    _rule_edges(g)
    return g


CHAIN_TYPES = ("finding", "injury", "intervention", "competency", "role", "echelon")
RULE_TYPES = ("threshold", "observation", "priority")


def node_counts(graph: Graph | None = None) -> dict:
    g = care_graph() if graph is None else graph
    return {t: len(g.nodes(t)) for t in CHAIN_TYPES + RULE_TYPES}


def edge_table(graph: Graph | None = None) -> pd.DataFrame:
    """Every edge with its five fields."""
    g = care_graph() if graph is None else graph
    return pd.DataFrame([{"from": name_of(e.src), "type": e.type, "to": name_of(e.dst), "label": e.label,
                          "source": e.source, "version": e.version, "valid_from": e.valid_from,
                          "population": e.population} for e in g.edges()])


# ------------------------------------------------------------------------------------------------ dates and populations

def _date(text: str) -> date:
    parts = [int(p) for p in str(text).split("-")]
    return date(parts[0], parts[1] if len(parts) > 1 else 1, parts[2] if len(parts) > 2 else 1)


def first_found(src: str, dst: str, edge_type: str = "treated_by", graph: Graph | None = None) -> Edge:
    """The query that ignores versions: the first edge entered between the two nodes."""
    g = care_graph() if graph is None else graph
    return g.edges(src=src, dst=dst, type=edge_type)[0]


@dataclass(frozen=True)
class Dated:
    edge: Edge | None             # the newest edge valid on the date asked, or None where none is or several tie
    tied: tuple                   # equally new edges, where more than one is valid from the same date
    later: tuple                  # edges between the same nodes valid only after that date
    earlier: tuple                # older versions


def as_of(src: str, dst: str, when: str = TODAY, edge_type: str = "treated_by", graph: Graph | None = None) -> Dated:
    """The date-aware query: the newest edge valid on `when`, with any versions before or after it."""
    g = care_graph() if graph is None else graph
    edges = g.edges(src=src, dst=dst, type=edge_type)
    valid = [e for e in edges if _date(e.valid_from) <= _date(when)]
    later = tuple(e for e in edges if _date(e.valid_from) > _date(when))
    if not valid:
        return Dated(None, (), later, ())
    newest = max(_date(e.valid_from) for e in valid)
    current = tuple(e for e in valid if _date(e.valid_from) == newest)
    earlier = tuple(e for e in valid if _date(e.valid_from) < newest)
    if len(current) == 1:
        return Dated(current[0], (), later, earlier)
    return Dated(None, current, later, earlier)


HOLDS, NOT_STATED, OTHER = "holds", "population not stated", "another population"


def holds_for(edge: Edge, population: str) -> str:
    """Whether an edge's population covers the casualty's, by its population field alone."""
    pop = edge.population.lower()
    if "not stated" in pop:
        return NOT_STATED
    return HOLDS if population.lower() in pop else OTHER


def population_query(src: str, dst: str, population: str = "military", edge_type: str = "treated_by",
                     graph: Graph | None = None) -> list[tuple[Edge, str]]:
    """Every edge between the two nodes, each with whether it holds for the population asked about."""
    g = care_graph() if graph is None else graph
    return [(e, holds_for(e, population)) for e in g.edges(src=src, dst=dst, type=edge_type)]


def select_edge(src: str, dst: str, when: str = TODAY, population: str = "military",
                graph: Graph | None = None) -> tuple[Edge | None, tuple[str, ...]]:
    """The edge a careful query would use: the newest valid on `when`; where several are equally new, the one whose
    population holds for the casualty. The notes say what was set aside."""
    d = as_of(src, dst, when, graph=graph)
    notes = []
    if d.edge is not None:
        chosen = d.edge
    elif d.tied:
        ranked = sorted(d.tied, key=lambda e: (HOLDS, NOT_STATED, OTHER).index(holds_for(e, population)))
        chosen = ranked[0]
        notes += [f"an edge whose population is {e.population.split(':')[0]} set aside ({holds_for(e, population)})"
                  for e in ranked[1:]]
    else:
        chosen = None
    if d.earlier:
        notes.append(f"{len(d.earlier)} earlier version{'s' if len(d.earlier) > 1 else ''} set aside")
    if d.later:
        notes.append(f"{len(d.later)} later version{'s' if len(d.later) > 1 else ''} not yet valid on {when}")
    return chosen, tuple(notes)


# ------------------------------------------------------------------------------------------------ diagnosis

@dataclass(frozen=True)
class Candidate:
    injury: str
    score: float
    rank: int                     # 1 + the number of candidates scoring higher; tied candidates share a rank
    tied: int                     # how many candidates share this rank
    edges: tuple                  # the suggests edges that produced it

    def because(self) -> str:
        return ", ".join(name_of(e.src) for e in self.edges)


@dataclass(frozen=True)
class Diagnosis:
    findings: tuple
    context: str
    candidates: tuple             # ranked, ties kept together in the order the injuries were entered

    def first(self) -> Candidate | None:
        return self.candidates[0] if self.candidates else None


def out_degree(finding: str, graph: Graph | None = None) -> int:
    g = care_graph() if graph is None else graph
    return len(g.edges(src=_k("finding", finding), type="suggests"))


def rank(found: tuple, how: str, graph: Graph | None = None) -> tuple[Candidate, ...]:
    """Traverse the suggests edges from each finding present, following an edge only where the casualty presents as
    it says, and add one over the finding's number of suggests edges to the injury it reaches."""
    g = care_graph() if graph is None else graph
    scores: dict[str, Fraction] = {}
    edges: dict[str, list] = {}
    for f in found:
        k = _k("finding", f)
        if not g.has_node(k):
            continue
        out = g.edges(src=k, type="suggests")
        for e in out:
            if e.props.get("when", INJURY) != how:
                continue
            scores[e.dst] = scores.get(e.dst, Fraction(0)) + Fraction(1, len(out))
            edges.setdefault(e.dst, []).append(e)
    order = {k: n for n, k in enumerate(g.nodes("injury"))}
    keys = sorted(scores, key=lambda k: (-scores[k], order[k]))
    return tuple(Candidate(name_of(k), float(scores[k]), 1 + sum(scores[j] > scores[k] for j in keys),
                           sum(scores[j] == scores[k] for j in keys), tuple(edges[k])) for k in keys)


def diagnose_record(record: Mapping[str, Any]) -> Diagnosis:
    found = findings_of(record)
    how = ILLNESS if record.get("stream") == "disease" else INJURY
    return Diagnosis(found, how, rank(found, how))


@lru_cache(maxsize=1)
def _weights() -> tuple[int, np.ndarray, np.ndarray]:
    """Integer weight matrices, finding by injury, one for each way of presenting, so that ties are exact."""
    g = care_graph()
    scale = lcm(*(out_degree(f) for f in FINDING_NAMES))
    w = {INJURY: np.zeros((len(FINDING_NAMES), len(INJURIES)), int),
         ILLNESS: np.zeros((len(FINDING_NAMES), len(INJURIES)), int)}
    for a, f in enumerate(FINDING_NAMES):
        out = g.edges(src=_k("finding", f), type="suggests")
        for e in out:
            w[e.props["when"]][a, INJURIES.index(name_of(e.dst))] += scale // len(out)
    return scale, w[INJURY], w[ILLNESS]


def score_matrix(observed: pd.DataFrame) -> np.ndarray:
    """Every casualty's score for every injury, in units of one over the scale (exact integers)."""
    _, w_inj, w_ill = _weights()
    f = findings(observed).to_numpy(int)
    ill = context(observed) == ILLNESS
    return np.where(ill[:, None], f @ w_ill, f @ w_inj)


def list_results(observed: pd.DataFrame, truth: pd.DataFrame) -> dict:
    """The ranked list scored against each casualty's true condition, and the flag 'any candidate' against need."""
    s = score_matrix(observed)
    top = s.max(axis=1)
    flag = top > 0
    cond = true_condition(truth)
    has = cond != ""
    idx = np.array([INJURIES.index(c) if c else 0 for c in cond])
    own = s[np.arange(len(s)), idx]
    at_top = has & (own == top) & (top > 0)
    alone = at_top & ((s == top[:, None]).sum(axis=1) == 1)
    anywhere = has & (own > 0)
    by = {}
    for c in INJURIES:
        m = cond == c
        by[c] = {"casualties": int(m.sum()), "first, alone": float(alone[m].mean()) if m.any() else float("nan"),
                 "first, alone or tied": float(at_top[m].mean()) if m.any() else float("nan"),
                 "anywhere in the list": float(anywhere[m].mean()) if m.any() else float("nan")}
    need = truth["needs_lsi"].to_numpy(bool)
    return {"casualties": len(s), "with a condition": int(has.sum()),
            "first, alone": float(alone[has].mean()), "first, alone or tied": float(at_top[has].mean()),
            "anywhere in the list": float(anywhere[has].mean()),
            "candidates per casualty flagged": float((s[flag] > 0).sum(axis=1).mean()),
            "flag": flag, "need": need, "flag metrics": baseline.flag_metrics(flag, need), "by condition": by}


LIST_MEASURES = ("first, alone", "first, alone or tied", "anywhere in the list")


@lru_cache(maxsize=2 * SEEDS + 4)
def _sample(seed: int = EVAL_SEED, setting: str = "pre_hospital"):
    if seed == EVAL_SEED:
        return baseline.generator_sample(setting)
    return generator.sample(EVAL_N, seed, setting=setting, return_truth=True)


@lru_cache(maxsize=None)
def diagnosis_results(setting: str = "pre_hospital", seed: int = EVAL_SEED) -> dict:
    """The graph and the MPTT-24 on the military cohort's synthetic casualties (mechanism)."""
    observed, truth = _sample(seed, setting)
    r = list_results(observed, truth)
    need = r["need"]
    r["figure"] = baseline.flag_metrics(baseline.priority_one(observed, "figure"), need)
    r["text"] = baseline.flag_metrics(baseline.priority_one(observed, "text"), need)
    r["figure flag"] = baseline.priority_one(observed, "figure")
    r["text flag"] = baseline.priority_one(observed, "text")
    return r


@lru_cache(maxsize=None)
def diagnosis_spread(setting: str = "pre_hospital") -> pd.DataFrame:
    """The graph's flag less the MPTT-24's (figure reading), and the list measures, across 20 further samples."""
    t = decision.threshold()
    rows = []
    for seed in range(EVAL_SEED + 1, EVAL_SEED + 1 + SEEDS):
        r = diagnosis_results(setting, seed)
        g, f = r["flag metrics"], r["figure"]
        rows.append({"seed": seed,
                     "sensitivity, graph less rule": g["sensitivity"] - f["sensitivity"],
                     "specificity, graph less rule": g["specificity"] - f["specificity"],
                     "Brier, graph less rule": g["brier"] - f["brier"],
                     "net benefit per 100, graph less rule":
                         100 * (decision.net_benefit(r["flag"], r["need"], t)
                                - decision.net_benefit(r["figure flag"], r["need"], t)),
                     **{m: r[m] for m in LIST_MEASURES}})
    return pd.DataFrame(rows).set_index("seed")


def by_condition(setting: str = "pre_hospital") -> pd.DataFrame:
    r = diagnosis_results(setting)
    return pd.DataFrame(r["by condition"]).T[["casualties", *LIST_MEASURES]]


# ------------------------------------------------------------------------------------------------ treatment

@dataclass(frozen=True)
class Link:
    intervention: str
    edge: Edge                    # injury to intervention: the version a careful query returns
    notes: tuple                  # versions or populations set aside
    competency: str | None
    role: str | None
    echelon: str | None           # the nearest echelon on the route that holds the competency, or None
    path: tuple                   # requires, held_by and available_at edges
    timeline: str                 # the timeline on the edge into that echelon, or the point of injury's own
    minutes: int | None


@dataclass(frozen=True)
class Chain:
    injury: str
    start: str
    route: tuple
    links: tuple

    def nearest(self) -> Link | None:
        held = [link for link in self.links if link.echelon is not None]
        return min(held, key=lambda link: self.route.index(link.echelon)) if held else None


def route_from(start: str = POINT, graph: Graph | None = None) -> tuple[str, ...]:
    g = care_graph() if graph is None else graph
    route, here = [start], _k("echelon", start)
    while True:
        nxt = g.edges(src=here, type="leads_to")
        if not nxt:
            return tuple(route)
        here = nxt[0].dst
        route.append(name_of(here))


def timeline_into(echelon: str, start: str = POINT, graph: Graph | None = None) -> tuple[str, int | None]:
    g = care_graph() if graph is None else graph
    if echelon == start:
        if start == POINT:
            return FIRST_RESPONSE, 10
        return "here", None
    e = g.edges(dst=_k("echelon", echelon), type="leads_to")[0]
    return e.props["timeline"], e.props["minutes"]


def chain(injury: str, start: str = POINT, when: str = TODAY, population: str = "military",
          graph: Graph | None = None) -> Chain:
    """Injury to intervention to competency to role to echelon, by traversal, choosing for each intervention the
    nearest echelon on the route from `start` at which a role holding its competency is available."""
    g = care_graph() if graph is None else graph
    route = route_from(start, g)
    links = []
    seen = []
    for e in g.edges(src=_k("injury", injury), type="treated_by"):
        if e.dst in seen:
            continue
        seen.append(e.dst)
        chosen, notes = select_edge(e.src, e.dst, when, population, g)
        best = None
        for req in g.edges(src=e.dst, type="requires"):
            for held in g.edges(src=req.dst, type="held_by"):
                for at in g.edges(src=held.dst, type="available_at"):
                    where = name_of(at.dst)
                    if where in route and (best is None or route.index(where) < route.index(best[3])):
                        best = (req, held, at, where)
        if best is None:
            links.append(Link(name_of(e.dst), chosen, notes, None, None, None, (), "not held on the route from here",
                              None))
            continue
        req, held, at, where = best
        words, minutes = timeline_into(where, start, g)
        links.append(Link(name_of(e.dst), chosen, notes, name_of(req.dst), name_of(held.dst), where, (req, held, at),
                          words, minutes))
    return Chain(injury, start, route, tuple(links))


def placed_at(intervention: str, echelon: str, graph: Graph | None = None) -> tuple | None:
    """The requires, held_by and available_at edges that put an intervention at an echelon, or None. Of every such
    path the graph holds, the first that carries an edge labelled doctrine is returned, otherwise the first."""
    g = care_graph() if graph is None else graph
    paths = [(req, held, at)
             for req in g.edges(src=_k("intervention", intervention), type="requires")
             for held in g.edges(src=req.dst, type="held_by")
             for at in g.edges(src=held.dst, dst=_k("echelon", echelon), type="available_at")]
    for path in paths:
        if any(e.label == "doctrine" for e in path):
            return path
    return paths[0] if paths else None


def options_at(echelon: str, graph: Graph | None = None) -> pd.DataFrame:
    """What can be done at an echelon: every intervention whose competency is held by a role available there, with
    the edges that place it. Offered as a bound on the options a decision may consider."""
    g = care_graph() if graph is None else graph
    rows = []
    for v in g.nodes("intervention"):
        placed = placed_at(name_of(v), echelon, g)
        if placed:
            req, held, at = placed
            rows.append({"intervention": name_of(v), "competency": name_of(req.dst), "role": name_of(held.dst),
                         "labels": ", ".join(sorted({req.label, held.label, at.label}))})
    return pd.DataFrame(rows, columns=["intervention", "competency", "role", "labels"])


# The generator's clock for each echelon: time to pre-hospital care stands in for reaching Role 1, an assumption.
CLOCK = {ROLE1: "t_phec_min", ROLE2: "t_role2_min"}


@lru_cache(maxsize=None)
def treatment_table(setting: str = "pre_hospital") -> pd.DataFrame:
    """For each condition and each intervention its chain reaches from the point of injury: the nearest echelon, the
    timeline on the edge into it, and the share of the generator's casualties with the condition whose assumed time
    to that echelon falls within the timeline, read as time from injury (mechanism). The generator draws the times for
    every casualty, including those it has dead from bleeding before then."""
    observed, truth = _sample(EVAL_SEED, setting)
    cond = true_condition(truth)
    rows = []
    for injury in INJURIES:
        m = cond == injury
        for link in chain(injury).links:
            col = CLOCK.get(link.echelon)
            within = (float((observed[col].to_numpy()[m] <= link.minutes).mean())
                      if col is not None and link.minutes is not None and m.any() else float("nan"))
            rows.append({"condition": injury, "casualties": int(m.sum()), "intervention": link.intervention,
                         "edge label": shown_label(link.edge), "echelon": link.echelon or "not on the route",
                         "timeline": link.timeline, "share within the timeline": within})
    return pd.DataFrame(rows)


@lru_cache(maxsize=None)
def txa_windows(setting: str = "pre_hospital") -> dict:
    """The share of battle casualties bleeding significantly whose time to pre-hospital care, which the generator takes
    as the time tranexamic acid is given, falls within each version's window (mechanism)."""
    observed, truth = _sample(EVAL_SEED, setting)
    m = (observed["stream"].to_numpy() == "battle") & truth["bleeding"].to_numpy(bool)
    t = observed["t_phec_min"].to_numpy()[m]
    return {"casualties": int(m.sum()),
            **{k: float((t <= v["window_min"]).mean()) for k, v in TXA_DOSES.items()}}


# ------------------------------------------------------------------------------------------------ by hand and the map

HAND_NODES = (("finding", "free fluid on the scan"), ("injury", "truncal haemorrhage"), ("intervention", TXA),
              ("intervention", SURGERY), ("competency", "advanced resuscitation"), ("competency", "operating"),
              ("role", PHEC), ("role", SURGEONS), ("echelon", POINT), ("echelon", ROLE1), ("echelon", ROLE2),
              ("echelon", ROLE3))


def subgraph(nodes: tuple, graph: Graph | None = None) -> CareGraph:
    """The nodes named, with their properties, and every edge of the graph that runs between two of them."""
    g = care_graph() if graph is None else graph
    keys = {_k(t, n) for t, n in nodes}
    sub = CareGraph()
    for t, n in nodes:
        sub.add_node(t, n, **{k: v for k, v in g.node(_k(t, n)).items() if k != "type"})
    for e in g.edges():
        if e.src in keys and e.dst in keys:
            sub.add_edge(e.src, e.dst, e.type, label=e.label, source=e.source, version=e.version,
                         valid_from=e.valid_from, population=e.population, **e.props)
    return sub


def hand_graph() -> CareGraph:
    """Twelve nodes for the count by hand: free fluid on the scan traced to the place that can treat it."""
    return subgraph(HAND_NODES)


def hand_edges() -> list[tuple[str, str, str]]:
    """The twelve-node graph as a plain list of (from, edge type, to), one entry per pair of nodes joined."""
    return list(dict.fromkeys((name_of(e.src), e.type, name_of(e.dst)) for e in hand_graph().edges()))


def trace(finding: str, graph: Graph | None = None, start: str = POINT) -> pd.DataFrame:
    """From a finding to every injury it suggests, and on along each injury's chain from `start`."""
    g = care_graph() if graph is None else graph
    rows = []
    for e in g.edges(src=_k("finding", finding), type="suggests"):
        for link in chain(name_of(e.dst), start, graph=g).links:
            rows.append({"injury": name_of(e.dst), "intervention": link.intervention, "competency": link.competency,
                         "role": link.role, "echelon": link.echelon})
    return pd.DataFrame(rows, columns=["injury", "intervention", "competency", "role", "echelon"])


def map_of_care(injury: str, start: str = POINT) -> dict:
    """What the central figure draws: the route from the point of injury with the timelines on its edges, what is
    held at each echelon, and the chain for one injury from where the casualty lies."""
    g = care_graph()
    route = route_from(POINT)
    links = chain(injury, start).links
    return {"route": route,
            "legs": [(name_of(e.src), name_of(e.dst), e.props["timeline"], e.label) for e in g.edges(type="leads_to")],
            "held": {e: list(options_at(e)["intervention"]) for e in route},
            "lit": [(link.intervention, link.echelon, shown_label(link.edge)) for link in links],
            "behind": route[:route.index(start)],
            "first response": FIRST_RESPONSE}


EDGE_STYLES = {"doctrine": "-", "US doctrine": "-", "trial evidence": "-.", "registry evidence": "--",
               "assumption": ":"}


def shown_label(e: Edge) -> str:
    """An edge's label as it is shown: an edge from E-86 is US doctrine, and is shown as US doctrine wherever it
    appears."""
    return "US doctrine" if e.label == "doctrine" and "E-86" in str(e.source) else e.label


# ------------------------------------------------------------------------------------------------ the rule as a traversal

def _answer(test: dict, observed: pd.DataFrame, reading: str) -> np.ndarray:
    col = test["column"]
    if col not in observed:
        if test.get("absent") == "yes":                  # the generator records no breathing check: an assumption
            return np.ones(len(observed), bool)
        raise KeyError(col)
    x = observed[col]
    if test["kind"] == "flag":
        return x.astype("boolean").fillna(False).to_numpy(bool)
    if test["kind"] == "not in":
        return ~x.isin(test["exits"][reading]).to_numpy()
    if test["kind"] == "range":
        return ((x >= test["from"]) & (x <= test["to"])).to_numpy()
    if test["kind"] == "below":
        return (x < test["value"]).to_numpy()
    raise ValueError(test["kind"])


def rule_by_traversal(observed: pd.DataFrame, reading: str = baseline.DEFAULT_READING,
                      graph: Graph | None = None) -> np.ndarray:
    """The MPTT-24 run from its edges: the thresholds in step order, each testing its observation and assigning a
    priority on the answer its edge names. The first step that assigns ends the triage."""
    g = care_graph() if graph is None else graph
    out = np.full(len(observed), "", dtype=object)
    open_ = np.ones(len(observed), bool)
    for th in sorted(g.nodes("threshold"), key=lambda k: g.node(k)["step"]):
        test = g.edges(src=th, type="tests")[0].props
        yes = _answer(test, observed, reading)
        for a in g.edges(src=th, type="assigns"):
            hit = open_ & (yes if a.props["when"] == "yes" else ~yes)
            out[hit] = name_of(a.dst)
            open_ &= ~hit
    return out


@lru_cache(maxsize=None)
def rule_agreement() -> pd.DataFrame:
    """The traversal against the coded rule (baseline.py) on the 100,000 synthetic casualties, under each reading."""
    observed, _ = baseline.generator_sample("pre_hospital")
    rows = []
    for reading in baseline.READINGS:
        coded = baseline.triage_table(observed, reading)["priority"].to_numpy()
        walked = rule_by_traversal(observed, reading)
        rows.append({"reading": reading, "casualties": len(coded), "agree": int((coded == walked).sum())})
    return pd.DataFrame(rows).set_index("reading")


# ------------------------------------------------------------------------------------------------ provenance

@lru_cache(maxsize=1)
def provenance_graph() -> Graph:
    """Every generator parameter to its source (R-0.10), with each notebook as a node holding its evidence list."""
    doc = yaml.safe_load(provenance.PARAMS_PATH.read_text(encoding="utf-8"))
    g = provenance.build_provenance(doc)
    for path in sorted((ROOT / "notebooks").glob("*.ipynb")):
        meta = json.loads(path.read_text(encoding="utf-8")).get("metadata", {})
        g.add_node("notebook", path.stem, evidence=tuple(meta.get("evidence", [])))
    return g


def parameter_sources() -> pd.DataFrame:
    g = provenance_graph()
    rows = []
    for k in g.nodes("parameter"):
        e = g.edges(src=k, type="taken_from")
        rows.append({"parameter": name_of(k), "source": ", ".join(name_of(x.dst) for x in e),
                     "label": e[0].label if e else "", "population": e[0].population if e else ""})
    return pd.DataFrame(rows).set_index("parameter")


def depends_on(eid: str) -> dict:
    """What the graph holds that depends on one evidence id: the parameters taken from it, and the notebooks whose
    evidence lists name it."""
    g = provenance_graph()
    return {"parameters": tuple(name_of(e.src) for e in g.edges(dst=_k("source", eid), type="taken_from")),
            "notebooks": tuple(name_of(k) for k in g.nodes("notebook") if eid in g.node(k)["evidence"])}


# ------------------------------------------------------------------------------------------------ the lens

def _pct(x: float, places: int = 1) -> str:
    return f"{100 * x:.{places}f}%"


def spread_words(differences, places: int = 2, unit: str = "") -> str:
    return stochastic.spread_words(differences, places, unit)


class KnowledgeLens:
    """Lens 08 behind the Lens interface (R-0.8, R-8.1)."""

    name = NAME

    def diagnose(self, casualty: Mapping[str, Any]) -> Diagnosis:
        return diagnose_record(casualty)

    def treat(self, casualty: Mapping[str, Any]) -> Chain | None:
        """The chain for the casualty's `injury` if given, otherwise for the first candidate of the diagnosis."""
        injury = casualty.get("injury")
        if injury is None:
            first = diagnose_record(casualty).first()
            if first is None:
                return None
            injury = first.injury
        return chain(str(injury), str(casualty.get("echelon", POINT)))

    def scorecard(self) -> list[ScorecardRow]:
        rows = []
        for setting in SETTINGS:
            r = diagnosis_results(setting)
            for key, name in (("sensitivity", "sensitivity"), ("specificity", "specificity"), ("brier", "Brier score, where lower is better"),
                              ("calibration", "share flagged minus share in need")):
                rows.append(ScorecardRow(NAME, "diagnosis",
                                         f"{name}, any candidate against need for a life-saving intervention, "
                                         f"{SETTING_NAMES[setting]}", round(r["flag metrics"][key], 4),
                                         round(r["figure"][key], 4), "mechanism", "native", "generator"))
            for m in LIST_MEASURES:
                rows.append(ScorecardRow(NAME, "diagnosis", f"true condition {m}, among casualties with a condition "
                                         f"needing a life-saving intervention, {SETTING_NAMES[setting]}",
                                         round(r[m], 4), NO_BASELINE, "mechanism", "native", "generator"))
        table = treatment_table()
        for _, row in table.dropna(subset=["share within the timeline"]).iterrows():
            rows.append(ScorecardRow(NAME, "treatment", f"share of casualties with {row['condition']} whose assumed "
                                     f"time to {row['echelon']} is within the timeline on the edge into "
                                     f"{row['echelon']} ({row['timeline']}), the timeline read as time from injury, an "
                                     f"assumption; {row['echelon']} is the first echelon on the route holding "
                                     f"{row['intervention']}, and the timeline is not a target for it",
                                     round(row["share within the timeline"], 4), NO_BASELINE, "mechanism", "native",
                                     "generator"))
        return rows


LENS = KnowledgeLens()


HOSPITAL = ("The generator's physiology is an assumption, tuned until the rule landed within 0.05 of E-09's accuracy, "
            "which was measured on first recorded hospital respiratory rate and registry GCS, not at the point of injury")


def seven_axes() -> pd.DataFrame:
    """The scorecard on the seven axes of D-21, with the baseline under both readings (D-24) and axis 7 at 0.10
    (D-26)."""
    pre, inside = diagnosis_results("pre_hospital"), diagnosis_results("in_hospital")
    sp, si = diagnosis_spread("pre_hospital"), diagnosis_spread("in_hospital")
    tt = treatment_table()
    counts = node_counts()
    labels = edge_table()["label"].value_counts()
    n_edges = int(labels.sum())

    def flag_disc(r):
        m = r["flag metrics"]     # to four places, as the scorecard rows give them (lesson 14)
        return f"sensitivity {_pct(m['sensitivity'], 2)}, specificity {_pct(m['specificity'], 2)}"

    def lists(r):
        return (f"of the {r['with a condition']:,} casualties with a condition needing a life-saving intervention, the "
                f"true condition is first and alone for {_pct(r['first, alone'])}, first alone or tied for "
                f"{_pct(r['first, alone or tied'])}, and in the list for {_pct(r['anywhere in the list'])}")

    def rule_disc(m):
        return f"sensitivity {_pct(m['sensitivity'])}, specificity {_pct(m['specificity'])} against need"

    def cal(m, what):
        gap = m["calibration"]
        return (f"Brier {m['brier']:.3f}, where lower is better; it flags {100 * abs(gap):.1f} points "
                f"{'more' if gap > 0 else 'fewer'} than are in need. {what} gives no probability, so the Brier score "
                f"is the share misclassified")

    def timely(row):
        return f"{row['intervention']} at {row['echelon']}, {_pct(row['share within the timeline'])} within its timeline"

    reach = "; ".join(f"{c}: " + ", ".join(timely(r) for _, r in tt[(tt.condition == c)].dropna(
        subset=["share within the timeline"]).iterrows()) for c in INJURIES if not tt[(tt.condition == c)].dropna(
        subset=["share within the timeline"]).empty)
    assumed = int(labels.get("assumption", 0))
    rows = [
        ("1 Discrimination (mechanism)",
         f"Flag when the list holds any candidate, before hospital: {flag_disc(pre)} against need for a life-saving "
         f"intervention, on the military cohort's 100,000 synthetic casualties; {lists(pre)}. Sensitivity less the "
         f"rule's (figure) is {spread_words(100 * sp['sensitivity, graph less rule'], 1, ' points')}; specificity less "
         f"the rule's is {spread_words(100 * sp['specificity, graph less rule'], 1, ' points')}",
         f"{rule_disc(pre['figure'])}. {rules.d23_sentence()} {HOSPITAL}", rule_disc(pre["text"]),
         f"Not a classifier: the chain from the point of injury for each condition, and the share of the generator's "
         f"casualties with it whose assumed time to the nearest echelon holding the intervention is within the timeline "
         f"on the edge into that echelon (E-42), {FROM_INJURY}. The timeline belongs to the edge, as E-42 states it, and "
         f"is not a target for each intervention. {reach}. Times to pre-hospital care and to Role 2 are the generator's "
         f"assumptions, drawn for every casualty, including those it has dead from bleeding before then; time to "
         f"pre-hospital care stands in for reaching Role 1, and the generator holds no time for care at the point of "
         f"injury or for reaching Role 3"),
        ("2 Calibration (mechanism)", cal(pre["flag metrics"], "A list") + f". Brier less the rule's, where lower is "
         f"better, is "
         f"{spread_words(sp['Brier, graph less rule'], 3)}",
         cal(pre["figure"], "A rule"), cal(pre["text"], "A rule"),
         "Does not apply: a chain gives no probability"),
        ("3 Uncertainty expressed",
         "None as a probability. A ranked list, with ties shown as ties; every edge carries a label saying what kind "
         "of claim it is, not how sure", "None: a priority", "None: a priority",
         "None as a probability. Each edge carries its label, version, date and population, and the query says when "
         "a version or population was set aside"),
        ("4 What it needed",
         f"A hand-built graph and no labelled cases: {len(SUGGESTS)} suggests edges, every one an assumption written "
         f"from what the generator's code does",
         "Rules only (E-08)", "Rules only (E-08)",
         f"Edges from AJP-4.10 (E-42 to E-44, currency not confirmed), US doctrine (E-86), CRASH-2, a civilian trial "
         f"(E-19, E-20), "
         f"E-104 and assumptions: {assumed} of the graph's {n_edges} edges are assumptions. Nodes: "
         f"{sum(counts[t] for t in CHAIN_TYPES)} in the capability chain and {sum(counts[t] for t in RULE_TYPES)} in "
         f"the rule"),
        ("5 Readability", "Each candidate carries the edges that produced it: one step from finding to injury",
         "Six yes-or-no steps", "Six yes-or-no steps",
         "Four steps, injury to intervention to competency to role to echelon, then the route with its timelines"),
        ("6 Robustness, setting changed (mechanism)",
         f"Scan in hospital: {flag_disc(inside)}; {lists(inside)}. Sensitivity less the rule's is "
         f"{spread_words(100 * si['sensitivity, graph less rule'], 1, ' points')}",
         f"Scan in hospital: {rule_disc(inside['figure'])}, unchanged because the setting changes only the scan",
         f"Scan in hospital: {rule_disc(inside['text'])}, unchanged",
         "Unchanged: the chain does not read the scan, and the generator's times to pre-hospital care and to Role 2 "
         "do not change with the setting"),
        ("7 Decision value",
         stochastic.axis7(pre["flag"], pre["need"]) + ", against need for a life-saving intervention. Net benefit "
         f"less the rule's (figure) is {spread_words(sp['net benefit per 100, graph less rule'], 1, ' per 100')}",
         stochastic.axis7(pre["figure flag"], pre["need"]) + ", against need",
         stochastic.axis7(pre["text flag"], pre["need"]) + ", against need",
         "Does not apply: a chain is not a flag. It bounds the options a decision may consider, by what the graph "
         "holds at each echelon"),
    ]
    return pd.DataFrame(rows, columns=["axis", "diagnosis: ranked candidates from findings",
                                       "baseline: MPTT-24, figure (as published)",
                                       "baseline: MPTT-24, text (as validated)",
                                       "treatment: the chain of care"]).set_index("axis")


# ------------------------------------------------------------------------------------------------ app page 1

def _edge_words(e: Edge) -> str:
    if e.label == "assumption":
        return "assumption"
    if e.source == "E-86":
        return "US doctrine, E-86, not UK practice"
    if e.source == "E-104":
        return f"{e.label}, E-104, measured on CT of 100 male military cases"
    return f"{e.label}, {e.source}"


def panel(record: Mapping[str, Any], setting: str = "pre_hospital") -> dict:
    """The knowledge graph panel for one synthetic casualty on app page 1. Every number is formatted here, so the
    page shows only what the library computed (gate G-8)."""
    d = diagnose_record(record)
    if d.candidates:
        listed = "; ".join(
            f"{c.rank}. {c.injury}, score {c.score:.2f}{' (tied)' if c.tied > 1 else ''}, from {c.because()}"
            for c in d.candidates)
        cand = (f"Candidates, ranked by the graph's own weights, each finding adding one over the number of injuries "
                f"it suggests: {listed}. Every suggests edge is an assumption, written from what the generator's code "
                f"does.")
    elif not d.findings:
        cand = "No finding is present in the record, so the list is empty."
    else:
        cand = (f"None of the findings present is joined to an injury along an edge the graph follows for a casualty "
                f"{d.context}, so the list is empty.")
    found = ", ".join(d.findings) if d.findings else "none"
    out = {
        "heading": "Knowledge graph panel: what the map joins to this casualty's findings",
        "findings": (f"Findings coded from the record ({SETTING_NAMES[setting]}), {len(d.findings)} of "
                     f"{len(FINDING_NAMES)}: {found}. The casualty is {d.context}."),
        "candidates": cand,
        "chain": "",
        "note": ("The graph retrieves what was put there. It does not reason, and every result here is a mechanism on "
                 "synthetic casualties."),
    }
    first = d.first()
    if first is None:
        out["chain"] = "No candidate, so no chain of care is traced."
        return out
    parts = []
    for link in chain(first.injury).links:
        if link.echelon is None:
            parts.append(f"{link.intervention}: {link.timeline}")
            continue
        notes = f"; {'; '.join(link.notes)}" if link.notes else ""
        dose = f", {link.edge.props['dose']} {link.edge.props['condition']}" if "dose" in link.edge.props else ""
        device = (f", {link.edge.props['device']} of {link.edge.props['length_cm']:g} cm"
                  if "device" in link.edge.props else "")
        parts.append(f"{link.intervention}{dose}{device} [{_edge_words(link.edge)}{notes}], needing {link.competency} "
                     f"(role: {link.role}), nearest at {link.echelon}, {link.timeline}")
    tie = f", tied with {first.tied - 1} other{'s' if first.tied > 2 else ''}" if first.tied > 1 else ""
    out["chain"] = (f"For the first candidate, {first.injury}{tie}, the chain from the point of injury: "
                    + "; ".join(parts) + ". Echelons and timelines are from AJP-4.10 (E-42, E-43), Edition C Version "
                    f"1, September 2019 (E-44), currency not confirmed, {FROM_INJURY}. Edges to competencies and roles "
                    "are assumptions.")
    return out


def page_panel(walk: Any) -> dict:
    """The knowledge graph panel on app page 1 for one walk-through casualty, given lens 03's Walkthrough (D-27)."""
    return panel(walk.record, walk.setting)
