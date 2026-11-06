"""TES-v0.1--v0.3 analytic, conservation and numerical contract tests."""
import math

import pytest

from sco2_braytonbench.thermal_storage import (
    PackedBedSpec, PackedBedState, solid_soc, step_packed_bed,
    stored_energy_j,
)
from sco2_braytonbench.tes_schumann import schumann_inlet_step


def spec(n=16, hv=80000.0):
    return PackedBedSpec(
        length_m=1.0, area_m2=1.0, porosity=0.4,
        fluid_density_kg_m3=1000.0, fluid_cp_j_kg_k=1000.0,
        solid_density_kg_m3=2600.0, solid_cp_j_kg_k=800.0,
        interphase_hv_w_m3_k=hv, n_cells=n
    )


@pytest.mark.parametrize("field,value", [
    ("length_m", 0), ("area_m2", float("nan")),
    ("fluid_density_kg_m3", -1), ("fluid_cp_j_kg_k", float("inf")),
    ("porosity", 0), ("porosity", 1), ("porosity", -0.1),
    ("solid_density_kg_m3", 0), ("solid_cp_j_kg_k", -1),
    ("interphase_hv_w_m3_k", -1), ("interphase_hv_w_m3_k", float("nan"))
])
def test_spec_invalid_physics(field, value):
    d = dict(vars(spec()))
    d[field] = value
    with pytest.raises(ValueError):
        PackedBedSpec(**d)


@pytest.mark.parametrize("n", [0, -1, 2.5, True])
def test_invalid_cell_count(n):
    d = dict(vars(spec()))
    d["n_cells"] = n
    with pytest.raises(ValueError):
        PackedBedSpec(**d)


def test_full_fluid_and_solid_holdup_is_independent_of_n():
    s1, s128 = spec(1), spec(128)
    assert s1.total_fluid_capacity_j_k == pytest.approx(400000.0)
    assert s1.total_solid_capacity_j_k == pytest.approx(1248000.0)
    assert s128.total_fluid_capacity_j_k == pytest.approx(s1.total_fluid_capacity_j_k)
    assert s128.total_solid_capacity_j_k == pytest.approx(s1.total_solid_capacity_j_k)


def test_uniform_inlet_state_is_exact_fixed_point():
    s = spec(13)
    st = PackedBedState.uniform(s, 480.0, 480.0)
    for mdot in (40.0, -40.0, 0.0):
        r = step_packed_bed(s, st, inlet_k=480, mdot_kg_s=mdot, duration_s=25)
        assert r.state == st
        assert r.conservation_residual_j == 0.0
        assert r.energy_boundary_j == 0.0


def test_zero_exchange_has_exponential_one_cell_transport():
    s = spec(1, hv=0)
    st = PackedBedState.uniform(s, 350.0, 350.0)
    r = step_packed_bed(
        s, st, inlet_k=650, mdot_kg_s=40, duration_s=3, max_step_s=0.05
    )
    rate = 40 * s.fluid_cp_j_kg_k / s.fluid_cell_capacity_j_k
    expected = 650 - 300 * math.exp(-rate * 3)
    assert r.state.fluid_k[0] == pytest.approx(expected, abs=2e-5)
    assert r.state.solid_k == st.solid_k
    assert abs(r.conservation_residual_j) < 1e-5


def test_zero_flow_has_exact_two_lump_equilibrium():
    s = spec(1)
    st = PackedBedState.uniform(s, 520, 340)
    r = step_packed_bed(
        s, st, inlet_k=800, mdot_kg_s=0, duration_s=10, max_step_s=0.05
    )
    cf, cs, h = (s.fluid_cell_capacity_j_k, s.solid_cell_capacity_j_k,
                 s.interphase_cell_w_k)
    equilibrium = (cf * 520 + cs * 340) / (cf + cs)
    decay = math.exp(-h * (1 / cf + 1 / cs) * 10)
    assert r.state.fluid_k[0] == pytest.approx(equilibrium + (520 - equilibrium) * decay, abs=2e-5)
    assert r.state.solid_k[0] == pytest.approx(equilibrium + (340 - equilibrium) * decay, abs=2e-5)
    assert r.energy_boundary_j == 0
    assert abs(r.conservation_residual_j) < 1e-5


def test_flow_reversal_is_exact_mirror_for_symmetric_thermal_bed():
    s = spec(7)
    st = PackedBedState(
        tuple(370 + 8 * i for i in range(7)),
        tuple(390 + 5 * i for i in range(7))
    )
    rev = PackedBedState(st.fluid_k[::-1], st.solid_k[::-1])
    fwd = step_packed_bed(s, st, inlet_k=620, mdot_kg_s=30, duration_s=7)
    backward = step_packed_bed(s, rev, inlet_k=620, mdot_kg_s=-30, duration_s=7)
    assert backward.state.fluid_k == pytest.approx(fwd.state.fluid_k[::-1])
    assert backward.state.solid_k == pytest.approx(fwd.state.solid_k[::-1])
    assert backward.energy_boundary_j == pytest.approx(fwd.energy_boundary_j)


def test_first_law_closes_charge_and_discharge():
    s = spec(32)
    initial = PackedBedState.uniform(s, 350, 350)
    charge = step_packed_bed(s, initial, inlet_k=650,
                             mdot_kg_s=40, duration_s=45)
    discharge = step_packed_bed(s, charge.state, inlet_k=350,
                                mdot_kg_s=-40, duration_s=75)
    for r in (charge, discharge):
        assert abs(r.conservation_residual_j) <= max(1e-5, abs(r.energy_boundary_j) * 1e-10)
        assert r.courant_per_substep <= 0.75 + 1e-14
        assert r.exchange_fluid_per_substep <= 0.75 + 1e-14
        assert r.exchange_solid_per_substep <= 0.75 + 1e-14
    assert charge.energy_boundary_j > 0
    assert discharge.energy_boundary_j < 0
    assert stored_energy_j(s, discharge.state, reference_k=350) == pytest.approx(
        charge.energy_change_j + discharge.energy_change_j, abs=1e-4
    )
    assert 0 < solid_soc(s, charge.state, cold_k=350, hot_k=650) < 1
    assert solid_soc(s, discharge.state, cold_k=350, hot_k=650) < solid_soc(
        s, charge.state, cold_k=350, hot_k=650)


def test_no_hidden_soc_clipping_and_fail_closed():
    s = spec()
    assert solid_soc(s, PackedBedState.uniform(s, 700, 700),
                     cold_k=350, hot_k=650) > 1
    with pytest.raises(ValueError):
        solid_soc(s, PackedBedState.uniform(s, 400, 400),
                  cold_k=650, hot_k=350)
    st = PackedBedState.uniform(s, 350, 350)
    with pytest.raises(ValueError):
        step_packed_bed(s, st, inlet_k=float("nan"), mdot_kg_s=1, duration_s=1)
    with pytest.raises(ValueError):
        step_packed_bed(s, st, inlet_k=650, mdot_kg_s=50, duration_s=10000,
                        max_substeps=10)
    with pytest.raises(ValueError):
        step_packed_bed(s, st, inlet_k=650, mdot_kg_s=40, duration_s=-1)


def test_schumann_reference_characteristic_and_bessel_series_limits():
    s = spec(32)
    assert schumann_inlet_step(
        s, x_m=1, t_s=5, mdot_kg_s=40, initial_k=350, inlet_k=650
    ).fluid_k == 350
    at_characteristic = schumann_inlet_step(
        s, x_m=1, t_s=10, mdot_kg_s=40, initial_k=350, inlet_k=650)
    assert at_characteristic.fluid_k == pytest.approx(350 + 300 * math.exp(-2))
    assert at_characteristic.solid_k == pytest.approx(350)
    at_entry = schumann_inlet_step(
        s, x_m=0, t_s=1, mdot_kg_s=40, initial_k=350, inlet_k=650)
    assert at_entry.fluid_k == pytest.approx(650)
    assert at_entry.solid_k > 350
    late = schumann_inlet_step(
        s, x_m=1, t_s=500, mdot_kg_s=40, initial_k=350, inlet_k=650)
    assert late.fluid_k == pytest.approx(650, abs=1e-6)
    assert late.solid_k == pytest.approx(650, abs=1e-6)


def test_spatial_refinement_converges_to_continuous_schumann():
    """Independent step response at outlet + centre solid node, same t."""
    t = 30.0
    outlet_ref = schumann_inlet_step(
        spec(16), x_m=1.0, t_s=t, mdot_kg_s=40,
        initial_k=350, inlet_k=650).fluid_k
    errors = []
    centre_errors = []
    for n in (16, 32, 64, 128):
        s = spec(n)
        r = step_packed_bed(s, PackedBedState.uniform(s, 350, 350),
                            inlet_k=650, mdot_kg_s=40,
                            duration_s=t, max_step_s=0.04)
        errors.append(abs(r.outlet_k - outlet_ref))
        k = n // 2
        xmid = (k + 0.5) * s.cell_dx_m
        mid_ref = schumann_inlet_step(
            s, x_m=xmid, t_s=t, mdot_kg_s=40,
            initial_k=350, inlet_k=650).solid_k
        centre_errors.append(abs(r.state.solid_k[k] - mid_ref))
        assert abs(r.conservation_residual_j) < 1e-4
    assert all(a > b for a, b in zip(errors, errors[1:])), errors
    assert all(a > b for a, b in zip(centre_errors, centre_errors[1:])), centre_errors
    assert errors[-1] < 8
    assert centre_errors[-1] < 8


def test_time_refinement_separate_from_spatial_error():
    s = spec(64)
    st = PackedBedState.uniform(s, 350, 350)
    a = step_packed_bed(s, st, inlet_k=650, mdot_kg_s=40,
                        duration_s=20, max_step_s=0.1)
    b = step_packed_bed(s, st, inlet_k=650, mdot_kg_s=40,
                        duration_s=20, max_step_s=0.05)
    c = step_packed_bed(s, st, inlet_k=650, mdot_kg_s=40,
                        duration_s=20, max_step_s=0.025)
    assert abs(b.outlet_k - c.outlet_k) < abs(a.outlet_k - c.outlet_k)
    assert abs(a.outlet_k - c.outlet_k) < 0.1
