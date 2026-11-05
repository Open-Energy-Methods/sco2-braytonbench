# G3.5 — Stuttgart H1: experimental sCO₂ local heat-transfer benchmark

**Status:** new external **measured-derived HTC** versus *uncalibrated, orientation-blind* engineering baselines. This is **not** a calibrated buoyancy-aware correlation, compressor map, CO₂-cycle validation or a claim that published supercritical-specific correlations were reproduced.

## Source and data

Theologou et al. (2022), *Experimental Investigations on Heat Transfer of CO₂ Under Supercritical Pressure in Heated Horizontal Pipes*, Energy 254 (2022), article 124171; DOI [10.1016/j.energy.2022.124171](https://doi.org/10.1016/j.energy.2022.124171). Original research dataset [10.17632/4mvk4nxrkz.1](https://doi.org/10.17632/4mvk4nxrkz.1), **CC BY 4.0**. Original researchers report 54 pipe experiments at approximately 7.75 MPa and horizontal 4/8-mm heated tubes. Buoyancy-induced differences up to ~90 K between circumferential wall locations. The publication reports Bishop had the lowest average deviation **52%** among four correlations *it* tested; that is **not a target achieved by our different formulas**.

This repository contains the complete CC-BY-licensed **normalized** source intake at [`data/validation/stuttgart`](../data/validation/stuttgart/README.md), 54 experiment records and 2,508 axial rows, 2,398 with an experimentally-derived local HTC. A dedicated source notice preserves the original DOI, author attribution, transformation and checksums.

## Calculated baselines

For each admissible local experimental station, the model evaluates CO₂ bulk **temperature, cp, viscosity and conductivity** from pinned CoolProp HEOS::CO₂. The local measured input is bulk specific enthalpy **increment** along that run, a derived experimental signal; pressure is held at the measured inlet P because local P is not included in the normalized record.

**Reference enthalpy caveat:** the paper used REFPROP to derive the supplied bulk `h(x)`. It is unsafe to treat its absolute zero-point as identical to CoolProp. We set `h_CO2(x) = h_CoolProp(P_in,T_in,measured) + [h_dataset(x)-h_dataset(x=0)]`. This is a physical enthalpy-difference alignment using the independently measured inlet temperature, not a fitted heat-transfer coefficient; it nevertheless inherits the experiment's heat-input and bulk-enthalpy estimation.

For tube diameter `D` and mass flow `m`:

```text
Re = 4m/(π D μ_bulk)       Pr = cp_bulk μ_bulk/k_bulk
Nu_Gnielinski = [(f/8) (Re-1000) Pr] / [1+12.7 sqrt(f/8)(Pr^(2/3)-1)]
f_smooth = (0.79 ln(Re)-1.64)^(-2)
Nu_DittusBoelter = 0.023 Re^0.8 Pr^0.4  (heating)
htc_predicted = Nu*k_bulk/D
```

Hard physical applicability gates:
- Gnielinski smooth tube: `3000<=Re<=5e6`, `0.5<=Pr<=2000`, `x/D>=10`.
- Dittus–Boelter heating: `Re>=10000`, `0.7<=Pr<=160`, `x/D>=10`.

The **local** comparisons use textbook fully-developed forced-convection expressions on local bulk properties even though the experimental flow is sometimes thermally developing and strongly buoyant. Thus this is a declared **baseline failure analysis**, not an appropriately calibrated near-critical Nusselt correlation. No measured wall temperature is given to the model formula; it is retained as diagnostic data only.

Published Gnielinski form, for example: [PolyKin tube correlation documentation](https://hugomvale.github.io/polykin/reference/hmt/correlations/Nu_tube/). The paper's tested correlation set and its reported errors must not be confused with this project's results.

## Quarantine and grouping

**STU-001** original experiment ID `4MM_HM_77.5_10_20_90_A`: source q=832.992 kW/m² against nominal HB/HT ~91.7 kW/m². No value is overwritten; the **entire run** is excluded from performance scoring until the mismatch is resolved. Source kept in versioned CSV.

Nominal families are grouped by removing orientation code `HB/HM/HT` from the original experiment ID. A fixed SHA256-based 4/18-family **held-out partition** ensures all orientations of one nominal run stay together. **No parameters are fitted** in the current baseline; splits are reported to prepare scientifically defensible future calibration without axial/run leakage.

## Metrics and epistemic limits

Every valid station is included in `local_predictions.csv` with experiment ID, axial position, orientation, model, predictions, reported local HTC, local reported HTC sigma, `Re`, `Pr`, and domain checks. Summary `report.json` includes per-correlation:
- Point-weighted relative MAPE, signed mean bias, RMS percentage error, median and p90 absolute errors;
- per-run macro MAPE and equal-family macro MAPE, so long axial runs do not silently over-weight the benchmark;
- separate HB/HM/HT, 4/8-mm and development/held-out strata;
- fraction of |residual| within source-reported **one local HTC sigma** and normalized residual median, for **descriptive** checks only.

Crucially, the quoted HTC percentages are **experimentally derived and may correlate with heat flux, wall temperature, pressure, bulk enthalpy and adjacent axial locations**. This work has **not** propagated input covariance or evaluated statistical 95% coverage, and does not assert independence of axial station errors. Reported one-sigma fraction must not be interpreted as a calibrated confidence interval.

The program rejects out-of-domain correlations rather than extrapolating and records source exceptions. Large observed baseline errors can be scientifically informative; **do not fit multipliers to hide stratification**.

## Reproduction

```bash
python -m pip install -e '.[test,co2]' 'CoolProp==8.0.0'
python -m pytest -q tests/test_stuttgart_h1.py
python scripts/stuttgart_h1.py \
  --data-dir data/validation/stuttgart \
  --out evidence/generated/stuttgart_h1
```

CI publishes `report.json` and `local_predictions.csv` as `g35-stuttgart-h1` artifact. Development/test fixture uses **artificial constant-property CO₂-like values only** to verify arithmetic and data grouping; this is **not a real-CO₂ result**. The real property comparison must complete separately on GitHub Actions.

## Gate decision and future improvements

**G3.5 H1 is only closed as a baseline implementation after all 54 source IDs, quarantine, grouped split, model domain, measured HTC comparison and reproducible CI have been reviewed.** It does NOT close actual buoyancy/heat-transfer model validation unless the specific correlation's predictive errors and uncertainty are scientifically acceptable. Follow-on work should add buoyancy criteria, thermal entry and wall-property corrections, source-aligned Bishop/Jackson/Petukhov formulations as actually specified in the original paper, and held-out validation.

This is a **single-pipe heated-flow component comparison** and cannot validate PCHE recuperator geometry, installed UA of a complete Brayton plant, compressor/turbine maps or PI/MPC.
