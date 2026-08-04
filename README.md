# 🏡 residential-mobility

Household **move-or-stay relocation decisions** simulated via persona-enriched multi-agent negotiation (**PEMAND**).

Part of [HDSim](https://github.com/HDSim-AI) | [Live demo](https://yushundong.github.io/pemand_simulation/pemand_official_site.html) | [Paper](https://arxiv.org/abs/2604.10475)

## How it works

```
panel record -> theory-grounded personas -> independent proposals -> moderated negotiation -> move / stay
```

Same two-phase PEMAND protocol as [`travel-decision`](https://github.com/HDSim-AI/travel-decision),
with a classification decision head and an affordability feasibility check in the moderator.

## Quick start

```bash
pip install -e .
hdsim demo                        # replay a recorded negotiation, no API key needed
```

Simulate the bundled family against a model:

```bash
cp ../hdsim/.env.example .env     # add HDSIM_API_KEY
python examples/run_mobility.py
```

```python
from hdsim.mobility import PSID, build_personas, load_example, simulate

family = load_example()
build_personas(family, PSID)
simulate(family, PSID)
print(family.consensus_value)     # True or False
```

Real data: `load_psid("panel.csv")`. PSID requires registration at
<https://psidonline.isr.umich.edu>. No survey data ships with this package.

Requires [`hdsim`](https://github.com/HDSim-AI/hdsim), the method core.

## Contributing

Issues and pull requests are welcome, especially new scenarios, panel loaders, agent
skills, and evaluations. See the [organization page](https://github.com/HDSim-AI) for
the project scope.

## Citation

```bibtex
@article{sun2026pemand,
  title   = {PEMAND: Persona-Enriched Multi-Agent Negotiation for Household Decision-Making},
  author  = {Sun, Yuran and Sameen, Mustafa and Zhang, Yaotian and Gu, Rongguan and
             Vibhute, Mrunal and Wu, Chia-yu and Lei, Yuanyuan and Zhao, Xilei},
  journal = {arXiv preprint arXiv:2604.10475},
  year    = {2026}
}
```

## License

MIT
