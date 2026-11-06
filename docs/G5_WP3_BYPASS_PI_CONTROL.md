# G5/WP3 — finite-source bypass and wall-temperature PI control

**Status: code in stacked draft PR #24; validation and review are release gates, not assumed completed. Date: 6 November 2026.**

## 1. Model scope and scientific classification

WP3 extends the [WP2b dynamic wall and quasi-steady Brayton research model](G4_WP2B_FINITE_SOURCE_WALL_CYCLE.md). The only physical state integrated over time is **lumped solid-wall temperature**. Gas-flow temperature/mass flow are prescribed piecewise constant; the Brayton block remains an algebraic, six-state real-/fixture-property calculation at each RK4 stage.

**What is new:** a physically traced *source-side bypass mass split*, an actuator on the diverted source gas **fraction**, a causal sampled PI loop regulating wall temperature, explicit mechanical limits (maximum bypass, slew rate and minimum active exchanger mass flow), and numerical full-system source enthalpy closure. PI is only claimed as a demonstrator with assumed gains, not an experimentally identified controller.

**What is not here:** CO₂ mass/pressure inventories, turbine or compressor maps, speed/shaft inertia, compressor inlet controls, recuperator/wall distributed capacitance, a hydraulic valve `Cv` curve, source-gas pressure loss, sensor noise/deadtime, PLC safety interlocks, full HZDR/CARBOSOLA plant representation, experimentally measured transient load profiles or identified cost/performance coefficients. These limitations remain open research requirements.

## 2. Conservation and bypass geometry

Single upstream hot stream at `T_g,in`, `m_g`, and constant `cp_g`. The bypass fraction `0 <= b < 1` diverts **mass**, not heat directly:

```text
                      +-- (b * m_g) untouched at T_g,in ---------+
Source m_g, T_g,in ---+                                             +-- Mixed exhaust
                      +-- ((1-b) * m_g) -> UA_g,w -> T_g,out,active--+
                                                   |
                                             Q_g,w to C_wall
                                                   |
                                            UA_wall,CO2 -> Brayton heater 3→4
```

```text
m_active  = (1-b)*m_total
m_bypass  = b*m_total
m_active + m_bypass = m_total

C_active = m_active*cp_g
epsilon_active = 1-exp(-UA_g,w/C_active)
Q_g,w = C_active*(T_g,in-T_wall)*epsilon_active
T_g,out,active = T_g,in - Q_g,w/C_active

T_g,out,mixed = (1-b)*T_g,out,active + b*T_g,in

m_total*cp_g*(T_g,in-T_g,out,mixed) = Q_g,w
```

For each interval, the **mean mixed exhaust temperature** is calculated using time-integrated `E_g,w`:

```text
T_mix,mean = T_g,in - E_g,w/(m_total*cp_g*Delta_t)
E_g,total = m_total*cp_g*Delta_t*(T_g,in-T_mix,mean) = E_g,w

E_g,total = Delta_U_wall + E_net,shaft + E_cooler
```

This first-law identity is **checked numerically** with the full WP2b RK4 integration. The bypass branch carries enthalpy but does not heat the wall or Brayton cycle; no duplicate gas-to-CO₂ heater is added.

**Assumptions:** same idealised constant `cp_g` for both branches; zero thermal loss from bypass pipe and downstream mixing junction; fixed gas-wall UA even when active flow varies (an **assumption**, not a correlated flow-dependent UA law); wall heater UA separately specified; no bypass pressure-control authority or additional pump load. The model does not represent the bypass as a physical gas mixing at the wall or a direct heat source.

## 3. Actuator, control signal and anti-windup

`SourceBypass` sets:
- `max_fraction` (strictly less than 1 so the wall exchanger always sees positive mass flow);
- `max_rate_fraction_s` for stepwise actuator movement;
- `minimum_active_mass_flow_kg_s` as a fail-closed operating constraint.

The command is updated **only at the beginning of each source-load interval** and held for the entire integration interval. At sampling step `k`, with `e_k = T_wall,k - T_wall,setpoint`:

```text
u_raw,k = b_bias + Kp*e_k + I_k
u_req,k = clamp(u_raw,k, 0, b_max)
u_actual,k = clamp(u_req,k,
                    max(0, u_actual,k-1-r_max*dt),
                    min(b_max, u_actual,k-1+r_max*dt))

I_k+1 = clamp( I_k + Ki*e_k*dt
               + K_aw*dt*(u_actual,k-u_raw,k),
               -I_limit, I_limit )
```

A **positive wall-temperature error increases bypass**, reducing heating: the sign reverses the normal positive heat-input gain. The tracking term is back-calculation from the **actual rate- and position-limited** output, not only the clipped requested command; hence integral state cannot wind up indefinitely while valve motion is blocked. The code rejects `K_aw*dt > 1` and clamps `I` to the declared finite limit.

The model assumes a perfect wall-temperature measurement at each sample and zero-order-held mass fraction between samples. No unreported measurement filter, predictor, anticipative load knowledge or industrial commissioning tuning has been inserted.

**Fixed open-loop baseline:** set the exact same source loads, initial wall temperature, initial bypass fraction, source/cycle parameters, interval durations and target temperature, but no controller. The commanded bypass fraction remains fixed, and the integral is zero. **Control has no free access to future disturbance values.**

## 4. Required evidence and metrics

Run:

```bash
python -m pip install -e '.[test]'
python -m pytest -q tests/test_control_whr.py
python examples/waste_heat_bypass_pi_comparison.py
```

Optional real-CO₂ branch (after `pip install -e '.[test,co2]' 'CoolProp==8.0.0'`):

```bash
python -m pytest -q tests/test_control_whr_co2.py
```

The synthetic experiment writes:
- `evidence/generated/v1_wp3/control_trace.csv` (exactly matched source/time profiles; actuator, bypassed/active mass, wall temperatures, mixed exhaust, turbine inlet and stage energy ledger);
- `evidence/generated/v1_wp3/control_summary.json` (assumed hardware and PI gains, performance summaries, limitations and energy residuals).

Metrics:
- **Endpoint sample RMSE**: duration-weighted mean of squared *end-of-interval* setpoint deviations (not a continuous-time integral of squared error).
- **Trapezoidal IAE estimate**: piecewise trapezoid of absolute wall temperature error at interval boundaries (not an exact time integral).
- Net **shaft** energy: time-integrated algebraic turbine-minus-compressor power, not generator electrical output.
- Source/wall/cycle conservation: integrated gas enthalpy extraction = wall energy stored + shaft energy + cooler rejection.
- Hard actuator constraints: position limits, finite slew-rate, positive active gas flow and allowed branch outlet/stack thermal approaches.
- Independent gas mixing relation checked both instantaneously and over the integrated step.
- Zero anticipative gain: changing later load inputs must not change earlier actuator outputs.

Any lower PI RMSE on the chosen synthetic 850→880 K profile is **scenario-specific**; it does not establish universally better control, plant stability/robustness, adequate sampling for a real installation, or process safety.

## 5. Validation gates and next architecture

The WP3 API is experimental until CI has passed both Python versions and the full reference data/real-fluid suite on a single SHA, the new source-mixing/antiwindup tests and the actual wheel/sdist smoke job pass, and an independent reviewer checks physical assumptions. The existing WP2a/WP2b code and Kim H1d source ambiguity must not be relabelled as newly validated.

**Future WP3b**: true transient actuator dynamics and instrumentation uncertainty, plant-identified gains and constraints, controlled perturbation experiments, source-flow-dependent transfer coefficients, coolant-side inventory, watchdog/safety logic and a fully specified PI tuning/robustness process.

**Future full G4**: CO₂ mass, internal energy, pressure and flow inventories with robust `rho,u -> p,T` EOS inversion, turbine/compressor speed/flow maps and heat-exchanger wall/fluid dynamics. Only after those data and equations exist can broad real-plant dynamic/control claims be considered.
