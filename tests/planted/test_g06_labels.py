"""Planted defects for G-6: an unlabelled row, an evidence label on synthetic data, and a pending baseline after\nslice 2 is BUILT (R-1.8)."""
import json

from harness.gates import g06_labels


def _row(**overrides):
    row = {"lens": "test", "case": "diagnosis", "metric": "sensitivity", "value": 0.7, "baseline": 0.6,
           "label": "mechanism", "fit": "native", "data_source": "generator"}
    row.update(overrides)
    return row


class FakeLens:
    def __init__(self, rows):
        self.rows = rows

    def diagnose(self, casualty):
        return None

    def treat(self, casualty):
        return None

    def scorecard(self):
        return self.rows


def test_correct_labels_pass(tmp_path):
    lenses = {"fake": FakeLens([_row(), _row(label="evidence", data_source="/data/real/crash2.csv")])}
    result = g06_labels.check(tmp_path, 0, lenses=lenses)
    assert result.passed, result.reason


def test_unlabelled_row_fails(tmp_path):
    row = _row()
    del row["label"]
    result = g06_labels.check(tmp_path, 0, lenses={"fake": FakeLens([row])})
    assert not result.passed and "label" in result.reason


def test_evidence_on_synthetic_data_fails(tmp_path):
    result = g06_labels.check(tmp_path, 0, lenses={"fake": FakeLens([_row(label="evidence")])})
    assert not result.passed and "evidence" in result.reason


def test_evidence_on_a_path_inside_the_repository_fails(tmp_path):
    inside = str(tmp_path / "tests" / "fixtures" / "crash2.csv")
    result = g06_labels.check(tmp_path, 0, lenses={"fake": FakeLens([_row(label="evidence", data_source=inside)])})
    assert not result.passed


def test_pending_baseline_passes_until_slice_2_is_built(tmp_path):
    lenses = {"fake": FakeLens([_row(baseline="pending slice 2")])}
    assert g06_labels.check(tmp_path, 1, lenses=lenses).passed
    (tmp_path / "reviews").mkdir()
    (tmp_path / "reviews" / "slice-2.verdict.json").write_text(json.dumps({"verdict": "BUILT"}))
    result = g06_labels.check(tmp_path, 1, lenses=lenses)
    assert not result.passed and "slice 2" in result.reason


def test_any_other_string_in_place_of_a_number_fails(tmp_path):
    result = g06_labels.check(tmp_path, 1, lenses={"fake": FakeLens([_row(value="about 70%")])})
    assert not result.passed and "number" in result.reason
