# Dataset licence and redistribution review — v1.0 candidate

**Audit date:** 2026-11-06. **Review class:** public-source inspection and repository-content inventory, not a written rights-holder legal opinion or formal licence clearance. **Current release decision:** allow continued software development; hold v1.0 publication pending #27 and independent research-data review.

| Material in repository | Upstream source | Confirmed on publisher/repository landing page | Current release treatment |
|---|---|---|---|
| `data/validation/stuttgart/{experiment_index.csv,axial_profiles.csv}` | Theologou, Mertz, Laurien, Starflinger (2022), Mendeley Data DOI [10.17632/4mvk4nxrkz.1](https://data.mendeley.com/datasets/4mvk4nxrkz/1) | Dataset publicly lists **CC BY 4.0**; authors and version listed; source CSVs here are an adapted/extracted transformation | **Permissive with attribution**: keep original contributors, DOI, CC BY 4.0 link, adapted notice and STU-001 original anomaly/quarantine. Never treat data as BSD-covered software. Full credit in [dataset README](../data/validation/stuttgart/README.md) |
| `data/reference/mantilla2010_thermoml_density.csv` | Mantilla et al. (2010) *J. Chem. Eng. Data*, DOI [10.1021/je1001158](https://trc.nist.gov/ThermoML/10.1021/je1001158.html), curated NIST TRC archive | **No explicit unrestricted downstream redistribution licence established for this normalized complete 49-point transcription.** NIST states ThermoML files are available with permission of *journal publishers*. Public availability is not blanket authority to repackage in a BSD software source archive. | **BLOCKED FOR DISTRIBUTION** until authorized. Explicit `MANIFEST.in` exclude, with actual sdist check in WP5 gate; provenance citation remains. Public Git repo already contains this file; maintainer must consider separately whether to remove, replace with opt-in download, or obtain written publisher permission. See [rights issue #27](https://github.com/Open-Energy-Methods/sco2-braytonbench/issues/27). |
| `data/reference/kim2019_coefficients.json` | Kim et al. (2019), Elsevier journal DOI 10.1016/j.ijheatmasstransfer.2018.11.075 | Contains an attributed *numerical coefficient/source-form transcription*, not the copyrighted source PDF; upstream data source declares no licence for the paper | **Attribution + manual legal/content review still needed**. Do not rehost original PDF. The disputed Eq.24 exponent remains unresolved [issue #20](https://github.com/Open-Energy-Methods/sco2-braytonbench/issues/20) and is excluded from claimed stable validation |
| `data/validation/reported_source_cases.json` | Small calculated/transcribed values and metadata from Zhang, Sandia, KAIST, HZDR reports | Each individual source has its own terms, not an umbrella BSD software grant | **Manual review / evidence-limited**. Keep only short attributed source facts/numeric benchmarks; no paper images, entire tables or large bulk data without specific rights |
| `data_requests/fr2016_table3_reference_template.csv` | Friedman & Rapp original paper mapped into a *project-created request template* | No original PDF included in the project | Attribution and source-extraction scope review; verify it does not republish large protected source content before v1 release |
| `protocols/wp4/*`, `examples/*`, `src/*` | Project-authored source/control/metrology software and explicitly synthetic templates | BSD-3-Clause project licence, except named third-party content | Research software/test fixtures; no claims of instrument approval or measurements |

## Confirmed public-source evidence

- [Mendeley Data, Theologou et al., Version 1](https://data.mendeley.com/datasets/4mvk4nxrkz/1): authors, publication date 2022-05-12, 54 experiments and licence **CC BY 4.0** explicitly displayed.
- [NIST ThermoML archive](https://www.nist.gov/mml/acmd/trc/thermoml): records experimental data published in participating journals, says archive files are accessible **with permission of journal publishers** and requests journal/ThermoML archive citation.
- [Mantilla 2010 individual NIST record](https://trc.nist.gov/ThermoML/10.1021/je1001158.html): Journal of Chemical & Engineering Data article, 49 mass-density points, no clear CC0/CC BY reuse licence on that record.
- [NIST copyright and SRD policy](https://www.nist.gov/open/copyright-fair-use-and-licensing-statements-srd-data-software-and-technical-series-publications): SRD and other NIST work have different terms; a third-party journal-curated experimental dataset should **not** be assumed US-government public domain.
- [Data.gov ThermoML archive contact](https://catalog.data.gov/dataset/thermoml-data-archive): Demian Riccardi, NIST, `demian.riccardi@nist.gov` (published contact). Confirmation from authorized rights holder/journal remains necessary.

## Current technical mitigation

1. The repository remains alpha and no release tag, DOI or standalone data deposit is being issued.
2. The candidate *sdist* excludes the Mantilla full extracted 49-point CSV; `scripts/v1_release_gate.py` now **asserts it is absent** in the built source archive. Documentation/provenance YAML remains packaged, and the measured-density test is still runnable from the existing **source checkout** pending a rights decision.
3. The Stuttgart CC BY material retains explicit acknowledgement and adapted-dataset notice, even when included in the source archive. BSD software metadata do **not** relicense these derived tables.
4. The public Git repository already having an unlicensed or uncertain file is **not resolved merely by excluding it from a new archive**. Review GitHub source visibility and commit history separately with the authorized data owner; avoid publishing more copies before the rights decision.

## Rights-holder question ready for sending

**To:** `demian.riccardi@nist.gov` (NIST ThermoML archive contact; may refer to ACS permissions team)

**Subject:** Permission/terms for redistributing 49 experimental CO₂ density records from NIST ThermoML, DOI 10.1021/je1001158

> We maintain an open-source thermodynamic research tool (sCO₂-BraytonBench) with attribution to Mantilla, Cristancho, Ejaz and Hall (2010), DOI 10.1021/je1001158. We have transcribed 49 experimental pressure–temperature–density records and source uncertainty metadata from NIST/TRC ThermoML into a normalized CSV for reproducible CoolProp property checks. We would like to know the correct licence and rights holder, and whether it is permitted to redistribute this attributed, transformed CSV in a public GitHub repository and downloadable source package (and later Zenodo archive), rather than merely linking to the NIST original. If separate ACS permission is required, please advise on the appropriate contact and terms. Until clarified, we will withhold the CSV from new source-distribution archives. Thank you.

**Not sent by the assistant; no rights holder has responded.** Retain written permission or the specific binding license text and apply its attribution conditions before marking #27 closed. This is a factual process plan, not legal advice.
