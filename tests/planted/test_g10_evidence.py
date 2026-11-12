"""Planted defects for G-10: an evidence id that does not resolve, an id cited but not listed, a NOT READ
entry quoted as a number, and a CARRIED entry without the word provisional (in the notebook and in the app).
A READ entry whose status note mentions papers not read is still READ."""
import nbformat

from harness.gates import g10_evidence

REGISTER = """| Id | Claim | Verified value | Source | Status |
|---|---|---|---|---|
| E-14 | Scan in hospital | 74% / 98% | `netherton2019` | READ (full text) |
| E-18 | Open image data | None found | search | CARRIED |
| E-33 | A reanalysis | None confirmed | search | NOT READ |
| E-70 | A method | Draws as objects | `gelman2026` | READ (the papers it names were not read) |
"""
GOOD_LINES = [
    "In hospital the scan finds 74% of bleeds (E-14).",
    "No open image set was found (E-18, provisional).",
    "No published reanalysis of CRASH-3 was confirmed (E-33).",
    "The belief is carried as 4,000 draws (E-70).",
]


def _check(tmp_path, lines=GOOD_LINES, evidence=("E-14", "E-18", "E-33", "E-70"), app=None):
    (tmp_path / "EVIDENCE.md").write_text(REGISTER)
    nb = nbformat.v4.new_notebook()
    nb.metadata["evidence"] = list(evidence)
    nb.cells.append(nbformat.v4.new_markdown_cell("\n".join(lines)))
    path = tmp_path / "nb.ipynb"
    nbformat.write(nb, path)
    app_files = []
    if app is not None:
        (tmp_path / "app.py").write_text(app)
        app_files = [tmp_path / "app.py"]
    return g10_evidence.check(tmp_path, 1, notebooks=[path], app_files=app_files, evidence_path=tmp_path / "EVIDENCE.md")


def test_correct_use_passes(tmp_path):
    result = _check(tmp_path)
    assert result.passed, result.reason


def test_an_id_that_does_not_resolve_fails(tmp_path):
    result = _check(tmp_path, evidence=("E-14", "E-18", "E-33", "E-70", "E-999"))
    assert not result.passed and "E-999" in result.reason


def test_an_id_cited_but_not_listed_fails(tmp_path):
    result = _check(tmp_path, evidence=("E-14", "E-18", "E-70"))
    assert not result.passed and "E-33" in result.reason


def test_a_not_read_entry_quoted_as_a_number_fails(tmp_path):
    lines = GOOD_LINES[:2] + ["A reanalysis found a 93% probability of benefit (E-33).", GOOD_LINES[3]]
    result = _check(tmp_path, lines=lines)
    assert not result.passed and "NOT READ" in result.reason


def test_a_carried_entry_without_provisional_fails(tmp_path):
    lines = [GOOD_LINES[0], "No open image set was found (E-18).", GOOD_LINES[2], GOOD_LINES[3]]
    result = _check(tmp_path, lines=lines)
    assert not result.passed and "CARRIED" in result.reason


def test_the_app_is_held_to_the_same_rules(tmp_path):
    result = _check(tmp_path, app='st.caption("Image data: none found (E-18)")\n')
    assert not result.passed and "app.py" in result.reason
