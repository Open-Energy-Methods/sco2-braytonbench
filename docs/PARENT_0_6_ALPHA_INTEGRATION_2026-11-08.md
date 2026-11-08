# Parent sCO₂-BraytonBench 0.6.0a0 — scientific integration and version contract

**Status:** proposed integrated **research-alpha development snapshot** (8 November 2026); no public GitHub Release, Git tag, PyPI or Zenodo DOI authorized.  
**Baseline before integration:** main 4a866b721558ff9dba2f09dc334916abec69467f after historical ThermoML rights dossier PR #43.  
**Purpose:** reconcile all completed primary-cycle, thermal/control, TES and H1d experimental research into one maintained branch without declaring source-author model parity, laboratory validation or permission to relicense measurements.

## A. Version decision

The parent package changes from 0.5.0a0 to **0.6.0a0** as an explicit **pre-release alpha development revision**. This is **not v1.0.0**. TES-v1.0 is a separately scoped *TES research-baseline candidate*; a module's milestone number is not a parent SemVer release. H1d is experimental, not the supported stable heat-transfer design API.

A 0.x alpha development bump is justified by new publicly reviewable *functional modules* (TES and physics-source-specific Kim evaluation) and revised source/test contracts. To remain fully truthful:
- pyproject.toml, CITATION.cff, wheel/sdist metadata, installed scientific smoke, TES-v0.9/v1.0 and WP5 pre-release gates must agree on 0.6.0a0.
- Do not tag 0.6.0a0, publish a source archive or request a DOI as an automatic side effect of merging development. Packaging CI artifacts are build/testing evidence, not publication authorization.
- Historical dated reports (5 and 6 November) retain the versions and scientific status at their own dates and must not be retroactively rewritten.
- The release gate must classify any recognized 0.x alpha as unreleased research, but continue to fail closed on mismatched wheel/sdist/CFF metadata, historic data and human review.

## B. Scientific scope actually present on parent branch

| Research area | Executable source | Evidence status | Explicit limits |
|---|---|---|---|
| Recuperated 6-state sCO₂ cycle | cycle, core, exchangers, properties | Algebraic balance/real-CoolProp regression | No calibrated plant/turbomachinery maps, measured CARBOSOLA |
| Open source/cooler and fixed-UA coupling | whr, fixed_ua, coupled_plant, hydraulics | Source/end-use first law, real-CO₂ tests | No specified installed industrial geometry/actuator |
| Source-to-wall thermal transient | thermal_dynamics, dynamic_whr | Closed-form thermal limit, RK4 energy integration, real-CoolProp smoke | No full changing CO₂ mass/pressure inventory |
| Sampled gas bypass and PI | source_bypass and dynamic control modules | Physical source-gas split, net source energy and synthetic PI scenario | No characterized commercial valve/controller |
| Prospective measurement/uncertainty protocol | experimental_readiness and reports | Proposed schema and mathematical error propagation | No facility permission, calibration or experimental run |
| Stuttgart H1a–H1c | measured-derived source tests/correlation scripts | Credited CC BY 4.0 data, negative cross-domain findings | No general PCHE geometry-calibrated design |
| **Kim H1d (experimental)** | kim2019.py, stuttgart_h1d.py, exact-station comparison, 3-mode CI | Printed semi-empirical, literal printed empirical and clearly labelled sign-hypothesis; original 2019 paper source ambiguity and negative fit-domain transfer retained | **Issue #20 original Eq.24 denominator/sign unresolved; all Stuttgart points outside Kim original heat-flux fit envelope, author's 620-point original study not replicated. No coefficient fitting, no stable design recommendation.** |
| TES-v0.1–0.5 | Schumann, FV model, stateful cycles, one-pass Brayton endpoint | Analytic inlet-step, full fluid/solid energy ledger, unit/time separation | Idealized constant-cp sensible bed, no loop inventory or TES experiment |
| TES-v0.6–0.7 | synthetic split and frozen ROM | 512 trajectories; train 256 / validation 64 / test 128 / OOD 64; test 6.20 K vs 15.09 K for coarse 2-cell; **OOD failure** 14.25 K vs 6.60 K for coarse solver | No conservative full-state ROM or OOD guarantee |
| TES-v0.8–v1 candidate | operating-grade analysis and distribution/research audit | N96/192 grade disparity, 29 OAT + 8 factorial; Python 3.10/3.11/3.12 wheel/sdist replay; 46-file integrity ledger | No independent quantified model-form uncertainty; no qualified independent human review |

## C. Three legacy PR dispositions

1. **PR #43**: historical NIST Mantilla audit, 17 old branch-head copies, measured old Actions artifacts and six-author correction **merged** separately before this integration. **Issue #27 remains open** until rights steward explicitly resolves historical public redistribution and artifact/branch treatment.
2. **PR #21**: preserve its 5 November 2026 **historical 1,245-line archival report** exactly as authored in docs/reports/2026-11-05/. Integrate via a new current-main parent consolidation rather than rebasing it through unrelated source changes. The report's PR-19-draft and 0.5.0a0 statements are *as of 5 November*, not current claims.
3. **PR #19**: selectively integrate original source-audit H1d model, three interpretation variants, 54-experiment source-aligned evaluation, exact common-station comparison, numerical negative findings, tests, coefficient registry and matrix CI on top of modern main. Do **not** merge its old README/CI wholesale and clobber 6–8 November advances. Close original stacked draft as **superseded by integrated current-main PR**, while **keeping source ambiguity issue #20 OPEN** and no claim of original-author method equivalence.

## D. CI/release gates to validate on exact integration head

- Existing parent pytest across Python 3.10/3.11/3.12 and real-fluid source/sink/HX, WP2–WP5 tests; pinned CoolProp 8.0.0 when required.
- New H1d source/inversion tests, **three** separate actual synthetic-to-Stuttgart transfer modes, complete original source denominator, exact common-station comparison and negative/extrapolation diagnosis.
- TES-v0.8 operating-grade evidence; TES-v0.9 Python3.10–3.12 wheel/sdist isolated replay; TES-v1.0 metadata and numerical invariance gate; WP5 source rights exclusion.
- Verify optional Mantilla table is absent from **current source, wheel and sdist**, that tests skip unless given a user-supplied external dataset, and that historic rights were **not** falsely marked cleared.
- Reconcile **0.6.0a0** package, citation, current report, build filenames and numerical version controls. Ensure no automatic release/tag/DOI action was introduced.
- After merging the source integration, run post-merge main CI; source-head passing status must not be silently copied to the new merge commit.

## E. Release classification / outstanding issues

**Acceptable claim:** "0.6.0a0 development alpha: reproducible numerically verified sCO₂ energy-cycle/finite-source/thermal-control and sensible packed-bed TES research toolkit, with experimental source-model benchmarking and explicitly negative cross-domain data."

**Not acceptable:** "v1.0 certified", "real CARBOSOLA/HZDR lab-validated", "author-reproduced Kim 2019 Eq.24 or 620-point original empirical errors", "validated full dynamic CO₂ pressures/inventory", "industrial approved gas-bypass controller", "TES ROM extrapolation successful", or "NIST historical data rights settled."

**Blockers for a formal stable parent v1.0 release:** [historic source rights #27](https://github.com/Open-Energy-Methods/sco2-braytonbench/issues/27), [independent qualified human review #28](https://github.com/Open-Energy-Methods/sco2-braytonbench/issues/28), and explicit maintainer release authorization. The separate Kim source-equation ambiguity [#20](https://github.com/Open-Energy-Methods/sco2-braytonbench/issues/20) must be resolved before promoting H1d to an experimentally validated API.

## F. Reproduction — after integration CI succeeds

~~~bash
python -m pip install -e '.[test,co2,ml]' 'CoolProp==8.0.0'
python -m pytest -q
python scripts/tes_schumann_convergence.py --out evidence/generated/tes_v03
python scripts/tes_operating_window_study.py --out evidence/generated/tes_v08
python scripts/stuttgart_h1d.py --variant semi_empirical
python scripts/stuttgart_h1d.py --variant empirical_literal
python scripts/stuttgart_h1d.py --variant empirical_hypothesis
~~~

Those commands may be expensive and use synthetic or separately attributed original Stuttgart data; they are *not* a physical experimental validation protocol. For the final numeric and source support evidence, use the exact final workflow run IDs and checksums, not a textual example alone.
