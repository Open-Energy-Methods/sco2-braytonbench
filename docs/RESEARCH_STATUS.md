# Research and verification status

Updated: 2026-11-05. **Pre-alpha research software — PR #1 remains draft.**

This independent repo is not an extension of HTHP-ControlBench
and is **not** a CARBOSOLA digital twin.

## Results to date

- Algebraic tests for pressure closure, energy conservation and
  heat-exchanger calculations have passed on an artificial
  constant-property fixture. **Those are not real-CO2 tests.**
- GitHub Actions run **41991114530** passed 30 real-fluid checks
  on CoolProp 8.0.0, including NIST REFPROP reference densities
  and h/s differences, near-critical density and a twelve-state
  source-mapped conceptual cycle.
- Friedman & Rapp (2016) Figure 2b, Table 2 conceptual comparison
  obtained `eta = 24.3058%` vs Table 3 `24.3812%`.
  The difference is `-0.0754` percentage points. Power comparison
  is normalized to the source's reported 100.20 MW heat input,
  **not** a separate determination of installed capacity.
- New CI tests check entropy generation and thermodynamic derivatives.
  A sensitivity report probes recuperator segmentation and low
  pressure/temperature assumptions. Results require CI inspection.
- Source Figure 4 EES turbine split, component maps and individual
  state data remain unknown; matching Table 3 totals is **not
  confirmation of an equivalent detailed plant model**.

## Literature provenance

- Friedman & Rapp (2016): 12-state conceptual Figure 2b and
  Table 2 pressure network reviewed; complete Figure 4 EES
  model not reproduced.
- Mohagheghi & Kapat (2014): finite waste-heat source and RC/RRC
  designs reviewed. REFPROP/GA optimum not reproduced.
- NIST REFPROP guide (2013): independent software-output reference
  values, not experimental measurement data.
- New alternative CO2 EOS by Lemmon, Harvey & Hellmann (2026):
  potential future sensitivity study, not implemented.

See `docs/REFERENCE_VERIFICATION.md` and CI artifact for
specific temperatures, pressures, provenance and limitations.

## Verification stage gates

| Gate | Status | Blocker |
|---|---|---|
| G0 original-source mapping | Partial | Detailed EES state table |
| G1-A analytic conservation | Passed local and CI | Retain regression tests |
| G1-E CO2 real-fluid | **Partially verified** | Larger independent data and edge regimes |
| G2 source-model reproduction | **Open** | Full source-model identifiability |
| G3 source gas recovery | Partial prototype | Full real-fluid/finite-UA verification |
| G4 transient plant | Not implemented | Mass and energy inventory dynamics |
| G5 PI/MPC | Not implemented | Physical actuation and safety |
| G6 economics | Not implemented | Grounded cost and sizing assumptions |

No experimental sCO2 test-rig experience or CARBOSOLA-specific
measurements or geometry is claimed. The repository is a fresh
reconstruction; the previously referenced v0.5 archive was not
available for direct import.
