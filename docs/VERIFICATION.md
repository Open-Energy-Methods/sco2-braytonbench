# Reproducibility and verification protocol

## Install and test

Python 3.10+ is required. Clone, then:

```bash
python -m pip install -e '.[test]'
python -m pytest -q
```

To run optional CO2 EOS smoke checks locally:

```bash
python -m pip install -e '.[test,co2]'
python -m pytest -q tests/test_coolprop_optional.py
```

The GitHub Actions workflow executes fixture tests on Python 3.11/3.12 and runs EOS smoke checks separately using optional CoolProp. The EOS smoke checks do not constitute integrated cycle validation.

## Physical checks

1. Pressure drops use absolute Pa; temperatures use K; enthalpy J/kg; powers W; HX UA W/K.
2. Compressor `h_out >= h_in`; turbine `h_out <= h_in`; both require efficiencies `0 < eta <= 1`.
3. Recuperator conserves enthalpy between both streams; a real-fluid internal minimum temperature approach is searched over 30 or more segments.
4. Gas-side heater checks stack gas cooling, counterflow pinch and positive `UA_required` for an imposed duty.
5. Complete cycle energy residual: `Q_heater - Q_cooler - (W_turbine - W_compressor) ≈ 0`.
6. No constant-cp analytic fixture value is used as a CO2 benchmark point.

## Limitations and next tests

- More independent real-fluid EOS points, derivatives, property-edge checks and uncertainty tests are required.
- Require grid/segment-convergence tests for real-fluid exchanger pinch and UA.
- No fixed-geometry off-design heat-exchanger correlation, turbomachinery map or fluid-inventory dynamic model yet.
- No measured experimental profiles or closed-loop PI/MPC results exist.
- Separate source-faithful paper state reconstruction from our reduced-cycle comparisons.

Source files are open for review; numerical outputs are *illustrative* until independently checked.
