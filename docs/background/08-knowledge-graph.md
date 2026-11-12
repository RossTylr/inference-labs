# 08 — Knowledge graphs

**The lesson in one line:** some knowledge is neither a rule nor a statistic but a maintained map of what connects to what, and its value and its danger both come from the fact that people keep it.

---

## Anchors

| Id | Finding | Numbers | Limits |
|---|---|---|---|
| E-107 | An ontology doing diagnostic work at national scale | 4,660 participants; features coded as Human Phenotype Ontology terms, then sequencing with automated prioritisation. Diagnosis in about 25%; 35% where a single-gene cause was likely, 11% where complex. A quarter of diagnoses changed management | Rare disease; the ontology is one part of a pipeline |
| E-86 | Doctrine as a source of edges | Product order (whole blood, then 1:1:1), triggers, targets, doses. Published 2019, superseding 2017, with rapid updates in 2023 that changed the tranexamic acid dose to a single 2 g bolus | US guideline |
| E-42, E-43 | Echelons and timelines | Role 1, Role 2 (forward, basic, enhanced), Role 3, Role 4; 10 minutes, 1 hour, 2 hours | 2019 edition; currency unchecked (O-3) |
| E-104 | An edge that was wrong for the population | "A 5 cm needle reaches the pleural space" against a mean chest wall of 5.36 cm | — |
| E-111 | Retrieval from curated sources | On 314 clinical questions a language model with retrieval was rated better than standard models for factuality, completeness and safety | No effect sizes in the abstract |

---

## Thinking

**Proof that the idea earns its keep.** The rare disease result (E-107) is the strongest real-world case for a knowledge graph in medicine. A clinician's free-text description cannot be matched against thousands of genes. The same description, coded as terms from a shared ontology, can. The ontology did not make the diagnosis; it made the patient comparable. A quarter of families got an answer. The military analogue is modest by comparison, but the principle is identical: code the finding in a shared vocabulary, and a traversal can tell you what it connects to.

**Doctrine is already a graph, written as prose.** The resuscitation guideline (E-86) states that a casualty with three of four findings has about a 70% risk of needing massive transfusion, that whole blood is preferred, that components follow at roughly equal ratios, that tranexamic acid is given only within three hours. Each sentence is an edge with a condition on it. Writing them as edges adds two things prose lacks: every edge can carry its source, and a query can ask what is possible at a given echelon.

**Edges go out of date, and the guideline shows it.** The 2019 document superseded a 2017 one, and in 2023 the tranexamic acid dose changed from a split dose to a single bolus. A graph built in 2020 would be confidently wrong about dosing by 2024. This is the lens's characteristic failure with a real date attached. Every edge therefore needs a version and a "valid from", and the notebook should hold two versions of the dosing edge and show a query returning the stale one.

**An edge can be true in general and false here.** "A 5 cm needle reaches" is a fact about a reference population (E-104). The graph needs somewhere to say for whom an edge holds. This is the epistemic label in the design, doing real work.

**What the graph is for in this repository.** The other lenses estimate what is likely. The graph answers a different question: given that estimate, what can be done at this echelon, by whom, and where is the nearest place that can do more. It bounds the choices lenses 09 and 10 are allowed to consider. A treatment decision that recommends surgery at Role 1 is not wrong statistically; it is impossible, and only the graph knows that.

**Retrieval is the bridge to language models.** E-111 suggests that grounding a model in curated sources improves its answers. The work on that belongs to another project; here it is noted as the reason a maintained, sourced graph is worth having.

---

## Added from the full text

Findings taken from the papers themselves on 12 November 2026. Each is in the evidence register under the id shown.

| Id | Finding | How the notebook can use it |
|---|---|---|
| E-51 | A knowledge base of 49 conditions, 110 symptoms and 113 antecedents, driving a rule-based system that outputs a differential diagnosis, not a single answer | The output of a graph traversal is a ranked list. The diagnosis case should return candidates with reasons, and the scorecard should score the list |
| E-51 | The knowledge base and the rule system are proprietary | A graph whose edges cannot be inspected has no provenance. The contrast with this repository's graph, where every edge carries a source, is the point of the lens |
| E-20 | The trial's entry criteria: adult, within 8 hours, bleeding or at risk by clinical judgement | Each is a condition on the edge from 'bleeding casualty' to 'tranexamic acid', with the trial as its source and the later three-hour limit (E-22) as a newer version |

---

## Use in the notebook

| Part | Material |
|---|---|
| Hook | In 2023 the guideline changed the tranexamic acid dose. How would your system know? |
| By hand | Twelve nodes on paper: finding, injury, intervention, competency, echelon. Trace free fluid to the place that can treat it |
| Diagnosis case | Findings to candidate injuries by traversal |
| Treatment case | Injury to intervention to competency to echelon, with the timelines as properties of the edges between echelons |
| Failure | A stale dosing edge; a needle edge that holds for the wrong population |
| Central figure | The map of care |

## What must not be claimed

- That the graph reasons. It retrieves what a person put there.
- That US doctrine (E-86) is UK practice. It is used as an open, citable source of structure; UK clinical guidance for operations is not openly published and should replace it where the builder has access.

## Open items

- O-3: confirm the current edition of AJP-4.10.
- A UK-sourced set of edges for the capability chain.
