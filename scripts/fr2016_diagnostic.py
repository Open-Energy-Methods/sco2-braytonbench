"""Write machine-readable and explicitly NON-VALIDATION comparison.

Requires optional CoolProp. The normalized MW outputs assume the paper's
100.20 MW heat input to permit comparison of power ratios and do not infer
a real CARBOSOLA plant mass flow or component sizing.
"""
from __future__ import annotations
import json, platform, pathlib
from CoolProp import __version__ as coolprop_version
from CoolProp.CoolProp import PropsSI
from sco2_braytonbench.properties import CoolPropCO2
from sco2_braytonbench.reference_cycle import (
    FR2016_REPORTED,fr2016_conceptual_cycle)

pcrit=PropsSI("Pcrit","HEOS::CO2")
tcrit=PropsSI("Tcrit","HEOS::CO2")
res=fr2016_conceptual_cycle(
    CoolPropCO2(),low_pressure_pa=1.13*pcrit,
    low_temperature_k=tcrit)
scaled=res.equivalent_MW_at_reported_heater_duty()
paper_eta=FR2016_REPORTED["eta_thermal"]
r={
    "comparison_class":"exploratory_conceptual_figure2b_NOT_full_EES",
    "numerical_validation_gate":"OPEN",
    "paper":"Friedman & Rapp 2016, Figure 2b/Table 2/Table 3",
    "paper_configuration":"detailed EES Figure 4 contains compressor turbine and extra branches",
    "model_configuration":"single-compressor single-turbine Figure 2b with given pressure graph",
    "interpretation":"T_low assigned to paper point 7; P_low assigned to point 8; NOT confirmed from EES files",
    "EOS":"HEOS::CO2",
    "coolprop_version":coolprop_version,
    "python":platform.python_version(),
    "source_inputs":{"T1_K":550,"P1_Pa":30e6,"eta_c":.85,
       "eta_t":.9,"eps_recup":.925,"T_low_K":tcrit,"P8_Pa":1.13*pcrit,
       "recuperator_segments":30},
    "calculated":{"eta_thermal":res.eta_thermal,
       "eta_percentage_point_difference":100*(res.eta_thermal-paper_eta),
       "specific_heater_kJ_kg":res.q_heater_j_kg/1000,
       "specific_net_work_kJ_kg":(res.w_turbine_j_kg-res.w_compressor_j_kg)/1000,
       "energy_residual_J_kg":res.energy_residual_j_kg,
       "recuperator_min_dT_K":res.recuperator_min_dt_k,
       "equivalent_MW_if_Qheater_100_2MW":scaled,
       "paper_states":[{"point":i,"P_MPa":s.p/1e6,"T_K":s.t,
          "h_J_kg":s.h,"s_J_kgK":s.s} for i,s in sorted(res.points.items())]},
    "paper_table3_MW":FR2016_REPORTED,
    "limitations":[
       "not a reproduction of the approximately 400-equation EES plant",
       "no compressor-turbine/main turbine split",
       "paper provides no full CO2 state point table",
       "matching aggregate numbers alone would not validate model",
       "no HZDR/CARBOSOLA measurements used"]
}
p=pathlib.Path("evidence/generated/fr2016_conceptual_diagnostic.json")
p.parent.mkdir(parents=True,exist_ok=True)
p.write_text(json.dumps(r,indent=2)+"\n")
print(json.dumps({k:v for k,v in r.items() if k!="calculated"},indent=2))
print("CALCULATED",json.dumps({k:v for k,v in r["calculated"].items() if k!="paper_states"},indent=2))
print("Written:",p)
