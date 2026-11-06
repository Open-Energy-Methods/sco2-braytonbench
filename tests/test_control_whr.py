"""WP3: independent source mixing, actuation bounds and sampled wall PI tests.

Analytical ideal-gas fixture checks mathematical and control causality,
not a measured CO2 plant nor an optimal/calibrated industrial controller.
"""
from dataclasses import replace
from math import isfinite

import pytest

from sco2_braytonbench import CycleInputs, IdealGasFixture, PressureLosses, DomainError
from sco2_braytonbench.control_whr import (
    SourceBypass, WallPI, control_performance, simulate_bypass_control,
    _next_bypass,
)
from sco2_braytonbench.dynamic_whr import FiniteGasLoad, WallCycleEquipment

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
        wall_capacity_j_k=2e6, gas_to_wall_ua_w_k=40e3,
        wall_to_co2_ua_w_k=25e3, gas_cp_j_kg_k=1100.,
        minimum_stack_temperature_k=360., t4_bounds_k=(560., 760.),
        co2_heater_segments=6, root_scan_intervals=8,
    )


def actuator():
    return SourceBypass(
        max_fraction=.85, max_rate_fraction_s=.025,
        minimum_active_mass_flow_kg_s=1.,
    )


def controller():
    return WallPI(
        setpoint_temperature_k=700., kp_fraction_k=.04,
        ki_fraction_k_s=.0025, bias_fraction=.15,
        tracking_gain_s=.2, integral_limit_fraction=1.0,
    )


def loads(n=12):
    return [
        FiniteGasLoad(850. if i < n // 2 else 880., 30., 5.)
        for i in range(n)
    ]


def run(*, pi=None, n=12, fraction=.15, source=None):
    return simulate_bypass_control(
        F, cycle(), equipment(), source if source is not None else loads(n),
        actuator(), initial_wall_temperature_k=700.,
        initial_bypass_fraction=fraction,
        setpoint_temperature_k=700.,
        controller=pi,
    )


def test_bypass_branch_mass_conservation_and_independent_energy_mixing():
    rows=run(n=3)
    for row in rows:
        load = row.plant.input_load
        total = row.active_gas_flow_kg_s+row.diverted_gas_flow_kg_s
        expected_total=30.
        assert total == pytest.approx(expected_total, rel=1e-15)
        assert row.active_gas_flow_kg_s == pytest.approx(
            (1.-row.bypass_fraction)*expected_total
        )
        assert load.mass_flow_kg_s == pytest.approx(
            row.active_gas_flow_kg_s
        )
        t_gas = load.inlet_temperature_k  # Actual step source; may change.
        active_t_initial = row.plant.initial.hot_gas_outlet_temperature_k
        mixed = (
            (row.active_gas_flow_kg_s*active_t_initial
             + row.diverted_gas_flow_kg_s*t_gas)/expected_total
        )
        assert row.mixed_gas_outlet_initial_k == pytest.approx(mixed)
        # Independent control-volume source enthalpy consistency:
        expected_instant_heat = (
            expected_total*equipment().gas_cp_j_kg_k
            * (t_gas-row.mixed_gas_outlet_initial_k)
        )
        assert expected_instant_heat == pytest.approx(
            row.plant.initial.hot_to_wall_w,rel=1e-12
        )
        qintegral = (
            expected_total*equipment().gas_cp_j_kg_k
            * (t_gas-row.mixed_gas_outlet_mean_k)
            * 5.
        )
        assert qintegral == pytest.approx(
            row.plant.hot_gas_to_wall_energy_j,abs=1e-7
        )
        assert abs(row.source_energy_residual_j)<1e-7
        assert abs(row.combined_total_stream_residual_j)<1e-5
        assert row.mixed_gas_outlet_initial_k > active_t_initial
        assert row.diverted_gas_flow_kg_s > 0


def test_more_bypass_reduces_wall_heat_input_at_the_same_wall_state():
    low = run(n=1,fraction=.0)[0]
    high = run(n=1,fraction=.5)[0]
    assert high.plant.initial.wall_temperature_k == pytest.approx(
        low.plant.initial.wall_temperature_k
    )
    assert high.plant.initial.hot_to_wall_w < low.plant.initial.hot_to_wall_w
    assert high.plant.final_wall_temperature_k < low.plant.final_wall_temperature_k


def test_slew_rate_is_a_hard_bound_even_for_saturated_PI():
    act = SourceBypass(max_fraction=.85,max_rate_fraction_s=.01)
    pi = WallPI(
        setpoint_temperature_k=700., kp_fraction_k=.2,
        ki_fraction_k_s=.01, bias_fraction=.2, tracking_gain_s=.1,
    )
    raw,req,actual,nxt = _next_bypass(
        act,pi,750.,700.,.1,0.,5.
    )
    assert raw > act.max_fraction
    assert req == act.max_fraction
    assert actual == pytest.approx(.15)
    assert nxt < pi.ki_fraction_k_s*50.*5.
    assert abs((actual-.1)/5.) <= act.max_rate_fraction_s + 1e-12


def test_back_calculation_antiwindup_tracks_achieved_valve_not_raw_request():
    act = SourceBypass(max_fraction=.7,max_rate_fraction_s=.025)
    pi = WallPI(
        setpoint_temperature_k=700.,kp_fraction_k=.1,
        ki_fraction_k_s=.001,bias_fraction=.2,tracking_gain_s=.1,
        integral_limit_fraction=.5,
    )
    position, integ=0.,0.
    for _ in range(15):
        raw,request,position,integ = _next_bypass(
            act,pi,720.,700.,position,integ,2.
        )
        assert 0. <= position <= .7
        assert abs(integ)<=.5
    assert position == pytest.approx(.7)
    assert integ < 0  # tracking term prevents positive integrator windup
    _,_,next_position,_ = _next_bypass(
        act,pi,680.,700.,position,integ,2.
    )
    assert next_position < position


def test_controller_is_causal_and_uses_no_future_load_values():
    all_loads=loads(8)
    first=run(pi=controller(),source=all_loads)
    changed=all_loads[:4]+[
        FiniteGasLoad(900.,30.,5.) for _ in range(4)
    ]
    second=run(pi=controller(),source=changed)
    for i in range(4):
        assert first[i].bypass_fraction == pytest.approx(
            second[i].bypass_fraction
        )
        assert first[i].plant.final_wall_temperature_k == pytest.approx(
            second[i].plant.final_wall_temperature_k
        )


def test_PI_vs_open_loop_on_identical_source_profile_and_evidence_metrics():
    source=loads(18)
    open_loop=run(source=source)
    closed_loop=run(pi=controller(),source=source)
    m_open=control_performance(open_loop)
    m_pi=control_performance(closed_loop)
    assert len(open_loop)==len(closed_loop)==len(source)
    assert all(o.plant.input_load.inlet_temperature_k ==
               c.plant.input_load.inlet_temperature_k
               for o,c in zip(open_loop,closed_loop))
    assert all(0 <= r.bypass_fraction <= actuator().max_fraction
               for r in closed_loop)
    assert any(r.bypass_fraction != pytest.approx(.15)
               for r in closed_loop)
    # Scenario-specific demonstration, not a general PI superiority claim.
    assert m_pi.sample_endpoint_rmse_k < m_open.sample_endpoint_rmse_k
    assert m_pi.absolute_error_trapezoid_k_s < m_open.absolute_error_trapezoid_k_s
    assert abs(m_open.total_energy_residual_j) < 1e-3
    assert abs(m_pi.total_energy_residual_j) < 1e-3
    assert all(abs(r.applied_rate_fraction_s) <=
               actuator().max_rate_fraction_s + 1e-12
               for r in closed_loop)


@pytest.mark.parametrize("bad",[-.1, 1., float("nan"),float("inf")])
def test_initial_position_invalid_is_rejected(bad):
    with pytest.raises(DomainError):
        run(fraction=bad,n=1)


@pytest.mark.parametrize("bad",[0.,1.,-1.,float("nan"),float("inf")])
def test_invalid_maximum_bypass_fail_closed(bad):
    with pytest.raises(DomainError):
        replace(actuator(),max_fraction=bad)


@pytest.mark.parametrize("bad",[-1.,float("nan"),float("inf")])
def test_invalid_PI_gain_rejected(bad):
    with pytest.raises(DomainError):
        replace(controller(),kp_fraction_k=bad)


def test_mismatch_controller_setpoint_rejected():
    with pytest.raises(DomainError,match="setpoint"):
        run(pi=replace(controller(),setpoint_temperature_k=710.),n=1)


def test_empty_source_profile_explicit_failure():
    with pytest.raises(DomainError,match="one or more source intervals"):
        run(source=[])


def test_minimum_active_mass_flow_enforced():
    with pytest.raises(DomainError,match="minimum active flow"):
        simulate_bypass_control(
            F,cycle(),equipment(),[FiniteGasLoad(850.,1.1,5.)],
            SourceBypass(max_fraction=.85,max_rate_fraction_s=.1,
                         minimum_active_mass_flow_kg_s=1.),
            initial_wall_temperature_k=700.,initial_bypass_fraction=.5,
            setpoint_temperature_k=700.,
        )


def test_tracking_gain_sample_stability_gate():
    pi=replace(controller(),tracking_gain_s=.5)
    with pytest.raises(DomainError,match="gain\\*duration"):
        run(pi=pi,n=1)


def test_open_loop_has_no_integrator_drift_or_unintended_actuation():
    results=run(n=7)
    assert all(r.bypass_fraction==pytest.approx(.15) for r in results)
    assert all(r.integral_fraction_after==0 for r in results)
    assert all(r.applied_rate_fraction_s == 0 for r in results)
    assert all(isfinite(r.plant.net_shaft_energy_j) for r in results)
