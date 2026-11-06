# G4/WP2b — finite waste-gas source, thermal storage and quasi-steady Brayton cycle

**Research status (6 November 2026):** implemented and awaiting independent CI/review. This is a **single-lumped-wall transient system with an algebraic recuperated Brayton power block**, not a full CO₂-inventory transient model, G3.2 finite-coolant transient solver or CARBOSOLA digital twin.

## 1. Physical system and control-volume ledger

The new `src/sco2_braytonbench/dynamic_whr.py` replaces the instantaneous *direct gas→CO₂ heating assumption* with two distinct fixed-thermal-conductance interfaces:

```text
 finite gas waste-heat stream        single thermal solid wall            recuperated CO2 cycle
  (m_g, cp_g, Tg,in)          (Twall, Cwall = dUwall/dT)              (states 3 -> 4)
        |                              |                                   |
        +--- installed UA_g,w ---> [ Q_g,w ] -- stored Uwall --- [ Q_w,CO2 ] ---> CO2 heater
                                                                    |
                                                 cycle first law: Q_w,CO2 = Wnet + Qcooler
```

Gas flow is *finite* and leaves at an explicitly calculated temperature; the wall holds the **only dynamic energy inventory**. The cycle state at a given wall temperature is solved algebraically with existing `solve_cycle`. The compressor-inlet temperature and CO₂ flow/pressures and compressor/turbine efficiencies remain **prescribed, not dynamic states**. The recuperator, compressor, turbine and cooler are **quasi-steady** at every evaluation.

No original `waste_gas_heater` direct-to-CO₂ duty is added. **The CO₂ cycle's existing state 3→4 heater duty is the energy leaving the thermal wall:** double-counting that heat would violate the combined first law.

### Finite source gas to isothermal wall

For a constant source gas specific heat and gas-side UA at instantaneous wall temperature:

```text
C_g = m_g * cp_g                                        [W/K]
epsilon_g = 1 - exp(-UA_g,w/C_g)                         [-]
Q_g,w = C_g*(T_g,in - T_wall)*epsilon_g                 [W]
T_g,out = T_g,in - Q_g,w/C_g                            [K]
```

This is the *exact constant-property gas stream / isothermal wall* relation, not a counterflow gas→CO₂ LMTD calculation. Source inlet temperature and mass flow can be changed between load intervals. Gas exit is checked against a specified stack-temperature floor; the gas-wall outlet approach must remain positive.

### Isothermal wall to actual CO₂ heater

```text
Q_w,CO2 = m_CO2 * (h4 - h3)                             [W]
T_CO2(x) = T(p3 + x*(p4-p3), h3 + x*(h4-h3)), x in [0,1]
UA_w,CO2,required = sum_i [ (Q_w,CO2/n) /
   LMTD(T_wall-T_CO2(x_i), T_wall-T_CO2(x_{i+1})) ]  [W/K]
UA_w,CO2,required(T4) = UA_w,CO2,installed               [W/K]
```

For each prescribed wall temperature, the code finds the turbine inlet temperature **T4** satisfying the installed isothermal wall→CO₂ conductance *equality*, while the existing cycle solver provides the recuperator outlet state 3 and full cycle duties. It checks local approach, root brackets, actual installed UA residual and physical cycle feasibility. Invalid/unbracketed/multiple roots are explicit exceptions.

**Important:** the wall is an assumed isothermal solid, source gas and CO₂ transfer interfaces have independent UAs. This is *not* a measured overall PCHE U-value and should never be mistaken for a single conventional counterflow gas→CO₂ exchanger UA.

### The only differential equation

```text
C_wall * dT_wall/dt = Q_g,w(Twall, Tg,in, mg) - Q_w,CO2(Twall)
```

The RK4 solver evaluates the **full quasi-steady CO₂ cycle at each RK4 stage**; it integrates `Q_g,w`, `Q_w,CO2`, `Q_cooler` and `W_net` with the *same four quadrature stage weights*:

```text
E_g,w - E_w,CO2 = ΔU_wall = C_wall * (Twall,end - Twall,start)
E_w,CO2 = E_cooler + E_net                    (quasi-steady cycle, stagewise)
E_g,w = ΔU_wall + E_cooler + E_net            (combined transient first law)
```

Thus the gas energy removed is accounted for **exactly once** as either wall storage, cycle shaft energy, or cooler rejection. Both the source gas and the cycle heater states are independently checked. A small residual verifies *algebraic bookkeeping*, **not** temporal discretisation accuracy. Time-step refinement against an independently derived exponential limit is also mandatory.

RK4 is explicit, so the implementation enforces a conservative `dt <= fraction * Cwall/(effective_gas_conductance+installed_wall_CO2_UA)` bound and fails rather than silently taking an unstable step. A continuous underlying ODE solution is only approximated; the source load is piecewise constant during each declared interval.

## 2. Analytical closed-form verification, independent of the implementation

For an *artificial constant-cp fluid*, installed recuperator UA = 0, and fixed compressor inlet state, the compressor outlet temperature `T3` is fixed independently by textbook ideal-gas compression:

```text
T3 = T1 + (T1*(P2/P1)^(R/cp) - T1)/eta_compressor
C_CO2 = m_CO2*cp_CO2
T4(Twall) = Twall - (Twall-T3)*exp(-UA_w,CO2/C_CO2)
H_g = C_g*(1-exp(-UA_g,w/C_g))
H_c = C_CO2*(1-exp(-UA_w,CO2/C_CO2))
T_wall,eq = (H_g*Tg,in + H_c*T3)/(H_g+H_c)
tau = C_wall/(H_g+H_c)
T_wall(t) = T_wall,eq + (T_wall,0-T_wall,eq)*exp(-t/tau)
```

The test fixture uses: `P1=8 MPa`, `P4=24 MPa`, `T1=310 K`, `eta_c=0.89`, `eta_t=0.9`, `mCO2=10 kg/s`, `cp=1000 J/(kg K)`, `R=200 J/(kg K)`, `mgas=30 kg/s`, `Tg,in=850 K`, `cp_g=1100 J/(kg K)`, `Cwall=2 MJ/K`, gas-wall `UA=40 kW/K`, wall-CO₂ `UA=25 kW/K`, initial wall `T=700 K`. These are **synthetic**.

Independently re-derived reference values:

| Analytic quantity | Expected |
|---|---:|
| Compressor outlet T3 | 396.4919 K |
| Gas-wall effective conductance Hg | 23,180.3415 W/K |
| Wall-CO₂ effective conductance Hc | 9,179.1500 W/K |
| Wall equilibrium temperature | 721.3571 K |
| Thermal time constant | 61.8057 s |
| Initial instant T4 at Twall=700 K | 675.0865 K |
| Wall temperature after 60 s constant source | 713.2673 K |

Tests compare the code **against these independently obtained relations**, not against another invocation of its own root solver. They also verify a cooler/power/output first law, wall storage, change of load and flow, finite stack, unbracketed UA, explicit failure of excessively long time steps, and finer-step convergence.

## 3. Evidence and reproduction

```bash
python -m pip install -e '.[test]'
python -m pytest -q tests/test_dynamic_whr.py
python examples/waste_heat_wall_coupled_cycle.py
```

The source-controlled example outputs `evidence/generated/v1_wp2b/scenario_trace.csv` and `scenario_summary.json`. The two *hypothetical* inputs include a 45-s variable-gas-temperature and mass-flow disturbance and a constant-source baseline. The time series reports gas exit T, wall T, turbine inlet T, quasi-steady predicted shaft power, and integrated gas/wall/cycle energy budgets. The comparison is on exactly matched time grids and assumptions.

**Test evidence classes:**
1. Independent textbook constant-cp closure, exact exponential solution, integral conservation and time-step refinement — **analytic/numerical mathematical verification**.
2. Same code with real CoolProp `HEOS::CO2` under chosen feasible boundary values — **real-fluid model numerical smoke only**, if the dedicated CI job is successful.
3. No matching CARBOSOLA operating measurements, no independent experimental transient energy data, no identified wall C/UA/pressure maps — **full G4 validation OPEN**.

## 4. Explicit non-claims and next work

- This is **not** the existing G3.2 fixed hot-gas + finite liquid-coolant **two-UA cycle model with time dependence added**. Instead, this is a *new* three-interface architecture: gas-to-wall UA + wall-to-CO₂ UA + algebraic recuperated cycle; cooler inlet state T1 remains fixed.
- Constant gas cp is illustrative. Stream composition, variable cp and combustion chemistry are not yet coupled dynamically.
- T4 is solved from fixed isothermal wall UA, but compressor/turbine machine efficiencies, pressure drops, CO₂ mass flow, compressor inlet and recuperator geometry performance are fixed assumptions. A physical pump/fan/shaft/valve is not modelled.
- No CO₂ pressure/mass inventories, `rho,u` real-fluid inversion, inertia, valve flow, actuator or controller; G4 full-inventory and G5 PI/MPC remain OPEN.
- The wall state is lumped/isothermal with a **chosen** capacity and two independently chosen UAs. There is no thermal metal/casing measurement or facility geometry in the code.
- Admissible operating regions are the solver's declared temperature, stack and pinch feasibility bounds; this is **not** a validated plant operating envelope.

**WP3 next:** physically declared waste-gas source bypass or controlled hot-side thermal input with explicit mixing/source enthalpy, actuator bounds, rate limits and anti-windup PI, compared with the same open-loop load profiles. A larger **full CO₂ mass/inventory transient** requires independent density/internal-energy EOS inversions, closed flow/pressure and rotating-shaft dynamics.

WP2b should be promoted to a v1.0 research-software feature only after its completed tests, full CI and a reviewer audit of the physical boundaries. PR #22 remains its dependency; PR #19 Kim interpretation remains unrelated and scientifically open.
