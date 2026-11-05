# Research and verification status

Updated: 2026-11-05. **Pre-alpha research software.**

This is a fresh, independently structured repository. It is not a copy of HTHP-ControlBench, and it is **not** a CARBOSOLA digital twin.

## Provenance and scope

- **Friedman & Rapp (2016):** the pressure-loss labels in Table 2 and Figure 2b have been visually reviewed. The repository reconstructs a 12-point **pressure network only**; the original authors' detailed EES plant uses additional elements. The reference model has **not** been reproduced numerically.
- **Mohagheghi & Kapat (2014):** the RC/RRC topology and finite exhaust-gas heat supply were visually reviewed. Their GA/REFPROP optimum has **not** been numerically reproduced. Plot readings are **not** benchmark truth data.
- **Analytic fixture:** constant-property ideal-gas fluid, used to test equations, signs, pressure closure, heat transfer and numerical procedures. It **must not** be described as real CO2 or as validation against either paper.
- **CoolProp:** an optional real-fluid interface exists; real-fluid state inversion and cycle integration await CI and independently referenced values.

## Gate register

| Gate | Current status | Requirement to close |
|---|---|---|
| G0 — literature provenance | **Partial** | Topology/parameter traceability, especially full paper state tables and equation-of-state reference |
| G1-A — algebraic invariants | **Local tests passed** | Stable CI on clean environments |
| G1-E — real CO2 EOS | **Open** | CoolProp property tests and external benchmark comparisons near criticality |
| G2 — fully coupled steady cycle | **Open** | Real-fluid convergence, source-paper quantitative comparison, energy/entropy checks |
| G3 — source waste heat | **Partial prototype** | Finite-UA source/inventory of constraints with verified parameter ranges |
| G4 — dynamic plant | **Not implemented** | Conserved states, thermal masses and valid time scales |
| G5 — PI/MPC | **Not implemented** | Physically credible actuators, safety limits and observer assumptions |
| G6 — TEA, modular variants | **Not implemented** | Credible design/economic boundary and uncertainty |

An optional EOS property smoke test alone **does not pass G1-E or G2**.

## Traceability limitations

No proprietary HZDR/CARBOSOLA data were used. No experimental sCO2 test-rig work is claimed. No test of the exact earlier v0.5 software package has been reconstructed from unavailable original artifacts.

The local test report in `evidence/` applies to the **new repository reconstruction** and must not be conflated with a previously reported 61-test experiment whose source files were not available for import.

## AI assistance

Design drafting and implementation received AI assistance and require human engineering review. Benchmark provenance, independent numerical tests and reproducibility are treated as release prerequisites.
