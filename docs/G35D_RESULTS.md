# G3.5 H1d — executed Kim 2019 source-equation interpretation audit

**Results completed 2026-11-05, CoolProp 8.0.0 `HEOS::CO2`**.

Original paper: Kim et al., *International Journal of Heat and Mass Transfer* 131 (2019), 1117–1128, [DOI 10.1016/j.ijheatmasstransfer.2018.11.075](https://doi.org/10.1016/j.ijheatmasstransfer.2018.11.075). Original experimental test benchmark: Theologou et al. (2022), Stuttgart dataset [DOI 10.17632/4mvk4nxrkz.1](https://doi.org/10.17632/4mvk4nxrkz.1), CC BY 4.0. Code and exact source provenance in [H1d methodology](G35D_KIM2019_BENCHMARK.md).

[Initial successful 3-variant experimental computation — GitHub Actions 42053984073](https://github.com/Open-Energy-Methods/sco2-braytonbench/actions/runs/42053984073). Full independently generated CSV/JSON:
- [Semi-empirical, Eqs.23/29](https://github.com/Open-Energy-Methods/sco2-braytonbench/actions/runs/42053984073/artifacts/13429195215)
- [Empirical, printed Eq.24/30 literally](https://github.com/Open-Energy-Methods/sco2-braytonbench/actions/runs/42053984073/artifacts/13427848957)
- [Empirical, **UNVERIFIED** sign-placement interpretation](https://github.com/Open-Energy-Methods/sco2-braytonbench/actions/runs/42053984073/artifacts/13426784512)

## Source domain and unchanged experiment controls

Original Stuttgart intake: 54 experimental source IDs, 2,508 axial records, 2,398 reduced local HTCs. Earlier source heat-flux anomaly STU-001 whole experiment is still quarantined, original numerical source cell preserved. H1a/H1b provide 2,318 eligible observations. There is no published Kim middle-wall equation: **HB bottom 790 + HT top 790 = 1,580 candidate points**; HM 738 excluded by definition. **Four original held-out nominal experiment families remain unchanged; zero parameters fitted or retuned.** Metrics on successfully solved stations are reported with coverage, not silently projected to failed-root candidates.

Original Kim POSTECH q'' interval **1.2–25.9 kW/m²**, supplemental Adebiyi–Hall to **26.9 kW/m²**. Stuttgart q'' minimum among all 54 source experiments **30.55 kW/m²**. Consequently **1,580/1,580 candidate stations lie outside Kim's original heat-flux fitting envelope**, independently of interpretation. Kim POSTECH diameter was 7.75 mm while Stuttgart tubes are 4/8 mm. **These are extrapolation stress tests, not in-domain physical validation.**

## Numerical errors relative to experimentally derived local HTC

**Flux-driven wall-temperature inversion, measured wall T NOT supplied to the model:**

| Kim variant | Successful / 1,580 | Overall local HTC MAPE | HB bottom MAPE | HT top MAPE | Held-out MAPE |
|---|---:|---:|---:|---:|---:|
| **Semi-empirical, printed Eqs.23/29** | **1,573** | **52.56%** | 62.99% (790) | 42.03% (783) | **49.06%** (356) |
| **Empirical, printed Eq24 denominator and Table4 negatives** | **1,337** | **30,230,230%** | 46,604% (790) | 73,822,670% (547) | **24,407,695%** (298) |
| **Empirical, unverified signed-numerator hypothesis** | **1,522** | **43.90%** | 42.46% (783) | 45.44% (739) | **36.84%** (330) |

The enormous literal empirical overprediction **corroborates the unresolved original Eq.24 / Table 4 sign-placement inconsistency**. It does not prove exactly which alternative the original authors calculated. Treating the unverified 43.90% result as an authenticated reproduction would be wrong.

For context, **Jackson–Hall flux-driven** has ~**55.52% MAPE** on the original **1,580 HB/HT candidate** set, but exact fair contrasts require restricting Jackson to the exact successful Kim station IDs. The scripts supply these matched-station comparisons. The unverified sign hypothesis yields a **+14.43 percentage-point** mean advantage over Jackson when weighting each of the 18 physical nominal families equally on the **1,522 successfully solved** stations; a seeded 3,000-draw **between-family** bootstrap gives approximately **[+0.65, +30.45] pp**, but this excludes **58** failed-root points and **every point is out of Kim's source fit range**. It does not prove a universal improvement or an author's validated CO₂ model.

The printed semi-empirical form's matched-family comparison with Jackson gives approximately **+5.64 pp** advantage on its successfully solved subset, but its between-family bootstrap interval **crosses zero** (approximately −11 to +25 pp). Thus no decisive winner.

### Why conditioned scores are not independent predictions

The same formulas evaluated with **measured wall temperature** as an *input* gave:
- Semi-empirical **35.79%** MAPE on 1,580 points;
- Empirical literal **18,699,508%** MAPE on 1,580;
- Empirical signed-numerator hypothesis **21.32%** MAPE on 1,580.

These lower scores, where applicable, are **posterior diagnostics with experimentally derived target-associated wall temperature**. Since the source HTC itself is obtained from q''/(Tw_measured−Tb), they do **not** measure predictive accuracy without target leakage. The flux-driven inversions use measured q'' and reconstructed bulk state but **never feed measured Tw to the solver**.

## Failure and numerical admissibility accounting

| Flux solver | Unresolved/failed of 1,580 | Breakdown |
|---|---:|---|
| Semi-empirical | **7** | root/heat-balance tolerance not reached |
| Literal empirical | **243** | no sampled unique physical root bracket |
| Unverified empirical interpretation | **58** | 45 unbracketed, 2 multiple observed brackets, 11 nonconverged |

No failed root is silently replaced by a default wall temperature or excluded from the source candidate count. The flux-driven solver enforces **0.2% relative wall heat-flux balance** and finite root width; its finite scan does **not mathematically prove global uniqueness**. A run may complete and still fail the physics validation gate. Where root failures produce selection effects, successful-point-only MAPE is potentially optimistic.

## Source-reconstruction warning and next acceptance gate

The original paper's Table 6 reports **10.00% top and 10.44% bottom** *on the authors' own source data*. This analysis has **not reproduced** those original errors, and has not recovered the authors' original coefficient fitting code or 620-point benchmark table. Printed Eq.24 with negative exponents generates enormous heat-transfer coefficients at ordinary near-critical Reynolds numbers; an alternative algebraic interpretation produces more plausible values but is **unverified**. Until an authoritative equation clarification or original study pointwise benchmark can reconcile the source, neither empirical interpretation should be promoted to a source-validated installed-UA correlation.

**Gate:** pure equation arithmetic + full Stuttgart conditional comparison **EXECUTED**; original-source empirical parity **OPEN**, complete in-domain original-fit validation **OPEN**, reliable top/bottom near-critical sCO₂ HTC prediction **OPEN**, industrial PCHE and Brayton-cycle UA validation **OPEN**.

No emails were sent; no new release, tag or DOI was issued.

## Exact three-way common-station robustness audit

The preliminary three-model summary above uses each model's successfully solved station subset; those MAPE values are **not a common-support ranking**. A further CI analysis intersects the exact successful `(experiment_id, axial_position_m, orientation)` station IDs across all three Kim variants, checks the source metadata and fixed original holdout grouping, and evaluates a **matched Jackson–Hall baseline on those same points**.

The reproducible CI artifacts are `common_station_comparison.md`, `common_station_comparison.json`, `common_station_comparison.csv`, and the audited `common_station_errors.csv`. This removes unequal-subset comparison from the matched comparison but **does not repair nonrandom failed-root exclusions**. Original Kim fit-domain overlap remains zero because of the published heat-flux ceiling. Published data from this audit are reported only when the revised CI workflow completes.

