# Prospective experimental validation protocol — sensible packed-bed TES and exploratory liquid-piston interface

**Document type:** proposed research protocol only, **not** an approved/commissioned experiment or a facility operating procedure. **No sensors, calibration certificates, data, authorised operators, equipment limits or ethical/safety approvals exist in this repository.** This plan is not specific to a CIC energiGUNE installation and may only be adapted after the actual facility has provided a P&ID, safe operating envelope and independently approved experimental plan.

**Current numerical truth model:** an adiabatic, constant-property, 1-D two-temperature packed-bed finite-volume solver with solid and fluid inventory. It has no pressure loss, axial conduction, wall leakage, variable properties, fluid bypass/maldistribution, detailed CFD, or material-identified Hv. The surrogate is an 8-cell synthetic input/output emulator, and its 64-run OOD performance is worse than coarse two-cell physical simulation. These limitations define the model-to-data tests rather than disappear with an instrument list.

## A. Research questions and evidence hierarchy

1. Can measured outlet temperature, interior axial fluid/solid temperature trends and charged/discharged energy be predicted **without altering the model form after reviewing held-out runs**?
2. Can interphase volumetric exchange Hv, heat leakage and the sensor-response time scale be independently identified from available signals? Can length/area and flow/Hv confounding, already observed synthetically, be separated by run design?
3. At prescribed temperature thresholds, what fraction of physically withdrawn heat qualifies as service? Keep temperature-qualified energy **separate** from the first-law ledger.
4. Does the CFD/expanded PDE/experimental hierarchy quantify errors the simple 1-D model cannot represent? A solved energy residual is numerical verification, **not** empirical accuracy.
5. For a future liquid-piston rig, are measured fluid pressure/volume/temperature pathways consistent with ideal-gas compressive work plus a *rate-, material- and history-dependent* intrusion–extrusion pressure relation? Do not assume constant capillary offsets can predict nanopores.

## B. Instrumentation proposals — not an installed sensor register

The versioned candidate instrument map is in ../../protocols/tes_prospective/measurement_channels.csv. Suggested concepts require facility approval:

- Inlet and outlet fast-response, shielded fluid temperature measurement **T-IN/T-OUT** with verified immersion and sensor thermal time constant; report temperature in K, time monotonic seconds.
- **10 axial paired interior points** at x/L = 0.05, 0.15, ..., 0.95, with optional fluid/solid separation at each station if the mechanical layout supports it. A single thermocouple touching the packing **does not** independently measure both fluid and solid; tag each sensor's material contact, radial position and sheath conduction bias. The minimum candidate matrix chooses ten total axial temperature channels, not 20 falsely independent phases.
- Mass-flow measurement M-FLOW (kg/s), including signed direction for reverse discharge; pressure upstream/downstream P-IN/P-OUT (Pa absolute) for scope/failure diagnostics and future friction calibration. Current base TES model predicts **no** pressure drop.
- Ambient T-AMBIENT and optionally outside-wall T-WALL to quantify previously omitted heat losses. Electrical heater power Q-ELEC is auxiliary cross-check only and requires its own efficiency/loss boundary.
- Hardware timestamps, DAQ channel gain/offset, units, serial number, traceable calibration ID/date, response time, saturation, missingness and instrument spatial coordinates **must** be captured before a run can be counted as validated data.
- For future piston experiments, independent displacement volume/force, fluid/gas absolute pressures, fluid/gas temperatures, loading direction, cycling rate and specimen mass/structure are necessary. High-pressure material experiments require institution-approved containment, pressure relief, interlocks, risk review and qualified operators. This document provides **no** facility setpoints or operational permission.

The 10 axial positions are *suggested sampling points*, not a measured geometry or fixed manufacturing prescription. Physical design, safe taps, pressure class, materials, DAQ limits and funding are unknown.

## C. Acquisition, calibration and synchronized uncertainty

**Proposed acquisition:** choose sampling frequency after a pilot estimate of the fastest response and actual sensor bandwidth; an initial **5 Hz candidate for slow thermal TES** may be considered, but must be rejected if transit/mixing/response dynamics are under-resolved. Source sampling, postfilter and each sensor time constant must be reported. Record UTC start and monotonic relative time; synchronize signal acquisition across temperature/flow/pressure channels, document missing intervals, and retain *raw* unfiltered signals separately from predeclared analysis transformations.

For every channel: perform independent traceable calibration across the relevant authorized range; record calibration uncertainty (k=1 vs k=2 unambiguously), drift/repeatability, thermal response, radiative/axial conduction bias and common-reference correlations. No default error bars or nominal commercial model accuracy are assumed without actual certificates.

Compute the fluid-boundary heat through measured mass and specific enthalpy:

E_boundary = ∫ mdot [h(Tin,pin) − h(Tout,pout)] dt.

For the repository's constant-cp comparison, the explicitly restricted approximation is ∫|mdot| cp (Tin−Tout)dt with the inlet/outlet correctly relabelled under reversal. For a physical fluid, use an independently documented suitable enthalpy/EOS and propagate its uncertainty. Heat leakage, wall energy and pumping power are separate, not silently zero.

Fluid+solid inventory: ΔU ≈ Σ_cells (mf,i cpf ΔTf,i + ms,i cps ΔTs,i). Actual sensor coverage and parameter uncertainty may make this inference unidentifiable: **do not** claim all interior solid energy is measured from ten fluid-probe readings. In a refined validation closure include Q_loss, wall capacitance and fluid inventories; maintain the sign convention ΔU = E_boundary − E_loss + other independently quantified transfer. For uncertain correlated observations, use covariance-based propagation u_y² ≈ J Σ Jᵀ rather than adding correlated calibration uncertainties as if they were independent. Report sample-correlation-adjusted integrals/blocked bootstrap or run-level uncertainty, not independent per-time-row standard errors.

## D. Proposed experimental matrix and anti-leakage design

The companion versioned proposal ../../protocols/tes_prospective/run_matrix.csv lists training and held-out **candidate**, not executed, run IDs. The experiment owner must refine the levels from *approved hardware limits*, not the illustrative 350/650 K simulation numbers.

- Commissioning/feasibility: no research score; characterize sensor response, timebase, saturation, safe flow-direction reversals and energy boundary.
- Training/calibration: low/nominal/high **permitted** flow and thermal-inlet patterns, with charge/hold/reverse stages; first partition complete runs by physical operating sequence and material configuration.
- Independent test: pre-register at least two distinct complete schedules with unobserved combinations; prevent their signals affecting fitted Hv, leakage and sensor response.
- OOD/range extension: only if facility-safe, separately pre-register a source-temperature/flow or material-family shift. The synthetic ROM's negative OOD result is a prior caution, NOT empirical evidence.
- Replicate runs at distinct dates and instrument recalibration intervals; use within-run repeated observations for transient curves but **run IDs are the statistical independence unit**.

Before data acquisition freeze the hydraulic/thermal topology and model boundary conventions, test selection, calibration parameter search/priors, filtering, outlier rules, error metrics and planned operating envelopes.

## E. Parameter identification, falsification and holdout tests

Calibration candidates: Hv, initial bed state, axial dispersion/wall leakage *only after an extended governing equation is separately derived*, thermal sensors' dynamic lag, flow meter scale, and material cp/rho if separately measured. Do not fit a missing-physics coefficient into the current 1-D model while still claiming the model is unchanged.

Weighted least squares (WLS) objective for training runs only:

J(theta) = Σ_train (y_measured−y_model)ᵀ Σ_y^(-1) (y_measured−y_model) + prior regularization.

The covariance must be estimated from actual instrument data; no invented weighting. Profile likelihood/parameter recovery, constrained sensitivity Jacobian singular values, leave-one-parameter-fixed perturbations and independent validation reveal weak identifiability. In this code's current synthetic OAT, area and length can be confounded through bed volume, and flow/Hv can be partly confounded; treat these as experimental design threats.

Report **held-out** T_out RMSE/MAE, p95 error, normalized error relative to certified sensor uncertainty, temperature arrival/front delay, axial profile discrepancy, cycle E_boundary and ΔU estimates with confidence intervals, threshold-qualified energy with its observation quadrature sensitivity, and repeated-run between-experiment variability. Define pass/fail tolerances from safety, measurement uncertainty and modelling purpose **before running the tests**. There is no legitimate universal 5 K/1% acceptance threshold before facility context.

Compare against: (a) constant outlet/persistence, (b) the independently discretized 1-D model, (c) a simple two-cell physically conservative baseline, (d) frozen synthetic ROM without retraining, and later (e) CFD if independent mesh/time-physics and calibration are provided. Negative/failed-root runs stay in the denominator; do not silently score only successful conditions.

## F. Minimum review and release of research measurements

- Named responsible experiment owner, P&ID, pressure/thermal/electrical hazard and operator approval — **UNMET**.
- Calibrated instrument register, actual certificate numbers and raw timestamp schema — **UNMET**.
- Signed experimental protocol including a held-out run manifest, uncertainty budget and analysis preregistration — **UNMET**.
- Data rights, participant/industrial access rules, instrument source permissions and long-term archiving plan — **UNMET**.
- Predeclared comparison calculations and independent numerical review — **UNMET**.

No experimental value, fitted material property or thermal/storage efficiency is claimed by this proposed protocol. The liquid-piston algebra demo is a *mathematically verifiable* preparatory study, not a wetting physics model. Historic Mantilla data rights (#27) and independent release review (#28) continue as separate open repo governance gates.
