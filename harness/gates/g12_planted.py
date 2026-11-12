"""G-12 Planted defects: for every gate, a test in tests/planted/ introduces one defect and asserts the gate
fails. The gate fails when a gate has no planted test, or when any planted test fails (a gate passed its own
defect)."""
from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

from harness.common import GateResult

GATE_MODULE = re.compile(r"^g(\d{2})_\w+\.py$")


def check(root: Path, slice_id: int, **_: object) -> GateResult:
    gate_dir = root / "harness" / "gates"
    planted_dir = root / "tests" / "planted"
    numbers = sorted(m.group(1) for p in gate_dir.glob("g*.py") if (m := GATE_MODULE.match(p.name)))
    if not numbers:
        return GateResult(False, "no gate modules found", evaluable=False)
    uncovered = [f"G-{int(n)}" for n in numbers if not list(planted_dir.glob(f"test_g{n}_*.py"))]
    if uncovered:
        return GateResult(False, f"no planted-defect test for {', '.join(uncovered)}")

    proc = subprocess.run(
        [sys.executable, "-m", "pytest", "-q", "-p", "no:cacheprovider", str(planted_dir)],
        cwd=root,
        capture_output=True,
        text=True,
    )
    if proc.returncode != 0:
        failed = [line for line in proc.stdout.splitlines() if line.startswith(("FAILED", "ERROR"))]
        return GateResult(False, f"a gate passed its own defect: {'; '.join(failed[:5]) or proc.stdout[-300:]}")
    summary = proc.stdout.strip().splitlines()[-1] if proc.stdout.strip() else ""
    return GateResult(True, f"{len(numbers)} gates each fail their planted defect ({summary})")
