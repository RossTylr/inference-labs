# Read-through: notebooks 00 to 11

Read in order from the committed notebooks and their outputs. Cells count from 0.

## Does the thread hold?

Mostly. Every notebook keeps one order, every hook is answered, and the backward links are accurate. Three places strain:

- From 00 onward axis 7 shows flagging every battle casualty beating every method, but the reason waits for 10 (01 cell 40, 02 cell 28, 04 cell 27).
- 03 cell 19 and 10 cell 19 cite "the walk-through", which is in the app. Casualty 1 in 10 cell 22 (8.1%, 40 minutes) matches 03's casualty in cell 18 (8%, 39.9 minutes), but neither says so.
- The D-23 sentence calling the injured "a milder cohort" sits on scorecards of battle casualties alone (03 cell 42, 07 cell 37), 50.2% of whom are in need. 00 cell 25 and 11 cell 11 add the corrective sentence; 01 cell 41, printing 00's scorecard, does not.

## Quantities that differ

1. Bleeding into the abdomen (free fluid, one generator variable) among battle casualties. Its share: 03 cell 17, 12.3% (724 of 5,882); 07 cell 15, 12.7% (3,805 of 29,925). The MPTT-24's Priority 1 against it: 03 cell 43, sensitivity 0.577, specificity 0.578, Brier 0.422; 07 cell 38, 57.1%, 57.4%, 0.426. Different samples, not errors: 03 counts its prior on 20,000 casualties (seed 1) and scores on 30,000; 07 uses 100,000. 11 cell 27 (rows 8 to 11, 16 to 19) sets both side by side without the sample.
2. The generator's relative risk with tranexamic acid, 1 to 3 hours and over 3 hours: 05 cell 22, 0.791 and 1.439; 07 cell 25, 0.77 and 1.17. Different measures: 05 sums each casualty's chances, 07 counts realised deaths (7 in the late band). Not an error; 05 does not say its figure is an expectation.
3. MPTT-24 figure-reading sensitivity, civilian cohort: 01 cell 37, 0.524; 02 cell 13, 0.525. Same casualties; the value is 0.5245, rounded twice in 01. A small error.

The rule's sensitivity is 62.7% (figure) and 64.1% (text) both for the injured (01 cell 13, 02 cell 13) and for battle casualties alone (06 cell 17, 09 cell 13). In the generator no non-battle injury needs a life-saving intervention, so the two groups hold the same casualties in need. No notebook says so, yet it is why the injured look milder.

## Terms used before they are explained

- Need for a life-saving intervention: every diagnosis target from 00 cell 25; defined in 08 cell 8.
- Brier score: every scorecard from 00 cell 25; defined only for a rule.
- GCS (00 cell 24) and eFAST (02 cell 17): never expanded.
- AVPU: letters in 01 cells 2 and 6; the scale in 06 cell 16.
- Roles 1 and 2: from 00 cell 3; described in 08 cells 4 and 22. Role 3 first appears in 07 cell 0.
- E- and D- numbers (00 cells 0 and 4) and "the register" (01 cell 4): never introduced.

## Three changes that would most help a reader

1. Add a short glossary to notebook 00 covering the terms above and what the E- and D- numbers point to.
2. State in 00 that only battle casualties ever need an intervention in the generator, and make the D-23 sentence match the group each scorecard reports.
3. Print the MPTT-24 baseline columns once, in 01; in later scorecards show only what differs, naming the sample behind each figure. The repetition buries each lesson.
