# 00 — The casualty thread and the framing

**Feeds:** notebook 00, the generator, and every lens that needs a patient mix or a timeline.
**The lesson in one line:** the military record contains all three kinds of question a method can answer (what happened, who is at risk, what would change it), and each lens is good at one of them.

Evidence ids refer to [`../EVIDENCE.md`](../EVIDENCE.md). Status words (READ, SECONDARY, NOT READ) are defined there.

---

## Anchors

| Id | Finding | Numbers | Limits |
|---|---|---|---|
| E-34 to E-36 | Who arrives at a UK field hospital | 7,601 admissions, Afghanistan 2006-2014: disease about 44%, battle injury about 30%, non-battle injury about 27% | One theatre; shares derived from rows that do not sum exactly |
| E-84 | UK combat casualties, 2003-2012 | 2,792 casualties, 608 deaths (22%). About 70% of hostile-action casualties from explosive munitions. Extremities 43% of injuries. The injury score at which half survive rose from 32 to 60 | Registry of combat casualties, not all admissions |
| E-39 to E-41 | Where and why battlefield deaths occur | 87.3% of deaths before any treatment facility; of the potentially survivable, 90.9% from haemorrhage: truncal 67.3%, junctional 19.2%, extremity 13.5% | US deaths, 2001-2011 |
| E-105 | Chest injury as a cause of death | Tension pneumothorax estimated to contribute to about 3 to 4% of fatal combat casualties | Vietnam-era data; denominator unclear |
| E-82 | What reduced combat mortality | Case fatality fell from 20.0% to 8.6% (Afghanistan). Of deaths averted, 44.2% attributed to three things: tourniquets 12.9%, blood transfusion 23.8%, faster transport 7.5% | US data; the attribution comes from a simulation |
| E-42, E-43 | The planning timelines and roles of care | 10 minutes, 1 hour, 2 hours; Role 1 to Role 4 | Doctrine, not measurement |
| E-115, E-116 | Two cultures; explain or predict | Assume a model of how data arose, or judge by prediction; the goal changes every modelling choice | Arguments, not findings |

---

## Thinking

**Three questions, one record.** E-34 and E-84 describe: they say who was hurt and how. E-39 to E-41 begin to predict: they say which casualties die and when. E-82 asks the counterfactual: how many would have died without tourniquets, blood and faster helicopters. These are the three tasks usually separated as description, prediction and counterfactual prediction (E-117, not read at source). Notebook 00 should sort the ten lenses under them before any method is taught, because most misuse of a method is asking it the wrong kind of question.

**The same three interventions recur.** Tourniquets, blood and time are the three items in E-82. They come back as a rule (lens 01), a decaying benefit (lens 05) and a causal claim under test (lens 07). The thread is therefore not only one casualty moving through echelons; it is one set of interventions examined ten ways.

**Common is not lethal.** Extremities are 43 to 44% of injuries (E-84, E-38), but truncal bleeding is two thirds of survivable haemorrhage deaths (E-41). Any method scored on overall accuracy will do well by getting limbs right. Lens 10 is built on that gap, and the generator must reproduce it.

**Two cultures, both needed.** Breiman's division (E-115) maps onto the table directly: frequentist, Bayesian, stochastic and causal lenses assume a model of how the data arose; trees, networks and reinforcement learning do not. The repository's position is the one Shmueli argues (E-116): neither is better, the goal decides.

---

## Added from the full text

Findings taken from the papers themselves on 12 November 2026. Each is in the evidence register under the id shown.

| Id | Finding | How the notebook can use it |
|---|---|---|
| E-117 | The three tasks, with the source's own example from health records: how can women with a history of stroke be grouped; what is the probability of a stroke next year; will starting a statin reduce the risk | The thread's three questions are now cited at source. Restate the example for the casualty: who is injured and how; who will die of bleeding; does tranexamic acid reduce those deaths |
| E-81 | The golden hour authors say that, with several things changing at once and only 37.3% of casualties having matched records, only a descriptive reading was viable | An honest statement of which of the three questions a famous military result can answer |

---

## Use in the notebook

| Part | Material |
|---|---|
| Hook | Over the Afghanistan campaign the case-fatality rate for US battle casualties fell from 20% to under 9%. Guess how much of the fall is accounted for by tourniquets, blood and faster evacuation together. (44%.) |
| By hand | A hundred admissions sorted by stream using E-34 to E-36, then the battle-injured sorted by mechanism using E-35 |
| Central figure | The casualty's route from point of injury to Role 2, with the three timelines marked and the three interventions placed on it |

## What must not be claimed

- That the 44% attribution is measured. It is modelled, and 56% is unexplained.
- That US outcome figures describe UK casualties, or that Afghanistan's mix describes a future operation.

## Open items

- A UK source for where deaths occur, to sit beside E-39. None was found open.
