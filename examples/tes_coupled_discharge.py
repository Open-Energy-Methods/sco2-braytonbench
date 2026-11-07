#!/usr/bin/env python3
"""Reproducible ONE-PASS TES outlet to existing ideal-gas Brayton cycle.

The bed is evolved for 0.5 s; the cycle is a quasi-steady snapshot at
the FINAL outlet state. Interval [J] and snapshot [W] evidence are
separate and must never be summed as though measured concurrently.
"""
import json
from pathlib import Path

from sco2_braytonbench import CycleInputs, IdealGasFixture, PressureLosses
from sco2_braytonbench.thermal_storage import PackedBedSpec, PackedBedState
from sco2_braytonbench.tes_coupling import advance_storage_to_cycle_snapshot


def main():
    s = PackedBedSpec(
        length_m=1, area_m2=1, porosity=.4,
        fluid_density_kg_m3=10, fluid_cp_j_kg_k=1100,
        solid_density_kg_m3=2600, solid_cp_j_kg_k=800,
        interphase_hv_w_m3_k=30000, n_cells=16
    )
    c = CycleInputs(
        p1_pa=8e6, p4_pa=24e6, t1_k=310, t4_k=670,
        mdot_kg_s=10, eta_compressor=.89, eta_turbine=.9,
        losses=PressureLosses(100e3, 150e3, 100e3, 50e3),
        recuperator_ua_w_k=0., segments=6
    )
    x = advance_storage_to_cycle_snapshot(
        IdealGasFixture(cp=1000,gas_constant=200),
        c,s,PackedBedState.uniform(s,850,850),
        bed_inlet_k=650,mass_flow_kg_s=30,duration_s=.5,
        minimum_gas_heater_exit_k=600,maximum_heater_ua_w_k=200000,
        heater_segments=6,
    )
    out = {
        "evidence_class": "synthetic-single-pass-open-htf-quasi-steady-cycle",
        "source_independent_facility": True,
        "no_claims": ["CIC energiGUNE experimental data","CARBOSOLA data",
                      "closed recirculation","dynamic CO2 mass inventory",
                      "actual generator electricity"],
        "bed_interval": {
            "duration_s": .5,
            "energy_boundary_j": x.bed_step.energy_boundary_j,
            "energy_change_j": x.bed_step.energy_change_j,
            "first_law_residual_j": x.bed_step.conservation_residual_j,
        },
        "instantaneous_end_of_interval": {
            "bed_inlet_k": x.bed_feed_temperature_k,
            "bed_outlet_k": x.bed_outlet_temperature_k,
            "heater_outlet_k": x.heater_gas_exit_temperature_k,
            "bed_storage_inventory_rate_w": x.storage_inventory_rate_w,
            "co2_heater_rate_w": x.heater_to_co2_rate_w,
            "net_open_stream_boundary_rate_w": x.net_stream_boundary_rate_w,
            "cooler_rate_w": x.cooler_rate_w,
            "net_shaft_rate_w": x.shaft_rate_w,
            "combined_first_law_residual_w": x.combined_instantaneous_residual_w,
        },
    }
    p=Path("evidence/generated/tes_v05")
    p.mkdir(parents=True,exist_ok=True)
    (p/"synthetic_one_pass_cycle_snapshot.json").write_text(
        json.dumps(out,sort_keys=True,indent=2)+"\n",encoding="utf-8"
    )
    print(json.dumps(out["instantaneous_end_of_interval"],indent=2))


if __name__ == "__main__":
    main()
