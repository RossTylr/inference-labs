# Review of slice 9: lens 09, Reinforcement learning

**Date:** 17 November 2026 · **Author:** Ross Taylor

Fourth review of slice 9, and the re-review after the final consolidation pass (commit 305c8a3, D-33), under `docs/BUILD.md` section 5 and D-31. The base is commit da0d1bd, the last that changed this file; the third review it holds read the files at 53a4f39 and found no breach, and its hash block matches the review sources at da0d1bd. Only the lines changed between da0d1bd and the current head, e333028, are checked, against every item below and each standing lesson in `docs/BUILD.md` section 8. Between da0d1bd and e333028 the review sources changed in commit 305c8a3 alone, which carried deferred items a and c; item c took up the third review's limit 4. A breach in a line unchanged since da0d1bd would be one the third review should have recorded, and would be marked MISSED. Cells are numbered from 0 in file order; the notebook has 39 cells. Line numbers are those of the file named, at e333028.

What changed since da0d1bd, in all:
- **Notebook.** Cell 11 sets beside each route's share in need on every stream a marker for the share among the training sample's battle casualties on the same route, from `question_tree(stream="battle")`; each label adds how many of the route's training casualties are battle casualties; the title names both groups; a legend is added; and the cell displays the battle casualties' tree. Cell 13 prints `rules.d23_sentence` with the group "every stream and battle" and the scope "every stream of the military cohort, disease included, and, where a row says so, on battle casualties alone", in place of the default. Cell 14 retitles its first two panels "every stream", adds a third, the policy's net benefit at 0.10 among battle casualties alone with both readings and flagging every casualty as lines, and prints the battle casualties' questions and net benefit at the chosen cost and, for every cost on the grid, the spread across 20 further samples of the policy's net benefit among them less each reading, less flagging every casualty and less the chosen cost. Cell 15 gains one sentence. Cell 35's output changes in axis 1 of the figure column alone, in its HTML and its plain-text table, through `d23_sentence`. The `concludes:` tags of cells 11 and 14 are extended. No other cell source or text output changes; the cell tags, the other six `concludes:` tags and the evidence list are unchanged, and the other six images are byte-identical to those at da0d1bd.
- **Lens module.** `question_tree` (lines 264 to 276) takes a stream and counts that stream's training casualties on each route of the policy solved on every stream; `cost_curve` (lines 355 to 368) adds the policy's questions asked and net benefit among battle casualties alone. Of the library functions the module calls, only `rules.d23_sentence` changed (rules.py lines 164 to 213, with `D23_GROUPS` and `need_shares` new); the module calls it once, at line 865, with its defaults. `baseline.calibration_check` and `stochastic.seven_axes` changed, and the module calls neither; `stochastic.axis7`, `decision.py`, `bayesian.py`, `generator.py` and `params.yaml` are unchanged.
- **Panel.** `app/panels/reinforcement.py` and `panel` (lines 967 to 1001) are unchanged, and neither calls a changed function. Rendered for all 1,736 entries app page 1 can show, from the package at da0d1bd and at e333028, the panel is identical.
- **Background file and register.** `docs/background/09-reinforcement-learning.md`, `docs/EVIDENCE.md`, `docs/BUILD.md` and PRD sections 3, 6.0 and 6.9 are unchanged since da0d1bd; the PRD gains sections 6.10 and 6.11, and `docs/DESIGN.md` gains D-33.

The helpers the changed lines call were read: `reinforcement.py` lines 138 to 148 (`answer_counts`), 174, 220 to 251 (`route`, `route_table`), 304 to 344 (`_measured`, `diagnosis_results`, `diagnosis_spread`) and 865 to 901; `rules.py` lines 145 and 164 to 213; `baseline.py` lines 77, 167 to 169 and 194 to 202; `decision.py` lines 68, 99 to 102 and 120 to 128; and `generator.py` lines 79, 305 and 338 to 343. The register row E-09, and D-23, D-24, D-26 and D-33 in `docs/DESIGN.md`, were opened. The notebook was run top to bottom from a fresh kernel in its own folder, as gate G-7 runs it, into a scratch copy, in 18.1 seconds without error. Its reader view hashes to the committed value, and its eight images match the committed ones byte for byte; the two changed images were viewed. Gates G-1, G-5, G-6, G-8, G-9, G-10 and G-13, and G-7's structure check, called on their own without writing, pass. Every changed figure was recomputed at full precision on the seed-7 training sample, the seed-42 evaluation sample and seeds 43 to 62.

No breach is found, and none is missed.

## What must not be claimed

- That the original paper showed patients do better under the policy: HOLDS (cells 11, 13, 14, 15 and 35; reinforcement.py lines 264 to 276 and 355 to 368). No changed line cites E-120 or speaks of patients under the learned policy; every changed line is in the diagnosis case or in axis 1 of the rule's column.
- That CLOVERS refutes the learned policy: HOLDS (the same lines). No changed line cites E-97 or any trial.
- That results on a 716-state benchmark say anything about a patient: HOLDS (the same lines). No changed line cites E-49 or the benchmark; the changed figures are of the generator's synthetic casualties and are marked mechanism.

## Epistemic checks

- Accuracy quoted for the wrong cohort or setting: HOLDS (cells 11, 13, 14, 15 and 35; lines 264 to 276 and 355 to 368). Every changed figure names its group and its sample. Cell 11's markers and table are the training sample's battle casualties, labelled "battle casualties alone on the same route" and "training battle casualties", and cell 15 places its 0.209 "among the training sample's battle casualties". Cell 14's third panel and printout are the evaluation sample's battle casualties, titled and printed "battle casualties alone", with their spread on the 20 further samples; its first two panels now say "every stream". Cell 13's D-23 sentence says its figures are on every stream "and, where a row says so, on battle casualties alone", as the rows ending ", battle" and the blocks headed "battle casualties alone" are, and gives the share in need of each group. Cell 35's axis 1 adds the every-stream share to a column scored on every stream. `cost_curve` scores in the pre-hospital setting; unchanged cell 34 says the setting changes only the scan, which no method reads.
- Proxy data read as the real thing: HOLDS (the same cells and lines). Every changed figure is of the generator's synthetic casualties: the title of cell 11, the three panel titles of cell 14 and its battle printout end "(mechanism)". The D-23 sentence sets the generator's shares beside E-09's registry figure as a comparison of cohorts; "the military cohort" is the notebook's name for the synthetic cohort (cell 9, "100,000 synthetic casualties of the military cohort").
- Civilian data read as military: HOLDS (cells 13 and 35). The only source the changed lines cite is E-09, for "the military registry", the JTTR row; its civilian TARN figures are not used. G-10 passes.
- A diagnosis result read as a treatment result: HOLDS (cells 11, 13, 14, 15 and 35). Cells 11 to 15 are tagged `case-dx` and sit under cell 9's diagnosis heading; cell 35's change is in axis 1 of the rule's column. The treatment cells, the treatment column and the panel's treatment line are unchanged.

## Numbers traced to the evidence register

- E-09 (cells 13 and 35): HOLDS. 47.6% Priority 1 among the JTTR's 3,654 adults is the row's; the sentence takes it from `PUBLISHED["MPTT-24, military"]`, which holds 0.476 citing E-09 (rules.py line 145).
- D-23 and D-33 (cells 13 and 35): HOLDS. D-33 gives battle casualties alone 50.2% in need against 47.6%, and the injured 26.5%, and asks that each scorecard's sentence name its group and give that group's share, and that none on battle casualties alone call them milder. Cell 13's sentence names every stream and battle casualties alone, gives 16.7% and 50.2%, calls the battle casualties not a milder cohort and the injured a milder one; axis 1 of cell 35 names every stream and gives 16.7%. Neither repeats D-33's "occurs only among battle casualties": in the seed-42 sample 1,688 of the 43,366 disease admissions need one through septic shock (generator.py line 305), and they are counted in the 16.7%.
- E-93 (cell 14): HOLDS. Flagging every casualty is `decision.flag_all` (decision.py lines 99 to 102), the comparator unchanged cell 34 describes; the changed lines add no citation.
- The generator's figures: HOLDS. On the seed-7 training sample, 29,618 battle casualties, the routes hold 17,682 at 0.613845 in need, 7,025 at 0.209395 (the unflagged route), 4,389 at 0.507861, 407 at 0.540541 and 115 at 1.000000, beside 50,841, 35,673, 12,096, 1,275 and 115 on every stream; the threshold is 0.1 exactly. Across seeds 43 to 62 the battle casualties on the unflagged route run from 0.200 to 0.216 in need. On the seed-42 sample 16,704 of 100,000 are in need (0.16704), 15,016 of the 29,925 battle casualties (0.501788) and 15,016 of the 56,634 injured (0.265141); across seeds 43 to 62 battle casualties run from 49.3% to 50.2% in need, above 47.6% on every seed. Among the seed-42 battle casualties the policy's net benefit per 100 is 37.207834 at a cost of 0 (4.04 questions), 41.611807 at 0.005 to 0.02 (1.90), 40.600019 at 0.05 and 0.1 (1.40) and 44.643089 at 0.2 (none), equal to flagging every casualty's 44.643089; the readings score 29.998700 and 30.700455. Across seeds 43 to 62 the policy less flagging every casualty runs from -7.572 to -6.997 at 0, -3.071 to -2.632 at 0.005 to 0.02 and -4.082 to -3.616 at 0.05 and 0.1, and lies within 1e-14 of zero at 0.2, where it is rounded to six places and printed as a tie; at 0.005 and 0.02 the policy is the one at 0.01 and the difference is exactly zero; less the figure reading it runs from +7.077 at its lowest to +15.114 at its highest. On every one of the 20 samples the battle casualties' net benefit is lowest at a cost of 0 and highest at 0.2. Each display is one rounding of its value.

## Sentences about the generator and the graph

- `question_tree`'s docstring (lines 266 to 269): HOLDS. `route_table(cost)` follows `question_policy(cost)`, solved on `answer_counts()` with no stream (line 174); given a stream, `answer_counts(stream)` keeps that stream's casualties (line 143), and a route none of them takes is dropped (line 274).
- `cost_curve`'s docstring (lines 357 to 358): HOLDS. Each row is `diagnosis_results("pre_hospital", c)` (line 361), the seed-42 evaluation sample on every stream, with `"question policy, battle"` taken by the observed stream (`_measured`, line 306).
- Cell 11, the markers and labels: HOLDS. Each marker is `question_tree(stream="battle")` on the route of the same name; the battle counts on the five routes sum to 29,618, every battle casualty of the training sample.
- Cells 13 and 35, the D-23 sentence: HOLDS. `need_shares` (rules.py lines 167 to 176) takes `needs_lsi` on the seed-42 military sample on every stream and among battle casualties by the observed stream, and `calibration_need` the injured, battle and non-battle (baseline.py lines 77 and 194 to 202); `milder` compares each share with 0.476 at full precision (rules.py lines 190 to 191). Cell 13 prints the branch at rules.py lines 211 to 212; axis 1 (reinforcement.py lines 865 and 901) the every-stream branch, lines 206 to 207.
- Cell 15, "every route the policy can end on at the default cost holds a share in need above the threshold": HOLDS. The route table at 0.01 has one ending beyond the five routes shown, a walking casualty who responds only to pain or not at all, stopped unflagged after two questions; the generator lets only alert and voice casualties walk (generator.py lines 79 and 341 to 343), so no casualty can end there.
- Cell 15, "at every cost shown above at which the policy asks a question its net benefit among them lies below flagging every casualty on every one of the 20 further samples": HOLDS, as traced above; at 0.2 it asks nothing and ties.
- Cell 15, "what lifts it above the rule there is flagging more casualties, not the questions": HOLDS on the notebook's own figures. Among battle casualties the policy scores highest where it asks nothing and flags every casualty and lowest where it asks most, and at the default cost its sensitivity is 0.898 against the readings' 0.627 and 0.641 (cell 13).
- The `concludes:` tags of cells 11 and 14: HOLDS. Among battle casualties every route lies above 0.10; on every stream the net benefit never rises and at 0.2 falls below both readings' 8.04 and 8.21 to 7.45; among battle casualties it lies above both readings at every cost, is lowest at 0 and highest at 0.2, where it equals flagging every casualty.

## Figures

- Cell 11: HOLDS. The title describes what is plotted; the bars are the every-stream shares as before, the markers the battle casualties' shares, and the legend and labels say which is which and give the counts. A reader now concludes, as the tag says, that among battle casualties every route, the unflagged one included, lies above the threshold; the earlier figure did not show it.
- Cell 14: HOLDS. Each of the three panels is titled with its group and "(mechanism)", and each has its own scale, shown on its ticks. A reader concludes that among battle casualties the curve runs the other way from every stream, lowest where a question is free and reaching flagging every casualty where the policy asks nothing, while staying above both readings; the printout's spreads show that each step holds on all 20 further samples.
- Cells 3, 8, 21, 24, 30 and 32: HOLDS. Sources, titles and `concludes:` tags are unchanged since da0d1bd, and each image is byte-identical to that at da0d1bd.
- App page 1, the reinforcement learning panel: HOLDS. It holds no figure.

## Strings the lens module returns, and the panel

- `question_tree` (lines 264 to 276): HOLDS. It returns route strings and the decisions "flag" and "do not flag" of the policy solved on every stream, with the counts and shares of the stream asked for; it is reached on every stream in cells 10 and 14 and `seven_axes` (line 866), and for battle casualties in cell 11.
- `cost_curve` (lines 355 to 368): HOLDS. The two added columns are numbers; its other columns are unchanged.
- `seven_axes`, axis 1 of the figure column (lines 865 and 901): HOLDS, as set out above. Every other entry of every column prints as at da0d1bd.
- Every other string the module can return: HOLDS. Its source lines and every function it calls are unchanged since da0d1bd, and every other cell's text output prints as before.
- `panel` (lines 967 to 1001) and `app/panels/reinforcement.py`: HOLDS. Unchanged, and identical on all 1,736 entries at da0d1bd and e333028.

## Standing lessons

- Lesson 1: HOLDS. E-09 is named with its id and population, the military registry, in the same sentence, and is set beside the generator's cohorts, not applied to a casualty.
- Lesson 2: HOLDS. Each changed figure names its group: every stream, battle casualties alone, or the training sample's battle casualties; E-09's 47.6% is "Priority 1 in the military registry", as its row gives it.
- Lesson 3: HOLDS. No number on app page 1 changes; G-8 passes.
- Lesson 4: HOLDS. "Lies below flagging every casualty" (cell 15), "lower" in each spread of cell 14, and "a milder cohort" and "not a milder cohort" are stated in words.
- Lesson 5: HOLDS. Cell 14's cost axes say "(an assumption)", and cell 15's added sentence stands in the paragraph that opens "Read the comparison with its assumptions in view".
- Lesson 6: HOLDS. Every changed title describes what is plotted.
- Lesson 7: HOLDS. Every changed line is in the diagnosis section or the rule's column.
- Lesson 8: HOLDS. No changed line calls a figure performance at the point of injury; the hospital-observation sentence still follows the D-23 sentence in cell 13 and axis 1.
- Lesson 9: HOLDS. "115 training casualties, 115 of them battle casualties", "17,682", "20 further samples".
- Lesson 10: HOLDS, as set out under the sentences about the generator and the graph.
- Lesson 11: HOLDS. "The one the rule was validated on" is D-23's; no changed line says why anything was chosen or what a source omits or forbids.
- Lesson 12: HOLDS. Every comparison in cell 14's printout carries its spread across 20 further samples, and the three whose spread covers zero (0.005 and 0.02 against 0.01; 0.2 against flagging every casualty) are called ties. Cell 15's comparison holds on all 20. The battle casualties' 50.2% against 47.6% holds on every seed from 43 to 62.
- Lesson 13: HOLDS. No chance of death is in the changed lines.
- Lesson 14: HOLDS. The 0.209 and the threshold are compared at full precision and printed alike, "0.209 against 0.100"; net benefits are compared at full precision through their spreads, and the difference at 0.2 is rounded to six places so that it prints as a tie and not as a sign.
- Lesson 15: HOLDS. The reversal among battle casualties of cells 11 and 14 is now shown with that subgroup, in both figures, cell 14's printout and cell 15.
- Lesson 16: HOLDS. The D-23 sentence stands in cell 13 with the rule's figures and in axis 1 of the figure column, and says the generator's injured are a milder cohort; cell 14's battle figures follow cell 13 and do not call battle casualties milder (D-33).
- Lesson 17: HOLDS. The policy's net benefit falling below flagging every casualty among battle casualties, at every cost at which it asks a question, is reported as it fell.

## Limits

None recorded. A re-review after consolidation records no new limits (`docs/BUILD.md` section 5); the limits of the review committed at da0d1bd stand as a record (D-31).

VERDICT: HOLDS

## Reviewed sources

- `notebooks/09_reinforcement_learning.ipynb` e421935d3deae54dbc0259445b1a326d548518c208dbb8bc9aad40c649b5d2ea
- `src/inference_labs/lenses/reinforcement.py` 2768bacc1e52b081a9fd8d09b93dd5c68e490a6ff955cb4849f8249427b2e7f6
- `app/panels/reinforcement.py` 5119fcbe70dcad42a0a2ba2eedc0d65c354a8dfc4faea1bc797ff165e8ba8d8b
