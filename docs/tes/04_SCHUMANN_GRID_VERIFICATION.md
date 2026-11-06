# TES-v0.3 — Grid, temporal and Schumann-step verification

**Files:** `src/sco2_braytonbench/tes_schumann.py`; `tests/test_thermal_storage.py`; `scripts/tes_schumann_convergence.py`.

## Independent evidence hierarchy

1. **Continuum analytical model:** the Laplace/Poisson-series reference solves the ideal Schumann equations for a step in inlet temperature and equal initial uniform fluid/solid temperatures, with a pore-advection delay. It does not reuse the numerical solver's stencil or integrator.
2. **Finite-volume model:** two-temperature first-order upwind/SSPRK3 simulation with conservative flux accounting.
3. **Direct limiting checks:** Hv=0, mdot=0, uniform state and reverse flow independent of the complex benchmark.
4. **Grid study:** N=16,32,64,128 at held benchmark conditions; exact outlet reference and internal solid reference.
5. **Time study:** held N=64 and maximum solver steps 0.2, 0.1, 0.05, 0.025 s.

The Schumann outlet has a characteristic discontinuity at the pore transit time. Numerical diffusion smears this front in a coarse-cell representation; do **not** assert uniform pointwise convergence precisely on the advancing discontinuity. Comparisons at t=30 s are separated from the transit boundary.

## Sanity check independent of the committed finite-volume code

An independent scipy sparse-matrix exponential evaluation of the *linear semi-discrete* 2N+1 ODE for the synthetic case obtained outlet errors approximately 2.6845 K, 1.3442 K, 0.6719 K and 0.3358 K at N=16,32,64,128, respectively, against the Poisson-series continuous analytical outlet. At the centre solid cell the respective approximate errors were 3.9273 K, 2.1177 K, 1.0987 K and 0.5595 K.

**These are a separately calculated mathematical check**, not the exact committed SSPRK3 output nor experimental storage measurements. The authoritative actual-run values come from the dedicated TES GitHub Actions artifact and must be accepted only after its execution passes. The comparison is deliberately not calibrated to an external error target; every error is reported.

## Reproduction

Run:

~~~bash
python -m pip install -e '.[test]'
python -m pytest -q tests/test_thermal_storage.py
python scripts/tes_schumann_convergence.py --out evidence/generated/tes_v03
~~~

Generated files:

- `tes_grid_convergence.csv` — N, outlet and centre solid numerical/reference temperatures, errors K and percent span, energy closure, substeps, Courant and interphase factors.
- `tes_temporal_sensitivity.csv` — N=64 absolute continuous reference error under timestep refinement, with first-law closure.
- `tes_verification_manifest.json` — SI inputs, synthetic evidence classification, numerical summary and SHA256 hashes of both CSV files.

The script fails on nondecreasing spatial error, rather than reporting its output as a successful verification. The four N values are not “four experimental replications”; all are discretisations of the same synthetic PDE case.

## Gate

**TES-v0.3 may be called numerically verified only if:** all dedicated tests pass; the convergence script completes on the PR head; full first-law errors remain within the documented floating-point tolerance; and a reviewer confirms that the source form and boundary/initial conditions were not changed to force an artificially favorable comparison.

A mathematical verification against Schumann is not validation against CIC energiGUNE, HZDR, molten-salt storage, high-pressure CO₂ hardware or an operating thermocline rig.
