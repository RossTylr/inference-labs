# Review of slice 2: lens 01, Rules

**Date:** 17 November 2026 · **Author:** Ross Taylor

Fifteenth review, a re-review after the final consolidation pass (commit 305c8a3, D-33), under `docs/BUILD.md` section 5 and D-31. The base is commit 0c69b05, the last that changed this file. There the notebook hashes to 2a00a680 and the lens module to 71d63c7e, the digests the fourteenth review recorded, so the base is what that review read. Only the lines changed between 0c69b05 and the current head, 7d97beb, are checked, against every item below and each standing lesson in `docs/BUILD.md` section 8. Cells are numbered from 0 in file order; the notebook still has 46 cells and none was added or removed.

What changed. In the lens module, lines 164 to 213 only: a new constant, `D23_GROUPS` (line 164); a new function, `need_shares` (lines 167 to 175), which gives the share in need of a life-saving intervention on every stream, among the injured and among the battle casualties alone; and `d23_sentence` (lines 178 to 213), rewritten with two new parameters, `group` and `share`, four branches and an error for any other group. `seven_axes` still calls `d23_sentence()` with its defaults (line 414), so slice 2's own scorecard takes the "every stream" branch. In the notebook, one source line and one output entry: cell 40's second paragraph, and axis 1 of cell 41's figure column, in both its text and HTML forms. In each, "The scorecard's figures are on every stream of the military cohort, disease included" now ends its own sentence and is followed by "On every stream of the military cohort, 16.7% of casualties need a life-saving intervention;", and "of whom 26.5% need a life-saving intervention" becomes "of whom 26.5% need one". No other cell source, text output, tag, `concludes` or `sources` entry, evidence list or image has changed; every other difference in the file is execution timing. `app/panels/rules.py` is byte-identical to 0c69b05 and hashes as recorded. Neither the panel nor `rules.page_panel` calls `need_shares` or `d23_sentence`, so no element of the panel has changed.

The notebook was run top to bottom from a fresh kernel into a scratch copy in 5.4 seconds. Its reader view, every cell source and text output, matched the committed file and gives the hash below, and each of its eight images matched the committed file and those at 0c69b05 byte for byte. Slice 2's tests pass (30). Every share in the changed lines was recomputed from `generator.sample(100_000, 42, cohort="military")` without the lens's helpers:
- On every stream, 16,704 of 100,000 casualties are in need (0.16704).
- Among the injured, 15,016 of 56,634 are in need (0.26514); the injured are 29,925 battle and 26,709 non-battle casualties.
- Among the battle casualties, 15,016 of 29,925 are in need (0.50179).
- The other 1,688 in need are disease casualties with septic shock, out of 43,366; no non-battle casualty is in need.
- Need for an intervention is identical, casualty by casualty, with the scan before hospital and in hospital.
- Across seeds 43 to 62, the shares run from 0.4932 to 0.5020 among the battle casualties, 0.2586 to 0.2660 among the injured, and 0.1636 to 0.1689 on every stream.

Axis 1's 60.0% and 78.6%, unchanged text in a changed line, were recomputed with the MPTT-24's figure reading coded inline: 10,021 of 16,704 and 65,436 of 83,296. Every string `d23_sentence` can return was generated: the four branches, the `share` branches (none, exactly 1, and any other value) and the error message.

No breach is found. None is missed: the base is the commit of the fourteenth review, so every changed line is new since it.

## What must not be claimed

- That a rule's published accuracy is a property of the rule: HOLDS (cells 40 and 41; rules.py lines 164 to 213). The changed lines quote no published accuracy. The one published figure they carry, 47.6%, is given as "Priority 1 in the military registry (E-09)", a property of that population. The accuracy beside it in axis 1, 60.0% and 78.6%, is the generator's, on "all 100,000 synthetic casualties, disease included". Each branch of `d23_sentence` sets a group's share in need on the generator against that registry figure and calls the group milder, or not milder, than "the one the rule was validated on". That ties the validation to a cohort, not to the rule.
- That the MPTT-24 has been validated on pre-hospital observations: HOLDS (cells 40 and 41; rules.py lines 167 to 213). No changed line names a setting for the validation. "The one the rule was validated on" names a cohort, and in cell 40 the next sentence, unchanged, says that E-09 was measured on hospital observations (E-11) and that none of it is performance at the point of injury. `need_shares` draws its sample with the scan before hospital (line 171). Need is the same in either setting and the MPTT-24 reads no scan, so no share in the changed lines is a pre-hospital result of the rule.
- The lines under "What must not be claimed" in the other background files: HOLDS (changed lines only). The changed lines give the generator's shares in need and E-09's 47.6%, from the UK military registry. They name no US outcome figure, attribution or operation (00); no transport time or over-triage (02); no posterior or CRASH-3 analysis (03); no PECARN or forest (04); no E-85, E-81 or E-26 timing (05); no network (06); no MATTERs, mandate or 44.2% (07); no graph or E-86 (08); no learned policy, CLOVERS or benchmark (09); no exchange rate, civilian benchmark or PATCH (10); and no language model or conformal guarantee (11).

## Epistemic checks

- Accuracy quoted for the wrong cohort or setting: HOLDS (cell 40; cell 41, axis 1 of the figure column; rules.py lines 167 to 213). The only accuracy in a changed line is axis 1's sensitivity of 60.0% and specificity of 78.6%, on all 100,000 casualties of the military cohort. The new sentence beside it gives that same group's share in need, 16.7%. The comparison with E-09 stays with the injured, 26.5%, from `baseline.calibration_need`: the battle and non-battle streams, the group the calibration checks of cells 12 and 13 hold to E-09. In the module, each branch gives the share of the group it names: every stream, the injured, the battle casualties alone, or, through `share`, a group within them. The setting moves no share.
- Proxy data read as the real thing: HOLDS (cells 40 and 41; rules.py lines 167 to 213). "On every stream of the military cohort, 16.7%" stands in the same entry and paragraph as "all 100,000 synthetic casualties" and follows "The scorecard's figures are on every stream of the military cohort". The sentence it opens ends with "the generator's injured". The battle branches likewise end with "so the generator's injured are" in the sentence that gives the battle share. `need_shares`'s docstring says "synthetic casualties" and "(mechanism)". The 16.7% is not E-11's 16.7% of military cases with complete pre-hospital data, given in cell 19. The two figures coincide, and cell 40 cites no id for its own figure and places it on the generator's cohort.
- Civilian data read as military: HOLDS (cells 40 and 41; rules.py lines 164 to 213). The only source the changed lines cite is E-09's military registry (JTTR). No civilian source is cited or applied to a military casualty.
- A diagnosis result read as a treatment result: HOLDS (cells 40 and 41). The changed sentence stands in axis 1 of the column headed "diagnosis: MPTT-24, figure (as published)" and in cell 40's paragraph on the diagnosis columns. Its share is of need for a life-saving intervention, the diagnosis target, not of significant bleeding, the treatment column's target. The treatment column is unchanged and carries no share from `need_shares`.

## Numbers and their evidence ids

- 16.7%, cells 40 and 41 (rules.py lines 174 and 199): HOLDS. 16,704 of 100,000, recomputed inline. It is a generator figure, labelled as mechanism, and carries no evidence id, nor needs one. It agrees with limit 3 of the review at 83743ee ("16.7% of the 100,000 need an intervention"). It is a different quantity from E-11's 16.7% in cell 19.
- 26.5%, cells 40 and 41 (rules.py line 174; baseline.py lines 194 to 202): HOLDS. 15,016 of 56,634, recomputed inline, as cell 12 prints.
- 47.6%, cells 40 and 41 (rules.py lines 145 and 186): HOLDS. E-09's JTTR row reads "47.6% Priority 1", and the sentence quotes it as Priority 1, not as need.
- 50.2%, the battle branches (rules.py lines 175 and 200): HOLDS. 15,016 of 29,925, recomputed inline. It is D-33's figure, and the same casualties as axis 7's "a share of 0.502 need it". No cell of this notebook prints the branch.
- `share`, rules.py line 209: HOLDS. It is printed to one place like the other shares, and "all of whom" is given only when the share is exactly 1.
- 60.0% and 78.6%, cell 41, axis 1: HOLDS. 0.59992 and 0.78558, recomputed with the rule coded inline.
- "(D-23)": HOLDS. D-23 is restated by D-33, which gives 50.2% for the battle casualties alone, 47.6% for E-09 and 26.5% for the injured, and asks each scorecard's sentence to name its group and give that group's share. The strings say no more.

## The generator and the graph

- "On every stream of the military cohort, 16.7% of casualties need a life-saving intervention", cells 40 and 41: HOLDS (rules.py lines 171 to 174 and 199; baseline.py lines 166 to 169). `need_shares` draws `baseline.generator_sample("pre_hospital", "military")`: 100,000 casualties at seed 42 over the battle, non-battle and disease streams. It takes the mean of `needs_lsi` over all of them.
- "The comparison with E-09 holds for the injured only, of whom 26.5% need one ... so the generator's injured are a milder cohort than the one the rule was validated on", cells 40 and 41: HOLDS (rules.py lines 190 to 196; baseline.py lines 77 and 194 to 202). `calibration_need` takes `CALIBRATION_STREAMS`, battle and non-battle, the group `calibration_check` holds to E-09. `milder` compares 0.26514 with 0.476 at full precision.
- The battle branch: HOLDS (rules.py lines 200 to 203 and 208 to 210). "Of the battle casualties alone, 50.2% need a life-saving intervention ... so they are not a milder cohort" holds because `need[battle].mean()` is 0.50179, and 0.50179 is not below 0.476. "Of the injured as a whole, battle and non-battle" names `CALIBRATION_STREAMS`. Neither word depends on the seed: on each of seeds 43 to 62 the battle share is above 47.6% and the injured share below it.
- The "injured" and "every stream and battle" branches and the error message: HOLDS (rules.py lines 204 to 207 and 211 to 213). Each joins the clauses above and adds no claim.
- The docstrings of `need_shares` and `d23_sentence`: HOLDS (rules.py lines 168 to 170 and 181 to 185). The first describes lines 171 to 175: 100,000 synthetic casualties, seed 42, every stream, the injured (battle and non-battle) and the battle casualties alone. The second describes lines 186 to 213.
  - Called with `group="battle"` and the default `scored`, the function would say the figures are on every stream and then give only the battle share. Each clause would still be true, and no caller does so: each passes a battle group as `scored`.
  - No changed line says that need for an intervention occurs only among battle casualties, which is D-33's wording in `docs/DESIGN.md`. In the generator, 1,688 of the 43,366 disease casualties also need one (septic shock; generator.py lines 303 to 305), and the 16.7% counts them.
- The graph: HOLDS. No changed line concerns the graph.

## Standing lessons

Each lesson against the changed lines.

- Lesson 1: HOLDS. The registry figure, 47.6%, names its source and population in the same sentence: "Priority 1 in the military registry (E-09)". It is set beside the generator and not applied to the casualty. No civilian source is cited.
- Lesson 2: HOLDS. The change is this lesson's own: the sentence now gives the share in need of the group the figures are on, 16.7% of every stream, beside the injured's 26.5%. Each branch names its group: "every stream", "the injured as a whole, battle and non-battle", "the battle casualties alone". E-09's population is quoted as the register gives it, "47.6% Priority 1".
- Lesson 3: HOLDS. The panel is unchanged, and neither changed function reaches it.
- Lesson 4: HOLDS. "A milder cohort" and "not a milder cohort" are stated in words.
- Lesson 5: HOLDS. The shares follow the generator's assumed mix. They stand in a row headed "(mechanism)", under cell 40's unchanged "computed on the generator ... synthetic data can only confirm the model that made them".
- Lesson 6: HOLDS. No figure title changed.
- Lesson 7: HOLDS. The changed sentence sits in a diagnosis column and in the paragraph on the diagnosis columns.
- Lesson 8: HOLDS. No changed line calls any figure performance at the point of injury, and cell 40's next sentence says that none is.
- Lesson 9: HOLDS. The changed lines give shares, not counts, and "100,000" is exact.
- Lesson 10: HOLDS, as set out under the generator and the graph.
- Lesson 11: HOLDS. No changed line says where an item came from, what a source omits or forbids, or why anything was chosen.
- Lesson 12: HOLDS. The changed lines compare the generator's shares with a published figure. Across seeds 43 to 62 the battle share runs from 49.3% to 50.2% and the injured share from 25.9% to 26.6%. Neither range reaches 47.6%, so "milder" and "not milder" hold on every seed and neither is a tie.
- Lesson 13: HOLDS. No chance of death is given.
- Lesson 14: HOLDS. `milder` compares at full precision (line 191), and each share and the 47.6% beside it are displayed to one place.
- Lesson 15: HOLDS (cells 40 and 41; rules.py lines 200 to 212). The injured's "milder" reverses among the battle casualties alone: 50.2% against 47.6%, on every seed. The changed line confines "milder" to the injured, as before. The battle share stands in the same table, in axis 7's "a share of 0.502 need it", and in cell 40's first paragraph, "half of whom need an intervention". No line calls the battle casualties milder, and limit 6 of the review at 83743ee records the battle share. The module's battle branches state the reversal in a single sentence.
- Lesson 16: HOLDS. The changed sentence is D-23's statement as D-33 restates it. It stands in axis 1 of cell 41, beside the rule's accuracy on the generator, and in cell 40's paragraph on the diagnosis columns. It calls the injured milder and no group of battle casualties milder.
- Lesson 17: HOLDS. No learned model is concerned.

## Figures

- Every figure: HOLDS. No figure changed. The images of cells 3, 9, 16, 18, 23, 30, 33 and 39 are byte-identical to those at 0c69b05 and to the rerun, and no tag or `concludes` entry changed. The changed outputs are table entries, taken above.
- App page 1, the rules panel: HOLDS. `app/panels/rules.py` is unchanged, and `rules.page_panel` calls neither changed function.

## Limits

None recorded. A re-review after consolidation records no new limits (`docs/BUILD.md` section 5); the limits of the review committed at 83743ee stand as a record (D-31).

VERDICT: HOLDS

## Reviewed sources

- `notebooks/01_rules.ipynb` 144558dd779f66a5d656a51676120f7c1d5ffe4e903876c19de7e35ed0de803a
- `src/inference_labs/lenses/rules.py` 0df4eb43f094dbbb0a881ba5b199eb974400862f756826e356dc340d49e79fd2
- `app/panels/rules.py` fb89ef560936cfc6c83a08a99c327ab9d110d346d11adc71f9cd05ead0f6b33e
