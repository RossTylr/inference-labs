"""Planted defects for G-10: an evidence id that does not resolve, an id cited but not listed, a NOT READ
entry quoted as a number, a CARRIED entry without the word provisional (in the notebook and in the app), and a
civilian source cited without the word civilian (in a notebook markdown cell and in a panel string). A READ entry
whose status note mentions papers not read is still READ. A source with no recognised population cannot be
evaluated."""
import nbformat

from harness.gates import g10_evidence

REGISTER = """| Id | Claim | Verified value | Source | Status |
|---|---|---|---|---|
| E-14 | Scan in hospital | 74% / 98% | `netherton2019` | READ (full text) |
| E-18 | Open image data | None found | search | CARRIED |
| E-33 | A reanalysis | None confirmed | search | NOT READ |
| E-70 | A method | Draws as objects | `gelman2026` | READ (the papers it names were not read) |
| E-20 | CRASH-2 mortality | RR 0.91 | `crash2_2010` | READ |
"""
CURATED = """netherton2019: {kind: B, read: read, population: unstated}
gelman2026: {kind: A, read: read, population: not_applicable}
crash2_2010: {kind: B, read: read, population: civilian}
"""
GOOD_LINES = [
    "In hospital the scan finds 74% of bleeds (E-14).",
    "No open image set was found (E-18, provisional).",
    "No published reanalysis of CRASH-3 was confirmed (E-33).",
    "The belief is carried as 4,000 draws (E-70).",
    "CRASH-2, a trial in a civilian population, found a risk ratio of 0.91 (E-20).",
]


def _check(tmp_path, lines=GOOD_LINES, evidence=("E-14", "E-18", "E-33", "E-70", "E-20"), app=None, cells=None,
           panel=None, curated=CURATED):
    (tmp_path / "EVIDENCE.md").write_text(REGISTER)
    (tmp_path / "curated.yaml").write_text(curated)
    nb = nbformat.v4.new_notebook()
    nb.metadata["evidence"] = list(evidence)
    for text in cells if cells is not None else ["\n".join(lines)]:
        nb.cells.append(nbformat.v4.new_markdown_cell(text))
    path = tmp_path / "nb.ipynb"
    nbformat.write(nb, path)
    app_files = []
    if app is not None:
        (tmp_path / "app.py").write_text(app)
        app_files = [tmp_path / "app.py"]
    return g10_evidence.check(tmp_path, 1, notebooks=[path], app_files=app_files, evidence_path=tmp_path / "EVIDENCE.md",
                              curated_path=tmp_path / "curated.yaml", panel_text=panel or {})


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


def test_a_civilian_source_cited_in_a_cell_without_the_word_fails(tmp_path):
    lines = GOOD_LINES[:4] + ["CRASH-2 found a risk ratio of 0.91 (E-20)."]
    result = _check(tmp_path, lines=lines)
    assert not result.passed and "nb.ipynb cell 0" in result.reason and "E-20" in result.reason


def test_the_word_civilian_must_be_in_the_same_cell(tmp_path):
    cells = ["CRASH-2 was a civilian trial.", "CRASH-2 found a risk ratio of 0.91 (E-20)."]
    result = _check(tmp_path, cells=cells)
    assert not result.passed and "nb.ipynb cell 1" in result.reason


def test_a_civilian_source_cited_in_a_panel_string_without_the_word_fails(tmp_path):
    panel = {"bayesian.py.metrics[key]": "CRASH-2 absolute reduction (E-20)", "bayesian.py.caption": "Belief (E-14)"}
    result = _check(tmp_path, panel=panel)
    assert not result.passed and "bayesian.py.metrics[key]" in result.reason
    assert "bayesian.py.caption" not in result.reason


def test_a_panel_string_that_says_civilian_passes(tmp_path):
    result = _check(tmp_path, panel={"bayesian.py.treatment": "CRASH-2 is civilian (E-20)."})
    assert result.passed, result.reason


def test_a_source_without_a_recognised_population_cannot_be_evaluated(tmp_path):
    result = _check(tmp_path, curated=CURATED.replace("population: unstated", "population: unknown"))
    assert not result.passed and not result.evaluable and "netherton2019" in result.reason
