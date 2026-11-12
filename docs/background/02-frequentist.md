# 02 — Frequentist inference and signal detection

**The lesson in one line:** every test and every trial reports error rates under repetition; the errors come in two kinds, the balance between them is a choice, and "not significant" is a statement about the trial, not about the treatment.

---

## Anchors

### Tests: two errors and a movable line

| Id | Finding | Numbers | Limits |
|---|---|---|---|
| E-03 to E-09 | One triage rule, four cohorts | Sensitivity from 53.5% to 83.6%; specificity from 51.0% to 74.8% | Different cohorts, sizes and versions of the tool |
| E-87 | Field triage protocols in general | Across 21 studies sensitivity ran from 10% to 100% and specificity from 9% to 100%. Benchmark: under-triage below 5%, over-triage below 50% | Benchmark is for severe injury (ISS 16 or more), a different target from "needs a life-saving intervention" |
| E-88 | A protocol against the people using it | Protocol alone: under-triage 63.8%, over-triage 7.4%. Crews in practice: 21.6% and 30.6% | One Dutch region |
| E-14, E-16 | One scan, two settings | Free fluid: 74% and 98% in hospital; 25% and 96% before it | In hospital: pooled, heterogeneous. Before hospital: one civilian service, 98% blunt trauma, a third of abdominal scans indeterminate |
| E-101 | One network, two operating points | 90.3% sensitivity with 98.1% specificity, or 97.5% with 93.4% | Retinal images |

### Trials: reading a result

| Id | Trial | Result | What it teaches |
|---|---|---|---|
| E-20 | CRASH-2 | 14.5% against 16.0%, RR 0.91 (0.85-0.97) | A small effect shown clearly by a very large trial |
| E-72 | PROPPR | 12.7% against 17.0% at 24 hours, P=.12; a secondary outcome at P=.03 | A 4-point difference that 680 patients could not confirm; a significant secondary is not a rescue |
| E-76 | COMBAT | 15% against 10%, odds ratio 1.54 (0.60-3.98) | 125 patients: the interval allows a large benefit and a large harm. Median transport 19 and 16 minutes |
| E-75 | PAMPer | 23.2% against 33.0%, P=.03 | The same intervention as COMBAT, opposite direction |
| E-77 | RePHILL | 64.3% against 64.8%; difference near zero, interval -9 to 9 points | A null result that still cannot exclude a 9-point benefit |
| E-78 | PATCH-Trauma | Primary: 53.7% against 53.5%. Death by 28 days: 17.3% against 21.8%, RR 0.79 (0.63-0.99) | The answer depends on which outcome was named in advance |

---

## Thinking

**The crews moved the line.** E-88 is the cleanest signal detection result in the pack. The written protocol missed 64% of the severely injured and almost never over-called. The ambulance crews, using the same protocol, missed 22% and over-called 31%. They did not become better at telling the two groups apart; they shifted the criterion, trading false alarms for hits, because they judged a miss to be the worse error. The benchmark in E-87 says the system agrees with them. This is the hook for lens 10 as well.

**A range, not a number.** Triage protocols span sensitivity from 10% to 100% (E-87). The MPTT's own four cohorts span thirty points (E-03 to E-09). Reporting one figure is the commonest error in the clinical literature on tests, and the notebook should make the reader produce the table before quoting anything.

**Absence of evidence.** PROPPR found 12.7% against 17.0% and reported no significant difference. The confidence interval runs from a 9.6-point benefit to a 1.1-point harm. A reader who concludes "the ratio does not matter" has read a statement about the trial's size as a statement about blood. Lens 03 returns to the same trial and asks the question the clinician wanted answered.

**Six trials, one question each.** Plasma before hospital helped in the air (E-75) and did not on the ground (E-76). Tranexamic acid before hospital reduced deaths and did not increase good recoveries (E-78). None of these contradicts another: each is one draw from a different population under a different protocol. The frequentist frame is honest about that, and its limitation is that it gives no way to combine them. That is the handover to lens 03.

---

## Added from the full text

Findings taken from the papers themselves on 12 November 2026. Each is in the evidence register under the id shown.

| Id | Finding | How the notebook can use it |
|---|---|---|
| E-20 | CRASH-2 by time from injury, all-cause: 0.87 within 1 hour, 0.87 at 1 to 3 hours, 1.00 after 3 hours; heterogeneity p = 0.11 against a prespecified threshold of p < 0.001 | The trial that established the drug did not itself show a timing effect by its own rule. The timing result came from a later exploratory analysis (E-22). A clean lesson in prespecification |
| E-20 | Blood products given to 50.4% against 51.3%, relative risk 0.98 (0.96-1.01) | A drug that cuts bleeding deaths and does not cut transfusion. The authors' explanation, that survivors live long enough to be transfused, hands the question to lens 07 |
| E-77 | RePHILL stopped at 432 of 490. Composite outcome 64% against 65%. Death 43% against 45%. Death within 3 hours 16% against 22%, relative risk 0.75 (0.50-1.13) | A UK prehospital trial for the same exercise as PROPPR: the interval runs from halving early deaths to a 13% increase. 'No difference' and 'not enough patients to tell' are different statements |
| E-79 | The brain injury trial set its significance thresholds at 0.1 for benefit and 0.025 for harm | The 0.05 line is a convention. Here the investigators moved it, and moved it differently in each direction |
| E-76 | COMBAT's median transport was 19 and 16 minutes; median infusion before arrival was small | The trial tested plasma where there was little time to give it. The setting is part of the result |
| E-124 | The timing effect of tranexamic acid survived restriction to blunt trauma, to no head injury and to low blood pressure; the interaction stayed at p < 0.0001 | The follow-up to the subgroup lesson: an exploratory finding that was then tested against rival explanations. What makes a subgroup result more believable is shown, not asserted |

---

## Use in the notebook

| Part | Material |
|---|---|
| Hook | 680 bleeding patients: 12.7% died with one transfusion ratio, 17.0% with the other. The paper reports no significant difference. Does the ratio matter? |
| By hand | A hundred casualties sorted into hits, misses, false alarms and correct rejections for the MPTT-24, then again for the Military Sieve |
| Diagnosis case | Protocol against practice (E-88) as two points on one curve; the scan in two settings |
| Treatment case | Reading CRASH-2 beside PROPPR and RePHILL: same kind of question, very different certainty. Then CRASH-2's own time subgroups against its prespecified rule |
| Failure | One accuracy figure quoted for the wrong setting; a non-significant result read as no effect |
| Central figure | Two hills and a sliding line |

## What must not be claimed

- That transport time is the proven reason COMBAT and PAMPer differ. The COMBAT authors suggest it (median transport was 19 and 16 minutes, and they write that blood products might help where transport is longer), but it is their interpretation, not a tested result.
- That over-triage means 1 minus specificity. The triage literature defines it as 1 minus positive predictive value (E-12).

## Open items

- None. COMBAT and the 2022 RePHILL paper have now been read in full.
