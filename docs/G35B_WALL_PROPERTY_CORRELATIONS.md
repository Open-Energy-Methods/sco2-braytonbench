# G3.5 H1b — Published wall-property sCO₂ heat-transfer comparisons

**Stage:** experimental component comparison. The 2022 Stuttgart source data are preserved under CC BY 4.0; we do not fit coefficients or change the existing four SHA256-selected held-out nominal families.

## Equations and scientific provenance

**Bishop (1964)**, reproduced as equation (15) by Theologou et al., *Energy* 254 (2022), 124171 [DOI](https://doi.org/10.1016/j.energy.2022.124171):

```
Nu = 0.0069 * Re_b^0.90 * Prbar_b^0.66
     * (rho_w/rho_b)^0.43 * (1+2.4*D/x)
Prbar_b = mu_b/k_b * [h(P,Tw)-h(P,Tb)]/(Tw-Tb)
```

Bishop was calibrated to **upward supercritical water**, at far higher pressures; the benchmark preserves the original spatial interval `30<=x/D<=565` but all horizontal CO₂ use remains **cross-fluid extrapolation**, NOT validated physical applicability. This correlation has no explicit top/bottom buoyancy term.

**Jackson–Hall** temperature-dependent property correction as compiled by Ye et al. (2022), *International Journal of Refrigeration* 140:57–69, Table 3 ([source PDF](https://ntnuopen.ntnu.no/ntnu-xmlui/bitstream/handle/11250/3038137/Ye.pdf?sequence=1)):

```
Nu = 0.0183 * Re_b^0.82 * Pr_b^0.5 * (rho_w/rho_b)^0.30
     * (cpbar/cp_b)^n

n = 0.4                                      when Tw <= Tpc, or Tb >= 1.2*Tpc
n = 0.4+0.2*(Tw/Tpc-1)                      when Tb <= Tpc < Tw
n = 0.4+0.2*(Tw/Tpc-1)*(1-5*(Tb/Tpc-1))   when Tpc < Tb < 1.2*Tpc and Tw>Tb
```

`Tpc` is located via an isobaric CO₂ `cp(T)` peak at each reported inlet pressure using pinned CoolProp 8.0.0. The displayed domain is the computational equation, **not a validated envelope for the Stuttgart geometry**. Axial pressure remains the inlet value, a stated approximation.

**Buoyancy diagnostic** from Theologou et al., section 3.5:

```
Ri = Gr/Re_b² = (rho_bulk-rho_wall)*rho_bulk*g*D/G²
```

`Ri>0.001` flags substantial buoyancy risk. Richardson is **only a diagnostic** and never changes either formula's heat-transfer coefficient.

## Critical separation of input leakage

The same Bishop and Jackson equations are computed in two modes:

- **Measured-wall-conditioned**: use experimentally derived local wall T as a correlation input. It is a posteriori, **not an a-priori prediction**. Experimental local HTC and wall T use correlated raw inputs.
- **Flux-driven inverse**: use the experiment's reported heat flux `q''` (not its measured wall temperature), its pressure, flow/geometry and measured-inlet-anchored bulk enthalpy increment. Solve `q'' = HTC(Tw)*(Tw-Tb)` for Tw. This is a prospective local HTC calculation **conditioned on measured source heat flux and bulk state**, not a whole-loop predictive model.

Source anomalies STU-001 and all 54 original experimental records remain unchanged; the quarantined run is excluded. The exact four held-out nominal families established in H1a are reused without refitting any coefficient or splitting axial points.

All scores record sample counts, per-run and nominal-family macro error, MAPE, signed bias, p90 error, HB/HM/HT, diameter and split. Within-reported-1σ figures are **descriptive only**: no covariance propagation, independent uncertainty, or coverage claim. Compare models on their **same eligible stations**, not on unrelated subsets.

## Verification and completion gates

`python -m pytest -q tests/test_stuttgart_h1b.py` verifies independent printed equations, the exponent's three regimes, thermodynamic wall inversion against an analytic synthetic fluid, Richardson definition and the untouched original experiment/split. The CI job regenerates H1a with CoolProp pinned at 8.0.0 and runs the full H1b real-CO₂ benchmark, uploading per-station CSV and JSON.

The 2022 authors report ~52% Bishop deviation under **their** method, not necessarily identical to ours. Do not claim replicated author statistics without source-aligned eligibility, thermophysical reference treatment and uncertainty review. Neither formula explicitly resolves circumferential buoyancy or establishes an industrial sCO₂ exchanger UA.

The first dedicated real-CO₂ run has completed; see [H1b executed results](G35B_RESULTS.md) and the [full machine archive](https://github.com/Open-Energy-Methods/sco2-braytonbench/actions/runs/42035909213/artifacts/13417234462). The result is a **partial improvement**, not a validated buoyancy-resolving model. **H1b accurate-prediction stage remains OPEN**.
