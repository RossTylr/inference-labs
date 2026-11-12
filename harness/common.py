"""Shared pieces for the validator and the gates."""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parent.parent


@dataclass
class GateResult:
    """The outcome of one gate. `evaluable` is False when the gate could not be run at all."""

    passed: bool
    reason: str
    evaluable: bool = True
    detail: Any = field(default=None)


def load_yaml(path: Path) -> Any:
    with open(path, encoding="utf-8") as fh:
        return yaml.safe_load(fh)


def load_manifest(root: Path) -> dict:
    return load_yaml(root / "manifest.yaml")


def slice_config(manifest: dict, slice_id: int) -> dict:
    slices = manifest.get("slices") or {}
    if slice_id not in slices:
        raise KeyError(f"slice {slice_id} is not in the manifest")
    return slices[slice_id]


def item_status(entry: Any) -> str:
    """Status of an open item, written either as `O-6: closed` or `O-6: {status: waived, reason: ...}`."""
    if isinstance(entry, dict):
        return str(entry.get("status", "open"))
    return str(entry)


def unresolved_items(manifest: dict, slice_id: int) -> list[str]:
    """Items in the slice's blocked_by list that are not closed, or waived with a reason."""
    items = manifest.get("open_items") or {}
    out = []
    for item in slice_config(manifest, slice_id).get("blocked_by") or []:
        entry = items.get(item)
        status = item_status(entry) if entry is not None else "open"
        if status == "closed":
            continue
        if status == "waived" and isinstance(entry, dict) and str(entry.get("reason", "")).strip():
            continue
        out.append(item)
    return out


_EVIDENCE_ROW = re.compile(r"^\|\s*(E-\d+)\s*\|(.*)\|\s*$")


def evidence_rows(evidence_md: Path) -> dict[str, str]:
    """Map each evidence id to the text of its status column in docs/EVIDENCE.md."""
    rows: dict[str, str] = {}
    for line in evidence_md.read_text(encoding="utf-8").splitlines():
        m = _EVIDENCE_ROW.match(line.strip())
        if m:
            cells = [c.strip() for c in line.strip().strip("|").split("|")]
            rows[m.group(1)] = cells[-1]
    return rows
