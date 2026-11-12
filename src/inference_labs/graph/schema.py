"""Node and edge types for the knowledge graph (design section 6; R-0.9).

One graph, three jobs: the capability chain, provenance, and rules as a graph. Every edge carries an
epistemic label, its source, a version, the date from which it holds and the population it holds for (B-7).
"""

NODE_TYPES = frozenset({
    # capability chain
    "finding", "injury", "intervention", "competency", "role", "echelon",
    # provenance
    "parameter", "source", "notebook",
    # rules as graph
    "threshold", "observation", "priority",
})

# edge type -> (allowed source node type, allowed target node type)
EDGE_TYPES = {
    "suggests": ("finding", "injury"),
    "treated_by": ("injury", "intervention"),
    "requires": ("intervention", "competency"),
    "held_by": ("competency", "role"),
    "available_at": ("role", "echelon"),
    "taken_from": ("parameter", "source"),
    "used_in": ("parameter", "notebook"),
    "tests": ("threshold", "observation"),
    "assigns": ("threshold", "priority"),
}

EDGE_LABELS = frozenset({"doctrine", "trial evidence", "registry evidence", "assumption"})

# every edge must carry these, non-empty
EDGE_FIELDS = ("label", "source", "version", "valid_from", "population")
