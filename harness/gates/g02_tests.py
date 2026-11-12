"""G-2 Tests: `pytest -q` passes, and nothing is skipped without a reason string."""
from __future__ import annotations

import subprocess
import sys
import tempfile
import xml.etree.ElementTree as ET
from pathlib import Path

from harness.common import GateResult

NO_REASON = {"", "unconditional skip"}


def check(root: Path, slice_id: int, **_: object) -> GateResult:
    with tempfile.TemporaryDirectory() as tmp:
        report = Path(tmp) / "junit.xml"
        proc = subprocess.run(
            [sys.executable, "-m", "pytest", "-q", "-p", "no:cacheprovider", f"--junitxml={report}"],
            cwd=root,
            capture_output=True,
            text=True,
        )
        if not report.exists():
            tail = (proc.stdout + proc.stderr).strip().splitlines()[-3:]
            return GateResult(False, f"pytest produced no report (exit {proc.returncode}): {' | '.join(tail)}")
        tree = ET.parse(report)

    cases = list(tree.iter("testcase"))
    failed = [c for c in cases if c.find("failure") is not None or c.find("error") is not None]
    bare_skips = []
    for c in cases:
        skip = c.find("skipped")
        if skip is not None and skip.get("message", "").strip().lower() in NO_REASON:
            bare_skips.append(f"{c.get('classname')}::{c.get('name')}")

    if proc.returncode == 5 or not cases:
        return GateResult(False, "no tests were collected")
    if failed or proc.returncode not in (0,):
        names = [f"{c.get('classname')}::{c.get('name')}" for c in failed][:5]
        return GateResult(False, f"{len(failed)} failing: {', '.join(names) or 'pytest exit ' + str(proc.returncode)}")
    if bare_skips:
        return GateResult(False, f"skipped without a reason: {', '.join(bare_skips[:5])}")
    skipped = sum(1 for c in cases if c.find("skipped") is not None)
    return GateResult(True, f"{len(cases)} tests, {skipped} skipped with a reason, none failing")
