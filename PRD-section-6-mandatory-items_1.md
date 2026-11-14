### 6.0 Mandatory items by slice

Each item below is a requirement of its slice (BUILD.md section 3, rule 4). They are held here so that the builder and the reviewer read the same list. Slices 2 to 5 are built; their items are in sections 6.2 to 6.5.

#### Slice 6 — lens 05, stochastic processes

a. A time-varying hazard for death from bleeding set against the three measured points in E-85, and a constant-hazard chain shown failing against the same points. The constant-hazard option is used for this failure and nowhere else.
b. By hand: a small state chain on paper, stepped forward three intervals.
c. The decline of tranexamic acid benefit with delay (E-22, E-24) as a function of time. The timing analysis was exploratory (E-23) and civilian; both are stated.
d. Early against late outcome: on the generator, a benefit visible at 3 hours diluted by 30 days, as mechanism, beside RePHILL's figures (E-77).
e. Recorded time is rounded (E-20): the generator's times rounded to the nearest half hour, and what that does to a fitted decline.
f. A second, independent source for a front-loaded risk before hospital (E-127), beside E-85, with what each measures and from when.
g. E-85's rates are measured from hospital admission and run here from injury; said wherever they are used.
h. The golden hour study's limit: transport time was matched for only 37.3% of casualties (E-81).
i. If the generator holds no repeated observations, any series over time is simulated in the notebook from the hazard and labelled as constructed.

#### Slice 7 — lens 07, causal

a. The generator's causal graph drawn, with the statement that the true effect is known here only because the generator was built with it.
b. The effect of tranexamic acid estimated three ways on the generator: naively, adjusted for what drives who is treated, and against the generator's true value.
c. Survival bias reproduced and removed: treatment available only to those alive at a given time, a naive comparison, then one aligned at a common start. Beside it, the published correction 0.37 to 0.84 (E-80) and the transfusion contrast in military data, with the authors naming the bias (E-81).
d. An unmeasured cause: one variable hidden, the adjusted estimate repeated and still wrong. Beside it, what the golden hour re-analysis could and could not remove by weighting (E-123).
e. Selection on reaching care: killed in action against died of wounds (E-81) as the same structure.
f. By hand: one stratified two-by-two table in which the combined and the within-stratum comparisons disagree.
g. MATTERs (E-71) beside CRASH-2 (E-21), their populations stated. They are not reconciled, and the notebook says why they cannot be from these sources.
h. The three tasks of data science (E-117) as a table, with this lens's anchors sorted into its columns.
i. "Mortality was lowest where clinicians matched the algorithm" (E-120) offered as an association to question. The reading that it is confounded is the notebook's own and is labelled so.
j. No real trial data while O-2 is open.

#### Slice 8 — lens 08, knowledge graph

a. A hand-built graph of about fifty nodes: finding, injury, intervention, competency, echelon. Every edge carries label, source, version, valid_from and population.
b. By hand: twelve nodes on paper, tracing free fluid to the place that can treat it.
c. Diagnosis: findings to candidate injuries by traversal, returned as a ranked list with the edges that produced each candidate (E-51). The scorecard scores the list.
d. Treatment: injury to intervention to competency to echelon, with the timelines as properties of the edges between echelons (E-42, E-43, under D-28).
e. A query for what can be done at a given echelon, offered as a bound on the options a decision may consider. The decision theory lens is not changed to use it.
f. The MPTT-24's six steps as edges (E-08), and a provenance query: every generator parameter to its source, and "which results depend on E-16".
g. Failure one, a stale edge: two versions of the tranexamic acid dosing edge, a query that returns the old one, and a date-aware query that catches it. Only what E-86 states about the 2023 change is used. If the earlier guideline wording is not in the register, the earlier edge is represented by the CRASH-2 regimen (E-19) and the notebook says the earlier wording is not held.
h. Failure two, an edge true for another population: the needle length edge (E-104).
i. US doctrine is labelled as US doctrine on every edge it supplies and is never described as UK practice.
j. The graph retrieves what was put there; nothing says it reasons. No retrieval-augmented generation and no graph learning are built.

#### Slice 9 — lens 09, reinforcement learning

a. The environment. Use the published ICU-Sepsis environment (E-49) if it can be installed from its public source at build time and its licence allows the tables to be held in the repository. If not, build a small sepsis-like decision process in the library, label it as constructed, and quote E-49's figures only as published figures. Record which was done.
b. By hand: a four-state, two-action world, with the value of each state worked out on paper.
c. A policy learned from logged episodes of a behaviour policy, not from free interaction.
d. The learned policy's value estimated from the logs by importance sampling, with the effective sample size shown (E-119), and then its true value revealed by running the environment.
e. Failure: a do-nothing policy scoring above the behaviour policy under naive evaluation from logs (E-50), with the reason shown in the weights.
f. A variable the learner sees and the logged policy did not: the estimated value rises, the true value does not (E-120's own limitation; E-119's first question).
g. The trial of the same clinical choice (E-97) and the timing result for fluids (E-94) set beside the learned policy's claim (E-120). The notebook says the trial tested two fixed strategies and does not refute an adaptive one.
h. The benchmark's estimated clinician policy scoring the same as a random one (E-49), put to the reader as a question about the model.
i. Sepsis is a stand-in for prolonged casualty care, for which no open data exist; said at the start. The graph's bound on available actions is described, not built in.
j. Diagnosis is a weak fit for this lens and is labelled so.

#### Slice 10 — lens 06, connectionist

a. By hand: one unit's forward pass and one gradient step, on paper.
b. A small network on the generator's signs, scored against the logistic score and the forest. If it does no better, that is the result (E-118).
c. An image task on a constructed proxy: small synthetic images generated in the library, labelled wherever shown as constructed and not ultrasound. No dependency heavier than scikit-learn is added without stopping to say so.
d. Failure: a marker correlated with the label is planted in the training images; accuracy rises; an occlusion map moves to the marker; accuracy falls on images without it. Beside it, the published site-identification result (E-98) and the heat maps from military working dog scans (E-103).
e. An unseen site: the model scored where it was not trained, beside the sepsis challenge result on its unseen hospital system (E-48).
f. A saliency or occlusion map shows where a model looked, not why (E-118); printed beside every such map.
g. Two operating points from one model (E-101), as the hand-over to decision theory.
h. Published military work on automating the scan is on swine, dogs and phantoms (E-102, E-103, E-122). Nothing is claimed about scans of human casualties.
i. The brain analogy with where it breaks (E-55 to E-58 as the background file cites them).

#### Slice 11 — notebooks 00 and 11, app pages, gallery

a. Notebook 00, the casualty thread: the three questions (E-117) put to the casualty; what reduced combat mortality (E-82) and who died after reaching care in UK data (E-128); a map of the ten lenses.
b. Notebook 11: prediction sets by conformal prediction on the baseline and on the tree (E-112), with coverage checked on held-out casualties.
c. Two failures in notebook 11: coverage lost when the casualty mix shifts, and a set that is always every label. The requirement that calibration cases resemble new ones is stated as general knowledge, not as a finding of E-112.
d. The kinds of join, each with its source: a test feeding a rule (E-31), a trial feeding a prior (E-74), an ontology feeding a ranking (E-107), rules generating data for a learner (E-51). The physician and language model trial (E-110) is the hook, with its limits.
e. The lens table generated from the scorecards. No number in it is typed by hand.
f. App pages: mix and setting; lens table; graph explorer; one explainer page per lens; the visual gallery. Each is its own file. All run on synthetic data only.
g. Retrieval-augmented generation and graph learning are described and pointed to, not built.
h. The `deferred` list is empty before this slice starts.
