"""Quantify the consequences of counterfactual boundary-state labels in FR2016.

Does not reconstruct the detailed author EES plant, or estimate parameter
uncertainty from a probability distribution. Mapping sensitivity diagnoses
mislabel sensitivity; the paper identifies T7 and compressor suction P8 in its conceptual schematic.
"""
from __future__ import annotations
import json
from pathlib import Path
from CoolProp.CoolProp import PropsSI
from sco2_braytonbench.properties import CoolPropCO2
from sco2_braytonbench.reference_cycle import fr2016_conceptual_cycle,FR2016_REPORTED

props=CoolPropCO2()
pstar=1.13*PropsSI("Pcrit","HEOS::CO2")
tstar=PropsSI("Tcrit","HEOS::CO2")
cases=[]
for lp in (7,8):
    for lt in (7,8):
        try:
            r=fr2016_conceptual_cycle(
                props,low_pressure_pa=pstar,low_temperature_k=tstar,
                low_pressure_point=lp,low_temperature_point=lt)
            cases.append({
                "reported_Plow_assigned_to_point":lp,
                "reported_Tlow_assigned_to_point":lt,
                "status":"solved",
                "efficiency_percent":100*r.eta_thermal,
                "deviation_from_paper_percentage_points":100*(
                    r.eta_thermal-FR2016_REPORTED["eta_thermal"]),
                "energy_residual_J_per_kg":r.energy_residual_j_kg,
                "recuperator_minimum_approach_K":r.recuperator_min_dt_k,
                "P7_MPa":r.points[7].p/1e6,
                "P8_MPa":r.points[8].p/1e6,
                "T7_K":r.points[7].t,
                "T8_K":r.points[8].t
            })
        except Exception as exc:
            cases.append({"reported_Plow_assigned_to_point":lp,
                          "reported_Tlow_assigned_to_point":lt,
                          "status":"solver_or_domain_failure",
                          "message":str(exc)})
valid=[c for c in cases if c["status"]=="solved"]
r={"source":"Friedman and Rapp 2016, Figure 2b/Table 2/Table 3",
   "paper_reported_low_pressure_ratio_to_Pcrit":1.13,
   "paper_reported_low_temperature_ratio_to_Tcrit":1.0,
   "paper_thermal_efficiency_percent":100*FR2016_REPORTED["eta_thermal"],
   "source_model_identified":False,
   "purpose":"Stress-test erroneous alternative state labels against the source-supported T7/P8 default; no full EES model is recovered",
   "n_mapping_cases":4,
   "cases":cases,
   "observed_counterfactual_mapping_spread_pp":
       max(c["efficiency_percent"] for c in valid)-min(c["efficiency_percent"] for c in valid) if len(valid)>1 else None,
   "unidentified_items":[
      "Original detailed Figure 4 pressure boundary mapping (may differ from Figure 2b)",
      "Original EES compressor-turbine and main-turbine shaft split",
      "Original compressor/turbine maps, motor-generator performance",
      "Complete plant state table and external loop conditions",
      "Original source property reference and geometry details",
      "Full EES equations and optimizer initialization"],
   "nonidentifiability_reason":"Published aggregate energy balance yields fewer independent scalar constraints than the unknown plant state, flow, split and performance variables.",
   "gate":"G2_NOT_IDENTIFIED"}
out=Path("evidence/generated/fr2016_identifiability.json")
out.parent.mkdir(parents=True,exist_ok=True)
out.write_text(json.dumps(r,indent=2)+"\n")
print(json.dumps(r,indent=2))
