# inference-labs — Design

**Status:** design complete; requirements in `PRD.md` · **Date:** 12 November 2026 · **Author:** Ross Taylor

inference-labs is a learning repository: its aim is to learn inference through useful examples. This document fixes what it is, what each lens does, where every clinical number comes from, and what the evidence check changed. The PRD turns it into numbered requirements and gates. Evidence ids (E-nn) and open items (O-n) refer to [`EVIDENCE.md`](EVIDENCE.md).

---

## 1. Purpose

**Plain.** One casualty is followed from the point of injury to the surgeon. At each step ten different ways of reasoning are asked the same two questions: what is wrong, and what should be done. The repository shows where they agree, where they differ, and how they fit together.

**Developer.** A Python library (`inference_labs`) holds a seeded casualty generator, ten lens modules behind one interface, and a small knowledge graph. Twelve notebooks teach the lenses one at a time. A Streamlit app runs them together on the same casualty. A manifest generates the scaffold and a validator gates every slice.

**Technical.** Each lens is treated as an inference procedure with stated inputs, assumptions and a characteristic failure. Diagnosis is framed as abduction: inference to the best explanation of the findings. Lenses are compared on a common scorecard and against a common rule-based baseline, on synthetic data with known generating structure (mechanism) and on open trial and registry data (evidence), with the two kept labelled apart.

---

## 2. Decisions

| # | Decision | Reason |
|---|---|---|
| D-1 | The repository is `inference-labs`; the package is `inference_labs` | Only three of the ten lenses are machine learning. Inference is what all ten do |
| D-2 | Ten lenses, capped | Rules, frequentist and signal detection, Bayesian, decision trees, stochastic processes, connectionist, causal, knowledge graph, reinforcement learning, decision theory |
| D-3 | Every lens has one diagnosis case and one treatment case, with native or weak fit recorded | Lenses have a natural job. Recording the weak fits is part of the comparison |
| D-4 | One casualty thread: point of injury, pre-hospital emergency care, Role 2 | Gives the comparison a single spine. Echelons and timelines from E-42, E-43 |
| D-5 | Four patient types: haemorrhage, chest injury, head injury, disease and non-battle injury | See section 3. Haemorrhage now carries three sites (D-12) |
| D-6 | The generator is a known causal graph with casualty mix and care setting as parameters | One generator gives ground truth to five lenses and makes the prior a control the reader can move |
| D-7 | Real data in notebooks only; the app runs on synthetic data only | CRASH-2 and CRASH-3 need registration (O-2). The app must run for anyone |
| D-8 | Every result is labelled **mechanism** (synthetic) or **evidence** (real data) | Synthetic data can only confirm the model that produced it |
| D-9 | The rule a medic would use is the baseline for every lens | Borrowed from the clinician baseline in ml-algorithms-labs. Here it is the MPTT-24 |
| D-10 | A hand-built graph of about fifty nodes, in the same in-process store and key conventions as MYRDDIN, with no import | Teaches the idea; keeps the projects separate; keeps a later join cheap |
| D-11 | Hybrids (retrieval-augmented generation, graph learning) are described, not built; conformal prediction is built | The first two belong to POLYBIUS and ARIADNE. Conformal prediction is cheap and fits triage |
| D-12 | Haemorrhage is split into extremity, junctional and truncal | Forced by the evidence: see C-4 in section 8 |
| D-13 | Triage and scan accuracy are never single numbers; they are tables keyed by cohort and setting | Forced by the evidence: see C-1 and C-2 |
| D-14 | Notebooks may hold teaching code; the app may hold none | In a teaching notebook the code is the lesson. Any number the app shows comes from the library, tied by a parity test |
| D-15 | Harness carried from ml-algorithms-labs: manifest, computed verdict, gates proven on planted defects, builder and sceptic only, ledger | Section 9 |
| D-16 | Full scope is kept: ten lenses, two cases each, the graph and the app. The aim is to learn inference through useful examples | Ruled 9 November 2026 after a scope review that proposed starting with three lenses. Breadth of worked examples is the point; the build order in section 10 still delivers one lens at a time |
| D-17 | A single belief carries through the pathway. The posterior is the casualty's running state: set by the mix, updated by triage and by the scan, moved forward in time, then used by the treatment and evacuation steps | It is what joins the lenses. Each lens still gives its own answer in its own terms beside it, so the page shows comparison and integration together. Section 7 and section 12.4 |
| D-18 | Every lens opens with a plain general explainer of the idea before any clinical case, and is taught through many visuals, in three registers | Section 12. The explainer makes each notebook usable by someone who has never met the method |
| D-19 | The belief is carried as a random variable: an array of draws with ordinary arithmetic defined on it, summarised only at the end of the pathway | The scan's accuracy is known only as an interval, so the belief is too. A point of 61% hides a 9% chance of being below one half. Idea from E-70; worked in `docs/explainers/belief-as-a-random-variable.md` |
| D-20 | Every lens has a background file in `docs/background/` that the builder reads before writing the notebook. It fixes the hook, the by-hand case, the two worked cases and the failure against published findings, and lists what must not be claimed | Synthetic data show a mechanism; real findings are what the mechanism is checked against. Section 13 |

---

## 3. Patient types and mix

The mix is a parameter of the generator. Its default comes from the one open UK source found (E-34 to E-38); every other mix is the reader's assumption and is labelled so.

| Stream | Share of UK field hospital admissions, Afghanistan 2006–2014 | Source |
|---|---|---|
| Disease (natural causes) | About 44% | E-34 |
| Battle injury | About 30% | E-36, derived |
| Non-battle injury | About 27% | E-36, derived |

Two facts from the same evidence shape the design.

- **The disease stream is the largest.** A trauma-only repository would describe under a third of admissions. The fourth patient type therefore carries real weight, and the 10-minute and 1-hour timelines apply to it as well as to trauma (E-42).
- **What is common is not what kills.** Extremities account for about 44% of injuries in trauma team patients and the torso for about 7% (E-38). Yet among potentially survivable battlefield deaths, nine in ten were from bleeding, and two thirds of that bleeding was truncal (E-40, E-41). The decision theory lens is built on this gap between frequency and consequence.

| Patient type | Diagnosis question | Treatment question | Real data |
|---|---|---|---|
| Haemorrhage (extremity, junctional, truncal) | Is this casualty bleeding to death, and from where? | Tourniquet, tranexamic acid, blood, surgery: which, and how soon? | CRASH-2 |
| Chest injury | Is there a pneumothorax? | Decompress here or move? | None open; published accuracy only |
| Head injury | How severe, and is there bleeding inside the skull? | Does tranexamic acid help this patient? | CRASH-3 |
| Disease and non-battle injury | Is this sepsis? What is the differential? | Fluids and vasopressors over time | PhysioNet 2019, ICU-Sepsis, DDXPlus |

---

## 4. The ten lenses

Each lens module exposes the same three calls: `diagnose(casualty)`, `treat(casualty)` and `scorecard()`. Each notebook follows the same seven-part pattern, set out in section 12.2: hook, general explainer, by hand, the two worked cases, the failure, the scorecard, and the brain analogy with where it breaks.

### 4.1 Cases and data

| # | Lens | Diagnosis case | Treatment case | Data | Fit |
|---|---|---|---|---|---|
| 01 | Rules | MPTT-24 priority | ABC score of 2 or more activates transfusion (E-31); tourniquet for extremity bleeding | Synthetic | Both |
| 02 | Frequentist and signal detection | Triage and scan accuracy as hits and false alarms across cohorts (E-03 to E-17) | Reading the CRASH-2 result: 14.5% against 16.0% (E-20) | Published figures; CRASH-2 | Diagnosis |
| 03 | Bayesian | Probability of abdominal bleeding after a scan, in hospital and before it (E-14, E-16). Warm-up on the ASIA network | Belief in tranexamic acid for head injury: CRASH-2 as prior, CRASH-3 as evidence (E-27, E-28) | Synthetic; CRASH-3 | Diagnosis |
| 04 | Decision trees | Risk of death from bleeding from age, pressure and GCS (E-30); a differential on DDXPlus | Who gets blood first | CRASH-2; DDXPlus | Both |
| 05 | Stochastic processes | Deterioration over the evacuation timeline as a Markov chain | Benefit of treatment decaying with delay (E-22, E-24) | Synthetic | Treatment |
| 06 | Connectionist | Ultrasound image classification on a proxy set | Predicting need for intervention from vital signs | BreastMNIST; synthetic | Diagnosis; treatment weak |
| 07 | Causal | Who gets scanned, and why that biases accuracy | Effect of tranexamic acid from a randomised trial, then the same question asked of observational tourniquet data (E-32) | CRASH-2 | Treatment; diagnosis weak |
| 08 | Knowledge graph | Findings to injury | Injury to intervention to competency to echelon (E-43) | Hand-built | Both |
| 09 | Reinforcement learning | Which test next | Sequential resuscitation | ICU-Sepsis | Treatment; diagnosis weak |
| 10 | Decision theory | Where to set the triage threshold given unequal costs | Treat here or evacuate; allocating scarce blood. Worked example: the PhysioNet utility score (E-48) | Synthetic; PhysioNet 2019 | Treatment |
| 11 | Hybrids and brain analogies | Conformal prediction on triage; summary of the analogies and their limits | — | Synthetic | — |

Notebook 00 frames the whole: abduction, the casualty thread, and the four questions the lenses divide between them (what is uncertainty, how does the world behave, where does knowledge live, what is being claimed).

### 4.2 Characteristic failure and brain analogy

| Lens | Failure demonstrated | Brain analogy | Where the analogy breaks |
|---|---|---|---|
| Rules | Brittleness: the same rule loses twelve points of sensitivity on a civilian cohort (E-03, E-05) | Deliberate, explicit reasoning | People do not apply rules without context |
| Frequentist | A single accuracy figure quoted for the wrong setting (E-13) | Signal detection as a model of perception | It models a decision criterion, not how the brain sets one |
| Bayesian | Base-rate neglect; a prior borrowed from the wrong population | Predictive coding: predictions flow down, errors flow up (E-55) | It is a model of visual cortex, not evidence the brain computes posteriors |
| Decision trees | Instability: a small change in data gives a different tree | Fast-and-frugal trees, a few cues checked in order (E-59) | Loose; a description of some decisions, not a mechanism |
| Stochastic | A memoryless model applied to a process with memory | Neural noise and sampling | Suggestive only |
| Connectionist | Shortcut learning; a proxy dataset read as the real task | Layered cortex; feedback approximating error signals (E-58) | Backpropagation has no agreed biological form |
| Causal | Confounding by indication: asthma appearing to protect against pneumonia death (E-60) | Internal models for "what if I act" | No specific neural account is claimed |
| Knowledge graph | An edge missing or out of date gives a confident wrong answer | Schema and semantic memory | Human association is graded and context-bound |
| Reinforcement learning | A policy that looks good because of how it is scored: withholding treatment rated above clinicians (E-50) | Dopamine as reward prediction error (E-56) | The abstract read supports prediction error, not a full learning algorithm |
| Decision theory | Optimising the measurable cost and ignoring the unmeasured one | Value-based choice | Stated utilities are not how people choose |

Two cross-cutting analogies sit in notebook 11. Complementary learning systems (E-57) is the analogy for retrieval joined to a learned model: a fast store of specific cases beside a slow learner of structure. Dual process is the analogy for rules beside pattern recognition, with one correction from the evidence: the fast mode is not the faulty one (C-8).

---

## 5. The generator

A directed acyclic graph, sampled forward with a fixed seed. `return_truth=True` returns the latent nodes.

```
mix ──> stream ──> mechanism ──> injury site ──> bleeding ──┬──> physiology ──> MPTT-24 priority
                                                           ├──> scan result  <── setting
                                                           └──> outcome      <── treatment, delay
setting ──> scan accuracy, time to each echelon
```

| Parameter | Default | Source | Label |
|---|---|---|---|
| Stream shares | 44 / 30 / 27 (disease, battle, non-battle; rounded, and the source rows do not sum exactly) | E-34 to E-36 | Evidence, one theatre |
| Battle mechanism | Explosion 1,164 : small arms 974 : other 133 | E-35 | Evidence, one theatre |
| Site of lethal haemorrhage | Truncal 67.3 : junctional 19.2 : extremity 13.5 | E-41 | Evidence, US deaths; applies to fatal bleeding only |
| Scan accuracy, in hospital | Free fluid 74 / 98; pneumothorax 69 / 99 | E-14 | Evidence, provisional (O-6) |
| Scan accuracy, pre-hospital | Free fluid 25 / 96; pneumothorax 38 / 96 | E-16 | Evidence, civilian helicopter service |
| Treatment effect on bleeding death | Relative risk 0.68 within 1 hour, 0.79 at 1 to 3 hours, 1.44 after 3 hours | E-22 | Evidence, exploratory analysis |
| Decay of benefit | About 10% per 15 minutes; none after about 3 hours | E-24 | Evidence, half obstetric (E-26) |
| Physiology given bleeding | Chosen so the MPTT-24 reproduces a stated sensitivity and specificity for the selected cohort | E-09 | Assumption, calibrated to evidence |
| Every other number | — | — | Assumption |

Every row becomes a node in the provenance graph (section 6), and the assumptions register is generated from that graph in the same seven-column format ml-algorithms-labs uses.

The generator is slice 0 and is frozen once the first lens is built. A change after that is a manifest version bump.

---

## 6. The knowledge graph

One graph, three jobs.

| Job | Nodes | Edges |
|---|---|---|
| Capability chain | Finding, injury, intervention, competency, role, echelon | *suggests*, *treated by*, *requires*, *held by*, *available at* |
| Provenance | Parameter, source, notebook | *taken from*, *used in* |
| Rules as graph | Threshold, observation, priority | *tests*, *assigns* |

- **Echelons** are Role 1, Role 2 forward, basic and enhanced, Role 3 and Role 4 (E-43). The 10-minute, 1-hour and 2-hour timelines are properties on the edges between them (E-42).
- **Epistemic label on every edge:** doctrine, trial evidence, registry evidence, or assumption.
- **What the graph is for.** The other lenses say what is likely. The graph says what is possible at this node, and where the nearest place is that can do more. It bounds the actions open to the decision theory and reinforcement learning lenses.
- **One edge, three readings.** The same edge from mechanism to injury site is read as "can cause" by the graph, "how probable" by the Bayesian network, and "what changes if I intervene" by the causal diagram.

---

## 7. The app

| Page | Content |
|---|---|
| 1. Casualty walk-through | Choose a patient type and setting. Step through triage, scan, risk, treatment and evacuation, with each lens's answer beside the baseline |
| 2. Mix and setting | Move the casualty mix and the echelon; every lens's answer updates |
| 3. Lens table | The comparison, generated from the scorecards, with a diagnosis and treatment toggle |
| 4. Graph explorer | The capability chain, the provenance of every number, and one edge read three ways |

A belief line runs across the five steps of page 1 (D-17): the probability that this casualty is bleeding, shown at the start, after triage and after the scan, and then marked where the treatment and evacuation steps consume it. Two lens pages sit behind the four main ones: an explainer page per lens, built from the notebook's general explainer and central visual, and a gallery of the visuals.

The integration the design promised lives on page 1: the positive scan from the Bayesian lens is one of the four items the transfusion rule counts (E-31), the risk estimate feeds the treatment decision, and the delay clock from the stochastic lens sets how much benefit is left.

---

## 8. What the evidence check changed

| # | Finding | Consequence |
|---|---|---|
| C-1 | The figure quoted earlier for the MPTT (83.6% and 51.0%) is one prospective cohort of 357. Across cohorts and versions, sensitivity runs from 53.5% to 83.6% (E-13) | D-13. Accuracy is a table keyed by cohort. Quoting one figure is a sceptic finding |
| C-2 | The source defines over-triage as 1 − positive predictive value, not 1 − specificity (E-12). On that definition civilian over-triage is 66% | The scorecard states which definition it uses. The frequentist notebook teaches the difference |
| C-3 | The MPTT was validated on first hospital observations, not pre-hospital ones (E-11) | Every triage result carries that caveat in its evidence label |
| C-4 | Extremity injuries are the most common; truncal bleeding is the most lethal (E-38, E-41) | D-12. Haemorrhage has three sites, and tourniquets enter as a treatment |
| C-5 | Disease is about 44% of admissions (E-34) | The fourth patient type is the largest stream, not an afterthought |
| C-6 | The transfusion rule counts a positive scan (E-31) | A real link between two lenses, used on app page 1 |
| C-7 | The time-to-treatment result is exploratory, and the decay estimate is half obstetric (E-23, E-26) | The stochastic and causal notebooks say so, and use the pair as a lesson in how far a subgroup finding carries |
| C-8 | A review of dual process reasoning finds the fast mode no more error-prone than the slow one (E-53) | The brain analogy text is rewritten. Pattern recognition is not cast as the source of error |
| C-9 | The CRASH-3 primary confidence interval includes no effect, while one subgroup looks clearly positive (E-27, E-28) | This is the Bayesian treatment case as planned, and it now has its numbers. No published Bayesian reanalysis was confirmed (E-33), so the notebook's analysis is its own and is labelled as such |
| C-10 | The best-known clinical reinforcement learning result has a published critique: the scoring method can reward withholding treatment (E-50) | This becomes the failure demonstration for lens 09 |
| C-11 | Tourniquet survival data are observational and strongly confounded (E-32) | The causal notebook sets them beside the randomised trial |
| C-12 | No open human FAST image set was found (E-18) | Lens 06 teaches the method on a proxy and says so in its title cell |

---

## 9. Harness

Carried from ml-algorithms-labs without change: the manifest as the single source of truth, a validator that computes BUILT, REVISE or BLOCKED, a test that plants one defect per gate, a builder and a sceptic in a fresh context and no other agent, a ledger in which a blocked attempt is committed like a built one, pre-registered experiments, and legal abstention.

Adapted:

| Labs practice | Here |
|---|---|
| Synthetic data only | Two bars: mechanism and evidence (D-8) |
| Unit of work is a notebook | Unit of work is a lens: library module, notebook, scorecard, app panel |
| Sceptic's epistemic checks | Four replaced: accuracy quoted for the wrong cohort or setting; proxy data read as the real thing; civilian data read as military; a diagnosis result read as a treatment result |
| Three configurations | One: the agent loop. No headless tier, parallel seats or nightly run |
| Gate tally typed by the agent | Written by the validator. The labs ledger holds a row reading "13/11 pass" |

The gates bound what may be claimed as built. They do not generate work.

---

## 10. Build order

| Slice | Content | Done when |
|---|---|---|
| 0 | Manifest, validator with planted-defect tests, generator, graph skeleton, provenance, fixtures for the real datasets | The generator reproduces its parameters within tolerance and every gate fails on its defect |
| 1 | Lens 03 (Bayesian), notebook, scorecard, app page 1 with one panel | The thinnest slice proves library, notebook and app together |
| 2–10 | One lens each, in the order 01, 02, 04, 10, 05, 07, 08, 09, 06 | Each adds its panel to page 1 |
| 11 | Notebook 00 and notebook 11; app pages 2 to 4 | At least five lenses exist |

Rules come second because every later lens is compared against them (D-9).

---

## 11. Open items

Carried from `EVIDENCE.md` Part C. None blocks the PRD. O-1, O-2, O-3 and O-6 each block the slice named beside them.

| # | Item | Blocks |
|---|---|---|
| O-1 | Confirm the MPTT-24 flowchart steps and heart rate comparison from the figure | Slice 2 (rules) |
| O-2 | Read the freeBIRD data sharing terms | Any notebook using CRASH-2 or CRASH-3 |
| O-3 | Confirm the current edition of AJP-4.10 | Slice 8 (knowledge graph) |
| O-4, O-5, O-7 | Citation and table checks | Nothing; tidy before publication |
| O-6 | Re-read the provisional entries, the eFAST sources above all | Slice 1 (Bayesian) |

---

## 12. Teaching design

### 12.1 Principles

Each principle is tied to a source read on 9 November 2026 (evidence ids E-61 to E-69), or marked as a design choice where none was found.

| # | Principle | In practice | Grounding |
|---|---|---|---|
| T-1 | Earn attention before explaining | Every notebook opens on one concrete question with an answer that surprises | Fry builds a reason to care before the technical content, often with a demonstration (E-66) |
| T-2 | Predict, then reveal | The reader commits to a guess before the first result. The guess is not marked | The predict and run stages of PRIMM: low-stakes prediction before seeing the output (E-63) |
| T-3 | Count people, not probabilities | A hundred casualties drawn as a grid, before any notation | Natural frequencies improve diagnostic inference; adding a grid raised accuracy from 32% to 55% in one patient study, most for the least numerate (E-64) |
| T-4 | Concrete first, then fade to the abstract | Ten rows by hand, then plain Python, then the library, then the notation | Concreteness fading (E-65). CS50 starts in a block language before C (E-62). PRIMM has novices read and trace code before writing it (E-63) |
| T-5 | Demonstrate, do not only describe | A control the reader can drag; a result that moves | Fry's live demonstrations (E-66); CS50 has students act out sorting on stage (E-62). That an on-screen control teaches better than a static figure is a design choice, not something a source here shows |
| T-6 | Break it on purpose | The characteristic failure is produced, not described | Design choice, carried from the failure-modes gate in ml-algorithms-labs. No source found |
| T-7 | One room, several depths | Plain, developer and technical registers on the same idea, with the plain one written for someone new to the method | CS50 keeps beginners and the experienced in one course, with sections and problem-set variants by comfort level (E-61, E-62). Fry does not simplify the subject down (E-66) |
| T-8 | Fewer, relevant pictures, with one to remember | Every figure carries an argument; one is marked central; labels sit beside what they describe | Mayer's coherence, signalling and spatial contiguity principles (E-67) |
| T-9 | Familiar before clinical | The general explainer uses an everyday example; the casualty comes second | Fry anchors mathematics to what the audience already knows (E-68). Mayer's pre-training principle: key ideas before the main lesson (E-67) |
| T-10 | Problems from a real domain | The casualty thread, not toy data | CS50 problem sets are set in cryptography, forensics and finance (E-62) |
| T-11 | Say what the model is not | Mechanism and evidence labels; "where the analogy breaks" in every notebook | Fry: a model represents reality and is not reality, as a satnav estimate is useful without being exact (E-68) |
| T-12 | Accessible is not the same as easy | The technical register is never thinned to make the plain one easier | Malan: a first course should be within anyone's reach and still demanding (E-61) |
| T-13 | Done with the reader, not to them | Guess prompts, teach-back paragraphs, quizzes | Fry (E-69) |

**A tension to manage.** The brief asks for many creative visuals. Mayer's coherence principle says material that is not needed for the point makes learning worse, however attractive it is (E-67). The two are reconciled by a rule the sceptic already applies: every figure must change what the reader concludes, and a figure that only decorates is a finding. Creative means a memorable way of showing the idea, not an extra picture.

**What the check did not support.** T-6, and the claim inside T-5 that interactivity itself helps, rest on judgement. The grid evidence in T-3 is from patients given natural frequencies, not clinicians or students, and tested grids only.

### 12.2 The notebook pattern

| Part | Content | Principle |
|---|---|---|
| 1. Hook | The question, and a prompt to guess | T-1, T-2, T-13 |
| 2. General explainer | The idea in an everyday setting, in three registers, with the central visual | T-7, T-8, T-9, T-12 |
| 3. By hand | Ten casualties counted, then plain Python, then the library and the notation | T-3, T-4 |
| 4. The two cases | Diagnosis and treatment, on the casualty thread, against the baseline | T-5, T-10 |
| 5. The failure | The characteristic failure, produced deliberately | T-6 |
| 6. Scorecard | The seven axes, the fit, the evidence labels | T-11 |
| 7. Brain analogy | What it resembles, and where the resemblance stops | T-11 |

### 12.3 Explainers and visuals, lens by lens

The hook and the plain explainer are drafts for the builder to work from. The first visual in each row is the central figure.

| Lens | Hook | Plain explainer | Visuals |
|---|---|---|---|
| 00 Framing | A detective has five clues and three suspects. What is she actually doing? | Diagnosis is neither proof nor pattern-matching alone. It is choosing the story that best explains the clues, and staying ready to change it | **The evidence board**: clues pinned and strung to suspects, strings thickening as evidence arrives. The casualty's journey drawn as a route map. The four questions as a compass |
| 01 Rules | Can four yes-or-no questions sort a hundred casualties in a minute? | A rule is a decision someone made in advance so that nobody has to think under pressure. It is fast, the same every time, and blind to anything it was not written for | **The sieve**: casualties drop through a stack of gates and collect in three bins; drag a threshold and watch them re-sort. The flowchart as a pinball table. The same sieve fed a different crowd |
| 02 Frequentist and signal detection | The alarm went off. How often is it right? | Any test makes two kinds of mistake, and you cannot shrink one without growing the other. Where you set the line is a choice, not a fact | **Two hills and a sliding line**: overlapping distributions with a movable cut, the four outcomes shaded, the ROC curve drawing itself as you slide. A crowd of a hundred sorted into four pens. The same test in three rooms, as small multiples |
| 03 Bayesian | The scan is clear. Is she safe? | What you believe after a test depends on what you believed before it. A good test moves a belief; it does not replace one | **A hundred casualties**: an icon grid coloured by truth, then filtered by scan result, so the answer can be counted. The belief needle that swings with each finding. A see-saw for the likelihood ratio. The same grid redrawn for a different mix |
| 04 Decision trees | How would a machine play twenty questions? | A tree asks the single question that splits the crowd most cleanly, then asks again inside each half. It is a rule that the data wrote | **The carving**: a scatter of casualties cut into rectangles one split at a time. The tree growing as rows are added. A flickering forest: twenty trees from twenty resamples, to show how much they disagree |
| 05 Stochastic processes | Run the same hour a thousand times. How many ways does it end? | Some things cannot be predicted one at a time but are very predictable in bulk. You describe the dice, not the roll | **Many lives**: a hundred simulated trajectories fanning out from one starting point, with the share in each state stacked beneath. Dots flowing round a state diagram. The melting hour: treatment benefit as an ice block shrinking with the clock |
| 06 Connectionist | It gets the answer right. What was it looking at? | A network learns its own features from examples instead of being told them. That is its strength, and the reason it can be right for the wrong reason | **What it saw**: an image beside a heat map of where the network looked. Blur to sharp: what each layer responds to. The shortcut reveal: the same score from the label in the corner |
| 07 Causal | Asthma patients die less often of pneumonia. Should we be pleased? | Seeing that two things go together is not the same as knowing what happens if you change one. To learn that, you must intervene, or argue very carefully | **Cutting the arrow**: a diagram where scissors cut the line into treatment, and the downstream numbers change. Twin casualties, one treated and one not. Two jars filling by coin toss until they match. The paradox flip: a trend that reverses when the crowd is split |
| 08 Knowledge graph | What can be done for her here, and where is the nearest place that can do more? | Some knowledge is neither a rule nor a statistic. It is a map of what connects to what, kept by people, with a source for every line | **The map of care**: echelons as stations and interventions as lines, lighting up what is reachable from where she lies. One edge read three ways. Footnote trails from any number back to its source |
| 09 Reinforcement learning | How do you learn a good sequence of moves when the score only comes at the end? | You try, see what follows, and prefer what led somewhere good. The danger is learning to please the scorer instead of doing the job | **The board**: a grid of patient states shaded by how good it is to be there, with the learned route drawn across it. Learning curve as a race. The cheating scoreboard: a do-nothing policy outscoring the clinicians |
| 10 Decision theory | Two casualties, one helicopter. On what grounds? | A probability is not a decision. You also need to say what each mistake costs, and those costs are yours to set | **The scales**: a miss on one pan and a false alarm on the other, with weights the reader sets and the threshold moving in response. Common against lethal: two bars that disagree. A regret table that fills in as choices are made |
| 11 Hybrids and analogies | When should a model say "I am not sure"? | The best systems combine a fast memory for cases with a slow sense of the general pattern, and know when to hand back a short list instead of one answer | **The envelopes**: a prediction that opens into a set, wider when the model is less sure. The belief line across the whole pathway. Fast store and slow learner drawn side by side |

Developer and technical registers follow the labs convention: the developer paragraph gives the pseudocode, interface and cost; the technical paragraph gives the notation, the objective and the assumptions. They are written per notebook at build time against these plain drafts.

### 12.4 The belief line

The belief line is the integration visual and appears in notebook 11 and on app page 1.

| Step | What happens to the belief | Lens responsible |
|---|---|---|
| Start | Set by the casualty mix | Generator |
| Triage | Updated by the physiology | Bayesian, with rules as baseline |
| Scan | Updated by the result, by an amount that depends on setting | Bayesian |
| Time | Carried forward between observations | Stochastic |
| Treatment | Used: expected benefit is belief, times risk if bleeding, times relative reduction, times the benefit left after delay | Causal, stochastic |
| Evacuation | Used: the decision acts on expected benefit, not on a yes or no | Decision theory |

Three cautions are taught, not hidden. Physiology and scan both reflect blood loss, so updating on them as if independent overstates certainty; the generator knows the true dependence and the notebook shows the error. A rule discards the belief: the transfusion score treats a positive scan the same whether it moved belief to 61% or to 90%. And a trial's relative risk is a population average, so applying it to one casualty's probability is a modelling step and carries the mechanism label.

**The belief is a distribution (D-19).** From the scan step onward the belief is an array of draws, not one number. Related quantities share draws and are never sorted or resampled separately. The notebook shows the draws as a table before hiding them behind the type (T-4). On the app, moving the prior recomputes the draws; the walk-through page draws a band, not a bar.

### 12.5 Visual standards

- At least seven figures a notebook, as in ml-algorithms-labs, and each must carry an argument (T-8). A decorative figure is a sceptic finding.
- Figure titles state the finding.
- One figure per notebook is marked central and reused on the lens page of the app.
- People are drawn as counts wherever a probability could be a count.
- Colour never carries meaning alone; pairs that must be told apart also differ in lightness.
- At least one figure per notebook responds to a control.

---

## 13. Background pack

Each lens is grounded in published work before it is built (D-20). The pack is in [`background/`](background/README.md): one file for the casualty thread and one per lens, each with anchors (finding, numbers, limits), the reasoning, the use in the notebook and the claims that are ruled out. Its 52 sources are E-71 to E-122 in `EVIDENCE.md`, most read as abstracts.

### 13.1 What the pack changed

| # | Change | Evidence |
|---|---|---|
| B-1 | PROPPR is the shared case for lenses 02 and 03: the same trial read as P=.12 and as a 93% probability of benefit | E-72, E-73 |
| B-2 | Lens 07 leads with MATTERs against CRASH-2, with survival bias as its failure. Tourniquets become the second example | E-71, E-21, E-80 |
| B-3 | Lens 05 fits a time-varying hazard to measured hourly death rates; the fixed-rate chain is the failure | E-85 |
| B-4 | Lens 06's failure uses the hospital-identification result and the military working dog heat maps | E-98, E-103 |
| B-5 | Lens 09 sets the learned sepsis policy beside the trial of the same choice | E-97, E-50 |
| B-6 | Lens 10 opens on a deployed sepsis model judged by its consequences | E-96 |
| B-7 | Every graph edge carries a version, a valid-from date and the population it holds for | E-86, E-104 |
| B-8 | Notebook 11 opens on the physician and language model trial and builds conformal prediction | E-110, E-112 |
| B-9 | The triage benchmark is under-triage below 5% and over-triage below 50% | E-87 |

Where this table and the lens tables in section 4 differ, this table rules; the PRD is written from both.

### 13.2 Effect on the build

- The generator's hazard for bleeding deaths is time-varying from slice 0, since lens 05 needs it (B-3).
- The graph schema gains `version`, `valid_from` and `population` on edges in slice 0 (B-7).
- The sceptic gains one check: a notebook claim listed under "What must not be claimed" in its background file blocks the slice.
- Head injury has the thinnest evidence (two tranexamic acid trials and a children's rule). No lens is blocked by it.

