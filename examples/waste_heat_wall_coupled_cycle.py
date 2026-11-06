"""Reproducible WP2b SYNTHETIC industrial-waste-heat disturbance.

The CO2-like working-fluid fixture here is an artificial constant-cp
ideal gas for deterministic analytical tests. The code also accepts
CoolPropCO2, but this example is NOT a measured CARBOSOLA power cycle.
T1, pressures, shaft efficiencies and CO2 mass flow are quasi-steady.
"""
import csv
import json
from pathlib import Path

from sco2_braytonbench import (
    CycleInputs, IdealGasFixture, PressureLosses,
)
from sco2_braytonbench.dynamic_whr import (
    FiniteGasLoad, WallCycleEquipment, simulate_wall_coupled_cycle,
)

DIR = Path("evidence/generated/v1_wp2b")
DIR.mkdir(parents=True, exist_ok=True)
fluid = IdealGasFixture(cp=1000., gas_constant=200.)
cycle = CycleInputs(
    p1_pa=8e6, p4_pa=24e6, t1_k=310., t4_k=600.,
    mdot_kg_s=10., eta_compressor=.89, eta_turbine=.90,
    losses=PressureLosses(100e3, 150e3, 100e3, 50e3),
    recuperator_ua_w_k=0., segments=6,
)
device = WallCycleEquipment(
    wall_capacity_j_k=2e6,
    gas_to_wall_ua_w_k=40e3,
    wall_to_co2_ua_w_k=25e3,
    gas_cp_j_kg_k=1100.,
    minimum_stack_temperature_k=360.,
    t4_bounds_k=(560.,760.),
    co2_heater_segments=6,
    root_scan_intervals=8,
)
initial_wall_k = 700.
# 5 s intervals: steady -> cooler waste source -> hotter reduced flow.
loads = [
    *[FiniteGasLoad(850., 30., 5.) for _ in range(3)],
    *[FiniteGasLoad(815., 30., 5.) for _ in range(3)],
    *[FiniteGasLoad(875., 24., 5.) for _ in range(3)],
]
baseline_loads = [FiniteGasLoad(850., 30., 5.) for _ in loads]
scenarios = {
    "constant_source": simulate_wall_coupled_cycle(
        fluid, cycle, device, initial_wall_k, baseline_loads,
    ),
    "variable_source": simulate_wall_coupled_cycle(
        fluid, cycle, device, initial_wall_k, loads,
    ),
}

rows = []
summaries = {}
for name, records in scenarios.items():
    for record in records:
        rows.append({
            "scenario": name,
            "time_start_s": record.time_start_s,
            "time_end_s": record.time_end_s,
            "source_temperature_k": record.input_load.inlet_temperature_k,
            "source_mass_flow_kg_s": record.input_load.mass_flow_kg_s,
            "wall_initial_k": record.initial_wall_temperature_k,
            "wall_final_k": record.final_wall_temperature_k,
            "gas_exit_final_k": record.final.hot_gas_outlet_temperature_k,
            "turbine_inlet_final_k": record.final.turbine_inlet_temperature_k,
            "compressor_inlet_final_k": record.final.cycle.states[0].t,
            "net_shaft_power_final_w": record.final.cycle.net_w,
            "gas_to_wall_energy_j": record.hot_gas_to_wall_energy_j,
            "wall_to_co2_energy_j": record.wall_to_co2_energy_j,
            "cooler_energy_j": record.cooler_energy_j,
            "net_shaft_energy_j": record.net_shaft_energy_j,
            "wall_storage_energy_j": record.wall_stored_energy_j,
            "wall_residual_j": record.wall_energy_residual_j,
            "combined_residual_j": record.combined_gas_cycle_wall_residual_j,
        })
    totals = {
        "gas_energy_j": sum(r.hot_gas_to_wall_energy_j for r in records),
        "co2_heater_energy_j": sum(r.wall_to_co2_energy_j for r in records),
        "cooler_energy_j": sum(r.cooler_energy_j for r in records),
        "net_shaft_energy_j": sum(r.net_shaft_energy_j for r in records),
        "wall_storage_energy_j": sum(r.wall_stored_energy_j for r in records),
    }
    totals["combined_energy_residual_j"] = (
        totals["gas_energy_j"]
        - totals["cooler_energy_j"]
        - totals["net_shaft_energy_j"]
        - totals["wall_storage_energy_j"]
    )
    summaries[name] = {
        "interval_count": len(records),
        "elapsed_s": records[-1].time_end_s,
        "final_wall_temperature_k": records[-1].final_wall_temperature_k,
        "final_turbine_inlet_temperature_k":
            records[-1].final.turbine_inlet_temperature_k,
        "final_net_shaft_power_w": records[-1].final.cycle.net_w,
        **totals,
    }
    scale = max(abs(totals["gas_energy_j"]), 1.)
    assert abs(totals["combined_energy_residual_j"]) < 1e-7 * scale

assert summaries["constant_source"]["final_wall_temperature_k"] != (
    summaries["variable_source"]["final_wall_temperature_k"]
)

columns = list(rows[0])
with (DIR / "scenario_trace.csv").open("w", newline="", encoding="utf-8") as handle:
    writer = csv.DictWriter(handle, fieldnames=columns)
    writer.writeheader()
    writer.writerows(rows)

report = {
    "type": "WP2b finite gas->thermal wall->quasi-steady Brayton fixture",
    "evidence_class": "hypothetical ideal-gas numeric/analytical example",
    "code_scope": "heat-storage thermal ODE + algebraic six-state cycle",
    "is_carbsosola_or_measured_CO2": False,
    "co2_mass_and_pressure_dynamic_state": False,
    "thermal_capacity_j_k": device.wall_capacity_j_k,
    "gas_wall_ua_w_k": device.gas_to_wall_ua_w_k,
    "wall_co2_ua_w_k": device.wall_to_co2_ua_w_k,
    "working_fluid_fixture_cp_j_kg_k": fluid.cp,
    "working_fluid_fixture_gas_constant_j_kg_k": fluid.gas_constant,
    "source_gas_cp_j_kg_k": device.gas_cp_j_kg_k,
    "fixed_CO2_inlet_temperature_k": cycle.t1_k,
    "fixed_CO2_mass_flow_kg_s": cycle.mdot_kg_s,
    "limitations": [
        "synthetic source loads, UAs, wall capacity and properties",
        "no finite-coolant G3.2 dynamics or thermally identified hardware",
        "CO2 pressure, flow and cold inlet prescribed throughout scenario",
        "turbomachinery and recuperator re-solved as quasi-steady algebraic states",
        "no actuator, PI, MPC, measured facility data or CARBOSOLA calibration",
    ],
    "scenarios": summaries,
}
with (DIR / "scenario_summary.json").open("w", encoding="utf-8") as handle:
    json.dump(report, handle, indent=2)
    handle.write("\n")
print(json.dumps(report, indent=2))
