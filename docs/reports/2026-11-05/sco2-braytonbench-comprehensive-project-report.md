---
title: 'sCO₂-BraytonBench'
subtitle: 'Comprehensive Research, Engineering, Verification and GitHub History Report'
author: 'Open Energy Methods — research record'
date: '5 November 2026'
lang: en-GB
---

# Contents

*Document control and reading instructions* and *Executive assessment* precede the 24 numbered technical sections. Headings are also available through the Word navigation pane.

| Sections 1–12 | Sections 13–24 |
|---|---|
| **1** — Project origin, identity and scope | **13** — Lei water-correlation negative transfer result |
| **2** — Software architecture and conventions | **14** — Original Kim (2019) CO₂ model recovery |
| **3** — GitHub chronology and PR consolidation | **15** — H1d numerical solver and heldout controls |
| **4** — Friedman–Rapp model comparison | **16** — H1d exact common-station final audit |
| **5** — CO₂ property and measured-density verification | **17** — Independent physical validation sources |
| **6** — G3 finite waste-heat source screening | **18** — Verification and CI evidence |
| **7** — G3.1 fixed heater UA | **19** — Uncertainty and risk register |
| **8** — G3.2 coupled heater/cooler UA | **20** — Stage-gate status |
| **9** — G3.3 reference properties and mesh | **21** — Research roadmap and acceptance criteria |
| **10** — G3.4 external-source intake and anomalies | **22** — Reproduction instructions |
| **11** — G3.5 H1a Stuttgart experimental baseline | **23** — Citations and source-of-truth index |
| **12** — G3.5 H1b Bishop/Jackson correlations | **24** — Final preservation statement |

# Document control and reading instructions

| Field | Recorded value |
|---|---|
| Report classification | Comprehensive technical **historical and current-state reference**, not a validation certificate |
| Project | **sCO₂-BraytonBench** (Python package `sco2-braytonbench`) |
| Repository | <https://github.com/Open-Energy-Methods/sco2-braytonbench> |
| Maintainer and software attribution | Open Energy Methods; `CITATION.cff` names Abhijith Sivaprasadan |
| Report evidence cut-off | 5 November 2026, after GitHub Actions run **42058735222** completed |
| Package version | `0.5.0a0` / **0.5.0-alpha research reconstruction**, not an industrial release |
| Main integrated baseline | `217bb27b71a2162c0a75e4e1c3f521b0073a8318` |
| Latest H1d branch commit examined | `cf170a07a4e02d190d03c986f103f642aea4ca59` |
| Active research branch | `feat/g35d-kim2019-original-equation-benchmark` |
| Active pull request | [#19 — Kim 2019 source-equation audit](https://github.com/Open-Energy-Methods/sco2-braytonbench/pull/19): **OPEN / DRAFT / NOT MERGED** |
| Main integration | [PR #18](https://github.com/Open-Energy-Methods/sco2-braytonbench/pull/18): **MERGED** |
| Latest H1d verification | [GitHub Actions run 42058735222](https://github.com/Open-Energy-Methods/sco2-braytonbench/actions/runs/42058735222): **15 of 15 jobs successful** |
| Most important open issue | [Issue #17](https://github.com/Open-Energy-Methods/sco2-braytonbench/issues/17), original Kim CO₂ model parity and validation |
| Data and software licences | Repository: **BSD-3-Clause**; reused Stuttgart research dataset: **CC BY 4.0**; copyright on original articles preserved |
| Publication / DOI status | No additional release, tag or DOI was issued as part of the audited H1d work |

**Reliability convention.** This report distinguishes: **(A) executed GitHub CI or machine-generated result**, **(B) version-controlled implementation or test specification**, **(C) article-author result quoted from literature**, **(D) researcher interpretation, extrapolation or decision**, and **(E) proposed but not completed work**. A unit test passing is never described as experimental validation of a plant. All numerical inputs labelled *illustrative*, *synthetic* or *assumed* remain just that, even when the calculations use real-CO₂ thermophysical properties.

**Version control convention.** Unless a section explicitly says otherwise, G0–H1c records discussed here are on integrated **`main`**. Kim H1d additions are on **draft PR #19 only**, not on `main`. Older documents in the repository sometimes describe their own historical “not yet implemented” state; this report resolves that temporal ambiguity without rewriting the historical event.

**Purpose.** This is a detailed preservation report: what questions motivated the work, the exact engineering models added, how experiments and sources were screened, which computations were actually run, the observed numerical outputs, the mistakes detected, the changes made, what was and was not proven, and the shortest defensible path forward. It is intended to remain useful even if project branches, individual workflow artifacts or informal conversations are no longer readily accessible.

# Executive assessment

The project has progressed from an **unavailable historical v0.5 software archive** to a reproducible, separately packaged and CI-tested Python research platform for **steady-state recuperated supercritical-CO₂ Brayton cycles** and **single heated-tube heat-transfer model benchmarking**. It has a functioning six-state thermodynamic core, component heat-exchanger/stream models, optional CoolProp real-fluid properties, fixed-installed-UA operating-point inversions, finite heat-source/coolant constraints, reference-property and friction utilities, and a carefully partitioned experimental heat-transfer evaluation pipeline.

The most defensible accomplishments are methodological and computational, not a declaration of achieved industrial predictive accuracy. The **49-point independent experimental density comparison** showed small residuals at the recorded conditions. The **Friedman–Rapp 2016 conceptual-cycle** comparison reproduced aggregate efficiency to within 0.07544 percentage points after heat-input normalisation, while showing why that closeness does not identify the original complex EES model. The finite-source G3 study demonstrated how maximising recovered **net shaft power** differs from maximising **cycle thermal efficiency**. G3.1 and G3.2 solved coupled, fixed-installed heater and cooler UA equations with conservation checks. G3.3 improved sensible-stream properties and demonstrated narrow component segmentation sensitivity.

The more consequential experimental research started with the **Stuttgart Theologou et al. 2022** horizontal sCO₂ heated-pipe dataset: 54 original experiment IDs, 2,508 axial records, and 2,398 experimentally reduced local heat-transfer coefficients (HTCs). Its original data, 18 nominal families, top/middle/bottom orientations, quarantined anomalous run and fixed four-family holdout split were preserved. Uncalibrated forced-convection baselines were poor; near-wall property corrections improved the errors but remained insufficient; source-faithful transfer of an orientation-dependent water correlation failed badly; and the later Kim (2019) CO₂-specific models exposed both published-equation ambiguity and domain-transfer problems.

**The decisive last-stage quantitative result** is the final [three-way common-support audit](https://github.com/Open-Energy-Methods/sco2-braytonbench/actions/runs/42058735222/artifacts/13431221211). For **1,275 identical successfully solved HB/HT stations** (272 in the held-out families), flux-driven local HTC MAPE was **33.89% for Jackson–Hall**, **54.39% for Kim semi-empirical**, **45.73% for an explicitly unverified empirical exponent-placement hypothesis**, and **29,622,281.81% for the empirical formula interpreted literally as printed**. The tested original Kim correlations did **not** outperform the Jackson–Hall comparator on this matched selection. This does not overturn the Kim authors’ own reported results: all Stuttgart heat fluxes exceed the original Kim paper’s published fitting range and some inverse problems failed to converge, so it is an **out-of-fit-domain stress test**, not original-study reproduction or universal correlation ranking.

The project has **not** become an HZDR CARBOSOLA digital twin, validated industrial PCHE model, source-faithful 400-equation Friedman–Rapp EES reproduction, experimentally calibrated compressor/turbine-map model, transient plant or PI/MPC system. Those remain explicitly outside the verified work. The correct status is **substantial research-software implementation and evidence generation, with material scientific validation gates still open**.

## Snapshot: what is done, what is open

| Area | Completed record | Interpretation / still open |
|---|---|---|
| Package foundation | Six-state cycle, sources, tests, CI, licensing and provenance | No exact import of earlier unavailable v0.5 archive |
| CO₂ property evidence | 49 directly measured densities compared to CoolProp 8.0.0 | Density subset only; full near-critical h/s/cp and uncertainty parity open |
| 2016 literature comparator | 12-state conceptual pressure network and aggregate comparison executed | The detailed ~400-equation EES source model is not identifiable |
| G3 source-constrained screening | 20-point hypothetical finite-source grid, 16 base-feasible, two objectives | Not a global optimisation or industrial source model |
| G3.1 installed heater | Fixed-UA heater/bulk source and T4 solved; conservation tests | Synthetic UA and machine assumptions; not an identified piece of hardware |
| G3.2 installed heater + cooler | Coupled T1/T4 and finite coolant; two source perturbations | Coarse HX discretisation and illustrative coolant/air properties |
| G3.3 property/hydraulic components | NIST dry-air, CoolProp water, Darcy/Haaland module, mesh checks | Pipe geometry not attached to actual equipment; full dual-UA mesh gate open |
| G3.4 evidence intake | Seven source classes, uncertainty provenance and anomaly log | Sodium PCHE/turbomachinery/HZDR datasets not validated against the cycle |
| G3.5 H1a | Stuttgart data, fixed groups, Gnielinski/DB evaluation | Errors 150.15% / 119.60%; poor predictive description |
| H1b | Bishop/Jackson conditional and flux-inverse comparisons | 46.40% / 49.47% on different eligible subsets; high HT error |
| H1c | Lei HB/HT implementation and negative CO₂ transfer test | 631.72% MAPE; water-source domain inappropriate |
| H1d | Original Kim source recovered; three variants implemented and exercised | Eq.24/Table 4 ambiguity, source-domain excess, incomplete roots; no original parity |
| Git hygiene | Nine dependent draft PRs consolidated through merged PR #18 | Draft H1d PR #19 remains unmerged by scientific decision |
| Latest CI | 15/15 successful on H1d commit `cf170a0` | CI establishes executable software gates, not calibrated physical validity |

# 1. Project origin, identity and research boundaries

## 1.1 Why an independent repository was necessary

The work started from the need for an **auditable open-source methods test bench** for supercritical-CO₂ Brayton-cycle thermodynamics and, eventually, experimental heat-transfer, component performance, off-design behaviour and control. The previously discussed executable “v0.5” archive was **not available for direct import**. Rather than pretend continuity with unavailable binaries or models, the codebase was explicitly designated a **reconstruction** from earlier v0.4 specifications and accessible literature/source evidence. The presence of code, pressure mappings or matching efficiency numbers must not be represented as recovery of an author’s complete original programme.

The repository was established under **Open Energy Methods** as `Open-Energy-Methods/sco2-braytonbench`, with a conventional `src/` Python package, test suite, GitHub Actions, reference/data folders and dedicated research documents. Its packaging metadata requires Python **3.10 or later**, records the version `0.5.0a0`, and exposes optional `co2` and `test` extras. The testing workflow uses Python **3.11 and 3.12**, and the real-fluid runs pin **CoolProp 8.0.0**, `HEOS::CO2`.

The repository is licensed BSD-3-Clause, with `CITATION.cff` prepared for software attribution. A licence and citation file make the work citable *when properly released*; they do not mean a DOI has been minted or a journal result independently accepted. The old `CHANGELOG.md` still records only the initial foundation, so this comprehensive report also functions as a consolidated retrospective milestone ledger.

## 1.2 Principal research questions

The research programme is driven by related but separate questions:

1. **Thermodynamic arithmetic.** Can a recuperated closed CO₂ cycle satisfy consistent pressure, energy, property and component relations in SI units, against independent analytical tests and selected literature references?
2. **Heat-source realism.** What changes when the heat source has finite flow and temperature, stack and pinch limits, and a fixed physical exchanger rather than an unconstrained imposed heater duty?
3. **Off-design coupling.** Can the model solve installed-heater and installed-cooler constraints *together*, and what illustrative thermal changes follow from gas or coolant perturbations?
4. **Component fidelity.** Can realistic dry-air/water property services and geometry-based friction utilities improve traceability without silently inventing equipment dimensions or maps?
5. **Experimental validation.** How do published HTC correlations compare against a real near-critical horizontal CO₂ experimental campaign, with correct wall orientation, original source uncertainty, whole-run quarantine, fixed group holdouts and explicit model applicability?
6. **Future model hierarchy.** What independent evidence would be required before extending a correlation to actual PCHE geometry, fitted UA, real turbomachinery, transient fluid inventory, control and economics?

These are distinct gates. One should not jump from a successful local property test to a validated plant, or from a favorable correlation MAPE to a legitimate PCHE design correlation.

## 1.3 Deliberate nonclaims

The current project **does not** claim that it owns or reproduces CARBOSOLA rig sensor records, hardware geometry, compressor and turbine maps, actual industrial heat-source composition, whole-cycle experimental state tables, heat-exchanger wall conduction or fouling, transient CO₂ inventory dynamics, shaft-speed dynamics, safety interlocks, actuator constraints, PI/MPC performance, export electrical power, industrial cost optimisation or complete Mohagheghi–Kapat 2014 genetic-algorithm outcomes. It does **not** present one author’s CFD-predicted data as measured laboratory quantities. Future work may use relevant outside datasets under their documented permissions, but source category and reuse rights must always be preserved.

The quantitative powers throughout G3–G3.3 are **net shaft powers** in illustrative steady calculations, not electricity exported through a measured generator and auxiliary system. The readme’s warning that a fixture fluid is not CO₂ is a standing project rule.

# 2. Software architecture and engineering conventions

## 2.1 Physical abstraction and state accounting

The foundational cycle is a six-state **recuperated closed Brayton-cycle reduced model**. It represents compressor, turbine, recuperator, main heater and cooler, with idealised but explicit pressure drops and machine isentropic efficiency relations. A set of state temperatures, pressures, enthalpies and entropy is calculated using either a deliberately simple analytical-fluid fixture (for exact regression equations) or pinned real-CO₂ properties. Compressor work is positive consumption; turbine work is positive production; net shaft work is their difference. Heat transfer and recirculating recuperator duty are accounted for without creating or destroying energy.

An especially important naming rule is that the project’s internal **six-state model numbering is not Friedman–Rapp’s literature Figure 2b 12-state numbering or the full EES Figure 4 18-state numbering**. Source-specific pressure and state ledgers are maintained separately to avoid false matches when reading a paper’s Table 2/Table 3.

The core energy relationship is:

```text
Q_heater - Q_cooler - (W_turbine - W_compressor) = 0
eta_thermal = (W_turbine - W_compressor)/Q_heater
```

These balances are **algebraic/conservation constraints**. They are essential but insufficient evidence of physical accuracy. An unphysical correlation can still satisfy a numerically closed energy balance.

## 2.2 Thermophysical and numerical conventions

- Absolute pressure: **Pa**; temperature: **K**; specific enthalpy: **J/kg**; power and heat rate: **W**; heat-exchanger conductance `UA`: **W/K**; local HTC: **W/(m² K)**; wall heat flux: **W/m²**.
- `HEOS::CO2` is the reference real-fluid backend for computed CO₂ states. Analytic fixture tests do not imply CoolProp/CO₂ was called.
- The gas source and coolant may have analytical sensible-property models; source EOS and coolant EOS are independent of the CO₂ circuit.
- Segmented counterflow heat exchangers check local approach temperatures and the possibility of interior temperature pinch. An imposed UA or recuperator effectiveness must not be confused with a measured exchanger geometry.
- Internal CO₂ pressure losses begin as user-supplied fixed absolute drops, with an optional uncalibrated flow-scaled scenario. The later `hydraulics.pipe_loss` utility is not automatically wired to installed equipment without actual length, diameter, roughness and minor loss constants.
- CoolProp and REFPROP absolute enthalpy may use different reference conventions. The Stuttgart pipeline anchors a run at its measured inlet temperature and pressure, and applies the published **within-run enthalpy increment**; it does not assume equality of absolute references.
- Numeric root searches use explicit brackets/domains, energy residuals and finite tolerances; uniqueness beyond sampled brackets is not claimed.

## 2.3 Repository components and intended separation of concerns

| Directory or module | Responsibility |
|---|---|
| `src/sco2_braytonbench/core.py`, `cycle.py` | Cycle states, pressure/energy bookkeeping and main thermodynamic calculations |
| `properties.py`, `reference_streams.py`, `streams.py` | Property interface, synthetic test fluid, reference fluid/sensible source streams |
| `exchangers.py`, `cooler.py`, `fixed_ua.py`, `coupled_plant.py` | Recuperator/heat-exchanger models, installed-UA inverses and finite sink coupling |
| `whr.py`, `offdesign.py`, `hydraulics.py` | Finite-source waste-heat screening, optional off-design assumptions, geometry-based pressure loss functions |
| `reference_cycle.py`, `references.py` | Source-specific Friedman–Rapp conceptual mappings and literature context |
| `stuttgart_correlations.py`, `lei_mixed_convection.py` | Source-aware experimental HTC baselines and Lei HB/HT transfer benchmark |
| `kim2019.py` (draft PR #19) | Kim (2019) thermophysical averages, orientation-specific source equations and wall inversions |
| `data/reference/` | Measured density source and verified coefficient/provenance registry |
| `data/validation/stuttgart/` | Preserved reduced external-experiment index and axial profiles |
| `scripts/` | Executed reference diagnostics, engineering screens and H1a–H1d evaluations |
| `tests/` | Analytical, source-integrity, reference-property, numerical and report consistency tests |
| `docs/` | Technical methods, numerical result reports, source audits, research gate decisions |
| `.github/workflows/ci.yml` | CI matrices, experimental reproducibility jobs and per-milestone artifacts |

Not every module listed has an industrial-level API stability guarantee. Interfaces, scientific meaning and applicability metadata matter more at the current research stage than premature public API promises.

# 3. Development chronology and GitHub provenance

## 3.1 The nine-stage stacked research chain

The work accumulated on **nine dependent draft PRs**. This allowed early scientific layers to evolve separately but eventually created a fragile dependency stack: reviewers could not treat a downstream PR as independent of its unpublished upstream base; docs could fall out of sync, and repeated merge operations could obscure the experimental history. The consolidation audit recorded a development head **38 commits ahead of the prior `main`, 0 behind**, touching **96 files**, with approximately **11,221 added and 20 removed lines** before the final source-integration additions.

| Research order | Original PR | Principal contribution | Verified example CI run |
|---|---|---|---|
| 1 | [#1](https://github.com/Open-Energy-Methods/sco2-braytonbench/pull/1) | Reconstructed v0.5-alpha foundation; thermodynamics; measured-density and FR2016 comparison | [41995718964](https://github.com/Open-Energy-Methods/sco2-braytonbench/actions/runs/41995718964) |
| 2 | [#6](https://github.com/Open-Energy-Methods/sco2-braytonbench/pull/6) | G3 finite industrial waste-heat-source screening and objective comparison | [42000144494](https://github.com/Open-Energy-Methods/sco2-braytonbench/actions/runs/42000144494) |
| 3 | [#8](https://github.com/Open-Energy-Methods/sco2-braytonbench/pull/8) | G3.1 installed heater UA and coupled turbine inlet state | [42003355229](https://github.com/Open-Energy-Methods/sco2-braytonbench/actions/runs/42003355229) |
| 4 | [#9](https://github.com/Open-Energy-Methods/sco2-braytonbench/pull/9) | G3.2 dual installed heater/cooler UAs and finite coolant | [42007026597](https://github.com/Open-Energy-Methods/sco2-braytonbench/actions/runs/42007026597) |
| 5 | [#10](https://github.com/Open-Energy-Methods/sco2-braytonbench/pull/10) | G3.3 NIST dry-air, real water, hydraulic friction, mesh sensitivity | [42011217580](https://github.com/Open-Energy-Methods/sco2-braytonbench/actions/runs/42011217580) |
| 6 | [#12](https://github.com/Open-Energy-Methods/sco2-braytonbench/pull/12) | G3.4 source registry, experimental/predicted classification, anomaly handling | [42018591734](https://github.com/Open-Energy-Methods/sco2-braytonbench/actions/runs/42018591734) |
| 7 | [#13](https://github.com/Open-Energy-Methods/sco2-braytonbench/pull/13) | G3.5 H1a full Stuttgart data and original Gnielinski/Dittus–Boelter baselines | [42032549353](https://github.com/Open-Energy-Methods/sco2-braytonbench/actions/runs/42032549353) |
| 8 | [#15](https://github.com/Open-Energy-Methods/sco2-braytonbench/pull/15) | G3.5 H1b Bishop and Jackson–Hall wall-property model audit | [42036923202](https://github.com/Open-Energy-Methods/sco2-braytonbench/actions/runs/42036923202) |
| 9 | [#16](https://github.com/Open-Energy-Methods/sco2-braytonbench/pull/16) | G3.5 H1c published Lei HB/HT transfer **negative result** | [42041906147](https://github.com/Open-Energy-Methods/sco2-braytonbench/actions/runs/42041906147) |

All nine draft heads had passing GitHub Actions runs and were reported mergeable at the audit. This establishes **software-execution history**, not acceptance of every scientific model. The historical [consolidation audit](https://github.com/Open-Energy-Methods/sco2-braytonbench/blob/main/docs/PR_CONSOLIDATION_AUDIT.md) records the exact dependency sequence and CI links.

## 3.2 Consolidation and source recovery: PR #18

Rather than issuing nine unrelated merges, the development commits were integrated into [PR #18](https://github.com/Open-Energy-Methods/sco2-braytonbench/pull/18), targeting `main`. The original incremental history was preserved using a **merge commit**, not squashed into an unexplained monolith. The earlier #1 PR was automatically associated with the merged history, while the other stacked drafts were closed as **superseded**, not falsely presented as nine separate independently reviewed merges. The consolidated main commit is **`217bb27b71a2162c0a75e4e1c3f521b0073a8318`**.

An additional milestone was folded into that integration: the complete original **Kim et al. (2019) 12-page PDF** was obtained, hash-audited, visually checked for nomenclature, experiment and formula tables, and its Table 4 coefficients transcribed to machine-readable JSON. The article itself was **not uploaded to the public repository**. The source-only audit explicitly did **not** implement the Kim model at that point. The post-merge main CI [42049395268](https://github.com/Open-Energy-Methods/sco2-braytonbench/actions/runs/42049395268) is recorded as successful.

This consolidation is important for reproducibility: `main` now contains a unified baseline of the G0–G3.5 H1c methods. H1d can be reviewed against a stable and appropriately labelled source baseline, rather than against transient dependent feature branches.

## 3.3 New H1d research PR #19 and subsequent hardening

The subsequent [draft PR #19](https://github.com/Open-Energy-Methods/sco2-braytonbench/pull/19) introduces **16 changed files** at the latest examined head, including executable `kim2019.py`, the Stuttgart H1d driver, three-way summary and common-support audit, additional independent source-triage documentation and tests. Its head commit is **`cf170a07a4e02d190d03c986f103f642aea4ca59`** and the PR had **14 commits** in the examined metadata. It remains **open, mergeable according to GitHub, and marked DRAFT**, deliberately unmerged.

Development proceeded through an initial completed run, documentation and numerical-convergence additions, and further changes that enforced common station IDs. The incremental CI history contains **temporary failing runs** during those edits. The decisive visible test failure in a recent run was a deliberately synthetic regression fixture expecting a Jackson mean absolute error of **30%** where its own two values were 10% and 40%; the correct mean was **25%**. The fixture assertion was corrected in `cf170a0`. That was a test-expected-value error, not evidence of a failed real-CO₂ physical root. The final exact-head [run 42058735222](https://github.com/Open-Energy-Methods/sco2-braytonbench/actions/runs/42058735222) later completed **15/15 successful jobs**.

The later common-support analysis materially improved the credibility of the reported cross-model comparisons by avoiding an otherwise misleading ranking based on different successful root sets. The final CI summary artifact contains **eight files**: the earlier scientific summary `.md/.json/.csv` and logarithmic error SVG, plus a source-ID audited common-support `.md/.json/.csv` and pointwise error CSV. These files were **generated as CI artifacts**, not automatically committed to `main`.

## 3.4 Governance choices preserved

- **No release / DOI / Zenodo action** was undertaken for the H1d research branch.
- **No original copyrighted Kim paper binary** was redistributed to GitHub.
- **No author/researcher email** was sent as part of the reported H1d milestone.
- The full original Stuttgart source value at the anomalous experiment was **not silently changed**.
- Earlier experimentally incorrect or scientifically negative correlation outcomes were retained as research evidence, rather than removed or relabelled as successful plant validations.
- Original nominal-family heldouts were not re-split after seeing model errors, and Kim empirical variant coefficients were not tuned on Stuttgart results.
- Issues and documentation distinguish code-complete, physics-incomplete and source-recovery-open status rather than using a single ambiguous “done” label.

# 4. G0/G2: Friedman–Rapp literature benchmark and source identifiability

## 4.1 Scope of the 2016 source

The principal historical source was **Friedman and Rapp (2016)**, *Parametric Analysis of SCO2 Power Cycles Operating at Moderate Temperatures*, 5th International Symposium on Supercritical CO₂ Power Cycles, Paper 051. The original paper is linked at <https://www.sco2symposium.com/papers2016/SystemModeling/051paper.pdf>; a conference presentation also exists. The published **Figure 2b** describes a conceptual 12-point recuperated pressure/energy network. Its **Figure 4** is a more complex plant model, reportedly consisting of approximately **400 Engineering Equation Solver (EES) equations**, a PWR source, separate main and compressor turbine machinery, a compressor motor and generator, source/sink paths, CO₂ states 1–18, and additional P1–P3/C1–C2 external states. Reported discretisation includes **30 recuperator sections**, **10 IHX sections**, and a presentation reference to **20 precooler sections**.

The paper's conceptual source inputs include **T1 = 550 K**, **P1 = 30 MPa**, **turbine isentropic efficiency 0.90**, **compressor isentropic efficiency 0.85**, and **recuperator effectiveness 0.925**, together with a table of component and pipe pressure drops. The analysis was carried out using an EES property library and an **IIR reference convention**. Absolute enthalpy and entropy values may therefore differ from default CoolProp states; physical **differences** across transitions are the defensible comparator without reference-state harmonisation.

The project explicitly reconstructed a **12-state conceptual counterpart**, not the full Figure 4 EES code. Pressure and source labels were kept separate from the six-state standalone cycle model. The low-temperature source condition was mapped to **T7**, and the compressor suction pressure to **P8**, a documented paper-grounded reading. Counterfactual adjacent-state label choices were evaluated to estimate indexing sensitivity, not represented as equally author-endorsed source interpretations.

## 4.2 Source-to-model numerical comparison

The independently executed conceptual model used CoolProp 8.0.0, approximately 30 counterflow recuperator segments, real-fluid local property calls, adiabatic isenthalpic piping pressure drops, and source-imposed aggregate heater input to normalise calculated powers.

| Variable | Source paper Table 3 | BraytonBench conceptual calculation |
|---|---:|---:|
| Heat input | 100.200 MW | 100.200 MW **normalisation** |
| Turbine work | 38.080 MW | 38.152614 MW |
| Compressor work input | 13.650 MW | 13.798208 MW |
| Cooler rejection | 75.800 MW | 75.845593 MW |
| Net output | 24.430 MW | 24.354407 MW |
| Cycle efficiency | 24.381238% | **24.305795%** |

The efficiency difference is **−0.075442 percentage points**; the project reports specific input heat approximately **243.809207 kJ/kg**, specific net work **59.259766 kJ/kg**, and conceptual first-law residual **5.82×10⁻¹¹ J/kg**. The modelled recuperator minimum approach was **5.12389 K**. These numbers form a traceable consistency check. Crucially, the 100.20 MW heat-input value is **forced to match the source for scaling**; the resulting turbine/net MW values are **not independently inferred installed turbine capacities**.

## 4.3 Source condition and discretisation sensitivity

Segment counts of **15 / 30 / 60** yielded identical reported thermal efficiency **24.305795%**, while inferred recuperator `UA` per unit mass flow changed **9384.950 → 9398.771 → 9402.247 W/K per (kg/s)**. Between 30 and 60 segments the change was approximately **0.037%**, but imposed effectiveness can make heat duty insensitive at that one operating point. This is **not** proof of general near-critical mesh independence.

Changing the assumed low-side temperature by **−1 K** raised efficiency to **24.483395%**; a **+1 K** shift reduced it to **24.121585%**. The total 2-K contrast, **0.3618 percentage points**, is far larger than the −0.07544 percentage-point paper/model efficiency difference. A ±1% low-side pressure perturbation gave efficiency approximately **24.305776% / 24.308721%**. The counterfactual neighbouring point-label mappings gave approximately **24.2907–24.3058%**, a spread of **0.01510 percentage points**.

Thus the project used a close nominal paper comparison to motivate additional **identifiability and sensitivity tests**, rather than to claim the published detailed model had been recovered.

## 4.4 Original-source recovery limitation

Searches of public proceedings, code and scholarly indexes **did not recover the original `.EES` programme** or the complete source Figure 4 state tables. The user-supplied original 21-page PDF contained no embedded code attachment. The detailed paper describes branches, maps, heat sources and iterative initialization that are not uniquely constrained by published aggregate Table 3 numbers. Even a perfect fit to all aggregate powers would not identify the separate compressor/main turbine flow split, component efficiencies, source model and non-reported state table.

A blank original-state data request schema was created at `data_requests/fr2016_table3_reference_template.csv`. It is explicitly a template, **not an observed dataset**. An independent Figure 4 reproduction would require a permission-cleared original EES file or a much fuller state and loss ledger. The detailed [FR2016 source recovery audit](https://github.com/Open-Energy-Methods/sco2-braytonbench/blob/main/docs/FR2016_ORIGINAL_MODEL_RECOVERY.md) documents this negative source search and the minimum defensible request specification.

**Gate decision:** G0 conceptual source mapping is partial and G2 full source-model reproduction is **open**. The reduced conceptual calculation is a legitimate literature consistency test, not a source-equivalent cycle simulator.

# 5. G1: CO₂ property verification and independent experimental density

## 5.1 Property services and why reference values are not all independent

The code first checked CoolProp real-CO₂ properties against NIST REFPROP guide values and independent software-rendered h/s/density reference points, including near-critical behaviour and thermodynamic consistency. These are useful implementation checks, but default CoolProp and traditional REFPROP are strongly linked through the **Span–Wagner** underlying CO₂ thermodynamic formulation. Agreement of two implementations of essentially the same EOS is not a measurement-based validation of the EOS. The project therefore deliberately sought **independent measured P–ρ–T data**.

## 5.2 Mantilla et al. (2010): measurement provenance

The dataset from **Mantilla, Cristancho, Ejaz and Hall (2010)**, *P–ρ–T Data for Carbon Dioxide from (310 to 450) K up to 160 MPa*, *Journal of Chemical & Engineering Data* 55, 4611–4613, DOI [10.1021/je1001158](https://doi.org/10.1021/je1001158), was sourced through [NIST ThermoML](https://trc.nist.gov/ThermoML/10.1021/je1001158.json). The paper reports measurements with a **single-sinker magnetic suspension densimeter**. The retained machine files are `data/reference/mantilla2010_thermoml_density.csv` and `mantilla2010_provenance.yaml`.

**49 observed densities** at **310, 350, 400 and 450 K** and approximately **0.999–159.844 MPa** were compared with pinned CoolProp 8.0.0 at the **measured P and T**. The measurement values were not fit or generated from the software being evaluated. A direct relative residual was calculated for each state as `(rho_CoolProp - rho_experimental)/rho_experimental`, then aggregated to signed mean, RMS and maximum absolute errors.

## 5.3 Executed measured-density results

| Quantity | Completed result |
|---|---:|
| Original measured states compared | **49** |
| Mean signed density residual | **−0.005608%** |
| RMS relative residual | **0.034731%** |
| Maximum absolute relative residual | **0.090241%** |
| Final regression-screen maximum threshold | **0.2%** |
| Final regression-screen RMS threshold | **0.1%** |
| Tightened regression CI | [41993973281](https://github.com/Open-Energy-Methods/sco2-braytonbench/actions/runs/41993973281), all **3 jobs passed** |

The per-isotherm record is:

| T (K) | Number of points | Maximum absolute residual | RMS residual |
|---|---:|---:|---:|
| 310 | 12 | 0.04660% | 0.02968% |
| 350 | 9 | 0.02784% | 0.01646% |
| 400 | 20 | 0.06498% | 0.03414% |
| 450 | 8 | 0.09024% | 0.05336% |

The worst reported residual was near **450 K and 122.193 MPa**. The original paper’s density measurement uncertainty description is around or below **0.03%** over its stated conditions. The observed largest discrepancy of **0.09024%** exceeds that quoted measurement uncertainty; it does **not** automatically invalidate the data, but prevents claiming all property residuals are measurement-uncertainty limited. The ThermoML numeric uncertainty column was retained **without silently assuming it was a 1σ standard deviation, a 95% confidence width or percentage**. The code thresholds were chosen as reproducibility screens and are **not calibrated uncertainty budgets**.

This phase also distinguished the 2026 NIST alternative CO₂ EOS, Lemmon–Harvey–Hellmann NISTIR 8608, as a future research candidate. A REFPROP-readable fluid file was known, but **no alternate EOS comparison was executed** because it is not automatically an independent `HEOS::CO2` backend.

## 5.4 Property evidence limit

The measured-density validation is **narrow but genuine**: it uses external experimental density values. It is **not** an independent measurement validation of enthalpy, entropy, heat capacity, viscosity, conductivity, near-critical divergent derivatives, phase-boundary behaviour or installed plant operating points. Most of the 49 states are not immediately at the most difficult critical-region conditions. Thus **G1-E is partial**, while G1-A analytical conservation verification passed its declared tests.

The source-record [density decision document](https://github.com/Open-Energy-Methods/sco2-braytonbench/blob/main/docs/EXPERIMENTAL_DENSITY_DECISION.md) and [real-fluid evidence report](https://github.com/Open-Energy-Methods/sco2-braytonbench/blob/main/docs/EXPERIMENTAL_DENSITY_AND_IDENTIFIABILITY.md) preserve the exact numbers and caveats.

# 6. G3: finite industrial waste-heat-source design screening

## 6.1 Motivation and departure from an imposed infinite heater

A recuperated sCO₂ cycle can display an attractive thermal efficiency while recovering relatively little of the sensible heat actually available in an industrial exhaust stream. Optimising **cycle efficiency** and **net recovered shaft power** are therefore not equivalent when source-gas mass flow, inlet temperature, minimum stack temperature and heat-exchanger pinch are finite. Mohagheghi and Kapat (2014), *Thermodynamic Optimization of Recuperated S-CO₂ Brayton Cycles for Waste Heat Recovery Applications*, provided a research motivation for separating these objectives. The work did **not** reproduce that paper’s specific REFPROP/genetic algorithm, RRC topology or fractional pressure-loss scheme.

The implemented G3 screen evaluates a prescribed **six-state recuperated real-CO₂** cycle across a small finite grid, computes heat exchanged with a gas stream that must actually cool, imposes stack and local heater approach checks, estimates the required gas-to-CO₂ heater UA, checks first-law feasibility and source exergy bounds, and ranks only the candidates satisfying the declared constraints. It does **not** yet solve a fixed installed exchanger equality: at this stage UA is a *sizing requirement* checked against a chosen maximum allowance.

## 6.2 Exact illustrative base assumptions

| Parameter | Independently selected modelling assumption |
|---|---:|
| Gas mass flow | **100 kg/s** |
| Gas inlet temperature | **760 K** |
| Constant gas sensible cp | **1100 J/(kg K)** |
| Minimum gas/stack exit temperature | **360 K** |
| Minimum local heater approach | **10 K** |
| Permitted heater UA sizing upper bound | **1.2 MW/K** |
| CO₂ low pressure and compressor inlet T | **8.5 MPa**, **310 K** |
| CO₂ turbine inlet pressure | **24 MPa** |
| Turbine / compressor isentropic efficiency | **0.90 / 0.89** |
| Recuperator imposed UA | **200 kW/K** |
| Cold recuperator / heater / hot recuperator / cooler pressure losses | **100 / 150 / 100 / 50 kPa** |
| Candidate turbine inlet temperatures | **550, 600, 650, 700, 770 K** |
| Candidate CO₂ mass flows | **20, 40, 70, 100 kg/s** |

The grid contains **5 × 4 = 20 candidates**. It is a transparent enumerated screen, **not** a mathematically global optimum, surrogate optimiser or plant set-point recommendation. The rejected 770 K cases specify turbine inlet temperatures hotter than the 760 K source inlet, which the finite-source model correctly rules infeasible.

## 6.3 Executed baseline selection and trade-off

There were **16 feasible** and **4 rejected** points under the base requirements.

| Performance / feasibility metric | Best sampled shaft-power candidate | Best sampled cycle-efficiency candidate |
|---|---:|---:|
| Turbine inlet T | 700 K | 700 K |
| CO₂ mass flow | **100 kg/s** | **20 kg/s** |
| Net shaft power | **8.109835 MW** | **1.621967 MW** |
| Cycle thermal efficiency | 25.2184% | **33.5039%** |
| Heater external heat absorbed | 32.1585 MW | 4.8411 MW |
| Cooler heat rejected | 24.0486 MW | 3.2192 MW |
| Gas leaving/stack temperature | 467.650 K | 715.990 K |
| Available sensible-source heat recovered | **73.087%** | **11.003%** |
| Recuperator minimum internal approach | 64.738 K | 4.627 K |
| Heater minimum local approach | 13.108 K | 60.000 K |
| Required heater UA | 923.866 kW/K | 40.528 kW/K |

The sample illustrates the intended system-level result: the efficiency winner runs much less CO₂ and leaves most heat in the exhaust. In contrast, the higher shaft-power candidate uses far more heat but requires a much higher cooler duty and heater conductance. The low 4.627-K recuperator approach of the efficiency candidate is already a warning that thermodynamic merit and feasible hardware approach may conflict.

## 6.4 Sensitivity to two additional illustrative limits

A second screen added a **cooler duty cap of 15 MW thermal** and a **minimum internal recuperator approach of 10 K**. These are user-selected hypothetical limits, not restrictions measured on an installed heat exchanger. Only **6 of 20** candidates then remained feasible, and both base-grid winners were rejected.

| Metric | Power winner under added constraints | Efficiency winner under added constraints |
|---|---:|---:|
| CO₂ turbine inlet T | 650 K | 700 K |
| CO₂ mass flow | 70 kg/s | 40 kg/s |
| Net shaft power | **4.983670 MW** | 3.243934 MW |
| Thermal efficiency | 25.8575% | **30.7281%** |
| Cooler thermal rejection | 14.2899 MW | 7.3130 MW |
| Recuperator minimum internal approach | 35.626 K | 19.698 K |
| Source heat recovered fraction | 43.804% | 23.993% |
| Stack gas exit T | 584.785 K | 664.028 K |

Thus the high-level objective trade-off is not sensitive merely to a change of numerical algorithm: it is sensitive to **whether the plant’s actually feasible heat sink, UA and local pinch requirements are represented**. Without defensible hardware constraints it would be premature to publish one “optimal cycle” design.

## 6.5 Segmentation check and limitations

The two original baseline winners were recomputed with **12, 24 and 48** heat-exchanger sections. The power candidate’s reported efficiency changed **25.218353% → 25.218877% → 25.219007%**. The efficiency candidate changed **33.503907% → 33.491661% → 33.488291%**. Required heater UA for the power candidate changed **923.866 → 922.637 → 922.326 kW/K** across those resolutions; its heater minimum approach changed only slightly. Net shaft power at fixed pressure, turbine inlet state, flow and machine efficiencies can be invariant **by construction**; that mathematical property does not prove grid convergence of an independent rated operating point.

The executed [G3 real-fluid screen](https://github.com/Open-Energy-Methods/sco2-braytonbench/blob/main/docs/G3_STEADY_SCREENING_RESULTS.md) and [Actions 41999222234](https://github.com/Open-Energy-Methods/sco2-braytonbench/actions/runs/41999222234) document four successful jobs, including two fixture suites (**136 passed, 6 optional skipped** each), **61** reference/EOS checks and **3** multi-point CO₂ waste-heat integration checks.

**Gate:** the physical idea and constrained steady software screen passed its defined numerical tests. It remained **G3 exploratory/partial**, because UA was a sizing inequality rather than a constant installed piece of hardware and no machine, pressure-loss or industrial gas/coolant maps had been obtained.

# 7. G3.1: fixed installed gas-heater UA

## 7.1 Why G3 was not a true off-design exchanger model

A prescribed turbine inlet temperature plus inequality `UA_required <= UA_max` permits many mathematically feasible points, but an installed heat exchanger without bypass or variable wetted area does not spontaneously reduce conductance merely because less heat is needed. G3.1 corrected this by **holding installed heater UA fixed** and solving for the actual turbine inlet temperature `T4` at the chosen source and flow conditions. Its root condition is:

```text
R_heater(T4) = UA_required(T4) - UA_installed = 0
```

The coupled calculation also solves the finite exhaust gas leaving temperature from gas sensible-energy conservation, uses a counterflow exchanger with local pinch checks, and enforces the associated CO₂ cycle and source-gas first laws. There is no fictional bypass, assumed active-area throttling or controller hidden in the equation.

## 7.2 Nominal calibration and executed perturbation

The **synthetic nominal** G3.1 setting used an 800 K gas inlet, gas flow 100 kg/s, cp 1100 J/(kg K), CO₂ flow 20 kg/s, low/high pressure 8.5/24 MPa, T1 = 310 K, turbine/compressor isentropic efficiencies 0.90/0.89, recuperator UA 200 kW/K and a selected nominal T4 = 650 K. The installed heater was sized from this very reference state as **UA = 21,783.3278627 W/K**. It is therefore an **inverse software design point**, not an independently identified measured exchanger.

| Output | Gas source 800 K | Gas source 810 K |
|---|---:|---:|
| Fixed installed heater UA | 21.783328 kW/K | 21.783328 kW/K |
| Solved turbine inlet T4 | **649.989014 K** | **658.953857 K** |
| Gas stack/exit T | 758.003237 K | 767.638266 K |
| Net shaft power | 1.4238615 MW | 1.4599094 MW |
| Cycle efficiency | 30.8218883% | 31.3299343% |
| Implied UA from solved state | 21.782025 kW/K | 21.782885 kW/K |
| Absolute UA residual | −1.303 W/K | −0.443 W/K |
| Relative UA error | 0.0059802% | 0.0020320% |
| Root evaluations / bisection iterations | 18 / 9 | 18 / 9 |

With the same installed UA and a **10 K hotter gas source**, solved turbine inlet temperature rises by approximately **8.964844 K**, and modelled net shaft power rises around **36.05 kW**. Those are **two independently solved steady states**, not a 10-K thermal transient, response time or gain estimate for a real control system.

The temperature root was accepted under `|UA_required−UA_installed|/UA_installed ≤ 1e−4` and final T4 width **≤0.03 K**. Separate tests check source gas energy and exergy, CO₂ conservation, stack temperature, positive local HX approaches and no-bracket rejection.

## 7.3 Independent analytical test

For an artificial constant-cp working fluid with zero recuperator UA, the coupled heater reduces to a classical **counterflow effectiveness–NTU relation**. Unit tests recover its closed-form result at multiple installed UAs, and the ideal-gas compressor is checked against a separate analytical isentropic relation. This is a meaningful mathematical root verification because the expected answer does not come from the production segmentation routine itself. It is still **not experimental CO₂ validation**.

[Actions run 42002609837](https://github.com/Open-Energy-Methods/sco2-braytonbench/actions/runs/42002609837) passed **five** CI jobs; the two fixture suites each reported **151 passed, 7 optional skipped**, and a dedicated real-CO₂ G3.1 suite passed **three tests**. Full numerical evidence and limitations are in [G3.1 results](https://github.com/Open-Energy-Methods/sco2-braytonbench/blob/main/docs/G31_FIXED_UA_NUMERICAL_RESULTS.md).

**Gate:** numerically verified for these synthetic cases; industrial installed-UA identification, gas composition, temperature-dependent U, real flow hydraulics and machine maps remain open.

# 8. G3.2: coupled installed heater, installed cooler and finite coolant

## 8.1 Governing improvement

G3.2 removes the assumption that compressor inlet state can be treated as fixed independently of the coolant. It couples a finite hot exhaust stream and a finite sensible coolant through **two fixed installed exchanger UAs**, solving compressor inlet **T1** and turbine inlet **T4** simultaneously (as nested feasible nonlinear problems). Both exchanger duties satisfy stream-side enthalpy balances, local temperature approaches and conductance constraints; coolant outlet temperature is determined from heat rejection. The core now responds coherently to source and heat-sink conditions in a reduced steady physical framework.

The fixed heater and cooler UAs were **synthetically sized** from an internal nominal point. The nominal calculation used **five exchanger sections** in the G3.2 example and was therefore marked **coarse, not converged**. Optional gas and coolant cp functions were added, as well as an optional illustrative flow-scaled pressure-loss/efficiency scenario, but the main example retained independently specified constant nominal machine efficiencies and losses.

## 8.2 Nominal input ledger

| Input | Value / source nature |
|---|---:|
| Gas inlet temperature / flow | 800 K / 100 kg/s |
| Gas sensible cp | 1100 J/(kg K) at 300 K, linear slope +0.20 J/(kg K²) — **assumed** |
| Coolant inlet / flow | 285 K / 75 kg/s |
| Coolant cp | 4180 J/(kg K), constant — **assumed** |
| Nominal CO₂ T1 / T4 / flow | 310 K / 650 K / 20 kg/s |
| CO₂ pressures | 8.5 MPa low, 24 MPa high |
| Recuperator UA | 200 kW/K |
| Installed heater UA | **21.625962 kW/K**, derived from nominal reference |
| Installed cooler UA | **100.514392 kW/K**, derived from nominal reference |
| Component resolution | **5 sections** (initial coarse exercise) |

## 8.3 Two independently solved coolant conditions

| Calculated quantity | 285 K coolant inlet | 287 K coolant inlet |
|---|---:|---:|
| Compressor inlet T1 | **310.004883 K** | **310.463867 K** |
| Turbine inlet T4 | **650.019531 K** | **652.216797 K** |
| Gas exit T | 761.434830 K | 761.969130 K |
| Coolant outlet T | 295.172950 K | 297.025449 K |
| Net shaft output | **1.423728 MW** | **1.406263 MW** |
| Cycle thermal efficiency | 30.863734% | 30.912031% |
| Heater duty | 4.612948 MW | 4.549241 MW |
| Cooler duty | 3.189220 MW | 3.142978 MW |
| Heater actual calculated UA | 21.625691 kW/K | 21.627529 kW/K |
| Cooler actual calculated UA | 100.448503 kW/K | 100.572653 kW/K |
| Relative heater UA residual | 0.001251% | 0.007246% |
| Relative cooler UA residual | 0.065552% | 0.057963% |
| Cooler entropy generation | +1154.805 W/K | +1125.584 W/K |
| Outer iterations / evaluations | 10 / 14 | 10 / 14 |

Increasing the assumed coolant inlet from 285 to 287 K changes modelled compressor inlet by **+0.458984 K**, turbine inlet by **+2.197266 K** and net shaft power by **−17.465 kW**. The small calculated cycle efficiency increase of **+0.0483 percentage points** arises because the chosen model also reduces heater duty; it is **not** evidence that warmer coolant generally improves a practical sCO₂ cycle.

The source energy residuals are of order **10⁻⁹ W** at both cases (floating-point conservation closure), and the cooler entropy generation remains positive. The declared acceptance tolerances were **<0.08%** relative cooler UA error and **<0.02%** relative heater UA error. Again, these are computational residual tolerances, not measurement accuracies.

## 8.4 Optional flow-loss scenario and its correct interpretation

An optional scenario used `ΔP = ΔP_ref × (m/m_ref)^2`, where nominal CO₂ flow was 20 kg/s, plus efficiency penalties `0.02 × (flow_ratio−1)^2`. Example heater pressure drops for 10, 20, 30 kg/s were **37.5, 150 and 337.5 kPa** and cooler drops **12.5, 50 and 112.5 kPa**. These values were **not used in the main two coolant-temperature calculations**, do not derive from measured tube geometry, and are **not** vendor performance maps. They are opt-in model sensitivity assumptions only.

[Actions run 42005964249](https://github.com/Open-Energy-Methods/sco2-braytonbench/actions/runs/42005964249) passed **six** jobs; Python fixture runs each reported **178 passed / 8 optional skipped**, and the dedicated real-CO₂ dual-UA inverse exercise passed. The [full G3.2 report](https://github.com/Open-Energy-Methods/sco2-braytonbench/blob/main/docs/G32_NUMERICAL_VERIFICATION.md) records the inputs, source limitations, residuals and solver status.

**Gate:** G3.2 nonlinear coupled software prototype is verified for the declared cases. Full industrial off-design validity remains open because near-critical discretisation, calibrated fluid/flow properties, equipment UAs, phase/pressure treatment, machinery maps, pump/fan parasitics and measured operating data are not provided.

# 9. G3.3: source-grounded gas/water properties, hydraulics and mesh sensitivity

## 9.1 Why this step mattered

The G3.2 gas stream used illustrative linear sensible cp; the coolant used a constant cp; and pressure losses were externally imposed. G3.3 introduced **reference-backed optional property services** and a **geometry-demanding standalone hydraulic calculation**, while avoiding the equally problematic step of pretending unknown industrial tubing sizes were known. G3.3 also ran explicitly stated multi-resolution component checks at more than one real-CO₂ operating point.

## 9.2 NIST Shomate dry-air model

`DryAirNISTShomate` uses **79 mol% N₂ / 21 mol% O₂**, a fixed dry-air composition, and published NIST Shomate coefficients between **300 and 1000 K**. It computes sensible enthalpy and temperature-dependent heat capacity, and can calculate the associated sensible entropy differences under fixed composition and pressure conventions. Example values are **cp = 1011.459 J/(kg K) at 300 K** and **1106.475 J/(kg K) at 800 K**.

The fluid is **dry air**, not an actual sampled flue gas. Real exhaust may include H₂O, CO₂, argon, residual oxygen, NOx and other species; reactions, dew points, gas-side pressure and chemical exergy remain outside this model. It would be wrong to call this a validated combustion-gas mixture from merely supplying NIST property coefficients. Primary sources are [NIST N₂](https://webbook.nist.gov/cgi/cbook.cgi?ID=C7727379&Mask=1) and [NIST O₂](https://webbook.nist.gov/cgi/cbook.cgi?ID=C7782447&Mask=17).

## 9.3 CoolProp liquid water and circular-pipe friction

`CoolPropLiquidWater` uses an isobaric `HEOS::Water` stream at specified example pressure **0.3 MPa**, with its declared liquid-only temperature range **280–340 K**. It does not represent boiling, freezing, fluid-pump work or a measured cooling-loop pressure drop. The thermodynamic reference is <https://coolprop.org/fluid_properties/fluids/Water.html>.

`hydraulics.pipe_loss` implements **Darcy–Weisbach**, laminar `f=64/Re`, turbulent **Haaland** approximation to Colebrook, and explicit length, diameter, roughness, minor-loss `K`, density and viscosity input. Transition **2300 ≤ Re < 4000 is rejected** rather than covered by an invented interpolating accuracy. Without geometry or pump curves, this function remains deliberately separate from the Brayton cycle’s actual equipment pressure ledger.

## 9.4 Two-point real-CO₂ component segmentation study

The two test cases were **prescribed pressure/temperature states**, not simultaneous fixed installed-heater and installed-cooler UA solutions at each segmentation level:

| Input | Case A | Case B |
|---|---:|---:|
| Low CO₂ pressure / compressor inlet | 8.5 MPa / 310 K | 9 MPa / 314 K |
| Turbine inlet pressure / T | 24 MPa / 650 K | 24 MPa / 690 K |
| CO₂ mass flow | 20 kg/s | 20 kg/s |
| Recuperator installed UA | 200 kW/K | 200 kW/K |
| Dry gas inlet and flow | 800 K, 100 kg/s | 850 K, 100 kg/s |
| Water inlet and flow | 285 K, 75 kg/s | 285 K, 75 kg/s |

The outputs at **6 / 12 / 24 / 48** heat-exchanger sections were:

| Case A metric | 6 | 12 | 24 | 48 |
|---|---:|---:|---:|---:|
| Cycle efficiency (%) | 30.850478 | 30.822519 | 30.813657 | **30.811261** |
| Recuperator heat duty (MW) | 4.503075 | 4.498888 | 4.497560 | **4.497200** |
| Recuperator internal minimum approach (K) | 3.728545 | 3.864567 | 3.907765 | **3.919449** |
| Required heater UA (kW/K) | 21.766931 | 21.777700 | 21.781380 | **21.782395** |
| Required cooler UA (kW/K) | 100.798020 | 101.347517 | 101.490975 | **101.527335** |

| Case B metric | 6 | 12 | 24 | 48 |
|---|---:|---:|---:|---:|
| Cycle efficiency (%) | 32.298377 | 32.277097 | 32.269671 | **32.267599** |
| Recuperator heat duty (MW) | 5.190599 | 5.187679 | 5.186659 | **5.186374** |
| Recuperator internal minimum approach (K) | 4.438926 | 4.538104 | 4.572764 | **4.582438** |
| Required heater UA (kW/K) | 20.014165 | 20.022297 | 20.025315 | **20.026170** |
| Required cooler UA (kW/K) | 75.643259 | 75.984806 | 76.074502 | **76.097360** |

From **24 to 48 sections**, recuperator duty changed **0.007989% / 0.005489%**, heater required UA **0.004661% / 0.004270%**, and cooler required UA **0.035813% / 0.030037%** for A/B. The efficiency change was **0.002396 / 0.002072 percentage points**, and local minimum approach changed **0.011684 / 0.009674 K**. These are useful *local* mesh-sensitivity observations.

An equally important **physical warning** is that 48-section recuperator minimum approaches were only **3.919 K and 4.582 K**. Both would fail a hypothetical **10 K** minimum approach. Numerically smooth required UA values do not automatically mean the proposed physical design is feasible. For the prescribed cases, heater minimum approach remained 150 K (A) / 160 K (B), and cooler approaches were positive.

## 9.5 Numerical corrections, tests and gate

Three corrections are recorded in the original G3.3 work: (i) use the cooler’s actual declared `minimum_approach_k` field, (ii) compare energy conservation on a sensible relative scale rather than demanding a ~10⁻⁵ W numerical residual on MW duties, and (iii) refine a CoolProp `P,H` temperature flash against a direct `P,T` enthalpy equation using `cp=(dh/dT)_P`. The dedicated property/hydraulic CI job passed **35** tests. Both fixture suites passed **205 tests / 9 optional modules skipped**; see [Actions 42010735595](https://github.com/Open-Energy-Methods/sco2-braytonbench/actions/runs/42010735595) and the [G3.3 numerical report](https://github.com/Open-Energy-Methods/sco2-braytonbench/blob/main/docs/G33_NUMERICAL_VERIFICATION.md).

**Gate:** G3.3 properties and two prescribed-point component segmentation checks passed narrow test conditions. Broad near-critical grid independence, full dual-UA operating-point convergence, measured equipment geometry, accurate exhaust composition and industrial operating envelopes remain open.

# 10. G3.4: external evidence intake, provenance taxonomy and quality control

## 10.1 The source taxonomy was itself a research contribution

A recurring problem in engineering benchmarking is the casual treatment of every published number as a laboratory measurement. G3.4 built a source-intake and QC approach designed to preserve how each observation was generated. At minimum the repository distinguishes **`measured`**, **`experimentally_derived`**, **`model_corrected`**, **`simulated`** and **`predicted_design`** quantities. The target for a single-pipe HTC test is not the same as the target for a sodium-PCHE heat balance, a turbomachinery speed-map check or a whole-cycle power balance.

The external source registry covers seven evidence families. Each is a *candidate* for its appropriate physical module, not interchangeable evidence for all components.

| Evidence identifier | Actual source / available form | Evidence type and appropriate target |
|---|---|---|
| **STUTTGART-2022** | Theologou et al. [original dataset DOI 10.17632/4mvk4nxrkz.1](https://doi.org/10.17632/4mvk4nxrkz.1), **54 experiments**, **2,508 axial records**, **2,398 reduced local HTC points** | Measured temperatures/heat input and **experimentally derived local HTC**; horizontal heated circular pipe stratification |
| **ZHANG-2022** | Zhang et al. [10.3389/fenrg.2022.835224](https://doi.org/10.3389/fenrg.2022.835224), Na/CO₂ PCHE; 4-mm sodium and 1.5-mm CO₂ channels; ~7.3-m² area; rated hot/cold duties **54.8 / 54.2 kW** | Published **experimental** heat duties and geometry-specific PCHE thermal comparison; not automatically a water cooler or gas recuperator |
| **KAIST-2024** | Lee et al., sCO₂ symposium Paper 6; **15 RPM sweep rows**, about **12,000–36,000 RPM**; leakage/flow/pressure and corrected turbine-inlet temperatures | Mixture of **measured**, indirectly inferred and **model-corrected** turbine information; not a direct standalone isentropic-efficiency map |
| **SANDIA-2010** | Wright et al., SAND2010-0171; predicted Table 2.1 design states and separate measured §5.3 compressor-map figures | Table 2.1 is **predicted design**, not measurement; only separately extracted measured map data can benchmark a compressor |
| **HZDR-PCHE-2025** | Guille-Bourdas et al., [RODARE DOI 10.14278/rodare.3928](https://doi.org/10.14278/rodare.3928); nine figure/workbook files | **Numerical/economic** HX prediction and cost sensitivity, not laboratory sCO₂ sensor data |
| **HZDR-TPMS-2026** | Guille-Bourdas et al., RODARE CARBOSOLA TPMS CAD/Fluent archive; CAD, scripts, large CFD cases and seven cleaned text tables | **Simulated geometry/CFD outputs**; no experimental validation simply from an ANSYS result |
| **KTH-SPG-MSR** | KTH publicly listed 2025–2027 research project with Siemens Energy partner and heat-exchanger/test-infrastructure objectives | Publicly documented project prospect; **no released operating rig measurements** established in the intake |

The source audit deliberately refused to incorporate large vendor CFD archives, copyrighted journal PDFs or unclear-rights files into the repository indiscriminately. Measured, model-corrected and simulated data must remain traceable all the way from original source through the appropriate test.

## 10.2 STU-001: original Stuttgart source anomaly

The original Excel workbook’s **TS4** sheet contains experiment **`4MM_HM_77.5_10_20_90_A`**, with reported heat flux **832.9920767421186 kW/m²**. Nominally corresponding bottom and top orientation runs show heat fluxes approximately **91.7575** and **91.7029 kW/m²**, while source electrical input powers are very close, around **2309–2310 W**. The discrepancy is strongly suggestive of a source-cell mistake, but the repository **does not claim proof** of which source value is correct.

Accordingly the **whole run is quarantined** from correlation scoring; its source value is **retained unchanged**. The correct model-development action was not to replace the anomaly with a convenient 91.7 kW/m² value and then quietly include the altered run. That choice preserved reproducibility and made the denominator of each benchmark explicit.

The original source also gives a matched top/bottom circumferential temperature difference up to **86.813 K** at an 0.76-m axial station in a particular 8-mm nominal family. The associated article discusses around 90 K of stratification. This is a source-consistency check of a measured profile feature, not a successful HTC prediction.

## 10.3 ZH-001: PCHE published rated U inconsistency

The Zhang sodium-PCHE rated case provides sodium temperature **501.5 → 326.7 °C**, CO₂ temperature **317.8 → 498.5 °C**, heat-duty reports **54.8 kW** sodium / **54.2 kW** CO₂, total area **7.3 m²**, and quoted rated overall U **1264 W/(m² K)**. Taken literally with the paper’s counterflow terminal differences:

```text
DeltaT_hot_end  = 501.5 - 498.5 = 3.0 K
DeltaT_cold_end = 326.7 - 317.8 = 8.9 K
LMTD = (8.9 - 3.0)/ln(8.9/3.0) = 5.425592 K
U_from_CO2_duty = 54.2 kW/(7.3 m² × 5.425592 K)
                = 1368.451 W/(m² K)
```

The simple calculation is **8.264% above** the reported rated U. The table also reports **1388 W/(m² K)** at one 20.0-MPa condition, which is not assumed to be the exact same condition and reduction method. Possible area, temperature averaging, loss or processing conventions have **not** been resolved. Therefore this **ZH-001** discrepancy must be reconciled before adopting a rated UA as calibrated PCHE truth.

## 10.4 KAIST-001 and SANDIA-001: avoiding false machinery maps

KAIST’s turbine inlet thermocouple sits upstream of secondary-flow merging in the reported system. Correcting turbine inlet state for windage and leakage is a **model-dependent reconstruction**, not a direct temperature measurement at the main turbine inlet. Reported motor electrical power is not the measured turbine shaft-power output, and should not be used to back-calculate a credible isentropic efficiency map without additional efficiency and loss measurements. Similarly, Sandia Table 2.1’s three 75,000-RPM conditions were **predictions**; the separately published measured compressor figures require proper raw data or digitised points before independent map comparison.

**Gate:** G3.4 source classification, provenance and QC are completed as an intake stage; detailed sodium-PCHE, compressor, turbine, CFD and system benchmarking against those sources is **not complete**. The [G3.4 evidence audit](https://github.com/Open-Energy-Methods/sco2-braytonbench/blob/main/docs/G34_EXTERNAL_VALIDATION_INTAKE.md) preserves the exact classification and outstanding source mismatches.

# 11. G3.5 H1a: complete Stuttgart horizontal sCO₂ experimental benchmark

## 11.1 Why local HTC became a new scientific bottleneck

The finite-UA cycle framework and source/coolant stream balances are computationally useful, but the actual installed **U** of a real exchanger depends on CO₂-side convection, wall conduction, channel geometry, opposite-side heat transfer, flow distribution and fouling. Conventional correlations can be severely misleading near the CO₂ pseudocritical region because density, cp and transport properties vary strongly with temperature, while gravity can produce **circumferentially nonuniform top/middle/bottom temperatures** in horizontal heated pipes. Rather than fitting an arbitrary cycle-wide UA from one hypothetical point, G3.5 moved down the hierarchy to examine a **single heated-pipe HTC closure** against original external experimental data.

The source is **Theologou, Mertz, Laurien and Starflinger (2022)**, original [Mendeley dataset 10.17632/4mvk4nxrkz.1](https://doi.org/10.17632/4mvk4nxrkz.1), licensed CC BY 4.0, and the associated paper [10.1016/j.energy.2022.124171](https://doi.org/10.1016/j.energy.2022.124171). Dataset-derived numbers are reported as **experimentally reduced HTCs**, not as independent stand-alone HTC sensor measurements.

## 11.2 Source ledger and admissibility chain

| Filtering operation | Number of records |
|---|---:|
| Original experimental IDs | **54** |
| Original axial source positions | **2508** |
| Original reduced local HTC entries | **2398** |
| Whole anomalous experiment STU-001 | **1 run** |
| Local HTC entries excluded with STU-001 | **50** |
| Remaining reduced HTC records | **2348** |
| Additional source/applicability exclusions per primary baseline | **30** |
| **Final admissible local comparison points** | **2318** |
| Source runs represented in final sample | **53** |
| Original nominal physical families | **18** |
| Predeclared held-out nominal families | **4** |
| H1a valid held-out local comparisons | **534** |

HB = **bottom 180°** (790 admissible stations), HM = **middle 90°** (738), HT = **top 0°** (790). The 30 near-inlet exclusions largely arise from **8-mm tubes at x = 0.04 m, x/D = 5**, where adopted fully developed/source validity conditions require at least x/D = 10. The original source data remain in `data/validation/stuttgart/experiment_index.csv` and `axial_profiles.csv`, with an attribution README.

The 18 physical nominal experiment families contain all wall orientations of a nominal experimental setting. The split uses a fixed **SHA256-based family key** so the three wall orientations and axial positions of one nominal configuration remain together. **Four entire families** were declared held-out *before* the later correlation calculations; they were neither shuffled by axial position nor altered after observing results. These groups are:

```text
4MM_H*_77.5_10_20_30_A
4MM_H*_77.5_5_5_50_A
8MM_H*_77.5_40_30_90_A
8MM_H*_77.5_40_5_130_A
```

Because H1a–H1d did **not** fit their published coefficients, this fixed split is a rigorous preservation of an evaluation stratum but **not a substitute for a newly trained model's external generalisation trial**.

## 11.3 Bulk thermodynamic reconstruction and output definition

The experiment’s published axial thermodynamic reductions used REFPROP. BraytonBench does not assume the same **absolute enthalpy zero** as its CoolProp backend. It obtains a CoolProp inlet state at the recorded measured inlet pressure and temperature, adds the source's reported **axial enthalpy increment from that inlet**, and reconstructs the bulk state through CoolProp at the recorded approximate constant run pressure. This respects source-relative energy increments while maintaining a consistent property convention.

The reported comparison target is `h_source = q''/(Twall,measured - Tbulk,source)` under the source reduction conventions. This target is **derived from q and measured thermal states**. If a model is then fed measured `Twall` and compared with this target, the input already carries information that appears in the target definition. It can still be a useful conditioned diagnostic, but it is **not a prospective wall-temperature prediction**.

H1a deliberately uses **bulk-property** forced-convection correlations without wall-temperature inputs:

```text
Dittus-Boelter heating: Nu = 0.023 Re^0.8 Pr^0.4
Gnielinski: Nu = ((f/8)(Re-1000)Pr) /
               (1 + 12.7 sqrt(f/8) (Pr^(2/3)-1))
f = (0.79 ln Re - 1.64)^(-2)
h = Nu k_bulk / D
```

Explicit applicability checks are enforced for Re/Pr and minimum x/D. These correlations are not made orientation-dependent by applying an invented angular multiplier.

## 11.4 H1a executed numerical errors

| Metric | Gnielinski | Dittus–Boelter |
|---|---:|---:|
| Successful source station comparisons | 2318 | 2318 |
| **Overall HTC MAPE** | **150.15%** | **119.60%** |
| Mean signed percentage bias | +137.05% | +100.55% |
| Median APE | 55.07% | 47.17% |
| 90th-percentile APE | 385.05% | 298.15% |
| RMS percentage error | 266.27% | 210.29% |
| Equal-run macro MAPE | 156.89% | 124.70% |
| Equal-nominal-family macro MAPE | 156.39% | 124.24% |
| Held-out MAPE, 534 records | **158.10%** | **121.82%** |

The errors vary severely by original wall station:

| Original wall station | n | Gnielinski MAPE | Dittus–Boelter MAPE |
|---|---:|---:|---:|
| HB, bottom | 790 | **87.71%** | 69.65% |
| HM, middle | 738 | **124.23%** | 98.76% |
| HT, top | 790 | **236.81%** | **189.01%** |

By diameter: **4-mm** tubes (1150 stations) gave **96.13% / 78.65%** Gnielinski/DB MAPE; **8-mm** tubes (1168 stations) gave **203.34% / 159.91%**. The positive bias and especially high top-wall errors are compatible with substantial buoyancy/stratification effects not addressed by orientation-blind fully developed forced-convection formulas. They are **not** an independent causal identification of one flow mechanism: other transport, thermal development or source reduction assumptions may contribute.

The comparison included the fraction of model predictions within the source’s reported local 1σ HTC error bounds as a **descriptive normalisation only** (approximately **15.44% / 11.22%** for Gnielinski/DB). Those percentages cannot be interpreted as a proper confidence-interval coverage because experimental HTC components and their uncertainties are correlated and model-form error is not included.

The [complete H1a report](https://github.com/Open-Energy-Methods/sco2-braytonbench/blob/main/docs/G35_STUTTGART_RESULTS.md), per-point CSV and [Actions 42031845343](https://github.com/Open-Energy-Methods/sco2-braytonbench/actions/runs/42031845343) reproduce this analysis. **H1a experimental ingestion and computation pipeline passed; predictive closure did not**.

# 12. G3.5 H1b: Bishop and Jackson–Hall wall-property correlations

## 12.1 Scientific change from H1a

H1b implemented published **Bishop** and **Jackson–Hall** forms that incorporate properties near the wall or temperature-averaged transport effects. It also introduced a diagnostic **Richardson-number buoyancy-risk indicator**. The purpose was not to fit a replacement formula on Stuttgart, but to test whether better handling of strong real-fluid property changes improved local HTC predictions while retaining H1a’s unchanged data, quarantine and group split.

Two computational modes were explicitly separated:

- **Measured-wall-conditioned:** evaluate a correlation at the experiment’s measured wall temperature. This is a *posterior diagnostic*, not a prediction of wall T from prescribed heat flux; the target HTC already depends on the same measured wall temperature.
- **Flux-driven inversion:** use prescribed source heat flux, reconstructed bulk enthalpy, flow, pressure and geometry, then solve `q'' = h_model(Twall)(Twall-Tbulk)` without using experimental wall temperature as an input. This gives a legitimate **conditional local wall balance prediction** relative to those supplied source quantities, not a complete HX/plant prediction.

**Coverage matters:** Bishop’s original x/D range **30–565** excludes **166** of the H1a 2318 points, leaving **2152**; Jackson uses **2318**. A naive all-point comparison of 2152 to 2318 scores would mix different populations.

## 12.2 Full executed H1b outcomes

| Mode and model | Source measured Tw used? | Eligible n | Overall HTC MAPE | Held-out MAPE | HB MAPE | HT MAPE |
|---|---|---:|---:|---:|---:|---:|
| Bishop, conditioned | **Yes** | 2152 | 21.94% | 20.72% | 14.23% | 33.94% |
| Jackson–Hall, conditioned | **Yes** | 2318 | 28.46% | 24.16% | 17.84% | 44.48% |
| **Bishop, flux-driven** | **No** | 2152 | **46.40%** | 39.72% | 24.79% | 80.65% |
| **Jackson–Hall, flux-driven** | **No** | 2318 | **49.47%** | 43.16% | 26.41% | **84.63%** |

For the **flux-driven** modes, mean signed error was approximately **+37.2076% Bishop** and **+35.1829% Jackson**; 90th-percentile absolute error was **120.6929% / 123.1989%**, and nominal-family macro MAPE **47.2946% / 50.9267%**. The fraction flagged `Ri > 0.001` was around **98.65% / 98.58%**. That Richardson threshold flags the possibility of buoyancy relevance; it does not establish an angular mixed-convection law or solve the transverse CO₂ velocity profile.

On exactly **2152 Bishop-eligible stations**, Jackson flux-driven MAPE becomes **52.14%**, versus Bishop **46.40%**. Bishop has lower nominal-family mean absolute error in **12 of 18** families, Jackson in **6**, with an equal-family mean advantage about **7.03 percentage points** for Bishop. A preliminary family-resampling percentile interval was approximately **−4.6 to +18.3 percentage points**, crossing zero. Therefore H1b supports an improvement over simple baselines on these data, but does **not** prove Bishop universally superior to Jackson or either sufficient for CO₂ orientation-resolved design.

The original source data also satisfy the algebraic reduction `q''/(Twall-Tbulk) ≈ measured-derived HTC` extremely closely (median mismatch on Bishop-eligible data around **8.1×10⁻⁸%**). This is an **internal reduction consistency check**, not independent confirmation of experimental sensor accuracy. In fact it reinforces why conditioned scores look optimistic: they consume quantities already used to derive the target.

The [H1b results](https://github.com/Open-Energy-Methods/sco2-braytonbench/blob/main/docs/G35B_RESULTS.md), [methods](https://github.com/Open-Energy-Methods/sco2-braytonbench/blob/main/docs/G35B_WALL_PROPERTY_CORRELATIONS.md), [paired audit script](https://github.com/Open-Energy-Methods/sco2-braytonbench/blob/main/scripts/stuttgart_h1b_paired_audit.py), and [CI 42035909213](https://github.com/Open-Energy-Methods/sco2-braytonbench/actions/runs/42035909213) preserve the complete population and source limitations.

**Gate:** H1b numerical implementation passed, and selected wall-property correlations improved over basic forced convection. The surviving **~81–85% top-wall MAPE**, unknown full original-source applicability and lack of a physical angular closure kept predictive validation open.

# 13. G3.5 H1c: Lei water-correlation transfer to sCO₂ as a negative research result

## 13.1 The test hypothesis and its built-in limitation

Theologou et al. (2022) reproduce published Lei et al. (2017) bottom/top orientation formulations, with heat-flux-based Grashof and wall/bulk thermophysical property dependencies. H1c implemented those source equations explicitly for **HB** and **HT**. However, Lei’s original calibrated measurements were **supercritical water** at approximately **23–25 MPa**, in **26- and 43-mm horizontal tubes**. Stuttgart’s near-critical CO₂ is at approximately **7.75 MPa** in **4/8-mm tubes**. H1c was therefore designed as an **honestly labelled cross-fluid and cross-geometry transferability stress test**, not in-domain validation of the source authors.

The paper supplies **no published HM middle-wall equation**. H1c did not invent one or interpolate the top/bottom coefficients. The available H1b population contributed **790 HB + 790 HT = 1580** candidate stations, from **36 orientation-specific runs** spanning the original 18 nominal families; **738 HM** observations were excluded by source-definition. The four originally held-out nominal families contained **356** eligible HB/HT stations. All original source and split constraints were retained.

## 13.2 Numerical issue identified and corrected

An initial wall-inverse calculation used a comparatively coarse **0.008-K root bracket width**, even while demanding a **0.2% independent heat-balance residual**. This mismatch led to **234/1580** points being rejected as unconverged, despite usable root brackets. The rejected points were **numerical discretisation artifacts**, not a new model applicability decision. The calculation was revised to **1×10⁻⁵ K** root width, allowing up to **35 bisection iterations**, with the separate relative wall energy residual still required to satisfy `≤0.002`.

The corrected real-CO₂ benchmark solved **1580/1580** flux-driven points. Maximum relative wall heat-flux balance residual was approximately **1.2722×10⁻⁵** (**0.00127%**), median around **4.4174×10⁻⁷**. Good numerical closure established that the final large HTC errors were not artifacts of the earlier root stop tolerance. It did **not** mean the source correlation transferred physically.

## 13.3 Actual Lei outcomes on matched HB/HT stations

| Model and computational mode | Common n | Overall HTC MAPE | HB bottom MAPE | HT top MAPE | Held-out MAPE |
|---|---:|---:|---:|---:|---:|
| Lei, **measured-wall-conditioned** | 1580 | 175.18% | 76.26% | 274.09% | 177.26% |
| **Lei, flux-driven** | **1580** | **631.72%** | **197.73%** | **1065.72%** | **638.83%** |
| Jackson–Hall flux-driven, same IDs | 1580 | **55.52%** | 26.41% | 84.63% | 49.35% |
| Gnielinski, same IDs | 1580 | 162.26% | 87.71% | 236.81% | 170.29% |

Bishop had only **1468** admissible HB/HT points under its distinct x/D gate, with approximately **52.72%** MAPE on its own allowed subset. It was not misrepresented as a 1580-point direct comparison.

The Lei flux-driven signed mean bias was approximately **+630.69%**, identifying extremely strong HTC overprediction. Its median absolute error was approximately **269.67%**; top-wall performance was dramatically worse than bottom-wall performance. In **all 18 nominal families**, Jackson had lower family-average flux-driven error than Lei. The family-equal-weighted Jackson-minus-Lei error difference was **−599.17 percentage points**; a 4000-draw between-family bootstrap percentile interval was **[−756.20, −460.04] points**. This resampling is **not** measurement uncertainty, out-of-domain predictive confidence or formal proof of performance in unobserved equipment.

## 13.4 Why a failed transfer is an important result

H1c showed that **adding angular labels to a correlation is insufficient**. A formula can properly represent a top/bottom asymmetry in water while being disastrously wrong when transferred to CO₂, different diameters and a different pressure/thermophysical regime. It also demonstrated the value of keeping numerical convergence and physical validity separate: a small `q''−hΔT` residual does not rescue an inaccurate constitutive closure. The appropriate next source was a **CO₂-specific mixed-convection formulation**, not yet another uncalibrated multiplier attached to the Lei equations.

The source formula and real-fluid computation were therefore retained as a **reproducible negative-result** research milestone. The [H1c report](https://github.com/Open-Energy-Methods/sco2-braytonbench/blob/main/docs/G35C_LEI_RESULTS.md) and [Actions 42040967963](https://github.com/Open-Energy-Methods/sco2-braytonbench/actions/runs/42040967963) contain the raw model-station records and accepted convergence evidence.

**Gate:** H1c source-equation implementation **PASS**; transferability to Stuttgart near-critical CO₂ **FAILS**; validated CO₂ horizontal orientation-resolved HTC **OPEN**.

# 14. G3.5 H1d: recovery of the original Kim (2019) CO₂ model

## 14.1 Why the original article, rather than an abstract, was required

After the Lei water-to-CO₂ failure, the high-priority next paper was **Tae Ho Kim, Jin Gyu Kwon, Joo Hyun Park, Hyun Sun Park and Moo Hwan Kim (2019)**, *Heat transfer model for horizontal flows of CO₂ at supercritical pressures in terms of mixed convection*, *International Journal of Heat and Mass Transfer* **131**, pp. 1117–1128, DOI [10.1016/j.ijheatmasstransfer.2018.11.075](https://doi.org/10.1016/j.ijheatmasstransfer.2018.11.075).

The published summary indicates a particularly relevant topic: **supercritical CO₂ itself**, horizontal flow and explicit **top/bottom** mixed convection. However, an abstract’s claim of roughly 10% error is not sufficient to write a scientifically traceable model: the exact formula, fitted exponents, property reference state, heat-flux Grashof definition, superposition convention, geometry and training domain must all be known. The **complete 12-page original article** was obtained through the project work, and its rendered pages were checked for **p.2 nomenclature, p.4 Table 1, p.8 Eqs. 23/24 and Table 4, and p.10 Eqs. 29/30 and the authors’ model comparison table**.

Original article PDF SHA-256 recorded in the versioned coefficient registry:

```text
8407a94d23a048cc8e3c1889296108b4da0d812bba6cd8ec91a13a3babb47651
```

The PDF was **not publicly rehosted**. Only the model-specific factual coefficient registry, author/source identification, formulas and audit comments were versioned. See [Kim original source audit](https://github.com/Open-Energy-Methods/sco2-braytonbench/blob/main/docs/KIM2019_ORIGINAL_SOURCE_RECOVERY.md) and [coefficient registry](https://github.com/Open-Energy-Methods/sco2-braytonbench/blob/main/data/reference/kim2019_coefficients.json).

## 14.2 Original source experiment ranges and authors' reported errors

The article’s POSTECH horizontal tube experiment is reported as **7.75-mm internal diameter**, **0.91-m heated length**, and **0.1-m unheated entrance**. Inlet pressure was **73.83–77.35 bar**, inlet temperature **24.5–30.07 °C**, mass flux **52.1–250.5 kg/(m² s)** and heat flux **1.2–25.9 kW/m²**. An additional **Adebiyi–Hall** dataset was used at about **75.86–76.14 bar**, mass flux **104.34–391.91 kg/(m² s)** and heat flux **5.1–26.9 kW/m²**, with inlet temperatures **13.8–30.1 °C**.

The article reports **620 original evaluation points**: **495 POSTECH** and **125 Adebiyi–Hall**, with an `x/D < 10` exclusion. Its Table 6 reports the **authors’ original-study empirical mean absolute deviations** of **10.00% top** and **10.44% bottom**. The authors’ **semi-empirical** entries are **21.73% top** and **22.35% bottom**. The table also contains an aggregate top/bottom metric of **8.71%** for the empirical model; it should be labelled an *author-defined aggregation* rather than reconstructed as the simple average of 10.00% and 10.44%.

**None of the 620 original pointwise records or original fitting/implementation source code was reproduced from this paper.** The printed original error values remain citations to the authors’ work, **not achieved BraytonBench model MAPE**. Without the original observations and the precise author code convention, exact source-study numeric parity cannot be established.

## 14.3 Thermophysical definitions actually implemented

For bulk CO₂ state at source pressure **P** and temperature **Tb**, and candidate heated inner-wall temperature **Tw > Tb**, define the fixed-pressure bulk-to-wall temperature integral average of any property `psi` as:

```text
psi_avg = integral[ Tb to Tw ] psi(P,T) dT / (Tw - Tb)
cp_avg  = [h(P,Tw) - h(P,Tb)] / (Tw - Tb)
Re_b    = G D / mu_b
Pr_b    = cp_b mu_b / k_b
beta_b  = (rho_b - rho_avg) / [rho_b (Tw - Tb)]
Q_b     = beta_b q'' D / k_b
Gr_q    = g beta_b q'' D^4 / [(mu_b/rho_b)^2 k_b]
```

Here `G = 4 m_dot/(pi D²)` for one circular tube; bulk properties carry subscript `b`, `avg` indicates the temperature-integral average, and `q''` is the measured source heating flux used as the conditional driver. Importantly **`beta_b` is the Kim source-defined bulk/averaged-density expansion term**, not the separate film-property formula used by the earlier Lei paper. Replacing the two with each other would silently change the original physical model.

Averaged **cp** is recovered from the *isobaric enthalpy difference* rather than numerically integrating a narrow pseudocritical cp peak, a useful numerical consistency choice. Density, viscosity and thermal conductivity are numerically integrated using **eight-point Gauss quadrature** across bounded temperature subintervals. CoolProp P/T evaluations are cached, both to avoid excess backend calls during repeated wall-root searches and to preserve consistent state evaluations. The implementation validates finite/positive necessary properties and enforces a heated-wall/positive effective expansion domain. The model is a source-equation calculator, not a resolved 2-D or 3-D buoyant flow solver.

## 14.4 Published model structure and source-equation interpretation

The published model separates a **forced-convection contribution**, a **natural-convection contribution** and their quadratic superposition:

```text
Nu_forced = c1 * Re_b^0.8 * Pr_b^0.4
            * Q_b^n3 / [Re_b^n1 * Pr_b^n2]
            * (rho_avg/rho_b)^n4
            * (mu_avg/mu_b)^n5
            * (k_avg/k_b)^n6

1/Nu_natural = c2 * Gr_q^m1 * Pr_b^m2
               * (rho_avg/rho_b)^m3
               * (mu_avg/mu_b)^m4
               * (cp_avg/cp_b)^m5
               * (k_avg/k_b)^m6

Nu_mixed = sqrt(Nu_forced^2 + Nu_natural^2)
HTC     = Nu_mixed * k_bulk / D
```

The reciprocal in the natural component is essential: the printed expression specifies **`1/Nu_natural`**, which must be inverted. The forced/natural combination is **square root of summed squares**, not direct arithmetic addition. The source includes separate empirical and semi-empirical coefficient sets, not one universal mix-and-match table.

**Empirical Table 4 `c1` and `n1`–`n6` coefficients:**

| Position | c1 | n1 | n2 | n3 | n4 | n5 | n6 |
|---|---:|---:|---:|---:|---:|---:|---:|
| Top | **1.14** | −0.50 | −0.36 | 0.54 | 0.83 | −3.48×10⁻¹⁴ | 0.52 |
| Bottom | **0.11** | −0.15 | −0.41 | 0.26 | 0.54 | −4.12×10⁻⁴ | 0.63 |

**Empirical Table 4 `c2` and `m1`–`m6` coefficients:**

| Position | c2 | m1 | m2 | m3 | m4 | m5 | m6 |
|---|---:|---:|---:|---:|---:|---:|---:|
| Top | **7.05** | −0.30 | −0.55 | −14.64 | 3.52×10⁻⁶ | −8.23×10⁻¹¹ | −5.35 |
| Bottom | **19.0** | −0.33 | −0.14 | −0.40 | 3.98×10⁻⁶ | −3.55×10⁻⁵ | −0.88 |

**Semi-empirical Table 4 coefficients** recorded separately:

| Position | c1 | n1,n2,n3,n4,n5,n6 | c2 | m1,m2,m3,m4,m5,m6 |
|---|---:|---|---:|---|
| Top | **2.56** | 13/24, 1/3, 1/3, 1/3, −2/3, 1 | **989** | −0.25, −0.15, −0.50, +0.35, −0.15, −0.60 |
| Bottom | **0.000406** | 13/24, 1/3, 1/3, 1/3, −2/3, 1 | **2.08** | −0.25, −0.15, −0.50, +0.35, −0.15, −0.60 |

The machine registry preserves tiny scientific-notation fitted exponents rather than replacing them with round values. They appear unusual, but no scientifically justified “cleaning” is performed on source-fitted coefficients. The semi-empirical and empirical families are kept individually labelled.

## 14.5 Unresolved Eq. (24) / Table 4 source ambiguity

A key scientific problem emerged during direct transcription: the original empirical Eq. (24), as visually recorded from the PDF, places the fitted Reynolds and Prandtl factors **in a denominator**, yet Table 4 gives **negative n1 and n2**. Under literal algebra:

```text
Re_b^0.8 / Re_b^(-0.50) = Re_b^1.30       [empirical top]
Pr_b^0.4 / Pr_b^(-0.36) = Pr_b^0.76
```

At representative dimensionless values `Re = 10^5`, `Pr = 2`, `Qb = 3` and averaged density/viscosity/conductivity ratios **0.7 / 0.8 / 1.2**, the **literal empirical forced Nusselt** is approximately **9.04 million**. Replacing the denominator placement by an *unverified numerator interpretation* `Re^(0.8+n1) Pr^(0.4+n2)` gives approximately **54.85** under the same illustrative inputs. This enormous discrepancy is very difficult to reconcile with the authors’ reported low source-study errors and plotted predictions, but **it does not by itself prove the equation has a typo or tell us how the authors actually evaluated it**.

Three H1d code paths therefore remain explicit:

| Variant ID | Scientific status | Meaning |
|---|---|---|
| `semi_empirical` | **Published source form** | Eqs. (23)/(29) with corresponding semi-empirical source coefficients |
| `empirical_literal` | **Literal printed interpretation** | Eq. (24) denominator exactly as printed, original signed Table 4 values and published natural component |
| `empirical_hypothesis` | **UNVERIFIED HYPOTHESIS** | Alternative empirical exponent placement as numerator correction, otherwise same published empirical coefficients |

The code may compare these alternatives as an equation-source audit. It **must not** silently call the hypothesis “Kim author verified”, splice coefficients from different versions, tune signed exponents on Stuttgart, or assert reproduction of the original 620-point source study. A correction notice or the original author’s numerical pointwise reference/code is necessary for that stronger claim.

# 15. H1d real-CO₂ numerical implementation, wall solve and held-out controls

## 15.1 Implemented software and solver interfaces

The draft implementation resides at [source `kim2019.py`](https://github.com/Open-Energy-Methods/sco2-braytonbench/blob/feat/g35d-kim2019-original-equation-benchmark/src/sco2_braytonbench/kim2019.py). It defines a typed CO₂ thermophysical state, a cached `CoolPropCO2Transport` callable, source coefficient registry reading/validation, temperature-integral property averages, safe log-space power products, labelled Nusselt-component evaluation, direct evaluation at a supplied wall state, and a separately called **flux-driven wall-temperature inverse**.

The wall balance is:

```text
F(Tw) = h_model(Tw ; P, Tb, q'', m_dot, D) * (Tw - Tb) - q'' = 0
```

The **prospective conditional mode does not supply measured wall T**. Instead it samples physically permitted heated-wall temperatures, scans for sign-change brackets, rejects absent or multiple sampled roots, performs bisection, and independently checks relative heat-flux closure. The default implementation has a declared finite maximum wall-temperature search around **650 K**, up to **36** bisection steps, and a relative heat-balance tolerance **0.002 (0.2%)**. The temperature scan begins very close to bulk temperature because the literal empirical equation can create extreme HTC values and correspondingly tiny temperature differences.

The finite scan is a reproducible engineering numerical method, **not a mathematical proof of global physical-root uniqueness**. A positive valid-looking bracket outside the original article’s fit region can still yield a physically inappropriate HTC. Brackets across invalid property intervals are not joined artificially. Excluded points carry explicit root/no-domain/failure reasons in the reports.

## 15.2 Direct mathematical and real-property verification

Independent equation tests cover the literal empirical and hypothesis expressions with hand-derived exponent algebra, the reciprocal natural component, the square-root forced/natural combination, original coefficient-sign integrity, temperature-integral averages of a known ideal-gas density function, exact sensible cp from enthalpy differences, rejection of HM orientation, invalid inputs, and an independently checked synthetic wall-root conservation identity. They use a deliberately artificial gas fixture for some exact checks and **do not assert real-CO₂ experimental accuracy**.

Real-fluid sensitivity tests examine fixed-pressure CO₂ near pseudocritical and higher-temperature intervals, comparing **coarser and denser Gauss-subinterval integration** for density, viscosity and conductivity with a tolerance on changes, while cp remains obtained from the exact backend enthalpy difference. CI separately executes `CoolProp==8.0.0` property-based tests. Report synthesis is also tested so wrong variant IDs, absent source populations, missing extrapolation warnings or inconsistent metadata cannot be published as valid summaries.

## 15.3 The unchanged Stuttgart provenance and original fit-domain mismatch

The H1d experiment driver regenerates the H1a/H1b source-based benchmark, reads exactly the **54 original Stuttgart experiments**, confirms source anomaly STU-001 remains excluded, confirms the original 18 nominal groups, verifies the source-split marker and four original holdouts, and uses the **2,318** H1b Jackson flux-inverted eligible stations as its downstream candidate inventory. It excludes **HM 738** by definition, and evaluates **HB 790 + HT 790 = 1580** source stations for the two orientations published by Kim. There are **356** original HB/HT candidate observations in the four held-out groups before model-specific root failures.

**Critical scientific mismatch:** the smallest reported Stuttgart heat flux is approximately **30.55 kW/m²**. Kim’s original POSTECH source reaches only **25.9 kW/m²** and the additional Adebiyi–Hall source reaches **26.9 kW/m²**. Consequently **all 1580 candidate Stuttgart stations lie beyond the published original-source maximum heat-flux envelope**. Even though some pressure conditions overlap, and Stuttgart includes an 8-mm diameter close to the POSTECH 7.75-mm diameter, this single definitive non-overlap makes the test **out-of-fit-domain extrapolation for every station**.

During the later code audit, an original POSTECH full-domain applicability flag was corrected to use only its proper **POSTECH P/G/q/D fields** rather than combining validity indicators for the additional dataset. This is a provenance and classification fix, not a change to source measurements or a Kim coefficient refit.

## 15.4 Measured-wall and flux-driven modes remain different data products

In **`measured_wall_conditioned`** mode, measured wall temperature is provided to the source equation; the resulting HTC is compared to the published reduced HTC. This can be useful for seeing whether the formula’s property dependence is consistent with the observed state, but it is **target-associated input leakage**, because `HTC_source = q''/(Twall_source - Tbulk_source)`.

In **`flux_driven_inverse`** mode, the measured source heat flux and source-derived bulk state are known, while wall temperature is solved from the model equation. This is stronger evidence of **conditional local prediction**, but it is still not fully independent of experimental inputs and is not a complete wall-conduction/geometry or Brayton-cycle simulation. No `q''` or thermodynamic state is freely predicted from a plant-wide heater and coolant model at H1d.

The algorithm reports each model’s successful sample count, convergence failures, local HTC errors, held-out errors, orientation/diameter errors, signed bias, family/run macro errors, paired Jackson/Bishop/Gnielinski errors where matching data exist, heat-balance residuals and source applicability flags. It does not project a successful-points MAPE onto rejected stations.

## 15.5 Original full candidate-set results, including failures

The first complete H1d experimental computation and later confirmed repeat generated:

| Flux-driven variant | Successful / 1580 | Overall MAPE on its own success set | HB MAPE | HT MAPE | Held-out MAPE on successes |
|---|---:|---:|---:|---:|---:|
| Semi-empirical, printed equations | **1573** | **52.56%** | 62.99% (790) | 42.03% (783) | 49.06% (356) |
| Empirical literal, original Table 4 signs | **1337** | **30,230,230.33%** | 46,604.28% (790) | 73,822,670.16% (547) | 24,407,694.81% (298) |
| Empirical **unverified** sign hypothesis | **1522** | **43.90%** | 42.46% (783) | 45.44% (739) | 36.84% (330) |

Root-failure inventory:

| Variant | Failed/unresolved | Breakdown established |
|---|---:|---|
| Semi-empirical | **7** | Root / heat-balance tolerance not satisfied |
| Empirical literal | **243** | No unique sampled physical root bracket |
| Empirical hypothesis | **58** | 45 unbracketed, 2 multiple observed brackets, 11 tolerance failures |

The measured-wall-conditioned overall diagnostics were **35.79% semi-empirical**, approximately **18,699,508% empirical literal**, and **21.32% empirical hypothesis**, each reported for the measured-wall-conditioned 1580 stations. They must **not** be used as the primary evidence of predictive performance simply because some are numerically lower. The conditioned variant has information from the target wall temperature.

The relative residual acceptance of the flux-driven wall equation is a **numerical convergence criterion** independent of the correlation MAPE. Even a numerical success with an enormous HTC MAPE is a successful inversion of a poor or inapplicable model, not a physically successful design calculation. The large difference in successful-root subsets also means the above three overall MAPE values are **not** a strictly fair model leaderboard.

# 16. H1d final common-station audit: corrected comparison and interpretation

## 16.1 Why additional post-benchmark work was necessary

The H1d three-way experiment runs initially completed and documented three individually calculated MAPE values. However, each formula had a **different numerical success population**, especially the printed literal empirical model, which could not find a unique physically scanned wall root for 243 of the 1580 candidates. A comparison of **52.56%, 43.90% and 30.23 million%** alone would mix predictions over 1573, 1522 and 1337 points. If failed roots correlate with the most difficult thermophysical conditions, ranking successful-points-only error could be systematically optimistic for a poorly robust method.

The H1d hardening therefore created [the common-support audit script](https://github.com/Open-Energy-Methods/sco2-braytonbench/blob/feat/g35d-kim2019-original-equation-benchmark/scripts/h1d_common_support.py) and [independent fixture tests](https://github.com/Open-Energy-Methods/sco2-braytonbench/blob/feat/g35d-kim2019-original-equation-benchmark/tests/test_kim2019_common_support.py). It reads all three source variant pointwise CSVs and their machine reports from the corresponding CI artifacts. For each variant it requires the correct 2318 H1b source total, 790 HB/790 HT/738 HM counts, the original no-fit flag and anomaly quarantine, the fixed original four holdouts, and the stated all-outside-fit heat-flux status. It rejects duplicate successful station keys, missing fields, nonfinite errors and cross-variant changes to source metadata.

Each record is identified by the **exact** `(experiment_id, axial_position_m, orientation)` tuple. The script selects the set intersection of the three successful-key sets, checks all common rows agree on nominal family, original split, diameter, source heat flux, experimentally reduced HTC and Jackson–Hall baseline error, and then calculates every Kim variant and Jackson on **the same station IDs**. It reports pointwise MAPE, signed bias, original held-out MAPE, HB/HT MAPE and equal-nominal-family macro MAPE. A seeded 3000-draw **between-family** bootstrap records comparative family variability; it is not experimental noise propagation or future equipment prediction intervals.

The specific regression fixture includes deliberately incomplete successful-root coverage, an altered-source metadata case and a duplicate station case. Its first test expectation mistakenly required **30%** for the mean of **10% and 40%** synthetic Jackson errors; this was corrected to **25%** in commit **`cf170a0`**. The preceding failure runs are retained as CI history rather than hidden.

## 16.2 Final matched-support experimental numbers

At the **exact final head** and [successful Actions run 42058735222](https://github.com/Open-Energy-Methods/sco2-braytonbench/actions/runs/42058735222), the common-support scientific-summary job printed:

- **1275 / 1580** original HB/HT candidate stations in the **three-way common root-success intersection** (approximately **80.7%** of candidates).
- **272** of those common stations belong to the original four predeclared held-out nominal families.
- All 1275 retained original source heat fluxes remain **above Kim's original 26.9 kW/m² maximum published heating range**.
- The matching comparison includes the previously computed **Jackson–Hall flux-driven** baseline on the **same IDs**, not an unmatched whole-sample aggregate.

| Flux-driven model on **identical 1275 stations** | Pointwise HTC MAPE | Equal-family macro MAPE | Held-out MAPE on 272 identical stations |
|---|---:|---:|---:|
| **Jackson–Hall** | **33.89%** | **35.31%** | **21.70%** |
| **Kim semi-empirical, published formula** | **54.39%** | **55.23%** | **52.67%** |
| **Kim empirical, printed literal interpretation** | **29,622,281.81%** | **33,696,878.32%** | **22,756,407.13%** |
| **Kim empirical, UNVERIFIED sign-placement hypothesis** | **45.73%** | **45.75%** | **37.54%** |

**This common-station comparison changes the defensible conclusion:** the tested Jackson–Hall flux-driven calculation has lower error than both the published semi-empirical Kim form and the unverified empirical sign hypothesis on this particular intersected Stuttgart set. The printed literal empirical interpretation remains catastrophically large. The apparent improvement of the unverified hypothesis over Jackson on its own 1522-point success population was **not sustained under this strict common-support ranking**.

This conclusion is deliberately narrow. The common set is formed from **root-convergence eligibility**, not a statistically random sample of the physical population. Removing 305 candidate IDs from the three-way intersection may change orientation and thermophysical distributions. The **failure rates themselves** are therefore part of model reliability. A small MAPE on a smaller source-selected set would not establish practical deployability. All points are out of Kim’s source heat-flux range, while Jackson’s own original application domain and lack of a genuine angular model remain limitations. No claim is made that Jackson is universally the better correlation under in-domain CO₂ mixed convection.

## 16.3 How the final result was actually evidenced

The exact-head [Actions run **42058735222**](https://github.com/Open-Energy-Methods/sco2-braytonbench/actions/runs/42058735222) completed **15/15 jobs successfully**. The `kim-h1d-summary` CI job ran the established three-model summary and the new `h1d_common_support.py` comparator, printed the common-support table above and uploaded eight files in the `g35d-kim-scientific-summary` artifact [**13431221211**](https://github.com/Open-Energy-Methods/sco2-braytonbench/actions/runs/42058735222/artifacts/13431221211). It includes:

```text
summary.md
summary.json
summary.csv
htc_mape_log_scale.svg
common_station_comparison.md
common_station_comparison.json
common_station_comparison.csv
common_station_errors.csv
```

The GitHub upload log recorded archive SHA-256:

```text
04fc30963789e325c49958bb557a2110be334db4c929f064b7808f76ff3cfef3
```

This hash identifies the **particular final scientific-summary ZIP artifact**, not the entire repository or original article. Each Kim variant also has a separate machine JSON/pointwise CSV artifact in the same workflow, making the statistics independently traceable to the code-produced station records. The exact final workflow additionally passed the two Python package suites, previous G3 real-fluid screens, G3.1/G3.2/G3.3 checks, H1a/H1b/H1c experimental jobs, CO₂ property verification and the final scientific aggregator.

**The latest verified H1d result is the common-support table, not the earlier “pending verification” note in the historical PR body.** Historical files and comments may retain their original timing. The final CI has subsequently resolved that pending execution status; it has **not** resolved the scientific source/fit-domain blockers.

# 17. Independent physical validation sources and why they were not admitted as new HTC points

## 17.1 TU Delft horizontal CO₂ stratification: strong physical context, incompatible geometry

The later project [independent source-triage note](https://github.com/Open-Energy-Methods/sco2-braytonbench/blob/feat/g35d-kim2019-original-equation-benchmark/docs/G35D_INDEPENDENT_VALIDATION_SOURCE_TRIAGE.md) records **Draškić, Westerweel and Pecnik (2025)**, *The stability of stratified horizontal flows of carbon dioxide at supercritical pressures*, *Journal of Fluid Mechanics* 1012, A17, DOI [10.1017/jfm.2025.10162](https://doi.org/10.1017/jfm.2025.10162), with a [TU Delft open repository record](https://repository.tudelft.nl/record/uuid:ab5dcd17-55d8-49fb-b5c1-673566b77974).

The relevant experimental physics is separate **top versus bottom wall heating** of horizontal supercritical CO₂: **bottom heating** can create unstable buoyancy and thermally driven plumes/vertical mixing, whereas **top heating** can produce stable stratification and suppressed vertical transport. This is valuable independent qualitative support for why a simple wall-orientation-blind closure might fail.

However, the experiment uses an optically accessible **rectangular horizontal channel** with one-sided top or bottom heating, not Kim’s fully circular uniformly heated pipe and circumferential generatrices. A source with approximately 88.5-bar pressure, 32.6-°C inlet and heating up to the cited order of 12 kW/m² does **not** create a direct local Kim top/bottom circular-tube HTC benchmark by itself. The reviewed open material did not establish a complete licensed pointwise dataset carrying the necessary `P, G, q'', D, Tb, inner Tw, HTC, uncertainties` records and the same geometry. Source pictures and movies are physical evidence, not numerical CSV. Consequently **no Delft observation was added to the 1275-station MAPE**.

## 17.2 Cheng, Wang and Xu (2024): circular-tube follow-up candidate

The source-triage note also identifies **Cheng, Wang and Xu (2024)**, *Supercritical heat transfer of CO₂ in horizontal tube emphasizing pseudo-boiling and stratification effects*, *International Journal of Heat and Mass Transfer* 220, 124953, DOI [10.1016/j.ijheatmasstransfer.2023.124953](https://doi.org/10.1016/j.ijheatmasstransfer.2023.124953). Its published study concerns an approximately **10-mm circular tube** over a broad pressure range **7.531–20.513 MPa**, with mass flux **496.7–1346.2 kg/(m² s)** and heat flux approximately **97.4–400.3 kW/m²**, and discusses differing top and bottom thermal responses and stratification.

This is geometrically closer to Kim/Stuttgart than the TU Delft rectangular channel, but it remains significantly different from Kim’s source fit range, and a usable permission-cleared pointwise original data package was **not established** in the H1d audit. The paper’s abstract or plotted wall temperatures alone must not be rewritten as invented measured HTC records. It is a **priority dataset-retrieval candidate**, not a completed external quantitative model check.

## 17.3 Other relevant literature paths

The research issue also flags **Park and Kim (2022)**, *Modeling of local heat transfer on supercritical pressure CO₂ in horizontal semicircular tube*, *International Journal of Heat and Mass Transfer* 184, 122197, DOI [10.1016/j.ijheatmasstransfer.2021.122197](https://doi.org/10.1016/j.ijheatmasstransfer.2021.122197). The half-round channel/hydraulic diameter make it conceptually closer to some PCHE channels than a perfectly circular pipe, but it still needs exact source equations, geometry and pointwise experimental support before use. **Xie, Gong and Wang (2025)**, *Experimental investigations on heat transfer to highly buoyant sCO₂ flows in a large horizontal tube*, DOI [10.1016/j.icheatmasstransfer.2025.108725](https://doi.org/10.1016/j.icheatmasstransfer.2025.108725), was listed as another prospective experimental source; its complete usable stationwise data and licence were **not verified**.

## 17.4 Minimum acceptance packet for independent quantitative tests

A future independent experiment must provide original point/experiment identifiers; a definitive source licence and downloadable data files; measured pressure, temperature, mass flow or mass flux, tube/channel cross-section and hydraulic diameter; heating flux with **precise wetted-area convention**; axial locations; bulk-state reduction; measured or appropriately conduction-corrected **inner-wall temperatures** at known top/bottom positions; independently reduced local HTC and instrument/reduction uncertainty/covariance; and the distinction between imposed source heat flux and wall-conduction losses.

The frozen as-published Kim variant should then be run **without fitting on the external test**. Report all failed roots, both orientations, diameter/pressure/heat-flux applicability, paired conventional baselines on identical IDs, nominal-experiment uncertainty and group-level error. Only after original-study parity and more than one truly independent physical regime are established should the research consider using an HTC closure to infer equipment installed UA. This is the proper order of validation; multiplying an out-of-domain correlation by a tuned factor based on all Stuttgart families would be poor science.

**Gate:** physical mechanism context identified and documented; independent H1d *quantitative* validation remains **OPEN**.

# 18. Verification system, CI evidence and reproducibility philosophy

## 18.1 Why the project has separate numerical and physics gates

The project’s strongest engineering process decision has been to require **several different forms of evidence**. The classes should not be collapsed:

1. **Algebraic source verification** — tests that SI-unit conservation, sign conventions, exponent arithmetic, enthalpy differences, segment and reference-state transformations are calculated as intended.
2. **Numerical verification** — root brackets, tolerances, local quadrature refinement, mesh sensitivity and robust finite-property errors.
3. **Software regression verification** — package installation, Python-version compatibility, consistent input provenance, reproducible scripts, no state/group leakage, CSV/JSON output contracts.
4. **Measurement-based component validation** — residuals relative to physical experimental observations whose uncertainties and source conditioning are known.
5. **System-level physical validation** — whole assembled equipment with known geometry, correlated source/sink conditions, installed UA and pressure maps, transients and independent measurement.

G1/G3/G3.5 H1a–H1d have various successes in the first four categories. The project has **not** met the fifth category. In particular, an HTC correlation selected from single horizontal pipes is not automatically a PCHE, turbine or whole Brayton-cycle constitutive relation.

## 18.2 Major CI execution ledger

The table below gives representative historically executed records, not a claim that each job was independently run under the *current* latest branch unless indicated. Each cited run is a distinct historical software snapshot.

| Work stage | Executed workflow | Noteworthy recorded evidence |
|---|---|---|
| Early FR2016 comparison | [41991703407](https://github.com/Open-Energy-Methods/sco2-braytonbench/actions/runs/41991703407) | 64 analytic fixture passes, 46 dedicated real-fluid checks; conceptual source/segmentation sensitivity |
| Density-screen tightening | [41993973281](https://github.com/Open-Energy-Methods/sco2-braytonbench/actions/runs/41993973281) | 49 measured density points; 73 fixture tests and 61 real-fluid tests in documented jobs |
| G3 finite source | [41999222234](https://github.com/Open-Energy-Methods/sco2-braytonbench/actions/runs/41999222234) | 4 successful jobs; 20-point screen, feasibility/robustness CSV and JSON |
| G3.1 installed heater UA | [42002609837](https://github.com/Open-Energy-Methods/sco2-braytonbench/actions/runs/42002609837) | 5 successful jobs; fixed-UA root residuals and gas-temperature perturbation |
| G3.2 dual-UA cycle | [42005964249](https://github.com/Open-Energy-Methods/sco2-braytonbench/actions/runs/42005964249) | 6 successful jobs; 178 fixture test passes per Python version and coupled coolant response |
| G3.3 property/mesh | [42010735595](https://github.com/Open-Energy-Methods/sco2-braytonbench/actions/runs/42010735595) | 35 dedicated tests; 205 fixture passes per version; 6/12/24/48 section output |
| Stuttgart H1a | [42031845343](https://github.com/Open-Energy-Methods/sco2-braytonbench/actions/runs/42031845343) | 2318 station baseline HTC statistics and pointwise records |
| Stuttgart H1b | [42035909213](https://github.com/Open-Energy-Methods/sco2-braytonbench/actions/runs/42035909213) | Bishop/Jackson modes and paired physical-family audit |
| Stuttgart H1c | [42040967963](https://github.com/Open-Energy-Methods/sco2-braytonbench/actions/runs/42040967963) | 1580 converged Lei flux inversions, negative transfer metrics |
| Integration PR #18 | [42047607493](https://github.com/Open-Energy-Methods/sco2-braytonbench/actions/runs/42047607493) | Consolidation/source-registry branch successful |
| Postmerge `main` | [42049395268](https://github.com/Open-Energy-Methods/sco2-braytonbench/actions/runs/42049395268) | Merged `main` baseline confirmed successful |
| Early complete H1d | [42053984073](https://github.com/Open-Energy-Methods/sco2-braytonbench/actions/runs/42053984073) | Three original Kim variant computations completed, with source-domain flags |
| H1d report and tests | [42055736197](https://github.com/Open-Energy-Methods/sco2-braytonbench/actions/runs/42055736197) | **15/15 successful jobs** at earlier H1d head |
| **Final common-station H1d head** | [**42058735222**](https://github.com/Open-Energy-Methods/sco2-braytonbench/actions/runs/42058735222) | **15/15 successful**, final original-support intersection, exact common model scores and eight-file scientific artifact |

Several intermediate H1d workflow runs failed while the common-support testing code was changing. Their existence is not hidden or interpreted as proof that the final corrected head failed. **The exact head SHA and final job conclusion** are what matters for asserting green CI. Future work should similarly avoid copying a green badge from an older commit onto newer, untested source code.

## 18.3 Final H1d workflow job families

The latest successful 15-job matrix included: `test (3.11)` and `test (3.12)`; `co2-property-smoke`; `whr-design-screen`; `fixed-installed-heater-ua`; `coupled-heater-cooler`; `reference-properties-hydraulic`; `g33-component-convergence`; `stuttgart-h1`; `stuttgart-h1b-property-correlations`; `stuttgart-h1c-lei-orientation`; the **three** `Kim H1d` variants; and the dependent `kim-h1d-summary` job. The last summary job only completed after consuming the three separately generated Kim artifacts.

This is a useful reproducibility architecture because the scientific summary does not require copying remembered numbers into source code. It reopens data products generated from the current experiment source and validates the original inventory, no-fit/provenance markers and heat-flux extrapolation accounting before composing tables.

## 18.4 How to understand CI artifacts

GitHub Actions artifacts are machine-generated, downloadable research evidence tied to a **specific workflow and commit**, and may be subject to GitHub retention. Their URLs are important references but not immutable journal archives. The report therefore preserves exact numeric summary values and artifact IDs as text. A proper future public research release should package selected non-copyright-restricted **source datasets, parameter schemas, environment lock/requirements, scripts, expected numerical checksums and manifest hashes** under a stable tagged version and, if appropriate, a research-data DOI. It should not rely exclusively on transient Actions artifacts.

# 19. Scientific uncertainty, methodological pitfalls and current risk register

## 19.1 Four fundamentally different uncertainty sources

**Measurement/reduction uncertainty.** Stuttgart HTC is reduced from a heat input, bulk enthalpy evolution and wall/bulk temperatures. Errors in any of those can be correlated, especially when local wall-temperature measurement, heat loss, wall conduction or calculated bulk state enters the same expression. Source-reported local HTC sigma values are important but cannot be blindly treated as independent normal-distribution standard deviations for every input. No full joint instrument covariance, between-run systematic bias or inverse wall-conduction uncertainty has been propagated through H1a–H1d.

**Numerical approximation uncertainty.** Heat-exchanger discretisation, CoolProp thermodynamic inversions, quadrature near pseudocritical peaks and wall-root search widths can change outputs without changing the underlying physical equations. The project has narrowed these at selected cases; it has not demonstrated verified global Newton/bisection uniqueness or high-order grid convergence across all cycle conditions and all near-critical heat-transfer regimes. The early Lei wall-root width failure demonstrates why convergence needs explicit evidence rather than implicit reliance on successful script termination.

**Constitutive/model-form uncertainty.** Artificial constant-cp gas, installed UA chosen from a synthetic reference point, assumed turbine/compressor efficiencies, estimated pressure loss and published water/CO₂ empirical heat-transfer correlations represent models, not direct geometry or CFD-resolved actual flow. The greatest H1d issue is not a 0.1% numerical tolerance: it is possible **source-equation sign-placement ambiguity** and **out-of-calibration heat-flux extrapolation for the entire Stuttgart sample**. Neither can be solved by making the numerical solver faster or increasing test count.

**Source provenance / selection uncertainty.** A figure digitisation, simulated CFD workbook, model-corrected turbine state, experimental HTC reduction and direct temperature measurement have different epistemic standing. Source anomalies and the H1d nonrandom missing-root intersection can affect apparent averages. Fixed original physical-family groups are necessary; a group bootstrap describes observed family-to-family variability and is not a new independent rig population or lab instrument distribution.

## 19.2 Explicit priority risks

| Priority | Risk | Present evidence | Required mitigation / release implication |
|---|---|---|---|
| **Critical** | Kim published empirical Eq.24/negative Table 4 signs are inconsistent under literal reading | Literal prediction ~30 million% MAPE; alternative remains unverified | Obtain authoritative correction or original 620-point reference code/data; do not select as validated physical closure |
| **Critical** | All Stuttgart q'' exceed Kim original 26.9-kW/m² source envelope | Observed candidate minimum ~30.55 kW/m²; 1580/1580 out of source fitting range | Acquire independent in-range CO₂ measurements; label Stuttgart results extrapolation only |
| **High** | H1d failed roots are nonrandom and differ by formula | 7 semi, 243 literal, 58 hypothesis failures; 1275 three-way intersection | Retain all failure causes and coverage; perform bounded solver sensitivity without dropping failures |
| **High** | Source HTC target shares measured wall T and heat flux with conditioned formula | Strong reduction identity; conditioned scores much smaller in several modes | Never use conditioned MAPE as prospective design accuracy; keep flux-driven reporting primary |
| **High** | Single circular-tube HTC is not a PCHE UA | Missing actual channel geometry, wall conduction, opposite-side h, fouling and flow distribution | Geometry-specific thermal resistance and measured exchanger tests before plant coupling |
| **High** | Detailed 2016 EES model is underdetermined | Figure 4 branch states and original ~400 equations unavailable | Retain conceptual-only paper comparison; request publication-cleared state ledger if practical |
| **High** | Installed UA was sized from the same nominal model | G3.1/3.2 synthetic inverse construction | Calibrate on independent measured geometry, duty, temperatures and flows before industrial inference |
| **High** | Machine maps and auxiliaries absent | Constant efficiencies and nominal pressure losses | Add source-verified compressor/turbine maps, speed dependence, cooling/pump work |
| **Medium** | Source article/cell anomalies and inconsistent PCHE U | STU-001 original q ~833 vs ~91.7; ZH-001 U calculation mismatch | Preserve original raw cells, source flags and author/source corrections, never overwrite silently |
| **Medium** | Local near-critical property accuracy beyond density remains under-tested | 49 measured density points but no comparable independent h/s/cp/transport coverage | Broader independent property dataset and uncertainty analysis |
| **Medium** | GitHub Actions artifact retention and outdated docs | Main and PR branch document histories; generated files are artifacts | Tag frozen reproducible milestones, archive permitted evidence and maintain a current research status index |
| **Low-to-medium** | Software API/algorithm changes may regress earlier stages | Multi-stage CI currently green; historical source vs current docs sometimes differ | Version interfaces and numerical source manifests; retain cross-stage CI on each PR |

A **release gate** should be tied to the concrete claim being made. Releasing the code as a **research alpha with documented negative and partial validation** is potentially appropriate after maintainers review its documentation and provenance. Promoting it as a physically validated CO₂ PCHE sizing or Brayton-cycle control system is **not** justified by this record.

# 20. Research stage-gate status as of the evidence cutoff

| Gate / milestone | Scientific acceptance status | Explanation |
|---|---|---|
| G0: original-source mapping | **PARTIAL** | Friedman–Rapp conceptual and source pressure ledger documented; original Figure 4 EES source absent |
| G1-A: analytic conservation / basic components | **PASSED for declared tests** | Analytical gas/HX fixtures, source and pressure relations, energy closure checked |
| G1-E: CO₂ EOS property confidence | **PARTIAL** | 49 real measured densities and software consistency passed; not independent full h/s/cp validation |
| G2: original detailed source-model parity | **OPEN** | 400-equation EES model and state/branch ledger not recovered |
| G3: finite-source screen | **PARTIAL exploratory** | Sourced methodology and real-fluid grid executed; no global optimiser or measured source |
| G3.1: installed gas-heater UA | **Numerical test PASSED; physical validation OPEN** | Synthetic fixed-UA roots and source perturbations checked |
| G3.2: installed heater + cooler UA | **Numerical test PASSED; physical validation OPEN** | Synthetic coolant perturbation, energy and residuals checked |
| G3.3: reference streams and mesh | **Narrow component checks PASSED; broader proof OPEN** | NIST/Water/friction and 2 prescribed-state 6/12/24/48 checks |
| G3.4: external source intake | **Structural QC PASSED; component validation OPEN** | Seven source categories and source anomalies preserved |
| G3.5 H1a: Stuttgart baseline | **Pipeline PASSED; physical HTC accuracy POOR** | Complete original inventory and 2318-point Gnielinski/DB benchmark |
| G3.5 H1b: property-aware correlations | **Equations / tests PASSED; predictive HTC validation OPEN** | ~46–49% global flux-driven MAPE, high top-wall error |
| G3.5 H1c: Lei orientation transfer | **Numerical evaluation PASSED; physical transfer FAILED** | 1580 converged CO₂ inversions, 631.72% MAPE |
| G3.5 H1d: Kim source implementation | **Source retrieval and numerical CI PASSED** | Three variant implementations and matched-support audit completed |
| H1d source-study model parity | **OPEN** | Original empirical source ambiguity and 620-point data/code not recovered |
| H1d independent in-domain validation | **OPEN** | All Stuttgart points out of original heat-flux fitting range |
| H1d industrial HX/PCHE UA | **NOT VALIDATED** | No actual channel/wall/flow calibration against a complete exchanger |
| G4 transient plant dynamics | **NOT IMPLEMENTED** | No mass, shaft, wall, source/sink inventories or time integration system |
| G5 PI/MPC system | **NOT IMPLEMENTED** | No physical actuators, safety constraints, plant dynamics, observed control response |
| G6 techno-economics | **NOT IMPLEMENTED** | No measurement-grounded hardware costs, plant duty/annual availability, LCOE or optimisation |

**The correct overall descriptor remains `0.5.0-alpha`: a reproducible scientific computation and benchmark framework with real discoveries and negative transfer studies, not an experimentally validated industrial digital twin.**

# 21. Planned next research sequence and precise acceptance criteria

## 21.1 P0 — preserve a clean reproducible archival baseline

**Objective:** keep the completed H1a–H1d methods and observed negative results auditable without losing scientific nuance or depending indefinitely on short-lived Actions artifacts.

Actions: capture the current `main` SHA and H1d draft head; archive the latest CI job list, source input file digests and summary artifact digest; document all original licences; make the final H1d same-station table and failed-root coverage prominently visible; update PR #19 and Issue #17 to say final common-support CI is **green**, but source/physics gates remain **open**. Keep the model variations clearly separated. Add a current release-gate status file rather than changing author-original historical reports retroactively without marking the date.

**Acceptance:** one reproducibility manifest with package/CO₂ backend versions, exact data identifiers, source coefficients, original four held-out keys, expected candidate counts, exact station-level output hashes and report-generation commands; no false claims of physical validity.

## 21.2 P1 — resolve Kim empirical Eq.24 authenticity before adding new fitted physics

**Objective:** establish which, if any, interpretation of empirical Eq.24 was actually used for the original paper’s low reported error.

First, independently inspect the original PDF formula/typography and Table 4 numerical layout again, looking for multiplication signs, implicit bracket semantics, exponents, proof revisions or published corrigenda. A quantitative source reference is superior: recover the original **620-point** pointwise source records or a small authorised input/output example from the authors’ implementation, then compare published `Nu_forced`, `Nu_natural`, `Nu_mixed` and HTC before any Stuttgart exercise. Maintain source PDF copyright restrictions and do not infer author confirmation from plausibility alone.

**Acceptance:** at least one unambiguous published/authoritative source equation convention, verified property reference definitions, exact coefficient mapping, and independent original-study per-point predictions reproducing the relevant Table 6 metric within a declared tolerance. If this cannot be achieved, preserve `empirical_literal` and `empirical_hypothesis` as **source-interpretation research branches**, not as production CO₂ models.

## 21.3 P2 — improve H1d root robustness without hiding failures

Study the sensitivity of candidate root existence to temperature-envelope boundaries, small-gap sampling, quadrature subdivision, property phase/critical-region validity and bisection width. For each original candidate record, preserve whether no bracket, multiple sampled brackets, property invalidity or iteration tolerance caused exclusion. Do **not** artificially impute a model wall temperature for a failed root. A separate monotonicity/interval study, if possible, should distinguish observed numerical uniqueness from a proved mathematical property.

**Acceptance:** compare root coverage and HTC stability under a predeclared finite set of solver settings; retain identical original candidate denominator and four source-family holdouts; publish every source station’s inclusion/exclusion and numerical energy balance. This is a numerical-stability milestone, not source-domain validation.

## 21.4 P3 — obtain truly independent in-domain CO₂ heat-transfer data

Prioritise usable pointwise horizontal CO₂ top/bottom experimental data **within Kim’s original heat flux range** and with all pressure, geometry and wall-heating details needed for the original equations. If different geometries or heat-flux regimes are used, label them **transferability experiments** and report source-domain distances. TU Delft is strong for physical directionality but rectangular geometry means qualitative use; Cheng et al. and Xie et al. are more comparable circular-tube leads if pointwise data/rights become available.

**Acceptance:** source checksum, original-source licence, unaltered raw table, independent research-group provenance, measured/derived variable classification, uncertainty/covariance document, exact station-matched benchmarks and no retuning on the test set. Only then can a source-authentic correlation be credibly discussed as validated over a *specified* CO₂ envelope.

## 21.5 P4 — bridge the gap from pipe HTC to geometry-specific exchanger conductance

A physical `UA` is governed by gas-/CO₂-/coolant-side heat transfer, internal/external wetted surface area, actual wall material/conduction, channel count, thermal development, pressure loss, roughness, manufacturing geometry, fouling, flow maldistribution and thermal boundary conditions. A single local circular pipe `h` is not a PCHE effective U. Select a **geometry-specific independently documented** PCHE/sCO₂ heat-exchanger dataset, resolve discrepancies such as ZH-001, and build a complete resistance-network/segmented energy balance with source-appropriate boundary conditions. Include finite opposite-side stream enthalpy and source/sink temperature approach, without invented channel dimensions.

**Acceptance:** prediction of several **independent measured** exchanger duties and inlet/outlet temperatures at frozen geometry and both-flow conditions, agreement within specified experimental uncertainty or transparent model-form error, observed pressure-loss comparison and validated local mesh/energy balances. A standalone model-to-model CFD crosscheck is useful but **not** sufficient for experimental PCHE acceptance.

## 21.6 P5 — full G3 installed-UA and turbomachinery off-design evidence

Combine the validated source/sink streams and exchanger relations with measured compressor/turbine maps (corrected flow, pressure ratio, speed, isentropic efficiency, leakage and applicable corrected states). Introduce geometry-based pressure losses only when real geometry is provided, and realistic dry-air/flue-gas mixture properties when actual exhaust composition is known. Test grid convergence and operating-point stability across near-critical variations, source/sink extremes, flow limits and feasible pinch margins. Include cooling pumps/fans and electrical/generator conversion only after an equipment basis exists.

**Acceptance:** true independent multi-point pressure/temperature/flow/power comparisons from a traceable rig or published integrated plant, proper measurement/reference-state alignment, conservation, numerical convergence and quantified model error. Do not claim a CARBOSOLA digital twin unless legitimate facility-specific measured states and a documented calibration protocol are actually available.

## 21.7 P6 — only then consider transient plant and controls

A dynamic CO₂ Brayton plant requires material/energy inventories, wall thermal capacitance, source/sink dynamics, compressor/turbine rotational inertia, recirculation and valves, compressor surge/choke constraints, heat-transfer lag and controllable actuators. A PI or MPC design requires an independently verified dynamic model, a control variable/actuator mapping, safe operating envelope, initialization and measured or credible test trajectories. A steady-state gas-temperature perturbation is **not** a dynamic response and cannot identify a controller.

**Acceptance:** conservation-respecting dynamic equations, independently checked time integration, physically plausible disturbance trajectories, actuator limits/safety interlocks and validated closed-loop performance at multiple independent dynamic operating points. Economic optimisation follows when capex/opex and plant energy availability are evidenced.

# 22. Reproduction instructions for future maintainers

## 22.1 Starting from the frozen integrated baseline versus draft H1d

For **G0–H1c** integrated work, use `main` at `217bb27b...` rather than an arbitrary future default-branch head if exact historic reproduction is required. For **H1d**, explicitly check out `feat/g35d-kim2019-original-equation-benchmark` at commit **`cf170a07a4e02d190d03c986f103f642aea4ca59`** and verify that the original branch still exists. Do not accidentally report H1d code as already merged into the 2026-11-05 `main` snapshot.

```bash
git clone https://github.com/Open-Energy-Methods/sco2-braytonbench.git
cd sco2-braytonbench
# For integrated foundation through H1c:
git checkout 217bb27b71a2162c0a75e4e1c3f521b0073a8318

# OR: For full H1d research branch at the audited head:
git checkout cf170a07a4e02d190d03c986f103f642aea4ca59

python -m pip install -e '.[test,co2]' 'CoolProp==8.0.0'
python -m pytest -q
```

**Optional dependency note:** `pyproject.toml` formally permits a CoolProp version range (`>=6.6,<9`) for general installation, but **the verified research calculations intentionally pin 8.0.0**. Reproducing an experimental comparison on a later backend version without rerunning validation is a new computation, not the frozen published result.

## 22.2 Executed script sequence and dependency order

The H1d source workflow regenerates H1a and H1b baselines as inputs before running the Kim variants. The commands at the research branch are:

```bash
python scripts/fr2016_diagnostic.py
python scripts/fr2016_sensitivity.py
python scripts/fr2016_identifiability.py
python scripts/co2_measured_density_report.py
python scripts/whr_design_screen.py
python scripts/fixed_ua_coupled_demo.py
python scripts/coupled_sink_demo.py
python scripts/g33_component_mesh_sensitivity.py

python scripts/stuttgart_h1.py
python scripts/stuttgart_h1b.py
python scripts/stuttgart_h1b_paired_audit.py
python scripts/stuttgart_h1c.py

python scripts/stuttgart_h1d.py --variant semi_empirical
python scripts/stuttgart_h1d.py --variant empirical_literal
python scripts/stuttgart_h1d.py --variant empirical_hypothesis
```

The **three-way H1d aggregation** expects the three CI-produced variant artifacts under a collected folder. The workflow’s `actions/download-artifact` step retrieves separately named `g35d-kim-*` artifacts into `evidence/kim-h1d-collected`, maintaining variant directories. The aggregator then runs:

```bash
python scripts/kim_h1d_summary.py
python scripts/h1d_common_support.py
```

When reproducing locally outside GitHub Actions, download the [final three variant artifacts and summary](https://github.com/Open-Energy-Methods/sco2-braytonbench/actions/runs/42058735222) and preserve the respective expected directory layout. The aggregator uses **actual JSON/CSV** and verifies original source controls; it cannot manufacture missing experimental input records. Every generated `evidence/generated` output should be labelled with the commit, backend version, data-source hash and command used.

## 22.3 Local source-verification tests

```bash
python -m pytest -q \
  tests/test_kim2019_source_registry.py \
  tests/test_kim2019_model.py \
  tests/test_kim2019_real_co2.py \
  tests/test_kim2019_summary.py \
  tests/test_kim2019_common_support.py
```

The repository-wide test suite contains analytic fixtures and optional real-fluid tests. A fixture-only Python CI job may legitimately skip real-CO₂ modules if that job does not install CoolProp; the **separate dedicated real-CO₂ jobs** must be checked before claiming the full source calculation ran. A local `pytest` success on a minimal dependency installation is not equivalent to execution of all experiment scripts.

# 23. Citation, source-of-truth and archival index

## 23.1 Primary software and research-status pages

| Reference | Permanent logical role |
|---|---|
| [GitHub repository](https://github.com/Open-Energy-Methods/sco2-braytonbench) | Source code, issue/PR history, CI links and package licence |
| [README](https://github.com/Open-Energy-Methods/sco2-braytonbench/blob/main/README.md) | Integrated foundation descriptions and current public entry point |
| [Research status](https://github.com/Open-Energy-Methods/sco2-braytonbench/blob/main/docs/RESEARCH_STATUS.md) | Historical gated status, caveats and numerical result log through H1c |
| [PR consolidation audit](https://github.com/Open-Energy-Methods/sco2-braytonbench/blob/main/docs/PR_CONSOLIDATION_AUDIT.md) | Nine stacked research PRs, source-head and merge history |
| [PR #18](https://github.com/Open-Energy-Methods/sco2-braytonbench/pull/18) | Approved integrated software baseline, source recovery |
| [PR #19](https://github.com/Open-Energy-Methods/sco2-braytonbench/pull/19) | **Draft** Kim H1d implementation and new source audit |
| [Issue #17](https://github.com/Open-Energy-Methods/sco2-braytonbench/issues/17) | Original-source/physical validation blockers and decisions |
| [Final H1d Actions](https://github.com/Open-Energy-Methods/sco2-braytonbench/actions/runs/42058735222) | Latest executed 15/15 green CI run, exact head SHA |
| [Final H1d scientific summary artifact](https://github.com/Open-Energy-Methods/sco2-braytonbench/actions/runs/42058735222/artifacts/13431221211) | Matched comparison and individual-summary output files |

## 23.2 Methods and numerical-results documentation

- [Friedman–Rapp 2016 conceptual comparison](https://github.com/Open-Energy-Methods/sco2-braytonbench/blob/main/docs/FR2016_COMPARISON_REVIEW.md) and [original EES source-recovery record](https://github.com/Open-Energy-Methods/sco2-braytonbench/blob/main/docs/FR2016_ORIGINAL_MODEL_RECOVERY.md).
- [Measured-density result and decision](https://github.com/Open-Energy-Methods/sco2-braytonbench/blob/main/docs/EXPERIMENTAL_DENSITY_DECISION.md).
- [G3 waste-heat screen](https://github.com/Open-Energy-Methods/sco2-braytonbench/blob/main/docs/G3_STEADY_SCREENING_RESULTS.md).
- [G3.1 fixed heater UA](https://github.com/Open-Energy-Methods/sco2-braytonbench/blob/main/docs/G31_FIXED_UA_NUMERICAL_RESULTS.md).
- [G3.2 finite coolant dual UA](https://github.com/Open-Energy-Methods/sco2-braytonbench/blob/main/docs/G32_NUMERICAL_VERIFICATION.md).
- [G3.3 NIST/Water/mesh](https://github.com/Open-Energy-Methods/sco2-braytonbench/blob/main/docs/G33_NUMERICAL_VERIFICATION.md).
- [G3.4 external-source QC](https://github.com/Open-Energy-Methods/sco2-braytonbench/blob/main/docs/G34_EXTERNAL_VALIDATION_INTAKE.md).
- [H1a Stuttgart original baseline](https://github.com/Open-Energy-Methods/sco2-braytonbench/blob/main/docs/G35_STUTTGART_RESULTS.md).
- [H1b Bishop/Jackson](https://github.com/Open-Energy-Methods/sco2-braytonbench/blob/main/docs/G35B_RESULTS.md).
- [H1c Lei negative transfer](https://github.com/Open-Energy-Methods/sco2-braytonbench/blob/main/docs/G35C_LEI_RESULTS.md).
- [Kim original-source audit](https://github.com/Open-Energy-Methods/sco2-braytonbench/blob/main/docs/KIM2019_ORIGINAL_SOURCE_RECOVERY.md).
- [H1d research method](https://github.com/Open-Energy-Methods/sco2-braytonbench/blob/feat/g35d-kim2019-original-equation-benchmark/docs/G35D_KIM2019_BENCHMARK.md), [H1d executed report](https://github.com/Open-Energy-Methods/sco2-braytonbench/blob/feat/g35d-kim2019-original-equation-benchmark/docs/G35D_RESULTS.md), and [independent source triage](https://github.com/Open-Energy-Methods/sco2-braytonbench/blob/feat/g35d-kim2019-original-equation-benchmark/docs/G35D_INDEPENDENT_VALIDATION_SOURCE_TRIAGE.md).

## 23.3 Important external source DOIs

| Scientific source | DOI / canonical identifier | How this project actually used it |
|---|---|---|
| Mantilla et al. (2010) CO₂ density | [10.1021/je1001158](https://doi.org/10.1021/je1001158) | **Direct independent measured-density regression** (49 points) |
| Friedman & Rapp (2016) | [2016 symposium Paper 051](https://www.sco2symposium.com/papers2016/SystemModeling/051paper.pdf) | **Conceptual** source-mapped 12-state comparison; not full EES reproduction |
| NIST dry-air coefficients | [N₂ WebBook](https://webbook.nist.gov/cgi/cbook.cgi?ID=C7727379&Mask=1), [O₂ WebBook](https://webbook.nist.gov/cgi/cbook.cgi?ID=C7782447&Mask=17) | Published sensible-property source values |
| Theologou et al. (2022) data | [10.17632/4mvk4nxrkz.1](https://doi.org/10.17632/4mvk4nxrkz.1) | **Original external Stuttgart source**, H1a–H1d |
| Theologou et al. (2022) article | [10.1016/j.energy.2022.124171](https://doi.org/10.1016/j.energy.2022.124171) | Heat-transfer and buoyancy source equations/context |
| Lei et al. (2017) | [10.1016/j.ijheatmasstransfer.2017.06.052](https://doi.org/10.1016/j.ijheatmasstransfer.2017.06.052) | Original **water**-fit top/bottom transfer stress test |
| Kim et al. (2019) | [10.1016/j.ijheatmasstransfer.2018.11.075](https://doi.org/10.1016/j.ijheatmasstransfer.2018.11.075) | Original CO₂ model source audit, three interpretations and Stuttgart extrapolation |
| Zhang et al. (2022) PCHE | [10.3389/fenrg.2022.835224](https://doi.org/10.3389/fenrg.2022.835224) | External-source QC with open `U` discrepancy, not plant calibration |
| HZDR PCHE data | [10.14278/rodare.3928](https://doi.org/10.14278/rodare.3928) | Numerical/economic evidence intake, not measured CARBOSOLA validation |
| Draškić et al. (2025) | [10.1017/jfm.2025.10162](https://doi.org/10.1017/jfm.2025.10162) | Independent qualitative buoyancy physics; non-equivalent rectangular geometry |
| Cheng et al. (2024) | [10.1016/j.ijheatmasstransfer.2023.124953](https://doi.org/10.1016/j.ijheatmasstransfer.2023.124953) | Potential additional circular-tube experiment; pointwise validation not performed |
| Xie et al. (2025) | [10.1016/j.icheatmasstransfer.2025.108725](https://doi.org/10.1016/j.icheatmasstransfer.2025.108725) | Literature/data-retrieval candidate only |
| Park & Kim (2022) | [10.1016/j.ijheatmasstransfer.2021.122197](https://doi.org/10.1016/j.ijheatmasstransfer.2021.122197) | Future semicircular PCHE-relevant research candidate |

# 24. Final preservation statement

As at **5 November 2026**, **sCO₂-BraytonBench is a verified executable research-software platform for its declared numerical tests and a reproducible archive of several useful positive and negative scientific comparisons**. It has real measured-CO₂ density evidence, source-mapped thermodynamic calculations, coupled finite-source heat-exchanger solvers and a carefully documented horizontal sCO₂ HTC benchmarking pipeline. The most recent source and CI audit confirms a **15/15-job successful H1d run**, on **draft PR #19 at `cf170a0`**, with a fully matched **1275-station** comparison that favours **Jackson–Hall** over the tested Kim semi-empirical and unverified empirical interpretations in that **out-of-fit-domain subset**.

It is **not** a proof that the industrial cycle, original authors’ exact EES or Kim empirical model, a PCHE or an actual controller has been faithfully reproduced. Its main scientific bottlenecks now are **reconciling the original Kim Eq.24/Table 4 source convention, obtaining independent in-range local CO₂ thermal data, and validating geometry-specific heat-transfer/UA and machinery relations**. Preserving these unresolved gates is part of the project’s credibility, not a reason to erase its completed technical work.

**Archive rule:** use this report as a dated snapshot. If later work merges PR #19, corrects the original Kim equation or publishes a DOI, create an explicit subsequent revision with an exact Git commit, raw-data/CI references, change log and adjusted scientific gate table. Do **not** silently edit this historical 2026-11-05 evidence record to make later results appear to have existed earlier.
