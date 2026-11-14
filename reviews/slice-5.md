# Review of slice 5: lens 10, Decision theory

**Date:** 13 November 2026 · **Author:** Ross Taylor

Fifth review. D-25 allows three rounds. The fourth review (commit e731258) read the files at c8e6ed8 and recorded no breach, with three new limits. Commits 92e69fb and 7c110bd then changed how the aircraft comparison is scored, and this review reads the files as they stand at 7c110bd. The review was made against PRD sections 3 and 6.5, decisions D-8, D-19, D-21 and D-23 to D-27, design section 9, and `docs/background/10-decision-theory.md`.

These were read in full: `notebooks/10_decision_theory.ipynb`, `src/inference_labs/lenses/decision.py`, `app/panels/decision.py`, `app/panels/__init__.py` and `app/streamlit_app.py`. These were read for what the lens draws on, and are unchanged since the fourth review:
- frequentist.py lines 43, 195 to 211 and 478 to 483;
- rules.py lines 144 to 152 and 187 to 196;
- trees.py line 68;
- bayesian.py lines 63 to 75, 165 to 174, 344 to 356 and 436 to 541;
- baseline.py lines 70 and 167 to 177;
- the axis 7 rows that call `decision_value`: rules.py lines 308 to 311, frequentist.py lines 465 to 467 and trees.py lines 506 to 511.

For every sentence that cites them, the evidence register rows the notebook, library and panel cite were opened, together with the background notes on them. `src/inference_labs/generator.py` and `params.yaml` were read for every sentence that says how the generator works.

The notebook was run top to bottom from a fresh kernel. It finished in 30.0 seconds without error, every text output matched the committed one, and all eight figures were byte-identical to the committed ones. Each figure was viewed. The decision panel was rendered through `app/panels/decision.py` for every casualty app page 1 can show: all three patient types in both settings, 1,736 entries. Every entry was laid out as one subheader and two markdown lines, each equal to what `decision.panel` returns for that casualty, and no entry held an unformatted or missing value.

Cells are numbered from 0 in file order. Line numbers are those of the file named, as it stands at 7c110bd.

## What changed since the fourth review

**Notebook.** Cells 21, 23 and 29 changed in source, and cell 23 also in its `concludes:` tag, its figure and its outputs. The outputs of cells 27 and 28 changed with the library. The other 26 cells are unchanged in source, tag and output, and their figures are byte-identical to the ones the fourth review viewed.

**Library.** In `decision.py` these lines are new or changed:
- lines 270 to 274: the docstring of `aircraft_policy`, which now says each true bleeder is scored at their own chance of a bleeding death;
- line 286: `own`, each casualty's own chance of a bleeding death without tranexamic acid, from the generator's truth;
- line 295: the scoring of the random pairs passes `own` to `death_between`, in place of the trunk's average;
- line 313: the fourth way of choosing is renamed "knowing who is bleeding, and how badly";
- lines 585 and 586: the axis 1 string, renamed to match.

Every other line is unchanged. Lines after 270 have moved down by two, after 286 by three, and after 586 by four.

**App panel.** `app/panels/decision.py`, `app/panels/__init__.py` and `app/streamlit_app.py` are unchanged since the fourth review, and so is `panel` (decision.py lines 626 to 665, formerly 622 to 661) and every function it calls. Lines 9 to 13 of `app/panels/decision.py` lay out the same three elements as lines 85 to 88 of `git show 9da1c2c:app/streamlit_app.py`: the heading as a subheader, then the costs line and the evacuation line as markdown, in that order. They sit in the same place on the page, last of the panels and above the closing caption. The panel's ORDER is 5, after the trees panel's 4, and `panels.discovered()` returns the five panels in the order bayesian, rules, frequentist, trees, decision. The entry file renders them in that order (lines 31 and 32) and then the closing caption (lines 34 to 38).
- At 9da1c2c the page took the three elements from `decision.panel(self.record, self.line)` (bayesian.py line 518 at that commit).
- It now takes them from `decision.page_panel(walk)`, which calls `panel(walk.record, walk.line)` with the same arguments (decision.py lines 668 to 671).

So the panel's content is unchanged from 9da1c2c apart from what `panel` now returns. Since 9da1c2c, the threshold is given to three places and the probability is set against it by `against_threshold`. The evacuation line is now conditioned on the casualty being alive at the decision, says that surgery on arrival is taken to stop a bleeding death, and names its sources.

## Findings in brief

No breach is found. The changed lines hold. The aircraft comparison now scores each casualty truly bleeding into the abdomen at their own chance of a bleeding death in the generator. Cell 23's tag, its printed lines, cell 29, axes 1 and 6 of the treatment column and scorecard rows 8 and 9 say that ordering by belief and clock gives fewer expected deaths than the rule's priority on every sample in both settings, by about twice as much with the scan before the flight. That holds on the generator:
- on all 20 further samples, before hospital the paired difference runs from -0.233 to -0.192 per 100 pairs, mean -0.211;
- in hospital it runs from -0.115 to -0.083, mean -0.101;
- the ratio of the mean margins is 2.09, and sample by sample it runs from 1.87 to 2.39.

Two of the fourth review's three new limits are resolved:
- the scoring at the trunk's average chance is replaced by each bleeder's own chance, and the figures above are the ones the fourth review gave for that rescoring;
- the figure at cell 23 now draws the paired difference for each sample, so "on every sample" can be read from the figure itself.

The third, on `spread_words`, is carried unchanged.

Nothing in lines unchanged since the fourth review is found to be a breach, so nothing is marked MISSED.

New limits are recorded under each check:
- cell 21's "the choice itself sees only the belief and the clock" and the `aircraft_policy` docstring hold for the belief-and-clock choice only. In the generator, the belief and the rule's priority each carry part of the severity through the signs;
- the spread of each bleeder's own chance around the trunk's average comes from an assumed severity slope, which the notebook does not name;
- the right-hand panel of the figure at cell 23 carries no "synthetic", "mechanism" or "expected" of its own;
- the in-hospital mean for belief and clock prints as 1.749 in cell 23 and as 1.750 in cell 28;
- the module docstring still describes only the trunk's average chance.

## What must not be claimed

- That the civilian benchmark applies to military triage: HOLDS (cells 14, 16; decision.py line 186; the panel). Cell 14 says the review of 21 studies "cites benchmarks of under-triage below 5% and over-triage below 50% (E-87)", and that "It is drawn as one region among others, not as a standard the military rule should meet". The figure at cell 16 draws it as "benchmark region (E-87)", and its tag calls it "one choice among several rather than a fixed target". No cell, library string or panel line measures a military rule or the generator against it. Cells 12, 13, 21, 23, 26 and 29 and the panel do not mention it. Two limits, unchanged:
  - The notebook never says that the benchmark belongs to civilian trauma systems. Nor does it say that the benchmark's target condition differs from the MPTT-24's Priority 1. The benchmark's condition is severe injury in civilian systems (the background file's anchors); the rule's is need for a life-saving intervention. That difference is the background file's reason for the prohibition. The figure sets the military registry's point and the generator's military points beside the region on one plane. What may be claimed is only that the benchmark is a stated choice. How far any military point lies from it may not be read as a shortfall.
  - The register gives no definition of over-triage for E-87, so the region's horizontal edge at 0.50 may be on a different scale from E-12's 1 minus the positive predictive value. Cell 14 says the register gives none.
- That PATCH shows extra survivors were left with poor function: HOLDS (cells 0 to 30; decision.py lines 1 to 671; app/panels/decision.py lines 1 to 13). PATCH, E-78 and functional outcome are not mentioned in the notebook, the library or the panel, and E-78 is not in the notebook's evidence list.
- A specific exchange rate between a miss and a false alarm: HOLDS (cells 2 to 5, 8, 12, 13, 18, 26, 27, 29; decision.py lines 3 to 5, 16 to 17, 47 to 50, 427 to 429 and 643 to 644). The default of nine to one is called an assumption wherever it is set or stated:
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
  - E-101 gives two operating points of one model, not a rate.

  The overflow cost of 3, the flight time and the time held are each called an assumption. The changed cells 21, 23 and 29 and the changed library lines state no weight. One limit, unchanged:
  - Some cells give the weight without the word assumption, and rely on the cells around them to state it. They are:
    - the suptitle of the figure at cell 3 and the legend of the figure at cell 8 ("a miss weighed 9 times a false alarm" and "9 each");
    - cell 2's "the default costs weigh a miss nine times a false alarm, and every cost is a control the reader sets";
    - cell 12 ("the threshold of 0.10", "At 0.10, flagging a group pays wherever more than one in ten of them need an intervention");
    - the headings cell 13 prints.

    Lifted out of the notebook, none of them may be read as stating a rate from any source.

## Epistemic checks

- Accuracy quoted for the wrong cohort or setting: HOLDS (cells 3, 6, 10 to 16, 21 to 29; decision.py lines 98 to 207, 268 to 349, 450 to 483, 521 to 604 and 614 to 665). The battle figures are scoped as they are counted:
  - Cell 12 sets every stream (16.7% in need) against the battle casualties alone (50.2%).
  - Cell 13 prints both, with net benefit for each method on each.
  - The axis 7 strings give "Battle casualties alone, where a share of 0.502 need it".
  - The panel gives its battle figures as "On the battle casualties among that cohort's 100,000 synthetic casualties, the kind this page shows".

  Each was recomputed: 0.275 against 50.2%, 25.4% told not to act and 22.1% of those in need. At the panel's costs, not acting on those casualties costs 1.99 per casualty against 0.78 for acting, so "acting on all of them would cost less" is right.

  The aircraft comparison is scoped in every place it appears:
  - cell 21 gives "random pairs of synthetic battle casualties alive at the decision: 200,000 pairs from each of 20 further samples of 400,000 synthetic casualties";
  - so do the title of the figure at cell 23, cell 26, axes 1 and 6 of the treatment column, and scorecard rows 8 and 9.

  The further samples are drawn in the default military cohort (`params.yaml` line 25) and in the setting named. Cell 29 gives "on synthetic battle casualties", leaning on cells 21 and 26 for "alive at the decision". The rest of the notebook's figures keep their cohorts:
  - Its diagnosis figures are scoped to all 100,000 synthetic casualties of the military cohort, every stream (cell 3 and cell 11 titles, cells 26 and 29, axis 1 in cell 27), where lens 02's calibration is +0.001.
  - D-23's statement stands beside the MPTT-24's figures in cells 10 and 26.
  - The treatment figures belong to battle casualties alive at the decision.
  - Every published figure is given with its own cohort: E-96's 38,455 hospitalisations, E-87's 21 studies, E-88's ten Dutch hospitals, E-126's London incident, E-09's two registries, E-37 and E-38's trauma team cohort, and E-39 to E-41's US deaths.

  Eight limits, unchanged:
  - The generator's points in the table at cell 15 and the figure at cell 16 are on every stream, disease included, and are labelled only "generator's military cohort". On them the MPTT-24's over-triage is 64.1% (figure reading) against 33.0% in the military registry. The generator's points may not be read beside the registry's as like for like.
  - The MPTT-24's and the Military Sieve's points in cells 14 to 16 were measured on first recorded hospital observations and registry GCS, not at the point of injury (E-09, E-11). The notebook does not say so. The figure sets them beside triage in the field (E-88) and at the scene (E-126). They may not be read as the rules' accuracy at the point of injury.
  - The scorecard's diagnosis metric names (decision.py lines 532 and 533, cell 28) give the threshold, the target and the setting but not the cohort. Cell 26 scopes them to all 100,000 casualties of the military cohort, and they may be read only so.
  - The ten casualties of the by-hand count (cells 5 to 8) are battle casualties, on whom lens 02's probability runs low: four of the ten need an intervention, against a mean probability of 0.27. The count is arithmetic on ten and claims nothing about calibration.
  - In the torso failure (cells 24 and 25) the deaths by site are the generator's. The generator sets each site's chance of a bleeding death so that its bleeding deaths split as E-41 does. E-41's split was measured in potentially survivable deaths before a facility. Applying it to every bleeding death is an assumption of the generator (`params.yaml` lines 398 to 407).
  - Cell 24's "The injuries seen most often are not the bleeding that kills most often" sets E-38's injuries against E-41's lethal haemorrhage. "Kills most often" holds within the potentially survivable deaths named in the sentence before.
  - The diagnosis figures count every casualty in the sample, including the 482 battle casualties, 1.6%, whom the generator records as dead from bleeding before the triage time (decision.py lines 386 to 390). That covers cells 3 to 18, 27 and 28, the axis 7 strings, and the panel's costs line through `battle_not_acted` and `frequentist.battle_calibration`. The treatment and failure cases exclude those casualties. On the battle casualties alive at triage, 49.4% need an intervention against 50.2%; 25.7% are told not to act, and 21.7% of those need an intervention. The direction of every statement is unchanged. But the diagnosis and treatment halves of the notebook are on slightly different cohorts, and the notebook does not say so.
  - Cell 12's "The methods were fitted on every stream" holds for lens 02 and both trees (frequentist.py lines 195 to 199; trees.py line 68). It does not hold for the MPTT-24, which is coded from the published flowchart (E-08) and is not fitted. For the rule, the reversal rests only on the clause that follows: 33.7% need an intervention among the battle casualties it leaves unflagged.
- Proxy data read as the real thing: HOLDS (cells 3, 4, 8, 11 to 29; decision.py lines 30, 112, 164, 178 to 181, 193, 270 to 274, 320 to 321, 359, 402, 429, 452 to 453, 469, 479, 534, 546, 579 to 602, 617, 647, 652 to 653 and 664; app/panels/decision.py lines 11 to 13). Every result on the generator is called synthetic or a mechanism:
  - every figure title on generator data says so, the figure at cell 23 included ("synthetic casualties ... mechanism");
  - the operating-point table marks its generator rows "mechanism";
  - every scorecard row is labelled mechanism, rows 8 and 9 included;
  - axes 1, 2 and 6 carry "(mechanism)" in their names, and every axis 7 string carries it;
  - both sentences of the panel's costs line and its evacuation line close with it;
  - cell 12 and cell 13's printed headings carry it;
  - cell 29's treatment paragraph says "on every one of 20 synthetic samples" and "Both are on synthetic battle casualties and under assumed times".

  Cell 4 says the central curve "shows how the arithmetic works on the generator, not what any real choice costs". Cell 17 calls the load demonstration "not a finding about any real system". Six limits, unchanged, and one new:
  - The axis 7 strings' "Battle casualties alone ... net benefit 41.2 (below treating all), treat all 44.6" (decision.py lines 444 to 446) carries no label or "synthetic" of its own. It follows the "(mechanism)" of the sentence before. The printed lines of cells 23 and 25 likewise lean on the table and title beside them. Lifted out, none may be read as a figure for real battle casualties.
  - The aircraft comparisons (cells 21 to 23, 27 to 29; decision.py lines 268 to 349) score only deaths from bleeding into the abdomen, and their labels say so. In the evaluation sample, 6,867 battle casualties alive at triage bleed from a limb or junction and still count as none, though the MPTT-24's catastrophic haemorrhage step is written for them. The comparison may be read only as about bleeding into the abdomen.
  - The level of the chance of a bleeding death rests on three things. The first is the share of bleeders the E-85 hazard kills within 24 hours (18.8%, generator.py lines 152 to 156). The second is E-41's split. The third is the generator's assumed mix of bleeding sites among battle casualties (35.0% truncal, lines 160 to 163). Together they give the trunk 36.2%. The panel (decision.py lines 659 to 664) and cell 19 credit the level to E-41 and only the timing to E-85, and neither names the site mix. The panel's figure may not be read as resting on E-41 and E-85 alone, or on E-85 for timing only. The same three set the average level of each bleeder's own chance, which the aircraft comparison now scores.
  - The conditioning on survival in `expected_deaths` (decision.py lines 232 to 238) treats a casualty not bleeding into the abdomen as certain to be alive. In the generator, 162 of the 26,120 such battle casualties, 0.6%, are dead before triage, against 320 of 3,805 bleeding into the abdomen. The effect is negligible, and "surviving so far is itself evidence against bleeding" (cell 19) holds.
  - The load demonstration (cells 17 and 18; decision.py lines 190 to 207) charges every casualty flagged beyond capacity, those in need included, not false alarms alone. It is not a model of E-125's simulation.
  - The two-casualty comparison's "Chance flying casualty 64 first is better: 100.0%" (cell 22) is the share of the belief's draws. Those draws carry the uncertainty in the scan's accuracy, not whether either casualty is bleeding. In the generator's truth, casualty 64 is bleeding from an extremity, not into the abdomen, and casualty 1 is bleeding into the abdomen. So the order chosen, right in expectation, flies the wrong casualty first. The 100.0% may not be read as certainty that the order turns out better.
  - New. The right-hand panel of the figure at cell 23, "The same comparison, sample by sample", carries no "synthetic" or "mechanism" of its own, and its axis reads "fewer deaths" where the left-hand axis reads expected deaths. It leans on the left-hand title, which says "synthetic casualties ... mechanism" and "expected deaths". Lifted out, it may be read only as fewer expected deaths on synthetic casualties.
- Civilian data read as military: HOLDS (cells 0, 10, 14, 16, 17, 19, 20; decision.py lines 21 to 22, 165 to 170, 217, 593 to 595 and 662 to 664). No civilian source is described as military, or applied to a military casualty as if it were one. E-85 is named as from civilian centres wherever it is applied to a casualty: the module docstring, `share_dead_by`, cell 19, the cell 20 title, axis 4 of the treatment column and the panel. Applying it to a battle casualty, and from injury, is called an assumption. E-96 is a sepsis model in hospitalisations, E-88 ten Dutch hospitals, E-126 London on 7 July 2005 and E-125 a simulation. The TARN figures are labelled "MPTT-24, civilian registry". The only military figures are military: the JTTR's (E-01, E-09, E-10) and E-37 to E-41's. The changed cells and library lines cite no source. One limit, unchanged:
  - E-87, E-88 and E-126 are civilian, which the notebook does not say. It does not call them military either, and draws them as published points and an incident, not as figures for the military rule.
- A diagnosis result read as a treatment result: HOLDS (cells 12, 17 to 29; decision.py lines 7 to 13, 215 to 349, 450 to 483 and 626 to 665; app/panels/decision.py lines 12 and 13). Cell 19 says the treatment section's results are kept apart from the diagnosis results. Cell 29 keeps them in separate paragraphs, and the scorecard keeps them in separate cases and columns. Cell 12's "flagging them as well, which is what treating everyone does, gains more than it costs" calls treating everyone flagging, scored in net benefit, not an effect of treatment. The panel's "acting" is the same flag. The treatment case's expected deaths rest on an assumption stated in cell 19, the module docstring and the panel: that surgery on arrival stops a bleeding death. The changed cells 21, 23 and 29 stay within the treatment case. Two limits, unchanged:
  - The figure at cell 25 counts the expected bleeding deaths after triage among the missed bleeders. Each is the generator's chance of a bleeding death, without tranexamic acid, for a bleeder the cut misses. Nothing in the generator or the notebook makes a flag avert a death. The bars are where the bleeding deaths fall among those missed, not deaths caused by missing them. The tag's "accuracy ignores which misses kill" may be read only so.
  - The panel's "flown now ... before arrival is" and "held 30 minutes more" give the chance of dying before surgery. They say nothing of what surgery achieves, and may not be read as the benefit of flying now.

## Numbers and their evidence ids

- E-96: HOLDS (cells 0, 10). A deployed model checked independently, 38,455 hospitalisations, 7% with sepsis, alerts on 18%, 67% not identified and an area under the curve of 0.63 are E-96's. "It still catches a third" is 100 less 67.
- E-93: HOLDS (cells 2, 10; decision.py lines 84 to 85). Net benefit judging a model by its consequences across threshold probabilities, and the threshold encoding how a false positive is weighed against a false negative, are E-93. The formula is introduced with "Here it is computed as" and is not attributed to the source, which was read in abstract only. E-52 is not cited.
- E-01 and E-09: HOLDS (cells 10, 14 to 16, 26). 47.6% Priority 1 in the Joint Theatre Trauma Registry is in both rows. The registry points are 1 minus 66.7% and 1 minus 67.0%, and TARN's are 1 minus 53.5% and 1 minus 34.0%, all from E-09 (rules.py lines 145 and 146). TARN's 0.660 is E-12's 66.0%.
- E-10: HOLDS (cells 14 to 16; decision.py lines 154 to 160). The Sieve's 43.2% and 93.7% are E-10's. Its over-triage of 0.138 is calculated here and labelled "calculated here". The arithmetic was checked: a positive predictive value of 0.862.
- E-12: HOLDS (cells 14, 15; decision.py lines 27 to 28 and 148 to 151). `under_over` computes exactly the authors' definitions.
- E-125: HOLDS (cells 14, 17). The definition and both findings are E-125's own words. One limit, unchanged: E-12's and E-125's definitions have the same form and differ in the condition counted as positive. Cell 14's "The sources do not all mean the same thing by over-triage" rests on that difference and on the register's silence on the rest.
- E-87: HOLDS (cells 14, 16; decision.py line 186). The 21 studies of field triage protocols and the cited benchmarks are E-87's.
- E-88: HOLDS (cells 14 to 16; decision.py lines 173 and 174). Ten Dutch hospitals; 63.8% and 7.4%; 21.6% and 30.6%. Its intervals are not drawn.
- E-126: HOLDS (cells 14, 16; decision.py line 187). 64%, 82% and 33%, and critical mortality of 15% judged unrelated to over-triage, are E-126's. The register gives no under-triage and the figure draws none.
- E-85: HOLDS (cells 19, 20; decision.py lines 18 to 22, 215 to 219, 593 to 595 and 662 to 664; axis 4 in cell 27). Five prospective studies, 4,064 haemorrhaging patients and three hourly rates measured from admission are the row's. The generator's hazard is fitted exactly through 4.6%, 1.0% and 0.1% at 1, 6 and 9 hours (generator.py lines 141 to 146; `params.yaml` lines 409 to 418). One limit, unchanged:
  - The register row does not say the studies were at civilian centres. The sentences that say so rest on the background file for lens 05 (`05-stochastic.md` line 11, "civilian centres"), the fox2017 note (`_notes.md` line 121, "civilian trauma centres") and `params.yaml` line 417.
- E-37 and E-38: HOLDS (cell 24). UK Service personnel admitted under a trauma team, in the register's section on UK field hospital admissions in Afghanistan (E-34); 10,371 injuries, extremities 44% and torso 7%.
- E-39: HOLDS (cell 24). US battlefield deaths, 2001 to 2011.
- E-40: HOLDS (cell 24; decision.py lines 661 to 662). 976 pre-facility deaths judged potentially survivable, 90.9% of them from haemorrhage.
- E-41: HOLDS (cell 24; decision.py lines 660 to 662). The three shares are E-41's. The notebook and the panel give them as the site of lethal haemorrhage among E-40's potentially survivable pre-facility deaths. That is the population the eastridge2012 brief and `params.yaml` line 406 give.
- E-08: HOLDS (axes 4 and 5 in cell 27). "Rules only (E-08)" and "Six yes-or-no steps" are E-08's six steps.
- D-23's statement: HOLDS (cells 10, 26). 26.5% is the share in need among the generator's injured in the military cohort, 0.2651. 47.6% is E-01's and E-09's.
- Generator figures: HOLDS (cells 6, 7, 11, 13, 15, 18, 20, 22, 23, 25, 27, 28; the panel's values). Each was reproduced in the run or recomputed:
  - the hand count, the plain Python and the library agree on 3, 29 and 28;
  - net benefit at 0.10 is 10.5, 9.8, 10.5, 8.0, 8.2 and 7.4 on every stream, and 41.2, 41.3, 41.3, 30.0, 30.7 and 44.6 among battle casualties;
  - the unflagged shares run from 0.221 to 0.337;
  - the hold curve runs from 2.04 to 8.80 per 100;
  - the two-casualty sums are 0.0302 and 0.0612;
  - the policy means over the 20 further samples are 1.639, 1.851, 1.982 and 1.123 before hospital, and 1.749, 1.851, 1.982 and 1.123 in hospital. The paired differences run from -0.233 to -0.192 before hospital and from -0.115 to -0.083 in hospital, all 20 below zero in each setting. The fourth way, knowing who is bleeding and how badly, is lowest on every sample;
  - "about twice as much" (cells 23 and 29) is the ratio of the mean margins, 0.211 against 0.101, which is 2.09. Sample by sample the ratio runs from 1.87 to 2.39. "The scan roughly doubles what the belief adds" (cell 23's tag) is the same ratio: of the margin over the rule with the scan before the flight, 52.1% comes through the scan (46.4% to 58.2% by sample);
  - the failure counts and the 20 further samples of cell 25 check out;
  - so do the seven axes, the scorecard, and the panel's figures for every casualty the page shows.

## The generator

- The generator as the notebook, library and panel describe it: HOLDS (cells 1, 12, 19, 21, 23, 24, 26, 29; axes 4 and 6 in cell 27; decision.py lines 18 to 26, 100, 212 to 238, 268 to 330, 354 to 414, 598 to 602 and 654 to 664). Each sentence was checked against `generator.py` and `params.yaml`.
  - "Fitted on the whole military cohort, disease admissions included" is right for lens 02's training sample: 100,000 casualties, seed 7, in the default mix (frequentist.py line 43 and lines 195 to 199; generator.py line 277).
  - Free fluid in the abdomen is bleeding in the trunk (line 299).
  - Each site's chance of a bleeding death is set so that bleeding deaths split as E-41 does (lines 24 and 160 to 165). It is averaged over severity (lines 167 to 173), without tranexamic acid (line 367).
  - New. Each bleeder's own chance is the logistic of the site's intercept plus 0.75 times their severity (generator.py lines 364 to 367), the intercept set so that the average over severity is the site's chance. So "each true bleeder's own chance of a bleeding death in the generator, which depends on how severe the bleeding is" (cell 21) is right. Among the evaluation sample's casualties bleeding into the abdomen and alive at triage, it runs from 0.027 to 0.882, mean 0.357, against the trunk's average of 0.362.
  - The death time is drawn from the normalised distribution of the fitted hazard, independently of the chance of a bleeding death (lines 152 to 157 and 372). For a bleeder with chance q, the chance of being alive at a time t is therefore 1 minus q F(t). For a bleeder alive at the decision, the chance of dying between the decision and a later time is q times the difference of F over that span, divided by the chance of being alive at the decision. That is what `death_between` computes (decision.py lines 222 to 229), now with each bleeder's own q in the scoring (lines 286 and 294 to 295) and the trunk's average in `expected_deaths` (lines 232 to 238). "Deaths before the decision are not counted" and "over the chance of being alive now" are therefore right.
  - `alive_at_triage` drops exactly the casualties whose bleeding death without tranexamic acid falls at or before the triage time (generator.py lines 369 and 376). `_score_pairs` applies it before any pair is drawn (decision.py line 281), so "alive at the decision" is right for every pair.
  - The 20 further samples of cell 21 are `generator.sample(400,000, seed)` for seeds 43 to 62, in the setting named and the default military cohort. Each sample is cut to its battle stream exactly as `rules.battle_sample` cuts the evaluation sample (rules.py lines 187 to 189). 200,000 pairs are drawn from each, and the second casualty of a pair is never the first (decision.py lines 291 and 292).
  - `torso_spread` draws seeds 43 to 62 at 100,000 (baseline.py line 70).
  - "The setting changes only the scan" is right. Lens 02's probabilities are identical across the two settings. In every one of the 20 further samples, the rule's priority, chance and knowing who is bleeding and how badly score the same in both settings, so the change from one setting to the other isolates the scan.
  - "Where the scan is done in hospital it comes on arrival, after the flight" (cell 21) matches the generator, which times the scan in hospital at arrival at Role 2. The belief used there is the one after triage (decision.py line 283).
  - The hazard runs from injury, an assumption the generator states (line 22).
  - Haemorrhage casualties 64 and 1 are battle casualties with a positive and a negative scan before hospital, alive at triage, as cells 19 and 21 say.

  Three limits:
  - The page draws its casualties from 3,000 synthetic casualties without regard to survival (bayesian.py lines 436 to 443). The generator records ten haemorrhage casualties in each setting as dead from bleeding before their triage time: 28, 122, 193, 279, 324, 400, 413, 437, 552 and 556. Casualty 413, for example, dies at 2 minutes and is triaged at 78. For these 20 of the 1,736 entries, the panel's "Alive now and flown now" runs against the generator's record. Its figures there may be read only as those for a casualty like them who is alive. The pool is the walk-through's (unchanged).
  - New. Cell 21's "the choice itself sees only the belief and the clock" and the `aircraft_policy` docstring's "The choice itself can use only the belief and the trunk's average chance, since severity is not seen" (decision.py lines 272 and 273) describe the belief-and-clock choice. The rule's choice uses the MPTT-24's priority and the clock, and chance uses neither. Severity is a latent the choices do not see directly, but it reaches them through the signs. In bleeding casualties, systolic pressure falls 12 mm Hg per standard deviation of severity (generator.py line 311; `params.yaml` lines 335 to 341). Heart rate rises with its centile (line 317; `params.yaml` line 179). Lens 03's belief updates on systolic pressure at or below 90 (bayesian.py lines 69 and 346), and the rule reads heart rate and conscious level. "Not seen" may be read only as "not seen directly". The comparison is not one between choices blind to severity and an oracle that sees it.
  - New. The spread of each bleeder's own chance around the trunk's average comes from the severity slope of 0.75 log odds per standard deviation (`params.yaml` lines 420 to 426), labelled an assumption. The "and how badly" of the fourth way, and the size of the margins in cells 23 and 29, rest on that assumption as well as on the three things behind the level. The notebook does not name it. The margins may be read only as the generator's, under that slope.

## Figures

Each figure was viewed and checked against its `concludes:` tag and the output it is drawn from.

- Cell 3, central figure: HOLDS. At nine to one, the lowest expected cost, 56.1 per 100, falls at 0.10. Other weights move the lowest point to 0.05, 0.19, 0.31 and 0.52, for implied thresholds of 0.05, 0.20, 0.33 and 0.50. One limit, unchanged: the curve stops at 0.60, so for an implied threshold of 0.67 the lowest point sits at the edge (0.59). The tag holds only within that range, and only because lens 02 is calibrated on the cohort the curve is drawn on.
- Cell 8: HOLDS. One miss outweighs all the false alarms at these weights, as the tag says. The cut at 0.1 misses none and costs 3.
- Cell 11: HOLDS, within the cohort limits above. The learned models lie at or above both readings of the rule at every threshold drawn, by 0.09 per 100 at the closest (0.18). Both readings fall below treating everyone from 0.01 to 0.09, and below treating no one from 0.36. The y-axis is cut at -10 and 18, and the curves that leave it have their values in the table below.
- Cell 16: HOLDS, within the limits recorded under the wrong cohort or setting, the benchmark and E-125.
- Cell 18: HOLDS. The best threshold climbs from 0.10 at a capacity of 60 per 100 to 0.37 at 10, within the limit on what the overflow cost charges.
- Cell 20: HOLDS. Each ten minutes held adds to the expected deaths: 0.66 per 100 in the first ten minutes and 0.45 in the last, from 2.04 at no delay to 8.80 at two hours. The title says "per 100 casualties like them", not this casualty's own risk: casualty 64's scan was a false positive.
- Cell 23: HOLDS, within the new limits under the generator and the proxy check. The tag says that scoring on twenty samples "shows the belief and the clock beating the rule's priority on every sample in both settings, by about twice as much when the scan comes before the flight as when it comes only after, so on the generator the scan roughly doubles what the belief adds". The left-hand panel draws the four means with the range across the samples. The right-hand panel draws the paired difference, belief and clock less the rule's priority, for each of the 20 samples in each setting. All 40 points lie below zero, from -0.233 to -0.192 before hospital and from -0.115 to -0.083 in hospital, with the before-hospital cluster at about twice the depth of the in-hospital one. The printed lines give the same ranges to two places. The ranges drawn on the left still overlap in hospital (belief and clock 1.691 to 1.811, the rule's priority 1.792 to 1.920). That no longer matters, because the right-hand panel shows the paired comparison on which "on every sample" rests. The fourth review's limit on this figure is resolved. One limit, new:
  - Cell 23's table prints the in-hospital mean for belief and clock as 1.749, and scorecard row 9 in cell 28 prints it as 1.750: the same mean, 1.74947, rounded once to three places and once to four and then displayed to three. Axis 6 gives 1.75. The difference is display only.
- Cell 25: HOLDS, within the limit under diagnosis and treatment. At the accuracy cut, 0.32 (79.9%), 1,264 of 3,485 truncal bleeders are missed, with 257.1 expected bleeding deaths after triage. At the cost cut, 0.12 (60.8%), 367 are missed, with 52.3: 4.9 times fewer. On each of the 20 further samples the ratio runs from 4.5 to 5.3, so "several times ... on all twenty further samples" holds. Two limits, unchanged:
  - The move from 0.32 to 0.12 comes from the default weight of a miss over a false alarm, not from weighing by lethality. At nine to one without the lethality weights, the cheapest cut is 0.01, which flags every battle casualty alive at triage, since the tree's lowest leaf is 0.115. At equal costs with the lethality weights alone it is 0.53, above the accuracy cut. The expected deaths among those missed fall mostly on truncal bleeders because the generator makes them the likeliest to die after triage: 30.1% on average, against 19.3% junctional and 3.9% extremity.
  - Neither cut tells sites apart. The accuracy cut misses 36.3% of truncal, 40.9% of junctional and 40.9% of extremity bleeders; the cost cut misses 10.5%, 10.9% and 10.2%. "Losing the torso bleeds" is true in number and in expected deaths, not in share.
- App panel: HOLDS (app/panels/decision.py lines 9 to 13). It adds no figure. It is text, covered above, and its layout is that of 9da1c2c's lines 85 to 88.

## Further checks

- Axis 7 strings the module returns to every lens: HOLDS (decision.py lines 419 to 447 and 486 to 494; rules.py lines 308 to 311; frequentist.py lines 465 to 467; trees.py lines 506 to 511). Each was regenerated and read. Each gives net benefit at 0.10 (D-26) with the assumed rate and "(mechanism)", and each qualifier is right against its numbers:
  - "below treating all" for 41.2, 41.3, 30.0 and 30.7 against 44.6 among battle casualties, and for the ABC score's 8.2 against 29.1;
  - "it flags every casualty at this threshold" for the treatment tree, whose lowest leaf is 0.115;
  - no qualifier for lens 03's 4.3 and 9.3, or the MPTT-24's 3.1, against 3.0.
- `against_threshold`: HOLDS (decision.py lines 65 to 73; the panel's costs line). It compares at full precision, and where the two values print alike it says so. The six panel entries that print at 0.100 state the right side: haemorrhage 76 and 114 and chest 83, in each setting. Their probabilities are 0.10010, at or above, and 0.09957 and 0.09981, below.
- `spread_words`: HOLDS (decision.py lines 333 to 340). With every spread the notebook, scorecard and panel pass to it, it returns "fewer" or "more" with the range, and each is right against its numbers. One limit, unchanged:
  - For a spread that covers zero it still returns "a tie: no detectable difference". Cell 21 and the module docstring (lines 23 and 24) define a tie only as a spread that covers zero. A mean across the same seeds can detect what the range does not. No output of this slice shows the phrase. Should any later caller show it, it may be read only as "the range across the seeds covers zero".
- `aircraft_summary`'s "pairs" (decision.py line 349) is taken from `aircraft_policy`, the evaluation sample's draw, while its means come from the further samples. Both draws use 200,000 pairs, and no output shows the entry.
- The analogy, cell 30: HOLDS. It cites no source and no number. One limit, unchanged: "they shift it with fatigue, with what happened last time and with how full the system feels" is unsourced. The register supports only that practice moved the line (E-88).
- The page's closing caption: HOLDS (app/streamlit_app.py lines 34 to 38). The decision panel's only published figures, E-85's 4,064 patients and five studies, carry their id. E-40 and E-41 are cited by id, and every other figure it shows is a mechanism or a stated assumption.
- Statements outside the checks. Three are noted without a mark:
  - Axis 5 of the treatment column, "Two sums of two products, compared" (decision.py line 597), was right when the second review read it. Since the conditioning on survival, each term is a product divided by the chance of being alive now (lines 232 to 238). The module docstring's "lens 03's belief ... times the generator's chance" (lines 10 to 13) is the same simplification (unchanged).
  - Axis 3 of the treatment column, "The belief behind each casualty is a distribution (lens 03)" (line 591), is true of lens 03's belief. But the scored policy acts on each belief's mean (lines 284 and 300 to 301); the distribution is carried only in the two-casualty example of cell 22 (unchanged).
  - New. The module docstring's assumptions (lines 18 to 22) still give the chance of dying before arrival as the truncal site's average. That is the chance every choice, the hold curve, the two-casualty example and the panel use. The scoring of the random pairs now uses each bleeder's own chance (lines 286 and 294 to 295), as the `aircraft_policy` docstring (lines 270 to 274) and cell 21 say. The module docstring is shown in neither the notebook nor the panel.

VERDICT: HOLDS

## Reviewed sources

- `notebooks/10_decision_theory.ipynb` 0abedac52abc458f0eacda3394410cbf94c476419d163ffc19345590478649d5
- `src/inference_labs/lenses/decision.py` 7f322c5e5793a01a9294159739e2c2cac49c94e8df9560ccaffff06726e49c4f
- `app/panels/decision.py` 8fc7fb89f394638291f092de6f3dc73103967cf5e48f8cc57dd43e85663cf6f1
