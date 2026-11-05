# G3.5 H1 — Stuttgart measured local HTC benchmark results

**First executed experimental comparison:** 2026-11-05  
**Source:** Theologou, Mertz, Laurien and Starflinger, original [Mendeley dataset DOI 10.17632/4mvk4nxrkz.1](https://doi.org/10.17632/4mvk4nxrkz.1), CC BY 4.0; paper [10.1016/j.energy.2022.124171](https://doi.org/10.1016/j.energy.2022.124171).  
**Backend:** CoolProp **8.0.0** `HEOS::CO2`.  
**Successful experiment job:** [GitHub Actions run 42031845343, `stuttgart-h1`](https://github.com/Open-Energy-Methods/sco2-braytonbench/actions/runs/42031845343).  
**Full per-point CSV and numeric JSON:** [GitHub artifact 13416397877](https://github.com/Open-Energy-Methods/sco2-braytonbench/actions/runs/42031845343/artifacts/13416397877).

## Source and exclusion ledger

| Quantity | Records |
|---|---:|
| Original source experiment IDs | 54 |
| Original source axial records | 2,508 |
| Original local **experimentally derived** HTC records | 2,398 |
| Source anomaly STU-001 quarantined experiment | 1 |
| Quarantined local HTC stations | 50 |
| Retained local HTC observations | 2,348 |
| Excluded per model: x/D and applicability limits | 30 |
| **Successfully predicted local HTC comparisons per correlation** | **2,318** |
| Successfully compared individual runs | 53 |
| Nominal orientation families represented | 18 |
| Held-out nominal families | 4 |
| Held-out valid local comparisons per correlation | 534 |

The complete source data (including original anomalous q) are retained in [`data/validation/stuttgart/`](../data/validation/stuttgart/README.md) and the original original publication is credited under its CC BY 4.0 licence. The experiment `4MM_HM_77.5_10_20_90_A` is **quarantined** because its 832.992 kW/m² source q conflicts strongly with its matched top/bottom runs (~91.7 kW/m²). It was **not silently corrected**.

The 30 applicability exclusions per model arise from the selected near-inlet x/D eligibility, primarily the 8 mm pipe stations at x=0.04 m (x/D=5), not failed experimental property computations. No property exceptions affected the reported totals.

## Two independently chosen reference correlations

- Smooth-tube **Gnielinski**, conventional fully developed forced convection, `Nu=((f/8)(Re−1000)Pr)/(1+12.7 sqrt(f/8)(Pr^(2/3)−1))` with `f=(0.79 ln Re−1.64)^−2`. Hard applicability domain `Re 3000–5×10^6`, `Pr 0.5–2000` and x/D≥10.
- Heating **Dittus–Boelter**, `Nu=0.023 Re^0.8 Pr^0.4`, `Re≥10000`, `Pr 0.7–160`, x/D≥10.

Only **bulk CO₂ properties** are used to calculate local `Re`, `Pr` and HTC. Both models ignore wall temperature, buoyancy, thermal development, circumferential orientation and strong supercritical property-gradient corrections. Their apparent failure is not proof that a more suitable sCO₂ correlation fails.

Because the source paper derived bulk enthalpy with REFPROP, the property state uses measured inlet `P`, `T` as CoolProp reference and then the source's **within-run enthalpy increment** rather than assuming an identical absolute REFPROP/CoolProp enthalpy reference. Axial pressure is approximated by the recorded inlet pressure. The local HTC is experimentally **derived**, not independently measured by a standalone HTC sensor; its input quantities are correlated.

## Measured-derived local HTC prediction errors

**MAPE** = mean of stationwise `100*|HTC_model−HTC_source|/HTC_source`. It is calculated **without training** either correlation.

| Metric | Gnielinski | Dittus–Boelter |
|---|---:|---:|
| Evaluated stations | 2,318 | 2,318 |
| **Overall MAPE** | **150.15%** | **119.60%** |
| Mean signed relative error (bias) | +137.05% | +100.55% |
| Median absolute percentage error | 55.07% | 47.17% |
| 90th percentile absolute percentage error | 385.05% | 298.15% |
| Root mean square percentage error | 266.27% | 210.29% |
| **Experiment-macro mean MAPE** | 156.89% | 124.70% |
| Family-macro mean MAPE | 156.39% | 124.24% |
| Descriptive fraction within source's reported 1-σ local HTC | 15.44% | 11.22% |
| Median absolute error in units of source's reported local HTC σ | 11.46 | 8.03 |

Large positive mean signed errors indicate **strong overprediction**, particularly in top- and 8 mm-wall profiles. Descriptive within-σ rates **must not be treated as formal confidence coverage** because HTC, wall temperatures, axial enthalpy and heat input are experimentally derived and correlated, while source uncertainty does not include prediction/model-form uncertainty.

### Circumferential orientation

| Location | Number of admissible stations | Gnielinski MAPE | Dittus–Boelter MAPE |
|---|---:|---:|---:|
| **HB — bottom 180°** | 790 | 87.71% | 69.65% |
| **HM — middle 90°** | 738 | 124.23% | 98.76% |
| **HT — top 0°** | 790 | **236.81%** | **189.01%** |

The orientation split is a critical failure signature: both baseline expressions are **orientation-blind**, so they cannot predict independent top/middle/bottom coefficients under substantial buoyancy-driven stratification. Even when the underlying inlet properties differ slightly across nominal matched runs, a uniform fully developed forced-convection model is not an adequate description of these measurements.

### Tube diameter

| Diameter | Stations | Gnielinski MAPE | Dittus–Boelter MAPE |
|---|---:|---:|---:|
| 4 mm | 1,150 | 96.13% | 78.65% |
| 8 mm | 1,168 | **203.34%** | **159.91%** |

### Predeclared held-out experiment families

All orientations of a nominal experimental configuration are assigned together based on a fixed SHA256 source key; **no single-run axial leakage and no fitted coefficients**.

| Split | Stations | Gnielinski MAPE | Dittus–Boelter MAPE |
|---|---:|---:|---:|
| Development groups | 1,784 | 147.77% | 118.93% |
| **Held-out groups** | **534** | **158.10%** | **121.82%** |

Held-out families: `4MM_H*_77.5_10_20_30_A`, `4MM_H*_77.5_5_5_50_A`, `8MM_H*_77.5_40_30_90_A`, `8MM_H*_77.5_40_5_130_A`.

Because neither baseline was fitted, these held-out metrics are **evaluation strata**, not genuine out-of-sample evidence of a newly trained model.

## Comparison to published findings

The paper describes strong circumferential stratification (up to ~90 K) and reports that its own set of four tested correlations had a **Bishop correlation average deviation of 52%**. The latter is not necessarily the same metric or eligibility subset as this project's Gnielinski/Dittus numbers. **Do not claim a direct quantitative leaderboard against the authors or attribute our 119.6% to the Bishop model.**

Our scientific conclusion is limited but useful: **under declared bulk-property, smooth-tube and forced-convection conditions, neither conventional baseline describes local experimentally derived HTC well across the Stuttgart source envelope**. This is a credible case for source-aligned near-critical/buoyancy-aware formulations.

## What has and has not passed

**Passed:**
- Full source-integrity and quarantine checks (54/2508/2398).
- Seven fixture-only mathematical/source/grouping tests using an **artificial fluid** (not CO₂) locally and in the dedicated CI job.
- Real-CO₂ CoolProp 8.0.0 actual 2,318-prediction comparisons for *each* baseline, archived per-point and as aggregate metrics.
- Reproducible deterministic nominal-family partition and source reported-σ documentation.
- Fully uncalibrated baseline; no training leakage from tuned parameters.

**Not achieved:**
- An accurate/validated predictive sCO₂ HTC correlation (MAPEs are very large).
- Full covariance propagation, measured pressure profile or experimentally calibrated fluid transport model.
- Buoyancy/acceleration/wall-property/local thermal development modelling.
- A PCHE HX, turbine/compressor map, installed-UA plant, or Brayton-cycle experimental validation.

**Gate: H1a data-to-comparison pipeline PASS; H1b predictive correlation validation OPEN.**

Next milestone: scientifically implement and independently source-review at least two buoyancy/near-critical-aware correlation formulations as specified in Theologou et al., calculate applicability and uncertainty, then compare against **unchanged four held-out nominal families**. Do not change the split post hoc or simply tune a multiplier to the full dataset.
