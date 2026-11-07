# TES-v0.4 — Prescribed charge/hold/discharge schedules

## Operation and causality

A stage specifies an **observed-from-outside / prescribed** (not optimized) inlet temperature, signed mass flow and duration. Charge and discharge flow may have opposite sign: negative flow enters at the opposite end of the *same physical bed*. Hold requires exactly zero throughflow, but fluid and solid temperatures may continue equilibrating through finite interphase heat transfer.

Each stage calls the conservative TES-v0.2 finite-volume solver from the previous state. No stage can instantaneously reset the bed temperature. The full fluid and solid holdup carries across all stage boundaries.

A stage labelled charge must result in nonnegative **actual** net inlet-minus-outlet energy; discharge must result in nonpositive net energy. A contrary result raises a ValueError rather than silently misclassifying a source reversal as charging.

## Integrated energy quantities

Charge input = sum of positive stage boundary heat integrals, in J.
Recovered heat = magnitude of the sum of negative stage boundary integrals, in J.
Residual inventory = final fluid+solid sensible inventory minus the initial fluid+solid inventory, in J.

The executable identity is

\[
E_{\mathrm{charge}}-E_{\mathrm{withdrawn}}=\Delta U_{\mathrm{bed}}
\]

where `U_bed` includes **fluid and solid storage** and signed inlet/outlet advection.

The **designed solid capacity** `C_s,tot (T_hot-T_cold)` is distinct from the bed's initial/final heat and does not automatically include fluid or any useful outlet-temperature constraint.

## Incomplete cycles

A gross energy round-trip ratio is returned **only when**:
1. At least one charge and one discharge stage were declared.
2. The charged energy is positive.
3. Every final **fluid and solid cell temperature** returns within a declared `state_return_tolerance_k` of the corresponding initial cell.

Merely having charge and discharge stages does not close the cycle. Even a near-zero net energy balance can conceal a different temperature profile, so energy-only closure is not sufficient.

If the full-state return condition fails, `gross_energy_efficiency=None` and `complete_cycle=False`. A null ratio is not evidence of zero efficiency. The model is adiabatic and ideal, so it must not be presented as a measured plant round-trip-efficiency forecast.

## Demonstration and evidence

```bash
python -m pytest -q tests/test_tes_cycles.py
python examples/tes_charge_discharge.py
```

The example saves `evidence/generated/tes_v04/synthetic_storage_stage_trace.csv` with signed stage duty, actual outlet and solid SOC, followed by `synthetic_storage_summary.json` with the real global first-law residual and `complete_cycle` flag.

Tests cover charge/hold/reverse discharge, invalid stage modes and signs, no-flow equilibration, incomplete-cycle criteria, unique stage IDs, capacity and full-stage energy conservation.

The example is **a synthetic thermal packed-bed exercise**. It is not a direct gas→sCO₂ power-block interface, an experimental TES unit, a real turbine controller or a physical full-cycle heat-loss calibration. A future TES-v0.5 adapter must supply distinct real gas-side and CO₂-side exchanger boundaries so that heat is never counted twice.
