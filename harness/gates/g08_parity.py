"""G-8 Parity: every number the app displays equals the library's value for the same inputs; app/ imports no
numerical library other than through inference_labs.

How it is checked
- Statically, every file under app/ is parsed, the panel files under app/panels/ included, and its imports are
  compared with a list of numerical libraries.
- Each panel file names, as SOURCE, the library function that computes what it shows (D-27). SOURCE must belong
  to inference_labs.
- The page is run headless (Streamlit's AppTest) for a set of control settings. The controls are keyed by the
  argument names of the function that makes the walk-through casualty, and for each setting the gate compares
  what the page shows with what every panel's SOURCE returns for that casualty: every metric, every table cell
  and every point of the belief band. Any other number in the page's text must be one the library displayed.
"""
from __future__ import annotations

import ast
import importlib.util
import re
from pathlib import Path
from typing import Callable

from harness.common import GateResult

NUMERICAL = {"numpy", "pandas", "scipy", "sklearn", "statsmodels", "torch", "math", "statistics", "random",
             "decimal", "fractions", "numbers", "cmath", "jax", "polars"}
NUMBER = re.compile(r"(?<![\w.\-])\d+(?:\.\d+)?%?")
TEXT_ELEMENTS = ("title", "header", "subheader", "markdown", "caption", "text", "info", "success", "warning", "error")

# Page 1 (R-1.9): controls keyed by the arguments of inference_labs.lenses.bayesian.walkthrough.
CASES = (
    {"patient_type": "haemorrhage", "setting": "pre_hospital", "prior": None, "casualty": 1},
    {"patient_type": "haemorrhage", "setting": "in_hospital", "prior": 0.2, "casualty": 3},
    {"patient_type": "chest", "setting": "pre_hospital", "prior": 0.35, "casualty": 2},
)
WIDGETS = {"patient_type": "selectbox", "setting": "radio", "prior": "slider", "casualty": "number_input"}


def forbidden_imports(path: Path) -> list[str]:
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    found = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            names = [a.name for a in node.names]
        elif isinstance(node, ast.ImportFrom):
            names = [node.module or ""]
        else:
            continue
        found += [n for n in names if n.split(".")[0] in NUMERICAL]
    return found


def panel_modules(root: Path) -> list:
    """The panel files under app/panels/, each imported from its path, in page order."""
    modules = []
    for path in sorted((root / "app" / "panels").glob("*.py")):
        if path.name == "__init__.py":
            continue
        spec = importlib.util.spec_from_file_location(f"_g08_panel_{path.stem}", path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        modules.append(module)
    return sorted(modules, key=lambda m: getattr(m, "ORDER", 0))


def panel_problems(root: Path) -> list[str]:
    problems = []
    for module in panel_modules(root):
        name = module.__name__.removeprefix("_g08_panel_")
        missing = [a for a in ("ORDER", "SOURCE", "render") if not hasattr(module, a)]
        if missing:
            problems.append(f"panel {name} has no {', '.join(missing)}")
        elif not str(getattr(module.SOURCE, "__module__", "")).startswith("inference_labs."):
            problems.append(f"panel {name} takes its numbers from {module.SOURCE!r}, not from inference_labs")
    return problems


def library_display(inputs: dict, root: Path | None = None) -> dict:
    """What the library computes for the page: every panel's SOURCE applied to the walk-through casualty. Metrics,
    the step table and the belief band are compared element by element; everything else supplies the numbers the
    page's text may show."""
    from inference_labs.lenses import bayesian

    walk = bayesian.walkthrough(**inputs)
    root = Path(__file__).resolve().parents[2] if root is None else root
    expected: dict = {"metrics": {}, "scan_sources": bayesian.SCAN_SOURCES}
    for module in panel_modules(root):
        shown = module.SOURCE(walk)
        expected["metrics"].update(shown.get("metrics", {}))
        for key, value in shown.items():
            if key in ("table", "band"):
                expected[key] = value
            elif key != "metrics":
                expected[f"{module.__name__}:{key}"] = value
    return expected


def _tokens(value) -> set[str]:
    if isinstance(value, dict):
        return set().union(*(_tokens(v) | _tokens(k) for k, v in value.items())) if value else set()
    if isinstance(value, (list, tuple)):
        return set().union(*(_tokens(v) for v in value)) if value else set()
    return set(NUMBER.findall(str(value)))


def _chart_rows(at) -> list[list[dict]]:
    import pyarrow as pa

    rows = []
    for el in at.main:
        if getattr(el, "type", None) == "vega_lite_chart":
            proto = el.proto
            rows.append(pa.ipc.open_stream(proto.data.data).read_all().to_pylist() if proto.HasField("data") else [])
    return rows


def page_problems(app: Path, inputs: dict, expected: dict) -> list[str]:
    from streamlit.testing.v1 import AppTest

    at = AppTest.from_file(str(app), default_timeout=120)
    at.run()
    for key, value in inputs.items():
        if value is None:
            continue
        getattr(at, WIDGETS[key])(key=key).set_value(value)
    at.run()
    if at.exception:
        return [f"the page raised: {at.exception[0].value}"]

    problems = []
    shown = {m.label: m.value for m in at.metric}
    if shown != expected.get("metrics", {}):
        problems.append(f"metrics {shown} differ from the library's {expected.get('metrics')}")
    tables = [t.value.astype(str).to_dict(orient="records") for t in at.table]
    if expected.get("table") and expected["table"] not in tables:
        problems.append("the step table differs from the library's")
    charts = _chart_rows(at)
    if expected.get("band") and expected["band"] not in charts:
        problems.append("the belief band differs from the library's")

    allowed = _tokens({k: v for k, v in expected.items() if k != "band"})
    for kind in TEXT_ELEMENTS:
        for el in getattr(at, kind):
            stray = sorted(set(NUMBER.findall(str(el.value))) - allowed)
            if stray:
                problems.append(f"{kind} shows {', '.join(stray)}, which the library did not display")
    return problems


def check(root: Path, slice_id: int, app: Path | None = None, cases=None,
          expected: Callable[[dict], dict] | None = None, **_: object) -> GateResult:
    app_dir = root / "app"
    app = app_dir / "streamlit_app.py" if app is None else Path(app)
    if not app.is_file():
        return GateResult(False, f"{app.name} is missing")
    files = sorted(app_dir.rglob("*.py")) if app_dir.is_dir() else []
    problems = [f"{f.name} imports {', '.join(bad)}" for f in set(files) | {app} if (bad := forbidden_imports(f))]

    cases = CASES if cases is None else cases
    if expected is None:
        problems += panel_problems(root)
        expected = lambda inputs: library_display(inputs, root)
    for inputs in cases:
        resolved = dict(inputs)
        problems += [f"{resolved}: {p}" for p in page_problems(app, resolved, expected(resolved))]
    if problems:
        return GateResult(False, "; ".join(problems[:6]))
    return GateResult(True, f"{len(cases)} control settings: every metric, table cell, band point and number shown "
                            "matches the library; no numerical import under app/")
