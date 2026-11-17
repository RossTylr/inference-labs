# Review of slice 11: notebooks 00 and 11, app pages, gallery

**Date:** 17 November 2026 · **Author:** Ross Taylor

Fifth review of slice 11, a re-review of the changed lines only. The base is 4466a34 ("Slice 11: close"), the last commit to change this file; the sources are read as they stand at eb1efab ("Read-through: errors and clarity"). Of the nineteen review sources, only `notebooks/00_casualty_thread.ipynb` differs. One markdown cell, tagged explainer and headed "Terms used across the notebooks", is inserted as cell 5. Every other cell's source, tags, metadata and text output is unchanged and every figure is byte-identical, so the fourth review's notebook 00 cells 5 to 26 are now cells 6 to 27, of 28. The other eighteen sources are byte-identical. Outside them, eb1efab changed `baseline.calibration_check` (line 218, which no longer rounds), called only by notebook 01, and one text output of notebook 01 (cell 37, 0.524 to 0.525). No slice 11 source calls that function. The lens 01 page and the gallery draw on notebook 01, but its explainer cells and its eight figures are unchanged.

Both notebooks were executed top to bottom on copies outside the repository with the harness's own executor, notebook 00 in 37.3 seconds and notebook 11 in 41.8 seconds, without error. Every cell source and text output matches the committed files. The gallery was rendered for notebook 00. Read for the new cell: the preamble of `docs/EVIDENCE.md`, rows E-08, E-09, E-43 and E-44, and the `ajp410` brief; the decision table of `docs/DESIGN.md`; `generator.py` lines 77 and 276 to 305; `baseline.py` lines 150 to 162; the Brier computation in every lens module; and every use of "register" in the twelve notebooks. Cells are numbered from 0 in file order. Nothing in the repository other than this file was changed.

## Findings in brief

The inserted cell gives no figure and no result. Each of its sentences is borne out by the register, the design document or the code. No fault was found in the changed lines. Unchanged lines were not re-examined except where the new cell speaks of them, and nothing seen there is a fault, so nothing is marked MISSED. The fourth review's findings on the unchanged lines stand, with notebook 00's cell numbers from 5 onward raised by one. No limit is added; the five recorded at 4466a34 are carried below.

## What must not be claimed: 00, the casualty thread

- That the 44% attribution is measured: HOLDS (notebook 00 cell 5). The new cell gives no figure from E-82 and no attribution. The cells that give them, now 0, 15, 16 and 21, are unchanged.
- That US outcome figures describe UK casualties, or that Afghanistan's mix describes a future operation: HOLDS (cell 5). The cell gives no outcome figure and no mix. The one source it applies, E-43, is NATO doctrine, not US data.

## What must not be claimed: 11, hybrids

- That language models diagnose better than doctors: HOLDS (cell 5). The cell does not mention models set against doctors, and notebook 11 is unchanged.
- That a conformal guarantee holds when the casualty mix changes: HOLDS (cell 5). The cell does not mention prediction sets or the mix, and notebook 11 and the pages are unchanged.

## Epistemic checks

- Accuracy quoted for the wrong cohort or setting: HOLDS (cell 5). No accuracy is quoted; the Brier entry defines the score and gives no value.
- Proxy data read as the real thing: HOLDS (cell 5). The need entry begins "In the generator" and says what the generator counts as need, not what a casualty needs. The Brier entry's "over casualties" is not true of lens 06's image Brier score, which is taken over constructed images, but the scorecard rows that carry it say "constructed images" (notebook 06 cell 34, notebook 11 cell 27), so no reader takes those images for casualties.
- Civilian data read as military: HOLDS (cell 5). No civilian source is cited; E-43 is NATO doctrine.
- A diagnosis result read as a treatment result: HOLDS (cell 5). No result is given.

## Numbers traced to the evidence register

- E-43 (cell 5): HOLDS. "Role 1 as primary care, triage and pre-hospital emergency care, Role 2 in three forms, forward, basic and enhanced, and Role 3 as a deployed hospital with CT" is the row (2F, 2B, 2E). "NATO doctrine, AJP-4.10" is the `ajp410` brief: NATO Standardization Office, Allied Joint Doctrine for Medical Support. Role 4 is left out, not misstated. The edition, and the fact that its currency was not confirmed (E-44, D-28), are given in cell 4 directly above.
- E-09 and D-23 (cell 5): HOLDS. Each is named only as an example of the form of an id, with no figure.
- The description of the register and the design document (cell 5): HOLDS. The register's preamble says every clinical number is listed "with its source and the way it was checked", and each row carries a source and a status. The design document's decisions sit in a table with columns "Decision" and "Reason". Every D- id cited in the notebooks (D-4, D-8, D-9, D-11, D-19, D-21, D-23, D-24, D-26, D-28) is a row of it.
- "Where a notebook says *the register*, it means this one" (cell 5): HOLDS. Every unqualified "the register" in the twelve notebooks refers to the evidence register: notebook 01 cells 4, 10, 17, 20, 24 and 40; 02 cells 9 and 21; 04 cell 20; 06 cell 15; 08 cells 8, 26, 30, 31 and 37; 10 cells 4, 10, 14, 15 and 16; and 11 cells 2, 14 and 16. The one other use, "the developer register above" in notebook 09 cell 18, is qualified and names the explainer's Developer paragraph. "Registry", as in the JTTR or the UK registry, is a different word throughout.

## Sentences about the generator, the graph and the code

- "In the generator, a casualty needs one if bleeding significantly, or with a tension pneumothorax, a severe head injury or septic shock" (cell 5): HOLDS. `generator.py` line 305 sets `needs_lsi = bleeding | tension | head_severe | septic_shock`. Here `bleeding` is significant bleeding among haemorrhage casualties (line 297), `tension` a tension pneumothorax (line 301), `head_severe` a severe head injury (line 302) and `septic_shock` septic shock in the disease stream (line 304). The definition is the same for both cohorts.
- The Brier score entry (cell 5): HOLDS. `baseline.flag_metrics` (lines 150 to 162) scores a rule's flag as one or nought, so its Brier score is the share misclassified, as its docstring says. Every lens that gives a probability computes the mean squared difference from the outcome (`hybrids.py` line 167, `trees.py` line 167, `frequentist.py` line 338, `bayesian.py` line 377, `connectionist.py` line 322, `reinforcement.py` line 290, `stochastic._brier`). In notebook 11 cell 24, the model beneath the sets on the MPTT-24 has Brier 0.125 from a probability that the same cell attributes to "the share in need at each priority", not to the rule. The rule's own columns give 0.245 and 0.249 as "the share misclassified". That agrees with the entry.
- The GCS, AVPU and eFAST entries (cell 5): HOLDS. They give names and definitions only, with no figure. AVPU's four levels are the generator's (`generator.py` line 77), and "responds to voice" is E-08's wording. eFAST is the register's heading for section A2.
- Gallery captions for notebook 00: HOLDS. `pages._figures` computes the cell numbers, and as rendered they read 3, 9, 14, 16, 20 and 24, the cells that now hold the six figures. No source refers to a notebook 00 cell by number.

## Figures

- Notebook 00: HOLDS. The new cell holds no figure. The six figures are byte-identical to those reviewed at 4466a34, and their cells' tags and `concludes:` statements are unchanged.
- Notebook 11, the lens pages and the gallery: HOLDS. Unchanged, and so is notebook 01's part in the lens 01 page and the gallery.

## The app pages

- Pages 2 to 15: HOLDS. No page file and nothing in `pages.py` changed. The only page that reads notebook 00 is the gallery, as above.

## Standing lessons

- Lessons 1 to 9 and 12 to 17: HOLDS for cell 5. It applies no trial or registry figure, quotes no accuracy or count, and shows no prior, result, figure or comparison.
- Lessons 10 and 11: HOLDS for cell 5. The one sentence about the generator matches the code (above). The cell does not say where a rule's items came from, what a source omits or forbids, or why anything was chosen.

## Limits

Carried from the review at 4466a34; none is added. Limit 4's notebook 00 cell is renumbered.

1. At the level of 0.90 every set from both models holds "no need" (cell 13), so every miss is a casualty in need told "no need" alone, with no "look again": 40.0% of those in need under the MPTT-24's sets and 52.9% under the tree's, 37.3% and 49.8% among battle casualties, and all twenty ringed in cell 3. Cells 2 and 10 present the set as giving one answer when the tool is sure and a list when it is not. A reader concludes the sets mark the casualties they may be wrong about, when for those in need their errors are confident.
2. Cell 12 plots coverage at 0.99 as 1.000 for both models, battle casualties included, because at 0.99 every casualty's set holds both labels, the set that says nothing of cell 22. At 0.80 the MPTT-24's 0.833 is the share not in need, every set being "no need" alone, and the tree gives 8.1% of casualties an empty set. A reader of the figure concludes that raising the level restores coverage among battle casualties.
3. On page 3 and in cell 27, some rows differ between "scan before hospital" and "scan in hospital": lens 03's sensitivity 0.0475 against 0.7285, lens 07's scan sensitivity 0.2560 against 0.7382, and the ABC score's 0.2386 against 0.3147. They differ because the generator's scan uses one civilian helicopter service's accuracy (E-16) before hospital and an assumption centred on pooled in-hospital figures (E-14) in hospital. Only notebook 11's belief rows say so. A reader of page 3 concludes the setting itself makes the difference for military casualties.
4. Page 3's caption gives D-23's statement beside the rows on battle casualties alone and ends that the generator's injured are a milder cohort. Unlike notebook 11 cells 11 and 24 and notebook 00 cell 26, it does not add that battle casualties alone, 50.2% in need against E-09's 47.6% Priority 1, are not. Page 3 carries no other statement of it, so its reader takes those rows of the MPTT-24 as measured on a milder cohort than the registry's.
5. Page 2 gives each method on one sample of 20,000 at seed 42, with no spread. At the default mix the logistic score, forest, signs network and knowledge graph read 9.4, 9.5, 9.6 and 9.7 per 100. Across seeds 43 to 62 at the same size, the forest less the score runs from -0.01 to +0.18, the network less the forest from -0.05 to +0.19 and the graph less the network from -0.21 to +0.33. A reader ranks four methods that are tied.

VERDICT: HOLDS

## Reviewed sources

- `notebooks/00_casualty_thread.ipynb` c50a901bd1adda9f3f2aaa81b442dbd356d5447dd59ebc21c524335258785694
- `notebooks/11_hybrids.ipynb` 69f0443164c17fac5197498c8d42b36fb9b252742991169ff280cb36d80b1d01
- `src/inference_labs/thread.py` bef5efd7451c51b407f075922fa5f68e09b7e03ca27a5c5c353ee3a2bf7c0aff
- `src/inference_labs/lenses/hybrids.py` 2cabc36329585254a3d77f1cbdcd03c89904820a758bb389b5eb898a56df9e48
- `src/inference_labs/pages.py` 6655098f43403d2db842ca0fa30009b724143c8fd9fd327fa8f113034f6c131f
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
