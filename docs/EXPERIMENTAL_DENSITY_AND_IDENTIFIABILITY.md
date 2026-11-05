# Independent measurements and source-model identifiability — v0.5 verification addition

## 1. Measured density: Mantilla et al. (2010)

Independent property-data class: **experimentally measured pure-CO₂ density** using a single-sinker magnetic suspension densimeter.

- Primary source: Mantilla, Cristancho, Ejaz and Hall, *P-ρ-T Data for Carbon Dioxide from (310 to 450) K up to 160 MPa*, J. Chem. Eng. Data 55 (2010), 4611–4613, DOI [10.1021/je1001158](https://doi.org/10.1021/je1001158).
- Machine-readable source: NIST ThermoML [landing page](https://trc.nist.gov/ThermoML/10.1021/je1001158.html) / [JSON](https://trc.nist.gov/ThermoML/10.1021/je1001158.json).
- 49 observations at **310, 350, 400, 450 K**, pressure approximately **0.999–159.844 MPa**.
- Archive: `data/reference/mantilla2010_thermoml_density.csv` and explicit `data/reference/mantilla2010_provenance.yaml`.
- Measurements are separate from the older 1996 Span–Wagner parameter fitting, giving real experimental evidence beyond cross-checking REFPROP against CoolProp.

**Do not confuse** NIST-reported combined uncertainty values with standard deviations, 95% coverage intervals, or percent values: the numeric field is retained *as printed* pending confirmation of its metadata interpretation. The source article reports density precision below 0.03% over its studied range; the initial regression limits in our tests (max 2%, RMS 1%) are only broad software checks and **are not a claim that CoolProp's true uncertainty is 1–2%**.

### Test protocol

For each measured state ((T_i,P_i,\rho_i^{exp})), evaluate CoolProp `HEOS::CO2` at the **measured** T and P. Report
`e_i=(rho_CoolProp-rho_exp)/rho_exp`, mean bias, maximum absolute residual, RMS relative residual, worst cases and per-temperature statistics.

Check 49-row integrity and finite positive values. Compute all numerical statistics in GitHub Actions with the version-pinned CoolProp 8.0.0; store `evidence/generated/mantilla2010_measured_density.json` with the observation CSV SHA-256. Tests may pass at broad screening limits while the gate remains open pending review of maximum deviations and measured uncertainties.

Coverage limitations: no measured enthalpy, entropy, heat capacity, sound speed, vapour-liquid boundary or near-critical singular-region (c_p) values. Most points are not immediately adjacent to CO₂'s critical point.

## 2. Alternative thermodynamic model

NIST released a new alternative CO₂ fundamental EOS in 2026:

- Lemmon, Harvey and Hellmann, [*Alternative Fundamental Equation of State for Fluid Carbon Dioxide*](https://doi.org/10.6028/NIST.IR.8608), NISTIR 8608 (2026).
- NIST also hosts a [REFPROP-readable new CO₂ fluid file](https://data.nist.gov/od/id/mds2-3953).

**Not executed:** this EOS is not automatically available within standard CoolProp `HEOS::CO2`, and the REFPROP-readable file is not a standalone Python property-engine replacement. Claiming an alternative-EOS comparison without a correctly implemented thermodynamic backend would be misleading. Independent experimental comparisons are executed first.

## 3. Friedman–Rapp source identifiability

The 2016 paper's **Figure 2b** provides a 12-point conceptual cycle, and the more complex **Figure 4** shows a model with compressor turbine, main turbine, motor/generator and bypass paths (FM3 and FM4 are set to zero in the reported calculations).

What **is constrained by the paper**:
- P1 = 30 MPa; T1 = 550 K; compressor/turbine efficiencies, nominal recuperator effectiveness, component/pipe pressure losses (Table 2).
- The paper identifies `T7` as the low temperature in its parametric analysis; the *compressor-suction pressure* corresponds naturally to point 8 of the conceptual cycle.
- Table 3's net energy balance and reported system aggregate powers at one illustrative operating point.

What **is not sufficiently disclosed for exact reproduction**:
- All state temperatures, densities and enthalpies in the ~400-equation EES Figure 4 plant.
- Detailed compressor turbine / main turbine mass flow and shaft-work allocation and machinery maps.
- External reactor/heat-sink system model and all initialization constraints.
- Numerical library/reference state and losses outside the reduced Table 2 ledger.
- The original EES model files, which would be needed to establish parameter-by-parameter equivalence.

**Source-condition mapping discipline:** The default `T7/P8` interpretation is grounded in the paper's low-temperature label and compressor-suction terminology. We additionally calculate `T8`, `P7` alternatives as **counterfactual boundary-label stress tests**, not equally likely or paper-authorized interpretations. Their variation tests the consequences of an indexing error rather than creating uncertainty where the paper explicitly labels a state.

The aggregate Table 3 energy totals impose only a small number of independent scalar constraints. For example, knowing combined turbine work alone cannot determine an auxiliary-turbine/main-turbine split (even before considering feasible flow routing). Therefore even a small efficiency discrepancy does not prove original plant-model identifiability.

## 4. Gate decision

- G1-E: measured PVT data available and tested in CI; **partial** until actual residuals reviewed, uncertainty evaluated and critical-region/h/s independent data collected.
- G2: the conceptual source cycle and perturbation analysis are auditable; **original detailed EES plant remains not identifiable** from the published aggregates.
- The benchmark shall never be relabelled an HZDR CARBOSOLA twin, measured test campaign or full EES code reproduction.

## Final regression check

The stricter density regression screens of **0.2% maximum absolute relative residual** and **0.1% RMS relative residual** passed GitHub Actions [run 41993973281](https://github.com/Open-Energy-Methods/sco2-braytonbench/actions/runs/41993973281).
The tests are not a statistical fit of uncertainties. The original article's statement of <0.03% density uncertainty should not be confused with these regression thresholds; the observed largest EOS–measurement residual of approximately 0.090% is larger.
