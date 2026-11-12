# 11 — Hybrids, and what integration really costs

**The lesson in one line:** combining methods is not addition; the join between a model and whatever uses its output, another model or a person, is where most of the value is won or lost.

---

## Anchors

| Id | Finding | Numbers | Limits |
|---|---|---|---|
| E-110 | Physicians with and without a language model | Diagnostic reasoning score 76% with the model, 74% without; difference 2 points (-4 to 8). The model alone: 92% | 50 physicians; written cases, not patients |
| E-111 | Retrieval from curated sources | Rated better than standard models on 314 clinical questions | No effect sizes in the abstract |
| E-107 | Ontology plus statistics in one pipeline | Coded features, then sequencing and automated prioritisation: diagnosis in about 25% | Rare disease |
| E-112 | Conformal prediction | Any model's output turned into a set that contains the truth at a chosen rate, without distributional assumptions | Method |
| E-113 | How far it has reached the clinic | 14 clinical applications found, scattered, rarely with clinicians involved | Review to 2021 |
| E-74 | One trial's answer used as another's prior | Interval narrows from 0.52-1.23 to 0.85-0.97 | Bayesian reanalysis |
| E-31 | A rule that consumes a test | The transfusion score counts a positive scan as one of four items | — |
| E-70 | Uncertainty carried between steps | Belief as draws, summarised at the end | Method |
| E-57 | Fast store and slow learner | Hippocampus stores episodes; cortex learns structure; replay protects old knowledge | A model of two brain systems |
| E-53 | Fast thinking is not the faulty mode | Review finds the intuitive mode no more error-prone than the deliberate one | Abstract |

---

## Thinking

**The tool was better alone.** In the trial (E-110), doctors given a language model scored two points higher than doctors without, a difference the trial could not distinguish from none. The model by itself scored sixteen points above them. So the capability was there and the combination did not transmit it. This is the most important finding for a chapter on integration: a strong component does not guarantee a strong system, and the weak link was the hand-off. Every join in the walk-through page deserves the same suspicion.

**Three kinds of join, all in the evidence.**

- *A model feeding a rule.* The transfusion score takes the scan as a yes or no (E-31). Simple, robust, and lossy: the strength of the evidence is discarded.
- *A model feeding a model.* One trial becomes the prior for the next (E-74). Nothing is discarded, but an assumption is added, that the two populations are alike.
- *Knowledge feeding a model.* An ontology makes patients comparable so a statistical step can rank candidates (E-107); curated documents constrain what a language model says (E-111).

Each has a characteristic way of failing, and the notebook can show all three on the casualty.

**Say how sure you are, as a set.** A triage tool that outputs "Priority One" hides its doubt. Conformal prediction (E-112) wraps the same tool so that it outputs "Priority One", or "Priority One or Two", with a guarantee about how often the set contains the truth. That is cheap to build and suits triage, where "not sure, look again" is a legitimate answer. The review (E-113) shows it has barely been used clinically, so this is new ground and should be presented as a demonstration, not as established practice.

**Uncertainty has to survive the join.** If lens 03 passes a point estimate to lens 10, the decision inherits a certainty that was never there. Carrying the belief as draws (E-70) is the mechanism that stops that. It is also why the belief line exists.

**The brain analogy, with its limit.** The pairing of a fast store of specific cases with a slow learner of general structure (E-57) resembles retrieval joined to a trained model. The resemblance is useful for intuition and stops there: nothing in the source says a clinical system built this way behaves like a brain. And the common story that quick pattern recognition is where errors come from is not supported (E-53).

---

## Use in the notebook

| Part | Material |
|---|---|
| Hook | Doctors given a chatbot scored 76%. Doctors without it scored 74%. The chatbot alone scored 92%. What does that say about putting tools and people together? |
| By hand | Ten triage decisions with a calibration set of twenty: build the prediction sets by hand |
| Built | Conformal prediction on the MPTT-24 and on the tree from lens 04 |
| Described, not built | Retrieval-augmented generation and graph learning, with pointers to the projects that own them |
| Failure | A point estimate passed across a join; a set that is always the whole label space and so always "right" |
| Central figure | The envelopes: a prediction opening into a set |

## What must not be claimed

- That language models diagnose better than doctors. The comparison was on written cases, the model-alone result was a secondary analysis, and no patient was involved.
- That a conformal guarantee holds when the casualty mix changes. The guarantee assumes the calibration cases resemble the new ones; that requirement is general knowledge and was not in the abstract read.

## Open items

- None blocking.
