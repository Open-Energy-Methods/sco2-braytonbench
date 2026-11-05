"""Reproducible fixed-UA CO2 cycle + finite-source coupling demonstration.

The installed heater UA is DERIVED FROM one feasible nominal point
to provide a traceable, verifiable manufactured-design target. It is
then HELD FIXED when gas inlet temperature changes, and T4 is solved
rather than prescribed. This is a numerical software experiment,
NOT a calibrated industrial heater, and NOT MK2014 published data.
"""
from __future__ import annotations

from dataclasses import replace
import json
import platform
from pathlib import Path

from CoolProp import __version__ as coolprop_version
from sco2_braytonbench import (
    CoolPropCO2,CycleInputs,PressureLosses
)
from sco2_braytonbench.fixed_ua import solve_fixed_ua_whr
from sco2_braytonbench.whr import WasteGasSource,evaluate_whr_design

f=CoolPropCO2()
base=CycleInputs(
    p1_pa=8.5e6,p4_pa=24e6,t1_k=310.,t4_k=650.,
    mdot_kg_s=20.,eta_compressor=.89,eta_turbine=.90,
    losses=PressureLosses(100e3,150e3,100e3,50e3),
    recuperator_effectiveness=None,
    recuperator_ua_w_k=200e3,segments=12
)
gas=WasteGasSource(inlet_temperature_k=800.,
    mass_flow_kg_s=100.,cp_j_kg_k=1100.,
    minimum_stack_temperature_k=350.,
    maximum_heater_ua_w_k=1.2e6,
    minimum_heater_approach_k=10.,
    dead_state_temperature_k=300.,segments=12
)
nominal=evaluate_whr_design(f,base,gas)
installed=nominal.heater.required_ua_w_k

def measure(name,inp,src):
    out=solve_fixed_ua_whr(
        f,inp,src,installed_heater_ua_w_k=installed,
        turbine_inlet_bounds_k=(610.,695.),
        scan_intervals=8,max_iterations=26,
        tolerance_ua_relative=1e-4,
        tolerance_temperature_k=.03)
    return {
        "case":name,
        "source_gas_inlet_temperature_k":src.inlet_temperature_k,
        "source_gas_mdot_kg_s":src.mass_flow_kg_s,
        "working_fluid_mdot_kg_s":inp.mdot_kg_s,
        "solved_turbine_inlet_temperature_k":out.turbine_inlet_temperature_k,
        "gas_outlet_temperature_k":out.stack_temperature_k,
        "installed_heater_ua_w_k":installed,
        "calculated_ua_w_k":out.calculated_heater_ua_w_k,
        "ua_residual_w_k":out.ua_residual_w_k,
        "ua_residual_relative":out.ua_residual_relative,
        "source_exergy_consumed_w":out.point.source_exergy_consumed_w,
        "net_shaft_power_w":out.point.net_shaft_power_w,
        "cycle_efficiency":out.point.cycle_thermal_efficiency,
        "heat_absorbed_w":out.point.cycle.heater_w,
        "gas_to_co2_first_law_residual_w":out.point.first_law_combined_residual_w,
        "cycle_first_law_residual_w":out.point.cycle.first_law_residual_w,
        "minimum_heater_approach_k":out.point.heater.min_approach_k,
        "minimum_recuperator_approach_k":out.point.cycle.recuperator.min_approach_k,
        "evaluations":out.evaluations,
        "iterations":out.iterations,
        "bracket_k":list(out.root_bracket_k),
    }

cases=[
    measure("nominal_gas_800_K",base,gas),
    measure("hotter_gas_810_K_same_installed_UA",base,
            replace(gas,inlet_temperature_k=810.)),
]
assert abs(cases[0]["solved_turbine_inlet_temperature_k"]-650.)<.1
assert cases[1]["solved_turbine_inlet_temperature_k"]>cases[0]["solved_turbine_inlet_temperature_k"]

result={
    "type":"reduced_RC_6state_fixed_installed_UA_coupled_rating",
    "CoolProp_version":coolprop_version,
    "Python":platform.python_version(),
    "source_provenance":"independent illustrative design, NOT published MK2014 numerical results",
    "base_turbine_inlet_t_for_UA_sizing_k":650.,
    "installed_heater_ua_w_k":installed,
    "heating_source":"constant_cp_air_like_gas",
    "recuperator_UA_w_k":base.recuperator_ua_w_k,
    "turbomachinery":"constant_isentropic_efficiency",
    "pressure_drops":"fixed_absolute_Pa",
    "stack_floor_k":gas.minimum_stack_temperature_k,
    "heating_minimum_pinching_k":gas.minimum_heater_approach_k,
    "cases":cases,
    "limitations":[
        "heater UA sized at initial assumed nominal point; not measured",
        "no bypass, variable UA or reduced heat exchanger area",
        "fixed pressure drops and efficiencies across off-design",
        "gas constant cp and no source pressure-exergy or composition",
        "cooler sink fixed via compressor inlet, not installed cooling-UA",
        "not CARBOSOLA or MK2014 benchmark replication",
        "not a dynamic transient control simulation",
        "root search only examines declared T4 interval; may miss other roots"
    ],
    "verification_status":"exploratory_software_integration_not_industrial_validation"
}
out=Path("evidence/generated/fixed_ua_coupled_demo.json")
out.parent.mkdir(parents=True,exist_ok=True)
out.write_text(json.dumps(result,indent=2)+"\n")
print(json.dumps(result,indent=2))
