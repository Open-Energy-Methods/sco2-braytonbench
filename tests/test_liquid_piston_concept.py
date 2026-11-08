"""Independent algebraic and dimensional regression for the UNVALIDATED piston concept."""
import math

import pytest
from sco2_braytonbench.liquid_piston_concept import (
    LiquidPistonSpec, gas_state, gas_compression_work, simulate_liquid_piston,
)


def test_isothermal_gas_exact_log_work_and_pvt():
    s = LiquidPistonSpec()
    r = simulate_liquid_piston(s)
    assert r.gas_compression_work_j == pytest.approx(
        s.gas_initial_pressure_pa * s.gas_initial_volume_m3 *
        math.log(s.gas_initial_volume_m3 / s.gas_final_volume_m3), rel=1e-13
    )
    assert r.gas_internal_energy_increase_j == 0
    assert r.reservoir_heat_rejected_on_compression_j == pytest.approx(r.gas_compression_work_j)
    for x in (0, 0.21, 0.6, 1):
        v, p, t = gas_state(s, x)
        assert p * v == pytest.approx(s.gas_mass_kg * s.gas_specific_r_j_kg_k * t)
        assert t == s.gas_initial_temperature_k


def test_adiabatic_first_law_and_temperature_growth():
    s = LiquidPistonSpec(gas_path="reversible_adiabatic", heat_capacity_ratio=1.4)
    r = simulate_liquid_piston(s)
    v, p, t = gas_state(s, 1)
    ratio = s.gas_initial_volume_m3 / v
    assert t == pytest.approx(s.gas_initial_temperature_k * ratio ** 0.4)
    assert p == pytest.approx(s.gas_initial_pressure_pa * ratio ** 1.4)
    assert p * v == pytest.approx(s.gas_mass_kg * s.gas_specific_r_j_kg_k * t)
    assert r.reservoir_heat_rejected_on_compression_j == 0
    assert r.gas_internal_energy_increase_j == pytest.approx(r.gas_compression_work_j)
    assert r.gas_compression_work_j > simulate_liquid_piston(LiquidPistonSpec()).gas_compression_work_j


@pytest.mark.parametrize("path", ["isothermal", "reversible_adiabatic"])
@pytest.mark.parametrize("pin,pex", [(20e6, 12e6), (10e6, 10e6), (21e6, 0)])
def test_energy_cannot_be_created_by_hysteresis(path, pin, pex):
    s = LiquidPistonSpec(gas_path=path, intrusion_overpressure_pa=pin, extrusion_overpressure_pa=pex)
    r = simulate_liquid_piston(s)
    expect = (pin - pex) * s.displaced_liquid_volume_m3
    assert r.hysteresis_dissipation_j == pytest.approx(expect)
    assert r.hydraulic_input_work_j == pytest.approx(r.hydraulic_recovered_work_j + expect)
    assert 0 < r.work_recovery_fraction <= 1
    assert max(abs(r.loading_energy_residual_j), abs(r.unloading_energy_residual_j),
               abs(r.full_cycle_energy_residual_j)) < 1e-9
    assert len(r.points) == 2 * (s.samples_per_branch + 1)


def test_independent_midpoint_pdv_quadrature():
    s = LiquidPistonSpec()
    result = simulate_liquid_piston(s)
    n = 20000
    dv = s.displaced_liquid_volume_m3 / n
    approximate = math.fsum(gas_state(s, (i + .5) / n)[1] * dv for i in range(n))
    assert approximate == pytest.approx(result.gas_compression_work_j, rel=2e-10)


def test_pressure_volume_path_and_hysteresis_orientation():
    s = LiquidPistonSpec(samples_per_branch=18)
    r = simulate_liquid_piston(s)
    i = r.points[:19]
    o = r.points[19:]
    assert [p.intrusion_fraction for p in i] == pytest.approx([j / 18 for j in range(19)])
    assert [p.intrusion_fraction for p in o] == pytest.approx([j / 18 for j in range(18, -1, -1)])
    assert i[0].gas_volume_m3 > i[-1].gas_volume_m3
    assert i[0].gas_pressure_pa < i[-1].gas_pressure_pa
    for a, b in zip(i, reversed(o)):
        assert a.gas_volume_m3 == pytest.approx(b.gas_volume_m3)
        assert a.gas_pressure_pa == pytest.approx(b.gas_pressure_pa)
        assert a.hydraulic_pressure_pa - b.hydraulic_pressure_pa == pytest.approx(
            s.intrusion_overpressure_pa - s.extrusion_overpressure_pa
        )


def test_scaling_entire_volume_increases_work_not_pressure():
    a = LiquidPistonSpec()
    b = LiquidPistonSpec(gas_initial_volume_m3=2*a.gas_initial_volume_m3,
                         displaced_liquid_volume_m3=2*a.displaced_liquid_volume_m3)
    ar = simulate_liquid_piston(a)
    br = simulate_liquid_piston(b)
    for xa, xb in zip(ar.points, br.points):
        assert xa.gas_pressure_pa == pytest.approx(xb.gas_pressure_pa)
    assert br.hydraulic_input_work_j == pytest.approx(2*ar.hydraulic_input_work_j)
    assert br.hydraulic_recovered_work_j == pytest.approx(2*ar.hydraulic_recovered_work_j)
    assert br.hysteresis_dissipation_j == pytest.approx(2*ar.hysteresis_dissipation_j)


@pytest.mark.parametrize("update", [
    {"gas_initial_volume_m3": 0}, {"gas_initial_pressure_pa": -2},
    {"gas_initial_pressure_pa": float("nan")},
    {"gas_initial_volume_m3": 0.0003}, {"displaced_liquid_volume_m3": 0},
    {"displaced_liquid_volume_m3": 0.002},
    {"intrusion_overpressure_pa": 10e6, "extrusion_overpressure_pa": 12e6},
    {"extrusion_overpressure_pa": -1},
    {"gas_path": "unknown"}, {"heat_capacity_ratio": 1}, {"heat_capacity_ratio": 3},
    {"samples_per_branch": 1}, {"samples_per_branch": 0.5},
    {"gas_specific_r_j_kg_k": True},
])
def test_invalid_states_rejected(update):
    with pytest.raises(ValueError):
        LiquidPistonSpec(**update)


def test_out_of_range_stroke_rejected_and_reporting_flags():
    s = LiquidPistonSpec()
    for x in (-1e-6, 1.0001, float("inf"), True):
        with pytest.raises(ValueError):
            gas_state(s, x)
    r = simulate_liquid_piston(s)
    report = r.to_json_dict()
    assert report["evidence_class"].startswith("illustrative")
    assert any("experimental" in x for x in report["not_claimed"])
    assert report["spec"]["gas_path"] == "isothermal"
