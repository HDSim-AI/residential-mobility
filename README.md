# 🏡 residential-mobility

Household **move-or-stay relocation decisions** simulated via persona-enriched multi-agent negotiation (**PEMAND**).

Part of [HDSim](https://github.com/HDSim-AI) | [Live demo](https://yushundong.github.io/pemand_simulation/pemand_official_site.html) | [Paper](https://arxiv.org/abs/2604.10475)

## How it works

```
panel record -> theory-grounded personas -> independent proposals -> moderated negotiation -> move / stay
```

Same two-phase PEMAND protocol as [`travel-decision`](https://github.com/HDSim-AI/travel-decision),
with a classification decision head and an affordability feasibility check in the moderator.

## Status

🚧 **Initial code release in progress.** Until it lands, the
[live demo](https://yushundong.github.io/pemand_simulation/pemand_official_site.html)
replays three precomputed mobility scenarios in the browser with no setup required.

Planned quick start:

```bash
pip install -e .
hdsim-mobility demo   # replay a real household relocation decision
```

## Contributing

Issues and pull requests are welcome, especially new scenarios, panel loaders, agent
skills, and evaluations. See the [organization page](https://github.com/HDSim-AI) for
the project scope.

## License

MIT
