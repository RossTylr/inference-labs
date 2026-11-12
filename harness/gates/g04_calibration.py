"""G-4 Calibration: at n = 100,000 the generator reproduces each parameter in params.yaml within that
parameter's stated tolerance."""
from __future__ import annotations

from pathlib import Path
from typing import Callable

from harness.common import GateResult, load_yaml


def check(
    root: Path,
    slice_id: int,
    sampler: Callable | None = None,
    params: dict | None = None,
    measures: dict | None = None,
    **_: object,
) -> GateResult:
    from inference_labs import calibration

    if params is None:
        params = load_yaml(root / "params.yaml")
    table = calibration.calibration_table(params, sampler=sampler, measures=measures)
    failing = [row for row in table if not row["pass"]]
    if failing:
        names = [f"{r['parameter']}.{r['key']} ({r['achieved']} against {r['target']} ± {r['tolerance']})"
                 if r["key"] else f"{r['parameter']} ({r['achieved']} against {r['target']} ± {r['tolerance']})"
                 for r in failing[:6]]
        return GateResult(False, f"{len(failing)} of {len(table)} outside tolerance: {'; '.join(names)}", detail=table)
    n_params = len({r["parameter"] for r in table})
    return GateResult(True, f"{n_params} parameters, {len(table)} figures within tolerance", detail=table)
