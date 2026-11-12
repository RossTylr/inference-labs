# 06 — Connectionist models

**The lesson in one line:** a network finds its own features, which is why it can match a specialist and why it can be right for a reason that has nothing to do with the patient.

---

## Anchors

| Id | Finding | Numbers | Limits |
|---|---|---|---|
| E-101 | What is possible with enough labelled images | 128,175 retinal images, each graded 3 to 7 times; AUC 0.991 and 0.990 on two outside sets | A task with abundant, well-labelled data |
| E-98 | A network that learned the hospital | Identified the source hospital for 99.95% of images. Pneumonia prevalence 34.2% at one site, 1.2% at another. Internal AUC 0.931; outside 0.815. Ranking by hospital alone: 0.861 | Three US systems |
| E-99 | Good on average, poor on a subgroup | Relative differences of over 20% on clinically important subsets not labelled in the data | Abstract only |
| E-100 | Shortcuts over signal | COVID radiograph models relied on confounding features and failed in new hospitals | No figures in the abstract |
| E-102 | Deep learning on eFAST | Images from 27 swine. M-mode views above 85% accuracy; B-mode views 68 to 74%; pelvic bleeding 62% | Swine; accuracy only |
| E-103 | Accuracy without the right evidence | Five military working dogs, 327 clips. One model 99.8% at the bladder view; heat maps showed the most accurate models did not always attend to the relevant region | Dogs and a cadaver model |
| E-122 | State of military ultrasound AI | Trained on tissue phantoms, tested on swine; 71.5% on blind inference from a full-torso phantom; a Norwegian forces project with plans and no results yet | No human validation found |
| E-18 | Open human FAST images | None found | Search, not proof of absence |
| E-58 | Backpropagation and the brain | Feedback may approximate error signals locally | A hypothesis |

---

## Thinking

**Two papers, one method, opposite lessons.** E-101 and E-98 use the same kind of network on the same kind of problem. One reaches specialist level and holds up on outside data. The other learns which hospital the film came from, because one hospital had thirty times the pneumonia rate of the other and the films carried the hospital's marks. A model that ignored the lungs entirely and ranked by hospital scored 0.861. The difference between the papers is not architecture. It is whether anything in the image other than the disease predicts the label.

**The military evidence is honest about where it is.** The published work on automating the trauma scan uses swine, dogs and gelatin phantoms (E-102, E-103, E-122). Accuracy on the easier views is above 85% and on the harder ones is in the sixties. No open human image set was found. So this lens cannot teach on the real task, and saying so is part of the lesson. It teaches the method on a proxy (a breast ultrasound set) and labels every result as proxy.

**The failure is already in the military literature.** In E-103 the model with 99.8% accuracy was not always looking at the fluid. A second model with lower headline accuracy had heat maps that matched the right region, and the authors preferred it. That is the shortcut problem found and handled correctly, in a military paper, with five animals. It is a better failure demonstration than any invented one.

**Small animal numbers are a clue.** Twenty-seven swine and five dogs supply thousands of frames, but the frames from one animal resemble each other. E-102 validated by leaving one animal out at a time, which is the right design. A random split of frames would have given a much higher and meaningless score. The notebook can reproduce exactly this on its proxy data: split by image, then split by patient, and watch the score fall.

**What a subgroup hides.** E-99's point is that an average conceals the cases that matter. For a trauma scan the analogue is obvious: performance on a large, easy haemoperitoneum tells you little about a small, early one. The scorecard should require subgroup results, not only an overall figure.

---

## Use in the notebook

| Part | Material |
|---|---|
| Hook | A network can tell which hospital a chest film came from 99.95% of the time. Why is that bad news? |
| By hand | A two-pixel, two-weight "network" trained by hand on eight examples |
| Diagnosis case | Ultrasound classification on the proxy set, split by image and then by patient |
| Treatment case | Weak fit: predicting need for intervention from vital signs, compared with the tree from lens 04 |
| Failure | Plant a marker in the corner of one class, show the accuracy rise and the heat map move to the corner |
| Central figure | What it saw: an image beside its heat map |

## What must not be claimed

- That anything here shows a network can read a military trauma scan in a human. No source does.
- That E-99's pneumothorax and chest drain example is in the abstract. It is commonly cited from the paper and was not in what was read.

## Open items

- Authors for E-102, E-103 and E-122 (O-8).
