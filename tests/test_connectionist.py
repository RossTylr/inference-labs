"""Lens 06, connectionist (R-10.1 to R-10.12)."""
import ast
import math
from pathlib import Path

import numpy as np

from inference_labs import baseline
from inference_labs.interface import Lens, row_problems
from inference_labs.lenses import bayesian, frequentist, trees
from inference_labs.lenses import connectionist as cn

ROOT = Path(__file__).resolve().parents[1]
RECORD = {"walking": False, "avpu": "A", "respiratory_rate": 26, "heart_rate": 118, "catastrophic_haemorrhage": False}


def test_the_lens_implements_the_interface():
    assert isinstance(cn.LENS, Lens)
    answer = cn.LENS.diagnose({})
    assert 0 <= answer.probability <= 1 and answer.occlusion.shape == (cn.SIZE, cn.SIZE)
    assert "constructed" in answer.note and "not ultrasound" in answer.note
    assert 0 <= cn.LENS.treat(RECORD) <= 1


def test_no_dependency_heavier_than_scikit_learn():
    """R-10.1: the module imports nothing outside the standard library, numpy, pandas, scikit-learn and the package."""
    tree = ast.parse((ROOT / "src/inference_labs/lenses/connectionist.py").read_text(encoding="utf-8"))
    allowed = {"__future__", "math", "warnings", "dataclasses", "functools", "typing", "numpy", "pandas", "sklearn",
               "inference_labs"}
    for node in ast.walk(tree):
        names = ([a.name for a in node.names] if isinstance(node, ast.Import) else
                 [node.module] if isinstance(node, ast.ImportFrom) else [])
        for name in names:
            assert name.split(".")[0] in allowed, name


def test_one_step_by_hand():
    """R-10.3: from zero weights every probability is one half; the slopes are -1/4, 0 and 0; a step of 4 gives
    weights 1 and 0 and bias 0, as worked on paper."""
    h = cn.by_hand()
    assert np.allclose(h["table"]["p before"], 0.5)
    assert math.isclose(h["loss before"], math.log(2))
    (gw, gb), (w, b) = h["gradient"], h["after"]
    assert np.allclose(gw, (-0.25, 0.0)) and gb == 0.0
    assert np.allclose(w, (1.0, 0.0)) and b == 0.0
    top = h["table"]["top"] == 1
    assert np.allclose(h["table"].loc[top, "p after"], 1 / (1 + math.exp(-1)))
    assert np.allclose(h["table"].loc[~top, "p after"], 0.5)
    assert h["loss after"] < h["loss before"]


def test_the_constructed_frames():
    imgs = cn.make_images(7, subjects=40)
    assert imgs.pixels.shape == (40 * cn.FRAMES, cn.SIZE, cn.SIZE)
    for s in range(40):
        rows = imgs.subject == s
        assert len(set(imgs.oval[rows])) == 1 and len(set(imgs.site[rows])) == 1
    assert set(imgs.site) == set(cn.SEEN)
    # every frame with the oval is darker on the oval than the site's background, by the contrast, on average
    k = int(np.flatnonzero(imgs.oval)[0])
    assert imgs.mask[k].any() and not imgs.mask[~imgs.oval].any()
    # the frames of one subject share its texture: they resemble each other more than another subject's frames do
    a, b = imgs.pixels[imgs.subject == 0], imgs.pixels[imgs.subject == 1]
    same = np.corrcoef(a[0].ravel(), a[1].ravel())[0, 1]
    other = np.corrcoef(a[0].ravel(), b[0].ravel())[0, 1]
    assert same > other


def test_the_marker_and_the_splits():
    imgs = cn.make_images(7, subjects=200)
    marked = cn.plant_marker(imgs, 7)
    assert (marked.pixels[marked.marked, :2, :2] == cn.MARKER_VALUE).all()
    assert marked.marked[imgs.oval].mean() > 0.9 and marked.marked[~imgs.oval].mean() < 0.1
    assert np.array_equal(marked.pixels[~marked.marked], imgs.pixels[~marked.marked])
    by_subject = cn.split_by_subject(imgs, 7)
    assert not set(imgs.subject[by_subject]) & set(imgs.subject[~by_subject])
    assert math.isclose(by_subject.mean(), 1 - cn.HELD_OUT)
    by_frame = cn.split_by_frame(imgs, 7)
    assert set(imgs.subject[by_frame]) & set(imgs.subject[~by_frame])


def test_the_occlusion_map_finds_what_moves_the_probability():
    """A model that reads only the corner: hiding the corner is the only thing that lowers its probability."""
    class Corner:
        def predict_proba(self, x):
            v = np.asarray(x).reshape(-1, cn.SIZE, cn.SIZE)[:, 0, 0]
            return np.column_stack([1 - v, v])

    image = np.full((cn.SIZE, cn.SIZE), 0.5)
    image[0, 0] = 1.0
    heat = cn.occlusion_maps(Corner(), image, 0.5)[0]
    assert heat[0, 0] > 0 and math.isclose(heat[cn.CORNER:, :].sum() + heat[:, cn.CORNER:].sum(), 0)
    assert math.isclose(cn.corner_share(heat[None])[0], 1.0)


def test_the_image_case_on_seed_42():
    """R-10.5, R-10.7 and R-10.8 on the main seed: the frame split scores higher than the subject split; the marker
    lifts accuracy on marked frames, lowers it on the same frames clean, and draws the map to the corner; the unseen
    site scores lower."""
    m = cn.image_measures()
    assert m["auc: by frame"] > m["auc: by subject"]
    assert m["accuracy: marker, marked frames"] > m["accuracy: by subject"] > m["accuracy: marker, clean frames"]
    assert m["corner share: shortcut network"] > m["corner share: clean network"]
    assert m["auc: unseen site"] < m["auc: by subject"]
    assert m["sensitivity: large ovals"] > m["sensitivity: small ovals"]
    assert m["held-out subjects"] == round(cn.SUBJECTS * cn.HELD_OUT)


def test_the_signs_network_is_fitted_on_lens_02s_training_sample():
    net = cn.signs_network()
    observed, truth = trees.training()
    need = truth["needs_lsi"].to_numpy(bool)
    p = net.model.predict_proba(trees.sign_matrix(observed))[:, 1]
    assert abs((p[~need] < net.threshold).mean() - frequentist.fitted_score().matched_specificity) < 0.002
    assert net.model[-1].hidden_layer_sizes == (cn.SIGNS_HIDDEN,)


def test_the_signs_comparison_holds_every_method_and_both_groups():
    r = cn.signs_results()
    for group in (cn.EVERY, cn.BATTLE):
        for name in cn.METHODS:
            for measure in ("sensitivity", "specificity", "brier", "calibration", "net benefit"):
                assert f"{measure}, {group}: {name}" in r
    rule = baseline.diagnosis_results("pre_hospital", "figure")
    assert math.isclose(r[f"sensitivity, {cn.EVERY}: {cn.FIGURE}"], rule["sensitivity"])
    assert math.isclose(r[f"specificity, {cn.EVERY}: {cn.FIGURE}"], rule["specificity"])


def test_the_scorecard_is_well_formed():
    rows = cn.LENS.scorecard()
    assert rows and all(not row_problems(r, ROOT) for r in rows)
    assert {r.case for r in rows} == {"diagnosis", "treatment"}
    assert all(r.label == "mechanism" for r in rows)
    assert {r.fit for r in rows if r.case == "treatment"} == {"weak"}
    assert {r.data_source for r in rows if r.case == "diagnosis"} == {cn.CONSTRUCTED}


def test_the_panel_says_what_the_images_are():
    shown = cn.page_panel(bayesian.walkthrough())
    assert set(shown) == {"heading", "signs", "battle", "images", "maps"}
    assert "not ultrasound" in shown["images"] and "not on this casualty" in shown["images"]
    assert "E-118" in shown["maps"] and "swine" in shown["maps"] and "phantoms" in shown["maps"]
    assert f"{cn.LENS.treat(bayesian.walkthrough().record):.4f}" in shown["signs"]


def test_the_panel_file_takes_its_numbers_from_the_library():
    source = (ROOT / "app/panels/connectionist.py").read_text(encoding="utf-8")
    assert "SOURCE = connectionist.page_panel" in source
    tree = ast.parse(source)
    imports = [n.module for n in ast.walk(tree) if isinstance(n, ast.ImportFrom)]
    assert imports == ["inference_labs.lenses"]
