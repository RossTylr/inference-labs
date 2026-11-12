# 10 — Decision theory

**The lesson in one line:** a probability is not a decision; to act you must also say what each kind of mistake costs, and that part is a judgement that someone owns.

---

## Anchors

| Id | Finding | Numbers | Limits |
|---|---|---|---|
| E-87 | A value judgement written as a benchmark | Under-triage below 5%, over-triage below 50% | For severe injury in civilian systems |
| E-88 | What crews do with it | Protocol alone: 63.8% missed, 7.4% over-called. In practice: 21.6% and 30.6% | One region |
| E-07, E-09 | The same trade in a military rule | MPTT against the Military Sieve: under-triage 19.6 points lower, over-triage 11.6 points higher | One prospective cohort of 357 |
| E-93 | Net benefit | A model is scored by its consequences across a range of thresholds; the threshold states how a false alarm is weighed against a miss | Method |
| E-52 | The threshold approach | Probability of disease decides between withholding, testing and treating | Abstract summary only |
| E-96 | A model judged by consequences | Alerts on 18% of admissions; 67% of sepsis cases missed | One health system |
| E-78 | Which outcome is the utility | Tranexamic acid before hospital: deaths at 28 days 17.3% against 21.8%; survival with good function 53.7% against 53.5% | Secondary against primary outcome |
| E-38, E-41 | Common against lethal | Extremities about 44% of injuries, torso about 7%; truncal bleeding two thirds of survivable haemorrhage deaths | Different cohorts |
| E-86 | A deliberately accepted risk | Systolic pressure held at about 100 before surgical control; above 110 if the brain is injured | Doctrine |
| E-48 | A utility written down | The sepsis challenge scored early alerts up and late or false ones down. The winning entry scored 0.360 overall and -0.123 on the hospital system it had not seen | A competition, not a deployment |
| E-101 | Two operating points from one model | 90.3% and 98.1%, or 97.5% and 93.4% | Retinal screening |

---

## Thinking

**The benchmark is a statement of values.** "Miss fewer than 5%, and accept up to 50% over-calls to do it" (E-87) is not a fact about injuries. It says that sending many uninjured people to a trauma centre is an acceptable price for missing few of the injured. Every threshold in this repository hides a sentence like that. The notebook's job is to make the reader write the sentence before choosing the number.

**The crews had already decided.** The protocol as written missed 64% and over-called 7%. The people using it missed 22% and over-called 31% (E-88). They moved the line because they weighed a miss more heavily than the protocol's authors had. Decision theory describes what they did; it did not need to tell them.

**Accuracy is the wrong score.** A sepsis model that alerts on nearly one admission in five and still misses two thirds of cases (E-96) has an AUC that sounds moderate and a consequence that is poor: staff interrupted constantly for little gain. Net benefit (E-93) is the tool for seeing that. It asks, at the threshold where you would actually act, whether using the model beats treating everyone or no one.

**The outcome you choose is the utility you hold.** In PATCH the treated group had fewer deaths at 28 days, and the share alive with good function at six months was the same in both groups (E-78). One reading is that the drug works. Another is that it did not deliver what the trial set out to find. Which reading is right depends on what you were trying to achieve, and the trial cannot tell you that. This is the cleanest real example of a decision that the data inform and do not make.

**Rare and deadly beats common and survivable.** A classifier that sorts limb injuries well will score well overall, because limbs are nearly half of injuries (E-38). The casualties it must not miss are the few with torso bleeding (E-41). An unweighted score rewards the wrong skill. Weight the errors by what they cost and the best threshold moves.

**Doctrine accepts risk on purpose.** Holding blood pressure at about 100 in a bleeding casualty, and higher if the brain is injured (E-86), is a trade between two harms written as a target. It is decision theory already done and compiled into a rule, in the same way lens 01 found evidence compiled into rules.

**Scarcity changes the problem.** With one helicopter and two casualties, the question is no longer whether each is above a threshold but which gains more. That needs the belief from lens 03, the decay from lens 05 and the reachable options from lens 08 together. It is where the lenses meet, and it belongs on the walk-through page.

---

## Added from the full text

Findings taken from the papers themselves on 12 November 2026. Each is in the evidence register under the id shown.

| Id | Finding | How the notebook can use it |
|---|---|---|
| E-79 | Significance thresholds of 0.1 for benefit and 0.025 for harm | A stated exchange rate between two errors, written into a trial protocol. The cleanest real example of a utility hiding in a statistical threshold |
| E-48 | The challenge's authors say the utility values can be chosen to reflect a hospital's preferences; the best entries by utility were not the best by area under the curve | The diagnosis case can rank three models by accuracy and again by utility and show the order change |
| E-77 | A composite outcome of death or failure to clear lactate: 64% against 65% overall, with death 43% against 45% | A composite weighs a death and a laboratory value equally. Ask the reader what weights they would choose, then recompute |
| E-20 | Vascular occlusive events 1.7% against 2.0%; deaths 14.5% against 16.0% | Both sides of the ledger for the treatment decision, from one trial |

---

## Use in the notebook

| Part | Material |
|---|---|
| Hook | An alarm fires on 18% of all admissions and still misses two thirds of sepsis cases. Would you switch it on? |
| By hand | Ten casualties, a cost for each kind of error, total cost at three thresholds |
| Diagnosis case | Where to set the triage threshold: MPTT-24 and Military Sieve as two points; the benchmark as a third; the reader's own weights as a fourth |
| Treatment case | Treat here or evacuate, with benefit decaying; then two casualties and one aircraft |
| Failure | Optimising overall accuracy and losing the torso bleeds |
| Central figure | The scales |

## What must not be claimed

- That the civilian benchmark applies to military triage. The target condition differs.
- That PATCH shows extra survivors were left with poor function. The abstract supports only that good-function survival did not rise.
- A specific exchange rate between a miss and a false alarm. None of the sources states one.

## Open items

- The threshold formulae in E-52 were not read at source.
