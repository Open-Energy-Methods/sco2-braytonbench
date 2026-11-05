# G3.2 — finite cooling medium and two installed-UA steady-state roots

**Scope:** research-grade *numerical prototype* of a recuperated six-state
sCO₂ Brayton circuit with finite industrial exhaust-gas source and coolant.
This is separate from HTHP-ControlBench. It is NOT a CARBOSOLA or MK2014
reconstruction and is NOT a dynamic/PI/MPC model.

## Model boundaries

Previously the compressor inlet T1 was prescribed, and the G3.1
fixed-installed-UA heater solved T4 for a given gas supply. With a
physical cooler, the compressor inlet T1 must be determined from the
actual cooling medium and installed **cooler UA** instead.

We now solve the **nested steady-state boundary-value problem**:

```text
F_heater(T4 | T1) = UA_heater,required(T4,T1) - UA_heater,installed = 0
F_cooler(T1 | solved T4) =
    UA_cooler,required(T1,T4) - UA_cooler,installed = 0

Q_h = m_CO2(h4-h3) = m_hot * [H_hot(Tin)-H_hot(Tout)]
Q_c = m_CO2(h6-h1) = m_cool * [H_cool(Tout)-H_cool(Tin)]
Q_h - Q_c - (Wt-Wc) ≈ 0
```

The recuperator state h3 and hot outlet h6 are recalculated at
each inner/outer solve, using its fixed UA. The CO₂ cooler pressure
changes linearly from cooler inlet P6 to compressor inlet P1 along
the equal-enthalpy-duty discretization. This is a simplified prescribed
pressure profile, not a geometry-calibrated friction law.

The coolant enters at the **CO₂ cooler cold end** next to state 1,
and leaves at the **CO₂ cooler hot end** next to state 6. The gas
source is counterflow to the CO₂ heater. Both heat-exchanger profiles
enforce a local minimum temperature approach and estimate UA using
segment-wise LMTD. Each stream has a measured-temperature outlet
computed from its sensible enthalpy balance. The cooler also checks
the combined CO₂ and coolant entropy generation and an imposed
coolant outlet-temperature maximum.

**Bisection:** the solver scans an explicitly declared T1 interval,
solves the fixed-installed-UA heater at each valid T1 and bisects
an identified sign-changing cooler-UA bracket. It rejects
non-bracketing, non-unique detected roots, infeasible midpoint
states and nonconvergence. This is **not a global proof of
root uniqueness** and no disconnected feasible-domain search is
claimed.

## Temperature-dependent heat capacity — explicit model, not a fluid EOS

Both source gas and coolant support:

```text
cp(T) = cp_ref + b (T - T_ref)
H(T2) - H(T1) = (T2-T1) [cp(T1)+cp(T2)] / 2
S(T2)-S(T1) =
  (cp_ref-b T_ref) ln(T2/T1) + b(T2-T1)
```

The `LinearCp` model has an analytic, monotonic enthalpy inverse
over the accepted strictly positive-cp range. The gas-side heater
now calculates source enthalpy, stack temperature and exergy using
those expressions; the prior **constant cp** case remains the
b=0 default and retains legacy tests.

**No measured mixture composition, high-temperature cp correlation
or source-gas reference fluid parameters have been supplied.**
A trial slope is a declared sensitivity scenario only, not NIST or
REFPROP air-property equivalence. Sensible streams exclude evaporation
and two-phase cooling.

## Flow-dependent equipment-loss sensitivity

`FlowScaling` has an explicitly synthetic pressure-drop law
`ΔP(m)=ΔP_ref (m/m_ref)^n`, default exponent n=2, and optional
quadratic penalties to compressor/turbine isentropic efficiencies:

```text
eta_c(m) = eta_c,ref - a_c (m/m_ref - 1)^2
eta_t(m) = eta_t,ref - a_t (m/m_ref - 1)^2
```

It rejects flows outside its user-declared range, pressure
exponents outside 0–4, nonpositive quantities and efficiencies
outside physical bounds. It is an **engineering sensitivity
parameterization, not a turbine/compressor map**; no shaft speed
or Reynolds number correction, pressure-drop measurements, or
flow-dependent heat transfer coefficient is modelled.

The default current-model simulation retains fixed loss/efficiency
inputs. Flow scaling is opt-in and must be reported separately.
A flow-scaling demonstration shall not be presented as MK2014's
fractional pressure-loss treatment.

## Verification strategy

1. Independent analytical tests for **sensible enthalpy and entropy**,
   state inversion and constant-cp recovery.
2. An equal/unequal-capacity-flow counterflow cooler test against
   **closed-form epsilon-NTU**, with an artificial constant-cp
   working fluid.
3. Energy-balance closure, minimum approach, positive entropy
   generation, coolant outlet and flow-loss domain tests.
4. **Dual inverse** from a synthetically sized known feasible
   operating point: recover both T1 and T4 when heater and cooler
   installed UA are held fixed. First run the analytic fixture,
   then the dedicated CoolProp 8.0.0 real-CO₂ test.
5. At fixed UAs and flow rates, perturb cooling-medium inlet
   temperature and independently solve the new steady state;
   export JSON energy balances, UA residuals and root diagnostics.
6. Run Python 3.11 and 3.12 fixture matrices and a separate
   real-fluid CI job. Tests must pass before claiming verification.

## Remaining restrictions

- No actual cooling-water pressure/phase property model,
  pump/fan auxiliary work, system intake/outfall or cooler geometry.
- Fixed UA is held across operating points; U's dependence on
  flow/composition/temperature and exchanger fouling is absent.
- No plant mechanical/electrical speed-control law, measured compressor
  map, rotor inertia, pressure-dynamics or fluid inventory.
- Flow-dependent pressure losses are only a bounded assumption,
  independent of the fixed-UA exchange model.
- Near-critical CO₂ and HX segment refinement over full operational
  envelopes is not established by a two-point smoke test.
- No system transient response; source/coolant perturbation
  experiments are distinct steady-state solves.
- The 2014 paper's REFPROP/GA results, RRC topology and
  2% fractional pressure-drop convention have not been reproduced.
- No proprietary/experimental HZDR/CARBOSOLA information is used.

**G3.2 decision:** treat as exploratory until actual CI results
and their convergence evidence are inspected. The industrial
off-design validation gate remains OPEN even after a test suite
passes, because plant geometry and equipment maps are missing.
