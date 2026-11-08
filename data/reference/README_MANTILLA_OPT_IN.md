# Mantilla et al. 2010 ThermoML measurement data — user-supplied optional test

The **current sCO₂-BraytonBench main source snapshot and tested wheel/sdist builds do not distribute the 49-point transcription** of the Mantilla, Cristancho, Ejaz, Hall, Atilhan and Iglesias-Silva (2010) experimental CO₂ density dataset from NIST ThermoML. Historical Git revisions, 17 live older branch heads and at least two old Actions source-archive artifacts **still expose the file**, as documented in the dated rights audit below. The upstream article and source are:

- Mantilla et al., *P-ρ-T Data for Carbon Dioxide from (310 to 450) K up to 160 MPa*, *J. Chem. Eng. Data* (2010), DOI: https://doi.org/10.1021/je1001158
- NIST ThermoML record: https://trc.nist.gov/ThermoML/10.1021/je1001158.html
- Source metadata: [mantilla2010_provenance.yaml](mantilla2010_provenance.yaml)
- Redistribution/permission issue: https://github.com/Open-Energy-Methods/sco2-braytonbench/issues/27
- Historical Git/branch exposure and rights audit: ../../docs/data_licenses/MANTILLA_HISTORICAL_RIGHTS_AUDIT_2026-11-08.md

**Reason:** NIST states that ThermoML archive files are provided with permission of journal publishers. Specific downstream redistribution permission for the complete normalized 49-point data table has not been established. Merely downloading a file or citing a scientific publication does not establish relicensing of a third-party data compilation.

If you already have legitimate access to the data under terms permitting your intended use, you can personally prepare a CSV using the original ThermoML observation records. The optional measured-density tests accept a **user-supplied, external** CSV using an environment variable; they do not automatically download the source or redistribute it.

Required columns:

```text
T_K,P_kPa,rho_kg_m3,thermoml_combined_uncertainty_as_reported
```

`T_K` is absolute temperature in K, `P_kPa` absolute pressure in kPa, `rho_kg_m3` density in kg/m³; the last column preserves the ThermoML reported combined/expanded uncertainty **as reported**, not automatically `k=1`.

Linux/macOS:

```bash
SCO2_MANTILLA_DENSITY_CSV=/external/source/thermoml_density.csv \
  python -m pytest -q tests/test_co2_measured_density.py
```

PowerShell:

```powershell
$env:SCO2_MANTILLA_DENSITY_CSV = 'C:\\external\\source\\thermoml_density.csv'
python -m pytest -q tests/test_co2_measured_density.py
```

Run after `python -m pip install -e '.[test,co2]' 'CoolProp==8.0.0'`.

Without that external file, pytest reports an **explicit optional skip**. This is not equivalent to passing 49 independent experimental measurements. Historical recorded results from earlier repository/CI commits remain historical evidence, not a newly runnable release test.

The current HEAD omits the transcribed CSV and WP5 enforces exclusion from **new** source archives. **Historical Git history, 17 older public branch heads and at least two unexpired downloadable historical Actions sdist artifacts still contain the CSV.** Prior exposure is not undone by today's exclusion. See the linked dated audit; any old-artifact deletion, branch cleanup or historical-content remediation requires a documented maintainer/rights-steward decision.
