"""Lens 08, knowledge graph (R-8.1 to R-8.12)."""
from collections import deque
from pathlib import Path

import numpy as np
import pytest

from inference_labs import baseline
from inference_labs.graph.schema import EDGE_FIELDS
from inference_labs.interface import Lens, row_problems
from inference_labs.lenses import bayesian, rules
from inference_labs.lenses import knowledge as k

ROOT = Path(__file__).resolve().parents[1]
TRUNCAL, TXA = "injury:truncal haemorrhage", "intervention:tranexamic acid"


def test_the_lens_implements_the_interface():
    assert isinstance(k.LENS, Lens)
    record = {"stream": "battle", "catastrophic_haemorrhage": False, "scan_free_fluid": True,
              "scan_pneumothorax": False, "heart_rate": 120, "respiratory_rate": 18, "sbp": 85, "avpu": "A",
              "walking": False}
    d = k.LENS.diagnose(record)
    assert d.first().injury == "truncal haemorrhage" and d.first().tied == 1
    assert {name for name in d.findings} == {"free fluid on the scan", "heart rate 100 or more",
                                             "systolic pressure under 100", "not walking"}
    chain = k.LENS.treat(record)
    assert chain.injury == "truncal haemorrhage" and chain.nearest().echelon == "Role 1"
    assert k.LENS.treat({"stream": "battle", "catastrophic_haemorrhage": False, "heart_rate": 70,
                         "respiratory_rate": 16, "sbp": 120, "avpu": "A", "walking": True}) is None


def test_about_fifty_nodes_and_every_edge_carries_its_fields():
    """R-8.1: the store refuses an edge without its five fields, so every edge in the graph has them."""
    counts = k.node_counts()
    assert 40 <= sum(counts[t] for t in k.CHAIN_TYPES) <= 60
    edges = k.edge_table()
    assert not edges[list(EDGE_FIELDS)].isin(["", None]).any().any()
    with pytest.raises(KeyError):
        k.CareGraph().add_edge("echelon:a", "echelon:b", "leads_to", label="doctrine")
    g = k.CareGraph()
    g.add_node("echelon", "a")
    g.add_node("echelon", "b")
    with pytest.raises(ValueError):
        g.add_edge("echelon:a", "echelon:b", "leads_to", label="doctrine", source="x", version="v", valid_from="2019")


def test_ajp_edges_carry_the_edition_and_us_doctrine_is_labelled():
    """R-8.6 and R-8.11."""
    edges = k.edge_table()
    ajp = edges[edges["source"].str.contains("E-42|E-43")]
    assert len(ajp) and ajp["version"].str.contains("currency not confirmed").all()
    us = edges[edges["source"] == "E-86"]
    assert len(us) and us["population"].str.contains("US doctrine, not UK practice").all()
    assert not edges["population"].str.contains("UK practice").sum() > len(us)


def test_the_ranking_is_the_graphs_own_and_the_two_traversals_agree():
    """R-8.5: per casualty by edges, in bulk by matrix; the scores agree exactly."""
    observed, _ = baseline.generator_sample("pre_hospital")
    sample = observed.iloc[:1500]
    scale, _, _ = k._weights()
    scores = k.score_matrix(sample)
    for i in range(len(sample)):
        d = k.diagnose_record(sample.iloc[i].to_dict())
        got = {c.injury: c.score for c in d.candidates}
        want = {k.INJURIES[j]: scores[i, j] / scale for j in range(len(k.INJURIES)) if scores[i, j] > 0}
        assert got.keys() == want.keys() and all(abs(got[x] - want[x]) < 1e-12 for x in got)
    assert k.out_degree("free fluid on the scan") == 1 and k.out_degree("heart rate 100 or more") == 5


def test_ties_are_shown_as_ties():
    d = k.diagnose_record({"stream": "battle", "catastrophic_haemorrhage": True, "heart_rate": 80,
                           "respiratory_rate": 16, "sbp": 120, "avpu": "A", "walking": True})
    assert [c.rank for c in d.candidates] == [1, 1] and all(c.tied == 2 for c in d.candidates)


def test_the_list_is_scored_against_the_true_condition():
    r = k.diagnosis_results("pre_hospital")
    assert r["first, alone"] <= r["first, alone or tied"] <= r["anywhere in the list"] <= 1
    by = k.by_condition()
    assert by.loc["junctional haemorrhage", "first, alone"] == 0     # nothing in the record separates it
    assert k.diagnosis_results("in_hospital")["by condition"]["truncal haemorrhage"]["first, alone"] > \
        r["by condition"]["truncal haemorrhage"]["first, alone"]
    assert len(k.diagnosis_spread()) == k.SEEDS


def test_the_by_hand_trace_agrees_three_ways():
    """R-8.3: on paper, in plain Python over an edge list, and by the library."""
    on_paper = {("tranexamic acid", "Role 1"), ("surgery", "Role 2")}
    edges = k.hand_edges()
    assert len({a for a, _, _ in edges} | {b for _, _, b in edges}) == 12
    nxt = {}
    for a, t, b in edges:
        nxt.setdefault((a, t), []).append(b)
    route, here = ["point of injury"], "point of injury"
    while (here, "leads_to") in nxt:
        here = nxt[(here, "leads_to")][0]
        route.append(here)
    plain = set()
    for injury in nxt[("free fluid on the scan", "suggests")]:
        for v in nxt[(injury, "treated_by")]:
            places = [e for c in nxt[(v, "requires")] for r in nxt[(c, "held_by")] for e in nxt[(r, "available_at")]]
            plain.add((v, min(places, key=route.index)))
    library = set(map(tuple, k.trace("free fluid on the scan", k.hand_graph())[["intervention", "echelon"]].values))
    assert on_paper == plain == library


def test_the_bound_query():
    """R-8.7: surgery is held at Role 2 and not before."""
    assert "surgery" not in set(k.options_at("Role 1")["intervention"])
    assert "surgery" in set(k.options_at("Role 2")["intervention"])
    assert k.options_at("Role 4").empty


def test_the_rule_as_edges_agrees_with_the_coded_rule():
    """R-8.8: on every one of the 100,000 casualties, under each reading."""
    agree = k.rule_agreement()
    assert (agree["agree"] == agree["casualties"]).all() and set(agree.index) == set(baseline.READINGS)


def test_provenance():
    """R-8.8: every parameter to its source; what depends on E-16."""
    sources = k.parameter_sources()
    assert (sources["source"] != "").all() and len(sources) > 30
    dep = k.depends_on("E-16")
    assert dep["parameters"] == ("scan_accuracy_pre_hospital",)
    assert {"01_rules", "02_frequentist", "03_bayesian", "07_causal"} <= set(dep["notebooks"])


def test_the_stale_edge_is_returned_and_then_caught():
    """R-8.9."""
    assert k.first_found(TRUNCAL, TXA).source == "E-19, E-20"
    now = k.as_of(TRUNCAL, TXA)
    assert now.edge.source == "E-86" and len(now.earlier) == 1
    before = k.as_of(TRUNCAL, TXA, "2020-01-01")
    assert before.edge.source == "E-19, E-20" and len(before.later) == 1
    edge, notes = k.select_edge(TRUNCAL, TXA)
    assert edge.props["dose"] == "2 g" and any("earlier" in n for n in notes)


def test_the_needle_edge_is_flagged_for_a_military_casualty():
    """R-8.10."""
    verdicts = {e.props["length_cm"]: v for e, v in k.population_query("injury:tension pneumothorax",
                                                                        "intervention:needle decompression")}
    assert verdicts == {rules.NEEDLE_CM: k.NOT_STATED, rules.CATHETER_CM: k.HOLDS}
    link = [x for x in k.chain("tension pneumothorax").links if x.intervention == k.NEEDLE][0]
    assert link.edge.props["length_cm"] == rules.CATHETER_CM


def test_the_treatment_chain_reaches_echelons_with_timelines():
    """R-8.6."""
    links = {x.intervention: x for x in k.chain("truncal haemorrhage").links}
    assert links["surgery"].echelon == "Role 2" and links["surgery"].minutes == 120
    assert links["tranexamic acid"].echelon == "Role 1" and links["tranexamic acid"].minutes == 60
    assert k.chain("severe head injury").links[-1].echelon == "Role 3"
    table = k.treatment_table()
    shares = table["share within the timeline"].dropna()
    assert len(shares) and ((shares >= 0) & (shares <= 1)).all()


def test_scorecard_rows_are_labelled():
    rows = k.LENS.scorecard()
    assert rows and all(not row_problems(r, ROOT) for r in rows)
    assert {r.case for r in rows} == {"diagnosis", "treatment"}


def test_seven_axes():
    axes = k.seven_axes()
    assert len(axes) == 7 and axes.shape[1] == 4
    assert "D-23" in axes.iloc[0, 1]


def test_the_panel_reads_from_the_library():
    shown = k.page_panel(bayesian.walkthrough("haemorrhage", "pre_hospital", None, 1))
    assert set(shown) == {"heading", "findings", "candidates", "chain", "note"}
    assert "does not reason" in shown["note"] and "currency not confirmed" in shown["chain"]
