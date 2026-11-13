"""Lens 01, rules (R-2.7 to R-2.10, R-2.12)."""
import math

import pytest

from inference_labs import baseline
from inference_labs.interface import Lens, row_problems
from inference_labs.lenses import rules as r


def _casualty(**overrides):
    c = {"mechanism": "explosion", "scan_free_fluid": False, "sbp": 120, "heart_rate": 80, "t_phec_min": 50.0,
         "catastrophic_haemorrhage": False, "walking": False, "avpu": "A", "respiratory_rate": 16}
    c.update(overrides)
    return c


def test_the_lens_implements_the_interface():
    assert isinstance(r.LENS, Lens)
    assert r.LENS.diagnose(_casualty()) == baseline.triage(_casualty())


def test_abc_score_counts_four_unweighted_items_and_activates_at_two():
    """E-31: penetrating mechanism, positive scan, systolic 90 or less, heart rate 120 or more."""
    assert r.abc_score(_casualty()) == 0
    assert r.abc_score(_casualty(mechanism="small_arms", scan_free_fluid=True, sbp=90, heart_rate=120)) == 4
    assert r.abc_score(_casualty(sbp=91, heart_rate=119)) == 0
    assert r.abc_score(_casualty(scan_free_fluid=None)) == 0                   # no scan is not a positive one
    one, two = r.LENS.treat(_casualty(sbp=85)), r.LENS.treat(_casualty(sbp=85, heart_rate=130))
    assert (one.abc_score, one.transfusion) == (1, False)
    assert (two.abc_score, two.transfusion) == (2, True)


def test_the_table_version_of_the_abc_score_agrees(small_sample):
    observed, _ = small_sample
    observed = observed[observed["stream"] == "battle"]
    table = r.abc_table(observed)
    for i in range(0, len(observed), 53):
        assert table["score"].iloc[i] == r.abc_score(observed.iloc[i].to_dict())


def test_the_doctrine_rule_cannot_be_met_from_the_bedside_alone():
    """E-86: three of four items, two of which need a laboratory."""
    assert r.doctrine_bedside_items(_casualty(sbp=80, heart_rate=130)) == 2 < r.DOCTRINE_NEEDS
    assert len(r.DOCTRINE_LABORATORY_ITEMS) == 2


def test_tranexamic_acid_only_within_three_hours():
    assert r.txa_inside(180) and not r.txa_inside(181)
    assert r.LENS.treat(_casualty(t_phec_min=200.0)).tranexamic_acid_time_condition_met is False
    assert r.LENS.treat(_casualty(t_phec_min=50.0)).tranexamic_acid_time_condition_met is True


def test_the_military_sieve_is_only_a_published_operating_point():
    """R-2.7: the register holds the Sieve's performance (E-10), not its algorithm, so nothing codes it."""
    sieve = [p for p in r.PUBLISHED.values() if p.rule == "Military Sieve"]
    assert {(p.sensitivity, p.specificity, p.source) for p in sieve} == {(0.432, 0.937, "E-10"), (0.280, 0.941, "E-10")}
    for module in (r, baseline):
        assert not [name for name in dir(module) if "sieve" in name.lower() and callable(getattr(module, name))]


def test_predictive_values_follow_from_the_two_prevalences():
    """R-2.9: E-09's 67.0% and 34.0% reproduced from its accuracy and its two shares of Priority 1."""
    for key in ("MPTT-24, military", "MPTT-24, civilian"):
        p = r.PUBLISHED[key]
        assert r.ppv(p.sensitivity, p.specificity, p.prevalence) == pytest.approx(p.ppv, abs=0.005)


def test_the_assumed_chest_wall_shape_reproduces_e104s_catheter_figure():
    """R-2.9: the normal shape is an assumption, checked against E-104's 99% for an 8 cm catheter."""
    assert r.needle_reaches(r.CATHETER_CM) == pytest.approx(r.CATHETER_REACH_PUBLISHED, abs=0.01)
    assert r.needle_reaches(r.NEEDLE_CM) < 0.5        # the mean chest wall is thicker than the needle is long


def test_scorecard_has_both_cases_and_the_seven_axes(root):
    rows = r.LENS.scorecard()
    assert rows and all(not row_problems(row, root) for row in rows)
    assert {row.case for row in rows} == {"diagnosis", "treatment"}
    assert all(row.label == "mechanism" and row.fit == "native" for row in rows)
    assert all(isinstance(row.baseline, float) and not math.isnan(row.baseline) for row in rows)
    axes = r.seven_axes()
    assert [a.split()[0] for a in axes.index] == [str(i) for i in range(1, 8)]
    assert all(axes.loc[a].str.len().gt(0).all() for a in axes.index)
    assert axes.iloc[6].tolist() == ["Pending until lens 10"] * 2


def test_the_panel_states_both_readings_and_labels_its_published_figures():
    from inference_labs.lenses import bayesian

    for patient_type, casualty in (("haemorrhage", 1), ("chest", 2), ("head", 3)):
        shown = bayesian.walkthrough(patient_type, "pre_hospital", None, casualty).display()["baseline"]
        assert "reading the published figure" in shown["priority"] and "Reading the paper's text" in shown["priority"]
        assert "(E-09, E-11)" in shown["published"] and "not at the point of injury" in shown["published"]
        assert "an assumption" in shown["transfusion"] and "(E-86)" in shown["txa"]
