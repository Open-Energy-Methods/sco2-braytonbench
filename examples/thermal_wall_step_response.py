"""Generate a reproducible G4-0 SYNTHETIC thermal wall step-response fixture.

No CO2 inventory, turbine/shaft dynamics, pump/fan parasitic work,
physical controls, calibrated conductance or CARBOSOLA measurements.
"""
import csv
import json
from pathlib import Path

from sco2_braytonbench.thermal_dynamics import (
    ThermalStepInput, ThermalWall, simulate_thermal_wall,
)

HERE = Path("evidence/generated/v1_thermal_wall")
HERE.mkdir(parents=True, exist_ok=True)

wall = ThermalWall(
    capacity_j_k=500_000.0,
    hot_conductance_w_k=4_000.0,
    cold_conductance_w_k=2_000.0,
)
initial_wall_temperature_k = 520.0
profile = [
    ThermalStepInput(hot, 400.0, 15.0)
    for hot in ([650.0] * 4 + [620.0] * 4 + [680.0] * 4)
]
records = simulate_thermal_wall(wall, initial_wall_temperature_k, profile)

trace = HERE / "thermal_wall_trace.csv"
columns = [
    "time_start_s", "time_end_s", "hot_reservoir_temperature_k",
    "cold_reservoir_temperature_k", "initial_wall_temperature_k",
    "final_wall_temperature_k", "mean_wall_temperature_k",
    "hot_energy_j", "cold_energy_j", "stored_energy_j",
    "energy_residual_j",
]
with trace.open("w", newline="", encoding="utf-8") as handle:
    writer = csv.DictWriter(handle, fieldnames=columns)
    writer.writeheader()
    for source, record in zip(profile, records):
        writer.writerow({
            "time_start_s": record.time_start_s,
            "time_end_s": record.time_end_s,
            "hot_reservoir_temperature_k": source.hot_temperature_k,
            "cold_reservoir_temperature_k": source.cold_temperature_k,
            "initial_wall_temperature_k": record.initial_wall_temperature_k,
            "final_wall_temperature_k": record.final_wall_temperature_k,
            "mean_wall_temperature_k": record.mean_wall_temperature_k,
            "hot_energy_j": record.hot_energy_j,
            "cold_energy_j": record.cold_energy_j,
            "stored_energy_j": record.stored_energy_j,
            "energy_residual_j": record.energy_residual_j,
        })

totals = {
    "hot_energy_j": sum(r.hot_energy_j for r in records),
    "cold_energy_j": sum(r.cold_energy_j for r in records),
    "stored_energy_j": sum(r.stored_energy_j for r in records),
}
totals["energy_residual_j"] = (
    totals["hot_energy_j"] - totals["cold_energy_j"] - totals["stored_energy_j"]
)
report = {
    "model": "analytical_single_thermal_wall_control_volume",
    "status": "synthetic_thermal_fixture_NOT_CO2_Brayton_transient",
    "description": "exact piecewise-constant two-reservoir thermal-wall solution",
    "assumed_parameters": {
        "capacity_j_k": wall.capacity_j_k,
        "hot_conductance_w_k": wall.hot_conductance_w_k,
        "cold_conductance_w_k": wall.cold_conductance_w_k,
        "initial_wall_temperature_k": initial_wall_temperature_k,
        "interval_duration_s": 15.0,
        "hot_temperature_profile_k": [r.hot_temperature_k for r in profile],
        "cold_reservoir_temperature_k": 400.0,
    },
    "results": {
        "interval_count": len(records),
        "total_duration_s": records[-1].time_end_s,
        "final_wall_temperature_k": records[-1].final_wall_temperature_k,
        **totals,
    },
    "limitations": [
        "no CO2 fluid-inventory or pressure/mass-flow dynamics",
        "constant assumed thermal conductances and wall capacity",
        "reservoir temperatures prescribed, not finite gas/coolant stream balances",
        "not coupled to BraytonBench steady cycle",
        "not a source-dependent hardware calibration or CARBOSOLA prediction",
    ],
}
with (HERE / "thermal_wall_summary.json").open("w", encoding="utf-8") as handle:
    json.dump(report, handle, indent=2)
    handle.write("\n")

scale = max(*(abs(x) for x in totals.values()), 1.0)
assert abs(totals["energy_residual_j"]) <= 1e-10 * scale
assert records[-1].time_end_s == 180.0
print(json.dumps(report, indent=2))
