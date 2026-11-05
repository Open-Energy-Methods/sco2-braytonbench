# FR2016 Conceptual Benchmark — Independent Numerical Review

**Date:** 2026-11-05  
**Software:** CoolProp 8.0.0, HEOS::CO2; Python 3.11 on GitHub Actions  
**Model:** Figure 2b conceptual 12-state recuperated cycle  
**Comparison class:** source-parameterized *model-to-model comparison*, **not reproduction of the full Figure 4 EES plant**  
**Gate status:** G1-E partial; G2 open

## Traceable inputs and modelling assumptions

Friedman and Rapp (2016), Figure 2b and Table 2, specify
`T1=550 K`, `P1=30 MPa`, turbine isentropic efficiency
`0.90`, compressor isentropic efficiency `0.85`,
recuperator effectiveness `0.925` and a complete pressure-drop
ledger of four component and six piping losses.

The paper's hypothetical Table 3 case gives normalized low
temperature `T_low/T_critical=1`, normalized low pressure
`P_low/P_critical=1.13`. Our **explicit mapping assumption** is
`T_low=T7` (pre-cooler outlet) and `P_low=P8` (compressor
inlet). Figure 4 shows additional compressor-turbine machinery
and unavailable EES state details. The full detailed plant
therefore cannot be reconstructed uniquely from the published
paper.

The model uses local real-fluid CO2 property calls and a
30-segment counterflow recuperator with internal-pinch-limited
effectiveness. Piping pressure losses are adiabatic
(isenthalpic) in the conceptual comparison.

## Source-to-model numerical comparison

| Metric | Table 3 published | Our conceptual calculation |
|---|---:|---:|
| Heat input (MW) | 100.200 | 100.200 (normalization) |
| Turbine output (MW) | 38.080 | 38.152614 |
| Compressor input (MW) | 13.650 | 13.798208 |
| Cooler rejection (MW) | 75.800 | 75.845593 |
| Net output (MW) | 24.430 | 24.354407 |
| Thermal efficiency (%) | 24.381238 | 24.305795 |

Our **specific** heater input is 243.809207 kJ/kg and specific
net shaft work is 59.259766 kJ/kg. The first-law residual of the
conceptual cycle is 5.82 × 10⁻¹¹ J/kg (floating-point rounding).
The base recuperator minimum approach is 5.12389 K.

**Difference:** −0.075442 percentage points in thermal
efficiency. However, MW values use the paper's 100.20 MW
imposed thermal input to normalize the model's specific works.
They are not measurements or independently sized installed
powers, and closeness of aggregates is **not sufficient** to
validate nonidentical cycle topologies.

## Segment refinement

| Recuperator segments | Thermal efficiency (%) | UA per kg/s (W/K) |
|---:|---:|---:|
| 15 | 24.305795 | 9384.950 |
| 30 | 24.305795 | 9398.771 |
| 60 | 24.305795 | 9402.247 |

At this point the efficiency remained unchanged at reported
precision, because recuperator effectiveness was imposed and
the maximum feasible transfer was not limited by a newly
resolved interior crossing. **This is not proof of general
grid independence across critical-region operating states.**
UA changed by around 0.037% between 30 and 60 segments,
and by about 0.184% between 15 and 60.

## Low-side condition sensitivity

| Variation | Efficiency (%) | Recuperator minimum approach (K) |
|---|---:|---:|
| Baseline | 24.305795 | 5.123890 |
| P_low × 0.99 | 24.305776 | 5.117904 |
| P_low × 1.01 | 24.308721 | 5.124557 |
| T_low − 1 K | 24.483395 | 5.098417 |
| T_low + 1 K | 24.121585 | 5.121063 |

The 2 K end-to-end temperature perturbation spans **0.3618
percentage points** of efficiency, exceeding the baseline
source comparison discrepancy (0.0754 percentage points).
Thus the selected low-side temperature boundary is a more
important modelling uncertainty than numerical segment
count for this operating point.

## Verification execution

CI run:
https://github.com/Open-Energy-Methods/sco2-braytonbench/actions/runs/41991703407

Machine-readable 12-state diagnostic and 7-case sensitivity
artifact:
https://github.com/Open-Energy-Methods/sco2-braytonbench/actions/runs/41991703407/artifacts/13398178456

- Analytic-fixture tests: **64 passed, 4 optional modules skipped**
  in the Python 3.11 test job.
- Dedicated CoolProp job: **46 passed**.
- Independent reference sources: NIST REFPROP 9.1 user guide,
  p.18, plus NIST-derived values published by Hiroshima University.
- These NIST numbers are calculated EOS outputs, not
  independently gathered physical measurements.
- CoolProp and NIST REFPROP share the original
  Span–Wagner (1996) thermodynamic formulation.

## Decision and next gate

**Retain the source-mapped conceptual comparator as a credible
literature consistency check. Do not designate G2 complete.**

Remaining:
1. Resolve low-pressure state mapping from source EES files or
   obtain additional tabulated state data.
2. Use a genuine source-faithful detailed Figure 4 implementation,
   including the compressor-turbine branch, before claiming full
   reproduction of Table 3.
3. Widen property comparisons beyond the currently available
   reference points and document near-critical and phase
   uncertainty.
4. Validate fixed-UA, off-design recuperator behaviour and
   demonstrate grid convergence at multiple operating points.
5. Independently benchmark the Mohagheghi–Kapat waste-heat
   system before extending to dynamics or PI/MPC.

**No HZDR/CARBOSOLA measurements were used.**
