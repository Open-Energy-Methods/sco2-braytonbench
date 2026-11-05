# G3.2 — coupled installed heater/cooler UA verification record

**Date:** 2026-11-05  
**Model:** independently assumed six-state recuperated CO₂ + finite gas and coolant streams  
**Backend:** CoolProp 8.0.0 `HEOS::CO2` / Python 3.11  
**Evidence:** [GitHub Actions run 42005964249](https://github.com/Open-Energy-Methods/sco2-braytonbench/actions/runs/42005964249) (**all six jobs passed**) and [machine-readable G3.2 JSON artifact](https://github.com/Open-Energy-Methods/sco2-braytonbench/actions/runs/42005964249/artifacts/13405495551).

## Boundary conditions and provenance

Both installed heat exchangers are **synthetically sized** from a single
self-consistent nominal model case. This is a software inverse-validation
exercise: the selected UAs are neither measured hardware parameters
nor independently reported reference values.

| Assumption | Value |
|---|---:|
| Exhaust gas inlet | 800 K |
| Exhaust flow | 100 kg/s |
| Gas sensible cp model | 1100 J/(kg K) at 300 K; linear slope +0.20 J/(kg K²) |
| Coolant inlet reference | 285 K |
| Coolant flow | 75 kg/s |
| Coolant sensible cp | 4180 J/(kg K), constant |
| Nominal compressor inlet | 310 K |
| Nominal turbine inlet | 650 K |
| CO₂ flow | 20 kg/s |
| CO₂ low-side pressure | 8.5 MPa |
| Turbine inlet pressure | 24 MPa |
| Recuperator installed UA | 200 kW/K |
| Heater installed UA from nominal sizing | 21.625962 kW/K |
| Cooler installed UA from nominal sizing | 100.514392 kW/K |
| Heat-exchanger segments | 5 (coarse; illustration only) |
| Source model | Sensible air-like stream, **no measured composition** |

Other pressure drops, efficiencies and source/coolant bounds are
explicit in `scripts/coupled_sink_demo.py`. The source gas cp slope,
water-like coolant cp and fixed HX UAs are **illustrative choices**,
not NIST air/water datasets or industrial equipment maps. A 5-section
HX calculation should **not** be interpreted as converged.

## Two independently solved steady operating points

| Output | Coolant entering at 285 K | Coolant entering at 287 K |
|---|---:|---:|
| Compressor inlet T1 (K) | 310.004883 | 310.463867 |
| Turbine inlet T4 (K) | 650.019531 | 652.216797 |
| Exhaust gas exit (K) | 761.434830 | 761.969130 |
| Coolant outlet (K) | 295.172950 | 297.025449 |
| Net shaft power (MW) | 1.423728 | 1.406263 |
| Thermal efficiency (%) | 30.863734 | 30.912031 |
| Heater transferred heat (MW) | 4.612948 | 4.549241 |
| Cooler rejected heat (MW) | 3.189220 | 3.142978 |
| Heater actual required UA (kW/K) | 21.625691 | 21.627529 |
| Cooler actual required UA (kW/K) | 100.448503 | 100.572653 |
| Relative heater UA residual (%) | 0.001251 | 0.007246 |
| Relative cooler UA residual (%) | 0.065552 | 0.057963 |
| Cooler entropy generation (W/K) | 1154.805 | 1125.584 |
| Outer iterations | 10 | 10 |
| Outer thermo evaluations | 14 | 14 |
| Final inner iterations | 8 | 9 |

Changing only coolant inlet temperature from 285 to 287 K, with
installed heater UA and cooler UA constant, gives:

- `T1` shift **+0.458984 K**
- `T4` shift **+2.197266 K**
- Net shaft power shift **−17.465 kW**
- Cycle thermal efficiency shift **+0.0483 percentage points**

The efficiency increase is consistent with this particular model's
reduced transferred heater duty; it is **not** evidence that
warmer coolant generally improves sCO₂ cycle thermodynamics.

## Conservation and numerical checks

For the 285 K coolant reference:
- CO₂ cycle first-law residual **+1.40e−9 W**
- Gas-to-CO₂ heater first-law residual **+9.31e−10 W**
- CO₂-to-coolant cooler first-law residual **−2.33e−9 W**
- Total cooler entropy generation **+1154.8 W/K**

For the 287 K inlet:
- CO₂ cycle first-law residual **+4.66e−10 W**
- Gas-to-CO₂ first-law residual **+9.31e−10 W**
- Cooler first-law residual **−9.31e−10 W**
- Total cooler entropy generation **+1125.6 W/K**

The numerical equality tolerances for this demonstration were
`relative UA error < 0.08%` on the cooler and `<0.02%`
on the heater. These are computational error bounds, **not physical
uncertainty or experimental measurement accuracy**.

### CI execution

The [verified run](https://github.com/Open-Energy-Methods/sco2-braytonbench/actions/runs/42005964249)
passed all six jobs, including:
- Fixture test suites on Python 3.11 and 3.12:
  **178 tests passed, 8 optional real-fluid modules skipped** each.
- Legacy real-CO₂ property crosschecks / measured-density suite passed.
- G3 finite-source screen passed.
- G3.1 fixed-installed heater-UA checks passed.
- Dedicated G3.2 real-CO₂ dual-UA inverse test: **1 passed**.
- Cooler-inlet perturbation script completed and exported source/UA
  and flow-loss sensitivity JSON.

## Flow-dependent pressure loss: optional scenario, not identification

The bundled **assumption-only** example defines
`ΔP=ΔP_ref*(m/m_ref)^2` at reference CO₂ 20 kg/s. With
efficiency penalties of 0.02*(ratio−1)²:

| CO₂ flow (kg/s) | Heater pressure drop (kPa) | Cooler drop (kPa) | ηc | ηt |
|---:|---:|---:|---:|---:|
| 10 | 37.5 | 12.5 | 0.885 | 0.895 |
| 20 | 150.0 | 50.0 | 0.890 | 0.900 |
| 30 | 337.5 | 112.5 | 0.885 | 0.895 |

**These flow-scaled losses were NOT applied in the two dual-UA
temperature-perturbation results above.** They are available as
an opt-in model for future sensitivity studies. Without measured
geometry, hydraulic characteristics, compressor/turbine maps or
shaft-speed dependence, this formula is **not a validated equipment
model** and does not match MK2014's 2% fractional pressure loss
assumption.

## Gate decision / blockers

**G3.2 narrow numerical implementation verification:** passed on
the specified analytic and real-CO₂ cases.

**G3 industrial off-design validation:** remains **OPEN**.

Important remaining blockers:

1. Only five HX segments and one synthetically sized reference
   configuration were tested with real CO₂. Temperature/pinch and UA
   convergence must be assessed over a range, especially near the
   pseudocritical region.
2. Coolant is a no-phase-change sensible stream; liquid-water
   thermophysical property variations, cooling loop pressure,
   pump/fan parasitics and environmental outlet constraints remain
   unsolved.
3. Source cp is a trial linear function, not a composition-resolved
   combustion-gas property model or independent experimental data.
4. Heat-transfer coefficients, UA, fouling, wall temperature,
   mechanical integrity, and pressure losses are not linked to
   exchanger geometry or flow.
5. Compressor/turbine isentropic efficiencies remain fixed in the
   principal dual-UA calculation. Pressure/efficiency scaling is
   available only as an uncalibrated opt-in scenario.
6. The nested numerical solver is computationally costly; its
   finite scan only detects roots within a user-selected feasible
   domain and is not a proof of unique global steady state.
7. No rotor/working-fluid inventory dynamics, actuators, control
   authority, MPC, cost model, CARBOSOLA measurements or source-paper
   optimum reproduction is present.

**Next priority:** calibrated heat exchanger and turbomachinery
characteristics, a coolant pressure/phase model, source composition
and a broader segmentation/operating-envelope study. Do not begin
physical closed-loop control claims on this numerical evidence alone.
