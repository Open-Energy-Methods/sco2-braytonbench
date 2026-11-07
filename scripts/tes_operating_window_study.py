"""Reproducible, provenance-tagged TES-v0.8 operating-window study.

The OAT ensemble is parameter sensitivity, NOT propagated measurement
uncertainty. Space/time resolution studies are separately labelled.
There is no experimental or alternate-model-form uncertainty estimate.
"""
from __future__ import annotations

import argparse
import csv
from dataclasses import asdict, replace
import hashlib
import json
import math
import os
from pathlib import Path

from sco2_braytonbench.thermal_storage import PackedBedSpec
from sco2_braytonbench.tes_operating_window import (
    OperatingInputs, OperatingResult, run_operating_case,
)

SCHEMA = "tes-v08-synthetic-operating-window-1"
BASE_SPEC = PackedBedSpec(
    length_m=1.0, area_m2=0.1, porosity=0.5,
    fluid_density_kg_m3=5.0, fluid_cp_j_kg_k=1000.0,
    solid_density_kg_m3=1000.0, solid_cp_j_kg_k=700.0,
    interphase_hv_w_m3_k=500.0, n_cells=12,
)
BASE_INPUTS = OperatingInputs()
PHYSICAL_AXES = {
    "flow_kg_s": (0.025, 0.05, 0.1),
    "porosity": (0.35, 0.5, 0.65),
    "length_m": (0.75, 1.0, 1.25),
    "area_m2": (0.075, 0.1, 0.125),
    "interphase_hv_w_m3_k": (250.0, 500.0, 1000.0),
    "charge_turnovers": (0.6, 0.8, 1.0),
    "hold_turnovers": (0.0, 0.1, 0.2),
    "discharge_turnovers": (0.8, 1.0, 1.2),
    "useful_outlet_threshold_k": (450.0, 500.0, 550.0, 700.0),
}
NUMERICAL_AXES = {
    "n_cells": (6, 12, 24, 48),
    "observations_per_stage": (12, 24, 48),
    "solver_timestep_factor_of_nominal_limit": (1.0, 0.5, 0.25),
}
OUTPUTS = (
    "recovered_energy_j", "useful_discharge_energy_j",
    "useful_discharge_duration_s", "charged_total_exergy_j",
    "charged_solid_soc", "charged_thermocline_width_m",
    "first_downcrossing_time_s",
)


def _nominal_stability_step(spec: PackedBedSpec, inputs: OperatingInputs) -> float:
    cf = spec.fluid_cell_capacity_j_k
    cs = spec.solid_cell_capacity_j_k
    h = spec.interphase_cell_w_k
    rate = max(
        (inputs.flow_kg_s * spec.fluid_cp_j_kg_k + h) / cf,
        h / cs,
    )
    return 0.75 / rate


def _row(group: str, axis: str, level: float,
         spec: PackedBedSpec, inputs: OperatingInputs,
         baseline: OperatingResult) -> dict:
    result = run_operating_case(spec, inputs)
    data = asdict(result)
    row = {
        "group": group, "axis": axis, "level": level,
        "n_cells": spec.n_cells, "length_m": spec.length_m,
        "area_m2": spec.area_m2, "porosity": spec.porosity,
        "hv_w_m3_k": spec.interphase_hv_w_m3_k,
        "flow_kg_s": inputs.flow_kg_s,
        "charge_turnovers": inputs.charge_turnovers,
        "hold_turnovers": inputs.hold_turnovers,
        "discharge_turnovers": inputs.discharge_turnovers,
        "useful_outlet_threshold_k": inputs.useful_outlet_threshold_k,
        "observations_per_stage": inputs.observations_per_stage,
        "max_solver_step_s": inputs.max_solver_step_s,
    }
    row.update(data)
    for output in OUTPUTS:
        value = data[output]
        base = getattr(baseline, output)
        row["delta_" + output] = (
            value - base if value is not None and base is not None else None
        )
    return row


def _validate_rows(rows: list[dict]) -> None:
    if not rows:
        raise ValueError("study produced zero rows")
    for row in rows:
        if not row["group"] or not row["axis"]:
            raise ValueError("each scenario requires group and axis")
        for key, value in row.items():
            if isinstance(value, float) and not math.isfinite(value):
                raise ArithmeticError("nonfinite result in " + key)
        if row["first_law_relative_residual"] > 1e-9:
            raise ArithmeticError("energy ledger failed")
        if row["useful_discharge_duration_s"] < 0:
            raise ArithmeticError("negative qualified duration")
        if row["useful_discharge_duration_s"] > row["discharge_duration_s"] * (1 + 1e-10):
            raise ArithmeticError("grade duration exceeds discharge")
        if not row["complete_cycle"] and row["gross_round_trip_efficiency"] is not None:
            raise AssertionError("incomplete cycle reported gross efficiency")
        if (row["first_qualified_time_s"] is None
                and row["useful_discharge_energy_j"] > 1e-9):
            raise ArithmeticError("qualified energy without qualified time")


def _write_csv(path: Path, rows: list[dict]) -> str:
    _validate_rows(rows)
    with path.open("w", newline="", encoding="utf-8") as fp:
        w = csv.DictWriter(fp, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)
    return hashlib.sha256(path.read_bytes()).hexdigest()


def generate_study(outdir: Path) -> dict:
    """One nominal run + OAT + independent numerical-refinement panels."""
    outdir.mkdir(parents=True, exist_ok=True)
    base = run_operating_case(BASE_SPEC, BASE_INPUTS)
    physical = [_row(
        "physical_sensitivity", "baseline", 1.0, BASE_SPEC,
        BASE_INPUTS, base,
    )]
    for axis, levels in PHYSICAL_AXES.items():
        for level in levels:
            if axis in vars(BASE_SPEC):
                spec, inputs = replace(BASE_SPEC, **{axis: level}), BASE_INPUTS
            else:
                spec, inputs = BASE_SPEC, replace(BASE_INPUTS, **{axis: level})
            physical.append(_row(
                "physical_sensitivity", axis, level, spec, inputs, base,
            ))

    numerical = []
    for n in NUMERICAL_AXES["n_cells"]:
        numerical.append(_row(
            "spatial_refinement", "n_cells", n,
            replace(BASE_SPEC, n_cells=n), BASE_INPUTS, base,
        ))
    for count in NUMERICAL_AXES["observations_per_stage"]:
        numerical.append(_row(
            "observation_quadrature_refinement",
            "observations_per_stage", count,
            BASE_SPEC, replace(BASE_INPUTS, observations_per_stage=count), base,
        ))
    bound = _nominal_stability_step(BASE_SPEC, BASE_INPUTS)
    for fraction in NUMERICAL_AXES["solver_timestep_factor_of_nominal_limit"]:
        numerical.append(_row(
            "solver_timestep_refinement",
            "solver_timestep_factor_of_nominal_limit", fraction,
            BASE_SPEC, replace(BASE_INPUTS, max_solver_step_s=bound*fraction),
            base,
        ))
    # Crossing absent is a censored/undefined event, not an arbitrary time=0.
    missing_grade = [
        r for r in physical
        if r["axis"] == "useful_outlet_threshold_k"
        and r["level"] == 700.0
    ]
    if len(missing_grade) != 1:
        raise AssertionError("high-grade stress scenario absent")

    files = {}
    physical_file = "tes_v08_physical_sensitivity.csv"
    numerical_file = "tes_v08_numerical_refinement.csv"
    files[physical_file] = _write_csv(outdir / physical_file, physical)
    files[numerical_file] = _write_csv(outdir / numerical_file, numerical)
    manifest = {
        "schema": SCHEMA,
        "evidence_class": "synthetic_constant_property_1d_two_temperature",
        "parent_package_version": "0.5.0a0",
        "source_commit": os.environ.get("TES_SOURCE_SHA", "not-recorded"),
        "base_spec": asdict(BASE_SPEC),
        "base_inputs": asdict(BASE_INPUTS),
        "study_design_predeclared": {
            "physical_axes": PHYSICAL_AXES,
            "numerical_axes": NUMERICAL_AXES,
            "comparisons": "One-at-a-time vs nominal, not factorial/causal inference",
            "time_semantics": (
                "Physical phase durations scale with total fluid+solid "
                "thermal turnover; changing flow or geometry changes seconds"
            ),
            "grade_semantics": (
                "Discharge recovered heat counted by exact SSPRK3 boundary "
                "ledger; temperature-qualifying subenergy is piecewise-linear "
                "observation quadrature and never replaces withdrawn heat"
            ),
            "cycle_semantics": (
                "Only a full fluid+solid cell state return permits gross "
                "round-trip efficiency; otherwise null"
            ),
        },
        "uncertainty_partition": {
            "numerical_discretization": (
                "N/SSPRK3 step and outlet-observation resolution panels"
            ),
            "parameter_sensitivity": (
                "Declared OAT contrasts; not probability/uncertainty intervals"
            ),
            "model_form": (
                "Unquantified: only constant-cp adiabatic 1-D model, "
                "no independent alternate closure or experimental data"
            ),
        },
        "excluded_claims": [
            "measured thermal-storage performance",
            "full industrial sCO2 dynamic inventory",
            "pressure loss/pump power or heat leaks",
            "experimental validation",
            "phase-change TES",
            "plant round-trip efficiency of incomplete cycles",
            "statistical confidence intervals for parameter sweeps",
        ],
        "counts": {
            "physical_rows": len(physical),
            "numerical_rows": len(numerical),
        },
        "baseline": asdict(base),
        "numerical_panel": [
            {
                "group": r["group"], "level": r["level"],
                "useful_discharge_energy_j": r["useful_discharge_energy_j"],
                "recovered_energy_j": r["recovered_energy_j"],
                "observation_quadrature_error_j": r[
                    "observation_quadrature_error_j"
                ],
                "first_law_relative_residual": r[
                    "first_law_relative_residual"
                ],
                "charged_solid_soc": r["charged_solid_soc"],
                "charged_thermocline_width_m": r[
                    "charged_thermocline_width_m"
                ],
            }
            for r in numerical
        ],
        "physical_grade_panel": [
            {
                "grade_k": r["level"],
                "useful_energy_j": r["useful_discharge_energy_j"],
                "qualification_s": r["useful_discharge_duration_s"],
                "first_downcrossing_s": r["first_downcrossing_time_s"],
            }
            for r in physical if r["axis"] == "useful_outlet_threshold_k"
        ],
        "null_threshold_case": {
            "grade_k": 700.0,
            "qualified_energy_j": missing_grade[0]["useful_discharge_energy_j"],
            "first_downcrossing_s": missing_grade[0][
                "first_downcrossing_time_s"
            ],
        },
        "sha256": files,
    }
    (outdir / "tes_v08_manifest.json").write_text(
        json.dumps(manifest, indent=2, sort_keys=True, allow_nan=False) + "\n",
        encoding="utf-8",
    )
    return manifest


def verify_study(outdir: Path) -> dict:
    """Fail closed on modified/missing CSV outputs and inconsistent manifest."""
    manifest_path = outdir / "tes_v08_manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    if manifest.get("schema") != SCHEMA:
        raise ValueError("unexpected v0.8 manifest schema")
    if manifest.get("base_spec") != asdict(BASE_SPEC):
        raise ValueError("scenario specification drift")
    if manifest.get("base_inputs") != asdict(BASE_INPUTS):
        raise ValueError("operating-input specification drift")
    counts = manifest["counts"]
    for filename, claimed_hash in manifest["sha256"].items():
        path = outdir / filename
        actual_hash = hashlib.sha256(path.read_bytes()).hexdigest()
        if actual_hash != claimed_hash:
            raise ValueError("artifact hash mismatch: " + filename)
        with path.open(newline="", encoding="utf-8") as fp:
            rows = list(csv.DictReader(fp))
        expect = (counts["physical_rows"] if "physical" in filename
                  else counts["numerical_rows"])
        if len(rows) != expect:
            raise ValueError("artifact row count mismatch: " + filename)
    if set(manifest["sha256"]) != {
        "tes_v08_physical_sensitivity.csv",
        "tes_v08_numerical_refinement.csv",
    }:
        raise ValueError("unexpected artifact table set")
    return manifest


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--out", type=Path,
        default=Path("evidence/generated/tes_v08"),
    )
    parser.add_argument(
        "--verify", action="store_true",
        help="verify generated hashes and row counts without recalculating",
    )
    args = parser.parse_args()
    manifest = verify_study(args.out) if args.verify else generate_study(args.out)
    print(json.dumps({
        "schema": manifest["schema"],
        "counts": manifest["counts"],
        "sha256": manifest["sha256"],
        "numerical_panel": manifest["numerical_panel"],
        "physical_grade_panel": manifest["physical_grade_panel"],
        "baseline": {
            "recovered_energy_j": manifest["baseline"]["recovered_energy_j"],
            "useful_discharge_energy_j": manifest["baseline"][
                "useful_discharge_energy_j"
            ],
            "first_law_relative_residual": manifest["baseline"][
                "first_law_relative_residual"
            ],
            "complete_cycle": manifest["baseline"]["complete_cycle"],
        },
    }, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
