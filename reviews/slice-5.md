# Review of slice 5: lens 10, Decision theory

**Date:** 17 November 2026 · **Author:** Ross Taylor

Eighth review, and the re-review after the final consolidation pass (commit 305c8a3, D-33), under `docs/BUILD.md` section 5 and D-31. The base is commit 3ef5eec, the last that changed this file. There the notebook's reader view hashes to 0c0e3ba4, the lens module to f6612588 and the panel to 8fc7fb89, the digests the seventh review recorded, so the base is what that review read. Only the lines changed between 3ef5eec and the current head, 97dcf93, are checked, against every item below and each standing lesson in `docs/BUILD.md` section 8. Each changed line keeps words the seventh review read; a breach in those words would be marked MISSED. Cells are numbered from 0 in file order; the notebook still has 31 cells and none was added or removed. Line numbers are those of the file named, at 97dcf93.

What changed. Of the three review sources only the notebook has changed, in commit 305c8a3: one source line in each of two cells, and one entry of one output.
- Cell 10, the paragraph opening "On the generator the question can be asked", and cell 26, the paragraph opening "The diagnosis column is". In each, the clause naming every stream now ends its own sentence ("... every stream." in cell 10, "... disease included." in cell 26). It is followed by "On every stream of the military cohort, 16.7% of casualties need a life-saving intervention;", and "of whom 26.5% need a life-saving intervention" becomes "of whom 26.5% need one".
- Cell 27's output, axis 1 of the figure column, in its HTML and plain-text forms: the same change. The other six rows of that column differ only in the padding of the plain-text view.

No other cell source, text output, tag, `concludes:` tag, evidence list or image has changed; every other difference in the file is execution timing. `src/inference_labs/lenses/decision.py` and `app/panels/decision.py` are byte-identical to 3ef5eec. The changed entry is written at decision.py line 691 by `rules.d23_sentence()`, called with its defaults. In 305c8a3 that function was rewritten (rules.py lines 164 to 213) to take its shares from the new `need_shares`. Line 691 is the module's only call of it, so the "every stream" branch (rules.py lines 206 and 207) is the only form of the sentence the module can return, whatever costs are passed to `seven_axes`. Of the other code the module draws on, `trees.py` changed in line 93 alone, where the forest is now built with `n_jobs=1`, and `baseline.py` in `calibration_check` alone, which this slice does not call. Neither moves a figure in the reader view. `generator.py`, `params.yaml`, `docs/EVIDENCE.md`, `library/curated.yaml` and `docs/background/10-decision-theory.md` are unchanged since 3ef5eec; `docs/DESIGN.md` gains D-33 alone.

What was run. The notebook was run top to bottom from a fresh kernel, as gate G-7 runs it, into a scratch copy in 32.8 seconds without error. Its reader view matches the committed file exactly and gives the hash below, and its eight images match the committed ones and those at 3ef5eec byte for byte. Slice 5's tests pass (17). Gates G-6, G-8, G-9 and G-10, called on their own without writing, pass. The decision panel was rendered through `decision.page_panel` for every casualty app page 1 can show, all three patient types in both settings, 1,736 entries, at 3ef5eec (from an archive of that commit) and at 97dcf93. The two sets are identical, and every entry has its heading, costs line and evacuation line. Every share in the changed lines was recomputed from `generator.sample(100_000, 42, setting="pre_hospital", cohort="military")`, without `need_shares` or the lens's helpers:
- on every stream, 16,704 of 100,000 casualties need a life-saving intervention (0.16704), and the same number in hospital;
- among the injured, 15,016 of 56,634 (0.26514), who are 29,925 battle and 26,709 non-battle casualties;
- among the battle casualties alone, 15,016 of 29,925 (0.50179); among the disease admissions, 1,688 of 43,366; among the non-battle injuries, none.

On seeds 43 to 62 the share runs from 16.4% to 16.9% on every stream, from 25.9% to 26.6% among the injured and from 49.3% to 50.2% among the battle casualties. Axis 1's 60.0% and 78.6%, unchanged words in a changed entry, were recomputed with `baseline.priority_one(observed, "figure")`: 10,021 of 16,704 and 65,436 of 83,296. The register row of E-09 was opened again, with the population of its source in `library/curated.yaml`.

No breach is found, and none is missed.

## What must not be claimed

- That the civilian benchmark applies to military triage: HOLDS (cells 10 and 26, the changed paragraphs; cell 27, axis 1 of the figure column). No changed line mentions the benchmark, E-87, under-triage or over-triage. The one published figure in them, 47.6%, is E-09's share at Priority 1 in the military registry, set against the generator's injured. No changed figure is measured against the benchmark.
- That PATCH shows extra survivors were left with poor function: HOLDS (the same lines). No changed line mentions PATCH, E-78, tranexamic acid or functional outcome.
- A specific exchange rate between a miss and a false alarm: HOLDS (the same lines). The changed lines give no weight. Cell 10's paragraph names only "the weight $t/(1-t)$" of net benefit, a function of the threshold. Cell 26's paragraph speaks of "the threshold the default costs set", and cells 3 and 4 call those costs an assumption, the reader's to set. The new sentence is a share in need, not a cost.

## Epistemic checks

- Accuracy quoted for the wrong cohort or setting: HOLDS (cells 10 and 26; cell 27, axis 1 of the figure column; decision.py line 691; rules.py lines 167 to 213). The only accuracy in a changed line is axis 1's sensitivity of 60.0% and specificity of 78.6%, computed by `diagnosis_inputs("pre_hospital")` (decision.py line 175) on the seed-42 sample of every stream. The new sentence beside it gives that same group's share in need, 16.7%, taken on that same sample. The comparison with E-09 stays with the injured, whose 26.5% is `baseline.calibration_need`, the battle and non-battle streams (baseline.py lines 77 and 194 to 202). The setting moves no share: 0.16704 before hospital and in hospital.
- Proxy data read as the real thing: HOLDS (the same lines). The 16.7% and 26.5% are shares of the generator's synthetic casualties. In cell 10 they follow "all 100,000 synthetic casualties of the military cohort, every stream"; in cell 26, "scored on all 100,000 synthetic casualties of the military cohort, every stream"; in cell 27 they stand in the row "1 Discrimination (mechanism)", in a sentence that names "the generator's injured". The only published figure, 47.6%, carries E-09 and is said to belong to the registry.
- Civilian data read as military: HOLDS (the same lines). The changed lines cite only E-09, for 47.6% Priority 1 "in the military registry". That is the JTTR row of `vassallo2017d`, whose population is recorded as mixed; its civilian row, TARN, is not quoted. G-10 passes.
- A diagnosis result read as a treatment result: HOLDS (the same lines). The new sentence is the share in need of a life-saving intervention, the diagnosis target. It stands in cell 10 under the heading "Diagnosis", in cell 26's account of the diagnosis and baseline columns, and in axis 1 of the figure column. Cell 26 still describes the treatment column in sentences of its own, on its own group. No changed line gives the effect of any treatment.

## Numbers and their evidence ids

- 16.7% on every stream (cells 10 and 26, typed; cell 27, axis 1, from rules.py line 174): HOLDS. No evidence id is due: it is a share on the generator. On seed 42, 16,704 of the 100,000 casualties need a life-saving intervention, 0.16704; on seeds 43 to 62 it runs from 16.4% to 16.9%. The typed figure agrees with the unchanged figures around it: cell 13 prints "every stream 16.7%" from `battle_share_in_need` (decision.py lines 544 to 549), and axis 7's "flag every casualty 7.4" is 16.704 less 83.296 over 9.
- 26.5% among the injured (the same lines; rules.py lines 174 and 194): HOLDS. 15,016 of 56,634, the battle and non-battle streams. No evidence id is due.
- 47.6% Priority 1 in the military registry, E-09 (the same lines; rules.py line 186): HOLDS. The register row of E-09 gives "JTTR (3,654 adults, 2006-2013; ... 47.6% Priority 1)". The population is quoted as the row gives it, Priority 1, not need for an intervention.
- 60.0% and 78.6% (cell 27, axis 1 of the figure column): HOLDS. 10,021 of 16,704 and 65,436 of 83,296, which print as shown.
- The other figures in cell 26's changed paragraph, "all 100,000", "20 synthetic samples of 400,000 casualties with 200,000 random pairs from each": HOLDS. `EVAL_N` is 100,000 (baseline.py line 70); `SEEDS`, `SPREAD_N` and `PAIRS` are 20, 400,000 and 200,000 (decision.py lines 53 to 55), and `aircraft_spread` draws them so (lines 396 to 406).
- "(D-23)" and "(D-24)": HOLDS. D-23, as D-33 restates it, gives 26.5% for the injured against 47.6% for E-09 and asks each scorecard's sentence to name the group it reports and give that group's share. D-24 names the two readings of the MPTT-24. The changed lines say no more of either.

## The generator and the graph

- "On every stream of the military cohort, 16.7% of casualties need a life-saving intervention" (cells 10, 26 and 27): HOLDS. `need_shares` (rules.py lines 167 to 175) takes the mean of `needs_lsi` over `baseline.generator_sample("pre_hospital", "military")`: 100,000 casualties at seed 42 over the battle, non-battle and disease streams (baseline.py lines 70 and 167). `needs_lsi` is bleeding, tension pneumothorax, severe head injury or septic shock (generator.py line 305). The sentence says nothing of which streams hold the need. No changed line repeats D-33's wording that need occurs only among battle casualties: in the generator 1,688 of the 43,366 disease admissions also need an intervention, through septic shock (generator.py lines 303 to 305), and the 16.7% counts them.
- "The comparison with E-09 holds for the injured only, of whom 26.5% need one ... so the generator's injured are a milder cohort than the one the rule was validated on" (the same lines): HOLDS. "The injured" is `calibration_cohort`, the streams in `CALIBRATION_STREAMS`, battle and non-battle (baseline.py lines 77 and 194 to 202). `milder` compares 0.26514 with E-09's 0.476 at full precision (rules.py lines 190 and 191).
- Cell 10's changed paragraph, its unchanged words: HOLDS. The curves are `net_benefit_table` (decision.py lines 187 to 197), on `diagnosis_inputs()`, the seed-42 sample of 100,000, every stream. Its rows are lens 02's logistic score, lens 04's single tree and forest, the MPTT-24's figure and text readings, flagging every casualty and flagging none, as the paragraph lists them. Each reading's flag is fixed across thresholds and enters `net_benefit` (lines 91 to 96) as true positives less false positives weighted by $t/(1-t)$, so its net benefit changes only through that weight.
- Cell 26's changed paragraph, its unchanged words: HOLDS. The diagnosis column flags lens 02's probability at `threshold(costs)` on `diagnosis_inputs("pre_hospital")` (decision.py lines 659 to 665). The casualties dead from bleeding before pre-hospital care are in `diagnosis_inputs` and are removed by `alive_at_triage` in `_score_pairs` (line 358), which scores the treatment column on battle casualties alone (line 401). The scorecard's rows give "weak" for each of the eight diagnosis rows and "native" for both treatment rows, as the paragraph says.
- The graph: HOLDS. No changed line describes a graph.

## Standing lessons

Each lesson against the changed lines.

- Lesson 1: HOLDS. No changed line applies a trial or registry figure to the casualty. E-09's 47.6% is given with its id and its population, the military registry, as a comparison of cohorts.
- Lesson 2: HOLDS. The change is this lesson's own: the sentence now gives the share in need of the group the figures beside it are on, 16.7% of every stream, beside the injured's 26.5%. E-09's population is quoted as the register gives it, "47.6% Priority 1".

  "The scorecard's figures are on every stream of the military cohort, disease included" now stands as a sentence of its own, in cell 26 and in axis 1 of the figure column. Its words are unchanged. In axis 1 it stands beside the rule's sensitivity and specificity, which are on every stream. In cell 26 it follows the account of the diagnosis and baseline columns, and the sentences after it name the treatment column's group. Each figure in the table that is not on every stream names its own group in its entry: the battle clauses of axis 7 ("Battle casualties alone, where a share of 0.502 need it") and the treatment column ("battle casualties alive at the decision").
- Lesson 3: HOLDS. The panel shows none of the changed strings. Its file, `panel` and `page_panel` are unchanged, and all 1,736 entries are identical to those at the base. `seven_axes`, which writes the changed entry, is called by no file under `app/`.
- Lesson 4: HOLDS. The changed lines state no difference as a sign. "A milder cohort" is in words.
- Lesson 5: HOLDS. The 16.7% and 26.5% rest on the generator alone; no prior and no assumed cost enters them.
- Lesson 6: HOLDS. No figure title has changed.
- Lesson 7: HOLDS. The changed lines are on the diagnosis side: cell 10 under "Diagnosis", cell 26's account of the diagnosis and baseline columns, and axis 1 of the figure column. The treatment column and its description are unchanged.
- Lesson 8: HOLDS. No changed line quotes a performance measured on hospital observations. E-09's row is quoted for its population alone.
- Lesson 9: HOLDS. "100,000", "20", "400,000" and "200,000" are exact, and the 16.7% and 26.5% recompute from 16,704 of 100,000 and 15,016 of 56,634.
- Lesson 10: HOLDS, as set out under the generator and the graph.
- Lesson 11: HOLDS. No changed line says where a rule's items came from, what a source omits or forbids, or why anything was chosen.
- Lesson 12: HOLDS. The one comparison in the changed lines sets the injured's share against E-09's 47.6%. On seeds 43 to 62 that share runs from 25.9% to 26.6%, so "milder" holds on every seed and is not a tie. The 16.7% is a single share, not a comparison.
- Lesson 13: HOLDS. No changed line gives a chance of death. The unchanged words of cell 26's paragraph count expected deaths among battle casualties "alive at the decision", which `_score_pairs` keeps (decision.py line 358).
- Lesson 14: HOLDS. 16.7%, 26.5% and 47.6% are each shown to one place and each rounds from full precision as printed; "milder" is decided at full precision.
- Lesson 15: HOLDS (cells 10, 26 and 27). The injured's "milder" reverses among the battle casualties alone: 50.2% need an intervention against E-09's 47.6%, and 49.3% to 50.2% on seeds 43 to 62. The changed lines confine "milder" to the injured, as before. The battle share is shown in the same notebook and table: cell 12, "among the battle casualties half do"; cell 13, "battle casualties alone 50.2%"; and axis 7 of each classifier column, "a share of 0.502 need it". No line calls the battle casualties milder.
- Lesson 16: HOLDS. D-23's statement, as D-33 restates it, still stands with the rule's accuracy on the generator in each changed place: cells 10 and 26, and axis 1 of the figure column, beside the rule's sensitivity and specificity. It calls the injured milder and no group of battle casualties milder.
- Lesson 17: HOLDS. The changed lines compare no learned model with the baseline.

## Figures

- Cell 11, net benefit across thresholds: HOLDS. The image is byte-identical to the one at the base, and its source, title and `concludes:` tag are unchanged. The paragraph above it in cell 10 now gives the share in need on every stream, 16.7%, the group the figure's title names. It agrees with cell 13's printout and with the curve for flagging every casualty, and changes nothing a reader concludes from the figure.
- The other seven figures (cells 3, 8, 16, 18, 20, 23 and 25): HOLDS. Each image is byte-identical to the one at the base, and each source, title and `concludes:` tag is unchanged.
- App page 1, the decision panel: HOLDS. It holds no figure, and its 1,736 rendered entries are identical to those at the base.

## Limits

None recorded. A re-review after consolidation records no new limits (`docs/BUILD.md` section 5); the limits of the fifth review stand as a record (D-31).

VERDICT: HOLDS

## Reviewed sources

- `notebooks/10_decision_theory.ipynb` 4e9d64f73e5c42fca0b0941dc9582b64b2d9ea3c6bff4924ffc21d3249e7956d
- `src/inference_labs/lenses/decision.py` f6612588c2231dfa9b30a0e8bed2bb3fa3568bf5ecbfc7bc4cde0b10a617f67a
- `app/panels/decision.py` 8fc7fb89f394638291f092de6f3dc73103967cf5e48f8cc57dd43e85663cf6f1
