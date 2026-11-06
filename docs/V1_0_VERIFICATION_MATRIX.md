# v1.0 requirements-to-evidence matrix

**Baseline captured:** 2026-11-06, initial v1.0 foundation. This file must track **evidence and failures**, not simply mark planned components complete.

Legend: **P** passed on the scoped existing evidence; **PARTIAL** evidence is limited; **OPEN** not implemented/reviewed; **BLOCKED** external provenance/data.

| ID | Requirement | Baseline evidence | Status | Proof required to close |
|---|---|---|---|---|
| R-01 | Six-state SI-unit cycle conservation | `tests/test_model.py`, `test_heat_exchanger_analytical.py`, real-fluid CI; `docs/VERIFICATION.md` | P (fixtures), PARTIAL (physical scope) | Stable API checks, numerical edge and near-critical cases |
| R-02 | Independently measured CO₂ density | Mantilla (2010) NIST ThermoML, 49 measured data; RMS 0.034731%; max 0.090241% | P (density observations), PARTIAL (property validation) | h/s/cp and near-critical independent measurement coverage |
| R-03 | Source-model identity | Friedman–Rapp 2016 12-state **conceptual** comparator: 24.305795% vs 24.381238% published | PARTIAL | Never claim Figure 4 EES source-equivalent without source state data |
| R-04 | Finite-source, fixed-UA balances | G3/G3.1/G3.2 CI source/sink and analytic fixtures | P (numerical examples), PARTIAL (parameter identification) | Reproducible range and failure-domain diagnostics |
| R-05 | HX segment sensitivity | Two prescribed-state G3.3 cases, 6/12/24/48 sections | PARTIAL | Wider state grid, pinch-margin and coupled-root convergence |
| R-06 | Stuttgart data provenance and quarantine | 54 experiments; 2,508 source axial records; 2,318 H1b eligible points; four SHA256-defined holdout families | P (source ingestion) | Preserve exact source ledger in all future merges |
| R-07 | Correlation predictive validation | H1a–H1c numerical experimental-derived HTC comparison | OPEN | Independent in-domain validation; do NOT substitute CI passes |
| R-08 | Kim Eq.24 source parity | Original PDF read, Table 4 registry and H1d three interpretation tests, PR #19 | BLOCKED | Authoritative erratum/code/original fitting data; issue #20 |
| R-09 | Thermal CV analytic solution | `src/sco2_braytonbench/thermal_dynamics.py` + dedicated tests on this branch | OPEN until CI | Closed form, integrated first law, zero/finite time-step and domain tests |
| R-10 | Thermal-coupled finite-source Brayton response | [WP2b physical scope](G4_WP2B_FINITE_SOURCE_WALL_CYCLE.md), synthetic finite stream/thermal storage and quasi-steady six-state model (stacked PR #23) | PARTIAL, pending CI and independent review | Match exact zero-recuperator limit, integrated whole-system energy, real-CoolProp smoke, step refinement; full CO₂ inventory still OPEN |
| R-11 | Physical actuator and PI | Not implemented in BraytonBench | OPEN | Actuator energy path, bounds, sample-time and antiwindup tests |
| R-12 | Experimental readiness | External source inventory `docs/G34_EXTERNAL_VALIDATION_INTAKE.md` | PARTIAL | Instrumented operating-point matrix, uncertainty and identification plan |
| R-13 | Technoeconomic comparison | Not implemented | OPTIONAL | Parameter provenance and same-load energy/cost comparison |
| R-14 | Distribution reproducibility | pytest/Actions on 3.11/3.12; no v1 built wheel/source install gate | OPEN | Build `sdist`+wheel, fresh-install each, run examples, license/CFF audit |
| R-15 | Historical and scientific honesty | Original stacked PRs integrated by #18; H1d draft #19, archival report draft #21 | P (history), OPEN (v1 review) | Review/freeze updated limitations and release statements |

## Current action order

1. Record WP0 decisions; exclude Kim source ambiguity from stable API promotion.
2. Strengthen numerical input guards without altering correctly computed historical benchmark values.
3. Add independent thermal-CV exact-solution checks as **WP2a only**.
4. Run full CI and inspect failed numerical examples; do not assume fixtures equal real-fluid verification.
5. Integrate further transient coupling and PI work in small reviewable PRs.
6. Conduct release candidate/packaging validation after implementation, not prematurely.

**Evidence quality hierarchy:** actual measured independent data > externally sourced calculation with mapped assumptions > independent analytical fixture > same-code reproduction > synthetic scenario > unit-test execution alone. Evidence in one tier does not imply another.

## Examples of gates that stay open even if all tests pass

- No CO₂ inventory dynamics or real turbomachinery speed/flow response.
- Installed UA values in G3.1/3.2 are generated from chosen hypothetical nominal conditions, not measured equipment geometry.
- All Stuttgart heat-flux points exceed the original published Kim fit range (25.9/26.9 kW/m² maxima); source coefficients remain ambiguous.
- An absent compressor map is not replaced by a fixed isentropic efficiency and relabelled a calibrated map.
- No CARBOSOLA experimental signals, commissioning records or hardware-dependent PI constraints are in the repository.
