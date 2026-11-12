"""G-7 Notebook: the notebook runs top to bottom in under 5 minutes; holds the seven parts of the pattern in
order (cell tags hook, explainer, by-hand, case-dx, case-tx, failure, scorecard, analogy); the explainer holds
the three registers; every figure cell has a `concludes:` tag stating what the figure changes.

Conventions checked here
- A part tag is a cell tag. Cells without a part tag are allowed; reading down the notebook, the parts never
  go back to an earlier one, and every part is present.
- The three registers are the bold run-in headings **Plain.**, **Developer.** and **Technical.** in cells
  tagged explainer.
- A figure cell is a code cell whose outputs, once run, include an image. Its `concludes:` tag is held in the
  cell metadata as `concludes: <what the figure changes>`, at least four words.
- The notebook is run in memory and never written back, so running the gate changes no source file. The kernel
  is started without MPLBACKEND, which Streamlit sets on import and which would otherwise hide every figure.
"""
from __future__ import annotations

import os
import time
from pathlib import Path

from harness.common import GateResult, load_manifest, slice_config

PARTS = ("hook", "explainer", "by-hand", "case-dx", "case-tx", "failure", "scorecard", "analogy")
REGISTERS = ("**Plain.**", "**Developer.**", "**Technical.**")
TIME_LIMIT_S = 300
IMAGE_TYPES = ("image/png", "image/svg+xml", "image/jpeg")


def slice_notebooks(root: Path, slice_id: int) -> list[Path]:
    files = slice_config(load_manifest(root), slice_id).get("files") or []
    return [root / f for f in files if str(f).endswith(".ipynb")]


def _tags(cell) -> list[str]:
    return list(cell.get("metadata", {}).get("tags", []))


def structure_problems(nb) -> list[str]:
    problems, last = [], -1
    seen = set()
    for i, cell in enumerate(nb.cells):
        parts = [t for t in _tags(cell) if t in PARTS]
        if len(set(parts)) > 1:
            problems.append(f"cell {i} carries more than one part tag: {parts}")
        for part in parts:
            k = PARTS.index(part)
            if k < last:
                problems.append(f"cell {i} returns to part '{part}' after '{PARTS[last]}'")
            last = max(last, k)
            seen.add(part)
    missing = [p for p in PARTS if p not in seen]
    if missing:
        problems.append(f"missing parts: {', '.join(missing)}")
    explainer = "\n".join(c.source for c in nb.cells if "explainer" in _tags(c))
    absent = [r.strip("*") for r in REGISTERS if r not in explainer]
    if absent:
        problems.append(f"explainer lacks the registers: {', '.join(absent)}")
    return problems


def figure_problems(nb) -> tuple[list[str], int]:
    problems, figures = [], 0
    for i, cell in enumerate(nb.cells):
        if cell.cell_type != "code":
            continue
        if not any(t in out.get("data", {}) for out in cell.get("outputs", []) for t in IMAGE_TYPES):
            continue
        figures += 1
        concludes = str(cell.get("metadata", {}).get("concludes", "")).strip()
        if len(concludes.split()) < 4:
            problems.append(f"figure in cell {i} has no concludes: statement")
    return problems, figures


def execute(path: Path):
    """Run the notebook in memory from its own folder. Returns the executed notebook and the seconds taken."""
    import nbformat
    from nbclient import NotebookClient

    nb = nbformat.read(path, as_version=4)
    for cell in nb.cells:
        if cell.cell_type == "code":
            cell.outputs = []
    client = NotebookClient(nb, timeout=TIME_LIMIT_S, kernel_name="python3",
                            resources={"metadata": {"path": str(path.parent)}})
    inherited = os.environ.pop("MPLBACKEND", None)
    t0 = time.monotonic()
    try:
        client.execute()
    finally:
        if inherited is not None:
            os.environ["MPLBACKEND"] = inherited
    return nb, time.monotonic() - t0


def check(root: Path, slice_id: int, notebooks: list[Path] | None = None, **_: object) -> GateResult:
    import nbformat

    paths = slice_notebooks(root, slice_id) if notebooks is None else list(notebooks)
    if not paths:
        return GateResult(False, "the slice lists no notebook")
    problems, notes = [], []
    for path in paths:
        name = path.name
        if not path.is_file():
            problems.append(f"{name}: missing")
            continue
        problems += [f"{name}: {p}" for p in structure_problems(nbformat.read(path, as_version=4))]
        try:
            executed, seconds = execute(path)
        except Exception as exc:  # a cell raised, or the kernel failed
            first = str(exc).strip().splitlines()
            problems.append(f"{name}: execution failed: {first[-1] if first else type(exc).__name__}")
            continue
        if seconds > TIME_LIMIT_S:
            problems.append(f"{name}: took {seconds:.0f} s, over {TIME_LIMIT_S} s")
        figure_issues, figures = figure_problems(executed)
        problems += [f"{name}: {p}" for p in figure_issues]
        notes.append(f"{name} ran in {seconds:.0f} s with {figures} figures")
    if problems:
        return GateResult(False, "; ".join(problems[:8]))
    return GateResult(True, "; ".join(notes) + "; eight parts in order, three registers, every figure concludes")
