# Background pack

**Status:** research complete to abstract level, 12 November 2026 · **Author:** Ross Taylor

This folder holds the real research each lens is built on. There is one file per lens and one for the casualty thread. Each gives the anchors (a finding, its numbers, its limits), the reasoning that turns those findings into an inference lesson, how the notebook should use them, and what must not be claimed.

Every number carries an evidence id that resolves in [`../EVIDENCE.md`](../EVIDENCE.md), where its source and the way it was read are recorded. Sources are registered in [`../../library/curated.yaml`](../../library/curated.yaml). `_notes.md` holds the notes taken as each source was read.

## How to use it

The builder reads the lens's background file before writing the notebook. The hook, the by-hand case, the two worked cases and the failure are specified there against real findings. Synthetic data are used to show a mechanism; these findings are what the mechanism is checked against.

## The anchors at a glance

| Lens | Lead anchor | Numbers | Lesson |
|---|---|---|---|
| [00 Thread](00-casualty-thread.md) | What reduced combat mortality | Case fatality 20.0% to 8.6%; 44.2% of averted deaths assigned to tourniquets, blood and transport | Describe, predict, intervene: three different questions |
| [01 Rules](01-rules.md) | A rule written for a different body | 5 cm needle, 5.36 cm chest wall | A rule carries its population with it |
| [02 Frequentist](02-frequentist.md) | Protocol against practice | Missed 63.8% and over-called 7.4% as written; 21.6% and 30.6% as used | Two errors and a line someone chooses |
| [03 Bayesian](03-bayesian.md) | One trial read twice | P=.12, and a 93% probability of benefit | The answer to the question actually asked |
| [04 Trees](04-decision-trees.md) | Ten methods, one problem | The single tree came last; the forest came first | Readable and fragile, or strong and opaque |
| [05 Stochastic](05-stochastic.md) | When bleeding deaths happen | Median 2.0 to 2.6 hours; hourly risk 4.6% falling to under 0.1% | Risk is front-loaded, so a fixed rate is wrong |
| [06 Connectionist](06-connectionist.md) | A network that learned the hospital | Source hospital identified in 99.95%; 0.931 inside, 0.815 outside | Right for the wrong reason |
| [07 Causal](07-causal.md) | Observation against randomisation | 17.4% against 23.9% observed; relative risk 0.85 randomised. Survival bias: 0.37 becomes 0.84 | To be treated you must first survive |
| [08 Knowledge graph](08-knowledge-graph.md) | An ontology at national scale | Diagnosis in about 25% of 4,660 | A maintained map, with a date on every edge |
| [09 Reinforcement learning](09-reinforcement-learning.md) | The trial of the choice a policy learns | 14.0% against 14.9% | The learning is easy; knowing it is good is not |
| [10 Decision theory](10-decision-theory.md) | A value judgement written as a benchmark | Miss under 5%, over-call up to 50% | A probability is not a decision |
| [11 Hybrids](11-hybrids.md) | The tool was better alone | 76% with, 74% without, 92% alone | The join is where value is lost |

## The three anchors as first stated, corrected

| Anchor | As stated | As verified |
|---|---|---|
| Triage | "In a prospective military cohort the MPTT reached 83.6% sensitivity and 51.0% specificity" under the heading MPTT-24 | That figure is the earlier MPTT in one cohort of 357 (E-07). The MPTT-24 itself reached 66.7% and 69.9% on the military registry and 53.5% and 74.8% on a civilian one (E-09). Derivation by logistic regression is confirmed (E-02) |
| Ultrasound | In hospital 69% and 99% for pneumothorax, 74% and 98% for free fluid; before hospital 25% and 96% | Unchanged, but still read only from search extracts (O-6). New: published military work on automating the scan is on swine, dogs and phantoms (E-102, E-103, E-122) |
| Tranexamic acid | CRASH-2, 20,211 patients; prognostic model C-statistic 0.84 | Consistent with the register: 10,096 and 10,115 allocated (20,211), 20,127 analysed (E-19, read through a secondary source; E-30). New: a military observational counterpart (E-71) and a Bayesian reanalysis that uses CRASH-2 as a prior (E-74) |

## What this pass changed in the design

| # | Change | Reason |
|---|---|---|
| B-1 | PROPPR is used in both lens 02 and lens 03 | Same data read two ways: P=.12, then 93% (E-72, E-73) |
| B-2 | The causal lens leads with MATTERs against CRASH-2, with survival bias as the failure; tourniquets become the second example | A military observational study, a randomised trial and a quantified bias on one question (E-71, E-21, E-80) |
| B-3 | The stochastic lens fits a time-varying hazard to measured hourly death rates | E-85 supplies three points on the curve; the fixed-rate chain fails against them |
| B-4 | The connectionist failure uses the hospital-identification result and the military working dog heat maps | Real, and the second is from the military literature (E-98, E-103) |
| B-5 | The reinforcement learning lens sets the learned policy beside the trial of the same choice | E-97 |
| B-6 | The decision theory lens opens on a deployed model judged by consequences | E-96 |
| B-7 | The knowledge graph gives every edge a version and a population | The resuscitation guideline replaced its 2017 edition in 2019 and was updated twice in 2023; a needle rule held for the wrong population (E-86, E-104) |
| B-8 | The hybrids notebook opens on the physician and language model trial | E-110 |
| B-9 | The over-triage benchmark is "below 50%", with under-triage below 5% | E-87. An earlier working figure of 25 to 35% was not supported |

## Coverage by patient type

| Patient type | Lenses with a real anchor |
|---|---|
| Haemorrhage | 01, 02, 03, 04, 05, 07, 08, 10 |
| Chest injury | 00, 01, 02, 06, 08 |
| Head injury | 03, 04, 07 |
| Disease and non-battle injury (sepsis) | 00, 05, 09, 10 |

Head injury is the thinnest: its anchors are two tranexamic acid trials and a children's rule. Chest injury has no trial evidence, only accuracy and anatomy.

## Limits of this pass

- **Abstracts, not papers.** Most entries were read as the publisher's abstract through Europe PMC, OpenAlex or Crossref. Three were read in full (E-86, E-98, E-110). Three were read through summaries (E-76, E-79, E-81). Five are cited without having been read (E-117 to E-120, and the 2013 early warning score paper).
- **No files were downloaded.** The workspace cannot reach the publishers. DOIs are recorded for local retrieval.
- **Author names** for about a dozen entries are from general knowledge or marked "to complete" (O-8).
- **US and civilian weight.** Outcome and trial evidence is mostly US military or civilian. UK-specific anchors are the admissions statistic (E-34), the registry survival paper (E-84), the triage studies (E-01 to E-11) and RePHILL (E-77).
- **Reasoning is mine.** The "Thinking" sections draw connections the sources do not make. Where a point goes beyond a source, the file says so.
