# inference-labs — Product Requirements

**Status:** v1.0, ready to build · **Date:** 12 November 2026 · **Author:** Ross Taylor

This document turns [`DESIGN.md`](DESIGN.md) into numbered requirements with gates a program can check. It is read with the design, the evidence register ([`EVIDENCE.md`](EVIDENCE.md)) and the background pack ([`background/`](background/README.md)). Where they disagree, the order of authority is: this document, then the design, then the background pack.

Slices 0 and 1 are specified in full. Slices 2 to 11 have one row each and are written out when reached (section 6). That is deliberate: requirements bound what may be claimed as built; they are not written ahead of the build.

---

## 1. What is being built

**Plain.** A teaching repository that follows one casualty from injury to surgery and asks ten ways of reasoning the same two questions: what is wrong, and what should be done.

**Developer.** A Python package `inference_labs` (generator, belief type, ten lens modules, knowledge graph), twelve notebooks, a Streamlit app, and a harness that computes a verdict for each slice.

**Technical.** Each lens is an inference procedure behind one interface, compared on a common scorecard against a rule baseline, on seeded synthetic data with known generating parameters (mechanism) and, in notebooks only, on real trial data (evidence).

### Out of scope

- Any clinical use. Every notebook and app page carries the line "Teaching material. Not for clinical use."
- Retrieval-augmented generation and graph learning (described in notebook 11, built elsewhere).
- Real patient data in the app or in the repository. Real data are read from a local path outside the repository; continuous integration runs on fixtures.
- Any agent other than one builder and one sceptic.

---

## 2. Repository layout

```
inference-labs/
  CLAUDE.md                  standing rules; points every session to docs/BUILD.md
  manifest.yaml              single source of truth: slices, files, gates, parameters file, version
  params.yaml                every generator parameter with source (E-id or "assumption") and label
  pyproject.toml
  LEDGER.md                  one row per attempt, written by the validator
  src/inference_labs/
    generator.py             the causal graph, sampled forward
    belief.py                the RV type (D-19)
    interface.py             Lens protocol: diagnose, treat, scorecard
    baseline.py              MPTT-24 (stub in slice 0, coded in slice 2)
    graph/                   store, schema, provenance
    lenses/                  one module per lens
  harness/
    validate.py              computes BUILT, REVISE or BLOCKED
    gates/                   one module per gate
  tests/
    planted/                 one planted defect per gate
    fixtures/                small synthetic stand-ins for the real datasets
  notebooks/                 00 to 11
  app/                       Streamlit; no computation of its own
  reviews/                   the sceptic's record, one file per slice
  docs/                      design, evidence, background, explainers, this file
  library/curated.yaml
```

**Stack.** Python 3.11 or later; numpy, pandas, scipy, scikit-learn, matplotlib, pyyaml, streamlit, pytest, nbclient, nbformat. Anything further is added to `pyproject.toml` in the slice that first needs it and named in that slice's ledger row.

---

## 3. Gates

Every gate is a function in `harness/gates/` returning pass or fail with a reason. `python -m harness.validate --slice N` runs the gates listed for slice N in the manifest, writes `reviews/slice-N.verdict.json`, and appends one row to `LEDGER.md`. The validator writes the tally; no person or agent types it.

| Gate | Checks | Fails when |
|---|---|---|
| G-1 Manifest | Every file the manifest lists for the slice exists; no file under `src/`, `notebooks/` or `app/` is unlisted | A file is missing or unlisted |
| G-2 Tests | `pytest -q` | Any test fails or is skipped without a reason string |
| G-3 Determinism | The generator run twice with seed 42 gives byte-identical output | Hashes differ |
| G-4 Calibration | At n = 100,000 the generator reproduces each parameter in `params.yaml` within that parameter's stated tolerance. A parameter marked `emergent: true` is not set directly; it is measured on the generated cohort and must land within its stated tolerance. | Any parameter is outside tolerance |
| G-5 Provenance | Every parameter has a source and a label; every E-id resolves to a row in `EVIDENCE.md`; the generated assumptions register matches the committed one | An id does not resolve, a label is missing, or the register is stale |
| G-6 Labels | Every scorecard row is labelled `mechanism` or `evidence`; `evidence` appears only where the data source is a real-data path | A row is unlabelled or mislabelled |
| G-7 Notebook | The notebook runs top to bottom in under 5 minutes; holds the seven parts of the pattern in order (cell tags `hook`, `explainer`, `by-hand`, `case-dx`, `case-tx`, `failure`, `scorecard`, `analogy`); the explainer holds the three registers; every figure cell has a `concludes:` tag stating what the figure changes | A part or register is missing, a figure has no conclusion, or execution fails |
| G-8 Parity | Every number the app displays equals the library's value for the same inputs; `app/` imports no numerical library other than through `inference_labs` | A value differs or a forbidden import is present |
| G-9 Synthetic app | Nothing under `app/` reads outside the package and its bundled synthetic data | A real-data path is referenced |
| G-10 Evidence use | The notebook's `evidence:` list resolves; no entry with status NOT READ is quoted as a number; any CARRIED entry is shown with the word "provisional" | An unread source supplies a number, or a provisional one is unmarked |
| G-11 Sceptic | `reviews/slice-N.md` exists, was written after the last source change, and records a verdict against each line of "What must not be claimed" in the lens's background file plus the four epistemic checks in design section 9 | The file is missing, stale, or records a breach |
| G-12 Planted defects | For every gate above, a test in `tests/planted/` introduces one defect and asserts the gate fails | Any gate passes its own defect |
| G-13 Frozen generator | After slice 1 is BUILT, the hash of `generator.py` and `params.yaml` matches the manifest unless the manifest version has been bumped | The hash changed without a version bump |

**Verdict.** BUILT: every listed gate passes. REVISE: one or more gates fail and the builder may try again. BLOCKED: a gate cannot be evaluated, or an open item listed for the slice is unresolved. A REVISE or BLOCKED attempt is committed and recorded in the ledger like a BUILT one.

**Abstention.** The builder may stop and record "cannot be done as specified" with the reason. That is a legal outcome and is recorded as BLOCKED.

---

## 4. Slice 0 — foundations

| Id | Requirement | Gate |
|---|---|---|
| R-0.1 | `manifest.yaml` lists every slice, its files, its gates, its `approved` date and its blocking open items, and holds an `open_items` map recording each item as open, closed or waived with a reason | G-1 |
| R-0.2 | `params.yaml` holds every row of the parameter table in design section 5, each with `value`, `tolerance`, `source`, `label` and, where the source is CARRIED, `provisional: true` | G-5 |
| R-0.3 | `generator.sample(n, seed, mix, setting, return_truth=False)` samples the graph in design section 5 forward and returns a table of casualties. With `return_truth=True` it also returns the latent nodes | G-3, G-4 |
| R-0.4 | Patient types are haemorrhage (extremity, junctional, truncal), chest injury, head injury, and disease and non-battle injury. Mix and setting are arguments, not constants | G-4 |
| R-0.5 | The hazard of death from bleeding varies with time since injury and is fitted to the three measured points in E-85. A constant-hazard option exists only for the failure demonstration in lens 05 | G-4 |
| R-0.6 | Triage and scan accuracy are tables keyed by cohort and setting, never single numbers (D-13). The default cohort is the military registry row of E-09 | G-4, G-5 |
| R-0.7 | `belief.RV` implements the type in `docs/explainers/belief-as-a-random-variable.md`: draws, arithmetic that preserves pairing of draws, `mean`, `interval`, `prob` | G-2 |
| R-0.8 | `interface.Lens` defines `diagnose(casualty)`, `treat(casualty)` and `scorecard()`. `scorecard()` returns rows with a fixed schema including `label` and `fit` (native or weak) | G-2, G-6 |
| R-0.9 | The graph store holds typed nodes and edges. Every edge carries `label` (doctrine, trial evidence, registry evidence, assumption), `source`, `version`, `valid_from` and `population` | G-2 |
| R-0.10 | Every parameter in `params.yaml` is a node in the provenance graph, and `docs/ASSUMPTIONS.md` is generated from it | G-5 |
| R-0.11 | `tests/fixtures/` holds synthetic stand-ins with the column names of the CRASH-2 and CRASH-3 files, generated by a script, with no real records | G-9 |
| R-0.12 | The validator and gates G-1 to G-6, G-12 and G-13 exist, and each has a planted-defect test | G-12 |
| R-0.13 | `baseline.py` exposes the MPTT-24 behind the Lens interface as a stub that raises `NotImplementedError("O-1")` | G-2 |
| R-0.14 | Heart rate, respiratory rate, conscious level, systolic pressure, walking and catastrophic haemorrhage are each drawn from the casualty's latent state. No triage priority is drawn or used anywhere in the generator; rules are applied to the generated signs afterwards | G-2, G-4 |
| R-0.15 | The signs carry information beyond the rule: on 100,000 casualties, a logistic regression of need for intervention on the four signs has an area under the curve at least 0.03 above that of the MPTT-24 priority, and within each MPTT-24 priority the same regression still separates need from no need with an area under the curve above 0.55 | G-2, G-12 |

**Done when:** `python -m harness.validate --slice 0` writes BUILT.
**Gates run:** G-1 to G-6, G-12.
**Blocked by:** nothing.

---

## 5. Slice 1 — lens 03, Bayesian

The thinnest slice that proves library, notebook and app together. Background: [`background/03-bayesian.md`](background/03-bayesian.md).

| Id | Requirement | Gate |
|---|---|---|
| R-1.1 | `lenses/bayesian.py` implements the Lens interface. `diagnose` returns the belief that the casualty is bleeding as an `RV` | G-2 |
| R-1.2 | The belief line: prior from the mix, update on triage, update on the scan, carried unchanged to treatment and evacuation. Each step is a function that takes and returns an `RV` | G-2 |
| R-1.3 | With seed 42, prior 0.20, sensitivity Beta(21, 63) and specificity Beta(257, 9) taken from the counts in E-16, 4,000 draws, the belief after a positive pre-hospital scan is 65% (48 to 82%) and the probability it exceeds one half is 96%. With in-hospital accuracy, drawn as Beta(74, 26) and Beta(294, 6) and marked as an assumption because E-14 is pooled, it is 90% (83 to 96%). Tolerance one percentage point | G-2 |
| R-1.4 | The treatment case re-reads a trial with a prior: given a likelihood summary and a prior, return the posterior for the relative risk and the probability of benefit. Run on the fixture, and on real data only if a local path is supplied | G-2, G-6 |
| R-1.5 | The failure case: a prior taken from the wrong population (in-hospital accuracy applied before hospital) and the belief it produces, shown beside the correct one | G-7 |
| R-1.6 | The shuffled-draws failure from the explainer is reproduced as a test: sorting or resampling one of two paired quantities changes the answer | G-2 |
| R-1.7 | Notebook `03_bayesian.ipynb` follows the seven-part pattern, with the hook, by-hand case, two worked cases and failure taken from the background file | G-7, G-10 |
| R-1.8 | The scorecard compares the lens with the baseline on the generator. While the baseline is a stub, the baseline row reads "pending slice 2" and the gate accepts that string only until slice 2 is BUILT | G-6 |
| R-1.9 | App page 1 shows the casualty walk-through with one panel (Bayesian) and the belief line drawn as a band. Patient type, setting and prior are controls | G-8, G-9 |
| R-1.10 | Every scan accuracy figure shown carries the word "provisional" until O-6 is closed | G-10 |
| R-1.11 | The sceptic's review is recorded | G-11 |
| R-1.12 | The generator and parameters are frozen at the end of this slice and their hash written to the manifest | G-13 |

**Done when:** `python -m harness.validate --slice 1` writes BUILT.
**Gates run:** all.
**Blocked by:** O-6 for the scan accuracy rows (E-14 to E-16). Those rows were read in full and confirmed on 12 November 2026, so O-6 is to be marked closed in the manifest before this slice starts. Were it still open, the slice could be built with those rows marked provisional and the verdict would be BLOCKED, not BUILT, until it was closed or waived. The review is not held up by O-6: it goes ahead once every gate other than G-11 passes.

---

## 6. Slices 2 to 11

One row each. Before a slice starts, its row is expanded into a requirements table in the style of section 5, appended to this document as section 6.N, and the manifest updated. The expansion is done by the builder from the design and the background file, and approved by Ross before any code is written.

| Slice | Lens | Background file | Must demonstrate | Blocked by |
|---|---|---|---|---|
| 2 | 01 Rules | `01-rules.md` | MPTT-24 coded from the published flowchart; transfusion score; the needle-length failure; replaces the baseline stub | O-1 |
| 3 | 02 Frequentist | `02-frequentist.md` | Accuracy tables by cohort; protocol against practice; one trial read as a P value | — |
| 4 | 04 Decision trees | `04-decision-trees.md` | A single tree against a forest; instability under resampling | — |
| 5 | 10 Decision theory | `10-decision-theory.md` | Threshold from stated costs; net benefit; two casualties and one aircraft | — |
| 6 | 05 Stochastic | `05-stochastic.md` | Time-varying hazard against measured points; constant-hazard failure; decay of benefit | — |
| 7 | 07 Causal | `07-causal.md` | Observational against randomised estimate on the generator; survival bias reproduced and removed | O-2 for any real-data cell |
| 8 | 08 Knowledge graph | `08-knowledge-graph.md` | Capability chain traversal; provenance query; a stale dosing edge returned and then caught | O-3 |
| 9 | 09 Reinforcement learning | `09-reinforcement-learning.md` | Policy learned on the benchmark; do-nothing policy winning under naive off-policy evaluation; true value revealed | — |
| 10 | 06 Connectionist | `06-connectionist.md` | Method on a proxy image set, labelled as such; a shortcut feature learned and exposed | — |
| 11 | Notebooks 00 and 11; app pages 2 to 4; lens pages and gallery | `00-casualty-thread.md`, `11-hybrids.md` | Conformal prediction on the baseline and the tree; the lens table generated from scorecards | At least five lenses BUILT |

### 6.2 Slice 2 — lens 01, Rules

The rule every later lens is compared against (D-9). Background: [`background/01-rules.md`](background/01-rules.md).

| Id | Requirement | Gate |
|---|---|---|
| R-2.1 | `baseline.py` replaces the stub with the MPTT-24 coded as the six steps of E-08, in E-08's order and with E-08's thresholds and no others: catastrophic haemorrhage, yes gives Priority 1; walking, yes gives Priority 3; breathing, no gives Dead; responds to voice (R-2.2); respiratory rate 12 to 23, no gives Priority 1; heart rate below 100, yes gives Priority 2 and no gives Priority 1. It returns the priority and the step at which the casualty left. The generator records no breathing check, so its casualties are taken as breathing, and that is stated as an assumption | G-2 |
| R-2.2 | The voice step has a switch. `figure`, the default, reads the published figure: only a casualty who does not respond to voice leaves for Priority 1. `text` reads the paper's text: anything below alert leaves for Priority 1. The notebook counts the casualties whose priority differs between the two readings on the generator's military cohort (n = 100,000, seed 42) | G-2, G-7 |
| R-2.3 | A calibration check on the generator, not evidence about the rule: on the military cohort at n = 100,000, seed 42, the coded rule under the `text` reading, the one that matches the GCS below 14 on which E-09 was measured, reproduces E-09's sensitivity and specificity within the tolerances in `params.yaml`. The `figure` reading's figures are shown beside them and are not held to E-09 | G-2 |
| R-2.4 | Notebook `01_rules.ipynb` follows the seven-part pattern and opens on the background file's hook: guidance recommended a needle of about 5 cm; in 100 soldiers the mean chest wall was 5.36 cm (E-104); what happened in the field? The reader guesses before the answer is given | G-7, G-10 |
| R-2.5 | By hand: ten synthetic casualties from the generator are run through the MPTT-24 on paper, then in plain Python, then through the library, which must agree with the hand count | G-7 |
| R-2.6 | Central figure: the sieve. Synthetic casualties drop through the six steps into the priority bins, shaded by whether they need a life-saving intervention, with the reading and the cohort as controls. Marked central | G-7 |
| R-2.7 | Diagnosis case: MPTT-24 priority on the generator's casualties, with the Military Sieve beside it as E-10's published operating point and the MPTT-24's own as E-09's, both in the military registry: the newer rule finds more of those who need intervention and wrongly flags more of those who do not. The Sieve is not coded, because the register holds its performance and not its algorithm. Every published figure is said to come from first hospital observations (E-11) | G-7, G-10 |
| R-2.8 | Treatment case: `lenses/rules.py` codes the ABC score (E-31) as a second rule, four unweighted items with a score of 2 or more activating transfusion, and runs it on the generator's battle casualties in both settings. Beside it: the four-item doctrine rule (E-86), of which only the two bedside items can be read at the point of injury, and tranexamic acid inside or outside three hours (E-86, from E-22). Which mechanisms count as penetrating, and significant bleeding as the stand-in for massive transfusion, are assumptions and are stated where used | G-2, G-7, G-10 |
| R-2.9 | Failure: a rule meeting a population it was not written for. The needle rule is produced from E-104's mean and standard deviation under an assumed normal shape, checked against E-104's 99% for an 8 cm catheter, and set beside the field record (E-106). With it, from the background file: the MPTT-24 in the civilian registry (E-09), with its two predictive values reproduced from the two prevalences, and the ABC score's fall (E-31 against E-90) | G-2, G-7, G-10 |
| R-2.10 | The lens's scorecard reports the seven axes of D-21. Axes 1, 2 and 6 are computed on the generator for the MPTT-24 (diagnosis) and the ABC score (treatment) and carry the mechanism label; axes 3, 4 and 5 are stated; axis 7 reads pending until lens 10. Fit is native for both cases | G-6, G-7 |
| R-2.11 | The Bayesian scorecard's "pending slice 2" baselines are replaced by the MPTT-24 under its default reading, scored on the same casualties against the same target. The treatment row, for which the rule states no probability, holds NaN and the notebook says why. `03_bayesian.ipynb` is re-executed | G-6, G-7 |
| R-2.12 | App page 1 gains the rules panel beside the Bayesian one for the selected casualty: the MPTT-24's steps and priority under both readings, the ABC score and its items, and the three-hour rule for tranexamic acid. Every number comes from the library and carries a label; a published figure carries its evidence id and population | G-8, G-9, G-10 |

**Done when:** `python -m harness.validate --slice 2` writes BUILT.
**Gates run:** all. The sceptic's review is checked by G-11.
**Blocked by:** O-1, closed 12 November 2026.


### 6.3 Slice 3 — lens 02, Frequentist and signal detection

Every test and every trial reports error rates under repetition. Background: [`background/02-frequentist.md`](background/02-frequentist.md).

| Id | Requirement | Gate |
|---|---|---|
| R-3.1 | `lenses/frequentist.py` implements the Lens interface. `diagnose` returns a logistic score's probability that the casualty needs a life-saving intervention, fitted on the four signs the MPTT-24 reads (walking, conscious level, respiratory rate and heart rate) on a generator sample separate from the casualties it is scored on. Its operating threshold is where its specificity on the training sample equals the MPTT-24's under the figure reading. Real trial data are not used while O-2 is open: the treatment row runs on the CRASH-2 fixture and is labelled as a fixture | G-2, G-6 |
| R-3.2 | Notebook `02_frequentist.ipynb` follows the seven-part pattern and opens on the background file's hook: 680 bleeding patients, 12.7% died with one transfusion ratio and 17.0% with the other, and the paper reports no significant difference (E-72). Does the ratio matter? The reader guesses before the answer is given | G-7, G-10 |
| R-3.3 | By hand: a hundred synthetic casualties sorted into hits, misses, false alarms and correct rejections for the MPTT-24, counted on paper, in plain Python and by the library, which must agree; then the Military Sieve's published operating point (E-10) applied to the same hundred as expected counts, because the Sieve is not coded | G-7 |
| R-3.4 | Central figure: two hills and a sliding line. The score's distribution in those who need an intervention and those who do not, a movable threshold with the four outcomes shaded, and the receiver operating curve beside it with the threshold's point. The threshold is a control. Marked central | G-7 |
| R-3.5 | Sensitivity and specificity with 95% intervals, by cohort and setting, for the baseline under both readings (D-24) and for the logistic score, on the generator (mechanism). Wherever the rule's accuracy on the generator is quoted, D-23's statement goes with it | G-2, G-7 |
| R-3.6 | The receiver operating curve for the score, with the MPTT-24's points on the generator and the published points of the MPTT-24 (E-09) and the earlier MPTT (E-03, E-05, E-07), each labelled by source and cohort | G-7, G-10 |
| R-3.7 | Diagnosis case, from the background file: the accuracy of one rule across cohorts (E-03, E-05, E-07, E-09) produced as a table before any one figure is quoted (E-13); protocol against practice (E-88) as two points in the study's own terms; the scan in two settings (E-14, E-16). Over-triage is never equated with 1 minus specificity (E-12) | G-7, G-10 |
| R-3.8 | Sampling variability: repeated samples of 357 casualties from the generator, the size of the prospective cohort in E-07, showing how far one cohort's estimate can sit from the long-run value. The notebook says this illustrates sample size on synthetic data and does not explain E-07 | G-2, G-7 |
| R-3.9 | Treatment case: PROPPR (E-72) read as a test and an interval, beside CRASH-2 (E-19 to E-21) and RePHILL (E-77). An interval is recomputed by hand only where the register holds the counts needed, otherwise quoted. The asymmetric significance thresholds of E-79 are shown as evidence that the line is chosen | G-2, G-7, G-10 |
| R-3.10 | CRASH-2's time subgroups against its prespecified heterogeneity threshold (E-20), then the later exploratory time result (E-22, E-23) and the check on rival explanations (E-124) as the sequel | G-7, G-10 |
| R-3.11 | Failure, from the background file: one accuracy figure quoted for the wrong setting, and a non-significant result read as no effect | G-7, G-10 |
| R-3.12 | The lens's scorecard reports the seven axes of D-21, with the baseline under the figure reading and the text reading beside it, labelled as validated (D-24). App page 1 gains the frequentist panel for the selected casualty; every number comes from the library and carries a label | G-6, G-7, G-8, G-9 |

**Done when:** `python -m harness.validate --slice 3` writes BUILT.
**Gates run:** all. The sceptic's review is checked by G-11.
**Blocked by:** nothing. O-2 stays open; no real trial data are read.


### 6.4 Slice 4 — lens 04, Decision trees

A tree is a rule the data wrote; one tree is readable and fragile, many are strong and opaque. Background: [`background/04-decision-trees.md`](background/04-decision-trees.md).

| Id | Requirement | Gate |
|---|---|---|
| R-4.1 | `lenses/trees.py` implements the Lens interface. A single tree of depth three and a random forest predict need for a life-saving intervention from the same four of the MPTT-24's signs as lens 02's score (walking, conscious level, respiratory rate, heart rate), fitted on the same training sample and scored on the evaluation sample. `diagnose` returns the forest's probability with the single tree's leaf and the path to it | G-2, G-6 |
| R-4.2 | Notebook `04_decision_trees.ipynb` follows the seven-part pattern and opens on the background file's hook: ten model families were set against a transfusion score on the same patients (E-90). Which fell short? The reader guesses before the answer is given | G-7, G-10 |
| R-4.3 | By hand: twenty synthetic casualties on paper, and the single question that splits them best found by counting, then in plain Python, then by the library's tree of depth one, which must agree | G-7 |
| R-4.4 | Central figure: the carving. Synthetic casualties as a scatter of two signs, cut into rectangles one split at a time, with the depth as a control. Marked central | G-7 |
| R-4.5 | Diagnosis case: the single tree and the forest scored against the baseline under both readings (D-24) and against lens 02's logistic score, on the generator (mechanism): area under the curve, sensitivity and specificity at the baseline's specificity, Brier score and calibration. The single tree is printed in a form a reader can follow. D-23's statement goes with the rule's accuracy | G-2, G-7 |
| R-4.6 | A fast-and-frugal tree on three cues with two exit orders, showing its sensitivity and specificity move with the exits (E-59) | G-2, G-7, G-10 |
| R-4.7 | The U-shaped relation to respiratory rate (E-30): a tree finds the raised need at both ends and a single linear term does not. The generator's respiratory rate is two-sided by assumption, and the notebook says so | G-2, G-7, G-10 |
| R-4.8 | The published comparison: in E-90 every model family except the single decision tree and the support vector machine reached an area under the curve above 0.75, and in E-91 the random forest's pooled area was the highest reported; set against the argument for readable models (E-118). Both are presented and neither is adjudicated. Three variables against six (E-30) and a rule validated on a large cohort (E-89) are set beside them | G-7, G-10 |
| R-4.9 | Treatment case, from the background file: who gets blood first. A tree on the ABC score's bedside items against the ABC score and the doctrine rule from lens 01, on the generator's battle casualties in both settings, with significant bleeding as the stand-in for transfusion, an assumption stated where used | G-2, G-7 |
| R-4.10 | Failure, from the background file: the same small sample resampled twenty times gives twenty trees, and the splits that survive are counted; and a variable recorded after the decision, constructed in the notebook and said to be constructed, lifts the tree's apparent accuracy | G-2, G-7 |
| R-4.11 | The lens's scorecard reports the seven axes of D-21 for the single tree, the forest and the treatment tree, with the baseline under the figure reading and the text reading beside it, labelled as validated (D-24) | G-6, G-7 |
| R-4.12 | App page 1 gains the trees panel for the selected casualty: the single tree's path and leaf, the forest's probability, and the treatment tree beside the ABC score. Every number comes from the library and carries a label | G-8, G-9 |

**Done when:** `python -m harness.validate --slice 4` writes BUILT.
**Gates run:** all. The sceptic's review is checked by G-11.
**Blocked by:** nothing. CRASH-2 and DDXPlus data are not read; O-2 stays open.

---

## 7. Build plan

| Step | Who | Action | Output | Gate to pass |
|---|---|---|---|---|
| 1 | Ross | Create the repository and commit the `docs/` and `library/` folders | Repository with design, evidence, background, PRD | — |
| 2 | Builder | Slice 0 | Manifest, parameters, generator, belief type, interface, graph store, harness | G-1 to G-6, G-12 |
| 3 | Ross | Read the slice 0 ledger row; spot-check the calibration table | Go or revise | — |
| 4 | Ross | Close O-6. Done 12 November 2026: both source papers read in full and the figures confirmed. Remaining action: mark O-6 closed in the manifest | `EVIDENCE.md` rows E-14 to E-16 at READ | — |
| 5 | Builder | Slice 1 | Bayesian lens, notebook 03, app page 1 | All |
| 6 | Sceptic | Review slice 1 in a fresh context | `reviews/slice-1.md` | G-11 |
| 7 | Ross | Run the notebook and the app; decide whether the pattern is right before repeating it nine times | Go, or change the pattern once here | — |
| 8 | Ross | Close O-1: confirm the MPTT-24 flowchart. Done 12 November 2026; the algorithm is recorded in E-08 | Note in `EVIDENCE.md` | — |
| 9 | Builder, sceptic | Slices 2 to 10, one at a time: expand the row, approve, build, review | One lens each | All |
| 10 | Builder, sceptic | Slice 11 | Notebooks 00 and 11, app pages 2 to 4 | All |

**Rules of the build.**

1. One slice at a time. The next slice does not start until the current one is BUILT or explicitly parked by Ross.
2. The builder builds. The sceptic reviews what was built and may only narrow what is claimed. Neither creates work for a later slice.
3. Step 7 is the only planned point at which the pattern changes. A change after that is a manifest version bump.
4. If a gate proves wrong, the gate is fixed with its planted-defect test in the same commit, and the ledger says so.

---

## 8. How the build is run

The build is run from [`BUILD.md`](BUILD.md), not from prompts. `CLAUDE.md` at the repository root points every session to it. Ross types one of four words, `build`, `review`, `status` or `unstick`; the session reads the manifest and ledger, works out the state of the build, carries out the single next action and stops.

---

## 9. Open items carried into the build

| Item | What Ross does | Blocks |
|---|---|---|
| O-6 | Confirmed on 12 November 2026 for E-14 to E-16. Mark it closed in the manifest once slice 0 has created it | Slice 1 verdict, until marked |
| O-1 | Closed 12 November 2026. The algorithm is in E-08, with one ambiguity between text and figure for the builder to expose as a switch | Nothing |
| O-2 | Read the freeBIRD data sharing terms; register if content | Real-data cells only |
| O-3 | Confirm the current edition of AJP-4.10 | Slice 8 |
| O-9 | Read the papers behind E-76, E-79, E-81 | Nothing; tidy before publication |
