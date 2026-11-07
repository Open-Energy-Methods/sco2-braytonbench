#!/usr/bin/env python3
"""Reproduce the TES-v0.3 Schumann finite-volume refinement tables.

Produces deterministic CSV/JSON; no third-party experimental data or
network downloads.  Run from an installed checkout:
  python scripts/tes_schumann_convergence.py --out evidence/generated/tes_v03
"""
from __future__ import annotations
import argparse
import csv
import hashlib
import json
from pathlib import Path

from sco2_braytonbench.thermal_storage import (
    PackedBedSpec, PackedBedState, step_packed_bed
)
from sco2_braytonbench.tes_schumann import schumann_inlet_step


def spec(n):
    return PackedBedSpec(
        length_m=1.0, area_m2=1.0, porosity=0.4,
        fluid_density_kg_m3=1000.0, fluid_cp_j_kg_k=1000.0,
        solid_density_kg_m3=2600.0, solid_cp_j_kg_k=800.0,
        interphase_hv_w_m3_k=80000.0, n_cells=n
    )


def write_csv(path, rows):
    if not rows:
        raise ValueError("no results to write")
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def run(output):
    output.mkdir(parents=True, exist_ok=True)
    initial, inlet, flow, time = 350.0, 650.0, 40.0, 30.0
    physical = spec(16)
    analytic_out = schumann_inlet_step(
        physical, x_m=1, t_s=time, mdot_kg_s=flow,
        initial_k=initial, inlet_k=inlet
    )
    grid = []
    for n in (16, 32, 64, 128):
        s = spec(n)
        r = step_packed_bed(s, PackedBedState.uniform(s, initial, initial),
                            inlet_k=inlet, mdot_kg_s=flow,
                            duration_s=time, max_step_s=0.04)
        j = n // 2
        xmid = (j + .5) * s.cell_dx_m
        analytic_mid = schumann_inlet_step(
            s, x_m=xmid, t_s=time, mdot_kg_s=flow,
            initial_k=initial, inlet_k=inlet
        )
        grid.append({
            "n_cells": n,
            "t_s": time,
            "fluid_outlet_numerical_k": r.outlet_k,
            "fluid_outlet_analytical_k": analytic_out.fluid_k,
            "fluid_outlet_abs_error_k": abs(r.outlet_k - analytic_out.fluid_k),
            "outlet_error_percent_of_300k": 100 * abs(r.outlet_k - analytic_out.fluid_k) / 300.0,
            "mid_solid_numerical_k": r.state.solid_k[j],
            "mid_solid_analytical_k": analytic_mid.solid_k,
            "mid_solid_abs_error_k": abs(r.state.solid_k[j] - analytic_mid.solid_k),
            "boundary_energy_j": r.energy_boundary_j,
            "energy_change_j": r.energy_change_j,
            "first_law_residual_j": r.conservation_residual_j,
            "substeps": r.n_substeps,
            "max_cfl": r.courant_per_substep,
            "max_exchange_fluid": r.exchange_fluid_per_substep,
            "max_exchange_solid": r.exchange_solid_per_substep
        })
    temporal = []
    for h in (0.2, 0.1, 0.05, 0.025):
        s = spec(64)
        r = step_packed_bed(s, PackedBedState.uniform(s, initial, initial),
                            inlet_k=inlet, mdot_kg_s=flow,
                            duration_s=time, max_step_s=h)
        temporal.append({
            "max_step_s": h, "substeps": r.n_substeps,
            "outlet_k": r.outlet_k,
            "outlet_abs_error_vs_continuum_k": abs(r.outlet_k - analytic_out.fluid_k),
            "first_law_residual_j": r.conservation_residual_j,
            "max_cfl": r.courant_per_substep
        })
    assert all(a["fluid_outlet_abs_error_k"] > b["fluid_outlet_abs_error_k"]
               for a, b in zip(grid, grid[1:])), "failed monotone spatial refinement"
    assert all(a["mid_solid_abs_error_k"] > b["mid_solid_abs_error_k"]
               for a, b in zip(grid, grid[1:])), "failed mid-solid refinement"
    pgrid, ptime = output / "tes_grid_convergence.csv", output / "tes_temporal_sensitivity.csv"
    write_csv(pgrid, grid)
    write_csv(ptime, temporal)
    manifest = {
        "source_class": "independent-analytic-versus-synthetic-finite-volume",
        "physics": "constant-property 1D-2T Schumann packed bed, ideal inlet step",
        "not_claimed": ["CIC energiGUNE facility validation", "CFD", "PCM",
                        "CO2 fluid inventory", "independent experimental validation"],
        "analytical_source_doi": "10.1016/S0016-0032(29)91186-8",
        "inputs": {"length_m": 1.0, "area_m2": 1.0, "porosity": .4,
                   "rho_f_kg_m3": 1000, "cp_f_j_kg_k": 1000,
                   "rho_s_kg_m3": 2600, "cp_s_j_kg_k": 800,
                   "hv_w_m3_k": 80000, "mass_flow_kg_s": flow,
                   "initial_k": initial, "inlet_k": inlet, "time_s": time},
        "results": {
            "production_n": 128,
            "outlet_abs_error_k": grid[-1]["fluid_outlet_abs_error_k"],
            "mid_solid_abs_error_k": grid[-1]["mid_solid_abs_error_k"],
            "production_max_cfl": grid[-1]["max_cfl"],
            "max_first_law_abs_residual_j": max(abs(x["first_law_residual_j"])
                                                for x in grid)
        },
        "files_sha256": {}
    }
    for path in (pgrid, ptime):
        manifest["files_sha256"][path.name] = hashlib.sha256(path.read_bytes()).hexdigest()
    with (output / "tes_verification_manifest.json").open("w", encoding="utf8") as f:
        json.dump(manifest, f, indent=2, sort_keys=True)
        f.write("\n")
    print(json.dumps(manifest["results"], indent=2))


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", type=Path,
                    default=Path("evidence/generated/tes_v03"))
    run(ap.parse_args().out)
