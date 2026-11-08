# Mantilla 2010 ThermoML — historical Git exposure and downstream data-rights audit

**Checked:** 8 November 2026. **Scope:** Open-Energy-Methods/sco2-braytonbench, specifically the 49-point extracted/normalized CO2 density file formerly stored at data/reference/mantilla2010_thermoml_density.csv.  
**Verdict:** Current main and tested wheel/sdist distributions **exclude** the measurement table. **17 of 29 current live branch tips still include it**, and the blob remains reachable via Git history. **No source-specific downstream republication authorization is established**. This is an evidence audit, **not a determination that copying scientific facts is inherently copyright infringement**.

## 1. Primary provenance and licensing evidence

- The original paper is **Ivan D. Mantilla, Diego E. Cristancho, Saquib Ejaz, Kenneth R. Hall, Mert Atilhan and Gustavo A. Iglesias-Silva**, *P-ρ-T Data for Carbon Dioxide from (310 to 450) K up to 160 MPa*, *Journal of Chemical & Engineering Data*, 55(11), 4611–4613 (2010), DOI https://doi.org/10.1021/je1001158 . The ACS article page identifies © 2010 American Chemical Society. Earlier repository metadata **omitted two coauthors**, now corrected.
- NIST TRC ThermoML original record: https://trc.nist.gov/ThermoML/10.1021/je1001158.html . Archive DOI: https://doi.org/10.18434/mds2-2422 .
- The NIST archive describes publisher-permission **hosting/access**: https://www.nist.gov/mml/acmd/trc/thermoml/thermoml-archive . That statement does not explicitly grant every downloader the right to relicense/publish journal-derived tables.
- Official data.gov ThermoML dataset metadata https://catalog.data.gov/dataset/thermoml-data-archive-08162 links to a **general NIST data/work policy**, https://www.nist.gov/open/license . The NIST policy allows broad distribution of NIST-authored non-SRD data, but separately acknowledges third-party/extramural sources. ThermoML was extracted from original journal articles. The interaction between these statements for the complete 49-row normalized ACS-derived dataset **requires source/rights-owner confirmation**.
- The ACS policy https://pubs.acs.org/pages/authors_copyright routes non-OA journal material reuse through RightsLink and distinguishes facts from protected publisher content; for other rights questions see https://pubs.acs.org/pages/rightslinkno . It is not a finding that every *individual experimental numeric fact* is copyrighted.
- US Supreme Court Feist v. Rural Telephone, 499 U.S. 340 (1991), https://www.law.cornell.edu/supremecourt/text/499/340 , holds individual facts cannot be copyrighted under US law but some original selection/arrangement can. EU laws can also protect qualifying databases, https://digital-strategy.ec.europa.eu/en/policies/protection-databases . Whether either applies to these 49 points and this 2020 NIST compilation in the relevant jurisdictions is **not determined by an AI or the current evidence**. Do not infer either automatic legal infringement or blanket permission.

## 2. Repository source timeline and evidence

The actual GitHub commits and their recursive trees were inspected without reprinting numerical observation rows:

| Event | UTC date | Source commit | Finding |
|---|---|---|---|
| Measurement CSV introduced | 2026-11-05 08:18:36 | 11e8606555649758bc975d722f33376337a5d8b8 | 50 lines: header plus 49 observations, blob 1,232 bytes |
| Measurement CSV removed | 2026-11-06 17:41:13 | 7e38a0cad3a77795e2a27861bdfccae6393c1659 | 50-line deletion |
| Latest main examined | 2026-11-08 | 16d8a2d221bc7906dc6c89b38aea3888f2e441f3 | CSV absent, citation metadata/opt-in procedure remain |

Historic Git blob SHA: a70d13d600a6434e5e2c7cfa510eaf4ec4b0fb01. Its measured content is intentionally **not included** in this report.

All **29 current public branch tips** returned by GitHub's branches API were inspected by their recursive trees. **17 still include the 49-observation CSV**:

~~~text
docs/archive-sco2-project-report-2026-11-05
feat/g3-whr-design-screening
feat/g31-installed-heater-ua
feat/g32-coupled-cooler-gas-props
feat/g33-reference-properties-and-convergence
feat/g34-external-evidence-intake
feat/g35-stuttgart-htc-benchmark
feat/g35b-wall-property-correlations
feat/g35c-lei-top-bottom-mixed-convection
feat/g35d-kim2019-original-equation-benchmark
feat/initial-v05-research-foundation
feat/v1-foundation-thermal-physics-wp0-wp1
feat/v1-wp2b-finite-source-wall-cycle-dynamics
feat/v1-wp3-source-bypass-pi-control
feat/v1-wp4-experimental-readiness-and-metrology
feat/v1-wp5-release-engineering-and-evidence
integration/consolidated-g35-and-kim-source
~~~

**12 of 29 branch tips lack the CSV**, including main, the TES branches, and fix/v1-rights-optin-thermoml-dataset. Deleting a branch may remove that particular ref but does not necessarily remove its underlying blob from main ancestry, other refs, caches, forks, clones or historical artifacts.

There were **no GitHub Releases** and the Git refs/tags API returned **zero tags** at audit time. However, historical GitHub Actions artifacts were checked more closely and **two still-downloadable artifacts did contain the 49-row source CSV inside their built source distribution (sdist)**:

| Workflow run | Artifact ID | Name | Inspected sdist | Inspected wheel |
|---|---:|---|---|---|
| https://github.com/Open-Energy-Methods/sco2-braytonbench/actions/runs/42253583972 | 13521677319 | v1-wheel-sdist-build-smoke | **CSV PRESENT** | CSV absent |
| https://github.com/Open-Energy-Methods/sco2-braytonbench/actions/runs/42253583972 | 13521522512 | v1-wp5-wheel-sdist-release-audit | **CSV PRESENT** | CSV absent |

Both sdists contained the same 1,232-byte measurement CSV with SHA256 97ed4e33f42ffdc087de85d5bdd686833abc766d8e56a31fac995b0cc6d10616. Sdist archive SHA256 values were respectively 4b016d04ae038e46ce744a7c981c3c527ee166336a911abc2d4e023948841d8e and edde1b01a84c7cf44b4548ed49ec853172ea4f82e69bb4eb58dc0084ed21cf9d. This was established by *archive-member inspection*, not by republishing numerical observations. **The two artifacts remain present/unexpired at the time of audit.**

Two additional sampled artifacts after exclusion (IDs 13523418148 and 13524430071 from run 42258225916) did **not** contain the CSV in their wheel or sdist. These are specific inspected examples, **not a complete count of every potentially affected earlier Actions artifact**. Forks, downloaded clones, historical PR refs, other Actions runs and externally uploaded data were not exhaustively assessed.

**Remediation priority:** Obtain explicit maintainer/rights-steward authorization to delete or expire the two confirmed public downloadable Actions artifacts and inventory other pre-removal build artifacts. GitHub artifact removal must use an authorized human maintainer or tooling with Actions write permission; the current automated read/audit process did not delete any artifact. Artifact deletion removes that distribution endpoint but not the historical Git blob, branch heads, previous downloads or third-party forks.

## 3. Present mitigations and remaining limitations

- Latest main contains no Mantilla numerical table. MANIFEST.in explicitly excludes it. TES-v0.9 wheel/sdist tests reject its presence; distributed wheel/sdist remain synthetic and reproducible.
- Optional CoolProp measured-density regression tests load the **external user-provided data** only if environment variable SCO2_MANTILLA_DENSITY_CSV is supplied. Otherwise tests explicitly skip. That skip is not a newly successful measured-data validation.
- Metadata, original DOI, method and source instructions remain. Historical snapshots and old branch tips still expose the copied table.
- Other scientific inputs need separate licensing decisions. The Stuttgart Mendeley original dataset is marked **CC BY 4.0**, https://data.mendeley.com/datasets/4mvk4nxrkz/1 , and attributed separately in the project's Stuttgart data README. Stuttgart’s licence does not apply to Mantilla.

## 4. Proposed rights steward decision path (no external inquiry sent)

**Preferred route is continued exclusion, not restoring the measured file.**

1. Request a written scope clarification from the NIST ThermoML data contact **Demian Riccardi (demian.riccardi@nist.gov)**, listed in https://catalog.data.gov/dataset/thermoml-data-archive-08162 . Specifically ask whether the archive-level general license permits republication of the 49 normalized ACS-derived measurement rows in public Git repositories and downloadable archives. If not, ask who can authorize or classify the data use.
2. Ask ACS (copyright@acs.org, via https://pubs.acs.org/pages/rightslinkno ) or its RightsLink unit to distinguish copying numeric scientific facts from reproducing their protected article/table formatting and any material-specific restrictions. Disclose **historic Git posting**, continuing exposure in 17 branch tips, removal from current main and the intention **not to bundle the measurements** in future wheel/sdist/Zenodo releases.
3. Record actual replies, sender and rights-owner authority, exact permitted or excluded scope, dates, required acknowledgments and public/private evidence references. A generic no-response is not affirmative permission.
4. With named maintainer and rights-steward approval, classify old branches as active or already merged/retired, **remove confirmed exposed Actions artifacts**, inventory similar old uploads, and implement approved branch-ref retirement or file-removal commits. **Do not automatically rewrite main history or force-push**, which could disrupt provenance and may not remove public copies from PR refs/forks/caches.
5. Reinspect the exact public release candidate's Git snapshot, source/wheel archives, retained data, third-party license attributions and relevant historical exposure. Document the actual rights disposition and close #27 only on explicit rights-steward approval.

For each external inquiry distinguish (A) reading/citing original ThermoML, (B) using numerical facts to run research tests, (C) public GitHub redistribution of the entire normalized table, and (D) source-archive/Zenodo deposit/relicensing. These are not necessarily the same permission.

**Potential outcomes:** REUSE PERMITTED ON DOCUMENTED CONDITIONS / EXCLUSION AND HISTORIC REMEDIATION APPROVED / CHANGES REQUESTED. At this point **no source-specific written approval or historic-remediation policy was obtained**, so #27 remains open. Independent scientific peer review #28 is a separate gate. This document is an evidence inventory, not legal advice.
