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
- A second CI run **41991703407** passed **64 analytic-fixture tests**
  (4 optional CoolProp modules skipped in the fixture jobs) and
  **46 real-fluid reference/consistency checks** in the dedicated
  CoolProp 8.0.0 job. Its 12-state diagnostic and sensitivity JSON
  are available as reproducible Actions artifacts.
- At the chosen FR2016 point, increasing HX segments 30->60
  changed calculated efficiency by **0** at printed precision,
  while inferred recuperator UA increased **0.037%**.
  Imposed effectiveness and a terminal-limited Qmax can make duty
  segment-insensitive; this is **not universal grid independence**.
- A +/-1 K shift of T_low changed efficiency from
  24.4834% to 24.1216% (baseline 24.3058%). This assumption
  sensitivity exceeds the 0.0754-percentage-point paper difference.
  See `docs/FR2016_COMPARISON_REVIEW.md`.
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

## Independent measured-density validation (GitHub Actions 2026-11-05)

The source-curated `data/reference/mantilla2010_thermoml_density.csv` includes
**49 directly measured pure-CO₂ densities** from Mantilla et al. (2010)
at 310/350/400/450 K, spanning approximately 1–160 MPa. Unlike the
older REFPROP-versus-CoolProp tests, this is experimental validation
**of density only**.

The real-fluid CI job on [run 41993477851](https://github.com/Open-Energy-Methods/sco2-braytonbench/actions/runs/41993477851)
passed **61 tests**. Both fixture-only Python jobs passed **73 tests**
and skipped 5 optional CoolProp modules.

- Mean density residual: **−0.005608%**
- RMS relative density residual: **0.034731%**
- Maximum absolute relative density residual: **0.090241%**
  (among the 49 recorded conditions).
- Per-temperature maximum residuals: 310 K **0.04660%**;
  350 K **0.02784%**; 400 K **0.06498%**;
  450 K **0.09024%**.

The regression-screen thresholds have been tightened to **0.2% maximum**
and **0.1% RMS** based on this first clean baseline. They are test
thresholds, **not** physically derived measurement uncertainty bounds.
Independent validation of enthalpy, entropy and heat capacity is
still outstanding, particularly in the closest near-critical region.

## Original source-model identifiability

The FR2016 default `T7/P8` mapping remains source-supported.
Deliberately relabelling the low-side pressure and/or temperature
to adjacent states produces a conceptual-cycle efficiency range
**24.2907–24.3058%** (spread **0.01510 percentage points**).
These are **counterfactual mapping tests**, not equally credible
interpretations of the authors' paper. They do not recover the
Figure 4 EES plant's compressor-turbine branch, full state table
or missing performance maps.

See `docs/EXPERIMENTAL_DENSITY_AND_IDENTIFIABILITY.md`.

### Tightened regression confirmed

GitHub Actions [run 41993973281](https://github.com/Open-Energy-Methods/sco2-braytonbench/actions/runs/41993973281) **passed all three jobs** after the stricter density screens:
**73 passed / 5 CoolProp modules skipped** per fixture-only Python job; **61 passed** in the dedicated real-fluid job. Regression criteria `max absolute density residual < 0.2%` and `RMS < 0.1%` passed. The report contains measured and calculated densities and is retained in [the evidence artifact](https://github.com/Open-Energy-Methods/sco2-braytonbench/actions/runs/41993973281/artifacts/13398788849).

The worst observed density residual (0.09024% at 450 K and approximately 122.193 MPa) is larger than the paper's quoted <0.03% density uncertainty, despite lying within its reported ~0.1% high-pressure EOS discrepancies. A formal experimental uncertainty consistency test remains outstanding. This does not invalidate the density agreement, but prevents a stronger claim about uncertainty-limited accuracy.
