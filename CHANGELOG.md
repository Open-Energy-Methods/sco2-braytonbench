# Changelog

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
