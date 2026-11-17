# Review of slice 7: lens 07, Causal inference

**Date:** 17 November 2026 · **Author:** Ross Taylor

Fifth review of slice 7, and the re-review after the final consolidation pass (commit 305c8a3, D-33), under `docs/BUILD.md` section 5 and D-31. The base is commit 232c148, the last that changed this file; the fourth review it holds read the files at 4e8d55f and found no breach. Only the lines changed between 232c148 and the current head, a114f94, are checked, against every item below and each standing lesson in `docs/BUILD.md` section 8. Between 232c148 and a114f94 the review sources changed in commit 305c8a3 alone. A breach in a line unchanged since 232c148 would be one the fourth review should have recorded, and would be marked MISSED. Cells are numbered from 0 in file order; the notebook has 42 cells. Line numbers are those of the file named, at a114f94.

What changed since 232c148, in all:
- **Notebook.** Cell 37's second paragraph replaces its D-23 sentence with D-33's. Where it read "; the comparison with E-09 holds for the injured only, of whom 26.5% need a life-saving intervention against 47.6% Priority 1 in the military registry (E-09), so the generator's injured are a milder cohort than the one the rule was validated on (D-23).", it now reads ". Of the battle casualties alone, 50.2% need a life-saving intervention against 47.6% Priority 1 in the military registry (E-09), so they are not a milder cohort than the one the rule was validated on; of the injured as a whole, battle and non-battle, 26.5% need one, so the generator's injured are a milder cohort (D-23)." Cell 38's output changes in axis 1 of the figure column alone, in both its HTML and its plain-text table, which print the same sentence; the plain-text table's other rows change only in padding. No other cell source or text output changes, and the cell tags, `concludes:` tags and the notebook's evidence list are unchanged.
- **Lens module.** Line 629: `d23` now calls `rules.d23_sentence` with `group="battle"`. Nothing else changes. Of the library functions `causal.py` calls, only `rules.d23_sentence` changed; `baseline.py` changes only in `calibration_check`, which this slice does not call, and `decision.py`, `generator.py` and `params.yaml` are unchanged.
- **Panel.** `app/panels/causal.py` is unchanged, and `panel` and `page_panel` do not call `d23_sentence`. Rendered for all 1,736 casualties app page 1 can show, from the package at 232c148 and at a114f94, the panel is identical.
- **Background file and register.** `docs/background/07-causal.md`, PRD sections 6.0 and 6.7, `docs/BUILD.md` and `docs/EVIDENCE.md` are unchanged since 232c148.

The helpers the changed lines call were read: `rules.py` lines 145 (E-09's 0.476) and 164 to 213 (`D23_GROUPS`, `need_shares`, `d23_sentence`); `baseline.py` lines 77, 167 to 169 and 194 to 202 (`CALIBRATION_STREAMS`, `generator_sample`, `calibration_cohort`, `calibration_need`); `causal.py` lines 116 to 119 (`_sample`) and 410 to 431 (`scan_accuracy`); and `generator.py` lines 300 to 305 (`needs_lsi`). The register row E-09, D-23 and D-33 in `docs/DESIGN.md`, and the population `library/curated.yaml` records for `vassallo2017d`, were opened.

The notebook was run top to bottom from a fresh kernel into a scratch copy in 9.8 seconds without error. Its text outputs and its seven images match the committed file byte for byte, and the seven images are byte-identical to those at 232c148. Gates G-6, G-8 and G-10, called on their own without writing, pass. The changed figures were recomputed at full precision from the seed-42 sample and from seeds 43 to 62, 100,000 casualties each.

No breach is found, and none is missed.

## What must not be claimed

- That MATTERs is wrong: HOLDS (cell 37, second paragraph; cell 38, axis 1 of the figure column; causal.py line 629). No changed line names MATTERs or E-71.
- That the sixty-minute mandate caused the fall in deaths, or that the 44.2% is measured: HOLDS (the same lines). No changed line cites E-81, E-82, E-123, the mandate, killed in action or the 44.2%.
- That the plasma trials disagree because of transport time: HOLDS (the same lines). No changed line cites a plasma trial, E-80 or transport time.

The changed lines carry lens 01's rule, and were also read against that background file's list and the others:

- That a rule's published accuracy is a property of the rule, and that the MPTT-24 has been validated on pre-hospital observations (lens 01): HOLDS (cells 37 and 38; causal.py line 629). No changed line quotes the MPTT-24's published accuracy or says on what observations it was validated; E-09 is cited for its registry's share at Priority 1 only, and "the one the rule was validated on" names a single cohort, D-23's words.
- The lists of 00, 02, 03, 04, 05, 06 and 08 to 11: HOLDS (changed lines only). No changed line uses the 44% attribution, US outcome figures, COMBAT or PAMPer, over-triage, a posterior, CRASH-3, PECARN, a forest, a network, E-85, E-26, the mandate, a graph, E-86, a learned policy, CLOVERS, the civilian benchmark, PATCH, an exchange rate between a miss and a false alarm, a conformal set or a language model.

## Epistemic checks

- Accuracy quoted for the wrong cohort or setting: HOLDS (cell 37; cell 38, axis 1 of the figure column; causal.py lines 629 and 656). The rule's accuracy beside the sentence, sensitivity 57.1% and specificity 57.4% for free fluid, is on the 29,925 battle casualties of the seed-42 military sample (`scan_accuracy`, lines 416 to 417, through `_sample` and `baseline.generator_sample`), and the sentence's 50.2% is measured on the same 29,925 (`need_shares`, rules.py lines 167 to 175). The 26.5% is given for the 56,634 injured of that sample, battle and non-battle, and is called theirs. No changed line quotes E-09's accuracy for any cohort, and none concerns setting.
- Proxy data read as the real thing: HOLDS (cells 37 and 38). The 50.2% and 26.5% are the generator's: the paragraph is on "the 100,000 synthetic casualties (seed 42)", the row is labelled mechanism beside "29,925 synthetic battle casualties", and the 26.5% is "the generator's injured". The only published figure is E-09's 47.6%, set beside them as a comparison of cohorts, not as a figure about the generator.
- Civilian data read as military: HOLDS (cells 37 and 38). The only source cited in the changed lines is E-09, for "the military registry", the JTTR row of a source `library/curated.yaml` records as mixed; its civilian TARN row is not used. G-10 passes.
- Diagnosis result read as a treatment result: HOLDS (cells 37 and 38). The sentence sits in the paragraph on the diagnosis and baseline columns, before the treatment column is introduced, and in the rule's column of axis 1; it concerns only who needs a life-saving intervention. The treatment column's text is unchanged.

## Numbers traced to the evidence register

- E-09 (cell 37; cell 38, axis 1 of the figure column): HOLDS. The row gives 47.6% Priority 1 among the JTTR's 3,654 adults, 2006 to 2013; the sentence takes it from `PUBLISHED["MPTT-24, military"]`, which holds 0.476 citing E-09 (rules.py line 145).
- D-23 and D-33 (the same lines): HOLDS. D-33 gives battle casualties alone 50.2% in need against the registry's 47.6% (E-09) and the injured, battle and non-battle, 26.5%, and says no scorecard of battle casualties alone calls them milder; the sentence gives both figures, calls the battle casualties not milder and the injured milder, and cites D-23, which D-33 restates.
- The generator's figures: HOLDS. In the seed-42 sample 15,016 of the 29,925 battle casualties need a life-saving intervention, 0.50179, printed 50.2%; 15,016 of the 56,634 injured (29,925 battle and 26,709 non-battle, none of whom needs one), 0.26514, printed 26.5%. Across seeds 43 to 62 the battle share runs from 49.3% to 50.2% and the injured share from 25.9% to 26.6%.

## Sentences about the generator and the graph

- "The scorecard's figures are on the battle casualties of the military cohort": HOLDS. Its words are unchanged; it now ends at a full stop. The diagnosis and baseline columns take the battle casualties of `baseline.generator_sample("pre_hospital")`, whose cohort is military by default (baseline.py lines 167 to 169; causal.py lines 116 to 119 and 416 to 417).
- "Of the battle casualties alone, 50.2% need a life-saving intervention": HOLDS. `need_shares` takes `needs_lsi` among stream `battle` of the same seed-42 military sample (rules.py lines 167 to 175); `needs_lsi` is significant bleeding, tension pneumothorax, severe head injury or septic shock (generator.py line 305). The setting changes only the scan, so the share is the same for axis 6's sample in hospital.
- "so they are not a milder cohort than the one the rule was validated on": HOLDS. `milder` compares 0.50179 with 0.476 at full precision (rules.py lines 190 to 191); the battle share is above 47.6% on every seed from 43 to 62.
- "of the injured as a whole, battle and non-battle, 26.5% need one, so the generator's injured are a milder cohort (D-23)": HOLDS. "The injured" are the streams `battle` and `non_battle` (baseline.py line 77); the 26.5% is `calibration_need("military")` (lines 199 to 202), below 47.6% on every seed from 43 to 62. The sentence does not repeat D-33's "occurs only among battle casualties"; in the generator 1,688 of the 43,366 disease casualties need one through septic shock (generator.py lines 303 to 305), and the sentence claims nothing of them.
- Cell 37's capitals after "(D-24);" and "on the generator:" are unchanged, as the fourth review recorded.

## Standing lessons

- Lesson 1: HOLDS. E-09 is named with its id and its population, the military registry, in the same sentence; it is set beside the generator's cohorts, not applied to the casualty.
- Lesson 2: HOLDS. Each share names its group: "the battle casualties alone" and "the injured as a whole, battle and non-battle"; E-09's 47.6% is "Priority 1 in the military registry", as its row gives it.
- Lesson 3: HOLDS. No number on the app changes: the panel is identical on all 1,736 entries, and nothing under `app/` calls `causal.seven_axes`. G-8 passes.
- Lesson 4: HOLDS. "Not a milder cohort" and "a milder cohort" are stated in words.
- Lesson 5: HOLDS. The shares are the generator's, in a row labelled mechanism; no prior enters them.
- Lesson 6: HOLDS. No figure changes.
- Lesson 7: HOLDS. The sentence stays in the diagnosis paragraph and the rule's column; the treatment column is unchanged.
- Lesson 8: HOLDS. E-09 was measured on hospital observations; the changed lines quote only its share at Priority 1 and call nothing performance at the point of injury.
- Lesson 9: HOLDS. The changed lines give shares, not counts.
- Lesson 10: HOLDS, as set out under the sentences about the generator.
- Lesson 11: HOLDS. "The one the rule was validated on" is D-23's; no changed line says why anything was chosen or what a source omits or forbids.
- Lesson 12: HOLDS. The battle share is above 47.6% and the injured share below it on every seed from 43 to 62; neither comparison is a tie, and "not a milder cohort" would hold of a tie.
- Lesson 13: HOLDS. No chance of death is in the changed lines.
- Lesson 14: HOLDS. 0.50179 and 0.26514 are compared with 0.476 at full precision and printed to one decimal alike.
- Lesson 15: HOLDS. The injured as a whole are milder and the battle casualties within them are not; the subgroup is shown in the same sentence as the whole.
- Lesson 16: HOLDS. The D-23 sentence stands in cell 37 and in axis 1 of the figure column, where the rule's accuracy on the generator is quoted, and says the generator's injured are a milder cohort; the scorecard's own group, the battle casualties, is not called milder, as D-33 requires.
- Lesson 17: HOLDS. No learned model is in the changed lines.

## Figures

- The seven figures (cells 3, 10, 16, 26, 28, 32 and 35): HOLDS. Each source, title and `concludes:` tag is unchanged since 232c148, and each image is byte-identical to that at 232c148. Cell 38's scorecard is a table, not a figure.
- App page 1, the causal panel: HOLDS. It holds no figure.

## Strings the lens module returns, and the panel

- `seven_axes`, axis 1 of the figure column (lines 629 and 656): HOLDS, as set out above. With `group="battle"` and no `share`, `d23_sentence` returns the subject, the group and the battle clause (rules.py lines 200 to 210); the notebook prints it word for word.
- Every other string `causal.py` can return: HOLDS. Their source lines and every function they call are unchanged since 232c148, and cell 38's other entries print as before.
- `app/panels/causal.py`: HOLDS. Unchanged: one subheader and four markdown lines, each the library's string, identical on all 1,736 entries at 232c148 and a114f94.

## Limits

None recorded. A re-review after consolidation records no new limits (`docs/BUILD.md` section 5); the limits of the review committed at da34e41 stand as a record (D-31).

VERDICT: HOLDS

## Reviewed sources

- `notebooks/07_causal.ipynb` d24d32adcfa348e1044b3083a30e9a82a7d1b1591d96383b17b37226a9a4db87
- `src/inference_labs/lenses/causal.py` c4a6fa4e3b6ef268939d5c4d879c93abbfcda11e6c15a04ecd53eea2da73c01b
- `app/panels/causal.py` 81b97a554414318751e31de9d4a6fdc7daa012dd00427d4a8281e82e04340e97
