"""G-6 Labels: every scorecard row is labelled `mechanism` or `evidence`; `evidence` appears only where the
data source is a real-data path."""
from __future__ import annotations

import importlib
import pkgutil
from pathlib import Path

from harness.common import GateResult


def discover_lenses() -> dict[str, object]:
    """Every object named LENS in inference_labs.baseline and the modules of inference_labs.lenses."""
    import inference_labs.lenses as lenses_pkg

    found = {}
    modules = ["inference_labs.baseline"] + [
        f"inference_labs.lenses.{m.name}" for m in pkgutil.iter_modules(lenses_pkg.__path__)
    ]
    for name in modules:
        module = importlib.import_module(name)
        if hasattr(module, "LENS"):
            found[name] = module.LENS
    return found


def check(root: Path, slice_id: int, lenses: dict | None = None, **_: object) -> GateResult:
    from inference_labs.interface import row_problems

    if lenses is None:
        lenses = discover_lenses()
    problems, rows_checked, pending = [], 0, []
    for name, lens in lenses.items():
        try:
            rows = lens.scorecard()
        except NotImplementedError as exc:
            pending.append(f"{name} ({exc})")
            continue
        for i, row in enumerate(rows):
            rows_checked += 1
            for p in row_problems(row, repo_root=root):
                problems.append(f"{name} row {i}: {p}")

    if problems:
        return GateResult(False, "; ".join(problems[:8]))
    note = f"; not yet implemented: {', '.join(pending)}" if pending else ""
    return GateResult(True, f"{rows_checked} scorecard rows correctly labelled across {len(lenses)} lenses{note}")
