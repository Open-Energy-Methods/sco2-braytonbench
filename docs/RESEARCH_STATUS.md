# Research and verification status

Updated: 2026-11-05. **Pre-alpha research software — PR #1 remains draft.**

This independent repo is not an extension of HTHP-ControlBench
and is **not** a CARBOSOLA digital twin.

## Results to date

- Algebraic tests for pressure closure, energy conservation and
  heat-exchanger calculations have passed on an artificial
  constant-property fixture. **Those are not real-CO2 tests.**
- GitHub Actions run **41991114530** passed 30 real-fluid checks
  on CoolProp 8.0.0, including NIST REFPROP reference densities
  and h/s differences, near-critical density and a twelve-state
  source-mapped conceptual cycle.
- Friedman & Rapp (2016) Figure 2b, Table 2 conceptual comparison
  obtained `eta = 24.3058%` vs Table 3 `24.3812%`.
  The difference is `-0.0754` percentage points. Power comparison
  is normalized to the source's reported 100.20 MW heat input,
  **not** a separate determination of installed capacity.
- A second CI run **41991703407** passed **64 analytic-fixture tests**
  (4 optional CoolProp modules skipped in the fixture jobs) and
  **46 real-fluid reference/consistency checks** in the dedicated
  CoolProp 8.0.0 job. Its 12-state diagnostic and sensitivity JSON
  are available as reproducible Actions artifacts.
- At the chosen FR2016 point, increasing HX segments 30->60
  changed calculated efficiency by **0** at printed precision,
  while inferred recuperator UA increased **0.037%**.
  Imposed effectiveness and a terminal-limited Qmax can make duty
  segment-insensitive; this is **not universal grid independence**.
- A +/-1 K shift of T_low changed efficiency from
  24.4834% to 24.1216% (baseline 24.3058%). This assumption
  sensitivity exceeds the 0.0754-percentage-point paper difference.
  See `docs/FR2016_COMPARISON_REVIEW.md`.
- Source Figure 4 EES turbine split, component maps and individual
  state data remain unknown; matching Table 3 totals is **not
  confirmation of an equivalent detailed plant model**.

## Literature provenance

- Friedman & Rapp (2016): 12-state conceptual Figure 2b and
  Table 2 pressure network reviewed; complete Figure 4 EES
  model not reproduced.
- Mohagheghi & Kapat (2014): finite waste-heat source and RC/RRC
  designs reviewed. REFPROP/GA optimum not reproduced.
- NIST REFPROP guide (2013): independent software-output reference
  values, not experimental measurement data.
- New alternative CO2 EOS by Lemmon, Harvey & Hellmann (2026):
  potential future sensitivity study, not implemented.

See `docs/REFERENCE_VERIFICATION.md` and CI artifact for
specific temperatures, pressures, provenance and limitations.

## Verification stage gates

| Gate | Status | Blocker |
|---|---|---|
| G0 original-source mapping | Partial | Detailed EES state table |
| G1-A analytic conservation | Passed local and CI | Retain regression tests |
| G1-E CO2 real-fluid | **Partially verified** | Larger independent data and edge regimes |
| G2 source-model reproduction | **Open** | Full source-model identifiability |
| G3 source gas recovery | Partial prototype | Full real-fluid/finite-UA verification |
| G4 transient plant | Not implemented | Mass and energy inventory dynamics |
| G5 PI/MPC | Not implemented | Physical actuation and safety |
| G6 economics | Not implemented | Grounded cost and sizing assumptions |

No experimental sCO2 test-rig experience or CARBOSOLA-specific
measurements or geometry is claimed. The repository is a fresh
reconstruction; the previously referenced v0.5 archive was not
available for direct import.

## Independent measured-density validation (GitHub Actions 2026-11-05)

The source-curated `data/reference/mantilla2010_thermoml_density.csv` includes
**49 directly measured pure-CO₂ densities** from Mantilla et al. (2010)
at 310/350/400/450 K, spanning approximately 1–160 MPa. Unlike the
older REFPROP-versus-CoolProp tests, this is experimental validation
**of density only**.

The real-fluid CI job on [run 41993477851](https://github.com/Open-Energy-Methods/sco2-braytonbench/actions/runs/41993477851)
passed **61 tests**. Both fixture-only Python jobs passed **73 tests**
and skipped 5 optional CoolProp modules.

- Mean density residual: **−0.005608%**
- RMS relative density residual: **0.034731%**
- Maximum absolute relative density residual: **0.090241%**
  (among the 49 recorded conditions).
- Per-temperature maximum residuals: 310 K **0.04660%**;
  350 K **0.02784%**; 400 K **0.06498%**;
  450 K **0.09024%**.

The regression-screen thresholds have been tightened to **0.2% maximum**
and **0.1% RMS** based on this first clean baseline. They are test
thresholds, **not** physically derived measurement uncertainty bounds.
Independent validation of enthalpy, entropy and heat capacity is
still outstanding, particularly in the closest near-critical region.

## Original source-model identifiability

The FR2016 default `T7/P8` mapping remains source-supported.
Deliberately relabelling the low-side pressure and/or temperature
to adjacent states produces a conceptual-cycle efficiency range
**24.2907–24.3058%** (spread **0.01510 percentage points**).
These are **counterfactual mapping tests**, not equally credible
interpretations of the authors' paper. They do not recover the
Figure 4 EES plant's compressor-turbine branch, full state table
or missing performance maps.

See `docs/EXPERIMENTAL_DENSITY_AND_IDENTIFIABILITY.md`.

### Tightened regression confirmed

GitHub Actions [run 41993973281](https://github.com/Open-Energy-Methods/sco2-braytonbench/actions/runs/41993973281) **passed all three jobs** after the stricter density screens:
**73 passed / 5 CoolProp modules skipped** per fixture-only Python job; **61 passed** in the dedicated real-fluid job. Regression criteria `max absolute density residual < 0.2%` and `RMS < 0.1%` passed. The report contains measured and calculated densities and is retained in [the evidence artifact](https://github.com/Open-Energy-Methods/sco2-braytonbench/actions/runs/41993973281/artifacts/13398788849).

The worst observed density residual (0.09024% at 450 K and approximately 122.193 MPa) is larger than the paper's quoted <0.03% density uncertainty, despite lying within its reported ~0.1% high-pressure EOS discrepancies. A formal experimental uncertainty consistency test remains outstanding. This does not invalidate the density agreement, but prevents a stronger claim about uncertainty-limited accuracy.

## G3 finite-source steady screening, 2026-11-05

Draft stacked [PR #6](https://github.com/Open-Energy-Methods/sco2-braytonbench/pull/6) models an industrial gas source coupled to a six-state real-CO₂ cycle, with explicit first-law, heater UA sizing, stack and pinch feasibility checks. [GitHub Actions 41999222234](https://github.com/Open-Energy-Methods/sco2-braytonbench/actions/runs/41999222234) passed all four jobs: **136 analytic tests (6 optional skipped) per Python version, 61 property/EOS tests and 3 real-fluid gas-source checks**.

Base independent grid (16/20 feasible): power maximum **8.110 MW, η=25.218%** at CO₂ 100 kg/s, T4=700 K versus efficiency maximum **33.504%, Wnet=1.622 MW** at CO₂ 20 kg/s, T4=700 K. Under hypothetical cooler cap 15 MW_th and recuperator local minimum 10 K (6/20 feasible), power-max becomes **4.984 MW** (70 kg/s, 650 K) and efficiency-max **30.728%** (40 kg/s, 700 K). These are not MK2014 paper results or plant predictions. Both original winners underwent a **12/24/48 segment** sensitivity check; see [G3 results](docs/G3_STEADY_SCREENING_RESULTS.md) and [full G3 inputs/limitations](docs/G3_WASTE_HEAT_DESIGN_SCREENING.md).

**G3 partial only.** The heater UA is an inequality design sizing allowance; a fixed installed heater, gas heat-capacity variation, flow-dependent pressure loss and real cooling/powertrain maps remain unimplemented.

## G3.1 fixed-installed-UA coupled heater — 2026-11-05

New stacked draft [PR #8](https://github.com/Open-Energy-Methods/sco2-braytonbench/pull/8) extends G3 by solving **installed heater UA equality and turbine-inlet T4** under a finite hot-gas supply, rather than checking a heater sizing allowance against a prescribed T4. The parent G3 sizing-grid feature remains available separately; no physical bypass, actuator or used-area adjustment is assumed.

[CI run 42002609837](https://github.com/Open-Energy-Methods/sco2-braytonbench/actions/runs/42002609837) **passed five jobs**: 151 analytic-fixture tests (7 optional real-fluid skips) per Python version, the existing property and G3 jobs, and 3 new real-fluid coupling tests plus off-design diagnostic.

In an **independently assumed illustrative** 800 K gas inlet/20 kg/s CO₂ design, an installed heater UA of **21.783328 kW/K** was sized from nominal `T4=650 K`. Re-solving yields `T4=649.989 K`, gas outlet 758.003 K, net shaft power 1.424 MW, `η=30.822%`. Keeping that UA fixed and raising gas inlet to **810 K** yields `T4=658.954 K`, gas outlet 767.638 K, net shaft power 1.460 MW, `η=31.330%`. Relative UA residuals 0.00598% and 0.00203% respectively. These are independent steady-state solutions, **not dynamic responses or actual plant predictions**.

See [G3.1 methods](docs/G31_FIXED_UA_COUPLING.md), [G3.1 numerical results](docs/G31_FIXED_UA_NUMERICAL_RESULTS.md) and [reproducibility evidence](https://github.com/Open-Energy-Methods/sco2-braytonbench/actions/runs/42002609837/artifacts/13403581114).

**G3.1 physical/industrial validation OPEN:** gas property variation, real heat-transfer/pressure-loss correlations, cooling-UA equipment coupling and independent operating data remain necessary.

## G3.2 — two installed-UAs and finite coolant, 2026-11-05

[Stacked draft PR #9](https://github.com/Open-Energy-Methods/sco2-braytonbench/pull/9) solves compressor inlet T1 and turbine inlet T4 from a finite hot-gas stream, finite coolant and two **fixed installed exchanger UAs**. It also introduces source and coolant temperature-dependent linear sensible cp (optional) and **uncalibrated** flow-dependent loss/efficiency scenarios. Existing constant-cp behaviour is retained by default. The sink has no phase change, measured geometry, pump/fan power or transient inventory.

[GitHub Actions run 42005964249](https://github.com/Open-Energy-Methods/sco2-braytonbench/actions/runs/42005964249) passed all six jobs: **178 fixture tests passed/8 optional real-fluid modules skipped** on each Python version; previous property, G3 and G3.1 jobs passed; the new dual-UA real-CO₂ test passed, and two coolant-perturbation operating points were exported.

At a synthetic installed heater UA **21.626 kW/K** and cooler UA **100.514 kW/K**, coolant inlet 285→287 K changed calculated **T1 310.005→310.464 K**, **T4 650.020→652.217 K**, net shaft power **1.424→1.406 MW**, and cooler outlet **295.173→297.025 K**, with both UA errors below the declared solver tolerances. See [full numerical record](docs/G32_NUMERICAL_VERIFICATION.md).

**Status:** G3.2 numerical prototype verified at these tests; industrial G3 gate **still OPEN**, pending calibrated geometry/flow properties, near-critical convergence, actual cooling equipment constraints and machine maps.

## G3.3 — sourced dry-air and real-water properties; component mesh check

Draft stacked [PR #10](https://github.com/Open-Energy-Methods/sco2-braytonbench/pull/10) adds NIST N₂/O₂ Shomate dry-air sensible properties (300–1000 K), CoolProp single-phase Water coolant properties at specified pressure, Darcy–Weisbach/Haaland circular-pipe friction functions **without inventing equipment geometry**, and two-point real-CO₂ component mesh refinement 6/12/24/48 sections. These are optional, with legacy simple cp/flow models preserved.

At prescribed CO₂ input states 8.5 MPa/310 K/650 K and 9 MPa/314 K/690 K, the 24→48 refinement changes heat-exchanger required UA by **<0.04%** and cycle efficiency by **0.0021–0.0024 percentage points**, while the internal recuperator minimum approaches remain just **3.92/4.58 K** (below a hypothetical 10 K margin). [Full G3.3 numerical report](docs/G33_NUMERICAL_VERIFICATION.md) and [machine JSON](https://github.com/Open-Energy-Methods/sco2-braytonbench/actions/runs/42010735595/artifacts/13407415665).

The new property/hydraulic job passed 35 tests and the fixture suites passed 205/9 skipped each. **G3.3 narrow component verification PARTIAL; full industrial coupled-UA convergence OPEN.** No measured geometry or compressor maps are claimed.

## G3.5 — Stuttgart experimental heat-transfer benchmark (new stage)

The [G3.5 methods](docs/G35_STUTTGART_HTC.md) and full CC-BY source-derived 54-experiment / 2,508-axial-record [dataset](data/validation/stuttgart/README.md) are now versioned. The model compares Gnielinski smooth-tube and heating Dittus–Boelter **uncalibrated orientation-blind forced-convection baselines**, with real-fluid CoolProp properties and an explicit measured-inlet-temperature/enthalpy-increment alignment to the REFPROP-derived source enthalpy.

Nominal HB/HM/HT orientation triplets remain in a group-level held-out partition, no coefficients fitted. The STU-001 832.992 kW/m² source cell is preserved unchanged but its full experiment excluded from performance scoring. Descriptive local HTC uncertainty normalization does not claim independent errors or statistical experimental uncertainty propagation. **G3.5 model–measurement evaluation is ongoing until the real-fluid Actions report is inspected; full industrial G3 remains OPEN.**

### G3.5 first executed external measured-derived HTC comparison (2026-11-05)

[GitHub Actions 42031845343](https://github.com/Open-Energy-Methods/sco2-braytonbench/actions/runs/42031845343) `stuttgart-h1` job **passed**: 54 original runs / 2,508 axial positions / 2,398 reported reduced local HTCs, one quarantined source experiment (50 local points) and 30 axial applicability exclusions per correlation → **2,318 scored local HTC predictions** per model. CoolProp 8.0.0 properties with measured inlet anchor/within-run REFPROP-derived enthalpy increments, no fitted coefficient. Gnielinski smooth forced-convection baseline **MAPE 150.15%**, Dittus–Boelter heating baseline **119.60%**. Top-wall errors **236.81% / 189.01%** respectively. Four nominal held-out families remain untouched; [full method/uncertainty and all strata](docs/G35_STUTTGART_RESULTS.md). **H1a executed comparison PASS, H1b predictive heat-transfer validation FAILS/REMAINS OPEN.** Do not declare these conventional correlations accurate or apply them as calibrated industrial HX UAs.

### G3.5 H1b wall-property correlations (in development)

The follow-on draft implements source-documented Bishop and Jackson–Hall equations in separately reported experimentally conditioned and flux-driven wall-inverse modes, plus a diagnostic Richardson buoyancy indicator. The experiment IDs, STU-001 quarantine, SHA256 family holdouts, original bulk enthalpy alignment and H1a code remain unchanged. **Bishop is a supercritical-water correlation extrapolated to horizontal CO₂, and neither equation is a genuine orientation-resolved buoyancy model.** Accuracy conclusions are withheld until complete real-CO₂ execution and review.

### G3.5 H1b executed source correlation comparison (2026-11-05)

The [H1b measured-versus-calculated result](docs/G35B_RESULTS.md) was produced on [Actions run 42035909213](https://github.com/Open-Energy-Methods/sco2-braytonbench/actions/runs/42035909213) (dedicated H1b job passed, pinned CoolProp 8.0.0). Flux-driven (measured wall T NOT an input) Bishop MAPE **46.40%/2152 stations** and Jackson–Hall **49.47%/2318 stations**; held-out MAPE **39.72%/43.16%**, top wall **80.65%/84.63%**. In contrast measured wall conditioned diagnostics give **21.94%/28.46%** but are NOT independent predictions because reduced HTC shares wall-T and q inputs. `Ri>0.001` for ~98.6% of tested points indicates strong buoyancy exposure, which neither model resolves angularly. No coefficients were fitted and the original four nominal group heldouts and STU-001 quarantine remain intact. **H1b implementation and evidence PASSED; accurate predictive HTC validation remains OPEN.**

### G3.5 H1c (in development): Lei top/bottom transfer test

New [H1c methods](docs/G35C_LEI_TOP_BOTTOM.md) implement the **published Lei et al. 2017 orientation-specific bottom/top equations** as reproduced by Theologou et al. 2022 Eq.17, including heat-flux Grashof with film-density mean expansion coefficient. HM has no published equation and is excluded, not interpolated. Both measured-wall-conditioned diagnostic and actual flux-driven wall-temperature inverse are evaluated; no new coefficients fitted and the original Stuttgart experimental data, STU-001 quarantine and 4 nominal held-outs are untouched. **All applications are explicitly OUT OF original-domain water/26–43 mm fitting conditions.** Results withheld pending CI; industrial H3 and accurate predictive H1b/H1c validation OPEN.

### G3.5 H1c executed external-domain Lei stress test — 2026-11-05

[Source-faithful H1c report](docs/G35C_LEI_RESULTS.md) and [machine output](https://github.com/Open-Energy-Methods/sco2-braytonbench/actions/runs/42040967963/artifacts/13421155963): full 1,580 HB/HT station comparison (790 each), no HM equation (738 excluded), preserved STU-001 quarantine and four original nominal-family heldouts. Refined flux-driven Lei root solver gives maximum relative heat balance ~0.00127%, zero numerical rejections. **Lei flux-driven HTC MAPE 631.72% overall, bottom 197.73%, top 1065.72%, held-out 638.83%**, versus **55.52% Jackson** on same 1,580 points. All 18 nominal families favor Jackson over Lei in flux mode; a 4,000 draw family bootstrap interval of Jackson−Lei advantage is entirely negative, but does not establish external predictive uncertainty. Lei original fit used WATER 26/43 mm at ~23–25 MPa; the CO₂ 4/8 mm transfer is out-of-domain. This is a **verified negative transferability finding**, not original Lei source invalidation. Original-domain CO₂ horizontal mixed-convection 2019 Kim et al. study identified; its complete original equations were recovered later in the source-integration audit, but numerical Kim model implementation remains OPEN. **G3.5 accurate orientation-resolved CO₂ HTC validation OPEN**.

### Original Kim et al. (2019) source retrieval — 2026-11-05

The complete 12-page original published paper was uploaded, hash-verified and visually inspected. Original mixed-convection Eq. (24) and (30) plus quadratic superposition, alternative semi-empirical equations, full **Table 4** top/bottom coefficients, 7.75-mm/0.91-m test section, source domain and Table 6 author-reported errors are now traceable: [Kim source audit](docs/KIM2019_ORIGINAL_SOURCE_RECOVERY.md) and [transcription JSON](data/reference/kim2019_coefficients.json). **Source retrieval closed; correlation implementation and independent Stuttgart validation NOT STARTED.** The copyrighted paper PDF is not redistributed. [PR consolidation audit](docs/PR_CONSOLIDATION_AUDIT.md) retains the nine original development stages in Git history.
