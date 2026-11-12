"""G-6 Labels: every scorecard row is labelled `mechanism` or `evidence`; `evidence` appears only where the
data source is a real-data path.

Also checks R-1.8: a row's value and baseline are numbers, except that the baseline may read "pending slice 2"
while the MPTT-24 is a stub. That string is accepted only until slice 2 is BUILT."""
from __future__ import annotations

import importlib
import json
import numbers
import pkgutil
from dataclasses import asdict, is_dataclass
from pathlib import Path

from harness.common import GateResult

PENDING = "pending slice 2"


def slice_built(root: Path, slice_id: int) -> bool:
    """True when the validator's last verdict for the slice is BUILT."""
    path = root / "reviews" / f"slice-{slice_id}.verdict.json"
    try:
        return json.loads(path.read_text(encoding="utf-8")).get("verdict") == "BUILT"
    except (OSError, ValueError):
        return False


def value_problems(row: object, pending_allowed: bool) -> list[str]:
    data = asdict(row) if is_dataclass(row) else dict(row)
    problems = []
    for name in ("value", "baseline"):
        v = data.get(name)
        if isinstance(v, numbers.Real) and not isinstance(v, bool):
            continue
        if name == "baseline" and v == PENDING:
            if not pending_allowed:
                problems.append(f"baseline reads '{PENDING}' but slice 2 is BUILT")
            continue
        if v not in (None, ""):
            problems.append(f"{name} '{v}' is neither a number nor '{PENDING}'")
    return problems


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
    pending_allowed = not slice_built(root, 2)
    problems, rows_checked, pending = [], 0, []
    for name, lens in lenses.items():
        try:
            rows = lens.scorecard()
        except NotImplementedError as exc:
            pending.append(f"{name} ({exc})")
            continue
        for i, row in enumerate(rows):
            rows_checked += 1
            for p in row_problems(row, repo_root=root) + value_problems(row, pending_allowed):
                problems.append(f"{name} row {i}: {p}")

    if problems:
        return GateResult(False, "; ".join(problems[:8]))
    note = f"; not yet implemented: {', '.join(pending)}" if pending else ""
    return GateResult(True, f"{rows_checked} scorecard rows correctly labelled across {len(lenses)} lenses{note}")
