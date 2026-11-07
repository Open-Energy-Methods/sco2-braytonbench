# TES-v0.9 — Offline distribution, isolated installation and evidence replay gate

**Version semantics:** TES-v0.9 is an internal *milestone* of the TES extension, **not** a release of parent package v0.9 or v1.0. Parent package/CITATION.cff remain 0.5.0a0. This work makes no GitHub release, PyPI upload, Zenodo DOI, laboratory-access or experimental-validation claim.

## 1. Acceptance criteria

A TES-v0.9 pull request is eligible for merge only after:
1. At the exact PR-head SHA, the dedicated **3.10, 3.11, 3.12** Python matrix is green, including both clean wheel and clean sdist installations in *separate* venvs with **no editable install** and no source-tree imports.
2. For each interpreter, both distributions use exactly the same explicit numeric support versions: CoolProp 8.0.0, numpy 1.26.4, scikit-learn 1.5.2 and joblib 1.4.2. Transitive versions are recorded in the environment but the audit does not claim every downstream package is globally locked.
3. The built distributions contain the enumerated TES modules, corresponding scripts, independent tests, documentation and BSD license metadata. Wheel and sdist SHA256 digests and source commit are recorded. The copy of the Mantilla NIST ThermoML extracted 2010 density table (historical rights issue #27) is **not** in either archive; provenance YAML is retained. PDF and model pickle/joblib payloads are not shipped.
4. An installed-import origin gate checks that the package actually comes from the chosen venv, not the checkout.
5. The analytic Schumann step, full-fluid/solid charge-hold-discharge, single-pass ideal/real-CO₂ Brayton endpoint, solid/fluid capacity, grade-aware operating window and small local surrogate estimator produce matched wheel/sdist numerical observations. Comparison is strict for shape, Boolean, string, null, filenames and rows, and allows only finite numeric values with rtol 2e-9 and atol 2e-8.
6. A matching analytical FV grid table, temporal refinement table, charge/discharge trace and summary, and one-pass snapshot are replayed by **the sdist-bundled scripts/examples** (copied to source-free workspaces). These are independent of the synthetic installed probe's direct API checks.
7. A SHA256 manifest enumerates the exact seven declared per-environment evidence files, both distributions and the exact source Git commit. Verification fails if an artifact, archive, manifest schema or expected file set changes.
8. Failure injection tests reject unsafe traversal/duplicate archive paths, absent required modules, unauthorized extracted datasets and PDFs/serialized model payloads, missing/altered evidence, nonfinite/changed numerical CSV cells, changed categories and schema drift.
9. The original complete TES-v0.6 **512-trajectory** data and v0.7 frozen model/holdout/OOD results are untouched. The v0.9 smoke only trains its own small 96-row, deterministic *toy* local predictor to exercise the installed HistGradientBoostingRegressor/joblib interfaces. This does not rerun or alter holdout selection, assert the surrogate's OOD performance, or promote it to a conservative full-state ROM.
10. The existing project-wide full CI remains an independent exact-head requirement, even if the three TES-v0.9 matrix jobs pass.

These are *software integrity and numeric consistency* gates. Good replay is **not** experimental agreement or quantified model-form uncertainty.

## 2. Repository files

- scripts/tes_v09_installed_probe.py — isolated installed-version, module-origin, physic numerical scenarios, local trusted toy ML smoke; emits JSON.
- scripts/tes_v09_release_gate.py — required archive inventories, controlled redistribution exclusions, wheel/sdist replay comparison, digest manifest and tamper detection.
- tests/test_tes_v09_release_gate.py — failure injection, exact type and finite numerical comparison tests.
- .github/workflows/tes-v09-distribution-replay.yml — Python 3.10/3.11/3.12 source freeze/build → isolated installation → shipped examples and independent physics tests → compare/verify → archive.

## 3. Outputs

Workflow uploads a separate artifact per Python version, including the freshly built wheel and sdist and evidence/generated/tes_v09/tes_v09_release_manifest.json. The manifest contains:

- source SHA, both package archive SHA256 values, mandatory member audit;
- seven named synthetic scenario files per environment with SHA256;
- exact matched categorical/numerical scenario reports;
- declared comparison tolerances;
- explicit false flags for measured validation, cleared third-party redistribution rights, frozen holdout retraining, scientific reviewer approval and release authorization.

**Archive hashes are expected to differ across Python build versions** and possibly between separate builds because build metadata may vary. The software gate compares the **wheel vs sdist from one source commit, built once per Python-matrix cell**; it does not assume reproducible build bytes across independent machines.

## 4. Scope and rights

The model remains an idealized conservative constant-property packed bed connected through an **open, one-pass** HTF boundary to quasi-steady Brayton analysis; no closed TES→CO₂ gas loop, transient CO₂ pressure/mass inventory, real plant valve response or facility calibration is implied. The v0.7 surrogate smoke uses locally generated test vectors and a newly fitted temporary estimator, not any historical test/OOD samples.

A distribution-file scan proves **absence of the named uncleared copied dataset within the audited archives**, not that all licensing and research measurement rights have been resolved. Historical repository history, citations and hosted datasets remain subject to issue #27 and qualified legal/data-rights review. The provenance note is shipped without its underlying measurement table. The independent scientific/software human review in #28 is outstanding regardless of green automation.

An unresolved permission gate or lack of measured facility validation must remain visible. Software archive integrity by itself cannot authorize an industrial controller, safety-critical use or a v1.0 research release.

## 5. How to reproduce

CI workflow is the authoritative reproducible installation demonstration because it provisions new virtual environments and downloads pinned build/science dependencies. For developer checks before packaging:

~~~bash
python -m pip install 'pytest>=8,<10' 'build==1.2.2'
python -m pytest -q tests/test_tes_v09_release_gate.py
python -m build --wheel --sdist
python scripts/tes_v09_release_gate.py audit --dist dist
~~~

Do **not** run the installed replay from an editable checkout and call it isolated. For a clean installed reproduction, follow the CI steps: extract one freshly built sdist, copy only its scripts/examples/tests to an empty workspace, independently install its wheel and source distribution into distinct venvs, run the installed probe with --expect-prefix pointed to the venv, run packaged example scripts from the empty workspaces, and call replay/verify against the resulting artifact roots.

## 6. Release decision

TES-v0.9 may be marked *integrated* when **all exact-head workflow checks and manifest content** are verified and the PR merged. TES-v1.0 remains **blocked** until the agreed full scientific scope report, third-party rights issue #27, actual independent qualified reviewer identity/sign-off issue #28 and merged-main CI check are separately satisfied. Parent package stays 0.5.0a0.
