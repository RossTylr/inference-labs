# Review of slice 4: lens 04, Decision trees

**Date:** 17 November 2026 · **Author:** Ross Taylor

Eighth review, and the re-review after the final consolidation pass (commit 305c8a3, D-33), under `docs/BUILD.md` section 5 and D-31. The base is commit b0371a6, the last that changed this file; the review sources there hash to the seventh review's block. Only the lines changed between b0371a6 and the current head, 62f20c9, are checked, against every item below and each standing lesson in `docs/BUILD.md` section 8. Every changed line is new since the seventh review; a breach in the part of a changed line that the seventh review read unchanged would be marked MISSED. Cells are numbered from 0 in file order; the notebook has 32 cells. Line numbers are those of the file named, at 62f20c9.

What changed since b0371a6, all in commit 305c8a3. In the notebook: one sentence is added to the third paragraph of cell 10 and to the second paragraph of cell 27, "On every stream of the military cohort, 16.7% of casualties need a life-saving intervention;", after which "of whom 26.5% need a life-saving intervention" becomes "of whom 26.5% need one"; and in cell 28's output the axis 1 entry of the figure column carries the same sentence, from `rules.d23_sentence()`. In the lens module, line 93 alone: the forest is built with `n_jobs=1` in place of `n_jobs=-1`. `app/panels/trees.py`, every other line of the lens module, every other cell's source and text output, the nine images, `generator.py`, `params.yaml`, `docs/EVIDENCE.md` and `docs/background/04-decision-trees.md` are unchanged since b0371a6. The new sentence is written by `rules.d23_sentence` and `rules.need_shares` (rules.py lines 164 to 213), which were read. The other changes since b0371a6 to modules this slice imports, `decision.seven_axes` (b953dc2) and `baseline.calibration_check` (eb1efab), are not called by this slice.

The notebook was run top to bottom from a fresh kernel into a scratch copy in 32 seconds without error. Its reader view hashes as the committed file's, and its nine images match the committed file and those at b0371a6 byte for byte. The end the seventh review found printing -8.8 or -8.7 from run to run, the forest's specificity less the figure reading's among the battle casualties, prints -8.8 in both: with the trees averaged in one process the forest's probabilities repeat exactly, and they differ from the parallel average by at most 4.4e-16, which moves no casualty of the evaluation sample across the forest's threshold. Slice 4's tests pass (13). Gates G-6 and G-10, called on their own without writing, pass. Every figure in the changed lines was recomputed at full precision from `generator.sample(100_000, 42, setting="pre_hospital")`, without the lens's or the rule lens's helpers.

No breach is found, and none is missed.

## What must not be claimed

- That PECARN was derived by recursive partitioning, without checking the paper: HOLDS (cell 10, third paragraph; cell 27, second paragraph; cell 28, axis 1 of the figure column; trees.py line 93). No changed line names PECARN or E-89, mentions recursive partitioning, or says how any published rule was derived.
- That a forest's 0.89 will hold on military casualties: HOLDS (the same lines). No changed line carries 0.89 or E-91. Line 93 changes how the forest's 100 probabilities are summed, and no figure the notebook prints.

The new sentence is lens 01's D-23 statement, and the changed lines were also read against the lists in the other background files:

- That a rule's published accuracy is a property of the rule, and that the MPTT-24 has been validated on pre-hospital observations (lens 01): HOLDS (cells 10, 27 and 28). The new sentence gives a share in need on the generator; no changed line quotes either rule's published accuracy or says on what observations the MPTT-24 was validated.
- The lists of 00, 02, 03 and 05 to 11: HOLDS (changed lines only). E-09's 47.6% is a share Priority 1, set beside the generator's injured as a comparison of cohorts, not an outcome figure applied to a casualty. No changed line uses the 44% attribution, over-triage, transport time, a posterior, CRASH-3, E-85, a network, a causal claim, a graph, E-86, a learned policy, a weight between a miss and a false alarm, the civilian benchmark, PATCH, a language model or a conformal guarantee.

## Epistemic checks

- Accuracy quoted for the wrong cohort or setting: HOLDS (cell 10, third paragraph; cell 27, second paragraph; cell 28, axis 1 of the figure column). The new sentence names its group, "every stream of the military cohort", and in each place stands beside figures on that group: in cell 10 after "These figures are on all 100,000 synthetic casualties of the military cohort, every stream"; in cell 27 after "The scorecard's figures are on every stream of the military cohort, disease included"; and in cell 28 after the figure reading's sensitivity and specificity, computed by `baseline.diagnosis_results("pre_hospital", "figure")` on the seed-42 sample of every stream. The 16.7% is taken on that same sample (`rules.need_shares`, through `baseline.generator_sample`). The comparison with E-09 stays with the injured, its 26.5% taken on the battle and non-battle streams (`baseline.calibration_cohort`). No figure in the changed lines depends on the setting.
- Proxy data read as the real thing: HOLDS (the same lines). The 16.7% is the share of the generator's synthetic casualties in need. In cells 10 and 27 it follows a sentence naming the 100,000 synthetic casualties; in cell 28 it stands in the row "1 Discrimination (mechanism)", in the sentence that names "the generator's injured". It is set beside no published figure.
- Civilian data read as military: HOLDS (the same lines). The one source cited in the changed lines is E-09, for 47.6% Priority 1 "in the military registry", the JTTR row of the register; its TARN row is not used. G-10 passes.
- A diagnosis result read as a treatment result: HOLDS (the same lines). The new sentence gives the share in need of a life-saving intervention, the diagnosis target, in the diagnosis paragraphs of cells 10 and 27 and in the baseline column of cell 28. It gives no effect of any intervention, and the treatment column is unchanged.

## Numbers and their evidence ids

- The 16.7% in cells 10, 27 and 28: HOLDS. No evidence id is due: it is a share on the generator. On the seed-42 sample 16,704 of the 100,000 casualties need a life-saving intervention, 0.16704, which `rules.need_shares()["every stream"]` returns and cells 10 and 27 type as 16.7%.
- The 26.5%, now "of whom 26.5% need one": HOLDS. 15,016 of the 56,634 injured, battle and non-battle, 0.26514, as `baseline.calibration_need("military")` returns.
- E-09's 47.6%, with D-23: HOLDS. The register row was opened: 47.6% Priority 1 among the JTTR's 3,654 adults. `rules.PUBLISHED["MPTT-24, military"].prevalence` is 0.476.
- The figure reading's sensitivity and specificity in the same entry of cell 28, 60.0% and 78.6%: HOLDS. Unchanged since b0371a6 and reproduced by the fresh run.

## The generator and the graph

- "On every stream of the military cohort, 16.7% of casualties need a life-saving intervention" (cells 10, 27 and 28): HOLDS. `generator.sample`, whose cohort defaults to the military, returns `needs_lsi` for every casualty, and the share is taken over all 100,000 casualties of every stream, those dead before pre-hospital care included, as cell 27 says they are counted. By stream it is 50.2% of the 29,925 battle casualties, 3.9% of the 43,366 disease admissions and none of the 26,709 non-battle injuries; the sentence says nothing of which streams hold the need.
- `rules.d23_sentence()` as called at trees.py line 593: HOLDS. With its defaults (`group="every stream"`, rules.py lines 178 to 213) it returns the sentence printed in cell 28. It is the lens module's only call, so this is the only form of the sentence the module can return. "a milder cohort" is chosen by comparing the injured share with E-09's at full precision, 0.26514 against 0.476.
- Line 93, `n_jobs=1`: HOLDS. No sentence in the review sources says how the forest is computed, and the change alters no printed figure, as set out above.
- The graph: HOLDS. No changed line describes a graph.

## Standing lessons

Each lesson against the changed lines.

- Lesson 1: HOLDS. No changed line applies a trial or registry figure to the casualty; E-09's 47.6% is given with its id and its population, the military registry, as a comparison of cohorts.
- Lesson 2: HOLDS. The new share names its group, every stream of the military cohort, the group of the figures beside it; the comparison with E-09 names the injured.
- Lesson 3: HOLDS. The panel shows none of the changed strings: `app/panels/trees.py`, `panel` and `page_panel` are unchanged, and the forest's probability they show moves only in the last places (by at most 4.4e-16 on the evaluation sample). The lens page for notebook 04 shows cells 2 and 4 and the central figure, none changed. The sentence reaches the app only in the gallery's note to notebook 04's third figure, written outside this slice by `pages.figure_notes`, where each of its numbers says what it is and comes from `rules.d23_sentence`.
- Lesson 4: HOLDS. The changed lines carry no difference or sign; "a milder cohort" is in words.
- Lesson 5: HOLDS. The 16.7% rests on the generator alone, in a row labelled "(mechanism)" and beside sentences naming the synthetic casualties; no prior enters it.
- Lesson 6: HOLDS. No figure or title has changed since b0371a6.
- Lesson 7: HOLDS. The new sentence stands with the diagnosis results and the baseline, against need for a life-saving intervention.
- Lesson 8: HOLDS. No changed line concerns observations made in hospital.
- Lesson 9: HOLDS. "100,000" is exact; the share recomputes from 16,704 of 100,000.
- Lesson 10: HOLDS, as set out under the generator and the graph.
- Lesson 11: HOLDS. No changed line says where a rule's items came from, what a source omits or forbids, or why anything was chosen.
- Lesson 12: HOLDS. The new sentence compares no method with another. Across seeds 43 to 62 the share runs from 16.4% to 16.9%, and it is set against no figure.
- Lesson 13: HOLDS. No changed line gives a chance of death.
- Lesson 14: HOLDS. 16.7%, 26.5% and 47.6% are each to one place and each rounds from full precision; "milder" is decided at full precision.
- Lesson 15: HOLDS. The new figure is one share, not a comparison, so it cannot reverse in a subgroup; its split by stream is set out above.
- Lesson 16: HOLDS. D-23's statement still stands with the rule's accuracy on the generator in each changed place, cells 10, 27 and 28's figure column, and still scopes "a milder cohort" to the injured. No changed line calls the battle casualties milder.
- Lesson 17: HOLDS. No changed line reports a learned model's result, and line 93 changes none.

## Figures

- The nine figures (cells 3, 8, 13, 15, 17, 19, 22, 25 and 26): HOLDS. None has changed since b0371a6: each image is byte-identical to the base and to the fresh run, and each source, title and `concludes:` tag is unchanged.
- App page 1, the trees panel: HOLDS. It holds no figure; its file, `panel` and `page_panel` are unchanged since b0371a6.

## Limits

None recorded. A re-review after consolidation records no new limits (`docs/BUILD.md` section 5); the limits of the review committed at b06f8dc stand as a record (D-31).

VERDICT: HOLDS

## Reviewed sources

- `notebooks/04_decision_trees.ipynb` 5b04f3c11e37d57c0c64a40e836607b10c64aa525567ed2ae097694bc4660e49
- `src/inference_labs/lenses/trees.py` 0ef18599a00e7b4818d8de429500d3dd1e87b427a367bff1a642af7ef2cb33b0
- `app/panels/trees.py` c31e459b0ecb5535cda93df897b5be5db6d2ba657f7b91e2bd8d74cadf198a7e
