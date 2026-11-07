# TES-v0.5 — Explicit open-stream TES-to-quasi-steady-Brayton boundary

**Topology matters more than a matching plot.** This prototype connects a synthetic packed bed to the *existing* finite-source heater and six-state quasi-steady Brayton model without creating a second imaginary heat input.

## Physically declared interfaces

The independently prescribed, open heat-transfer-fluid path is:

~~~text
External boundary: HTF at T_in, mass flow mdot
  -> sensible packed bed (solid/fluid energy inventory)
  -> existing gas-to-CO2 finite-source heater
  -> external outlet at T_heater_exit.

CO2 path is the existing six-state recuperated cycle:
  CO2 state 3 -> heater -> state 4 -> turbine/recuperator/cooler
  with Q_heater = Q_cooler + W_net (within model convention).
~~~

**This is an OPEN SINGLE-PASS STREAM.** No closed recirculation or return-temperature solve, simultaneous shared industrial exhaust split, turbine shaft-inertia dynamics or TES-charging waste-gas exchanger is asserted. The bed inlet is an external specified boundary. The cycle is algebraic at the bed's **final** outlet temperature, not a time-integrated dynamic Brayton cycle.

## Thermodynamics: no double counting

At an end-of-interval snapshot let HTF capacity rate `Cdot=mdot*cp_f` [W/K]. Using bed inlet `T_in`, final bed outlet `T_b` and the *actual* finite-source heater gas outlet `T_h` solved by the existing `whr.py` model:

\[
\dot U_{\mathrm{bed,end}}=\dot C(T_{in}-T_b),
\quad
\dot Q_{\mathrm{CO2,heater}}=\dot C(T_b-T_h),
\]

\[
\dot Q_{\mathrm{external,net}}=\dot C(T_{in}-T_h)
=\dot U_{\mathrm{bed,end}}+\dot Q_{\mathrm{heater}}.
\]

For the internal cycle, \(\dot Q_{\mathrm{heater}}=\dot Q_{\mathrm{cooler}}+\dot W_{\mathrm{net}}\). Therefore the **combined instantaneous** residual is

\[
R_W=\dot Q_{\mathrm{external,net}}
-\dot U_{\mathrm{bed,end}}
-\dot Q_{\mathrm{cooler}}
-\dot W_{\mathrm{net}}.
\]

The code checks both the gas-to-CO2 heater equality and this combined power balance. The bed's time-step ledger `E_boundary−ΔU_bed` is separately in **J**, not W.

It is **invalid** to add an interval-integrated bed heat (J) to the final snapshot heater duty (W). A future fully integrated schedule requires evaluating the algebraic CO2 state over the interval (e.g. stage quadrature at every RK evaluation) and handling the resulting root solver and HX constraints.

## Numerical implementation

- `src/sco2_braytonbench/tes_coupling.py`: advances a constant-property bed under a specified flow/temperature, forms a **new** `WasteGasSource` from its final outlet, and uses the existing `evaluate_whr_design` cycle/heater source.
- Enforces positive forward HTF flow and a positive hot-end approach; rejects an outlet below specified stack floor.
- Reuses the actual `point.cycle.heater_w`, `point.heater.gas_out_k`, `point.cycle.cooler_w` and `point.cycle.net_w` rather than assigning a new independent thermal power.
- Explicitly labels the returned state `instantaneous_stage_time="end_of_interval"`.
- Synthetic ideal-gas fixture and a guarded real-CoolProp compatibility smoke use **different** working-fluid sources; both require separately feasible states.

## Verification

~~~bash
python -m pytest -q tests/test_tes_coupling.py
python examples/tes_coupled_discharge.py
~~~

The synthetic JSON includes the end-stage bed J-terms and end-stage cycle W-terms as distinct objects with explicit source classification. Dedicated CI includes a CoolProp-pinned smoke test in addition to the ideal-gas check.

This is the **narrow, checkable beginning** of TES-v0.5 integration: a single-pass discharge to a quasi-steady Brayton cycle. It does not yet establish full simultaneous source/TES dispatch, a closed thermal loop, storage during changing external gas input, or experimentally identified power output. Those remain scoped continuation work rather than falsely treated as complete.
