"""G-13 Frozen generator: after slice 1 is BUILT, the hashes of generator.py and params.yaml match the manifest
unless the manifest version has been bumped.

The `frozen` block is written to the manifest at the end of slice 1 (R-1.12). Until then there is nothing to
enforce."""
from __future__ import annotations

import hashlib
from pathlib import Path

from harness.common import GateResult, load_manifest

GENERATOR = Path("src/inference_labs/generator.py")
PARAMS = Path("params.yaml")


def file_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def check(root: Path, slice_id: int, **_: object) -> GateResult:
    manifest = load_manifest(root)
    frozen = manifest.get("frozen")
    if not frozen:
        return GateResult(True, "not frozen yet: the hashes are written when slice 1 is BUILT")

    changed = [
        str(rel) for rel, key in ((GENERATOR, "generator_sha256"), (PARAMS, "params_sha256"))
        if file_sha256(root / rel) != frozen.get(key)
    ]
    if not changed:
        return GateResult(True, f"generator and parameters match the hashes frozen at version {frozen.get('version')}")
    if int(manifest.get("version", 0)) > int(frozen.get("version", 0)):
        return GateResult(True, f"{', '.join(changed)} changed under manifest version {manifest['version']}")
    return GateResult(False, f"{', '.join(changed)} changed without a manifest version bump")
