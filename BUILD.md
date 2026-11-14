# Build instruction

**Status:** v2.0 · **Date:** 14 November 2026 · **Author:** Ross Taylor

This is the whole procedure for building inference-labs. The state of the build is read from the repository and the next action follows from it. Requirements, gates and each slice's mandatory items are in [`PRD.md`](PRD.md). Nothing is carried in prompts: if an instruction is not in this file, the PRD or `CLAUDE.md`, it does not apply.

Version 2 changes four things learnt from slices 0 to 5: one session builds one slice; a review goes stale only when what a reader sees has changed; changes that cross lenses are batched; and the standing rules live here, not in pasted prompts.

| Command | Does |
|---|---|
| `build` | Works out the state, carries out one unit of work from the table below, pushes and stops |
| `review` | Reviews one slice by hand, in a session that did not build it. Rarely needed: `build` starts its own reviewer |
| `status` | Reports the state and the next action. Changes nothing |
| `unstick` | Diagnoses a slice that cannot reach BUILT. Changes nothing |

---

## 1. One session, one unit

A session does one unit of work and stops. A unit is one slice taken from requirements to BUILT and pushed, or one consolidation pass (section 7). Ross then opens a new session and types `build` again.

This is a cost rule, not a courtesy. A session that carries several slices re-reads all of them on every turn. If a session is interrupted, the next one picks up from the ledger and the commit history; nothing depends on memory of the earlier session.

---

## 2. Work out the state

Read `manifest.yaml` and the last rows of `LEDGER.md`. Take the first row below that applies. Say in one line which state was found and which action follows.

| # | State | How to tell | Action |
|---|---|---|---|
| S-1 | A built slice's review is stale | A slice at BUILT now fails only G-11 | Re-review that slice (section 5). One slice per session, lowest number first |
| S-2 | Consolidation is due | The manifest's `deferred` list is not empty and the last BUILT slice is 8, or slice 11 is next | Run a consolidation pass (section 7) |
| S-3 | Next slice not specified | No section 6.N in `PRD.md` for the lowest slice not BUILT | Write its requirements (section 3), then continue to S-5 in the same session |
| S-4 | Next slice blocked | An item in its `blocked_by` is neither closed nor waived | Stop and name the item |
| S-5 | Next slice ready | Requirements written and approved, nothing blocking | Build it to BUILT (sections 4 to 6) |
| S-6 | Slice part-built | Commits for the slice exist and it is not BUILT | Resume at the first phase not yet committed |
| S-7 | Stopped on a breach | The slice's third review ends `VERDICT: BREACH` | Stop. Report the breach in full. Ross decides |
| S-8 | All built | Slice 11 is BUILT and `deferred` is empty | Report completion |

---

## 3. Requirements

1. Read the slice's row and its mandatory items in `PRD.md` section 6, its background file, and `DESIGN.md` sections 4, 7 and 12.
2. Write the table as `PRD.md` section 6.N: ids R-N.1 onward, one requirement per row, each naming its gate. Twelve rows at most.
3. The hook, by-hand case, diagnosis case, treatment case, failure and central figure come from the background file's "Use in the notebook" table, one requirement each. Draw also on "Added from the full text".
4. Every mandatory item is a requirement.
5. The scorecard reports the seven axes (D-21), both baseline readings (D-24) and axis 7 at the common threshold (D-26). An axis that does not apply is answered in words.
6. Add the slice's files, its `review_sources` (section 5) and its gates to `manifest.yaml`.

**Approval.** The table is approved in advance when rules 2 to 6 are met; write today's date as `approved` and go on. If a rule cannot be met, stop and show Ross the table.

Commit as "Slice N: requirements".

---

## 4. Build

Order: library module, tests, notebook, app panel.

- The lens adds one panel file under `app/panels/` and changes no other slice's files (D-27). If the work seems to need a change to another slice, do not make it: add one line to the manifest's `deferred` list and carry on (section 7).
- Do not change `generator.py` or `params.yaml`. If the slice seems to need it, stop and report.
- Follow the seven-part notebook pattern and the cell tags in gate G-7.
- Apply the standing lessons (section 8).
- Run `python -m harness.validate --slice N`. Fix any gate other than G-11, three attempts at most. If a gate other than G-11 still fails, stop and report.

**The sweep.** Before any review, check your own work:

1. List every sentence that cites an evidence id, attributes a statement to a source, or describes the generator or the graph. Check each against its register row or the code, and cut it back to what is supported. Add no claim in its place.
2. For each computed quantity, ask whether it uses information the casualty or the clinician would not yet have, and whether it is conditioned on the right population. Fix errors in the code, not the wording.
3. Leave no checklist or document behind.

Commit the build and the sweep as "Slice N: build".

---

## 5. Review

The reviewer did not build the slice. `build` starts a subagent with a fresh context and gives it only the instruction below.

**What is reviewed.** Each slice's `review_sources` in the manifest: its notebook, its lens module and its app panel. Nothing else. Harness code, tests, the app's entry file and other slices' files are not review sources.

**When a review is stale.** The review file ends with a block listing each review source and a content hash. Gate G-11 recomputes the hashes and fails only if one differs. For a notebook the hash covers cell sources and text outputs, not execution counts, timings, metadata or image bytes. Re-running a notebook without changing what a reader sees does not make a review stale.

**Instruction given to the reviewer:**

> You are the sceptic for slice N of the repository in the current directory. You did not build it. Read `docs/PRD.md` section 3 and the slice's section, the slice's background file, and the standing lessons in `docs/BUILD.md` section 8. Then read the slice's review sources and run the notebook.
>
> Write `reviews/slice-N.md`, one line per check, each marked HOLDS or BREACH with the cell or line:
> each line under "What must not be claimed" in the background file; accuracy quoted for the wrong cohort or setting; proxy data read as the real thing; civilian data read as military; a diagnosis result read as a treatment result; each number traced to an evidence id that says what the notebook says; each sentence about the generator or graph against the code; each figure, whether it changes what a reader would conclude.
>
> Be exhaustive in one pass: every cell, every string the lens module can return, every element of the panel, against every item. Mark as MISSED any breach in lines unchanged since the previous review. Under a heading "Limits", list anything worth recording that is not a breach. End with `VERDICT: HOLDS` or `VERDICT: BREACH`, then the hash block. Edit nothing else. Propose no features and no later work.

**After the review.**

- HOLDS: go to section 6.
- BREACH: fix only the lines marked, re-run the validator, and start a new reviewer. Three rounds at most (D-25). After a third BREACH, stop (state S-7).
- Limits: copy each to the manifest's `deferred` list, one line each. Do not fix them now.
- Never edit a review file. If a finding looks wrong, stop and say why.

---

## 6. Close

1. Run the validator for the slice. It must read BUILT.
2. Confirm no other slice's review sources changed. If one did, say which and why; it will be re-reviewed under S-1 in a later session.
3. One commit, "Slice N: close", holding the review, ledger and verdict files. The ledger records every validator run; the commit history does not need to.
4. `git push origin main`.
5. Report (section 9) and stop.

---

## 7. Consolidation

A change that touches more than one lens is never made inside a lens slice. It is added to the manifest's `deferred` list and done in a consolidation pass, which runs at two planned points: after slice 8, and before slice 11.

A pass does every deferred item, re-executes the notebooks affected, runs the sweep on the changed lines, validates every slice, and commits as "Consolidation after slice N". It then pushes and stops. The reviews it made stale are redone one slice per session under S-1.

Ross may ask for a pass at any other time by typing `build consolidate`.

---

## 8. Standing lessons

Each of these cost a review round before it was written down.

1. Where a trial or registry figure is applied to the casualty, name the source, its id and its population in the same cell or panel. A civilian source applied to a military casualty is an assumption and is called one. Gate G-10 checks the word "civilian" mechanically.
2. State the group a result belongs to. Quote a population as the register gives it: "deaths judged potentially survivable" is not "deaths".
3. Every number on the app says what it is and comes from the library. No relative figure without the absolute beside it.
4. Harm, or a negative result, is stated in words, not left as a sign.
5. A result driven by a prior or an assumption says so where it is shown.
6. A figure title describes what is plotted, not a conclusion.
7. Diagnosis and treatment results sit in separate, labelled cells.
8. Performance measured on hospital observations is never called performance at the point of injury.
9. Counts are exact: "52 of the 75 studies".
10. A sentence about the generator or the graph is checked against the code.
11. Do not say where a rule's items came from, what a source omits or forbids, or why something was chosen, unless the register row says so.
12. A difference smaller than its spread across seeds is a tie and is called one. Report the spread across at least 20 seeds.
13. A chance of death is conditional on being alive when the decision is made.
14. Probabilities and thresholds are compared at full precision and displayed alike.
15. A result that reverses in a subgroup is shown with that subgroup.
16. The generator's injured cohort is milder than the registry the rule was validated on (D-23). Say so wherever the rule's accuracy on the generator is quoted.
17. A learned model that does no better than the baseline is a finding. Report it; do not tune until it wins.

---

## 9. Report

Under 200 words:

1. State found and unit of work done.
2. Verdict and tally, copied from the validator.
3. The scorecard, or for a consolidation pass the items done.
4. The one result a reader should remember, in a sentence.
5. Review rounds used, and each breach.
6. Anything assumed, and anything added to `deferred`.
7. The pushed commit hash, and the next state.

---

## 10. Unstick

Read the slice's verdict file, its review and the last three ledger rows. Change nothing. Tell Ross in under 150 words which gate or check fails; whether the fault lies in the code, the requirement or the gate; and the smallest change that would resolve it. If a gate is wrong, the fix changes the gate and its planted-defect test in one commit.

---

## 11. What Ross does

| When | Action |
|---|---|
| To move the build on | Open a new session at the repository root and type `build`. One session per unit |
| When a session reports S-7 | Read the breach. Fix it, waive it in the manifest with a reason, or type `unstick` |
| When a session stops on a blocked item | Close or waive the item in the manifest: `open_items: {O-2: {status: closed}}` |
| After slice 8 | Run the notebooks and the app before the consolidation pass, and add anything to `deferred` |
| Before any real-data cell | Close O-2: read the freeBIRD terms |
