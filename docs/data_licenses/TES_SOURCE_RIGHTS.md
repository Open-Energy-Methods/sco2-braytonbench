# TES source data and third-party redistribution-rights dossier — pre-release status

**Updated historical audit (8 November 2026):** [Source-specific NIST/ACS licensing analysis and 17-of-29-branch exposure inventory](MANTILLA_HISTORICAL_RIGHTS_AUDIT_2026-11-08.md). Current and historical distribution are separate questions. NIST catalog metadata points to its general reuse policy, but ThermoML is publisher-sourced and its particular downstream rights remain unconfirmed. No permission or independent stewardship sign-off is claimed.

**Issue:** [#27](https://github.com/Open-Energy-Methods/sco2-braytonbench/issues/27).  
**Status:** UNRESOLVED / **no permission to redistribute historical extracted measurements has been demonstrated**.  
**Scope:** governance of third-party historical data in this repository and archives; not evidence that the underlying original experimental paper is inaccurate.  
**Owner:** release maintainer plus an independent rights steward; no identity/signature is asserted here.

## Exactly which source is implicated

- Original source: Mantilla, I.D., Cristancho, D.E., Ejaz, S., Hall, K.R., Atilhan, M. and Iglesias-Silva, G.A., Journal of Chemical & Engineering Data (2010), doi:10.1021/je1001158, original high-pressure CO2 P-rho-T density measurements.
- ThermoML curated record: https://trc.nist.gov/ThermoML/10.1021/je1001158.html — identifies **49 observation points** with temperature and pressure coordinates.
- Historic repository derivative: data/reference/mantilla2010_thermoml_density.csv — a normalized/transcribed measurement table whose exact downstream distribution rights have **not** been documented.
- Retained non-measurement provenance: data/reference/mantilla2010_provenance.yaml and data/reference/README_MANTILLA_OPT_IN.md. This is citation/provenance metadata, not the 49 measurement rows.
- NIST/TRC's own archive note states that the ThermoML files are available *with permission of the journal publishers* and requests reference to original journals and the ThermoML archive (https://www.nist.gov/mml/acmd/trc/thermoml). **Permission for NIST to host a publisher-derived record does not automatically convey permission to a third party to relicense and republish its 49-row normalized table under a BSD software release.**
- The original article's publisher page is https://pubs.acs.org/doi/10.1021/je1001158. No explicit downstream right to republish the extracted 49-row CSV under the repository BSD-3-Clause has been established in this audit.

## Present source/archive state (updated Git tree and CI check, 8 November 2026)

The named derived table is **absent from the current Git tree at 16d8a2d221bc7906dc6c89b38aea3888f2e441f3**. The source manifest contains an explicit denylist exclusion of that CSV, and TES-v0.9 checks absence in both built wheel and sdist alongside packaged model-pickle/PDF exclusions. Provenance YAML remains.

The 8 November 2026 GitHub API inventory found the historical CSV still present **at 17 of 29 current public branch tips**, even though main and the current TES branches exclude it. The repository has **zero GitHub Releases and zero Git tag refs** at this audit time; older CI artifacts/forks were not comprehensively enumerated. See the detailed dated audit linked above for the exact branch names, introduction/deletion commits and measured-data blob identifier.

**Important distinction:** removal from the latest tree and build archives does **not** automatically remove material from public Git history, forks, earlier tags/releases, prior artifact bundles or downstream copies. An archival history and distribution-rights review is still required; neither original publication nor NIST-hosted download establishes a permissive downstream license by implication.

## Release steward's decision branches

### Branch A — permission or demonstrably allowed redistribution

Secure evidence from the rights owner or an authorized delegate specifically covering the **transcribed/normalized table**, reuse scope (public Git tree/history, source archive, hosted artifact/Zenodo), attribution and required conditions. Preserve dated documents and evidence of signatory authority under a controlled rights folder, with public metadata referencing them as appropriate. The software BSD license must not be falsely applied to data with a different license.

### Branch B — exclusion with historical remediation

If permission is not granted or cannot be verified, keep the derived measurement values out of source and distribution archives, with opt-in download instructions and original attribution. Have an independent rights steward assess any **existing public Git history/older releases** and recommend remediation with explicit documented approval. Removing a file from current main is not a retroactive permission grant. Rewrite public history only after a coordinated maintainer/rights decision, never as a concealed automated step.

## Verifiable decision register before any v1.0 release

- [ ] Identify actual copyright/licence owner(s), with evidence of authority for this derivative.
- [ ] Obtain and archive either explicit reuse permission **or** independent documented approval of an exclusion/history-remediation path.
- [ ] Specify conditions for transformed scientific data separately from software.
- [ ] Record attribution to the original journal article (DOI) and ThermoML/NIST archival representation.
- [ ] Audit current release commit, earlier distribution exposure and the actual final archives.
- [ ] Record rights steward name, affiliation/authority, date, version/source commit, evidence path, and a signed/traceable decision.
- [ ] Update #27 only after documented review; do not close it based solely on a green CI absence test.

Other sources (Schumann, Avallone, Furnas, original Stuttgart CC BY materials, any new citations) require their own attribution/permission assessment as applicable. An institutional manuscript URL or CC BY notice for a different dataset is **not** permission for Mantilla.

**Current verdict: NO PERMISSION CONFIRMED / BLOCKED FOR FORMAL v1.0 RELEASE.** This document is a public review dossier and does not itself constitute legal advice or a rights determination.
