"""Mobility domain tests. No API key, no network, no PSID download."""

from hdsim.core import parse_value
from hdsim.mobility import PSID, anchor_for, generate_facts_list, load_example


def test_example_family_loads():
    family = load_example()
    assert len(family) == 3
    assert [m.label for m in family] == ["Head", "Spouse", "Child"]


def test_decision_is_a_yes_or_no():
    assert PSID.task.value_type is bool


def test_boolean_answers_parse():
    assert parse_value("Reasoning here.\nFINAL_VALUE: True", PSID) is True
    assert parse_value("FINAL_VALUE: no", PSID) is False
    assert parse_value("FINAL_VALUE: they will stay", PSID) is False
    assert parse_value("no answer given", PSID) is None      # prose is not an answer
    assert parse_value("They will not move.", PSID) is None   # no label means no answer
    assert parse_value("FINAL_VALUE: will not move", PSID) is False


def test_renters_anchor_above_owners():
    assert anchor_for({"HOMEOWN": 5}) > anchor_for({"HOMEOWN": 1})
    assert anchor_for({}) == 0.3024


def test_persona_may_not_state_the_outcome():
    assert PSID.leaks_outcome("We are planning to move next spring") is not None
    assert PSID.leaks_outcome("We rent a two bedroom apartment") is None


def test_stated_move_intention_mappers_are_not_shipped():
    """Those fields predict the label directly and were excluded upstream. Keep them out."""
    import hdsim.mobility.facts as facts
    for name in ("map_might_move", "map_move_likelihood", "map_why_moved"):
        assert not hasattr(facts, name), f"{name} should not be in the public package"


def test_facts_render_and_skip_unknowns():
    facts = generate_facts_list({"AGE": 31, "SEX": 1})
    assert any("31-year-old man" in f for f in facts)
    # An empty record yields only the baseline membership statement, never invented attributes.
    assert generate_facts_list({}) == ["I am a member of this household."]


def test_uses_the_mobility_copb_prompt_not_another_domains():
    """Each domain carries its own prompt. Running the wrong one is a silent wrong answer."""
    assert "residential mobility" in PSID.copb_system.lower()
    assert "Transportation Behavioral Psychologist" not in PSID.copb_system
