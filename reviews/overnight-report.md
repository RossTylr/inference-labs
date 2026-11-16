# Overnight run

Unattended run under BUILD.md section 12. One line per unit; the final report follows the table when the run ends.

| Unit | Outcome | Validator verdict | Commit |
|---|---|---|---|
| Steps 1 and 2 | BUILD.md and DESIGN.md amended (D-31, D-32); `deferred` cut to 14 items | Not run | 26d94d2, f8fdd01 |
| U1 | Consolidation after slice 8: all 14 items done, `deferred` empty | Slice 0 BUILT (7/7); slices 1 to 8 REVISE (12/13), G-11 only | 7f59d45 |
| U2 slice 1 | Re-review HOLDS on round 3 (rounds 1 and 2 BREACH: a mislabelled real-data row; no spread for calibration), fixed in e35404d and 978dec9 | BUILT (13/13) | f51299c |
| U2 slice 2 | Re-review HOLDS on round 3 (round 1 BREACH: spread claim; round 2 BREACH: axis 7 with no spread, Brier and over-flagging reversed among battle casualties), fixed in 7bc0832 and 1ba8a5c | BUILT (13/13) | 3c49e84 |
| U2 slice 3 | Re-review HOLDS on round 3 (round 1 BREACH: spread claim, every-stream spread under battle casualties; round 2 BREACH: specificity and over-flagging reverse among the injured and battle casualties), fixed in 1d8b8fd and a75c956. Noted, not marked: the score's calibration shortfall among battle casualties is not shown; axis 7 reverses among non-battle injuries; cell 27 figure labels crowded | BUILT (13/13) | 12b8df4 |
| U2 slice 4 | Re-review HOLDS on round 3 (round 1 BREACH: spread claim, every-stream spread under battle casualties; round 2 BREACH: over-flagging reverses among battle casualties), fixed in 85615f9 and 6e1b2a0. Noted, not marked: disease-only reversals; one forest figure prints -8.7 or -8.8 between runs (ties at the threshold under parallel averaging), so a re-run can change the notebook hash | BUILT (13/13) | b0371a6 |
| U2 slice 5 | Re-review HOLDS on round 2 (round 1 BREACH: every-stream spread joined to the battle sentence), fixed in b953dc2. Noted, not marked: D-23 sentence wider than the treatment column; battle-only decision against rule without a spread (not a tie); decision.py line 57 comment cites E-93 for the reference strategies | BUILT (13/13) | 3ef5eec |
| U2 slice 6 | Re-review HOLDS on round 1. Noted, not marked: two unreachable edge cases in axis7 and rule_cal wording at exactly zero. Run stalled 15 Nov 16:14 to 16 Nov 20:38: the review's hand-back was not delivered until Ross wrote | BUILT (13/13) | d3ee9b7 |
