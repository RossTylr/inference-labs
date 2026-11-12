"""The Lens interface (R-0.8) and the fixed scorecard schema checked by gate G-6.

Every lens exposes three calls: `diagnose(casualty)`, `treat(casualty)` and `scorecard()`. A scorecard row
says what was measured, against what baseline, on which data, and whether the result is a mechanism
(synthetic data, which can only confirm the model that made it) or evidence (real trial data) (D-8).
"""
from __future__ import annotations

from dataclasses import asdict, dataclass, fields, is_dataclass
from pathlib import Path
from typing import Any, Mapping, Protocol, runtime_checkable

LABELS = ("mechanism", "evidence")
FITS = ("native", "weak")
CASES = ("diagnosis", "treatment")
SYNTHETIC_SOURCES = ("generator",)
FIXTURE_PREFIX = "fixture:"


@dataclass(frozen=True)
class ScorecardRow:
    lens: str
    case: str            # diagnosis or treatment
    metric: str
    value: float | str
    baseline: float | str
    label: str           # mechanism or evidence
    fit: str             # native or weak
    data_source: str     # "generator", "fixture:<name>", or a real-data path outside the repository


SCORECARD_FIELDS = tuple(f.name for f in fields(ScorecardRow))


@runtime_checkable
class Lens(Protocol):
    def diagnose(self, casualty: Mapping[str, Any]) -> Any: ...

    def treat(self, casualty: Mapping[str, Any]) -> Any: ...

    def scorecard(self) -> list[ScorecardRow]: ...


def is_real_data_path(source: str, repo_root: Path) -> bool:
    """True only for an absolute filesystem path outside the repository. The generator and fixtures are not real data."""
    if not isinstance(source, str) or source in SYNTHETIC_SOURCES or source.startswith(FIXTURE_PREFIX):
        return False
    path = Path(source)
    if not path.is_absolute():
        return False
    try:
        path.resolve().relative_to(Path(repo_root).resolve())
    except ValueError:
        return True
    return False


def row_problems(row: Any, repo_root: Path) -> list[str]:
    """Everything wrong with one scorecard row. An empty list means the row is well formed and correctly labelled."""
    data = asdict(row) if is_dataclass(row) else dict(row)
    problems = [f"missing {name}" for name in SCORECARD_FIELDS if data.get(name) in (None, "")]
    label, source = data.get("label"), data.get("data_source")
    if label not in (None, "") and label not in LABELS:
        problems.append(f"label '{label}' is not mechanism or evidence")
    if data.get("fit") not in (None, "") and data.get("fit") not in FITS:
        problems.append(f"fit '{data.get('fit')}' is not native or weak")
    if data.get("case") not in (None, "") and data.get("case") not in CASES:
        problems.append(f"case '{data.get('case')}' is not diagnosis or treatment")
    if source not in (None, ""):
        real = is_real_data_path(source, repo_root)
        if label == "evidence" and not real:
            problems.append(f"labelled evidence but the data source '{source}' is not a real-data path")
        if label == "mechanism" and real:
            problems.append(f"labelled mechanism but the data source '{source}' is real data")
    return problems
