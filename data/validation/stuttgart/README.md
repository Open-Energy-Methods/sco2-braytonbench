# Stuttgart experimental benchmark inputs (H1)

Source: Theologou, Mertz, Laurien, Starflinger (2022), *Experimental Investigations on Heat Transfer of CO₂ Under Supercritical Pressure in Heated Horizontal Pipes*, [Mendeley Data DOI 10.17632/4mvk4nxrkz.1](https://doi.org/10.17632/4mvk4nxrkz.1), Version 1 (12 May 2022).

**Licence for original deposited dataset: [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/).** These tables are **adapted/extracted** from the source spreadsheet `EXPERIMENTAL DATASET.xlsx`, with attribution and no intentional modification of numerical cells. Please cite the original source and DOI when using them. The code repository's BSD-3-Clause licence does **not** replace CC BY 4.0 for these derived data.

- `experiment_index.csv`: 54 distinct HB/HM/HT experiment records, source workbook sheet, inner diameter, inlet T/pressure, mass flow, reported q, electrical power and measurement-reported percentage uncertainties.
- `axial_profiles.csv`: all 2,508 source workbook axial records, including 2,398 rows with measured-derived local heat transfer coefficient, inner wall temperature and their reported percentage uncertainties.
- Source zip SHA256: `2c978a8c0d97bc2aa5f0266b1199a120fe844a7549d54dcb0ace60fdeef126d1`.
- Original source workbook SHA256: `ee1e28b3f204b15e65fc546725a7cb5ec7ac115db891286fe1392885d299778a`.
- Normalized original CSV SHA256 (with CRLF separators in extraction): experiment index `47745aef4f7bb77e04b2c7cdbb188de6aa9876c5d8509a5669342d048e19fd11`, axial `eb4f3cf4123c7c55c52c5bd75060c5833c637fc2392ed05777f0bf054583a536`. Git uses LF-normalized records (numerical fields unchanged).

**Critical QC:** source experiment `4MM_HM_77.5_10_20_90_A` reports 832.992 kW/m² while matching top/bottom nominal experiments report ~91.7 kW/m² and essentially the same electrical power. This is a possible **source error**, not a verified correction. The source value remains present unmodified; the H1 benchmark quarantines that entire experiment. See [G3.4 intake audit](../../../docs/G34_EXTERNAL_VALIDATION_INTAKE.md).

The 54 experiments consist of 18 orientation triplets. Do **not** randomly divide individual axial points from the same nominal experiment group across training and testing. Axial local HTC values are **derived** using experimental heat input/temperature fields, not independently directly measured local sensors.

Benchmark: [G3.5 methodology](../../../docs/G35_STUTTGART_HTC.md). Example command: `python scripts/stuttgart_h1.py`.
