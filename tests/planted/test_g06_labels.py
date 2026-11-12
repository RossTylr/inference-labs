"""Planted defects for G-6: an unlabelled row, and an evidence label on synthetic data."""
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
