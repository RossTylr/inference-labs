"""The MPTT-24 coded from E-08 (R-2.1 to R-2.3)."""
import pytest

from inference_labs import baseline as b
from inference_labs.generator import load_params
from inference_labs.interface import Lens, row_problems


def _casualty(**overrides):
    """A casualty who passes every step and ends in Priority 2."""
    c = {"catastrophic_haemorrhage": False, "walking": False, "avpu": "A", "respiratory_rate": 16, "heart_rate": 80}
    c.update(overrides)
    return c


def test_the_baseline_implements_the_lens_interface():
    assert isinstance(b.LENS, Lens)
    assert b.LENS.reading == b.DEFAULT_READING == "figure"


@pytest.mark.parametrize("overrides, priority, step", [
    ({"catastrophic_haemorrhage": True, "walking": True}, b.P1, 1),     # step 1 comes before walking
    ({"walking": True, "heart_rate": 140}, b.P3, 2),                    # a walker leaves before any vital sign
    ({"breathing": False, "avpu": "U"}, b.DEAD, 3),                     # breathing comes before voice
    ({"avpu": "U", "respiratory_rate": 40}, b.P1, 4),                   # voice comes before respiratory rate
    ({"respiratory_rate": 11}, b.P1, 5),
    ({"respiratory_rate": 24, "heart_rate": 150}, b.P1, 5),             # respiratory rate comes before heart rate
    ({"heart_rate": 100}, b.P1, 6),
    ({}, b.P2, 6),
])
def test_the_six_steps_run_in_e08_order(overrides, priority, step):
    result = b.triage(_casualty(**overrides))
    assert (result.priority, result.step) == (priority, step)


@pytest.mark.parametrize("field, passes, fails", [
    ("respiratory_rate", (12, 23), (11, 24)),     # E-08: 12 to 23 passes
    ("heart_rate", (99,), (100,)),                # E-08: below 100 gives Priority 2
])
def test_thresholds_are_e08s(field, passes, fails):
    for value in passes:
        assert b.triage(_casualty(**{field: value})).priority == b.P2
    for value in fails:
        assert b.triage(_casualty(**{field: value})).priority == b.P1


def test_the_voice_step_has_two_readings():
    """R-2.2: the figure lets a casualty who responds to voice go on; the text sends anything below alert to P1."""
    voice = _casualty(avpu="V")
    assert b.triage(voice, "figure").priority == b.P2
    assert b.triage(voice, "text") == b.Triage(b.P1, 4, "recovery position", "text")
    for level in ("P", "U"):
        assert b.triage(_casualty(avpu=level), "figure").priority == b.P1
        assert b.triage(_casualty(avpu=level), "text").priority == b.P1
    with pytest.raises(ValueError):
        b.triage(voice, "either")


def test_a_casualty_without_a_breathing_entry_is_taken_as_breathing():
    assert b.triage(_casualty()).step == 6
    assert b.triage(_casualty(breathing=False)).priority == b.DEAD


def test_treat_returns_the_flowcharts_own_instruction():
    assert b.LENS.treat(_casualty(catastrophic_haemorrhage=True)) == "apply a tourniquet or haemostatic dressing"
    assert b.LENS.treat(_casualty(avpu="P")) == "recovery position"
    assert b.LENS.treat(_casualty()) == ""


@pytest.mark.parametrize("reading", b.READINGS)
def test_the_table_version_agrees_with_one_casualty_at_a_time(small_sample, reading):
    observed, _ = small_sample
    table = b.triage_table(observed, reading)
    for i in range(0, len(observed), 97):
        one = b.triage(observed.iloc[i].to_dict(), reading)
        assert (table["priority"].iloc[i], table["step"].iloc[i]) == (one.priority, one.step)


def test_the_readings_differ_only_for_casualties_who_respond_to_voice():
    observed, _ = b.generator_sample()
    changes = b.reading_changes(observed)
    assert len(changes) > 0
    assert set(observed.loc[changes.index, "avpu"]) == {"V"}
    assert set(zip(changes["figure"], changes["text"])) == {(b.P2, b.P1)}


def test_the_text_reading_reproduces_e09_on_the_military_cohort():
    """R-2.3: a calibration check on the generator, not evidence about the rule."""
    check = b.calibration_check("military")
    held = check[check["held to E-09"]]
    assert set(held["reading"]) == {"text"} and len(held) == 2
    assert held["within tolerance"].all()
    target = load_params()["parameters"]["triage_accuracy_military"]
    for _, row in held.iterrows():
        assert row["E-09"] == target["value"][row["measure"]]
        assert row["tolerance"] == target["tolerance"] == 0.05


def test_scorecard_rows_are_well_formed(root):
    rows = b.LENS.scorecard()
    assert len(rows) == 8 and all(not row_problems(r, root) for r in rows)
    assert all(r.label == "mechanism" and r.case == "diagnosis" and r.value == r.baseline for r in rows)
    pre, inside = rows[:4], rows[4:]
    assert [r.value for r in pre] == [r.value for r in inside]      # the generator's physiology ignores the setting
