# TES-v0.8 — executed operating-window and sensitivity results

**Date:** 7 November 2026  
**Evidence class:** Original **synthetic** packed-bed calculation, 1-D constant-property two-temperature sensible TES  
**Engineering status:** Completed numerical investigation; integration/release dependent on exact-final-head CI. Not experimentally validated.  
**Execution evidence:** [TES-v0.8 fully completed Actions run #42353380198](https://github.com/Open-Energy-Methods/sco2-braytonbench/actions/runs/42353380198) at source commit ed97e1138a6c7520d40dd2cc40143e7f7e11adf2 (22 passing dedicated tests; full OAT/factorial/numerical artifact and SHA256 verification). Subsequent source edits require a new exact-head evidence check.

This report follows the predeclared numerical and parameter design in [10_OPERATING_WINDOW_SENSITIVITY.md](10_OPERATING_WINDOW_SENSITIVITY.md). No external plant measurements or experimental TES data were used. The original TES-v0.6/v0.7 train/validation/test/OOD partitions and their documented negative OOD result were not modified.

## 1. Main result and physically bounded interpretation

The N=96 nominal synthetic operating case (1 m bed, 0.1 m² area, 50% porosity, 500 W/(m³ K) Hv, 0.05 kg/s flow, 350→650 K charge, 0.8 charge/0.1 hold/1.0 discharge thermal turnovers) gives:

| Quantity | Calculated nominal result | Interpretation |
|---|---:|---|
| Recovered sensible heat | 2.120487 MJ | **All** heat withdrawn over prescribed reverse discharge |
| Discharge heat delivered at or above 500 K | 6.570557 kJ | Temperature-qualified enthalpy, separate from conservation |
| Qualified share of recovered heat | 0.310% | Not plant electricity efficiency |
| After-charge solid SOC | 0.402502 | Unclipped, solid-only SOC |
| After-charge solid+fluid reversible thermal exergy | ~1.280 MJ | Availability relative to 300 K constant-cp ambient; not exergy gain or usable work |
| Relative first-law residual | 4.83×10⁻¹² | Numerical energy closure, **not** physical validation |
| 10–90% solid thermocline width | Undefined | Insufficient simultaneous full-crossing profile; do not report zero width |
| Gross energy round-trip efficiency | **Null** | Final solid+fluid cell state does **not** return within the declared 0.5 K tolerance |

This negative temperature-grade result is material: the synthetic bed can release substantial low-grade heat while providing very little heat at 500 K. The correct storage-service question depends on the temperature threshold, not only on the gross energy recovered.

## 2. Numerical refinement and trustworthiness

The original 24-macro-sample outlet reconstruction severely overstated threshold-qualified output. TES-v0.8 now records the **actual conservative solver's SSPRK3 internal substep outlet trace**; enabling this optional trace leaves the legacy solver temperatures, boundary ledger and first-law residual unchanged.

| Grid cells | Recovered MJ | Qualified heat kJ | Full-discharge observation quadrature bias J |
|---:|---:|---:|---:|
| 6 | 1.96917 | 0.175 | +18.973 |
| 12 | 2.04763 | 3.469 | +6.495 |
| 24 | 2.08876 | 5.206 | +1.893 |
| 48 | 2.10983 | 6.109 | +0.512 |
| 96 | 2.12049 | 6.571 | +0.133 |
| 192 | 2.12585 | 6.804 | +0.034 |

The 96→192 relative difference is ~0.253% in total recovered heat and ~3.42% in temperature-qualified heat (referenced to N=192). **N=96 is retained for the parameter ensemble because N=12 materially underresolves this threshold observable.** N=192 is a comparison grid, not a proved continuum solution.

At N=96, the independently varied **substep trace decimation stride** 4/2/1 gives useful heat of 6.577/6.571/6.571 kJ; maximum SSPRK3 timestep factors 1/0.5/0.25 give 6.571/6.570/6.570 kJ. Timestep and grade-observation error are much smaller than the N=96→192 spatial discrepancy for the nominal scenario. This does **not** prove that all OAT corners have the same spatial convergence.

Numerical closure and spatial convergence are different gates. In particular, the first law can close to machine precision on an inaccurate coarse grid.

## 3. One-at-a-time physical sensitivity (N=96)

All OAT cases use the same prescribed **thermal-turnover counts**, not the same duration in physical seconds. Input changes can therefore alter both instantaneous duty and total runtime; these comparisons must not be described as fixed-clock-time partial derivatives.

| Physical parameter | Low level recovered MJ | Low level qualified kJ | High level recovered MJ | High level qualified kJ |
|---|---:|---:|---:|---:|
| Flow 0.025→0.100 kg/s | 3.640 | 301.9 | 0.974 | 0 |
| Porosity 0.35→0.65 | 2.726 | 4.36 | 1.515 | 9.40 |
| Length 0.75→1.25 m | 1.185 | 0 | 3.235 | 21.88 |
| Area 0.075→0.125 m² | 1.185 | 0 | 3.235 | 21.88 |
| Interphase Hv 250→1000 W/(m³ K) | 0.974 | 0 | 3.640 | 301.9 |
| Charge duration 0.6→1.0 turnovers | 1.691 | 0 | 2.497 | 22.05 |
| Hold duration 0→0.2 turnovers | 2.131 | 46.75 | 2.120 | 6.57 |
| Discharge duration 0.8→1.2 turnovers | 1.801 | 6.57 | 2.400 | 6.57 |
| Qualified outlet threshold 450→700 K | 2.120 | 31.87 | 2.120 | 0 |

The 500 K reference grade produces 6.57 kJ; raising the grade to 550 K makes service **zero** in the nominal synthetic case (and the absent downcrossing is null rather than time=0). The energy ledger remains unchanged when only the service threshold is changed.

**Identifiability caution.** Changing length and area in the same proportion gives identical outputs when both produce the same bed volume in this particular adiabatic 1-D closure, without pressure-drop, wall-area or axial-conduction distinctions. Likewise, changing flow and Hv in compensating proportions yields equivalent dimensionless transport/time behavior for some OAT settings. This is a **model limitation and parameter confounding**, not a physical statement that real length, cross-section, flow and heat transfer are interchangeable.

The pronounced hold-time effect on a narrowly short-lived high-grade outlet window also emphasizes that temperature-grade availability is sensitive to initial transient thermal equilibration.

## 4. Fully crossed flow × porosity × Hv study

To move beyond OAT, all **eight corners** of the high/low flow (0.025/0.10 kg/s), porosity (0.35/0.65) and Hv (250/1000 W/(m³ K)) design were executed with N=96. For each response, seven orthogonal signed high-minus-low contrasts were reconstructed from the eight independent runs. A contrast is a finite-window average over these artificial corners, not a derivative, variance or uncertainty interval.

| Contrast | Signed recovered-heat effect MJ | Signed 500 K qualified-heat effect kJ |
|---|---:|---:|
| Flow | −2.373 | −1,501.7 |
| Porosity | −1.399 | −428.7 |
| Hv | +2.373 | +1,501.7 |
| Flow × porosity | +0.702 | +431.2 |
| Flow × Hv | −0.619 | −1,494.9 |
| Porosity × Hv | −0.702 | −431.2 |
| Flow × porosity × Hv | +0.187 | +433.7 |

The **large flow × Hv interaction** is evidence against relying on additive single-factor extrapolation for this particular temperature-grade observable. Temperature-grade qualification is a thresholded output; effect sizes can change sharply when a corner has zero service. It is inappropriate to interpret the contrast magnitude as a calibration uncertainty.

## 5. Integrity and provenance

The reproducibility evidence contains four CSV files plus one JSON manifest. Reported SHA256 values from the executed pre-report source run:

| Evidence table | SHA256 |
|---|---|
| Physical OAT | 196dfa7696c14f5b8ce84e4a5f47bc3257bcc39558d731c3ffed9c2a9f10e0b0 |
| Numerical refinement | c137c2bfdde800af3bfdd89610336cdb7bc2ac2e17dd936009a5939d14bd3818 |
| Factorial cases | 4c6e216d81e833e6d75eda6e8dc7a13350f688583d406899ca34907ba62c1e76 |
| Factorial effects | d235dd192daae865f63c7c6250499be067ade1a7206bf8af5b78eb34106daac5 |

The integrated CI tests also verify threshold integration identities, preserved physical conservation under temperature qualification, absent threshold and incomplete-cycle null semantics, explicitly completed state return, recorded substep trace invariance, design corner orthogonality and artifact tamper rejection. All tabulated units are SI-based, with MJ/kJ presentation conversions.

## 6. Uncertainty categories and claims not established

- **Numerical:** Reported via N, SSPRK3 timestep and independently decimated substep trace. No unproven universal grid convergence claim; the 96→192 difference is observable-specific.
- **Parametric:** Reported via OAT and full 2³ factorial contrasts within the declared synthetic bounds. No parameter probability distribution or confidence interval is supplied.
- **Model form:** **Not quantified.** No independent alternative porous-bed heat-transfer closure, temperature-dependent fluid properties, pressure loss, heat leakage, variable interphase coefficients, physical maldistribution or physical benchmark is available in this report.
- **Experimental/industrial:** **Absent.** No CIC energiGUNE, HZDR, CARBOSOLA or other facility data or validation are claimed.

The learned TES-v0.7 **input/output emulator is not used as the energy-conserving storage state**. Its previously documented negative out-of-domain performance relative to two-cell physics remains unchanged. This study does not solve full dynamic sCO₂ pressure/mass inventory, closed return piping, pumping energy, PCM mechanics or facility control.

**Research conclusion:** TES-v0.8 now provides a reproducible quantitative operating-window framework with a completed nominal mesh/time/observation comparison, one-factor and factorial sensitivity, and strict energy/qualification separation. Scientific conclusions remain bounded by the model form and the particular synthetic turnover schedule. These results support a properly scoped **research baseline**, not a verified industrial TES design.

**Release decision:** TES-v0.9 distribution/replay audit, independent qualified scientific review, and source-rights governance remain separately open. The parent package is **0.5.0a0**; no v1.0 tag, DOI or experimental-validation claim is implied.
