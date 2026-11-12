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
| G-4 Calibration | At n = 100,000 the generator reproduces each parameter in `params.yaml` within that parameter's stated tolerance | Any parameter is outside tolerance |
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
| 8 | Ross | Close O-1: confirm the MPTT-24 flowchart | Note in `EVIDENCE.md` | — |
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
| O-1 | Open Figure 2 of `vassallo2017d`; confirm step order and the heart rate comparison | Slice 2 |
| O-2 | Read the freeBIRD data sharing terms; register if content | Real-data cells only |
| O-3 | Confirm the current edition of AJP-4.10 | Slice 8 |
| O-9 | Read the papers behind E-76, E-79, E-81 | Nothing; tidy before publication |
