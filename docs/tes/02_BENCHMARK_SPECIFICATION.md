# TES-v0.3 — Schumann analytical inlet-step benchmark specification

**Evidence type:** independently derived *continuous-PDE mathematical* reference. Not direct experimental measurements.

## Fixed synthetic reference fixture

The bed is initially at Tf=Ts=T0=350 K. At t=0 the inlet fluid temperature steps to Tin=650 K and is held there. Flow goes from x=0 to x=L and all constitutive parameters are fixed:

| Input | Value | SI unit |
|---|---:|---|
| Bed length L | 1 | m |
| Bulk area A | 1 | m² |
| Porosity epsilon | 0.4 | — |
| Fluid rho | 1000 | kg/m³ |
| Fluid cp | 1000 | J/(kg K) |
| Solid rho | 2600 | kg/m³ |
| Solid cp | 800 | J/(kg K) |
| Interphase Hv | 80,000 | W/(m³ K) |
| Positive mass flow | 40 | kg/s |
| T0 / Tin | 350 / 650 | K |
| Readout time | 30 | s |
| N values | 16, 32, 64, 128 | cells |

The temperatures, heat-transfer coefficient and mass flow define an idealized benchmark, not a proposed operating envelope for any laboratory.

## Laplace/Poisson derivation

Define pore speed `u=mdot/(epsilon*rho_f*A)`, characteristic travel time `t_x=x/u`, reduced length `a=Hv*A*x/(mdot*cp_f)`, solid response rate `b=Hv/[(1-epsilon)*rho_s*cp_s]`, reduced retarded time `z=b*(t-t_x)` and normalized temperature `theta=(T-T0)/(Tin-T0)`.

For `t>=t_x`, Laplace-transform the solid equation in retarded time: `Theta_s=b/(s+b)*Theta_f`. Along the fluid characteristic, integrate the resulting x-equation to obtain

\[
\widehat\theta_f(x,s)=\frac{1}{s}\exp[-a\,s/(s+b)],
\qquad
\widehat\theta_s(x,s)=\frac{b}{s+b}\widehat\theta_f.
\]

Expanding `exp(-a)*exp(a*b/(s+b))` in its power series leads to the equivalent convergent representation:

\[
\theta_f=P\{\operatorname{Poisson}(a)\le\operatorname{Poisson}(z)\},
\quad
\theta_s=P\{\operatorname{Poisson}(a)<\operatorname{Poisson}(z)\}.
\]

Both normalized phases are zero for `t<t_x`. At `t=t_x` the fluid response has right limit `exp(-a)` and the solid response remains zero. At late times both approach one.

This Poisson comparison is a convenient independent evaluation of the Schumann Bessel-series solution **for these exact boundary conditions**. The evaluator in `tes_schumann.py` never calls the finite-volume model, and restricts `a<=35`, `z<=60` rather than claiming arbitrary special-function precision.

## Acceptance evidence

1. Compare finite-volume outlet `Tf_N` at t=30 s to exact continuum `Tf(L,30)`.
2. Compare the centre-cell solid temperature to exact `Ts(x_cellcenter,30)`. Its x-coordinate is the actual cell centre, not a hard-coded L/2.
3. Run N=16,32,64,128; report absolute and 300-K-range-normalized error and verify a decreasing refinement trend. First-order upwind numerical diffusion creates expected O(dx) error.
4. At N=64, independently vary the maximum RK timestep 0.2/0.1/0.05/0.025 s and record resulting outlet temperature and first-law residual.
5. Record actual RK substeps, Courant/exchange factors and SHA256 of both machine-generated CSV tables. Do not overclaim uniform pointwise convergence at the moving discontinuity.

```bash
python -m pip install -e '.[test]'
python -m pytest -q tests/test_thermal_storage.py
python scripts/tes_schumann_convergence.py --out evidence/generated/tes_v03
```

The script fails if the required main grid trend is not found. Until the actual CI run succeeds, every numerical error remains **unverified**; the script never supplies a hand-picked “validation percentage.”
