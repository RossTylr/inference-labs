"""G-9 Synthetic app: nothing under app/ reads outside the package and its bundled synthetic data (D-7).

Every file under app/ is parsed. It fails on a module that reaches the file system, the network or the
environment; on a call that reads a file or an upload; on a library call that takes a data path; and on a
string that looks like a file path or names a real dataset. The page gets its casualties from the generator
inside inference_labs, and from nowhere else.
"""
from __future__ import annotations

import ast
import re
from pathlib import Path

from harness.common import GateResult

MODULES = {"os", "pathlib", "io", "glob", "shutil", "sys", "urllib", "requests", "http", "socket", "subprocess",
           "tempfile", "sqlite3", "pickle", "csv", "json"}
READ_CALLS = {"open", "read_csv", "read_table", "read_excel", "read_parquet", "read_json", "read_feather",
              "read_pickle", "read_sql", "load", "loadtxt", "genfromtxt", "fromfile", "read_text", "read_bytes",
              "file_uploader", "summary_from_file", "get_env", "getenv"}
PATH_KEYWORDS = {"path", "crash3_path", "data_path", "file", "filename"}
PATH_LIKE = re.compile(r"(^[/~]|^[A-Za-z]:\\|\.(csv|tsv|xlsx?|parquet|feather|json|pkl|pickle|npz|npy|sav|dta|txt)$)", re.I)
REAL_DATA = re.compile(r"data/real|crash-?[23]|freebird|physionet|ddxplus|icu-sepsis", re.I)


def problems_in(path: Path) -> list[str]:
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    found = []
    for node in ast.walk(tree):
        if isinstance(node, (ast.Import, ast.ImportFrom)):
            names = [a.name for a in node.names] if isinstance(node, ast.Import) else [node.module or ""]
            found += [f"imports {n}" for n in names if n.split(".")[0] in MODULES]
        elif isinstance(node, ast.Call):
            func = node.func
            name = func.attr if isinstance(func, ast.Attribute) else getattr(func, "id", "")
            if name in READ_CALLS:
                found.append(f"calls {name}() at line {node.lineno}")
            found += [f"passes {k.arg}= at line {node.lineno}" for k in node.keywords if k.arg in PATH_KEYWORDS]
        elif isinstance(node, ast.Constant) and isinstance(node.value, str):
            text = node.value.strip()
            if PATH_LIKE.search(text) or REAL_DATA.search(text):
                found.append(f"refers to '{text[:40]}' at line {node.lineno}")
    return found


def check(root: Path, slice_id: int, app_files: list[Path] | None = None, **_: object) -> GateResult:
    if app_files is None:
        app_dir = root / "app"
        app_files = sorted(app_dir.rglob("*.py")) if app_dir.is_dir() else []
    if not app_files:
        return GateResult(False, "no app files found under app/")
    problems = [f"{f.name}: {p}" for f in app_files for p in problems_in(f)]
    if problems:
        return GateResult(False, "; ".join(problems[:8]))
    return GateResult(True, f"{len(app_files)} app file(s) read nothing outside the package")
