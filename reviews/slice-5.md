# Review of slice 5: lens 10, Decision theory

**Date:** 13 November 2026 · **Author:** Ross Taylor

Third review, the last of the three rounds D-25 allows. The files were reviewed as they stand at cfe7d87. The second review (commit 343b5a9) read the files at be39f72 and found no breach. Since then three commits have changed the slice. 3ea3625 moved the decision panel out of `app/streamlit_app.py` into `app/panels/decision.py` (D-27) and added `page_panel`. 9afd893 and 8b2f410 changed the library and the notebook. The review was made against PRD sections 3 and 6.5, decisions D-8, D-19, D-21 and D-23 to D-27, design section 9, and `docs/background/10-decision-theory.md`.

These were read in full: `notebooks/10_decision_theory.ipynb`, `src/inference_labs/lenses/decision.py`, `app/panels/decision.py`, `app/panels/__init__.py` and `app/streamlit_app.py`. These were read for what the lens draws on:
- frequentist.py lines 43, 195 to 211 and 478 to 483;
- rules.py lines 144 to 152 and 193 to 196;
- trees.py line 68;
- bayesian.py lines 63 to 75, 165 to 174, 344 to 355 and 437 to 541;
- baseline.py lines 70 and 167 to 177;
- the axis 7 rows that call `decision_value`: rules.py lines 308 to 311, frequentist.py lines 465 to 467 and trees.py lines 506 to 511.

For every sentence that cites them, the evidence register rows the notebook, library and panel cite were opened, together with their Part B briefs and the background notes on them. `src/inference_labs/generator.py` and `params.yaml` were read for every sentence that says how the generator works.

The notebook was run top to bottom from a fresh kernel. It finished in 8.0 seconds without error, every text output matched the committed one, and all eight figures were byte-identical to the committed ones. Each figure was viewed. The decision panel was rendered from the library for every casualty app page 1 can show: all three patient types in both settings, 1,736 entries. No entry held an unformatted or missing value.

Cells are numbered from 0 in file order. Line numbers are those of the file named, as it stands at cfe7d87.

## What changed since the second review

**Notebook.** Cells 12 and 13 are new: the reversal among battle casualties. Cells 19 to 26 and 29 changed. Cells 0 to 11, 14 to 18 (12 to 16 before), 27 and 28 (25 and 26 before) and 30 (28 before) are unchanged in source and in their `concludes:` tags. The outputs of cells 27 and 28 changed with the library.

**Library.** These lines are new or changed in `decision.py`: 18 to 24, 54, 64 to 72, 214 to 237, 240 to 245, 255 to 336, 341 to 401, 406 to 481, 522 to 532, 550 to 587, 614 to 647 and 651 to 654. Two parts are unchanged: the diagnosis functions (lines 59 to 206) and the lens's `diagnose`.

**App panel.** Lines 9 to 13 of `app/panels/decision.py` lay out the same three elements as lines 85 to 88 of `git show 9da1c2c:app/streamlit_app.py`: the heading as a subheader, then the costs line and the evacuation line as markdown. They sit in the same place on the page, last of the panels and above the closing caption. The panel's ORDER is 5, after the trees panel's 4.
- At 9da1c2c the page took the three elements from `decision.panel(self.record, self.line)` (bayesian.py line 518 at that commit).
- It now takes them from `decision.page_panel(walk)`, which calls `panel(walk.record, walk.line)` with the same arguments (decision.py lines 651 to 654).

So the panel is unchanged apart from what `panel` now returns. The threshold is now given to three places. The probability is set against it by `against_threshold`. The evacuation line is now conditioned on the casualty being alive at the decision, and names its sources.

## Findings in brief

One breach is found, in changed lines. It concerns the figure at cell 23 and the sentences that carry its conclusion: the two orderings for one aircraft are said to "tie" with "no detectable difference" when the scan is done in hospital. On the generator they do not tie.
- On the 20 draws shown, ordering by belief and clock gives fewer expected deaths than the rule's priority on 15 draws, by 0.046 per 100 pairs on average.
- On 400,000 pairs it gives 1.849 against 1.901.
- On three further synthetic samples it gives fewer every time.

Nothing in lines unchanged since the second review is found to be a breach, so nothing is marked MISSED.

Three of the second review's limits are resolved by the changes:
- the diagnosis sentence of the closing summary now carries its cohort and the mechanism label;
- the aircraft comparisons, the hold curve and the panel now say that they count deaths from bleeding into the abdomen;
- E-85 is now said to come from civilian centres, and its application to a battle casualty is called an assumption.

The second review's limit on the in-hospital margin was answered by the tie wording, which is the breach recorded below.

New limits are recorded under each check:
- the diagnosis figures still count the battle casualties the generator records as dead before triage;
- ten haemorrhage casualties per setting that the page can show are, in the generator, dead before triage;
- the level of the chance of a bleeding death rests on E-85's hazard and the assumed site mix as well as on E-41.

## What must not be claimed

- That the civilian benchmark applies to military triage: HOLDS (cells 14, 16; decision.py line 185; the panel). Cell 14 says the review of 21 studies "cites benchmarks of under-triage below 5% and over-triage below 50% (E-87)", and that "It is drawn as one region among others, not as a standard the military rule should meet". The figure at cell 16 draws it as "benchmark region (E-87)", and its tag calls it "one choice among several rather than a fixed target". No cell, library string or panel line measures a military rule or the generator against it. The new cells 12 and 13 and the panel do not mention it. Two limits, unchanged:
  - The notebook never says that the benchmark belongs to civilian trauma systems. Nor does it say that the benchmark's target condition differs from the MPTT-24's Priority 1: severe injury in civilian systems (the background file's anchors) against need for a life-saving intervention. That difference is the background file's reason for the prohibition. The figure sets the military registry's point and the generator's military points beside the region on one plane. What may be claimed is only that the benchmark is a stated choice. How far any military point lies from it may not be read as a shortfall.
  - The register gives no definition of over-triage for E-87, so the region's horizontal edge at 0.50 may be on a different scale from E-12's 1 minus the positive predictive value. Cell 14 says the register gives none.
- That PATCH shows extra survivors were left with poor function: HOLDS (cells 0 to 30; decision.py lines 1 to 654; app/panels/decision.py lines 1 to 13). PATCH, E-78 and functional outcome are not mentioned in the notebook, the library or the panel, and E-78 is not in the notebook's evidence list.
- A specific exchange rate between a miss and a false alarm: HOLDS (cells 2 to 5, 8, 12, 13, 18, 26, 27, 29; decision.py lines 3 to 5, 16 to 17, 47 to 50, 413 to 416, 421 to 422 and 626 to 627). The default of nine to one is called an assumption wherever it is set or stated:
  - in the module docstring and the constant's comment;
  - in the controls of cell 3 ("an assumption: the reader's to set");
  - in cell 4 ("the default of nine to one is an assumption");
  - in every axis 7 string ("with a miss weighed 9 times a false alarm (an assumption)");
  - in the panel ("an assumption: no source states an exchange rate between a miss and a false alarm").

  Cell 26 ties the 0.10 of D-26 to "the value the default costs set". Cell 4's statement that no source in the register states such a rate was checked against the register:
  - E-87 gives two separate limits, not a rate.
  - E-79's thresholds of 0.1 for benefit and 0.025 for harm weigh a false claim of benefit against a false claim of harm, not a miss against a false alarm.
  - E-48's utility penalises late and false alerts, and the register gives no values for it.
  - E-93 says that the threshold encodes the weighing, without giving one.
  - E-86's pressure target trades two harms.

  The overflow cost of 3, the flight time and the time held are each called an assumption. One limit, widened:
  - The suptitle of the figure at cell 3 and the legend of the figure at cell 8 give "a miss weighed 9 times a false alarm" and "9 each" without the word assumption. So do the new cell 12 ("the threshold of 0.10", "At 0.10, flagging a group pays wherever more than one in ten of them need an intervention") and the headings cell 13 prints. In each case the assumption is stated in the cells around, not in the cell itself. Lifted out of the notebook, none of them may be read as stating a rate from any source.

## Epistemic checks

- Accuracy quoted for the wrong cohort or setting: HOLDS (cells 3, 6, 10 to 16, 24 to 29; decision.py lines 98 to 206, 437 to 470, 543 to 587 and 597 to 636). The new battle figures are scoped as they are counted:
  - Cell 12 sets every stream (16.7% in need) against the battle casualties alone (50.2%).
  - Cell 13 prints both, with net benefit for each method on each.
  - The axis 7 strings give "Battle casualties alone, where a share of 0.502 need it".
  - The panel gives its battle figures as "On the battle casualties among that cohort's 100,000 synthetic casualties, the kind this page shows".

  Each was recomputed: 0.275 against 50.2%, 25.4% told not to act and 22.1% of those in need. At the panel's costs, not acting on those casualties costs 1.99 per casualty against 0.78 for acting, so "acting on all of them would cost less" is right. On the 868 battle casualties the page itself draws from, 214 are told not to act and 43 of them, 20.1%, need an intervention: the same direction. The rest of the notebook's figures keep their cohorts:
  - Its diagnosis figures are scoped to all 100,000 synthetic casualties of the military cohort, every stream (cell 3 and cell 11 titles, cells 26 and 29, axis 1 in cell 27), where lens 02's calibration is +0.001.
  - D-23's statement stands beside the MPTT-24's figures in cells 10 and 26.
  - The treatment figures belong to battle casualties alive at the decision.
  - Every published figure is given with its own cohort: E-96's 38,455 hospitalisations, E-87's 21 studies, E-88's ten Dutch hospitals, E-126's London incident, E-09's two registries, E-37 and E-38's trauma team cohort, and E-39 to E-41's US deaths.

  Eight limits:
  - The generator's points in the table at cell 15 and the figure at cell 16 are on every stream, disease included, and are labelled only "generator's military cohort" (unchanged). On them the MPTT-24's over-triage is 64.1% (figure reading) against 33.0% in the military registry. The generator's points may not be read beside the registry's as like for like.
  - The MPTT-24's and the Military Sieve's points in cells 14 to 16 were measured on first recorded hospital observations and registry GCS, not at the point of injury (E-09, E-11) (unchanged). The notebook does not say so. The figure sets them beside triage in the field (E-88) and at the scene (E-126). They may not be read as the rules' accuracy at the point of injury.
  - The scorecard's metric names (decision.py lines 519 to 520, cell 28) give the threshold, the target and the setting but not the cohort (unchanged). Cell 26 scopes them to all 100,000 casualties of the military cohort, and they may be read only so.
  - The ten casualties of the by-hand count (cells 5 to 8) are battle casualties, on whom lens 02's probability runs low: four of the ten need an intervention, against a mean probability of 0.27 (unchanged). The count is arithmetic on ten and claims nothing about calibration.
  - In the torso failure (cells 24 and 25) the deaths by site are the generator's, which sets each site's chance of a bleeding death so that its bleeding deaths split as E-41 does. Applying to every bleeding death a split measured in potentially survivable deaths before a facility is an assumption of the generator (`params.yaml` lines 398 to 407) (unchanged).
  - Cell 24's "The injuries seen most often are not the bleeding that kills most often" sets E-38's injuries against E-41's lethal haemorrhage. "Kills most often" holds within the potentially survivable deaths named in the sentence before (unchanged).
  - New. The diagnosis figures count every casualty in the sample: cells 3 to 18, 27 and 28, the axis 7 strings, and the panel's costs line through `battle_not_acted` and `frequentist.battle_calibration`. That includes the 482 battle casualties, 1.6%, whom the generator records as dead from bleeding before the triage time (decision.py lines 373 to 377). The treatment and failure cases exclude them. On the battle casualties alive at triage, 49.4% need an intervention against 50.2%; 25.7% are told not to act, and 21.7% of those need an intervention. The direction of every statement is unchanged, but the diagnosis and treatment halves of the notebook are on slightly different cohorts, and the notebook does not say so.
  - New. Cell 12's "The methods were fitted on every stream" holds for lens 02 and both trees (frequentist.py lines 195 to 199; trees.py line 68), but not for the MPTT-24, which is coded from the published flowchart (E-08) and is not fitted. For the rule, the reversal rests only on the clause that follows: 33.7% need an intervention among the battle casualties it leaves unflagged.
- Proxy data read as the real thing: HOLDS (cells 3, 4, 8, 11 to 29; decision.py lines 30, 111, 163, 177 to 179, 192, 269 to 272, 314, 343 to 346, 389, 416, 440, 456, 466, 521, 532, 564 to 585, 600 and 630 to 647; app/panels/decision.py lines 11 to 13). Every result on the generator is called synthetic or a mechanism:
  - every figure title on generator data says so;
  - the operating-point table marks its generator rows "mechanism";
  - every scorecard row is labelled mechanism;
  - every axis 7 string carries "(mechanism)";
  - both sentences of the panel's costs line and its evacuation line close with it;
  - the new cell 12 and cell 13's printed headings carry it;
  - cell 29's diagnosis sentence now carries it, resolving the second review's limit.

  Cell 4 says the central curve "shows how the arithmetic works on the generator, not what any real choice costs". Cell 17 calls the load demonstration "not a finding about any real system". Six limits:
  - The axis 7 strings' "Battle casualties alone ... net benefit 41.2 (below treating all), treat all 44.6" (decision.py lines 431 to 433) follows the "(mechanism)" of the sentence before and carries no label or "synthetic" of its own. The printed lines of cells 23 and 25 likewise lean on the table and title beside them. Lifted out, none may be read as a figure for real battle casualties.
  - The aircraft comparisons (cells 21 to 23, 27 to 29; decision.py lines 267 to 336) score only deaths from bleeding into the abdomen. Their labels now say so, resolving the second review's limit on the words. The 6,867 battle casualties alive at triage who bleed from a limb or junction still count as none, though the MPTT-24's catastrophic haemorrhage step is written for them. The comparison may be read only as about bleeding into the abdomen.
  - The level of the chance of a bleeding death rests on three things: the share of bleeders the E-85 hazard kills within 24 hours (18.8%, generator.py lines 152 to 156), E-41's split, and the generator's assumed mix of bleeding sites among battle casualties (35.0% truncal, lines 160 to 163). Together they give the trunk 36.2%. The panel (decision.py lines 642 to 646) and cell 19 credit the level to E-41 and only the timing to E-85, and none names the site mix. The panel's figure may not be read as resting on E-41 and E-85 alone, or on E-85 for timing only.
  - The conditioning on survival (decision.py lines 231 to 237) treats a casualty not bleeding into the abdomen as certain to be alive. In the generator 162 of the 26,120 such battle casualties, 0.6%, are dead before triage, against 320 of 3,805 bleeding into the abdomen. The effect is negligible, and "surviving so far is itself evidence against bleeding" (cell 19) holds.
  - The load demonstration (cells 17 and 18; decision.py lines 189 to 206) charges every casualty flagged beyond capacity, those in need included, not false alarms alone (unchanged). It is not a model of E-125's simulation.
  - The two-casualty comparison's "Chance flying casualty 64 first is better: 100.0%" (cell 22) is the share of the belief's draws, which carry the uncertainty in the scan's accuracy and not whether either casualty is bleeding (unchanged). In the generator's truth casualty 64 is bleeding from an extremity, not into the abdomen, and casualty 1 is bleeding into the abdomen. So the order chosen, right in expectation, flies the wrong casualty first. The 100.0% may not be read as certainty that the order turns out better.
- Civilian data read as military: HOLDS (cells 0, 10, 14, 16, 17, 19, 20; decision.py lines 21 to 22, 215 to 216, 576 to 577 and 645 to 647). No civilian source is described as military or applied to a military casualty as if it were one. E-85 is now named as from civilian centres wherever it is applied to a casualty: the module docstring, `share_dead_by`, cell 19, the cell 20 title, axis 4 of the treatment column and the panel. Applying it to a battle casualty and from injury is called an assumption, which resolves the second review's limit. E-96 is a sepsis model in hospitalisations, E-88 ten Dutch hospitals, E-126 London on 7 July 2005 and E-125 a simulation, and the TARN figures are labelled "MPTT-24, civilian registry". The only military figures, the JTTR's (E-01, E-09, E-10) and E-37 to E-41's, are military. One limit, unchanged:
  - E-87, E-88 and E-126 are civilian, which the notebook does not say. It does not call them military either, and draws them as published points and an incident, not as figures for the military rule.
- A diagnosis result read as a treatment result: HOLDS (cells 12, 17 to 29; decision.py lines 7 to 13, 214 to 336, 341 to 401, 437 to 470 and 614 to 647; app/panels/decision.py lines 12 and 13). Cell 19 says the treatment section's results are kept apart from the diagnosis results. Cell 12's "flagging them as well, which is what treating everyone does, gains more than it costs" names treating everyone as flagging, scored in net benefit, not as an effect of treatment. The panel's "acting" is the same flag. The treatment case's expected deaths rest on an assumption stated in cell 19, the module docstring and the panel: that surgery on arrival stops a bleeding death. Two limits, unchanged:
  - The figure at cell 25 counts the expected bleeding deaths after triage among the missed bleeders: the generator's chance of a bleeding death, without tranexamic acid, for each bleeder the cut misses. Nothing in the generator or the notebook makes a flag avert a death. The bars are where the bleeding deaths fall among those missed, not deaths caused by missing them.
  - The panel's "flown now ... before arrival is" and "held 30 minutes more" give the chance of dying before surgery. They say nothing of what surgery achieves, and may not be read as the benefit of flying now.

## Numbers and their evidence ids

- E-96: HOLDS (cells 0, 10). 38,455 hospitalisations, 7% with sepsis, alerts on 18%, 67% not identified and an area under the curve of 0.63 are E-96's. "It still catches a third" is 100 less 67.
- E-93: HOLDS (cells 2, 10; decision.py lines 83 to 84). Net benefit judging a model by its consequences across threshold probabilities, and the threshold encoding how a false positive is weighed against a false negative, are E-93. The formula is introduced with "Here it is computed as" and not attributed to the source, which was read in abstract only. E-52 is not cited.
- E-01 and E-09: HOLDS (cells 10, 14 to 16, 26). 47.6% Priority 1 in the Joint Theatre Trauma Registry is both rows. The registry points are 1 minus 66.7% and 1 minus 67.0%; TARN's are 1 minus 53.5% and 1 minus 34.0%, all from E-09 (rules.py lines 145 and 146).
- E-10: HOLDS (cells 14 to 16; decision.py lines 153 to 159). The Sieve's 43.2% and 93.7% are E-10. Its over-triage of 0.138 is calculated here and labelled "calculated here". The arithmetic was checked: a positive predictive value of 0.862.
- E-12: HOLDS (cells 14, 15; decision.py lines 27 to 28 and 147 to 150). `under_over` computes exactly the authors' definitions.
- E-125: HOLDS (cells 14, 17). The definition and both findings are E-125's own words. One limit, unchanged: E-12's and E-125's definitions have the same form and differ in the condition counted as positive. Cell 14's "The sources do not all mean the same thing by over-triage" rests on that difference and on the register's silence on the rest.
- E-87: HOLDS (cells 14, 16; decision.py line 185). 21 studies of field triage protocols and the cited benchmarks are E-87.
- E-88: HOLDS (cells 14 to 16; decision.py lines 172 and 173). Ten Dutch hospitals; 63.8% and 7.4%; 21.6% and 30.6%. Its intervals are not drawn.
- E-126: HOLDS (cells 14, 16; decision.py line 186). 64%, 82% and 33%, critical mortality of 15% judged unrelated to over-triage. The register gives no under-triage and the figure draws none.
- E-85: HOLDS (cells 19, 20; decision.py lines 18 to 22, 214 to 218, 576 to 577 and 645 to 647; axis 4 in cell 27). Five prospective studies, 4,064 haemorrhaging patients and three hourly rates measured from admission are the row's. The generator's hazard is fitted exactly through 4.6%, 1.0% and 0.1% at 1, 6 and 9 hours (generator.py lines 141 to 146; `params.yaml` lines 409 to 418). One limit:
  - The register row does not say the studies were at civilian centres. The sentences that now say so rest on the background file for lens 05 (`05-stochastic.md` line 11, "civilian centres"), the fox2017 note (`_notes.md` line 121, "civilian trauma centres") and `params.yaml` line 417.
- E-37 and E-38: HOLDS (cell 24). UK Service personnel admitted under a trauma team; 10,371 injuries, extremities 44% and torso 7%.
- E-39: HOLDS (cell 24). US battlefield deaths, 2001 to 2011.
- E-40: HOLDS (cell 24; decision.py lines 644 to 645). 976 pre-facility deaths judged potentially survivable, 90.9% from haemorrhage.
- E-41: HOLDS (cell 24; decision.py lines 642 to 645). The three shares are E-41's. The notebook and the panel give them as the site of lethal haemorrhage among E-40's potentially survivable pre-facility deaths, the population the eastridge2012 brief and `params.yaml` line 406 give.
- E-08: HOLDS (axes 4 and 5 in cell 27). "Rules only (E-08)" and "Six yes-or-no steps" are E-08's six steps.
- D-23's statement: HOLDS (cells 10, 26). 26.5% is the share in need among the generator's injured in the military cohort, 0.2651. 47.6% is E-01 and E-09.
- Generator figures: HOLDS (cells 6, 7, 11, 13, 15, 18, 20, 22, 23, 25, 27, 28; the panel's values). Each was reproduced in the run or recomputed:
  - the hand count, the plain Python and the library agree on 3, 29 and 28;
  - net benefit at 0.10 is 10.5, 9.8, 10.5, 8.0, 8.2 and 7.4 on every stream, and 41.2, 41.3, 41.3, 30.0, 30.7 and 44.6 among battle casualties;
  - the unflagged shares are 0.221 to 0.337;
  - the hold curve runs from 2.04 to 8.80 per 100;
  - the two-casualty sums are 0.0302 and 0.0612;
  - the policy means are 1.699, 1.890, 1.992 and 1.155 before hospital, and 1.844, 1.890, 1.992 and 1.155 in hospital;
  - the failure counts and the 20 further samples check out;
  - so do the seven axes, the scorecard, and the panel's figures for every casualty the page shows.

## The generator

- The generator as the notebook, library and panel describe it: HOLDS (cells 1, 12, 19, 21, 24, 26; axes 4 and 6 in cell 27; decision.py lines 18 to 22, 99, 211 to 237, 269 to 272, 343 to 346, 373 to 401, 582 to 583 and 640 to 647). Each sentence was checked against `generator.py` and `params.yaml`.
  - "Fitted on the whole military cohort, disease admissions included" is right for lens 02's training sample, which is 100,000 casualties, seed 7, in the default mix (frequentist.py line 43 and lines 195 to 199; generator.py line 268).
  - Free fluid in the abdomen is bleeding in the trunk (line 299).
  - Each site's chance of a bleeding death is set so that bleeding deaths split as E-41 does (lines 24 and 160 to 165), averaged over severity (lines 167 to 173), without tranexamic acid (line 367).
  - The death time is drawn from the normalised distribution of the fitted hazard (lines 152 to 157 and 372). For a bleeder with chance q, the chance of being alive at a time t is therefore 1 minus q F(t). The chance of dying between the decision and a later time, alive at the decision, is q times the difference of F over that, which is what `death_between` and `expected_deaths` compute (decision.py lines 221 to 237). "Deaths before the decision are not counted" and "over the chance of being alive now" are therefore right.
  - `alive_at_triage` drops exactly the casualties whose bleeding death without tranexamic acid falls at or before the triage time (generator.py lines 369 and 376).
  - `torso_spread` draws seeds 43 to 62 (baseline.py line 70).
  - "The setting changes only the scan" is right: lens 02's probabilities are identical across the two settings.
  - The hazard runs from injury, an assumption the generator states (line 22).
  - Haemorrhage casualties 64 and 1 are battle casualties with a positive and a negative scan before hospital, alive at triage, as cells 19 and 21 say.

  One limit, new:
  - The page draws its casualties from 3,000 synthetic casualties without regard to survival (bayesian.py lines 437 to 444). Ten haemorrhage casualties in each setting (28, 122, 193, 279, 324, 400, 413, 437, 552 and 556) are recorded by the generator as dead from bleeding before their triage time. Casualty 413, for example, dies at 2 minutes and is triaged at 78. For these 20 of the 1,736 entries the panel's "Alive now and flown now" runs against the generator's record. Its figures there may be read only as those for a casualty like them who is alive. The pool is the walk-through's.

## Figures

Each figure was viewed and checked against its `concludes:` tag and the output it is drawn from.

- Cell 3, central figure: HOLDS. At nine to one the lowest expected cost, 56.1 per 100, falls at 0.10. Other weights move the lowest point to 0.05, 0.19, 0.31 and 0.52 for implied thresholds of 0.05, 0.20, 0.33 and 0.50. One limit, unchanged: the curve stops at 0.60, so for an implied threshold of 0.67 the lowest point sits at the edge (0.59). The tag holds only within that range, and only because lens 02 is calibrated on the cohort the curve is drawn on.
- Cell 8: HOLDS. One miss outweighs all the false alarms at these weights, as the tag says.
- Cell 11: HOLDS, within the cohort limits above. The learned models lie at or above both readings of the rule at every threshold drawn, by 0.09 per 100 at the closest (0.18). Both readings fall below treating everyone from 0.01 to 0.09, and below treating no one from 0.36. The y-axis is cut at -10 and 18, and the curves that leave it have their values in the table below.
- Cell 16: HOLDS, within the limits recorded under the wrong cohort or setting, the benchmark and E-125.
- Cell 18: HOLDS. The best threshold climbs from 0.10 at 60 per 100 to 0.37 at 10, within the limit on what the overflow cost charges.
- Cell 20: HOLDS. Each ten minutes held adds to the expected deaths, 0.66 per 100 in the first ten minutes and 0.45 in the last, from 2.04 at no delay to 8.80 at two hours. The title says "per 100 casualties like them", not this casualty's own risk: casualty 64's scan was a false positive.
- Cell 23: BREACH (the `concludes:` tag of cell 23 and its printed line for the scan in hospital; the treatment paragraph of cell 29; axis 6 of the treatment column in cell 27 and row 9 of the scorecard in cell 28; all from decision.py lines 320 to 327, through lines 335, 529 and 585). These say that, with the scan in hospital, ordering by belief and clock and ordering by the MPTT-24's priority "tie", with "no detectable difference":
  - the tag says "tying with it, with no detectable difference, when it comes only after, so on the generator the belief earns its place when the scan comes before the flight";
  - cell 29 says "the two orderings tie: there is no detectable difference";
  - the strings say "a tie: no detectable difference (the difference runs from -0.19 to +0.06 across 20 seeds)".

  The word tie is defined in cell 21 and the module docstring (lines 23 and 24) as the range across the 20 draws covering zero. The claim that the two do not differ goes beyond that rule, and the generator contradicts it:
  - Of the 20 draws of 2,000 pairs the figure is drawn from, belief and clock gives fewer expected deaths from bleeding into the abdomen in 15. The mean difference is -0.046 per 100 pairs (standard deviation 0.068 across draws), a difference the same 20 draws detect when their mean is taken.
  - On 400,000 pairs from the same casualties it gives 1.849 against 1.901, and on two more such draws -0.060 each.
  - On three further synthetic samples of 100,000 (seeds 43 to 45), 400,000 pairs each, it gives -0.050, -0.027 and -0.030.

  Before hospital the margin is -0.19, so the in-hospital margin is about a quarter of it, and smaller than the variation between single draws of 2,000 pairs. But it is not absent. A reader of the figure, the tag and the summary would conclude that the belief after triage adds nothing to the rule's priority when the scan comes only after the flight. On the generator it adds a little, every time it is measured on enough pairs. What may be claimed is three things. With the scan only in hospital, ordering by the belief after triage and the clock gives fewer expected deaths than the rule's priority by about 0.05 per 100 pairs. That is about a quarter of the margin before hospital. And a single draw of 2,000 pairs cannot reliably show it. It may not be claimed that the two orderings tie, that there is no detectable difference, or that the belief earns its place only when the scan comes before the flight. The figure itself, its bars at the mean and lines at the range, is drawn correctly; the sentences that state its conclusion are not.
- Cell 25: HOLDS, within the limit under diagnosis and treatment. At the accuracy cut, 0.32 (79.9%), 1,264 of 3,485 truncal bleeders are missed, with 257.1 expected bleeding deaths after triage. At the cost cut, 0.12 (60.8%), 367 are missed, with 52.3: 4.9 times fewer. On each of the 20 further samples the ratio runs from 4.5 to 5.3, so "several times ... on all twenty further samples" holds. Two limits, unchanged in substance and recomputed:
  - The move from 0.32 to 0.12 comes from the default weight of a miss over a false alarm, not from weighing by lethality. At nine to one without the lethality weights the cheapest cut is 0.01, which flags every battle casualty alive at triage, since the tree's lowest leaf is 0.115. At equal costs with the lethality weights alone it is 0.53, above the accuracy cut. The expected deaths among those missed fall mostly on truncal bleeders because the generator makes them likeliest to die after triage: 30.1% on average, against 19.3% junctional and 3.9% extremity.
  - Neither cut tells sites apart. The accuracy cut misses 36.3% of truncal, 40.9% of junctional and 40.9% of extremity bleeders; the cost cut 10.5%, 10.9% and 10.2%. "Losing the torso bleeds" is true in number and in expected deaths, not in share.
- App panel: HOLDS (app/panels/decision.py lines 9 to 13). It adds no figure. It is text, covered above, and its layout is that of 9da1c2c's lines 85 to 88.

## Further checks

- Axis 7 strings the module returns to every lens: HOLDS (decision.py lines 406 to 434 and 473 to 481; rules.py lines 308 to 311; frequentist.py lines 465 to 467; trees.py lines 506 to 511). Each was regenerated and read. Each gives net benefit at 0.10 (D-26) with the assumed rate and "(mechanism)", and each qualifier is right against its numbers:
  - "below treating all" for 41.2, 41.3, 30.0 and 30.7 against 44.6 among battle casualties, and for the ABC score's 8.2 against 29.1;
  - "it flags every casualty at this threshold" for the treatment tree, whose lowest leaf is 0.115;
  - no qualifier for lens 03's 4.3 and 9.3, or the MPTT-24's 3.1, against 3.0.
- `against_threshold`: HOLDS (decision.py lines 64 to 72; the panel's costs line). It compares at full precision and says so where the two print alike. The six panel entries that print at 0.100 (haemorrhage 76 and 114 and chest 83, in each setting) state the right side: 0.10010 at or above, 0.09957 and 0.09981 below.
- The analogy, cell 30: HOLDS. It cites no source and no number. One limit, unchanged: "they shift it with fatigue, with what happened last time and with how full the system feels" is unsourced; the register supports only that practice moved the line (E-88).
- The page's closing caption: HOLDS (app/streamlit_app.py lines 34 to 38). The decision panel's only published figures, E-85's 4,064 patients and five studies, carry their id. E-40 and E-41 are cited by id, and every other figure it shows is a mechanism or a stated assumption.
- Statements outside the checks. Two are noted without a mark:
  - Axis 5 of the treatment column, "Two sums of two products, compared" (decision.py line 580), was right when the second review read it. Since the conditioning on survival, each term is a product divided by the chance of being alive now (lines 231 to 237).
  - Axis 3 of the treatment column, "The belief behind each casualty is a distribution (lens 03)" (line 574), is true of lens 03's belief. But the scored policy acts on each belief's mean (lines 279 and 297 to 298); the distribution is carried only in the two-casualty example of cell 22.

VERDICT: BREACH
