# inference-labs

Ten ways of reasoning applied to one military casualty, from point of injury to Role 2.

**Teaching material. Not for clinical use.**

**Status:** slices 0 to 10 built; slice 11 built and under review · **Date:** 17 November 2026 · **Author:** Ross Taylor

---

## What it is

**Plain.** One casualty is followed from the point of injury to the surgeon. At each step, ten ways of reasoning are asked the same two questions: what is wrong, and what should be done. The repository shows where they agree, where they differ, and how they fit together.

**Developer.** A Python package, `inference_labs`, holding a seeded casualty generator, a belief type, ten lens modules behind one interface (`diagnose`, `treat`, `scorecard`) and a small knowledge graph. There are twelve notebooks: one per lens, with notebook 00 framing the whole and notebook 11 on the hybrids. A Streamlit app runs them side by side on the same synthetic casualty.

**Technical.** Each lens is an inference procedure with stated inputs, assumptions and a characteristic failure. Diagnosis is framed as abduction: inference to the best explanation of the findings. Every lens is scored on the same seven axes (D-21) against a rule-based baseline, the MPTT-24, coded from the published flowchart (E-08), on synthetic data with known generating structure.

## What is built

Slices 0 to 10 are built: the foundations, then the ten lenses, each lens with its library module, its notebook and its panel on the app's first page. Each slice reads BUILT, and each lens has passed a review.

Slice 11 is built and under review: notebooks 00 and 11, app pages 2 to 4, the lens pages and the gallery. They run, but they are not finished, and what they say may change before the review closes.

| Notebook | Title |
|---|---|
| `00_casualty_thread` | The casualty thread: three kinds of question (slice 11, under review) |
| `01_rules` | Rules |
| `02_frequentist` | Frequentist |
| `03_bayesian` | Bayesian inference |
| `04_decision_trees` | Decision trees |
| `05_stochastic` | Stochastic processes |
| `06_connectionist` | Connectionist |
| `07_causal` | Causal inference |
| `08_knowledge_graph` | Knowledge graphs |
| `09_reinforcement_learning` | Reinforcement learning |
| `10_decision_theory` | Decision theory |
| `11_hybrids` | Hybrids: when a model should say it is not sure (slice 11, under review) |

Every notebook follows the same pattern: a hook, a plain explainer with a central figure, a case worked by hand and checked against the library, a diagnosis case and a treatment case, the characteristic failure produced on purpose, the scorecard, and an analogy with where it breaks.

## The ten lenses

Each lens has a diagnosis case and a treatment case. The table below is `thread.lens_map()` as the library returns it, the same table notebook 00 shows in its scorecard section. Which of E-117's three tasks each case asks (description, prediction or counterfactual prediction) is my own sorting, not a source's. The fit, native or weak, is read from each lens's scorecard, not typed here. Diagnosis is nearly always prediction, and several treatment cases are predictions too: the ABC score and lens 04's treatment tree predict who will need blood; they do not estimate what blood does.

| lens | diagnosis case | diagnosis asks | diagnosis fit | treatment case | treatment asks | treatment fit |
|---|---|---|---|---|---|---|
| 01 Rules | MPTT-24 priority | prediction | native | ABC score: who is likely to need massive transfusion | prediction | native |
| 02 Frequentist | a test's error rates, by cohort and setting | description | native | a randomised trial read as a test and an interval | counterfactual prediction | weak |
| 03 Bayesian | belief in bleeding into the abdomen after a scan | prediction | native | belief that tranexamic acid helps, from a trial and a prior | counterfactual prediction | weak |
| 04 Decision trees | need for an intervention from four signs | prediction | native | who gets blood first: who is bleeding | prediction | native |
| 05 Stochastic processes | chance of dying from bleeding in the next hour | prediction | weak | the benefit of tranexamic acid left at a delay | counterfactual prediction | native |
| 06 Connectionist | a constructed image: is the oval there? | prediction | native | need for an intervention from four signs | prediction | weak |
| 07 Causal | who gets scanned, and how that biases measured accuracy | description | weak | the effect of tranexamic acid, naive, adjusted and true | counterfactual prediction | native |
| 08 Knowledge graph | findings to candidate injuries, by traversal | prediction | native | injury to intervention to the echelon that holds it | description | native |
| 09 Reinforcement learning | which question to ask next | prediction | weak | a dosing policy's value, estimated from logs of another | counterfactual prediction | native |
| 10 Decision theory | where to set the triage threshold, given costs | prediction | weak | treat here or evacuate; two casualties and one aircraft | counterfactual prediction | native |

## The lens table

Every lens reports its results as scorecard rows: what was measured, the lens's value, the baseline's value on the same casualties where the lens states one, the label, the fit and the data the row was computed on. The library sets every lens's rows side by side in `thread.lens_table(case)`: 122 diagnosis rows and 53 treatment rows, too many to reproduce here. Notebook 11 shows them in full in its scorecard section, and page 3 of the app shows them with a diagnosis and treatment toggle. The lenses do not all score the same target, so read each metric's wording there before setting two rows against each other.

The summary below is `thread.lens_summary()` as the library returns it: one row per lens, with the number of rows in each case, their fit, their labels and the data they were computed on. MPTT-24 is the baseline's own rows. Prediction sets, from notebook 11, wrap the MPTT-24 and lens 04's single tree. To print it yourself:

```bash
python -c "from inference_labs import thread; print(thread.lens_summary().to_string())"
```

It computes every lens's scorecard first, so allow a minute.

| lens | diagnosis rows | diagnosis fit | treatment rows | treatment fit | labels | data |
|---|---|---|---|---|---|---|
| MPTT-24 | 8 | native | 0 | no row | mechanism | generator |
| Bayesian | 8 | native | 1 | weak | mechanism | fixture:crash3.csv, generator |
| Causal inference | 16 | weak | 4 | native | mechanism | generator |
| Connectionist | 4 | native | 8 | weak | mechanism | constructed images, generator |
| Decision theory | 8 | weak | 2 | native | mechanism | generator |
| Frequentist | 8 | native | 1 | weak | mechanism | fixture:crash2.csv, generator |
| Hybrids: prediction sets | 16 | native | 6 | weak | mechanism | generator |
| Knowledge graph | 14 | native | 9 | native | mechanism | generator |
| Reinforcement learning | 8 | weak | 4 | native | mechanism | constructed decision process, generator |
| Rules | 8 | native | 8 | native | mechanism | generator |
| Stochastic processes | 8 | weak | 2 | native | mechanism | generator |
| Decision trees | 16 | native | 8 | native | mechanism | generator |

Every row carries the mechanism label, because every row is computed on synthetic data.

## What synthetic data can and cannot show

Every computed result is labelled *mechanism* or *evidence*. A mechanism is a result on synthetic data: the generator's casualties, the CRASH-2 and CRASH-3 fixtures, constructed images or a constructed decision process. Synthetic data can only confirm the model that made them. Evidence would be a result on real trial data, and there is none yet (see Data). Figures quoted from published sources carry their evidence id.

**What it can show.**

- Whether the code does what the method says. Each notebook works a case by hand and checks it against the library.
- What no record holds. The generator holds both outcomes of tranexamic acid for every casualty, so a counterfactual can be read directly and a naive reading checked against it. In notebook 00, a constructed before and after in which the mix and the treatment change at once credits the drug, read naively, with the whole fall in deaths from bleeding; read from both outcomes, the drug accounts for 15% to 21% of the fall across 20 further pairs of samples (mechanism).
- How a method fails. Each notebook produces its lens's characteristic failure on purpose, on casualties whose truth is known.

**What it cannot show.**

- That a method works on real casualties. The generator holds the effect of tranexamic acid because it was built with it: the effect is an input, not a discovery, and the harm the drug does in the generator when given after 3 hours is taken from an exploratory analysis (E-23) of a civilian trial (E-22).
- A finding about injury sites. The generator reproduces the gap between where casualties are most often injured and where the lethal haemorrhage lay among deaths judged potentially survivable, but not as a finding: its share of bleeding deaths at each site is set to E-41 by construction.
- A different operation, or a real evacuation chain. The default mix is the UK field hospital admissions of one theatre (E-34 to E-36); it does not describe a future operation, and any other mix is an assumption. The times to care are drawn from assumed distributions, so they measure no evacuation chain. Each synthetic casualty has at most one condition.
- The cohort the baseline was validated on. Of the generator's injured, 26.5% need a life-saving intervention (mechanism), against 47.6% Priority 1 in the military registry (E-09), so they are a milder cohort than the one the MPTT-24 was validated on (D-23). Of its battle casualties alone, 50.2% need one (mechanism), so they are not (notebook 11).
- Anything about a scan or a patient from the proxy tasks. Lens 06's image task runs on constructed images: it shows how a network behaves, not how well any network reads any scan. Lens 09's treatment case runs on a constructed decision process, not ICU-Sepsis (E-49), and every number in it is an assumption.

## Data

The notebooks and the app run on synthetic data, so they need no download. Notebook 03 has one cell that reads a CRASH-3 file only if a local path outside the repository is given in the environment variable `INFERENCE_LABS_CRASH3`. CRASH-3's patient-level data need registration with the data holder, and I have not yet read the terms of use (open item O-2), so that cell has not been run on a real file and no trial file is in the repository. Notebooks 02 and 03 run their trial code on synthetic fixtures of 200 rows each in `tests/fixtures/`, which hold no trial records.

## Install

Python 3.11 or later. Continuous integration runs on 3.12.

```bash
git clone https://github.com/RossTylr/inference-labs.git
cd inference-labs
python -m venv .venv
source .venv/bin/activate
pip install -e .
```

## Run the notebooks

Jupyter's interface is not among the package's dependencies, so install it first:

```bash
pip install jupyterlab
jupyter lab notebooks/
```

Each notebook runs from top to bottom on the synthetic generator. Where a central figure has a control, such as `CASUALTY` in notebook 00 or `LEVEL` in notebook 11, change it and run the cell again. To run a notebook without opening it, which reports any error and saves nothing:

```bash
jupyter execute notebooks/03_bayesian.ipynb
```

The app's lens pages and gallery show the notebooks as last saved, so saving a re-run notebook changes what they show.

## Run the app

```bash
streamlit run app/streamlit_app.py
```

| Page | Shows |
|---|---|
| Casualty walk-through | One synthetic casualty through each lens's panel in turn, with the patient type, where the scan is done, the prior and the casualty chosen in the sidebar |
| 2 Mix and setting | Every method that flags need for a life-saving intervention, re-scored on synthetic casualties of the mix and setting chosen |
| 3 Lens table | Every lens's scorecard rows for one case, generated from the scorecards |
| 4 Graph explorer | The capability chain for an injury, the provenance of every generator parameter and what depends on one evidence id, and one edge read three ways |
| 5 to 14 | One page per lens: its notebook's explainer and central figure, as last run |
| 15 Gallery | The figures of the executed notebooks |

Pages 2 to 15 are part of slice 11 and are under review. Every number on a page comes from the library, and every page runs on synthetic casualties or on the notebooks as last executed.

## Tests and the validator

```bash
python -m pytest
python -m harness.validate --slice 3
```

The validator runs the gates the manifest lists for one slice and writes its verdict, BUILT, REVISE or BLOCKED, to `reviews/slice-N.verdict.json`, with a row in `LEDGER.md`; running it changes those two files. Every gate is proven by a test that plants a defect and confirms the gate catches it. On each push, continuous integration runs the tests and the validator for every slice whose verdict reads BUILT.

## How claims are kept honest

- **Two labels.** Every result is marked *mechanism* (synthetic data) or *evidence* (real trial data), and the two are kept apart.
- **Every clinical number has a source.** Each one traces to an id in the evidence register. The generator's parameters are listed in the assumptions register, and anything without a source is marked as an assumption.
- **Accuracy is never a single figure.** Triage and scan accuracy are tables keyed by cohort and setting, because the same rule performs differently on a military and a civilian population.
- **Gates, then review.** Each slice must pass the validator, and a separate review then narrows what its notebook, lens module and panel may claim.

## Documents

| Document | Holds |
|---|---|
| [`docs/PRD.md`](docs/PRD.md) | Requirements and gates. Rules where documents disagree |
| [`docs/DESIGN.md`](docs/DESIGN.md) | Decisions and the reasons for them |
| [`docs/background/`](docs/background/README.md) | The published findings each lens is built on, and what must not be claimed |
| [`docs/EVIDENCE.md`](docs/EVIDENCE.md) | The source and verification status of every clinical number |
| [`docs/ASSUMPTIONS.md`](docs/ASSUMPTIONS.md) | Every parameter of the casualty generator, with its evidence id or marked as an assumption |
| [`docs/explainers/`](docs/explainers/belief-as-a-random-variable.md) | Belief as a random variable, the idea that joins the lenses |
| [`docs/BUILD.md`](docs/BUILD.md) | How the build is run, slice by slice |

**Teaching material. Not for clinical use.**
