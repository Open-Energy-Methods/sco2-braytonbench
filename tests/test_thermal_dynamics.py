"""Independent analytical and conservation tests for WP2a thermal dynamics.

These exercises use a SYNTHETIC solid heat capacity, not CO2/CARBOSOLA
measurements and not a time-dependent Brayton-cycle plant.
"""
from math import exp, isclose, isfinite

import pytest

from sco2_braytonbench.properties import DomainError
from sco2_braytonbench.thermal_dynamics import (
    ThermalStepInput,
    ThermalWall,
    simulate_thermal_wall,
    thermal_wall_step,
)


def test_exponential_solution_and_integrated_first_law():
    wall = ThermalWall(
        capacity_j_k=12000.,
        hot_conductance_w_k=60.,
        cold_conductance_w_k=40.,
    )
    interval = ThermalStepInput(500., 250., 30.)
    result = thermal_wall_step(wall, 310., interval)
    # Independent solution of linear constant-coefficient ODE:
    # T_eq=(60*500+40*250)/100=400 K; tau=120 s.
    expected = 400. + (310. - 400.) * exp(-30. / 120.)
    assert wall.time_constant_s == pytest.approx(120.)
    assert result.equilibrium_temperature_k == pytest.approx(400.)
    assert result.final_wall_temperature_k == pytest.approx(expected, rel=1e-13)
    assert result.time_start_s == 0.
    assert result.time_end_s == 30.
    assert result.mean_wall_temperature_k == pytest.approx(
        400. + (310. - 400.) * (1 - exp(-.25)) / .25, rel=1e-13,
    )
    assert result.stored_energy_j == pytest.approx(
        wall.capacity_j_k * (result.final_wall_temperature_k - 310.),
        rel=1e-12,
    )
    assert result.hot_energy_j - result.cold_energy_j == pytest.approx(
        result.stored_energy_j, abs=1e-8,
    )
    assert abs(result.energy_residual_j) < 1e-8


def test_equilibrium_temperature_has_zero_storage_but_nonzero_heat_throughput():
    wall = ThermalWall(10000., 60., 40.)
    out = thermal_wall_step(wall, 400., ThermalStepInput(500., 250., 40.))
    assert out.final_wall_temperature_k == pytest.approx(400.)
    assert out.stored_energy_j == pytest.approx(0., abs=1e-12)
    assert out.hot_energy_j == pytest.approx(240000.)
    assert out.cold_energy_j == pytest.approx(240000.)
    assert out.energy_residual_j == pytest.approx(0., abs=1e-8)


def test_one_large_step_matches_many_small_steps_on_same_boundary_conditions():
    wall = ThermalWall(50000., 70., 20.)
    whole = thermal_wall_step(wall, 310., ThermalStepInput(650., 280., 120.))
    records = simulate_thermal_wall(
        wall, 310., [ThermalStepInput(650., 280., 1.)] * 120
    )
    assert len(records) == 120
    assert records[-1].time_end_s == 120.
    assert records[-1].final_wall_temperature_k == pytest.approx(
        whole.final_wall_temperature_k, abs=1e-10,
    )
    assert sum(x.hot_energy_j for x in records) == pytest.approx(
        whole.hot_energy_j, rel=1e-12,
    )
    assert sum(x.cold_energy_j for x in records) == pytest.approx(
        whole.cold_energy_j, rel=1e-12,
    )
    assert sum(x.stored_energy_j for x in records) == pytest.approx(
        whole.stored_energy_j, rel=1e-12,
    )


def test_piecewise_thermal_load_is_sequential_and_causally_changes_state():
    wall = ThermalWall(25000., 60., 30.)
    records = simulate_thermal_wall(
        wall, 330., (
            ThermalStepInput(500., 280., 50.),
            ThermalStepInput(350., 280., 50.),
            ThermalStepInput(500., 280., 50.),
        ),
    )
    assert [r.time_end_s for r in records] == [50., 100., 150.]
    assert records[1].initial_wall_temperature_k == records[0].final_wall_temperature_k
    assert records[2].initial_wall_temperature_k == records[1].final_wall_temperature_k
    comparison = simulate_thermal_wall(
        wall, 330., (ThermalStepInput(500., 280., 50.),) * 3,
    )
    assert records[-1].final_wall_temperature_k < comparison[-1].final_wall_temperature_k
    assert all(isfinite(r.energy_residual_j) for r in records)


def test_reverse_signed_heat_flow_is_allowed():
    wall = ThermalWall(10000., 50., 0.)
    out = thermal_wall_step(wall, 450., ThermalStepInput(300., 275., 10.))
    assert out.final_wall_temperature_k < 450.
    assert out.hot_energy_j < 0.
    assert out.cold_energy_j == 0.
    assert out.stored_energy_j < 0.
    assert out.hot_energy_j == pytest.approx(out.stored_energy_j, rel=1e-12)


@pytest.mark.parametrize("capacity,kh,kc", [
    (0., 50., 30.),
    (-1., 50., 30.),
    (float("nan"), 50., 30.),
    (float("inf"), 50., 30.),
    (1000., -1., 30.),
    (1000., 1., -3.),
    (1000., float("nan"), 30.),
    (1000., float("inf"), 30.),
    (1000., 0., 0.),
])
def test_invalid_wall_physics_is_rejected(capacity, kh, kc):
    with pytest.raises(DomainError):
        ThermalWall(capacity, kh, kc)


@pytest.mark.parametrize("hot,cold,duration", [
    (0., 280., 5.),
    (500., -1., 5.),
    (500., 280., 0.),
    (500., 280., -5.),
    (500., 280., float("nan")),
    (500., 280., float("inf")),
    (float("inf"), 280., 5.),
])
def test_invalid_boundary_inputs_are_rejected(hot, cold, duration):
    with pytest.raises(DomainError):
        ThermalStepInput(hot, cold, duration)


@pytest.mark.parametrize("initial,start", [
    (0., 0.),
    (float("nan"), 0.),
    (float("inf"), 0.),
    (300., -1.),
    (300., float("nan")),
    (300., float("inf")),
])
def test_invalid_initial_states_and_times_are_rejected(initial, start):
    with pytest.raises(DomainError):
        thermal_wall_step(
            ThermalWall(10000., 50., 30.),
            initial,
            ThermalStepInput(500., 280., 5.),
            time_start_s=start,
        )


def test_no_profile_is_explicitly_rejected():
    with pytest.raises(DomainError, match="at least one interval"):
        simulate_thermal_wall(ThermalWall(10000., 40., 20.), 310., [])


def test_near_zero_dt_over_tau_is_stable_not_nan():
    wall = ThermalWall(1.e12, 10., 20.)
    out = thermal_wall_step(wall, 300., ThermalStepInput(400., 280., 1.e-5))
    assert isfinite(out.final_wall_temperature_k)
    assert 0. <= abs(out.energy_residual_j) < 1e-5
