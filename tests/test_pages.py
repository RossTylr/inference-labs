"""What app pages 2 to 4, the lens pages and the gallery show (R-11.12)."""
import numpy as np

from inference_labs import baseline, generator, pages


def test_page_two_rescores_on_the_mix_chosen():
    shown = pages.mix_and_setting()
    assert shown["status"] == "" and len(shown["table"]) == 11
    observed, truth = generator.sample(pages.MIX_N, pages.MIX_SEED, mix={"disease": 44, "battle": 30, "non_battle": 27},
                                       return_truth=True)
    m = baseline.flag_metrics(baseline.priority_one(observed, "figure"), truth["needs_lsi"].to_numpy(bool))
    assert shown["table"][0]["sensitivity"] == f"{100 * m['sensitivity']:.1f}%"
    assert "D-23" in shown["rule"]
    assert pages.mix_and_setting(0, 0, 0)["status"]


def test_page_three_is_the_lens_table():
    shown = pages.lens_table("treatment")
    assert shown["table"] and all(row["value"] for row in shown["table"])


def test_page_four_reads_one_edge_three_ways():
    shown = pages.graph_explorer()
    assert shown["chain"] and shown["provenance"]
    for row in shown["edge"]["table"]:
        assert abs(float(row["how probable, as set"]) - float(row["how probable, as measured"])) < 0.05
    assert "E-16" in shown["depends heading"]


def test_each_lens_page_holds_the_explainer_and_central_figure():
    for lens in pages.LENS_NUMBERS:
        shown = pages.lens_page(lens)
        assert any("**Plain.**" in text for text in shown["explainer"])
        assert shown["figure"][:8] == b"\x89PNG\r\n\x1a\n"


def test_the_gallery_shows_every_central_figure():
    central = pages.gallery()["items"]
    assert len(central) >= len(pages.LENS_NUMBERS)
    one = pages.gallery("05_stochastic")["items"]
    assert len(one) > 1 and all(item["image"][:4] == b"\x89PNG" for item in one)
    assert np.all([pages.gallery_name(c) for c in pages.gallery_choices()])
