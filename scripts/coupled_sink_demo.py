"""Dual-installed-UA steady-state CO2 demonstration, not an industrial twin.

The two UAs are synthetically sized from one specified steady state,
then held fixed when coolant inlet T changes. Result is 2 independent
steady roots; no actuator/thermal inventory/time dynamics is modelled.
"""
from dataclasses import replace
from pathlib import Path
import json,platform
from CoolProp import __version__ as coolprop_version
from sco2_braytonbench import CycleInputs,CoolPropCO2,PressureLosses
from sco2_braytonbench.whr import WasteGasSource,evaluate_whr_design
from sco2_braytonbench.cooler import CoolerSink,rate_cooler
from sco2_braytonbench.coupled_plant import solve_coupled_plant
from sco2_braytonbench.offdesign import FlowScaling

f=CoolPropCO2()
base=CycleInputs(
    p1_pa=8.5e6,p4_pa=24e6,t1_k=310.,t4_k=650.,
    mdot_kg_s=20.,eta_compressor=.89,eta_turbine=.90,
    losses=PressureLosses(100e3,150e3,100e3,50e3),
    recuperator_effectiveness=None,recuperator_ua_w_k=200e3,
    segments=5
)
source=WasteGasSource(inlet_temperature_k=800.,
    mass_flow_kg_s=100.,cp_j_kg_k=1100.,
    cp_slope_j_kg_k2=.20,cp_reference_temperature_k=300.,
    minimum_stack_temperature_k=350.,
    maximum_heater_ua_w_k=1.2e6,segments=5)
sink=CoolerSink(inlet_temperature_k=285.,
    mass_flow_kg_s=75.,cp_j_kg_k=4180.,
    installed_ua_w_k=10000.,
    maximum_outlet_temperature_k=340.,segments=5)

nom=evaluate_whr_design(f,base,source)
rated=rate_cooler(f,nom.cycle.states[5],nom.cycle.states[0],20.,sink)
sink=replace(sink,installed_ua_w_k=rated.required_ua_w_k)
installed_hot=nom.heater.required_ua_w_k

def point(label,sink_case):
    x=solve_coupled_plant(
        f,replace(base,t1_k=320.,t4_k=600.),source,sink_case,
        installed_heater_ua_w_k=installed_hot,
        t1_bounds_k=(305.,320.),t4_bounds_k=(625.,685.),
        outer_scan_intervals=3,outer_max_iterations=13,
        cooler_ua_tolerance_relative=8e-4,t1_tolerance_k=.12,
        inner_scan_intervals=4,inner_max_iterations=18,
        inner_ua_tolerance_relative=2e-4,inner_t4_tolerance_k=.07)
    return {
        "case":label,"coolant_inlet_temperature_k":sink_case.inlet_temperature_k,
        "compressor_inlet_temperature_k":x.compressor_inlet_temperature_k,
        "turbine_inlet_temperature_k":x.turbine_inlet_temperature_k,
        "source_gas_outlet_temperature_k":x.heater.stack_temperature_k,
        "coolant_outlet_temperature_k":x.cooler.coolant_outlet_k,
        "net_shaft_power_w":x.net_shaft_power_w,
        "cycle_thermal_efficiency":x.heater.point.cycle_thermal_efficiency,
        "cooler_heat_rejected_w":x.cooler.rejected_heat_w,
        "heater_heat_absorbed_w":x.heater.point.cycle.heater_w,
        "cooler_installed_UA_w_k":sink_case.installed_ua_w_k,
        "cooler_calculated_UA_w_k":x.cooler.required_ua_w_k,
        "cooler_UA_residual_relative":x.cooler_ua_residual_relative,
        "heater_installed_UA_w_k":installed_hot,
        "heater_calculated_UA_w_k":x.heater.calculated_heater_ua_w_k,
        "heater_UA_residual_relative":x.heater.ua_residual_relative,
        "cooler_entropy_generation_w_k":x.cooler.entropy_generation_w_k,
        "cooler_first_law_residual_w":x.cooler.coolant_energy_residual_w,
        "gas_first_law_residual_w":x.heater.point.first_law_combined_residual_w,
        "cycle_first_law_residual_w":x.heater.point.cycle.first_law_residual_w,
        "outer_iterations":x.outer_iterations,
        "outer_evaluations":x.outer_evaluations,
        "inner_iterations_last_state":x.heater.iterations,
        "inner_evaluations_last_state":x.heater.evaluations,
    }

cases=[point("coolant_285_K",sink),point(
    "coolant_287_K_same_installed_UAs",
    replace(sink,inlet_temperature_k=287.))]
scaling=FlowScaling(reference_mass_flow_kg_s=20.,
    pressure_loss_exponent=2.,compressor_efficiency_penalty=.02,
    turbine_efficiency_penalty=.02,
    min_relative_flow=.5,max_relative_flow=1.5)
scaled={str(m):{
    "mdot_kg_s":m,
    "heater_dP_pa":scaling.at_flow(base,m).losses.heater,
    "cooler_dP_pa":scaling.at_flow(base,m).losses.cooler,
    "eta_c":scaling.at_flow(base,m).eta_compressor,
    "eta_t":scaling.at_flow(base,m).eta_turbine}
    for m in (10.,20.,30.)}
out={
    "kind":"finite_source_and_coolant_dual_UA_steady_rating",
    "CoolProp_version":coolprop_version,
    "python":platform.python_version(),
    "source":"independently assumed synthetic example, not MK2014 or HZDR measurements",
    "hot_gas_cp_at_300_K_J_kg_K":source.cp_j_kg_k,
    "hot_gas_cp_slope_J_kg_K2":source.cp_slope_j_kg_k2,
    "heater_UA_sized_from_nominal_w_k":installed_hot,
    "cooler_UA_sized_from_nominal_w_k":sink.installed_ua_w_k,
    "two_fixed_UA_solutions":cases,
    "flow_loss_scenario_not_calibrated":scaled,
    "flow_law_applied_to_coupled_demo":False,
    "numerical_limitations":"only 5 segments and one locally bracketed root interval",
    "gate":"G3_PARTIAL_NOT_INDUSTRIAL_VALIDATION",
}
p=Path("evidence/generated/g32_coupled_cooler.json")
p.parent.mkdir(parents=True,exist_ok=True)
p.write_text(json.dumps(out,indent=2)+"\n")
print(json.dumps(out,indent=2))
