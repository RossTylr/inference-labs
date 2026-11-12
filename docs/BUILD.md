# Build instruction

**Status:** v1.0 · **Date:** 12 November 2026 · **Author:** Ross Taylor

This is the procedure for building inference-labs. It replaces per-slice prompts: the state of the build is read from the repository, and the next action follows from the state. Requirements and gates are in [`PRD.md`](PRD.md).

There are four commands. Ross types one word; the session does one action and stops.

| Command | Seat | Does |
|---|---|---|
| `build` | Builder | Works out the next action from the state table and carries it out |
| `review` | Sceptic | Reviews the slice awaiting review. Must be a new session |
| `status` | Either | Reports the state and the next action. Changes nothing |
| `unstick` | Either | Diagnoses a slice stuck at REVISE. Changes nothing |

---

## 1. Work out the state

Read `manifest.yaml` and the last rows of `LEDGER.md`. Take the lowest-numbered slice that is not `BUILT` and find its row below.

| # | State of that slice | How to tell | Next action | Seat |
|---|---|---|---|---|
| S-1 | Nothing built | No `manifest.yaml` | Build slice 0 (section 2) | Builder |
| S-2 | Not yet specified | No section 6.N in `PRD.md` for the slice | Expand the row (section 3), then stop for approval | Builder |
| S-3 | Specified, not approved | Section 6.N exists; manifest has no `approved` date for the slice | Stop. Show the table again and ask Ross to approve | Builder |
| S-4 | Approved, open item unresolved | An item in the slice's `blocked_by` is not marked closed or waived in the manifest | Build with provisional marking if the PRD allows it for that item; otherwise stop and name the item | Builder |
| S-5 | Approved, ready | Approved, nothing blocking, no BUILT row | Build the slice (section 4) | Builder |
| S-6 | Built, awaiting review | All gates pass except G-11 | Stop. Tell Ross to open a new session and type `review` | — |
| S-7 | Review found a breach | `reviews/slice-N.md` ends `VERDICT: BREACH` | Fix only the lines marked BREACH, re-run the validator, return to S-6 | Builder |
| S-8 | Revise limit reached | Three consecutive REVISE rows for the slice | Stop. Tell Ross to type `unstick` | — |
| S-9 | All slices built | Slice 11 is `BUILT` | Report completion. Do nothing else | — |

Slices 0 and 1 are already specified in the PRD and count as approved. State S-2 first applies at slice 2.

Before acting, say in one line which state was found and which action follows.

---

## 2. Build slice 0

1. Read `PRD.md` sections 2 to 4; `DESIGN.md` sections 2, 5, 6 and 9; `explainers/belief-as-a-random-variable.md`; and the `EVIDENCE.md` rows named in design section 5.
2. Write `manifest.yaml` and `params.yaml` first.
3. Write each gate and its planted-defect test before the code that gate checks.
4. Build requirements R-0.1 to R-0.13. No lens, notebook or app page.
5. Run `python -m harness.validate --slice 0`. Commit whatever the verdict.
6. On REVISE, fix and run again. Three attempts at most.
7. Report (section 7).

---

## 3. Expand a slice's row

1. Read the slice's row in `PRD.md` section 6, its background file, and `DESIGN.md` sections 4, 7 and 12.
2. Write a requirements table in the style of PRD section 5: ids R-N.1 onward, one requirement per row, each naming the gate that checks it. Twelve rows at most.
3. The hook, by-hand case, two worked cases and failure are taken from the background file's "Use in the notebook" table. Each becomes a requirement.
4. Append the table to `PRD.md` as section 6.N. Add the slice's files and gates to `manifest.yaml`, without an `approved` date.
5. Write no code. Show Ross the table and stop.

When Ross replies "approved", write today's date to the slice's `approved` field in the manifest and commit. If he asks for changes, make them and show the table again.

---

## 4. Build a lens slice

1. Read `PRD.md` section 3 and the slice's section; the background file; the `EVIDENCE.md` rows it cites; and `notebooks/03_bayesian.ipynb` as the pattern once it exists.
2. Build the library module, then its tests, then the notebook, then the app panel, in that order.
3. Follow the seven-part notebook pattern and the cell tags in gate G-7.
4. Do not change `generator.py` or `params.yaml`.
5. Run `python -m harness.validate --slice N`. Commit whatever the verdict.
6. On REVISE, fix and run again. Three attempts at most.
7. Report (section 7). The expected verdict at this point is REVISE with only G-11 failing, which is state S-6.

---

## 5. Review

The sceptic did not build the slice. If this session wrote any of the slice's code, stop and tell Ross to open a new session.

1. Read `PRD.md` section 3 and the slice's section, and the background file. Then read the notebook, library module and app panel. Run the notebook.
2. Write `reviews/slice-N.md`, one line per check, each marked HOLDS or BREACH with the cell or line number:
   - each line under "What must not be claimed" in the background file;
   - accuracy quoted for the wrong cohort or setting;
   - proxy data read as the real thing;
   - civilian data read as military;
   - a diagnosis result read as a treatment result;
   - each number traced to an evidence id, and the id says what the notebook says;
   - each figure: does it change what a reader would conclude.
3. End the file with `VERDICT: HOLDS` or `VERDICT: BREACH`.
4. Run `python -m harness.validate --slice N` and commit.

The sceptic does not edit the notebook, library or app, and does not propose features or later work. Its job is to narrow what may be claimed.

---

## 6. Unstick

1. Read `reviews/slice-N.verdict.json` and the last three ledger rows.
2. Change nothing.
3. Tell Ross in under 150 words: which gate fails; whether the fault lies in the code, the requirement or the gate; and the smallest change that would resolve it.

If the gate itself is wrong, the fix changes the gate and its planted-defect test in one commit, and the ledger row says so.

---

## 7. Report

Under 200 words, in this order:

1. State found and action taken.
2. Verdict and gate tally, copied from the validator's output.
3. For slice 0: the calibration table (parameter, target, achieved, tolerance). For a lens: the scorecard.
4. Anything assumed.
5. The next state, and who acts.

---

## 8. What Ross does

| When | Action |
|---|---|
| Once, before anything | Create the repository; commit `CLAUDE.md`, `docs/` and `library/` |
| To move the build on | Open a session at the repository root and type `build` |
| After slice 0 is BUILT | Spot-check the calibration table in the report |
| Before slice 1 can be BUILT | Close O-6: confirm E-14 to E-16 against the two source papers, update `EVIDENCE.md`, and mark O-6 closed in the manifest (or record a waiver there) |
| When told a slice awaits review | Open a new session and type `review` |
| After slice 1 is BUILT | Run the notebook and the app. If the pattern needs changing, change it now |
| Before slice 2 | Close O-1: confirm the MPTT-24 flowchart |
| When shown a requirements table | Reply "approved", or say what to change |
| Before slice 8 | Close O-3: confirm the current edition of AJP-4.10 |
| Before any real-data cell | Close O-2: read the freeBIRD terms |

Closing an open item means editing the manifest: `open_items: {O-6: closed}` or `{O-6: waived, reason: "..."}`. The validator reads it from there.
