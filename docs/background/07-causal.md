# 07 — Causal inference

**The lesson in one line:** seeing that treated casualties did better is not knowing that treatment made them better; military medicine can rarely randomise, so it has to learn exactly where observation goes wrong.

---

## Anchors

### The ladder, on one drug

| Id | Study | Design | Result |
|---|---|---|---|
| E-71 | MATTERs | Observational, military hospital, 896 casualties | Mortality 17.4% with tranexamic acid, 23.9% without, though the treated were more badly injured. In those massively transfused: 14.4% against 28.1% |
| E-19 to E-21 | CRASH-2 | Randomised, 20,211 patients | Death from bleeding 4.9% against 5.7%, RR 0.85 (0.76-0.96) |
| E-78 | PATCH-Trauma | Randomised, prehospital, advanced trauma systems | Death by 28 days RR 0.79 (0.63-0.99); survival with good function unchanged |
| E-74 | STAAMP | Randomised, prehospital | Hazard ratio 0.81 (0.59-1.11) |
| E-79 | Brain injury, prehospital | Randomised | 65% against 62% good outcome; no benefit shown |
| E-86 | Doctrine | — | Give within 3 hours; a later military analysis found more venous clots |

### How observation misleads, with numbers

| Id | Finding | Numbers |
|---|---|---|
| E-80 | Survival bias | High plasma ratio: relative risk of death 0.37 when the ratio is measured at 24 hours; 0.84 (0.47-1.50) when measured as it changes. 54% of deaths occurred in the first 6 hours |
| E-72 | The trial of the same question (PROPPR) | 12.7% against 17.0%, P=.12 |
| E-83 | Prehospital blood, observational | 5% against 19% dead at 24 hours; adjusted hazard ratio 0.26 (0.08-0.84); 55 treated |
| E-75, E-76, E-77 | Prehospital plasma and blood, randomised | Benefit in one trial, none in two |
| E-81 | A policy change | Killed in action 16% to 9.9% after the sixty-minute mandate. In the same paper, among the critically injured, 6.8% of those who received a blood transfusion were killed in action against 51.0% of those who did not. Most transfusions are given after reaching a facility, and the killed in action by definition never reach one, so the contrast invites the survival-bias question |
| E-82 | Attribution by simulation | 44.2% of averted deaths assigned to tourniquets, blood and transport |
| E-32 | Tourniquets | 90% survival if applied before shock, 10% after |
| E-60 | Confounding by treatment | Asthma appeared to protect against pneumonia death because asthmatic patients went straight to intensive care |

---

## Thinking

**The observational effect is several times the randomised one.** In the military hospital, the massively transfused who received tranexamic acid died at half the rate of those who did not (E-71). In the randomised trial the drug cut bleeding deaths by about 15% (E-21). Both can be honest reports. The gap between them is what the lens is about.

**To be treated you must first survive.** E-80 shows the mechanism with a single contrast. Patients who die in the first hours have received little plasma, because plasma takes time to thaw and arrive. Measure the ratio at 24 hours and the dead are concentrated in the low-ratio group by construction: 0.37. Let the ratio vary with time, so each death is compared with what the survivors had received by that same hour, and it becomes 0.84 with an interval that crosses 1. The same reasoning applies to MATTERs: a casualty has to live long enough to be given the drug. The notebook should reproduce this on synthetic data where the drug has no effect at all, and recover a protective association anyway.

**Then someone randomised it.** PROPPR (E-72) put the plasma question to a trial. The answer was smaller and less certain than the observational studies suggested. This sequence, a strong observational signal, a demonstration of bias, then a trial, is the complete story in three papers on one question.

**When you cannot randomise.** Nobody will randomise casualties to slower helicopters. E-81 is what is available instead: a policy changed on a known date, and outcomes before and after can be compared. The weakness is that other things changed in the same years, blood on the aircraft among them (E-83). E-82 tries to separate the contributions by simulation and assigns blood three times the share of transport. These are the designs military medicine actually has, and the notebook should name each one's assumption instead of dismissing them.

**Does a trial transport?** PATCH (E-78) was run in mature civilian trauma systems and STAAMP (E-74) in another. Whether their answers hold at a forward aid post, with different delays and different injuries, is not a statistical question. It needs the causal diagram: which of the things that differ between settings lie on the path from drug to outcome?

**Indication runs both ways.** In E-71 the treated were sicker and did better. In E-60 the sicker-looking were treated harder and so did better. In E-32 those tourniqueted late were already in shock. In each case the decision to treat carries information about the patient, and that information travels to the outcome by a path that does not pass through the treatment.

---

## Use in the notebook

| Part | Material |
|---|---|
| Hook | In a military hospital, casualties given tranexamic acid were more badly hurt and still died less often: 17.4% against 23.9%. Proof that it works? |
| By hand | Twelve casualties, a coin for treatment, then the same twelve with treatment decided by who survives the first hour |
| Diagnosis case | Weak fit: who gets scanned, and how that biases measured accuracy |
| Treatment case | Effect of tranexamic acid from CRASH-2; then a generator-built observational version of the same patients, analysed naively and with time handled properly, set beside E-71 and E-80 |
| Failure | Survival bias producing a benefit from a drug with none |
| Central figure | Cutting the arrow |

## What must not be claimed

- That MATTERs is wrong. Its direction agrees with the trials; its size is what is in doubt.
- That the sixty-minute mandate caused the fall in deaths, or that the 44.2% is measured.
- That the plasma trials disagree because of transport time. Not read here.

## Open items

- O-2 for CRASH-2 data. O-9 for the sources read through summaries.
- None for E-117, now read at source.
