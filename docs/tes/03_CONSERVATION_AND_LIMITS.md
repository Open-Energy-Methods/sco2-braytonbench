# TES-v0.2 — Conservative numerical kernel and independent limit tests

**Implementation:** `src/sco2_braytonbench/thermal_storage.py`.
**Test:** `tests/test_thermal_storage.py`.

The finite-volume fluid and solid cell capacities are computed from *fluid holdup* epsilon*rho_f and solid fraction (1-epsilon)*rho_s. A packed bed's rock capacity must not implicitly replace the moving fluid's thermal inventory.

## Executable contracts

| Case | Independent check | Why |
|---|---|---|
| All initial cell temperatures = inlet | All derivatives and heat fluxes exactly zero | No spurious heating or dilution |
| Zero interphase conductance | One-cell fluid has analytic exponential response to inlet; solid unchanged | Verifies advection term and units |
| Zero flow | One-cell fluid and solid approach capacity-weighted thermal equilibrium exponentially | Verifies internal heat transfer and no false source energy |
| Reverse direction | A spatially reversed profile and sign-reversed flow produce spatially mirrored output | No accidental reverse-flow energy creation |
| Uniform volumes vs cell count | Total Cf, Cs independent of N | Grid-independent physical inventory |
| Charge with hot fluid | Positive boundary heat; solid temperature/SOC increase | Correct physical sign |
| Reverse discharge to cold fluid | Negative boundary heat; solid SOC decreases | Correct physical sign |
| Complete energy ledger | Boundary enthalpy integral = total fluid+solid energy increase | First law |
| Invalid porosity, N, Hv, temperatures, dt | ValueError rather than silently repaired input | Domain integrity |
| Excessive required number of substeps | Explicit error | Prevents hidden runaway workload |

## SSPRK3 stage bookkeeping

The method uses Shu–Osher SSPRK3 stages. With state y and ODE F(y):

- y1 = y + h F(y)
- y2 = 3y/4 + (y1 + h F(y1))/4
- y_next = y/3 + 2(y2 + h F(y2))/3

Rearrangement yields the same step as y_next=y+h*(F(y)/6+F(y1)/6+2*F(y2)/3). The boundary flux is integrated with **exactly those weights**. An energy residual close to roundoff is an expected algebraic consequence of this matched quadrature, and cannot be treated as measurement accuracy.

For positive initial/source temperatures, each forward Euler stage is a convex mixture if h*(adv_rate+fluid_exchange)≤1 and h*solid_exchange≤1. SSPRK3 is likewise convex under this bound. We use a safety factor of 0.75 and automatically divide each requested held-input interval into enough substeps; if it would exceed a declared max_substeps the operation fails transparently.

A positivity-preserving scheme can still be quantitatively inaccurate due to numerical diffusion. See the separate Schumann and timestep study.

## State of charge

Solid SOC is defined against **declared** design temperatures cold_k<hot_k. It is the weighted solid sensible inventory fraction only; fluid inventory is counted separately in the full first law. Out-of-range SOC is returned, **not silently clipped**. An apparently perfect SOC trajectory does not establish usable outlet-temperature grade.

## Missing physics

There is no momentum equation, pressure drop, detailed fluid composition, axial conduction, moving solid, PCM melt fraction, wall heat leak, stratification in cross-section, actual particle Biot-number check or plant-scale valve dynamics. For a real rig, these are candidates for independent investigation rather than implied solved physics.

**Release meaning:** If CI passes, TES-v0.2 is a numerically conservative *idealized simulator kernel*, not experimentally validated TES.
