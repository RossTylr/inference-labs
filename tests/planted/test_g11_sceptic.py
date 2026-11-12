"""Planted defects for G-11: no review, a review older than the source, a check left unrecorded, a recorded
breach, and a review without a final verdict."""
import os

import yaml

from harness.gates import g11_sceptic

BACKGROUND = """# 03 — Bayesian

## What must not be claimed

- That a 93% posterior probability is proof. It is conditional on the model and the prior.
- That the notebook's CRASH-3 analysis is a published result. It is a teaching reanalysis.

## Open items

- Something else.
"""
REVIEW = """# Review of slice 1

- That a 93% posterior probability is proof: HOLDS (cell 30)
- The notebook's CRASH-3 analysis is a published result: HOLDS (cell 31)
- Accuracy quoted for the wrong cohort or setting: HOLDS (cells 12, 20)
- Proxy data read as the real thing: HOLDS
- Civilian data read as military: HOLDS (cell 12)
- A diagnosis result read as a treatment result: HOLDS (cell 25)

VERDICT: HOLDS
"""


def _setup(tmp_path, review=REVIEW, review_age=0, source_age=100):
    manifest = {"slices": {1: {"files": ["src/lens.py", "reviews/slice-1.md"], "background": "background.md"}}}
    (tmp_path / "manifest.yaml").write_text(yaml.safe_dump(manifest))
    (tmp_path / "background.md").write_text(BACKGROUND)
    (tmp_path / "src").mkdir()
    source = tmp_path / "src" / "lens.py"
    source.write_text("x = 1\n")
    now = 2_000_000_000
    os.utime(source, (now - source_age, now - source_age))
    if review is not None:
        (tmp_path / "reviews").mkdir()
        path = tmp_path / "reviews" / "slice-1.md"
        path.write_text(review)
        os.utime(path, (now - review_age, now - review_age))
    return g11_sceptic.check(tmp_path, 1)


def test_a_current_complete_review_passes(tmp_path):
    result = _setup(tmp_path)
    assert result.passed, result.reason


def test_no_review_fails(tmp_path):
    result = _setup(tmp_path, review=None)
    assert not result.passed and "missing" in result.reason


def test_a_review_older_than_the_source_fails(tmp_path):
    result = _setup(tmp_path, review_age=200, source_age=100)
    assert not result.passed and "older" in result.reason


def test_an_unrecorded_check_fails(tmp_path):
    review = "\n".join(l for l in REVIEW.splitlines() if "Civilian" not in l)
    result = _setup(tmp_path, review=review)
    assert not result.passed and "civilian data read as military" in result.reason


def test_an_unrecorded_must_not_claim_line_fails(tmp_path):
    review = "\n".join(l for l in REVIEW.splitlines() if "93%" not in l)
    result = _setup(tmp_path, review=review)
    assert not result.passed and "93% posterior probability" in result.reason


def test_a_recorded_breach_fails(tmp_path):
    review = REVIEW.replace("Proxy data read as the real thing: HOLDS", "Proxy data read as the real thing: BREACH (cell 9)")
    result = _setup(tmp_path, review=review.replace("VERDICT: HOLDS", "VERDICT: BREACH"))
    assert not result.passed and "BREACH" in result.reason


def test_a_review_without_a_final_verdict_fails(tmp_path):
    result = _setup(tmp_path, review=REVIEW.replace("VERDICT: HOLDS\n", ""))
    assert not result.passed and "VERDICT" in result.reason
