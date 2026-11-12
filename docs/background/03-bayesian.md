# 03 — Bayesian inference

**The lesson in one line:** evidence moves a belief; where you end depends on where you began, and saying where you began is a strength, not an embarrassment.

---

## Anchors

### Diagnosis: a belief after a test

| Id | Finding | Numbers | Limits |
|---|---|---|---|
| E-14, E-16 | Scan accuracy by setting | Free fluid 74% and 98% in hospital; 25% (16-36) and 96% (93-98) before it, from 21 of 84 detected and 257 of 266 correctly clear | In hospital: pooled, heterogeneous. Before hospital: one civilian service, 98% blunt trauma, a third of abdominal scans indeterminate |
| E-114 | Counting helps | Given frequencies in place of probabilities, untrained people reached Bayesian answers in up to 50% of inferences | Laboratory problems |
| E-64 | Pictures help further | Adding a grid raised accuracy from 32% to 55% in patients | Patients, not clinicians |
| E-70 | Belief as a random variable | Carry the belief as draws, not one number | Method, not finding |

### Treatment: a belief about an effect

| Id | Reanalysis | Frequentist result | Bayesian result |
|---|---|---|---|
| E-73 | PROPPR | P=.12 at 24 hours | 93% probability that 1:1:1 is better at 24 hours; 87% at 30 days |
| E-74 | STAAMP, prehospital tranexamic acid | Hazard ratio 0.81 (0.59-1.11) | Ratio 0.91 (0.85-0.97) with a CRASH-2 prior; 0.80 (0.65-0.97) with a PATCH prior; 0.82 (0.52-1.23) with none. Probability of benefit 84% to 99% |
| E-108 | EOLIA, four priors | 35% against 46%, not significant | Probability of any benefit 96% (minimal prior), 88% (sceptical), 99% (enthusiastic). Probability of the large effect the trial was sized for: 2% or less |
| E-121 | Cold stored platelets | 5.9% against 10.2%, p=0.28 | 86% probability of reduced mortality |
| E-109 | Method | — | A proposed standard way to do and report such reanalyses |
| E-27, E-28 | CRASH-3 | RR 0.94 (0.86-1.02); mild to moderate subgroup 0.78 (0.64-0.95) | No published reanalysis found (E-33); the notebook's is its own |

---

## Thinking

**The question people actually ask.** A clinician reading PROPPR wants to know how likely it is that the balanced ratio is better. The trial report cannot answer that; it can only say how surprising the data would be if the ratios were equal. The reanalysis (E-73) answers it: 93%. Nothing about the data changed between lens 02 and lens 03. Using the same trial in both notebooks makes that plain.

**The prior is on the table.** E-108 shows one trial under four priors: the probability of any benefit moves from 88% to 99%, while the probability of the large benefit the trial was designed to find stays near zero under all of them. That is the most useful single table for teaching priors, because it shows both what a prior changes and what it cannot rescue.

**Borrowing is a judgement.** E-74 uses CRASH-2 as the prior for a prehospital trial in a different health system. The interval tightens from 0.52-1.23 to 0.85-0.97. Almost all of that certainty comes from the earlier trial, not the new one. Whether CRASH-2's patients are exchangeable with STAAMP's is a clinical question no formula settles. The design's treatment case (CRASH-2 as the prior for CRASH-3) now has a published precedent to be compared against, and the same warning applies: bleeding into the abdomen and bleeding into the skull are not obviously the same problem.

**Small trials are where it matters.** E-121 has 200 patients and p=0.28. The Bayesian reading gives 86%. Neither number settles the question, but they invite different next steps: one says "no evidence", the other says "probably, run the larger trial". For military medicine, where trials are small or absent, this is the usual position.

---

## Use in the notebook

| Part | Material |
|---|---|
| Hook | The scan is clear. Is she safe? (Explainer already written: `../explainers/belief-as-a-random-variable.md`.) |
| By hand | A hundred casualties as a grid, in hospital and before it; then ten draws of the scan's sensitivity |
| Diagnosis case | Belief after a positive and a negative scan in both settings, as a distribution |
| Treatment case | Reproduce the logic of E-74 on CRASH-3 with a CRASH-2 prior, then with a sceptical prior, and show the four-prior table in the style of E-108 |
| Failure | A prior borrowed from the wrong population; updating twice on two readings of the same blood loss |
| Central figure | A hundred casualties |

## What must not be claimed

- That a 93% posterior probability is proof. It is conditional on the model and the prior, and the abstract of E-73 does not state the prior.
- That the notebook's CRASH-3 analysis is a published result. It is a teaching reanalysis and carries the mechanism label.

## Open items

- E-108 was read from a machine-reconstructed abstract; check its figures against the paper.
- O-2: freeBIRD terms before any CRASH data is used.
