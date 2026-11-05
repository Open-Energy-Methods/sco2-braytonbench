# G3.5 H1b — Real-fluid Bishop and Jackson–Hall measured HTC comparisons

**Executed:** 2026-11-05 · **CoolProp:** 8.0.0 `HEOS::CO2`  
**Source:** Theologou et al. (2022), [experimental dataset DOI 10.17632/4mvk4nxrkz.1](https://doi.org/10.17632/4mvk4nxrkz.1), licensed CC BY 4.0.  
**CI calculation:** [GitHub run 42035909213](https://github.com/Open-Energy-Methods/sco2-braytonbench/actions/runs/42035909213) (H1b job passed).  
**Machine evidence:** [G3.5 H1b full report and local point CSV](https://github.com/Open-Energy-Methods/sco2-braytonbench/actions/runs/42035909213/artifacts/13417234462).  
**Source formulas and validity:** [H1b methodology](G35B_WALL_PROPERTY_CORRELATIONS.md).

## Original data and unmodified benchmark gates

The H1a full baseline regenerated unchanged: **54 original experimental run IDs**, 2,508 source axial records, 2,398 experimentally reduced local HTC records, 50 HTC points quarantined from source run STU-001 (anomalous original q), then 30 near-inlet applicability exclusions per original model. H1a provides 2,318 admissible station predictions per baseline.

H1b uses the exact **same four held-out nominal experiment families**, with every HB/HM/HT orientation and axial location from one nominal family in the same group. **No coefficients fitted.** All comparisons use CoolProp local bulk states reconstructed from inlet-T-anchored *within-run* source bulk enthalpy increments, not unverified absolute REFPROP/CoolProp reference equality.

**Bishop-specific restriction:** original x/D spatial interval 30–565 excludes **166** of 2,318 baseline-eligible stations. Thus Bishop scores use **2,152 stations**; Jackson–Hall uses **2,318**. Both correlations are extrapolated from their published flow conditions to horizontal near-critical sCO₂. A like-for-like comparison should use the same 2,152 stations, not compare naive overall figures on different subsets.

## Direct numerical results

**Pointwise MAPE, lower is better; source reduced local HTC is the target.**

| Evaluated expression | Measured wall T input? | n | All MAPE | Held-out MAPE | Bottom HB | Top HT |
|---|---|---:|---:|---:|---:|---:|
| H1a Gnielinski smooth forced convection | No | 2,318 | 150.15% | 158.10% | 87.71% | 236.81% |
| H1a Dittus–Boelter heating | No | 2,318 | 119.60% | 121.82% | 69.65% | 189.01% |
| **Bishop wall conditioned** | **YES** | 2,152 | 21.94% | 20.72% | 14.23% | 33.94% |
| **Jackson–Hall wall conditioned** | **YES** | 2,318 | 28.46% | 24.16% | 17.84% | 44.48% |
| **Bishop flux-driven wall inversion** | **NO** | 2,152 | **46.40%** | **39.72%** | 24.79% | 80.65% |
| **Jackson–Hall flux-driven wall inversion** | **NO** | 2,318 | **49.47%** | **43.16%** | 26.41% | 84.63% |

**Caution:** Measured-wall-conditioned 21.94% and 28.46% are **diagnostic values**, NOT independent predictive validation. The experimental HTC is itself derived from heat flux and measured wall-to-bulk temperature difference. The flux-driven modes hold the experimentally reported `q''` and derived bulk enthalpy fixed but solve wall T independently.

The flux-driven models remain **orientation-blind**: local top-wall MAPE is still very high (~81–85%). That means a single circumferentially uniform HTC should **not** be presented as valid for stratified sCO₂ horizontal heat exchangers.

## Deviation metrics and comparison coverage

| Metric | Bishop flux driven | Jackson–Hall flux driven |
|---|---:|---:|
| All-point MAPE | 46.4037% | 49.4698% |
| Mean signed bias | +37.2076% | +35.1829% |
| Median APE | 31.2815% | 27.4168% |
| 90th percentile APE | 120.6929% | 123.1989% |
| Run-macro MAPE | 47.7130% | 51.1883% |
| Nominal-family macro MAPE | 47.2946% | 50.9267% |
| Held-out sample count | 498 | 534 |
| Held-out mean signed bias | +35.5198% | +39.0421% |
| Fraction within source-reported 1-σ HTC (descriptive only) | 17.47% | 21.83% |
| Fraction classified `Ri>0.001` | 98.65% | 98.58% |

The **Richardson number** is calculated from density difference at the modelled wall T, inlet-pressure bulk density and measured mass flux, based on Theologou et al. Sec. 3.5. It is only a **buoyancy-risk diagnostic**. Neither Bishop nor Jackson–Hall includes an explicit buoyancy-induced angular temperature field.

On the **2,152 identical Bishop-eligible stations**: Jackson flux-driven MAPE is **52.14%**, versus Bishop **46.40%**. Across 18 equally weighted nominal families, Bishop is lower error in **12**, Jackson in **6**. The mean family-level difference (Jackson APE minus Bishop APE) is about **+7.03 percentage points**. A preliminary 10,000-replicate family-resampled percentile interval is approximately **−4.6 to +18.3 percentage points**; it crosses zero and is **not** measurement uncertainty or a formal externally validated confidence interval. See the deterministic paired audit script and published machine result for exact values. **Do not claim Bishop universally outperforms Jackson**.

### Four held-out nominal families (descriptive, not fitting)

| Original nominal family | Bishop flux-driven MAPE | Jackson flux-driven MAPE |
|---|---:|---:|
| `4MM_H*_77.5_10_20_30_A` | 39.89% | 8.84% |
| `4MM_H*_77.5_5_5_50_A` | 20.33% | 35.39% |
| `8MM_H*_77.5_40_30_90_A` | 60.86% | 79.77% |
| `8MM_H*_77.5_40_5_130_A` | 44.93% | 60.50% |

**This table uses each model's own allowed x/D subset.** It illustrates heterogeneity across physical conditions, not paired differences on identical stations. The full pointwise CSV and paired-audit report are the correct sources for matched-station inference.

## Independent physical-consistency check

At each source station we compared `q''/(Twall,measured - Tbulk,source)` with the experimentally reduced local HTC. The source data are virtually algebraically consistent; median absolute relative mismatch on the Bishop-eligible set is ~**8.1×10⁻⁸ percent** with mean ~**8.6×10⁻⁶ percent**.

**This is not independent experimental validation:** it confirms that the HTC and measured wall temperature share the same underlying reduced-data relation. This is why the low measured-wall-conditioned MAPE is not a prospective predictive result. The H1a CoolProp reconstruction reproduces the source's bulk temperature very closely under its explicit inlet/enthalpy alignment, but this does not establish instrument calibration, REFPROP–CoolProp property parity over the complete domain, or independent uncertainty covariance.

## Gates and limits

- **H1b equations and source pipeline:** passed mathematical tests and completed real-fluid CI evaluation.
- **H1b predictive model improvement:** clearly improved over basic forced-convection baselines, **but not satisfactorily validated**; 46–49% global MAPE and 81–85% top-wall MAPE remain substantial, with uncertain original fit applicability.
- **Experimental confidence:** no propagated instrument covariance, between-experiment instrumental biases, wall conduction inverse uncertainty or source-pressure variation.
- **Full industrial Brayton cycle:** not validated. These are 4/8 mm single horizontal heated tubes, **not** PCHE, installed recuperator UA or a CARBOSOLA rig.

**Next high-ROI direction:** physically justified mixed-convection/buoyancy *orientation-sensitive* closure with independent source calibration/validation and rejection outside its published regime. It should never infer a "buoyancy multiplier" by tuning on the full 54 experiments or by leaking measured wall temperatures into a priori predictions.
