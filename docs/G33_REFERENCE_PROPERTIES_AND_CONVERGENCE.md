# G3.3 — sourced sensible properties, geometry-based hydraulics and mesh sensitivity

**Status:** draft numerical verification extension, updated 2026-11-05.
**Parent:** G3.2 (PR #9), stacked under G3.1/G3/initial research foundations.
**Scope:** industrial-sCO₂ Brayton-cycle *research software*. Not a measured
industrial plant, CARBOSOLA, or numerical reproduction of Mohagheghi & Kapat (2014).

## A. Source gas: NIST dry-air approximation

NIST Chemistry WebBook SRD 69 gas-phase Shomate polynomials:
- [N₂, 100–500 and 500–2000 K tables](https://webbook.nist.gov/cgi/cbook.cgi?ID=C7727379&Mask=1).
- [O₂, 100–700 and 700–2000 K tables](https://webbook.nist.gov/cgi/cbook.cgi?ID=C7782447&Mask=17).

The class `DryAirNISTShomate` models **79 mole% N₂ and 21 mole% O₂**,
fixed composition, ideal-gas sensible properties between **300–1000 K**.
This approximate dry air excludes argon and excludes **exhaust-gas
CO₂, H₂O, pollutants, reaction products, variable moisture and
mixture pressure effects**. Published gas-phase Shomate coefficients
are not experimental plant-composition data.

For species coefficient vector (A,B,C,D,E,F,G), t=T/1000:

```text
cp = A + Bt + Ct² + Dt³ + E/t²                  J/mol/K
h  = 1000 (At + Bt²/2 + Ct³/3 + Dt⁴/4 - E/t + F)  J/mol
s  = A ln(t) + Bt + Ct²/2 + Dt³/3 - E/(2t²) + G   J/mol/K
```

Mole-weighted mixture h/cp/s are divided by the mixture molar
mass to get J/kg, J/kg/K. Only h/s **differences** are used, and
pressure-entropy and ideal mixing entropy (constant for fixed
composition) cancel in differences at constant pressure. The
published rounded polynomial pieces have tiny h/s jumps at 500 K
for nitrogen and 700 K for oxygen: above-break constants are
shifted to be continuous at the break without altering cp.

The stream implements `cp(T)`, `delta_h`, `delta_s`, and
`temperature_for_delta_h`. The heater and exhaust gas balances
now use these methods if `WasteGasSource.gas_property_model`
is supplied; the older `cp_j_kg_k` and optional linear slope
remain the compatible default.

## B. Coolant: CoolProp single-phase liquid water

`CoolPropLiquidWater(pressure_pa,minimum_temperature_k,
maximum_temperature_k)` uses `HEOS::Water` h/s/cp values
for the **specified fixed water pressure**, returning enthalpy and
entropy *differences*. It rejects inputs outside the declared
temperature interval or at/above the saturation temperature.
It is an opt-in `CoolerSink.fluid_property_model`, which replaces
the nominally constant 4180 J/kg/K water-like placeholder.

Sources:
- [CoolProp Water fluid documentation](https://coolprop.org/fluid_properties/fluids/Water.html)
- [CoolProp 8 high-level property API](https://coolprop.org/coolprop/HighLevelAPI)

The water backend models liquid properties at a fixed pressure.
It does **not** solve water-side friction/pump power, liquid-water
temperature changes along an actual pressured cooling loop,
two-phase quality, environmental discharge limits or tower/fan
performance. CoolProp water EOS values are computational property
reference values, not independent operating measurements.

## C. Hydraulic losses: Darcy–Weisbach + Haaland

New standalone `hydraulics.py` provides:

```text
v = mdot/(rho * πD²/4)
Re = rho*v*D / mu
ΔP = [f*(L/D) + K] * rho*v²/2
f_laminar = 64/Re          (Re < 2300)
1/sqrt(f_turbulent) = -1.8 log10[(eps/3.7D)^1.11 + 6.9/Re]
                             (Re >= 4000)
```

Transition between 2300 and 4000 is **explicitly rejected**.
The published Haaland approximation to Colebrook is an empirical
**pipe friction-factor correlation**; geometry-specific hydraulic
calibration is still necessary before treating it as a heat-exchanger
pressure-drop model. Numerical tests compare laminar results
independently with Hagen–Poiseuille and turbulent friction against
an independently solved Colebrook iteration. References:
- [Literature review of Haaland/Colebrook approximations](https://doi.org/10.3390/jmse10060803).
- [CoolProp density/viscosity API](https://coolprop.org/coolprop/HighLevelAPI).

`co2_pipe_loss` can evaluate real CO₂ density and viscosity at
one specified P/T state. It is **not** a segment-integrated
compressible-pressure-drop solver and does not account for varying
density, thermal profile, hydraulic diameter for microchannels,
entrance effects, branching, fittings, heat-transfer friction
coupling or component maps. No invented physical pipe dimensions
are silently attached to `PressureLosses`.

The existing `FlowScaling` option remains a labelled
**hypothetical sensitivity** and is not replaced with an
unverified geometry guess.

## D. Multi-point component mesh sensitivity

`scripts/g33_component_mesh_sensitivity.py` evaluates two
real-CO₂ operating points, including different near-critical
compressor inlet conditions, on **6/12/24/48** axial sections.
At each prescribed pressure/temperature/mass-flow point, it
re-evaluates the finite-UA recuperator, the NIST dry-air heater
and the CoolProp liquid-water cooler.

It writes `evidence/generated/g33_component_mesh_sensitivity.json`
with individual:
- recuperator heat duty, minimum approach and required UA;
- heater required UA, internal minimum approach, exhaust exit;
- cooler required UA, internal minimum approach, coolant exit
  and entropy generation;
- net shaft output, efficiency and first-law residuals;
- absolute/relative changes from 24 to 48 sections, for each point.

**Distinction:** these are *component ratings at prescribed CO₂ states*,
not solutions satisfying both installed heater and cooler UAs at
each n. They do not validate full coupled operating-point mesh
convergence. No Richardson extrapolation or generalized
grid-convergence index is claimed from two adjacent meshes.

## E. Verification gates and remaining work

- Pure-function tests independently check the printed NIST
  Shomate cp values, piecewise continuity, enthalpy inversions,
  CoolProp water properties, and laminar/turbulent pipe equations.
- The dedicated real-fluid test includes full dual-UA inverse
  with NIST dry air and CoolProp water, using **synthetically sized
  installed UAs** and a coarse 5-section configuration.
- Fixed-state component refinement is documented separately
  from the solved dual-UA control volume.
- G3 physically constrained plant calibration remains **OPEN**
  pending actual geometry and turbomachinery/heat-transfer maps,
  composition-resolved gas, cooling/pumping parasitics, and full
  coupled-plant multi-point near-critical mesh/solver convergence.

## G3.3 acceptance policy

A green CI run establishes *code execution and tested equations*,
not physical model validity. Mark the gate PARTIAL even when the
NIST and CoolProp tests pass. No original Friedman–Rapp EES
replication or MK2014 GA optimum is claimed.
