# Measured-density validation decision — 2026-11-05

## Verdict

**Partial G1-E progress: experimental density comparison passed at the 49 published conditions; complete real-fluid validation is NOT closed.**

The measured-density record from Mantilla et al. (2010), archived by
NIST ThermoML, is a physically independent check against density
measurements; prior REFPROP guide values were predictions from another
implementation of the same equation of state. All data are
versioned in `data/reference/mantilla2010_thermoml_density.csv`.

| Metric | Result |
|---|---:|
| Independent experimental density points | 49 |
| Measured isotherms | 310, 350, 400, 450 K |
| Measured pressures | 0.999 to 159.844 MPa |
| CoolProp version | 8.0.0 (`HEOS::CO2`) |
| Mean relative density residual | −0.005608% |
| RMS relative density residual | 0.034731% |
| Maximum absolute relative density residual | 0.090241% |
| Initial broad software screen | 2% max / 1% RMS (passed) |
| New tighter regression screen | 0.2% max / 0.1% RMS (must pass new CI) |

By temperature:

| T (K) | Number of observations | Maximum absolute residual (%) | RMS residual (%) |
|---:|---:|---:|---:|
| 310 | 12 | 0.04660 | 0.02968 |
| 350 | 9 | 0.02784 | 0.01646 |
| 400 | 20 | 0.06498 | 0.03414 |
| 450 | 8 | 0.09024 | 0.05336 |

These are **relative residuals**, not uncertainty estimates or
statements of statistical significance. The NIST ThermoML
uncertainty column is preserved as reported but needs documentation
before being used as a statistical weighting scheme.

## Source-model identifiability decision

The calculated Figure 2b conceptual-cycle result
`24.3058%` is close to Friedman & Rapp's Table 3
`24.3812%`, differing by `−0.07544 percentage points`.

The source paper explicitly uses `T7` for low-side temperature
and describes compressor suction pressure (conceptual `P8`).
Changing the interpreted temperature or pressure to adjacent
points in **deliberate counterfactual tests** yields efficiency
values between 24.2907% and 24.3058%, spread 0.01510 percentage
points. This change is smaller than the observed comparator
discrepancy; it does not eliminate the structural differences
between the conceptual Figure 2b model and the complex Figure 4 EES
plant.

**Why exact source-model identification is not established:**
Table 3 gives aggregate heat input, turbine/compressor work and
cooling duty, whose first-law balance removes one independent
constraint. The detailed plant's extra compressor turbine,
different branch flows, machinery maps, generator efficiencies,
full thermodynamic state table, external heat-source model
and complete EES solver configuration are not supplied.

Fitting an available parameter until aggregate efficiency matches
would be **calibration to an underdetermined target**, not
verification of the authors' original plant.

## Next scientific priorities

1. Expand independent near-critical experimental **density and heat
   capacity** measurements, not merely more Span–Wagner-generated
   property tables.
2. Add measured thermodynamic or calorimetric energy-related
   constraints (enthalpy/heat capacity) to complement density.
3. Compare alternate EOS formulations only when an independent,
   correctly implemented backend is available. NISTIR 8608
   (2026) and its REFPROP-readable CO₂ fluid file are candidates,
   not presently executable substitutes in standard CoolProp.
4. Request original Figure 4 EES code or tabulated state points
   before declaring full Friedman–Rapp reproduction.
5. Keep G2 open and the repository pull request in draft pending
   human technical review.

## Machine-readable evidence

GitHub Actions run:
https://github.com/Open-Energy-Methods/sco2-braytonbench/actions/runs/41993477851

Measurements source:
https://trc.nist.gov/ThermoML/10.1021/je1001158.json

This software has **not** been validated against the HZDR
CARBOSOLA test rig or any independent sCO₂ dynamic experiment.
