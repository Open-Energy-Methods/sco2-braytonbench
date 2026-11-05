# G3.5-H1c — Published Lei bottom/top correlation transferability: negative result

**Executed on 2026-11-05** using CoolProp 8.0.0, `HEOS::CO2`.  
**Source experimental data:** Theologou et al. (2022), [Stuttgart Mendeley DOI 10.17632/4mvk4nxrkz.1](https://doi.org/10.17632/4mvk4nxrkz.1), original source licensed CC BY 4.0.  
**Equations:** Theologou et al. (2022), *Energy* 254, 124171, Eq. 17, [DOI 10.1016/j.energy.2022.124171](https://doi.org/10.1016/j.energy.2022.124171), citing Lei, Li, Dinh & Zhang (2017), [DOI 10.1016/j.ijheatmasstransfer.2017.06.052](https://doi.org/10.1016/j.ijheatmasstransfer.2017.06.052).  
**Completed real-fluid CI:** [Actions run 42040967963, H1c job passed](https://github.com/Open-Energy-Methods/sco2-braytonbench/actions/runs/42040967963).  
**Raw numerical evidence:** [G3.5-H1c JSON + 3,160 model-station CSV records](https://github.com/Open-Energy-Methods/sco2-braytonbench/actions/runs/42040967963/artifacts/13421155963).  
**Code/method:** [H1c provenance and equation specification](G35C_LEI_TOP_BOTTOM.md).

## Scientific verdict

**Lei top/bottom equations could be executed source-faithfully; they are NOT transferable as useful predictive correlations to these Stuttgart near-critical sCO₂ 4/8-mm measurements without substantial model change.**

This is **not a failure of the original water experiments or a contradiction** of Lei et al.'s work. The original fitting/validation conditions were **supercritical water at approximately 23–25 MPa in 26/43-mm horizontal pipes**, while this study applies the equations to CO₂ at about 7.75 MPa in 4/8-mm tubes. This is an *out-of-original-domain stress test*. Even a small error would not validate the new fluid or geometry.

### Exact eligible station inventory and provenance

- Original Stuttgart source: **54** experiments, **2,508** axial rows, **2,398** reduced local HTCs.
- Original source anomaly STU-001 (`4MM_HM_77.5_10_20_90_A`, q = 832.992 kW/m² vs ~91.7 matched runs): **whole experiment still quarantined**, original CSV remains unmodified.
- H1a/H1b admissible population: **2,318** original H1b Jackson-flux comparison stations.
- Bottom HB **790** + top HT **790** = **1,580** Lei-candidate stations, across **36** orientation-specific experimental runs and **18** original nominal families.
- Middle HM **738** excluded because **Lei has no published HM equation**. No interpolation or angular multiplier invented.
- **Four original SHA256-selected held-out nominal families** preserved unchanged: **356** eligible HB/HT stations; no parameters fitted or dataset resplit.
- The original source temperature and heat-flux reduced data are used as stated inputs. In particular, experimental local HTC and measured wall temperature are *not independent measurements*.

## Measured-derived HTC prediction errors on SAME HB/HT stations

| Model and method | Eligible HB+HT stations | Overall local MAPE | HB bottom MAPE | HT top MAPE | Held-out MAPE |
|---|---:|---:|---:|---:|---:|
| **Lei**, measured-wall conditioned (diagnostic) | 1,580 | **175.18%** | 76.26% | 274.09% | 177.26% |
| **Lei**, flux-driven wall inversion (no measured Tw input) | **1,580** | **631.72%** | **197.73%** | **1065.72%** | **638.83%** |
| Jackson–Hall, flux-driven, matched 1,580 stations | 1,580 | **55.52%** | 26.41% | 84.63% | **49.35%** |
| Gnielinski bulk forced convection, matched 1,580 stations | 1,580 | **162.26%** | 87.71% | 236.81% | 170.29% |

**Bishop flux-driven is available only on 1,468 of the same HB/HT stations**, due to its earlier original x/D gate. Its MAPE on that subset is **52.72%**, but it must not be compared as though all 1,580 points were shared.

**Important data leakage distinction:** the Lei *measured-wall conditioned* 175.18% uses experimentally reported Tw as an input; the **flux-driven** 631.72% obtains Tw by solving `q'' = HTC(Tw)*(Tw−Tb)`, with q'' and bulk enthalpy sourced from the experiment. Both remain conditional on the measured source flux/bulk; only the second avoids inputting the experimental wall temperature.

### Statistics and uncertainty interpretation

The Lei flux-driven mean signed percentage bias was **+630.69%**: gross systematic overprediction rather than symmetric noise. Its **median** absolute percentage error was **269.67%**, and the top-wall error was far larger than bottom-wall error. For Jackson flux-driven on matched stations the signed bias was +41.02%.

In **all 18 nominal experimental families**, Jackson has lower mean absolute error than Lei in the flux-driven head-to-head. The mean family-equal-weighted advantage (Jackson error minus Lei error) was **−599.17 percentage points**; a deterministic **4,000-draw resampling of nominal families** gave a between-family percentile interval of **[−756.20, −460.04] percentage points**. This interval is **not experimental measurement uncertainty, statistical generalization to unseen rigs, or proof of a universal physical law**. The four held-out families are unchanged, and the same source station IDs were used for all paired scores.

## Solver convergence and initial-run correction

Initial exploratory [run 42040294906](https://github.com/Open-Energy-Methods/sco2-braytonbench/actions/runs/42040294906) used a coarse `0.008 K` root-width tolerance. Despite clear wall-balance brackets, **234/1,580** flux-driven points were rejected because the wall-energy residual remained greater than the separately imposed 0.2% threshold. These were **numerical resolution artifacts**, not thermophysical exclusions.

The revised solver used a wall-root bracket width **1e-5 K**, with up to 35 bisection iterations, retaining independent `|h(Tw)(Tw−Tb)-q''|/q'' <=0.002` acceptance. The refined H1c run completed **1,580/1,580 flux-driven points** without a numerical rejection, and the largest observed relative heat-flux balance residual was **1.2722×10⁻⁵**, equivalent to **0.00127%**; median relative residual **4.4174×10⁻⁷**. The final poor predictive error therefore does **not** stem from the early solver-resolution exclusions.

The local bisection scan detects **sampled** sign changes; it does not mathematically prove uniqueness of the physically coupled mixed-convection state. The model does not solve the CO₂ fluid's transverse velocity/temperature field.

## Interpretation and research direction

1. The published Lei equations *do distinguish* HB and HT physically and are implemented with the correct wall/bulk density, conductivity, integrated Prandtl and heat-flux Grashof definitions. However, simply transferring them from **supercritical water/26–43mm** to **near-critical CO₂/4–8mm** produces huge positive HTC bias and is **unacceptable for equipment design**.
2. The original H1b Bishop/Jackson formulae, although not genuinely angular, remain significantly more accurate under the specific conditional benchmark; they too are not fully validated as CO₂ orientation-specific laws.
3. A directly relevant **horizontal supercritical-CO₂** mixed-convection study exists: Kim, Kwon, Park, Park & Kim (2019), *Heat transfer model for horizontal flows of CO₂ at supercritical pressures in terms of mixed convection*, *Int. J. Heat Mass Transfer* 131:1117–1128, [DOI 10.1016/j.ijheatmasstransfer.2018.11.075](https://doi.org/10.1016/j.ijheatmasstransfer.2018.11.075). Its abstract reports ~10% *original-study* top/bottom mean absolute deviation for an empirical formulation. **Full coefficients and model equations were not recovered in publicly accessible text during this review.** No implementation, source-aligned benchmark or reproducing that 10% is claimed.
4. The other alternative is a geometry- and fluid-grounded mixed-convection reduced-order model, but it would require **transparent calibration on development families only, with the four existing held-outs untouched**; a fitted top/bottom multiplier to the full dataset would be scientifically weak.
5. Do not silently use this Lei HTC to set BraytonBench PCHE UA or sCO₂ cycle efficiency. Tube orientation, wall heat flux, buoyancy and nonuniform channels matter.

## Gate decision

**H1c source-equation implementation and 1,580-point numerical benchmark: PASS.**  
**H1c cross-fluid heat-transfer correlation transferability: FAILS badly.**  
**G3.5 validated near-critical, orientation-resolved CO₂ heat-transfer model: OPEN.**  
**Full industrial G3 and Brayton-cycle plant/controls validation: OPEN.**

This source-faithful negative result is appropriate to retain for a reproducible methods benchmark. Do not tune original Lei published coefficients post hoc and then claim a Lei replication.
