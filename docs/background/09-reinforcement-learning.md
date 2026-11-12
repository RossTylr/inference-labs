# 09 — Reinforcement learning

**The lesson in one line:** learning a sequence of treatments from past records is possible in principle, and the hard part is not the learning but knowing whether the learned policy is any good without trying it on patients.

---

## Anchors

| Id | Finding | Numbers | Limits |
|---|---|---|---|
| E-120 | The paper that started the debate | Trained on 17,083 admissions, tested on 79,073 from 128 hospitals; 750 states, 25 actions. Estimated value 84.5 for the learned policy against 56.9 for clinicians. It recommended less fluid and more vasopressor. Mortality was lowest where the dose given matched the recommendation | Evaluated from records by weighted importance sampling; the authors call for prospective trials |
| E-50 | The critique | Evaluation by importance sampling gives almost no weight to patients whose care departed from the learned policy, so a policy of withholding treatment can score well. A zero-drug policy outscored the clinicians in most of the critics' reproductions | One side of an exchange |
| E-119 | Guidance from the original authors and others | Three questions: did the algorithm see every variable the clinicians used; how large is the effective sample; will it behave as intended in prospective use | A comment, not a study |
| E-97 | The trial of the same choice (CLOVERS) | Vasopressors first against fluids first, 1,563 patients: death by 90 days 14.0% against 14.9%, difference -0.9 points (-4.4 to 2.6). The groups differed by about 2 litres of fluid | US centres; after initial fluid |
| E-94 | Timing of the same treatments | Each hour to antibiotics raised the odds of death by 4%. Each hour to the fluid bolus: 1.01 (0.99-1.02), no association | Observational |
| E-96 | A deployed sepsis model, checked | AUC 0.63; missed 67% of cases; alerted on 18% of admissions | A prediction model, not a policy |
| E-49 | ICU-Sepsis environment | 716 states, 25 actions; random policy 0.78 survival, estimated clinician policy 0.78, optimal 0.88 | A teaching benchmark; not for practice |
| E-45 to E-47 | Sepsis-3 | Definitions the environment's states rest on | — |
| E-56 | Dopamine and prediction error | Firing tracks the gap between expected and received reward | Abstract only |

---

## Thinking

**The claim and the trial point in different directions.** The learned policy (E-120) recommended less fluid and more vasopressor than clinicians gave, and its estimated value was 84.5 against 56.9 for the clinicians. CLOVERS (E-97) then randomised 1,563 patients between the two broad strategies that such a policy chooses between, with a two-litre difference in fluid, and found mortality of 14.0% and 14.9%. E-94 found no association between fluid timing and death. If the largest available lever makes less than a point of difference in a trial, a claim that a policy pulling the same lever more cleverly saves many lives needs strong evidence. That is not a proof the policy is wrong. It is the prior the notebook should start from.

**The score can be gamed without anyone cheating.** Records only contain what clinicians actually did. To score a new policy, the usual method re-weights the patients whose care happened to match it. If the new policy differs from practice in the sickest patients, those patients drop out of the score, and what remains are the patients who were doing well anyway. A policy of giving nothing matched only the patients who needed nothing, and scored above the clinicians (E-50). The original authors' own later guidance names the same hazard as its second question: how large is the effective sample once only the patients treated as the new policy would treat them are counted (E-119). The notebook should reproduce this on the benchmark: write the do-nothing policy, evaluate it the naive way, and watch it win.

**In the simulator you can check; in the ward you cannot.** ICU-Sepsis (E-49) lets a policy be run forward thousands of times, so its true value is known: 0.78 at random, 0.78 for the estimated clinician policy, 0.88 at best. That the clinicians' estimated policy does no better than chance in this model is itself a caution about the model, not a finding about clinicians. That is what makes it a teaching tool and what makes it unlike the real problem. The useful exercise is to hide the simulator, estimate a policy's value from logged episodes only, and then reveal the truth. The gap between the two is the lesson.

**A deployed model is a warning about the whole class.** E-96 is not reinforcement learning, but it is the nearest thing to a field test of machine-driven sepsis care: a widely deployed proprietary model, with an AUC of 0.63 when an outside team measured it. Performance claimed from the developer's own data did not survive contact.

**The casualty version.** Prolonged care of a casualty who cannot be evacuated is a sequence of decisions under uncertainty: fluid, blood, drugs, when to re-examine. No open data exist for it, so the notebook uses sepsis as a stand-in and says so. The graph from lens 08 supplies what the stand-in lacks: which actions are possible at the echelon.

---

## Use in the notebook

| Part | Material |
|---|---|
| Hook | A learned policy claimed to beat intensive care doctors at sepsis. On the same test, a policy of giving no treatment at all also beat them. What went wrong? |
| By hand | A four-state, two-action world on paper: work out the value of each state by hand |
| Diagnosis case | Weak fit: which observation to take next |
| Treatment case | Sequential resuscitation on ICU-Sepsis: learn a policy, evaluate it from logs, then reveal its true value |
| Failure | The do-nothing policy winning under naive off-policy evaluation |
| Central figure | The board: states shaded by value with the learned route across them |

## What must not be claimed

- That the original paper showed patients do better under the policy. Its evidence is an estimate from records, and its authors state that it needs prospective evaluation.
- That CLOVERS refutes the learned policy. It tested two fixed strategies, not an adaptive one.
- That results on a 716-state benchmark say anything about a patient.

## Open items

- None. E-119 and E-120 have now been read in full.
