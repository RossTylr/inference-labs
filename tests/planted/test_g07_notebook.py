"""Planted defects for G-7: a missing part, parts out of order, a missing register, a figure without a
conclusion (also when the environment sets a non-interactive plotting backend), and a cell that fails."""
import nbformat

from harness.gates import g07_notebook

PARTS = g07_notebook.PARTS
EXPLAINER = "**Plain.** a\n\n**Developer.** b\n\n**Technical.** c"
FIGURE = "import matplotlib.pyplot as plt\nplt.plot([0, 1])\nplt.show()"


def _notebook(tmp_path, parts=PARTS, explainer=EXPLAINER, figure_meta=None, code="x = 1"):
    nb = nbformat.v4.new_notebook()
    nb.metadata["kernelspec"] = {"name": "python3", "display_name": "Python 3", "language": "python"}
    for part in parts:
        source = explainer if part == "explainer" else f"Part {part}"
        nb.cells.append(nbformat.v4.new_markdown_cell(source, metadata={"tags": [part]}))
    fig = nbformat.v4.new_code_cell(FIGURE, metadata={"tags": ["case-dx"], **(figure_meta or {})})
    nb.cells.insert(list(parts).index("case-dx") + 1 if "case-dx" in parts else len(nb.cells), fig)
    nb.cells.append(nbformat.v4.new_code_cell(code))
    path = tmp_path / "nb.ipynb"
    nbformat.write(nb, path)
    return path


GOOD = {"concludes": "the line rises as the scan arrives"}


def test_a_well_formed_notebook_passes(tmp_path):
    result = g07_notebook.check(tmp_path, 1, notebooks=[_notebook(tmp_path, figure_meta=GOOD)])
    assert result.passed, result.reason


def test_a_missing_part_fails(tmp_path):
    parts = [p for p in PARTS if p != "failure"]
    result = g07_notebook.check(tmp_path, 1, notebooks=[_notebook(tmp_path, parts=parts, figure_meta=GOOD)])
    assert not result.passed and "failure" in result.reason


def test_parts_out_of_order_fail(tmp_path):
    parts = ["explainer", "hook"] + list(PARTS[2:])
    result = g07_notebook.check(tmp_path, 1, notebooks=[_notebook(tmp_path, parts=parts, figure_meta=GOOD)])
    assert not result.passed and "returns to part" in result.reason


def test_a_missing_register_fails(tmp_path):
    path = _notebook(tmp_path, explainer="**Plain.** a\n\n**Technical.** c", figure_meta=GOOD)
    result = g07_notebook.check(tmp_path, 1, notebooks=[path])
    assert not result.passed and "Developer" in result.reason


def test_a_figure_without_a_conclusion_fails(tmp_path):
    result = g07_notebook.check(tmp_path, 1, notebooks=[_notebook(tmp_path)])
    assert not result.passed and "concludes" in result.reason


def test_a_failing_cell_fails(tmp_path):
    path = _notebook(tmp_path, figure_meta=GOOD, code="raise ValueError('planted')")
    result = g07_notebook.check(tmp_path, 1, notebooks=[path])
    assert not result.passed and "execution failed" in result.reason


def test_a_figure_without_a_conclusion_fails_when_the_backend_is_non_interactive(tmp_path, monkeypatch):
    monkeypatch.setenv("MPLBACKEND", "Agg")
    result = g07_notebook.check(tmp_path, 1, notebooks=[_notebook(tmp_path)])
    assert not result.passed and "concludes" in result.reason
