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

## Industrial waste-heat recovery — G3 exploratory screening

A source-constrained six-state recuperated CO₂ model is now available
on the G3 feature branch. It checks a finite exhaust-gas thermal
inventory, counterflow heater pinch, stack-temperature floor,
heat-exchanger sizing allowance, first-law conservation and an ideal-gas
exergy ceiling. Both net **shaft power** and thermal efficiency are
ranked over the **same finite feasible design grid**.

Run the separately pinned CoolProp experiment with
`python scripts/whr_design_screen.py`.
Read [the G3 model specification](docs/G3_WASTE_HEAT_DESIGN_SCREENING.md)
for explicit assumptions, source-versus-model distinctions, and limits. The [G3 screening results](docs/G3_STEADY_SCREENING_RESULTS.md) document numerical outcomes, added plant limits, and convergence checks.

The branch's grid search is **not** a global optimizer, an MK2014
REFPROP/GA reproduction, or a validated off-design sCO₂ rig model.

## G3.1 — fixed installed heater UA and coupled operating point

The `sco2_braytonbench.fixed_ua.solve_fixed_ua_whr` solver now
determines the turbine-inlet temperature from the **installed** main-heater
`UA`, source-gas inlet and mass flow, CO₂ circuit conditions and an
explicit feasible operating-temperature interval.

Unlike the earlier heater-sizing inequality, its accepted solution
satisfies `UA_required ≈ UA_installed` together with gas-side
and CO₂-cycle first-law balances. It also checks stack temperature,
heater pinch and a stream exergy bound. It **does not** invoke a
fictional bypass or usable-area adjustment.

Read [the coupled operating-point specification](docs/G31_FIXED_UA_COUPLING.md)
and run `python scripts/fixed_ua_coupled_demo.py` with CoolProp
installed to generate an explicit real-fluid source-temperature
perturbation report.

No physical cooler-UA coupling, measured equipment maps or transient
control is implemented. The initial heater-UA value in the example is
sized from a chosen hypothetical nominal operating point, not
measured hardware or a published benchmark.

## G3.2 — two installed UAs, finite cooling stream and sensible-source cp

The new `sco2_braytonbench.coupled_plant.solve_coupled_plant`
function calculates both **compressor inlet T1** and **turbine inlet T4**
from an installed heater UA, installed cooler UA, finite hot-gas flow,
finite cooling-medium flow and a fixed-UA recuperator.

The coolant outlet and exhaust gas outlet temperatures follow separate
enthalpy balances; pinch and stack constraints are enforced. A
documented linear sensible-heat-capacity model can be used for both
streams, while constant cp remains the default for compatibility.
An optional separately identified **quadratic flow-loss scaling scenario**
is provided for sensitivity only, not a measured map.

Read [the G3.2 physics and verification scope](docs/G32_COUPLED_COOLING.md) and the [G3.2 numerical verification](docs/G32_NUMERICAL_VERIFICATION.md).
The model is still steady-state, with no phase change, real turbomachinery
maps, calibrated heat-transfer correlations or transient control.

## Source literature

- Friedman, P. D., and Rapp, M. P. (2016), *Parametric Analysis of SCO2 Power Cycles Operating at Moderate Temperatures*, 5th International Symposium on Supercritical CO₂ Power Cycles, Paper 51. Supports pressure-network mapping, recuperator-pinch methodology and moderate-temperature cycle studies.
- Mohagheghi, M., and Kapat, J. (2014), *Thermodynamic Optimization of Recuperated S-CO2 Brayton Cycles for Waste Heat Recovery Applications*, 4th International Symposium on Supercritical CO₂ Power Cycles. Supports open-loop source-gas balances and the distinction between maximum net-power and maximum-efficiency cycle designs.

See [measured-density and identifiability evidence](docs/EXPERIMENTAL_DENSITY_AND_IDENTIFIABILITY.md), [source distinctions](docs/REFERENCES.md), [FR2016 source/benchmark review](docs/FR2016_COMPARISON_REVIEW.md), [real-fluid reference verification](docs/REFERENCE_VERIFICATION.md), [research gate status](docs/RESEARCH_STATUS.md), and [verification protocol](docs/VERIFICATION.md).

## Explicit exclusions

This is **not a CARBOSOLA digital twin**. No HZDR rig data, experimental campaign, real-sCO₂ cycle benchmark replication, source plant dynamic model, PI/MPC controller, or techno-economic optimum is claimed. An ideal-gas test-fluid result must never be labelled as a CO₂ prediction.

The related [HTHP-ControlBench](https://github.com/Open-Energy-Methods/hthp-controlbench) is a separate repository; general testing/control methods may be adapted, but their physics models remain independent.

BSD-3-Clause license. AI-assisted work is subject to scientific and human review.
