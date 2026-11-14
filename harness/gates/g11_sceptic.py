"""G-11 Sceptic: reviews/slice-N.md exists, its hash block matches the current content of the slice's review
sources, and it records a verdict against each line of "What must not be claimed" in the lens's background file
plus the four epistemic checks in design section 9.

Conventions checked here
- The background file is named by the slice's `background` entry in the manifest, and the review sources by its
  `review_sources` list: the slice's notebook, lens module and app panel (D-29).
- A check is recorded by a line that quotes it and is marked HOLDS or BREACH. A line of "What must not be
  claimed" is quoted by its first sentence, with or without the opening "That".
- The review ends with `VERDICT: HOLDS` or `VERDICT: BREACH`, followed by a block headed "Reviewed sources" that
  gives one line per review source and the SHA-256 of its content. Any BREACH fails the gate.
- The review is stale only when the content of a review source differs from its hash. For a notebook the hash is
  taken over cell sources and text outputs only, so re-executing it without changing what a reader sees does not
  make the review stale. For any other file it is taken over the bytes. Times are not compared, and no file
  outside the review sources is consulted.
- `python -m harness.validate --slice N --stamp-review` writes the block (`write_hash_block`).
"""
from __future__ import annotations

import hashlib
import json
import re
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
BLOCK_HEADING = "Reviewed sources"
BLOCK_START = re.compile(r"^#+\s*reviewed sources\s*$", re.IGNORECASE)
BLOCK_LINE = re.compile(r"^-\s+`?(?P<path>[^`\s]+)`?\s+(?:sha256[:\s]\s*)?(?P<digest>[0-9a-f]{64})\s*$")


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


def _text(value: object) -> str:
    return "".join(value) if isinstance(value, list) else str(value)


def notebook_reader_view(path: Path) -> list[dict]:
    """What a reader sees of a notebook: each cell's type and source, and its text outputs. Execution counts,
    timings, metadata and image bytes are left out."""
    nb = json.loads(path.read_text(encoding="utf-8"))
    cells = []
    for cell in nb.get("cells", []):
        outputs = []
        for out in cell.get("outputs", []) or []:
            kind = out.get("output_type")
            if kind == "stream":
                outputs.append({"stream": out.get("name"), "text": _text(out.get("text", ""))})
            elif kind in ("execute_result", "display_data"):
                text = {m: _text(v) for m, v in (out.get("data") or {}).items() if m.startswith("text/")}
                if text:
                    outputs.append(text)
            elif kind == "error":
                outputs.append({"error": out.get("ename"), "value": out.get("evalue")})
        cells.append({"type": cell.get("cell_type"), "source": _text(cell.get("source", "")), "outputs": outputs})
    return cells


def content_hash(path: Path) -> str:
    """SHA-256 of a review source: a notebook's reader view, or any other file's bytes."""
    if path.suffix == ".ipynb":
        canonical = json.dumps(notebook_reader_view(path), sort_keys=True, ensure_ascii=False)
        return hashlib.sha256(canonical.encode("utf-8")).hexdigest()
    return hashlib.sha256(path.read_bytes()).hexdigest()


def split_review(text: str) -> tuple[list[str], list[str] | None]:
    """The review's lines before the hash block, and the block's lines (None when there is no block)."""
    lines = text.splitlines()
    for i, line in enumerate(lines):
        if BLOCK_START.match(line.strip()):
            return lines[:i], lines[i + 1:]
    return lines, None


def hash_block(root: Path, sources: list[str]) -> str:
    rows = "\n".join(f"- `{rel}` {content_hash(root / rel)}" for rel in sources)
    return f"## {BLOCK_HEADING}\n\n{rows}\n"


def review_sources(root: Path, slice_id: int) -> list[str]:
    return [str(f) for f in slice_config(load_manifest(root), slice_id).get("review_sources") or []]


def write_hash_block(root: Path, slice_id: int) -> str:
    """Append the hash block to reviews/slice-N.md, or replace the one already there. No other line changes."""
    review = root / "reviews" / f"slice-{slice_id}.md"
    if not review.is_file():
        raise FileNotFoundError(f"{review.relative_to(root)} is missing")
    sources = review_sources(root, slice_id)
    if not sources:
        raise ValueError(f"the manifest lists no review_sources for slice {slice_id}")
    missing = [s for s in sources if not (root / s).is_file()]
    if missing:
        raise FileNotFoundError(f"review source missing: {', '.join(missing)}")
    body, _ = split_review(review.read_text(encoding="utf-8"))
    if not any(FINAL.match(l.strip()) for l in body):
        raise ValueError("the review has no VERDICT line; finish it before stamping")
    while body and not body[-1].strip():
        body.pop()
    block = hash_block(root, sources)
    review.write_text("\n".join(body) + "\n\n" + block, encoding="utf-8")
    return block


def check(root: Path, slice_id: int, **_: object) -> GateResult:
    config = slice_config(load_manifest(root), slice_id)
    review_rel = f"reviews/slice-{slice_id}.md"
    review = root / review_rel
    if not review.is_file():
        return GateResult(False, f"{review_rel} is missing: the sceptic has not reviewed this slice")
    background = config.get("background")
    if not background or not (root / background).is_file():
        return GateResult(False, "the manifest names no background file for this slice", evaluable=False)
    sources = [str(f) for f in config.get("review_sources") or []]
    if not sources:
        return GateResult(False, "the manifest lists no review_sources for this slice", evaluable=False)

    problems = []
    body, block = split_review(review.read_text(encoding="utf-8"))
    if block is None:
        problems.append(f"the review has no '{BLOCK_HEADING}' block")
    else:
        recorded = {m.group("path"): m.group("digest") for l in block if (m := BLOCK_LINE.match(l.strip()))}
        for rel in sources:
            if rel not in recorded:
                problems.append(f"{rel} is not in the hash block")
            elif not (root / rel).is_file():
                problems.append(f"{rel} is missing")
            elif content_hash(root / rel) != recorded[rel]:
                problems.append(f"{rel} has changed since the review")

    raw = [l.strip() for l in body if l.strip()]
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
        problems.append("the review does not end with VERDICT: HOLDS or VERDICT: BREACH before the hash block")
    elif final.group(1) == "BREACH":
        problems.append("the review's verdict is BREACH")

    if problems:
        return GateResult(False, "; ".join(problems[:8]))
    return GateResult(True, f"{review_rel} matches its {len(sources)} review sources and records HOLDS against "
                            f"{len(required)} checks")
