# Review of slice 10: lens 06, Connectionist

**Date:** 17 November 2026 · **Author:** Ross Taylor

Fourth review of slice 10, and the re-review after the final consolidation pass (commit 305c8a3, D-33), under `docs/BUILD.md` section 5 and D-31. The base is commit 22fa76b ("Slice 10: close"), the last that changed this file; the third review it holds read the files at ac9f931 and found no breach, and its hash block matches the review sources at 22fa76b. Only the lines changed between 22fa76b and the current head, 484daaf, are checked, against every item below and each standing lesson in `docs/BUILD.md` section 8. Between 22fa76b and 484daaf the review sources changed in commit 305c8a3 alone, which carried deferred item a, D-33 through the shared sentence; deferred item b, the forest fitted with `n_jobs=1` (`trees.py` line 93), changed a module this one calls but no review source. A breach in a line unchanged since 22fa76b would be one the third review should have recorded, and would be marked MISSED. Cells are numbered from 0 in file order; the notebook has 37 cells. Line numbers are those of the file named, at 484daaf.

What changed since 22fa76b, in all:
- **Lens module.** In `seven_axes`, lines 742 to 743 call `rules.d23_sentence` with the scope "every stream of the military cohort, disease included, and among battle casualties alone" and the group "every stream and battle", in place of the defaults; the subject stays the default, "The scorecard's figures are". The sentence reaches axis 1 of the figure column (line 790), between the rule's figures and `HOSPITAL`. No other line changes.
- **Notebook.** Cell 17 prints `rules.d23_sentence` with the same scope and group and the subject "These figures are", in place of the defaults, and its text output changes in that sentence alone. Cell 33's output changes in axis 1 of the figure column alone, in its HTML and its plain-text table, whose column widths move with it. No other cell source or text output changes; the cell tags, every `concludes:` tag and the evidence list are unchanged, and the ten images are byte-identical to those at 22fa76b.
- **Panel.** `app/panels/connectionist.py` is unchanged, and so are `panel` and `page_panel` (connectionist.py lines 849 to 906). Rendered for all 1,736 walk-through casualties, three patient types in both settings, from the package at 22fa76b and at 484daaf, the panel is identical.
- **Library.** Of the functions the module calls, `rules.d23_sentence` changed (rules.py lines 178 to 213, with `D23_GROUPS` at line 164 and `need_shares` at lines 167 to 175 new), and `trees.models` now fits the forest in one process. `baseline.calibration_check` and `stochastic.seven_axes` changed, and the module calls neither; `stochastic.axis7`, `decision.py`, `bayesian.py`, `frequentist.py`, `generator.py` and `params.yaml` are unchanged.
- **Background file and register.** `docs/background/06-connectionist.md`, `docs/EVIDENCE.md`, `docs/BUILD.md` and PRD sections 3, 6.0 and 6.10 are unchanged since 22fa76b; the PRD gains section 6.11, and `docs/DESIGN.md` gains D-33.

The code the changed lines rest on was read: connectionist.py lines 445 to 446 and 736 to 790; rules.py lines 145, 164 to 213 and 315 to 316; baseline.py lines 167 to 169 and 194 to 202; and generator.py lines 300 to 305. The register row E-09, and D-23 and D-33 in `docs/DESIGN.md`, were opened. The notebook was run top to bottom from a fresh kernel in its own folder, as gate G-7 runs it, into a scratch copy, in 40.9 seconds without error. Its reader view hashes to the committed value, and its ten images match the committed ones byte for byte. The run-to-run variation in lens 04's forest that the third review set out no longer arises: the forest's figures in cells 17 and 18 print as committed. Gates G-1, G-5, G-6, G-8, G-9, G-10 and G-13, called on their own without writing, pass. Every figure in the changed sentence was recomputed at full precision on the seed-42 evaluation sample and on seeds 43 to 62.

No breach is found, and none is missed.

## What must not be claimed

- That anything here shows a network can read a military trauma scan in a human: HOLDS (cells 17 and 33; connectionist.py lines 742 to 743 and 790). No changed line speaks of a scan, an image or a network reading one; every changed line is in the treatment section or in axis 1 of the rule's column.
- That E-99's pneumothorax and chest drain example is in the abstract: HOLDS (the same cells and lines). No changed line cites E-99, and neither "pneumothorax" nor "drain" appears in any review source.

## Epistemic checks

- Accuracy quoted for the wrong cohort or setting: HOLDS (cells 17 and 33; lines 742 to 743 and 790). Cell 17's sentence follows its two tables, the first headed "Every stream, 100,000 synthetic casualties of the military cohort, seed 42 (mechanism)" and the second "Battle casualties alone, 29,925 of the same casualties", and says its figures are on those two groups, which they are. It gives each group's share in need and sets each beside E-09 as D-33 asks. In axis 1 of the figure column the sentence follows the rule's figures "on every stream; among battle casualties alone", and its subject, "The scorecard's figures", stands in a column that cell 32 says belongs to the treatment column. Every figure of the treatment and baseline columns in axes 1, 2 and 7 is on every stream or among battle casualties alone. The diagnosis column is headed "image network (constructed images)", and its axis 1 entry in the same row says "(constructed images, seed 42)". A reader does not take its figures for the military cohort's, and the subject was in this place, unchanged in wording, at 22fa76b. The setting is the scan before hospital, as before.
- Proxy data read as the real thing: HOLDS (cells 17 and 33). The changed figures are of the generator's synthetic casualties; cell 17 labels them "(mechanism)", and "the military cohort" is the notebook's name for the synthetic cohort. The sentence sets the generator's shares beside E-09's registry figure as a comparison of cohorts, not as data on casualties, and `HOSPITAL` still follows it in both places.
- Civilian data read as military: HOLDS (cells 17 and 33). The only source the changed lines cite is E-09, for "the military registry", its JTTR figures; its civilian TARN figures are not used. G-10 passes.
- A diagnosis result read as a treatment result: HOLDS (cells 17 and 33). Cell 17 is tagged `case-tx` and sits under cell 16's treatment heading; the change in cell 33 is in axis 1 of the figure column, which cell 32 places with the treatment column. The diagnosis cells and the diagnosis column are unchanged.

## Numbers traced to the evidence register

- E-09 (cells 17 and 33): HOLDS. 47.6% Priority 1 among the JTTR's 3,654 adults is the row's; the sentence takes it from `PUBLISHED["MPTT-24, military"]`, which holds 0.476 citing E-09 (rules.py line 145).
- D-23 and D-33 (cells 17 and 33): HOLDS. D-33 gives battle casualties alone 50.2% in need against 47.6%, and the injured, battle and non-battle together, 26.5%; it asks that each scorecard's sentence name the group it reports and give that group's share, and that none on battle casualties alone call them milder. Both changed sentences name every stream and battle casualties alone, give 16.7% and 50.2%, call the battle casualties not a milder cohort and the injured a milder one. Neither repeats D-33's "occurs only among battle casualties": in the seed-42 sample 1,688 of the 43,366 disease admissions need one through septic shock (generator.py line 305), and they are counted in the 16.7%. Among the injured the statement holds: none of the 26,709 non-battle injuries is in need.
- The generator's figures: HOLDS. On the seed-42 sample 16,704 of 100,000 are in need (0.16704), 15,016 of the 29,925 battle casualties (0.501788) and 15,016 of the 56,634 injured (0.265141). Across seeds 43 to 62 battle casualties run from 49.3% to 50.2% in need, above 47.6% on every seed, and the injured from 25.9% to 26.6%, below it on every seed. The 29,925 and 50.2% agree with `signs_results`, from which the treatment column's axis 7 and the panel's battle line take them.

## Sentences about the generator and the graph

- Cells 17 and 33, the D-23 sentence: HOLDS. `need_shares` (rules.py lines 167 to 175) takes `needs_lsi` on the seed-42 military sample before hospital on every stream and among battle casualties by the observed stream, and `calibration_need` the injured, battle and non-battle (baseline.py lines 194 to 202); `milder` compares each share with 0.476 at full precision (rules.py lines 190 to 191). Both places print the branch at rules.py lines 211 to 212. "Every stream of the military cohort, disease included" is `baseline.generator_sample` with its defaults (baseline.py lines 167 to 169), which holds disease admissions.
- Cell 17, "These figures are on every stream of the military cohort, disease included, and among battle casualties alone": HOLDS. `signs_table()` and `signs_table(cn.BATTLE)` are the two tables the cell displays.
- Axis 1 of the figure column, "The scorecard's figures are on every stream of the military cohort, disease included, and among battle casualties alone": HOLDS, as set out under the first epistemic check.

## Figures

- Cells 3, 8, 10, 13, 14, 19, 20, 26, 27 and 30: HOLDS. Sources, titles and `concludes:` tags are unchanged since 22fa76b, and each image is byte-identical to that at 22fa76b.
- App page 1, the connectionist panel: HOLDS. It holds no figure.

## Strings the lens module returns, and the panel

- `seven_axes`, axis 1 of the figure column (lines 742 to 743 and 790): HOLDS, as set out above. Every other entry of every column prints as at 22fa76b.
- Every other string the module can return: HOLDS. Its source lines are unchanged since 22fa76b, the forest's single-process fit leaves every printed figure as committed, and every other cell's text output prints as before.
- `panel` and `page_panel` (lines 849 to 906) and `app/panels/connectionist.py`: HOLDS. Unchanged, and identical on all 1,736 walk-through casualties at 22fa76b and 484daaf.

## Standing lessons

- Lesson 1: HOLDS. E-09 is named with its id and population, the military registry, in the same sentence, and is set beside the generator's cohorts, not applied to a casualty.
- Lesson 2: HOLDS. Each changed figure names its group: every stream of the military cohort, battle casualties alone, or the injured, battle and non-battle; E-09's 47.6% is "Priority 1 in the military registry", as its row gives it.
- Lesson 3: HOLDS. No number on app page 1 changes; G-8 passes.
- Lesson 4: HOLDS. "A milder cohort" and "not a milder cohort" are stated in words.
- Lesson 5: HOLDS. The changed lines show no result driven by a prior or an assumption; `HOSPITAL`, which calls the generator's signs assumptions, still follows the sentence in both places.
- Lesson 6: HOLDS. No title changes.
- Lesson 7: HOLDS. Every changed line is in the treatment section or the rule's column.
- Lesson 8: HOLDS. No changed line calls a figure performance at the point of injury; the hospital-observation sentence follows the D-23 sentence in cell 17 and axis 1.
- Lesson 9: HOLDS. The changed lines give shares, not counts; the count beside them in cell 17, "29,925 of the same casualties", is exact.
- Lesson 10: HOLDS, as set out under the sentences about the generator and the graph.
- Lesson 11: HOLDS. "The one the rule was validated on" is D-23's; no changed line says why anything was chosen or what a source omits or forbids.
- Lesson 12: HOLDS. The battle casualties' 50.2% against 47.6% holds on every seed from 43 to 62, and the injured's 26.5% lies below 47.6% on every one.
- Lesson 13: HOLDS. No chance of death is in the changed lines.
- Lesson 14: HOLDS. Each share is compared with 0.476 at full precision and printed alike, to one decimal place in per cent.
- Lesson 15: HOLDS. The comparison with E-09 reverses between the injured and battle casualties alone, and both changed sentences now show it with each group.
- Lesson 16: HOLDS. The D-23 sentence stands in cell 17 with the rule's figures and in axis 1 of the figure column, and says the generator's injured are a milder cohort; it does not call battle casualties milder (D-33).
- Lesson 17: HOLDS. No changed line concerns how a learned model fares against the baseline.

## Limits

None recorded. A re-review after consolidation records no new limits (`docs/BUILD.md` section 5); the limits of the review committed at 22fa76b stand as a record (D-31).

VERDICT: HOLDS

## Reviewed sources

- `notebooks/06_connectionist.ipynb` a3ffacf069c3f049b20b1390a440024228695a4adba476421c19e9a0a595d837
- `src/inference_labs/lenses/connectionist.py` 6647c98536be2d03747d382586171458639b57be33ac3d9e752e070e366ab84c
- `app/panels/connectionist.py` c542d32429d9e4aaf701cb6ea429a5cf4f92cae7435792e983ed838e17ac64bd
