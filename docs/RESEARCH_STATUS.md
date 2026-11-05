# Research and verification status

Updated: 2026-11-05. **Pre-alpha research software — PR #1 remains draft.**

The repository is independent of HTHP-ControlBench, and it is
**not** a CARBOSOLA digital twin.

## Provenance

- **Friedman & Rapp (2016):** Figure 2b state/pressure graph is
  visually reviewed. A 12-point **conceptual-cycle** comparator has
  now been implemented separately from the six-state waste-heat
  prototype. The original authors' complete Figure 4 EES model is
  not reproduced.
- **Mohagheghi & Kapat (2014):** RC/RRC layouts and finite gas
  heat-exchanger assumptions are source-audited. Their REFPROP/GA
  optimizations have not been numerically reproduced.
- **NIST REFPROP User's Guide (2013):** published CO2 state values
  at 293.15 K are recorded for version-controlled cross-implementation
  checks (density and reference-offset-safe enthalpy/entropy deltas).
  See `docs/REFERENCE_VERIFICATION.md`.
- **Analytic test fixture:** ideal gas, not actual CO2; used for
  pressure, enthalpy and conservation logic tests only.
- **CoolProp:** optional HEOS backend and CI reference tests; real
  fluid cycle validation remains pending independent review.

## Verification gates

| Gate | Status | Closure conditions |
|---|---|---|
| G0 — original-paper provenance | Partial | Unidentified Figure 4 EES assumptions documented |
| G1-A — algebraic invariants | Local & CI fixture tests passed | Maintain CI |
| G1-E — real CO2 EOS | **Open / reference tests in CI** | Check numerical comparisons and broaden domain |
| G2 — FR2016 numerical reproduction | **Open** | Source-model identifiability and quantitative reproduction |
| G3 — waste-heat transfer | Partial prototype | Real-fluid heater and fixed geometry validated |
| G4 — conserved transient plant | Not implemented | Mass/energy inventories |
| G5 — PI/MPC | Not implemented | Controlled plant and safety authority |
| G6 — economics/modular | Not implemented | Validated operating scenarios |

Even if the new NIST and near-critical density tests pass,
they do not close the entire G1-E gate without uncertainty and
a broader domain of independent thermodynamic comparisons.

No hardware or experimental sCO2 performance is claimed.
The earlier v0.5 package was not available for import; this
repository contains a fresh and explicitly labelled reconstruction.
