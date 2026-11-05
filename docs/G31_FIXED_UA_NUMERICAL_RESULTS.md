# G3.1: fixed installed-heater UA coupled steady-state verification

**Execution date:** 2026-11-05  
**Model state:** exploratory, physically coupled steady-state numerical prototype.  
**CoolProp:** 8.0.0, `HEOS::CO2`, Python 3.11.  
**CI:** [GitHub Actions 42002609837](https://github.com/Open-Energy-Methods/sco2-braytonbench/actions/runs/42002609837), **all five jobs passed**.  
**Machine-readable source/cycle/UA report:** [g31-installed-ua-coupling artifact](https://github.com/Open-Energy-Methods/sco2-braytonbench/actions/runs/42002609837/artifacts/13403581114).

## Modelled boundary value problem

For fixed installed gas-to-CO₂ heater `UA`, gas inlet state,
gas mass flow, CO₂ mass flow, compressor inlet state, cycle pressures,
recuperator installed `UA`, and fixed compressor/turbine efficiencies,
the solver determines turbine-inlet `T4`, exhaust leaving `Tgas,out`,
heater heat duty and recuperator duty together. It searches for
`UA_required(T4) = UA_installed`, enforcing gas and working-fluid
enthalpy balances with counterflow segment approaches.

This is **not** the original G3 sizing inequality
`UA_required <= UA_max`. No simulated bypass, exchanger area reduction
or arbitrary modulation is introduced.

## Independently selected synthetic design

The nominal point `T4=650 K`, exhaust inlet `800 K`, CO₂ mass flow
`20 kg/s`, exhaust mass flow `100 kg/s`, `cp_gas=1100 J/(kg K)`,
working-fluid pressure `8.5/24 MPa`, `T1=310 K`, recuperator
`UA=200 kW/K`, and fixed pressure losses were chosen for the
engineering software experiment. Their turbine/compressor isentropic
efficiencies are 0.90/0.89. The initial **installed gas-heater UA was
sized from that nominal steady-state candidate**:

`UA_heater,installed = 21,783.3278627 W/K.`

That is not a published source-paper installed HX, CARBOSOLA component
or calibrated industrial measurement. In subsequent source-temperature
perturbations, it is held unchanged.

## Numerical off-design result

| Quantity | Gas inlet 800 K | Gas inlet 810 K |
|---|---:|---:|
| Fixed installed heater UA (kW/K) | 21.783328 | 21.783328 |
| **Solved turbine-inlet T4 (K)** | **649.989014** | **658.953857** |
| Gas leaving heater/stack (K) | 758.003237 | 767.638266 |
| Net shaft power (MW) | 1.4238615 | 1.4599094 |
| Cycle thermal efficiency (%) | 30.8218883 | 31.3299343 |
| Calculated UA (kW/K) | 21.782025 | 21.782885 |
| Absolute UA residual (W/K) | −1.303 | −0.443 |
| Relative UA error (%) | 0.0059802 | 0.0020320 |
| Root function evaluations | 18 | 18 |
| Bisection iterations | 9 | 9 |

`T4` rises **8.964844 K** when the source inlet rises 10 K,
while installed UA and CO₂ compressor inlet properties are held fixed.
Net shaft power increases around **36.05 kW**. No thermal inventory or
time axis has been modelled, so this is **two independently solved
steady states**, not a transient time response or controller result.

The root meets `|UA_required-UA_installed|/UA_installed <= 1e-4`
and a final T4 bracket width `<=0.03 K`. The tests also verify both
gas-side and CO₂ first-law balances, a positive recuperator/heater
temperature approach, the stack-temperature floor and a
constant-cp source-exergy upper bound.

## Independent analytical verification

`tests/test_fixed_ua_analytic.py` checks coupled heater outlet
temperature against **the independent textbook counterflow
effectiveness–NTU expression** for several installed UA values,
using a constant-cp artificial fluid and zero recuperator UA.
The compressor is calculated with a separate isentropic ideal-gas
relation. This reduces the full coupled problem to a closed-form
equation and checks that the root solver recovers the exact answer
within tolerance.

The test suite further covers source-temperature sensitivity,
non-bracketing cases, input errors, heater approach and cooling
limits, and conservation of legacy G3 sizing-cap behavior.
Analytical textbook equations are not experimental real-CO₂ data.

## Verification execution

- Fixture-only Python 3.11 job: **151 passed, 7 optional modules skipped**.
- Fixture-only Python 3.12 job: **151 passed, 7 optional modules skipped**.
- Separate CoolProp density/reference/source EOS job: successful.
- Existing G3 real-fluid WHR design screen: successful.
- Dedicated G3.1 CoolProp tests: **3 passed**, followed by successful
  nominal and off-design JSON diagnostic.
- All **five** jobs in [Actions run 42002609837](https://github.com/Open-Energy-Methods/sco2-braytonbench/actions/runs/42002609837) passed.

## Known limitations

1. Heater UA is held constant, but actual U may depend on mass flow,
   fluid properties, surface material, geometry, fouling, and conduction;
   the model does **not** predict those effects.
2. The fluid remains a reduced six-state constant-machine-efficiency
   cycle with fixed absolute pressure losses and a prescribed compressor
   inlet state/temperature.
3. Gas `cp` is constant and composition is unmodelled.
4. The cooler is not yet coupled to a fixed installed sink UA, water/air
   inlet and fan/pump parasitic duties.
5. Numerical bracketing searches only the declared turbine-temperature
   interval, with no proof of global uniqueness or convergence over
   all operating regimes.
6. The gas energy/exergy screen neglects source pressure, chemical and
   kinetic exergy, as well as auxiliary electrical consumption.
7. No source-paper MK2014 genetic algorithm/RRC optimum is reproduced.
   No CARBOSOLA/HZDR measurements, plant dynamics or PI/MPC controller
   is present.

**Decision:** fixed-heater-UA software coupling and tested synthetic
real-fluid operating points **pass this narrow numerical prototype
verification**. G3.1 as a fully calibrated **industrial off-design
plant gate remains OPEN**, pending temperature-dependent source gas
properties, heat-transfer correlations, flow-dependent equipment
performance, cooling coupling and extended robustness evaluation.
