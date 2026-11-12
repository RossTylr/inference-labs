import numpy as np
import pytest

from inference_labs.belief import RV


def test_needs_one_dimensional_non_empty_draws():
    with pytest.raises(ValueError):
        RV([])
    with pytest.raises(ValueError):
        RV(np.ones((2, 2)))


def test_two_rvs_combine_draw_by_draw():
    a, b = RV([1.0, 2.0, 3.0]), RV([10.0, 20.0, 30.0])
    assert np.array_equal((a + b).draws, [11, 22, 33])
    assert np.array_equal((b - a).draws, [9, 18, 27])
    assert np.array_equal((a * b).draws, [10, 40, 90])
    assert np.array_equal((b / a).draws, [10, 10, 10])
    assert np.array_equal((a ** 2).draws, [1, 4, 9])
    assert np.array_equal((-a).draws, [-1, -2, -3])


def test_a_number_combines_with_every_draw_from_either_side():
    a = RV([1.0, 2.0, 4.0])
    assert np.array_equal((0.5 * a).draws, (a * 0.5).draws)
    assert np.array_equal((1 - a).draws, [0, -1, -3])
    assert np.array_equal((a + 1).draws, (1 + a).draws)
    assert np.array_equal((4 / a).draws, [4, 2, 1])
    assert isinstance(np.float64(0.2) * a, RV)


def test_pairing_is_preserved_through_a_chain_of_arithmetic():
    sens = RV(np.random.default_rng(1).beta(21, 63, 4000))
    total = sens + (1 - sens)
    assert np.allclose(total.draws, 1.0)


def test_different_numbers_of_draws_cannot_be_combined():
    with pytest.raises(ValueError):
        RV([1.0, 2.0]) + RV([1.0, 2.0, 3.0])


def test_a_bare_array_cannot_be_combined_with_an_rv():
    with pytest.raises(TypeError):
        RV([1.0, 2.0]) + np.array([1.0, 2.0])


def test_summaries():
    draws = np.arange(1, 1001, dtype=float)
    rv = RV(draws)
    assert rv.mean() == pytest.approx(500.5)
    lo, hi = rv.interval()
    assert (lo, hi) == pytest.approx(tuple(np.percentile(draws, [2.5, 97.5])))
    assert rv.interval(0.5) == pytest.approx(tuple(np.percentile(draws, [25, 75])))
    assert rv.prob(lambda d: d > 900) == pytest.approx(0.1)
    with pytest.raises(ValueError):
        rv.interval(1.5)


def test_draws_are_read_only():
    rv = RV([1.0, 2.0])
    with pytest.raises(ValueError):
        rv.draws[0] = 5.0
