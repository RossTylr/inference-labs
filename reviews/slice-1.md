# Review of slice 1: lens 03, Bayesian

**Date:** 12 November 2026 · **Author:** Ross Taylor

Reviewed against PRD section 5 and `docs/background/03-bayesian.md`. Read: `notebooks/03_bayesian.ipynb`, `src/inference_labs/lenses/bayesian.py` and `app/streamlit_app.py`. The notebook was run top to bottom from a fresh kernel; it finished in about two seconds and every text output matched the committed one. Cells are numbered from 0 in file order. Line numbers are those of the file named.

## What must not be claimed

- That a 93% posterior probability is proof: HOLDS (cells 21, 27). Cell 21 gives the PROPPR figure (E-73) and says in the same paragraph that it is not proof, that it is conditional on the model and the prior, and that the abstract does not state the prior. Cell 27 sets the RePHILL figure beside it and says the Bayesian answer rests on a prior that has to be defended. No posterior in the notebook or the app is presented as settling a question.
- That the notebook's CRASH-3 analysis is a published result: HOLDS (cells 21, 42). Cell 21 states in bold that it is a teaching reanalysis, not a published result, and that it carries the mechanism label; it cites E-33 for the absence of a published reanalysis. The only CRASH-3 figure on the scorecard (cell 42, row 8) is computed on the synthetic fixture and labelled mechanism. The app shows no CRASH-3 result.

## Epistemic checks

- Accuracy quoted for the wrong cohort or setting: HOLDS (cells 4, 5, 13, 14, 16, 17, 32 to 34; bayesian.py lines 72 to 81). Scan accuracy is used only in its own setting: E-16 before hospital, E-14 in hospital. The in-hospital Beta shapes are stated as an assumption (cell 13). The one cross-setting use is the failure case, where it is the point and is named as such. E-31 supplies only the 90 mm Hg threshold; its 75% and 86% are not quoted, and the accuracy of the triage reading is counted on the generator and labelled mechanism. E-64 and E-114 are given with their populations.
- Proxy data read as the real thing: HOLDS (cells 16, 20, 27, 28, 41 to 43; app line 57). The CRASH-3 fixture is called synthetic, random and clinically meaningless where it is used, and its scorecard row carries the mechanism label and the data source `fixture:crash3.csv`. Every result on the generator is called a mechanism. Row 8's value of 0.998 comes almost wholly from the CRASH-2 prior, since the fixture's own interval runs from 0.41 to 1.54 (cell 28); it says nothing about tranexamic acid.
- Civilian data read as military: HOLDS (cell 5; app line 59). Both scan studies are called civilian, with the statement that no military figure was found and that using them for a military casualty is an assumption. PROPPR, STAAMP, CRASH-2, CRASH-3 and RePHILL are nowhere described as military. The tranexamic acid effect by delay (E-22) is a CRASH-2 result, from 274 hospitals in 40 countries (E-19), and is applied to a casualty at cell 30 and on the app (bayesian.py lines 476 to 477) without its population being named. Both places call it a modelling step or a mechanism, so it is not read as military evidence; it may be claimed only as that.
- A diagnosis result read as a treatment result: HOLDS (cells 29 to 31, 42; bayesian.py lines 383 to 385, 464). Cell 31 says the belief-weighted reduction is a diagnosis result put to use, not a treatment result. The lens's `treat` returns the belief unchanged, and the scorecard keeps the diagnosis rows apart from the one treatment row. The app's "Belief-weighted reduction in bleeding death" is a relative reduction multiplied by a belief; it is not a change in that casualty's risk of death and may not be read as one.

## Numbers and their evidence ids

- Scan accuracy: HOLDS (cells 3, 5, 6, 8, 9). 21 of 84, 257 of 266, 25% and 96%, the third of abdominal scans indeterminate, the physician-staffed service and the blunt trauma are all in E-16 and its brief; 74% and 98% are in E-14.
- Counts and grids: HOLDS (cell 4). 108 patients and 32% to 55% are in E-64; the frequency finding is E-114.
- PROPPR and its reanalysis: HOLDS (cell 21). P=.12 is E-72; 93% is E-73.
- CRASH-2: HOLDS (cells 21, 24). 0.91 (0.85 to 0.97) and the prespecified heterogeneity threshold are in E-20; reading that rule as a prior is the background file's.
- STAAMP, the brain injury trial and the missing reanalysis: HOLDS (cell 21). E-74 is used without a number; 0.1 and 0.025 are in E-79; E-33 supplies no number.
- CRASH-3 population: BREACH (cells 22, 24). The table labels the 0.94 (0.86 to 1.02) result "all patients (E-27)", and cell 24 says a reduction of a fifth or more stays near zero "in the whole trial". E-27 does not say that: it gives 12,737 randomised and 9,202 treated within 3 hours, then the result, and does not attribute the result to all randomised patients. The numbers are right; the population named for them is not supported by the register.
- CRASH-3 subgroup: HOLDS (cells 21, 22). 0.78 (0.64 to 0.95) is in E-28.
- RePHILL: HOLDS (cells 25 to 27). Every figure is in E-77, and the probabilities are marked as calculated here, not reported by the trial, as the background file requires.
- Tranexamic acid by delay: HOLDS (cell 29; bayesian.py lines 84 to 88). All three bands match E-22; the log-normal shape is stated as an assumption.
- Triage threshold: HOLDS (cell 16; bayesian.py line 63). 90 mm Hg is in E-31.
- Predictive coding: HOLDS (cell 44). E-55.
- Generator figures: HOLDS (cells 17, 19, 33, 36, 42). Each is counted on the generator and labelled as such.

## Figures

Each figure was checked against its `concludes:` tag and the output it is drawn from.

- Cell 3, central figure: HOLDS. Counting 15 of 92 casualties still bleeding after a clear scan changes the answer a reader gives to the hook.
- Cell 7: HOLDS. The same hundred in two settings shows that the setting decides what a clear result is worth.
- Cell 10: HOLDS. Ten draws show the belief as a spread, one of the ten below one half.
- Cell 15: HOLDS. A positive scan in hospital is decisive; before hospital it is not, and a clear scan barely moves the belief.
- Cell 18: HOLDS. The same synthetic casualty appears in both settings (systolic 108 mm Hg, scan clear in both, bleeding), so the two lines are comparable and the title is true.
- Cell 20: HOLDS. The calibration plot is titled mechanism, not evidence, and the text says its agreement confirms the arithmetic only.
- Cell 23: HOLDS. The prior moves the probability of any benefit; no prior puts weight on a reduction of a fifth or more.
- Cell 34: HOLDS. The pre-hospital curve meets the count because the generator uses the same accuracy; the figure's point is the gap to the borrowed curve, and that stands.
- Cell 37: HOLDS. A repeated scan overstates the belief by a large margin, two signs of one derangement by a small one, and independent findings agree with the count.
- Cell 39: BREACH. The title says the shuffled program "reports scans that catch 113% of bleeds". The plotted quantity is sensitivity plus miss rate, and shuffling leaves the sensitivity draws unchanged; what reaches 113% is the share of bleeds counted as either found or missed. The figure's conclusion stands; its title misstates what was computed.
- App page 1, belief band: HOLDS (app lines 34 to 51). The band and table come from the library, the dotted line is the evacuation threshold, and the caption says treatment and evacuation leave the belief unchanged.

VERDICT: BREACH
