# Review of slice 2: lens 01, Rules

**Date:** 17 November 2026 · **Author:** Ross Taylor

Fourteenth review, a re-review after the read-through (commit eb1efab), under `docs/BUILD.md` section 5 and D-31. The base is commit 3c49e84, the last that changed this file. The notebook there hashes to 9a881e37, the digest the thirteenth review recorded, so the base is what that review read. Only the lines changed between 3c49e84 and the current head, eb1efab, are checked, against every item below and each standing lesson in `docs/BUILD.md` section 8. Cells are numbered from 0 in file order; the notebook still has 46 cells and none was added or removed.

What changed. Of the three review sources only the notebook has changed, and in it one entry of one output: cell 37's table of the calibration check on the generator's civilian cohort, `baseline.calibration_check("civilian")`, now gives the figure reading's sensitivity as 0.525 where it gave 0.524, in both its text and its HTML rendering. No cell source, tag, `concludes` or `sources` entry, evidence list or image has changed; every other difference in the file is execution timing. The cause lies outside the review sources: `baseline.calibration_check` (baseline.py line 218) no longer rounds the achieved figure to four places before returning it. `src/inference_labs/lenses/rules.py` and `app/panels/rules.py` are byte-identical to 3c49e84 and hash as the thirteenth review recorded; neither calls `calibration_check`, so no string the lens module can return and no element of the panel has changed. Among the review sources the changed function also feeds cell 13, which prints the military check, and cell 18, whose figure plots it; both are taken below.

The notebook was run top to bottom from a fresh kernel into a scratch copy in 5.4 seconds. Its reader view, every cell source and text output, matched the committed file and gives the hash below, and each of its eight images matched the committed file and those at 3c49e84 byte for byte. Slice 2's tests pass (30). The changed figure was recomputed from `generator.sample(100_000, 42, cohort="civilian")` with the MPTT-24 coded inline rather than through the library: 11,141 of the 21,240 casualties in need are in Priority 1 under the figure reading, 0.524529, which displays as 0.525 at the three places of the columns beside it. The earlier 0.524 was that value rounded to 0.5245 and then again to three places. The figure is the same with the scan in hospital, because the MPTT-24 reads no scan.

No breach is found. None is missed: the base is the commit of the thirteenth review, so every changed line is new since it.

## What must not be claimed

- That a rule's published accuracy is a property of the rule: HOLDS (cell 37). The changed entry is the generator's figure, not E-09's. It stands in the "achieved" column beside E-09's civilian 0.535, in a row marked False under "held to E-09"; the cell's printout names the generator's civilian cohort and the civilian registry (E-09), and cell 36, unchanged, calls the table "a check on the generator, not a second finding". The changed line attaches no published figure to the rule apart from its population.
- That the MPTT-24 has been validated on pre-hospital observations: HOLDS (cell 37). The changed line claims no validation. Its E-09 column is the civilian registry's figure on first hospital observations, as cell 34 says ("Both are on first hospital observations (E-11)"), and the generator's figure beside it is a check on the generator, not a test of the rule at the point of injury.
- The lines under "What must not be claimed" in the other background files: HOLDS (changed line only). The changed line is a single table entry, a sensitivity on the generator. It names no over-triage, transport time, belief, value of a decision, hazard or graph, and cites no source but E-09, through the column beside it.

## Epistemic checks

- Accuracy quoted for the wrong cohort or setting: HOLDS (cell 37). 0.525 is on the generator's civilian cohort, 100,000 casualties all in the non-battle injury stream, so the injured filter that `calibration_check` applies keeps every one; 21,240 of them, 21.2%, need a life-saving intervention, as the cell prints. It is set beside E-09's TARN figure, the civilian registry, the cohort it is meant to be compared with, and `params.yaml`'s `triage_accuracy_civilian` names the same population. The setting does not move it: the figure is identical with the scan before hospital and in hospital.
- Proxy data read as the real thing: HOLDS (cells 36 and 37). The figure is the generator's. Cell 36's "That is a check on the generator, not a second finding" stands directly above it, and the figure reading's row is marked as not held to E-09.
- Civilian data read as military: HOLDS (cell 37). The civilian registry's figures are compared with the generator's civilian cohort, not applied to a military casualty; the printout and cell 34 call the registry civilian.
- A diagnosis result read as a treatment result: HOLDS (cell 37). The figure is the share of casualties in need of a life-saving intervention whom the rule calls Priority 1, a triage result in the failure section; no treatment is named.

## Numbers and their evidence ids

- The generator's figure reading, civilian cohort, cell 37: HOLDS. 0.5245292 (11,141 of 21,240), recomputed without the library, prints 0.525. The table's other three achieved figures, 0.771, 0.565 and 0.763, from 0.770848, 0.565207 and 0.763306, are unchanged and round correctly. "Within tolerance" stays True: 0.535 less 0.52453 is 0.0105, inside 0.05, and the comparison was already made at full precision. The entry now agrees with notebook 02 cell 13, which prints 0.525 for the same casualties.
- The E-09 column, cell 37: HOLDS. 0.535 and 0.748 are E-09's TARN sensitivity and specificity, 53.5% and 74.8%, as `params.yaml`'s `triage_accuracy_civilian` holds them, with tolerance 0.05. Unchanged.
- The military check, cells 13 and 18: HOLDS. The text of cell 13's table is unchanged. At full precision the achieved figures are 0.626665, 0.737253, 0.641449 and 0.730621, which print 0.627, 0.737, 0.641 and 0.731, as before, and the text reading's two agree with cell 12's 64.1% and 73.1%.

## The generator and the graph

- The changed figure against the code: HOLDS (cell 37; baseline.py lines 205 to 222). `calibration_check("civilian")` draws `generator.sample(100_000, 42, setting="pre_hospital", cohort="civilian")`, keeps the battle and non-battle injury streams, and scores `priority_one` under each reading against `needs_lsi`; its figures now carry full precision. Cell 36's sentences on the civilian cohort are unchanged and describe the text reading, which the change does not touch; none describes the figure reading's sensitivity.
- The graph: HOLDS. No changed line concerns the graph.

## Standing lessons

Each lesson against the changed line.

- Lesson 1: HOLDS. The civilian registry's figure sits in the same cell as its id and population, "civilian registry (E-09)", and is not applied to the military casualty.
- Lesson 2: HOLDS. The cell names its group, "the generator's civilian cohort".
- Lesson 3: HOLDS. The panel is unchanged.
- Lesson 4: HOLDS. The changed entry is a share, not a difference, and has no sign to be read.
- Lesson 5: HOLDS. Cell 36 says the civilian cohort's physiology carries two assumed changes, tuned to the civilian figures.
- Lesson 6: HOLDS. No figure title changed.
- Lesson 7: HOLDS. The changed line is a diagnosis result in a table of diagnosis results.
- Lesson 8: HOLDS. Nothing calls the generator's figure, or E-09's, performance at the point of injury.
- Lesson 9: HOLDS. The changed line gives no count.
- Lesson 10: HOLDS, as set out under the generator and the graph.
- Lesson 11: HOLDS. The changed line says nothing of where the rule's items came from or why anything was chosen.
- Lesson 12: HOLDS. The changed line sets the generator's figure beside E-09's against a stated tolerance; it calls no difference a finding, and the figure reading's row is not held to E-09.
- Lesson 13: HOLDS. No chance of death is given.
- Lesson 14: HOLDS (cell 37). The change brings the cell into line with this lesson: the achieved figure is carried at full precision and displayed to the three places of the E-09 and tolerance columns beside it, 0.52453 as 0.525, where the earlier 0.524 came from rounding twice. The tolerance comparison was and is at full precision.
- Lesson 15: HOLDS. No comparison in the changed line reverses in a subgroup; the civilian cohort is a single stream.
- Lesson 16: HOLDS (cell 37). D-23 concerns the military injured. The changed line quotes the rule's accuracy on the generator's civilian cohort, and the cell prints, in the same output, the comparison that bears on it: 21.2% in need against 19.5% Priority 1 in the civilian registry.
- Lesson 17: HOLDS. No learned model is concerned.

## Figures

- Every figure: HOLDS. No figure changed. Cell 18 plots the military check's achieved figures, which `calibration_check` now returns at full precision rather than to four places, a shift of at most 0.00005; its image is byte-identical to that at 3c49e84 and to the rerun, and its title, legend and `concludes` tag are unchanged. The images of cells 3, 9, 16, 23, 30, 33 and 39 are likewise identical, and no tag changed. The changed output of cell 37 is a table, taken above.
- App page 1, the rules panel: HOLDS. `app/panels/rules.py` is unchanged and does not call the changed function.

## Limits

None recorded. A re-review after consolidation records no new limits (`docs/BUILD.md` section 5); the limits of the review committed at 83743ee stand as a record (D-31).

VERDICT: HOLDS

## Reviewed sources

- `notebooks/01_rules.ipynb` 2a00a6800a3b69b62a082608581cb1d062104b03ea1a76d8e39a60358a9ea297
- `src/inference_labs/lenses/rules.py` 71d63c7e99fc6392b0064a2974f6b00dc2fcb52cac87d2f05e67ecb23b7740cb
- `app/panels/rules.py` fb89ef560936cfc6c83a08a99c327ab9d110d346d11adc71f9cd05ead0f6b33e
