# inference-labs

A teaching repository: ten ways of reasoning applied to one military casualty, from point of injury to Role 2. Teaching material only; not for clinical use.

## What to do

When Ross says **build**, **review**, **status** or **unstick**, follow [`docs/BUILD.md`](docs/BUILD.md). It tells you how to work out where the build stands and what the single next action is. Do that action and stop.

## Order of authority

1. `docs/PRD.md` — requirements and gates
2. `docs/DESIGN.md` — decisions and reasons
3. `docs/background/` — the published findings each lens is built on
4. `docs/EVIDENCE.md` — the source of every clinical number

## Standing rules

- One slice at a time. Never start a slice the build instruction did not select.
- Build what the requirements list and nothing else. Do not add requirements, documents, agents or process.
- Every clinical number comes from `docs/EVIDENCE.md` with its id. If a number is not there, mark it as an assumption. Do not look one up or invent a source.
- Nothing listed under "What must not be claimed" in a background file may appear in a notebook or the app.
- `generator.py` and `params.yaml` are frozen after slice 1. If a slice seems to need a change, stop and report.
- The validator writes the verdict and the gate tally. Never type them.
- Commit every attempt, whatever its verdict.
- If something cannot be done as specified, stop and record BLOCKED with the reason. That is a legitimate outcome.
- British English. Plain professional prose. No emojis in code, notebooks or documents.
- Notebooks and documents are written in Ross's voice as author, with no reference to how they were produced.
