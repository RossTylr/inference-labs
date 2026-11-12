# Review of slice 1: lens 03, Bayesian

**Date:** 12 November 2026 · **Author:** Ross Taylor

Second review, after attempt 4. Reviewed against PRD sections 3 and 5 and `docs/background/03-bayesian.md`. Read: `notebooks/03_bayesian.ipynb`, `src/inference_labs/lenses/bayesian.py` and `app/streamlit_app.py`, with the evidence register rows the notebook cites and the briefs of their sources. The notebook was run top to bottom from a fresh kernel; it finished in 2.5 seconds and every text output matched the committed one. Cells are numbered from 0 in file order. Line numbers are those of the file named.

The two findings of the first review are corrected. Cells 22 and 24 now name the primary analysis, the 9,202 patients treated within 3 hours, as E-27 does, and the title of the figure at cell 39 now describes the sum of bleeds found and bleeds missed.

## What must not be claimed

- That a 93% posterior probability is proof: HOLDS (cells 21, 27). Cell 21 gives E-73's figure and says in the same paragraph that it is not proof, that it is conditional on the model and the prior, and that the abstract of the reanalysis does not state the prior. Cell 27 sets the RePHILL figure beside it and says the Bayesian answer rests on a prior that has to be defended. No posterior in the notebook or the app is presented as settling a question.
- That the notebook's CRASH-3 analysis is a published result: HOLDS (cells 21 to 24, 28, 42). Cell 21 states in bold that it is a teaching reanalysis, not a published result, and that it carries the mechanism label, citing E-33 for the absence of a published one; E-33 supplies no number. The only CRASH-3 figure on the scorecard (cell 42, row 8) is computed on the synthetic fixture and labelled mechanism. The app shows no CRASH-3 result.

## Epistemic checks

- Accuracy quoted for the wrong cohort or setting: HOLDS (cells 5, 13, 14, 16, 32 to 34; bayesian.py lines 72 to 81). Each scan figure is used in its own setting: E-16 before hospital, E-14 in hospital, with the in-hospital Beta shapes stated as an assumption (cell 13). The one cross-setting use is the failure case, where it is the point and is named as such. The statements that the 25% describes a scan called positive and that the paper does not make clear how indeterminate scans enter its table are the register's own (partyka2022 brief). E-31 supplies only the 90 mm Hg threshold; its accuracy is not quoted.
- Proxy data read as the real thing: HOLDS (cells 16, 20, 27, 28, 41 to 43; app lines 57 to 60). Every result on the generator is called a mechanism, and the CRASH-3 fixture is called synthetic, random and clinically meaningless where it is used. Two limits on what may be claimed. Scorecard row 8 is 0.998 because the CRASH-2 prior on its own gives 0.997; the fixture's own interval runs from 0.41 to 1.54, so the row measures the prior, not the fixture, and says nothing about tranexamic acid. The pre-hospital belief in cell 34 meets the generator's count because the generator draws its scans with E-16's accuracy, so that agreement holds by construction.
- Civilian data read as military: BREACH (cell 29; bayesian.py lines 476 to 477, shown at app line 54; app lines 57 to 60). The relative risk of bleeding death by delay is E-22, from CRASH-2 (crash2_2011). The register describes CRASH-2's population as civilian and largely from low- and middle-income settings, and says it cannot support claims about military casualties specifically (crash2_2010 brief; E-19). Cell 29 applies the figure to the casualty without naming the trial or its population. The app applies it to a synthetic battle casualty with no source at all, while its caption names the scan studies as civilian, so a reader cannot tell that this input is civilian too. Cell 5 sets the standard the notebook itself uses: a civilian figure used for a military casualty is stated to be an assumption. The scan studies, PROPPR, STAAMP, CRASH-3 and RePHILL are nowhere described as military.
- A diagnosis result read as a treatment result: BREACH (bayesian.py lines 464 and 476 to 477, shown at app lines 31 to 32 and 54). The notebook holds: cell 31 says the belief-weighted reduction is a diagnosis result put to use, not a treatment result, and the lens's `treat` returns the belief unchanged (bayesian.py lines 383 to 385). The app does not carry that statement. For haemorrhage casualty 39 before hospital, at the default prior, it shows a metric "Belief-weighted reduction in bleeding death" of 0.15 and, in the findings, "the reduction is 0.15 (0.07 to 0.24)", with nothing to say what the number is. It is a belief multiplied by a relative reduction, not a change in that casualty's risk of death. Read as a change in risk, as the wording invites, it is six times the whole absolute reduction E-22 reports for treatment within an hour (7.7% against 5.3%, 2.4 points).

## Numbers and their evidence ids

- Scan accuracy: HOLDS (cells 3, 5, 6, 8, 9). 21 of 84, 257 of 266, 25% and 96%, the third of abdominal scans indeterminate, the physician-staffed civilian helicopter service and the blunt trauma are in E-16 and the partyka2022 brief; 74% and 98% are in E-14. The statement that both studies are civilian goes beyond the netherton2019 brief, which says only that its pooled studies are largely in hospital; it narrows the claim rather than widening it.
- Counts and grids: HOLDS (cell 4). 108 patients, 32% and 55% are in E-64; the frequency finding is E-114, used without its number.
- PROPPR and its reanalysis: HOLDS (cell 21). P=.12 is E-72; 93% is E-73.
- CRASH-2: HOLDS (cells 21, 24). 0.91 (0.85 to 0.97) and the prespecified rule on subgroups are in E-20. Cell 24 calls CRASH-2's patients "bleeding into the trunk"; the register describes them as trauma patients with significant haemorrhage, wherever the bleeding. The sentence's point, that exchangeability with head injury is a clinical question, does not depend on it.
- CRASH-3: HOLDS (cells 21, 22, 24). 0.94 (0.86 to 1.02) for the 9,202 treated within 3 hours is E-27 as now worded; 0.78 (0.64 to 0.95) is E-28.
- STAAMP, the brain injury trial and the missing reanalysis: HOLDS (cell 21). E-74 is used without a number; 0.1 and 0.025 are in E-79; E-33 supplies no number.
- RePHILL: HOLDS (cells 25 to 27). Every figure is in E-77, and the probabilities are marked as calculated here, not reported by the trial, as the background file requires.
- Tranexamic acid by delay: HOLDS (cell 29; bayesian.py lines 84 to 88). All three bands match E-22, and the log-normal shape is stated as an assumption. Two limits on what may be claimed: E-23 records that the timing analysis is exploratory, which cell 29's "reduced death from bleeding" does not say; and the app takes the time to pre-hospital care as the time of treatment (bayesian.py lines 476 and 499) without saying so.
- Triage threshold: HOLDS (cell 16; bayesian.py line 63). 90 mm Hg is in E-31.
- Predictive coding: HOLDS (cell 44). E-55.
- Generator figures: HOLDS (cells 17, 19, 33, 35, 36, 42). Each is counted on the generator and labelled as such. The structural statement in cell 35 was checked on 100,000 generated casualties: no casualty with a heart rate over 100 is walking.

## Figures

Each figure was checked against its `concludes:` tag and the output it is drawn from.

- Cell 3, central figure: HOLDS. Counting 15 of 92 casualties still bleeding after a clear scan changes the answer a reader gives to the hook.
- Cell 7: HOLDS. The same hundred in two settings shows that the setting decides what a clear scan is worth.
- Cell 10: HOLDS. Ten draws show the belief as a spread, one of the ten below one half.
- Cell 15: HOLDS. A positive scan in hospital is decisive; before hospital it is not, and a clear scan there barely moves the belief.
- Cell 18: HOLDS. Casualty 1 has the same record in both settings (systolic 108 mm Hg, scan clear, bleeding), so the two lines are comparable and the title is true.
- Cell 20: HOLDS. The calibration plot is titled mechanism, not evidence, and the text says its agreement confirms the arithmetic only.
- Cell 23: HOLDS. The prior moves the probability of any benefit from 91% to 99.9%; no prior puts weight on a reduction of a fifth or more in the primary analysis, which is the only result plotted.
- Cell 34: HOLDS. The figure's point is the gap between the borrowed curve and the count, and that stands; the pre-hospital curve meets the count by construction.
- Cell 37: HOLDS. A scan counted twice overstates the belief by a large margin, two signs of one derangement by a small one, and independent findings agree with the count.
- Cell 39: HOLDS. The title now describes the plotted sum correctly. Its "up to 113%" is the upper end of the 95% range, and single draws reach 125%; the conclusion, that the program reports an impossible sum without warning, does not depend on which.
- App page 1, belief band: HOLDS (app lines 34 to 53). The band and table come from the library, the dotted line is one half, and the caption says treatment and evacuation leave the belief unchanged.

VERDICT: BREACH
