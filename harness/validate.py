"""Compute the verdict for one slice: BUILT, REVISE or BLOCKED (PRD section 3).

    python -m harness.validate --slice N
    python -m harness.validate --slice N --stamp-review

Runs the gates the manifest lists for slice N, writes reviews/slice-N.verdict.json and appends one row to
LEDGER.md. The verdict and the gate tally are written here and nowhere else.

With --stamp-review it instead writes the "Reviewed sources" hash block at the end of reviews/slice-N.md (gate
G-11) and stops: no gate is run and no ledger row is written. The reviewer uses it once the review is finished.

BUILT    every listed gate passes and no open item in the slice's blocked_by list is unresolved
REVISE   one or more gates fail; the builder may try again
BLOCKED  a gate cannot be evaluated, or an open item listed for the slice is unresolved
"""
from __future__ import annotations

import argparse
import json
import sys
import traceback
from datetime import datetime, timezone
from pathlib import Path

from harness.common import ROOT, GateResult, load_manifest, slice_config, unresolved_items

LEDGER_HEADER = """# Ledger

One row per validation attempt, written by `python -m harness.validate`. Do not edit by hand.

| When (UTC) | Slice | Attempt | Verdict | Gates | Failing or not evaluable | Open items unresolved |
|---|---|---|---|---|---|---|
"""


def run_gates(root: Path, slice_id: int, gate_ids: list[str], registry: dict | None = None) -> dict[str, GateResult]:
    if registry is None:
        from harness.gates import GATES as registry
    results: dict[str, GateResult] = {}
    for gid in gate_ids:
        fn = registry.get(gid)
        if fn is None:
            results[gid] = GateResult(False, "gate not implemented", evaluable=False)
            continue
        try:
            results[gid] = fn(root, slice_id)
        except Exception as exc:  # a gate that crashes cannot be evaluated
            last = traceback.format_exception_only(type(exc), exc)[-1].strip()
            results[gid] = GateResult(False, f"gate raised {last}", evaluable=False)
    return results


def verdict_for(results: dict[str, GateResult], unresolved: list[str]) -> str:
    if unresolved or any(not r.evaluable for r in results.values()):
        return "BLOCKED"
    if all(r.passed for r in results.values()):
        return "BUILT"
    return "REVISE"


def tally(results: dict[str, GateResult]) -> str:
    return f"{sum(r.passed for r in results.values())}/{len(results)} pass"


def _attempt(ledger: Path, slice_id: int) -> int:
    if not ledger.exists():
        return 1
    rows = [line for line in ledger.read_text(encoding="utf-8").splitlines() if line.startswith("| 20")]
    return 1 + sum(1 for line in rows if line.split("|")[2].strip() == str(slice_id))


def record(root: Path, slice_id: int, results: dict[str, GateResult], unresolved: list[str]) -> dict:
    verdict = verdict_for(results, unresolved)
    ledger = root / "LEDGER.md"
    attempt = _attempt(ledger, slice_id)
    when = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M")
    payload = {
        "slice": slice_id,
        "attempt": attempt,
        "when": when,
        "verdict": verdict,
        "tally": tally(results),
        "open_items_unresolved": unresolved,
        "gates": {
            gid: {"passed": r.passed, "evaluable": r.evaluable, "reason": r.reason, "detail": r.detail}
            for gid, r in results.items()
        },
    }
    reviews = root / "reviews"
    reviews.mkdir(exist_ok=True)
    (reviews / f"slice-{slice_id}.verdict.json").write_text(json.dumps(payload, indent=2, default=str) + "\n")

    failing = [gid for gid, r in results.items() if not r.passed]
    if not ledger.exists():
        ledger.write_text(LEDGER_HEADER, encoding="utf-8")
    row = (f"| {when} | {slice_id} | {attempt} | **{verdict}** | {payload['tally']} | "
           f"{', '.join(failing) or '—'} | {', '.join(unresolved) or '—'} |\n")
    with open(ledger, "a", encoding="utf-8") as fh:
        fh.write(row)
    return payload


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--slice", type=int, required=True)
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--stamp-review", action="store_true",
                        help="write the review's hash block (gate G-11) and stop, without validating")
    args = parser.parse_args(argv)

    if args.stamp_review:
        from harness.gates.g11_sceptic import write_hash_block

        print(write_hash_block(args.root, args.slice), end="")
        return 0

    manifest = load_manifest(args.root)
    gate_ids = list(slice_config(manifest, args.slice).get("gates") or [])
    unresolved = unresolved_items(manifest, args.slice)
    results = run_gates(args.root, args.slice, gate_ids)
    payload = record(args.root, args.slice, results, unresolved)

    for gid, r in results.items():
        status = "PASS" if r.passed else ("NOT EVALUABLE" if not r.evaluable else "FAIL")
        print(f"{gid:<5} {status:<13} {r.reason}")
    if unresolved:
        print(f"open items unresolved: {', '.join(unresolved)}")
    print(f"slice {args.slice}, attempt {payload['attempt']}: {payload['verdict']} ({payload['tally']})")
    return {"BUILT": 0, "REVISE": 1, "BLOCKED": 2}[payload["verdict"]]


if __name__ == "__main__":
    sys.exit(main())
