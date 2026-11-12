"""G-3 Determinism: the generator run twice with seed 42 gives byte-identical output."""
from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Callable

from harness.common import GateResult

N = 100_000
SEED = 42


def _digest(sampler: Callable) -> str:
    casualties, truth = sampler(N, SEED, return_truth=True)
    h = hashlib.sha256()
    h.update(casualties.to_csv(index=False).encode("utf-8"))
    h.update(truth.to_csv(index=False).encode("utf-8"))
    return h.hexdigest()


def check(root: Path, slice_id: int, sampler: Callable | None = None, **_: object) -> GateResult:
    if sampler is None:
        from inference_labs.generator import sample as sampler
    first, second = _digest(sampler), _digest(sampler)
    if first != second:
        return GateResult(False, f"hashes differ: {first[:12]} and {second[:12]}")
    return GateResult(True, f"two runs at n = {N:,}, seed {SEED}: sha256 {first[:12]}", detail={"sha256": first})
