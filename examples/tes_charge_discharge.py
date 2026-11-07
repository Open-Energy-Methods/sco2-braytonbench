#!/usr/bin/env python3
"""TES-v0.4 prescribed synthetic charge/hold/discharge run.

Each segment yields a simulated cell state, boundary enthalpy and
full energy ledger. Incomplete cycle metrics are deliberately null.
"""
from __future__ import annotations
from dataclasses import asdict
import csv
import json
from pathlib import Path

from sco2_braytonbench.thermal_storage import PackedBedSpec, PackedBedState
from sco2_braytonbench.tes_cycles import StorageStage, run_storage_schedule


def main():
    s = PackedBedSpec(
        length_m=1.0, area_m2=1.0, porosity=.4,
        fluid_density_kg_m3=1000, fluid_cp_j_kg_k=1000,
        solid_density_kg_m3=2600, solid_cp_j_kg_k=800,
        interphase_hv_w_m3_k=80000, n_cells=32
    )
    stages = []
    for i in range(10):
        stages.append(StorageStage(f"charge_{i:02}", "charge", 5, 650, 40))
    for i in range(2):
        stages.append(StorageStage(f"hold_{i:02}", "hold", 5, 350, 0))
    for i in range(16):
        stages.append(StorageStage(f"discharge_{i:02}", "discharge", 5, 350, -40))
    r = run_storage_schedule(
        s, PackedBedState.uniform(s, 350, 350),
        stages, cold_k=350, hot_k=650
    )
    path = Path("evidence/generated/tes_v04")
    path.mkdir(parents=True, exist_ok=True)
    with (path / "synthetic_storage_stage_trace.csv").open(
        "w", newline="", encoding="utf-8"
    ) as f:
        records = [asdict(row) for row in r.records]
        writer = csv.DictWriter(f, fieldnames=list(records[0]))
        writer.writeheader()
        writer.writerows(records)
    summary = {
        "evidence_class": "prescribed-synthetic-constant-property-packed-bed",
        "physical_exclusions": [
            "CFD", "PCM", "facility measurement", "CIC energiGUNE",
            "CARBOSOLA", "liquid piston", "CO2 inventory model"
        ],
        "n_cells": s.n_cells, "stages": len(r.records),
        "time_s": r.records[-1].t_end_s,
        "charged_energy_j": r.charged_energy_j,
        "recovered_energy_j": r.recovered_energy_j,
        "stored_energy_change_j": r.stored_energy_change_j,
        "first_law_residual_j": r.conservation_residual_j,
        "solid_usable_capacity_j": r.solid_usable_capacity_j,
        "final_solid_soc": r.final_solid_soc,
        "max_cell_return_error_k": r.max_cell_return_error_k,
        "complete_cycle": r.complete_cycle,
        "gross_energy_efficiency": r.gross_energy_efficiency,
        "interpretation": "An incomplete schedule is not a measured round-trip efficiency.",
    }
    with (path / "synthetic_storage_summary.json").open(
        "w", encoding="utf-8"
    ) as f:
        json.dump(summary, f, indent=2, sort_keys=True)
        f.write("\n")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
