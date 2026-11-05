"""Real-CO2, source-coupled *grid screening*, NOT an MK2014 GA replication.

This deliberately tests power-max vs thermal-efficiency-max objectives
over the same finite set of feasible CO2-cycle designs. Only selected
variables are sampled (T_turbine_in, CO2 mass flow); no global optimum
or accurate plant design is asserted.

Run: python scripts/whr_design_screen.py
"""
from __future__ import annotations

import csv
import json
import platform
from pathlib import Path
from CoolProp import __version__ as coolprop_version
from sco2_braytonbench import CoolPropCO2,CycleInputs,PressureLosses
from sco2_braytonbench.whr import WasteGasSource,screen_whr_designs

# The 100 kg/s gas supply is taken as the same order-of-magnitude framing
# used by Mohagheghi & Kapat (2014), but the other values are INDEPENDENT
# screening assumptions. This is NOT their reproduced reference case.
source=WasteGasSource(
    inlet_temperature_k=760.0,
    mass_flow_kg_s=100.,
    cp_j_kg_k=1100.,   # constant-cp air-like test approximation
    minimum_stack_temperature_k=360.,
    maximum_heater_ua_w_k=1_200_000.,
    minimum_heater_approach_k=10.,
    dead_state_temperature_k=300.,
    segments=12,
)
loss=PressureLosses(
    cold_recup=100e3,heater=150e3,hot_recup=100e3,cooler=50e3
)
# Explicit component/pipe lumping: NOT the MK2014 2% FPD convention.
temperatures_k=(550.,600.,650.,700.,770.)
mass_flows_kg_s=(20.,40.,70.,100.)
candidates=[
    CycleInputs(
       p1_pa=8.5e6,p4_pa=24e6,t1_k=310.,
       t4_k=T4,mdot_kg_s=mdot,
       eta_compressor=.89,eta_turbine=.90,losses=loss,
       recuperator_effectiveness=None,
       recuperator_ua_w_k=200e3,segments=12
    )
    for T4 in temperatures_k for mdot in mass_flows_kg_s
]
screen=screen_whr_designs(CoolPropCO2(),source,candidates)

def point_data(p):
    return {
        "turbine_inlet_k":p.inputs.t4_k,
        "co2_mdot_kg_s":p.inputs.mdot_kg_s,
        "net_shaft_power_w":p.net_shaft_power_w,
        "thermal_efficiency":p.cycle_thermal_efficiency,
        "gross_turbine_w":p.cycle.turbine_w,
        "compressor_w":p.cycle.compressor_w,
        "heat_input_w":p.cycle.heater_w,
        "cooler_heat_w":p.cycle.cooler_w,
        "recuperator_duty_w":p.cycle.recuperator.q_w,
        "recuperator_minimum_dT_k":p.cycle.recuperator.min_approach_k,
        "recuperator_UA_required_w_k":p.cycle.recuperator.required_ua_w_k,
        "heater_UA_required_w_k":p.heater.required_ua_w_k,
        "heater_minimum_dT_k":p.heater.min_approach_k,
        "gas_stack_temperature_k":p.heater.gas_out_k,
        "available_source_heat_w":p.source_available_w,
        "utilized_source_heat_fraction":p.heat_utilization,
        "gas_exergy_consumed_w":p.source_exergy_consumed_w,
        "cycle_first_law_residual_w":p.cycle.first_law_residual_w,
        "gas_heater_first_law_residual_w":p.first_law_combined_residual_w
    }

rows=[]
for x in screen.feasible:
    rows.append(dict(status="feasible",reason="",**point_data(x)))
for x in screen.rejected:
    rows.append(dict(status="rejected",reason=x.reason,
        turbine_inlet_k=x.inputs.t4_k,co2_mdot_kg_s=x.inputs.mdot_kg_s))
outdir=Path("evidence/generated")
outdir.mkdir(parents=True,exist_ok=True)
with (outdir/"whr_grid_matrix.csv").open("w",newline="") as stream:
    fieldnames=["status","reason","turbine_inlet_k","co2_mdot_kg_s"] + [
        k for k in point_data(screen.feasible[0])
        if k not in ("turbine_inlet_k","co2_mdot_kg_s")]
    writer=csv.DictWriter(stream,fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(rows)

best_power=point_data(screen.maximum_shaft_power)
best_eta=point_data(screen.maximum_cycle_efficiency)
report={
    "study_class":"independent exploratory 6-state real-CO2 WHR grid",
    "global_optimum_or_MK2014_replication":False,
    "CoolProp":coolprop_version,"python":platform.python_version(),
    "source_assumptions":{
        "waste_gas_in_K":source.inlet_temperature_k,
        "waste_gas_kg_s":source.mass_flow_kg_s,
        "gas_cp_J_kg_K":source.cp_j_kg_k,
        "stack_floor_K":source.minimum_stack_temperature_k,
        "heater_UA_sizing_limit_W_K":source.maximum_heater_ua_w_k,
        "minimum_heater_approach_K":source.minimum_heater_approach_k,
        "dead_state_K":source.dead_state_temperature_k,
    },
    "cycle_assumptions":{
        "P1_Pa":8.5e6,"P4_Pa":24e6,"T1_K":310.,
        "eta_compressor":.89,"eta_turbine":.90,
        "component_pressure_losses_Pa":{
            "cold_recup":loss.cold_recup,"heater":loss.heater,
            "hot_recup":loss.hot_recup,"cooler":loss.cooler},
        "recuperator_fixed_UA_W_K":200e3,
        "recuperator_segments":12,
        "gas_heater_segments":source.segments,
        "pressure_loss_method":"explicit independent lumped dP values, not MK2014 FPD",
    },
    "decision_grid":{
        "turbine_temperature_K":list(temperatures_k),
        "working_fluid_mdot_kg_s":list(mass_flows_kg_s)},
    "n_evaluated":screen.evaluated_count,
    "n_feasible":len(screen.feasible),
    "n_rejected":len(screen.rejected),
    "rejects":[{"turbine_inlet_K":x.inputs.t4_k,
        "co2_mass_flow_kg_s":x.inputs.mdot_kg_s,"reason":x.reason}
        for x in screen.rejected],
    "best_net_shaft_power":best_power,
    "best_thermal_efficiency":best_eta,
    "different_designs_selected":(
        (best_power["turbine_inlet_k"],best_power["co2_mdot_kg_s"])!=
        (best_eta["turbine_inlet_k"],best_eta["co2_mdot_kg_s"])),
    "limitations":[
        "This finite grid is not a genetic algorithm or global optimizer.",
        "Turbine inlet temperature is an externally prescribed candidate.",
        "Main heater UA is a design sizing upper bound, not a fixed installed UA equality.",
        "Recuperator UA is fixed, but compressor and turbine are constant efficiency; no maps.",
        "Pressure drops are fixed absolute values, not the source-paper fractional drops.",
        "Waste gas is constant-cp; no detailed waste-gas composition or emissions model.",
        "No cooling-water UA/pumping, generator loss, bypass dynamics, material limits or cost.",
        "No RRC topology implemented or MK2014 Figure 3 quantitative reproduction.",
        "Not a CARBOSOLA/HZDR plant prediction or experimental validation."
    ],
    "validation_gates":{"G3":"PARTIAL_EXPLORATORY","G2":"OPEN"}
}
(outdir/"whr_design_screen.json").write_text(json.dumps(report,indent=2)+"\n")
print(json.dumps({k:v for k,v in report.items()
  if k not in ("rejects","limitations")},indent=2))
print("Rejected:",json.dumps(report["rejects"],indent=2))
print("Wrote evidence/generated/whr_design_screen.json and whr_grid_matrix.csv")

# Scientific robustness extension. The limits below are independent,
# hypothetical design constraints; they are NOT the paper's 10-40 K
# terminal-dT decision variable or a published cooler sizing constraint.
from dataclasses import replace
from sco2_braytonbench.whr import PlantDesignLimits, evaluate_whr_design
limits=PlantDesignLimits(
    minimum_recuperator_approach_k=10.,
    maximum_cooler_duty_w=15e6,
)
constrained=screen_whr_designs(CoolPropCO2(),source,candidates,limits=limits)

# Finer segmentation at both originally selected operating points.
# Changing n does not rescan the design grid: evaluate identical points
# to distinguish mesh sensitivity from movement of the optimum.
refinements={}
for label,initial in (
    ("maximum_shaft_power",screen.maximum_shaft_power),
    ("maximum_cycle_efficiency",screen.maximum_cycle_efficiency),
):
    points=[]
    for n in (12,24,48):
        x=evaluate_whr_design(
            CoolPropCO2(),
            replace(initial.inputs,segments=n),
            replace(source,segments=n),
        )
        points.append({
            "segments":n,
            "net_shaft_power_w":x.net_shaft_power_w,
            "cycle_thermal_efficiency":x.cycle_thermal_efficiency,
            "recuperator_minimum_approach_k":x.cycle.recuperator.min_approach_k,
            "heater_minimum_approach_k":x.heater.min_approach_k,
            "heater_UA_required_w_k":x.heater.required_ua_w_k,
            "stack_temperature_k":x.heater.gas_out_k,
        })
    refinements[label]={
        "T4_K":initial.inputs.t4_k,
        "mdot_CO2_kg_s":initial.inputs.mdot_kg_s,
        "mesh_points":points,
        "net_shaft_power_change_rel_24_to_48":abs(
            points[2]["net_shaft_power_w"]-points[1]["net_shaft_power_w"]
        )/max(points[2]["net_shaft_power_w"],1.),
        "minimum_heater_approach_change_K_24_to_48":abs(
            points[2]["heater_minimum_approach_k"]-
            points[1]["heater_minimum_approach_k"]
        ),
    }
robustness={
    "type":"exploratory WHR feasibility and mesh refinement",
    "source_model_reproduction":False,
    "baseline_power_max":best_power,
    "baseline_efficiency_max":best_eta,
    "additional_limits":{
        "minimum_internal_recuperator_approach_K":limits.minimum_recuperator_approach_k,
        "maximum_cooler_thermal_duty_W":limits.maximum_cooler_duty_w,
        "note":"Independent hypothetical constraints, not MK2014 terminal dT or source-reported cooling design"},
    "constrained_n_feasible":len(constrained.feasible),
    "constrained_n_rejected":len(constrained.rejected),
    "constrained_power_max":point_data(constrained.maximum_shaft_power),
    "constrained_efficiency_max":point_data(constrained.maximum_cycle_efficiency),
    "refinement":refinements,
    "interpretation":"Optimum selection is grid- and constraint-dependent. These results do not close industrial validation gate G3.",
}
(outdir/"whr_robustness.json").write_text(
    json.dumps(robustness,indent=2)+"\n")
print("ROBUSTNESS",json.dumps({
    "constrained_n_feasible":robustness["constrained_n_feasible"],
    "constrained_n_rejected":robustness["constrained_n_rejected"],
    "constrained_power_max":robustness["constrained_power_max"],
    "constrained_efficiency_max":robustness["constrained_efficiency_max"],
    "refinement":robustness["refinement"]
},indent=2))
print("Wrote evidence/generated/whr_robustness.json")
