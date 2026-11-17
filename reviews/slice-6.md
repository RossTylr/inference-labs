# Review of slice 6: lens 05, Stochastic processes

**Date:** 17 November 2026 · **Author:** Ross Taylor

Fourth review of slice 6, and the re-review after the final consolidation pass (commit 305c8a3, D-33), under `docs/BUILD.md` section 5 and D-31. The base is commit d3ee9b7, the last that changed this file; the third review it holds read the files at 3348a8e and found no breach. Only the lines changed between d3ee9b7 and the current head, 972aeaa, are checked, against every item below and each standing lesson in `docs/BUILD.md` section 8. Between d3ee9b7 and 972aeaa the review sources changed in commit 305c8a3 alone. A breach in a line unchanged since d3ee9b7 would be one the third review should have recorded, and would be marked MISSED. Cells are numbered from 0 in file order; the notebook has 41 cells. Line numbers are those of the file named, at 972aeaa.

What changed since d3ee9b7, in all:
- **Notebook.** Cell 21's last paragraph gains one sentence: "Each of those generator figures is an expectation summed over the casualties: the sum of their chances of a bleeding death with the drug over the same sum without it, where notebook 07's relative risks by band are counts of realised deaths." Cell 36's second paragraph replaces its D-23 sentence with D-33's: the scorecard's casualties, "all of whom need a life-saving intervention"; the battle casualties alone, 50.2% in need against 47.6% Priority 1 in the military registry (E-09), "not a milder cohort"; the injured as a whole, 26.5%, "a milder cohort (D-23)"; and "are not among them" becomes "are not among the scorecard's casualties". Cell 37's output changes in axis 1 of the figure column alone, which prints the new sentence. No other cell source or text output changes, and cell tags and notebook metadata are unchanged.
- **Lens module.** Lines 810 to 812: `in_need`, the share needing a life-saving intervention among the scorecard's casualties, is new, and `d23` now calls `rules.d23_sentence` with `group="battle"` and `share=in_need`. Nothing else changes.
- **Panel.** `app/panels/stochastic.py` is unchanged, as are `panel` and `page_panel` (stochastic.py lines 869 to 908) and every function and constant they call. `bayesian.py`, `decision.py`, `generator.py` and `params.yaml` are unchanged since d3ee9b7; `baseline.py` changes only in `calibration_check`, which nothing in this slice calls.
- **Background file.** Unchanged since d3ee9b7.

The helpers the changed lines call were read: `rules.py` lines 145 (E-09's 0.476) and 164 to 213 (`D23_GROUPS`, `need_shares`, `d23_sentence`); `baseline.py` lines 167 to 202; `generator.py` lines 305 and 361 to 377; `decision.py` lines 452 to 455; and `stochastic.py` lines 325 to 341 (`at_care`, `_sample`). For cell 21's sentence, `stochastic.py` lines 477 to 498 (`band_check`), `causal.py` lines 175 to 243 and 256 to 274, and the band tables of notebook 07, cell 25, were read. The register row E-09, and D-23 and D-33 in `docs/DESIGN.md`, were opened.

The notebook was run top to bottom from a fresh kernel into a scratch copy in 28.2 seconds without error. Its text outputs and its nine images match the committed file byte for byte, and the nine images are byte-identical to those at d3ee9b7. Gates G-6 and G-10, called on their own without writing, pass. The changed figures were recomputed at full precision from the seed-42 sample, from seeds 43 to 62, 100,000 casualties each, and by mechanism.

No breach is found, and none is missed.

## What must not be claimed

- That E-85's timings apply from the moment of wounding: HOLDS (cell 21, last paragraph; cell 36, second paragraph; cell 37, axis 1 of the figure column; stochastic.py lines 810 to 812). No changed line cites E-85 or gives a time of death.
- That the mandate caused the fall in E-81: HOLDS (the same lines). No changed line cites E-81, the sixty-minute mandate or killed in action.
- That the 10% per 15 minutes figure is a trauma-only estimate (E-26): HOLDS (the same lines). The new sentence in cell 21 does not cite E-24 or the decline per 15 minutes; the paragraph's unchanged "against E-24's about 10%" follows the same cell's "The 10% per 15 minutes is not a trauma-only figure."

The changed lines carry lens 01's rule and name notebook 07, and were also read against those background files' lists:

- That a rule's published accuracy is a property of the rule, and that the MPTT-24 has been validated on pre-hospital observations (lens 01): HOLDS (cells 36 and 37; stochastic.py lines 810 to 812). No changed line quotes the MPTT-24's published accuracy or says on what observations it was validated; E-09 is cited for its registry's share at Priority 1 only, and "the one the rule was validated on" names a cohort.
- That MATTERs is wrong, that the mandate caused the fall in deaths, or that the plasma trials disagree because of transport time (lens 07): HOLDS (cell 21). The sentence names only how notebook 07's relative risks are counted.
- The lists of 00, 02, 03, 04, 06 and 08 to 11: HOLDS (changed lines only). No changed line uses the 44% attribution, US outcome figures, over-triage, a posterior, CRASH-3, PECARN, a forest, a network, a graph, E-86, a learned policy, the civilian benchmark, an exchange rate between a miss and a false alarm, a conformal set or a language model.

## Epistemic checks

- Accuracy quoted for the wrong cohort or setting: HOLDS (cell 36; cell 37, axis 1 of the figure column; stochastic.py lines 810 to 812). The rule's accuracy beside the sentence, sensitivity 62.0% and specificity 38.3%, is on the 10,352 battle casualties bleeding significantly and alive at pre-hospital care, which the sentence names, with their share in need. Each share is given for the group it is measured on: 50.2% for the 29,925 battle casualties of the seed-42 sample, 26.5% for its 56,634 injured. No changed line quotes E-09's accuracy for any cohort.
- Proxy data read as the real thing: HOLDS (cells 21, 36 and 37). The 50.2%, the 26.5% and the share of all are the generator's, in a row labelled mechanism and a paragraph on the 100,000 synthetic casualties, and the 26.5% is called "the generator's injured"; the only published figure is E-09's 47.6%, set beside them as a comparison of cohorts. Cell 21's sentence concerns the generator's figures and notebook 07's, both from the generator.
- Civilian data read as military: HOLDS (cells 21, 36 and 37). The only source cited in the changed lines is E-09 for "the military registry", the JTTR row of its source; cell 21's new sentence cites no source, and the same cell already calls CRASH-2 civilian and its application to a battle casualty an assumption. G-10 passes.
- Diagnosis result read as a treatment result: HOLDS (cells 21, 36 and 37). Cell 21's sentence sits in the treatment section, under its statement that the treatment results are kept apart, and concerns the drug's relative risks; the D-23 sentence sits in the diagnosis paragraph of cell 36 and in the rule's column of axis 1, and concerns only who needs a life-saving intervention.

## Numbers traced to the evidence register

- E-09 (cell 36; cell 37, axis 1 of the figure column): HOLDS. The row gives 47.6% Priority 1 among the JTTR's 3,654 adults; the sentence takes it from `PUBLISHED["MPTT-24, military"]` (rules.py line 145).
- D-33 and D-23 (the same lines): HOLDS. D-33 gives the battle casualties alone 50.2% against E-09's 47.6% and the injured 26.5%, and says that no scorecard of battle casualties alone calls them milder; D-23 gives the injured 26.5% against 47.6%. Recomputed on seed 42: `need_shares` gives 0.50179 for the battle casualties, 15,016 of 29,925, and 0.26514 for the injured; `in_need` on the scorecard's 10,352 casualties is exactly 1.0.
- Cell 21's new sentence holds no number. The generator figures it describes, 0.683, 0.791 and 1.439 in cell 22, are unchanged.

## Sentences about the generator

- Cell 21, "an expectation summed over the casualties: the sum of their chances of a bleeding death with the drug over the same sum without it": HOLDS. The generator column of `band_check` is `p1[m].sum() / p0[m].sum()` (stochastic.py line 497), where `p0` and `p1` are the generator's chances of a bleeding death without the drug and with it (generator.py lines 367 and 368), on the casualties of `_sample`. The chances are the generator's from injury, not conditional on being alive at pre-hospital care. The ratio is what is shown: the generator multiplies each chance by the relative risk at the casualty's delay, and draws the time of death apart from whether death occurs (line 372), so each casualty's ratio is the same with chances conditional on being alive then and only the weights in the sums change. So conditioned, the bands read 0.682, 0.785 and 1.439, against the printed 0.683, 0.791 and 1.439, and cell 21's account of the generator stands.
- Cell 21, "notebook 07's relative risks by band are counts of realised deaths": HOLDS. Notebook 07's cell 25 gives a relative risk for every delay and each band for four readings. The true value and the naive reading are ratios of counts of the generator's drawn outcomes (causal.py lines 175 to 181, 220 to 230), and the two adjusted readings are ratios of inverse-probability-weighted counts of the same drawn deaths (lines 238 to 243). The true values by band, 0.68, 0.77 and 1.17, are 633 deaths with the drug against 932 without, 447 against 579, and 7 against 6; every one of them falls among the same 10,352 casualties bleeding significantly, within notebook 07's 29,443.
- Cell 36 and cell 37, "all of whom need a life-saving intervention": HOLDS. The generator sets need for a life-saving intervention for every casualty bleeding significantly (generator.py line 305), and `_sample` keeps only such casualties (stochastic.py lines 325 to 341), so `in_need` is 1 and `d23_sentence` takes its "all of whom" branch (rules.py line 209).
- Cell 36 and cell 37, the battle casualties alone and the injured as a whole: HOLDS. `need_shares` reads the same seed-42 sample of 100,000 (rules.py lines 167 to 175); its battle share is taken over the stream `battle`, and its injured share is `calibration_need`, over the streams `battle` and `non_battle` (baseline.py lines 194 to 202). "Not a milder cohort" and "a milder cohort" come from `milder`, which compares each share with 0.476 (rules.py lines 190 to 191). Among the non-battle injured none is in need, so the injured are milder through their mix, as D-33 states.
- Cell 36, "not among the scorecard's casualties": HOLDS. The diagnosis and treatment columns are both on the 10,352 casualties of `_sample`, which `at_care` keeps only where `alive_at_triage` holds (decision.py lines 452 to 455); cell 37 prints that none of them died from bleeding before pre-hospital care.

## Standing lessons

- Lesson 1: HOLDS. E-09's figure is given with its id and its population, the military registry, and is not applied to the casualty.
- Lesson 2: HOLDS. The sentence names its group and gives that group's share, and gives each comparison's group: the battle casualties alone and the injured as a whole, battle and non-battle. The registry's population is quoted as "Priority 1 in the military registry", as the row gives it.
- Lesson 3: HOLDS. The app shows none of the changed strings: nothing under `app/` calls `seven_axes` or `d23_sentence` for this lens; the lens 05 page shows only the notebook's cells tagged explainer and its central figure, and the gallery its images, none of which changed (`pages.py` lines 365 to 446); and the panel and everything it calls are unchanged.
- Lesson 4: HOLDS. No changed line states a harm or a negative result; cell 21's harm after 3 hours stays in words.
- Lesson 5: HOLDS. No changed figure is driven by a prior or an assumption; the shares in need are the generator's and sit in a row labelled mechanism.
- Lesson 6: HOLDS. No figure title changed.
- Lesson 7: HOLDS. Cell 21's sentence is in the treatment section and the D-23 sentence in the diagnosis paragraph and the rule's column.
- Lesson 8: HOLDS. No changed line concerns hospital observations or the scan.
- Lesson 9: HOLDS. No changed line gives a count; the shares are percentages of the groups named.
- Lesson 10: HOLDS, as set out under the sentences about the generator.
- Lesson 11: HOLDS. No changed line says where the rule's items came from, what a source omits or why anything was chosen.
- Lesson 12: HOLDS. Across seeds 43 to 62 the battle casualties' share in need runs from 49.3% to 50.2% and the injured's from 25.9% to 26.6%; neither crosses 47.6%, so neither comparison is a tie.
- Lesson 13: HOLDS. No changed line reports a chance of death. Cell 21's sentence names the chances inside a relative risk; as set out above, the ratio for each casualty is the same with chances conditional on being alive at pre-hospital care.
- Lesson 14: HOLDS. `milder` compares each share with 0.476 at full precision, and `in_need` is compared with 1 exactly; the shares print to one decimal place alike, 50.2%, 26.5% and 47.6%.
- Lesson 15: HOLDS. The comparison with E-09 reverses for the battle casualties alone, and the sentence now shows that subgroup. Among the battle casualties no mechanism falls below 47.6% (explosion 50.7%, other 48.8%, small arms 49.8%). Among the injured, those hurt by explosion are at 49.9%; they are 15,268 battle casualties and 231 non-battle, the subgroup already shown. E-09 gives no share by mechanism.
- Lesson 16: HOLDS. The sentence stands in cell 36 and in axis 1 of the figure column, where the rule's accuracy on the generator is quoted, and still says the generator's injured are a milder cohort than the registry's; it calls the battle casualties alone not milder, as D-33 requires.
- Lesson 17: HOLDS. No learned model is in the changed lines.

## Figures

- The nine figures (cells 3, 9, 13, 16, 19, 23, 27, 30 and 33): HOLDS. Each source, title and `concludes:` tag is unchanged since d3ee9b7, and each image is byte-identical to that at d3ee9b7.
- App page 1, the stochastic panel: HOLDS. It holds no figure and is unchanged.

## Strings the lens module returns, and the panel

- `seven_axes`, axis 1 of the figure column (lines 810 to 818): HOLDS. Read as printed in cell 37. With `group="battle"`, `d23_sentence` can return "all of whom", "of whom" a share, or no share; only "all of whom" is reached, since every casualty of `_sample` is in need. `milder` returns "not a milder cohort" for the battle share and "a milder cohort" for the injured, each matching its comparison; the other outcome of each would also match its condition.
- The panel's heading, clock, risk, treatment and truth lines (lines 869 to 908; app/panels/stochastic.py lines 9 to 15): HOLDS. Unchanged, and their inputs are drawn as before.

## Limits

None recorded. A re-review after consolidation records no new limits (`docs/BUILD.md` section 5); the limits of the review committed at b9ae1de stand as a record (D-31).

VERDICT: HOLDS

## Reviewed sources

- `notebooks/05_stochastic.ipynb` ef96b79b4998d47afac42a1443e7c4506045a129a75fee08e9d5842ff6ecb19c
- `src/inference_labs/lenses/stochastic.py` 45e6ba32c2de0d0f14a18d7df7dd63559504722ebbb8551fc540fbbc1815fc9c
- `app/panels/stochastic.py` be84e2a540da721d98b38005088d103671219d294de577e6e6a0069b09bcc532
