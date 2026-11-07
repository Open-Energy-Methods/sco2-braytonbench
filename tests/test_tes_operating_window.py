"""Independent TES-v0.8 conservation, threshold and study-integrity gates."""
from dataclasses import replace
import csv
import math

import pytest

from sco2_braytonbench.tes_operating_window import (
    OperatingInputs, _qualified_segment, run_operating_case,
)
from sco2_braytonbench.thermal_storage import (
    PackedBedSpec, PackedBedState, step_packed_bed,
)
from scripts.tes_operating_window_study import (
    BASE_INPUTS, BASE_SPEC, generate_study, verify_study,
)


def test_grade_crossing_integral_has_exact_piecewise_linear_identity():
    # Linearly cooling 600 -> 400 K over 4 s: first 2 s qualify.
    hot_to_cold = _qualified_segment(600, 400, 500, 350, 10, 4)
    cold_to_hot = _qualified_segment(400, 600, 500, 350, 10, 4)
    assert hot_to_cold == pytest.approx((4000.0, 2.0, 0.0, 2.0))
    assert cold_to_hot[:2] == pytest.approx((4000.0, 2.0))
    assert cold_to_hot[2] == pytest.approx(2.0)
    assert cold_to_hot[3] is None
    assert _qualified_segment(400, 450, 500, 350, 10, 4) == (
        0.0, 0.0, None, None,
    )
    assert _qualified_segment(600, 550, 500, 350, 10, 4)[:2] == pytest.approx(
        (9000.0, 4.0)
    )


def test_energy_balance_is_not_conditioned_on_temperature_grade():
    low = run_operating_case(
        BASE_SPEC, replace(BASE_INPUTS, useful_outlet_threshold_k=450),
    )
    high = run_operating_case(
        BASE_SPEC, replace(BASE_INPUTS, useful_outlet_threshold_k=700),
    )
    assert low.charged_energy_j == pytest.approx(high.charged_energy_j)
    assert low.recovered_energy_j == pytest.approx(high.recovered_energy_j)
    assert low.first_law_residual_j == pytest.approx(high.first_law_residual_j)
    assert low.useful_discharge_energy_j > 0
    assert high.useful_discharge_energy_j == 0
    assert high.useful_discharge_duration_s == 0
    assert high.first_qualified_time_s is None
    assert high.first_downcrossing_time_s is None
    assert abs(low.first_law_relative_residual) < 1e-9
    assert low.charged_total_exergy_j > 0
    assert low.charged_solid_capacity_j > low.charged_fluid_capacity_j


def test_incomplete_cycle_remains_null_despite_positive_withdrawal():
    result = run_operating_case(BASE_SPEC, BASE_INPUTS)
    assert result.charged_energy_j > 0
    assert result.recovered_energy_j > 0
    assert result.max_cell_return_error_k > BASE_INPUTS.state_return_tolerance_k
    assert not result.complete_cycle
    assert result.gross_round_trip_efficiency is None
    assert result.max_courant_substep <= .75 + 1e-12
    assert result.total_solver_substeps > 0


def test_geometry_capacity_and_flow_turnover_semantics():
    larger = replace(BASE_SPEC, length_m=BASE_SPEC.length_m * 2)
    r = run_operating_case(BASE_SPEC, BASE_INPUTS)
    q = run_operating_case(larger, BASE_INPUTS)
    assert q.thermal_turnover_s == pytest.approx(2*r.thermal_turnover_s)
    assert q.charged_solid_capacity_j == pytest.approx(2*r.charged_solid_capacity_j)
    assert q.charged_fluid_capacity_j == pytest.approx(2*r.charged_fluid_capacity_j)
    fastest = run_operating_case(
        BASE_SPEC, replace(BASE_INPUTS, flow_kg_s=BASE_INPUTS.flow_kg_s*2)
    )
    assert fastest.thermal_turnover_s == pytest.approx(r.thermal_turnover_s/2)


@pytest.mark.parametrize("changes", [
    {"flow_kg_s": 0},
    {"charge_turnovers": -1},
    {"hold_turnovers": -0.01},
    {"discharge_turnovers": 0},
    {"useful_outlet_threshold_k": 300},
    {"useful_outlet_threshold_k": float("nan")},
    {"ambient_k": 0},
    {"hot_inlet_k": 349},
    {"observations_per_stage": 1},
    {"observations_per_stage": 2.5},
    {"grade_trace_stride": 0},
    {"grade_trace_stride": 1.5},
    {"max_solver_step_s": -1},
    {"state_return_tolerance_k": -1},
])
def test_invalid_operating_scenarios_fail_closed(changes):
    with pytest.raises(ValueError):
        replace(BASE_INPUTS, **changes)


def test_operating_study_is_deterministic_and_hash_tamper_detected(tmp_path):
    manifest = generate_study(tmp_path)
    assert manifest["schema"] == "tes-v08-synthetic-operating-window-1"
    assert manifest["counts"]["physical_rows"] == 1 + sum(
        len(x) for x in manifest["study_design_predeclared"]["physical_axes"].values()
    )
    assert manifest["counts"]["numerical_rows"] == 10
    assert verify_study(tmp_path)["sha256"] == manifest["sha256"]
    with (tmp_path / "tes_v08_physical_sensitivity.csv").open(
        newline="", encoding="utf-8"
    ) as fp:
        rows = list(csv.DictReader(fp))
    grade_rows = [
        x for x in rows
        if x["axis"] == "useful_outlet_threshold_k" and x["level"] == "700.0"
    ]
    assert len(grade_rows) == 1
    assert grade_rows[0]["first_downcrossing_time_s"] == ""
    assert float(grade_rows[0]["useful_discharge_energy_j"]) == 0.0
    assert not manifest["baseline"]["complete_cycle"]
    assert manifest["baseline"]["gross_round_trip_efficiency"] is None
    table = tmp_path / "tes_v08_numerical_refinement.csv"
    table.write_bytes(table.read_bytes() + b"tampered\n")
    with pytest.raises(ValueError, match="hash mismatch"):
        verify_study(tmp_path)


def test_numerical_mesh_and_outlet_sampling_provide_distinct_comparisons():
    # Numerical sensitivity is not the same thing as physical OAT.
    coarse = run_operating_case(
        replace(BASE_SPEC, n_cells=6), BASE_INPUTS
    )
    fine = run_operating_case(
        replace(BASE_SPEC, n_cells=24), BASE_INPUTS
    )
    sampled = run_operating_case(
        BASE_SPEC, replace(BASE_INPUTS, grade_trace_stride=4)
    )
    assert all(math.isfinite(x.first_law_residual_j) for x in (
        coarse, fine, sampled
    ))
    assert max(
        coarse.first_law_relative_residual,
        fine.first_law_relative_residual,
        sampled.first_law_relative_residual,
    ) < 1e-9
    assert fine.charged_solid_capacity_j == pytest.approx(
        coarse.charged_solid_capacity_j
    )
    # Space and grade-observation convergence need separate comparisons;
    # no assertion of monotonicity is made for nonlinear threshold crossings.
    assert sampled.thermal_turnover_s == pytest.approx(
        coarse.thermal_turnover_s
    )


def test_internal_substep_trace_does_not_modify_conservative_solution():
    spec = BASE_SPEC
    state = PackedBedState.uniform(spec, 350, 350)
    kwargs = {"inlet_k": 650, "mdot_kg_s": 0.05, "duration_s": 16.0}
    ordinary = step_packed_bed(spec, state, **kwargs)
    traced = step_packed_bed(
        spec, state, **kwargs, record_outlet_trace=True,
    )
    assert ordinary.outlet_trace is None
    assert traced.outlet_trace is not None
    assert len(traced.outlet_trace) == traced.n_substeps + 1
    assert traced.outlet_trace[0] == (0.0, 350.0)
    assert traced.outlet_trace[-1][0] == pytest.approx(16.0)
    assert traced.outlet_trace[-1][1] == pytest.approx(traced.outlet_k)
    assert traced.state == ordinary.state
    assert traced.energy_boundary_j == ordinary.energy_boundary_j
    assert traced.conservation_residual_j == ordinary.conservation_residual_j
    for (t0, _), (t1, _) in zip(traced.outlet_trace, traced.outlet_trace[1:]):
        assert 0 <= t0 < t1 <= 16.0
