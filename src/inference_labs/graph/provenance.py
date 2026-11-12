"""Provenance: every parameter in params.yaml is a node in the graph, joined to its sources (R-0.10).

docs/ASSUMPTIONS.md is generated from that graph, in the seven-column format of the ml-algorithms-labs
register, and gate G-5 checks that the committed copy is current.

    python -m inference_labs.graph.provenance            # write docs/ASSUMPTIONS.md
    python -m inference_labs.graph.provenance --check    # exit 1 if it is stale
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Any

import yaml

from inference_labs.graph.store import Graph, node_key

ROOT = Path(__file__).resolve().parents[3]
PARAMS_PATH = ROOT / "params.yaml"
REGISTER_PATH = ROOT / "docs" / "ASSUMPTIONS.md"

REGISTER_HEADER = """# Assumptions register: the casualty generator

Every number the generator uses or must reproduce, one row per parameter in `params.yaml`. A row marked
**Assumed: true** is a modelling choice, not a measured or published value; a notebook that quotes one is
quoting an assumption. Every other row traces to an evidence id in [`EVIDENCE.md`](EVIDENCE.md), and
"provisional" marks a source read only from a search extract (CARRIED). **Used in** lists the notebooks
that draw on the parameter.

This file is generated from the provenance graph by `python -m inference_labs.graph.provenance`. Do not edit
it by hand: change `params.yaml` and regenerate.

| Dataset | Parameter | Value | Unit | Source | Assumed | Used in |
|---|---|---|---|---|---|---|
"""


def sources_of(param: dict) -> list[str]:
    src = param.get("source")
    if src in (None, "", []):
        return []
    if isinstance(src, str):
        return [src]
    return [str(s) for s in src]


def param_key(pid: str) -> str:
    return node_key("parameter", pid)


def build_provenance(params_doc: dict) -> Graph:
    graph = Graph()
    version = str(params_doc.get("version", ""))
    valid_from = str(params_doc.get("valid_from", ""))
    for pid, p in (params_doc.get("parameters") or {}).items():
        key = graph.add_node(
            "parameter", pid,
            description=p.get("description", ""), value=p.get("value"), unit=p.get("unit", ""),
            label=p.get("label"), provisional=bool(p.get("provisional", False)),
        )
        for s in sources_of(p):
            skey = graph.add_node("source", s)
            graph.add_edge(key, skey, "taken_from", label=p.get("label"), source=s, version=version,
                           valid_from=valid_from, population=p.get("population"))
    return graph


def _fmt(value: Any) -> str:
    if isinstance(value, bool):
        return str(value).lower()
    if isinstance(value, int):
        return str(value)
    if isinstance(value, float):
        return f"{value:g}"
    if isinstance(value, list):
        if len(value) == 2 and all(isinstance(v, (int, float)) for v in value):
            return f"{_fmt(value[0])} to {_fmt(value[1])}"
        return ", ".join(_fmt(v) for v in value)
    if isinstance(value, dict):
        parts = []
        for k, v in value.items():
            parts.append(f"{k} ({_fmt(v)})" if isinstance(v, dict) else f"{k} {_fmt(v)}")
        return "; ".join(parts) if any(isinstance(v, dict) for v in value.values()) else ", ".join(parts)
    return str(value).replace("|", "/")


def register_markdown(graph: Graph) -> str:
    rows = []
    for key in graph.nodes("parameter"):
        node = graph.node(key)
        pid = key.split(":", 1)[1]
        sources = [e.dst.split(":", 1)[1] for e in graph.edges(src=key, type="taken_from")]
        source = ", ".join(sources) + (" (provisional)" if node.get("provisional") else "")
        used_in = ", ".join(e.dst.split(":", 1)[1] for e in graph.edges(src=key, type="used_in")) or "—"
        assumed = "true" if node.get("label") == "assumption" else "false"
        rows.append(f"| generator | `{pid}`: {node.get('description', '')} | {_fmt(node.get('value'))} | "
                    f"{node.get('unit', '')} | {source} | {assumed} | {used_in} |")
    return REGISTER_HEADER + "\n".join(rows) + "\n"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Generate docs/ASSUMPTIONS.md from the provenance graph.")
    parser.add_argument("--check", action="store_true", help="exit 1 if the committed register is stale")
    args = parser.parse_args(argv)
    with open(PARAMS_PATH, encoding="utf-8") as fh:
        text = register_markdown(build_provenance(yaml.safe_load(fh)))
    if args.check:
        current = REGISTER_PATH.read_text(encoding="utf-8") if REGISTER_PATH.exists() else ""
        if current != text:
            print("docs/ASSUMPTIONS.md is stale")
            return 1
        print("docs/ASSUMPTIONS.md is current")
        return 0
    REGISTER_PATH.write_text(text, encoding="utf-8")
    print(f"wrote {REGISTER_PATH.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
