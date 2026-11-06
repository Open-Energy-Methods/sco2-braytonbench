# WP5 — v1.0 release acceptance and independent evidence freeze

**Created:** 2026-11-06. **Status:** engineering candidate, review required; no tag, DOI or publication authorized.
**Current package identity:** `sco2-braytonbench 0.5.0a0`, BSD-3-Clause, Python `>=3.10` declared; CI checks Python 3.11 and 3.12. Version in `CITATION.cff` must match `pyproject.toml`.

## 1. Correct proposed scientific claim

The planned v1.0 is a **numerically verified, reproducible, openly auditable research software release** for a six-state recuperated CO₂ Brayton-cycle and finite-source waste-heat problems. It includes a bounded **synthetic thermal wall + quasi-steady cycle dynamic response** and a synthetic physically traced hot-gas bypass/PI demonstrator. The experimental-readiness package is a **proposed** measurement/uncertainty/validation protocol. Reported Stuttgart heat-transfer comparisons and earlier research comparisons remain limited to their actual documented evidence classes.

**v1.0 does NOT assert** experimental validation of the whole power cycle, CARBOSOLA-specific commissioning, correct transient CO₂ mass or pressure dynamics, turbomachinery speed/machine-map dynamics, hardware-calibrated UA/heat capacity/actuator, approved industrial controller, technoeconomic optimum, author-confirmed Kim Equation 24 or complete coverage of near-critical property uncertainty. Those are **explicit scope limitations**; their absence alone is not a reason to withhold a correctly described *research software* v1.0. Misrepresenting them is a release blocker.

## 2. PR ordering and independent review

Dependencies must be considered in exact order, **not accidentally reviewed as unrelated mergeable PRs**:

| Work package | Branch PR | Scope | Current integration requirement |
|---|---|---|---|
| WP0/1/2a | [#22](https://github.com/Open-Energy-Methods/sco2-braytonbench/pull/22) | release contract, numerical guards, analytic wall | review, full CI and merge into `main` |
| WP2b | [#23](https://github.com/Open-Energy-Methods/sco2-braytonbench/pull/23) | finite source, wall stored energy and quasi-steady cycle | review, then rebase/retarget onto resulting `main` |
| WP3 | [#24](https://github.com/Open-Energy-Methods/sco2-braytonbench/pull/24) | source mass bypass, mixing and PI | review, then rebase/retarget |
| WP4 | [#25](https://github.com/Open-Energy-Methods/sco2-braytonbench/pull/25) | candidate channels, safety and experiment/data readiness | review, then rebase/retarget |
| WP5 | stacked WP5 PR | release engineering, reproducibility evidence and acceptance dossier | review only after predecessors are integrated |

**All PRs are research/draft until independently reviewed.** A green CI, release branch or provisional document is neither scientific validation nor approval to merge. Kim H1d [PR #19](https://github.com/Open-Energy-Methods/sco2-braytonbench/pull/19) is experimental; published Eq.24 source ambiguity remains [Issue #20](https://github.com/Open-Energy-Methods/sco2-braytonbench/issues/20). The separate archived project report [PR #21](https://github.com/Open-Energy-Methods/sco2-braytonbench/pull/21) is a historical snapshot and must not be silently rewritten.

## 3. Automated numerical and packaging acceptance

A candidate commit must pass, **on the same final source SHA**, the following. Do not borrow a passing status from an older commit.

1. **Complete existing suites:** `pytest -q` on Python 3.11 and 3.12; distinguish optional CoolProp skips from real-fluid evidence.
2. **Actual EOS tests:** explicit real `CoolProp==8.0.0` jobs for property, steady-state fixed-UA/source, WP2b, WP3, and external-source references; do not infer EOS runs from a no-CoolProp `pytest`.
3. **Scientific fixtures:** exact analytical thermal CV, first-law/stored-energy closure, isothermal-wall/source-to-cycle constant-property limit, time-step refinement, fail-closed phase/pinch/root handling, source bypass mass/enthalpy and saturation/anti-windup/causality.
4. **Experiment-readiness honesty:** all 35 proposed channels and 13 prospective test cases remain unapproved/unconfirmed; actual measurement/calibration authorization unavailable; no mislabeled synthetic measurements; holdout/run provenance schema and input QC pass.
5. **Packaging:** build both wheel and source distribution from the same commit; verify CFF/version/SPDX consistency, LICENSE in wheel, named modules and input data/protocols/tests/examples/docs in the sdist. The **wheel** is an installable API package; standalone scripts/data are delivered with the **sdist/repository**, not misrepresented as installed executable entry points. **Exception:** the Mantilla 2010 NIST/TRC ThermoML 49-point density transcription is removed from current repository HEAD and all new source archives, pending [rights decision #27](https://github.com/Open-Energy-Methods/sco2-braytonbench/issues/27). Its provenance metadata is retained, and the measured-density test is explicitly opt-in with user-supplied data. Older Git history is still accessible and must be assessed separately.
6. **Fresh installation:** install wheel and sdist separately in fresh virtual environments; execute the same four deterministic synthetic scenario scripts from clean workspaces, using only the installed package plus checked-in example source/protocol files. Compare generated CSV and JSON structures, flags and all finite numerical values with stated tolerances.
7. **Machine-readable manifest:** capture full revision SHA from CI, Python/platform, package identity, SHA256 of distributions, source/fixture inputs and regenerated outputs. Dist/source archive checksums are integrity identifiers, **not** a claim that timestamp-bearing wheel/sgz bytes are bitwise reproducible across different builds.
8. **Failure diagnostics:** malformed CFF/metadata, missing or wrong-version archive, absent mandatory sdist file, forged measured-evidence classification, altered numerical output, unexpected CSV schema or nonfinite values must cause a nonzero exit.
9. **Report preservation:** CI attaches `release_gate_report.json`, `wheel_sdist_numerical_comparison.json`, wheel and sdist files, and newly regenerated synthetic CSV/JSON outputs. Do not commit build-dependent temporary outputs as golden measured data.

Build tool: `scripts/v1_release_gate.py`. It is designed to run **offline** and never calls GitHub release, Zenodo or DOI actions.

## 4. Manual independent reviewer checklist (unmet until signed)

These are independent release-governance decisions and **not satisfied by a script**:

- [ ] **Scientific basis:** independent reviewer examines the governing equations and source references, material/pressure/phase assumptions, energy accounting, test-derived result claims and limitations across steady and transient cases.
- [ ] **Negative evidence:** Stuttgart source ledger, fixed holdout design, STU-001 anomaly quarantine, matched-station comparisons and source-equation ambiguity are preserved, not rewritten as positive validation.
- [ ] **Data rights and attribution:** exact licenses, origin, redistributability, derived-data rights and complete authorship for every bundled source and validation fixture are verified. The `MANIFEST.in` expresses intended content, **not** consent to redistribute third-party materials. The Stuttgart Mendeley source is published under CC BY 4.0; Mantilla NIST ThermoML downstream permission is *unconfirmed*, tracked by #27. Its 49-point table is removed from current HEAD as well as excluded from the candidate sdist; opt-in experimental density tests are not run in CI without user-provided data, and history rights are unresolved.
- [ ] **API contract:** deterministic documented public interface, deprecation policy, supported ranges, user-facing errors and intended release version are reviewed.
- [ ] **Security/deployment:** check for secrets/private raw lab data, unexpected repository artifacts, unsafe auto-release actions and dependency licensing.
- [ ] **CITATION/Zenodo readiness:** author permission, version/commit identity, ORCID and licensing confirmed. Zenodo DOI concept/version relationships must be checked after actual repository release.
- [ ] **Full green final-head CI:** all jobs on the *same candidate commit* pass, including pinned real-CoolProp jobs and both fresh package installations.
- [ ] **Experimental nonclaims:** read each README, example, abstract and results page to ensure no unsupported plant or CARBOSOLA validation claim.
- [ ] **Formal review decision:** reviewer, review date, immutable commit SHA and waiver reasons are recorded for the release candidate. No self-approved tag based on an unreviewed script.

### Separate scientific limits, not release blockers if declared honestly

- No CARBOSOLA calibration or measured whole-cycle transient response.
- No CO₂ inventory, compressor/turbine shaft inertia, hydrodynamic valve or PLC safety system.
- Constant/hypothetical installed UA and lumped wall, synthetic PI gains, illustrative technoeconomics (if added later).
- Unresolved Kim Eq.24 interpretation excluded from the stable default claim.

## 5. Staged RC and v1.0 promotion

The following **has not happened** and is not automatic:

1. Review/merge #22 then #23 then #24 then #25, with conflict resolution and a new full CI after each integration as necessary. Review/merge WP5 last.
2. Confirm the precise v1.0 feature scope; consider whether Python `>=3.10` can honestly be advertised when automated validation is limited to 3.11/3.12. Add a 3.10 CI lane or narrow supported version metadata in an independently reviewed change.
3. Independently review data licenses and model evidence; resolve all *required* scope, attribution and distribution blockers. Leave optional experimental research in experimental modules.
4. Change version **together** in `pyproject.toml` and `CITATION.cff` to a `1.0.0rc1` RC (PEP 440), decide tag spelling `v1.0.0-rc1`, then review/approve a release branch at the exact target SHA.
5. Run all software + real-fluid + package + provenance jobs on that same candidate commit, record evidence and a written reviewer decision, and issue an immutable RC tag **only after success**.
6. If acceptance holds, set version `1.0.0`, rerun everything, publish release notes and GitHub tag, attach the exact source/wheel distributions and manifest, and optionally archive the resulting immutable release through Zenodo. Never replace numerical validation evidence with a link to a DOI.

### Critical stop rule

**A software pass is not permission to publish.** WP5 tooling always reports tag/Zenodo promotion as *not authorized*; only a separately documented independent review and an explicit user-directed release action can authorize a version/tag/DOI. Do not change the current `0.5.0a0` value or publish anything while those gates remain open.

## 6. Reproduce the WP5 software gate

The repository CI workflow `.github/workflows/ci.yml` includes a dedicated WP5 job. Locally:

```bash
python -m pip install 'build>=1,<2'
python -m build --sdist --wheel
# Create separate clean installations for wheel and sdist and execute all
# four synthetic scripts in separate workspaces, as in GitHub Actions.
python scripts/v1_release_gate.py compare \
  --reference /path/to/wheel-workspace \
  --candidate /path/to/sdist-workspace \
  --out evidence/generated/v1_wp5/wheel_sdist_numerical_comparison.json
python scripts/v1_release_gate.py audit \
  --root . --dist dist \
  --out evidence/generated/v1_wp5/release_gate_report.json
```

Machine artifacts are not lab results. In particular the WP4 audit's **0 approved measured-validation cases** is the correct result for the provided incomplete rig information.

## 7. Acceptance log

| Field | Current |
|---|---|
| Software release version | `0.5.0a0` |
| Release-candidate tag | **Not created** |
| GitHub release / Zenodo record | **Not created for this WP5 stage** |
| Independent scientific review | **Pending** |
| Source data redistribution review | **Pending** |
| Experiment and facility approval | **Not obtained; not required for an explicitly synthetic software claim** |
| Full integrated-main v1.0 gate | **Open** |
| Approver and signed acceptance SHA | **Not assigned** |

Update this log only with actual verified evidence, not estimated completion.
