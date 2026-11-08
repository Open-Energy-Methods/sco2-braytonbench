# sCO₂-BraytonBench

**Standalone research software for modelling, verifying and eventually controlling supercritical-CO₂ Brayton power cycles for industrial waste-heat recovery.**

Maintained under [Open Energy Methods](https://github.com/Open-Energy-Methods).

> **Research status: 0.7.0a0 (development alpha; no public release tag) — numerically verified research software, not an experimentally validated sCO₂ power-cycle or CARBOSOLA plant model.** The core solver has dedicated real-CoolProp test jobs; the thermal-wall, source-bypass/PI and experimental-readiness examples remain explicitly synthetic or prospective. No complete dynamic CO₂ mass/pressure inventory or industrial controller is claimed.

## Research portfolio — thermal and mechanical energy storage (PhD preparation)

The **[PhD-facing thermal/mechanical storage research portfolio](docs/portfolio/README.md)** is the recommended scientific entry point. It contains three actual-evidence vector figures (Schumann convergence; the charge/hold/reverse-discharge trace; and the **negative** frozen-ROM out-of-domain comparison), a proposed-but-**not executed** [experimental validation protocol](docs/portfolio/PROSPECTIVE_EXPERIMENTAL_VALIDATION_PROTOCOL.md), and a separately bounded, **unvalidated** [liquid-piston gas/work/hysteresis concept](docs/portfolio/LIQUID_PISTON_CONCEPT.md). Every figure has an [original CI-artifact provenance dossier](docs/portfolio/EVIDENCE_AND_FIGURE_SOURCES.md). This is independent applicant research, **not** CIC energiGUNE/COMPETENT work or a real laboratory validation.

[Schumann numerical verification](docs/portfolio/figures/01_schumann_grid_convergence.svg) · [TES charge/discharge](docs/portfolio/figures/02_tes_charge_hold_discharge.svg) · [ROM test/OOD comparison](docs/portfolio/figures/03_frozen_rom_test_ood.svg)

## Latest parent integration and dated technical reports

The [parent 0.6.0a0 consolidation record](docs/PARENT_0_6_ALPHA_INTEGRATION_2026-11-08.md) preserves the prior 8 November integration scope. The current application-focused source is **0.7.0a0 research alpha** and is described in the [storage portfolio](docs/portfolio/README.md). The archived
[5 November full G0–G3.5 research report](docs/reports/2026-11-05/sco2-braytonbench-comprehensive-project-report.md)
and 6 November WP0–WP5 report are dated historical records, not claims that
their version/PR statuses remain current.

## Current comprehensive technical report

The dated **[6 November 2026 comprehensive research, engineering and verification report](docs/reports/2026-11-06/sco2-braytonbench-comprehensive-research-report.md)** preserves the integrated WP0–WP5 technical baseline at that date. The [8 November parent alpha integration dossier](docs/PARENT_0_6_ALPHA_INTEGRATION_2026-11-08.md) tracks the current development scope, historical-PR reconciliation, Kim H1d experimental status, release-gate consistency and the unapproved data/review decisions. It covers the original G0–G3.5 research, Stuttgart H1a–H1d evidence, integrated WP0–WP5 models, governing equations, numerical results, optional measured-density rights cleanup, 20/20 integrated-main CI, reproducibility and the outstanding external-review gates. The [report index](docs/reports/README.md) distinguishes dated evidence from the historical 5 November snapshot.

**Verified baseline:** main `8df1711a425e21da342bd3f401da61a1375bbc0a`, [Actions 42266275348](https://github.com/Open-Energy-Methods/sco2-braytonbench/actions/runs/42266275348) 20/20 green. No v1.0 tag or DOI issued. The 49-point Mantilla ThermoML transcription has been removed from current HEAD and redistributed archives while historical reuse and independent human scientific review remain unresolved ([#27](https://github.com/Open-Energy-Methods/sco2-braytonbench/issues/27), [#28](https://github.com/Open-Energy-Methods/sco2-braytonbench/issues/28)).

## Thermal energy storage (TES) — synthetic research extension

The 1-D, **two-temperature sensible packed-bed TES** extension is intentionally separate from the existing sCO₂ plant model. Completed and merged core milestones are [Schumann verification #31](https://github.com/Open-Energy-Methods/sco2-braytonbench/pull/31), [charge/discharge #32](https://github.com/Open-Energy-Methods/sco2-braytonbench/pull/32), [single-pass Brayton coupling #33](https://github.com/Open-Energy-Methods/sco2-braytonbench/pull/33), [exergy/capacity metrics #34](https://github.com/Open-Energy-Methods/sco2-braytonbench/pull/34), and the verified [512-run synthetic dataset #38](https://github.com/Open-Energy-Methods/sco2-braytonbench/pull/38).

The merged **[frozen-split surrogate PR #39](https://github.com/Open-Energy-Methods/sco2-braytonbench/pull/39)** implements a supervised reduced-order **input/output emulator** of the eight-cell synthetic bed, not a dynamic CO₂ inventory model or a physical facility controller. The [methods](docs/tes/08_FROZEN_SPLIT_SURROGATE.md) and [executed heldout report](docs/tes/09_FROZEN_ROM_RESULTS_2026-11-07.md) document an in-domain test outlet RMSE of **6.20 K**, solid SOC RMSE **0.0116**, and comparison against a two-cell physically conservative baseline. The **out-of-domain test is a negative transfer result**: the ROM has **14.25 K** outlet RMSE versus **6.60 K** for two-cell physics. Results are *synthetic*; the exact-head PR gate passed 27/27 tests before merge.

- [Mathematical model and units](docs/tes/01_LITERATURE_AND_MODEL_CONTRACT.md); [independent Schumann analytic reference](docs/tes/02_BENCHMARK_SPECIFICATION.md); [conservation](docs/tes/03_CONSERVATION_AND_LIMITS.md) and [grid refinement](docs/tes/04_SCHUMANN_GRID_VERIFICATION.md).
- [Full-state charge/hold/discharge semantics](docs/tes/05_CYCLES_AND_METRICS.md), [open single-pass TES→Brayton power balance](docs/tes/06_SINGLE_PASS_CO2_COUPLING.md) and [constant-property capacity/exergy/thermocline metrics](docs/tes/07_PERFORMANCE_METRICS.md).
- Generate source data: `python scripts/tes_generate_synthetic_dataset.py --out evidence/generated/tes_v06`.
- Fit and freeze the surrogate with optional `.[ml]` dependencies: `python scripts/tes_surrogate_pipeline.py train --data evidence/generated/tes_v06 --model-dir evidence/generated/tes_v07/frozen`, then invoke `evaluate` separately.
- This code does **not** represent measured CIC energiGUNE or CARBOSOLA hardware, CFD, phase-change TES, PCM, a physically calibrated or validated molecular-spring liquid piston, a calibrated thermal-storage plant, or a validated full dynamic CO₂ power cycle. TES research milestones do not themselves confer a stable parent release; the current parent source is **0.7.0a0 development alpha**, without a release tag or external human scientific approval.

### TES-v0.8 — temperature-grade operating window and sensitivity

The [TES-v0.8 methodology and acceptance contract](docs/tes/10_OPERATING_WINDOW_SENSITIVITY.md)
defines a reproducible synthetic two-temperature packed-bed operating-window study,
with separate physical one-at-a-time sensitivity and numerical mesh/timestep/
outlet-observation refinement. It reports outlet-temperature-qualified recovered
heat **without removing lower-grade heat from the first-law balance**, null
crossings where no threshold is reached, independent solid/fluid capacity and
exergy, and null gross efficiency unless **all cell temperatures return**.

The [7 November executed numerical and factorial results](docs/tes/11_OPERATING_WINDOW_RESULTS_2026-11-07.md)
document the N=96 operating-window baseline, mesh refinement to N=192,
eight crossed flow/porosity/Hv scenarios, their large temperature-grade
interactions, and model-specific identifiability limitations. The dated
results remain synthetic and tied to their cited Actions evidence commit.

Run with python scripts/tes_operating_window_study.py --out evidence/generated/tes_v08
and verify its CSV hashes with --verify. GitHub Actions runs and archives
the full evidence; results are **synthetic** and do not establish model-form
uncertainty, experimental validation, real-pressure losses, or industrial TES
round-trip efficiency. Independent v1.0 scientific review remains open.

### TES-v0.9 — isolated distributions and deterministic replay (merged)

The [TES-v0.9 software release gate](docs/tes/12_DISTRIBUTION_AND_REPLAY_GATE.md)
builds a wheel and sdist from the same exact commit and exercises each through
separate non-editable installs on Python 3.10/3.11/3.12. It checks installed
module origin, analytically verified grid, charge/discharge, ideal and real-CO2
one-pass coupling, temperature-grade accounting and a locally generated *toy*
surrogate ABI smoke (not frozen v0.7 holdout retraining). It compares replay
results with strict categorical and finite numeric tolerances and archives
SHA256 manifests for both distributions and numerical evidence.

The archive audit excludes the uncleared Mantilla 2010 extracted density CSV
and disallowed packaged model pickles/PDFs while retaining source provenance.
**Passing software distribution checks does not establish redistribution rights,
experimental verification or scientific reviewer approval.** The TES-v0.9
milestone passed all three dedicated Python-version CI jobs, 27/27 repository
jobs, and the TES-v0.8 regression; merged as PR #41 (main commit
46db32e6e9a45bdfeb645aa6e0599380cb9bc9e4). Parent version remains
0.5.0a0 at the time of the TES-v0.9 merge; the parent source is now 0.7.0a0 development alpha, with #27/#28 still independent stable-release blockers.

### TES-v1.0 — integrated research baseline and review package (candidate)

The [integrated TES research report](docs/tes/13_RESEARCH_BASELINE_TECHNICAL_REPORT.md)
consolidates the conservative 1-D two-temperature governing equations, Schumann
analytical/grid comparisons, energy-preserving charge/hold/reverse-discharge,
explicit one-pass TES-to-Brayton boundary, exergy/temperature-grade accounting,
synthetic surrogate (including its **negative out-of-domain result**) and the
N=96/192 sensitivity limitations. Additional candidate tests cross-check
affine-temperature, area/flow dimensional scaling, exergy identities and
grade-independent conservation against independent physical constructions.

The [external scientific and software reviewer packet](docs/tes/14_EXTERNAL_REVIEW_PACKET.md),
[source and historical data rights dossier](docs/data_licenses/TES_SOURCE_RIGHTS.md)
and [release decision register](docs/tes/15_RELEASE_DECISION_REGISTER.md)
are **unsatisfied review requirements, not signed approvals**. The
candidate self-audit records exact commit/source SHA256 and *fails closed*
if release authorization, independent reviewer approval or historical
redistribution rights are asserted without a separate actual review.
No v1.0 tag, Zenodo DOI, real facility validation or parent version change
is implied. Parent source is now **0.7.0a0 alpha** (not a tagged, reviewed or formally published v1.0).

## v1.0 research release programme — work in progress

The [v1.0 scope and scientific release contract](docs/V1_0_RELEASE_CONTRACT.md)
and [requirements/evidence matrix](docs/V1_0_VERIFICATION_MATRIX.md) document
what **would** be required for a stable software release; **no v1.0 release
or CARBOSOLA experimental validation currently exists**.

The [exact lumped thermal-wall model](docs/G4_THERMAL_CONTROL_VOLUME_SCOPE.md)
is implemented and extended by the explicitly synthetic [finite-source
thermal coupling](docs/G4_WP2B_FINITE_SOURCE_WALL_CYCLE.md) and [sampled
bypass PI](docs/G5_WP3_BYPASS_PI_CONTROL.md). **None models a full dynamic
CO₂ mass/pressure inventory, rotating-shaft dynamics, identified valve
hydraulics or authorised plant control.** The full six-state cycle is
solved algebraically within the transient thermal surrogate.

### WP2b — finite-source storage coupled to the steady Brayton power block

The [WP2b physical specification](docs/G4_WP2B_FINITE_SOURCE_WALL_CYCLE.md)
documents an experimental **thermal transient** connecting three
nonidentical energy paths: finite hot waste gas → dynamic lumped
thermal wall → an installed-UA CO₂ heater → quasi-steady recuperated
six-state Brayton cycle. The real thermal wall temperature is solved
from its stored-energy differential equation, not a sequence of
independent steady-state temperature inputs.

`src/sco2_braytonbench/dynamic_whr.py` uses a separately rated,
isothermal wall-to-CO₂ UA so that the already-counted cycle heater
duty is the **only** heat leaving the wall. Matched RK4 stage quadrature
records integrated gas/wall/cooler/net-shaft energies, with an
independently derived ideal-gas/zero-recuperator closed-form test.

```bash
python -m pip install -e '.[test]'
python -m pytest -q tests/test_dynamic_whr.py
python examples/waste_heat_wall_coupled_cycle.py
```

This is **not a full dynamic CO₂ Brayton-cycle model**: compressor
inlet, pressure, mass flow, machine efficiencies and recuperator remain
algebraic/prescribed, cooler medium is not an inventory, and all wall
capacity/UAs, loads and properties in the example are synthetic. There
is no CARBOSOLA facility calibration, valve, PI or MPC controller.

### WP3 — finite hot-gas bypass and sampled thermal-wall PI

The experimental [WP3 source-bypass and PI control protocol](docs/G5_WP3_BYPASS_PI_CONTROL.md)
models a physical **mass split** of the total hot-gas source into (1) a
branch crossing the finite-source wall exchanger and (2) an untouched
bypass. The two branches are rejoined **after** heat transfer through an
enthalpy-conserving mixing junction. Bypass control never adds fictitious
heat to the Brayton cycle.

The [WP2b thermal wall](docs/G4_WP2B_FINITE_SOURCE_WALL_CYCLE.md)
remains the only time-integrated storage state; the Brayton states and
turbo-machine efficiencies are quasi-steady. A sampled wall-temperature PI
commands the **diverted gas mass fraction** using position and slew
constraints, a minimum active-stream flow, and back-calculation anti-windup.
The control law uses only present sampled wall temperature (no future
load information).

```bash
python -m pip install -e '.[test]'
python -m pytest -q tests/test_control_whr.py
python examples/waste_heat_bypass_pi_comparison.py
```

The output CSV and JSON compare fixed-bypass and PI response on exactly
the same hypothetical gas temperature/flow inputs, including **net shaft
energy cost** and a source+wall+cycle conservation ledger. The fixture is
an *artificial ideal gas*, not experimentally validated CO₂ or CARBOSOLA.
There are no CO₂ mass/pressure inventories, calibrated valve flow maps,
safety interlocks, plant-identified controller gains, or MPC.

### WP4 — prospective laboratory measurement and validation readiness

The [WP4 experimental-readiness protocol](docs/WP4_EXPERIMENTAL_READINESS_PROTOCOL.md)
now specifies a *proposed*, staged campaign for testing finite-source
thermal storage and the WP3 wall-temperature controller against future
facility observations. It introduces **35 candidate measurement/data tags**
and **13 proposed** desk, steady, transient, control and sealed-holdout
cases in `protocols/wp4/`. **No tag is confirmed installed/calibrated,
no run is approved and no measured CARBOSOLA data were supplied.**

An [experimental-readiness utility](src/sco2_braytonbench/experimental_readiness.py)
checks SI channel schemas, run and sample identifiers, long-format DAQ
quality flags/missing/timing gaps, unconfirmed standard uncertainties,
proposed campaign completeness, linearized **constant-cp gas** sensible
heat-duty uncertainty with explicitly correlated temperatures, and a
local parameter-sensitivity *rank* diagnostic. This is a conservative
data-quality/preparation tool, **not** sensor calibration, real-CO₂
near-critical uncertainty propagation or an installed experiment.

```bash
python -m pytest -q tests/test_experimental_readiness.py
python examples/wp4_readiness_audit.py
```

The audit writes machine-readable **readiness blockers** and an
explicitly synthetic metrology arithmetic example. It cannot turn
the document into real experiments or grant facility operating permission.

### WP5 — reproducible source and wheel release-candidate gate

The [WP5 v1.0 acceptance and independent-review dossier](docs/WP5_RELEASE_ACCEPTANCE.md)
defines the future **software** release gates separately from experimental
plant validation. The project is **`0.7.0a0` development alpha, not v1.0**. The WP5
tool `scripts/v1_release_gate.py` audits consistent package/citation/SPDX
licence metadata, verifies installed wheel and research-complete source
archive contents, fingerprints source files and numerical outputs, and
compares **four deterministic, explicitly synthetic examples** reproduced
from clean wheel and sdist installations.

CI builds both distributions, installs each independently in a fresh
environment, executes the WP2a thermal-wall, WP2b finite-source/cycle,
WP3 source-bypass/PI and WP4 prospective-readiness examples, compares
their CSV/JSON evidence with disclosed numerical tolerances, and retains
machine-readable release artifacts. All real-CoolProp and reference
jobs remain separate and mandatory for a release-candidate decision.

```bash
python -m pytest -q tests/test_v1_release_gate.py
# See docs/WP5_RELEASE_ACCEPTANCE.md for the complete wheel/sdist replay.
```

This code **cannot tag the repository, approve an experiment, issue
a DOI, resolve third-party data redistribution rights or perform
independent scientific review**. Tagging v1.0 remains blocked pending
the actual full-head green test results, integration of stacked PRs
and a documented independent acceptance decision.

Source dataset and redistribution rights are inventoried in the
[release data-rights dossier](docs/DATA_RIGHTS_V1.md): Stuttgart's
adapted experiment tables are attributed under the source CC BY 4.0
licence, while the 49-point Mantilla NIST ThermoML transcription is
**removed from current source HEAD and withheld from release source distributions** pending a
specific publisher/authorized-rights decision
([issue #27](https://github.com/Open-Energy-Methods/sco2-braytonbench/issues/27)).
The earlier public Git history still contains the historical
transcription, but current HEAD does not. The optional measured-density
suite requires a user-supplied external CSV. Public Git visibility does
not itself establish reuse permission. All software releases remain blocked on licence review and
a separate qualified reviewer decision.

## What is implemented

- SI-unit six-state recuperated Brayton **steady-state** calculation.
- Property adapter contract with **analytic ideal-gas test fixture** and optional **CoolProp HEOS CO₂** backend.
- Segmented counterflow recuperator with local pinch checking, feasible limiting duty, effectiveness input or inferred finite UA.
- Gas-source main heater with finite exhaust-gas energy balance, minimum pinch and estimated required UA.
- Pressure-only reconstruction of Friedman & Rapp (2016), Figure 2b / Table 2, with 12 numbered points (not their detailed full EES thermodynamic model).
- Independent tests and GitHub Actions workflow.

The demonstration code is in `src/sco2_braytonbench/`. Its 1–6 cycle-state numbering must **never** be mixed with the literature source's numbering.

## Install and verify

```bash
python -m pip install -e '.[test]'
python -m pytest -q
python examples/analytic_fixture_cycle.py
```

Run separate optional real-fluid property smoke tests:

```bash
python -m pip install -e '.[test,co2]'
python -m pytest tests/test_coolprop_optional.py -q
```

**A passed smoke test is not numerical validation of a complete CO₂ cycle.**

## Industrial waste-heat recovery — G3 exploratory screening

A source-constrained six-state recuperated CO₂ model is now available
on the G3 feature branch. It checks a finite exhaust-gas thermal
inventory, counterflow heater pinch, stack-temperature floor,
heat-exchanger sizing allowance, first-law conservation and an ideal-gas
exergy ceiling. Both net **shaft power** and thermal efficiency are
ranked over the **same finite feasible design grid**.

Run the separately pinned CoolProp experiment with
`python scripts/whr_design_screen.py`.
Read [the G3 model specification](docs/G3_WASTE_HEAT_DESIGN_SCREENING.md)
for explicit assumptions, source-versus-model distinctions, and limits. The [G3 screening results](docs/G3_STEADY_SCREENING_RESULTS.md) document numerical outcomes, added plant limits, and convergence checks.

The branch's grid search is **not** a global optimizer, an MK2014
REFPROP/GA reproduction, or a validated off-design sCO₂ rig model.

## G3.1 — fixed installed heater UA and coupled operating point

The `sco2_braytonbench.fixed_ua.solve_fixed_ua_whr` solver now
determines the turbine-inlet temperature from the **installed** main-heater
`UA`, source-gas inlet and mass flow, CO₂ circuit conditions and an
explicit feasible operating-temperature interval.

Unlike the earlier heater-sizing inequality, its accepted solution
satisfies `UA_required ≈ UA_installed` together with gas-side
and CO₂-cycle first-law balances. It also checks stack temperature,
heater pinch and a stream exergy bound. It **does not** invoke a
fictional bypass or usable-area adjustment.

Read [the coupled operating-point specification](docs/G31_FIXED_UA_COUPLING.md)
and run `python scripts/fixed_ua_coupled_demo.py` with CoolProp
installed to generate an explicit real-fluid source-temperature
perturbation report.

No physical cooler-UA coupling, measured equipment maps or transient
control is implemented. The initial heater-UA value in the example is
sized from a chosen hypothetical nominal operating point, not
measured hardware or a published benchmark.

## G3.2 — two installed UAs, finite cooling stream and sensible-source cp

The new `sco2_braytonbench.coupled_plant.solve_coupled_plant`
function calculates both **compressor inlet T1** and **turbine inlet T4**
from an installed heater UA, installed cooler UA, finite hot-gas flow,
finite cooling-medium flow and a fixed-UA recuperator.

The coolant outlet and exhaust gas outlet temperatures follow separate
enthalpy balances; pinch and stack constraints are enforced. A
documented linear sensible-heat-capacity model can be used for both
streams, while constant cp remains the default for compatibility.
An optional separately identified **quadratic flow-loss scaling scenario**
is provided for sensitivity only, not a measured map.

Read [the G3.2 physics and verification scope](docs/G32_COUPLED_COOLING.md) and the [G3.2 numerical verification](docs/G32_NUMERICAL_VERIFICATION.md).
The model is still steady-state, with no phase change, real turbomachinery
maps, calibrated heat-transfer correlations or transient control.

## G3.3 — reference stream properties, hydraulics and HX sensitivity

Research property options now include:
- a **NIST Shomate** ideal, dry, fixed-composition 79/21 mole-fraction N₂/O₂ stream (300–1000 K);
- a **CoolProp HEOS Water** liquid-coolant stream at user-specified
  pressure with no boiling or freezing;
- **Darcy–Weisbach** single-phase circular-pipe hydraulics with
  laminar `64/Re` and turbulent Haaland/Colebrook friction, rejecting
  transition regimes rather than interpolating fabricated accuracy.

The previous linear/constant cp and assumed-flow-loss models are still
available for comparative regressions. No industrial heat-exchanger
geometry, wetted path or roughness was provided, so the pipe
correlation is **not automatically applied to the cycle**.

Read [G3.3 reference-property and convergence protocol](docs/G33_REFERENCE_PROPERTIES_AND_CONVERGENCE.md) and [G3.3 numerical results](docs/G33_NUMERICAL_VERIFICATION.md)
and run `python scripts/g33_component_mesh_sensitivity.py` to
record a real-fluid, multi-point **component-level** mesh sensitivity
with 6/12/24/48 segments. This is **not** full nested dual-UA
operating-point grid convergence and does not close industrial G3.

## G3.5 — external measured-derived CO₂ heat-transfer benchmark

The source-reviewed [Stuttgart H1 campaign](docs/G35_STUTTGART_HTC.md)
compares pinned CoolProp real-CO₂ bulk properties and independent
turbulent forced-convection baseline correlations against **the complete
54-run experimental dataset** from Theologou et al. (2022), Mendeley DOI
10.17632/4mvk4nxrkz.1 (original data under **CC BY 4.0**).
All 2,508 axial source records (2,398 local HTC records) are included
with attribution in [the dataset folder](data/validation/stuttgart/README.md).

The experiment with the anomalous 832.99 kW/m² source entry is preserved
unchanged but **quarantined** from evaluation. Benchmark comparisons
report per-orientation errors, source-reported HTC sigma-normalized
residuals, domain exclusions, and four held-out nominal experiment
families without fitting any coefficients. This is a **single-pipe
forced-convection baseline**, not Brayton-cycle/PCHE validation.
Run `python scripts/stuttgart_h1.py` with pinned CoolProp to reproduce.

## G3.5 H1b — Bishop and Jackson–Hall comparison

The [H1b research protocol](docs/G35B_WALL_PROPERTY_CORRELATIONS.md)
adds Bishop and Jackson–Hall wall-property correlations and a
Richardson buoyancy diagnostic to the unchanged Stuttgart H1a
experiment benchmark. It distinguishes **measured-wall-conditioned
diagnostics** from **flux-driven wall-temperature inversions**,
without coefficient fitting or modifying the four nominal held-outs.

## G3.5 H1b — first wall-property comparison results

[The executed Bishop and Jackson–Hall experimental analysis](docs/G35B_RESULTS.md)
separates measured-wall-conditioned diagnostics from flux-driven wall-T
solutions. Flux-driven MAPE **46.40% (Bishop, 2,152 stations)**
and **49.47% (Jackson–Hall, 2,318)** improve materially over
the earlier forced-convection baselines, but top-wall MAPE remains
~81–85%, and these remain cross-fluid/horizontal-domain extrapolations.
A source-faithful Richardson indicator flags buoyancy risk rather
than inventing a heat-transfer enhancement factor.

## G3.5 H1c — orientation-specific published Lei equations

[The H1c test protocol](docs/G35C_LEI_TOP_BOTTOM.md) adds the
published Lei et al. **top (HT) and bottom (HB)** equations as an
explicit cross-fluid/geometry stress test on the Stuttgart experimental
dataset. These equations were fitted for supercritical WATER (26/43 mm),
**not** this supercritical CO₂ 4/8 mm dataset. No middle-wall formula
or angular interpolation is invented; measured-wall-conditioned
diagnostics are separated from flux-driven predictions, with the
same STU-001 quarantine and four held-out families.

## G3.5 H1c — published Lei top/bottom transferability audit

The [executed H1c results](docs/G35C_LEI_RESULTS.md) show the
originally **supercritical-WATER**, 26/43-mm Lei top/bottom correlations
transfer **very poorly** to Stuttgart CO₂ 4/8-mm tubes. On
1,580 identical HB/HT stations, Lei flux-driven local HTC MAPE is
**631.72%** (top **1065.72%**) compared with **55.52%** for the
previous Jackson–Hall flux-driven comparison. The wall-inverse
numerical flux balance closes to better than 0.0013%, so this
is a cross-fluid transferability failure rather than a solver
residual problem. No model correction, HM interpolation or
new coefficient fit was introduced.

## Consolidated research and recovered Kim 2019 source

[Consolidation history and CI verification](docs/PR_CONSOLIDATION_AUDIT.md)
covers the prior nine stacked research PRs without erasing their commit
history. A merge into `main` is a **repository integration milestone
only**, not an approval of all numerical model assumptions.

The **original Kim et al. (2019) CO₂ mixed-convection paper** has now
been obtained and its Eqs. (23), (24), (29), (30), top/bottom
**Table 4** coefficients and original experimental limits recorded in
[the source audit](docs/KIM2019_ORIGINAL_SOURCE_RECOVERY.md)
and [machine-readable coefficient registry](data/reference/kim2019_coefficients.json).
The copyrighted full PDF is **not included**. The [experimental H1d
implementation](src/sco2_braytonbench/kim2019.py), [reproducible benchmark
methods](docs/G35D_KIM2019_BENCHMARK.md), [executed negative Stuttgart
results](docs/G35D_RESULTS.md), [independent evidence triage](docs/G35D_INDEPENDENT_VALIDATION_SOURCE_TRIAGE.md)
and [exact-station comparison](scripts/h1d_common_support.py) are now
integrated into the development-alpha source, with three **distinct** modes:
published semi-empirical, printed empirical Eq.24/Table4 literal, and an
explicitly **UNVERIFIED sign-placement hypothesis**. The original article's
620-point parity and empirical equation ambiguity remain **open**
([#20](https://github.com/Open-Energy-Methods/sco2-braytonbench/issues/20));
all tested Stuttgart stations exceed Kim's original reported fitted heat-flux
domain. Do not use H1d as a validated design correlation or replace its
negative/failed-root observations with a favourable selected subset.

## Source literature

- Friedman, P. D., and Rapp, M. P. (2016), *Parametric Analysis of SCO2 Power Cycles Operating at Moderate Temperatures*, 5th International Symposium on Supercritical CO₂ Power Cycles, Paper 51. Supports pressure-network mapping, recuperator-pinch methodology and moderate-temperature cycle studies.
- Mohagheghi, M., and Kapat, J. (2014), *Thermodynamic Optimization of Recuperated S-CO2 Brayton Cycles for Waste Heat Recovery Applications*, 4th International Symposium on Supercritical CO₂ Power Cycles. Supports open-loop source-gas balances and the distinction between maximum net-power and maximum-efficiency cycle designs.

See [measured-density and identifiability evidence](docs/EXPERIMENTAL_DENSITY_AND_IDENTIFIABILITY.md), [source distinctions](docs/REFERENCES.md), [FR2016 source/benchmark review](docs/FR2016_COMPARISON_REVIEW.md), [real-fluid reference verification](docs/REFERENCE_VERIFICATION.md), [research gate status](docs/RESEARCH_STATUS.md), and [verification protocol](docs/VERIFICATION.md).

## Explicit exclusions

This is **not a CARBOSOLA digital twin**. No HZDR rig measurements, experimental campaign, validated real-sCO₂ cycle benchmark replication, full CO₂-inventory plant dynamics, experimentally identified plant PI/MPC controller, or techno-economic optimum is claimed. The WP3 wall-temperature PI is a synthetic, uncalibrated research demonstrator only. An ideal-gas test-fluid result must never be labelled as a CO₂ prediction.

The related [HTHP-ControlBench](https://github.com/Open-Energy-Methods/hthp-controlbench) is a separate repository; general testing/control methods may be adapted, but their physics models remain independent.

BSD-3-Clause license. AI-assisted work is subject to scientific and human review.
