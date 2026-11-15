# Overnight run

Unattended run under BUILD.md section 12. One line per unit; the final report follows the table when the run ends.

| Unit | Outcome | Validator verdict | Commit |
|---|---|---|---|
| Steps 1 and 2 | BUILD.md and DESIGN.md amended (D-31, D-32); `deferred` cut to 14 items | Not run | 26d94d2, f8fdd01 |
| U1 | Consolidation after slice 8: all 14 items done, `deferred` empty | Slice 0 BUILT (7/7); slices 1 to 8 REVISE (12/13), G-11 only | 7f59d45 |
| U2 slice 1 | Re-review HOLDS on round 3 (rounds 1 and 2 BREACH: a mislabelled real-data row; no spread for calibration), fixed in e35404d and 978dec9 | BUILT (13/13) | f51299c |
| U2 slice 2 | Re-review HOLDS on round 3 (round 1 BREACH: spread claim; round 2 BREACH: axis 7 with no spread, Brier and over-flagging reversed among battle casualties), fixed in 7bc0832 and 1ba8a5c | BUILT (13/13) | 3c49e84 |
| U2 slice 3 | Re-review HOLDS on round 3 (round 1 BREACH: spread claim, every-stream spread under battle casualties; round 2 BREACH: specificity and over-flagging reverse among the injured and battle casualties), fixed in 1d8b8fd and a75c956. Noted, not marked: the score's calibration shortfall among battle casualties is not shown; axis 7 reverses among non-battle injuries; cell 27 figure labels crowded | BUILT (13/13) | 12b8df4 |
