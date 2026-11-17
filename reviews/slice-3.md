# Review of slice 3: lens 02, Frequentist and signal detection

**Date:** 17 November 2026 · **Author:** Ross Taylor

Tenth review, and a re-review after the final consolidation pass (commit 305c8a3, D-33), under `docs/BUILD.md` section 5. The base is commit 12b8df4, the last that changed this file; only the lines changed between 12b8df4 and the current head, 0922cfe, are checked, against every item below and each standing lesson in `docs/BUILD.md` section 8. Cells are numbered from 0 in file order; the notebook still has 33 cells. Line numbers are those of the file named, at 0922cfe.

What changed. Of the three review sources only the notebook has changed, in commit 305c8a3. In cells 4, 12, 15 and 28 one sentence each, D-23's statement, now reads "... On every stream of the military cohort, 16.7% of casualties need a life-saving intervention; the comparison with E-09 holds for the injured only, of whom 26.5% need one against 47.6% Priority 1 in the military registry (E-09), so the generator's injured are a milder cohort than the one the rule was validated on (D-23)": the share on every stream is new, and "need a life-saving intervention" after 26.5% has become "need one". In cell 29's output the same change, and only that, is in axis 1 of the baseline figure column; the other rows of that column differ only in the padding of the printed table. No other cell source, text output or image has changed. `src/inference_labs/lenses/frequentist.py` and `app/panels/frequentist.py` are byte-identical to 12b8df4, but both places the lens module calls `rules.d23_sentence`, line 515 (axis 1 of the scorecard) and lines 603 to 604 (the panel's "errors" string), now return the new sentence, because `rules.d23_sentence` was rewritten in 305c8a3 (rules.py lines 164 to 213) to take its shares from the new `need_shares`. The panel string is therefore a changed line a reader sees and is checked here, although no hash covers it. Of the other library code this slice draws on, only `baseline.calibration_check` and `decision.seven_axes` have also changed since 12b8df4; this slice calls neither. `generator.py`, `params.yaml` and `docs/background/02-frequentist.md` are unchanged since 12b8df4. A breach in any line not changed since 12b8df4 would be one the ninth review should have recorded, and would be marked MISSED.

The notebook was run top to bottom from a fresh kernel into a scratch copy in 7.7 seconds; its reader view, every cell source and text output, matched the committed file and gives the hash below, and each of the nine images matched it byte for byte and matches those at 12b8df4. Slice 3's tests pass (11). Gates G-6, G-8 and G-10, run on their own, pass. The panel was rendered for every patient type and setting: its "errors" string is the same in each and carries the new sentence. Every figure in the changed lines was recomputed at full precision from `generator.sample` on seed 42, 100,000 casualties of the military cohort, without `need_shares`, and on seeds 43 to 62, and the E-09 row of the register was opened again.

No breach is found and none is missed.

## What must not be claimed

- That transport time is the proven reason COMBAT and PAMPer differ: HOLDS (cells 4, 12, 15 and 28; cell 29, axis 1, figure column; frequentist.py lines 515 and 603 to 604). The changed sentence names no trial and says nothing of transport time.
- That over-triage means 1 minus specificity: HOLDS (the same lines). The changed sentence gives a share in need and a share in Priority 1; it uses neither "over-triage" nor "specificity".

The changed sentence quotes the rule's registry, so it was also read against the lists in the other background files:

- That a rule's published accuracy is a property of the rule (lens 01): HOLDS (the same lines). The sentence ties E-09 to its registry and says the generator's injured differ from it; it offers no accuracy as the rule's own.
- That the MPTT-24 has been validated on pre-hospital observations (lens 01): HOLDS (the same lines). "The one the rule was validated on" names a cohort, the military registry, and no setting.
- That US outcome figures describe UK casualties (lens 00): HOLDS (the same lines). E-09 is called the military registry and is set beside the generator's casualties only to say they differ.
- The lists of 03 to 11: HOLDS (the same lines). The changed sentence quotes no figure from those lenses' sources and names no posterior, tree, network, graph, learned policy, exchange rate or language model.

## Epistemic checks

- Accuracy quoted for the wrong cohort or setting: HOLDS (cells 4, 12, 15 and 28; cell 29, axis 1, figure column; frequentist.py lines 515 and 603 to 604). The new share names its casualties, "every stream of the military cohort", the 100,000 the figures beside it are on, which each preceding clause names; it is the share on every stream, 16,704 of 100,000, and not the injured or battle share. The same setting is used: the share in need does not change with the setting (0.16704 before hospital and in hospital). The injured share, 26.5%, still carries "the comparison with E-09 holds for the injured only".
- Proxy data read as the real thing: HOLDS (the same lines). 16.7% and 26.5% are the generator's synthetic casualties: in cell 4 after "every result on them is a **mechanism**" and "all 100,000 synthetic casualties"; in cell 12 after "how precisely the generator's own value is known"; in cell 15 after "the curve belongs to the generator"; in cell 28 after "all 100,000 synthetic casualties"; in cell 29 in the row "1 Discrimination (mechanism)"; on the panel after "all 100,000 synthetic casualties of the military cohort, disease included (mechanism)". The only published figure, 47.6%, carries E-09 and is said to belong to the registry.
- Civilian data read as military: HOLDS (the same lines). No civilian source or civilian cohort figure is in the changed sentence. In cell 12, the one changed cell that also covers the civilian cohort, the new share is said of "every stream of the military cohort". G-10 passes.
- A diagnosis result read as a treatment result: HOLDS (the same lines). The new share is the prevalence of the diagnosis target, need for a life-saving intervention; in cell 29 it stands in the baseline figure column of axis 1, and the treatment column of that axis is unchanged.

## Numbers and their evidence ids

- 16.7% on every stream (cells 4, 12, 15 and 28; cell 29, axis 1; panel, frequentist.py lines 603 to 604): HOLDS. No evidence id: a generator figure. On seed 42, 16,704 of the 100,000 need a life-saving intervention, 0.16704, printed 16.7%. On seeds 43 to 62 it runs from 16.4% to 16.9%. It agrees with the unchanged figures beside it: axis 7's "flag every casualty 7.4" is 16.704 less 83.296 over 9, and axis 2's 11.2 points flagged above need follows from 60.0% and 78.6% at this share.
- 26.5% among the injured: HOLDS. No evidence id; 15,016 of the 56,634 battle and non-battle casualties, 0.26514, unchanged in value from 12b8df4; 25.9% to 26.6% on seeds 43 to 62.
- 47.6% Priority 1 (E-09): HOLDS. The register row gives the JTTR, 3,654 adults, "47.6% Priority 1"; the sentence says Priority 1 in the military registry, as the register does, not "in need".
- D-23 and D-33: HOLDS. D-33 requires each scorecard's sentence to name the group it reports and give that group's share; this scorecard reports every stream of the military cohort and now gives 16.7%. It is not a scorecard of battle casualties alone, so D-33's last rule does not bear on it, and nowhere is that group called milder.

## The generator and the graph

- "On every stream of the military cohort, 16.7% of casualties need a life-saving intervention" (cells 4, 12, 15 and 28; cell 29, axis 1; panel): HOLDS. `need_shares` (rules.py lines 167 to 175) takes the mean of `truth["needs_lsi"]` over `baseline.generator_sample("pre_hospital", "military")`, n = 100,000, seed 42, every stream, the same draw as the notebook's cell 1 and the panel's figures; recomputed directly from `generator.sample` it is 0.16704.
- "Of whom 26.5% need one ... so the generator's injured are a milder cohort" (the same lines): HOLDS. "The injured" is `baseline.calibration_cohort`, the battle and non-battle streams, 56,634 casualties; `milder` compares 0.26514 with E-09's 0.476 at full precision (rules.py lines 190 to 191).
- "These figures are on all 100,000 synthetic casualties of the military cohort, every stream, disease included" (panel, frequentist.py lines 603 to 604): HOLDS. Unchanged in wording; the panel's sensitivity and specificity before it are from `diagnosis_results("pre_hospital")` and `baseline.diagnosis_results("pre_hospital", "figure")` on that sample.
- The graph: HOLDS. No changed line describes a graph.

## Standing lessons

Each lesson against the changed lines.

- Lesson 1: HOLDS. The one registry figure, 47.6%, names its source, E-09, and its population, Priority 1 in the military registry, in the same sentence; it is not applied to a casualty.
- Lesson 2: HOLDS. The new share names its group, "every stream of the military cohort", and "casualties"; the registry figure is quoted as the register gives it, "Priority 1", not as need.
- Lesson 3: HOLDS (panel, frequentist.py lines 603 to 604). The new 16.7% on the panel comes from `rules.need_shares` and says what it is; G-8 passes.
- Lesson 4: HOLDS. The changed sentence states no harm and no negative result.
- Lesson 5: HOLDS. The new share is the generator's, shown beside the "(mechanism)" label in each place, as set out under the second epistemic check.
- Lesson 6: HOLDS. No figure title has changed.
- Lesson 7: HOLDS. The new share stands in the diagnosis material and the baseline column only.
- Lesson 8: HOLDS. The changed sentence calls nothing performance at the point of injury.
- Lesson 9: HOLDS. The changed sentence gives no count.
- Lesson 10: HOLDS, as set out under the generator and the graph.
- Lesson 11: HOLDS. The changed sentence says nothing of where a rule's items came from, what a source omits, or why anything was chosen.
- Lesson 12: HOLDS. The new share sets no method beside another. The injured against E-09, 26.5% against 47.6%, keeps its direction on every one of seeds 43 to 62.
- Lesson 13: HOLDS. No chance of death is given.
- Lesson 14: HOLDS. 16.7%, 26.5% and 47.6% are shown alike, as percentages to one place; the one comparison drawn, injured against E-09, is made at full precision in `milder`. Axis 7's "a share of 0.502" is set against a threshold of 0.100 and is shown as that threshold is; it is not compared with the new share.
- Lesson 15: HOLDS (cells 28 and 29; panel). The changed sentence weighed again: "the generator's injured are a milder cohort" is said of the injured as a whole, of whom 26.5% need an intervention; among the battle casualties alone the share, 50.2% (49.3% to 50.2% on seeds 43 to 62), is above E-09's 47.6%, and among the non-battle injuries it is nil. The battle share is shown in the same scorecard, "half of whom need an intervention" in cell 28 and "a share of 0.502" in axis 7 of the same column, and on the panel's score line, "50.2% need an intervention". The sentence calls only the injured milder, and D-33 gives this form to a scorecard of every stream; the change adds the every-stream share and alters no comparison.
- Lesson 16: HOLDS. D-23's statement stands wherever the rule's accuracy on the generator is quoted in the changed lines: cells 4, 12, 15 and 28, axis 1 of the figure column in cell 29, and the panel.
- Lesson 17: HOLDS. No learned model's result is in the changed lines.

## Figures

No image has changed since 12b8df4: the nine images, at cells 3, 8, 14, 16, 18, 20, 23, 25 and 27, are byte-identical to those there, and no `concludes:` tag has changed.

- Cell 3, the central figure, with the changed text of cell 4 beneath it: HOLDS. The new share is that of the casualties in need, whom the darker hill shows; it adds nothing that alters what the figure concludes.
- Cell 14, with the changed text of cell 12 above it, and cell 16, with the changed text of cell 15: HOLDS. The new sentence adds the share on every stream; what each figure shows and concludes is unchanged.
- App page 1, the frequentist panel: HOLDS. It holds no figure.

## Limits

None recorded. A re-review after consolidation records no new limits (`docs/BUILD.md` section 5).

VERDICT: HOLDS

## Reviewed sources

- `notebooks/02_frequentist.ipynb` 773a27e77f404d5cda8d6268c37fe72e4ef7c2bdfa3c09c6511cf56c14d98b76
- `src/inference_labs/lenses/frequentist.py` d0cced1f09c7e56823ced081b18146cbc6e5700cbc7c414fb8a8e244e1eb73fc
- `app/panels/frequentist.py` 77f7cfc5b0e96255a7786c5aebde61a24315525287faa2454111e181c6df6693
