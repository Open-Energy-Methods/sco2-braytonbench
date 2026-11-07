# TES performance and operating-window metrics — first mathematical layer

**Engineering scope:** synthetic, constant-property 1-D two-temperature sensible packed bed. This is a **metrics foundation** for planned TES-v0.8, not completion of its entire sensitivity and operating-window study.

## Solid and fluid capacity cannot be conflated

For prescribed design cold and hot reference temperatures, `T_hot>T_cold>0`:

\[
E_{s,capacity}=C_{s,total}(T_{hot}-T_{cold}),
\quad E_{f,capacity}=C_{f,total}(T_{hot}-T_{cold}).
\]

The current actual solid or fluid energy, relative to the *same declared* cold state, is \(\sum C(T_i-T_{cold})\), without forcing a clip into [0, capacity]. Solid SOC is not a measured deliverable temperature or a round-trip efficiency.

## Reversible thermal exergy

With an explicitly selected ambient `T_0>0 K`, and constant cp, a thermal cell's reversible availability relative to that ambient is

\[
B=C\left[(T-T_0)-T_0\ln(T/T_0)\right].
\]

The model totals that separately for fluid and solid; it is nonnegative mathematically and zero at ambient equilibrium. The static capacity expression is **not** an independent physical work-output measurement.

For a flow stream with constant cp, the inlet-minus-outlet **sensible exergy flux** is

\[
\Delta\dot B=|\dot m|c_p\left[(T_{in}-T_{out})-T_0\ln(T_{in}/T_{out})\right].
\]

Pressure work, chemical exergy, viscosity, actual pumping, thermal deformation and plant irreversibility are excluded. Do not label this expression a complete industrial exergy balance without those terms.

## Thermocline thickness

From *solid* cell temperatures, normalize \(\theta_i=(T_{s,i}-T_{cold})/(T_{hot}-T_{cold})\). Check that the profile is monotone in the actual physical cell coordinate. Interpolate x where theta crosses 0.1 and 0.9, and report \(|x_{0.9}-x_{0.1}|\).

If the curve is nonmonotone or the full pair of crossings is not present, the width is returned as `None`. A partially charged bed with no 90% region does **not** have an invented “zero-width” thermocline. A uniform temperature state similarly has no proper 10/90 front.

## Verification

~~~bash
python -m pytest -q tests/test_tes_metrics.py
~~~

Independent mathematical fixtures include uniform 600 K bed versus 300 K ambient, zero exergy when at ambient, a five-cell linear profile with exact 0.64 m interpolated 10–90% thickness, failed and nonmonotone fronts, and the logarithmic stream-exergy identity.

The remaining TES-v0.8 **simulation ensemble**, including flow/porosity/Hv/N/time sensitivity and useful-outlet temperature-grade analysis, is not completed by this module. No measured efficiency, material-calibrated thermal capacity or liquid-piston work is claimed.
