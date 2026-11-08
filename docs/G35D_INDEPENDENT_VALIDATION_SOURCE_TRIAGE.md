# G3.5-H1d — independent physical evidence and quantitative validation source triage

**Date:** 2026-11-05. **Status:** published external studies checked; **NO new independent pointwise Kim HTC validation claimed**. This is a source suitability and provenance assessment, not a new experimental benchmark.

## 1. TU Delft / Draškić et al. (2025) — qualitative independent physical constraint

M. Draškić, J. Westerweel and R. Pecnik, *The stability of stratified horizontal flows of carbon dioxide at supercritical pressures*, Journal of Fluid Mechanics **1012** (2025), A17, [DOI 10.1017/jfm.2025.10162](https://doi.org/10.1017/jfm.2025.10162), [open TU Delft repository record](https://repository.tudelft.nl/record/uuid:ab5dcd17-55d8-49fb-b5c1-673566b77974).

- **Published apparatus:** optically accessible **horizontal rectangular channel**, rather than Kim's uniformly wall-heated **circular tube**. The authors separately heat the **top or bottom surface**, with shadowgraphy and surface-temperature measurements.
- **Published conditions:** approximately **88.5 bar**, **32.6 °C** inlet; the related experimental summary describes vertical imposed heating up to approximately **12.0 kW/m²**, and bulk Richardson numbers up to approximately 100. The published channel experiments are not the same as heating a complete circular tube and reading top/bottom generatrices.
- **Reported mechanism:** bottom heating creates unstable stratification with thermally driven plumes and stronger vertical mixing; top heating creates stable stratification and suppressed vertical turbulent transport. These are qualitative physical findings suitable for checking a model's orientation-dependent interpretation.
- **Data availability at this review:** open paper and supplementary **movies** were located. An independently ingestible pointwise numerical table with all `P,G,q'',D,Tb,Twall,HTC` and uncertainty metadata has **not** been verified. Values should not be manufactured from a chart or supplementary movie.

**Decision:** include as **independent physical context only**. Do not feed rectangular-channel surface-temperature values into the circular-pipe Kim `HB/HT` equations or count them as Stuttgart-independent MAPE. An encouraging top/bottom trend does not establish numeric agreement.

## 2. Cheng, Wang & Xu (2024) — promising circular-tube cross-domain candidate

Liangyuan Cheng, Qingyang Wang and Jinliang Xu, *Supercritical heat transfer of CO₂ in horizontal tube emphasizing pseudo-boiling and stratification effects*, International Journal of Heat and Mass Transfer **220** (2024), 124953, [DOI 10.1016/j.ijheatmasstransfer.2023.124953](https://doi.org/10.1016/j.ijheatmasstransfer.2023.124953).

The published study reports a **10.0-mm circular horizontal tube**, pressures **7.531–20.513 MPa**, mass flux **496.7–1346.2 kg/(m² s)**, heat flux **97.4–400.3 kW/m²**, and non-monotonic wall temperatures with **both positive and negative** bottom-minus-top differences.

Compared with Stuttgart (4/8-mm, approximately 7.75 MPa, original published heating about 30–130 kW/m²), the **tube geometry is more comparable** than Delft's one-sided heated rectangular channel, but physical regimes and heat flux are still well outside Kim's original maximum of 26.9 kW/m². This study also discusses wall conduction, pseudo-boiling interpretations and stratification, making an implicit convection-only wall model a potentially incomplete description.

**Data status:** a journal article and an openly reachable author-hosted article copy have been identified. **No confirmed licensed machine-readable raw top/bottom station dataset** was established in this audit. Do not create artificial records, infer experiment uncertainty or claim numeric validation on the basis of its abstract alone.

**Decision:** prioritize for **future quantitative external validation only after pointwise metadata and reuse rights are actually verified**. Do not calibrate Kim coefficients on Stuttgart to improve scores.

## 3. Xie, Gong & Wang (2025) — later circular-tube literature

X. Xie, J. Gong and J. Wang, *Experimental investigations on heat transfer to highly buoyant sCO₂ flows in a large horizontal tube*, International Communications in Heat and Mass Transfer (2025), [DOI 10.1016/j.icheatmasstransfer.2025.108725](https://doi.org/10.1016/j.icheatmasstransfer.2025.108725).

Published research addresses strong buoyancy and large horizontal-tube heat transfer. A usable full pointwise top/bottom numerical dataset, geometry/boundary conditions, original correlations and license **have not been verified** in this review. This is a **source candidate, not a benchmark**.

## 4. Acceptance checklist for any future external experiment

For an independent *quantitative* validation, record the **exact original dataset and license**, experiment ID, pressure, mass flow or mass flux, tube diameter, axial locations, reported heat flux with its area convention, inlet/bulk thermodynamic state, local **inner-wall** or appropriately corrected wall temperature, separate top and bottom wall identities, and reported uncertainty/covariance. Verify that the heat flux and stationwise HTC reduction match the source rather than assuming them.

Run the frozen model and coefficients first. Then report:

1. Numerical coverage and every failed-root source station;
2. Pointwise and nominal-family HTC MAPE and signed bias, separately for top and bottom;
3. Matched Jackson/Bishop comparators on identical source stations only;
4. Applicability flags for the original Kim paper's pressure, mass flux, temperature, heat flux and circular-tube geometry;
5. Exact presence/absence of source-original pointwise data and whether author-study ~10% errors were independently reproduced.

In the absence of a verified machine-readable source, the **external quantitative validation gate remains OPEN**. Qualitative agreement with observed buoyancy mechanisms is not an adequate substitute.

## Research decision

Kim H1d is a **reproducible equation-interpretation and Stuttgart extrapolation stress test**, not a validated `HTC`/installed-`UA` model. Preserve the unchanged four Stuttgart holdout families and the STU-001 anomaly quarantine. The empirical Eq. (24)/Table 4 sign-placement ambiguity must remain exposed until an authoritative correction or original author data/code resolves it. No source emails, publication claims, release or DOI action at this gate.
