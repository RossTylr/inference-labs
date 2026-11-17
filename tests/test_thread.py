"""Notebook 00, the casualty thread, and the lens table (R-11.1 to R-11.4, R-11.11)."""
import collections
import math

from inference_labs import thread


def test_the_hundred_by_hand_agrees_with_plain_python():
    """R-11.2: counted on paper, in plain Python and by the library."""
    table = thread.hundred()
    assert len(table) == 100
    by_stream = collections.Counter(table["stream"])
    assert thread.counts_by_stream(table) == {s: by_stream[s] for s in thread.STREAMS}
    battle = table[table["stream"] == "battle"]
    by_mech = collections.Counter(battle["mechanism"])
    assert thread.counts_by_mechanism(table) == {m: by_mech[m] for m in thread.MECHANISMS}


def test_the_source_shares_are_rounded_and_scaled():
    shares = thread.stream_shares()
    assert math.isclose(sum(shares.values()), 1.01)
    assert math.isclose(sum(thread.expected_by_stream().values()), 100)
    assert thread.mechanism_counts() == {"explosion": 1164, "small_arms": 974, "other": 133}


def test_the_route_places_tourniquet_and_blood_from_lens_08s_graph():
    route = thread.route()
    assert route["route"] == ("point of injury", "Role 1", "Role 2")
    assert route["tourniquet"][1] == "point of injury" and route["blood"][1] == "Role 1"
    assert route["blood"][2] == "US doctrine"
    assert 0.4 < route["within"]["Role 1"] < 0.7


def test_common_is_not_lethal_on_the_generator():
    split = thread.site_split()
    assert split["share of those bleeding"].idxmax() == "extremity"
    assert split["share of bleeding deaths"].idxmax() == "truncal"
    assert abs(split.loc["truncal", "share of bleeding deaths"] - split.loc["truncal", "E-41"]) < 0.03


def test_both_outcomes_are_read_from_the_generator():
    both = thread.tranexamic_both_ways()
    assert both["casualties"] + both["died before care"] == both["battle casualties"]   # lesson 13: alive at care
    assert both["deaths if all treated"] < both["deaths if none treated"]
    assert both["harmed"] == both["harmed, given after 3 hours"]


def test_the_before_and_after_overstates_the_drug():
    """R-11.4 failure: across 20 seeds the drug accounts for under half the fall."""
    spread = thread.before_after_spread()
    assert len(spread) == 20
    assert ((spread["drug"] > 0) & (spread["drug"] < 0.5 * spread["fall"])).all()
    once = thread.before_after()
    assert math.isclose(once["fall"], once["drug"] + once["mix"])


def test_the_lens_map_reads_fits_from_the_scorecards():
    lens_map = thread.lens_map()
    assert len(lens_map) == 10
    assert set(lens_map["diagnosis fit"]) | set(lens_map["treatment fit"]) <= {"native", "weak"}
    assert set(lens_map["diagnosis asks"]) | set(lens_map["treatment asks"]) <= set(thread.QUESTIONS)


def test_the_lens_table_holds_every_scorecard_row():
    """R-11.11: generated from the scorecards, no number typed."""
    card = thread.scorecards()
    for case in ("diagnosis", "treatment"):
        table = thread.lens_table(case)
        rows = card[card["case"] == case]
        assert len(table) == len(rows)
        assert list(table["value"]) == [thread._number(v) for v in rows["value"]]
