# TES-v0.8 — Synthetic operating window, useful-temperature grade, and sensitivity evidence

**Status:** implementation and CI evidence programme; numerical results must be read from the generated hashed artifacts at the tested commit. **Scientific class:** original numerical simulation of an idealized constant-property, adiabatic, 1-D, two-temperature sensible packed bed, *not* measured facility performance.

This stage extends the foundation in [07_PERFORMANCE_METRICS.md](07_PERFORMANCE_METRICS.md). The conservative thermal solver, not a learned ROM, is used for all storage trajectories. None of these calculations modifies the frozen TES-v0.6 data, TES-v0.7 model, or untouched evaluation sets.

## 1. Questions and acceptance contract

1. How do outlet temperature-grade availability, stored energy, solid SOC, ambient-relative reversible exergy and thermocline width change across a declared operating envelope?
2. Which changes are due to *physical input parameters*, and which are numerical grid, solver-timestep or observation-quadrature effects?
3. Does the physical *first-law ledger* close for every scenario, including those that do not reach the useful-temperature threshold?
4. Is a purported cycle truly completed by return of every fluid and solid cell temperature, or only a charge/discharge demonstration?

Hard numerical criteria: every scenario has relative first-law closure <= 1e-9; stages retain positive physical temperatures and stable substeps; temperature-grade duration does not exceed the discharge duration; every absent threshold crossing is represented as null; an incomplete cycle has null gross round-trip efficiency. All study CSVs and a declared manifest are SHA256 checked in CI. These criteria concern numerical integrity, **not** independent physical validity.

## 2. Explicit system and source of inputs

Synthetic model base:

| Quantity | Baseline | Unit |
|---|---:|---|
| Bed length | 1.0 | m |
| Bed cross-sectional area | 0.10 | m² |
| Porosity | 0.50 | – |
| Gas density / cp | 5 / 1000 | kg/m³; J/(kg K) |
| Solid density / cp | 1000 / 700 | kg/m³; J/(kg K) |
| Volumetric interphase heat-transfer coefficient | 500 | W/(m³ K) |
| Finite-volume cells | 12 | – |
| Initial / charge inlet temperature | 350 / 650 | K |
| Signed flow during charge / reverse discharge | +0.05 / -0.05 | kg/s |
| Charge / zero-flow hold / discharge durations | 0.8 / 0.1 / 1.0 | thermal turnovers |
| Qualifying discharge outlet grade | 500 | K |
| Ambient exergy reference | 300 | K |
| Macro stage partition intervals | 24 | – |
| Recorded SSPRK3 outlet substep stride | 1 (every substep) | – |

The turnover period is calculated from **both** fluid and solid capacities:

\[
 \tau = (C_{f,\mathrm{total}}+C_{s,\mathrm{total}})/(|\dot m|c_{p,f}).
\]

Using multiples of \(\tau\) in the sweep means changing geometry, porosity or flow **also changes the phase duration in seconds**. It is a dimensionless-duration comparison, *not* a fixed-clock-time comparison; physical sensitivities are conditional on this specific schedule. The original simulator automatically subcycles SSPRK3 with its stability bound.

## 3. What useful-temperature-grade energy means

The unchanged discharge first-law inventory loss equals the SSPRK3 stage-matched flux integral:

\[
E_{\mathrm{recovered}} =
-\int_{\mathrm{discharge}} \dot m c_{p,f}(T_{\mathrm{in}}-T_{\mathrm{out}})\,dt.
\]

The threshold-filtered **usable thermal output** is a separate operational quality indicator:

\[
E_{\mathrm{useful}}(T_q)=\int_{\mathrm{discharge}}
\mathbf 1[T_{\mathrm{out}}(t)\ge T_q]\,
|\dot m|c_{p,f}\,(T_{\mathrm{out}}(t)-T_{\mathrm{in}})\,dt.
\]

Here \(T_q>T_{\mathrm{in}}=T_{\mathrm{cold}}\). This quantity is not plant electric power, a heat-engine efficiency, or the entirety of heat withdrawn. It is integrated by piecewise-linear interpolation across the **SSPRK3 internal substep outlet trace**, not only 24 widely spaced macro observations, with linear segment splitting at threshold crossings. A new opt-in trace field leaves the pre-existing conservative thermal solve unchanged. This approximation does *not* replace or adjust the conservative first-law ledger. The output contains the **full-linearly-reconstructed discharge energy** and its signed difference from the SSPRK3 ledger so the observation-quadrature bias is visible. A stride parameter permits controlled decimation of the substep trace without changing the physical solve; refine the sampling stride and SSPRK3 timestep independently before trusting threshold-sensitive magnitudes.

A threshold never attained returns **zero qualified energy and duration**, correctly representing no service. An event such as a first crossing that never occurred is reported **null**, not zero time. A threshold can be above the physically possible inlet hot temperature as an explicit no-service stress case.

The after-charge design capacities and actual stored thermal energy are separated into fluid and solid terms. Thermal exergy is reversible constant-cp availability relative to 300 K, not a pressure-inclusive industrial exergy balance. The solid 10–90% front width is null for partial/nonmonotone fronts without two complete crossings.

## 4. Full-state completion and efficiencies

At the end of discharge, compare *all* fluid and solid cell temperatures against the initial state. The declared default maximum cell error tolerance is 0.5 K. Merely charging and then withdrawing energy does not constitute a completed cycle. Only a positive charge and withdrawal with full-state return permits the gross energy ratio. Otherwise:

- complete_cycle = false;
- gross_round_trip_efficiency = null.

Do **not** report \(E_\mathrm{recovered}/E_\mathrm{charged}\) for an incomplete cycle as round-trip efficiency, even when that ratio numerically exists.

## 5. Predeclared sensitivity design

The physical one-at-a-time (OAT) panel varies one independent coordinate from the baseline at a time:

| OAT axis | Values |
|---|---|
| Flow, kg/s | 0.025, 0.05, 0.10 |
| Porosity | 0.35, 0.50, 0.65 |
| Bed length, m | 0.75, 1.00, 1.25 |
| Bed area, m² | 0.075, 0.100, 0.125 |
| Interphase Hv, W/(m³ K) | 250, 500, 1000 |
| Charge turnovers | 0.6, 0.8, 1.0 |
| Hold turnovers | 0, 0.1, 0.2 |
| Discharge turnovers | 0.8, 1.0, 1.2 |
| Useful outlet temperature threshold, K | 450, 500, 550, 700 |

These produce **29 CSV rows** (1 nominal plus 28 perturbations). The independent numerical-discretization panels contain **10 rows**: N = 6/12/24/48, grade-trace decimation stride 4/2/1, and SSPRK3 maximum substep limited to 1/0.5/0.25 of the nominal stability timestep. Varying trace stride is *not* varying SSPRK3 timestep; the nominal grade observation uses every internal solver substep. Macro stage count stays at 24. Varying N is *not* changing the physical bed size.

Each row reports charge, recovered and threshold-qualified energy, qualified duration, first-qualified/first-downcrossing time where defined, residuals, capacity, SOC, exergy, thermocline width when defined, full-state return and solver diagnostics, alongside absolute OAT deltas from nominal. Nonmonotone responses are legitimate; do not silently fit a derivative across a threshold event.

The design is **not** a probabilistic Monte Carlo study, a complete factorial interaction analysis, a material-calibrated uncertainty budget or an experiment. Parameter impacts are not uncertainty intervals. Strong cross-effects among \(\dot m\), Hv and geometry could require a later interaction study.

## 6. Uncertainty and convergence are explicitly separated

**Numerical:** use mesh N, SSPRK3 timestep limit and independently decimated solver-substep outlet traces, plus known Schumann verification from TES-v0.3. The finest point here is not automatically an exact continuum truth. Results should be compared against the finest available reference and a plateau judged on relevant outputs; first-law closure alone cannot establish convergence.

**Parametric:** report signed physical OAT deltas under the declared scaled-turnover protocol. No distribution, standard error or confidence interval is inferred without justified input distributions.

**Model form:** **unquantified.** Single constant-cp adiabatic 1-D closure, lumped interphase Hv, no real gas state variation, axial conduction, wall loss, pressure drops, pumping parasitics, multidimensional maldistribution or experimentally established contact correlations. Changing Hv within this same model does not quantify closure-form uncertainty.

**Experimental:** absent. No actual bed data or permission to operate a facility are assumed.

## 7. Reproduction, integrity and evidence

~~~bash
python -m pip install -e '.[test]'
python -m pytest -q tests/test_tes_operating_window.py
python scripts/tes_operating_window_study.py --out evidence/generated/tes_v08
python scripts/tes_operating_window_study.py --verify --out evidence/generated/tes_v08
~~~

Outputs: tes_v08_physical_sensitivity.csv, tes_v08_numerical_refinement.csv and tes_v08_manifest.json, with SHA256 hashes and a source revision supplied by CI. The manifest freezes the input contract, baseline outputs, nominal parameters, excluded claims, and three noninterchangeable uncertainty classes. Direct artifact manipulation is rejected on re-verification.

Dedicated workflow: .github/workflows/tes-v08-operating-window.yml. The repository's inherited test matrix also exercises the new unit tests on Python 3.10/3.11/3.12.

## 8. What remains outside TES-v0.8

The chosen operating envelope is a **synthetic research study**. It does not validate the TES against a published measured experiment or license restricted data; it does not turn the TES-v0.7 output surrogate into a conservative reduced full-state model. It is not a physical CO₂ inventory transient, closed-loop return circuit, pressure-loss model, heat-loss validated plant model, or experimental CARBOSOLA/CIC energiGUNE equipment representation.

TES-v0.9 packaging/distribution, data-rights approval, a qualified independent human review and any formal v1.0 software tag remain separate gates in issue #37, #27 and #28. The parent package stays **0.5.0a0**.
