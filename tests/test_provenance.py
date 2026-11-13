import yaml

from inference_labs.graph import provenance


def _params(root):
    return yaml.safe_load((root / "params.yaml").read_text())


def test_every_parameter_is_a_node_joined_to_its_sources(root):
    params = _params(root)
    graph = provenance.build_provenance(params)
    for pid, p in params["parameters"].items():
        key = provenance.param_key(pid)
        targets = {e.dst for e in graph.edges(src=key, type="taken_from")}
        assert targets == {f"source:{s}" for s in provenance.sources_of(p)}


def test_edges_carry_version_date_and_population(root):
    params = _params(root)
    graph = provenance.build_provenance(params)
    assert (params["version"], str(params["valid_from"])) == (2, "2026-11-13")
    for e in graph.edges(type="taken_from"):
        assert e.version == "2" and e.valid_from == "2026-11-13" and e.population


def test_register_has_one_row_per_parameter_and_marks_assumptions(root):
    params = _params(root)
    text = provenance.register_markdown(provenance.build_provenance(params))
    rows = [line for line in text.splitlines() if line.startswith("| generator |")]
    assert len(rows) == len(params["parameters"])
    for line, (pid, p) in zip(rows, params["parameters"].items()):
        cells = [c.strip() for c in line.strip("|").split("|")]
        assert len(cells) == 7
        assert cells[5] == ("true" if p["label"] == "assumption" else "false")
        assert ("provisional" in cells[4]) == bool(p.get("provisional"))


def test_committed_register_is_current(root):
    text = provenance.register_markdown(provenance.build_provenance(_params(root)))
    assert (root / "docs" / "ASSUMPTIONS.md").read_text() == text
