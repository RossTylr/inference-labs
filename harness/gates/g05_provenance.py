"""G-5 Provenance: every parameter has a source and a label; every E-id resolves to a row in EVIDENCE.md;
the generated assumptions register matches the committed one.

Also checks R-0.2 (a parameter drawn from a CARRIED source is marked provisional) and R-0.10 (every
parameter is a node in the provenance graph)."""
from __future__ import annotations

from pathlib import Path

from harness.common import GateResult, evidence_rows, load_yaml

REQUIRED = ("value", "tolerance", "source", "label", "population")


def check(root: Path, slice_id: int, **_: object) -> GateResult:
    from inference_labs.graph import provenance
    from inference_labs.graph.schema import EDGE_LABELS

    params = load_yaml(root / "params.yaml")
    evidence = evidence_rows(root / "docs" / "EVIDENCE.md")
    problems: list[str] = []

    for pid, p in (params.get("parameters") or {}).items():
        missing = [k for k in REQUIRED if p.get(k) in (None, "", [])]
        if missing:
            problems.append(f"{pid}: missing {', '.join(missing)}")
            continue
        if p["label"] not in EDGE_LABELS:
            problems.append(f"{pid}: label '{p['label']}' is not one of {sorted(EDGE_LABELS)}")
        sources = provenance.sources_of(p)
        if sources == ["assumption"]:
            if p["label"] != "assumption":
                problems.append(f"{pid}: source is assumption but label is '{p['label']}'")
            continue
        if p["label"] == "assumption":
            problems.append(f"{pid}: label is assumption but sources are {sources}")
        unresolved = [s for s in sources if s not in evidence]
        if unresolved:
            problems.append(f"{pid}: {', '.join(unresolved)} not in EVIDENCE.md")
        carried = [s for s in sources if s in evidence and "CARRIED" in evidence[s].upper()]
        if carried and p.get("provisional") is not True:
            problems.append(f"{pid}: {', '.join(carried)} is CARRIED but the parameter is not marked provisional")

    try:
        graph = provenance.build_provenance(params)
    except (KeyError, TypeError, ValueError) as exc:
        problems.append(f"the provenance graph could not be built: {exc}")
        graph = None
    if graph is not None:
        for pid in params.get("parameters") or {}:
            key = provenance.param_key(pid)
            if not graph.has_node(key) or not graph.edges(src=key, type="taken_from"):
                problems.append(f"{pid}: not a node with a source in the provenance graph")

        committed = root / "docs" / "ASSUMPTIONS.md"
        expected = provenance.register_markdown(graph)
        if not committed.exists():
            problems.append("docs/ASSUMPTIONS.md is missing")
        elif committed.read_text(encoding="utf-8") != expected:
            problems.append("docs/ASSUMPTIONS.md is stale: regenerate with python -m inference_labs.graph.provenance")

    if problems:
        return GateResult(False, "; ".join(problems[:8]) + (f" (and {len(problems) - 8} more)" if len(problems) > 8 else ""))
    n = len(params.get("parameters") or {})
    return GateResult(True, f"{n} parameters sourced and labelled; every E-id resolves; register current")
