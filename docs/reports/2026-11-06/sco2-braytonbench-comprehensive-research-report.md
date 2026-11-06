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

# Part II — Thermodynamic models and installed heat-transfer boundaries

## 5. Six-state recuperated Brayton model: system boundary and laws

### 5.1 State numbering and physical interpretation

The baseline is a recuperated Brayton-cycle *mathematical abstraction* using six thermodynamic states. Actual piping and equipment geometry are not reconstructed from a plant P&ID.

| Station | Functional designation | What a measurement would require |
|---|---|---|
| 1 | Compressor inlet | CO₂ inlet pressure/temperature, composition, flow and near-critical margin |
| 2 | Compressor outlet / cold recuperator entry | Compressor pressure/enthalpy rise and efficiency reference state |
| 3 | Recuperator cold outlet / primary-heater inlet | Exchanger enthalpy and pressure, potential wall approach |
| 4 | Primary-heater outlet / turbine inlet | Turbine high-pressure boundary and allowable temperature |
| 5 | Turbine outlet / hot recuperator inlet | Turbine isentropic outlet relation, actual pressure/flow |
| 6 | Recuperator hot outlet / cooler inlet | Heat-rejection requirement and low-pressure heat-exchanger entry |

Topology is an assumption. The real HZDR demonstrator must be inspected before assigning these software station numbers to physical ports; some documented test stages may not have operated a turbine.

### 5.2 Compression and expansion

For compressor inlet 1 and compressor discharge pressure 2, the isentropic reference state has entropy \(s_{2s}=s_1\), while compressor efficiency gives:

\[
h_2=h_1+\frac{h_{2s}-h_1}{\eta_c},\quad
W_c=\dot m_{\rm CO2}(h_2-h_1).
\]

For turbine inlet 4 and outlet pressure 5:

\[
h_5=h_4-\eta_t(h_4-h_{5s}),\quad
W_t=\dot m_{\rm CO2}(h_4-h_5),\quad
W_{\rm net}=W_t-W_c.
\]

These are steady *device isentropic-efficiency relations*, not compressor and turbine maps, not speed-dependent pressure-flow constraints, and not shaft-inertia dynamics. For an ideal-gas fixture with constant \(c_p\) and gas constant \(R\), the isentropic temperature ratio is \((p_2/p_1)^{R/c_p}\), giving a textbook independent check.

Pressure loss terms for the recuperator cold side, primary heater, recuperator hot side and cooler are prescribed component inputs. Their numerical values in example cases are not calibrated pressure-loss maps.

### 5.3 Recuperator, external heater and cooler

The recuperator transfers enthalpy from the hot post-expansion stream to the colder post-compression stream. With separate hot/cold pressure losses, source/sink heat rates at an algebraic operating point must satisfy mass and enthalpy balances. The baseline can use prescribed effectiveness or segmented UA, but the two alternatives are not interchangeable independent design constraints.

At the steady cycle boundary:

\[
Q_{\rm heater}=\dot m(h_4-h_3), \qquad
Q_{\rm cooler}=\dot m(h_6-h_1).
\]

For the idealised complete cycle:

\[
Q_{\rm heater}-Q_{\rm cooler}-W_{\rm net}=0,\qquad
\eta_{\rm th}=W_{\rm net}/Q_{\rm heater}.
\]

A small residual means the code has reconciled its declared boundary terms. **It does not establish** that real fan/pump/valve parasitics, exchanger leakage, mechanical losses, electrical conversion or plant casing losses have been included.

### 5.4 Efficiency, recovered heat and net export

Three attractive but different optimisation targets must not be confused:

- \(\eta_{\rm th}\) compares net shaft power with heat *accepted into the modelled cycle*.
- \(W_{\rm net}\) is turbine-minus-compressor shaft power, subject to assumed efficiencies and pressure conditions.
- Source heat-recovery fraction compares absorbed thermal energy to the finite exhaust enthalpy potentially available above the declared stack floor.

High thermal efficiency can coexist with small recovered heat and low power. A credible power-plant objective must also consider auxiliary loads, rejected heat, installed equipment, unavailable heat, safety and economics.

### 5.5 Well-posedness and failure modes

A valid solution needs positive absolute pressure, positive thermodynamic temperature, finite mass flow, compatible pressure station ordering, valid fluid state evaluations and feasible recuperator/heater/cooler approaches. Nonphysical root branches or property exceptions are not to be silently converted into ordinary zero-power points.

Near the critical region, EOS behaviour is steep: finite-difference derivative conditioning, resolution and property-library version need explicit attention. There are no independently measured compressor maps or shaft dynamics in the integrated solver.

## 6. Thermophysical properties: EOS versus engineering assumptions

### 6.1 Property service contract

The software exposes thermodynamic states containing pressure, temperature, specific enthalpy and entropy. Properties can be obtained using \(p,T\), \(p,h\) and \(p,s\) transformations. The principal real-fluid backend is CoolProp CO₂; the artificial ideal-gas fixture supplies an independently controlled mathematical reference.

The ideal-gas fixture is **not a surrogate calibrated to sCO₂**. It is deliberately simple so conservation, inverse-UA and transient-wall algorithms can be verified against equations without hiding errors in numerical EOS inversion.

### 6.2 What “real-fluid verification” means

CoolProp can resolve nonideal density/enthalpy/entropy values and exhibit the strong thermal-property variation near supercritical operating states. A successful cycle solve with real CO₂ verifies compatibility between numerical algorithms and a thermophysical library for the tested pressures and temperatures.

It does not independently prove that CoolProp matches REFPROP or measured density over every fluid region. That requires separate source data and uncertainty analyses; library-to-library consistency is not the same as measurement independence.

### 6.3 Density reference and the present distribution change

Historical November 5 tests compared CoolProp 8.0.0 with **49 Mantilla et al. (2010) experimentally reported density points** over stated isotherms 310, 350, 400 and 450 K, spanning approximately 0.999–159.844 MPa. The historical recorded summary was:

| Historical statistic | Reported value |
|---|---:|
| Number of measured points | 49 |
| CoolProp backend | 8.0.0, HEOS::CO₂ |
| Mean relative residual | −0.005608% |
| RMS relative residual | 0.034731% |
| Maximum absolute relative residual | 0.090241% |
| Earlier tighter screen | 0.2% maximum / 0.1% RMS, passed |

**Current evidence caveat:** the 49-row normalized original-source transcription has since been **removed from current HEAD** because the downstream NIST ThermoML/journal-publisher redistribution grant is unconfirmed. Default CI therefore **does not rerun those measured-density observations**. The test and report now require a user-obtained external CSV through \`SCO2_MANTILLA_DENSITY_CSV\`; in its absence the measurement check is explicitly skipped. Historical values are historical run evidence, not a fresh current-version independent experimental validation claim.

See \`docs/EXPERIMENTAL_DENSITY_DECISION.md\`, \`data/reference/README_MANTILLA_OPT_IN.md\` and [rights issue #27](https://github.com/Open-Energy-Methods/sco2-braytonbench/issues/27).

### 6.4 Property-model boundary

A full time-dependent CO₂ volume model needs density and internal energy state transformations, consistent inverse \((\rho,u)\to(p,T)\), and a network of mass/enthalpy fluxes. The present property interface and quasi-steady six-state cycle do **not** supply that missing inventory model, even though CoolProp as a separate library supports richer property calls.

## 7. Friedman–Rapp 2016 comparison: meaningful but nonidentical models

### 7.1 Why it was investigated

The project's early literature work sought a credible source-to-model sanity check for recuperated Brayton thermodynamics. Friedman–Rapp (2016) provided a moderately heated cycle reference with reported nominal efficiency, making it more useful than an arbitrary textbook ideal-gas target.

A close matching headline is insufficient if the original paper’s internal state map, pressure losses, heat exchangers, turbine/compressor efficiency definitions and recuperator treatment differ.

### 7.2 Source-to-model numerical outcome

The historically recorded project comparison yielded about **24.3058%** thermal efficiency versus the literature table's **24.3812%**, a difference of approximately **−0.07544 percentage points** on the selected reconstruction. That is a numerical comparison under explicit assumptions, not exact recovery of the source's entire simulation.

The project documented that the original reference used a larger 12-state structure and model details that could not be fully identified from the accessible article. Therefore one cannot claim the proprietary/source EES model was reproduced or its hidden losses inferred uniquely from a single published efficiency number.

### 7.3 Structural limitation

The current six-state abstraction and the literature reference do not have identical thermal and pressure state maps. Calibrating unknown parameters until one efficiency matches would risk absorbing physical or numerical differences into arbitrary assumed losses.

The appropriate citation is \`docs/FR2016_COMPARISON_REVIEW.md\` together with \`docs/FR2016_ORIGINAL_MODEL_RECOVERY.md\`. Future parity requires published operating-point and state definitions, not merely another digit of efficiency agreement.

## 8. G3 — finite-source industrial waste-heat screening

### 8.1 Change from imposed inlet temperature

G3 introduced an explicit finite exhaust-gas enthalpy budget and heater temperature-approach constraints. Before that stage, an imposed turbine inlet state made the source effectively inexhaustible if not paired with an actual heat-source control volume.

For constant sensible exhaust \(c_p\), with source mass flow \(\dot m_g\):

\[
Q_g=\dot m_g c_{p,g}(T_{g,in}-T_{g,out}),\quad
Q_{g,\max}=\dot m_g c_{p,g}(T_{g,in}-T_{\rm stack,min}).
\]

This budget does not guarantee enough exchanger area/conductance to achieve a chosen duty. A counterflow temperature profile must remain feasible; the required UA must be computed and checked, rather than automatically assumed installed.

### 8.2 Illustrative screening inputs

The archived G3 screening example used:

| Quantity | Explicit example assumption |
|---|---:|
| Gas source | 100 kg/s at 760 K |
| Gas constant \(c_p\) | 1100 J/(kg·K) |
| Minimum stack temperature | 360 K |
| Minimum heater local approach | 10 K |
| Maximum allowed **sizing** UA | 1.2 MW/K |
| CO₂ compressor inlet | 8.5 MPa, 310 K |
| High-pressure turbine inlet | 24 MPa |
| Compressor / turbine efficiencies | 0.89 / 0.90 |
| Recuperator input | fixed 200 kW/K |
| Cold recuperator/heater/hot recuperator/cooler pressure losses | 100/150/100/50 kPa |
| Sampled turbine inlet temperatures | 550, 600, 650, 700, 770 K |
| Sampled CO₂ flows | 20, 40, 70, 100 kg/s |

The parameter grid and constraints are **illustrative and discretely screened**, not an industrial optimisation over all continuously accessible machine settings.

### 8.3 Power maximum and thermal-efficiency maximum were different points

| G3 result | Power-max selected point | Efficiency-max selected point |
|---|---:|---:|
| CO₂ flow | 100 kg/s | 20 kg/s |
| Turbine inlet T | 700 K | 700 K |
| Net shaft power | **8.109835 MW** | 1.621967 MW |
| Cycle thermal efficiency | 25.2184% | **33.5039%** |
| External heat absorbed | 32.1585 MW | 4.8411 MW |
| Cooler heat rejected | 24.0486 MW | 3.2192 MW |
| Stack outlet | 467.650 K | 715.990 K |
| Source sensible heat recovered | 73.087% | 11.003% |
| Recuperator minimum internal approach | 64.738 K | 4.627 K |
| Heater minimum approach | 13.108 K | 60.000 K |
| Heater **required** UA | 923.866 kW/K | 40.528 kW/K |

This contrast is central: the power-max solution uses far more source energy and requires far greater transfer surface/conductance. The efficiency-max solution achieves a larger *ratio* by consuming less heat. They are not competing measurements from one installed rig.

### 8.4 Additional imposed constraints

Under further hypothetical limits, archived selected points included power **4.983670 MW** at 70 kg/s / 650 K and efficiency **30.7281%** at 40 kg/s / 700 K. These are constrained scenario outputs, not independent performance measurements.

A numerical segmentation sensitivity on the original winners reported efficiency values that shifted slightly between 12, 24 and 48 heat-exchanger sections. The sensitivity indicates the chosen discretisation matters; it does not establish grid independence under all near-pinch states.

### 8.5 Engineering meaning

G3 is a **design screening/sizing tool**: it estimates which combinations demand a feasible \(\mathrm{UA}_{required}\). It does not force a single installed primary-heater UA across load cases, identify turbine maps, model actual pipe flow or enforce transient heat storage. That limitation motivated G3.1.

See \`docs/G3_WASTE_HEAT_DESIGN_SCREENING.md\` and \`docs/G3_STEADY_SCREENING_RESULTS.md\`.

## 9. G3.1 — solve the cycle around a fixed installed heater UA

### 9.1 A different boundary-value problem

Rather than computing the UA needed for a user-imposed \(T_4\), G3.1 fixes a hypothetical installed gas-heater conductance. The cycle state must respond to the finite gas source until:

\[
F(T_4)=\mathrm{UA}_{required}(T_4)-\mathrm{UA}_{installed}=0.
\]

The hot stream cools at finite flow; the CO₂ heating path satisfies its enthalpy duty; pinch and local exchanger profile remain admissible. A bracketed bisection avoids reporting an arbitrary root when the exchanger is infeasible.

### 9.2 Executed nominal and perturbed source example

The archived synthetic installed heater rating was approximately **21.783328 kW/K**. For a hot-gas inlet perturbation 800→810 K:

| G3.1 quantity | 800 K source | 810 K source |
|---|---:|---:|
| Fixed installed heater UA | 21.783328 kW/K | 21.783328 kW/K |
| Solved CO₂ turbine inlet \(T_4\) | **649.989014 K** | **658.953857 K** |
| Source gas exit | 758.003237 K | 767.638266 K |
| Net shaft power | 1.4238615 MW | 1.4599094 MW |
| Cycle thermal efficiency | 30.8218883% | 31.3299343% |
| Numerically required UA | 21.782025 kW/K | 21.782885 kW/K |
| UA residual | −1.303 W/K | −0.443 W/K |
| Relative UA error | 0.0059802% | 0.0020320% |

This is an **installed-UA equality response**, so the turbine inlet is an *output* of the coupled operating point, not the target imposed at all source conditions. Bisection/root stopping tolerance explains the small UA residual.

### 9.3 Independent mathematical verification and limits

An artificial constant-\(c_p\) ideal-gas exchanger admits well-defined sensible heat capacity rates and an independently derived exponential effectiveness limit. The dedicated tests verify the nonlinear boundary solver against that controlled fixture, then use real CoolProp for feasible cases.

The same installed conductance is a model hypothesis. Real exchanger UA often changes with flow, Reynolds/Prandtl regime, temperature, fouling and wall conductivity. No measured primary-heater UA distribution across operating points was supplied.

## 10. G3.2 — coupled installed heater and cooler with finite sink

### 10.1 Two temperatures solved simultaneously

G3.2 extends the fixed-UA boundary conditions to a cooler with finite coolant mass-flow and sensible heat capacity. The model solves for compressor inlet \(T_1\) and turbine inlet \(T_4\) such that **both** the installed heater and cooler UA equalities are fulfilled, subject to cycle feasibility and the finite source/sink states.

This prevents silently fixing compressor inlet temperature in a case where the cooler cannot maintain it as sink temperature rises. The warmer compressor inlet then influences compression work and cycle efficiency.

### 10.2 Illustrative installed equipment

A documented real-CoolProp/synthetic-hardware case used source **800 K**, 100 kg/s, dry-gas sensible cp approximately 1100 J/(kg·K) at 300 K with a small linear slope; coolant 75 kg/s, cp 4180 J/(kg·K), nominal inlet 285 K; CO₂ 20 kg/s, low pressure 8.5 MPa, high 24 MPa; recuperator UA 200 kW/K; heater installed UA about **21.625962 kW/K** and cooler installed UA **100.514392 kW/K**. The coarse five-section model is illustrative.

### 10.3 Cooler inlet disturbance result

| G3.2 output | Coolant at 285 K | Coolant at 287 K |
|---|---:|---:|
| Solved compressor inlet T1 | 310.004883 K | 310.463867 K |
| Solved turbine inlet T4 | 650.019531 K | 652.216797 K |
| Exhaust gas outlet | 761.434830 K | 761.969130 K |
| Coolant exit | 295.172950 K | 297.025449 K |
| Net shaft power | **1.423728 MW** | **1.406263 MW** |
| Thermal efficiency | 30.863734% | 30.912031% |
| Heater heat transferred | 4.612948 MW | 4.549241 MW |
| Cooler rejected heat | 3.189220 MW | 3.142978 MW |
| Heater required UA | 21.625691 kW/K | 21.627529 kW/K |
| Cooler required UA | 100.448503 kW/K | 100.572653 kW/K |
| Cooler entropy generation | 1154.805 W/K | 1125.584 W/K |

The output illustrates a finite heat sink's effect on the compressor-side boundary. An increase in computed thermal efficiency does not mean higher electrical power: net shaft output **decreases** in this example.

### 10.4 Residual and off-design distinctions

The archived heater equality residual was approximately **0.0013–0.0072%**, cooler equality residual **0.058–0.066%**, under the declared stopping tolerances. The outer boundary search and inner thermal calculations have distinct iteration counts.

A supplementary flow-scaling model varies quadratic pressure loss and efficiency penalties under prescribed parameters. It is **only a scenario extension**, not an identified compressor/turbine flow map or experimental part-load characteristic.

G3.2 is a coupled **steady** problem. Its finite coolant *stream* is not itself a transient coolant **inventory**. Likewise, WP2b later added a dynamic wall but did not silently transplant the G3.2 finite-coolant stream into a full transient cooling model.

## 11. G3.3 — sourced property alternatives, hydraulic models and mesh sensitivity

### 11.1 Property upgrades

The G3.3 research stage investigated temperature-dependent dry-air/gas sensible properties and actual liquid-water property calls for the cooling stream, rather than relying on constant cp for every stream. NIST Shomate dry-air inputs, CoolProp water and circular-pipe Darcy/Fanning conventions were documented. They are **source-grounded engineering formulas**, not calibrated representations of a specific industrial exhaust composition or heat exchanger.

### 11.2 Hydraulics and applicability

Pipe friction depends on Reynolds number, roughness and flow regime. A circular-pipe relationship is not automatically a valid pressure-loss model for printed circuit heat exchangers, manifold networks, compact fin passages or CO₂ compressors. Geometry-specific identification is still required. Friction factor conventions must be consistent: a Darcy factor differs by four from the corresponding Fanning factor.

### 11.3 Independent mesh/segment check

Two real-fluid operating points were solved at **6, 12, 24 and 48 exchanger sections**. One case had CO₂ low state 8.5 MPa / 310 K and turbine inlet 650 K; the second 9 MPa / 314 K and turbine inlet 690 K. The high pressure was 24 MPa, CO₂ flow 20 kg/s, and recuperator installed UA 200 kW/K.

Representative numerical trend at the first case:

| Output | 6 sections | 12 | 24 | 48 |
|---|---:|---:|---:|---:|
| Cycle thermal efficiency | 30.850478% | 30.822519% | 30.813657% | **30.811261%** |
| Recuperator duty | 4.503075 MW | 4.498888 MW | 4.497560 MW | 4.497200 MW |
| Recuperator minimum approach | 3.728545 K | 3.864567 K | 3.907765 K | 3.919449 K |
| Heater required UA | 21.766931 kW/K | 21.777700 | 21.781380 | 21.782395 |
| Cooler required UA | 100.798020 kW/K | 101.347517 | 101.490975 | 101.527335 |

For the 24→48 refinement, the first-case cooler UA changed about **0.0358%** while efficiency shifted **0.002396 percentage points**; the second case had corresponding changes about **0.0300%** and **0.002072 percentage points**.

### 11.4 Interpretation

This checks segment sensitivity at **two points**; it is not a proof of uniform convergence everywhere. Near heat-exchanger pinch, pseudo-critical \(c_p\) features, mixed phases or branch changes, numerical resolution and EOS interpolation may demand much finer treatment. A future engineering claim should test event/phase boundaries, root-conditioned states and a spatial or finite-volume refinement strategy.

The numerical evidence is preserved in \`docs/G33_NUMERICAL_VERIFICATION.md\`, \`docs/G33_REFERENCE_PROPERTIES_AND_CONVERGENCE.md\`, and associated CI examples.

---

# Part III — External evidence and heat-transfer transferability

## 12. G3.4 — external-source inventory, eligibility and anomalies

### 12.1 Evidence intake as its own research method

An independent validation project fails if it labels published design-state calculations as observations, uses authors' fitted/calibration data as sealed holdouts, or transfers a measured coefficient from an unrelated geometry without qualification.

The G3.4 intake introduced an evidence taxonomy: **direct measurements**, **experimentally reduced quantities**, **model-corrected values**, **source authors' numerical predictions**, and **proposed comparisons that have not been admitted**.

| Record | Original origin | What it can support | What it cannot support directly |
|---|---|---|---|
| STUTTGART-2022 | Theologou et al. 2022, Mendeley Data DOI 10.17632/4mvk4nxrkz.1, CC BY 4.0 | Horizontal circular-tube measured-derived local thermal behaviour and orientation effects | CARBOSOLA PCHE or complete cycle validation |
| ZHANG-2022 | Zhang et al. 2022 sodium/CO₂ PCHE paper DOI 10.3389/fenrg.2022.835224 | Geometry-specific coarse exchanger context | Direct conversion to gas–CO₂ recuperator or water precooler |
| KAIST-2024 | Lee et al. turbine-sweep/sCO₂ Symposium material | Qualified measured rpm/flow/pressure behaviour; separated model-corrected inlet estimates | Unqualified measured turbine efficiency map at every row |
| SANDIA-2010 | Wright et al. SAND2010-0171 | Design states plus separate measured compressor figures | Treating prediction table as experimental compressor measurements |
| HZDR-PCHE-2025 | RODARE modelling/cost outputs DOI 10.14278/rodare.3928 | Comparative modelling and techno-economic context | Direct calorimetric validation of an installed CARBOSOLA exchanger |
| HZDR-TPMS-2026 | ANSYS CAD/Fluent geometry/CFD archive | Geometry/CFD methods context | Measured plant pressure/temperature/HTC points |
| KTH industrial demonstrator context | Public concept/infrastructure descriptions | Possible future data contacts and research needs | Unpublished lab data or current operational authorization |

The source file \`docs/G34_EXTERNAL_VALIDATION_INTAKE.md\` distinguishes these sources and tracks which have enough detail for an admissible numerical comparison.

### 12.2 STU-001 source anomaly

One Stuttgart observation contained an anomalous source heat-flux value around **833 kW/m²** in a context inconsistent with the rest of its source family. The project recorded the original row and exclusion rationale as **STU-001**, quarantining the affected run/stations rather than “correcting” a number without an authoritative source answer.

This is an important measurement-data practice. An unexplained outlier may represent transcription, sensor, unit, geometry, control or operating-point information that cannot be resolved by a third-party analyst. Preserve the original and report the effect of any exclusion.

### 12.3 ZH-001, KAIST-001 and SANDIA-001

The Zhang PCHE source reported a rated heat-transfer coefficient that could not be obtained straightforwardly from the published terminal temperature/heat/area table under one apparent common LMTD convention. The project documented the quantitative discrepancy, including a derived value roughly **1,368.451 W/(m²·K)** versus an apparently stated **1,264 W/(m²·K)** (8.264% difference), as an unresolved source-equation issue rather than an excuse to assign a tuned UA.

The KAIST reference contained operating data that mixed direct measurements with a model-corrected turbine inlet. The Sandia source distinguished design calculations from real compressor performance figures. In both cases the correct action was to preserve original measurement type and require source review before using any row as an experimental machine-map calibration point.

### 12.4 Intake acceptance gate

A new external dataset should have: original DOI and authors; source licence and permitted redistribution scope; equipment topology, material/geometry, pressure and temperature definitions; instrument or reduction uncertainty; original units and coordinate map; eligibility/exclusion log; fit-versus-holdout restrictions; and numerical diagnostics showing if a formula is operating outside the source's original validation domain.

An accessible PDF alone is not a machine-readable experimental benchmark, and a property or correlation source can be scientifically useful without becoming a universal “validation” dataset.

## 13. G3.5 H1a — horizontal sCO₂ benchmark and forced-convection baseline

### 13.1 The source's scientific importance

Supercritical CO₂ in a heated horizontal tube can develop large radial and circumferential gradients, notably through density/viscosity changes and buoyancy. A simple bulk Reynolds–Prandtl forced-convection correlation cannot capture all top/bottom stratification effects.

The Stuttgart/Theologou dataset contains original experiments with measured-derived wall and bulk thermal information, local heat-flux/HTC reductions, and different circumferential orientations. It makes orientation-specific model errors visible rather than hiding them in a single average.

### 13.2 Exact source ledger and sample eligibility

The recorded source inventory was:

| Source stage | Count | Meaning |
|---|---:|---|
| Original experiment identifiers | **54** | Source runs, before anomaly processing |
| Original axial position records | **2,508** | Full axial ledger, not all local HTC cells |
| Source local experimentally reduced HTC cells | **2,398** | Original local cells |
| Quarantined STU-001 experiment | 1 | Exclusion tracked, not deleted from provenance |
| Quarantined local HTC stations | **50** | Affected entries |
| Retained local observations before other gates | **2,348** | Unquarantined data |
| Additional x/D/applicability exclusions | **30** | Model-specific admissibility |
| Final H1a successfully evaluated comparisons | **2,318** | Common Gnielinski/Dittus reference |
| Distinct contributing runs | 53 | Source run count after quarantine |
| Nominal source families | 18 | Used for group-based comparisons |
| Original heldout families | 4 | Predeclared families |
| Heldout valid stations per H1a formula | **534** | Not randomly shuffled sample rows |

A robust benchmark distinguishes *original measurement denominator*, *eligible set*, *success set* and *held-out count*. The 2,318 comparisons should never be described as 2,318 completely independent experiments.

### 13.3 Reconstruction and performance statistic

Using source input pressure/flow and an accepted enthalpy alignment, the code reconstructs CO₂ bulk thermodynamic states with CoolProp and predicts local forced-convection heat-transfer coefficients. The reference “measured HTC” is actually a **source experimentally reduced HTC**, not a raw sensor voltage. Source HTC and wall temperature may share the same reduction equations.

Pointwise mean absolute percentage error:

\[
\mathrm{MAPE} = \frac{100}{N}\sum_{i=1}^{N}
\left|\frac{h_{model,i}-h_{source,i}}{h_{source,i}}\right|.
\]

A signed relative bias and distributional metrics are also needed; one global MAPE can obscure systematic overprediction.

### 13.4 H1a full baseline errors

| H1a local thermal model | Gnielinski | Dittus–Boelter |
|---|---:|---:|
| Successfully evaluated local stations | 2,318 | 2,318 |
| **Overall MAPE** | **150.15%** | **119.60%** |
| Mean signed relative bias | +137.05% | +100.55% |
| Median APE | 55.07% | 47.17% |
| 90th percentile APE | 385.05% | 298.15% |
| RMS percentage error | 266.27% | 210.29% |
| Experiment-macro mean MAPE | 156.89% | 124.70% |
| Heldout-family station MAPE | 158.10% | 121.82% |

The large bias is physically and statistically important. An off-domain forced-convection formula can be systematically optimistic rather than randomly noisy.

### 13.5 Orientation and diameter explain substantial heterogeneity

| Source subset | Stations | Gnielinski MAPE | Dittus–Boelter MAPE |
|---|---:|---:|---:|
| HB — bottom, 180° | 790 | 87.71% | 69.65% |
| HM — middle, 90° | 738 | 124.23% | 98.76% |
| HT — top, 0° | 790 | **236.81%** | **189.01%** |
| 4 mm source tube | 1,150 | 96.13% | 78.65% |
| 8 mm source tube | 1,168 | **203.34%** | **159.91%** |

The top-wall degradation is a signal of inadequate representation of circumferential thermal physics, not an inconvenience to be averaged away.

### 13.6 What H1a actually established

H1a established a reproducible pipeline for *source-attributed measured-derived* local correlation comparisons, with an original-data ledger, exclusion audit, meaningful group-based holdouts, and negative model-transfer evidence. It **did not validate** these correlations as reliable plant PCHE prediction laws or recover the original entire experimental rig and its uncertainty budget.

Detailed outputs: \`docs/G35_STUTTGART_HTC.md\` and \`docs/G35_STUTTGART_RESULTS.md\`.

## 14. H1b — wall-conditioned Bishop and Jackson–Hall tests

### 14.1 Physical hypothesis

H1b investigated whether wall-dependent property ratios or buoyancy-aware correction structures would improve prediction compared with uncorrected forced-convection baselines. It also distinguished two operationally different questions:

1. **Measured-wall-conditioned diagnostic:** using the source’s measured wall temperature as a correlation input and comparing the implied HTC against the source-reduced HTC.
2. **Flux-driven wall prediction:** given source heating rate \(q''\), bulk fluid state and model geometry, solve \(q''=h(T_w)(T_w-T_b)\) for \(T_w\) and compare the resulting HTC—**without inputting measured wall temperature**.

Conditioned models can achieve lower apparent MAPE partly because HTC and wall-temperature measurements share a reduction relationship; that is not the same as prospective heat-transfer prediction.

### 14.2 Results on eligible source samples

| H1b comparison | Measured wall T supplied? | Stations | Overall MAPE | Heldout MAPE | Bottom MAPE | Top MAPE |
|---|---|---:|---:|---:|---:|---:|
| Baseline Gnielinski | No | 2,318 | 150.15% | 158.10% | 87.71% | 236.81% |
| Baseline Dittus–Boelter | No | 2,318 | 119.60% | 121.82% | 69.65% | 189.01% |
| Bishop conditioned | **Yes** | 2,152 | **21.94%** | 20.72% | 14.23% | 33.94% |
| Jackson–Hall conditioned | **Yes** | 2,318 | **28.46%** | 24.16% | 17.84% | 44.48% |
| Bishop flux-driven | **No** | 2,152 | **46.40%** | 39.72% | 24.79% | 80.65% |
| Jackson–Hall flux-driven | **No** | 2,318 | **49.47%** | 43.16% | 26.41% | 84.63% |

These row populations differ. A direct claim that 46.40 is universally better than 49.47 requires comparing on the **same eligible station keys**, not just juxtaposing unmatched overall statistics.

### 14.3 Matched-support inference

On the common 2,152 Bishop-eligible stations, the Jackson flux-driven MAPE was about **52.14%**, versus Bishop **46.40%**. Across 18 nominal families, Bishop had the lower error in 12 and Jackson in 6. Family-resampled difference uncertainty was broad, with a preliminary percentile range crossing zero. This is **not a formal measurement-error confidence interval** and is insufficient to assert universal Bishop superiority.

### 14.4 Orientation-blindness remains

Even the improved flux-driven models had **~81–85%** top-wall MAPE. A model lacking genuine angular physics can respond to wall property changes without resolving circumferential flow, buoyancy, stratification or different top/bottom heat-transfer processes.

The key H1b achievement is a careful diagnostic/predictive boundary, not a declaration that the problem was solved.

See \`docs/G35B_WALL_PROPERTY_CORRELATIONS.md\` and \`docs/G35B_RESULTS.md\`.

## 15. H1c — Lei top/bottom transfer is a recorded negative result

### 15.1 Hypothesis and mismatch

A published top/bottom heat-transfer relation from a different working-fluid/flow context was applied to the Stuttgart horizontal sCO₂ source. The test was intended to assess *transferability*, not to presume cross-fluid universality.

Because correlation development ranges depend on fluid properties, geometry, heat flux and buoyancy regime, out-of-domain use can fail dramatically even if numerical equation evaluation succeeds.

### 15.2 Matching the same HB/HT support

The original two wall orientations yielded **1,580** eligible HB+HT stations. The final refined H1c evaluation used the same station population for Lei and compared a Jackson–Hall baseline on matching keys:

| Flux/HTC comparison | Stations | Overall MAPE | Bottom HB | Top HT | Heldout MAPE |
|---|---:|---:|---:|---:|---:|
| Lei, measured-wall conditioned | 1,580 | **175.18%** | 76.26% | 274.09% | 177.26% |
| **Lei, flux-driven wall inversion** | **1,580** | **631.72%** | **197.73%** | **1065.72%** | **638.83%** |
| Jackson–Hall, flux-driven | 1,580 | 55.52% | 26.41% | 84.63% | 49.35% |
| Gnielinski, bulk | 1,580 | 162.26% | 87.71% | 236.81% | 170.29% |

Bishop flux-driven could be evaluated on only **1,468** corresponding HB/HT stations due to its own additional eligibility gate. Its 52.72% MAPE on that *smaller* subset is not an interchangeable matched-support comparator for the 1,580 rows.

### 15.3 Distinguish solver convergence from model fidelity

An early wall-root solve had discretisation/stopping precision issues, which were fixed. The final revised solver evaluated all 1,580 points without numerical rejection, with largest relative \(q''\) balance residual near **1.2722×10⁻⁵** and median about **4.4174×10⁻⁷**.

Therefore the final 631.72% MAPE is **not primarily a root residual artefact**. It reflects a severe model-form and fit-domain mismatch for this transfer.

### 15.4 Research lesson

Negative source-to-model evidence is a valuable output. The physically appropriate response is to characterize buoyancy, fluid/geometry domains and identify truly in-domain tests—not to hide an apparently nonphysical source or tune coefficients until an unrelated data population yields a pleasing headline.

See \`docs/G35C_LEI_TOP_BOTTOM.md\` and \`docs/G35C_LEI_RESULTS.md\`.

## 16. H1d — Kim 2019 original-source recovery and research branch

### 16.1 Why exact source transcription mattered

Kim et al. (2019) investigated top/bottom local supercritical CO₂ heat-transfer correlations. The team retrieved the original article to inspect the actual equations, coefficient tables and experimental ranges rather than extrapolating from an abstract.

The source audit identified the empirical form built on a Dittus–Boelter-like \(Re_b^{0.8}Pr_b^{0.4}\) component with property and buoyancy corrections, plus separately fitted semi-empirical alternatives. Mixing coefficient sets between equations would generate a formula never published by the authors.

### 16.2 Original equation discrepancy

An unresolved **Eq. (24) versus Table 4** exponent/sign-placement ambiguity affects the empirical model's numerical output. One evaluation follows the published printed form literally; another tests a **hypothesised** alternate interpretation. The hypothesis is *not* an author-confirmed correction, regardless of whether its numerical error is lower.

[Issue #20](https://github.com/Open-Energy-Methods/sco2-braytonbench/issues/20) preserves this unresolved source question. [Draft PR #19](https://github.com/Open-Energy-Methods/sco2-braytonbench/pull/19) is a research branch and **is not part of the integrated main release**. Neither variant should be silently promoted as the authoritative Kim empirical law.

### 16.3 Source-domain mismatch

The original Kim heating flux range ended around **26.9 kW/m²** in the documented source model study. The retained Stuttgart H1d comparison candidates were **all above** that original maximum. The entire H1d transfer is thus an *extrapolative stress test*, not direct replication of published experimental fidelity.

### 16.4 Exact common-station audit from historical H1d branch

An initial comparison mixed separately successful root populations: candidate evaluations were on 1,580 HB/HT stations, but some formulas failed to converge or violated admissibility. The hardening step intersected the exact successful station IDs before comparing model accuracy.

At the H1d branch [run #42058735222](https://github.com/Open-Energy-Methods/sco2-braytonbench/actions/runs/42058735222), all **15 CI jobs succeeded**. Exactly **1,275 of 1,580** candidates entered the *three-way common successful-root* intersection, including **272** original held-out-family stations.

| H1d model on exactly the same 1,275 source stations | Pointwise MAPE | Equal-family macro MAPE | Heldout MAPE on same 272 stations |
|---|---:|---:|---:|
| Jackson–Hall flux-driven reference | **33.89%** | **35.31%** | **21.70%** |
| Kim semi-empirical, published form | 54.39% | 55.23% | 52.67% |
| Kim empirical, **printed literal** interpretation | **29,622,281.81%** | 33,696,878.32% | 22,756,407.13% |
| Kim empirical, **unverified sign-placement hypothesis** | 45.73% | 45.75% | 37.54% |

The extremely large literal-interpretation error must not be silently clipped or transformed into a usable correlation. The common-support results also show that a comparison on each method’s own successful population could reverse model ranking; convergence/coverage are themselves outcomes.

### 16.5 Scientific status and gate

- Original source equations and the coefficient transcription have been inspected and preserved.
- Exact matched station comparison is executed **on the research branch**.
- All compared Stuttgart heat fluxes lie outside the stated original Kim experimental flux range.
- Empirical formula interpretation remains unresolved; independent source-author/publisher clarification is needed.
- Root failures, original-sample exclusion and held-out coverage remain part of the record.
- **No H1d model is designated a newly validated default in the current \`main\` package.**

See \`docs/KIM2019_ORIGINAL_SOURCE_RECOVERY.md\`, historical PR #21, and research PR #19.

## 17. Experimental density and source/data rights: two separate questions

### 17.1 Scientific validity is not a licence

Independent experimental property comparisons can support numerical EOS verification, but the right to *access* a journal-curated dataset and the right to *rehost a complete adapted table* are legally distinct. An attribution line does not automatically confer a redistribution licence.

The original Mantilla record is linked through NIST/TRC ThermoML and the journal DOI **10.1021/je1001158**. NIST states that ThermoML archive files are hosted with participating journal publishers' permission. The project has not established an unambiguous downstream grant for redistributing a normalized full 49-point dataset under BSD software packaging.

### 17.2 Current HEAD mitigation

[PR #29](https://github.com/Open-Energy-Methods/sco2-braytonbench/pull/29) removed the full 49-point normalized CSV from current \`main\`. The WP5 gate checks that it cannot reappear in the candidate source snapshot or source distribution. The optional density test and historical-density report require an **external user-supplied file**; neither silently substitutes a fake measurement.

Provenance and opt-in documentation remain, including \`data/reference/mantilla2010_provenance.yaml\` and \`data/reference/README_MANTILLA_OPT_IN.md\`.

### 17.3 Rights still outstanding

Older public Git objects and any earlier downloaded source archives may still contain the table. Removing a file from HEAD **does not erase Git history** or retrospectively grant permission. A draft message seeking NIST/authorized-rights guidance has been prepared but not sent; no licence reply is recorded. The possible need to obtain specific publisher permission or repair historical copies is tracked in [issue #27](https://github.com/Open-Energy-Methods/sco2-braytonbench/issues/27).

### 17.4 What can be honestly reported

A paper or application can cite the historic 49-point numerical error **as historical, source-attributed software evidence from an earlier recorded CI run**. It should not say the current default CI freshly validates all 49 measured points, and it should not distribute a complete source table that remains uncleared.

The broader lesson applies to every research dataset: scientific credit, numerical reproducibility and publisher/file-reuse rights are three distinct acceptance dimensions.

---

