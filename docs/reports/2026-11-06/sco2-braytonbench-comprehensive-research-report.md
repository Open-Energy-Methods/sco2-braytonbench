---
title: "sCO₂-BraytonBench — Comprehensive Research and Engineering Report"
subtitle: "Current integrated software, physical model, source evidence, numerical verification, control, experimental readiness, release governance and HZDR research relevance"
author: "Open Energy Methods — project research record"
date: "2026-11-06"
lang: "en-GB"
report-status: "Research software technical record; not experimental plant-validation certification"
---

# sCO₂-BraytonBench — Comprehensive Research, Engineering and Verification Report

**Current integrated research record — 6 November 2026**

> **Reading warning:** This report describes a numerically verified research software prototype. A passing first-law test, exact synthetic solution, or real-fluid CoolProp calculation is **not equivalent** to independent measured validation of an sCO₂ power plant. The present repo does not contain a CARBOSOLA experimental campaign, a full transient CO₂ inventory model, calibrated bypass valve hardware or an authorised plant controller. Claims must remain scoped accordingly.

## Contents and navigation

| Part | Sections and subject |
|---|---|
| **I — Identity and motivation** | 0. Control and evidence policy; 1. Executive assessment; 2. Scientific questions and application context; 3. Research chronology; 4. Architecture and provenance |
| **II — Physical modelling** | 5. State map and conservation; 6. Thermophysical properties; 7. G0/G2 literary comparisons; 8. G3 finite source; 9. G3.1 fixed heater UA; 10. G3.2 coupled cooler; 11. G3.3 properties, hydraulics and numerical resolution |
| **III — Measured-derived evidence** | 12. G3.4 source-intake policy; 13. Stuttgart H1a; 14. Bishop/Jackson H1b; 15. Lei H1c; 16. Kim H1d and unresolved publication ambiguity; 17. External experimental density and rights |
| **IV — Time-dependence and control** | 18. WP0/WP1 mathematical contracts; 19. WP2a thermal wall; 20. WP2b coupled source/wall/cycle; 21. WP3 source bypass and sampled PI; 22. Controller numerical evidence and limitations |
| **V — Readiness and reproducibility** | 23. WP4 candidate measurements and campaign; 24. Metrology, covariance and identifiability; 25. WP5 distribution and offline release audit; 26. Tests/CI traceability; 27. Licensing and copyright review |
| **VI — Decisions and continuation** | 28. Uncertainty and risk ledger; 29. Acceptance and release status; 30. HZDR doctoral-research alignment; 31. Scientific roadmap; 32. Reproduction instructions; 33. Sources and file index; 34. Preservation conclusions |

---

# Part I — Research identity, purpose and provenance

## 0. Document control and evidence policy

| Field | Recorded status |
|---|---|
| Software / public project | **sCO₂-BraytonBench**, GitHub [Open-Energy-Methods/sco2-braytonbench](https://github.com/Open-Energy-Methods/sco2-braytonbench) |
| Publisher / maintainer | Open Energy Methods; \`CITATION.cff\` names Abhijith Sivaprasadan |
| Package name and current version | \`sco2-braytonbench\`, **0.5.0a0** (alpha; not v1.0) |
| Snapshot commit | \`8df1711a425e21da342bd3f401da61a1375bbc0a\` on \`main\` |
| Snapshot date | **6 November 2026** |
| Source licence | **BSD-3-Clause** for original repository software; third-party datasets retain **their own** terms |
| Current integrated GitHub PRs | #22 (WP0/1/2a), #23 (WP2b), #24 (WP3), #25 (WP4), #26 (WP5), #29 (data-rights cleanup) |
| Earlier development preserved | Source-to-model stages G0–G3.5; historical 5 Nov report is on draft [PR #21](https://github.com/Open-Energy-Methods/sco2-braytonbench/pull/21) |
| Unmerged exploratory research | [PR #19](https://github.com/Open-Energy-Methods/sco2-braytonbench/pull/19), Kim 2019 Eq. (24) source discrepancy |
| Integrated-main CI | [GitHub Actions run #42266275348](https://github.com/Open-Energy-Methods/sco2-braytonbench/actions/runs/42266275348), **20/20 jobs successful** |
| Current external blockers | [Issue #27](https://github.com/Open-Energy-Methods/sco2-braytonbench/issues/27): historical Mantilla data rights; [issue #28](https://github.com/Open-Energy-Methods/sco2-braytonbench/issues/28): qualified external review |
| Release / DOI | No v1.0 tag, new GitHub release or Zenodo DOI is represented by this report |
| Regulatory / laboratory implication | None; no permission to operate real pressurised machinery or bypass safety interlocks |

### 0.1 Evidence grading convention

The report deliberately separates evidence into six classes:

**E1 — executed CI/numerical outputs.** A recorded test run, build artifact, example trace, measured/derived regression metric or comparison produced by actual code under stated inputs.

**E2 — source implementation and analytical test.** Mathematical expressions traceable to a named module and a test whose independent derivation can be reviewed. E2 means the software implements the described mathematics, not that nature matches the assumptions.

**E3 — licensed, attributed measured-derived source.** Published experimental records with a known transformation path and source conditions. Source quality and correlations still require explicit limitations.

**E4 — original scientific literature.** Equations, reference values and physical context identified to the original publication; claims are attributed to authors and are not automatically reproduced by the project.

**E5 — research inference or editorial interpretation.** Scientific reasoning about model suitability, lessons, limitations, acceptance policy and research direction. These are not independently measured truths.

**E6 — proposed, unexecuted or externally blocked.** Planned instrumentation, identification, approvals, new experiments, data permissions, human sign-off or future physics that should never be described as complete.

Some historical files use dated language such as “G4/G5 not implemented.” They accurately record the preceding G3.5 snapshot, but **are superseded as a current software-status description** by the WP2a–WP5 integration. Conversely, a historical measurement comparison is not invalidated by removal of the unlicensed *transcribed* CSV from HEAD; it becomes historical evidence that is no longer rerun in default CI.

### 0.2 How to read numerical values

All pressures are **absolute** unless explicitly identified otherwise. Temperature differences in kelvin can also be stated in °C difference, but absolute input temperatures are in K. Thermal duty, net shaft power and electrical power are distinct system-boundary quantities.

“Installed UA” describes a specified total conductance used as an equality or a component rating. “Required UA” describes an exchanger sizing demand calculated from heat rate and temperature approaches. Confusing these reverses the engineering meaning of G3 versus G3.1/3.2.

“Real CO₂” means CoolProp's thermophysical equation of state was evaluated in an idealised cycle. It does **not** imply the geometric, pressure-drop, mechanical or control parameters have been measured.

The supplied numerical outputs are generally **fixed scenario values**, not uncertainty intervals. Intervals and residuals are not statistical confidence statements without a stated model, measurement covariance, sampling process and coverage calculation.

## 1. Executive assessment

### 1.1 Core achievement

The repository evolved from an auditable six-state recuperated Brayton-cycle reconstruction into a layered sCO₂ research programme combining: finite hot-source screening, heater/cooler installed-UA boundary-value problems, source-grounded property/hydraulic options, sensitivity to exchanger discretisation, external experimentally reduced heat-transfer comparison, a *genuine stored-wall thermal ODE* coupled to an algebraic cycle, a conserved hot-gas bypass with bounded sampled PI control, prospective laboratory metrology/data protocols, and offline release reproducibility gates.

The distinctive engineering practice is not the existence of a cycle solver. It is the insistence that every physical claim has a named model scope, an admissibility range, a measured-versus-synthetic classification, a versioned source, and a test/CI or documented evidence gap.

### 1.2 What has demonstrably passed

- Six-state cycle and finite-source model tests with real-fluid CoolProp-specific jobs, plus independent synthetic ideal-gas and conservation fixtures.
- Numerical screen of candidate waste-heat operating points with explicit source, approach, installed/required UA and cooler consequences.
- Fixed-UA single- and dual-exchanger inverse solutions on documented examples.
- Heat-transfer study with exactly tracked original Stuttgart rows, excluded anomalies and stratified top/bottom error.
- Independent analytical transient wall solution, finite source and wall-to-CO₂ heat ledger, and step refinement.
- A bounded sampled bypass PI demonstration with conserved source mass and enthalpy and explicit heat-recovery versus tracking trade-off.
- 35 **proposed/unconfirmed** experimental channels and 13 **proposed/unapproved** laboratory cases, validated as data schemas but not field measurements.
- Machine-readable offline release audit, separate wheel/sdist build and installation, same-scenario output comparison, and SHA256 evidence manifests.
- Latest integrated HEAD \`8df1711a…\` with [20 successful CI jobs](https://github.com/Open-Energy-Methods/sco2-braytonbench/actions/runs/42266275348).

### 1.3 What has not been demonstrated

No experimental CARBOSOLA power-cycle validation, turbine/compressor machine map identification, inventory-based full CO₂ transient, hydraulic bypass valve \`C_v\` relation, plant-approved control, verified installed sensor list, calibrated wall thermal capacity, measured PCHE geometry-specific UA transfer, rigorous techno-economic optimum or independent human reviewer approval exists in the integrated baseline.

Measured-derived local heat-transfer correlations exhibit substantial prediction errors, especially in thermally stratified top-wall zones. A small first-law residual shows coherent mathematical accounting; it does not heal those physical gaps.

### 1.4 Release decision

The sensible present state is **integrated and CI-verified alpha research software**. Source distribution and GitHub current HEAD no longer contain the 49-row Mantilla transcription with uncertain downstream rights, but older public Git commits remain an unresolved historical reuse problem. Requests for written rights clarification and for an independent scientific review have been prepared; external approvals are not recorded.

A formal v1.0 is reasonable **as a correctly limited research software release**, but only after license/history assessment, reviewer sign-off and a deliberate versioned candidate procedure. The project need not falsely claim a complete plant digital twin to become useful scientific software.

## 2. Scientific motivations and research questions

### 2.1 The practical problem

Recovering industrial waste heat through a recuperated supercritical-CO₂ Brayton loop is a coupled problem. The available heat stream is finite; compressor work can vary steeply with inlet state; recuperator pinch can dictate feasibility; cooling requirements affect the cycle boundary condition; and high-temperature heat-exchanger materials/geometry must deliver the assumed conductance.

A single imposed turbine inlet temperature is inadequate for judging what real heat-source conditions can sustain. A nominally attractive net power condition may violate gas-stack minimum temperature, exchanger approach or installed heat-transfer area. A high predicted thermal efficiency may occur at low absolute recovered energy. Correct model formulation must make those trade-offs explicit.

### 2.2 Primary research questions

1. **Thermodynamics:** Does a transparent six-state recuperated solver conserve energy and reproduce documented analytical limits at physically feasible property states?
2. **Finite waste heat:** How do exhaust temperature, gas heat-capacity rate, stack-temperature floor, CO₂ mass flow, turbine-inlet state, recuperator effectiveness/UA and heater approach combine to set feasible power?
3. **Installed hardware:** When heater and cooler UA are fixed rather than sized freely, which cycle temperatures are determined by the heat-transfer equations and which assumptions remain externally imposed?
4. **Thermophysical reliability:** How sensitive are cycle and exchanger results to EOS calls, sensible gas/coolant assumptions, wall/bulk temperature differences and numerical mesh resolution?
5. **Empirical transfer:** Do common and wall-conditioned pipe HTC correlations transfer to measured-derived horizontal sCO₂ data, particularly in strong circumferential stratification?
6. **Transient heat recovery:** Can the finite source, thermal wall and quasi-steady power cycle be coupled without treating unrelated steady solutions as a complete dynamic model or counting heater energy twice?
7. **Control under disturbances:** Can a bounded gas bypass regulate wall temperature and what recoverable shaft energy is sacrificed?
8. **Experimental identifiability:** What actual independent sensors, calibration data, time synchronization, operating-point variation and sealed validation groups would be necessary to infer useful physical parameters?
9. **Reproducibility and release:** Can a reader recover source and results using independent distribution formats, while preserving the right to redistribute every included evidence asset?

These research questions separate **what has been computed** from **what needs experimental access**.

### 2.3 HZDR research-role relevance, without misleading transfer

The HZDR doctoral topic on dynamic modelling and experimental investigation of supercritical CO₂ Brayton cycles in waste-heat recovery makes the modelling/evidence progression directly relevant: real-fluid thermodynamics, coupled heat-source behaviour, transient thermal storage, source-side control, instrument design and uncertainty. The report supports a job application as a portfolio artifact of methodology. It does not imply that HZDR endorsed, provided equipment for, or operated this repository, and its hypothetical flow rates/pressure boundaries must not be represented as CARBOSOLA specifications.

A doctoral research programme could expand these methods into inventory/rotating-machine dynamics and actually commissioned experiments; the missing parts are research opportunities, **not completed achievements**.

## 3. Development chronology and change control

### 3.1 Earlier G0–G3.5 reconstruction

The 5 November 2026 milestone reconstructed the thermodynamic cycle and multiple heat-source/exchanger boundary conditions, revisited Friedman–Rapp literature parity, tested property sources, consolidated GitHub development branches, and obtained source-attributed Stuttgart pipe heat-transfer data. The original comprehensive 1,245-line report is preserved on [draft PR #21](https://github.com/Open-Energy-Methods/sco2-braytonbench/pull/21), not silently rewritten to include subsequent work.

The early G3.5 H1d Kim analysis remained on exploratory [draft PR #19](https://github.com/Open-Energy-Methods/sco2-braytonbench/pull/19) because a discrepancy between original published equation notation and a coefficient-table exponent interpretation requires scientific source confirmation.

### 3.2 The new WP0–WP5 integration

| PR | Engineering work | Integration meaning |
|---|---|---|
| [#22](https://github.com/Open-Energy-Methods/sco2-braytonbench/pull/22) | WP0 research release contract, WP1 numerical domain checks, WP2a exact thermal-wall kernel and dedicated tests | Stable *alpha numerical* foundation, not transient CO₂ inventory |
| [#23](https://github.com/Open-Energy-Methods/sco2-braytonbench/pull/23) | WP2b finite gas→thermal wall→algebraic Brayton cycle, analytical comparisons, real-fluid compatibility check | Transient thermal subsystem with fixed quasi-steady power block |
| [#24](https://github.com/Open-Energy-Methods/sco2-braytonbench/pull/24) | WP3 source mass-split bypass, mixing first law, sample-bounded PI, actuator constraints, matched scenarios | Synthetic control study, not industrial valve calibration |
| [#25](https://github.com/Open-Energy-Methods/sco2-braytonbench/pull/25) | WP4 candidate measurement channels, prospective tests, GUM example, CSV validation, run provenance | Experimental *readiness method*, no data collected |
| [#26](https://github.com/Open-Energy-Methods/sco2-braytonbench/pull/26) | WP5 distributions, SHA256, dual-install numerical replay, release acceptance and technical audit | Engineering prerequisites, no automatic tag/release |
| [#29](https://github.com/Open-Energy-Methods/sco2-braytonbench/pull/29) | Current-HEAD removal of disputed NIST ThermoML table, optional external-data tests/report, archive failure gate | Reduced future redistribution exposure; historical Git risk remains |

All six were merged sequentially into \`main\` while preserving \`0.5.0a0\). A “merged” software PR means GitHub integration, **not independent peer review, licence approval or scientific field validation**.

### 3.3 Traceable integrated commits

The WP0–WP5 integrated development commit was \`88579f7ff8a723124744dde0ac53a38e8adf1837\`, verified by [20/20 CI jobs in run #42258225916](https://github.com/Open-Energy-Methods/sco2-braytonbench/actions/runs/42258225916).

The subsequent data-rights cleanup produced the current main SHA \`8df1711a425e21da342bd3f401da61a1375bbc0a\`. [Run #42266275348](https://github.com/Open-Energy-Methods/sco2-braytonbench/actions/runs/42266275348) succeeded in all **20** jobs. Thus the report's present state is **after** the cleanup, not the earlier CI checkpoint that had one job pending.

### 3.4 GitHub discipline

New claims should be introduced on a dedicated branch with code, independent tests, scientific context, machine-readable evidence where appropriate, and a PR specifying accepted and excluded functionality. The project should not automatically convert an exploratory numerical correlation or an unverified rights claim into the default stable API.

Every published number belongs to a run/commit and a supporting source. Source datasets should retain their provenance, historical anomalies and explicit attribution, rather than being silently corrected to improve a benchmark.

## 4. Repository architecture and roles

### 4.1 Top-level structure

| Location | Function |
|---|---|
| \`src/sco2_braytonbench/\` | Core property interfaces, cycle, recuperator/HXs, finite source, cooler, installed-UA solvers, thermal dynamics, bypass/PI, experiment-readiness utilities |
| \`tests/\` | Unit, domain, regression, analytic, numerical, source and optional real-CoolProp verification |
| \`examples/\` | Reproducible ideal-gas and real-fluid scientific examples; synthetic transient/control and prospective readiness scenarios |
| \`scripts/\` | Research benchmark scripts, original-source comparisons, reporting tools, WP5 offline release gate |
| \`data/reference/\` | Reference-source metadata and permitted model inputs; Mantilla 49-point CSV no longer in current HEAD |
| \`data/validation/\` | Attribution-labelled validation-source transformations, e.g. Stuttgart reduced measurements |
| \`data_requests/\` | Publication/data recovery requests, known source gaps and prospective intake templates |
| \`protocols/wp4/\` | Candidate sensor/channel registry, test matrix, blank standard-uncertainty ledger and synthetic DAQ-format fixture |
| \`docs/\` | Engineering derivations, source-recovery audits, numerical tables, physical limitations, release/rights decisions |
| \`evidence/generated/\` | Reproducible scenario artifacts when executed; CI uploaded artifacts are evidence tied to a run |
| \`.github/workflows/ci.yml\` | Independent Python-version, CoolProp, research and distribution gates |
| \`MANIFEST.in\` | Source archive include/exclude policy with explicit protection for disputed data |
| \`CITATION.cff\`, \`pyproject.toml\`, \`LICENSE\` | Authorship, software identity, supported versions, licensing and packaging contract |

### 4.2 Separation of independent roles

The **Properties** interface supplies thermodynamic state transformations; its correctness cannot be inferred from conservation tests alone. The **cycle** module performs nominal state and work/heat balances. Finite gas/coolant, recuperator and UA modules impose different boundary-value problems. **thermal_dynamics** is an analytically soluble wall kernel and is not an EOS. **dynamic_whr** couples a physically stored wall state to an algebraic cycle. **control_whr** alters source gas routing and uses only measured-like wall feedback *in a synthetic simulation*. **experimental_readiness** validates data structures and intended campaigns but does not access plant instrumentation.

This separation allows testing the equations at deliberately simple ideal-gas limits before exposing the model to real-fluid property nonlinearity. Equally, a real-fluid CoolProp smoke test is a useful compatibility check but cannot substitute for mechanical geometry and measurements.

### 4.3 Software dependencies and portability

The alpha package declares Python \`>=3.10\`, no unconditional runtime dependencies, and optional CoolProp \`>=6.6,<9\`. The cross-version CI test suite runs Python 3.10/3.11/3.12; the dedicated real-CO₂ checks pin a known CoolProp version for reproducible comparisons. The source package is under BSD-3-Clause; the Stuttgart data and any other third-party evidence require their separate source licenses and attribution.

The package's supported-domain claims are narrower than Python syntax compatibility: a numerical result is meaningful only for physically admissible temperatures, pressures, composition assumptions and component approach constraints.

---

