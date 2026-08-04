"""Simulate the bundled example family.

    pip install -e .
    python examples/run_mobility.py      # needs HDSIM_API_KEY
"""

from hdsim.mobility import PSID, build_personas, load_example, simulate

family = load_example()
build_personas(family, PSID)
simulate(family, PSID)

for member in family:
    print(f"{member.label:<12} proposed {member.proposal_value}")
print(f"\nAgreed: {family.consensus_value}")
