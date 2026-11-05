# G3.5 H1c — Lei et al. top/bottom mixed-convection benchmark

**Work:** add source-defined orientation-sensitive Nusselt formulas, not a calibrated model or a free numerical interpolation. **Parent:** G3.5 H1b draft PR #15, Stuttgart data DOI 10.17632/4mvk4nxrkz.1, CC BY 4.0.

## Scientific source and exact formulas

Theologou et al. (2022), *Experimental investigations on heat transfer of CO₂ under supercritical pressure in heated horizontal pipes*, *Energy* 254, 124171, [DOI 10.1016/j.energy.2022.124171](https://doi.org/10.1016/j.energy.2022.124171), Eq. (17), reproduces top/bottom equations from:

Lei, X., Li, H., Dinh, N., Zhang, W. (2017), *A study of heat transfer scaling of supercritical pressure water in horizontal tubes*, *Int. J. Heat Mass Transfer* 114, 923–933, [DOI 10.1016/j.ijheatmasstransfer.2017.06.052](https://doi.org/10.1016/j.ijheatmasstransfer.2017.06.052).

```text
For bottom orientation HB:
Nu = 0.27227 Re_b^0.64 Prbar_b^0.731 (rho_w/rho_b)^1.189
             (lambda_b/lambda_w)^0.449

For top orientation HT:
Nu = 0.01482 Re_b^0.8175 Prbar_b^0.5868 (rho_w/rho_b)^0.589
             (Gr_q)^0.05879

Prbar_b = [h(P,Tw)-h(P,Tb)]/(Tw-Tb) * mu_b/lambda_b

Gr_q = g*beta_bar*q''*D^4 / (nu_b^2 * lambda_b)
nu_b = mu_b/rho_b
beta_bar = (rho_b-rho_w) / [rho_f*(Tw-Tb)]
rho_f = rho(P, (Tw+Tb)/2).
```

All temperatures are in kelvins, mass flux `G=4m_dot/(pi D²)`, Re=`G*D/mu_b`, `HTC=Nu*lambda_b/D`. The source paper provides **NO** Lei equation at the middle-wall sensor (HM): HM is explicitly withheld, with no geometric interpolation fabricated.

**Critical domain limitation:** the original Lei correlation was fitted/validated for **supercritical WATER in 26 mm and 43 mm horizontal pipes**, approximately 23–25 MPa. Applying it to the 2022 **supercritical CO₂, 4 mm/8 mm pipes, ~7.75 MPa** is **outside its source fluid and geometry/pressure domain**. Numerical comparison is a *transferability stress test*, NOT source-valid calibration, industrial prediction or a new validated formula. This qualification applies to every scored point even if MAPE is small.

## Two epistemically distinct evaluation modes

- **Conditioned on measured wall T**: diagnostic only. Experimental reduced local HTC is approximately q''/(Tw_measured−Tb). Using measured wall T as correlation input is *target-associated information leakage*, so lower MAPE must NOT be presented as independent prediction.
- **Flux-driven implicit wall solution**: uses experimental heat flux, inlet-anchored source bulk enthalpy, P, mass flow, tube diameter, and CoolProp 8.0.0 CO₂ properties. Solves `q''=HTC(Tw)*(Tw−Tb)` for Tw without accessing experimental Tw as a solver input. The result is a conditional local prediction (not autonomous heat-source or coolant simulation). Scans for a single sign-changing root in specified wall-temperature range; refuses ambiguous/nonconvergent/physically impossible cases. Excluded states and energy residuals are recorded.

Lei HT `Gr_q` depends explicitly on `q''` and temperature/density, so both modes use the source heat flux. The result is not an independent flux prediction. Lei HB uses wall/bulk densities and conductivities but not `Gr_q` explicitly.

## Holdouts, original source QC and comparisons

Preserve **all 54 original Stuttgart experiments**, 2,508 axial records and 2,398 reduced local HTC points. Source run STU-001 with anomalous original 832.992 kW/m² is never edited or included in scores. Reuse identical **four deterministic held-out nominal orientation families** (never randomly sample correlated axial points); no regression coefficients, calibration multiplier or new split fitting.

H1c takes the 2,318 original H1b Jackson-flux-successful stations as its reference input population: 790 HB, 790 HT, 738 HM. HM is **excluded by source definition**, leaving at most 1,580 top/bottom stations per Lei mode. It records separate error and convergence exclusions rather than silently filling missing values. Any successful model comparison must use the *same eligible station IDs*, not compare misleading overall MAPE values across different H1b subsets.

For each Lei mode report point MAPE/bias, macro run and nominal-family error, HB/HT and 4/8 mm errors, unchanged four held-out groups, matched-station H1b Jackson, Bishop and Gnielinski errors, and a **seeded 4,000-resample nominal-family bootstrap**. Bootstrap assesses variation across 18 source configurations; it is NOT instrument covariance, a 95% predictive confidence interval or external test-set generalization. Original source HTC and measured wall T are calculated from related sensors and are not statistically independent.

## Reproduce

```bash
python -m pip install -e '.[test,co2]' 'CoolProp==8.0.0'
python -m pytest -q tests/test_lei_mixed_convection.py
python scripts/stuttgart_h1.py
python scripts/stuttgart_h1b.py
python scripts/stuttgart_h1c.py
```

The dedicated GitHub Actions job `stuttgart-h1c-lei-orientation` uploads per-station matched records and source-split metrics. A **green CI status proves reproducible arithmetic and completed evaluations; it does not establish physics validation**, particularly because every Stuttgart point is outside Lei's fitted fluid and channel-diameter domain.

**Gate:** H1c implementation/real-fluid transferability comparison only; **orientation-sensitive CO₂ heat-transfer correlation validation remains OPEN** pending original-domain CO₂ testing or an independently validated sCO₂ mixed-convection closure.
