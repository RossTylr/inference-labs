"""The belief as a random variable (D-19; docs/explainers/belief-as-a-random-variable.md).

An `RV` holds an array of simulation draws. Arithmetic is done draw by draw, so draw s of one quantity
always meets draw s of another: the pairing of draws is preserved. A plain number combines with every
draw. Summaries are taken only at the end, with `mean`, `interval` and `prob`.

Quantities that come from the same source must come from the same draws, in the same order, and must
never be sorted or resampled on their own.
"""
from __future__ import annotations

from typing import Callable

import numpy as np


class RV:
    """A random variable carried as draws, with arithmetic that preserves the pairing of draws."""

    __array_ufunc__ = None  # numpy defers to RV's own operators, so 0.2 * rv stays an RV

    def __init__(self, draws) -> None:
        d = np.array(draws, dtype=float)
        if d.ndim != 1 or d.size == 0:
            raise ValueError("an RV needs a one-dimensional, non-empty array of draws")
        d.setflags(write=False)
        self._d = d

    @property
    def draws(self) -> np.ndarray:
        """The draws, read-only, in their original order."""
        return self._d

    def __len__(self) -> int:
        return self._d.size

    def _operand(self, other) -> np.ndarray | float:
        if isinstance(other, RV):
            if len(other) != len(self):
                raise ValueError(f"draws are paired by position: cannot combine {len(self)} draws with {len(other)}")
            return other._d
        value = np.asarray(other, dtype=float)
        if value.ndim != 0:
            raise TypeError("combine an RV with another RV or a single number, not a bare array of draws")
        return float(value)

    def __add__(self, other):
        return RV(self._d + self._operand(other))

    def __radd__(self, other):
        return RV(self._operand(other) + self._d)

    def __sub__(self, other):
        return RV(self._d - self._operand(other))

    def __rsub__(self, other):
        return RV(self._operand(other) - self._d)

    def __mul__(self, other):
        return RV(self._d * self._operand(other))

    def __rmul__(self, other):
        return RV(self._operand(other) * self._d)

    def __truediv__(self, other):
        return RV(self._d / self._operand(other))

    def __rtruediv__(self, other):
        return RV(self._operand(other) / self._d)

    def __pow__(self, other):
        return RV(self._d ** self._operand(other))

    def __neg__(self):
        return RV(-self._d)

    def mean(self) -> float:
        return float(self._d.mean())

    def interval(self, level: float = 0.95) -> tuple[float, float]:
        """The central interval holding `level` of the draws (95% by default: the 2.5th and 97.5th percentiles)."""
        if not 0 < level < 1:
            raise ValueError("level must lie between 0 and 1")
        tail = (1 - level) / 2 * 100
        lo, hi = np.percentile(self._d, [tail, 100 - tail])
        return float(lo), float(hi)

    def prob(self, test: Callable[[np.ndarray], np.ndarray]) -> float:
        """The share of draws for which `test` holds, e.g. `belief.prob(lambda d: d > 0.5)`."""
        return float(np.mean(np.asarray(test(self._d), dtype=bool)))

    def __repr__(self) -> str:
        lo, hi = self.interval()
        return f"RV(mean={self.mean():.3g}, 95% interval {lo:.3g} to {hi:.3g}, {len(self)} draws)"
