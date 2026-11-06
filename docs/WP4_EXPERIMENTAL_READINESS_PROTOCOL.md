# WP4 — proposed sCO₂ experimental readiness and validation programme

**Version:** WP4 draft, 2026-11-06. **Status:** desk research and software verification only. **Facility:** CARBOSOLA/HZDR is a possible future host, **not** an approved or characterized installation in this repository. **No test has been performed or authorized.**

This prospective plan connects the existing [WP2b heat-storage/Brayton surrogate](G4_WP2B_FINITE_SOURCE_WALL_CYCLE.md) and [WP3 bypass PI](G5_WP3_BYPASS_PI_CONTROL.md) to a realistic experiment design. It must **not** be presented as a commissioned CARBOSOLA test procedure.

## 1. Evidence boundaries and source chronology

- [RODARE CARBOSOLA community](https://rodare.hzdr.de/communities/carbosola/) publicly describes an HZDR facility with *possible* operating conditions up to **520 °C, 300 bar and 1.32 kg/s**. This is a public capability description, **not** a source of approved setpoints, ramp rates, sensor list, instrumentation tolerances or as-operated plant P&ID. Public materials describing earlier design stages may give different target temperatures/configurations; do not silently harmonize historical targets with current operation.
- [Unger et al., ASME Turbo Expo 2024, GT2024-122133 abstract](https://asme-turboexpo.secure-platform.com/a/solicitations/223/sessiongallery/15735/application/122133) discusses the CARBOSOLA design and initial operational dynamic behavior, with a laboratory demonstrator. It does not provide our repo with time series, calibrated sensors or permission to perform tests.
- The currently documented WP2b/WP3 models are **synthetic** and use a lumped wall, two assumed UAs, a six-state recuperated Brayton solver, algebraic turbine/compressor efficiencies and an idealized gas-bypass mass fraction. The actual CARBOSOLA **loop topology, expansion equipment, wall and bypass hardware, control authority and instrumentation must be mapped first**. An earlier facility-development stage may not contain an expansion device. Never infer a turbine from the project's name.
- Metrology approach follows [BIPM JCGM 100:2008 GUM](https://doi.org/10.59161/JCGM100-2008E) for Type A/B standard uncertainties, influence quantities and correlations. For nonlinear near-critical CO₂ properties or strongly non-Gaussian inputs, [JCGM 101:2008](https://doi.org/10.59161/JCGM101-2008) Monte Carlo propagation is the appropriate *future* method; it is **not implemented** by the small, linearized source-gas demo.
- The user-supplied 2026 HZDR position specifically emphasizes dynamic load profiles, a comprehensive steady/dynamic CARBOSOLA campaign, data-informed dynamic modeling, operation/control strategies, technoeconomics and publication. This protocol is designed as a prospective research programme, not a summary of completed laboratory work.

**Source/status rule:** public design limits are not approval limits; proposed channels are not installed sensors; a simulated signal is not an independent measurement; a read-only interlock log is not authority to operate or override a safety system.

## 2. Experimental phases and go/no-go boundaries

The complete [13-case experimental matrix](../protocols/wp4/prospective_test_matrix.csv) is a **proposed** set of tests; every `approval_status` is `not_requested`. Do not fill in unsafe arbitrary temperatures, pressure ramps or short sampling times merely to make the plan concrete.

| Phase | Proposed cases | Purpose | Non-negotiable gate |
|---|---|---|---|
| P0 — hardware and safety intake | D00 | Approve actual P&ID, loop topology, heater/cooler locations, bypass existence, turbine presence, hazard review and permitted supervisory control | Facility supervisor/operations owner must approve any facility-specific research procedure |
| P1 — DAQ and metrology | D01 | Identify instrument tags, installed positions, calibration curves/certificates, uncertainty and clocks/latency | Verified independent clock synchronization, safe-range checks, sensor response and acquisition records |
| P2 — steady baselines | S01–S03 | Repeat nominal and multiple approved points; independently measure active/mixed stream enthalpy, wall gradients, CO₂ heater and cooler | Measured mass/energy residuals evaluated **with** uncertainty; no acceptance thresholds invented from a synthetic simulation |
| P3 — open-loop transients | T01–T05 | Approved small step, ramp, flow, bypass and bounded frequency excitation; identify thermal lags and flow dependence | Each excitation requires engineering safety approval; abort thresholds, actuator permissions and sensor bandwidth fixed **before** test |
| P4 — controller comparison | C01 | Compare matched fixed-bypass/PI responses where real controllable bypass is available | No use of uncommissioned PI on a real plant; existing PLC/interlocks remain dominant |
| P5 — independent holdout | V01 and passive A01 | Seal unseen runs for *honest* predictive validation, audit approved event logs | Whole experimental *runs* held out, no refit after prediction; report validity and missing/fail cases |

**Stop conditions are facility-specific, not software-specified:** actual relief/protection envelope; emergency stop architecture; high/low pressure; maximum metal temperature; minimum inlet/critical-margin constraints; actuator travel and permitted load-rate; loss-of-flow and coolant outages; sensor failure and communication loss. The plan is strictly read-only until authorized. It does not prescribe an unsafe trip or forced interlock exercise.

## 3. Sensor, timestamp and calibration inventory

See [35 candidate measurements/metadata channels](../protocols/wp4/measurement_channels.csv) and [uncertainty register](../protocols/wp4/uncertainty_register.csv). They include:

- Hot source stream: upstream temperature, **total flow**, active-branch and bypass-branch **independently measured** flows, active exchanger outlet, mixed outlet, candidate source pressure changes, source gas cp/property composition. A bypass *command* is not a measurement of bypass mass fraction.
- Thermal wall: at least one temperature for the lumped model; two or more independent surface points if the physical wall exists to test whether the lumped isothermal state is tenable. Probe response, location, insulation and metal/casing temperatures require verified design.
- CO₂-side: fluid flow and **pressure and temperature** at physical heater inlet/outlet; separate stations around compressor, recuperator, expander and cooler **only when topology actually contains them**. State numbers 1–6 label *the model*, not confirmed physical CARBOSOLA sensor addresses.
- Cooler/shaft: coolant flow and inlet/outlet temperature; torque and rotational speed if measured; whether electrical power includes auxiliaries. Any comparison between `W_shaft` and `W_electric` requires measured parasitics and a defined system boundary.
- Control and safety: requested bypass fraction, measured actuator position, independently measured branch flows, interlock/event status and synchronized DAQ clock. The research software cannot control, alter or disable facility protection.

Required instrument specification per *verified* installed channel: manufacturer and full model, accuracy as **stated range distribution** rather than blindly treated as standard uncertainty, serial/location, calibrated range, certificate ID/date/traceability, time constant, logger/filter/anti-alias settings, nominal sampling interval, time source/clock drift, correlated shared reference groups, missing/overrange indicators, process-wall immersion/conduction effects, thermowell response and CO₂ phase/property domain. **All values are currently unknown**; no device type or accuracy has been invented.

DAQ / telemetry: export raw immutable signals and a separate quality-flag stream with an absolute-time epoch and/or monotonic timebase, map offsets from controller/event clocks, save sensor filter and sample-period configurations, and explicitly document jitter and data gaps. The long-format validator only checks numeric format, known units, missing flags, duplicate timestamps and optionally excessive gaps. It **does not** establish calibration, timestamp *cross-channel alignment*, sensor physics or protective validity.

## 4. Actual first-law measurements and residuals

For a **constant-property** source gas stream at total mass flow `m_g` and equal cp in both branches, the intended upstream/downstream **mixed** sensible heat extraction is:

```text
Q_gas = m_g * cp_g * (T_g,in - T_g,mixed,out)
m_g = m_active + m_bypass
Q_gas = Q_gas_to_wall + Q_loss,gas     (must measure/estimate losses)
```

For a real source with composition/variable cp, instead use `m_g [h_g(T_in,p_in,y)-h_g(T_out,p_out,y)]`, accounting for composition `y`, heat leaks and pressure work assumptions.

Measured CO₂ heater duty is `Q_CO2 = m_CO2 [h(T4,p4)-h(T3,p3)]`, with EOS input uncertainties and CO₂ composition/phase range. **Do not** evaluate as `m_CO2 cp_CO2 ΔT` near the critical region.

If the actual loop contains a turbine, cooler and recuperator matching the six-state model, the model identity is `Q_CO2 = W_t-W_c+Q_cooler` under explicitly stated ideal boundary conditions. Actual auxiliary power, unmetered losses, pump work, and other heaters must be added explicitly to a real plant balance. If the facility stage **has no expander**, do not claim that a measured net Brayton shaft power exists.

The target transient wall ledger (if a corresponding physical wall and instruments exist) is:

```text
Integral(Q_gas_to_wall - Q_wall_to_CO2 - Q_losses) dt
            = C_wall [Twall(end)-Twall(start)]  [for constant Cwall lumped CV]
```

Distinguish at all times *directly measured* heat flow, thermodynamic-inferred duty, and model-predicted energy. Intervals with missing channels do not become valid because an algebraic residual can be forced to zero using the same predictions on both sides.

## 5. Uncertainty and adequacy gate

Do not copy nominal values from manufacturers or choose convenient percentages to make uncertainty budgets complete. Start with calibrated data and derive **standard** Type A (repeatability, drift) and Type B (calibration, readout, location, lag) contributions and their covariance groups. Especially include shared calibration offsets for `T_in-T_out`, pressure/temperature cross-correlation in EOS-derived enthalpy, timing error across rapid transients, partial flows and mixed-stream enthalpy, and model mismatch from composition or spatial gradients. Report expanded uncertainty only with explicitly justified coverage factor and effective degrees of freedom.

For preliminary constant-`cp` gas sensible heat, the implemented **JCGM first-order local** estimator is:

```text
Q = m * cp * (Tin - Tout)
u(Q)^2 =
  (cp*DeltaT*u(m))^2 +
  (m*DeltaT*u(cp))^2 +
  (m*cp)^2 * [u(Tin)^2 + u(Tout)^2 - 2*rho*u(Tin)*u(Tout)]
```

This assumes the flow and cp estimates are independent of each other and both temperatures, while the temperature standard uncertainties may be correlated by `rho`. **Do not use it as an EOS/enthalpy uncertainty model or a calibrated result**, and do not report `k=2` automatically as a confidence interval. An independent Monte Carlo/real-gas propagation with covariance and calibration source documentation is future work.

For a dynamic comparison, compare the residual to an **independently propagated** uncertainty of *all* measured balance terms (including temporal covariance/lag and integration); an apparent zero residual from shared model predictions does not demonstrate validity. Define required precision **after** selecting actual detectable effects and instrumentation, not by an arbitrary universal tolerance.

## 6. Parameter identification and validation

The first three research quantities are (a) gas-to-wall conductance `UA_gw`, (b) wall-to-CO₂ `UA_wc` and (c) effective wall capacity `C_wall`, **only if the real hardware includes the corresponding wall and separately measurable heat paths**. A real facility without a physically distinct wall-and-gas-bypass energy pathway cannot meaningfully identify these hypothetical parameters; then redesign the model around the installed equipment rather than fit synthetic geometry.

Proposed sequential identification:
1. Obtain **independent** gas mass, temperatures and source cp/enthalpy to infer source duty; do not extract source duty from the wall model being tested.
2. In steady operating points, estimate effective `UA_gw` from measured active source flow and gas-wall temperature approaches, and `UA_wc` from CO₂ enthalpy gain and measured wall/heater spatial temperature. Source/wall loss terms must be audited separately.
3. In dynamic **open-loop** steps, identify `C_wall` and sensor lag using measured `Twall(t)`, observed gas/CO₂ heat rates, synchronized clocks and known measurement delay. Do not confuse thermal time constant with pure transport delay.
4. Vary flow and load independently to test whether fixed `UA` remains applicable. Repeat data collection across operating points; retune or invalidate the assumed model if flow dependent.
5. Only after a valid actuator mapping from **position to actual bypass mass fraction** should PI responses be compared. Report overshoot, settling, saturation/rate activity, total recovered shaft energy and protection/event behavior with uncertainty.
6. Split **whole contiguous runs/families** into fitting, selection and **predeclared sealed final holdout** groups. All tuning (including property assumptions, lag corrections and controller gains) must be fixed before the sealed evaluation. Document every dropped sample/run and reason.

Local identifiability: build normalized output/parameter sensitivity matrix `S_ij = (theta_j / sigma_yi) d(y_i)/d(theta_j)` for nonzero/reference-scaled parameters; the implemented QR-like column-normalized elimination checks only **local matrix rank**. Rank deficiency signals that at least one parameter direction is not independently resolved by the selected tests. Full rank does **not** prove global identifiability, good parameter conditioning, sufficient signal-to-noise or unbiased estimates. In future use `S^T Sigma_y^-1 S`, singular values, profile likelihood, parameter covariance and cross-validation.

**Minimum scientific acceptance:** complete calibration provenance, stability/equilibrium of declared steady windows, synchronized inputs/outputs, independent measurement of all relevant balance terms, an explicit uncertainty budget, immutable raw files, traceable run/operating point IDs, no unrecorded imputation, run-group held-out prediction and a posterior residual/coverage report. Forecast metrics cannot be compared if facility and model topologies differ.

## 7. Raw-run provenance and leak-free validation bookkeeping

The **prospective (never executed)** [run manifest template](../protocols/wp4/prospective_run_manifest.json) records a run ID, data class, facility and P&ID revision references, authorization reference, raw-data SHA256, channel register SHA256, certificate/timing evidence and predeclared run split. All actual evidence fields are deliberately **null**. `validate_provenance_manifest` checks format and blocks a purported *measured* run with missing references, but **cannot authenticate** referenced certificates, actual instrument installation, facility approval, file integrity or experiment completion. Even a syntactically complete measured manifest reports that external verification remains outstanding.

`audit_run_partition` requires three separate lists of **whole run or physical family IDs** for fitting, tuning and a predeclared sealed final holdout. It rejects shared/duplicate run IDs and empty groups; it cannot prove that two differently named IDs are physically independent or that a researcher never inspected the holdout. Such independent scientific controls require a steward-controlled registry and review.

Once real instrumentation and authorization are secured, store immutable raw datasets with independent SHA256 files, approved P&ID and sensor maps, calibration versions, timebase and quality flags. Raw data should remain preserved when reduced/filtered data are created, with all filters logged. Do not include real sensitive plant information or access-controlled engineering records in the public repository without written permission.

## 8. Files, execution and release meaning

```text
protocols/wp4/measurement_channels.csv       35 proposed channels
protocols/wp4/prospective_test_matrix.csv     13 prospective cases
protocols/wp4/uncertainty_register.csv        no supplied calibration accuracies
protocols/wp4/synthetic_format_fixture.csv   synthetic parser tests only
protocols/wp4/prospective_run_manifest.json   unexecuted/non-authorized metadata template
src/sco2_braytonbench/experimental_readiness.py
tests/test_experimental_readiness.py
examples/wp4_readiness_audit.py              produces machine report (not plant results)
```

```bash
python -m pip install -e '.[test]'
python -m pytest -q tests/test_experimental_readiness.py
python examples/wp4_readiness_audit.py
```

The mandatory WP4 software gate is *reproducible specification and fail-closed quality checks*. Actual rig readiness stays **blocked** until the real P&ID, approval, mounted sensors, certificates, time synchronization, uncertainty budget and measurement data are independently supplied and reviewed. A software v1.0 tag must not reclassify a proposed campaign as a completed experiment.
