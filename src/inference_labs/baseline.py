"""The MPTT-24, the rule-based baseline every lens is compared against (D-9).

A stub until slice 2. The rule is coded from the published flowchart only after open item O-1 confirms the
step order and the heart rate comparison.
"""
from __future__ import annotations

from typing import Any, Mapping

from inference_labs.interface import ScorecardRow


class MPTT24:
    """The MPTT-24 behind the Lens interface. Every call raises NotImplementedError("O-1") until slice 2."""

    name = "MPTT-24"

    def diagnose(self, casualty: Mapping[str, Any]) -> Any:
        raise NotImplementedError("O-1")

    def treat(self, casualty: Mapping[str, Any]) -> Any:
        raise NotImplementedError("O-1")

    def scorecard(self) -> list[ScorecardRow]:
        raise NotImplementedError("O-1")


LENS = MPTT24()
