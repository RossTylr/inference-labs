"""G-11 Sceptic: reviews/slice-N.md exists, was written after the last source change, and records a verdict
against each line of "What must not be claimed" in the lens's background file plus the four epistemic checks
in design section 9.

Conventions checked here
- The background file is named by the slice's `background` entry in the manifest.
- A check is recorded by a line that quotes it and is marked HOLDS or BREACH. A line of "What must not be
  claimed" is quoted by its first sentence, with or without the opening "That".
- The file ends with `VERDICT: HOLDS` or `VERDICT: BREACH`. Any BREACH fails the gate.
- Sources are the files the manifest lists for the slice, other than the review itself. A file's time is its
  last commit, or its modification time if it has changes not yet committed. The review must be no older than
  the newest source.
"""
from __future__ import annotations

import re
import subprocess
from pathlib import Path

from harness.common import GateResult, load_manifest, slice_config

EPISTEMIC_CHECKS = (
    "accuracy quoted for the wrong cohort or setting",
    "proxy data read as the real thing",
    "civilian data read as military",
    "diagnosis result read as a treatment result",
)
MARK = re.compile(r"\b(HOLDS|BREACH)\b")
FINAL = re.compile(r"^VERDICT:\s*(HOLDS|BREACH)\s*$")


def normalise(text: str) -> str:
    text = text.replace("’", "'").replace("‘", "'").replace("“", '"').replace("”", '"')
    return re.sub(r"\s+", " ", text).strip().lower()


def must_not_claim(background: Path) -> list[str]:
    """The first sentence of each bullet under the heading "What must not be claimed", without "That"."""
    keys, inside = [], False
    for line in background.read_text(encoding="utf-8").splitlines():
        if line.startswith("## "):
            inside = line.strip().lower() == "## what must not be claimed"
            continue
        if inside and line.lstrip().startswith("- "):
            first = re.split(r"(?<=\.)\s", line.lstrip()[2:].strip(), maxsplit=1)[0].rstrip(".")
            keys.append(re.sub(r"^that\s+", "", normalise(first)))
    return keys


def changed_at(root: Path, rel: str) -> float:
    """Last commit time of a file, or its modification time if it has uncommitted changes or no git history."""
    try:
        dirty = subprocess.run(["git", "status", "--porcelain", "--", rel], cwd=root, capture_output=True,
                               text=True, check=True).stdout.strip()
        if not dirty:
            stamp = subprocess.run(["git", "log", "-1", "--format=%ct", "--", rel], cwd=root, capture_output=True,
                                   text=True, check=True).stdout.strip()
            if stamp:
                return float(stamp)
    except (OSError, subprocess.CalledProcessError):
        pass
    return (root / rel).stat().st_mtime


def check(root: Path, slice_id: int, **_: object) -> GateResult:
    config = slice_config(load_manifest(root), slice_id)
    review_rel = f"reviews/slice-{slice_id}.md"
    review = root / review_rel
    if not review.is_file():
        return GateResult(False, f"{review_rel} is missing: the sceptic has not reviewed this slice")
    background = config.get("background")
    if not background or not (root / background).is_file():
        return GateResult(False, "the manifest names no background file for this slice", evaluable=False)

    problems = []
    sources = [str(f) for f in config.get("files") or [] if not str(f).startswith("reviews/") and (root / f).is_file()]
    if sources:
        newest = max(sources, key=lambda f: changed_at(root, f))
        if changed_at(root, review_rel) < changed_at(root, newest):
            problems.append(f"the review is older than {newest}")

    text = review.read_text(encoding="utf-8")
    raw = [l.strip() for l in text.splitlines() if l.strip()]
    marked = [(normalise(l), "BREACH" in MARK.findall(l)) for l in raw if MARK.search(l) and not FINAL.match(l)]
    required = [("must not be claimed", k) for k in must_not_claim(root / background)]
    required += [("epistemic check", k) for k in EPISTEMIC_CHECKS]
    for kind, key in required:
        hits = [breach for line, breach in marked if key in line]
        if not hits:
            problems.append(f"no verdict recorded for the {kind} '{key}'")
        elif any(hits):
            problems.append(f"BREACH recorded for the {kind} '{key}'")
    other_breaches = [line for line, breach in marked if breach and not any(k in line for _, k in required)]
    if other_breaches:
        problems.append(f"{len(other_breaches)} further line(s) marked BREACH")

    final = FINAL.match(raw[-1]) if raw else None
    if not final:
        problems.append("the review does not end with VERDICT: HOLDS or VERDICT: BREACH")
    elif final.group(1) == "BREACH":
        problems.append("the review's verdict is BREACH")

    if problems:
        return GateResult(False, "; ".join(problems[:8]))
    return GateResult(True, f"{review_rel} is current and records HOLDS against {len(required)} checks")
