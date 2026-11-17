"""What app pages 2 to 4, the lens pages and the gallery show (PRD R-11.12). Every number on those pages is formatted
here, so a page shows only what the library computed (gate G-8), and every page runs on the generator's synthetic
casualties or on what the executed notebooks hold (gate G-9).

    mix_and_setting   every method that flags need for a life-saving intervention, re-scored on synthetic casualties
                      of the mix and setting the reader chooses
    lens_table        every lens's scorecard rows for one case, generated from the scorecards (thread.lens_table)
    graph_explorer    the capability chain for an injury, the provenance of every generator parameter and what depends
                      on one evidence id, and the edge from mechanism to bleeding site read three ways
    lens_page         a lens notebook's general explainer and central figure, as last run
    gallery           the figures of the executed notebooks

The lens pages and the gallery read the notebooks in the repository's notebooks folder, as executed and saved. A
figure there is what the notebook drew on its last run; its controls are changed in the notebook.

Every result computed here on the generator is a mechanism, not evidence (D-8).
"""
from __future__ import annotations

import base64
import json
from functools import lru_cache
from pathlib import Path

import numpy as np
import pandas as pd

from inference_labs import NOT_FOR_CLINICAL_USE, baseline, generator, thread
from inference_labs.graph.provenance import ROOT

NOTEBOOKS = ROOT / "notebooks"
CENTRAL = "central"
CASES = ("diagnosis", "treatment")
CASE_NAMES = {"diagnosis": "Diagnosis", "treatment": "Treatment"}
MIX_N, MIX_SEED = 20_000, baseline.EVAL_SEED
LENS_NUMBERS = ("01", "02", "03", "04", "05", "06", "07", "08", "09", "10")
MECHANISM_NOTE = ("Every figure computed here is on synthetic casualties and is a mechanism: it can only confirm the "
                  "model that made it.")


def _pct(x: float, places: int = 1) -> str:
    return f"{100 * x:.{places}f}%"


def _table(df: pd.DataFrame) -> list[dict]:
    """A table as rows of strings, so the page shows exactly what is formatted here."""
    return [{str(k): str(v) for k, v in row.items()} for row in df.to_dict(orient="records")]


# ------------------------------------------------------------------------------------------------ page 2: mix and setting

def mix_defaults() -> dict[str, int]:
    """The default mix in whole per cent, as params.yaml holds it (E-34 to E-36)."""
    return {s: int(round(100 * v)) for s, v in thread.stream_shares().items()}


SETTINGS = baseline.SETTINGS
SETTING_NAMES = baseline.SETTING_NAMES
NOT_MOVED = (
    ("01 Rules, treatment case", "the ABC score is scored on battle casualties"),
    ("03 Bayesian", "its belief is about bleeding into the abdomen in battle casualties, who alone are scanned"),
    ("04 Decision trees, treatment case", "the treatment tree is scored on battle casualties"),
    ("05 Stochastic processes", "its chance is for battle casualties bleeding significantly and alive at pre-hospital "
                                "care"),
    ("06 Connectionist, image case", "it runs on constructed images, not on the generator's casualties"),
    ("07 Causal", "its estimates are on battle casualties under a constructed allocation of tranexamic acid"),
    ("09 Reinforcement learning, treatment case", "it runs on a constructed decision process, not on the generator's "
                                                  "casualties"),
)


def _flags(observed: pd.DataFrame) -> dict[str, np.ndarray]:
    """Each method's flag for need of a life-saving intervention, each at the threshold its own lens sets."""
    from inference_labs.lenses import connectionist, decision, frequentist, hybrids, knowledge, reinforcement, trees

    p_score = frequentist.probability(observed)
    p_trees, m = trees.probabilities(observed), trees.models()
    return {
        "MPTT-24, figure (as published)": baseline.priority_one(observed, "figure"),
        "MPTT-24, text (as validated)": baseline.priority_one(observed, "text"),
        "logistic score (lens 02), its own threshold": p_score >= frequentist.fitted_score().threshold,
        "single tree (lens 04), its own threshold": p_trees["single tree"] >= m.tree_threshold,
        "forest (lens 04), its own threshold": p_trees["forest"] >= m.forest_threshold,
        "signs network (lens 06), its own threshold":
            connectionist.signs_probability(observed) >= connectionist.signs_network().threshold,
        "knowledge graph (lens 08), any candidate": knowledge.score_matrix(observed).max(axis=1) > 0,
        "question policy (lens 09)": reinforcement.policy_output(observed)["flag"],
        "decision theory (lens 10), lens 02's score at the cost threshold": p_score >= decision.threshold(),
        "prediction sets on the single tree (notebook 11), set holds need": hybrids.flags(hybrids.TREE, observed),
    }


def _net_benefit(nb: float) -> str:
    """Net benefit per 100, with a value below zero said in words (lesson 4)."""
    from inference_labs.lenses import decision

    return f"{100 * nb:.1f}" + (f" (below zero: worse than {decision.FLAGGING_NONE})" if nb < 0 else "")


def _mix_rule(observed: pd.DataFrame, need: np.ndarray) -> str:
    """D-23's comparison made on the injured of the mix chosen, beside D-23's own statement for the default mix: the
    share of the injured in need against the share Priority 1 in the military registry (E-09)."""
    from inference_labs.lenses import rules

    registry = rules.PUBLISHED["MPTT-24, military"].prevalence
    injured = baseline.calibration_cohort(observed)
    head = (f"The MPTT-24's figures on this page are on the {MIX_N:,} synthetic casualties of the mix chosen here; the "
            f"comparison with E-09 holds for the injured only.")
    if injured.any():
        share = float(need[injured].mean())
        kind = "a milder cohort than" if share < registry else "not a milder cohort than"
        here = (f"Among the injured of this mix, {_pct(share)} need a life-saving intervention against "
                f"{_pct(registry)} Priority 1 in the military registry (E-09), so here they are {kind} the one the "
                f"rule was validated on.")
    else:
        here = "No casualty of this mix is injured, so the comparison cannot be made on it."
    default = (f"D-23 describes the default mix: among the injured of its {baseline.EVAL_N:,} synthetic casualties "
               f"(seed {baseline.EVAL_SEED}), {_pct(baseline.calibration_need('military'))} need one, a milder cohort "
               f"than the one the rule was validated on.")
    return " ".join((head, here, default))


@lru_cache(maxsize=32)
def mix_and_setting(disease: int = 44, battle: int = 30, non_battle: int = 27, setting: str = "pre_hospital") -> dict:
    """Page 2. The methods that flag need for a life-saving intervention, scored on 20,000 synthetic casualties (seed
    42) of the mix and setting chosen: sensitivity, specificity, positive predictive value and net benefit at 0.10, with
    flagging every casualty beside them (mechanism). The models were fitted on the default mix and are not refitted."""
    from inference_labs.lenses import decision

    raw = {"disease": float(disease), "battle": float(battle), "non_battle": float(non_battle)}
    total = sum(raw.values())
    head = {"title": "Mix and setting", "caption": NOT_FOR_CLINICAL_USE}
    if total <= 0:
        return {**head, "status": "Choose a share above zero for at least one stream.", "mix": "", "need": "",
                "table": [], "rule": "", "not moved heading": "", "not moved": [], "note": ""}
    mix = {k: v / total for k, v in raw.items()}
    observed, truth = generator.sample(MIX_N, MIX_SEED, mix=mix, setting=setting, return_truth=True)
    need = truth["needs_lsi"].to_numpy(bool)
    t = decision.threshold()
    rows = []
    for name, flag in _flags(observed).items():
        flag = np.asarray(flag, bool)
        hits = int((flag & need).sum())
        rows.append({"method": name,
                     "sensitivity": _pct(hits / need.sum()) if need.any() else "no one in need",
                     "specificity": _pct(float((~flag[~need]).mean())) if (~need).any() else "everyone in need",
                     "positive predictive value": _pct(hits / flag.sum()) if flag.any() else "flags no one",
                     "net benefit per 100 at the threshold": _net_benefit(decision.net_benefit(flag, need, t))})
    rows.append({"method": decision.FLAG_ALL, "sensitivity": _pct(1.0) if need.any() else "no one in need",
                 "specificity": _pct(0.0) if (~need).any() else "everyone in need",
                 "positive predictive value": _pct(float(need.mean())),
                 "net benefit per 100 at the threshold": _net_benefit(decision.flag_all(need, t))})
    shown = ", ".join(f"{thread.STREAM_NAMES[s]} {_pct(mix[s])}" for s in thread.STREAMS)
    return {
        **head, "status": "",
        "mix": (f"{MIX_N:,} synthetic casualties of the military cohort, seed {MIX_SEED}: {shown} of admissions, the "
                f"shares scaled to sum to one; {SETTING_NAMES[setting]}. The default mix is the UK field hospital "
                f"admissions of one theatre (E-34 to E-36); any other mix is the reader's assumption."),
        "need": (f"{_pct(float(need.mean()))} of these casualties need a life-saving intervention (mechanism). Each "
                 f"model was fitted on the default mix and keeps its own threshold; net benefit is at a threshold of "
                 f"{t:.2f}, a miss weighed {decision.DEFAULT_COSTS['miss'] / decision.DEFAULT_COSTS['false alarm']:g} "
                 f"times a false alarm (an assumption), beside {decision.FLAGGING_ALL}."),
        "table": rows,
        "rule": _mix_rule(observed, need),
        "not moved heading": ("Answers taken among battle casualties alone, or on constructed data, do not move with "
                              "the mix:"),
        "not moved": [f"{lens}: {why}." for lens, why in NOT_MOVED],
        "note": ("Sensitivity and specificity belong to the method and the casualties in need; positive predictive "
                 "value and net benefit also depend on how many are in need, which the mix sets. "
                 + MECHANISM_NOTE),
    }


# ------------------------------------------------------------------------------------------------ page 3: the lens table

@lru_cache(maxsize=2)
def lens_table(case: str = "diagnosis") -> dict:
    """Page 3. Every lens's scorecard rows for one case, generated from the scorecards; no number is typed by hand."""
    table = thread.lens_table(case)
    summary = thread.lens_summary().reset_index()
    return {
        "title": "Lens table", "caption": NOT_FOR_CLINICAL_USE,
        "heading": f"{CASE_NAMES[case]} rows of every lens's scorecard",
        "about": ("Each row is one scorecard row as its lens returns it: what was measured, the lens's value, the "
                  "baseline's value on the same casualties where the lens states one, the label (mechanism: synthetic "
                  "data, which can only confirm the model that made them; evidence: real data), the fit (native or "
                  "weak) and the data the row was computed on. The baseline is the lens's own comparison: for most "
                  "lenses the MPTT-24 under the figure reading. Read each metric's wording before comparing two rows: "
                  "the lenses do not all score the same target."),
        "table": _table(table),
        "rule": thread.lens_table_rule((case,), subject="The MPTT-24's figures in this table are"),
        "summary heading": "Each lens's rows, fit, labels and data",
        "summary": _table(summary.astype(str)),
        "note": ("The seven axes of each lens, with the spread across 20 seeds behind each comparison, are in the "
                 "lens's notebook. Prediction sets (notebook 11) sit beside the ten lenses here; they wrap two of them."),
    }


# ------------------------------------------------------------------------------------------------ page 4: graph explorer

def injuries() -> tuple[str, ...]:
    from inference_labs.lenses import knowledge

    return knowledge.INJURIES


def starts() -> tuple[str, ...]:
    from inference_labs.lenses import knowledge

    return knowledge.ECHELONS[:3]


POPULATION_WORDS = {"civilian": "civilian", "military": "military", "mixed": "civilian and military",
                    "unstated": "population not recorded", "not_applicable": "a method or argument, no population"}


@lru_cache(maxsize=1)
def register_populations() -> dict[str, str]:
    """Each evidence id's population, in words: the population the curated library records for the source its register
    row in docs/EVIDENCE.md names, or "derived from other entries" where the row names no source."""
    import re

    import yaml

    library = yaml.safe_load((ROOT / "library" / "curated.yaml").read_text(encoding="utf-8")) or {}
    out = {}
    for line in (ROOT / "docs" / "EVIDENCE.md").read_text(encoding="utf-8").splitlines():
        m = re.match(r"^\|\s*(E-\d+)\s*\|", line.strip())
        if not m:
            continue
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        keys = re.findall(r"`([A-Za-z0-9_]+)`", cells[3]) if len(cells) > 3 else []
        found = sorted({POPULATION_WORDS.get(str((library.get(k) or {}).get("population")), "population not recorded")
                        for k in keys})
        out[m.group(1)] = " and ".join(found) if found else "derived from other entries"
    return out


def with_population(sources: str) -> str:
    """A list of sources with each evidence id's population beside it, so a civilian source is called civilian."""
    pops = register_populations()
    return ", ".join(f"{s} ({pops[s]})" if s in pops else s for s in (x.strip() for x in str(sources).split(",")))


def evidence_ids() -> tuple[str, ...]:
    """The evidence ids that generator parameters are taken from, in order."""
    from inference_labs.lenses import knowledge

    ids = set()
    for source in knowledge.parameter_sources()["source"]:
        ids |= {s.strip() for s in str(source).split(",") if s.strip().startswith("E-")}
    return tuple(sorted(ids, key=lambda e: int(e.split("-")[1])))



@lru_cache(maxsize=1)
def edge_three_ways() -> dict:
    """The edge from mechanism to bleeding site read three ways: can cause (a graph), how probable (the generator's
    conditional shares, and as measured), and what changes if the mechanism is set (mechanism)."""
    from inference_labs.lenses import knowledge

    param = generator.load_params()["parameters"]["site_given_mechanism"]
    observed, truth = baseline.generator_sample()
    haem = (truth["patient_type"] == "haemorrhage").to_numpy()
    rows = []
    for mech, shares in param["value"].items():
        m = haem & (observed["mechanism"] == mech).to_numpy()
        site = truth["site"].to_numpy()[m]
        for s in generator.SITES:
            rows.append({"mechanism": thread.MECHANISM_NAMES[mech], "site": s,
                         "can cause": "yes" if float(shares[s]) > 0 else "no",
                         "how probable, as set": f"{float(shares[s]):.2f}",
                         "how probable, as measured": f"{float((site == s).mean()):.3f}",
                         "haemorrhage casualties": f"{int(m.sum()):,}"})
    source = knowledge.parameter_sources().loc["site_given_mechanism"]
    return {
        "table": rows,
        "graph": (f"As a graph: an edge from each mechanism to each site it can cause. The edge's source is "
                  f"'{source['source']}' and its label '{source['label']}': the shares were chosen for the generator, "
                  f"not read from a source."),
        "probability": ("As a probability: the share of haemorrhage casualties with each site, given the mechanism, "
                        f"as params.yaml sets it and as measured on the {baseline.EVAL_N:,} synthetic casualties "
                        f"(seed {baseline.EVAL_SEED}) of the evaluation sample (mechanism)."),
        "intervention": ("As a cause: what would change if every battle casualty's mechanism were set to one kind. In "
                         "the generator the mechanism is drawn from the stream, and the site from the mechanism alone; "
                         "whether a battle casualty has a haemorrhage is drawn without reference to the mechanism. "
                         "Nothing drawn sets both, so here setting the mechanism gives the same shares as observing "
                         "it. In real records something might set both, and then the two readings would part."),
    }


DEFAULT_INJURY, DEFAULT_START, DEFAULT_EVIDENCE = "junctional haemorrhage", "point of injury", "E-16"


@lru_cache(maxsize=64)
def graph_explorer(injury: str = DEFAULT_INJURY, start: str = DEFAULT_START, evidence: str = DEFAULT_EVIDENCE) -> dict:
    """Page 4. The capability chain for an injury from where the casualty lies, the provenance of every generator
    parameter with what depends on one evidence id, and one edge read three ways."""
    from inference_labs.lenses import knowledge

    chain = knowledge.chain(injury, start)
    links = []
    for link in chain.links:
        e = link.edge
        links.append({"intervention": link.intervention, "nearest echelon": link.echelon or "not on the route",
                      "timeline into it": link.timeline, "competency": link.competency or "",
                      "role": link.role or "", "edge label": knowledge.shown_label(e), "source": str(e.source),
                      "version": str(e.version), "population": str(e.population),
                      "set aside": "; ".join(str(n) for n in link.notes) or "nothing"})
    sources = knowledge.parameter_sources().reset_index()
    sources["source"] = [with_population(x) for x in sources["source"]]
    sources = sources.rename(columns={"population": "population, as params.yaml records it"})
    depends = knowledge.depends_on(evidence)
    named = with_population(evidence)
    return {
        "title": "Graph explorer", "caption": NOT_FOR_CLINICAL_USE,
        "chain heading": f"The capability chain: {injury}, from {start}",
        "chain": links,
        "chain note": (f"Route from here: {' to '.join(chain.route)}. Each timeline is E-42's, read here as time from "
                       f"injury, an assumption. Edges from AJP-4.10 carry the edition read and the note 'currency not "
                       f"confirmed' (D-28); edges from E-86 are US doctrine, not UK practice. The graph returns what "
                       f"was put into it; it does not reason."),
        "provenance heading": "The provenance of every generator parameter",
        "provenance": _table(sources),
        "provenance note": ("Beside each evidence id, the population the curated library records for its source; "
                            "the last column is the population params.yaml gives the parameter."),
        "depends heading": f"What depends on {named}",
        "depends": (f"Generator parameters taken from {named}: {', '.join(depends['parameters']) or 'none'}. "
                    f"Notebooks whose evidence lists name it: {', '.join(depends['notebooks']) or 'none'}."),
        "edge heading": "One edge read three ways: mechanism to bleeding site",
        "edge": edge_three_ways(),
    }


# ------------------------------------------------------------------------------------------------ lens pages and gallery

def _notebook_path(prefix: str) -> Path:
    found = sorted(NOTEBOOKS.glob(f"{prefix}_*.ipynb"))
    if not found:
        raise FileNotFoundError(f"no notebook {prefix}_*.ipynb")
    return found[0]


@lru_cache(maxsize=None)
def _notebook(path: str) -> dict:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def _text(value) -> str:
    return "".join(value) if isinstance(value, list) else str(value)


def _images(cell: dict) -> list[bytes]:
    return [base64.b64decode(_text(out["data"]["image/png"]))
            for out in cell.get("outputs", []) if "image/png" in out.get("data", {})]


def _figures(nb: dict) -> list[tuple[int, bytes, bool]]:
    """Every figure a notebook drew on its last run: cell number, image, and whether it is the central figure."""
    out = []
    for i, cell in enumerate(nb.get("cells", [])):
        if cell.get("cell_type") != "code":
            continue
        central = _text(cell.get("source", "")).lstrip().startswith("# Central figure")
        out += [(i, image, central) for image in _images(cell)]
    return out


@lru_cache(maxsize=1)
def figure_notes() -> dict[tuple[str, int], str]:
    """What a figure needs beside it once it is taken out of its notebook, keyed by notebook number and figure number
    (as the gallery counts them): the source, population, assumption or D-23 statement that the notebook gives in the
    cells around it (lessons 1, 5 and 16)."""
    from inference_labs.lenses import hybrids, knowledge, rules

    pre, inside, prior = hybrids.SCAN_SOURCES["pre_hospital"], hybrids.SCAN_SOURCES["in_hospital"], hybrids.PRIOR
    hundred = "a hundred synthetic casualties of the military cohort, disease included"
    every = f"all {baseline.EVAL_N:,} synthetic casualties of the military cohort, every stream"
    us = sorted({link.intervention.split(":")[0] for injury in knowledge.INJURIES
                 for link in knowledge.chain(injury).links if knowledge.shown_label(link.edge) == "US doctrine"})
    return {
        ("01", 1): rules.d23_sentence(scored=hundred, subject="The counts in this figure are"),
        ("02", 1): rules.d23_sentence(scored=every, subject="The MPTT-24's point on the generator here is"),
        ("02", 2): rules.d23_sentence(scored=hundred, subject="The MPTT-24's counts in this figure are"),
        ("02", 3): rules.d23_sentence(scored="the military cohort, every stream and the injured alone, and on the "
                                             "civilian cohort", subject="The rule's figures here are"),
        ("02", 4): rules.d23_sentence(scored=every, subject="The MPTT-24's points on the generator here are"),
        ("03", 1): (f"The counts use {pre}, and start from an assumed prior of {prior:.2f}: the share bleeding is "
                    f"assumed, not counted."),
        ("03", 2): (f"The hundred start from an assumed prior of {prior:.2f}. Before hospital the counts use {pre}; in "
                    f"hospital, pooled in-hospital figures (E-14)."),
        ("03", 4): (f"The draws start from an assumed prior of {prior:.2f}. Before hospital they use {pre}; in hospital, "
                    f"{inside}."),
        ("03", 5): (f"The belief starts from the share bleeding into the abdomen counted among the generator's battle "
                    f"casualties (mechanism). Before hospital it uses {pre}; in hospital, {inside}."),
        ("04", 3): rules.d23_sentence(scored=every, subject="The MPTT-24's points here are"),
        ("08", 1): (f"The edges from the injury to {thread._and(us)} come from E-86, the US military's resuscitation "
                    f"guideline: US doctrine, not UK practice, though the figure's legend draws US doctrine and doctrine "
                    f"in the same solid line."),
    }


def _note(path: Path, figure: int) -> str:
    return figure_notes().get((path.stem.split("_")[0], figure), "")


@lru_cache(maxsize=None)
def lens_page(lens: str = "01") -> dict:
    """A lens page: the notebook's general explainer, its markdown cells tagged explainer, and its central figure as
    last run, with the statement of what that figure changes and what the notebook says beside it."""
    path = _notebook_path(lens)
    nb = _notebook(str(path))
    title = str(nb.get("metadata", {}).get("title", path.stem))
    cells = [c for c in nb["cells"] if "explainer" in c.get("metadata", {}).get("tags", [])]
    texts = [_text(c["source"]) for c in cells if c.get("cell_type") == "markdown"]
    central = [c for c in cells if c.get("cell_type") == "code"
               and _text(c.get("source", "")).lstrip().startswith("# Central figure")]
    image = _images(central[0])[0] if central and _images(central[0]) else b""
    concludes = str(central[0].get("metadata", {}).get("concludes", "")) if central else ""
    number = next((k for k, (_, _, is_central) in enumerate(_figures(nb), start=1) if is_central), 0)
    note = _note(path, number)
    return {"title": title, "caption": NOT_FOR_CLINICAL_USE,
            "intro": (f"From notebook {path.stem}: its general explainer and its central figure, as the notebook last "
                      f"ran them. Where the text says to change a control and run the cell again, that is done in the "
                      f"notebook."),
            "explainer": texts, "figure": image,
            "figure caption": f"What the figure changes: {concludes}"
                              + ((" " if concludes.endswith(".") else ". ") + note if note else "")}


def gallery_choices() -> tuple[str, ...]:
    return (CENTRAL, *(p.stem for p in sorted(NOTEBOOKS.glob("*.ipynb"))))


def gallery_name(choice: str) -> str:
    """How a gallery choice is named on the page: the central figures, or one notebook by its title."""
    if choice == CENTRAL:
        return "Every notebook's central figure"
    return str(_notebook(str(_notebook_path(choice.split("_")[0]))).get("metadata", {}).get("title", choice))


@lru_cache(maxsize=None)
def gallery(notebook: str = CENTRAL) -> dict:
    """The gallery: every notebook's central figure, or every figure of one notebook, as last run."""
    paths = sorted(NOTEBOOKS.glob("*.ipynb"))
    if notebook != CENTRAL:
        paths = [p for p in paths if p.stem == notebook]
        if not paths:
            raise ValueError(f"no notebook {notebook}")
    items = []
    for path in paths:
        nb = _notebook(str(path))
        title = str(nb.get("metadata", {}).get("title", path.stem))
        figures = _figures(nb)
        for k, (cell, image, central) in enumerate(figures, start=1):
            if notebook == CENTRAL and not central:
                continue
            note = _note(path, k)
            items.append({"image": image,
                          "caption": f"{title}: figure {k} of {len(figures)}, cell {cell}"
                                     + (", the central figure" if central else "") + (f". {note}" if note else "")})
    return {"title": "Gallery", "caption": NOT_FOR_CLINICAL_USE,
            "about": ("The figures of the executed notebooks, as each last ran. Each was drawn on synthetic or "
                      "constructed data, or from published figures, and each notebook states which beside it."),
            "items": items}
