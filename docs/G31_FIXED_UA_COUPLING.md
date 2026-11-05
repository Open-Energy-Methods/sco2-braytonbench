# G3.1 — physically coupled fixed-installed-UA heater

**Version status:** G3.1 prototype / scientific validation partial (2026-11-05).
**Parent:** [G3 finite-source screening PR #6](https://github.com/Open-Energy-Methods/sco2-braytonbench/pull/6). The new coupled model is a **separate stacked draft PR**.

## Problem being solved

The earlier `evaluate_whr_design` accepts a user-prescribed turbine
inlet temperature `T4` and checks `UA_required <= UA_allowable`.
That is useful for **sizing feasibility**, but it is **not** the
operating point of an existing fixed-area exchanger with unchanged U
and no bypass.

For a single fixed installed gas-to-CO₂ heater, input gas flow and
inlet temperature, working-fluid flow/pressure, fixed recuperator UA,
and compressor inlet conditions, we now solve for **T4** such that:

```text
f(T4) = UA_heater_required(T4) - UA_heater_installed = 0

Q_heater = mdot_CO2 * [h4(T4) - h3(T4)]
Q_gas = mdot_gas * cp_gas * (T_gas_in - T_gas_out)
Q_heater = Q_gas

UA_heater_required = Σ_seg [ dQ_seg / LMTD_seg ]
T_gas(x) - T_CO2(x) >= prescribed minimum approach
T_gas_out >= stack floor
```

The recuperator outlet `h3(T4)` is **not constant**: it is
recomputed at every heater-root iteration using the actual turbine
outlet and **fixed recuperator UA**. This makes the full cycle and
external heater mathematically coupled at steady state.

Both exchanger pressure profiles are *imposed linear assumptions*;
the inlet/outlet pressure states are still set by fixed pressure
drops. Turbomachinery efficiencies and compressor inlet state are
prescribed, not corrected for changes in operating speed.

## Interface

```python
from sco2_braytonbench.fixed_ua import solve_fixed_ua_whr

solution = solve_fixed_ua_whr(
    props, cycle_inputs, waste_gas_source,
    installed_heater_ua_w_k=installed_UA,
    turbine_inlet_bounds_k=(lower_T4_K, upper_T4_K),
    scan_intervals=12,
    tolerance_ua_relative=1e-4,
    tolerance_temperature_k=0.03,
)
T4_solved = solution.turbine_inlet_temperature_k
```

`cycle_inputs.t4_k` is **ignored** by this function. All other
cycle inputs, including CO₂ mass flow, compressor inlet conditions
and recuperator UA, are unchanged.

The solver scans the user-supplied T4 interval and brackets adjacent
**physically feasible** states with opposite residual signs.
It then bisects until both UA relative residual and T4 bracket-width
criteria pass. It returns the actual UA residual, energy balances,
heat exchanger approaches, evaluation count, iteration count and
bracket range.

The solver **does not** extrapolate across an infeasible state or
claim global root uniqueness. It rejects zero or multiple detected
roots, invalid UA, violations of the stack / heater pinch /
recuperator / cooling constraints, and non-convergent brackets.
Coarse scanning can miss a root; the user must verify interval
and resolution sensitivity at important operating points.

## Mathematical independent benchmark

With **zero recuperator UA** and an artificial ideal-gas
constant-cp fluid, the compressor outlet `T2` is independent of
heater outlet `T4`. The gas-to-working-fluid counterflow heater
is then exactly described by classical epsilon–NTU:

```text
C_min = min(m_CO2 cp_CO2, m_gas cp_gas)
C_r = C_min/C_max
NTU = UA_installed/C_min
eps = [1 - exp(-NTU*(1-Cr))] /
      [1 - Cr*exp(-NTU*(1-Cr))]      (C_r != 1)

Q = eps * C_min * (T_gas_in - T2)
T4 = T2 + Q/(m_CO2 cp_CO2)
```

The test suite compares the **coupled T4 root** against this
independent analytical result across several installed heater UA
values, rather than merely checking that the solver reproduces
itself. This is **code verification**, not an actual CO₂ performance
benchmark.

A standard counterflow effectiveness–NTU expression is also
documented by the open-source Heat Transfer project:
https://ht.readthedocs.io/en/latest/ht.hx.html

## Real-fluid experimental study

`tests/test_fixed_ua_real_co2.py` checks two independent
real-CO₂ nominal conditions using CoolProp `HEOS::CO2`.
A known feasible heater point supplies a **synthetically sized
installed UA**; the inverse coupled solver must recover its
original T4, preserve both-side heat balances and satisfy UA,
pinch, exergy and source flow constraints.

`scripts/fixed_ua_coupled_demo.py` fixes this installed UA
after nominal sizing and changes source inlet from **800 K to 810 K**,
so the model must predict the turbine-inlet T shift rather than
accepting it as an input. The JSON records original sized UA,
both solved temperatures, gas outlets, work/efficiency, balances
and solver metadata.

**No measurement or independent original paper's installed-UA
value is used.** The apparatus assumptions and signs are entirely
declared in the code. This is **not** global optimization.

## Remaining physical limitations

1. The original G3 `WasteGasSource.cp_j_kg_k` is **constant**.
   Temperature-dependent source gas cp and composition remain future work.
2. The **cooler remains a boundary condition** imposed through
   compressor inlet T/P, not an independently coupled installed-UA
   cooler with water/air inlet and fan or pump duty.
3. Fixed component pressure losses and turbine/compressor
   isentropic efficiencies remain insensitive to flow and speed.
4. The recuperator assumed `UA` is fixed, but no material,
   geometry, conduction, fouling, pressure-drop/UA coupling or
   hardware measurement is represented.
5. The source exergy screen is constant-cp ideal-gas sensible
   flow-exergy only, with neglected source-pressure/chemical
   contributions, not a full industrial exergy audit.
6. The root scan **tests one user-selected interval** and can miss
   disconnected feasible intervals or additional roots.
7. No transient thermal mass, inventory, valve, bypass control,
   electrical export model, cost or experimental CARBOSOLA data.

**Do not claim full G3 closure or begin PI/MPC based on these
idealized operating points.** Further progress requires a coupled
cooling sink, variable gas cp and physically calibrated
flow-dependent equipment characteristics.
