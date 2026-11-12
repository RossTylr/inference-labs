# Evidence register — inference-labs

Clinical verification and background check carried out on 9 November 2026, before the PRD. Every clinical number the design relies on is listed here with its source and the way it was checked. The design document (`DESIGN.md`) cites these entries by id.

## How to read the status column

| Status | Meaning |
|---|---|
| **READ** | The abstract or full text was fetched and read at the source or an institutional repository during this check. |
| **CARRIED** | The figure was read from a search extract of the source earlier in the design conversation and has not been re-read since. Treat as provisional. |
| **SECONDARY** | Read from a secondary summary of the paper, not the paper itself. |
| **NOT READ** | The source could not be reached. The claim rests on general knowledge and must be confirmed before use. |
| **CORRECTED** | The check changed something the design had assumed. |

PubMed and PubMed Central returned a browser check for every request after the first, so several papers were read from university repositories and publisher pages instead. No PDF was downloaded: the build environment could not reach the hosting sites. Each brief in Part B gives the open-access link and licence so the files can be pulled locally. Where a page did not show volume and page numbers, they were completed from general knowledge; those are listed for checking in O-7.

---

## Part A — Verification register

### A1. Triage (MPTT and MPTT-24)

| Id | Claim | Verified value | Source | Status |
|---|---|---|---|---|
| E-01 | Derivation cohort | UK Joint Theatre Trauma Registry, adults at a deployed facility 2006–2013; 6,095 patients, 3,654 (60.0%) with complete data; 1,738 (47.6%) Priority One | `vassallo2017a` | READ |
| E-02 | How it was derived | Binary logistic regression on first recorded heart rate, respiratory rate and Glasgow Coma Scale | `vassallo2017a` | READ |
| E-03 | MPTT in the derivation cohort | Sensitivity 69.9% (67.7–72.0), specificity 65.3% (63.2–67.5) | `vassallo2017a` | READ |
| E-04 | MPTT steps and thresholds | Not walking, then Priority One on any of: the breathing check (criterion not stated in the text read), respiratory rate below 12 or at or above 22, heart rate at or above 100, or GCS below 14 | `vassallo2017b` | READ (text and table; step order of the last two differs between sources) |
| E-05 | MPTT, civilian validation | TARN, 218,985 adults, 127,233 (58.1%) analysed, 24,791 (19.5%) Priority One. Sensitivity 57.6% (56.9–58.2), specificity 71.5% (71.2–71.8), AUROC 0.645 | `vassallo2017b` | READ |
| E-06 | Comparators, civilian | Military Sieve 28.0% / 94.1%; START 28.8% / 94.3%; Careflight 23.6% / 95.9%; Triage Sieve 12.9% / 96.7% | `vassallo2017b` | READ |
| E-07 | MPTT, prospective military | Camp Bastion emergency department, March–September 2011, n = 357, 214 (59.9%) Priority One. Sensitivity 83.6% (78.0–88.3), specificity 51.0% (42.6–59.5). Under-triage 19.6 points lower and over-triage 11.6 points higher than the Military Sieve | `vassallo2017c` | READ (citation details incomplete on the page) |
| E-08 | MPTT-24 algorithm (Figure 2, corrected version of record) | Six steps in order: catastrophic haemorrhage, yes gives Priority 1 (apply tourniquet or haemostatic dressing); walking, yes gives Priority 3; breathing, no gives Dead; responds to voice, no gives Priority 1 (recovery position); respiratory rate 12 to 23, no gives Priority 1; heart rate below 100, yes gives Priority 2 and no gives Priority 1. Changes from the MPTT: upper respiratory rate threshold raised to 24, AVPU in place of GCS, haemorrhage check added. The text says 'responds to voice' replaces 'GCS below 14', the alert and voice boundary sitting at a median GCS of 13; read literally, the figure sends a casualty who responds only to voice on to the next step, where the GCS rule would have made them Priority 1. The text and the figure therefore differ for that group | `vassallo2017d` | READ (full text and figure, 12 Nov 2026) |
| E-09 | MPTT-24 performance | JTTR (3,654 adults, 2006-2013; 98.3% male, median age 24, 55.1% explosive, 34.3% gunshot, 47.6% Priority 1): sensitivity 66.7% (64.5–68.9), specificity 69.9% (67.8–71.9), positive predictive value 67.0%. TARN (127,233; 19.5% Priority 1): sensitivity 53.5% (52.9–54.1), specificity 74.8% (74.6–75.1), positive predictive value 34.0%. Respiratory rate at or above 24 alone, JTTR: 35.2% and 82.0%. Tested on first recorded hospital respiratory rate and registry GCS, not on AVPU at the scene. The authors estimate one extra under-triaged casualty per 30 true Priority 1 casualties compared with the MPTT | `vassallo2017d` | READ (full text, 12 Nov 2026) |
| E-10 | Military Sieve, same cohorts | JTTR 43.2% / 93.7%; TARN 28.0% / 94.1% | `vassallo2017d` | READ |
| E-11 | Physiology used | First recorded hospital values, not pre-hospital. Complete pre-hospital data existed for 16.7% of military and 37.2% of civilian cases | `vassallo2017d` | READ |
| E-12 | Definition of over-triage | The authors define under-triage as 1 − sensitivity and over-triage as 1 − positive predictive value. Civilian over-triage for MPTT-24 is 66.0% on that definition | `vassallo2017d` | **CORRECTED** — the design had treated over-triage as 1 − specificity |
| E-13 | "The MPTT has 83.6% sensitivity and 51.0% specificity" | True only of the prospective Bastion cohort. Sensitivity ranges from 53.5% to 83.6% across the four cohort and tool combinations | E-03, E-05, E-07, E-09 | **CORRECTED** |

Open item: the MPTT-24 flowchart (Figure 2 of `vassallo2017d`) was not readable as text, so the exact order of steps and the heart rate comparison (at or above 100, or above 100) must be confirmed against the figure before the rule is coded. The reader also reported that some confidence intervals in that paper's Table 2 do not contain their point estimates; check the version of record before quoting odds ratios or predictive values from it.

### A2. Ultrasound (eFAST)

| Id | Claim | Verified value | Source | Status |
|---|---|---|---|---|
| E-14 | In-hospital pooled accuracy | 75 studies, 24,350 patients. Pneumothorax 69% (66.0–72.7) / 99% (17 studies, 3,653 patients); pericardial effusion 91% (87.0–94.4) / 94% (92.2–95.7) (9 studies, 1,031 patients, penetrating trauma only); intra-abdominal free fluid 74% (72.6–75.8) / 98% (97.3–97.8) (52 studies) (sensitivity / specificity). Heterogeneity high throughout. Useful for ruling in, not for ruling out | `netherton2019` | READ (full text, 12 Nov 2026) |
| E-15 | Free fluid by blood pressure | Hypotensive (systolic below 90 mm Hg) 74% (68.1–79.9) / 95% (92.6–96.6); normotensive adult 76% (73.9–78.1) / 98% (97.5–98.1); paediatric 71% / 95% | `netherton2019` | READ (full text, 12 Nov 2026) |
| E-16 | Pre-hospital, helicopter service | New South Wales, 2013–2017. 896 scanned, 92 excluded before hospital and 393 in hospital, 411 analysed; 98% blunt trauma, median ISS 22. Free fluid 25% (16–36) / 96% (93–98), from 21 true positives, 63 false negatives, 9 false positives, 257 true negatives; pneumothorax 38% (29–47) / 96% (93–98); haemothorax 17% (6–36) / 97% (94–99); pericardial effusion 17% (0–64) / 100% (98–100), six cases only. 32% of abdominal scans were recorded as indeterminate. By shock index: high, sensitivity 50% and specificity 81%; low, 32% and 98%; intervals overlap. The results text gives haemothorax sensitivity as 20% (8–39), which disagrees with the abstract and Table 2; the table value is used | `partyka2022` | READ (full text, 12 Nov 2026) |
| E-17 | Pre-hospital, multicentre cohort | Any abdominal injury 27% (22–32) / 96% (93–98); haemoperitoneum 38% (28–48) / 94% (91–96); pneumothorax 23% (17–31) / 97% (95–99) | `efast2025` | SECONDARY |
| E-18 | Open human FAST image data | None found. Published models used private hospital archives or swine data | search, 9 Nov 2026 | CARRIED |

### A3. Haemorrhage, tranexamic acid and transfusion

| Id | Claim | Verified value | Source | Status |
|---|---|---|---|---|
| E-19 | CRASH-2 design | 274 hospitals, 40 countries; 20,211 randomised within 8 hours of injury: 10,096 allocated tranexamic acid and 10,115 placebo; 10,060 and 10,067 analysed; 1 g over 10 minutes then 1 g over 8 hours | `crash2_2010` | READ (full text, 12 Nov 2026) |
| E-20 | CRASH-2 all-cause mortality | 1,463 (14.5%) against 1,613 (16.0%); relative risk 0.91 (0.85–0.97), p = 0.0035. By time from injury, all-cause (99% intervals): within 1 hour 0.87 (0.75-1.00); 1 to 3 hours 0.87 (0.75-1.00); after 3 hours 1.00 (0.86-1.17); test for heterogeneity p = 0.11, against a prespecified threshold of p < 0.001. Blood products were given to 50.4% against 51.3%, relative risk 0.98 (0.96-1.01); the authors note that patients who survive because of treatment have more opportunity to be transfused. Vascular occlusive events 1.7% against 2.0%. Entry was by clinical judgement under the uncertainty principle, not by laboratory test. The authors note digit preference in the reported time from injury | `crash2_2010` | READ (full text, 12 Nov 2026) |
| E-21 | CRASH-2 death due to bleeding | 489 (4.9%) against 574 (5.7%); relative risk 0.85 (0.76–0.96), p = 0.0077 | `crash2_2010` | READ (full text, 12 Nov 2026) |
| E-22 | Effect by time to treatment (bleeding death) | Up to 1 hour: 5.3% against 7.7%, RR 0.68 (0.57–0.82). 1 to 3 hours: 4.8% against 6.1%, RR 0.79 (0.64–0.97). Over 3 hours: 4.4% against 3.1%, RR 1.44 (1.12–1.84). Interaction p < 0.0001 | `crash2_2011` | READ |
| E-23 | Status of the timing analysis | Exploratory analysis of the trial, not a pre-specified primary result | `crash2_2011` | READ |
| E-24 | Decay of benefit with delay | Pooled patient-level data, 40,138 patients: CRASH-2 (20,127, trauma) and WOMAN (20,011, postpartum haemorrhage). Overall odds ratio for survival 1.20 (1.08–1.33); immediate treatment 1.72 (1.42–2.10); benefit falls about 10% per 15 minutes of delay; none after about 3 hours | `gayetageron2018` | READ |
| E-25 | When bleeding deaths happen | 1,408 bleeding deaths; 884 (63%) within 12 hours of onset | `gayetageron2018` | READ |
| E-26 | Limits of the delay estimate | Half the patients are obstetric; trauma onset times are often unwitnessed; time-to-death data existed only for the obstetric trial; adjusted only for age and systolic pressure | `gayetageron2018` | READ |
| E-27 | CRASH-3 primary result | 12,737 randomised; 9,202 (72.2%) treated within 3 hours. The primary result is for that within-3-hours group, not the whole trial: head injury-related death 18.5% against 19.8%; risk ratio 0.94 (0.86–1.02) | `crash3_2019` | READ |
| E-28 | CRASH-3 subgroups | Excluding GCS 3 or bilateral unreactive pupils: 12.5% against 14.0%, RR 0.89 (0.80–1.00). Mild to moderate: RR 0.78 (0.64–0.95). Severe: RR 0.99 (0.91–1.07). Heterogeneity p = 0.030 | `crash3_2019` | READ |
| E-29 | CRASH-3 safety | Vascular occlusive events RR 0.98 (0.74–1.28); seizures RR 1.09 (0.90–1.33) | `crash3_2019` | READ |
| E-30 | Bleeding-death prognostic model | 13,485 CRASH-2 patients and 9,945 from a French registry, admitted within 3 hours. Bleeding deaths 815 (6%) and 102 (1%). Simple model: age, systolic pressure, GCS; C-statistic 0.84 (0.80–0.88). Full model adds heart rate, respiratory rate and penetrating injury; 0.85 (0.81–0.88). Penetrating injury was 51% of the trial cohort and 6% of the registry. Risk rose with age and fell with systolic pressure and GCS; heart rate and respiratory rate showed U-shaped relations. Calibration slope 1.01 (0.96-1.07) for the full model in development and 1.12 (0.95-1.29) in the registry | `ageron2019` | READ (full text, 12 Nov 2026) |
| E-31 | ABC transfusion score | Four unweighted items: penetrating mechanism, positive FAST, systolic pressure 90 mm Hg or less, heart rate 120 or more. Score of 2 or more: 75% sensitive, 86% specific; AUROC 0.842; 596 patients, massive transfusion rate 12.4% | `nunez2009` | READ |
| E-32 | Tourniquet survival | Baghdad combat support hospital, 2006; 2,838 casualties with major limb trauma, 232 with tourniquets (428 tourniquets, 309 limbs). Applied before shock against after: 90% against 10% survival. Pre-hospital against emergency department: 89% against 76%. Five who needed one and got none: 0% | `kragh2009` | READ |
| E-33 | A published Bayesian reanalysis of CRASH-3 | None confirmed in this check | search, 9 Nov 2026 | NOT READ |

### A4. Military patient mix and timelines

| Id | Claim | Verified value | Source | Status |
|---|---|---|---|---|
| E-34 | UK field hospital admissions, Afghanistan | 1 April 2006 to 30 November 2014: 7,601 UK Service personnel admitted. 3,347 (44.0%) natural causes; 4,220 injuries; 34 unclassified | `mod2016` | READ |
| E-35 | Battle against non-battle injury | Roughly half and half. Row counts: battle 2,271 (explosion 1,164, small arms 974, other 133); non-battle 2,019 (other 1,949, small arms 52, explosion 18) | `mod2016` | READ (rows sum to 4,290, not 4,220; shares are approximate) |
| E-36 | Derived shares of all admissions | Disease about 44%, battle injury about 30%, non-battle injury about 27% | arithmetic on E-34 and E-35 | Derived here, not stated in the source |
| E-37 | Trauma team activations | 1,982 personnel: 74% of battle and 18% of non-battle injury admissions | `mod2016` | READ |
| E-38 | Injuries by body region, trauma team cohort | 10,371 injuries. Extremities 4,590 (44%); head and neck 1,908 (18%); spine and back 1,339 (13%); torso 691 (7%); other 1,843 (18%) | `mod2016` | READ (percentages calculated here) |
| E-39 | Where battlefield deaths happen | 4,596 US deaths 2001–2011; 87.3% before reaching a treatment facility | `eastridge2012` | READ |
| E-40 | Potentially survivable deaths | Of pre-facility deaths, 24.3% (976) potentially survivable; 90.9% of those from haemorrhage | `eastridge2012` | READ |
| E-41 | Site of lethal haemorrhage | Truncal 67.3%, junctional 19.2%, extremity 13.5% | `eastridge2012` | READ |
| E-42 | Clinical timelines | 10 minutes: life-saving first response (control of severe bleeding, airway, breathing, circulation). 1 hour: advanced resuscitation and pre-hospital emergency care. 2 hours: life-, limb- and function-preserving surgery and resuscitation. The first two apply to any acute emergency, not only trauma | `ajp410` paras 3.19–3.20 | READ |
| E-43 | Roles of care | Role 1 primary care, triage, pre-hospital emergency care. Role 2 forward (2F), basic (2B), enhanced (2E). Role 3 deployed hospital with CT. Role 4 definitive care at home | `ajp410` paras 2.42–2.46 | READ |
| E-44 | Edition | Edition C Version 1, September 2019. Whether this is still the current edition was not checked | `ajp410` | READ |

### A5. Sepsis and the disease stream

| Id | Claim | Verified value | Source | Status |
|---|---|---|---|---|
| E-45 | Sepsis-3 definition | Life-threatening organ dysfunction from a dysregulated host response to infection; SOFA rise of 2 or more, in-hospital mortality above 10% | `singer2016` | READ |
| E-46 | qSOFA | Two or more of: respiratory rate 22 or more, altered mentation, systolic pressure 100 mm Hg or less | `singer2016` | READ |
| E-47 | Septic shock | Vasopressors needed for mean arterial pressure of 65 mm Hg, and lactate above 2 mmol/L without hypovolaemia; hospital mortality above 40% | `singer2016` | READ |
| E-48 | PhysioNet 2019 | Over 60,000 intensive care patients from three hospital systems, up to 40 hourly variables; Sepsis-3 onset. 40,336 records from systems A and B shared; 24,819 from A, B and C held back. 104 groups, 853 submissions. Utility score rewards prediction from 6 hours before onset and penalises late and false alerts. The winning entry scored 0.360 overall, 0.433 and 0.434 on the two systems it had seen, and -0.123 on the unseen one. The authors state the utility values can be chosen to reflect a hospital's own preferences, and that entries with the highest utility did not necessarily have a high area under the curve | `reyna2020` | READ (full text, 12 Nov 2026) |
| E-49 | ICU-Sepsis | 716 states, 25 actions, built from MIMIC-III; random policy 0.78, estimated clinician policy 0.78, optimal 0.88, dataset average 0.77; not to guide practice | `choudhary2024` | READ (full text, 12 Nov 2026) |
| E-50 | Critique of the original sepsis reinforcement learning work | Off-policy evaluation by importance sampling gives almost no weight to trajectories where the learned policy departs from clinicians, so a policy of withholding treatment can score well. A zero-drug policy beat the clinician policy in most of the critics' reproductions | `jeter2019` | READ |
| E-51 | DDXPlus | About 1.3 million synthetic patients, 49 pathologies, 110 symptoms and 113 antecedents, each with a differential diagnosis; generated from a proprietary knowledge base and a commercial rule-based system | `fansitchango2022` | READ (full text, 12 Nov 2026) |

### A6. Method and brain-analogy sources

| Id | Claim | Verified value | Source | Status |
|---|---|---|---|---|
| E-52 | Threshold approach | The probability of disease decides between withholding, testing and treating | `pauker1980` | READ (abstract summary only; threshold formulae not read) |
| E-53 | Dual process and error | Two modes, fast intuitive and slow deliberate. Norman's review finds the fast mode no more prone to error than the slow one; prompting use of both reduced error | `norman2009` | **CORRECTED** — the design must not present System 1 as the faulty mode |
| E-54 | Dual process model of diagnosis | Diagnosis as two systems: System 1, heuristic and intuitive, and System 2, systematic and analytical, joined in one schematic model. The author cautions that not all clinical reasoning falls neatly into one system. Either system can override the other; repeated analytical processing of a presentation leads to recognition and a default to the intuitive system; both outputs pass through a calibration step | `croskerry2009` | READ (abstract and opening of the full text, 12 Nov 2026) |
| E-55 | Predictive coding | Feedback connections carry predictions; feedforward connections carry the error between prediction and input | `rao1999` | READ |
| E-56 | Dopamine and prediction error | Dopamine neuron firing tracks the difference between expected and received reward | `schultz1997` | READ (abstract; the link to temporal-difference learning is in the full paper) |
| E-57 | Complementary learning systems | Hippocampus stores single episodes fast; neocortex learns structure slowly; replay protects old knowledge. The 2016 update adds that cortical learning can be fast when new information fits prior knowledge | `kumaran2016` | READ |
| E-58 | Backpropagation and the brain | Long thought implausible; feedback may instead induce activity differences that approximate error signals locally | `lillicrap2020` | READ |
| E-59 | Fast-and-frugal trees | The choice of exit structure in the tree corresponds directly to the setting of the decision criterion in signal detection; the tree's sensitivity depends on the order and properties of its cues. The trees search little information, are robust, and adapt to the payoff structure of the task | `luan2011`, `green1997` | READ for `luan2011` (abstract in the full text, 12 Nov 2026); `green1997` not read |
| E-60 | The pneumonia and asthma case | Models learned that asthma lowers pneumonia mortality because asthmatic patients went straight to intensive care; 14,199 patients, 10.86% mortality | `caruana2015` | READ |

### A7. Teaching sources

| Id | Claim | Verified value | Source | Status |
|---|---|---|---|---|
| E-61 | CS50's stated principles | Accessibility, rigour and community. Within reach of students with no background, but demanding: about 12 hours a week, and two thirds of students new to the subject. Sections by comfort level; half the problem sets offered in a lower-floor and a higher-ceiling version; final projects | `malan_statement` | READ (undated) |
| E-62 | CS50 practices | Week 0 in Scratch before C; problem sets set in cryptography, forensics and finance; sections for less comfortable, more comfortable and in between; students act out sorting algorithms on stage. Enrolment 132 (2006) to 282 (2007) | `malan2010` | READ |
| E-63 | PRIMM | Predict, Run, Investigate, Modify, Make. Evaluated in 13 schools with 493 pupils aged 11 to 14 over 8 to 12 weeks, against a control group without random assignment: the PRIMM group did better on the post-test, and teachers reported it helped in mixed-ability classes | `sentance2019` | READ (full text, 12 Nov 2026) |
| E-64 | Natural frequencies and grids | Natural frequencies improve diagnostic inference over probabilities. In 108 patients given natural frequencies, adding a grid raised accuracy from 32% to 55%; the least numerate gained most | `garciaretamero2015` | READ |
| E-65 | Concreteness fading | Begin with concrete material and fade explicitly and gradually to the abstract | `fyfe2014` | READ (abstract) |
| E-66 | Fry: earn attention, demonstrate, do not simplify down | A reason to care comes before the technical content; a calculated live demonstration opened the 2019 Christmas Lectures; she invites the audience up to the subject | `fry_leelavati2026` | READ |
| E-67 | Multimedia learning principles | Coherence (leave out what is not needed), signalling, redundancy, spatial and temporal contiguity, segmenting, pre-training, modality, personalisation, among fifteen in the third edition (twelve in the second) | `mayer2009` | READ (contents and opening chapters of the third edition, 2020, 12 Nov 2026) |
| E-68 | Fry: familiar anchors, human stories, honest models | Ties mathematics to a human story and to what the audience knows; a model represents reality and is not reality | `fry_chalkdust2015` | READ |
| E-69 | Fry: with the audience | Mathematics should feel done with people, not to them | `fry_plus2025` | READ |
| E-70 | Random variables as objects | Probabilistic programming tools run in batch and return arrays of draws. A random-variable datatype lets uncertain quantities be combined with ordinary arithmetic, the draws hidden. Implemented as `rv`, then `rvar` in the R `posterior` package. Comments: draws stay static unless the model is rerun; some prefer the draws visible | `gelman2026` | READ (opinion post on tooling; the papers and packages it names were not read) |

### A8. Background pack (12 November 2026)

Added for the lens background files in `docs/background/`. Abstracts were read through Europe PMC, OpenAlex and Crossref, which return the publisher's abstract; "READ (abstract)" means that and no more. The reasoning built on each entry is in the lens file that cites it.

| Id | Claim | Verified value | Source | Status |
|---|---|---|---|---|
| E-71 | Military observational study of tranexamic acid | Role 3 hospital, southern Afghanistan; 896 combat casualties given at least one unit of red cells, 293 given tranexamic acid. Unadjusted mortality 17.4% against 23.9% (P=.03) although the treated group was more severely injured (mean ISS 25.2 against 22.5). Massive transfusion subgroup: 14.4% against 28.1% (P=.004); odds ratio for survival 7.228 (3.016-17.322) | `matters2012` | READ (abstract) |
| E-72 | PROPPR transfusion ratio trial | 680 patients, 12 level I centres; 1:1:1 (338) against 1:1:2 (342). 24-hour mortality 12.7% against 17.0%, difference -4.2 points (-9.6 to 1.1), P=.12. 30-day 22.4% against 26.1%, difference -3.7 (-10.2 to 2.7), P=.26. Secondary: death from exsanguination in 24 hours 9.2% against 14.6% (P=.03); haemostasis 86% against 78% (P=.006) | `proppr2015` | READ (abstract) |
| E-73 | Bayesian reanalysis of PROPPR | Posterior probability that 1:1:1 is superior: 93% at 24 hours (Bayes factor 13.7; RR 0.75, 95% credible interval 0.45-1.11) and 87% at 30 days (Bayes factor 6.56; RR 0.82, 0.57-1.16). Priors not stated in the abstract | `lammers2023` | READ (abstract) |
| E-74 | Bayesian reanalysis of a prehospital tranexamic acid trial, with earlier trials as priors | STAAMP: 903 patients, tranexamic acid 447 against placebo 456; 30-day mortality 8.1% against 9.9%, hazard ratio 0.81 (0.59-1.11). Posterior ratio 0.91 (0.85-0.97) with a CRASH-2 prior; 0.80 (0.65-0.97) with a PATCH-Trauma prior; 0.82 (0.52-1.23) with a non-informative prior. Probability of reduced 30-day mortality 84% to 99% across priors | `staamp_bayes2026` | READ (abstract) |
| E-75 | PAMPer prehospital plasma trial | Cluster-randomised, air transport; 501 patients (230 plasma, 271 standard care). 30-day mortality 23.2% against 33.0%, difference -9.8 points (-18.6 to -1.0), P=.03. Survival curves separate from 3 hours | `pamper2018` | READ (abstract) |
| E-76 | COMBAT prehospital plasma trial | Single centre, urban ground transport, Denver; 144 randomised, 125 analysed (65 plasma, 60 saline). 28-day mortality 15% against 10%, odds ratio 1.54 (0.60-3.98), P=.37. Median transport 19 minutes against 16. The authors themselves suggest blood products might help where transport is longer | `combat2018` | READ (full text, 12 Nov 2026) |
| E-77 | RePHILL UK prehospital blood trial | Four English prehospital critical care services; 432 randomised of a target 490 (209 red cells and lyophilised plasma, 223 saline). Composite of death or impaired lactate clearance 64.3% against 64.8%; adjusted difference -0.025 points (-9.0 to 9.0), p=0.996. Components: death 43% against 45%, relative risk 0.97 (0.78-1.20); failure to clear lactate 50% against 55%, 0.94 (0.78-1.13). Death within 3 hours 16% against 22%, 0.75 (0.50-1.13) | `rephill2022` | READ (2022 Lancet Haematology report in full, 12 Nov 2026: 128 of 199 against 136 of 210; and the abstract of the NIHR monograph, PMID 38224557) |
| E-78 | PATCH-Trauma prehospital tranexamic acid trial | 1,310 patients, 15 services in Australia, New Zealand and Germany. Survival with favourable function at 6 months 53.7% against 53.5%, RR 1.00 (0.90-1.12). Death by 28 days 17.3% against 21.8%, RR 0.79 (0.63-0.99). Death by 6 months 19.0% against 22.9%, RR 0.83 (0.67-1.03) | `patch2023` | READ (abstract) |
| E-79 | Prehospital tranexamic acid in brain injury | 1,063 randomised, 966 analysed, GCS 12 or less, systolic pressure 90 or above, treated within 2 hours. Favourable 6-month outcome 65% with tranexamic acid against 62% with placebo; difference 3.5 points, lower one-sided 90% limit -0.9, P=.16. 28-day mortality 14% against 17%, difference -2.9 (-7.9 to 2.1). No benefit shown. Significance thresholds were asymmetric by design: 0.1 for benefit and 0.025 for harm | `rowell2020` | READ (full text, 12 Nov 2026) |
| E-80 | Survival bias in transfusion ratio studies | 134 massively transfused patients. With the plasma ratio fixed at 24 hours, a high ratio had a relative risk of death of 0.37 (0.22-0.64). With the ratio treated as changing over time, 0.84 (0.47-1.50). 54% of deaths occurred in the first 6 hours, when the ratio was still low | `snyder2009` | READ (abstract) |
| E-81 | The 2009 sixty-minute evacuation mandate | 21,089 US casualties, Afghanistan, 2001-2014. Killed in action 16.0% (386 of 2,411) before, 9.9% (964 of 9,755) after. Case fatality 13.7 before, 7.6 after. Died of wounds 4.1% before, 4.3% after, P=.71. Estimated 359 lives saved. Among 4,542 with detailed data: median transport 90 minutes before, 43 after; missions within 60 minutes 24.8% before, 75.2% after. Among the critically injured, killed in action 6.8% (40 of 589) of those who received a blood transfusion against 51.0% (249 of 488) of those who did not. The authors list as limitations: historical controls, post hoc analysis of non-randomised data, survival bias in the transfusion analysis, and several factors changing at once, so that only descriptive interpretation was viable. Only 37.3% of casualties had matched flight and facility data | `kotwal2016` | READ (full text, 12 Nov 2026) |
| E-82 | What reduced combat mortality | 56,763 US battle-injured. Case fatality fell from 20.0% to 8.6% in Afghanistan and 20.4% to 10.1% in Iraq. Survival of the critically injured (ISS 25-75) rose from 2.2% to 39.9% in Afghanistan. Simulation: 3,672 deaths averted (3,209-4,244), of which 44.2% attributed to three interventions: tourniquets 12.9%, blood transfusion 23.8%, faster prehospital transport 7.5% | `howard2019` | READ (abstract) |
| E-83 | Prehospital blood in combat casualties | 502 casualties with shock or proximal amputation, 2012-2015. Death within 24 hours 5% (3 of 55) with prehospital transfusion against 19% (85 of 447) without. Adjusted hazard ratio 0.26 (0.08-0.84) at 24 hours, 0.39 (0.16-0.92) at 30 days. Transfusion within 15 minutes of rescue (median 36 minutes after injury): 0.17 (0.04-0.73) | `shackelford2017` | READ (abstract) |
| E-84 | UK combat casualty survival | UK Joint Theatre Trauma Registry: 2,792 casualties, 14,252 injuries, 608 deaths (22%). About 70% of hostile-action casualties were from explosive munitions. Extremities 43% of injuries. The New Injury Severity Score at which half survive rose from 32 in 2003 to 60 in 2012 | `pennbarwell2015` | READ (abstract) |
| E-85 | When bleeding deaths happen after admission | Five prospective studies, 4,064 haemorrhaging patients. Median time from admission to death from haemorrhage 2.0 to 2.6 hours; about 85% within 6 hours. Hourly death rate about 4.6% at 1 hour, about 1% at 6 hours, under 0.1% by 9 hours | `fox2017` | READ (abstract) |
| E-86 | US military resuscitation doctrine | Whole blood preferred, otherwise components at about 1:1:1. Tranexamic acid 2 g only if started within 3 hours of injury. Systolic pressure target about 100 (90-110) before surgical control. Massive transfusion predictors: three of four of systolic pressure under 100, heart rate over 100, haematocrit under 32%, pH under 7.25 predicts about 70% risk; all four about 85%. Published 12 July 2019, with rapid updates in June and August 2023 | `jts_dcr2019` | READ (full guideline) |
| E-87 | How good field triage protocols are, and the benchmark | 21 studies. Sensitivity ranged from 10% to 100% and specificity from 9% to 100%; nearly all protocols had low sensitivity. Cites the American College of Surgeons benchmarks: under-triage below 5%, over-triage below 50% | `vanrein2017a` | READ (abstract) |
| E-88 | Triage protocol against triage practice | 4,950 patients, 10 Dutch hospitals; 436 (8.8%) severely injured. In practice: under-triage 21.6% (18.0-25.7), over-triage 30.6% (29.3-32.0). The protocol alone: under-triage 63.8% (59.2-68.1), over-triage 7.4% (6.7-8.2). Protocol compliance 73% | `vanrein2017b` | READ (abstract) |
| E-89 | A decision rule derived and validated on a large cohort (PECARN) | 42,412 children, 25 emergency departments; clinically important brain injury in 0.9%. Aged 2 and over: six predictors; validation negative predictive value 3798 of 3800 (99.95%), sensitivity 61 of 63 (96.8%, 89.0-99.6). Under 2: validation sensitivity 25 of 25. About a fifth to a quarter of scanned children were in the very-low-risk group | `kuppermann2009` | READ (abstract). Derivation by recursive partitioning is general knowledge and is not stated in the abstract |
| E-90 | Ten model families against the ABC score | 2,438 patients, 4.9% massively transfused. Every model except the single decision tree and the support vector machine reached an AUC above 0.75 (range 0.75-0.83). Model sensitivity 0.55-0.83 against 0.36 for the ABC score; specificity 0.75-0.81 against 0.80 | `wjs_ml2023` | READ (abstract) |
| E-91 | Pooled performance and quality of transfusion prediction models | 21 studies, 50 models. Pooled AUROC: random forest 0.89 (0.85-0.93), neural networks 0.88, XGBoost 0.86. Median quality score 51 of 100; no study met every reporting item; most had no external validation | `mhp_meta2026` | READ (abstract) |
| E-92 | A boosted model on 1.2 million patients | 1,232,956 adults, 8.9% transfused. XGBoost AUROC 0.845; sensitivity 0.79 and specificity 0.72 at the chosen threshold. Leading predictors: Injury Severity Score, systolic pressure, activation level, pulse, age. Internal validation only | `tqip_ml2026` | READ (abstract) |
| E-93 | Net benefit | A model is judged by its consequences: net benefit across a range of threshold probabilities, where the threshold encodes how a false positive is weighed against a false negative | `vickers2006` | READ (abstract) |
| E-94 | Hourly cost of delay in sepsis, modern cohort | 49,331 patients, 149 New York hospitals. Each hour to completing the 3-hour bundle: odds ratio for death 1.04 (1.02-1.05). Each hour to antibiotics: 1.04 (1.03-1.06). Each hour to the fluid bolus: 1.01 (0.99-1.02), not associated | `seymour2017` | READ (abstract) |
| E-95 | Hourly cost of delay in septic shock, older cohort | 2,731 patients, 1989-2004. Effective antimicrobial within the first hour of hypotension: 79.9% survival. Each hour of delay over the next six: survival fell by an average of 7.6%; adjusted odds ratio for death per hour 1.119 (1.103-1.136) | `kumar2006` | READ (abstract) |
| E-96 | A deployed sepsis model, checked independently | 38,455 hospitalisations, sepsis in 7%. AUC 0.63 (0.62-0.64). Alerts fired on 18% of all hospitalisations. The model did not identify 67% of sepsis cases | `wong2021` | READ (abstract) |
| E-97 | Fluids first or vasopressors first | 1,563 patients, 60 US centres. Death by 90 days 14.0% (restrictive) against 14.9% (liberal); difference -0.9 points (-4.4 to 2.6), P=.61. The restrictive group received a median 2,134 mL less fluid | `clovers2023` | READ (abstract) |
| E-98 | A network that learned the hospital | 158,323 radiographs, three hospital systems. Pneumonia prevalence 34.2% at one site and 1.2% at another. A network identified the source hospital for 99.95% and 99.98% of images. The jointly trained model scored AUC 0.931 internally and 0.815 at a third site. Ranking by hospital alone scored 0.861 | `zech2018` | READ (full text, open access) |
| E-99 | Good on average, poor on a subgroup | Relative performance differences of over 20% on clinically important subsets that were not labelled in the data | `oakdenrayner2019` | READ (abstract, arXiv:1909.12475) |
| E-100 | Shortcut learning | Chest radiograph models that looked accurate relied on confounding features, not lung pathology, and failed in new hospitals | `degrave2021` | READ (abstract) |
| E-101 | What a network achieves with enough labelled images | Trained on 128,175 images, each graded 3 to 7 times. AUC 0.991 and 0.990 on two validation sets. Two operating points: 90.3% sensitivity with 98.1% specificity, or 97.5% with 93.4% | `gulshan2016` | READ (abstract) |
| E-102 | Deep learning on eFAST, swine data | Six eFAST tasks, images from 27 swine. M-mode sites above 85% accuracy; B-mode sites 68-74%; pelvic haemorrhage 62% | `efast_arch2024` | READ (abstract) |
| E-103 | High accuracy without looking at the right thing | Five military working dogs and a cadaver model, 327 clips. All models above 82% accuracy; one reached 99.8% at the bladder view. Heat maps showed the most accurate models did not always attend to the relevant features | `mwd_pocus2024` | READ (abstract) |
| E-104 | A rule written for a different body | CT of 100 male military cases. Mean chest wall thickness 5.36 cm (SD 1.19) against a recommended needle of about 5 cm. An 8 cm catheter would reach in 99% | `harcke2007` | READ (abstract) |
| E-105 | Tension pneumothorax as a cause of combat death | Vietnam War data, 978 casualties with radiographs. Authors estimate tension pneumothorax contributed to about 3 to 4% of fatal combat casualties; the denominator is not clear in the abstract | `mcpherson2006` | READ (abstract) |
| E-106 | Needle decompression in the field | 111 patients, 1997-2012; 79% decompressed at the point of injury; 32% then had a chest tube placed in the field. Authors conclude the standard needle has a high failure rate on the battlefield | `idf_nt2015` | READ (abstract) |
| E-107 | An ontology doing diagnostic work at national scale | 4,660 participants. Clinical features coded as Human Phenotype Ontology terms, then sequencing with automated prioritisation. About 25% of probands received a diagnosis; 35% where a single-gene cause was likely against 11% where the cause was complex | `genomes2021` | READ (abstract) |
| E-108 | One trial, four priors | EOLIA: 249 patients, 60-day mortality 35% against 46%, reported as not significant. Posterior probability of any benefit: 96% with a minimally informative prior, 88% with a sceptical prior, 99% with an enthusiastic one. Probability of the large effect the trial was powered for: 2% or less | `goligher2018` | READ (abstract; the reader flagged the text as hard to parse, so check against the paper) |
| E-109 | How to do and report a Bayesian reanalysis | A methods overview with a worked reanalysis; proposes a standard approach to reduce misreading of P values and of non-significant results | `zampieri2021` | READ (abstract). Open access |
| E-110 | Physicians with and without a language model | 50 physicians. Median diagnostic reasoning score 76% with the model against 74% without; difference 2 points (-4 to 8), P=.60. The model alone scored 92%, 16 points above the physicians without it (2 to 30). Vignettes, not patients | `goh2024` | READ (full text, open access) |
| E-111 | Retrieval from curated sources | 314 clinical questions, nine specialties, rated by ten clinicians. The retrieval-augmented model was rated significantly better than standard models on factuality, completeness, preference and safety. No effect sizes in the abstract | `zakka2024` | READ (abstract) |
| E-112 | Prediction sets with a guarantee | Wraps any trained model to output a set of answers that contains the truth at a rate the user chooses, without assuming a distribution | `angelopoulos2021` | READ (abstract, arXiv:2107.07511) |
| E-113 | How far conformal prediction has reached the clinic | A review found 14 clinical applications, scattered and rarely involving clinicians | `vazquez2022` | READ (abstract) |
| E-114 | Natural frequencies | With information given as frequencies, statistically naive participants reached Bayesian answers in up to 50% of inferences | `gigerenzer1995` | READ (abstract) |
| E-115 | Two ways to learn from data | Assume a model of how the data arose, or treat the mechanism as unknown and judge by prediction | `breiman2001` | READ (abstract) |
| E-116 | Explanation and prediction are different goals | The goal changes the modelling choices at every step, and the two are often conflated | `shmueli2010` | READ (abstract) |
| E-117 | Three data science tasks | Description, prediction and counterfactual prediction. Causal questions need knowledge of the causal structure that the data alone do not supply. Worked example from health records: how can women with a history of stroke be grouped (description); what is the probability of a stroke next year (prediction); will starting a statin reduce the risk (causal) | `hernan2019` | READ (opening of the full text, 12 Nov 2026) |
| E-118 | The case for interpretable models | Explaining a black box after the fact is unreliable for high-stakes decisions; an explanation that is right 90% of the time is wrong 10% of the time. The assumed trade-off between accuracy and interpretability is called a myth for structured data with meaningful features. Example: a three-rule list using age, sex and prior offences set against a proprietary recidivism tool with over 130 inputs. A saliency map shows where a network looked, and can look the same for two different labels | `rudin2019` | READ (abstract and opening sections of the full text, 12 Nov 2026) |
| E-119 | Cautions for reinforcement learning from clinical records | Three questions to ask of any such study: was the algorithm given every variable that influenced the clinicians' decisions; how large is the effective sample once only patients treated as the new policy would treat them are counted; will it behave as intended when used prospectively. The authors include three of the original sepsis policy paper's authors | `gottesman2019` | READ (full text, 12 Nov 2026) |
| E-120 | The original sepsis reinforcement learning paper | Trained on 17,083 admissions from one hospital's database and tested on 79,073 from 128 hospitals; 48 variables, 750 states, 25 actions. Evaluated by weighted importance sampling: estimated value 84.5 for the learned policy against 56.9 for clinicians. The policy recommended less fluid and more vasopressor; vasopressors 30% of the time against 17% given. Mortality was lowest where the dose given matched the recommendation. The authors state it needs prospective evaluation. Listed limitations include that some laboratory values available to the algorithm would not have been available to clinicians at the time, and that hospital mortality replaced 90-day mortality in the test set | `komorowski2018` | READ (full text, 12 Nov 2026) |
| E-121 | A small trial read two ways | 200 patients; 24-hour mortality 5.9% against 10.2%, p=0.28. Bayesian model: 86.2% probability of reduced mortality, above 81% across priors | `csp_bayes2026` | READ (abstract) |
| E-122 | State of military ultrasound AI | Models trained on tissue phantoms and tested on swine; a full-torso phantom gave 71.5% accuracy on blind inference; a Norwegian armed forces project describes plans with no results yet. No human validation found | `mil_pocus_ai` | READ (abstracts) |
| E-123 | The golden hour result re-examined | 4,542 US casualties, Afghanistan, 2001-2014; inverse probability weighting for selection, then five rival explanations tested. No gradual time trend (adjusted odds ratio 0.99, 0.94-1.03). For military ISS of 25 or more, odds of being killed in action: 0.17 (0.06-0.51) with prehospital transfusion when needed; 0.67 (0.58-0.78) with first treatment by a forward surgical team; 0.61 (0.51-0.74) with transport within one hour. Simulation with transport times unchanged: 135 more killed in action (105-164) | `howard2018` | READ (abstract and results in the full text, 12 Nov 2026) |
| E-124 | Does anything else explain the timing effect of tranexamic acid | Exploratory analysis of CRASH-2. Blunt trauma, head injury and systolic pressure all rose with time to treatment, and GCS fell. Restricting to blunt trauma, to no head injury, or to systolic pressure below 100 did not remove the effect; the interaction with time stayed at p < 0.0001 in a multivariable model. No significant heterogeneity by pressure, GCS or injury type | `roberts2017` | READ (abstract and results in the full text, 12 Nov 2026) |
| E-125 | Over-triage and mortality in a simulated mass casualty incident | Discrete event simulation. Over-triage, defined as the share of non-critical patients among those labelled critical, was associated with higher, lower or mixed critical mortality depending on what caused it. The ratio of critical patients to treatment capability mattered more than the over-triage level in every scenario. The authors contrast this with earlier analyses that reported a positive linear relationship | `hupert2007` | READ (abstract and results in the full text, 12 Nov 2026) |
| E-126 | London, 7 July 2005 | 775 casualties, 56 deaths, 53 at the scene. 55 triaged to priority dispatch, 20 critically injured: scene over-triage 64%, 82% at the two sites triaged by ambulance staff and bystanders and 33% at the two triaged mainly by advanced prehospital teams. Critical mortality 15%; the authors judge it unrelated to over-triage | `aylwin2006` | READ (abstract and results in the full text, 12 Nov 2026) |
| E-127 | Torso injury, field hypotension and prehospital time | US registry 2012-2014; 42,135 adults with torso injury and prehospital systolic pressure of 110 or less, after excluding severe head injury and unsurvivable injury. Mortality 7.9%. Median prehospital time 37 minutes (28 penetrating, 40 blunt). Risk of death rose with prehospital time, most steeply in the first 30 minutes, in those with high-grade torso injury | `alarhayem2016` | READ (abstract and results in the full text, 12 Nov 2026) |
| E-128 | UK casualties who died after reaching care | 71 UK combat casualties, Iraq and Afghanistan, who reached a treatment facility alive and later died; 54 (76%) in Afghanistan. 38 (54%) died within 24 hours. 33 (47%) died of isolated head injury and 13 (18%) had unsurvivable head injury with other injuries. 15 (21%) died of haemorrhage after severe lower limb trauma, often with abdominal and pelvic injury | `keene2016` | READ (abstract and results in the full text, 12 Nov 2026) |

---

## Part B — Source briefs

Each brief follows the same five headings. All text is written for this register; nothing is copied from the source.

### vassallo2017a — MPTT derivation

- **Citation.** Vassallo J, Beavis J, Smith JE, Wallis LA. Major incident triage: derivation and comparative analysis of the Modified Physiological Triage Tool (MPTT). *Injury* 2017;48(5):992–999. doi:10.1016/j.injury.2017.01.038
- **What it shows.** A triage rule fitted to military registry data predicts the need for a life-saving intervention better than the tools then in use.
- **Numbers used.** E-01 to E-03. The best existing tool, the Modified Military Sieve, reached 50.9% sensitivity.
- **What it cannot support here.** Performance outside a deployed hospital, or on pre-hospital observations.
- **Access.** Author manuscript, CC BY-NC-ND 4.0: <https://eprints.bournemouth.ac.uk/27462>

### vassallo2017b — MPTT civilian validation

- **Citation.** Vassallo J, Smith JE, Bouamra O, Lecky FE, Wallis LA. The civilian validation of the Modified Physiological Triage Tool (MPTT). *Emergency Medicine Journal* 2017;34(12). doi:10.1136/emermed-2017-206647
- **What it shows.** On a large civilian registry the rule keeps the highest sensitivity of five tools and also the highest over-triage.
- **Numbers used.** E-04 to E-06.
- **What it cannot support here.** A claim that the rule performs equally in military and civilian casualties: sensitivity fell by twelve points.
- **Access.** Repository copy: <https://eprints.whiterose.ac.uk/123313/>

### vassallo2017c — MPTT prospective military evaluation

- **Citation.** Vassallo J and colleagues, *Journal of the Royal Army Medical Corps*, 2017. Title, volume and DOI were not shown on the page read and must be completed.
- **What it shows.** In a prospective cohort at Camp Bastion the rule found more of the casualties who needed intervention than the Military Sieve, at the cost of more over-triage.
- **Numbers used.** E-07.
- **What it cannot support here.** Generalisation: one site, seven months, 357 patients, 60% Priority One.
- **Access.** <https://militaryhealth.bmj.com/node/152737>

### vassallo2017d — MPTT-24

- **Citation.** Vassallo J, Smith JE, Wallis LA. Major incident triage and the implementation of a new triage tool, the MPTT-24. *Journal of the Royal Army Medical Corps* 2017. doi:10.1136/jramc-2017-000819
- **What it shows.** Three pragmatic changes make the rule faster to use and usable by less experienced staff, with a small loss of sensitivity.
- **Numbers used.** E-08 to E-12.
- **What it cannot support here.** Pre-hospital performance (E-11). The flowchart itself was not read.
- **Access.** Open access, CC BY 4.0: <https://militaryhealth.bmj.com/content/jramc/early/2017/12/04/jramc-2017-000819.full.pdf>

### netherton2019 — eFAST meta-analysis

- **Citation.** Netherton S, Milenkovic V, Taylor M, Davis PJ. Diagnostic accuracy of eFAST in the trauma patient: a systematic review and meta-analysis. *CJEM* 2019;21(6):727–738.
- **What it shows.** The scan is highly specific and only moderately sensitive, so a positive result rules in and a negative result does not rule out.
- **Numbers used.** E-14, E-15.
- **What it cannot support here.** Pre-hospital or austere use; the pooled studies are largely in-hospital. The pericardial figure comes from penetrating trauma only and should not be applied to blast or blunt injury.
- **Access.** doi:10.1017/cem.2019.381. Full text read 12 November 2026.

### partyka2022 — Pre-hospital eFAST

- **Citation.** Partyka C, Coggins A, Bliss J, Burns B, Fiorentino M, Goorkiz P, Miller M. A multicenter evaluation of the accuracy of prehospital eFAST by a physician-staffed helicopter emergency medical service. *Emergency Radiology* 2022;29(2):299–306.
- **What it shows.** Scanning before hospital keeps its specificity and loses most of its sensitivity.
- **Numbers used.** E-16.
- **What it cannot support here.** Military pre-hospital use: physicians on a civilian helicopter service, and fewer than half the scanned patients had hospital data for comparison. Almost all were blunt trauma. A third of abdominal scans were indeterminate, and the paper does not make clear how those enter the two-by-two table, so the 25% should be read as the sensitivity of a scan called positive, not of the examination as attempted.
- **Access.** doi:10.1007/s10140-021-02002-4. Full text read 12 November 2026.

### efast2025 — Pre-hospital eFAST, multicentre cohort

- **Citation.** Diagnostic performance of prehospital EFAST in predicting CT scan injuries in severe trauma patients: a multicenter cohort study. *European Journal of Trauma and Emergency Surgery* 2025;51(1):4. doi:10.1007/s00068-024-02693-7
- **What it shows.** The same pattern as `partyka2022`, in severe blunt trauma against CT.
- **Numbers used.** E-17.
- **What it cannot support here.** Read from a secondary summary only.
- **Access.** <https://journalfeed.org/article-a-day/2025/how-accurate-is-a-pre-hospital-fast-exam/>

### crash2_2010 — CRASH-2

- **Citation.** CRASH-2 trial collaborators. Effects of tranexamic acid on death, vascular occlusive events, and blood transfusion in trauma patients with significant haemorrhage (CRASH-2): a randomised, placebo-controlled trial. *Lancet* 2010;376:23–32.
- **What it shows.** Tranexamic acid given within 8 hours reduces death from any cause and from bleeding.
- **Numbers used.** E-19 to E-21.
- **What it cannot support here.** Military casualties specifically: the population is civilian and largely from low- and middle-income settings.
- **Access.** Data through freeBIRD after registration: <https://freebird.lshtm.ac.uk/>. Paper: <https://researchonline.lshtm.ac.uk/3305>

### crash2_2011 — CRASH-2, time to treatment

- **Citation.** CRASH-2 collaborators. The importance of early treatment with tranexamic acid in bleeding trauma patients: an exploratory analysis of the CRASH-2 randomised controlled trial. *Lancet* 2011;377:1096–1101. doi:10.1016/S0140-6736(11)60278-X
- **What it shows.** The benefit is concentrated in the first three hours; later treatment was associated with more bleeding deaths.
- **Numbers used.** E-22, E-23.
- **What it cannot support here.** A confirmatory claim. It is an exploratory subgroup analysis, which is itself a teaching point.
- **Access.** CC BY-NC-ND 3.0: <https://researchonline.lshtm.ac.uk/id/eprint/1035>

### gayetageron2018 — Delay and antifibrinolytics

- **Citation.** Gayet-Ageron A, Prieto-Merino D, Ker K, Shakur H, Ageron FX, Roberts I. Effect of treatment delay on the effectiveness and safety of antifibrinolytics in acute severe haemorrhage: a meta-analysis of individual patient-level data from 40 138 bleeding patients. *Lancet* 2018;391:125–132. doi:10.1016/S0140-6736(17)32455-8
- **What it shows.** Each quarter-hour of delay costs about a tenth of the survival benefit.
- **Numbers used.** E-24 to E-26.
- **What it cannot support here.** A trauma-only decay curve. Half the data are obstetric.
- **Access.** Open access: <https://pmc.ncbi.nlm.nih.gov/articles/PMC5773762>

### crash3_2019 — CRASH-3

- **Citation.** CRASH-3 trial collaborators. Effects of tranexamic acid on death, disability, vascular occlusive events and other morbidities in patients with acute traumatic brain injury (CRASH-3): a randomised, placebo-controlled trial. *Lancet* 2019;394:1713–1723. doi:10.1016/S0140-6736(19)32233-0
- **What it shows.** A small reduction in head injury death whose confidence interval includes no effect, with a larger apparent effect in mild to moderate injury.
- **Numbers used.** E-27 to E-29.
- **What it cannot support here.** A firm subgroup claim. The contrast between the primary result and the subgroup is the material for the Bayesian lens.
- **Access.** Data through freeBIRD. Paper: <https://researchonline.lshtm.ac.uk/id/eprint/4663114>

### ageron2019 — Prognostic model for bleeding death

- **Citation.** Ageron FX, Gayet-Ageron A, Steyerberg E, Bouzat P, Roberts I. Prognostic model for traumatic death due to bleeding: cross-sectional international study. *BMJ Open* 2019;9:e026823.
- **What it shows.** Three bedside variables predict death from bleeding nearly as well as six.
- **Numbers used.** E-30.
- **What it cannot support here.** Not re-read in this check.
- **Access.** Open access journal.

### nunez2009 — ABC score

- **Citation.** Nunez TC, Voskresensky IV, Dossett LA, Shinall R, Dutton WD, Cotton BA. Early prediction of massive transfusion in trauma: simple as ABC (assessment of blood consumption)? *Journal of Trauma* 2009;66(2):346–352.
- **What it shows.** A four-item bedside count predicts massive transfusion as well as scores that need laboratory results.
- **Numbers used.** E-31.
- **What it cannot support here.** The definition of massive transfusion was not on the page read.
- **Access.** <https://www.qxmd.com/r/19204506>

### kragh2009 — Tourniquets

- **Citation.** Kragh JF, Walters TJ, Baer DG, and colleagues. Survival with emergency tourniquet use to stop bleeding in major limb trauma. *Annals of Surgery* 2009;249(1):1–7.
- **What it shows.** Survival was far higher when a tourniquet went on before shock, and higher when applied before hospital.
- **Numbers used.** E-32.
- **What it cannot support here.** A causal estimate. The study is observational, and casualties who received a tourniquet late differ from those who received one early.
- **Access.** <https://read.qxmd.com/read/19106667/>

### mod2016 — UK official statistic

- **Citation.** Ministry of Defence. Types of injuries sustained by UK Service personnel on Operation HERRICK in Afghanistan, 1 April 2006 to 30 November 2014. Official Statistic, 23 February 2016.
- **What it shows.** Disease was the largest single reason for admission, and injuries were split about evenly between battle and non-battle.
- **Numbers used.** E-34 to E-38.
- **What it cannot support here.** Counts are admissions only; injury types exist only for trauma team patients; mechanism is limited to four categories.
- **Access.** Open Government Licence: <https://assets.publishing.service.gov.uk/media/5a80e0eaed915d74e6230f79/20160223_Afghanistan_Types_of_Injuries_Official_Statistic_Final_OS.pdf>

### eastridge2012 — Death on the battlefield

- **Citation.** Eastridge BJ, Mabry RL, Seguin P, and colleagues. Death on the battlefield (2001–2011): implications for the future of combat casualty care. *Journal of Trauma and Acute Care Surgery* 2012;73(6 Suppl 5):S431–S437. doi:10.1097/TA.0b013e3182755dcc
- **What it shows.** Most deaths occur before any treatment facility; of those judged potentially survivable, nine in ten were from bleeding, mostly in the trunk.
- **Numbers used.** E-39 to E-41.
- **What it cannot support here.** UK figures; airway and tension pneumothorax shares were not in the abstract.
- **Access.** <https://scholar.usuhs.edu/en/publications/death-on-the-battlefield-2001-2011-implications-for-the-future-of/>

### ajp410 — Allied Joint Doctrine for Medical Support

- **Citation.** NATO Standardization Office. AJP-4.10, Allied Joint Doctrine for Medical Support, Edition C Version 1, September 2019.
- **What it shows.** The planning timelines and the roles of care that give the knowledge graph its echelon nodes.
- **Numbers used.** E-42 to E-44.
- **What it cannot support here.** Formal definitions of damage control resuscitation and surgery were not in the sections read. Currency of the edition is unchecked.
- **Access.** <https://coemed.org/files/stanags/01_AJP/AJP-4.10_EDC_V1_E_2228.pdf>

### singer2016 — Sepsis-3

- **Citation.** Singer M, Deutschman CS, Seymour CW, and colleagues. The Third International Consensus Definitions for Sepsis and Septic Shock (Sepsis-3). *JAMA* 2016;315(8):801–810. doi:10.1001/jama.2016.0287
- **What it shows.** The definition the sepsis datasets are labelled against, and a three-item bedside screen.
- **Numbers used.** E-45 to E-47.
- **Access.** <https://research.monash.edu/en/publications/the-third-international-consensus-definitions-for-sepsis-and-sept/>

### jeter2019 — Critique of sepsis reinforcement learning

- **Citation.** Jeter R, Josef C, Shashikumar S, Nemati S. Does the "Artificial Intelligence Clinician" learn optimal treatment strategies for sepsis in intensive care? arXiv:1902.03271, 2019.
- **What it shows.** How a learned treatment policy can appear to beat clinicians because of the way it is scored, not because of what it does.
- **Numbers used.** E-50. The criticised model used 750 states, 25 actions and four-hour steps.
- **What it cannot support here.** The original paper (Komorowski and colleagues, *Nature Medicine* 2018) was not read; this is one side of the exchange.
- **Access.** Open: <https://arxiv.org/pdf/1902.03271>

### pauker1980, norman2009, croskerry2009 — Decision thresholds and dual process

- **Citations.** Pauker SG, Kassirer JP. The threshold approach to clinical decision making. *NEJM* 1980;302:1109–1117. Norman G. Dual processing and diagnostic errors. *Advances in Health Sciences Education* 2009;14(Suppl 1):37–49. Croskerry P. A universal model of diagnostic reasoning. *Academic Medicine* 2009;84(8):1022–1028.
- **What they show.** E-52, E-53.
- **What they cannot support here.** The threshold formulae and Croskerry's model were not read at source.
- **Access.** <https://scilit.com/publications/43c9d22464854fe6cdbeaed332bdb64f>, <https://experts.mcmaster.ca/display/publication840849>

### rao1999, schultz1997, kumaran2016, lillicrap2020 — Brain analogies

- **Citations.** Rao RPN, Ballard DH. Predictive coding in the visual cortex. *Nature Neuroscience* 1999;2:79–87. Schultz W, Dayan P, Montague PR. A neural substrate of prediction and reward. *Science* 1997;275:1593–1599. Kumaran D, Hassabis D, McClelland JL. What learning systems do intelligent agents need? *Trends in Cognitive Sciences* 2016;20:512–534. Lillicrap TP, Santoro A, Marris L, Akerman CJ, Hinton G. Backpropagation and the brain. *Nature Reviews Neuroscience* 2020;21:335–346.
- **What they show.** E-55 to E-58.
- **What they cannot support here.** Each is a model of one brain system. None licenses the statement that a clinical algorithm "works like the brain".
- **Access.** Kumaran preprint open: <https://web.stanford.edu/~jlmcc/papers/KumaranHassabisMcClelland16FinalMS.pdf>

### green1997, luan2011, caruana2015 — Trees and intelligible models

- **Citations.** Green L, Mehr DR. What alters physicians' decisions to admit to the coronary care unit? *Journal of Family Practice* 1997;45(3):219–226. Luan S, Schooler LJ, Gigerenzer G. A signal-detection analysis of fast-and-frugal trees. *Psychological Review* 2011;118(2):316–338. Caruana R, Lou Y, Gehrke J, Koch P, Sturm M, Elhadad N. Intelligible models for healthcare. *KDD* 2015:1721–1730.
- **What they show.** E-59, E-60.
- **What they cannot support here.** The two tree papers were read through a secondary summary; the bibliographic details for `luan2011` need confirming.
- **Access.** Caruana open: <https://people.dbmi.columbia.edu/noemie/papers/15kdd.pdf>

### Teaching sources

- **Citations.** Malan DJ. Reinventing CS50. *Proceedings of the 41st ACM Technical Symposium on Computer Science Education* 2010:152–156. doi:10.1145/1734263.1734316. Malan DJ. Teaching statement, undated. Sentance S, Waite J, Kallia M. Teaching computer programming with PRIMM: a sociocultural perspective. *Computer Science Education* 2019. Garcia-Retamero R, Cokely ET, Hoffrage U. Visual aids improve diagnostic inferences and metacognitive judgment calibration. *Frontiers in Psychology* 2015;6:932. Fyfe ER, McNeil NM, Son JY, Goldstone RL. Concreteness fading in mathematics and science instruction: a systematic review. *Educational Psychology Review* 2014;26:9–25. Mayer RE. *Multimedia Learning*, 2nd edition, Cambridge University Press, 2009. Hannah Fry: interview in *Chalkdust*, 24 March 2015; *Plus* podcast, 17 March 2025; International Mathematical Union article on the 2026 Leelavati Prize.
- **What they show.** E-61 to E-69.
- **What they cannot support here.** No source read shows that an interactive control teaches better than a static figure, or that demonstrating a failure improves learning. The grid result is from patients, not clinicians or students. PRIMM and Mayer were read through summaries, and the concreteness fading review only as its abstract. The Fry sources are interviews and a prize citation, which describe her practice and are not studies of its effect.
- **Access.** <https://core.ac.uk/download/28933023.pdf>, <https://cs.harvard.edu/malan/statements/teaching.pdf>, <https://www.frontiersin.org/articles/10.3389/fpsyg.2015.00932/full>, <https://www.doi.org/10.1007/S10648-014-9249-3>, <https://chalkdustmagazine.com/interviews/in-conversation-with-dr-hannah-fry/>, <https://www.mathunion.org/fileadmin/documents/2026-07/article-leelavati-final.pdf>, <https://plus.maths.org/content/living-proof-communicating-mathematics-hannah-fry>

### gelman2026 — Random variables as objects

- **Citation.** Gelman A. The challenge of truly probabilistic programming. *Statistical Modeling, Causal Inference, and Social Science*, 11 November 2026.
- **What it shows.** A way of programming with uncertainty in which the uncertain quantity, not an array of draws, is what the code handles.
- **Numbers used.** None. The figures in the explainer are computed here from E-14, E-16 and E-22.
- **What it cannot support here.** Any clinical claim. It is an opinion piece. It names no general Python equivalent; a comment mentions `gvar`, described as Gaussian only.
- **Access.** <https://statmodeling.stat.columbia.edu/2026/11/11/the-challenge-of-truly-probabilistic-programming/>

### Dataset sources

`reyna2020` (PhysioNet 2019), `choudhary2024` (ICU-Sepsis), `fansitchango2022` (DDXPlus), `yang2023` (MedMNIST v2), ASIA and ALARM (bnlearn repository), and OpenPOCUS were checked for access on 9 November 2026 and are recorded in `library/curated.yaml`. None was re-read in this check.

---

## Part C — Open items for a person

| # | Item | Why it matters |
|---|---|---|
| O-1 | Closed 12 November 2026: Figure 2 read from the version of record; step order and thresholds recorded in E-08. Heart rate comparison is 'below 100' for Priority 2 | One point for the builder: the text and the figure differ for a casualty who responds only to voice (E-08). Code the figure as published and expose the alternative as a switch |
| O-2 | Read the freeBIRD data sharing terms before any CRASH-2 or CRASH-3 file enters a notebook | Redistribution and acknowledgement terms were not on the page read |
| O-3 | Confirm AJP-4.10 Edition C is current | Timelines and roles are cited to it |
| O-4 | Closed 12 November 2026: `vassallo2017c` is Vassallo, Horne, Smith, Wallis, J R Army Med Corps 2017;163(6):383-387, doi:10.1136/jramc-2017-000771 | — |
| O-5 | Closed 12 November 2026: the oddities are in the version of record. Table 2 gives a positive predictive value of 61.1% with an interval of 65.2 to 71.2, and three odds ratios whose intervals are implausibly placed. None affects the sensitivity and specificity used here | Do not quote the odds ratios or that interval |
| O-6 | Re-read the CARRIED entries. Closed 12 November 2026 except E-17: E-14 to E-16, E-30, E-48, E-49 and E-51 read in full and confirmed | E-17 (prehospital eFAST against CT) is still read from a summary only |
| O-7 | Check volume and page numbers for `crash2_2010`, `ageron2019`, `nunez2009`, `kragh2009`, `croskerry2009`, `lillicrap2020`, `luan2011` | Completed from general knowledge, not from the page read |
| O-8 | Complete author lists marked "to complete" and check the surnames given for E-73, E-79, E-85, E-87, E-88, E-94 to E-96, E-104, E-105, E-108, E-109, E-111 | The abstract services returned titles and DOIs; several author names are from general knowledge |
| O-9 | Closed 12 November 2026: E-76, E-79, E-81 and the 2022 RePHILL report read in full and confirmed | — |
