# 01 — Rules

**The lesson in one line:** a rule is a decision made in advance; what matters is where it came from, who it was written for, and what it throws away.

---

## Anchors

| Id | Finding | Numbers | Limits |
|---|---|---|---|
| E-08, E-09 | MPTT-24, a triage rule fitted to military data | Military registry: sensitivity 66.7%, specificity 69.9%. Civilian registry: 53.5% and 74.8% | First hospital observations, not pre-hospital (E-11) |
| E-10 | The rule it replaced | Military Sieve: 43.2% and 93.7% on the same military cohort | — |
| E-31 | ABC score for massive transfusion | Four yes-or-no items; two or more: 75% sensitive, 86% specific | Original single-centre figures |
| E-90 | The ABC score tested later | Sensitivity 0.36, specificity 0.80 in a cohort of 2,438 | Different population and definition |
| E-86 | US military resuscitation doctrine | Three of four of: systolic pressure under 100, heart rate over 100, haematocrit under 32%, pH under 7.25 predicts about 70% risk of massive transfusion; all four about 85%. Tranexamic acid only within 3 hours of injury | A guideline; two of the four items need a laboratory |
| E-104 | A rule written for a different body | Needle of about 5 cm recommended; mean chest wall 5.36 cm in 100 military cases; an 8 cm catheter reaches in 99% | Autopsy imaging, male only |
| E-106 | The same rule in the field | 111 needle decompressions; a third went on to a chest tube in the field; authors report a high failure rate | Registry, no comparison group |
| E-89 | A rule written by data (PECARN) | 42,412 children; validation sensitivity 96.8% and negative predictive value 99.95% for those aged 2 and over | Children, civilian |

---

## Thinking

**Rules are compressed evidence.** The three-hour limit on tranexamic acid in E-86 is not an opinion. It is the time-to-treatment result of a trial (E-22) written as an instruction. Seen that way, a rule is the last step of an inference someone else did, and it inherits that inference's weaknesses. The trial analysis was exploratory (E-23); the rule is not marked as such.

**Who was it written for?** The MPTT-24 loses thirteen points of sensitivity moving from soldiers to civilians (E-09). The needle rule fails in the other direction: written from civilian anatomy, it meets a military chest wall thicker than the needle is long (E-104), and the field record agrees (E-106). Both are the same failure. A rule carries its population with it and does not announce when it has left.

**What does it throw away?** The ABC score counts a positive scan as one point whatever the scan showed and wherever it was done. A scan that moves belief to 65% and one that moves it to 90% score the same. That loss is the price of being usable in thirty seconds, and it is the comparison lens 03 exists to make.

**A rule can decay.** The ABC score's published sensitivity of 75% (E-31) became 36% in a later cohort (E-90). Nothing in the rule changed. Rules need revalidation as much as models do; they are simply less often given it.

---

## Added from the full text

Findings taken from the papers themselves on 12 November 2026. Each is in the evidence register under the id shown.

| Id | Finding | How the notebook can use it |
|---|---|---|
| E-54 | In the dual process model, repeated analytical working of the same presentation turns into recognition, and either mode can override the other | A rule is deliberation done once and stored. It also explains why crews override a protocol (E-88): the override is part of the model, not a breach of it |
| E-59 | The choice of exits in a fast-and-frugal tree corresponds directly to where the decision criterion is set | Read the MPTT-24 this way: every early exit is to Priority One, which is a liberal criterion written as a flowchart |
| E-30 | Risk of death from bleeding is U-shaped in heart rate and respiratory rate | Why a triage rule needs a band with two ends, not a single cut-off |
| E-118 | A three-rule list on age, sex and prior offences set against a proprietary tool with over 130 inputs | A rule list is a model that can be learned from data and checked by eye. Sets up lens 04 |
| E-20 | Entry to CRASH-2 was by the clinician's judgement that the patient was bleeding or at risk, not by a test | The rule 'give tranexamic acid to the bleeding casualty' inherits a judgement call at its first step |
| E-08 | The MPTT-24 flowchart, read from the paper: haemorrhage, walking, breathing, voice, respiratory rate 12 to 23, heart rate below 100 | The rule to code, step for step. Five of its six exits can end in Priority 1 or Dead before the last question is reached |
| E-08 | The text says 'responds to voice' replaces 'GCS below 14'; the figure, read literally, lets a casualty who responds only to voice pass to the next step | A rule's prose and its diagram disagree for one group of patients. Code both readings, count how many casualties change priority, and let the reader see what a one-word ambiguity costs |
| E-09 | The rule was tested on hospital respiratory rate and registry GCS, in a cohort where 47.6% were Priority 1; positive predictive value 67.0% there and 34.0% in a civilian cohort where 19.5% were | The same rule, two prevalences, two predictive values. Hands the base-rate point to lens 03 |

---

## Use in the notebook

| Part | Material |
|---|---|
| Hook | Guidance recommended a 5 cm needle to decompress a chest. In 100 soldiers the average chest wall was 5.36 cm thick. What happened in the field? |
| By hand | Ten synthetic casualties run through the MPTT-24 on paper |
| Diagnosis case | MPTT-24 priority, with the Military Sieve beside it (E-09, E-10): the newer rule finds more of those who need intervention and wrongly flags more of those who do not |
| Treatment case | Transfusion activation by the ABC score and by the four-item doctrine rule (E-31, E-86); tranexamic acid inside or outside three hours |
| Failure | The same rule on a civilian cohort (E-09); the ABC score's fall (E-90) |
| Central figure | The sieve: casualties dropping through gates into three bins |

## What must not be claimed

- That a rule's published accuracy is a property of the rule. It is a property of the rule in one population.
- That the MPTT-24 has been validated on pre-hospital observations.

## Open items

- O-1: confirm the MPTT-24 steps from the paper's flowchart before coding.
- E-118 (the argument for interpretable models) is cited by title only.
