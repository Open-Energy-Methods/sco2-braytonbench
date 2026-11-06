"""WP2b source / wall / Brayton coupling, independent constant-cp verification.

Every base fixture is an artificial ideal gas for mathematical testing,
not experimental CO2, CARBOSOLA hardware or a closed-loop control trial.
"""
from dataclasses import replace
from math import exp, isfinite, log

import pytest

from sco2_braytonbench import (
    CycleInputs, DomainError, IdealGasFixture, PressureLosses,
)
from sco2_braytonbench.dynamic_whr import (
    FiniteGasLoad, WallCycleEquipment,
    simulate_wall_coupled_cycle, solve_wall_cycle_instant, wall_cycle_step,
)

F = IdealGasFixture(cp=1000., gas_constant=200.)


def cycle():
    return CycleInputs(
        p1_pa=8e6, p4_pa=24e6, t1_k=310., t4_k=600.,
        mdot_kg_s=10., eta_compressor=.89, eta_turbine=.90,
        losses=PressureLosses(100e3, 150e3, 100e3, 50e3),
        recuperator_ua_w_k=0., segments=6,
    )


def equipment():
    return WallCycleEquipment(
        wall_capacity_j_k=2e6,
        gas_to_wall_ua_w_k=40e3,
        wall_to_co2_ua_w_k=25e3,
        gas_cp_j_kg_k=1100.,
        minimum_stack_temperature_k=360.,
        t4_bounds_k=(560., 760.),
        minimum_wall_co2_approach_k=2.,
        minimum_gas_wall_approach_k=1.,
        co2_heater_segments=6,
        root_scan_intervals=8,
    )


def load(temp=850., mdot=30., dt=5.):
    return FiniteGasLoad(temp, mdot, dt)


def independent_closed_form():
    # Independently derive from ideal-gas isentropic compressor:
    # T2s=T1*(P2/P1)^((gamma-1)/gamma)=T1*(P2/P1)^(R/cp)
    base = cycle()
    p2 = base.p4_pa + base.losses.heater + base.losses.cold_recup
    t3 = base.t1_k + (
        base.t1_k*(p2/base.p1_pa)**(F.gas_constant/F.cp)
        - base.t1_k
    ) / base.eta_compressor
    cg = load().mass_flow_kg_s * equipment().gas_cp_j_kg_k
    cc = base.mdot_kg_s * F.cp
    hg = cg*(1-exp(-equipment().gas_to_wall_ua_w_k/cg))
    hc = cc*(1-exp(-equipment().wall_to_co2_ua_w_k/cc))
    teq = (hg*850. + hc*t3)/(hg+hc)
    tau = equipment().wall_capacity_j_k/(hg+hc)
    return t3, cg, cc, hg, hc, teq, tau


def test_finite_gas_and_co2_wall_ua_match_separate_textbook_equations():
    base = cycle()
    equip = equipment()
    out = solve_wall_cycle_instant(F, base, equip, 700., load())
    t3, cg, cc, hg, hc, _, _ = independent_closed_form()
    expected_t4 = 700. - (700.-t3)*exp(-equip.wall_to_co2_ua_w_k/cc)
    expected_gas_out = 700. + (850.-700.)*exp(-equip.gas_to_wall_ua_w_k/cg)

    assert out.wall_temperature_k == 700.
    assert out.turbine_inlet_temperature_k == pytest.approx(expected_t4, abs=.05)
    assert out.hot_gas_outlet_temperature_k == pytest.approx(
        expected_gas_out, rel=1e-13
    )
    assert out.hot_to_wall_w == pytest.approx(
        cg*(850.-expected_gas_out), rel=1e-12
    )
    assert out.wall_to_co2_w == pytest.approx(
        cc*(expected_t4-t3), rel=4e-4
    )
    assert out.cycle.heater_w == pytest.approx(out.wall_to_co2_w)
    assert out.cycle.heater_w - out.cycle.cooler_w - out.cycle.net_w == (
        pytest.approx(0., abs=1e-6)
    )
    assert out.co2_wall_required_ua_w_k == pytest.approx(
        equip.wall_to_co2_ua_w_k, rel=1e-4
    )
    assert out.co2_wall_min_approach_k >= equip.minimum_wall_co2_approach_k


def test_dynamic_wall_matches_independent_first_order_constant_cp_response():
    equip = equipment()
    _, _, _, _, _, teq, tau = independent_closed_form()
    records = simulate_wall_coupled_cycle(
        F, cycle(), equip, 700., [load()] * 12,
    )
    expected_t60 = teq + (700. - teq)*exp(-60./tau)
    assert records[-1].time_end_s == pytest.approx(60.)
    assert records[-1].final_wall_temperature_k == pytest.approx(
        expected_t60, abs=.04
    )
    assert abs(records[-1].final_wall_temperature_k-700.) > 1.
    assert records[-1].final.turbine_inlet_temperature_k > (
        records[0].initial.turbine_inlet_temperature_k
    )
    assert all(abs(r.wall_energy_residual_j) < 1e-5 for r in records)
    assert all(abs(r.combined_gas_cycle_wall_residual_j) < 1e-5
               for r in records)

    ehot=sum(r.hot_gas_to_wall_energy_j for r in records)
    eco2=sum(r.wall_to_co2_energy_j for r in records)
    ewall=sum(r.wall_stored_energy_j for r in records)
    ecool=sum(r.cooler_energy_j for r in records)
    enet=sum(r.net_shaft_energy_j for r in records)
    assert ehot - eco2 == pytest.approx(ewall, abs=1e-4)
    assert ehot - ecool - enet == pytest.approx(ewall, abs=1e-4)


def test_step_refinement_against_textbook_closed_form():
    eq = independent_closed_form()[5]
    tau = independent_closed_form()[6]
    target=eq + (700.-eq)*exp(-40./tau)
    coarse=simulate_wall_coupled_cycle(
        F,cycle(),equipment(),700.,[load(dt=10.)]*4
    )[-1].final_wall_temperature_k
    fine=simulate_wall_coupled_cycle(
        F,cycle(),equipment(),700.,[load(dt=2.5)]*16
    )[-1].final_wall_temperature_k
    assert abs(fine-target)<.05
    assert abs(fine-target)<=abs(coarse-target)+.01


def test_load_temperature_and_mass_flow_disturbances_change_wall_and_power():
    baseline=simulate_wall_coupled_cycle(
        F,cycle(),equipment(),700.,[load()]*6
    )
    disrupted=simulate_wall_coupled_cycle(
        F,cycle(),equipment(),700.,[
            load(),load(),load(temp=810.),load(temp=810.),
            load(mdot=20.),load(mdot=20.),
        ]
    )
    assert disrupted[1].final_wall_temperature_k == pytest.approx(
        baseline[1].final_wall_temperature_k
    )
    assert disrupted[-1].final_wall_temperature_k < (
        baseline[-1].final_wall_temperature_k
    )
    assert disrupted[-1].final.cycle.net_w < baseline[-1].final.cycle.net_w


def test_zero_dynamic_storage_is_not_a_sequence_of_steady_states():
    with pytest.raises(DomainError, match="wall_capacity_j_k"):
        replace(equipment(),wall_capacity_j_k=0.)
    records=simulate_wall_coupled_cycle(
        F,cycle(),equipment(),700.,[load()]*2
    )
    assert records[0].final_wall_temperature_k != 700.
    assert records[1].initial_wall_temperature_k == pytest.approx(
        records[0].final_wall_temperature_k
    )


@pytest.mark.parametrize("bad",[
    float("nan"),float("inf"),0.,-1.,"50",
])
@pytest.mark.parametrize("field",[
    "wall_capacity_j_k","gas_to_wall_ua_w_k","wall_to_co2_ua_w_k",
    "gas_cp_j_kg_k","minimum_stack_temperature_k",
])
def test_invalid_equipment_fields_fail_closed(field,bad):
    with pytest.raises(DomainError):
        replace(equipment(), **{field:bad})


@pytest.mark.parametrize("field",[
    "inlet_temperature_k","mass_flow_kg_s","duration_s",
])
@pytest.mark.parametrize("bad",[float("nan"),float("inf"),0.,-1.])
def test_invalid_source_fields_fail_closed(field,bad):
    with pytest.raises(DomainError):
        replace(load(),**{field:bad})


def test_unbracketed_wall_to_co2_ua_is_rejected_not_assumed():
    with pytest.raises(DomainError,match="not bracketed|no feasible"):
        solve_wall_cycle_instant(
            F, cycle(), replace(equipment(),wall_to_co2_ua_w_k=1e8),
            700., load()
        )


def test_gas_stack_floor_and_reverse_heat_are_not_silently_allowed():
    with pytest.raises(DomainError,match="stack floor"):
        solve_wall_cycle_instant(
            F,cycle(),replace(equipment(),minimum_stack_temperature_k=800.),
            700.,load()
        )
    with pytest.raises(DomainError,match="hot-gas inlet"):
        solve_wall_cycle_instant(F,cycle(),equipment(),700.,load(temp=690.))


def test_fixed_step_must_be_subdivided_when_too_long():
    with pytest.raises(DomainError,match="subdivide"):
        wall_cycle_step(F,cycle(),equipment(),700.,load(dt=100.))


def test_invalid_thermal_profile_reports_interval_without_partial_success():
    with pytest.raises(DomainError,match="interval 1"):
        simulate_wall_coupled_cycle(
            F,cycle(),equipment(),700.,[load(),load(temp=650.)]
        )


def test_no_profile_fails_explicitly():
    with pytest.raises(DomainError,match="at least one interval"):
        simulate_wall_coupled_cycle(F,cycle(),equipment(),700.,[])


def test_cycle_source_uses_fixed_CO2_cold_inlet_and_both_energy_balances():
    results=simulate_wall_coupled_cycle(F,cycle(),equipment(),700.,[load()])
    r=results[0]
    assert r.final.cycle.states[0].t == pytest.approx(cycle().t1_k)
    assert r.hot_gas_to_wall_energy_j > r.wall_to_co2_energy_j > 0.
    assert r.cooler_energy_j > 0.
    assert r.net_shaft_energy_j > 0.
    assert isfinite(r.combined_gas_cycle_wall_residual_j)
