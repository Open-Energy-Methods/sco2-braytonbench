# G3 — Industrial waste-heat recuperated Brayton design screening

**Scope:** Independent and exploratory real-CO₂ steady-state model informed by
Mohagheghi & Kapat (2014), *Thermodynamic Optimization of Recuperated S-CO₂
Brayton Cycles for Waste Heat Recovery Applications*.

This is not a reproduction of the 2014 REFPROP/GA optimum, and is not an
HZDR/CARBOSOLA plant model.

## Source-derived motivation versus independently chosen design

### Source-derived (2014 paper, physical pages 5–11)

- Heat supplied by a **finite flow of exhaust gas** is not an externally
  fixed thermal-power boundary: the cycle mass flow, temperature programme,
  heater pinch and amount left for the stack interact.
- Their gas is modelled using **air thermophysical properties** and their
  illustrative mass flow is **100 kg/s**.
- Source Table 2: 300 K ambient, 310 K minimum cycle T, fractional
  pressure drop 0.02, compressor/turbine isentropic efficiencies 0.89/0.90.
- Their RC and RRC cycles are distinct. The recuperator terminal temperature
  difference and main-heater pinch are optimization decision variables.
- Their objective is bottoming-cycle power, not just Brayton thermal
  efficiency; their numerical results are mainly graphical.

### Our independent model

- **Six-state RC only.** Inputs are absolute pressures, compressor inlet T,
  turbine inlet T, working-fluid mass flow and component pressure losses in
  pascals. These pressure drops are **not equivalent** to their 2% FPD
  convention.
- Thermodynamic properties via **CoolProp HEOS::CO2**; the paper used
  REFPROP with its chosen reference state.
- Turbomachinery uses constant isentropic efficiencies and adiabatic
  enthalpy changes. No measured machine maps, shaft dynamics, or electrical
  conversion efficiency are included.
- Recuperator uses **fixed finite UA**, segmented enthalpy conservation,
  local counterflow temperature approaches, and an explicit pressure-profile
  assumption. Required UA is inferred using the local LMTD integral.
- External exhaust is represented by a specified mass flow and **constant
  sensible-gas `cp`**, source inlet temperature, stack minimum, dead state,
  and minimum heater pinch. This is a deliberate simplification of the
  paper's temperature-dependent REFPROP air model.
- The heater `maximum_heater_ua_w_k` is a **design sizing allowance**;
  `UA_required <= UA_limit` is a feasibility constraint. We do **not**
  solve `UA_required = UA_installed` for turbine inlet T, and no explicit
  bypass, part-load conductance or plant valve law is modelled.
- `maximum_shaft_power` refers to **net shaft work**
  `W_turbine-W_compressor`, not electrical export.
- Designs with negative net power, stack-temperature violations, pinch
  crossing, insufficient heater sizing allowance, or energy/exergy
  contradictions are rejected with machine-readable reasons.

## Conservation checks

For each feasible candidate:

```text
Q_IHX = m_CO2 * (h4 - h3)
Q_gas = m_gas * cp_gas * (T_gas_in - T_gas_out)
Q_gas - Q_IHX ~ 0

W_net_shaft = m_CO2 * [(h4-h5) - (h2-h1)]
Q_IHX - Q_cooler - W_net_shaft ~ 0

T_gas_out >= T_stack_floor
min_x [T_gas(x) - T_CO2(x)] >= DT_min
UA_heater,required <= UA_heater,allowable
Q_IHX <= m_gas * cp_gas * (T_in - T_stack_floor)
```

Optional steady-state finite-stream exergy screen uses a **constant-cp
ideal-gas sensible cooling** approximation with dead-state T0:

```text
E_gas,consumed = m_gas cp_gas [
  (T_gas_in - T_gas_out)
  - T0 ln(T_gas_in / T_gas_out)
]
W_net_shaft <= E_gas,consumed
```

This simple exergy upper bound neglects kinetic/pressure exergy,
chemical exergy and equipment auxiliary work. It does not constitute an
industrial exergy audit.

## Independent analytic regression cases

- Equal heat-capacity-rate counterflow HX:
  `epsilon = NTU/(1+NTU)`, `Q=epsilon*C*(T_hot,in-T_cold,in)`.
- Unequal heat capacity rates:
  `epsilon=(1-exp[-NTU(1-Cr)])/(1-Cr exp[-NTU(1-Cr)])`.
- Ideal-gas compressor/turbine:
  `T_is,out/T_in=(P_out/P_in)^(R/cp)`, corrected by isentropic efficiency.
- Source gas sensible-energy balance, heat-exchanger UA/stack/pinch limits,
  mass and enthalpy closure, rejection diagnostics and objective ranking.

These identities verify **implementation mathematics**, not real-sCO₂
experimental plant performance.

## Real-fluid screening

`python scripts/whr_design_screen.py` samples a deterministic,
independently chosen `T4 × m_CO2` grid with CoolProp 8.0.0, a gas
supply of 100 kg/s at 760 K and 1100 J/(kg K), compressor inlet
temperature 310 K, pressures 8.5/24 MPa and finite recuperator UA.

The script produces:
- `evidence/generated/whr_design_screen.json`: all assumptions,
  feasible/rejected counts, best-power and best-efficiency candidates,
  power/heat/exergy and performance data, and limitations.
- `evidence/generated/whr_grid_matrix.csv`: one row per candidate,
  including reason for rejection.

These are **screening optima over a finite prescribed grid**; no
global optimizer, figure digitization, published benchmark reproduction
or claim that the selected design is economic has been established.

## Gate requirements before real plant/control use

1. Verify temperature/discretization convergence under real-fluid
   near-critical gradients and fixed-UA off-design operation.
2. Add temperature-dependent gas properties and experimentally
   defensible heater/recuperator conductance and pressure-drop models.
3. Close energy, entropy and source-boundary checks over a larger
   operating domain, including non-feasible cases.
4. Add cooling-capacity and parasitic equipment constraints.
5. Compare source paper figures qualitatively only unless numerical
   design-point data and exactly equivalent assumptions are recovered.
6. Establish dynamics only from physically conserved inventories,
   calibrated time constants and admissible control actuators.

**G3 is partial / exploratory, not validated industrial operation.**

## Robustness audit — additional independent constraints

The source paper's recuperator terminal temperature-difference
design variable is **not** equivalent to our internal minimum
recuperator approach. Our optional `PlantDesignLimits` checks an
**independent engineering scenario** with:

- Minimum resolved recuperator approach: **10 K**.
- Cooler heat-rejection sizing allowance: **15 MW_th**.

Both are explicitly assumed here for sensitivity only, not as
measurements or values published by Mohagheghi & Kapat. They are
optional; the primary screening remains unchanged. For the original
unconstrained optimum, the initial coarse calculation found:

| Metric | Power-max case | Efficiency-max case |
|---|---:|---:|
| Turbine inlet T | 700 K | 700 K |
| CO₂ flow | 100 kg/s | 20 kg/s |
| Net shaft power | 8.110 MW | 1.622 MW |
| Cycle thermal efficiency | 25.218% | 33.504% |
| Available source heat recovered | 73.087% | 11.003% |
| Heater minimum approach | 13.108 K | 60.0 K |
| Recuperator minimum approach | 64.738 K | 4.627 K |
| Cooler thermal rejection | 24.049 MW_th | 3.219 MW_th |

The power-max design fails the additional **15 MW_th** cooler
constraint; the efficiency-max design fails the additional **10 K
internal recuperator approach** constraint. Neither baseline
winner is therefore robust to both of these **illustrative new
constraints**.

The script now rescans the complete grid under the new constraints,
and re-evaluates both original winners using **12, 24 and 48**
segments for the recuperator and gas heater. The reported
`whr_robustness.json` includes the quantitative mesh changes and
new feasible rankings. This is an independent engineering sensitivity
check, not a full convergence study over the entire parameter domain.

In the future, a fixed installed heater design requires equality
`UA_required ≈ UA_installed` or justified operation with
controlled bypass. A screening UA *upper limit* alone must not be
misrepresented as a closed off-design plant model.
