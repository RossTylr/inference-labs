"""G-1 Manifest: every file the manifest lists for the slice exists; no file under src/, notebooks/ or app/
is unlisted."""
from __future__ import annotations

from pathlib import Path

from harness.common import GateResult, load_manifest, slice_config

CHECKED_DIRS = ("src", "notebooks", "app")
IGNORED_PARTS = {"__pycache__", ".ipynb_checkpoints"}
IGNORED_NAMES = {".DS_Store"}
IGNORED_SUFFIXES = {".pyc"}


def _ignored(path: Path) -> bool:
    if path.name in IGNORED_NAMES or path.suffix in IGNORED_SUFFIXES:
        return True
    return any(part in IGNORED_PARTS or part.endswith(".egg-info") for part in path.parts)


def check(root: Path, slice_id: int, **_: object) -> GateResult:
    manifest = load_manifest(root)
    listed_here = [str(f) for f in slice_config(manifest, slice_id).get("files") or []]
    missing = [f for f in listed_here if not (root / f).is_file()]

    listed_anywhere = {str(f) for s in (manifest.get("slices") or {}).values() for f in (s.get("files") or [])}
    unlisted = []
    for d in CHECKED_DIRS:
        base = root / d
        if not base.exists():
            continue
        for path in sorted(base.rglob("*")):
            rel = path.relative_to(root)
            if path.is_file() and not _ignored(rel) and rel.as_posix() not in listed_anywhere:
                unlisted.append(rel.as_posix())

    if missing or unlisted:
        parts = []
        if missing:
            parts.append(f"missing: {', '.join(missing)}")
        if unlisted:
            parts.append(f"unlisted: {', '.join(unlisted)}")
        return GateResult(False, "; ".join(parts))
    return GateResult(True, f"{len(listed_here)} listed files present; nothing unlisted")
