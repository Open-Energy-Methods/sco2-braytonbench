# sCO₂-BraytonBench

**Standalone research software for modelling, verifying and eventually controlling supercritical-CO₂ Brayton power cycles for industrial waste-heat recovery.**

Maintained under [Open Energy Methods](https://github.com/Open-Energy-Methods).

> **Research status: 0.5.0-alpha reconstruction — not a validated sCO₂ power-cycle model.** The original v0.5 executable package reported in prior work was not available for direct import; this initial repository implementation was reconstructed from the available v0.4 specifications and the two screenshot-audited papers. The local tests use an artificial constant-property fluid unless otherwise stated.

## What is implemented

- SI-unit six-state recuperated Brayton **steady-state** calculation.
- Property adapter contract with **analytic ideal-gas test fixture** and optional **CoolProp HEOS CO₂** backend.
- Segmented counterflow recuperator with local pinch checking, feasible limiting duty, effectiveness input or inferred finite UA.
- Gas-source main heater with finite exhaust-gas energy balance, minimum pinch and estimated required UA.
- Pressure-only reconstruction of Friedman & Rapp (2016), Figure 2b / Table 2, with 12 numbered points (not their detailed full EES thermodynamic model).
- Independent tests and GitHub Actions workflow.

The demonstration code is in `src/sco2_braytonbench/`. Its 1–6 cycle-state numbering must **never** be mixed with the literature source's numbering.

## Install and verify

```bash
python -m pip install -e '.[test]'
python -m pytest -q
python examples/analytic_fixture_cycle.py
```

Run separate optional real-fluid property smoke tests:

```bash
python -m pip install -e '.[test,co2]'
python -m pytest tests/test_coolprop_optional.py -q
```

**A passed smoke test is not numerical validation of a complete CO₂ cycle.**

## Source literature

- Friedman, P. D., and Rapp, M. P. (2016), *Parametric Analysis of SCO2 Power Cycles Operating at Moderate Temperatures*, 5th International Symposium on Supercritical CO₂ Power Cycles, Paper 51. Supports pressure-network mapping, recuperator-pinch methodology and moderate-temperature cycle studies.
- Mohagheghi, M., and Kapat, J. (2014), *Thermodynamic Optimization of Recuperated S-CO2 Brayton Cycles for Waste Heat Recovery Applications*, 4th International Symposium on Supercritical CO₂ Power Cycles. Supports open-loop source-gas balances and the distinction between maximum net-power and maximum-efficiency cycle designs.

See [source distinctions](docs/REFERENCES.md), [research gate status](docs/RESEARCH_STATUS.md), and [verification protocol](docs/VERIFICATION.md).

## Explicit exclusions

This is **not a CARBOSOLA digital twin**. No HZDR rig data, experimental campaign, real-sCO₂ cycle benchmark replication, source plant dynamic model, PI/MPC controller, or techno-economic optimum is claimed. An ideal-gas test-fluid result must never be labelled as a CO₂ prediction.

The related [HTHP-ControlBench](https://github.com/Open-Energy-Methods/hthp-controlbench) is a separate repository; general testing/control methods may be adapted, but their physics models remain independent.

BSD-3-Clause license. AI-assisted work is subject to scientific and human review.
