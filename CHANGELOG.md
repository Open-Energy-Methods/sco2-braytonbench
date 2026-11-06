# Changelog

## Unreleased — WP4 prospective metrology and experimental design (2026-11-06)

- Added 35 *candidate*, unconfirmed sensor/metadata channels; 13 proposed and **unapproved** steady/transient/control/holdout cases; blank traceable standard-uncertainty register.
- Added strict CSV/DAQ sample schema, provenance/readiness blocking checks, first-order JCGM sensible-gas heat-duty uncertainty with temperature covariance and local experimental sensitivity-rank screening.
- Added independent mathematical/fault-injection tests and a synthetic data-format fixture; audit outputs readable CSV/JSON blockers without any fabricated plant measurements.
- Added a staged prospective CARBOSOLA **adaptation** and safety/holdout protocol. No facility access, instrument calibration, approval, measured time series or experimental validation is claimed.
- Package version remains `0.5.0a0`.

## Unreleased — WP3 source-gas bypass and sampled PI (2026-11-06)

- Adds finite hot-gas bypass **mass split**, uncooled branch return, constant-cp source enthalpy mixing, and wall/cycle first-law checks against the **total** source stream.
- Adds causal sampled wall-temperature PI with negative thermal-gain sign, position/rate limits, minimum flow, tracking back-calculation and bounded integral state. Fixed-bypass and PI compare on identical source scenarios.
- Adds independent analytical fixture tests (source mass/enthalpy, rate, anti-windup, no future-lookahead, infeasibility); matched synthetic scenario machine-readable CSV/JSON; separate real-CoolProp numerical smoke.
- The synthetic example shows a tracking/energy-output trade-off, not universal controller optimality.
- **No** industrial hardware/turbomachinery actuator maps, full CO₂ inventory dynamics or CARBOSOLA measurement validation. Package remains `0.5.0a0`.

## Unreleased — WP2b finite-source / storage / quasi-steady cycle (2026-11-06)

- Added finite constant-cp exhaust-flow gas→wall UA, genuinely dynamic lumped wall energy state, and a separate **installed wall→CO₂ UA** solved against the existing six-state Brayton heater duty. No double-counted direct gas→CO₂ heater.
- RK4 integration with corresponding gas, wall, CO₂ heater, shaft and cooler time-integral ledger, step-size gate and explicit infeasible-root/approach/stack failures.
- Independent constant-property/zero-recuperator exact-limit checks, piecewise source temperature/mass-flow disturbance example, machine-readable CSV/JSON evidence and optional real-CoolProp numerical smoke in CI.
- Still no CO₂ fluid inventory, pressure transients, physical actuator, PI/MPC, measured UAs or CARBOSOLA dynamic validation. Remains `0.5.0a0` until release gates pass.

## Unreleased — first v1.0 research-foundation increment (2026-11-06)

- Added a scoped v1.0 release contract and evidence traceability matrix; no change to package version (`0.5.0a0`), tag, measured hardware claims, or stable industrial model status.
- Added stand-alone exact analytical thermal-wall control-volume integration, independent exponential tests, signed time-integrated heat/storage conservation and synthetic profile evidence. This is **not yet a transient CO₂ Brayton-cycle solver**.
- Hardened nonfinite/invalid SI numeric inputs to the steady cycle and exchanger calculations; added fail-closed domain regression tests.
- Added dedicated CI for WP1 numerical guards, WP2a analytical thermal CV and machine-readable synthetic trace.


## Unreleased — initial research foundation (2026-11-05)

- Established standalone Open Energy Methods repository, Python packaging and GitHub Actions.
- Reconstructed six-state steady cycle, limited source-paper 12-point pressure map and finite source-gas heater.
- Introduced optional CoolProp CO₂ properties but kept numeric validation gates **open**.
- Added analytic-fixture regression tests, source provenance, contributing guide and gate status.
- This is a **reconstruction**, not an import of the originally described but unavailable v0.5 software archive.

See `docs/RESEARCH_STATUS.md` for limitations and verification state.
