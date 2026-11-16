# Review of slice 6: lens 05, Stochastic processes

**Date:** 15 November 2026 · **Author:** Ross Taylor

Third review of slice 6, and the first re-review after the consolidation after slice 8 (commit 7f59d45), under `docs/BUILD.md` section 5 and D-31. The base is commit b9ae1de, the last that changed this file; the second review it holds read the files at d9477b5 and found no breach. Only the lines changed between b9ae1de and the current head, 3348a8e, are checked, against every item below and each standing lesson in `docs/BUILD.md` section 8. Between b9ae1de and 3348a8e the review sources changed in commit 7f59d45 alone. A breach in a line unchanged since b9ae1de would be one the second review should have recorded, and would be marked MISSED. Cells are numbered from 0 in file order; the notebook has 41 cells. Line numbers are those of the file named, at 3348a8e.

What changed since b9ae1de, in all:
- **Notebook.** Cell 22 renames E-22's two columns "E-22 (CRASH-2, civilian)" and "E-22 (CRASH-2, civilian) interval"; its figures are unchanged. Cell 23 adds "(CRASH-2, civilian)" to the legend of the band after 3 hours and to the title; its `concludes:` tag is unchanged. Cell 36 gains E-93's account of net benefit, replaces its D-23 sentence (no longer citing E-01), and adds a sentence on casualties dead before pre-hospital care and one on the calibration rows. Cell 37 displays `seven_axes` and prints how many casualties dead before pre-hospital care the diagnosis column holds; its table gains "where lower is better" in axis 2, the new D-23 sentence in axis 1 of the figure column, "flag every casualty" and "flag none" in axis 7, and CRASH-2 as a civilian trial in axis 3 of the treatment column. Cell 38's output renames the metrics of rows 2, 3, 6 and 7. Cell 39's diagnosis paragraph says "flagging none" for "treating none". The notebook's evidence list gains E-93.
- **Lens module.** Lines 101 to 104, `spread_words` now calls `decision.spread_words`; lines 391 to 412, `axis7` uses `decision.as_flag`, `decision.flag_all` and the naming constants `FLAG_ALL`, `FLAG_NONE`, `FLAGGING_ALL` and `FLAGGING_NONE`; lines 743 to 746, `DIAGNOSIS_METRICS`; in `seven_axes`, the `registry` line is removed, and lines 801 to 805 (`rule_cal`), 810 and 811 (`d23`, from `rules.d23_sentence`), 825 to 829 (axis 2 of the diagnosis column) and 836 (axis 3 of the treatment column) change.
- **Panel.** `app/panels/stochastic.py` is unchanged, as are `panel` and `page_panel` (stochastic.py lines 868 to 907) and every function and constant they call (lines 61 to 99, 109 to 173 and 417 to 465). The walk-through record and the bleeding flag they read are drawn as before (bayesian.py lines 620 to 627); the walk-through gains only `died_before_care`, which this panel does not read.
- **Background file.** In "Added from the full text", the E-77 row now gives "death, a component of the primary outcome, 43% against 45%", as the register does. "What must not be claimed" is unchanged.

The helpers the changed lines call were read: `decision.py` lines 57 to 63 and 91 to 128 (`FLAG_ALL`, `FLAGGING_ALL`, `NET_BENEFIT_MEANING`, `net_benefit`, `flag_all`, `as_flag`, `spread_words`) and 452 to 455 (`alive_at_triage`); `rules.py` lines 164 to 172 (`d23_sentence`); `baseline.py` lines 77, 152 to 163 and 172 to 202 (`flag_metrics`, `died_before_care`, `died_before_care_count`, `died_before_care_note`, `calibration_cohort`, `calibration_need`); and `generator.py` lines 361 to 377. The register rows E-09, E-22 and E-93, D-23 and D-26 in `docs/DESIGN.md`, and the populations `library/curated.yaml` records for `crash2_2011`, `vassallo2017d` and `vickers2006` were opened.

The notebook was run top to bottom from a fresh kernel into a scratch copy in 28.3 seconds without error. Its text outputs and its nine images match the committed file byte for byte; against b9ae1de only cell 23's image differs. Gates G-6 and G-10, called on their own without writing, pass. Every figure in the changed lines was recomputed at full precision from the seed-42 sample and from seeds 43 to 62, 100,000 casualties each, and the changed axis 7 and calibration comparisons were recomputed by bleeding site and by mechanism.

No breach is found, and none is missed. The changed lines take up three of the second review's limits: axis 7 and cell 39 now name flagging every casualty and flagging none, not treating; the calibration rows' name now says what the baseline figure is; and the background file's RePHILL row now agrees with E-77.

## What must not be claimed

- That E-85's timings apply from the moment of wounding: HOLDS (changed lines of cells 22, 23 and 36 to 39; stochastic.py lines 101 to 104, 391 to 412, 743 to 746, 801 to 811, 825 to 829 and 836). No changed line cites E-85 or gives a time of death; axis 4 of the diagnosis column, which carries E-85 with its clock and its population, is unchanged.
- That the mandate caused the fall in E-81: HOLDS (the same lines). No changed line cites E-81, the sixty-minute mandate or killed in action.
- That the 10% per 15 minutes figure is a trauma-only estimate (E-26): HOLDS (the same lines). No changed line cites E-24 or the decline per 15 minutes; axis 4 of the treatment column, with E-26, is unchanged.

The changed lines carry lens 10's net benefit and lens 01's rule, and were also read against those background files' lists:

- A specific exchange rate between a miss and a false alarm (lens 10): HOLDS (cell 36; cell 37, axis 7; stochastic.py lines 409 to 412). Cell 36 says only that the threshold "encodes how a false alarm is weighed against a miss (E-93)"; axis 7's weight of nine is "(an assumption)" in every entry, as before.
- That a rule's published accuracy is a property of the rule, and that the MPTT-24 has been validated on pre-hospital observations (lens 01): HOLDS (cells 36 and 37). No changed line quotes the MPTT-24's published accuracy or says on what observations it was validated; E-09 is cited for its registry's share at Priority 1 only.
- The lists of 00, 02, 03, 04 and 06 to 11: HOLDS (changed lines only). No changed line uses the 44% attribution, US outcome figures, over-triage, a posterior, CRASH-3, PECARN, a forest, a network, MATTERs, a graph, E-86, a learned policy, a conformal set or a language model.

## Epistemic checks

- Accuracy quoted for the wrong cohort or setting: HOLDS (cells 36, 37 and 39; stochastic.py lines 801 to 811 and 825 to 829; rules.py lines 164 to 172). The new D-23 sentence names both groups: "The scorecard's figures are on the battle casualties of the military cohort bleeding significantly and alive at pre-hospital care", which is the group of every row of cells 37 and 38 in both settings (`_sample`, lines 336 to 341, through `at_care`, lines 329 to 333; 10,352 in each), and "the comparison with E-09 holds for the injured only", the battle and non-battle injuries of the seed-42 sample (`calibration_cohort`, baseline.py lines 77 and 194 to 196), of whom 26.5% need a life-saving intervention. Cell 39's "on every one of 20 samples" is on the same group in each further sample.
- Proxy data read as the real thing: HOLDS (cells 36, 37 and 39). The new figures are the generator's, in rows or entries labelled mechanism; the printed count of casualties dead before pre-hospital care is the generator's, and the only published figures in the changed lines are E-09's 47.6%, set beside the generator's 26.5% as a comparison of cohorts, and E-22's bands, relabelled but not recomputed.
- Civilian data read as military: HOLDS (cells 22, 23 and 37; stochastic.py line 836). Each changed line that cites CRASH-2 now calls it civilian: cell 22's column labels, cell 23's title and the legend of the band after 3 hours, and axis 3 of the treatment column, "E-22's bands, from CRASH-2, a civilian trial"; `library/curated.yaml` records `crash2_2011` as civilian. Cell 21, unchanged, calls applying them to a battle casualty an assumption. E-09 is cited for "the military registry", the JTTR row of a source recorded as mixed; E-93 concerns a method. G-10 passes.
- Diagnosis result read as a treatment result: HOLDS (cells 36, 37 and 39; stochastic.py lines 391 to 412). Axis 7's references, and cell 39's, are now "flag every casualty", "flag none" and "flagging none", which name flagging for death within the hour and no treatment; cell 36 defines them so. The treatment column's changed entry, axis 3, concerns the drug's bands only.

## Numbers traced to the evidence register

- E-93 (cell 36): HOLDS. The row: a model is judged by its consequences, by net benefit across threshold probabilities, the threshold encoding how a false positive is weighed against a false negative. The cell's computation "per 100 casualties as those correctly flagged less those wrongly flagged, the second weighted by the threshold over one minus it" is introduced as the notebook's own ("here it is computed"), and is `decision.net_benefit` (lines 91 to 96).
- E-09 and D-23 (cell 36; cell 37, axis 1 of the figure column): HOLDS. E-09's row gives 47.6% Priority 1 among the JTTR's 3,654 adults; D-23 gives 26.5% against 47.6% citing E-09 alone, so dropping E-01 loses nothing. `calibration_need("military")` is 0.26514.
- E-22 (cells 22 and 23; cell 37, axis 3): HOLDS. The relabelled figures, 0.68 (0.57 to 0.82), 0.79 (0.64 to 0.97) and 1.44 (1.12 to 1.84), are the row's; the source is the exploratory analysis of CRASH-2.
- The figures in the changed entries of cells 37 and 38: HOLDS. Recomputed on seed 42: the rule's share flagged 61.68% less the share who die 4.24%, +0.57438, printed 0.574 in rows 3 and 7 of cell 38 and "57.4 points more" in axis 2; flagging every casualty -6.399 per 100, printed -6.4; the readings -3.9 and -4.0; the lens 0.0, flagging no casualty. The Brier scores, 0.0406, 0.607 and 0.611, and the spread of the Brier difference, -0.573 to -0.558, are as before.
- The count in cell 37: HOLDS. `at_care` keeps 10,352 casualties, and `died_before_care_count` on them is 0.
- Cell 39's diagnosis paragraph: HOLDS. The rule flags 61.7% of the casualties; its net benefit across seeds 43 to 62 runs from -4.21 to -3.58 per 100 under the figure reading (and -4.24 to -3.61 under the text reading), below zero on all 20; the lens's is 0.0 on all 20; sensitivity and specificity add to 1.003.

## Sentences about the generator

- Cell 36, net benefit: HOLDS. `net_benefit` is true positives less false positives times t over 1 - t, per casualty, multiplied by 100 in `axis7` (line 397); `flag_all` is the same for flagging everyone (decision.py lines 99 to 102); flagging none scores zero (line 412).
- Cell 36 and cell 37, casualties dead before pre-hospital care: HOLDS. `at_care` keeps the battle casualties bleeding significantly for whom `alive_at_triage` holds, that is, not `baseline.died_before_care`: a bleeding death without the drug at or before the time of pre-hospital care (baseline.py lines 172 to 176). Of the 10,834 bleeding significantly, 482 are removed. The generator's recorded outcome has 424 of them dead (generator.py line 377; the other 58 drew the drug), and none of either set is among the 10,352, so "are not among them" and "No casualty the generator has dead from bleeding before pre-hospital care is among the 10,352 casualties behind the diagnosis column" hold on either reading. The printed sentence is `died_before_care_note` (baseline.py lines 185 to 191).
- Cell 36, the D-23 sentence: HOLDS. "The injured" are the streams `battle` and `non_battle` (baseline.py line 77), on which D-23 states the comparison; the sentence takes its 26.5% from `calibration_need` and its 47.6% from `PUBLISHED["MPTT-24, military"]` (rules.py line 145).
- Cell 36, the calibration rows: HOLDS. The lens's row is its mean chance less the share who die (line 384); the baseline's is `flag_metrics`' share flagged less the share who die (baseline.py line 162), and the row's name now says so.
- Cell 36's other sentences: HOLDS. The target is death from bleeding without the drug within the hour after pre-hospital care (`next_hour_target`, lines 361 to 365); every row of cell 38 is labelled mechanism, fit weak for diagnosis and native for treatment, and the treatment rows carry no baseline.

## Standing lessons

- Lesson 1: HOLDS. Each changed line citing CRASH-2 names it civilian beside E-22's id; E-09's figure is given with its id and its population, the military registry, and is not applied to the casualty.
- Lesson 2: HOLDS. Each new figure names its group as set out under the first epistemic check; cell 37's count names "the 10,352 casualties behind the diagnosis column".
- Lesson 3: HOLDS. The app shows none of the changed strings: nothing under `app/` calls `seven_axes`, `axis7` or the scorecard, and the panel and everything it calls are unchanged.
- Lesson 4: HOLDS. Cell 23's changed legend keeps "below zero is harm"; every axis 7 entry says "worse than flagging none" in words.
- Lesson 5: HOLDS. Axis 7 keeps "(an assumption)" for its weighting.
- Lesson 6: HOLDS. Cell 23's title describes what is plotted.
- Lesson 7: HOLDS. The diagnosis and treatment columns, rows and paragraphs stay apart, and the diagnosis references no longer use the word treating.
- Lesson 8: HOLDS. No changed line concerns hospital observations or the scan.
- Lesson 9: HOLDS. "10,352", "100,000", "20 further samples" and "20 seeds" are exact.
- Lesson 10: HOLDS, as set out under the sentences about the generator.
- Lesson 11: HOLDS. E-93's row says net benefit judges a model by its consequences and what the threshold encodes; the scope of the comparison with E-09 is D-23's. No changed line says why anything was chosen.
- Lesson 12: HOLDS. Cell 39's "on every one of 20 samples" is borne out for both readings, and axis 7's lens-less-rule spread, +3.6 to +4.2 per 100, is unchanged. The changed comparisons with flagging none and flagging every casualty are no tie on seed 42 and across seeds.
- Lesson 13: HOLDS. The renamed rows keep "chance of dying from bleeding in the next hour ... alive at pre-hospital care".
- Lesson 14: HOLDS. `as_flag` compares a chance with the threshold at full precision (decision.py lines 105 to 108), as before; the threshold prints 0.10 throughout.
- Lesson 15: HOLDS (cell 37, axes 2 and 7). On seed 42, by bleeding site (extremity, junctional, truncal) and by mechanism (explosion, other, small arms), flagging every casualty stays below flagging none (-10.1, -5.2 and -1.3; -7.1, -7.8 and -5.4 per 100), each reading stays below flagging none (-6.4, -3.4 and -0.4; -4.4, -4.6 and -3.2 for the figure, the text within 0.1), each reading flags more than die in every group, and the lens flags no casualty in any. The scorecard reports no subgroup.
- Lesson 16: HOLDS. The D-23 sentence stands in cell 36 and in axis 1 of the figure column, where the rule's accuracy on the generator is quoted, and scopes "a milder cohort" to the injured.
- Lesson 17: HOLDS. No learned model is in the changed lines.

## Figures

- Cell 23: HOLDS. Only the title and the legend of the band after 3 hours change, each adding "(CRASH-2, civilian)"; the data, the harm label and the `concludes:` tag are unchanged. A reader concludes what the second review recorded, now knowing the bands' population from the figure itself.
- The other eight figures (cells 3, 9, 13, 16, 19, 27, 30 and 33): HOLDS. Each source, title and `concludes:` tag is unchanged since b9ae1de, and each image is byte-identical to that at b9ae1de.
- App page 1, the stochastic panel: HOLDS. It holds no figure and is unchanged.

## Strings the lens module returns, and the panel

- `spread_words` (stochastic.py lines 101 to 104): HOLDS. It passes its arguments to `decision.spread_words` (decision.py lines 120 to 128) in that function's order with "lower" and "higher", and returns the same strings as the code it replaces: the outputs of cells 5, 18, 25, 27, 30 and 33 are unchanged.
- `axis7` (lines 391 to 412): HOLDS. Every branch was read: "it flags no casualty at this threshold, so it scores exactly as flagging none", "it flags every casualty at this threshold, so it scores exactly as flagging every casualty", "worse than flagging none", "below flagging every casualty", "above flagging none, and at or above flagging every casualty" and "no better than flagging none" each match their conditions. "better than flagging none" for flagging every casualty would misstate a net benefit of exactly zero, which needs a share dying of exactly 0.10; the share here is 0.0424, and no call reaches it.
- `rule_cal` (lines 801 to 805): HOLDS. "where lower is better" is right of the Brier score. "fewer" at a gap of exactly zero is not reached: the gap is +0.574 and +0.579.
- `DIAGNOSIS_METRICS` and the scorecard's metric names (lines 743 to 752): HOLDS. "Brier score, where lower is better" and "mean chance minus observed share; for the baseline, share flagged minus observed share" name what rows 2, 3, 6 and 7 hold.
- `seven_axes`, the changed entries (lines 810 to 836): HOLDS. Axis 1 of the figure column, axis 2 of the diagnosis column, axis 3 of the treatment column and axis 7 of each diagnosis column were read as printed in cell 37.
- The panel's heading, clock, risk, treatment and truth lines (lines 868 to 907; app/panels/stochastic.py lines 9 to 15): HOLDS. Unchanged, and their inputs are drawn as before.

## Limits

None recorded. A re-review after consolidation records no new limits (`docs/BUILD.md` section 5); the limits of the review committed at b9ae1de stand as a record (D-31).

VERDICT: HOLDS

## Reviewed sources

- `notebooks/05_stochastic.ipynb` 0924950909aae412420284c27aed3b5808772fcce83b445e161ae047f4c0eaa0
- `src/inference_labs/lenses/stochastic.py` 4b4fce68e2dc4c5b0f26d83cff6ecc153d28b4079d1b51c398aa0aec903075f2
- `app/panels/stochastic.py` be84e2a540da721d98b38005088d103671219d294de577e6e6a0069b09bcc532
