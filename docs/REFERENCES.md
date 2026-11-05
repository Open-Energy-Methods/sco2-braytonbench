# Research sources and modelling distinctions

## FR2016 — moderate-temperature recuperated cycle

Peter D. Friedman and Michael P. Rapp (2016), **Parametric Analysis of SCO2 Power Cycles Operating at Moderate Temperatures**, 5th International Symposium on Supercritical CO2 Power Cycles, Paper 51.

- Paper pages 5 and 10: Figure 2b (12-point conceptual recuperated cycle) and Figure 4 (more elaborate EES plant).
- Page 12, Table 2: 550 K at point 1, 30 MPa at point 1; turbine/compressor efficiencies 0.90/0.85, recuperator effectiveness 0.925, four component pressure losses and six piping-section losses.
- Page 9: original EES model segmented the recuperator into 30 sections; bypass FM3 and FM4 set to zero for the reported comparisons.
- Paper's source is a moderate-temperature reactor configuration, **not** an industrial waste-gas benchmark.
- Separate pressure mapping here: `src/sco2_braytonbench/references.py` and `docs/provenance/fr2016.yaml`.

## MK2014 — finite industrial waste-heat recovery

Mahmood Mohagheghi and Jayanta Kapat (2014), **Thermodynamic Optimization of Recuperated S-CO2 Brayton Cycles for Waste Heat Recovery Applications**, 4th International Symposium on Supercritical CO2 Power Cycles.

- Page 4: RC six-state and RRC nine-state schematics. Their numbering is unrelated to FR2016's numbering.
- Page 5, Table 2: `T_min=310 K`, `T_ambient=300 K`, fractional pressure drop `0.02`, turbine isentropic efficiency `0.90`, compressor isentropic efficiency `0.89`.
- Page 7: waste-gas stream assumed air-like, `m_gas=100 kg/s` for source study, finite gas cooling through a main heater. Working-fluid heating is **not a fixed supplied-power constraint**.
- Pages 9–11: maximizing net generation gives a different design than maximizing cycle thermal efficiency, while RRC shows limited net-power advantage in examined cases.
- Most optimized design points are presented as figures without complete numerical state tables. **Trend checks only** until reproducible numeric data are found.

## Interpretation and code boundaries

The six-state numerical solver uses its own 1–6 indexing: compressor 1→2, cold recuperator 2→3, heater 3→4, turbine 4→5, hot recuperator 5→6, cooler 6→1.

The FR2016 12-point pressure graph is not the six-state solver and is not a full thermodynamic replication.

The model's segmented heat exchangers prescribe linear pressure profiles along the exchanger. This is an explicit modelling assumption, not a validated correlation. Heat-transfer calculations use exact enthalpy conservation through the selected thermophysical backend. The gas-side heater currently assumes constant gas `cp`.

The original papers are cited, **not redistributed** in this repository. Their extracted results must not be treated as experimental CARBOSOLA data.
