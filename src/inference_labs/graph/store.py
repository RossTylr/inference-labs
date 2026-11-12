"""An in-process graph store with typed nodes and edges (D-10, R-0.9).

Node keys are written `type:slug`, for example `parameter:stream_shares` or `source:E-34`, so the type of a
node can be read from its key. Edges are typed, checked against the schema, and must carry every field in
`EDGE_FIELDS`.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from inference_labs.graph.schema import EDGE_FIELDS, EDGE_LABELS, EDGE_TYPES, NODE_TYPES


def node_key(node_type: str, slug: str) -> str:
    return f"{node_type}:{slug}"


@dataclass(frozen=True)
class Edge:
    src: str
    dst: str
    type: str
    label: str
    source: str
    version: str
    valid_from: str
    population: str
    props: dict = field(default_factory=dict, compare=False)


class Graph:
    def __init__(self) -> None:
        self._nodes: dict[str, dict[str, Any]] = {}
        self._edges: list[Edge] = []

    # nodes
    def add_node(self, node_type: str, slug: str, **props: Any) -> str:
        if node_type not in NODE_TYPES:
            raise ValueError(f"unknown node type '{node_type}'")
        key = node_key(node_type, slug)
        if key in self._nodes:
            self._nodes[key].update(props)
        else:
            self._nodes[key] = {"type": node_type, **props}
        return key

    def has_node(self, key: str) -> bool:
        return key in self._nodes

    def node(self, key: str) -> dict[str, Any]:
        return self._nodes[key]

    def nodes(self, node_type: str | None = None) -> list[str]:
        return [k for k, v in self._nodes.items() if node_type is None or v["type"] == node_type]

    # edges
    def add_edge(self, src: str, dst: str, edge_type: str, **attrs: Any) -> Edge:
        if edge_type not in EDGE_TYPES:
            raise ValueError(f"unknown edge type '{edge_type}'")
        for key in (src, dst):
            if key not in self._nodes:
                raise KeyError(f"no node '{key}'")
        want_src, want_dst = EDGE_TYPES[edge_type]
        if self._nodes[src]["type"] != want_src or self._nodes[dst]["type"] != want_dst:
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

    def edges(self, src: str | None = None, dst: str | None = None, type: str | None = None) -> list[Edge]:
        return [
            e for e in self._edges
            if (src is None or e.src == src) and (dst is None or e.dst == dst) and (type is None or e.type == type)
        ]

    def neighbours(self, key: str, edge_type: str | None = None) -> list[str]:
        return [e.dst for e in self.edges(src=key, type=edge_type)]
