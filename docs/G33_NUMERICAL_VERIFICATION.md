# G3.3 — reference properties and numerical mesh-refinement results

**Date:** 2026-11-05  
**Scope:** independent sCO₂ Brayton-cycle software; finite-source gas heater and coolant-side heat exchanger; **not a plant twin**.  
**Backend:** CoolProp 8.0.0, HEOS::CO2 and HEOS::Water, with NIST SRD 69 N₂/O₂ ideal Shomate gas.
**Source run:** [GitHub Actions 42010735595](https://github.com/Open-Energy-Methods/sco2-braytonbench/actions/runs/42010735595).
**Machine-readable file:** [G3.3 component-mesh evidence](https://github.com/Open-Energy-Methods/sco2-braytonbench/actions/runs/42010735595/artifacts/13407415665).

## Physically sourced property models — within their domain

`DryAirNISTShomate` uses **79 mol% N₂ / 21 mol% O₂**, fixed dry-air composition,
NIST published Shomate coefficients, valid only **300–1000 K**.
Calculated sensible cp: 300 K **1011.459 J/(kg K)** and 800 K
**1106.475 J/(kg K)**. Gas mixture entropy differences assume
unchanged composition and pressure; H₂O, CO₂, Ar and combustion chemistry
are **not modelled**. NIST references:
[N₂](https://webbook.nist.gov/cgi/cbook.cgi?ID=C7727379&Mask=1)
and [O₂](https://webbook.nist.gov/cgi/cbook.cgi?ID=C7782447&Mask=17).

`CoolPropLiquidWater` uses real-water EOS at fixed **0.3 MPa**,
accepting liquid temperatures within a declared **280–340 K**
interval. CoolProp water fluid file/source:
https://coolprop.org/fluid_properties/fluids/Water.html.
No boiling, water-loop pressure drop, fan/pump work or independent
laboratory coolant properties are claimed.

`hydraulics.pipe_loss` is **Darcy–Weisbach** with laminar
64/Re and turbulent **Haaland** approximated Colebrook friction,
requiring circular-pipe length/diameter/roughness/minor K and supplied
density/viscosity. Transition 2300≤Re<4000 is rejected. The
Haaland equation is an independently published hydraulic correlation
https://doi.org/10.3390/jmse10060803, but **no actual geometry is
provided or connected to the CO₂ component pressure losses**, and this
is not a calibrated HX hydraulic map.

## Multi-point real-CO₂ segment sensitivity

Two intentionally **prescribed-state** cycle operating points:

| Input | Case A | Case B |
|---|---:|---:|
| Low CO₂ pressure P1 | 8.5 MPa | 9 MPa |
| Compressor inlet T1 | 310 K | 314 K |
| Turbine inlet T4 | 650 K | 690 K |
| High-side pressure P4 | 24 MPa | 24 MPa |
| Working fluid flow | 20 kg/s | 20 kg/s |
| Recuperator fixed UA | 200 kW/K | 200 kW/K |
| Dry gas inlet | 800 K | 850 K |
| Gas flow | 100 kg/s | 100 kg/s |
| Liquid coolant inlet | 285 K | 285 K |
| Liquid coolant flow | 75 kg/s | 75 kg/s |

Component inlet/outlet pressures remain fixed nominal ledger values.
These are **not** solutions of both installed heater and cooler UA
equalities at every mesh refinement. The heater and cooler below
are **rated UA requirements** for each point, not concurrently
fixed-geometry operating states.

### Case A: compressor inlet 310 K, P1=8.5 MPa

| Metric | 6 sections | 12 | 24 | 48 |
|---|---:|---:|---:|---:|
| Cycle thermal efficiency (%) | 30.850478 | 30.822519 | 30.813657 | 30.811261 |
| Recuperator duty (MW) | 4.503075 | 4.498888 | 4.497560 | 4.497200 |
| Recuperator minimum approach (K) | 3.728545 | 3.864567 | 3.907765 | 3.919449 |
| Main heater required UA (kW/K) | 21.766931 | 21.777700 | 21.781380 | 21.782395 |
| Cooler required UA (kW/K) | 100.798020 | 101.347517 | 101.490975 | 101.527335 |

### Case B: compressor inlet 314 K, P1=9 MPa

| Metric | 6 sections | 12 | 24 | 48 |
|---|---:|---:|---:|---:|
| Cycle thermal efficiency (%) | 32.298377 | 32.277097 | 32.269671 | 32.267599 |
| Recuperator duty (MW) | 5.190599 | 5.187679 | 5.186659 | 5.186374 |
| Recuperator minimum approach (K) | 4.438926 | 4.538104 | 4.572764 | 4.582438 |
| Main heater required UA (kW/K) | 20.014165 | 20.022297 | 20.025315 | 20.026170 |
| Cooler required UA (kW/K) | 75.643259 | 75.984806 | 76.074502 | 76.097360 |

### Adjacent 24→48 section sensitivity

| Quantity | Case A | Case B |
|---|---:|---:|
| Recuperator Q relative change | 0.007989% | 0.005489% |
| Heater required UA relative change | 0.004661% | 0.004270% |
| Cooler required UA relative change | 0.035813% | 0.030037% |
| Cycle η absolute change | 0.002396 percentage points | 0.002072 percentage points |
| Recuperator minimum approach absolute change | 0.011684 K | 0.009674 K |

**Important physical finding:** although local numerical changes
are small, the *recuperator* approaches at 48 sections are only
**3.919 K and 4.582 K**. A hypothetical minimum 10 K approach
would reject both points. Small mesh sensitivity does **not**
imply adequate design pinch margin.

For reference, the heater minimum approach was **150 K** in A
and **160 K** in B at each resolution. The cooler minimum
approaches remained positive with no reported pinch violations.
The sensitivity script asserts relative stream energy residuals,
positive exchanger approaches, and real-fluid property domain.

## CI evidence, mathematical tests and caveats

[Successful G3.3 convergence artifact](https://github.com/Open-Energy-Methods/sco2-braytonbench/actions/runs/42010735595/artifacts/13407415665)
contains all figures above, full pressure/temperature assumptions,
and the residuals.

The independent property/hydraulic CI job passed **35 tests**
including NIST coefficient checks, enthalpy/entropy inversions,
real-water EOS consistency, classical laminar Hagen–Poiseuille
and Haaland/Colebrook comparison and a real-CO₂ dual-UA
inverse test with NIST dry-air and CoolProp water.

Both Python 3.11 and 3.12 fixture suites passed
**205 tests** each (9 optional CoolProp modules skipped in those
fixture-only jobs), and the existing real-CO₂ property and source
screen checks also passed.

Numerical implementation corrections made during verification:
(1) use the declared `minimum_approach_k` field of the cooler,
(2) evaluate energy conservation on a relative scale, rather
than demanding a temperature-inverted water duty residual
below 10⁻⁵ W at multi-MW duty, and (3) refine CoolProp's P/H
temperature flash against the direct P/T enthalpy equation
using cp=(dh/dT) at fixed pressure.

### Stage-gate decision

- G1-A: mathematical source/transport correlations implemented and tested
  at a small, auditable set of reference states.
- G1-E: CO₂ EOS experimentally supported for density by prior work;
  water EOS here is **software reference**, not independent measured
  water validation.
- G3.3: **local component-level mesh sensitivity passed** at two
  *prescribed state* operating points. No global Richardson/GCI
  proof or full dual-fixed-UA operating-point convergence.
- G3: **INDUSTRIAL OFF-DESIGN VALIDATION OPEN.** Missing actual gas
  composition, geometry/UA/friction maps, compressor/turbine maps,
  water-loop auxiliaries, source/sink seasonality and full
  near-critical envelope grid.
- G4/G5: no conserved transient plant or PI/MPC validation.

These numbers are computationally reproducible, not empirical
measurements from HZDR/CARBOSOLA or published numerical optima
from Mohagheghi–Kapat.
