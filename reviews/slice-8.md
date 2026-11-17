# Review of slice 8: lens 08, Knowledge graph

**Date:** 17 November 2026 · **Author:** Ross Taylor

Fifth review of slice 8, and the re-review after the final consolidation pass (commit 305c8a3, D-33), under `docs/BUILD.md` section 5 and D-31. The base is commit 0abe3f0, the last that changed this file; the fourth review it holds read the files at ddf543a and found no breach, and its hash block matches the review sources at 0abe3f0. Only the lines changed between 0abe3f0 and the current head, 1c3bfa0, are checked, against every item below and each standing lesson in `docs/BUILD.md` section 8. Between 0abe3f0 and 1c3bfa0 the review sources changed in commit 305c8a3 alone, and there only in the notebook. A breach in a line unchanged since 0abe3f0 would be one the fourth review should have recorded, and would be marked MISSED. Cells are numbered from 0 in file order; the notebook has 38 cells. Line numbers are those of the file named, at 1c3bfa0.

What changed since 0abe3f0, in all:
- **Notebook.** In cells 13, 33 and 36 the D-23 sentence, which read "The scorecard's figures are on every stream of the military cohort, disease included; the comparison with E-09 holds for the injured only, of whom 26.5% need a life-saving intervention against 47.6% Priority 1 ...", now reads "The scorecard's figures are on every stream of the military cohort, disease included. On every stream of the military cohort, 16.7% of casualties need a life-saving intervention; the comparison with E-09 holds for the injured only, of whom 26.5% need one against 47.6% Priority 1 ..."; the rest of the sentence and of each cell is unchanged. Cell 10's printout of `rules.d23_sentence()` changes in its last line to the same sentence, and cell 34's output in axis 1 of the figure column alone, in its HTML and its plain-text table; the plain-text table's other rows change only in padding. Cell 24's printout of `k.depends_on("E-16")` gains `'11_hybrids'` among the notebooks returned: notebook 11 was built after 0abe3f0 with E-16 in its evidence list, and notebook 08 was re-executed in 305c8a3. No other cell source or text output changes; the cell tags, the `concludes:` tags and the notebook's evidence list are unchanged, and the eight images are byte-identical to those at 0abe3f0.
- **Lens module.** `src/inference_labs/lenses/knowledge.py` is unchanged byte for byte. Of the library functions it calls, only `rules.d23_sentence` changed (rules.py lines 164 to 213, with `D23_GROUPS` and `need_shares` new); `knowledge.py` calls it once, at line 1025, with its defaults, group "every stream". `stochastic.py` changes only inside its own `seven_axes` (lines 810 to 812) and `baseline.py` only in `calibration_check`, neither of which this slice calls; `decision.py`, `bayesian.py`, `graph/`, `generator.py`, `params.yaml` and `library/` are unchanged. `depends_on` (lines 915 to 920) is unchanged; its output changes because it reads each notebook's evidence list.
- **Panel.** `app/panels/knowledge.py` is unchanged, and `panel` and `page_panel` call neither `d23_sentence` nor `depends_on`. Rendered for all 1,736 casualties app page 1 can show, from the package at 0abe3f0 and at 1c3bfa0, the panel is identical.
- **Background file and register.** `docs/background/08-knowledge-graph.md`, `docs/background/01-rules.md`, PRD sections 3, 6.0 and 6.8, `docs/BUILD.md` and `docs/EVIDENCE.md` are unchanged since 0abe3f0. `docs/DESIGN.md` gains D-33.

The helpers the changed lines call were read: `rules.py` lines 145 (E-09's 0.476) and 164 to 213 (`D23_GROUPS`, `need_shares`, `d23_sentence`); `baseline.py` lines 77, 167 to 169 and 194 to 202 (`CALIBRATION_STREAMS`, `generator_sample`, `calibration_cohort`, `calibration_need`); `knowledge.py` lines 589 to 593 (`_sample`), 915 to 920 (`depends_on`) and 1020 to 1025; `provenance.py` lines 53 to 67; and `generator.py` lines 298 to 305 (`needs_lsi`). The register rows E-09 and E-16, D-23 and D-33 in `docs/DESIGN.md`, the "What must not be claimed" lists of `01-rules.md` and `11-hybrids.md`, and the evidence lists of all twelve notebooks were opened.

The notebook was run top to bottom from a fresh kernel into a scratch copy in 6.7 seconds without error. Its reader view hashes to the same value as the committed notebook, and its eight images match the committed ones byte for byte. Gates G-6, G-8, G-9 and G-10, called on their own without writing, pass. The changed figures were recomputed at full precision from the seed-42 sample and from seeds 43 to 62, 100,000 casualties each.

No breach is found, and none is missed.

## What must not be claimed

- That the graph reasons: HOLDS (cells 10, 13, 24, 33, 34 and 36; knowledge.py lines 915 to 920 and 1025). No changed line says the graph reasons, infers or decides. The D-23 sentence concerns the generator's cohort and E-09, not the graph. Cell 24's added entry is returned because notebook 11's evidence list, held as a property of its node, names E-16; that is retrieval of what was entered, as unchanged cell 25 says ("the notebooks whose evidence lists name it are returned").
- That US doctrine (E-86) is UK practice: HOLDS (the same lines). No changed line cites E-86, US doctrine or UK practice.

The changed lines carry lens 01's rule and name notebook 11, and were also read against those background files' lists:

- That a rule's published accuracy is a property of the rule, and that the MPTT-24 has been validated on pre-hospital observations (lens 01): HOLDS (cells 10, 13, 33, 34 and 36; knowledge.py line 1025). The changed clause quotes E-09's share at Priority 1, not its accuracy; "the one the rule was validated on" names a single cohort, D-23's words; `HOSPITAL` in axis 1 and the last sentence of cell 13's second paragraph, both unchanged, keep E-09 measured on hospital observations.
- That language models diagnose better than doctors, and that a conformal guarantee holds when the casualty mix changes (lens 11): HOLDS (cell 24). Notebook 11 is named only as a notebook whose evidence list names E-16; no language model or conformal set is mentioned.

## Epistemic checks

- Accuracy quoted for the wrong cohort or setting: HOLDS (cells 10, 13, 33, 34 and 36; knowledge.py lines 589 to 593 and 1025; rules.py lines 167 to 175). The rule's 60.0% and 78.6% beside the sentence are on the seed-42 military sample of 100,000, every stream, through `_sample` and `baseline.generator_sample`; the new 16.7% is `needs_lsi` on the same sample, 16,704 of 100,000, the "16,704" and "16.7% in need" cell 10 already prints. In hospital the share is the same, 0.16704, so it also fits axis 6's sample. The 26.5% is given for the injured and is called theirs. No changed line quotes E-09's accuracy for any cohort.
- Proxy data read as the real thing: HOLDS (cells 10, 13, 33, 34 and 36). The 16.7% and 26.5% are the generator's: "the military cohort" is the notebook's name for the synthetic cohort ("100,000 synthetic casualties of the military cohort (seed 42)", cell 10; "the military cohort's 100,000 synthetic casualties", cell 33), the same sentence ends on "the generator's injured", and axis 1's row is labelled mechanism. Cell 24's added entry is the provenance graph's record of a notebook's citation, not a figure about any casualty.
- Civilian data read as military: HOLDS (cells 10, 13, 24, 33, 34 and 36). The only source cited in the changed D-23 clause is E-09, for "the military registry", the JTTR row; its civilian TARN row is not used. Cell 24's label "Depends on E-16, the civilian helicopter service's scan accuracy" is unchanged and stays beside the extended list. G-10 passes.
- A diagnosis result read as a treatment result: HOLDS (cells 10, 13, 33, 34 and 36). The sentence stands in the diagnosis case (cells 10 and 13), in the paragraph on the diagnosis and baseline columns before the treatment column is introduced (cell 33), in the rule's column of axis 1 (cell 34), and in the paragraph headed "Diagnosis" (cell 36); it concerns only who needs a life-saving intervention. Cell 24 sits in the provenance part of the failure section. The treatment column's text is unchanged.

## Numbers traced to the evidence register

- E-09 (cells 10, 13, 33, 34 and 36): HOLDS. The row gives 47.6% Priority 1 among the JTTR's 3,654 adults, 2006 to 2013; the sentence takes it from `PUBLISHED["MPTT-24, military"]`, which holds 0.476 citing E-09 (rules.py line 145).
- D-23 and D-33 (the same cells): HOLDS. D-33 gives the injured, battle and non-battle, 26.5%, and asks that each scorecard's sentence name the group it reports and give that group's share. This scorecard's group is every stream of the military cohort, disease included, and the sentence now gives its share, 16.7%. D-33's rule against calling battle casualties alone milder does not arise: no scorecard row of this notebook is on battle casualties alone, and the sentence calls only the injured milder. The sentence does not repeat D-33's "occurs only among battle casualties"; in the generator 1,688 of the 43,366 disease casualties need one through septic shock (generator.py line 305), and they are counted in the 16.7%, as they are in cell 10's 16,704.
- The generator's figures: HOLDS. In the seed-42 sample 16,704 of 100,000 need a life-saving intervention, 0.16704, printed 16.7%; 15,016 of the 56,634 injured (29,925 battle and 26,709 non-battle, none of whom needs one), 0.26514, printed 26.5%. Across seeds 43 to 62 the share on every stream runs from 16.4% to 16.9% and among the injured from 25.9% to 26.6%.
- E-16 (cell 24): HOLDS. The query's notebooks are 01, 02, 03, 07, 08 and 11; of the twelve notebooks these six, and no others, list E-16. Notebooks 04 and 10 do not, as unchanged cell 25 says.

## Sentences about the generator and the graph

- "The scorecard's figures are on every stream of the military cohort, disease included.": HOLDS. Its words are unchanged; it now ends at a full stop.
- "On every stream of the military cohort, 16.7% of casualties need a life-saving intervention": HOLDS. `needs_lsi` is significant bleeding, tension pneumothorax, severe head injury or septic shock (generator.py line 305); `need_shares` takes its mean over the seed-42 military sample (rules.py lines 167 to 175), the sample `knowledge.py` scores (lines 589 to 593).
- "the comparison with E-09 holds for the injured only, of whom 26.5% need one against 47.6% Priority 1 in the military registry (E-09), so the generator's injured are a milder cohort than the one the rule was validated on (D-23)": HOLDS. Only "need a life-saving intervention" became "need one". "The injured" are the streams `battle` and `non_battle` (baseline.py line 77); the 26.5% is `calibration_need("military")` (lines 199 to 202); `milder` compares 0.26514 with 0.476 at full precision (rules.py lines 190 to 191).
- Cell 24, `depends_on("E-16")`: HOLDS. `depends_on` returns the parameters with a taken-from edge to the source and the notebook nodes whose evidence property names the id (knowledge.py lines 915 to 920); the printed tuple is that set.

## Standing lessons

- Lesson 1: HOLDS. E-09 is named with its id and its population, the military registry, in the same sentence; it is set beside the generator's cohorts, not applied to the casualty.
- Lesson 2: HOLDS. Each share names its group, "every stream of the military cohort" and "the injured"; E-09's 47.6% is "Priority 1 in the military registry", as its row gives it.
- Lesson 3: HOLDS. No number on app page 1 changes: the panel is identical on all 1,736 entries. G-8 passes.
- Lesson 4: HOLDS. "A milder cohort" is stated in words.
- Lesson 5: HOLDS. The shares are the generator's, in cells and a row that say so; no prior enters them.
- Lesson 6: HOLDS. No figure changes.
- Lesson 7: HOLDS. The sentence stays in the diagnosis cells, the diagnosis paragraph and the rule's column; the treatment column is unchanged.
- Lesson 8: HOLDS. The changed lines quote only E-09's share at Priority 1 and call nothing performance at the point of injury.
- Lesson 9: HOLDS. The changed lines give shares, not counts; cell 24's tuple names each notebook.
- Lesson 10: HOLDS, as set out under the sentences about the generator and the graph.
- Lesson 11: HOLDS. "The one the rule was validated on" is D-23's; no changed line says why anything was chosen or what a source omits or forbids.
- Lesson 12: HOLDS. The injured share is below 47.6% on every seed from 43 to 62; the comparison is not a tie. The 16.7% is compared with nothing.
- Lesson 13: HOLDS. No chance of death is in the changed lines.
- Lesson 14: HOLDS. 0.16704 prints as 16.7% in the sentence and in cells 10 and 13 alike; 0.26514 is compared with 0.476 at full precision.
- Lesson 15: HOLDS. The changed clause adds the scorecard's own group and its share; the clause on the injured is unchanged and is D-33's form for a scorecard on every stream. No figure of the scorecard is given for the injured or for battle casualties alone, so none is shown without a subgroup in which it reverses.
- Lesson 16: HOLDS. The D-23 sentence stands in cells 10, 13, 33 and 36 and in axis 1 of the figure column, wherever the rule's accuracy on the generator is quoted, and says the generator's injured are a milder cohort.
- Lesson 17: HOLDS. No learned model is in the changed lines.

## Figures

- The eight figures (cells 3, 7, 11, 12, 18, 21, 28 and 31): HOLDS. Each source, title and `concludes:` tag is unchanged since 0abe3f0, and each image is byte-identical to that at 0abe3f0. Cell 34's scorecard is a table, not a figure.
- App page 1, the knowledge graph panel: HOLDS. It holds no figure.

## Strings the lens module returns, and the panel

- `seven_axes`, axis 1 of the figure column (line 1025): HOLDS, as set out above. With its defaults, `d23_sentence` returns the subject, the scope, the every-stream share and the injured clause (rules.py lines 206 to 207); cells 10 and 34 print it word for word. Its other groups are not reached from `knowledge.py`.
- `depends_on` (lines 915 to 920): HOLDS, as under E-16.
- Every other string `knowledge.py` can return: HOLDS. Their source lines and every function they call are unchanged since 0abe3f0, and every other cell's text output prints as before.
- `app/panels/knowledge.py`: HOLDS. Unchanged: one subheader and four markdown lines, each the library's string, identical on all 1,736 entries at 0abe3f0 and 1c3bfa0.

## Limits

None recorded. A re-review after consolidation records no new limits (`docs/BUILD.md` section 5); the limits of the review committed at 405ecb3 stand as a record (D-31).

VERDICT: HOLDS

## Reviewed sources

- `notebooks/08_knowledge_graph.ipynb` 80eb30d0371e7a428add12cf2ccbf1f0a5ad51026270eaa308d0784c33d92733
- `src/inference_labs/lenses/knowledge.py` ff3c152d71295f2f5cf38abb1e5813e2c4f672508d073055f80afb9ecf6a520d
- `app/panels/knowledge.py` 8c9a5b8af234fc7f9b04f64d652f8f9c922bbd09bec1290f21d3f9fad6311cf1
