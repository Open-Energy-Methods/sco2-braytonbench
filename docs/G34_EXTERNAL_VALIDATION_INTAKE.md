# G3.4 — external experimental and numerical evidence intake

**Date:** 2026-11-05. **Status:** source intake and QC completed, model-to-experiment validation **NOT** completed. This branch is stacked on [G3.3 PR #10](https://github.com/Open-Energy-Methods/sco2-braytonbench/pull/10). Keep this work separately auditable and unmerged until review.

## Evidence inventory and intended use

| ID | Source | Original measurements? | Available | Correct target |
|---|---|---|---|---|
| STUTTGART-2022 | Theologou et al., [dataset DOI 10.17632/4mvk4nxrkz.1](https://doi.org/10.17632/4mvk4nxrkz.1), CC BY 4.0 | **Yes** — reduced experiment with reported uncertainties | Original 9-sheet Excel workbook; **54** original experiment IDs; **2,508** axial rows, **2,398** local wall-temperature/HTC cells; 18 nominal HB/HM/HT sets | Single heated horizontal pipe heat-transfer and buoyancy/stratification benchmark; **not** plant cycle efficiency |
| ZHANG-2022 | Zhang et al., [DOI 10.3389/fenrg.2022.835224](https://doi.org/10.3389/fenrg.2022.835224), CC BY | **Yes**, sodium/CO2 PCHE test | Geometry 4 mm Na and 1.5 mm CO2 channels; reported area 7.3 m²; rated 54.8/54.2 kW Na/CO2 duty; 18 steady groups discussed; 3 published pressure-U rows | Coarse experimental geometry-specific PCHE benchmarking, **not** a CO2-gas recuperator or water precooler |
| KAIST-2024 | Lee et al., 8th sCO₂ Symposium Paper #6, pp. 15 and 18 | **Mixed**: measured speed/motor data and **model-corrected** turbine inlet temperature | 15 RPM sweep rows, 12,000–36,000 RPM; leakage/mass flow/PR/electrical motor power; 15 corrected inlet conditions | Off-design radial turbine **pressure/flow** comparison, cautiously; no direct η_t map inferred |
| SANDIA-2010 | Wright et al., report SAND2010-0171 | **Mixed** model and measured in same report | Table 2.1 three **predicted** states; §5.3 Figures 5-11/5-12 **measured** compressor maps | Independent compressor comparison after measured figure extraction; do not label design table as measured |
| HZDR-PCHE-2025 | Guille-Bourdas et al., [DOI 10.14278/rodare.3928](https://doi.org/10.14278/rodare.3928), CC BY 4.0 | **No** — numerical/economic published figure data | 9 supplied `Figure_*.xlsx` files (1-D predictions, cost studies, sensitivity) | Model-to-model HX/cost comparison, never experimental calibration |
| HZDR-TPMS-2026 | Guille-Bourdas et al., RODARE CARBOSOLA TPMS archive | **No** — ANSYS 24.1 CAD/CFD | CAD generation script, .stl/.pmdb, Fluent journals, ≈115 MB each case and results H5, seven cleaned text tables | Geometry and CFD/code comparison only; no experimental CARBOSOLA pressure/temperature points |
| KTH-SPG-MSR | 2025–2027 project publicly listed by KTH; Siemens Energy partner | **Not yet demonstrated** | Feasibility/conceptual heat exchanger and test-infrastructure objectives | Potential research contact for publication-cleared data and experimental planning; **not released rig measurements** |

*Uploaded scientific source files are not committed as PDFs/ANSYS binaries. The external data may be independently downloaded and cited using the DOIs; check each source's reuse rights before republishing normalized tables. Intentionally do not claim an HZDR figure study was a laboratory trial.*

## Source QC — two important unresolved mismatches

### STU-001: 833 kW/m² anomalous Stuttgart source cell

The Excel workbook's tab **TS4** for experiment `4MM_HM_77.5_10_20_90_A` has a source heat-flux value **832.9920767421186 kW/m²**. The nominally matched `HB` and `HT` experiments show **91.7575** and **91.7029 kW/m²**, respectively, and near-identical input electrical power **2,309–2,310 W**. This is strongly suggestive of a source-cell error but **not proven**. Raw value is retained unchanged, marked `QUARANTINE` for correlation calibration. Never silently replace with 91.7.

Independent consistency: 18 sets of three orientations are present, 800 paired top/bottom axial positions can be matched. Maximum observed matched top-to-bottom wall-temperature difference in the supplied profiles: **86.813 K** at `x=0.76 m`, nominal family `8MM_H?_77.5_20_5_90_A`. The associated paper reports differences up to ~90 K, providing a consistency crosscheck, **not a predictive model validation**.

### ZH-001: rated PCHE `U` does not follow directly from published terminal table

Zhang et al., Table 1 (PDF p.4) state sodium 501.5→326.7 °C, CO₂ 317.8→498.5 °C, CO₂-side duty 54.2 kW, sodium duty 54.8 kW. The paper gives heat-transfer area **7.3 m²** and rated overall coefficient **1,264 W/(m² K)** (PDF p.5), but its stated counterflow LMTD formula gives:

```text
ΔT_high = 501.5 - 498.5 = 3.0 K
ΔT_low  = 326.7 - 317.8 = 8.9 K
LMTD = (8.9 - 3.0) / ln(8.9 / 3.0) = 5.425592 K
U_Qcold = (54.2e3 W) / (7.3 m² × 5.425592 K)
        = 1,368.451 W/(m² K), or 8.264% above 1,264.
```

The separately reported **1,388 W/(m² K) at 20.0 MPa** in Table 2 must not be silently identified with the published rated `U` calculation: operating points/processing can differ. Possible causes (area definition, averaged temperatures, flow arrangement, processing, transcription) are **unverified**. Keep ZH-001 OPEN and seek author clarification before calibration.

### KAIST-001: model-corrected inlet temperature, not direct sensor

The paper explicitly notes the thermocouple is upstream of secondary-flow merging; leakage flow and shaft windage heat may yield `T_in,measured < T_out,measured` at high RPM. Table 7's corrected inlet T uses a windage model and indirect inference. Table 5's *motor power* is electrical, not directly measured turbine shaft work. Do not infer a turbine isentropic efficiency map merely from those quantities.

### SANDIA-001: Table 2.1 is design calculation, not experiment

Sandia Table 2.1 gives three **predicted** 75,000-RPM cases. The actual measured compressor maps are Figures 5-11/5-12 in §5.3 and require separately digitized source points or raw data.

## Downstream acceptance gates

1. Keep **source classification** `measured | experimentally_derived | model_corrected | simulated | predicted_design` on every point. Do not treat the same author's model output as independent validation.
2. Use isolated single-component benchmarks before full BraytonBench steady cycle validation: Stuttgart heated pipe → Zhang sodium-PCHE → Sandia compressor / KAIST turbine → numerical HZDR PCHE/TPMS.
3. For Stuttgart, evaluate by **nominal experiment group**, preserving HB (bottom 180°), HM (middle 90°), HT (top 0°) and reported uncertainties. Fit on separate groups and evaluate held-out groups; do not random-shuffle axial positions of one run between training and validation.
4. Document uncertainty propagation and instrument vs derived-data correlation; use actual dynamic CO₂ EOS and wall/bulk temperature profiles. Quarantine STU-001.
5. Do not calibrate a single global UA from Zhang's 54.2-kW rated row until ZH-001 is reconciled. Sodium thermal properties and flow/heat loss must be modelled explicitly.
6. Compare KAIST maps only within the experimentally tested low-temperature 77–88 bar region; handle secondary leakage and windage correction, not a fictitious high-T turbine.
7. For HZDR, numerical replication is its own gate; CAD/Fluent files may have software licence constraints. No full binary archive in Git, and do not claim live test data.
8. KTH SPG-MSR project contact can request public test matrices, permission-cleared heat-exchanger geometry and prospective research benchmarking; do not ask for protected Siemens Energy IP or assume an operational facility already exists.

## Reproducibility package

The separately produced research-intake package includes `stuttgart_experiment_index.csv` (54), `stuttgart_axial_profiles.csv` (2,508), KAIST Table 5/7 factual transcriptions, Zhang rated/pressure study, Sandia **predicted** states, HZDR workbook and TPMS archive inventories, a JSON source registry, `validate_intake.py` and audit results. These generated files are intentionally not automatically rehosted on this PR: original source PDFs, large vendor-specific CFD cases and uncertain-rights source transcriptions are not being redistributed.

**Gate status:** source intake and structural crosschecks PASS, two anomalies OPEN, no heat-transfer correlation, measured turbomachinery map or whole-plant model validation has yet passed.
