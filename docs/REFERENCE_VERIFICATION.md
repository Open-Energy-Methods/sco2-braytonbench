# G1-E / G2 Verification record — 2026-11-05

## Independent published reference values

NIST's *REFPROP 9.1 User's Guide* (Lemmon, Huber, McLinden, 2013),
printed page 18 (in the manual's section 5.2) includes a carbon-dioxide
table at 20°C, with pressure, density, enthalpy and entropy:
https://www.nist.gov/system/files/documents/srd/REFPROP9.PDF

We transcribed a short subset for reference tests, with the units printed
in the table. The source is **REFPROP 9.1 software output**, not
independently measured experimental points.

| P (MPa) | Density (kg/m³) | h (kJ/kg) | s (kJ/kg/K) |
|---:|---:|---:|---:|
| 5 | 140.65 | 432.38 | 1.8051 |
| 6 | 782.65 | 254.28 | 1.1811 |
| 7 | 808.60 | 249.95 | 1.1621 |
| 8 | 827.71 | 246.91 | 1.1475 |
| 9 | 843.17 | 244.58 | 1.1355 |
| 10 | 856.31 | 242.51 | 1.1251 |

The tests compare density directly and **enthalpy/entropy differences**
relative to the 8 MPa row. Reference-state-dependent absolute h/s values
are deliberately not taken as a success criterion. The comparison has
conservative tolerances for the printed reference precision and possible
implementation differences; a mismatch triggers inspection rather than
automatic retuning.

A separate coarse near-critical reference comes from Hiroshima
University's high-pressure fluid-properties laboratory, which explicitly
identifies NIST Chemistry WebBook / Span–Wagner values as the basis:
https://highpres.hiroshima-u.ac.jp/supercritical-co2-properties/
These are rounded to 3 significant figures and **not independent
experimental measurements**.

## What a successful test means

CoolProp HEOS::CO2 (also using Span–Wagner thermodynamics) agrees
reasonably with tabulated calculations from a different implementation
of the same EOS. Property inversions, critical parameters and
near-pseudocritical sensitivity are sanity-checked. This does **not**
establish global EOS accuracy, measurement agreement, property
derivative fidelity at the critical locus or full Brayton-cycle validation.

The G1-E gate can progress to **partial reference agreement** after CI
records the exact installed CoolProp version and results. It remains
**open** pending a wider property domain, more independent state data,
uncertainty analysis and full cycle sensitivity tests.

## Friedman & Rapp (2016) comparison

The paper's Figure 2b provides a twelve-state **conceptual** cycle, while
its Figure 4 EES model includes a separate compressor turbine and other
plant-specific equations. Table 3 is an illustrative reactor coupled
to a CO2 cycle; it is **not a CARBOSOLA or waste-heat rig measurement**.

The source table states `T1 = 550 K`, `P1 = 30 MPa`,
`eta_c = 0.85`, `eta_t = 0.90`, `epsilon_recup = 0.925`, with
individual piping and exchanger pressure losses. The Table 3 case
gives the low temperature and pressure as critical normalized values
`T_low/T_crit = 1.0` and `P_low/P_crit = 1.13`.
The source diagram labels `T7` as the low temperature; the comparator
interprets low pressure as **point 8**. This is a **transparent mapping
assumption**, not a verified translation of the EES Figure 4 model.

Our comparator independently computes all 12 Figure 2b state
enthalpies and pressures and an internally conserved cycle using
CoolProp real CO2; it writes detailed outputs to a CI artifact.
The paper's published Table 3 provides the following rounded
aggregates (not exact state points):

- Heater input: 100.20 MW
- Turbine output: 38.08 MW
- Compressor input: 13.65 MW
- Heat rejected: 75.80 MW
- Derived net: 24.43 MW; derived efficiency: 24.3812%.
- Printed first-law residual: approximately -0.03 MW due to rounding.

**The absolute MW values from our source-mapped comparator are
normalized to 100.20 MW heater input only to make power ratios
comparable.** This does not infer a measured CO2 mass flow. No
published tolerance or replication pass/fail threshold exists, so
the diagnostic deliberately makes **no reproduction claim**,
even if the aggregate numbers happen to agree.

## Stage-gate status

- G0 source topology: substantially advanced, full proprietary EES
  topology and original state table still unavailable.
- G1-A analytic conservation: passed in earlier fixture tests.
- G1-E real CO2 reference comparison: **CI result required; open
  until logs and reference values inspected**.
- G2 source-reported cycle reproduction: **open**, since a
  twelve-point conceptual comparator is not the detailed EES plant.

Outputs in `evidence/generated` are transient GitHub Actions artifacts
and not automatically committed benchmark results.
