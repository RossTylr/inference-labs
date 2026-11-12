# inference-labs

Ten ways of reasoning applied to one military casualty, from point of injury to Role 2.

**Teaching material. Not for clinical use.**

**Status:** design complete; build starting at slice 0 · **Date:** 12 November 2026 · **Author:** Ross Taylor

---

## What it is

**Plain.** One casualty is followed from the point of injury to the surgeon. At each step, ten ways of reasoning are asked the same two questions: what is wrong, and what should be done. The repository shows where they agree, where they differ, and how they fit together.

**Developer.** A Python package, `inference_labs`, holding a seeded casualty generator, a belief type, ten lens modules behind one interface (`diagnose`, `treat`, `scorecard`) and a small knowledge graph. Twelve notebooks teach the lenses one at a time. A Streamlit app runs them side by side on the same casualty.

**Technical.** Each lens is an inference procedure with stated inputs, assumptions and a characteristic failure. Diagnosis is framed as abduction: inference to the best explanation of the findings. Lenses are compared on a common scorecard against a rule-based baseline, the MPTT-24, on synthetic data with known generating structure and, in notebooks only, on trial data available on registration.

## The ten lenses

Built one at a time, in the order shown. Bayesian comes first because it is the thinnest slice that proves library, notebook and app together; rules come next because every later lens is compared against them.

| Slice | Lens | What it must show |
|---|---|---|
| 1 | 03 Bayesian | The belief after a scan, carried as a distribution; a trial re-read with a prior; a prior borrowed from the wrong population |
| 2 | 01 Rules | MPTT-24 coded from the published flowchart; the transfusion score; the needle-length failure |
| 3 | 02 Frequentist | Accuracy tables by cohort; protocol against practice; one trial read as a P value |
| 4 | 04 Decision trees | A single tree against a forest; instability under resampling |
| 5 | 10 Decision theory | A threshold from stated costs; net benefit; two casualties and one aircraft |
| 6 | 05 Stochastic | A time-varying hazard against measured points; the constant-hazard failure; decay of benefit |
| 7 | 07 Causal | Observational against randomised estimates; survival bias reproduced and removed |
| 8 | 08 Knowledge graph | Capability chain traversal; a provenance query; a stale dosing edge returned, then caught |
| 9 | 09 Reinforcement learning | A learned policy; a do-nothing policy winning under naive evaluation; the true value revealed |
| 10 | 06 Connectionist | The method on a proxy image set, labelled as such; a shortcut feature learned and exposed |

Notebook 00 frames the whole. Notebook 11 covers conformal prediction, the hybrids, and the brain analogies with where each one breaks.

Every notebook follows the same pattern: a hook, a plain explainer, a case worked by hand, a diagnosis case and a treatment case, the characteristic failure produced on purpose, the scorecard, and a brain analogy with its limits.

## How claims are kept honest

- **Two labels.** Every result is marked *mechanism* (synthetic data, which can only confirm the model that made it) or *evidence* (real trial data), and the two are kept apart.
- **Every clinical number has a source.** Each one traces to an id in the evidence register. Anything without one is marked as an assumption.
- **Accuracy is never a single figure.** Triage and scan accuracy are tables keyed by cohort and setting, because the same rule performs differently on a military and a civilian population.
- **Gates, not judgement.** Each slice is checked by a validator that runs a fixed set of gates and writes the verdict, BUILT, REVISE or BLOCKED, to a ledger. Every gate is proven by a test that plants a defect and confirms the gate catches it. A separate review then narrows what each notebook may claim.

## Data

The app runs on synthetic data only, so it works for anyone. Real data (CRASH-2 and CRASH-3) are used in notebooks only, read from a local path outside the repository, and never committed. Access requires registration with the data holder. Tests run on synthetic fixtures with the same column names.

## Documents

| Document | Holds |
|---|---|
| [`docs/PRD.md`](docs/PRD.md) | Requirements and gates. Rules where documents disagree |
| [`docs/DESIGN.md`](docs/DESIGN.md) | Decisions and the reasons for them |
| [`docs/background/`](docs/background/README.md) | The published findings each lens is built on, and what must not be claimed |
| [`docs/EVIDENCE.md`](docs/EVIDENCE.md) | The source and verification status of every clinical number |
| [`docs/explainers/`](docs/explainers/belief-as-a-random-variable.md) | Belief as a random variable, the idea that joins the lenses |
| [`docs/BUILD.md`](docs/BUILD.md) | How the build is run, slice by slice |

## Requirements

Python 3.11 or later. The package, notebooks and app arrive slice by slice; installation steps will be added with slice 0.
