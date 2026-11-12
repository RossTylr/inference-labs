from dataclasses import replace

from inference_labs.baseline import LENS as BASELINE
from inference_labs.interface import SCORECARD_FIELDS, Lens, ScorecardRow, is_real_data_path, row_problems

ROW = ScorecardRow(lens="03", case="diagnosis", metric="sensitivity", value=0.7, baseline="pending slice 2",
                   label="mechanism", fit="native", data_source="generator")


def test_schema_includes_label_and_fit():
    assert "label" in SCORECARD_FIELDS and "fit" in SCORECARD_FIELDS


def test_baseline_satisfies_the_protocol():
    assert isinstance(BASELINE, Lens)


def test_well_formed_mechanism_row_has_no_problems(root):
    assert row_problems(ROW, root) == []


def test_evidence_needs_a_real_data_path(root, tmp_path_factory):
    outside = tmp_path_factory.mktemp("real") / "crash3.csv"
    assert row_problems(replace(ROW, label="evidence"), root)
    assert row_problems(replace(ROW, label="evidence", data_source=str(outside)), root) == []
    assert row_problems(replace(ROW, data_source=str(outside)), root)


def test_fixtures_and_repository_paths_are_not_real_data(root):
    assert not is_real_data_path("fixture:crash2", root)
    assert not is_real_data_path(str(root / "tests" / "fixtures" / "crash2.csv"), root)
    assert not is_real_data_path("relative/path.csv", root)


def test_bad_fit_case_and_missing_fields_are_reported(root):
    assert row_problems(replace(ROW, fit="strong"), root)
    assert row_problems(replace(ROW, case="triage"), root)
    row = dict(ROW.__dict__)
    del row["fit"]
    assert any("fit" in p for p in row_problems(row, root))
