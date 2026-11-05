# Kim et al. (2019): original source recovered and verified

**Status:** original full 12-page source PDF **obtained and inspected** on 2026-11-05. The source-recovery gate is CLOSED. **H1d source-equation implementations and out-of-domain Stuttgart comparisons have since executed. Original author's exact empirical Eq24 interpretation and original-data numerical parity remain OPEN.**

Citation: Tae Ho Kim, Jin Gyu Kwon, Joo Hyun Park, Hyun Sun Park and Moo Hwan Kim, *Heat transfer model for horizontal flows of CO₂ at supercritical pressures in terms of mixed convection*, *International Journal of Heat and Mass Transfer* **131** (2019), pp. 1117–1128. DOI: [10.1016/j.ijheatmasstransfer.2018.11.075](https://doi.org/10.1016/j.ijheatmasstransfer.2018.11.075).

Source PDF SHA-256: `8407a94d23a048cc8e3c1889296108b4da0d812bba6cd8ec91a13a3babb47651`. Verified via the uploaded **original published PDF**, including visual inspection of rendered **PDF pages 2, 4, 8, 9 and 10**. The article remains copyrighted by Elsevier: **the complete PDF is not rehosted** here.

The versioned [machine-readable Table 4 transcription](../data/reference/kim2019_coefficients.json) contains both original semi-empirical and empirical coefficient sets, with source location, domain restrictions and source-only original evaluation statistics.

## Exact model structure and coefficient origin

- **Eq. (24), PDF p. 8:** empirical forced-convection part `Nu_fc` modifies Dittus–Boelter `Re_b^0.8 Pr_b^0.4` with `Q_b`, Reynolds/Prandtl exponents, and integral-averaged density, viscosity and conductivity ratios. Orientation-specific values are given in **Table 4**, PDF p. 8.
- **Eq. (30), PDF p. 10:** empirical natural-convection component is written as **`1/Nu_nc`**, not `Nu_nc`; it uses `Gr_q`, `Pr_b`, and averaged/bulk density, viscosity, heat-capacity and conductivity ratios. Invert the equation when constructing `Nu_nc`.
- **Section 3.4, PDF p. 10:** mixed convection combines `Nu_fc` and `Nu_nc` by `Nu_mc = sqrt(Nu_fc² + Nu_nc²)`, **not** their sum.
- **Eqs. (23) and (29):** alternative semi-empirical forms. Table 4 contains their separately fitted coefficients; these MUST NOT be substituted into the empirical equations indiscriminately.
- **PDF p. 2 nomenclature:** the source distinguishes local bulk and inner-wall thermophysical properties, and integral-averaged properties from bulk to wall temperature. `Q_b=beta_b*q*D/k_b`, `Gr_q=g*beta_b*q*D^4/(nu_b^2*k_b)` with `nu_b=mu_b/rho_b`. The expansion coefficient `beta_b` is source-defined using the density difference between bulk and temperature-averaged state over `Ti-Tb`. Do **not** replace this definition silently with the density-at-film expression from the earlier Lei benchmark.

### Machine-transcribed **empirical** Table 4 coefficients

| Position | c1 | n1 | n2 | n3 | n4 | n5 | n6 |
|---|---:|---:|---:|---:|---:|---:|---:|
| Top | 1.14 | −0.50 | −0.36 | 0.54 | 0.83 | −3.48e−14 | 0.52 |
| Bottom | 0.11 | −0.15 | −0.41 | 0.26 | 0.54 | −4.12e−4 | 0.63 |

| Position | c2 | m1 | m2 | m3 | m4 | m5 | m6 |
|---|---:|---:|---:|---:|---:|---:|---:|
| Top | 7.05 | −0.30 | −0.55 | −14.64 | 3.52e−6 | −8.23e−11 | −5.35 |
| Bottom | 19.0 | −0.33 | −0.14 | −0.40 | 3.98e−6 | −3.55e−5 | −0.88 |

**Preserve tiny or very large exponents exactly**: e.g. the Table 4 top `n5=-3.48×10⁻¹⁴` and bottom `m4=3.98×10⁻⁶` are source values, not typographic mistakes to overwrite with attractive round numbers. Floating-point computation of tiny exponents is normally close to unity for finite positive property ratios; model-form sensitivity and conditioning must be tested separately.

## Actual original experiment and reuse limits

**PDF p. 4, Table 1 and Section 2.1:** POSTECH used a **7.75-mm ID**, **0.91-m heated length** horizontal stainless tube with a 100-mm upstream hydraulic entrance. Source inlet P varied **73.83–77.35 bar**, inlet T **24.50–30.07 °C**, `G` **52.1–250.5 kg/(m²·s)**, and heating flux approximately **1.2–25.9 kW/m²**.

**PDF p. 7, Table 3 / p. 10, Section 4:** a second dataset from Adebiyi and Hall adds conditions of 75.86–76.14 bar, inlet T 13.8–30.1 °C, G 104.34–391.91 kg/(m²·s), flux 5.1–26.9 kW/m². Original comparison uses **620 points: 495 POSTECH and 125 Adebiyi–Hall**, excluding `x/D < 10`.

**PDF p. 10, Table 6:** the paper reports its **own** empirical model mean absolute difference (MAD) **10.00% top**, **10.44% bottom**, and **8.71% top/bottom average**. Its semi-empirical model reports **21.73% top / 22.35% bottom**. It also reports the original Lei water-fit correlation **381.45% top / 115.79% bottom** on its *own* source evaluation; this supports the independent finding that Lei may transfer poorly to CO₂. However, it is **not** a reproduction of our Stuttgart H1c 1065.72% top / 197.73% bottom error, because domains, property treatment and data populations differ.

**DO NOT report 10.00% / 10.44% as achieved in BraytonBench.** This PR implements **no Kim equation**, tests no Kim numerical predictions and performs no Stuttgart comparison of Kim. The original coefficient equations can now be implemented in a new isolated H1d PR with independent arithmetic reference points, a constrained wall-T solve, the existing identical 4 nominal held-outs and matched-station comparisons.

Additional caution: the model uses temperature-averaged **near-wall properties** and must treat any **experimentally measured wall-temperature input** as a conditioned diagnostic, not an a-priori predictive result. Actual source training/validation independence cannot be inferred solely from Table 6.

## Source retrieval decision

- **Original PDF: RETRIEVED and visually checked.**
- **Original eqs. (23), (24), (29), (30), superposition and Table 4: VERIFIED and machine-transcribed.**
- **Original source fit region and published error table: RECORDED.**
- **Original paper full text: NOT redistributed.**
- **H1d numerical interpretation comparison and unchanged Stuttgart held-out scoring: EXECUTED, with substantial source-level ambiguity and poor out-of-fit-range performance. Exact original-study 620-point replication and in-domain validation: NOT YET DONE.**

This source audit is part of the release/integration provenance; scientific model work remains in [Issue #17](https://github.com/Open-Energy-Methods/sco2-braytonbench/issues/17).

### H1d implementation warning — printed Eq24 / Table4 consistency check

The subsequently implemented source-equation audit exposed a **potential internal inconsistency**: Eq.24 visibly places `Re_b^n1 Pr_b^n2` in the denominator but empirical Table4 specifies negative n1 and n2. A literal reading causes Nusselt numbers orders of magnitude larger than original Fig10 suggests, and >30 million% MAPE in the independent Stuttgart flux-driven transfer test. An alternative sign convention is separately tested as an **UNVERIFIED hypothesis**, not a published author correction or original-model reproduction. The exact source-vs-model distinction, root coverage and all experiment errors are documented in [H1d results](G35D_RESULTS.md). The original 620-point author dataset is still needed to establish parity. 
