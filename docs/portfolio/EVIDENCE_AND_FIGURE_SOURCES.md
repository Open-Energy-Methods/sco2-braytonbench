# Evidence provenance — application portfolio research figures (8 November 2026)

**Purpose:** Numerical evidence chain for the three checked-in vector figures. All figures are original editorial visualizations of **synthetic** model calculations; they are not independent experimental measurements or published third-party plots. Source data CSV snapshots are small, losslessly transcribed/column-projected from machine-generated GitHub Actions artifacts (floating-point CSV values retained), and figure captions do not overwrite underlying evidence. Refer to the full original artifacts when auditing.

**Source software branch before this portfolio:** consolidated sCO₂-BraytonBench main 4b11fa48ee7ecd14a569a3afe82ddd79675e10f3, parent alpha 0.6.0a0. New app-facing version 0.7.0a0 modifies documentation and adds a *separate unvalidated conceptual piston component* without altering the original Schumann, TES-v0.4 and frozen v0.7 ROM numerical evidence.

## Figure 1. Independent continuum Schumann vs finite volume

- Figure: [01_schumann_grid_convergence.svg](figures/01_schumann_grid_convergence.svg)
- Data snapshot: [schumann_grid_20261108.csv](evidence/schumann_grid_20261108.csv); exactly four grid observations N=16/32/64/128, outlet and midpoint solid absolute errors K.
- Original Python 3.11 GitHub Actions run: [42447883665](https://github.com/Open-Energy-Methods/sco2-braytonbench/actions/runs/42447883665)
- Original artifact: [13604158225](https://github.com/Open-Energy-Methods/sco2-braytonbench/actions/runs/42447883665/artifacts/13604158225), member tes_grid_convergence.csv. **Original full CSV SHA256:** 2da67b495fae019fcb7d53907420d284661eabf6b90922df54350e91f66d7123.
- Original continuum condition: inlet 650 K, uniform initial 350 K, t=30s, area 1 m², length 1 m, porosity 0.4, mdot 40 kg/s, Hv 80000 W/(m³ K), synthetic constant fluid and solid properties. Actual outlet continuum value 487.80420119366613 K.
- No uniform convergence claim at the upstream pore-transit discontinuity. Graph y axis is **absolute temperature error K**, not energy residual or experimental fit.

## Figure 2. Synthetic charge/hold/reverse-discharge time history

- Figure: [02_tes_charge_hold_discharge.svg](figures/02_tes_charge_hold_discharge.svg)
- Data snapshot: [tes_stage_trace_20261108.csv](evidence/tes_stage_trace_20261108.csv), 28 consecutive stage-end observations with absolute times in seconds, outlet temperature K, solid SOC dimensionless and physically labelled stage.
- Original run: [42447883665](https://github.com/Open-Energy-Methods/sco2-braytonbench/actions/runs/42447883665).
- Original artifact: [13604701029](https://github.com/Open-Energy-Methods/sco2-braytonbench/actions/runs/42447883665/artifacts/13604701029), member synthetic_storage_stage_trace.csv. **Original full CSV SHA256:** e9ec5fa56fe570deee7e4ab071425069bce31dcbcb8e3d7a916dbaa3221bdc63.
- Original JSON synthetic_storage_summary.json: N=32, 140 s, charged energy 383146351.3393584 J, recovered energy 356164761.0774718 J, full-state return FALSE (48.060797 K max cell deviation), gross efficiency NULL. **Do not convert the partial recovered/charged ratio into cycle efficiency.**
- **Presentation processing:** Initial (t=0, T_out=350 K, solid SOC=0) is the declared initial condition; the 28 stage-end observations are unchanged. Lines are intentionally **segmented by stage**, avoiding interpolating the physical outlet jump at flow reversal. The diagram uses a second explicit axis for solid SOC; note its different units. The charge trace represents a different illustrative schedule than the separate N=96 operating window.

## Figure 3. Frozen surrogate heldout and OOD comparative error

- Figure: [03_frozen_rom_test_ood.svg](figures/03_frozen_rom_test_ood.svg)
- Data snapshot: [tes_frozen_holdout_20261108.csv](evidence/tes_frozen_holdout_20261108.csv). Four source RMSE rows; values reproduced at full original JSON precision. Synthetic ROM and conservative two-cell comparator, test (128 runs) and OOD (64 runs).
- Source GitHub Actions run: [42447883665](https://github.com/Open-Energy-Methods/sco2-braytonbench/actions/runs/42447883665), artifact [13604068966](https://github.com/Open-Energy-Methods/sco2-braytonbench/actions/runs/42447883665/artifacts/13604068966), member evaluation/tes_rom_holdout_report.json. **Original JSON SHA256:** c7615d7879d3ed2689fae6f3bc03fd757ed716b9e44b8da3dce6554c71f06bff.
- Source split is **256 training + 64 validation + 128 test + 64 OOD complete synthetic runs**. ROM was selected/frozen against validation only. OOD uses higher inlet temperatures 810–855 K and larger mass flows 0.105–0.15 kg/s than training, with declared other synthetic variation unchanged.
- Outlet RMSE plotted: test ROM 6.196479 K, test two-cell 15.091789 K, OOD ROM 14.252179 K, OOD two-cell 6.596487 K. The **negative OOD transfer** is an integral finding and the out-of-domain results were not used to retune this frozen model. The figure does not plot confidence intervals; none have been justified for real-world prediction.

## Figure integrity and reproduction

- SVG graphics are first-party, drawn from the three small CSV snapshots. No internet-hosted images, copyrighted source-article graphics or measured third-party data are included.
- The numeric source tables and the original upstream artifact IDs/full-file SHA256 are authoritative. No rendered pixel can override those values or create additional experiments.
- Verify the snapshot grammar, monotonic convergence, phase counts, held-out ranking, SVG metadata, protocol no-execution flags and first-law liquid-piston model with: python -m pytest -q tests/test_application_portfolio.py tests/test_liquid_piston_concept.py
- Source-generating programmes: ../../scripts/tes_schumann_convergence.py; ../../examples/tes_charge_discharge.py; ../../scripts/tes_surrogate_pipeline.py (the frozen model requires its documented, unaltered source-split and sealed-test process).
- Later changes to generated sources require a **new dated evidence cut-off, versioned data/plot update and CI run**. Do not quietly substitute different datasets under the same figures.

**Governance:** Existing historical third-party Mantilla density values remain excluded from current source/wheel/sdist, but historical Git/Actions redistribution rights issue #27 is open. Review #28 is also open; they do not affect the honesty of reporting internally synthetic figures, but do block formal parent-release certification.
