# Dated research reports

This directory preserves substantial technical reports as **versioned research records**, not automatically updated software documentation. Every report states the Git revision and evidence cut-off to which its numerical and release-governance claims apply.

## Current consolidated report

**[6 November 2026 — Comprehensive Research, Engineering and Verification Report](2026-11-06/sco2-braytonbench-comprehensive-research-report.md)**

This is the authoritative *dated overview* of the integrated sCO₂-BraytonBench alpha software at main commit `8df1711a425e21da342bd3f401da61a1375bbc0a`. It includes:

- Scientific origin, six-state recuperated real-fluid cycle, finite industrial source screening, fixed-UA heater/cooler and property/mesh verification.
- Stuttgart H1a–H1c quantitative external reduced-data comparisons and the negative result, plus **unmerged** H1d Kim source-evaluation limits.
- Exact WP2a wall-storage thermal model, WP2b finite-source/wall/algebraic Brayton coupling, and WP3 mass-conserving source bypass with sampled PI.
- WP4 prospective instrumentation, data quality, uncertainty and identifiability; WP5 independent wheel/sdist numerical reproducibility.
- Explicit evidence grading, historical 49-point measured-density comparison versus current opt-in source-data policy, licence issues and release governance.
- Results traceability, integrated [20/20 GitHub CI](https://github.com/Open-Energy-Methods/sco2-braytonbench/actions/runs/42266275348), limitations, HZDR research relevance and a sequenced doctoral-research roadmap.

**Interpretation:** numerically verified alpha research software, **not** an experimentally validated CARBOSOLA cycle or industrial dynamic-control system. The project is still `0.5.0a0`; no v1.0 tag or DOI. Qualified independent reviewer signoff and historical NIST ThermoML redistribution rights remain open ([review #28](https://github.com/Open-Energy-Methods/sco2-braytonbench/issues/28), [rights #27](https://github.com/Open-Energy-Methods/sco2-braytonbench/issues/27)).

## Historical preservation

The original **5 November 2026** comprehensive G0–G3.5/H1d research report was proposed as [draft historical archive PR #21](https://github.com/Open-Energy-Methods/sco2-braytonbench/pull/21); it is not silently overwritten or claimed to be merged into the default branch. That earlier report captures source and CI status at its own evidence cut-off, before the subsequent WP0–WP5 integration.

Use a historical report for the scientific state **as of its cut-off**, and the new 6 November report for the current integrated 0.5.0a0 baseline. Later model changes or experiments require their own dated report and exact commit/run citations.

## Maintenance conventions

1. Never silently relabel a synthetic or author's calculated value as independently measured or validated.
2. Preserve original source anomalies and eligibility denominators; changes require an explicit erratum and reproducible rerun.
3. Cite the precise Git commit and CI workflow run for executed numerical claims.
4. Keep external datasets under their original licensing/attribution terms; the current software BSD-3-Clause does not relicense journal measurements.
5. Do not interpret an internally authored research report as independent qualified peer review. Independent acceptance is tracked separately from ordinary CI.
