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
| Publisher / maintainer | Open Energy Methods; `CITATION.cff` names Abhijith Sivaprasadan |
| Package name and current version | `sco2-braytonbench`, **0.5.0a0** (alpha; not v1.0) |
| Snapshot commit | `8df1711a425e21da342bd3f401da61a1375bbc0a` on `main` |
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
- Latest integrated HEAD `8df1711a…` with [20 successful CI jobs](https://github.com/Open-Energy-Methods/sco2-braytonbench/actions/runs/42266275348).

### 1.3 What has not been demonstrated

No experimental CARBOSOLA power-cycle validation, turbine/compressor machine map identification, inventory-based full CO₂ transient, hydraulic bypass valve `C_v` relation, plant-approved control, verified installed sensor list, calibrated wall thermal capacity, measured PCHE geometry-specific UA transfer, rigorous techno-economic optimum or independent human reviewer approval exists in the integrated baseline.

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

All six were merged sequentially into `main` while preserving `0.5.0a0\). A “merged” software PR means GitHub integration, **not independent peer review, licence approval or scientific field validation**.

### 3.3 Traceable integrated commits

The WP0–WP5 integrated development commit was `88579f7ff8a723124744dde0ac53a38e8adf1837`, verified by [20/20 CI jobs in run #42258225916](https://github.com/Open-Energy-Methods/sco2-braytonbench/actions/runs/42258225916).

The subsequent data-rights cleanup produced the current main SHA `8df1711a425e21da342bd3f401da61a1375bbc0a`. [Run #42266275348](https://github.com/Open-Energy-Methods/sco2-braytonbench/actions/runs/42266275348) succeeded in all **20** jobs. Thus the report's present state is **after** the cleanup, not the earlier CI checkpoint that had one job pending.

### 3.4 GitHub discipline

New claims should be introduced on a dedicated branch with code, independent tests, scientific context, machine-readable evidence where appropriate, and a PR specifying accepted and excluded functionality. The project should not automatically convert an exploratory numerical correlation or an unverified rights claim into the default stable API.

Every published number belongs to a run/commit and a supporting source. Source datasets should retain their provenance, historical anomalies and explicit attribution, rather than being silently corrected to improve a benchmark.

## 4. Repository architecture and roles

### 4.1 Top-level structure

| Location | Function |
|---|---|
| `src/sco2_braytonbench/` | Core property interfaces, cycle, recuperator/HXs, finite source, cooler, installed-UA solvers, thermal dynamics, bypass/PI, experiment-readiness utilities |
| `tests/` | Unit, domain, regression, analytic, numerical, source and optional real-CoolProp verification |
| `examples/` | Reproducible ideal-gas and real-fluid scientific examples; synthetic transient/control and prospective readiness scenarios |
| `scripts/` | Research benchmark scripts, original-source comparisons, reporting tools, WP5 offline release gate |
| `data/reference/` | Reference-source metadata and permitted model inputs; Mantilla 49-point CSV no longer in current HEAD |
| `data/validation/` | Attribution-labelled validation-source transformations, e.g. Stuttgart reduced measurements |
| `data_requests/` | Publication/data recovery requests, known source gaps and prospective intake templates |
| `protocols/wp4/` | Candidate sensor/channel registry, test matrix, blank standard-uncertainty ledger and synthetic DAQ-format fixture |
| `docs/` | Engineering derivations, source-recovery audits, numerical tables, physical limitations, release/rights decisions |
| `evidence/generated/` | Reproducible scenario artifacts when executed; CI uploaded artifacts are evidence tied to a run |
| `.github/workflows/ci.yml` | Independent Python-version, CoolProp, research and distribution gates |
| `MANIFEST.in` | Source archive include/exclude policy with explicit protection for disputed data |
| `CITATION.cff`, `pyproject.toml`, `LICENSE` | Authorship, software identity, supported versions, licensing and packaging contract |

### 4.2 Separation of independent roles

The **Properties** interface supplies thermodynamic state transformations; its correctness cannot be inferred from conservation tests alone. The **cycle** module performs nominal state and work/heat balances. Finite gas/coolant, recuperator and UA modules impose different boundary-value problems. **thermal_dynamics** is an analytically soluble wall kernel and is not an EOS. **dynamic_whr** couples a physically stored wall state to an algebraic cycle. **control_whr** alters source gas routing and uses only measured-like wall feedback *in a synthetic simulation*. **experimental_readiness** validates data structures and intended campaigns but does not access plant instrumentation.

This separation allows testing the equations at deliberately simple ideal-gas limits before exposing the model to real-fluid property nonlinearity. Equally, a real-fluid CoolProp smoke test is a useful compatibility check but cannot substitute for mechanical geometry and measurements.

### 4.3 Software dependencies and portability

The alpha package declares Python `>=3.10`, no unconditional runtime dependencies, and optional CoolProp `>=6.6,<9`. The cross-version CI test suite runs Python 3.10/3.11/3.12; the dedicated real-CO₂ checks pin a known CoolProp version for reproducible comparisons. The source package is under BSD-3-Clause; the Stuttgart data and any other third-party evidence require their separate source licenses and attribution.

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

**Current evidence caveat:** the 49-row normalized original-source transcription has since been **removed from current HEAD** because the downstream NIST ThermoML/journal-publisher redistribution grant is unconfirmed. Default CI therefore **does not rerun those measured-density observations**. The test and report now require a user-obtained external CSV through `SCO2_MANTILLA_DENSITY_CSV`; in its absence the measurement check is explicitly skipped. Historical values are historical run evidence, not a fresh current-version independent experimental validation claim.

See `docs/EXPERIMENTAL_DENSITY_DECISION.md`, `data/reference/README_MANTILLA_OPT_IN.md` and [rights issue #27](https://github.com/Open-Energy-Methods/sco2-braytonbench/issues/27).

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

The appropriate citation is `docs/FR2016_COMPARISON_REVIEW.md` together with `docs/FR2016_ORIGINAL_MODEL_RECOVERY.md`. Future parity requires published operating-point and state definitions, not merely another digit of efficiency agreement.

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

See `docs/G3_WASTE_HEAT_DESIGN_SCREENING.md` and `docs/G3_STEADY_SCREENING_RESULTS.md`.

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

The numerical evidence is preserved in `docs/G33_NUMERICAL_VERIFICATION.md`, `docs/G33_REFERENCE_PROPERTIES_AND_CONVERGENCE.md`, and associated CI examples.

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

The source file `docs/G34_EXTERNAL_VALIDATION_INTAKE.md` distinguishes these sources and tracks which have enough detail for an admissible numerical comparison.

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

Detailed outputs: `docs/G35_STUTTGART_HTC.md` and `docs/G35_STUTTGART_RESULTS.md`.

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

See `docs/G35B_WALL_PROPERTY_CORRELATIONS.md` and `docs/G35B_RESULTS.md`.

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

See `docs/G35C_LEI_TOP_BOTTOM.md` and `docs/G35C_LEI_RESULTS.md`.

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
- **No H1d model is designated a newly validated default in the current `main` package.**

See `docs/KIM2019_ORIGINAL_SOURCE_RECOVERY.md`, historical PR #21, and research PR #19.

## 17. Experimental density and source/data rights: two separate questions

### 17.1 Scientific validity is not a licence

Independent experimental property comparisons can support numerical EOS verification, but the right to *access* a journal-curated dataset and the right to *rehost a complete adapted table* are legally distinct. An attribution line does not automatically confer a redistribution licence.

The original Mantilla record is linked through NIST/TRC ThermoML and the journal DOI **10.1021/je1001158**. NIST states that ThermoML archive files are hosted with participating journal publishers' permission. The project has not established an unambiguous downstream grant for redistributing a normalized full 49-point dataset under BSD software packaging.

### 17.2 Current HEAD mitigation

[PR #29](https://github.com/Open-Energy-Methods/sco2-braytonbench/pull/29) removed the full 49-point normalized CSV from current `main`. The WP5 gate checks that it cannot reappear in the candidate source snapshot or source distribution. The optional density test and historical-density report require an **external user-supplied file**; neither silently substitutes a fake measurement.

Provenance and opt-in documentation remain, including `data/reference/mantilla2010_provenance.yaml` and `data/reference/README_MANTILLA_OPT_IN.md`.

### 17.3 Rights still outstanding

Older public Git objects and any earlier downloaded source archives may still contain the table. Removing a file from HEAD **does not erase Git history** or retrospectively grant permission. A draft message seeking NIST/authorized-rights guidance has been prepared but not sent; no licence reply is recorded. The possible need to obtain specific publisher permission or repair historical copies is tracked in [issue #27](https://github.com/Open-Energy-Methods/sco2-braytonbench/issues/27).

### 17.4 What can be honestly reported

A paper or application can cite the historic 49-point numerical error **as historical, source-attributed software evidence from an earlier recorded CI run**. It should not say the current default CI freshly validates all 49 measured points, and it should not distribute a complete source table that remains uncleared.

The broader lesson applies to every research dataset: scientific credit, numerical reproducibility and publisher/file-reuse rights are three distinct acceptance dimensions.

---

# Part IV — Time-dependent thermal physics and source-side control

## 18. WP0/WP1 — stable evidence boundary and numerical-domain contracts

### 18.1 Why an explicit release contract came first

A numerical prototype can accumulate attractive features without a defensible answer to “What is this software qualified to predict?” WP0 forced that distinction into a version-controlled [v1.0 release contract](../../V1_0_RELEASE_CONTRACT.md). It defined a **research-software reproducibility** goal and refused to treat an experimentally uncalibrated model as an industrial sCO₂ digital twin.

The release scope is layered:

1. A stable numerical cycle and heat-transfer research foundation.
2. Explicit finite-source and cooler boundary assumptions.
3. Synthetic thermal storage/control models with domain and numerical checks.
4. Source-labelled, independently reviewable experimental-readiness protocols.
5. Released source, tests and evidence that are legally redistributable.
6. Strong claims beyond these boundaries stay experimental or external.

**WP0 is a governance requirement**, not a physical differential equation. Its success is a consistent scientific claim that a maintainer can defend.

### 18.2 WP1 numerical hardening

WP1 added strict guards around finite/nonfinite inputs and physically meaningful numerical domains. Examples include positive cycle mass flow, admissible temperatures and pressures, nonnegative/existing UA inputs, integer segment counts, feasible local exchanger approaches, valid LMTD computations and expected property transformations.

This matters because a near-critical real-fluid solver can return an apparently finite result on the wrong branch if exception cases are too easily converted to successful outputs. A credible engineering tool should distinguish **infeasible physics**, **insufficient data**, **numerical nonconvergence** and **software implementation error**.

### 18.3 Controlled numerical test hierarchy

The research suite uses:

- Independent ideal-gas limiting solutions.
- Exact first-law algebraic relations that can be derived without the implementation.
- Positive, negative and reversed heat-flow signs.
- Small-step and multiple-step consistency.
- Explicit failure tests for NaN, infinite, negative, zero or noninteger input domains where forbidden.
- Real-CoolProp separate test jobs for the actual CO₂ property path.
- Freshly installed package smoke tests, not just editable local imports.

A passing test is considered strong **software evidence for the stated formulation**. It is not direct validation of equipment metal temperatures, turbine maps, source composition or plant-control safety.

## 19. WP2a — exact single-lumped-wall thermal storage kernel

### 19.1 Physical control volume

The first genuine dynamic state introduced on the v1 development line is an **isothermal lumped solid wall** with thermal capacitance \(C_w\) and separate hot- and cold-side thermal conductances:

\[
C_w\frac{dT_w}{dt}
=K_h(T_h-T_w)-K_c(T_w-T_c).
\]

Dimensions: \(C_w\) in J/K; \(K_h,K_c\) in W/K; \(T\) in kelvin; signed \(Q\) in W. The wall can store energy even when incoming/outgoing heat rates differ at an instant.

**Physical assumptions:** uniform wall temperature, constant capacitance, prescribed reservoir temperatures during a step, fixed conductances, no distributed axial conduction, casing losses, material phase change or fluid pressure inventory.

### 19.2 Exact constant-input solution

Let \(K_\Sigma=K_h+K_c\). For positive total conductance:

\[
T_{eq}=\frac{K_hT_h+K_cT_c}{K_\Sigma},\qquad
\tau=\frac{C_w}{K_\Sigma}.
\]

At constant hot/cold inputs over a step \(\Delta t\):

\[
T_{w,1}=T_{eq}+(T_{w,0}-T_{eq})e^{-\Delta t/\tau}.
\]

The integration should use a numerically stable representation near \(\Delta t/\tau\to0\), rather than subtracting two almost equal floating-point exponentials. The implementation uses an `expm1`-based small-step form to preserve energy accuracy.

### 19.3 Integrated heat versus wall energy

The wall’s mean temperature over the interval is:

\[
\overline{T_w}
=T_{eq}+(T_{w,0}-T_{eq})\,
  \frac{1-e^{-\Delta t/\tau}}{\Delta t/\tau}.
\]

Then

\[
E_h=K_h(T_h-\overline{T_w})\Delta t,\qquad
E_c=K_c(\overline{T_w}-T_c)\Delta t
\]

and

\[
E_h-E_c=C_w(T_{w,1}-T_{w,0}).
\]

This identity includes the sign convention: if heat flows backwards under a cold wall or reversed temperature order, the energy must not be artificially clipped to zero.

### 19.4 Why time stepping matters

An isolated exact wall kernel tests whether thermal capacitance is treated as storage rather than as a tuning constant in unrelated steady-state solves. It is analytically verifiable because the ODE is linear for constant reservoirs/conductances. The exact answer also provides a standard for assessing a more complicated coupled integrator.

### 19.5 What WP2a does not contain

WP2a by itself does not know the CO₂ turbine inlet state, gas stack temperature, or Brayton net power. It therefore must not be described as a “dynamic sCO₂ power plant simulation.” That system coupling is the distinct WP2b task.

Source: `src/sco2_braytonbench/thermal_dynamics.py`, `tests/test_thermal_dynamics.py`, `examples/thermal_wall_step_response.py`, `docs/G4_THERMAL_CONTROL_VOLUME_SCOPE.md`.

## 20. WP2b — finite gas source, thermal-wall inventory and quasi-steady Brayton cycle

### 20.1 The new physical energy path

WP2b introduced two separate heat-transfer interfaces rather than reusing a direct gas→CO₂ heat input:

~~~text
Waste gas, finite m_g and cp_g
        │
        │ UA_g,wall (gas cools to a computed T_out)
        ▼
Single thermally stored solid-wall state T_w, C_w
        │
        │ UA_wall,CO2 (isothermal wall to CO₂ path)
        ▼
CO₂ heater, existing state 3 → 4 enthalpy gain
        │
        ▼
Algebraic six-state recuperated Brayton power block
        │
        ├── W_t - W_c = net modelled shaft power
        └── Q_cooler = rejected heat
~~~

There is **no second direct gas-to-CO₂ heater duty added**. The wall-to-CO₂ transfer is exactly the cycle's state-3→4 heater input at every model evaluation.

### 20.2 Constant-\(c_p\) finite source to wall

For active hot gas flowing over an assumed isothermal wall:

\[
C_g=\dot m_gc_{p,g},\quad
\epsilon_g=1-\exp(-UA_{g,w}/C_g),
\]

\[
Q_{g,w}
=C_g(T_{g,in}-T_w)\epsilon_g,\quad
T_{g,out}=T_{g,in}-Q_{g,w}/C_g.
\]

This is the exact constant-property source-to-constant-wall exponential effectiveness relation, **not** a full finite-two-stream PCHE counterflow correlation. The wall and gas-side transfer coefficients remain assumed.

The gas-source inlet temperature and mass flow may change between declared source intervals, creating a time-dependent load on the wall.

### 20.3 Separate isothermal wall→CO₂ installed-UA equality

The CO₂ heater duty is

\[
Q_{w,CO_2}=\dot m_{CO_2}(h_4-h_3).
\]

Given current wall temperature, the code finds a feasible \(T_4\) whose separately rated isothermal wall–CO₂ exchanger requires the specified installed UA:

\[
UA_{w,CO_2,required}(T_4)
   =UA_{w,CO_2,installed}.
\]

A segmented local fluid path is evaluated from enthalpy and pressure states 3→4. Its required conductance is derived by summing segment heat-rate/LMTD terms using the wall-to-fluid temperature differences.

The solver checks local approach, bracketing, unique feasible root and residual. It does not rely on an arbitrary *after-the-fact* heat factor to make first-law terms match.

### 20.4 Stored energy and coupled numerical step

The sole integrated differential state remains:

\[
C_w\dot T_w=Q_{g,w}(T_w,T_{g,in},\dot m_g)-Q_{w,CO_2}(T_w).
\]

At every RK4 stage, the quasi-steady Brayton equations are solved again for that stage's thermal wall temperature, producing \(T_4\), \(Q_{w,CO_2}\), cooler heat and predicted shaft power. This is a **differential–algebraic thermal-power surrogate** in practical interpretation, not a spatially distributed fluid dynamic/rotor system.

The RK4 integration applies matched quadrature weights to the heat and work contributions. For each interval:

\[
E_{g,w}-E_{w,CO_2}=\Delta U_w,\qquad
E_{w,CO_2}=E_{cooler}+E_{shaft},
\]

\[
\boxed{E_{g,w}=\Delta U_w+E_{cooler}+E_{shaft}}.
\]

A balanced integrated residual checks implementation bookkeeping. **Time-discretisation convergence is a separate requirement**; one can write numerically consistent integrals of an inaccurate model. WP2b therefore also tests a closed-form constant-\(c_p\) limit and time-step refinement.

### 20.5 Independently derived ideal-gas limit

For zero recuperator heat exchange, the compressor outlet/CO₂ heater inlet \(T_3\) is fixed by an ideal-gas compression equation. With synthetic \(P_1=8\) MPa, \(P_2=24.25\) MPa, \(T_1=310\) K, \(R/c_p=0.2\), and compressor efficiency 0.89:

\[
T_3=310+
\frac{310[(24.25/8)^{0.2}-1]}{0.89}
=396.4919\ {\rm K}.
\]

For synthetic source 30 kg/s, \(c_{p,g}=1100\) J/(kg·K), gas-wall UA 40 kW/K; CO₂ 10 kg/s, \(c_p=1000\) J/(kg·K), wall–CO₂ UA 25 kW/K; wall capacitance 2 MJ/K:

\[
H_g=C_g(1-e^{-UA_{g,w}/C_g})=23{,}180.3415\ {\rm W/K},
\]

\[
H_c=C_{CO_2}(1-e^{-UA_{w,CO_2}/C_{CO_2}})
  =9{,}179.1500\ {\rm W/K}.
\]

At gas inlet 850 K, \(T_{w,0}=700\) K:

\[
T_{w,eq}
=\frac{H_g(850)+H_cT_3}{H_g+H_c}
=721.3571\ {\rm K},
\quad
\tau=\frac{2{,}000{,}000}{H_g+H_c}=61.8057\ {\rm s}.
\]

| Analytic property | Reference |
|---|---:|
| Initial \(T_4\) at 700 K wall | **675.0865 K** |
| Wall equilibrium | **721.3571 K** |
| Time constant | **61.8057 s** |
| Wall temperature after 60 s constant source | **713.2673 K** |

These values are **independently derived mathematical fixtures**, not measured CO₂ or CARBOSOLA values.

### 20.6 Numerical disturbance example

A 45-s hypothetical variable-source demonstration compares a constant-source baseline to cooler/hotter and flow-modified gas inputs on an identical time grid.

The original CI example recorded wall end temperatures approximately **711.0451 K** (constant baseline) and **707.7506 K** (disturbed source). The combined source/wall/cycle integrated residual was on the order of \(10^{-7}\) J in these synthetic simulations. That tiny residual demonstrates consistent algebraic quadrature, not microjoule physical measurement accuracy.

### 20.7 Real-fluid compatibility

A separate CoolProp test constructs a feasible hypothetical CO₂ operating point and inverse-rates a wall-to-CO₂ UA against its real-fluid enthalpy path. It then solves at a nearby thermal wall state and checks the one-step first-law ledger.

Passing such a test means the *algorithm* is compatible with nonideal thermophysical calls under selected domain conditions. It does not identify installed UAs, turbine maps or fluid inventories.

### 20.8 Feasibility, integration and model limitations

- Source stack-temperature floor and positive hot-gas/wall approach.
- Local wall-to-CO₂ minimum temperature approach.
- Physically feasible \(T_4\) bounds and bracketed UA inverse.
- Finite/positive \(C_w\), \(c_p\), mass flow and installed thermal conductance.
- Explicit step-size restriction relative to estimated thermal time scale.
- Fail-closed behaviour on out-of-domain or nonunique roots.

The real system may require source cp variation, radiation, heat leaks, axial metal gradients, gas-side flow-dependent UA, multiple wall zones, fluid phase effects and a dynamic coolant inventory. Those are **outside** the WP2b abstract model.

Source: `src/sco2_braytonbench/dynamic_whr.py`, `tests/test_dynamic_whr.py`, `tests/test_dynamic_whr_co2.py`, `docs/G4_WP2B_FINITE_SOURCE_WALL_CYCLE.md`.

## 21. WP3 — conserved waste-gas bypass and sampled wall-temperature PI

### 21.1 Why a real heat/enthalpy path precedes control

A controller that directly adjusts “heater power” without identifying which stream supplies that power can violate energy conservation or make physically unimplementable assumptions. WP3 instead introduced a clear mass-flow routing abstraction: a controlled fraction of the incoming hot gas **bypasses** the gas-to-wall heat-transfer branch and recombines downstream.

The actual command is an idealised **mass fraction**, not a physical angle- or \(C_v\)-calibrated valve. Its distinction from hardware is explicit.

### 21.2 Gas bypass mass and sensible enthalpy ledger

For total source flow \(\dot m_g\) and bypass fraction \(b\):

\[
\dot m_{active}=(1-b)\dot m_g,\qquad
\dot m_{bypass}=b\dot m_g.
\]

The source gas entering the bypass stays at \(T_{g,in}\). The active branch cools through the existing WP2b gas-to-wall UA. After recombination:

\[
T_{mix}=(1-b)T_{active,out}+bT_{g,in},
\]

for equal constant \(c_p\). Therefore:

\[
\dot m_gc_p(T_{g,in}-T_{mix})
=\dot m_{active}c_p(T_{g,in}-T_{active,out})
=Q_{g,w}.
\]

This independent identity guards against accidentally generating two source contributions when a bypass is opened.

A real design must additionally model branch pressure drops, actuator authority, true source compositions, heat losses and variable cp; WP3 does none of those.

### 21.3 Command sign and actuation constraints

For wall setpoint \(T_{set}\) and wall temperature \(T_w\):

\[
e_k=T_{w,k}-T_{set}.
\]

A **positive** error means the wall is too hot, so the controller should **increase bypass** and reduce \(Q_{g,w}\). That sign is physically opposite to a controller that directly increases heater duty.

The PI raw command is

\[
u^{raw}_k=b_{bias}+K_p e_k+I_k,
\]

then is clamped to \(0\le b\le b_{max}<1\). The next held position is also clamped against

\[
|b_k-b_{k-1}|\le r_{max}\Delta t.
\]

A minimum active-gas flow prevents total starvation of the gas-to-wall branch under the stated model.

**Critical interpretation:** this is a **sample-to-sample movement bound** on the mass-fraction command. The simulation applies the next position for the entire source interval; it is **not** a differential model of a real valve continuously travelling at finite speed, nor a measured hydraulic actuator characteristic.

### 21.4 Back-calculation anti-windup

The PI integral state follows:

\[
I_{k+1}=\mathrm{clip}\left[
I_k+K_i e_k\Delta t
+K_{aw}\Delta t(b_{actual,k}-u^{raw}_k),
-I_{lim},I_{lim}\right].
\]

The tracking correction uses **achieved rate- and position-limited bypass**, not an impossible raw command. That helps avoid wind-up when the valve is saturated or cannot move as quickly as requested. The code also bounds the integral state and rejects an excessive \(K_{aw}\Delta t\) sample condition.

No analytical global closed-loop stability proof is claimed. Controller gains are chosen for a synthetic demonstration, not identified from plant dynamics.

### 21.5 Causality and legitimate open-loop comparison

At each interval start, the controller may use the current wall temperature and its previous state. It does **not** receive future source-temperature/flow inputs. Tests modify future load profiles and assert that earlier PI commands remain unchanged.

The open-loop and PI comparisons use the same initial wall state, source sequence, thermal hardware parameters and elapsed time. The only difference is the presence or absence of feedback. This preserves a fair within-model causal comparison, although it is not a blinded experimental trial.

### 21.6 Physical limits

Real plant bypass hardware may have significant pressure loss, hysteresis, temperature-dependent density, actuator lag, nonlinear position-to-flow calibration, sonic conditions and safety shutdown states. None is identified in the toy flow-fraction model. A true closed-loop operation design would require control-authority measurements and facility-specific protection logic.

Source: `src/sco2_braytonbench/control_whr.py`, `tests/test_control_whr.py`, `tests/test_control_whr_co2.py`, and `docs/G5_WP3_BYPASS_PI_CONTROL.md`.

## 22. WP3 numerical control outcome and its important trade-off

### 22.1 The executed synthetic scenario

An **artificial ideal-gas** model with zero installed recuperator UA, wall capacitance **2 MJ/K**, gas-wall UA **40 kW/K**, wall-CO₂ UA **25 kW/K**, total exhaust flow 30 kg/s and source gas cp 1100 J/(kg·K) was used. The prescribed source was 850 K in the first nine steps, then 880 K in the next nine steps—**18 steps × 5 s = 90 s**.

Both baseline and PI start at wall **700 K**, setpoint 700 K and bypass fraction **0.15**.

Representative PI coefficients: \(K_p=0.04\) fraction/K, \(K_i=0.0025\) fraction/(K·s), \(K_{aw}=0.20\) 1/s, with illustrative bias and integral limit. Position limit \(b_{max}=0.85\), per-step rate bound 0.025 fraction/s, minimum active branch flow 1 kg/s.

### 22.2 Accuracy and recovered-shaft-energy metrics

| Metric | Fixed bypass | Sampled wall PI | PI consequence |
|---|---:|---:|---|
| Interval count and duration | 18 / 90 s | 18 / 90 s | Matched scenario |
| Duration-weighted **end-sample** wall RMSE | **11.4627966 K** | **1.7170154 K** | **85.02% lower** |
| Trapezoid approximation to \(\int|e|dt\) | **812.851959 K·s** | **140.641923 K·s** | **82.70% lower** |
| Time-integrated **net shaft** energy | **29.6939315 MJ** | **28.6139387 MJ** | **1.079993 MJ lower, 3.64% decrease** |
| Integrated combined first-law residual | +8.20×10⁻⁸ J | −1.45×10⁻⁷ J | Consistent numerical bookkeeping |

The RMSE is computed at interval endpoints, with each squared error duration-weighted. The absolute-error integral is only an endpoint trapezoid approximation. Neither metric is a continuous-time optimum guaranteed by the code.

Net shaft energy represents integrated quasi-steady *turbine minus compressor* thermodynamic power, **not measured generator output**. There is no included motor/fan/coolant-pump parasitic energy penalty or physical valve actuator consumption.

### 22.3 Trade-off: why better control gave less net work

The PI achieves tighter wall-temperature tracking by diverting source gas rather than allowing the wall to absorb all incoming thermal energy. Some heat that could contribute to cycle power remains in the mixed exhaust. The lower recovered shaft energy is therefore **a physically expected cost**, not a hidden numerical failure.

One can define an objective combining tracking error, net work, actuator motion, temperature safety margin, equipment wear and emissions. WP3 did **not** perform a validated multi-objective techno-economic optimisation. It only recorded one constrained controller scenario.

### 22.4 First-law result is not independent plant performance

The ~10⁻⁷ J numerical residual is small compared with multi-megajoule model energy terms because source, wall, cooler and shaft are evaluated from the same conservation-consistent stage model. It is a useful regression test for missing/doubled terms. It is not a measured first-law uncertainty or evidence that the assumed UA and controller gains have physical accuracy.

### 22.5 What the WP3 study establishes

- The source bypass has a defined physically traceable mass/enthalpy path.
- The control sign and sample causality are testable.
- Position/slew/integral constraints can be enforced and stress tested.
- A matched synthetic scenario shows explicit temperature control versus heat-recovery trade-off.
- Separate real-CoolProp smoke checks support numerical use of the bypass/cycle coupling.

**It does not establish** universal PI superiority, field-tuned stability, safety, or a CARBOSOLA supervisory control implementation.

Detailed source: `docs/G5_WP3_RESULTS.md` and the machine CSV/JSON from the dedicated WP3 CI artifact.

---

# Part V — Prospective validation, metrology and reproducible release engineering

## 23. WP4 — experimental readiness, candidate instrumentation and staged test design

### 23.1 The conceptual move

Numerical verification asks whether an algorithm solves the equations it claims to solve. Experimental validation asks whether those equations and assumed parameters predict independent physical observations within an uncertainty budget. The second question cannot be answered by adding more synthetic tests to the same model.

WP4 therefore designed a **prospective experimental-readiness package**, with explicit sensor definitions, planned test families, data-quality rules, provenance and holdouts. It did **not** conduct a laboratory experiment or obtain permission to operate CARBOSOLA or any other high-pressure facility.

### 23.2 Measurement register

The 35 candidate channels in `protocols/wp4/measurement_channels.csv` cover distinct physical boundaries:

| Channel group | Proposed observables | Research purpose |
|---|---|---|
| Waste-gas thermal source | Inlet gas T, outlet active-branch T, downstream mixed T, source pressure | Energy removed, source loss and mixing assumptions |
| Waste-gas mass split | Total flow, active branch, bypass branch | Actual bypass fraction, not inferred solely from command |
| Source gas properties | Composition/enthalpy and cp estimate | Replace constant cp where necessary; quantify thermal-property uncertainty |
| Solid wall | Multiple candidate wall temperatures | Test lumped isothermal-wall assumption; estimate storage/gradient |
| CO₂ state path | T, P and mass flow around actual heater/recuperator/compressor/expander ports | Independently calculate CO₂ enthalpy duty and map state numbers |
| Cooler | Coolant inlet/outlet temperature and mass flow | Independent sink energy accounting |
| Machine/shaft if present | Speed, torque, net shaft/electrical power | Separate mechanical shaft work from electrical and parasitic power |
| Control | Bypass command and observed physical position | Identify latency, hysteresis, position-to-flow response |
| Acquisition/protection | Common time source, event and trip status | Align transient signals and document safety/quality without disabling interlocks |

Every listed channel has **unconfirmed** installation, calibration and clock-synchronisation status. Merely listing a plausible sensor does not assert that a facility has purchased, located, calibrated or recorded it.

### 23.3 Campaign cases and their intended identifiability

The [13-case matrix](https://github.com/Open-Energy-Methods/sco2-braytonbench/blob/main/protocols/wp4/prospective_test_matrix.csv) includes:

| Case ID | Proposed stage | Principal observable / research gate |
|---|---|---|
| WP4-D00 | Desk intake | Actual P&ID, loop topology, component presence, safe permissions and commissioning stage |
| WP4-D01 | DAQ/metrology | Calibration records, response/lag, time sync and alias filtering |
| WP4-S01 | Repeated nominal steady | Independent first-law closure and repeatability at approved conditions |
| WP4-S02 | Multiple steady source points | Temperature/flow dependence of effective source/wall/CO₂ conductance |
| WP4-S03 | Bypass split and mixing | Actual active/bypass flow and source enthalpy across junction |
| WP4-T01 | Source temperature step | Thermal time constant, wall response, sensor delay |
| WP4-T02 | Source flow perturbation | Effective gas-wall UA sensitivity and hydraulic loss |
| WP4-T03 | Bypass command step | Actuator movement, deadband, actual mass fraction and lag |
| WP4-T04 | Source ramp | Nonlinear transient response versus rate-limited boundary variation |
| WP4-T05 | Small bounded excitation | Local sensitivity to independent parameter directions |
| WP4-C01 | Controlled comparison | Matched fixed-bypass vs permitted feedback control, with energy cost |
| WP4-V01 | Sealed validation | Whole-run independent holdouts after fit/tuning freeze |
| WP4-A01 | Passive safety-log audit | Read-only trip/status and timestamp evidence; no forced interlock operation |

All thirteen cases are **proposed** and have `approval_status=not_requested`. Their appropriate operating points, perturbation amplitudes, hold durations, sensor sample rates, safety limits and scheduling can only be set after facility-specific review.

### 23.4 First required deliverable at a real laboratory

Before energised or dynamic tests, an authorised engineer must supply/confirm the real process and instrumentation diagram, current equipment/expander presence, wall and bypass topology, source gas composition, actual permitted pressure-temperature envelope, protection/interlocks and data access. If the real hardware **does not** contain the assumed gas→stored-wall→CO₂ interfaces, fitting the model's hypothetical UAs is scientifically meaningless; the model must be reformulated around the actual equipment.

A lab supervisor’s authority cannot be replaced by a GitHub CI status, software issue comment or proposed operating-point table.

### 23.5 Why compressor/turbine topology is conditional

The model uses a turbine state 4→5 to calculate \(W_t\). Some publicly documented sCO₂ demonstrator commissioning configurations have different levels of equipment completion. The proposed sensor register marks particular turbine and shaft channels conditional rather than assuming their installation. A real experimental plan must map instrument tags and units to the actual current plant P&ID before assigning model states.

### 23.6 Safety and operating constraints

A future test-specific protocol must separately review: maximum pressure and temperature, safe approach to critical/pseudocritical regions, minimum/source/recuperator stack and pinch limits, maximum metal temperature and thermal stress, cooling availability, trip logic, valve authority, loss-of-flow, pressure surge, actuator saturation and bypass failure.

WP4 does not set numerical values for these limits or perform a hazard analysis. The laboratory protection controller remains authoritative. Proposed software may ingest event logs **read-only** but may not override interlocks.

## 24. Measurement uncertainty, DAQ validation and parameter identifiability

### 24.1 Why uncertainty cannot be assigned from hope

The WP4 standard-uncertainty ledger currently contains **no fabricated manufacturer accuracies** and no implied calibration certificates. Every channel's physical resolution, calibration interval, repeatability, drift, contact error, thermowell lag, common reference bias and acquisition timing must be established before quantitative validation.

A published “maximum permitted error” does not automatically equal a one-standard-deviation uncertainty; distribution and coverage assumptions matter. Correlations can dominate a temperature **difference**, even if individual thermometers have similar nominal accuracies.

### 24.2 First-order sensible-source heat duty

For constant-\(c_p\) source gas:

\[
Q=\dot mc_p(T_{in}-T_{out}).
\]

With independent standard uncertainties in \(\dot m\) and \(c_p\), and a temperature correlation coefficient \(\rho\) between inlet and outlet readings:

\[
u(Q)^2=
(c_p\Delta T\,u_{\dot m})^2+
(\dot m\Delta T\,u_{c_p})^2+
(\dot mc_p)^2
[u_{T,in}^2+u_{T,out}^2-2\rho u_{T,in}u_{T,out}].
\]

This is a **linearised first-order propagation** following GUM-style sensitivity coefficients, with explicitly limited covariance assumptions. It is *not* a full thermophysical EOS uncertainty propagation for near-critical CO₂ enthalpy, and it does not include all sensor timing/mixing/systematic effects.

### 24.3 Independently checked toy numerical uncertainty

The fixture sets \(\dot m=2\) kg/s, \(c_p=1000\) J/(kg·K), \(T_{in}=400\) K and \(T_{out}=350\) K. Standard uncertainties: \(u_{\dot m}=0.1\) kg/s, \(u_{c_p}=20\) J/(kg·K), \(u_{T,in}=1\) K, \(u_{T,out}=2\) K; temperature correlation \(\rho=0.25\).

Then:

\[
Q=2(1000)(50)=100{,}000\ \mathrm W,
\]

\[
u^2(Q)=(50{,}000\cdot0.1)^2+(100\cdot20)^2+
2000^2(1^2+2^2-2(0.25)(1)(2))
=45{,}000{,}000\ \mathrm W^2,
\]

\[
u(Q)=6{,}708.2039\ \mathrm W\quad(k=1).
\]

Every number above is a **synthetic mathematical demonstration**, not the uncertainty of any installed CARBOSOLA probe.

A perfect shared temperature-offset covariance can cancel in an ideal temperature difference; conversely, independent temperature noise does not cancel. Both limiting cases are tested. At zero thermal duty, a relative uncertainty ratio may be undefined despite finite absolute uncertainty—this is handled explicitly.

### 24.4 Near-critical CO₂ uncertainty is different

A CO₂ heater or cooler heat rate should be obtained from measured pressure/temperature and a consistent EOS:

\[
Q_{\mathrm{CO2}}=\dot m_{\mathrm{CO2}}[h(p_{out},T_{out})-h(p_{in},T_{in})].
\]

Near pseudo-critical conditions, derivatives of \(h\) and \(\rho\) with temperature and pressure may be steep or non-Gaussian. Proper propagation should include correlated pressure/temperature errors, time lag, property-model uncertainty, composition and phase-domain restrictions. Future Monte Carlo propagation or uncertainty-aware inversion is needed; the present constant-\(c_p\) utility does **not** claim that capability.

### 24.5 Data-acquisition and quality contracts

The long-format DAQ validator checks:

- Exact channel IDs and SI unit matches against the candidate register.
- Numeric time stamps, unique tag/time combinations and monotonic order per tag.
- Optional maximum sample-gap violations.
- Explicit `OK`, `MISSING` and `REJECTED` statuses.
- Finite values in nonmissing rows and nonphysical nonpositive kelvin inputs in accepted samples.
- Run IDs, file columns and malformed rows.

This **does not** verify that two separate instruments share a genuinely synchronised physical clock, that sampling bandwidth is sufficient to resolve a wall time constant, or that an accepted numeric sensor value is calibrated.

For actual data, raw immutable files need independent hashes, a DAQ configuration version, timebase-offset record, filters, interpolation/imputation history, event-log references and a quality-control decision ledger.

### 24.6 Run provenance and external attestation

The prospective manifest `protocols/wp4/prospective_run_manifest.json` requires fields for run ID, source facility and P&ID revision, run authorization, calibration manifest, timing evidence and SHA256 of raw files/register. In the supplied example these evidence fields are **null** because no laboratory event occurred.

The structural validator can reject malformed/missing fields. It cannot authenticate whether a certificate signature exists, a safety approval is genuine, a Git hash corresponds to original device bytes, or an instrument was installed. Even syntactically complete external-looking metadata remain subject to independent stewardship.

### 24.7 Local identifiability versus real parameter recovery

To identify \(UA_{g,w}\), \(UA_{w,CO2}\) and \(C_w\), the observed outputs must respond to those parameters in distinguishable ways. A normalized local sensitivity matrix may be written as

\[
S_{ij}=
\frac{\theta_j}{\sigma_{y_i}}
\frac{\partial y_i}{\partial\theta_j},
\]

with appropriate nonzero parameter reference scales and observable covariance. If its columns are linearly dependent, multiple parameter combinations produce locally indistinguishable responses to the selected tests.

WP4 implements a column-scaled rank screen. It uses toy full-rank/dependent matrices to verify its logic. **Full rank alone does not guarantee** good conditioning, low parameter covariance, global identifiability or real-experiment calibration accuracy.

A stronger future study would inspect singular values and parameter profile likelihood, practical parameter confidence regions and posterior predictive error under independently measured disturbances. Actual source flow dependence and sensor lag must be separated from wall capacity rather than absorbed into it.

### 24.8 Holdout policy and leakage prevention

Randomly selecting individual time samples from the same transient can leak model-specific dynamical information between fit and test. WP4 instead defines disjoint lists of **complete experimental runs or physical run families** for training, model selection and sealed validation.

The validator rejects duplicated/overlapping IDs, while explicitly acknowledging that different labels may still refer to correlated physical experiments. A sealed holdout must be controlled operationally, not merely described as such in a JSON file.

The final measurement plan should predeclare fit parameters, allowed corrections, exclusion rules and validation metrics before opening the sealed data.

### 24.9 WP4 numerical audit outcome

The executable `examples/wp4_readiness_audit.py` reports:

| Readiness audit field | Result |
|---|---:|
| Candidate channel definitions | **35** |
| Proposed desk/steady/dynamic/control cases | **13** |
| Experiment cases formally authorized | **0** |
| Confirmed installed/calibrated candidate channels | **0 recorded** |
| Cases ready for actual measured validation | **0** |
| Real CARBOSOLA data acquisition performed | **No** |
| Mathematical uncertainty fixture | **100 kW ±6.7082 kW standard** (synthetic only) |

A report showing **zero** ready cases is correct and desirable when external metrology evidence is absent. Treating those blocked gates as “passed experiments” would be a serious scientific error.

Sources: `docs/WP4_EXPERIMENTAL_READINESS_PROTOCOL.md`, `src/sco2_braytonbench/experimental_readiness.py`, `tests/test_experimental_readiness.py`.

## 25. WP5 — distribution, installation and reproducibility engineering

### 25.1 What release engineering has to prove

A repository passing tests in a developer's editable checkout does not demonstrate that another researcher can install the released wheel, rebuild the source distribution, recover protocols and reproduce numerical examples without accidentally importing the working tree.

WP5 therefore introduced independently reviewable source-distribution, wheel, provenance and scenario-replay gates.

### 25.2 Distribution contract

**Wheel:** installable software package with its expected modules and SPDX/BSD licence metadata. The wheel does not pretend to install every research script or full external dataset.

**Source distribution (sdist):** source files, model scripts, methods documentation, tests, prospective protocols and any research fixtures authorized for redistribution. The `MANIFEST.in` policy excludes generated traces and the uncleared Mantilla transcription.

**Citation:** `pyproject.toml` and `CITATION.cff` both declare package **0.5.0a0**, BSD-3-Clause and a nonvalidated research-software identity. Any future RC must update version strings coherently.

### 25.3 Fresh-install replay method

The WP5 CI job builds wheel and sdist from the **same source commit**, installs each into a distinct virtual environment, copies checked-in example/protocol resources to clean workspaces, and runs four deterministic scenario families:

1. WP2a exact thermal-wall response.
2. WP2b finite-source/thermal-wall/algebraic cycle response.
3. WP3 matched fixed-bypass versus sampled PI.
4. WP4 prospective-readiness and toy GUM/rank audit.

The runner then compares regenerated CSV headers/rows, categorical evidence flags, JSON structure and all finite numerical values using documented tolerances. It rejects altered physics, changed evidence classification, NaN values, missing files or malformed record structure.

### 25.4 Why two distribution formats matter

An sdist may accidentally omit test fixtures, metadata, source files or licences; a wheel may be missing a package module or carry stale version metadata. A fresh-installed replay detects both a packaging inconsistency and inappropriate reliance on the developer's checkout.

A successful comparison is **numerical reproducibility within a specific environment/tolerance**, not bitwise reproducibility across every build OS or timestamp-bearing archive.

### 25.5 Release-gate tool and machine audit

`scripts/v1_release_gate.py` performs:

- Project name, version, Python support, BSD licence and CFF agreement checks.
- Required documentation/production module checks.
- Wheel metadata and included licence checks.
- Required research sdist member checks.
- Explicit failure if embargoed Mantilla CSV appears in source HEAD or sdist.
- Source and evidence SHA256 hashing.
- Structural and numeric comparison between independent wheel/sdist generated scenarios.
- Output report of **manual scientific and governance blockers**, instead of presenting a green script as release approval.

Its CI artifacts include numerical replay comparisons and an auditable source/distribution hash manifest.

### 25.6 Failure-injection coverage

WP5 tests deliberately simulate:

- Incorrect CFF/pyproject version pairing.
- Wrong SPDX licence metadata.
- Missing wheel/sdist archive or missing mandatory archive member.
- Altered synthetic scenario temperature/power number.
- Source-label mutation from “synthetic” to “measured.”
- Unexpected CSV columns and incompatible JSON keys.
- Nonfinite numerical values.
- Reintroduction of the embargoed third-party experimental-density table.

This approach is stronger than testing only that the success path prints “PASS.” A scientific release gate must reject plausible contamination cases.

### 25.7 Actual version and release action

The alpha code has **not** been bumped to `1.0.0rc1` or `1.0.0`. No new GitHub Release or Zenodo DOI is represented by WP5. The project has a **release-candidate preparation mechanism**, not independent authorization to publish.

Full detail: `docs/WP5_RELEASE_ACCEPTANCE.md`, `tests/test_v1_release_gate.py`, `MANIFEST.in`, `.github/workflows/ci.yml`.

## 26. Complete verification and CI evidence chain

### 26.1 How to interpret test counts

GitHub Actions has separate general Python suites and specialised real-fluid/scientific jobs. The general Python jobs skip optional CoolProp-only tests when CoolProp is not installed. Those skips do **not** prove real-fluid functionality; dedicated pinned CoolProp jobs run that path.

Similarly, a density measurement test may now be intentionally skipped without the separately obtained original Mantilla table. The numerical report must not count that skip as a newly executed experimental-density result.

### 26.2 Major historical and current CI runs

| Evidence run | Scope | Recorded status |
|---|---|---|
| [#42058735222](https://github.com/Open-Energy-Methods/sco2-braytonbench/actions/runs/42058735222) | 5 Nov H1d exploratory branch, original-source/common-key benchmark | **15/15** successful; exploratory PR remains unmerged |
| [#42202314460](https://github.com/Open-Energy-Methods/sco2-braytonbench/actions/runs/42202314460) | WP0/1/2a baseline and packaging | **13/13** successful |
| [#42206347763](https://github.com/Open-Energy-Methods/sco2-braytonbench/actions/runs/42206347763) | WP2b finite-source dynamic wall and real-fluid smoke | **15/15** successful |
| [#42246699219](https://github.com/Open-Energy-Methods/sco2-braytonbench/actions/runs/42246699219) | WP3 controller/real-fluid smoke head | **17/17** successful |
| [#42250403856](https://github.com/Open-Energy-Methods/sco2-braytonbench/actions/runs/42250403856) | WP4 prospective metrology, format/uncertainty/holdout | **18/18** successful |
| [#42256499369](https://github.com/Open-Energy-Methods/sco2-braytonbench/actions/runs/42256499369) | WP5 data-rights quarantined source branch | **20/20** successful |
| [#42258225916](https://github.com/Open-Energy-Methods/sco2-braytonbench/actions/runs/42258225916) | First WP0–WP5 integrated `main` SHA `88579f7...` | **20/20** successful |
| [#42264837301](https://github.com/Open-Energy-Methods/sco2-braytonbench/actions/runs/42264837301) | Rights-cleanup PR #29 | **20/20** successful |
| [#42266275348](https://github.com/Open-Energy-Methods/sco2-braytonbench/actions/runs/42266275348) | Current after-rights-cleanup `main`, SHA `8df1711...` | **20/20** successful |

The latest current `main` jobs, not an earlier successful PR run, are the decisive integrated software evidence for this report.

### 26.3 General Python and real-CoolProp division

During WP5, the Python 3.10, 3.11 and 3.12 suites each passed **474 tests** with **11 optional skips** on the then-current set. Later rights-cleanup regression tests and opt-in density behaviour change the exact total/skip composition; do not reuse “474/11” as the current exact HEAD suite count without inspecting the relevant latest job log.

Real-CoolProp jobs cover independent property/cycle/recuperator and finite source analyses, fixed heater UA, dual heater/cooler, WP2b wall cycle and WP3 bypass compatibility. The off-design coupled-heater/cooler job is long-running; its eventual passing **on both merged main commits** is recorded in the runs above.

### 26.4 WP2a–WP5 numerical evidence classes

| Model/test family | Strongest evidence presently supported | What remains unproven |
|---|---|---|
| WP2a exact wall | Analytical exponential response and integrated first law | Physical wall and material calibration |
| WP2b source-wall-cycle | Independent constant-cp limiting solution, RK4 step refinement, source/shaft/cooler energy ledger, one real-fluid smoke | Dynamic CO₂ fluid mass/pressure, spatial metal and source-plant validation |
| WP3 bypass PI | Correct conserved gas split and mixing, causality, anti-windup, open/closed synthetic comparison | Physical valve dynamics, robust industrial control and sensor delay |
| WP4 protocols | 35-channel/13-case schema, synthetic QA, GUM/rank fixtures, provenance/holdout checks | Every real sensor, calibration, actual experiment and measured parameter |
| WP5 reproducibility | Fresh wheel and sdist installation and same-scenario output agreement, licence/source hashing | Independently signed scientific review and full historical data-rights determination |

### 26.5 Artifacts and source-of-truth rule

An Actions artifact contains derived CSV/JSON reports, tests or built archives **tied to that run**. It should be referenced with the run ID, head SHA and model/fixture classification. Artifacts may expire; numerical results must remain reproducible from source inputs and scripts.

The release audit's SHA256 values establish file identity. They do not prove a source’s copyright status, correct experimental calibration or that two numerical models independently agree.

## 27. Data, code copyright and permission-to-publish governance

### 27.1 Software and source data are separate licensed works

BSD-3-Clause applies to the original repository software and any source assets actually licensed that way. It does not automatically relicense scientific papers, journal-curated datasets, machine figures or third-party transformed tables.

This distinction is especially important for an open-source research codebase intended for an immutable Zenodo deposition, where the **entire uploaded source archive** must be fit for redistribution.

### 27.2 Stuttgart CC BY 4.0

The Theologou et al. original Mendeley Data source DOI [10.17632/4mvk4nxrkz.1](https://doi.org/10.17632/4mvk4nxrkz.1) explicitly provides CC BY 4.0 terms. Attribution should retain original authors, DOI, original source licence link, identification of any transformations, and anomaly/exclusion decisions.

A BSD code archive may contain CC BY data **if its independent data licence and attribution are visibly preserved**. Do not describe transformed source records as wholly original BSD code.

### 27.3 NIST ThermoML: concrete risk mitigation

The Mantilla table's complete 49-point transcription carried uncertain downstream reuse rights under the NIST/TRC archive's publisher permission context. [Issue #27](https://github.com/Open-Energy-Methods/sco2-braytonbench/issues/27) documents the rights-holder inquiry and remediation decision.

At current HEAD:
- The normalized full 49-point CSV has been **deleted**.
- New wheel/sdist/source-snapshot gates reject its reintroduction.
- Original bibliographic/provenance metadata remain.
- The optional measured-density test and reporting script require user-supplied external data.
- No external redistribution permission or answer has been received.
- Historical Git objects/downloads may still contain the previous table; current HEAD deletion is **not** complete history erasure.

Those last two points mean issue #27 should remain open pending rights-holder reply or competent review of history treatment. A draft inquiry alone is not written permission.

### 27.4 Other source-derived materials

Numerical coefficients copied from journal equations, textbook correlations and source-reported benchmark values also require proper attribution and a case-specific assessment of allowed reuse. The original Kim paper PDF is **not** to be rehosted as part of this repository by default. HZDR numerical RODARE images/tables, Sandia plots and turbine source figures should be treated according to their own explicit terms and research provenance.

A release steward should inspect **every actual archive member**, not just `LICENSE` at repository root. Exact data content and rights matter, especially for all-version Git snapshots and future Zenodo tarballs.

### 27.5 Research integrity beyond copyright

Attribution cannot substitute for a measured-validation claim. “Data are public” cannot substitute for licence clearance. “Model agrees with a published number” cannot substitute for state-map parity. “Controller passes CI” cannot substitute for safe operation. These are **independent** necessary conditions at different research and engineering stages.

## 28. Quantified research uncertainty and scientific risk register

### 28.1 Four distinct uncertainty classes

1. **Measurement uncertainty:** actual pressure, temperature, mass-flow, heat-flux, wall-temperature and power instruments, calibration/reference covariance, time lag and data reduction.
2. **Thermophysical/material uncertainty:** source mixture composition, CoolProp/REFPROP EOS differences, temperature-dependent \(c_p,\mu,k,\rho\), near-pseudocritical behaviour and wall material properties.
3. **Model-form uncertainty:** six-state compression/expansion efficiencies, fixed-UA approximation, source mixer, one isothermal wall, lack of buoyancy/geometry coupling, missing rotating dynamics.
4. **Numerical uncertainty:** root tolerance, discretisation and transient step size, property inversions, cumulative integration error, station eligibility and apparent model ranking on different successful subsets.

Conflating these classes makes uncertainty statements meaningless. A numerical first-law residual belongs to category 4/implementation checking, not category 1.

### 28.2 Present high-priority risks

| Risk | Consequence | Current mitigation / status |
|---|---|---|
| CO₂ fluid inventory absent | Cannot predict pressure/flow transient and shaft–network dynamics | Explicit WP2b/G4 scope; future research |
| Thermal wall \(C_w\) and two UAs hypothetical | Transient time scale and heater response not identifiable physically | Independent mathematical limit; WP4 candidate measurements |
| Gas-side flow-dependence omitted | Bypass effects could be inaccurate outside narrow assumed regime | Tests label UA fixed; propose flow perturbations |
| PI actuator is sampled fraction, not real valve | Dynamic actuator motion/pressure loss/hysteresis absent | Discrete slew and anti-windup correctly documented |
| Stuttgart source conditional HTC | Reduced wall T and HTC not independent; orientation/geometry mismatch | Flux-driven versus conditioned separate, original exclusions retained |
| H1c cross-fluid transfer fails | Severe unphysical overprediction | Negative results preserved, not recommended as plant law |
| H1d source Eq.24 ambiguity | Wrong formula could be silently institutionalised | Issue #20 and exploratory PR #19 |
| ThermoML historic rights uncertain | Unlicensed redistribution via prior Git history | Removed from current HEAD; issue #27 awaiting authoritative resolution |
| No independent qualified reviewer | Cannot claim externally accepted scientific v1.0 | Issue #28 and reviewer inquiry prepared, not approved |
| No facility topology/calibration | Experimental claims unsupported | WP4 register/cases all unconfirmed and blocked |
| Near-critical EOS sensitivity | Apparent convergence/accuracy could be local | Property/regression tests plus planned sensitivity/uncertainty analysis |
| Packaging source drift | Released source not reproducible | WP5 wheel/sdist isolated replay, SHA256 and failure injection |

### 28.3 Prioritisation

The highest return on additional work for a **research software release** is now permission/citation cleanup, external model-form review, precise public claims and immutable evidence reproduction—not another speculative component formula.

For a **doctoral research programme**, the highest scientific return is independent experimental thermophysical/cycle data, identifiable wall/UA/actuator parameters and eventual CO₂ inventory dynamics. Those aims require access and instrumentation, not simply more code.

## 29. Stage-gate summary and formal release status

### 29.1 Current research-software gate matrix

| Gate | Status at evidence cut-off | Required qualification |
|---|---|---|
| G0/G2 original literature/source cycle | **Numerically reconstructed** | Original complete source model not recovered |
| G3 finite heat-source feasibility | **Numerically verified scenarios** | Source/geometry/controls hypothetical |
| G3.1 fixed installed heater UA | **Verified synthetic inverse and CoolProp tests** | No measured installed heater |
| G3.2 finite sink / two installed UAs | **Verified steady numerical examples** | No coolant/CO₂ inventory transient |
| G3.3 property alternatives and section refinement | **Verified selected numerical points** | Not global convergence proof |
| G3.4 source-intake provenance | **Documented** | Some source ambiguities unresolved |
| G3.5 H1a–H1c | **Executed source-attributed benchmark including negative results** | Out-of-domain correlation fidelity poor |
| G3.5 H1d Kim experimental branch | **Exploratory branch verified, NOT merged** | Eq.24 source/fit domain unresolved |
| WP0/WP1 and WP2a | **Integrated, CI green** | Not a CO₂ inventory solver |
| WP2b | **Integrated, CI green** | Synthetic stored wall + quasi-steady cycle only |
| WP3 | **Integrated, CI green** | Synthetic sample-bounded controller only |
| WP4 | **Integrated protocols and data-validator tests** | **Zero** experimental validation-ready cases |
| WP5 | **Integrated source/distribution reproducibility tests** | Scientific/legal release approval outstanding |
| Rights cleanup #29 | **Integrated; current HEAD and sdist exclude Mantilla rows** | Older Git history and publisher response pending |
| Full final integrated-main CI | **20/20 passed** | Software test success; not external validation |
| Independent human scientific review | **OPEN, issue #28** | Qualified reviewer must actually deliver assessment |
| Final v1.0 licence/historical content review | **OPEN, issue #27** | Written rights/history decision needed |
| `1.0.0rc1` and `1.0.0` publication | **NOT ISSUED** | A deliberate authorized release step |

### 29.2 Why “integration complete” and “v1.0 complete” differ

All feature and release-engineering branches may be merged for transparent **alpha development**, while formal publication remains blocked. Version tags, Zenodo DOI objects and bibliographic metadata are persistent claims. A tagged source snapshot can include data/metadata that a conventional Python sdist intentionally excluded, so legal rights must be examined at **whole-repository** scope.

A v1.0 release need only meet its correctly delimited *software* claim. It should **not** require impossible prior CARBOSOLA validation if that was never an advertised release promise. But it **must** preserve the scientific limitations in README, citation and release notes, and a credible independent review must check those claims.

### 29.3 Outside approvals cannot be self-certified

The repository's internal AI-assisted technical audit, even with correct analytical rederivations, is not a separate qualified human referee. Preparing an email does not mean a reviewer agreed to perform a review or signed an acceptance. Similarly, an NIST inquiry draft does not establish publisher permission.

Therefore an honest status statement is: **alpha source and integrated CI are ready; independent approval/licence-history decisions are not yet complete**.

---

# Part VI — Research relevance, continuation and preservation

## 30. Relation to a dynamic sCO₂ Brayton doctoral research programme

### 30.1 Research contribution already available

A future investigator can start with a numerically checked thermodynamic reference, finite heat-source and cooler boundary-value framework, separate property backend and synthetic dynamic-control method. The codebase offers a transparent way to introduce, test and reject assumptions.

For a doctoral programme involving dynamic simulation, changing waste-heat streams and experimental operation, the transferable capabilities include:

- Formulating state/enthalpy first laws rather than treating energy as an arbitrary control knob.
- Distinguishing fixed installed heat-transfer equipment from required heat-exchanger design sizing.
- Propagating finite-source disturbances through a defensible stored-heat control volume.
- Developing a controller whose physical input has a source-side energy/enthalpy trace.
- Designing test matrices around measurable observables and identifiable parameters.
- Preserving negative transferability findings and scientific source discrepancies.
- Building versioned, reproducible research software with independent verification gates.

These are **methods and preparations**. They must not be described as HZDR experimental outputs or proof of readiness for unsupervised operation of a 300-bar test facility.

### 30.2 Connection to facility-focused research

A facility-oriented dynamic study would need the actual layout, installed compressor/expander, high/low pressure volumes, heat exchangers, valves, pump/cooler, metal masses and control/protection hardware. Only then could the software boundaries be mapped to the real system.

The immediate scientific question is not merely “Can this model reproduce 520 °C?” It is whether measured time series can uniquely constrain the model parameters and whether any simulated dynamic pressure, fluid enthalpy and heat-transfer responses are physically correct across independent load cases.

A research programme should explicitly reserve opportunities to **reject** the present single-wall or constant-UA abstractions when measured data demand a more complex model.

### 30.3 Transfer to an HZDR application portfolio

As an application artifact, the repository can substantiate Python/research software, nonideal thermodynamics, numerical analysis, structured model verification, finite heat-source reasoning, and experimental-test planning. The qualified description is:

> An independently developed, CI-verified sCO₂ Brayton-cycle research framework combining real-fluid steady thermodynamics, finite-source and installed-UA heat-exchanger studies, a synthetic thermal-storage/PI demonstrator, and a documented prospective laboratory-validation protocol.

It is not accurate to call it a published v1.0 experimentally validated CARBOSOLA digital twin or a complete dynamic process simulator.

### 30.4 Formulation of defensible original-work contributions

A methods paper or software note could emphasize *model boundary separation, reproducible negative correlation transfer, source-data provenance and first-law-consistent transient surrogate coupling*. These are contributions demonstrably visible in the repository. Experimental predictive accuracy on real plant dynamics would require later evidence, probably in a distinct research paper.

## 31. Forward research roadmap — after the integrated alpha baseline

The roadmap is not a list of features to claim as already built. Each stage has a hypothesis, required evidence, failure criteria and a decision to make.

### 31.1 R0 — final research-software release clearance (near-term)

**Hypothesis:** the current alpha source can be released as v1.0 research software while preserving its narrow scientific claims.

Required actions:

- Obtain written advice/rights clarification for Mantilla historic Git copies and other source-derived materials, or authorise an appropriate archive/history remediation under policy.
- Obtain a named independent technical reviewer’s signed assessment of thermodynamics, heat flow, numerical behaviour and limits.
- Verify latest integrated-main CI on a deliberate immutable RC candidate SHA.
- Audit exact tag/Zenodo source membership, not merely the Python sdist.
- Make source/citation metadata, CHANGELOG and release notes mutually consistent.
- Issue a version only after an explicit maintainer release decision.

**Failure condition:** unsupported validation claim, unapproved data in a public tag/source archive, reviewer critical objection or non-green candidate CI.

### 31.2 R1 — physical metadata and independent pilot data intake

**Hypothesis:** a specific available laboratory configuration can support identifiable heat-exchanger and source-control terms.

Required: P&ID; working fluid composition and charge, wall geometry/material, sensor locations and calibrations, clock synchronization, safety/operating authorization, raw repeat measurements and full source licences.

Acceptance: source/sink and gas/CO₂ energy balances *within justified uncertainty*, calibrated instrument timing, documented exclusions and explicit topology agreement. A forced residual of zero using shared computed outputs is not sufficient.

Failure: source properties unknown, independent flow and temperatures missing, calibration older/invalid or physical flow path mismatched.

### 31.3 R2 — source-side, wall and flow-dependent UA identification

**Hypothesis:** the lumped thermal wall and two independent installed conductances are adequate over a limited measured domain.

Perform repeated steady operating points and low-amplitude transients over approved gas flows/temperatures. Estimate wall capacitance from independently inferred rates and measured metal temperature; distinguish source-side UA from wall–CO₂ UA, wall-to-ambient loss and sensor thermal lag. Test flow/temperature dependence.

Acceptance: parameter covariance/conditioning acceptable, held-out transient predictions with genuine measured uncertainty, and evidence that independent parameter directions are excited.

Failure: different parameter sets fit equally well, wall gradients cannot be neglected or fitted time constant collapses into sensor lag.

### 31.4 R3 — dynamic CO₂ fluid inventory and pressure-network model

**Hypothesis:** steady algebraic cycle states are insufficient to predict real start-up, pressure/flow transients and shaft interaction.

Required physics for each control volume:

\[
\frac{dm_i}{dt}
=\sum\dot m_{in}-\sum\dot m_{out},
\]

\[
\frac{d(m_iu_i)}{dt}
=\sum \dot m_{in}h_{in}
-\sum\dot m_{out}h_{out}
+\dot Q_i-\dot W_i
\]

with a robust EOS inverse \((\rho,u)\mapsto(p,T)\) and actual volume/geometry. Dynamic connections must model pressure-driven mass flow and machine maps; compressors/turbines cannot both be treated as imposed mass-flow devices independent of pressure network.

Potential additional shaft state:

\[
J\frac{d\omega}{dt}
=\tau_t-\tau_c-\tau_{generator}-\tau_{loss}.
\]

These equations are **future scope**, not present implementation. A real dynamic system needs consistent energy-work accounting at flow-connected components and protection constraints, including critical-region numerical regularization.

Acceptance: conservation tests on simple closed volumes, verified EOS inverse/domain behaviour, stable time integration, independent measured pressure/temperature/flow transients.

Failure: missing inventory identification, unphysical negative mass, unresolved phase branch or implied compressor flow exceeding published hardware envelope.

### 31.5 R4 — turbomachinery and actuator maps

**Hypothesis:** calibrated pressure/flow/efficiency/speed characteristics materially alter transient recovered power and control authority.

Required: measured compressor and expander data with clearly defined shaft/electrical boundaries, speed/surge/choke/regulation limits, turbine leakage and bypass valve flow coefficient with hysteresis/rate limits.

Acceptance: off-design maps tested against independent measured operating points, uncertainty bands and realistic actuating pressure differences. Do not infer a map merely from an isolated point or a source paper’s design table.

### 31.6 R5 — next-generation thermal and buoyancy models

**Hypothesis:** a single wall temperature and a scalar global UA conceal important transient/stratification effects.

Candidate progression: multiple axial wall segments; conjugate fluid-wall heat transfer; gas/CO₂ variable property correlations conditioned on real geometry; buoyancy/stratification-aware horizontal tube models; separate top/bottom wall fields; and dynamic cooler boundary.

Validation demands geometry-appropriate experimental stations rather than reusing the Stuttgart 4/8 mm tube error as if it were a PCHE response.

**Failure condition:** model complexity increases without independently identifiable new parameters or measurable predictive improvement.

### 31.7 R6 — source variation, control, robustness and operation strategy

**Hypothesis:** a plant-informed control strategy can improve thermal constraints and net delivered energy under specified industrial waste-heat disturbances.

Compare open loop, sampled PI, state-feedback and possible MPC **only after** physical actuators and dynamic pressure/flow constraints are available. Define a cost function with recovered heat, net exported electricity, metal-temperature safety, source exhaust/stack requirements, valve motion and availability.

Evaluate disturbances on *whole heldout runs* and distinguish predictive control from tuning to a known prerecorded future profile.

Acceptance: parameter/measurement uncertainty robustness, identified actuator performance, safe release/override mechanisms, and statistically defensible differences in predeclared performance metrics.

### 31.8 R7 — plant-level techno-economic analysis

**Hypothesis:** extra recovered shaft power is worthwhile after adding real equipment, cooling, auxiliary power, materials, maintenance and availability costs.

Needed inputs include calibrated HX dimensions/material and pressure losses, power-block equipment prices, coolant/pump/fan energy, waste-heat opportunity cost, duty-cycle distributions, downtime, maintenance, electricity value and investment discount assumptions.

Do not multiply nominal simulated Brayton net power by annual hours and call that a credible investment case without auxiliary/availability data. Levelized energy cost or payback becomes meaningful only with traceable sources, sensitivity and uncertainty.

### 31.9 R8 — publication and public evidence stewardship

Publish code, negative results and measured-derived data separately according to their rights; distinguish experimental instrument uncertainty from model residuals. Archive immutable source releases only when allowed. Provide data dictionaries and raw-to-reduced transformations, reviewer conflict/policy statements, independently rerunnable numerical examples and unambiguous author/DOI attribution.

## 32. Reproduction guide — exact current-source baseline

### 32.1 Select the verified commit

For the integrated 6 November evidence snapshot:

~~~bash
git clone https://github.com/Open-Energy-Methods/sco2-braytonbench.git
cd sco2-braytonbench
git checkout 8df1711a425e21da342bd3f401da61a1375bbc0a
git rev-parse HEAD
~~~

If reproducing a later report-edit PR, use that specific merged commit and verify its CI separately. Version/date labels alone are not immutable content identifiers.

### 32.2 Set up a local Python environment

~~~bash
python -m venv .venv
source .venv/bin/activate            # Linux/macOS
# On PowerShell: .venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -e '.[test]'
~~~

For real-fluid CO₂ analyses, separately install optional CoolProp:

~~~bash
python -m pip install -e '.[test,co2]'
python -m pip install 'CoolProp==8.0.0'
~~~

The version is pinned for the documented scientific CI checks; later versions may produce small numerical differences requiring new evidence. No live internet calls occur inside the scientific computational scripts other than package installation requirements.

### 32.3 Run general numerical tests

~~~bash
python -m pytest -q
python -m pytest -q tests/test_thermal_dynamics.py
python -m pytest -q tests/test_dynamic_whr.py
python -m pytest -q tests/test_control_whr.py
python -m pytest -q tests/test_experimental_readiness.py
python -m pytest -q tests/test_v1_release_gate.py
~~~

If CoolProp is not installed, certain tests are intentionally skipped. Read test summaries and do not reinterpret skips as successes. A project checkout **without the external Mantilla file** will skip its optional measured-density regression.

### 32.4 Reproduce the thermal and control examples

~~~bash
python examples/thermal_wall_step_response.py
python examples/waste_heat_wall_coupled_cycle.py
python examples/waste_heat_bypass_pi_comparison.py
python examples/wp4_readiness_audit.py
~~~

Example outputs are written under:

~~~text
evidence/generated/v1_thermal_wall/
evidence/generated/v1_wp2b/
evidence/generated/v1_wp3/
evidence/generated/v1_wp4/
~~~

These generated CSV/JSON files reflect **synthetic scenario fixtures**. Check the scenario metadata's physical assumptions and whether real CO₂ properties were actually used before citing a number.

### 32.5 Run the optional measured-density case responsibly

The current source does **not** contain the 49 Mantilla original-source observations. Obtain any experimental records independently and under suitable terms before preparing an external normalized CSV. Then:

~~~bash
SCO2_MANTILLA_DENSITY_CSV=/absolute/local/path/thermoml_density.csv \
  python -m pytest -q tests/test_co2_measured_density.py
~~~

Alternatively set the corresponding environment variable in PowerShell. Never commit or upload source rows to this repository without resolving [issue #27](https://github.com/Open-Energy-Methods/sco2-braytonbench/issues/27). An explicit missing-file skip is a legitimate conditional result, not a failed software installation.

### 32.6 Reproduce source-archive release checks

~~~bash
python -m pip install 'build>=1,<2'
python -m build --sdist --wheel
~~~

The complete WP5 gate requires two clean environments and independent execution of the four example families from wheel and sdist, followed by comparison and audit:

~~~bash
python scripts/v1_release_gate.py compare \
  --reference /path/to/wheel-workspace \
  --candidate /path/to/sdist-workspace \
  --out evidence/generated/v1_wp5/wheel_sdist_numerical_comparison.json

python scripts/v1_release_gate.py audit \
  --root . --dist dist \
  --out evidence/generated/v1_wp5/release_gate_report.json
~~~

Run the commands after the necessary workspaces have actually been populated by fresh-installed replay, as done in GitHub Actions. Running `audit` without generated evidence or archives correctly fails; it is not a missing feature to “fix” with fake files.

### 32.7 Expected original-source/data exclusions

- The Mantilla complete normalized density CSV must **not** be present in current source or release archive.
- Stuttgart source-derived files need original CC BY 4.0 attribution and adapted-source notice.
- The H1d Kim exploratory branch can be inspected separately, but is **not** part of current main by default.
- Lab-readiness metadata deliberately show no approved experimental runs.
- No released experiment data or safety credentials should be inferred from the synthetic WP4 fixture.

### 32.8 Check the final integrated CI directly

Use [the actual latest main run #42266275348](https://github.com/Open-Energy-Methods/sco2-braytonbench/actions/runs/42266275348). It records all 20 jobs successful at `8df1711a…`. Download artifacts if still retained; remember artifact IDs and retention vary over time.

The two-install replay is useful precisely because a local editable install might otherwise shadow an incorrect distribution.

## 33. Source, file and evidence index

### 33.1 Internal scientific documents

| Reference | Use this for |
|---|---|
| `docs/RESEARCH_STATUS.md` | Historical work through G3.5; some earlier timestamps describe planned G4/G5 before WP integration |
| `docs/FR2016_COMPARISON_REVIEW.md` | Friedman–Rapp original/parity and state-map limitations |
| `docs/EXPERIMENTAL_DENSITY_DECISION.md` | Historical EOS-to-measured-density numerical comparison only |
| `docs/G3_STEADY_SCREENING_RESULTS.md` | Exact finite source screening input grid, winner points and approaches |
| `docs/G31_FIXED_UA_NUMERICAL_RESULTS.md` | Single installed heater inverse and perturbation numbers |
| `docs/G32_NUMERICAL_VERIFICATION.md` | Installed heater and cooler inverse verification with finite sink |
| `docs/G33_NUMERICAL_VERIFICATION.md` | Source property alternatives and 6/12/24/48 segment study |
| `docs/G34_EXTERNAL_VALIDATION_INTAKE.md` | External evidence class and STU/ZH/KAIST/Sandia concerns |
| `docs/G35_STUTTGART_RESULTS.md` | H1a source gate and forced-convection errors |
| `docs/G35B_RESULTS.md` | Bishop/Jackson conditioned vs flux-driven and heldout comparisons |
| `docs/G35C_LEI_RESULTS.md` | Cross-fluid Lei negative-transfer results |
| `docs/KIM2019_ORIGINAL_SOURCE_RECOVERY.md` | Source equations, table coefficients and Eq.24 ambiguity |
| `docs/G4_THERMAL_CONTROL_VOLUME_SCOPE.md` | Exact lumped-wall kernel requirements |
| `docs/G4_WP2B_FINITE_SOURCE_WALL_CYCLE.md` | Finite gas→stored wall→quasi-steady cycle equations and analytic limit |
| `docs/G5_WP3_BYPASS_PI_CONTROL.md` | Conserved bypass and PI control physics |
| `docs/G5_WP3_RESULTS.md` | 90-s open/closed synthetic comparison and energy cost |
| `docs/WP4_EXPERIMENTAL_READINESS_PROTOCOL.md` | Candidate instrumentation, uncertainty, safety and holdout design |
| `docs/WP5_RELEASE_ACCEPTANCE.md` | Required science, licensing, CI, packaging and release gates |
| `docs/V1_TECHNICAL_AUDIT_2026-11-06.md` | AI-assisted numerical/model-boundary audit, not independent reviewer signoff |
| `docs/DATA_RIGHTS_V1.md` | Dataset-by-dataset copyright/reuse inventory |
| `docs/V1_0_RELEASE_CONTRACT.md` | Stable and experimental software-release scope |
| `docs/V1_0_VERIFICATION_MATRIX.md` | Requirement-to-evidence mapping and remaining gates |

### 33.2 Original article/data references

- Friedman–Rapp (2016): original recuperated cycle comparison, source model not fully recoverable from report detail. Refer to repository original comparison audit and bibliography for full citation.
- Mantilla, Cristancho, Ejaz & Hall (2010), *J. Chem. Eng. Data*, DOI **10.1021/je1001158**. NIST ThermoML original archive. Current downstream data copy excluded.
- Theologou, Mertz, Laurien and Starflinger (2022), horizontal sCO₂ tube heat transfer; Mendeley Data version 1 DOI **10.17632/4mvk4nxrkz.1**, CC BY 4.0.
- Zhang et al. (2022), sodium/CO₂ PCHE source, DOI **10.3389/fenrg.2022.835224**.
- Wright et al., Sandia report **SAND2010-0171**, compressor development, measured figures separate from predicted design table.
- Kim et al. (2019), *Int. J. Heat Mass Transfer*, DOI **10.1016/j.ijheatmasstransfer.2018.11.075**; Eq.24 ambiguity remains open.
- HZDR PCHE archive, DOI **10.14278/rodare.3928**, numerical studies and cost sensitivity, not measured CARBOSOLA validation.
- JCGM 100:2008 (GUM), DOI **10.59161/JCGM100-2008E**; JCGM 101:2008 Monte Carlo supplement, DOI **10.59161/JCGM101-2008**.

These references are included for provenance and scientific context; the exact implemented expressions and any original-author fit-domain restrictions must be checked against the cited source documents, not extrapolated from a shortened report table.

### 33.3 Unmerged and historical GitHub references

| Resource | Interpretation |
|---|---|
| [Draft PR #21](https://github.com/Open-Energy-Methods/sco2-braytonbench/pull/21) | Historical comprehensive 5 Nov research report; deliberately not rewritten here |
| [Draft PR #19](https://github.com/Open-Energy-Methods/sco2-braytonbench/pull/19) | Kim original-source interpretation and same-station H1d work; not in main |
| [Issue #20](https://github.com/Open-Energy-Methods/sco2-braytonbench/issues/20) | Kim empirical Eq.24 / Table 4 source discrepancy |
| [Issue #27](https://github.com/Open-Energy-Methods/sco2-braytonbench/issues/27) | ThermoML source-data rights and historical Git reuse |
| [Issue #28](https://github.com/Open-Energy-Methods/sco2-braytonbench/issues/28) | Named qualified independent reviewer / release-signoff gate |
| [Main integrated Actions #42266275348](https://github.com/Open-Energy-Methods/sco2-braytonbench/actions/runs/42266275348) | 20/20 successful integrated-main software CI |

### 33.4 Data-rights and source-of-truth hierarchy

**Highest priority:** original full source and explicit licence/certificate; public measurements with source-data dictionaries; signed lab records; independent numerical derivations.

**Intermediate:** project source inputs and instrumented logs; code/tests/CI tied to an immutable SHA; source-author equations and explanatory papers.

**Lower authority for external physical claims:** synthetic examples, internal model predictions, demonstration plots, project proposals, unmatched literature headlines and AI-assisted editorial interpretation.

When numbers conflict, use the original source and a traceable difference ledger. Do not silently overwrite source observations or claim that the repository independently settled an ambiguity solely through a lower residual.

## 34. Final preservation statement and handover

### 34.1 What this report preserves

This report joins the project's prior G0–G3.5 physical and data-source reconstruction with the subsequently integrated WP0–WP5 development sequence and the current source-rights cleanup. It records governing equations, real numerical benchmark values, table denominators, fit-domain limitations, design/control assumptions, uncertainty categories, provenance, executable tests, CI evidence, and the remaining independent scientific/reuse approvals.

It does **not** turn an unmerged exploratory branch into shipped functionality, a numerical property-library test into a field experiment, a drafted email into rights-holder permission, or a thermal-wall PI demonstration into a full transient turbine controller.

### 34.2 Defensible current status sentence

> At 6 November 2026, sCO₂-BraytonBench is an **integrated, CI-verified alpha research-software framework (0.5.0a0)** for recuperated real-fluid Brayton thermodynamics, finite-source and installed-UA heat-transfer analysis, with analytically verified synthetic thermal-wall dynamics, an energy-conserving sampled bypass/PI demonstrator, prospective measurement/uncertainty protocols, and independently replayed wheel/source-distribution evidence. The project is **not an experimentally validated CARBOSOLA dynamic plant model** and its formal v1.0 publication remains pending external qualified review and historical third-party data-rights determination.

### 34.3 Instructions to the next maintainer or reviewer

Verify the referenced SHA and successful CI **first**. Read the release contract and rights ledger **before** publishing an archive. Keep original experimental source transformations distinct from toy fixtures, and review negative stratification and out-of-domain results rather than deleting them. Do not impose a new set of assumed UAs or controller parameters as if they were calibrated.

For future experimental work, the first high-value contribution is **independently measured and traceable source/CO₂/coolant/wall transients** with clear P&ID and covariance—not a new arbitrary correlation. For software v1.0, the remaining external permissions/review must be genuinely completed and documented at an immutable commit.

### 34.4 Document maintenance rule

Do not rewrite this dated report in place to make future work appear to have existed on 6 November. Create a new dated report/release record referencing this one, and update a lightweight “latest report” pointer in the repository README. Correct a discovered factual error with a source-supported erratum referencing the exact affected text and commit rather than silently changing numerical claims.

**End of comprehensive report.**

