# G3 real-fluid waste-heat design screening — verified results

**Date:** 2026-11-05. **Gate:** G3 exploratory/partial, NOT industrial validation.
**Thermophysical backend:** CoolProp 8.0.0 `HEOS::CO2`. **Plant:** independent six-state recuperated Brayton prototype, NOT CARBOSOLA and NOT the Mohagheghi–Kapat (2014) numerical optimizer.

**[GitHub Actions 41999222234](https://github.com/Open-Energy-Methods/sco2-braytonbench/actions/runs/41999222234): all four CI jobs passed.**
[Download machine-readable JSON and CSV](https://github.com/Open-Energy-Methods/sco2-braytonbench/actions/runs/41999222234/artifacts/13402265636).

## Provenance and explicit assumptions

Mohagheghi & Kapat (2014), physical pages 5–11, motivate optimizing **net recovered power** rather than thermal efficiency when exhaust heat is finite. Their illustrative gas mass flow is 100 kg/s; other values below are OUR hypothetical design choices, and we do NOT reproduce their REFPROP/GA configuration, RRC topology or 2% fractional pressure-drop method.

| Input | Our assumption |
|---|---:|
| Exhaust gas | 100 kg/s, 760 K, constant cp=1100 J/(kg K) |
| Minimum stack temperature | 360 K |
| Heater min local approach | 10 K |
| Heater UA sizing upper bound | 1.2 MW/K (NOT fixed installed-UA equality) |
| Low CO₂ pressure and inlet temperature | 8.5 MPa; 310 K |
| Turbine inlet pressure | 24 MPa |
| Turbine/compressor isentropic efficiencies | 0.90/0.89 |
| Recuperator fixed UA | 200 kW/K |
| Independent fixed component pressure losses | 100/150/100/50 kPa (cold recup/heater/hot recup/cooler) |
| Turbine inlet T candidate grid | 550, 600, 650, 700, 770 K |
| CO₂ mass-flow candidate grid | 20, 40, 70, 100 kg/s |

Maxima mean **best sampled feasible candidate**, NOT global thermodynamic optima. Power means **net shaft power**, not electrical export.

## Base finite-source screening

**16 feasible, 4 rejected** (all rejected cases prescribed T4=770 K > 760 K source gas).

| Quantity | Best shaft power | Best thermal efficiency |
|---|---:|---:|
| Turbine inlet temperature | 700 K | 700 K |
| CO₂ mass flow | 100 kg/s | 20 kg/s |
| Net shaft power | **8.109835 MW** | 1.621967 MW |
| Cycle efficiency | 25.2184% | **33.5039%** |
| External heat absorbed | 32.1585 MW | 4.8411 MW |
| Cooler rejected heat | 24.0486 MW | 3.2192 MW |
| Stack gas temperature | 467.650 K | 715.990 K |
| Available source sensible heat recovered | 73.087% | 11.003% |
| Recuperator minimum **internal** approach | 64.738 K | 4.627 K |
| Heater minimum approach | 13.108 K | 60.000 K |
| Heater UA required | 923.866 kW/K | 40.528 kW/K |

**Conclusion:** Maximizing cycle thermal efficiency can lose recoverable power because it underuses the finite source. This is a *qualitative concept match* with Mohagheghi & Kapat, not a reproduced quantitative benchmark.

## Additional hypothetical plant constraints

The second screen adds (i) **Q_cooler <=15 MW_th**, and (ii) **minimum local recuperator approach >=10 K**. Neither is a source-specified or measured design limit; in particular local internal approach is **not** the published recuperator terminal-dT decision variable.

**6 feasible, 14 rejected** among the same 20 candidates.

| Quantity | Best shaft power | Best thermal efficiency |
|---|---:|---:|
| Turbine inlet temperature | 650 K | 700 K |
| CO₂ mass flow | 70 kg/s | 40 kg/s |
| Net shaft power | **4.983670 MW** | 3.243934 MW |
| Thermal efficiency | 25.8575% | **30.7281%** |
| Cooler rejected heat | 14.2899 MW_th | 7.3130 MW_th |
| Recuperator minimum internal approach | 35.626 K | 19.698 K |
| Stack gas temperature | 584.785 K | 664.028 K |
| Source heat recovered fraction | 43.804% | 23.993% |

The original 8.11 MW power-maximizing point violates this added cooling limit, and the original 33.5% efficiency-maximizing point violates the new recuperator margin. Therefore the baseline rankings are **not robust to these illustrative constraints**.

## Segmentation sensitivity (original two winners)

| Candidate | Efficiency, 12 sections | 24 sections | 48 sections |
|---|---:|---:|---:|
| Power-max winner | 25.218353% | 25.218877% | 25.219007% |
| Efficiency-max winner | 33.503907% | 33.491661% | 33.488291% |

At the power-max point the heater minimum approach changed 13.1076 → 13.1093 → 13.1098 K for 12/24/48 segments; between 24 and 48 it changed **0.000426 K**. Required heater UA changed 923.866 → 922.637 → 922.326 kW/K.

**Important:** Net shaft power does not vary at these fixed T/P/flow points because this model prescribes turbine/compressor boundary states and constant efficiencies. Invariance of net power is a *model identity*, **not proof of heat-exchanger mesh convergence**. Only two candidate points have been refined, so numerical convergence remains unproven over the full design domain.

## Test record

[Actions 41999222234](https://github.com/Open-Energy-Methods/sco2-braytonbench/actions/runs/41999222234): standard Python 3.11 and 3.12 fixture suites each **136 passed, 6 skipped (optional CoolProp)**; separate property reference suite **61 passed**; multi-point real-CO₂ waste-gas integration suite **3 passed**; design/robustness script completed, exported JSON/CSV.

Analytic regressions include closed-form counterflow HX epsilon–NTU with equal/unequal heat-capacity rates and exact constant-cp compressor/turbine state equations, plus conservation and infeasibility tests. **These are component implementation checks, not real-fluid experiments**.

## Open scientific limitations

1. Source gas cp is constant; the 2014 study uses REFPROP air.
2. Pressure losses are fixed absolute values rather than realistic flow-dependent drops or the paper's 2% FPD convention.
3. Heater UA is checked as a design upper bound. A fixed installed heater with no bypass would require a *coupled* T4–UA balance, which is not yet implemented.
4. Compressor/turbine are constant-efficiency devices with no corrected-speed or mass-flow maps, and cooler inlet state is imposed without a calibrated heat sink/cooling auxiliary model.
5. Generator losses, economics, hardware safety, time dynamics, composition/chemistry and experimental CARBOSOLA records are absent.
6. No global optimization, published MK2014 design-point replication or broad real-fluid numerical convergence has been demonstrated.

**Next engineering task:** fixed-installed-UA coupled gas/CO₂ heater temperature solution and better pressure-loss/cooling models, followed by source-aware operating constraints. **G3 remains partial; G4 and PI/MPC are not started.**
