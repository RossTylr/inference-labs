# 05 — Stochastic processes

**The lesson in one line:** one casualty's course cannot be predicted and a thousand casualties' can; the skill is choosing a description of the dice that matches how risk actually changes with time.

---

## Anchors

| Id | Finding | Numbers | Limits |
|---|---|---|---|
| E-85 | When bleeding deaths happen | Median 2.0 to 2.6 hours from admission; about 85% within 6 hours. Hourly death rate about 4.6% at 1 hour, 1% at 6 hours, under 0.1% by 9 hours | Time from hospital admission, civilian centres |
| E-25 | The same, from trial data | 63% of bleeding deaths within 12 hours of onset | Half the patients obstetric |
| E-22 | Tranexamic acid by time to treatment | Relative risk of bleeding death 0.68 within 1 hour, 0.79 at 1 to 3 hours, 1.44 after 3 | Exploratory analysis |
| E-24 | The decay as a rate | Benefit falls about 10% for each 15 minutes of delay; none after about 3 hours | Half obstetric |
| E-81 | Halving the evacuation time | Median transport 90 minutes to 43. Killed in action 16% to 9.9%. Died of wounds 4.1% to 4.3% | Before and after a policy |
| E-83 | Blood within minutes | Transfusion within 15 minutes of rescue, a median 36 minutes after injury: hazard ratio for death at 24 hours 0.17 (0.04-0.73) | 62 patients in the early group; observational |
| E-95 | Delay in septic shock, 1989-2004 | 79.9% survival if treated in the first hour; about 7.6% lower for each further hour | Observational |
| E-94 | Delay in sepsis, 2014-2016 | Odds of death up 4% for each hour to antibiotics | Observational; mandated-care setting |
| E-42 | The planning timelines | 10 minutes, 1 hour, 2 hours | Doctrine |

---

## Thinking

**Risk is front-loaded, so the simplest model is wrong.** A Markov chain with fixed transition probabilities assumes the chance of dying in the next hour is the same at hour one as at hour nine. E-85 measures it: 4.6% in the first hour, under 0.1% by the ninth. That is a fall of about fiftyfold. The notebook should build the fixed-rate chain first, fit it to the median, and show that it gets the tail badly wrong. Then let the rate depend on time since injury and fit it to the three points E-85 supplies. The failure is designed in, and the data to expose it are real.

**The clock is a treatment.** E-22 and E-24 say the benefit of a drug melts at roughly a tenth per quarter-hour. E-83 says the same of blood. E-95 and E-94 say it of antibiotics. Four interventions, one shape. This is why doctrine is written as timelines (E-42): the 10-1-2 is a stochastic model expressed as three deadlines.

**Two cohorts, two rates.** Each hour of delay cost about 12% in the odds of death in the older septic shock cohort (E-95) and about 4% in the modern sepsis cohort (E-94). The patients, the definition and the baseline care all differ. A transition rate is an estimate from a population, not a constant of nature, and a simulation that hard-codes one is making a claim about which population it describes.

**Moving people faster moves where deaths are counted.** After the sixty-minute mandate, deaths before reaching a facility fell from 16% to 9.9% while deaths after arrival stayed at about 4% (E-81). Some casualties who would previously have died in the field now arrived alive. Some of those survived and some died in hospital, and the hospital death rate did not rise. A model with a single "dead" state cannot represent this. Two absorbing states, killed in action and died of wounds, with a transfer between the paths, can. It is a small multi-state model with real numbers to fit.

**The hour is not a cliff.** "Golden hour" suggests a threshold. Every source here shows a slope. The central figure should make that visible.

---

## Added from the full text

Findings taken from the papers themselves on 12 November 2026. Each is in the evidence register under the id shown.

| Id | Finding | How the notebook can use it |
|---|---|---|
| E-77 | Death within 3 hours 16% against 22%; death within 30 days 42% against 45% | A six-point gap early and a three-point gap late. If benefit acts on early bleeding deaths, an outcome counted at 30 days dilutes it. Matches the front-loaded hazard in E-85 |
| E-20 | All-cause effect 0.87 in the first hour and at 1 to 3 hours, 1.00 after 3 hours; the authors note digit preference in reported times | Time since injury is rounded by the people who record it. The notebook can round the generator's times to the nearest half hour and show what that does to a fitted decline |
| E-81 | Only 37.3% of casualties had matched flight and facility records | Transport time, the central variable of this lens, was missing for most of the cohort it is famous for |

---

## Use in the notebook

| Part | Material |
|---|---|
| Hook | Among patients who bleed to death after reaching a trauma centre, how long does the middle one live? (About two hours.) |
| By hand | Ten casualties stepped through a three-state chain with a coin and a die |
| Diagnosis case | Deterioration from point of injury to Role 2: fixed-rate chain, then time-varying, each checked against E-85 |
| Treatment case | Benefit of tranexamic acid as a function of delay, using E-22 and E-24 with their uncertainty carried as draws |
| Failure | A constant hazard fitted to a front-loaded process |
| Central figure | Many lives: a hundred simulated trajectories from one starting point |

## What must not be claimed

- That E-85's timings apply from the moment of wounding. They start at hospital admission.
- That the mandate caused the fall in E-81. Blood on helicopters and other changes arrived in the same period; lens 07 takes this up.
- That the 10% per 15 minutes figure is a trauma-only estimate (E-26).

## Open items

- O-9: read the full golden hour paper; the figures here are from a summary.
- A source for time to death from the point of wounding, as opposed to admission, was not found.
