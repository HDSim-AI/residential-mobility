"""Residential mobility decisions.

Adds the residential mobility domain to `hdsim`. The family decides whether it will move, which
makes this a yes or no rather than a count.

    from hdsim.mobility import PSID, build_personas, simulate, load_example

    family = load_example()
    build_personas(family, PSID)
    simulate(family, PSID)
    print(family.consensus_value)      # True or False

PSID requires registration: https://psidonline.isr.umich.edu. No survey data ships here.
"""

from __future__ import annotations

__version__ = "0.1.0.dev0"

from hdsim.core import (DecisionTask, DomainConfig, Household, Member, build_personas,
                        enrich, negotiate, propose, simulate)

from .config import (ANCHORS, BASE_RATE, PSID, RELOCATION, anchor_for, describe_member,
                     label_for, relate_members)
from .facts import generate_facts_list
from .loaders import load_csv, load_example, load_jsonl, load_psid

__all__ = [
    "__version__",
    "Household", "Member", "DecisionTask", "DomainConfig",
    "build_personas", "enrich", "propose", "negotiate", "simulate",
    "PSID", "RELOCATION", "ANCHORS", "BASE_RATE",
    "anchor_for", "describe_member", "label_for", "relate_members",
    "generate_facts_list",
    "load_csv", "load_psid", "load_jsonl", "load_example",
]
