# Review of slice 11: notebooks 00 and 11, app pages, gallery

**Date:** 17 November 2026 · **Author:** Ross Taylor

Sixth review of slice 11, a re-review after the final consolidation pass (D-33), of the changed lines only. The base is fbee655 ("Slice 11: close re-review after read-through"), the last commit to change this file; the sources are read as they stand at 65f7eca. Four of the nineteen review sources differ:

- `notebooks/00_casualty_thread.ipynb`: the text output of cell 26 (D-23's statement inside the yardstick), and a new markdown cell 27, tagged scorecard, on the battle casualties alone. The analogy, formerly cell 27, is now cell 28, unchanged. The notebook has 29 cells.
- `notebooks/11_hybrids.ipynb`: the text outputs of cells 11, 24 and 27, in each case D-23's statement only. Every other line of the lens table in cell 27 is unchanged.
- `src/inference_labs/thread.py`: `lens_table_rule` (line 349) and `rule_on_both` (lines 352 to 359) now call `rules.d23_sentence` with `group="every stream and battle"`.
- `src/inference_labs/pages.py`: `figure_notes` entries ("01", 4) and ("02", 6) (lines 393 to 394 and 400 to 401) pass `group="injured"`. Their rendered text is identical to before.

`hybrids.py` and the fourteen page files are byte-identical. Outside the sources, `rules.d23_sentence` and the new `rules.need_shares` (rules.py lines 164 to 213) change what every D-23 call in the sources returns: the nine other D-23 figure notes, the page 3 caption and the hybrids scorecard's baseline row. `trees.models` now fits the forest with `n_jobs=1`, which feeds page 2. `reinforcement.py` changed `question_tree` and `cost_curve` but not `policy_output`, which is what page 2 uses. Among the notebooks the pages read, notebook 02's explainer (lens 02 page) and notebook 09's figures 3 and 4 (gallery) changed. Every other explainer cell, central figure, `concludes:` statement, figure count and figure cell number is unchanged in all twelve notebooks. Those changed outputs are what a reader of the pages now sees, so they are checked below.

Both notebooks were executed top to bottom on copies outside the repository with the harness's own executor, without error: notebook 00 in 41.2 seconds and notebook 11 in 71.6 seconds (run alongside another computation). Every cell source and text output matches the committed files. Read for the changed lines: PRD sections 3, 6.0 and 6.11; both background files; BUILD.md section 8; DESIGN rows D-23, D-24, D-26 and D-33; EVIDENCE row E-09; `rules.d23_sentence` and `rules.need_shares`; `baseline.calibration_cohort` and `calibration_need`; `generator.py` line 305; `decision.net_benefit` and `flag_all`; `pages._flags`; and notebook 10 cell 12. The claims of the new cell 27 were recomputed from `pages._flags` on seed 42 and seeds 43 to 62, 100,000 casualties each, both with the scan before hospital and with the scan in hospital. Cells are numbered from 0 in file order. Nothing in the repository other than this file was changed.

## Findings in brief

D-23's statement now gives each group its own share in need: 16.7% on every stream, 50.2% among the battle casualties alone, "not a milder cohort" than E-09's 47.6%, and 26.5% among the injured, "a milder cohort". Each figure and each comparison matches the code at full precision. Notebook 00 cell 27's claim reproduces exactly. Among the battle casualties, flagging every one beats each of page 2's ten methods on seed 42 and on every one of the 20 further samples. The nearest method is lens 08's graph on all 21, and its gap runs 0.277 to 0.559 per 100 across seeds 43 to 62. No fault was found in the changed lines. No breach was seen in unchanged lines, so nothing is marked MISSED. The page 3 caption now states that the battle casualties alone are not a milder cohort, which closes the earlier limit 4. No limit is added.

## What must not be claimed: 00, the casualty thread

- That the 44% attribution is measured: HOLDS (notebook 00 cells 26 and 27). Neither changed cell gives E-82's figures or any attribution. The cells that do (0, 15, 16 and 21) are unchanged.
- That US outcome figures describe UK casualties, or that Afghanistan's mix describes a future operation: HOLDS (cells 26 and 27; page 3 caption). The one source applied in the changed lines is E-09, named as "the military registry", the JTTR of the register row. Cell 27's result is on the generator's battle casualties and is labelled mechanism. Nothing in it is offered as a description of any operation.

## What must not be claimed: 11, hybrids

- That language models diagnose better than doctors: HOLDS (notebook 11 cells 11, 24 and 27). The changed lines are D-23's statement only. Cells 0, 1 and 10, which carry E-110, are unchanged.
- That a conformal guarantee holds when the casualty mix changes: HOLDS (notebook 11 cells 11, 24 and 27; notebook 00 cell 27). No coverage figure changed. Notebook 00 cell 27 names "prediction sets on the single tree" only as one of the ten flags scored by net benefit, and says nothing of coverage.

## Epistemic checks

- Accuracy quoted for the wrong cohort or setting: HOLDS. Each share in D-23's statement is taken on the group it names, among the 100,000 synthetic casualties at seed 42: every stream 0.16704, injured (battle and non-battle, `CALIBRATION_STREAMS`) 0.26514, battle 0.50179. Notebook 00 cell 27 names its group, the battle casualties alone, and its samples. Its setting is not named. Its range of 0.28 to 0.56 per 100 is that of the default, the scan before hospital. With the scan in hospital, flagging every battle casualty still beats each of the ten on all 21 samples, and the graph's gap is then 0.03 to 0.24 per 100, so the claim holds in either setting. The page 3 caption names the rows whose MPTT-24 figures are on battle casualties alone or a group within them, as `BATTLE_BASELINES` sets them.
- Proxy data read as the real thing: HOLDS. Cell 27 says "synthetic casualties" and "(mechanism)". Every changed D-23 sentence speaks of the generator's military cohort, and the comparison with E-09 is set out as a comparison, not as a measurement of the registry.
- Civilian data read as military: HOLDS. No civilian source is cited in a changed line. E-09's 47.6% is the military registry's own figure. The changed figure note ("02", 3) still names "the civilian cohort" where its figure uses one.
- A diagnosis result read as a treatment result: HOLDS. Cell 27 scores flags for need of a life-saving intervention, a diagnosis result, and makes no treatment claim. Page 3's caption is built for the case its toggle shows, naming only the diagnosis rows or only the treatment rows.

## Numbers traced to the evidence register

- E-09, "47.6% Priority 1 in the military registry" (notebook 00 cell 26; notebook 11 cells 11, 24 and 27; page 3; figure notes): HOLDS. The row gives JTTR, 3,654 adults, 47.6% Priority 1. `rules.PUBLISHED["MPTT-24, military"].prevalence` is 0.476.
- D-23 and D-33, "26.5%" of the injured and "50.2%" of the battle casualties alone: HOLDS. Both rows give these figures, and `need_shares` returns 0.26514 and 0.50179. "So they are not a milder cohort" and "so the generator's injured are a milder cohort" follow from comparing 0.50179 and 0.26514 with 0.476 at full precision (lesson 14). "(D-23)" is attached to the injured clause, which D-23 states.
- "On every stream of the military cohort, 16.7% of casualties need a life-saving intervention": HOLDS. It is computed (0.16704) and is not attributed to a register or design row.
- Notebook 00 cell 27, "of whom 50.2% need a life-saving intervention": HOLDS (0.50179).
- Notebook 00 cell 27, "the ten methods that page 2 of the app sets side by side": HOLDS. `pages._flags` returns ten flags, and page 2 adds flagging every casualty as the eleventh row.
- Notebook 00 cell 27, flagging every battle casualty "has a higher net benefit at the common threshold of 0.10 than each of the ten ... on the 100,000 synthetic casualties (seed 42) and on each of 20 further samples": HOLDS. The smallest margin on seed 42 is 0.37 per 100, and across seeds 43 to 62 the smallest margin on any sample is 0.28. The largest margins are the prediction sets' (20.5 on seed 42) and the MPTT-24 figure reading's (14.6).
- Notebook 00 cell 27, "The nearest, lens 08's graph, lies 0.28 to 0.56 per 100 below it across those samples": HOLDS. The graph is nearest on all 21 samples, and its gap across seeds 43 to 62 runs 0.277 to 0.559.
- Notebook 00 cell 27, "Notebook 10 explains why": HOLDS. Notebook 10 cell 12 gives the reason: flagging a group pays at 0.10 wherever more than one in ten of those left unflagged need an intervention. That arithmetic holds for any flag, so it covers the unfitted rule and graph as well as the fitted models it names.

## Sentences about the generator, the graph and the code

- "Of the injured as a whole, battle and non-battle" (every changed D-23 sentence): HOLDS. `calibration_need` takes the share over `CALIBRATION_STREAMS = ("battle", "non_battle")` (baseline.py line 77).
- "On every stream of the military cohort" and "Of the battle casualties alone": HOLDS. `need_shares` takes the generator's military sample at seed 42 with the scan before hospital, over every row and over `stream == "battle"`. Need is `generator.py` line 305 in both cases.
- Notebook 00 cell 27, "each flagging need at the threshold its own lens sets, the MPTT-24 under both readings among them": HOLDS. The flags are exactly `pages._flags`. The score, the tree, the forest and the network flag at their own thresholds, decision theory at the cost threshold, the prediction sets when the set holds need, the MPTT-24 at Priority 1 under each reading, the graph at "any candidate" and the policy by its own flag. For the last three, "threshold" means the lens's own flagging rule. Page 2 says the graph has no threshold, and lens 08's own rule is "any candidate" (knowledge.py line 561). The wording is loose, but the flags scored are the page's, so the result stands as stated.
- Notebook 00 cell 27, "lens 08's graph": HOLDS. It is `knowledge.score_matrix(observed).max(axis=1) > 0`, as page 2 scores it.
- `thread.rule_on_both` docstring, "each group's share in need and the comparison with E-09, on the evaluation sample (mechanism)": HOLDS against its body.
- `thread.lens_table_rule`: HOLDS. `BATTLE_BASELINES` is unchanged, and the rows it names for each case are those the earlier reviews checked.
- `thread.yardstick`, as shown in notebook 00 cell 26: HOLDS. It replaces lens 01's every-stream sentence with `rule_on_both`. The output carries one D-23 statement and none of the earlier wording.
- `pages.figure_notes` ("01", 4) and ("02", 6), `group="injured"`: HOLDS. Both figures are on the injured, and the rendered text is the same as before.
- The nine other D-23 figure notes, ("01", 1), ("01", 3), ("02", 1) to ("02", 4), ("04", 3), ("08", 4) and ("10", 4): HOLDS. Each adds "On every stream of the military cohort, 16.7% of casualties need a life-saving intervention" to the earlier statement on the injured. None calls battle casualties milder. The two notes on "a hundred synthetic casualties" give 16.7% as the share on every stream, not as the hundred's own.

## Figures

- Notebooks 00 and 11: HOLDS. No figure changed in either. The new cell 27 holds none.
- Gallery, notebook 09 figures 3 and 4: HOLDS. Both were redrawn in the pass. Figure 3 adds each route's share in need among the battle casualties. Figure 4 adds a panel of net benefit at 0.10 among the battle casualties alone, with both readings of the MPTT-24 and flagging every casualty beside the policy. The captions are unchanged ("figure 3 of 8, cell 11", "figure 4 of 8, cell 14"), and the titles describe what is plotted (lesson 6). The battle panel agrees with notebook 00 cell 27: at the default question cost the policy lies below flagging every casualty, and it reaches it only where it asks nothing. The MPTT-24's lines there are net benefit, not accuracy, and carry no gallery note, as with notebook 10 figure 3, so lesson 16 is not engaged.
- Lens pages: HOLDS. No central figure or `concludes:` statement changed. The captions of lens pages 01 and 02 carry the rewritten figure notes above.

## The app pages

- Page 3, the lens table caption for each case: HOLDS. It now gives the share on every stream and the battle casualties' 50.2%, "not a milder cohort", beside the injured's 26.5%. Every number comes from `rules.need_shares` through `pages.lens_table`.
- Page 2: HOLDS. The page and `_mix_rule` are unchanged. With the forest now fitted sequentially, the default-mix rows read as before: score 9.4, forest 9.5, network 9.6 and graph 9.7 per 100.
- Page 5 onward, the lens pages: HOLDS. The lens 02 page's explainer carries notebook 02's rewritten sentence, "These figures are on all 100,000 synthetic casualties of the military cohort, every stream. On every stream of the military cohort, 16.7% ...; the comparison with E-09 holds for the injured only, of whom 26.5% need one ...". It matches the code.
- Page 4 and the other page files: HOLDS. Neither the files nor anything they call changed.

## Standing lessons

- Lesson 1: HOLDS. The one registry figure applied, E-09's 47.6%, is given with its id and its population, Priority 1 in the military registry.
- Lessons 2 and 9: HOLDS. Each share names its group, and cell 27 names "the battle casualties alone", "ten methods", "100,000" and "20 further samples", each exact.
- Lesson 3: HOLDS. Page 3's caption figures come from the library, and each says what it is a share of.
- Lesson 4: HOLDS. Cell 27 gives the shortfall in words: "lies 0.28 to 0.56 per 100 below it".
- Lesson 5: HOLDS. Cell 27's result rests on the threshold of 0.10. Cell 25 calls it "the value implied by weighing a miss nine times a false alarm, an assumption", and cell 26, directly above cell 27, repeats "(an assumption)" on the axis 7 row it extends. Cell 27 calls it "the common threshold of 0.10" without repeating the word.
- Lessons 6, 7 and 8: HOLDS. No figure title is new in the slice's notebooks, and the gallery's two new titles describe what is plotted. Cell 27 is a diagnosis result in the scorecard section, apart from every treatment cell. No performance on hospital observations is called performance at the point of injury.
- Lessons 10 and 11: HOLDS. The sentences about the generator and the graph are checked above. No changed line says where a rule's items came from, what a source omits, or why anything was chosen.
- Lesson 12: HOLDS. Cell 27 states that the ordering holds on each of 20 further samples, and gives the spread of the nearest margin across them. No margin crosses zero, so none is a tie.
- Lessons 13 and 14: HOLDS. No chance of death is given. The comparison with E-09 is made at full precision and shown to one place on both sides.
- Lesson 15: HOLDS. Cell 27 shows the subgroup in which the comparison with flagging every casualty reverses. The every-stream reading sits in cell 26 and on page 2.
- Lesson 16: HOLDS. Every changed D-23 statement gives the share of the group it reports and does not call the battle casualties milder. Cell 27 quotes no accuracy of the rule and sits directly below cell 26's statement.
- Lesson 17: HOLDS. Cell 27 reports, as a finding, that no method beats flagging every battle casualty at 0.10.

## Limits

Carried from the review at 4466a34; none is added. The former limit 4 is closed by the page 3 caption above and is dropped, and the former limit 5 is now limit 4. Page 2's figures in it were re-read at the default mix, and the spreads across seeds 43 to 62 were recomputed with the forest fitted sequentially. They are unchanged.

1. At the level of 0.90 every set from both models holds "no need" (cell 13), so every miss is a casualty in need told "no need" alone, with no "look again": 40.0% of those in need under the MPTT-24's sets and 52.9% under the tree's, 37.3% and 49.8% among battle casualties, and all twenty ringed in cell 3. Cells 2 and 10 present the set as giving one answer when the tool is sure and a list when it is not. A reader concludes the sets mark the casualties they may be wrong about, when for those in need their errors are confident.
2. Cell 12 plots coverage at 0.99 as 1.000 for both models, battle casualties included, because at 0.99 every casualty's set holds both labels, the set that says nothing of cell 22. At 0.80 the MPTT-24's 0.833 is the share not in need, every set being "no need" alone, and the tree gives 8.1% of casualties an empty set. A reader of the figure concludes that raising the level restores coverage among battle casualties.
3. On page 3 and in cell 27, some rows differ between "scan before hospital" and "scan in hospital": lens 03's sensitivity 0.0475 against 0.7285, lens 07's scan sensitivity 0.2560 against 0.7382, and the ABC score's 0.2386 against 0.3147. They differ because the generator's scan uses one civilian helicopter service's accuracy (E-16) before hospital and an assumption centred on pooled in-hospital figures (E-14) in hospital. Only notebook 11's belief rows say so. A reader of page 3 concludes the setting itself makes the difference for military casualties.
4. Page 2 gives each method on one sample of 20,000 at seed 42, with no spread. At the default mix the logistic score, forest, signs network and knowledge graph read 9.4, 9.5, 9.6 and 9.7 per 100. Across seeds 43 to 62 at the same size, the forest less the score runs from -0.01 to +0.18, the network less the forest from -0.05 to +0.19 and the graph less the network from -0.21 to +0.33. A reader ranks four methods that are tied.

VERDICT: HOLDS

## Reviewed sources

- `notebooks/00_casualty_thread.ipynb` 0aa122b95887a6d5ba1750f1617e1d32003148878155850a143573788f2aac33
- `notebooks/11_hybrids.ipynb` 98893625239d7ca576c4d8e2fc7aa02a3f2dfb6f0cb478610fe1526e08bdb6e9
- `src/inference_labs/thread.py` 1b0817d0c823ebbde2e01b44316b4096d1c27cb5751b74b51f079adc57b20cc0
- `src/inference_labs/lenses/hybrids.py` 2cabc36329585254a3d77f1cbdcd03c89904820a758bb389b5eb898a56df9e48
- `src/inference_labs/pages.py` 9a895c7eef3e96036b68bf03d2d687f361969ca2fc051f09239da3fcaefc76d1
- `app/pages/2_Mix_and_setting.py` 4e67e9941d1f87f9486f7a7f7c359ef0cf72629d311fce0c4446a2477d6e06c5
- `app/pages/3_Lens_table.py` 40b4ecc982f1a46ba5e812bd937ee1a9d58a7ba444de52595d07a8070847bc54
- `app/pages/4_Graph_explorer.py` 560740e14d5ba27416c91bac4b3eb3399af555dc62f3f1e19bce1d9f7ffc6b20
- `app/pages/5_Lens_01_Rules.py` ea0ef91d483821cbc6f28e711fb20ee926c56979d2547ccded9a2f938dc6fe09
- `app/pages/6_Lens_02_Frequentist.py` 6b63a2aa448dd039e20ef33099846a3a0e2bdd843ea1f3726bb50699fbdaa4a9
- `app/pages/7_Lens_03_Bayesian.py` cecf50623d0ba095f8f4fa6ca5b7c3beb54e8c78b6a9595d1a1eebae984638dc
- `app/pages/8_Lens_04_Decision_trees.py` 482909cb87c46ec34b0af1f6bb633b3a42d5121a045eaba43fcd20bd587fc27f
- `app/pages/9_Lens_05_Stochastic.py` 141c369d5d0553dbbaeaeed35486cf40057ad27d6d081ced8bd5d3bf441c9ec8
- `app/pages/10_Lens_06_Connectionist.py` 55794f57af7d77c3266e50f12cf92c6461f02a6407d4a97de2ee8d85d01be729
- `app/pages/11_Lens_07_Causal.py` 65cd7ec07fca503533d9b771b13eea225fd381f86103e18be517198b9481fb00
- `app/pages/12_Lens_08_Knowledge_graph.py` 66fc5048061f76f683bdd0c2bfbf11de8de559647b6aeaa96047d19a7f572d3c
- `app/pages/13_Lens_09_Reinforcement_learning.py` eefc4d32055607d753ebd47e93d8e73d6796718b4138abdd858b4da4ad375864
- `app/pages/14_Lens_10_Decision_theory.py` ba1e496e5c10e13b10f9d161f60534b3b870055ba935c64ad8019f3bb9d8ce99
- `app/pages/15_Gallery.py` b6777104875d3d42e7beeefe47d66c7f29d3f664a248ae262b61f00705d3e18f
