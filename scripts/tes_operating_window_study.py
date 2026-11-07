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
from itertools import combinations, product
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
    interphase_hv_w_m3_k=500.0, n_cells=96,
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
FACTORIAL_AXES = {
    "flow_kg_s": (0.025, 0.1),
    "porosity": (0.35, 0.65),
    "interphase_hv_w_m3_k": (250.0, 1000.0),
}
FACTORIAL_EFFECT_OUTPUTS = (
    "recovered_energy_j", "useful_discharge_energy_j",
    "charged_solid_soc", "charged_total_exergy_j",
)
NUMERICAL_AXES = {
    "n_cells": (6, 12, 24, 48, 96, 192),
    "grade_trace_stride": (4, 2, 1),
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
        "grade_trace_stride": inputs.grade_trace_stride,
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


def _write_csv(path: Path, rows: list[dict], *, scenarios: bool = True) -> str:
    if scenarios:
        _validate_rows(rows)
    elif not rows or any(not r.get("term") for r in rows):
        raise ValueError("factorial contrasts are incomplete")
    else:
        for r in rows:
            if any(isinstance(v, float) and not math.isfinite(v) for v in r.values()):
                raise ArithmeticError("nonfinite factorial effect")
    with path.open("w", newline="", encoding="utf-8") as fp:
        w = csv.DictWriter(fp, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _factorial_effects(rows: list[dict]) -> list[dict]:
    """Orthogonal 2^3 effect contrasts, signed high-minus-low in response units.

    For a sign-coded 2^3 design, effect(S) = sum(y*prod(sign_S))/4.
    This is a descriptive finite-difference interaction, not an uncertainty
    interval or a derivative valid outside the eight declared corners.
    """
    if len(rows) != 8:
        raise ValueError("factorial design must have exactly eight corners")
    names = tuple(FACTORIAL_AXES)
    out = []
    for degree in (1, 2, 3):
        for subset in combinations(names, degree):
            effect = {"term": ":".join(subset), "degree": degree}
            for output in FACTORIAL_EFFECT_OUTPUTS:
                effect[output] = math.fsum(
                    math.prod(r["code_" + factor] for factor in subset)
                    * r[output] for r in rows
                ) / 4.0
            out.append(effect)
    if len(out) != 7:
        raise AssertionError("2^3 factorial contrast count drift")
    return out


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

    # Fully crossed extremes; high/low sign coding makes each main and
    # interaction contrast explicitly reconstructible from the eight rows.
    factorial = []
    names = tuple(FACTORIAL_AXES)
    for index, codes in enumerate(product((-1, 1), repeat=3), start=1):
        values = {
            name: FACTORIAL_AXES[name][0 if code == -1 else 1]
            for name, code in zip(names, codes)
        }
        spec = replace(BASE_SPEC, **{
            k: v for k, v in values.items() if k in vars(BASE_SPEC)
        })
        inputs = replace(BASE_INPUTS, **{
            k: v for k, v in values.items() if k in vars(BASE_INPUTS)
        })
        row = _row("factorial_2x2x2", "combination", index,
                   spec, inputs, base)
        row.update({"code_" + k: code for k, code in zip(names, codes)})
        factorial.append(row)
    effects = _factorial_effects(factorial)

    numerical = []
    for n in NUMERICAL_AXES["n_cells"]:
        numerical.append(_row(
            "spatial_refinement", "n_cells", n,
            replace(BASE_SPEC, n_cells=n), BASE_INPUTS, base,
        ))
    for stride in NUMERICAL_AXES["grade_trace_stride"]:
        numerical.append(_row(
            "observation_quadrature_refinement",
            "grade_trace_stride", stride,
            BASE_SPEC, replace(BASE_INPUTS, grade_trace_stride=stride), base,
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
    factorial_file = "tes_v08_factorial_cases.csv"
    effects_file = "tes_v08_factorial_effects.csv"
    files[physical_file] = _write_csv(outdir / physical_file, physical)
    files[numerical_file] = _write_csv(outdir / numerical_file, numerical)
    files[factorial_file] = _write_csv(outdir / factorial_file, factorial)
    files[effects_file] = _write_csv(outdir / effects_file, effects, scenarios=False)
    manifest = {
        "schema": SCHEMA,
        "evidence_class": "synthetic_constant_property_1d_two_temperature",
        "parent_package_version": "0.5.0a0",
        "source_commit": os.environ.get("TES_SOURCE_SHA", "not-recorded"),
        "base_spec": asdict(BASE_SPEC),
        "base_inputs": asdict(BASE_INPUTS),
        "study_design_predeclared": {
            "physical_axes": PHYSICAL_AXES,
            "factorial_axes": FACTORIAL_AXES,
            "factorial_effect_definition": "effect=sum(y*product(signs))/4 for eight +/- corners",
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
                "N/SSPRK3 step and substep-trace decimation panels"
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
            "factorial_rows": len(factorial),
            "factorial_effect_rows": len(effects),
        },
        "baseline": asdict(base),
        "factorial_effects": effects,
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
        "physical_panel": [
            {
                "axis": r["axis"], "level": r["level"],
                "recovered_energy_j": r["recovered_energy_j"],
                "useful_discharge_energy_j": r["useful_discharge_energy_j"],
                "charged_total_exergy_j": r["charged_total_exergy_j"],
                "charged_solid_soc": r["charged_solid_soc"],
            }
            for r in physical
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
    required = {
        "tes_v08_physical_sensitivity.csv": counts["physical_rows"],
        "tes_v08_numerical_refinement.csv": counts["numerical_rows"],
        "tes_v08_factorial_cases.csv": counts["factorial_rows"],
        "tes_v08_factorial_effects.csv": counts["factorial_effect_rows"],
    }
    if set(manifest["sha256"]) != set(required):
        raise ValueError("unexpected artifact table set")
    for filename, expected_count in required.items():
        path = outdir / filename
        actual_hash = hashlib.sha256(path.read_bytes()).hexdigest()
        if actual_hash != manifest["sha256"][filename]:
            raise ValueError("artifact hash mismatch: " + filename)
        with path.open(newline="", encoding="utf-8") as fp:
            rows = list(csv.DictReader(fp))
        if len(rows) != expected_count:
            raise ValueError("artifact row count mismatch: " + filename)
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
        "physical_panel": manifest["physical_panel"],
        "factorial_effects": manifest["factorial_effects"],
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
