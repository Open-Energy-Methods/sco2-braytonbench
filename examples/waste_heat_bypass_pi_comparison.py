"""WP3 synthetic open-loop vs feedback bypass experiment.

An ideal-gas mathematical fixture, prescribed source loads and guessed UA,
wall capacity and PI gains are used. NOT a CARBOSOLA/real-CO2 control study.
"""
from dataclasses import asdict
import csv
import json
from pathlib import Path

from sco2_braytonbench import (
    CycleInputs, IdealGasFixture, PressureLosses,
)
from sco2_braytonbench.dynamic_whr import FiniteGasLoad, WallCycleEquipment
from sco2_braytonbench.control_whr import (
    SourceBypass, WallPI, control_performance, simulate_bypass_control,
)

DIR = Path("evidence/generated/v1_wp3")
DIR.mkdir(parents=True, exist_ok=True)

fluid = IdealGasFixture(cp=1000., gas_constant=200.)
cycle = CycleInputs(
    p1_pa=8e6, p4_pa=24e6, t1_k=310., t4_k=600.,
    mdot_kg_s=10., eta_compressor=.89, eta_turbine=.90,
    losses=PressureLosses(100e3,150e3,100e3,50e3),
    recuperator_ua_w_k=0., segments=6,
)
equipment = WallCycleEquipment(
    wall_capacity_j_k=2e6,
    gas_to_wall_ua_w_k=40e3,
    wall_to_co2_ua_w_k=25e3,
    gas_cp_j_kg_k=1100.,
    minimum_stack_temperature_k=360.,
    t4_bounds_k=(560.,760.),
    co2_heater_segments=6,
    root_scan_intervals=8,
)
actuator = SourceBypass(
    max_fraction=.85,
    max_rate_fraction_s=.025,
    minimum_active_mass_flow_kg_s=1.,
)
pi = WallPI(
    setpoint_temperature_k=700.,
    kp_fraction_k=.04,
    ki_fraction_k_s=.0025,
    bias_fraction=.15,
    tracking_gain_s=.2,
    integral_limit_fraction=1.0,
)
loads = tuple(
    FiniteGasLoad(850. if index < 9 else 880.,30.,5.)
    for index in range(18)
)
shared = {
    "props":fluid,
    "base_cycle":cycle,
    "equipment":equipment,
    "loads":loads,
    "actuator":actuator,
    "initial_wall_temperature_k":700.,
    "initial_bypass_fraction":.15,
    "setpoint_temperature_k":700.,
}
scenarios = {
    "fixed_bypass_open_loop": simulate_bypass_control(**shared),
    "wall_temperature_PI": simulate_bypass_control(**shared,controller=pi),
}
rows = []
metrics = {}
for name, results in scenarios.items():
    for index, row in enumerate(results):
        p = row.plant
        rows.append({
            "scenario":name,
            "interval":index,
            "time_s":row.time_end_s,
            "hot_source_temperature_k":loads[index].inlet_temperature_k,
            "source_total_mass_flow_kg_s":loads[index].mass_flow_kg_s,
            "bypass_fraction":row.bypass_fraction,
            "requested_fraction":row.requested_fraction,
            "active_gas_mass_flow_kg_s":row.active_gas_flow_kg_s,
            "diverted_gas_mass_flow_kg_s":row.diverted_gas_flow_kg_s,
            "bypass_rate_fraction_s":row.applied_rate_fraction_s,
            "PI_integral_fraction":row.integral_fraction_after,
            "wall_temperature_k":p.final_wall_temperature_k,
            "wall_setpoint_k":row.setpoint_temperature_k,
            "wall_error_k":row.end_error_k,
            "turbine_inlet_k":p.final.turbine_inlet_temperature_k,
            "net_shaft_power_w":p.final.cycle.net_w,
            "mixed_gas_outlet_k":row.mixed_gas_outlet_final_k,
            "mixed_gas_outlet_interval_mean_k":row.mixed_gas_outlet_mean_k,
            "gas_to_wall_energy_j":p.hot_gas_to_wall_energy_j,
            "wall_to_CO2_energy_j":p.wall_to_co2_energy_j,
            "cooler_energy_j":p.cooler_energy_j,
            "net_shaft_energy_j":p.net_shaft_energy_j,
            "wall_storage_energy_j":p.wall_stored_energy_j,
            "total_source_enthalpy_residual_j":row.source_energy_residual_j,
            "combined_energy_residual_j":row.combined_total_stream_residual_j,
        })
    metrics[name] = asdict(control_performance(results))
    scale = max(abs(metrics[name]["total_gas_to_wall_energy_j"]), 1.)
    assert abs(metrics[name]["total_energy_residual_j"]) < 1e-7*scale

assert len(rows) == 36
assert all(0. <= r["bypass_fraction"] <= actuator.max_fraction for r in rows)
assert all(abs(r["bypass_rate_fraction_s"]) <=
           actuator.max_rate_fraction_s+1e-12 for r in rows)

with (DIR/"control_trace.csv").open("w",newline="",encoding="utf-8") as handle:
    writer = csv.DictWriter(handle,fieldnames=list(rows[0]))
    writer.writeheader()
    writer.writerows(rows)

report = {
    "evidence_class":"synthetic ideal-gas dynamic wall and PI controller",
    "physically_traced_actuator":"fractional source hot-gas bypass with downstream cp mixing",
    "control_target":"wall_temperature_k",
    "controller_sign":"T_wall - setpoint => increase bypass when too hot",
    "full_CO2_pressure_or_inventory_dynamics":False,
    "is_CARBOSOLA_or_measured":False,
    "fixture": {
        "gas_cp_j_kg_k":fluid.cp,
        "gas_R_j_kg_k":fluid.gas_constant,
        "wall_capacity_j_k":equipment.wall_capacity_j_k,
        "gas_wall_ua_w_k":equipment.gas_to_wall_ua_w_k,
        "wall_CO2_ua_w_k":equipment.wall_to_co2_ua_w_k,
        "total_source_mass_flow_kg_s":30.,
        "source_temperature_k_first_half":850.,
        "source_temperature_k_second_half":880.,
        "initial_wall_temperature_k":700.,
        "wall_setpoint_temperature_k":700.,
        "bypass_initial_fraction":.15,
        "actuator":asdict(actuator),
        "PI":asdict(pi),
        "time_step_s":5.,
    },
    "metrics_definition":{
        "sample_endpoint_rmse_k":"duration-weighted RMS of *sample-endpoint* errors, not continuous-time RMSE",
        "absolute_error_trapezoid_k_s":"trapezoid of |Twall-setpoint| across sample boundaries, approximation not exact integral",
        "net_shaft_energy_j":"time-integrated quasi-steady cycle net shaft power, not an electrical generator output",
    },
    "scenarios":metrics,
    "limitations":[
        "ideal-gas numerical fixture, not CO2",
        "unmeasured wall capacitance and two installed UAs",
        "bypass fraction equals mass split; no valve Cv, pressure regulation or flow-map",
        "valve position is sampled/held each load interval with a finite rate bound",
        "PI gains hypothetical and not tuned from identified real plant",
        "fixed CO2 compressor-inlet state, pressure, mass flow, recuperator and machine efficiencies",
        "no full CO2 inventory, compressor/turbine speed dynamics, pressure safety interlocks or experimental validation",
        "no claim that PI universally outperforms fixed bypass or is optimal",
    ],
}
with (DIR/"control_summary.json").open("w",encoding="utf-8") as handle:
    json.dump(report,handle,indent=2)
    handle.write("\n")
print(json.dumps(report,indent=2))
