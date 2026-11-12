import pytest

from inference_labs.graph import Graph

EDGE = dict(label="doctrine", source="E-43", version="1", valid_from="2019-09-01", population="NATO forces")


def _chain() -> Graph:
    g = Graph()
    f = g.add_node("finding", "free_fluid")
    i = g.add_node("injury", "truncal_haemorrhage")
    x = g.add_node("intervention", "damage_control_surgery")
    c = g.add_node("competency", "surgeon")
    r = g.add_node("role", "role_2_basic")
    e = g.add_node("echelon", "role_2")
    for src, dst, kind in ((f, i, "suggests"), (i, x, "treated_by"), (x, c, "requires"), (c, r, "held_by"),
                           (r, e, "available_at")):
        g.add_edge(src, dst, kind, **EDGE)
    return g


def test_keys_carry_the_node_type():
    g = Graph()
    assert g.add_node("parameter", "stream_shares") == "parameter:stream_shares"
    assert g.node("parameter:stream_shares")["type"] == "parameter"


def test_capability_chain_can_be_traversed():
    g = _chain()
    key, path = "finding:free_fluid", []
    while g.neighbours(key):
        key = g.neighbours(key)[0]
        path.append(key)
    assert path[-1] == "echelon:role_2" and len(path) == 5


def test_every_edge_carries_its_provenance_fields():
    g = _chain()
    for e in g.edges():
        assert e.label and e.source and e.version and e.valid_from and e.population


@pytest.mark.parametrize("field", ["label", "source", "version", "valid_from", "population"])
def test_an_edge_missing_a_field_is_refused(field):
    g = Graph()
    a, b = g.add_node("parameter", "p"), g.add_node("source", "E-01")
    attrs = {**EDGE, field: ""}
    with pytest.raises(ValueError):
        g.add_edge(a, b, "taken_from", **attrs)


def test_unknown_label_type_and_wrong_endpoints_are_refused():
    g = Graph()
    a, b = g.add_node("parameter", "p"), g.add_node("source", "E-01")
    with pytest.raises(ValueError):
        g.add_edge(a, b, "taken_from", **{**EDGE, "label": "opinion"})
    with pytest.raises(ValueError):
        g.add_edge(a, b, "treated_by", **EDGE)
    with pytest.raises(ValueError):
        g.add_edge(b, a, "taken_from", **EDGE)
    with pytest.raises(ValueError):
        g.add_node("hospital", "x")
    with pytest.raises(KeyError):
        g.add_edge(a, "source:missing", "taken_from", **EDGE)
