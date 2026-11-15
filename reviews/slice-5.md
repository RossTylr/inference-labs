# Review of slice 5: lens 10, Decision theory

**Date:** 15 November 2026 · **Author:** Ross Taylor

Seventh review, and the second re-review after the consolidation after slice 8 (commit 7f59d45), under `docs/BUILD.md` section 5 and D-31. The base is still commit 3ea84e0, the last that changed this file. Only the lines changed between 3ea84e0 and the current head, b953dc2, are checked, against every item below and each standing lesson in `docs/BUILD.md` section 8. The sixth review read the files at e5675a4 and recorded one breach: in cell 27, axis 7 of the diagnosis column, the decision's net benefit less the rule's, +2.3 to +2.6 per 100, a figure on every stream, named no group and was joined by a semicolon to the sentence on the battle casualties alone. Since then, in commit b953dc2, decision.py lines 717 and 718 join that entry's parts with full stops and name the group: the entry now reads "... flag every casualty 44.6 (mechanism). On every stream, across 20 further samples its net benefit less that of the MPTT-24 (figure) is higher: the difference runs from +2.3 to +2.6 per 100 across 20 seeds. Among the battle casualties alone, across 20 further samples its net benefit less that of flagging every casualty is lower: the difference runs from -3.7 to -3.2 per 100 across 20 seeds". Cell 27's output changes in that entry only, and in the padding of its column in the plain-text view. Nothing else a reader sees has changed since e5675a4, and outside the review sources only `LEDGER.md` and the verdict file have. A breach in any other changed line is one the sixth review should have recorded, and would be marked MISSED. Cells are numbered from 0 in file order; the notebook has 31 cells. Line numbers are those of the file named, at b953dc2; b953dc2 added and removed no line, so they are also those of e5675a4.

What changed since 3ea84e0, in all:
- **Notebook, commit 7f59d45.** Cell 2, the technical register, renames treating everyone and no one as flagging every casualty and flagging none. Cell 10 renames them and replaces its D-23 sentence, no longer citing E-01. Cell 11 changes its legend labels, its table's column labels and the wording of its `concludes:` tag. Cells 12 and 13 change in naming only. Cell 26 gains E-93's account of net benefit, the sentence on spreads across 20 further samples, the D-23 sentence and a sentence on casualties dead before pre-hospital care. Cell 27 displays `seven_axes` and prints those casualties' count; its table gains the spreads in axes 1, 2 and 7 of the diagnosis column, "where lower is better" in axis 2, the D-23 sentence in axis 1 of the figure column, "per 100" and "(mechanism)" in each battle clause of axis 7, and the new naming. Cell 28's metrics gain "where lower is better" and "where fewer is better". Cell 29's diagnosis paragraph gains the spreads.
- **Notebook, commit b953dc2.** Cell 27's axis 7 entry of the diagnosis column, as above.
- **Library, commit 7f59d45.** In `decision.py`: lines 37 and 55 to 63, the constants `SPREAD_SEEDS`, `FLAG_ALL`, `FLAGGING_ALL` and `NET_BENEFIT_MEANING`; lines 99 to 169, `flag_all` (formerly `treat_all`), `as_flag`, `across_seeds`, `spread_words` (moved here and given `places`, `lower` and `higher`), `need_spread` and `versus`; lines 188 to 197, naming in `net_benefit_table`; lines 399 to 406 and 471 to 480, `aircraft_spread` and `torso_spread` rewritten on `across_seeds`; line 455, `alive_at_triage` now `~baseline.died_before_care`; lines 487 to 512, naming and the battle clause in `_worse`, `_nb_text` and `decision_value`; lines 528 and 529, naming in `battle_reversal`; lines 552 to 582, `bayesian_spread` and the spreads added to `bayesian_decision_value`; lines 618, 619 and 628, the scorecard's metric names; lines 646 to 663, `_diagnosis_methods`, `diagnosis_spread` and the docstring of `seven_axes`; lines 672 to 720, the entries of `seven_axes` listed above.
- **Library, commit b953dc2.** `decision.py` lines 717 and 718, as above.

`app/panels/decision.py`, `panel` and `page_panel` in the lens module, `generator.py`, `params.yaml` and `docs/background/10-decision-theory.md` are unchanged since 3ea84e0. In `docs/EVIDENCE.md` only the row of E-104 has changed, which this slice does not cite.

These were read in full: the notebook, `decision.py` and `app/panels/decision.py`. These were read for the words and figures they put in the changed lines: `baseline.py` lines 70, 166 to 191 and 194 to 202 (`generator_sample`, `died_before_care`, `died_before_care_count`, `died_before_care_note`, `calibration_cohort`, `calibration_need`); `rules.py` lines 145, 164 to 172 (`d23_sentence`) and 198 to 206 (`_battle`, `battle_sample`); `generator.py` lines 240 and 241, 298 to 305 and 362 to 369 (`p0`, line 367; `died_untreated`, line 369), and the truth columns at lines 392 and 417 to 424; and `params.yaml` line 25. The axis 7 entries that `decision_value`, `versus` and `bayesian_decision_value` return to lenses 01, 02, 03 and 04 were regenerated at b953dc2 and read. The evidence register rows cited in the changed lines, E-09 and E-93, were opened with E-01, and the populations of their sources were read in `library/curated.yaml`.

The notebook was run top to bottom from a fresh kernel into a scratch copy in 31.4 seconds without error. Its reader view matches the committed file exactly, so the hash below, taken of the committed file, is also that of the fresh run. Its eight images match the committed ones byte for byte. Seven are byte-identical to those at 3ea84e0; cell 11's differs in its legend only, and was viewed beside the one at 3ea84e0. Slice 5's tests pass (17). Gates G-6, G-8 and G-10, called on their own without writing, pass. The decision panel was rendered through `decision.page_panel` for every casualty app page 1 can show, all three patient types in both settings, 1,736 entries, at 3ea84e0 (from an archive of that commit) and at b953dc2. The two sets are identical. Every entry has its heading, costs line and evacuation line, and none holds an unformatted or missing value. Every figure in the changed lines was recomputed at full precision from `generator.sample`, `frequentist.probability`, `baseline.priority_one` and `bayesian.beliefs`, without the lens's spread helpers. The recomputation used the seed-42 sample and seeds 43 to 62, 100,000 casualties each. Each comparison was recomputed on every stream, among the battle casualties, the injured, the non-battle injuries and the disease admissions, and with the casualties dead before pre-hospital care left out.

No breach is found, and none is missed. The sixth review's finding is resolved. The decision's net benefit less the rule's now opens "On every stream", is computed on every stream, and stands in its own sentence, apart from the one on the battle casualties alone.

## What must not be claimed

- That the civilian benchmark applies to military triage: HOLDS (changed lines of cells 2, 10 to 13 and 26 to 29; decision.py lines 37 to 169, 188 to 197, 399 to 582 and 618 to 720). No changed line mentions the benchmark, E-87, under-triage or over-triage. Every changed figure is of the generator's military cohort, measured against need for a life-saving intervention, against flagging every casualty, or, in lens 03's strings, against bleeding into the abdomen. None is measured against the benchmark. The lines new in b953dc2 add no figure.
- That PATCH shows extra survivors were left with poor function: HOLDS (the same lines). No changed line mentions PATCH, E-78 or functional outcome.
- A specific exchange rate between a miss and a false alarm: HOLDS (cells 26, 27 and 29; decision.py lines 59 to 63, 492 to 495 and 677 to 720). Every axis 7 entry keeps "with a miss weighed 9 times a false alarm (an assumption)", and the sentences new in b953dc2 follow it in the same entry and add no weight. Axis 2 gives the expected cost "at the stated costs (assumptions)", and its spread follows "at the default costs". Cell 26 and `NET_BENEFIT_MEANING` attribute to E-93 only that the threshold probability "encodes how a false alarm is weighed against a miss", which is the register's row. They give no weight. Cell 29's new figures stand under its opening "At the default costs".

## Epistemic checks

- Accuracy quoted for the wrong cohort or setting: HOLDS (cell 27, axes 1, 2 and 7; cells 10, 26 and 29; decision.py lines 131 to 169, 552 to 582 and 672 to 720). The entry new in b953dc2 names its groups, "On every stream" and "Among the battle casualties alone", and each figure is computed on the group it names. The first comes from `sp["net benefit: ..."]` (decision.py lines 153 and 718), recomputed as +2.259 to +2.637 on every stream. The second comes from `sp["net benefit, battle: ..."]` (lines 154, 148 and 719 to 720), recomputed as -3.675 to -3.186 among the battle casualties. Every other changed figure names its group, or stands in an entry or sentence that does, and is computed on it:
  - axes 1 and 2 of the diagnosis column: "all 100,000 synthetic casualties of the military cohort, disease included", then "Across 20 further samples". These are drawn by `need_spread` on 100,000 of the military cohort, every stream (lines 143 to 146; `generator.sample` defaults to the military cohort, `params.yaml` line 25);
  - cell 29: "on all 100,000 synthetic casualties", then "Among the battle casualties alone";
  - cells 10 and 26 and axis 1 of the figure column: the 26.5% "for the injured only", which is `baseline.calibration_need`, the battle and non-battle streams (baseline.py lines 194 to 202);
  - lens 03's strings: the evaluation sample's and the further samples' battle casualties against bleeding into the abdomen (lines 562 and 576), as the docstrings say.

  The diagnosis uses no scan, so the setting does not bear on these figures; axis 6 says so, and the scorecard's in-hospital rows equal the rows before hospital. Lens 03's spreads are drawn in the setting each column names (line 562).
- Proxy data read as the real thing: HOLDS (cells 10, 11, 13 and 26 to 29; decision.py lines 131 to 169 and 552 to 720). Every changed figure is computed on the generator's synthetic casualties. Each stands in a row labelled "(mechanism)", or in an entry that says "(mechanism)" before it, or in a sentence that says "(mechanism)" or "synthetic". The sentences new in b953dc2 follow "flag every casualty 44.6 (mechanism)." in the same entry, and cell 26 says what the spreads are drawn from. The docstrings of `need_spread`, `diagnosis_spread` and `bayesian_spread` say "(mechanism)". No changed figure is set beside a published one except E-09's 47.6%, given as a comparison of cohorts.
- Civilian data read as military: HOLDS (cells 10 and 26; cell 27, axis 1 of the figure column). The changed lines cite only E-09 and E-93. E-09 is cited for 47.6% Priority 1 "in the military registry". That is the JTTR row of `vassallo2017d`, whose population is recorded as mixed. E-93, `vickers2006`, is a method, recorded as not applicable. G-10 passes.
- A diagnosis result read as a treatment result: HOLDS (cells 2, 10 to 13 and 26 to 29; decision.py lines 57, 58, 99 to 102 and 485 to 495). The renaming takes "treat" out of the diagnosis comparison: net benefit's reference strategies are now "flag every casualty" and "flag none". The sentences new in b953dc2 compare flags against need for a life-saving intervention, in the diagnosis column. The other new spreads are in the same column, in cell 29's paragraph headed **Diagnosis**, and in lens 03's flags against bleeding into the abdomen. None gives the effect of any treatment. The treatment column and rows 8 and 9 of cell 28 change only in "where fewer is better".

## Numbers and their evidence ids

- The figures in axis 7 of the diagnosis column, cell 27 (decision.py lines 717 to 720): HOLDS. No evidence id is due. Net benefit per 100, the decision less the figure reading, runs from +2.259 to +2.637 on every stream. Among the battle casualties alone, the decision less flagging every casualty runs from -3.675 to -3.186. They print as +2.3 to +2.6 and -3.7 to -3.2. The seed-42 figures before them, 10.470, 7.449, 0.50179, 41.236 and 44.643, print as 10.5, 7.4, 0.502, 41.2 and 44.6.
- The spreads in axes 1 and 2 of the diagnosis column, cell 27 (decision.py lines 681 to 702): HOLDS. On seeds 43 to 62, every stream, the decision flags lens 02's probability at 0.10. Against the figure reading:
  - its sensitivity less the figure reading's runs from +25.891 to +27.323 points;
  - its specificity less the figure reading's from -22.072 to -21.203;
  - its expected cost per 100 at nine to one less the figure reading's from -23.731 to -20.333.

  They print as +25.9 to +27.3, -22.1 to -21.2 and -23.7 to -20.3. `need_spread` takes a probability not named in `own` at the common threshold (line 152), so "at the default costs" is right.
- Cell 29's figures: HOLDS. "Its expected cost lies 20.3 to 23.7 per 100 below the rule's, and its net benefit 2.3 to 2.6 per 100 above it" are the every-stream spreads above, in a paragraph that names all 100,000 synthetic casualties. "Among the battle casualties alone, flagging every casualty has a higher net benefit than either, by 3.2 to 3.7 per 100 over the decision on every sample" holds. Over the figure reading the margin runs from +14.233 to +15.114 on every sample.
- The seed-42 figures reprinted in the changed rows: HOLDS. These were recomputed:
  - 86.530% and 56.955%, 59.992% and 78.558%, and 61.440% and 77.797%;
  - expected costs 56.105, 78.007 and 76.463;
  - net benefit 10.470, 8.037 and 8.208 against 7.449;
  - among the battle casualties, 0.50179, 41.236, 29.999 and 30.700 against 44.643.

  Each prints as shown, and cell 13's table recomputes. The count of 482 dead before pre-hospital care among the 100,000 recomputes, and all 482 are battle casualties.
- The 26.5% and E-09's 47.6% (cells 10 and 26; cell 27, axis 1 of the figure column; rules.py lines 145 and 164 to 172): HOLDS. The 26.5% is `baseline.calibration_need("military")`, 0.26514, the share in need among the seed-42 sample's battle and non-battle injuries. E-09's row gives 47.6% Priority 1 among the JTTR's 3,654 adults. The comparison and "the one the rule was validated on" are D-23's words. Dropping E-01 from cell 10 leaves no number without its id; E-01 gives the same 47.6% for the same 3,654.
- E-93 (cells 2, 10 and 26; decision.py lines 57 and 59 to 63): HOLDS. The register row reads "A model is judged by its consequences: net benefit across a range of threshold probabilities, where the threshold encodes how a false positive is weighed against a false negative". Cell 26 and `NET_BENEFIT_MEANING` say no more of E-93. They give the computation and the two reference strategies as "here". The comment at line 57 cites E-93 for net benefit, the row's subject; no reader sees it.
- The strings `decision_value`, `versus` and `bayesian_decision_value` return to other lenses (decision.py lines 165 to 169, 485 to 513 and 552 to 582): HOLDS. Each was regenerated at b953dc2 and read; none changed in b953dc2.
  - The qualifiers stand against their numbers. "Below flagging every casualty" stands for 41.2, 41.3, 41.3, 30.0 and 30.7 against 44.6, and for the ABC score's 8.2 against 29.1. "It flags every casualty at this threshold" stands for the treatment tree, 29.1 against 29.1, where every casualty is flagged. Lens 03's 4.3, 9.3 and 3.1 against 3.0 carry none.
  - Lens 03's spreads recompute without the helper. The belief less the figure reading runs from +0.623 to +1.358 before hospital and from +5.633 to +6.378 in hospital. The figure reading less flagging every casualty runs from +0.157 to +0.486 in both settings. These print as +0.6 to +1.4, +5.6 to +6.4 and +0.2 to +0.5.

## The generator and the graph

- `alive_at_triage` and the casualties dead before pre-hospital care (cells 26 and 27; decision.py line 455; baseline.py lines 172 to 191): HOLDS.
  - `baseline.died_before_care` is the base's expression for those not alive at triage. It takes the generator's bleeding death without tranexamic acid (`died_if_untreated`, generator.py line 369, drawn on `p0`, line 367) at or before the time of pre-hospital care. The outputs of cells 23 and 25, which rest on it, are unchanged.
  - The diagnosis and baseline columns, and the spreads behind them, use every casualty (lines 177 and 144). `_score_pairs` keeps only those alive at `t_phec_min`, the time of the decision (lines 358, 359 and 364). So "counted in the diagnosis column and left out of the treatment column" is right.
  - The printed "No casualty ... is among the battle casualties alive at the decision behind the treatment column" is counted on the seed-42 sample. The treatment column is drawn from seeds 43 to 62, and the statement holds there by the same filter.
- `need_spread`, `across_seeds`, `spread_words`, `versus`, `diagnosis_spread`, `bayesian_spread` and `seven_axes`, docstrings and comments (lines 55, 56, 113 to 169, 552 to 568 and 654 to 663): HOLDS.
  - Each sample is `generator.sample(100,000, seed)` on seeds 43 to 62 (`EVAL_N`, `EVAL_SEED` = 42, baseline.py line 70), military cohort, every stream. The battle casualties are its battle stream (decision.py line 146; rules.py lines 198 to 200).
  - Net benefit at 0.10, expected cost per 100 at the default costs, and sensitivity and specificity are computed as the docstrings say. A spread is called a tie only where it covers zero (line 126).
  - `aircraft_spread` and `torso_spread` draw on the same seeds and pair seeds as at the base (lines 399 to 406 and 471 to 480). Rows 8 and 9 of cell 28 and the output of cell 25 are unchanged.
- Cell 2's and cell 26's account of net benefit: HOLDS. Net benefit is computed per 100 as those correctly flagged less those wrongly flagged, the second weighted by the threshold over one minus it. It is set against flagging every casualty, $\pi - (1-\pi)\,t/(1-t)$, and against flagging none at zero. That is `net_benefit` and `flag_all` (lines 91 to 102).
- Cell 11's `concludes:` tag: HOLDS. On the seed-42 sample, each learned model's net benefit is at or above each reading's at all 60 thresholds; the least margin is +0.086. Both readings fall below flagging every casualty at 0.01 to 0.09, and below zero from 0.36 to 0.60.
- The graph: HOLDS. No changed line describes a graph.

## Standing lessons

Each lesson against the changed lines.

- Lesson 1: HOLDS. No changed line applies a trial or registry figure to the casualty. E-09's 47.6% is given with its id and its population, the military registry, as a comparison of cohorts.
- Lesson 2: HOLDS. The sixth review's finding is resolved: the comparison with the rule in axis 7 now opens "On every stream", and the comparison with flagging every casualty opens "Among the battle casualties alone". Every other changed figure names its group, as set out under the first epistemic check.

  The D-23 sentence opens "The scorecard's figures are on every stream of the military cohort, disease included". In axis 1 it stands beside the rule's sensitivity and specificity, which are on every stream. In cell 26 the sentences after it name the treatment column's group. Each figure in the table that is not on every stream, in the battle clauses and the treatment column, names its own group in its entry.
- Lesson 3: HOLDS. The app shows none of the changed strings. The panel's file, `panel` and `page_panel` are unchanged, and all 1,736 entries are identical to those at the base.
- Lesson 4: HOLDS. Each difference in the changed lines names its direction in words: "higher", "lower" or "below flagging every casualty". Axis 2 and the scorecard's metrics add "where lower is better" and "where fewer is better".
- Lesson 5: HOLDS. The spreads of expected cost and net benefit are driven by the assumed costs. Each stands in an entry that says "(assumptions)" or "(an assumption)", or under cell 29's "At the default costs", which cells 3 and 4 call an assumption.
- Lesson 6: HOLDS. Cell 11's title is unchanged, and it describes what is plotted.
- Lesson 7: HOLDS. The new figures stand in the diagnosis column and cell 29's paragraph headed **Diagnosis**. The treatment column changes only in "where fewer is better".
- Lesson 8: HOLDS. No changed line concerns hospital observations or the point of injury.
- Lesson 9: HOLDS. "20 further samples", "20 seeds", "100,000" and "482" are exact.
- Lesson 10: HOLDS, as set out under the generator and the graph.
- Lesson 11: HOLDS. No changed line says where a rule's items came from, what a source omits or forbids, or why anything was chosen.
- Lesson 12: HOLDS (cells 26, 27 and 29; decision.py lines 120 to 169 and 681 to 720). Every comparison the table states in words carries its spread, and none is a tie. Cell 28's rows repeat the same comparisons of the decision with the rule on the seed-42 sample in both settings. Their spreads are in cell 27, and the diagnosis uses no scan.

  The table also sets values side by side without a spread, across its columns. None of those is a tie on seeds 43 to 62:
  - the decision against the text reading: sensitivity +24.3 to +25.7 points, specificity -21.3 to -20.4, expected cost -21.5 to -18.7 and net benefit +2.1 to +2.4;
  - the decision against the figure reading among the battle casualties: +10.9 to +11.7;
  - the decision against flagging every casualty on every stream: +3.0 to +3.2;
  - the text reading against the figure reading: +0.16 to +0.24 on every stream and +0.7 to +1.0 among the battle casualties;
  - the readings against flagging every casualty: +0.4 to +0.8 and +0.7 to +1.0 on every stream, and -15.1 to -14.2 and -14.2 to -13.3 among the battle casualties.
- Lesson 13: HOLDS. No changed line gives a chance of death. The count dead before care is a count, and the treatment column keeps only those alive at the decision.
- Lesson 14: HOLDS. The spreads are given to one place, as are the values beside them. Each end rounds from full precision as printed. In each battle clause the share in need and the threshold are both shown to three places.
- Lesson 15: HOLDS (cells 27 and 29; decision.py lines 681 to 720). The decision against flagging every casualty reverses among the battle casualties, where it is shown. Among the injured as a whole it is +0.1 to +0.5, among the non-battle injuries +4.3 to +4.5, and among the disease admissions +6.6 to +6.8. Against the figure reading, each comparison keeps its sign among the battle casualties, the injured and the disease admissions:
  - sensitivity +25.6 to +27.2 points among the battle casualties and the injured, and +28.2 to +32.1 among the disease admissions;
  - specificity lower in every group;
  - expected cost lower among the battle casualties (-105.3 to -98.0), the injured (-39.9 to -35.2) and the disease admissions (-2.4 to -0.9);
  - net benefit higher among the battle casualties (+10.9 to +11.7), the injured (+3.9 to +4.4) and the disease admissions (+0.1 to +0.3).

  Expected cost and net benefit change sign only among the non-battle injuries, of whom none needs an intervention, so every flag there is a false alarm (+33.6 to +34.8 and -3.9 to -3.7). The notebook reports that stream alone nowhere. As in this consolidation's re-reviews of slices 2 to 4, and in the sixth review, a reversal confined to that stream is not marked. With the casualties dead before pre-hospital care left out, every comparison keeps its sign: net benefit against the figure reading +2.1 to +2.5 on every stream, and against flagging every casualty -3.6 to -3.1 among the battle casualties.
- Lesson 16: HOLDS. The D-23 sentence stands in cells 10 and 26 and in axis 1 of the figure column. That is the same row as the decision's comparison with the rule's sensitivity and specificity.
- Lesson 17: HOLDS. Where the decision does worse, the scorecard and cell 29 report it with its spread. It does worse in specificity, and against flagging every casualty among the battle casualties; the second is now in a sentence of its own.

## Figures

- Cell 11, net benefit across thresholds: HOLDS. The figure changes in its legend only, "flag every casualty" and "flag none" for "treat all" and "treat none". Every curve, the axes and the title are as at the base. Its `concludes:` tag changes in the same words and holds, as set out above. What a reader concludes from it is unchanged.
- The other seven figures (cells 3, 8, 16, 18, 20, 23 and 25): HOLDS. Each image is byte-identical to the one at the base, and each source, title and `concludes:` tag is unchanged.
- App page 1, the decision panel: HOLDS. It holds no figure, and its 1,736 rendered entries are identical to those at the base.

## Limits

None recorded. A re-review after consolidation records no new limits (`docs/BUILD.md` section 5); the limits of the fifth review stand as a record (D-31).

VERDICT: HOLDS

## Reviewed sources

- `notebooks/10_decision_theory.ipynb` 0c0e3ba440932e73517dd8170e7192243855091d641c846e883b79d3d7bb1dd3
- `src/inference_labs/lenses/decision.py` f6612588c2231dfa9b30a0e8bed2bb3fa3568bf5ecbfc7bc4cde0b10a617f67a
- `app/panels/decision.py` 8fc7fb89f394638291f092de6f3dc73103967cf5e48f8cc57dd43e85663cf6f1
