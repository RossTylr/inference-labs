"""Planted defects for G-11: no review, no hash block, a review source whose content changed since the review
(notebook prose, a notebook text output, a lens module string), a check left unrecorded, a recorded breach, and a
review without a final verdict. Also what must not make a review stale: a notebook re-executed with the same
sources and text outputs, and a change to a harness file or another slice's file."""
import json

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
SOURCES = ["notebooks/03_lens.ipynb", "src/lens.py", "app/panels/lens.py"]


def _notebook(prose="The prior is stated.", printed="belief 0.21\n", count=1, png="iVBORw0KGgo=", meta=None):
    return {
        "nbformat": 4, "nbformat_minor": 5, "metadata": meta or {"kernelspec": {"name": "python3"}},
        "cells": [
            {"cell_type": "markdown", "id": "a", "metadata": {"tags": ["hook"]}, "source": [prose]},
            {"cell_type": "code", "id": "b", "execution_count": count,
             "metadata": {"execution": {"iopub.execute_input": f"2026-11-1{count}T10:00:00Z"}},
             "source": ["print('belief 0.21')\n", "plot()"],
             "outputs": [
                 {"output_type": "stream", "name": "stdout", "text": [printed]},
                 {"output_type": "display_data", "metadata": {},
                  "data": {"image/png": png, "text/plain": ["<Figure size 640x480 with 1 Axes>"]}},
             ]},
        ],
    }


def _write_nb(root, **kw):
    (root / SOURCES[0]).write_text(json.dumps(_notebook(**kw), indent=1))


def _setup(tmp_path, review=REVIEW, stamp=True):
    manifest = {"slices": {
        1: {"files": SOURCES + ["tests/test_lens.py"], "review_sources": SOURCES, "background": "background.md"},
        2: {"files": ["src/other.py"], "review_sources": ["src/other.py"], "background": "background.md"},
    }}
    (tmp_path / "manifest.yaml").write_text(yaml.safe_dump(manifest))
    (tmp_path / "background.md").write_text(BACKGROUND)
    for d in ("notebooks", "src", "app/panels", "harness", "tests"):
        (tmp_path / d).mkdir(parents=True)
    _write_nb(tmp_path)
    (tmp_path / "src" / "lens.py").write_text('LABEL = "belief after the scan"\n')
    (tmp_path / "app" / "panels" / "lens.py").write_text('TITLE = "Bayesian"\n')
    (tmp_path / "src" / "other.py").write_text("x = 1\n")
    (tmp_path / "harness" / "gate.py").write_text("y = 1\n")
    (tmp_path / "tests" / "test_lens.py").write_text("def test(): pass\n")
    if review is not None:
        (tmp_path / "reviews").mkdir()
        (tmp_path / "reviews" / "slice-1.md").write_text(review)
        if stamp:
            g11_sceptic.write_hash_block(tmp_path, 1)


def _check(tmp_path):
    return g11_sceptic.check(tmp_path, 1)


def test_a_current_complete_review_passes(tmp_path):
    _setup(tmp_path)
    result = _check(tmp_path)
    assert result.passed, result.reason


def test_stamping_changes_no_line_of_the_review(tmp_path):
    _setup(tmp_path)
    text = (tmp_path / "reviews" / "slice-1.md").read_text()
    assert text.startswith(REVIEW) and "## Reviewed sources" in text
    g11_sceptic.write_hash_block(tmp_path, 1)
    assert (tmp_path / "reviews" / "slice-1.md").read_text() == text


def test_no_review_fails(tmp_path):
    _setup(tmp_path, review=None)
    result = _check(tmp_path)
    assert not result.passed and "missing" in result.reason


def test_a_review_without_a_hash_block_fails(tmp_path):
    _setup(tmp_path, stamp=False)
    result = _check(tmp_path)
    assert not result.passed and "Reviewed sources" in result.reason


def test_changed_prose_in_the_notebook_fails(tmp_path):
    _setup(tmp_path)
    _write_nb(tmp_path, prose="The prior is stated, and it is proof.")
    result = _check(tmp_path)
    assert not result.passed and "03_lens.ipynb has changed" in result.reason


def test_a_changed_text_output_in_the_notebook_fails(tmp_path):
    _setup(tmp_path)
    _write_nb(tmp_path, printed="belief 0.31\n")
    result = _check(tmp_path)
    assert not result.passed and "03_lens.ipynb has changed" in result.reason


def test_a_changed_string_in_the_lens_module_fails(tmp_path):
    _setup(tmp_path)
    (tmp_path / "src" / "lens.py").write_text('LABEL = "proof after the scan"\n')
    result = _check(tmp_path)
    assert not result.passed and "src/lens.py has changed" in result.reason


def test_a_notebook_re_executed_with_the_same_sources_and_text_outputs_passes(tmp_path):
    _setup(tmp_path)
    _write_nb(tmp_path, count=7, png="AAAAAAAAAAAA", meta={"kernelspec": {"name": "python3"}, "language_info": {}})
    result = _check(tmp_path)
    assert result.passed, result.reason


def test_a_change_to_a_harness_file_or_another_slice_passes(tmp_path):
    _setup(tmp_path)
    (tmp_path / "harness" / "gate.py").write_text("y = 2\n")
    (tmp_path / "src" / "other.py").write_text("x = 2\n")
    (tmp_path / "tests" / "test_lens.py").write_text("def test(): assert True\n")
    result = _check(tmp_path)
    assert result.passed, result.reason


def test_an_unrecorded_check_fails(tmp_path):
    _setup(tmp_path, review="\n".join(l for l in REVIEW.splitlines() if "Civilian" not in l))
    result = _check(tmp_path)
    assert not result.passed and "civilian data read as military" in result.reason


def test_an_unrecorded_must_not_claim_line_fails(tmp_path):
    _setup(tmp_path, review="\n".join(l for l in REVIEW.splitlines() if "93%" not in l))
    result = _check(tmp_path)
    assert not result.passed and "93% posterior probability" in result.reason


def test_a_recorded_breach_fails(tmp_path):
    review = REVIEW.replace("Proxy data read as the real thing: HOLDS", "Proxy data read as the real thing: BREACH (cell 9)")
    _setup(tmp_path, review=review.replace("VERDICT: HOLDS", "VERDICT: BREACH"))
    result = _check(tmp_path)
    assert not result.passed and "BREACH" in result.reason


def test_a_review_without_a_final_verdict_fails(tmp_path):
    _setup(tmp_path, review=REVIEW.replace("VERDICT: HOLDS\n", ""), stamp=False)
    result = _check(tmp_path)
    assert not result.passed and "VERDICT" in result.reason
