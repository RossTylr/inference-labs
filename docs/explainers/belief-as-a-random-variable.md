# Belief as a random variable

**Status:** explainer, written to the notebook pattern in `DESIGN.md` section 12.2 · **Date:** 11 November 2026
**Reference:** Gelman A. The challenge of truly probabilistic programming. *Statistical Modeling, Causal Inference, and Social Science*, 11 November 2026 (evidence id E-70).

This page explains one idea from that post and shows why the belief line in inference-labs should use it. Every number below was produced by the code in section 3 with seed 42. The interval shapes for the scan's accuracy are assumptions fitted to published intervals, and are labelled where they appear.

---

## 1. Hook

A positive pre-hospital scan moves the belief that a casualty is bleeding from 20% to 61%. The rule is: evacuate first if the belief is above 50%.

**Before reading on, guess.** Given what is known about how accurate that scan is, how often would the true answer fall below 50%?

- Almost never
- About 1 time in 100
- About 1 time in 11
- About 1 time in 3

---

## 2. The idea, before any medicine

You are driving to a meeting. The drive takes 20 to 30 minutes and parking takes 5 to 10. You do not say the journey takes exactly 32.5 minutes. You say "about half an hour, could be nearer 40". You added two uncertain things and kept the uncertainty.

A computer does not do that unless it is told to. Give it 25 and 7.5 and it returns 32.5 and nothing else. The answer to "will I be there within 35 minutes?" is lost: with these ranges, about one journey in four takes longer.

The idea in the post is to make the uncertain quantity itself the thing the program handles. You write `drive + park`, and what comes back is not a number but a quantity that still knows how uncertain it is.

### Three registers

**Plain.** An uncertain number is carried as a large set of plausible values instead of one best guess. Arithmetic is done on every value in the set at once. At the end you can ask for the middle, the range, or the chance of crossing a line.

**Developer.** A small class wraps a NumPy array of draws and defines `+ - * /` on it. Two such objects combine draw by draw, so draw 17 of one always meets draw 17 of the other. A plain number combines with every draw. Summaries (`mean`, `interval`, `prob`) are methods called only at the end. Cost is one array operation per arithmetic step.

```python
class RV:
    def __init__(self, draws): self.d = np.asarray(draws, float)
    def _v(self, o): return o.d if isinstance(o, RV) else o
    def __add__(self, o): return RV(self.d + self._v(o))
    def __mul__(self, o): return RV(self.d * self._v(o))
    def __truediv__(self, o): return RV(self.d / self._v(o))
    def __rsub__(self, o): return RV(self._v(o) - self.d)
    __radd__, __rmul__ = __add__, __mul__
    def mean(self): return self.d.mean()
    def interval(self): return np.percentile(self.d, [2.5, 97.5])
    def prob(self, test): return test(self.d).mean()
```

**Technical.** A random variable X is represented by S simulation draws x₁…x_S. A function g(X, Y) is evaluated as g(x_s, y_s) for each s, which gives draws from the distribution of g(X, Y) provided the pairs (x_s, y_s) are draws from the joint distribution of X and Y. Expectations, quantiles and tail probabilities are Monte Carlo estimates over s. A constant is the degenerate case with the same value at every s. This is the representation Gelman describes, first in the `rv` package and now as `rvar` in the R `posterior` package.

---

## 3. By hand, then in code

### Ten draws by hand

The pre-hospital scan's sensitivity for free fluid is reported as 25%, with an interval of 16 to 36 (E-16). Take ten plausible values of sensitivity and specificity, and work out the belief after a positive scan for each, starting from 20%:

belief = (0.20 × sens) ÷ (0.20 × sens + 0.80 × (1 − spec))

| Draw | Sensitivity | Specificity | Belief after a positive scan |
|---|---|---|---|
| 1 | 0.24 | 0.96 | 0.61 |
| 2 | 0.17 | 0.96 | 0.49 |
| 3 | 0.23 | 0.95 | 0.55 |
| 4 | 0.24 | 0.97 | 0.69 |
| 5 | 0.24 | 0.96 | 0.61 |
| 6 | 0.21 | 0.97 | 0.67 |
| 7 | 0.22 | 0.94 | 0.46 |
| 8 | 0.22 | 0.95 | 0.50 |
| 9 | 0.21 | 0.96 | 0.58 |
| 10 | 0.26 | 0.96 | 0.60 |

Ten rows, ten answers, from 0.46 to 0.69. Two of the ten are below one half. That table is the random variable. Everything after this is the same table with more rows and the loop hidden.

### The same thing with the loop hidden

```python
rng  = np.random.default_rng(42)
sens = RV(rng.beta(20, 60, 4000))     # assumption: fitted to 25% (16 to 36)
spec = RV(rng.beta(288, 12, 4000))    # assumption: fitted to 96% (93 to 98)
prior = 0.20                          # assumption

belief = prior * sens / (prior * sens + (1 - prior) * (1 - spec))
```

The last line is the formula as you would write it on paper. There is no loop and no array index.

| Question | Call | Answer |
|---|---|---|
| Best single figure | `belief.mean()` | 61% |
| Plausible range | `belief.interval()` | 45% to 77% |
| Chance it is above one half | `belief.prob(lambda d: d > 0.5)` | 91% |

---

## 4. The two cases

### Diagnosis: the belief after a scan

The answer to the hook is **about 1 time in 11**. The point estimate says 61%, comfortably above the line. The random variable says there is a 9% chance the belief is really below 50%, because the scan's sensitivity is itself known only roughly.

The same calculation with the in-hospital accuracy (74% and 98%, E-14) gives 90%, with a range of 83% to 96%. The whole range is above the line. So the setting changes not only the answer but how firmly it can be held.

### Treatment: carrying the belief into the benefit

The relative risk of death from bleeding with tranexamic acid given within one hour is 0.68, with an interval of 0.57 to 0.82 (E-22). Treat that as a random variable too, and multiply:

```python
rr = RV(np.exp(rng.normal(np.log(0.68), 0.093, 4000)))   # fitted to 0.68 (0.57 to 0.82)
weighted_reduction = belief * (1 - rr)
```

| | Point arithmetic | Random variable |
|---|---|---|
| Belief-weighted relative reduction | 0.61 × 0.32 = 0.20 | 0.19, range 0.10 to 0.29 |

The middle is the same. What the point arithmetic hides is that the plausible benefit spans nearly threefold. This step applies a population average to one casualty's belief, so it carries the **mechanism** label, not the evidence one (`DESIGN.md` section 12.4).

---

## 5. The failure, on purpose

**Break the pairing.** Sensitivity and the miss rate are two views of one quantity: they must add to exactly 1. Compute `sens + (1 - sens)` and every draw gives 1.

Now shuffle the draws of the miss rate, as would happen if the two were sampled separately or sorted, and add again. The sum now ranges from 0.87 to 1.13. The program is reporting scans that catch 113% of bleeds.

Nothing warns you. The arithmetic ran, and each array on its own still looks right. The rule that prevents it: quantities that come from the same source must come from the same draws, in the same order, and must never be sorted or resampled on their own.

A second, quieter failure is summarising too early. Take the mean of the belief at the scan step, pass 61% on, and every later step inherits a false certainty. Summaries belong at the end of the pathway, not in the middle.

---

## 6. What this is and is not

| It is | It is not |
|---|---|
| A way to carry uncertainty through a calculation without writing loops | A way to create knowledge. The spread out is only as good as the spread put in |
| A fixed set of draws | Live. Change the starting belief and the draws must be recomputed, a point made in the comments on the post |
| A Monte Carlo estimate, so results shift slightly with the seed | Exact |
| Suited to the belief line, where five steps reuse one quantity | Needed for a single calculation that has a formula |

The beta and log-normal shapes above are assumptions chosen to match published intervals. They are not taken from the sources, and a different reasonable shape would move the tails.

---

## 7. Where it sits in inference-labs

- **Belief line.** The belief becomes an `RV` from the scan step onward. The walk-through page draws a band, not a bar.
- **Teaching order.** Show the ten-row table first, then hide it behind the type. This is the concrete-first principle (T-4), and it answers the comment on the post that seeing the draws is the more transparent view.
- **App.** Moving the prior recomputes the draws. It does not reuse stored ones.

## Sources

- Gelman A. The challenge of truly probabilistic programming, 11 November 2026: <https://statmodeling.stat.columbia.edu/2026/11/11/the-challenge-of-truly-probabilistic-programming/>. Read in full, with its three comments.
- Named in the post and not read here: Kerman and Gelman, "Manipulating and summarizing posterior simulations using random variable objects"; the `rvar` datatype in the R `posterior` package (Bürkner, Gabry, Kay, Vehtari); LazyPPL; the Python `gvar` library, described in a comment as Gaussian only.
