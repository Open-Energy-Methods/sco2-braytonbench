# v1.0 release contract — sCO₂-BraytonBench

**Initiated:** 2026-11-06. **Status:** proposed acceptance contract, NOT a release or a claim of plant validation.
**Base:** integrated `main` at `217bb27` (`pyproject.toml` version `0.5.0a0`); independently reviewed research in draft [PR #19](https://github.com/Open-Energy-Methods/sco2-braytonbench/pull/19); historical report in draft [PR #21](https://github.com/Open-Energy-Methods/sco2-braytonbench/pull/21).

## One-sentence release claim

A **reproducible, numerically verified research software toolkit** for steady recuperated CO₂ Brayton-cycle and finite-source waste-heat calculations, with separately labelled experimental component-correlation benchmarks and a narrowly bounded, conservation-checked **synthetic thermal transient/control demonstration**. It is **NOT** a CARBOSOLA digital twin, a geometry-calibrated power-cycle model, or a validated full-CO₂-inventory transient.

## Stable versus experimental boundaries

| Component | Candidate v1.0 status | What it can claim | What it cannot claim |
|---|---|---|---|
| `cycle`, `core`, `exchangers` | Stable numerical core after contract tests | Closed six-state balance under declared assumptions | Real plant power, turbomachinery performance maps |
| `fixed_ua`, `coupled_plant`, `whr` | Stable **illustrative** finite-source steady model after numerical audit | Two installed-UA equalities; pinch/stack and finite source/sink checks | Measured heat exchanger UA, bypass, hardware response |
| `properties`, `references`, `hydraulics` | Source-limited and unit tested | Version-pinned CoolProp and specific published reference checks | Independent near-critical full-property uncertainty quantification |
| Stuttgart H1a–H1c | Reproducible **research benchmark**, not design API | Measured-derived local HTC source comparison and transfer failures | Validated industrial PCHE/recuperator coefficients |
| Kim H1d (PR #19) | **Experimental, excluded from stable default** until source gate | Exact published interpretation audit, including out-of-domain negative comparisons | Confirmed Eq.24 correction or original-paper 620-point replication |
| Thermal-wall control volume | **Analytical demonstration only**, first substep of G4 | Explicit thermal capacitance, exact constant-input solution and first-law closure | CO₂ inventories, flow/pressure transient, turbine inertia, actual CARBOSOLA response |
| PI/load-profile/TEA | Pending separate WPs | Only after code, tests and evidence exist | Existing features, optimal operation or economic predictions |

**SemVer 1.0** means the documented API, examples and defined numerical tests are supportable. It does not upgrade experimental scientific validation. We will not relabel synthetic data as measured results.

## Required work packages / independently reviewable PRs

| WP | Required output | Gate |
|---|---|---|
| WP0 | This contract, source/provenance baseline, truthful README/limitations, traceability matrix | Architectural decisions and explicit version scope accepted |
| WP1 | Input-domain guards, dimensional/conservation/infeasibility checks, numerical convergence and built-distribution checks | Targeted tests green, no regression in real-CO₂ CI |
| WP2a | Analytically solved heat-capacitance control-volume kernel | Independent exponential limiting solution, integrated heat/storage closure, time-step invariance |
| WP2b | [Finite gas→stored wall→quasi-steady Brayton cycle](G4_WP2B_FINITE_SOURCE_WALL_CYCLE.md), independent analytic fixture, RK4 energy ledger | **Implemented on stacked PR #23; CI and independent review pending.** No CO₂-inventory transient, calibrated UA or G3.2 finite-coolant dynamics |
| WP3 | [Source gas-bypass mass split + downstream mixing + sampled wall PI](G5_WP3_BYPASS_PI_CONTROL.md) | **Implemented in stacked draft PR #24; all-source/real-fluid CI and independent review required.** Actuator flow fraction is idealised, not a calibrated valve |
| WP4 | [Prospective measurement, uncertainty, safety and holdout protocol](WP4_EXPERIMENTAL_READINESS_PROTOCOL.md), 35 candidate channels, 13 cases, tested software quality gates | **Implemented in stacked draft PR #25; complete CI and external review still required.** No installed/calibrated sensor status, facility authorization or measurements asserted |
| WP5 | [Acceptance, immutable-source and data-rights gates](WP5_RELEASE_ACCEPTANCE.md), wheel/sdist fresh replays, offline fingerprint/comparison and CFF/SPDX audit | **Implemented on stacked draft WP5 PR, final-head CI and independent review pending.** A tag/DOI is expressly NOT produced by this work |
| WP6 optional | Assumption-led net-energy and cost sensitivity | Explicit source and assumptions; not industrial TEA validation |

Do **not** treat numerical success as independent scientific accuracy. A no-root, multiple-root, nonfinite or phase-invalid state must raise an explicit, documented exception rather than returning an apparently legitimate operating point.

## Non-negotiable numerical and scientific gates

1. All state and public inputs are SI units: Pa, K, J/kg, W, W/K, kg/s, s, J/K. Reject nonfinite inputs at API boundaries.
2. Independent textbook/constant-property fixtures and real-CoolProp runs are **different evidence classes** and their results must not be confused.
3. Establish conservation residual scales and time-step/segment sensitivity on multiple physically feasible states; report infeasible cases and limits.
4. A transient **thermal wall** uses finite stored energy with analytically verifiable heat-rate integrals. Do not claim CO₂ mass/inventory conservation unless separately implemented and verified.
5. Keep 54 original Stuttgart runs, 2,508 axial records, STU-001 anomaly quarantine, fixed four held-out families and experimental/reduced-data provenance.
6. For correlations compare on identical solved station IDs and retain solver failures in the total candidate denominator; do not market a measured-wall-conditioned score as independent prediction.
7. Independently review original equations and applicability. For Kim Eq.24/Table 4, issue #20 stays OPEN; the sign hypothesis is not an author-confirmed correction.
8. All release artifacts must install in a fresh environment, generate declared examples, and carry reproducible source and machine-readable evidence.
9. The release citation, semver, license, supported Python versions and current scientific limitations must agree.

## Acceptance and promotion sequence

`main` stays `0.5.0a0` until the verified WPs are integrated. Produce `v1.0.0-rc1` only after all mandatory gates are green on the same source commit. A final `v1.0.0` tag/Zenodo snapshot follows independent review; neither a tag nor a passing CI can certify experimental plant validity. Historical `2026-11-05` reports are frozen records, not rewritten to make future work appear earlier.

Reference: [Verification matrix](V1_0_VERIFICATION_MATRIX.md); [Thermal CV scope](G4_THERMAL_CONTROL_VOLUME_SCOPE.md); [Existing research gates](RESEARCH_STATUS.md).
