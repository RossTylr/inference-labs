"""G-10 Evidence use: the notebook's `evidence:` list resolves; no entry with status NOT READ is quoted as a
number; any CARRIED entry is shown with the word "provisional"; a notebook cell or panel string that cites a source
recorded as civilian contains the word "civilian" (D-30).

Conventions checked here
- The `evidence:` list is the notebook-level metadata key `evidence`, a list of E-ids. Every id in it must be
  a row of docs/EVIDENCE.md, and every E-id the notebook mentions must be in it.
- Text is read line by line: markdown and code source, and the text the cells print. A table row is a line.
- An entry's status is the word its status cell opens with.
- A line that cites a NOT READ entry may not hold a number. Identifiers such as E-33 or CRASH-3 are not numbers.
- A line that cites a CARRIED entry must hold the word "provisional".
- The app's source is read under the same two rules, so a figure shown on the page is held to them too (R-1.10).
- An evidence id is civilian when a source its register row names in backticks has `population: civilian` in
  library/curated.yaml. Every markdown cell of the slice's notebook, and every string the slice's own panel shows
  (its SOURCE applied to the walk-through casualty under each of gate G-8's control settings), that cites a
  civilian id must contain the word "civilian" itself. A source the register names with no recognised population
  makes the gate not evaluable.
"""
from __future__ import annotations

import re
from pathlib import Path

from harness.common import GateResult, evidence_rows, load_manifest, load_yaml, slice_config

EID = re.compile(r"\bE-\d{2,3}\b")
POPULATIONS = {"civilian", "military", "mixed", "not_applicable", "unstated"}
CIVILIAN = re.compile(r"\bcivilian", re.IGNORECASE)
SOURCE_KEY = re.compile(r"`([A-Za-z0-9_]+)`")
REGISTER_ROW = re.compile(r"^\|\s*(E-\d+)\s*\|")
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


def register_sources(evidence_md: Path) -> dict[str, list[str]]:
    """Map each evidence id to the source keys its register row names in backticks."""
    out: dict[str, list[str]] = {}
    for line in evidence_md.read_text(encoding="utf-8").splitlines():
        m = REGISTER_ROW.match(line.strip())
        if m:
            cells = [c.strip() for c in line.strip().strip("|").split("|")]
            out[m.group(1)] = SOURCE_KEY.findall(cells[3]) if len(cells) > 3 else []
    return out


def civilian_ids(evidence_md: Path, curated: Path) -> tuple[set[str], list[str]]:
    """The evidence ids whose source is recorded as civilian, and the sources named without a known population."""
    sources = register_sources(evidence_md)
    library = load_yaml(curated) or {}
    unknown = sorted({k for keys in sources.values() for k in keys
                      if (library.get(k) or {}).get("population") not in POPULATIONS})
    civil = {eid for eid, keys in sources.items() if any((library.get(k) or {}).get("population") == "civilian"
                                                         for k in keys)}
    return civil, unknown


def _civilian_problem(text: str, civil: set[str], where: str) -> str | None:
    cited = sorted(set(EID.findall(text)) & civil)
    if cited and not CIVILIAN.search(text):
        return f'{where} cites {", ".join(cited)} (civilian source) without the word "civilian"'
    return None


def _strings(value, path: str):
    """Every string in a panel's output, with where it sits."""
    if isinstance(value, str):
        yield path, value
    elif isinstance(value, dict):
        for k, v in value.items():
            yield from _strings(k, f"{path}[key]")
            yield from _strings(v, f"{path}.{k}")
    elif isinstance(value, (list, tuple)):
        for i, v in enumerate(value):
            yield from _strings(v, f"{path}[{i}]")


def panel_strings(root: Path, panel_files: list[Path]) -> dict[str, str]:
    """Every string each panel shows for the walk-through casualty under gate G-8's control settings."""
    from harness.gates import g08_parity
    from inference_labs.lenses import bayesian

    modules = {m.__name__.removeprefix("_g08_panel_"): m for m in g08_parity.panel_modules(root)}
    out: dict[str, str] = {}
    seen: set[tuple[str, str]] = set()
    for path in panel_files:
        module = modules.get(path.stem)
        if module is None or not hasattr(module, "SOURCE"):
            continue
        for case in g08_parity.CASES:
            shown = module.SOURCE(bayesian.walkthrough(**case))
            for where, text in _strings(shown, path.name):
                if (where, text) not in seen:
                    seen.add((where, text))
                    out[f"{where} ({case['patient_type']}, {case['setting']})"] = text
    return out


def check(root: Path, slice_id: int, notebooks: list[Path] | None = None, app_files: list[Path] | None = None,
          evidence_path: Path | None = None, curated_path: Path | None = None,
          panel_text: dict[str, str] | None = None, **_: object) -> GateResult:
    """`panel_text`, when given, stands in for the strings the slice's panel shows (location to text)."""
    import nbformat

    evidence_md = evidence_path or root / "docs" / "EVIDENCE.md"
    evidence = evidence_rows(evidence_md)
    if not evidence:
        return GateResult(False, "no evidence rows could be read", evaluable=False)
    curated = curated_path or root / "library" / "curated.yaml"
    if not curated.is_file():
        return GateResult(False, f"{curated.name} is missing", evaluable=False)
    civil, unknown = civilian_ids(evidence_md, curated)
    if unknown:
        return GateResult(False, f"no recognised population in {curated.name} for {', '.join(unknown[:8])}",
                          evaluable=False)
    files = None
    if notebooks is None:
        files = [str(f) for f in slice_config(load_manifest(root), slice_id).get("files") or []]
        notebooks = [root / f for f in files if f.endswith(".ipynb")]
    if app_files is None:
        app_files = sorted((root / "app").rglob("*.py")) if (root / "app").is_dir() else []
    if not notebooks:
        return GateResult(False, "the slice lists no notebook")
    if panel_text is None:
        files = files if files is not None else [str(f) for f in
                                                 slice_config(load_manifest(root), slice_id).get("files") or []]
        panels = [root / f for f in files if f.startswith("app/panels/") and not f.endswith("__init__.py")]
        panel_text = panel_strings(root, panels)

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
        for n, cell in enumerate(nb.cells):
            if cell.cell_type == "markdown":
                problem = _civilian_problem(cell.source, civil, f"{path.name} cell {n}")
                if problem:
                    problems.append(problem)
    for path in app_files:
        problems += line_problems(path.read_text(encoding="utf-8").splitlines(), evidence, path.name)
    for where, text in panel_text.items():
        problem = _civilian_problem(text, civil, where)
        if problem:
            problems.append(problem)

    if problems:
        return GateResult(False, "; ".join(problems[:8]), detail=problems)
    return GateResult(True, f"{cited} evidence ids listed and resolved; no NOT READ entry quoted as a number; "
                            "every CARRIED entry marked provisional; every civilian source called civilian where "
                            f"cited ({len(panel_text)} panel strings read)")
