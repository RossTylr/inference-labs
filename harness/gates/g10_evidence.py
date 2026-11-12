"""G-10 Evidence use: the notebook's `evidence:` list resolves; no entry with status NOT READ is quoted as a
number; any CARRIED entry is shown with the word "provisional".

Conventions checked here
- The `evidence:` list is the notebook-level metadata key `evidence`, a list of E-ids. Every id in it must be
  a row of docs/EVIDENCE.md, and every E-id the notebook mentions must be in it.
- Text is read line by line: markdown and code source, and the text the cells print. A table row is a line.
- An entry's status is the word its status cell opens with.
- A line that cites a NOT READ entry may not hold a number. Identifiers such as E-33 or CRASH-3 are not numbers.
- A line that cites a CARRIED entry must hold the word "provisional".
- The app's source is read under the same two rules, so a figure shown on the page is held to them too (R-1.10).
"""
from __future__ import annotations

import re
from pathlib import Path

from harness.common import GateResult, evidence_rows, load_manifest, slice_config

EID = re.compile(r"\bE-\d{2,3}\b")
STATUS = re.compile(r"^[*\s]*(NOT READ|CARRIED|SECONDARY|CORRECTED|READ)\b")


def status_word(cell: str) -> str:
    """The status a register row opens with: "READ (... were not read)" is READ, not NOT READ."""
    m = STATUS.match(cell.upper())
    return m.group(1) if m else ""
NUMBER = re.compile(r"(?<![\w.\-])\d+(?:[.,]\d+)?%?")


def _lines_of_notebook(nb) -> list[str]:
    lines = []
    for cell in nb.cells:
        lines += cell.source.splitlines()
        for out in cell.get("outputs", []):
            if "text" in out:
                lines += str(out["text"]).splitlines()
            for kind in ("text/plain", "text/markdown", "text/html"):
                if kind in out.get("data", {}):
                    lines += str(out["data"][kind]).splitlines()
    return lines


def line_problems(lines: list[str], evidence: dict[str, str], where: str) -> list[str]:
    problems = []
    for n, line in enumerate(lines, start=1):
        ids = set(EID.findall(line))
        if not ids:
            continue
        status = {i: status_word(evidence.get(i, "")) for i in ids}
        not_read = sorted(i for i, s in status.items() if s == "NOT READ")
        if not_read and NUMBER.search(EID.sub("", line)):
            problems.append(f"{where} line {n}: {', '.join(not_read)} is NOT READ but the line quotes a number")
        carried = sorted(i for i, s in status.items() if s == "CARRIED")
        if carried and "provisional" not in line.lower():
            problems.append(f"{where} line {n}: {', '.join(carried)} is CARRIED but the line does not say provisional")
    return problems


def check(root: Path, slice_id: int, notebooks: list[Path] | None = None, app_files: list[Path] | None = None,
          evidence_path: Path | None = None, **_: object) -> GateResult:
    import nbformat

    evidence = evidence_rows(evidence_path or root / "docs" / "EVIDENCE.md")
    if not evidence:
        return GateResult(False, "no evidence rows could be read", evaluable=False)
    if notebooks is None:
        files = slice_config(load_manifest(root), slice_id).get("files") or []
        notebooks = [root / f for f in files if str(f).endswith(".ipynb")]
    if app_files is None:
        app_files = sorted((root / "app").rglob("*.py")) if (root / "app").is_dir() else []
    if not notebooks:
        return GateResult(False, "the slice lists no notebook")

    problems, cited = [], 0
    for path in notebooks:
        nb = nbformat.read(path, as_version=4)
        declared = nb.metadata.get("evidence")
        if not isinstance(declared, list) or not declared:
            problems.append(f"{path.name}: no evidence: list in the notebook metadata")
            declared = []
        unresolved = sorted(set(declared) - set(evidence))
        if unresolved:
            problems.append(f"{path.name}: evidence list does not resolve: {', '.join(unresolved)}")
        lines = _lines_of_notebook(nb)
        mentioned = set(EID.findall("\n".join(lines)))
        undeclared = sorted(mentioned - set(declared))
        if undeclared:
            problems.append(f"{path.name}: cites {', '.join(undeclared)} without listing it under evidence:")
        cited += len(set(declared))
        problems += line_problems(lines, evidence, path.name)
    for path in app_files:
        problems += line_problems(path.read_text(encoding="utf-8").splitlines(), evidence, path.name)

    if problems:
        return GateResult(False, "; ".join(problems[:8]))
    return GateResult(True, f"{cited} evidence ids listed and resolved; no NOT READ entry quoted as a number; "
                            "every CARRIED entry marked provisional")
