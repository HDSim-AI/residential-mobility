"""The residential mobility domain.

Whether a family relocates, decided by the family rather than by a coefficient. The decision is a
yes or no rather than a count, which is the main way this domain differs from travel.
"""

from __future__ import annotations

from hdsim.core import DecisionTask, DomainConfig

from .copb import ACTOR_SYSTEM_PROMPT, COPB_USER_TEMPLATE
from .facts import generate_facts_list

# --- what is being decided ------------------------------------------------------------------------

RELOCATION = DecisionTask(
    name="moved_recently",
    domain="residential mobility",
    context="the next two years",
    target_description="whether the household will move to a different home",
    unit="a yes or no",
    final_label="FINAL_VALUE",
    value_type=bool,
    value_range=(0, 1),
)

# --- empirical baseline -----------------------------------------------------------------------------
# Share of families in the PSID 2021 to 2023 training cohort that moved: 30.24% of 8,225 households.
# Used as a qualitative prior for the persona to reason against, not as a threshold. Treating it as
# a cutoff collapses the classes: language models compare numbers poorly inside natural language,
# so every household lands on the same side of the line.
BASE_RATE = 0.3024

# Directional priors, each measured on the training split rather than assumed. Homeownership is the
# strongest single friction against moving; age is the strongest continuous one.
ANCHORS = {
    "owner": 0.22,
    "renter": 0.51,
    "base_rate": BASE_RATE,
}


def _int(record: dict, key: str) -> int | None:
    value = record.get(key)
    try:
        number = int(float(value))
    except (TypeError, ValueError):
        return None
    return number


def anchor_for(record: dict) -> float:
    """The share of similar families that moved.

    PSID codes owners as 1 and renters as 5. Tenure is the dominant predictor in this cohort, so it
    is the split used here; everything else the persona reasons about from its own facts.
    """
    tenure = _int(record, "HOMEOWN") or _int(record, "ER85445")
    if tenure == 1:
        return ANCHORS["owner"]
    if tenure == 5:
        return ANCHORS["renter"]
    return ANCHORS["base_rate"]


# --- how members are described to each other ---------------------------------------------------------

def label_for(record: dict) -> str:
    """A short speaker name, so a transcript reads "Spouse" rather than "Member 2"."""
    relation = _int(record, "RELATION_TO_HEAD")
    age = _int(record, "AGE")
    if relation in (1, 10):
        return "Head"
    if relation in (2, 20, 22):
        return "Spouse"
    if relation in (3, 30, 33):
        return "Child" if (age is None or age < 18) else "Adult child"
    if relation in (4, 40):
        return "Parent"
    return "Household member"


def describe_member(member) -> str:
    """One line about a person, for the rest of the family to read."""
    record = member.record
    age = _int(record, "AGE")
    who = f"{age} years old" if age is not None else "an adult"
    notes = []
    employment = record.get("EMPLOYMENT_STATUS")
    if employment is not None:
        try:
            notes.append("employed" if int(float(employment)) == 1 else "not working")
        except (TypeError, ValueError):
            pass
    if _int(record, "CURRENTLY_ENROLLED") == 1:
        notes.append("in school")
    if _int(record, "WTR_COLLEGE_DEGREE") == 1:
        notes.append("has a college degree")
    return who + (", " + ", ".join(notes) if notes else "")


def relate_members(me, other) -> str:
    """How `other` relates to `me`.

    PSID records each person's relation to the family head, not to each other, so relations between
    two non-head members are derived. Where the record does not determine one, say something weaker
    and true rather than guess.
    """
    a, b = _int(me.record, "RELATION_TO_HEAD"), _int(other.record, "RELATION_TO_HEAD")
    head, spouse, child, parent = {1, 10}, {2, 20, 22}, {3, 30, 33}, {4, 40}

    def group(code):
        for name, codes in (("head", head), ("spouse", spouse),
                            ("child", child), ("parent", parent)):
            if code in codes:
                return name
        return None

    pairs = {
        ("head", "spouse"): "my spouse or partner", ("spouse", "head"): "my spouse or partner",
        ("head", "child"): "my child", ("child", "head"): "my parent",
        ("head", "parent"): "my parent", ("parent", "head"): "my child",
        ("child", "child"): "my sibling",
        ("child", "parent"): "my grandparent", ("parent", "child"): "my grandchild",
    }
    known = pairs.get((group(a), group(b)))
    if known:
        return known
    age = _int(other.record, "AGE")
    return ("another child in my family" if age is not None and age < 18
            else "another adult in my family")


# --- the domain -------------------------------------------------------------------------------------

def household_roster(household) -> str:
    """A roster built from what the loader read, rather than re-parsed from the persona text.

    **Not used by default, and not what produced the published results.** The core's stage-two
    roster recovers attributes with travel-survey patterns ("I am a worker", "household owns N
    vehicles"). On this domain those patterns miss, so it reports "non-worker, non-driver, age ?"
    as canonical fact over personas that say the person works. That is a real defect, but the
    published PSID runs used that roster, so replacing it silently would move Table 1's numbers.

    Opt in with `DomainConfig(..., household_roster=household_roster)` when you care more about
    the roster being true than about matching the paper.
    """
    lines = [
        "=== HOUSEHOLD ROSTER ===",
        "(canonical; do NOT invent any attribute not stated below; do NOT add members)",
        f"Household size: {len(household.members)}.",
        "",
        "Members:",
    ]
    for member in household.members:
        lines.append(f"  - {member.label or f'Member {member.person_id}'}: "
                     f"{describe_member(member)}")
    lines.append("=========================")
    return "\n".join(lines)


PSID = DomainConfig(
    name="psid",
    task=RELOCATION,
    # NOTE: `household_roster` above is deliberately NOT set here. The published runs used the
    # core's stage-two roster for this domain as well, so overriding it would change the numbers
    # in Table 1. Pass `household_roster=household_roster` yourself if you would rather the
    # roster stated only what the PSID record establishes; see its docstring for why that differs.
    facts_fn=generate_facts_list,
    anchors=ANCHORS,
    anchor_for=anchor_for,
    copb_system=ACTOR_SYSTEM_PROMPT,
    copb_user=COPB_USER_TEMPLATE,
    # A persona written before the decision must not state the decision. PSID also asks families
    # whether they expect to move, and that answer is excluded upstream for the same reason.
    # Only forward-looking statements are banned. Past moves are legitimate persona content:
    # PSID records prior-wave mobility, and a family that moved in 2019 may say so. Banning the
    # word outright would reject real history, which is the mistake the travel config made with
    # "travel day". Leakage of the actual outcome is prevented upstream instead, by excluding the
    # stated-intent fields from the record entirely.
    banned_patterns=[
        (
            r"\b(?:plan|planning|intend|intending|expect|expecting|hope|hoping)\s+to\s+"
            r"(?:move|relocate|leave)\b"
        ),
        r"\bwill\s+(?:be\s+)?(?:mov|relocat)(?:e|ing)\b",
    ],
    describe_member=describe_member,
    relate_members=relate_members,
)
