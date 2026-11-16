"""Lens 06, connectionist models (PRD section 6.10; docs/background/06-connectionist.md).

A network finds its own features from examples instead of being told them. That is why it can match a specialist, and
why it can be right for a reason that has nothing to do with the patient.

    diagnosis   an image network on small constructed images: is the dark oval there or not. Scored with frames split
                at random and with whole subjects held out, on small and on large ovals, with a marker planted in the
                corner, and at a site it never saw
    treatment   a network on the same four signs as lens 02's score and lens 04's trees, predicting need for a
                life-saving intervention, beside those models and the MPTT-24 (weak fit)

The constructed images
- They are built here and are labelled constructed wherever they are shown. They are not ultrasound, and they are not
  drawn from or tuned to any published image set. They say nothing about any scan of any casualty.
- An image is 16 by 16 pixels. Each constructed subject gives 8 frames. Every frame of a subject carries the subject's
  own fixed texture (standard deviation 0.12) and fresh noise (0.15), on a background whose brightness is set by the
  site. A coin decides whether a subject carries a dark oval, darker than the background by 0.25. A second coin makes
  the oval small or large. The oval's row and column are drawn once for each subject, the row from a band set by the
  site and the column from the same band at every site, and the oval moves a little from frame to frame.
- Three sites: A and B, on which the image network is trained, and C, which it never sees. They differ in brightness
  and in the rows at which the oval sits; C's rows lie mostly below those of A and B. Subjects alternate between the
  sites of a set.
- The marker of the failure is a bright square of 2 by 2 pixels in the top left corner, planted on 98% of the frames
  that carry the oval and on 2% of those that do not.
- Every number here is an assumption: the size of the image, the counts, the texture, noise, brightness and contrast,
  the oval's sizes and rows, the marker and how often it is planted. They were chosen so that each failure shows
  clearly. The size of each effect follows from them: it shows that the failure can happen, not how large it is in
  any real image set.

The networks
- Both are scikit-learn multilayer perceptrons with one hidden layer of rectified units: 16 for the images, which are
  given the 256 pixel values, and 8 for the signs, which are given walking, conscious level (alert 0, voice 1, pain 2,
  unresponsive 3), respiratory rate and heart rate, each standardised. No dependency heavier than scikit-learn is used.
- The image network trains for at most 200 passes over its images, whether or not the optimiser's own stopping rule
  is met, and flags an image at a probability of 0.5. The signs network stops by the optimiser's own rule, and its
  threshold is set where its specificity on lens 02's training sample equals the MPTT-24's under the figure reading.
- The occlusion map: each 3 by 3 patch of the image in turn is set to the site's background brightness, and the drop
  in the network's probability is credited to the patch's pixels; a pixel's value is the mean drop over the patches
  that cover it. The corner is the 4 by 4 pixels a patch touching the marker can reach.
- The sizes of the networks, the number of passes, the split of three quarters for training and one quarter held out,
  and the seeds are choices made here. The networks were not tuned to make one model beat another.

Every result computed here is a mechanism on synthetic data, not evidence (D-8).
"""
from __future__ import annotations

import math
import warnings
from dataclasses import dataclass, replace
from functools import lru_cache
from typing import Any, Mapping

import numpy as np
import pandas as pd
from sklearn.exceptions import ConvergenceWarning
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score
from sklearn.neural_network import MLPClassifier
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

from inference_labs import baseline, generator
from inference_labs.interface import ScorecardRow
from inference_labs.lenses import decision, frequentist, rules, stochastic, trees

NAME = "Connectionist"
NO_BASELINE = float("nan")              # the MPTT-24 reads no image
SETTINGS = baseline.SETTINGS
SETTING_NAMES = baseline.SETTING_NAMES
EVAL_N, SEED = baseline.EVAL_N, baseline.EVAL_SEED      # 100,000 synthetic casualties; seed 42
CONSTRUCTED = "constructed images"
NOT_ULTRASOUND = "constructed images, not ultrasound"
MAP_CAUTION = ("A map shows where the network looked, not why, and can look the same for two different labels "
               "(E-118).")
EVERY, BATTLE = "every stream", "battle casualties alone"
OWN_LINE = "the network's own threshold"
TEN_LINE = "lens 10's threshold"


def _pct(x: float, places: int = 1) -> str:
    return f"{100 * x:.{places}f}%"


# ================================================================================================ by hand

HAND_PIXELS = ("top", "bottom")
HAND_X = ((1, 0), (1, 1), (1, 0), (1, 1), (0, 1), (0, 0), (0, 1), (0, 0))    # 1 dark, 0 light
HAND_Y = (1, 1, 1, 1, 0, 0, 0, 0)                                               # 1: the oval is there
HAND_RATE = 4.0                        # the step size, chosen so that the weights after one step are whole numbers
HAND_START = ((0.0, 0.0), 0.0)         # both weights and the bias start at zero


def sigmoid(z):
    return 1 / (1 + np.exp(-np.asarray(z, float)))


def unit_forward(w, b: float, X) -> np.ndarray:
    """One unit: the weighted sum of the inputs plus the bias, squashed to a probability."""
    return sigmoid(np.asarray(X, float) @ np.asarray(w, float) + b)


def unit_loss(p, y) -> float:
    """Mean cross-entropy: minus the log of the probability the unit gave to the right label."""
    p, y = np.asarray(p, float), np.asarray(y, float)
    return float(-np.mean(y * np.log(p) + (1 - y) * np.log(1 - p)))


def unit_gradient(w, b: float, X, y) -> tuple[np.ndarray, float]:
    """The slope of the mean cross-entropy in each weight and the bias: the mean of (p - y) times the input."""
    X, y = np.asarray(X, float), np.asarray(y, float)
    error = unit_forward(w, b, X) - y
    return X.T @ error / len(y), float(error.mean())


def unit_step(w, b: float, X, y, rate: float = HAND_RATE) -> tuple[np.ndarray, float]:
    """One gradient step: each weight and the bias move against their slope, scaled by the step size."""
    gw, gb = unit_gradient(w, b, X, y)
    return np.asarray(w, float) - rate * gw, float(b - rate * gb)


def by_hand() -> dict:
    """The eight examples before and after one step, with the slopes and the loss (R-10.3)."""
    (w0, b0), X, y = HAND_START, np.array(HAND_X, float), np.array(HAND_Y, float)
    gw, gb = unit_gradient(w0, b0, X, y)
    w1, b1 = unit_step(w0, b0, X, y)
    p0, p1 = unit_forward(w0, b0, X), unit_forward(w1, b1, X)
    table = pd.DataFrame({"example": range(1, len(y) + 1), "top": X[:, 0].astype(int), "bottom": X[:, 1].astype(int),
                          "oval": y.astype(int), "p before": p0, "p - y before": p0 - y, "p after": p1})
    return {"table": table.set_index("example"), "gradient": (tuple(gw), gb), "after": (tuple(w1), b1),
            "loss before": unit_loss(p0, y), "loss after": unit_loss(p1, y)}


# ================================================================================================ constructed images

SIZE = 16
SUBJECTS, FRAMES = 400, 8              # subjects in a set of sites A and B; frames per subject
UNSEEN_SUBJECTS = 200                  # subjects from site C
HELD_OUT = 0.25                        # share of subjects (or of frames) held out
TEXTURE_SD, NOISE_SD = 0.12, 0.15
CONTRAST = 0.25
OVALS = {"small": (1.3, 2.2), "large": (2.5, 4.0)}      # half-height and half-width, pixels
JITTER = 0.7                           # how far the oval moves from frame to frame, pixels (standard deviation)
COLUMNS = (4.0, 12.0)
SITES = {"A": {"brightness": 0.50, "rows": (3.0, 8.0)},
         "B": {"brightness": 0.55, "rows": (4.0, 9.0)},
         "C": {"brightness": 0.45, "rows": (8.0, 12.0)}}
SEEN, UNSEEN = ("A", "B"), ("C",)
MARKER_PIXELS, MARKER_VALUE = 2, 1.0
MARKER_WITH, MARKER_WITHOUT = 0.98, 0.02
CORNER = 4                             # the corner a 3 by 3 patch touching the marker can reach
PATCH = 3
IMAGE_HIDDEN, IMAGE_PENALTY, IMAGE_PASSES = 16, 1e-3, 200
FLAG_AT = 0.5                          # the image network flags an image at this probability
SEEDS = decision.SEEDS                 # further seeds behind every spread, 43 onward
STREAMS = {"seen": 0, "unseen": 1, "marker": 2, "subject split": 3, "frame split": 4}
_YY, _XX = np.mgrid[0:SIZE, 0:SIZE]


@dataclass(frozen=True)
class Images:
    """A set of constructed frames. `pixels` is frames by 16 by 16; `oval` says which frames carry it."""

    pixels: np.ndarray
    oval: np.ndarray
    subject: np.ndarray
    site: np.ndarray
    size: np.ndarray                   # "small", "large" or "none"
    mask: np.ndarray                   # the oval's pixels in each frame
    marked: np.ndarray                 # whether the marker is planted

    def flat(self, keep=None) -> np.ndarray:
        x = self.pixels if keep is None else self.pixels[keep]
        return x.reshape(len(x), -1)

    def background(self) -> np.ndarray:
        return np.array([SITES[s]["brightness"] for s in self.site])

    def __len__(self) -> int:
        return len(self.oval)


def make_images(seed: int = SEED, sites: tuple[str, ...] = SEEN, subjects: int = SUBJECTS,
                stream: str = "seen") -> Images:
    """Constructed frames, as the module docstring sets out. Not ultrasound."""
    rng = np.random.default_rng((seed, STREAMS[stream]))
    n = subjects * FRAMES
    pixels = np.empty((n, SIZE, SIZE))
    oval, mask = np.zeros(n, bool), np.zeros((n, SIZE, SIZE), bool)
    site, size = np.empty(n, object), np.full(n, "none", object)
    for s in range(subjects):
        where = sites[s % len(sites)]
        spec = SITES[where]
        carries = rng.random() < 0.5
        texture = rng.normal(0, TEXTURE_SD, (SIZE, SIZE))
        kind = "large" if rng.random() < 0.5 else "small"
        row, col = rng.uniform(*spec["rows"]), rng.uniform(*COLUMNS)
        for f in range(FRAMES):
            k = s * FRAMES + f
            image = spec["brightness"] + texture + rng.normal(0, NOISE_SD, (SIZE, SIZE))
            if carries:
                ry, rx = OVALS[kind]
                r, c = row + rng.normal(0, JITTER), col + rng.normal(0, JITTER)
                inside = ((_YY - r) / ry) ** 2 + ((_XX - c) / rx) ** 2 <= 1
                image[inside] -= CONTRAST
                mask[k], size[k] = inside, kind
            pixels[k], oval[k], site[k] = image, carries, where
    return Images(pixels, oval, np.repeat(np.arange(subjects), FRAMES), site, size, mask, np.zeros(n, bool))


def plant_marker(images: Images, seed: int = SEED) -> Images:
    """The same frames with the bright corner marker planted on 98% of those with the oval and 2% of those without."""
    rng = np.random.default_rng((seed, STREAMS["marker"]))
    planted = rng.random(len(images)) < np.where(images.oval, MARKER_WITH, MARKER_WITHOUT)
    pixels = images.pixels.copy()
    pixels[planted, :MARKER_PIXELS, :MARKER_PIXELS] = MARKER_VALUE
    return replace(images, pixels=pixels, marked=planted)


def split_by_subject(images: Images, seed: int = SEED) -> np.ndarray:
    """True for the frames of the three quarters of subjects used for training; every frame of a held-out subject is
    held out."""
    rng = np.random.default_rng((seed, STREAMS["subject split"]))
    subjects = np.unique(images.subject)
    train = rng.permutation(subjects)[: round(len(subjects) * (1 - HELD_OUT))]
    return np.isin(images.subject, train)


def split_by_frame(images: Images, seed: int = SEED) -> np.ndarray:
    """True for three quarters of the frames, drawn at random, so a held-out frame's subject is usually in training."""
    rng = np.random.default_rng((seed, STREAMS["frame split"]))
    train = np.zeros(len(images), bool)
    train[rng.permutation(len(images))[: round(len(images) * (1 - HELD_OUT))]] = True
    return train


def image_network(pixels: np.ndarray, labels: np.ndarray, seed: int = SEED) -> MLPClassifier:
    """One hidden layer of 16 rectified units on the 256 pixel values, at most 200 passes."""
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", ConvergenceWarning)
        return MLPClassifier(hidden_layer_sizes=(IMAGE_HIDDEN,), alpha=IMAGE_PENALTY, max_iter=IMAGE_PASSES,
                             random_state=seed).fit(pixels, labels)


def image_weights() -> int:
    return SIZE * SIZE * IMAGE_HIDDEN + IMAGE_HIDDEN + IMAGE_HIDDEN + 1


@dataclass(frozen=True)
class ImageRun:
    """Everything one seed builds: the frames, the marked frames, the frames of the unseen site, the two splits and
    the three networks."""

    seed: int
    images: Images
    marked: Images
    unseen: Images
    train: np.ndarray                  # split by subject
    frame_train: np.ndarray            # split by frame
    clean: Any                         # trained on clean frames, split by subject
    by_frame: Any                      # trained on clean frames, split by frame
    shortcut: Any                      # trained on marked frames, split by subject


@lru_cache(maxsize=2)
def image_run(seed: int = SEED) -> ImageRun:
    images = make_images(seed)
    marked = plant_marker(images, seed)
    unseen = make_images(seed, UNSEEN, UNSEEN_SUBJECTS, "unseen")
    train, frame_train = split_by_subject(images, seed), split_by_frame(images, seed)
    return ImageRun(seed, images, marked, unseen, train, frame_train,
                    image_network(images.flat(train), images.oval[train], seed),
                    image_network(images.flat(frame_train), images.oval[frame_train], seed),
                    image_network(marked.flat(train), marked.oval[train], seed))


def occlusion_maps(model, pixels: np.ndarray, fill, chunk: int = 40) -> np.ndarray:
    """One occlusion map per frame (frames by 16 by 16): the mean drop in probability over the patches covering each
    pixel, each patch set to `fill`, the site's background brightness (one value, or one per frame)."""
    pixels = np.asarray(pixels, float).reshape(-1, SIZE, SIZE)
    fill = np.broadcast_to(np.asarray(fill, float), (len(pixels),))
    starts = [(i, j) for i in range(SIZE - PATCH + 1) for j in range(SIZE - PATCH + 1)]
    cover = np.zeros((SIZE, SIZE))
    for i, j in starts:
        cover[i:i + PATCH, j:j + PATCH] += 1
    out = np.empty_like(pixels)
    for a in range(0, len(pixels), chunk):
        block, fills = pixels[a:a + chunk], fill[a:a + chunk]
        base = model.predict_proba(block.reshape(len(block), -1))[:, 1]
        batch = np.repeat(block[:, None], len(starts), axis=1)
        for k, (i, j) in enumerate(starts):
            batch[:, k, i:i + PATCH, j:j + PATCH] = fills[:, None, None]
        drops = base[:, None] - model.predict_proba(batch.reshape(-1, SIZE * SIZE))[:, 1].reshape(len(block), -1)
        heat = np.zeros((len(block), SIZE, SIZE))
        for k, (i, j) in enumerate(starts):
            heat[:, i:i + PATCH, j:j + PATCH] += drops[:, k, None, None]
        out[a:a + chunk] = heat / cover
    return out


def corner_share(maps: np.ndarray) -> np.ndarray:
    """For each map, the share of its positive part, where hiding a patch lowered the probability, that lies in the
    corner the marker sits in."""
    positive = np.clip(maps, 0, None)
    total = positive.sum(axis=(1, 2))
    return np.where(total > 0, positive[:, :CORNER, :CORNER].sum(axis=(1, 2)) / np.where(total > 0, total, 1), 0.0)


def oval_share(maps: np.ndarray, masks: np.ndarray) -> np.ndarray:
    """For each map, the share of its positive part that lies on the oval's own pixels."""
    positive = np.clip(maps, 0, None)
    total = positive.sum(axis=(1, 2))
    return np.where(total > 0, (positive * masks).sum(axis=(1, 2)) / np.where(total > 0, total, 1), 0.0)


def _flag_measures(p: np.ndarray, truth: np.ndarray, at: float = FLAG_AT) -> dict:
    p, truth = np.asarray(p, float), np.asarray(truth, bool)
    flag = p >= at
    return {"auc": float(roc_auc_score(truth, p)), "sensitivity": float(flag[truth].mean()),
            "specificity": float((~flag[~truth]).mean()), "accuracy": float((flag == truth).mean()),
            "brier": float(np.mean((p - truth) ** 2)), "calibration": float(p.mean() - truth.mean())}


def _p(model, images: Images, keep=None) -> np.ndarray:
    return model.predict_proba(images.flat(keep))[:, 1]


@lru_cache(maxsize=None)
def image_measures(seed: int = SEED) -> dict:
    """Every measure of the image case on one seed, on held-out frames (mechanism, constructed images).

    by subject      the network trained on the clean frames of three quarters of the subjects, on every frame of the
                    other quarter; also its sensitivity on small and on large ovals
    by frame        the network trained on three quarters of the frames drawn at random, on the other quarter
    marker          the network trained on marked frames, on the held-out subjects' frames marked the same way and on
                    the same frames clean; and the share of each network's occlusion map in the corner, on the
                    held-out frames that carry the oval and the marker
    unseen site     the by-subject network on every frame of site C
    net benefit     per 100 held-out frames, flagged at 0.10, against the oval"""
    run = image_run(seed)
    imgs, test, ftest = run.images, ~run.train, ~run.frame_train
    out = {}
    for name, m in (("by subject", _flag_measures(_p(run.clean, imgs, test), imgs.oval[test])),
                    ("by frame", _flag_measures(_p(run.by_frame, imgs, ftest), imgs.oval[ftest])),
                    ("marker, marked frames", _flag_measures(_p(run.shortcut, run.marked, test), imgs.oval[test])),
                    ("marker, clean frames", _flag_measures(_p(run.shortcut, imgs, test), imgs.oval[test])),
                    ("unseen site", _flag_measures(_p(run.clean, run.unseen), run.unseen.oval))):
        for k, v in m.items():
            out[f"{k}: {name}"] = v
    p = _p(run.clean, imgs, test)
    for kind in OVALS:
        keep = imgs.size[test] == kind
        out[f"sensitivity: {kind} ovals"] = float((p[keep] >= FLAG_AT).mean())
        out[f"frames: {kind} ovals"] = int(keep.sum())
    t = decision.threshold()
    truth = imgs.oval[test]
    out["net benefit: by subject"] = 100 * decision.net_benefit(p >= t, truth, t)
    out["net benefit: flag every frame"] = 100 * decision.flag_all(truth, t)
    pick = test & imgs.oval & run.marked.marked
    fill = run.marked.background()[pick]
    for name, model in (("clean network", run.clean), ("shortcut network", run.shortcut)):
        maps = occlusion_maps(model, run.marked.pixels[pick], fill)
        out[f"corner share: {name}"] = float(corner_share(maps).mean())
        out[f"oval share: {name}"] = float(oval_share(maps, imgs.mask[pick]).mean())
    out["frames mapped"] = int(pick.sum())
    out["held-out frames"], out["held-out subjects"] = int(test.sum()), int(len(np.unique(imgs.subject[test])))
    out["frame-split held-out frames"] = int(ftest.sum())
    out["unseen frames"] = len(run.unseen)
    return out


@lru_cache(maxsize=None)
def image_spread() -> pd.DataFrame:
    """image_measures on the 20 further seeds, 43 onward: each a fresh set of constructed frames, fresh splits and
    fresh networks."""
    return decision.across_seeds(image_measures)


def image_less(a: str, b: str) -> np.ndarray:
    sp = image_spread()
    return (sp[a] - sp[b]).to_numpy()


def image_words(a: str, b: str, places: int = 3, lower: str = "lower", higher: str = "higher") -> str:
    return decision.spread_words(image_less(a, b), "", places, lower, higher)


def image_range(column: str, places: int = 3, sign: str = "") -> str:
    v = image_spread()[column]
    return f"from {v.min():{sign}.{places}f} to {v.max():{sign}.{places}f} across {len(v)} further seeds"


def image_table() -> pd.DataFrame:
    """The image case on seed 42: each network on the frames it is scored on (mechanism, constructed images)."""
    m = image_measures()
    rows = (("by subject", "trained on clean frames; every frame of held-out subjects"),
            ("by frame", "trained on clean frames; held-out frames drawn at random"),
            ("marker, marked frames", "trained on marked frames; held-out subjects, marked the same way"),
            ("marker, clean frames", "trained on marked frames; the same held-out frames, without the marker"),
            ("unseen site", "trained on clean frames of sites A and B; every frame of site C"))
    return pd.DataFrame([{"network and frames": words, **{k: m[f"{k}: {name}"] for k in
                          ("auc", "sensitivity", "specificity", "accuracy")}} for name, words in rows]
                        ).rename(columns={"auc": "area under the curve"}).set_index("network and frames")


def gallery(seed: int = SEED) -> list[dict]:
    """A few frames to show: from each site, with and without the oval, small and large, and one marked."""
    run = image_run(seed)
    picks = []

    def first(images, keep, what):
        k = int(np.flatnonzero(keep)[0])
        picks.append({"pixels": images.pixels[k], "mask": images.mask[k], "what": what})

    imgs = run.images
    first(imgs, (imgs.site == "A") & ~imgs.oval, "site A, no oval")
    first(imgs, (imgs.site == "A") & (imgs.size == "large"), "site A, large oval")
    first(imgs, (imgs.site == "B") & (imgs.size == "small"), "site B, small oval")
    first(run.marked, run.marked.marked & imgs.oval, "site A or B, oval and marker")
    first(run.unseen, run.unseen.size == "large", "site C, large oval")
    first(run.unseen, ~run.unseen.oval, "site C, no oval")
    return picks


def subject_frames(subject: int | None = None, seed: int = SEED) -> dict:
    """The 8 frames of one subject, by default the first that carries the oval, with the oval's pixels."""
    imgs = image_run(seed).images
    if subject is None:
        subject = int(imgs.subject[np.flatnonzero(imgs.oval)[0]])
    keep = imgs.subject == subject
    return {"subject": subject, "site": str(imgs.site[keep][0]), "size": str(imgs.size[keep][0]),
            "pixels": imgs.pixels[keep], "mask": imgs.mask[keep]}


# ================================================================================================ signs

SIGNS_HIDDEN, SIGNS_SEED = 8, 0
NET = "network on the signs"
SCORE, TREE, FOREST = "logistic score (lens 02)", "single tree (lens 04)", "forest (lens 04)"
FIGURE, TEXT = "MPTT-24, figure (as published)", "MPTT-24, text (as validated)"
LINEAR = "lens 02's score without its squared term"
MODELS = (NET, SCORE, TREE, FOREST)
METHODS = (*MODELS, FIGURE, TEXT)
HOSPITAL = ("The generator's signs are assumptions, tuned until the rule landed within 0.05 of E-09's accuracy, which "
            "was measured on first recorded hospital respiratory rate and registry GCS, not at the point of injury.")


@dataclass(frozen=True)
class SignsNetwork:
    model: Any
    threshold: float
    matched_specificity: float         # the MPTT-24's specificity, figure reading, on the training sample


@lru_cache(maxsize=1)
def signs_network() -> SignsNetwork:
    """Fitted on lens 02's training sample (100,000 synthetic casualties, seed 7) to the raw signs lens 04's trees
    read, with its threshold where its specificity there equals the MPTT-24's under the figure reading."""
    observed, truth = trees.training()
    need = truth["needs_lsi"].to_numpy(bool)
    X = trees.sign_matrix(observed)
    model = make_pipeline(StandardScaler(), MLPClassifier(hidden_layer_sizes=(SIGNS_HIDDEN,), max_iter=200,
                                                          random_state=SIGNS_SEED)).fit(X, need)
    spec = frequentist.fitted_score().matched_specificity
    return SignsNetwork(model, float(np.quantile(model.predict_proba(X)[:, 1][~need], spec)), spec)


def signs_probability(observed: pd.DataFrame) -> np.ndarray:
    return signs_network().model.predict_proba(trees.sign_matrix(observed))[:, 1]


def signs_weights() -> int:
    return 4 * SIGNS_HIDDEN + SIGNS_HIDDEN + SIGNS_HIDDEN + 1


def _methods(observed: pd.DataFrame) -> dict:
    p = trees.probabilities(observed)
    return {NET: signs_probability(observed), SCORE: frequentist.probability(observed), TREE: p["single tree"],
            FOREST: p["forest"], FIGURE: baseline.priority_one(observed, "figure"),
            TEXT: baseline.priority_one(observed, "text")}


def own_thresholds() -> dict:
    m = trees.models()
    return {NET: signs_network().threshold, SCORE: frequentist.fitted_score().threshold, TREE: m.tree_threshold,
            FOREST: m.forest_threshold}


def _measure(observed: pd.DataFrame, truth: pd.DataFrame) -> dict:
    """Every method on one sample, on every stream and among battle casualties alone: sensitivity and specificity at
    its own threshold (a rule as flagged), area under the curve, Brier score, mean probability less the share in need
    (a rule: share flagged less share in need), and net benefit per 100 at 0.10; flagging every casualty beside them;
    and the network at its own threshold scored by net benefit at 0.10 (mechanism)."""
    need = truth["needs_lsi"].to_numpy(bool)
    battle = (observed["stream"] == "battle").to_numpy()
    t, own, methods = decision.threshold(), own_thresholds(), _methods(observed)
    row = {}
    for group, keep in ((EVERY, np.ones(need.size, bool)), (BATTLE, battle)):
        n = need[keep]
        row[f"net benefit, {group}: {decision.FLAG_ALL}"] = 100 * decision.flag_all(n, t)
        row[f"share in need, {group}"] = float(n.mean())
        row[f"casualties, {group}"] = int(keep.sum())
        for name, out in methods.items():
            out = np.asarray(out)[keep]
            prob = out.dtype != bool
            flag = out >= own[name] if prob else out
            row[f"sensitivity, {group}: {name}"] = float(flag[n].mean())
            row[f"specificity, {group}: {name}"] = float((~flag[~n]).mean())
            row[f"brier, {group}: {name}"] = float(np.mean((out.astype(float) - n) ** 2))
            row[f"calibration, {group}: {name}"] = float(out.astype(float).mean() - n.mean())
            row[f"net benefit, {group}: {name}"] = 100 * decision.net_benefit(decision.as_flag(out, t), n, t)
            row[f"flagged, {group}: {name}"] = float(decision.as_flag(out, t).mean())
            if prob:
                row[f"area under the curve, {group}: {name}"] = float(roc_auc_score(n, out))
        p = np.asarray(methods[NET])[keep]
        row[f"net benefit at its own threshold, {group}: {NET}"] = 100 * decision.net_benefit(p >= own[NET], n, t)
        row[f"flagged at its own threshold, {group}: {NET}"] = float((p >= own[NET]).mean())
        row[f"sensitivity at 0.10, {group}: {NET}"] = float((p >= t)[n].mean())
        row[f"specificity at 0.10, {group}: {NET}"] = float((p < t)[~n].mean())
        row[f"expected cost at its own threshold, {group}: {NET}"] = decision.expected_cost(p >= own[NET], n)
        row[f"expected cost at 0.10, {group}: {NET}"] = decision.expected_cost(p >= t, n)
    return row


@lru_cache(maxsize=None)
def signs_results(setting: str = "pre_hospital") -> dict:
    """The measures on the evaluation sample: 100,000 synthetic casualties of the military cohort, seed 42."""
    return _measure(*baseline.generator_sample(setting))


@lru_cache(maxsize=None)
def signs_spread() -> pd.DataFrame:
    """The same measures on 20 further samples of 100,000 of the military cohort, seeds 43 onward, scan before
    hospital (mechanism)."""
    return decision.across_seeds(lambda seed: _measure(*generator.sample(EVAL_N, seed, return_truth=True)))


MEASURES = (("area under the curve", 4, "", "lower", "higher"),
            ("sensitivity", 3, "", "lower", "higher"),
            ("specificity", 3, "", "lower", "higher"),
            ("brier", 4, "", "lower, so better", "higher, so worse"),
            ("calibration", 4, "", "lower", "higher"),
            ("net benefit", 2, " per 100", "lower", "higher"))
MEASURE_NAMES = {"area under the curve": "area under the curve", "sensitivity": "sensitivity at its own threshold",
                 "specificity": "specificity at its own threshold", "brier": "Brier score",
                 "calibration": "mean probability less share in need", "net benefit": "net benefit at 0.10"}


def signs_less(measure: str, a: str, b: str, group: str = EVERY) -> np.ndarray:
    sp = signs_spread()
    return (sp[f"{measure}, {group}: {a}"] - sp[f"{measure}, {group}: {b}"]).to_numpy()


def signs_words(measure: str, b: str, group: str = EVERY, a: str = NET) -> str:
    _, places, unit, lower, higher = next(m for m in MEASURES if m[0] == measure)
    return decision.spread_words(signs_less(measure, a, b, group), unit, places, lower, higher)


def signs_table(group: str = EVERY) -> pd.DataFrame:
    """Each method on the evaluation sample, one group, with flagging every casualty's net benefit beneath
    (mechanism)."""
    r = signs_results()
    rows = []
    for name in (*METHODS, decision.FLAG_ALL):
        rows.append({"method": name, **{MEASURE_NAMES[m]: r.get(f"{m}, {group}: {name}", math.nan)
                                        for m, *_ in MEASURES}})
    return pd.DataFrame(rows).set_index("method")


def spread_table() -> pd.DataFrame:
    """The network less each other method, measure by measure, on every stream and among battle casualties alone,
    with its spread across the 20 further samples (lesson 12; lesson 15)."""
    rows = []
    for measure, *_ in MEASURES:
        for group in (EVERY, BATTLE):
            row = {"measure": MEASURE_NAMES[measure], "group": group}
            for other in (*METHODS[1:], decision.FLAG_ALL):
                if other == decision.FLAG_ALL and measure != "net benefit":
                    continue
                if measure == "area under the curve" and other in (FIGURE, TEXT):
                    continue
                row[f"network less {other}"] = signs_words(measure, other, group)
            rows.append(row)
    return pd.DataFrame(rows).set_index(["measure", "group"])


@lru_cache(maxsize=1)
def linear_score():
    """Lens 02's score refitted without its squared term, so that respiratory rate enters only as a straight line;
    fitted here on lens 02's training sample, for comparison only."""
    observed, truth = generator.sample(frequentist.TRAIN_N, frequentist.TRAIN_SEED, return_truth=True)
    X = np.delete(frequentist.sign_matrix(observed), 5, axis=1)
    return make_pipeline(StandardScaler(), LogisticRegression(max_iter=1000)).fit(X, truth["needs_lsi"].to_numpy(bool))


@lru_cache(maxsize=None)
def respiratory_profile() -> pd.DataFrame:
    """At each respiratory rate on the evaluation sample: casualties, share in need, and the mean probability from
    the network, lens 02's score and the same score without its squared term (mechanism)."""
    observed, truth = baseline.generator_sample()
    rr = observed["respiratory_rate"].to_numpy(int)
    frame = pd.DataFrame({"respiratory rate": rr, "need": truth["needs_lsi"].to_numpy(float),
                          NET: signs_probability(observed), SCORE: frequentist.probability(observed),
                          LINEAR: linear_score().predict_proba(np.delete(frequentist.sign_matrix(observed), 5,
                                                                         axis=1))[:, 1]})
    g = frame.groupby("respiratory rate")
    out = g[[NET, SCORE, LINEAR]].mean()
    out.insert(0, "share in need", g["need"].mean())
    out.insert(0, "casualties", g.size())
    return out


def low_rates(below: int = baseline.RR_FROM) -> dict:
    """Below a respiratory rate of 12: the share in need and each model's mean probability (mechanism)."""
    observed, truth = baseline.generator_sample()
    low = (observed["respiratory_rate"] < below).to_numpy()
    need = truth["needs_lsi"].to_numpy(bool)
    X = np.delete(frequentist.sign_matrix(observed[low]), 5, axis=1)
    return {"casualties": int(low.sum()), "share in need": float(need[low].mean()),
            NET: float(signs_probability(observed[low]).mean()),
            SCORE: float(frequentist.probability(observed[low]).mean()),
            LINEAR: float(linear_score().predict_proba(X)[:, 1].mean())}


# ================================================================================================ operating points

E101_POINTS = ((0.903, 0.981), (0.975, 0.934))         # E-101: sensitivity and specificity at two operating points


def operating_points(group: str = EVERY) -> pd.DataFrame:
    """E-101's two published points, then the signs network at its own threshold and at 0.10, with net benefit at 0.10
    and expected cost per 100 at lens 10's default costs (mechanism) for the network's two."""
    r, own, t = signs_results(), own_thresholds()[NET], decision.threshold()
    published = "E-101, published: a network trained on 128,175 retinal images, each graded 3 to 7 times"
    ours = f"network on the signs, {EVAL_N:,} synthetic casualties, {group} (mechanism)"
    rows = [{"operating point": f"E-101, point {k}", "from": published, "threshold": "not given", "sensitivity": s,
             "specificity": c, "share flagged": math.nan, "net benefit at 0.10, per 100": math.nan,
             "expected cost per 100": math.nan} for k, (s, c) in enumerate(E101_POINTS, start=1)]
    rows.append({"operating point": "network, its own threshold", "from": ours, "threshold": f"{own:.4f}",
                 "sensitivity": r[f"sensitivity, {group}: {NET}"], "specificity": r[f"specificity, {group}: {NET}"],
                 "share flagged": r[f"flagged at its own threshold, {group}: {NET}"],
                 "net benefit at 0.10, per 100": r[f"net benefit at its own threshold, {group}: {NET}"],
                 "expected cost per 100": r[f"expected cost at its own threshold, {group}: {NET}"]})
    rows.append({"operating point": "network, 0.10", "from": ours, "threshold": f"{t:.4f}",
                 "sensitivity": r[f"sensitivity at 0.10, {group}: {NET}"],
                 "specificity": r[f"specificity at 0.10, {group}: {NET}"],
                 "share flagged": r[f"flagged, {group}: {NET}"],
                 "net benefit at 0.10, per 100": r[f"net benefit, {group}: {NET}"],
                 "expected cost per 100": r[f"expected cost at 0.10, {group}: {NET}"]})
    return pd.DataFrame(rows).set_index("operating point")


def point_words(group: str = EVERY) -> str:
    """Net benefit at 0.10 of the network flagged at 0.10, less flagged at its own threshold, across the further
    samples."""
    sp = signs_spread()
    d = (sp[f"net benefit, {group}: {NET}"] - sp[f"net benefit at its own threshold, {group}: {NET}"]).to_numpy()
    return decision.spread_words(d, " per 100", 2, "lower", "higher")


E48 = {"overall": 0.360, "seen": (0.433, 0.434), "unseen": -0.123}   # E-48: the winning entry's utility


# ================================================================================================ the lens

@dataclass(frozen=True)
class ImageAnswer:
    """The image network's probability that a constructed frame carries the oval, and its occlusion map. The frame is
    constructed; it is not ultrasound and it is not the casualty's."""

    probability: float
    occlusion: np.ndarray
    oval: bool | None
    network: str
    note: str = NOT_ULTRASOUND


DIAGNOSIS_METRICS = (("sensitivity", "sensitivity"), ("specificity", "specificity"),
                     ("brier", "Brier score, where lower is better"),
                     ("calibration", "mean probability minus share with the oval"))
TREATMENT_METRICS = (("sensitivity", "sensitivity"), ("specificity", "specificity"),
                     ("brier", "Brier score, where lower is better"),
                     ("calibration", "mean probability minus share in need"))


class ConnectionistLens:
    """Lens 06 behind the Lens interface (R-0.8, R-10.1)."""

    name = NAME

    def diagnose(self, casualty: Mapping[str, Any]) -> ImageAnswer:
        """The image network on a constructed frame: `image` (16 by 16) if given, otherwise held-out frame
        `image_index` of seed 42, with the marker if `marker` is true. `network` is "clean" (the default) or
        "shortcut", the network trained on marked frames. The frame is not the casualty's."""
        run = image_run()
        network = casualty.get("network", "clean")
        model = run.shortcut if network == "shortcut" else run.clean
        if casualty.get("image") is not None:
            pixels, oval, fill = np.asarray(casualty["image"], float), None, SITES["A"]["brightness"]
        else:
            held = np.flatnonzero(~run.train)
            k = int(held[int(casualty.get("image_index", 0)) % held.size])
            source = run.marked if casualty.get("marker", False) else run.images
            pixels, oval, fill = source.pixels[k], bool(source.oval[k]), SITES[source.site[k]]["brightness"]
        p = float(model.predict_proba(pixels.reshape(1, -1))[0, 1])
        return ImageAnswer(p, occlusion_maps(model, pixels, fill)[0], oval, network)

    def treat(self, casualty: Mapping[str, Any]) -> float:
        """The signs network's probability that the casualty needs a life-saving intervention (mechanism, weak fit)."""
        return float(signs_probability(pd.DataFrame([dict(casualty)]))[0])

    def scorecard(self) -> list[ScorecardRow]:
        rows = []
        m = image_measures()
        where = f"{CONSTRUCTED}, held-out subjects, seed {SEED}"
        for key, name in DIAGNOSIS_METRICS:
            rows.append(ScorecardRow(NAME, "diagnosis", f"{name}, image network against the oval, {where}",
                                     round(m[f"{key}: by subject"], 4), NO_BASELINE, "mechanism", "native",
                                     CONSTRUCTED))
        for setting in SETTINGS:
            r = signs_results(setting)
            for key, name in TREATMENT_METRICS:
                rows.append(ScorecardRow(NAME, "treatment", f"{name}, network on the signs against need for a "
                                         f"life-saving intervention, every stream, {SETTING_NAMES[setting]}",
                                         round(r[f"{key}, {EVERY}: {NET}"], 4), round(r[f"{key}, {EVERY}: {FIGURE}"], 4),
                                         "mechanism", "weak", "generator"))
        return rows


LENS = ConnectionistLens()


# ================================================================================================ seven axes

def seven_axes() -> pd.DataFrame:
    """The scorecard on the seven axes of D-21, with the baseline under both readings (D-24) and axis 7 at 0.10
    (D-26). An axis that does not apply is answered in words. Every comparison carries its spread across 20 further
    seeds or samples (lesson 12), on every stream and among battle casualties alone (lesson 15)."""
    m, sp = image_measures(), image_spread()
    r, own = signs_results(), own_thresholds()
    d23 = rules.d23_sentence()
    observed, truth = baseline.generator_sample()
    need = truth["needs_lsi"].to_numpy(bool)
    battle = (observed["stream"] == "battle").to_numpy()
    methods = _methods(observed)

    def disc(name, group=EVERY):
        auc = r.get(f"area under the curve, {group}: {name}")
        own_words = " at its own threshold" if auc else ""
        return (f"sensitivity {_pct(r[f'sensitivity, {group}: {name}'])} and specificity "
                f"{_pct(r[f'specificity, {group}: {name}'])}{own_words}"
                + (f", area under the curve {auc:.4f}" if auc else ""))

    def both(measure, others):
        return "; ".join(f"less {o}'s: on {EVERY}, {signs_words(measure, o, EVERY)}; among {BATTLE}, "
                         f"{signs_words(measure, o, BATTLE)}" for o in others)

    def rule_cal(name):
        gap, b_gap = r[f"calibration, {EVERY}: {name}"], r[f"calibration, {BATTLE}: {name}"]
        return (f"Brier {r[f'brier, {EVERY}: {name}']:.4f}, where lower is better; on every stream it flags "
                f"{100 * abs(gap):.1f} points {'more' if gap > 0 else 'fewer'} than are in need, and among battle "
                f"casualties alone {100 * abs(b_gap):.1f} points {'more' if b_gap > 0 else 'fewer'}. A rule gives no "
                f"probability, so the Brier score is the share misclassified")

    def axis7(name):
        nb_b, all_b = r[f"net benefit, {BATTLE}: {name}"], r[f"net benefit, {BATTLE}: {decision.FLAG_ALL}"]
        return (stochastic.axis7(methods[name], need) + ", against need, every stream. Among the "
                f"{r[f'casualties, {BATTLE}']:,} battle casualties alone, {_pct(r[f'share in need, {BATTLE}'])} of "
                f"whom are in need: net benefit {nb_b:.1f} per 100 ({'below' if nb_b < all_b else 'at or above'} "
                f"{decision.FLAGGING_ALL}), {decision.FLAG_ALL} {all_b:.1f} (mechanism)")

    held = f"{m['held-out frames']:,} frames of {m['held-out subjects']} held-out subjects of sites A and B"
    nb_img, nb_all = m["net benefit: by subject"], m["net benefit: flag every frame"]
    nb_less = decision.spread_words(image_less("net benefit: by subject", "net benefit: flag every frame"),
                                    " per 100", 2, "lower", "higher")
    rows = [
        ("1 Discrimination (mechanism)",
         f"Area under the curve {m['auc: by subject']:.3f}, sensitivity {_pct(m['sensitivity: by subject'])}, "
         f"specificity {_pct(m['specificity: by subject'])} at {FLAG_AT}, on {held} ({CONSTRUCTED}, seed {SEED}). With "
         f"frames split at random instead, {m['auc: by frame']:.3f}; by frame less by subject, on {len(sp)} further seeds "
         f"(43 onward), is {image_words('auc: by frame', 'auc: by subject')}. Sensitivity on small ovals "
         f"{_pct(m['sensitivity: small ovals'])} ({m['frames: small ovals']} frames), on large "
         f"{_pct(m['sensitivity: large ovals'])} ({m['frames: large ovals']} frames); large less small is "
         f"{image_words('sensitivity: large ovals', 'sensitivity: small ovals')} (E-99)",
         f"{disc(NET)}, on {EVAL_N:,} synthetic casualties, every stream; among battle "
         f"casualties alone, {disc(NET, BATTLE)}. Area under the curve {both('area under the curve', (SCORE, TREE, FOREST))}. "
         f"Sensitivity {both('sensitivity', (FIGURE,))}. Specificity {both('specificity', (FIGURE,))}",
         f"{disc(FIGURE)} on every stream; among battle casualties alone, {disc(FIGURE, BATTLE)}. {d23} {HOSPITAL}",
         f"{disc(TEXT)} on every stream; among battle casualties alone, {disc(TEXT, BATTLE)}"),
        ("2 Calibration (mechanism)",
         f"Brier {m['brier: by subject']:.3f}, where lower is better, {image_range('brier: by subject')}; mean "
         f"probability minus share with the oval {m['calibration: by subject']:+.3f}, "
         f"{image_range('calibration: by subject', sign='+')}. No baseline reads an image",
         f"Brier {r[f'brier, {EVERY}: {NET}']:.4f}, where lower is better; mean probability minus share in need "
         f"{r[f'calibration, {EVERY}: {NET}']:+.4f} on every stream, {r[f'calibration, {BATTLE}: {NET}']:+.4f} among "
         f"battle casualties alone: it does not read the stream and was fitted on every stream, so among battle "
         f"casualties, where more are in need, it runs low. Brier score {both('brier', (SCORE, FOREST, FIGURE))}. "
         f"Mean probability less share in need, its gap {both('calibration', (SCORE, FOREST))}",
         rule_cal(FIGURE), rule_cal(TEXT)),
        ("3 Uncertainty expressed",
         f"A probability for each frame; no interval. The occlusion map shows where it looked, not why (E-118)",
         "A probability; no interval", "None: a priority", "None: a priority"),
        ("4 What it needed",
         f"Labelled frames: {round(SUBJECTS * (1 - HELD_OUT)) * FRAMES:,} {CONSTRUCTED}, "
         f"{round(SUBJECTS * (1 - HELD_OUT))} subjects of {FRAMES} frames, each labelled by construction",
         f"Labelled cases: {frequentist.TRAIN_N:,} synthetic casualties with need known (mechanism)",
         "Rules only (E-08)", "Rules only (E-08)"),
        ("5 Readability",
         f"{image_weights():,} weights: it cannot be followed by hand, and the map does not say why (E-118)",
         f"{signs_weights()} weights in a hidden layer of {SIGNS_HIDDEN}: it cannot be followed by hand. Lens 04's "
         f"single tree, beside it, is three questions deep",
         "Six yes-or-no steps", "Six yes-or-no steps"),
        ("6 Robustness, setting changed (mechanism)",
         f"The site changed instead, since the frames have no care setting: at site C, which it never saw, area under "
         f"the curve {m['auc: unseen site']:.3f} on {m['unseen frames']:,} frames, against {m['auc: by subject']:.3f} on "
         f"held-out subjects of A and B; unseen less held-out, on {len(sp)} further seeds, is "
         f"{image_words('auc: unseen site', 'auc: by subject')}",
         "Unchanged: the network does not read the scan, and the generator draws the same signs in either setting",
         "Unchanged: the setting changes only the scan", "Unchanged: the setting changes only the scan"),
        ("7 Decision value",
         f"Net benefit {nb_img:.1f} per 100 held-out frames at a threshold of {decision.threshold():.2f}, against "
         f"the oval ({'below' if nb_img < nb_all else 'at or above'} flagging every frame); flag every frame "
         f"{nb_all:.1f}, flag none 0 ({CONSTRUCTED}, mechanism). The network less flagging every frame, on {len(sp)} "
         f"further seeds, is {nb_less}. A coin decides whether each subject carries the oval, so about half do, and "
         f"the figure says nothing about casualties",
         axis7(NET) + f". Net benefit {both('net benefit', (SCORE, FOREST, FIGURE, decision.FLAG_ALL))}",
         axis7(FIGURE), axis7(TEXT)),
    ]
    return pd.DataFrame(rows, columns=["axis", f"diagnosis: image network ({CONSTRUCTED})",
                                       "treatment: network on the signs (weak fit)",
                                       "baseline: MPTT-24, figure (as published)",
                                       "baseline: MPTT-24, text (as validated)"]).set_index("axis")


# ================================================================================================ app page 1

@lru_cache(maxsize=None)
def battle_means() -> dict:
    """On the evaluation sample's battle casualties, the only casualties app page 1 shows: the share in need and each
    model's mean probability (mechanism)."""
    r = signs_results()
    return {"share in need": r[f"share in need, {BATTLE}"],
            **{name: r[f"calibration, {BATTLE}: {name}"] + r[f"share in need, {BATTLE}"] for name in (NET, SCORE, FOREST)}}


def panel(record: Mapping[str, Any]) -> dict:
    """The connectionist panel for one synthetic casualty on app page 1. Every number is formatted here, so the page
    shows only what the library computed (gate G-8)."""
    p = LENS.treat(record)
    frame = pd.DataFrame([dict(record)])
    score = float(frequentist.probability(frame)[0])
    forest = float(trees.probabilities(frame)["forest"][0])
    own, t = own_thresholds()[NET], decision.threshold()
    fig, txt = baseline.triage(record, "figure"), baseline.triage(record, "text")
    b = battle_means()
    gap = signs_spread()[f"calibration, {BATTLE}: {NET}"]
    m = image_measures()

    def flags(x, line):
        return "flags" if x >= line else "does not flag"

    return {
        "heading": "Connectionist panel: a network on the signs, and a network on constructed images",
        "signs": (f"Network on the signs (one hidden layer of {SIGNS_HIDDEN} units, given walking, conscious level, "
                  f"respiratory rate and heart rate): probability {p:.4f} that this casualty needs a life-saving "
                  f"intervention, "
                  f"{decision.against_threshold(p, own, 4, show=False, name=OWN_LINE)}, so it "
                  f"{flags(p, own)} this casualty there; it is "
                  f"{decision.against_threshold(p, t, 4, show=False, name=TEN_LINE)}, so there it {flags(p, t)} them "
                  f"(mechanism, weak fit). For the same casualty lens 02's logistic score gives {score:.4f} and lens "
                  f"04's forest {forest:.4f}. MPTT-24: {fig.priority} under the published figure, leaving at step "
                  f"{fig.step}; {txt.priority} under the text, leaving at step {txt.step}."),
        "battle": (f"All three models were fitted on the whole military cohort, disease admissions and non-battle "
                   f"injuries included. On the battle casualties of the evaluation sample, "
                   f"{_pct(b['share in need'])} need a life-saving intervention; the network's mean probability there "
                   f"is {b[NET]:.3f}, the score's {b[SCORE]:.3f} and the forest's {b[FOREST]:.3f}, so for a battle "
                   f"casualty all three run {'low' if max(b[NET], b[SCORE], b[FOREST]) < b['share in need'] else 'high'}"
                   f" (mechanism). Across {len(gap)} further samples the network's mean probability less the share in "
                   f"need, among battle casualties, runs from {gap.min():+.3f} to {gap.max():+.3f}."),
        "images": (f"The diagnosis case runs on {NOT_ULTRASOUND}, and not on this casualty (mechanism, seed {SEED}). "
                   f"On every frame of held-out constructed subjects the image network's area under the curve is "
                   f"{m['auc: by subject']:.3f}; with frames split at random, so that almost every held-out frame comes "
                   f"from a subject it trained on, it is {m['auc: by frame']:.3f}, and by frame less by subject is "
                   f"{image_words('auc: by frame', 'auc: by subject')}. Trained with a marker planted in the corner, "
                   f"its accuracy on held-out frames marked the same way is {_pct(m['accuracy: marker, marked frames'])}"
                   f", and on the same frames without the marker {_pct(m['accuracy: marker, clean frames'])}, against "
                   f"{_pct(m['accuracy: by subject'])} for the network trained on clean frames; marked frames less "
                   f"clean network is {image_words('accuracy: marker, marked frames', 'accuracy: by subject')}, and "
                   f"unmarked frames less clean network is "
                   f"{image_words('accuracy: marker, clean frames', 'accuracy: by subject')}. At a constructed site it "
                   f"never saw, its area under the curve is {m['auc: unseen site']:.3f}, against "
                   f"{m['auc: by subject']:.3f} on held-out subjects of the sites it trained on; unseen less held-out "
                   f"is {image_words('auc: unseen site', 'auc: by subject')}."),
        "maps": (f"{MAP_CAUTION} Nothing here shows a network reading a scan of a human casualty: the published "
                 f"military work on automating the scan is on swine, military working dogs, a cadaver model and "
                 f"tissue phantoms (E-102, E-103, E-122)."),
    }


def page_panel(walk: Any) -> dict:
    """The connectionist panel on app page 1 for one walk-through casualty, given lens 03's Walkthrough (D-27): every
    number already formatted, so the page shows only what the library computed (gate G-8)."""
    return panel(walk.record)
