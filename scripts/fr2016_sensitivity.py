"""Explicit uncertainty/exploratory sensitivity; not a passed FR2016 replication."""
import json
from pathlib import Path
from CoolProp import __version__ as coolprop_version
from CoolProp.CoolProp import PropsSI
from sco2_braytonbench.properties import CoolPropCO2
from sco2_braytonbench.reference_cycle import fr2016_conceptual_cycle

pcrit=PropsSI("Pcrit","CO2")
tcrit=PropsSI("Tcrit","CO2")
f=CoolPropCO2()

def evaluate(name,segments=30,p_mult=1.0,t_shift=0.0):
    r=fr2016_conceptual_cycle(
       f, low_pressure_pa=1.13*pcrit*p_mult,
       low_temperature_k=tcrit+t_shift,
       segments=segments)
    return {
       "case":name,"segments":segments,"p_low_multiplier":p_mult,
       "low_temp_shift_k":t_shift,
       "thermal_efficiency":r.eta_thermal,
       "recuperator_min_approach_K":r.recuperator_min_dt_k,
       "recuperator_UA_per_kg_s_W_K":r.recuperator_ua_per_kg_s_w_k,
       "heater_kJ_kg":r.q_heater_j_kg/1000,
       "net_kJ_kg":(r.w_turbine_j_kg-r.w_compressor_j_kg)/1000,
       "energy_residual_J_kg":r.energy_residual_j_kg
    }

rows=[]
for n in (15,30,60):
    rows.append(evaluate("segmentation",segments=n))
for p in (.99,1.01):
    rows.append(evaluate("low_pressure",p_mult=p))
for dT in (-1.0,1.0):
    rows.append(evaluate("low_temperature",t_shift=dT))
baseline=next(x for x in rows if x["case"]=="segmentation" and x["segments"]==30)
seg60=next(x for x in rows if x["case"]=="segmentation" and x["segments"]==60)
delta=abs(baseline["thermal_efficiency"]-seg60["thermal_efficiency"])
result={
    "kind":"Exploratory sensitivity of conceptual 12-state cycle",
    "validation_gate":"G2_OPEN",
    "coolprop_version":coolprop_version,
    "baseline":baseline,
    "delta_eta_absolute_30_vs_60_segments":delta,
    "cases":rows,
    "note":"Not a source-validated sensitivity study. Source paper reports a different complete EES plant with unreported states/geometry."
}
p=Path("evidence/generated/fr2016_sensitivity.json")
p.parent.mkdir(exist_ok=True,parents=True)
p.write_text(json.dumps(result,indent=2)+"\n")
print(json.dumps(result,indent=2))
