# Review of slice 1: lens 03, Bayesian

**Date:** 17 November 2026 · **Author:** Ross Taylor

Eighteenth review, and the re-review after the final consolidation pass (commit 305c8a3, D-33), under `docs/BUILD.md` section 5 and D-31. The base is commit f51299c, the last that changed this file. Only the lines changed between f51299c and the current head, 305c8a3, are checked, against every item below and each standing lesson in `docs/BUILD.md` section 8. A breach in any line unchanged since f51299c would be marked MISSED. Cells are numbered from 0 in file order in the current notebook.

What changed since f51299c. The lens module and the panel are byte-identical. In the notebook, apart from execution times, three places changed, all to carry D-33. In cell 42, after "The scorecard's figures are on the battle casualties of the military cohort", the clause "the comparison with E-09 holds for the injured only, of whom 26.5% need a life-saving intervention against 47.6% Priority 1 in the military registry (E-09), so the generator's injured are a milder cohort than the one the rule was validated on (D-23)" is replaced by "Of the battle casualties alone, 50.2% need a life-saving intervention against 47.6% Priority 1 in the military registry (E-09), so they are not a milder cohort than the one the rule was validated on; of the injured as a whole, battle and non-battle, 26.5% need one, so the generator's injured are a milder cohort (D-23)." Cell 43's source passes `group="battle"` to `rules.d23_sentence`, and the first line of its printout now carries the same wording. Cell 46's last sentence before the teach-back carries the same wording. No other cell source or text output changed.

The notebook was run top to bottom from a fresh kernel into a scratch copy in 6.7 seconds; its reader view, every cell source and text output, matched the committed file, and every image was byte-identical to it. Since f51299c the library beneath the lens module has changed only in parts the module does not call (the rounding in `baseline.calibration_check` and the lens 02 row of `decision.seven_axes`), so every string the module and the panel can return is as the previous review found it: the panel was rendered through `page_panel` for all 1,736 walk-through renderings, the 868 battle casualties of each setting, from the files at f51299c and at the head, with identical output, and the module's scorecard, spreads and axis 7 strings in cells 43 and 45 are unchanged. The three shares in the new sentence were recomputed from the library, across seeds 43 to 62, and among the battle casualties alive at pre-hospital care and at arrival at Role 2. Gates G-6 and G-10, run on their own, pass.

No check records a breach, and none is marked MISSED.

## What must not be claimed

- That a 93% posterior probability is proof: HOLDS (cells 42, 43, 46). The changed sentence gives the shares of the generator's casualties in need of a life-saving intervention and E-09's share in Priority 1; it holds no posterior probability and settles no question by one.
- That the notebook's CRASH-3 analysis is a published result: HOLDS (cells 42, 43, 46). No changed line concerns the treatment case; cell 42's account of the treatment row, the row itself and its label are unchanged.
- The other background files' lists: HOLDS (changed lines only). Under 01-rules, the sentence quotes no accuracy for the rule: 47.6% is the share in Priority 1 of the population the rule was validated on, named as the military registry, and "the one the rule was validated on" names that population, not its observations; cell 42's unchanged sentence still says E-09 was measured on first hospital observations. Under 00, the sentence compares how severe two cohorts are and applies no outcome figure to any casualty. Under 10-decision-theory, it touches neither the civilian benchmark nor an exchange rate. No changed line touches the lists of 02, 04 to 09 or 11.

## Epistemic checks

- Accuracy quoted for the wrong cohort or setting: HOLDS (cells 42, 43, 46). The changed sentence quotes no accuracy, for the rule or the lens; it compares shares in need, each given for the group it is measured on: 50.2% for the battle casualties alone, the group the scorecard reports, and 26.5% for the injured, battle and non-battle, on whom the rule is held to E-09 (`baseline.CALIBRATION_STREAMS`). With "the comparison with E-09 holds for the injured only" gone, the rule's accuracy is still tied to the injured by cell 42's unchanged "on the injured, the rule lands near its published accuracy in the military registry (E-09)". The setting does not enter: the generator draws the same casualties and the same need for intervention in both settings, so one share serves both.
- Proxy data read as the real thing: HOLDS (cells 42, 43, 46). The 50.2% and 26.5% are the generator's, and each place says so: the same sentence calls the second group "the generator's injured"; in cell 42 it follows "Every row is measured on synthetic data" and "run on the same synthetic casualties"; in cell 43 it is printed below a scorecard whose diagnosis rows carry the data source "generator" and the mechanism label; in cell 46 it follows "The comparison is made on the generator". "The battle casualties of the military cohort" are set against "the military registry (E-09)" and "the one the rule was validated on", so they cannot be read as the registry's. Only 47.6% is given as a registry figure, and it is one.
- Civilian data read as military: HOLDS (cells 42, 43, 46). The only source the changed lines cite is E-09, whose source `library/curated.yaml` records as mixed (vassallo2017d). They quote only its JTTR figure, 47.6% Priority 1, and call it the military registry, which it is; the civilian TARN figure, 19.5%, is not quoted.
- A diagnosis result read as a treatment result: HOLDS (cells 42, 43, 46). The sentence describes how severe the scored cohort is, by need for a life-saving intervention; it is neither a diagnosis nor a treatment result, and it sits where its predecessor sat, after the diagnosis rows in cells 42 and 43 and after the diagnosis comparisons in cell 46, apart from the treatment case.

## Numbers and their evidence ids

- 47.6% Priority 1, E-09, cells 42, 43, 46: HOLDS. E-09 gives the JTTR cohort, 3,654 adults, as 47.6% Priority 1; the code takes it from `rules.PUBLISHED["MPTT-24, military"].prevalence`, 0.476. Setting it against a share in need is the comparison D-23 and D-33 record.
- 50.2% of the battle casualties in need, cells 42, 43, 46: HOLDS. `rules.need_shares()["battle"]` is 0.50179, on the 29,925 battle casualties of the military cohort's 100,000 synthetic casualties at seed 42, the sample behind axis 7 in cell 45; it is the figure D-33 records. The 8,909 battle casualties behind the diagnosis rows, a smaller sample at the same seed, are 50.4% in need.
- 26.5% of the injured in need, cells 42, 43, 46: HOLDS. `baseline.calibration_need("military")` is 0.26514, on the battle and non-battle injury streams of the same sample, the figure D-23 and D-33 record.
- D-23 and D-33, cells 42, 43, 46: HOLDS. The sentence names the group the scorecard reports and gives that group's share, does not call the battle casualties milder, and keeps D-23's statement that the generator's injured are a milder cohort, as D-33 sets out.

## The generator and the graph

- "Of the battle casualties alone, 50.2% need a life-saving intervention ... so they are not a milder cohort", cells 42, 43, 46: HOLDS. The share is `needs_lsi` (generator.py line 305) on the battle stream. `rules.d23_sentence` with `group="battle"` and no `share` prints exactly this wording, and its `milder` compares the share with E-09's at full precision, 0.50179 against 0.476.
- "Of the injured as a whole, battle and non-battle, 26.5% need one, so the generator's injured are a milder cohort", cells 42, 43, 46: HOLDS. `calibration_need` takes the battle and non-battle injury streams (`baseline.CALIBRATION_STREAMS`); 0.26514 is below 0.476.
- "The scorecard's figures are on the battle casualties of the military cohort", cells 42, 43, 46: HOLDS. Only its closing punctuation changed, a full stop for a semicolon.
- The graph: HOLDS. No changed line concerns the graph.

## Standing lessons

Each lesson against the changed lines.

- Lesson 1: HOLDS. E-09's 47.6% is set against a cohort, not applied to the casualty, and its source, id and population are named in the same sentence.
- Lesson 2: HOLDS. Each share names its group: "the battle casualties alone", "the injured as a whole, battle and non-battle", and "Priority 1 in the military registry", as the register gives it.
- Lesson 3: HOLDS. No changed line is on the app, and the panel's output is unchanged.
- Lesson 4: HOLDS. The direction of each comparison is in words: "not a milder cohort", "a milder cohort".
- Lesson 5: HOLDS. The shares are measured on the generator, as each cell says, and no prior enters them.
- Lesson 6: HOLDS. No figure title changed.
- Lesson 7: HOLDS. The changed lines carry no diagnosis or treatment result into the other's cell.
- Lesson 8: HOLDS. The changed lines quote no performance; cell 42 keeps that E-09 was measured on first hospital observations.
- Lesson 9: HOLDS. The changed lines give shares, not counts; the counts beside them are unchanged.
- Lesson 10: HOLDS, as set out under the generator and the graph.
- Lesson 11: HOLDS. The sentence says neither why anything was chosen nor what a source omits.
- Lesson 12: HOLDS. "Not a milder cohort" is not a tie called a difference: across seeds 43 to 62 the battle casualties' share in need runs from 49.3% to 50.2% at 100,000 casualties and from 48.8% to 51.1% at the scorecard's 30,000, above 47.6% on every seed. It is 49.4% among the battle casualties alive at pre-hospital care and 48.8% among those alive at arrival at Role 2.
- Lesson 13: HOLDS. No changed line gives a chance of death.
- Lesson 14: HOLDS. 50.2%, 47.6% and 26.5% are displayed alike, to one place, and compared at full precision.
- Lesson 15: HOLDS. The sentence shows the group in which D-23's comparison reverses, the battle casualties alone, beside the injured as a whole.
- Lesson 16: HOLDS. In cells 42, 43 and 46, wherever the rule's accuracy on the generator is quoted, the sentence still says that the generator's injured are a milder cohort (D-23), and, as D-33 requires, does not call the battle casualties, the scorecard's group, milder.
- Lesson 17: HOLDS. No changed line concerns a learned model.

## Figures

- Every figure: HOLDS. No figure, title or `concludes:` tag has changed, and every image is byte-identical to the committed one. The changed cells hold text and a table only, and the panel's band is unchanged.

## Limits

None recorded. A re-review after consolidation records no new limits (`docs/BUILD.md` section 5); the limits of the review committed at a107b57 stand as a record (D-31).

VERDICT: HOLDS

## Reviewed sources

- `notebooks/03_bayesian.ipynb` b4873b397d37320b2ed0a9f35d357cab341d6cfc294706d59d06ab7a0864a343
- `src/inference_labs/lenses/bayesian.py` bdd3e49fa348e1a9132fc22563ea643e5f1de6776a7cc0025a1b5cd263ecd113
- `app/panels/bayesian.py` 554c7b609c2f56431ef8b736cbc037ebc9b87d4bda88eb532c85731c5d776e07
