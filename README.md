# sCO₂-BraytonBench

**Research software for modelling, verification, and control of recuperated supercritical-carbon-dioxide Brayton power cycles for industrial waste-heat recovery.**

[Open Energy Methods](https://github.com/Open-Energy-Methods) · Independent research / reproducible engineering

> **Status: pre-release research prototype.** This repository is being initialized from a separately audited v0.4 design/verification package and two source-paper audits. The earlier v0.5 numerical implementation is not yet imported. **No real-CO₂ cycle validation, experimental validation, or CARBOSOLA digital-twin capability is claimed.**

## Research objectives

1. Implement traceable real-fluid CO₂ thermodynamic properties and independently check component calculations.
2. Reconstruct the **Friedman & Rapp (2016)** recuperated-cycle pressure network separately from a simplified six-state cycle.
3. Represent finite industrial waste-heat supply using gas-side energy balance and main-heater pinch constraints, following the design framing of **Mohagheghi & Kapat (2014)**.
4. Progress through gated steady-state, dynamic, PI/MPC, uncertainty, and techno-economic studies **only after** the underlying conservation and numerical checks pass.

## Modelling boundaries

- The benchmark source cases are steady-state *research models*, not CARBOSOLA performance measurements.
- **CARBOSOLA geometry, control architecture, and experimental data are not available here.**
- An analytic constant-property test fluid may be used to verify implementation and conservation, but is **not** a substitute for real-CO₂ results.
- Maximizing waste-heat-recovery **net power** may differ from maximizing thermal efficiency; both must be reported with clearly defined boundaries.
- Experimental experience with an sCO₂ rig is **not claimed**.

## Current structure

See `docs/` for the imported source provenance, original v0.4 plan, and verification protocol. Implementation and continuous integration are introduced on a separate pull request.

## Reference studies

- Friedman, P. D., & Rapp, M. P. (2016), *Parametric Analysis of sCO2 Power Cycles Operating at Moderate Temperatures*. 5th International Symposium on Supercritical CO₂ Power Cycles, Paper 51.
- Mohagheghi, M., & Kapat, J. (2014), *Thermodynamic Optimization of Recuperated S-CO2 Brayton Cycles for Waste Heat Recovery Applications*. 4th International Symposium on Supercritical CO₂ Power Cycles.

This project is **independent of** [HTHP-ControlBench](https://github.com/Open-Energy-Methods/hthp-controlbench); tested engineering methods may be adapted, but neither project's physics modules should be made dependent on the other.
