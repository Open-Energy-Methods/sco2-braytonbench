# G5/WP3 — executed PI/bypass comparison (2026-11-06)

**Evidence type:** synthetic ideal-gas numerical study; not measured CO₂, HZDR or CARBOSOLA. Physical model, controller and units: [WP3 specification](G5_WP3_BYPASS_PI_CONTROL.md). This page reports actual results of [the executable example](../examples/waste_heat_bypass_pi_comparison.py) rather than forecasts.

## 1. Experiment configuration

Exactly matched 18 samples of 5 s each (90 s total); prescribed source **850 K** for samples 1–9 and **880 K** for samples 10–18, source gas 30 kg/s. Both scenarios start with wall **700 K**, wall target **700 K** and bypass fraction **0.15**. The only change is fixed bypass versus feedback PI.

The **artificial ideal-gas fixture** has CO₂-*unrepresentative* `cp=1,000 J/(kg K)` and `R=200 J/(kg K)`, `P1=8 MPa`, `P4=24 MPa`, `T1=310 K`, 10 kg/s nominal working-fluid flow, compressor/turbine efficiencies 0.89/0.90 and **zero installed recuperator UA**. Source gas has constant `cp=1,100 J/(kg K)`. Assumed, unmeasured wall thermal capacity **2 MJ/K**, gas-to-wall UA **40 kW/K** and wall-to-working-fluid UA **25 kW/K**.

The actuator diverts an explicit **fraction of hot-gas mass**, with maximum bypass 0.85, maximum slew 0.025 fraction/s and minimum active gas flow 1 kg/s. The controller is a reverse-gain wall PI: `e=Twall-700 K`, `Kp=0.040 fraction/K`, `Ki=0.0025 fraction/(K s)`, bias 0.15, tracking anti-windup gain 0.20/s and integral limit ±1.0. Gains are illustrative, **not experimentally tuned**.

## 2. Executed numerical results

Initial [GitHub Actions WP3 execution, run 42245315129](https://github.com/Open-Energy-Methods/sco2-braytonbench/actions/runs/42245315129) produced **23 passing dedicated WP3 tests** and both machine-readable trial traces.

| Quantity | Fixed bypass | Wall-temperature PI | PI impact |
|---|---:|---:|---|
| Duration | 90 s | 90 s | Identical |
| Duration-weighted **end-sample RMSE** | **11.4627966 K** | **1.7170154 K** | **85.02% reduction** |
| Endpoint-trapezoidal approximate **integrated absolute error** | **812.851959 K·s** | **140.641923 K·s** | **82.70% reduction** |
| Thermodynamic **net shaft energy** | **29.6939315 MJ** | **28.6139387 MJ** | **1.079993 MJ lower (3.64%)** |
| Combined gas/wall/cycle first-law residual | **+8.20×10⁻⁸ J** | **−1.45×10⁻⁷ J** | Both negligible against MJ energy totals |

The RMSE evaluates only interval-end samples; approximate IAE uses the trapezoid of absolute wall-temperature deviations at adjacent sample times. Shaft energy integrates **algebraic turbine minus compressor work**, not metered electrical output. The tiny closure residuals demonstrate **model energy bookkeeping**, not experimental accuracy or identified-UA uncertainty.

The lower PI tracking error is achieved partly by **diverting heat from the recovery path**. A 3.64% lower net shaft-energy output is a meaningful cost of this particular control strategy. This is **not universal PI superiority**, a lifetime-performance assessment or an energy-system economic optimum. The result applies only to these synthetic parameters and disturbance values.

## 3. Independently executed verification

The analytical/fixture tests check source mass conservation; mixing of bypassed hot stream with cooled active stream downstream; instantaneous and interval-integrated `m cp ΔT` source heat extraction; gas→wall→CO₂ heater→cooler/shaft conservation with **no double-counted heater**; effect of changing bypass on wall heat input; causal sampling without future source information; saturations, slew, minimum active flow and achieved-valve tracking anti-windup; identical open-/closed-loop load profile; explicit invalid-data rejection. WP2b independently checks the underlying thermal ODE and analytical constant-property heater solution.

**Reproduction commands:**

```bash
python -m pip install -e '.[test]'
python -m pytest -q tests/test_control_whr.py
python examples/waste_heat_bypass_pi_comparison.py
```

The script writes `evidence/generated/v1_wp3/control_trace.csv` and `control_summary.json`; GitHub Actions uploads both. A separate `test_control_whr_co2.py` tests one synthetic real-CoolProp 8.0.0 CO₂ thermo-property/energy-path smoke. It is **not** an experimentally validated transient control result. Do not claim final PR CI green until the matching head run completes.

## 4. Remaining scientific limitations and fair description

No measured bypass valve `Cv`, gas-flow-dependent UA, fan/pump losses, CO₂ mass/pressure inventory dynamics, turbine/compressor rotational dynamics, real wall thermal mass, sensor dead time/noise, physical emergency protection or HZDR facility measurements are modelled. WP3 commands an idealised **diverted mass fraction held over each source interval**; it does not represent a full valve/hydraulic control system.

A defensible statement: **A conservation-audited finite-source/lumped-thermal-wall numerical demonstrator can compare a bounded PI bypass strategy against an exactly matched fixed-bypass strategy, showing an explicit control-accuracy versus heat-recovery trade-off on one hypothetical scenario.** Full G4/G5 plant model validation and industrial controller deployment remain open.
