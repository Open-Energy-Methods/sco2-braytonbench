# G3.5 H1d — Kim (2019) CO₂ mixed-convection source-equation benchmark

**Stage:** component heat-transfer model implementation and Stuttgart extrapolation audit. **NOT** industrial equipment validation, original author's reported-error reproduction, or new model calibration.

**Source:** Kim, Kwon, Park, Park & Kim (2019), *International Journal of Heat and Mass Transfer* 131, 1117–1128, [DOI 10.1016/j.ijheatmasstransfer.2018.11.075](https://doi.org/10.1016/j.ijheatmasstransfer.2018.11.075). Exact Table 4 empirical/semi-empirical top/bottom coefficients checked against the original uploaded PDF and versioned in [source registry](../data/reference/kim2019_coefficients.json). Copyrighted paper **not** rehosted.

## 1. Original thermophysical formulation

At fixed source pressure, bulk-to-wall temperature averages use `Psi_av = integral(Psi(P,T)dT)/(Tw-Tb)`. For average cp use exact isobaric enthalpy difference, `cp_av=[h(P,Tw)-h(P,Tb)]/(Tw-Tb)`. Pinned `CoolProp==8.0.0` HEOS::CO2 properties are evaluated through cached P/T state calls, with 8-point Gaussian quadrature and segment splitting to capture nonlinear density, conductivity and viscosity.

```text
Re_b=G D / mu_b      Pr_b=cp_b*mu_b/k_b
beta_b=(rho_b-rho_av)/(rho_b*(Tw-Tb))
Q_b=beta_b*q''*D/k_b
Gr_q=g*beta_b*q''*D^4/[(mu_b/rho_b)^2*k_b]
```

Eq. (24) from the original PDF appears to put the empirical Reynolds and Prandtl corrections in a denominator:

```text
Nu_fc=c1 Re_b^0.8 Pr_b^0.4 * Q_b^n3/(Re_b^n1 Pr_b^n2)
      * (rho_av/rho_b)^n4 (mu_av/mu_b)^n5 (k_av/k_b)^n6
1/Nu_nc=c2 Gr_q^m1 Pr_b^m2 (rho_av/rho_b)^m3
      * (mu_av/mu_b)^m4 (cp_av/cp_b)^m5 (k_av/k_b)^m6
Nu_mixed=sqrt(Nu_fc^2+Nu_nc^2)
```

**Source ambiguity:** empirical Table 4 has negative `n1,n2`, e.g. top −0.50/−0.36. Applying the *printed* denominator literally implies `Nu_fc ∝ Re_b^1.3`; at representative dimensionless inputs (Re=10⁵, Pr=2, Qb=3, averaged density/viscosity/conductivity ratios 0.7/0.8/1.2), it produces **Nu_fc approximately 9.04 million**. Applying those negative exponents as a *numerator* correction produces **Nu_fc approximately 54.85**. The original paper's Fig. 10 and Table 6 are difficult to reconcile with the literal printed reading. **This does not establish an author typo or authorize a correction.**

Three explicit test variants are provided:
- `semi_empirical`: printed Eqs. 23/29 and semi-empirical Table 4 coefficients;
- `empirical_literal`: printed Eqs. 24/30 and empirical coefficients exactly as published;
- `empirical_hypothesis`: **unverified sign-placement interpretation** `Re_b^(0.8+n1) Pr_b^(0.4+n2)` with otherwise identical empirical coefficients; *not* an author-sourced implementation.

**Never silently combine the hypothetical sign interpretation with the source literal results.** Independent original 620-point reference data/code or an authorized correction would be needed for an original-paper numerical reproduction claim.

## 2. Experimental transfer domain is out of fit range

Kim's original POSTECH horizontal tube: **7.75 mm ID**, **0.91 m heated length**, inlet pressure **73.83–77.35 bar**, mass flux **52.1–250.5 kg/(m² s)**, heat flux **1.2–25.9 kW/m²**. Supplemental Adebiyi–Hall source heat flux extends to **26.9 kW/m²**. Original paper reports mean absolute deviations of **10.00% top and 10.44% bottom** for the empirical formulation on *its own* data, **not reproduced here**.

The Stuttgart data [DOI 10.17632/4mvk4nxrkz.1](https://doi.org/10.17632/4mvk4nxrkz.1), CC BY 4.0, use **4 and 8 mm** tubes, 54 experiments and reported fluxes starting at **30.55 kW/m²**; the anomalous 832.99-kW/m² experiment stays quarantined. **Every Stuttgart station exceeds both original Kim datasets' published maximum heat flux**. Therefore even apparently small predicted errors here can only be described as **out-of-fit-domain transferability evidence**, never validation within the original source range.

## 3. Numerics, holdouts and target leakage

Use original source-inlet-T anchored CO₂ bulk enthalpy increments (avoid assuming absolute REFPROP and CoolProp enthalpy references coincide), plus reported q'', P, mass flow and diameter. The exact H1a/H1b SHA256 four-family held-out partition is retained, no coefficients tuned; one entire anomalous source experiment is quarantined. Of 2,318 H1b eligible local points, only **790 HB bottom and 790 HT top** are considered; **738 HM middle points lack an original Kim equation and are withheld**.

Each variant is scored in two distinct modes: `measured_wall_conditioned` uses experimentally reported wall temperature (diagnostic only, **target-information leakage** because HTC is computed from q'' and Tw−Tb); `flux_driven_inverse` solves `q''=h_model(Tw)*(Tw-Tb)` with measured source q'' but **without measured wall T**. This is a conditional local prediction, not a full equipment simulation.

Root searches are finite/bracketed and enforce a separate heat-flux balance. Every excluded point has a reason. All comparison metrics report successful coverage, per-orientation/diameter and original held-out families, with **Jackson/Bishop/Gnielinski metrics on identical station IDs only**. Nominal-family bootstrap is between-group variability, not instrumental covariance or an external-domain confidence interval.

## 4. Reproduce

```bash
python -m pip install -e '.[test,co2]' 'CoolProp==8.0.0'
python -m pytest -q tests/test_kim2019_source_registry.py tests/test_kim2019_model.py
python scripts/stuttgart_h1.py
python scripts/stuttgart_h1b.py
for v in semi_empirical empirical_literal empirical_hypothesis; do
  python scripts/stuttgart_h1d.py --variant "$v"
done
```

The three variants run in a GitHub Actions matrix. Each uploads separate JSON and source-matched pointwise CSV. **CI passing does not prove physical adequacy.**

**Scientific gate:** source formulas implemented and auditable; original Kim published-error reproduction **OPEN** due to unresolved Eq24/Table4 ambiguity; all Stuttgart scores **extrapolation-only**; PCHE and Brayton-cycle industrial validation **OPEN**.
