# G1-E / G2 Verification record — 2026-11-05

## Published CO2 property points

NIST REFPROP 9.1 User's Guide (Lemmon, Huber and McLinden,
2013), printed p. 18, shows a CO2 property table at **293.15 K**:
https://www.nist.gov/system/files/documents/srd/REFPROP9.PDF

| Pressure (MPa) | Density (kg/m3) | h (kJ/kg) | s (kJ/kg/K) |
|---:|---:|---:|---:|
| 5 | 140.65 | 432.38 | 1.8051 |
| 6 | 782.65 | 254.28 | 1.1811 |
| 7 | 808.60 | 249.95 | 1.1621 |
| 8 | 827.71 | 246.91 | 1.1475 |
| 9 | 843.17 | 244.58 | 1.1355 |
| 10 | 856.31 | 242.51 | 1.1251 |

Tests compare density directly and enthalpy/entropy **differences**
relative to the 8 MPa point (to avoid reference-state ambiguity).
The quoted rounded REFPROP output is **calculated reference data**,
not measured experimental evidence.

Additional NIST-derived near-pseudocritical density values from Hiroshima
University High Pressure Fluid Properties Laboratory are used as
coarse, independently published look-up comparisons:
https://highpres.hiroshima-u.ac.jp/supercritical-co2-properties/

For independent thermodynamic sanity, the suite also checks
`cp = (dh/dT)_p`, `cp/T = (ds/dT)_p`, isentropic state inversions
and positive entropy generation in nonideal turbomachinery. These checks
demonstrate backend self-consistency, **not agreement with independent
measurements**.

CI run 41991114530 passed 30 separate tests across the NIST
comparison, phase-sensitive states and one source-mapped FR2016
real-CO2 conceptual cycle using **CoolProp 8.0.0 / Python 3.11**.
Detailed numerical run evidence:
https://github.com/Open-Energy-Methods/sco2-braytonbench/actions/runs/41991114530

## First Friedman-Rapp benchmark comparison

A twelve-point conceptual-cycle solver based on Friedman & Rapp
(2016), **Figure 2b and Table 2**, uses the 30-segment
internal pinch-limited recuperator and accounts for all published
piping and component pressure losses. The initial comparator
interprets `T_low` as paper point **7** and `P_low` as paper point
**8**, which is plausible from the schematic but not identified
as a unique source EES boundary condition.

| Quantity | Paper Table 3 | Conceptual comparator |
|---|---:|---:|
| External heat input (MW) | 100.20 | 100.20 (normalization) |
| Turbine power (MW) | 38.080 | 38.153 (normalized) |
| Compressor power (MW) | 13.650 | 13.798 (normalized) |
| Cooler (MW) | 75.80 | 75.846 (normalized) |
| Net (MW) | 24.430 | 24.354 (normalized) |
| Efficiency (%) | 24.381 | 24.306 |

**Difference in thermal efficiency: -0.0754 percentage points.**
Net shaft-power difference after normalization: -0.0756 MW.
The model's specific energy residual is `5.82e-11 J/kg`,
within floating-point precision at the chosen state.

Note: the power numbers are not independent absolute size
predictions; all model powers have been scaled to **exactly
100.20 MW imposed heat input**. The comparison does **not** identify
the original paper's compressor turbine, motor/generator or additional
detailed EES hardware. A numerical agreement may arise despite
non-equivalent plant models.

The 2026-11-05 CI artifact includes all 12 CO2 thermodynamic
states, source parameters and diagnostics:
https://github.com/Open-Energy-Methods/sco2-braytonbench/actions/runs/41991114530/artifacts/13397788214

A subsequent sensitivity script (see `scripts/fr2016_sensitivity.py`)
investigates 15/30/60 recuperator sections and low-pressure/
temperature perturbations; it must not be called the original
paper's parametric optimization.

## Reference-model scope and future EOS

CoolProp uses the 1996 **Span–Wagner** equation of state. NIST
published an alternative CO2 fundamental EOS in February 2026:
https://www.nist.gov/publications/alternative-fundamental-equation-state-fluid-carbon-dioxide

This is a future independent-model comparison candidate. Its
published improvements near the critical region are **not yet
implemented or validated in this repository**.

## Stage gates

- **G0 source provenance:** substantial progress on Figure 2b/Table 2;
  original Figure 4 EES states and assumptions still unavailable.
- **G1-A algebra:** passed on prior fixture/CI tests.
- **G1-E property verification:** **PARTIAL reference agreement
  established (CoolProp 8.0.0)**. Closure requires larger
  independent TP/PH/PS tables, boundary/uncertainty tests and
  independent critical-region reference models or measurements.
- **G2 FR2016 cycle reproduction:** **OPEN**. Published aggregate
  agreement is encouraging but topology and source boundary
  conditions are not uniquely identifiable; no full EES replication.
- **G3-G6:** open as documented in `docs/RESEARCH_STATUS.md`.

## Extension with independent measured densities

A new **experimental** source is the Mantilla et al. 2010 CO₂
`(P,ρ,T)` dataset, DOI [10.1021/je1001158](https://doi.org/10.1021/je1001158).
Its 49 observations were recovered as machine-readable NIST ThermoML data,
rather than digitized from a graph.

The first CoolProp 8.0.0 comparison (GitHub Actions
[41993477851](https://github.com/Open-Energy-Methods/sco2-braytonbench/actions/runs/41993477851))
yielded mean bias **−0.0056077%**, RMS **0.0347305%** and maximum
absolute residual **0.0902414%**. It spans four isotherms
310–450 K. This provides experimentally grounded confidence in
**density**, though it is not a measured (h/s/c_p) validation
and does not certify the immediate critical singular region.

A separate four-case T7/T8, P7/P8 labelling sensitivity exercise
shows a **0.01510 percentage point** efficiency range. T7 and
compressor suction P8 are grounded in the conceptual paper;
other labels are counterfactual index-misassignment sensitivity.
Unreported Figure 4 detailed EES component states still bar
full source-model reproduction.
