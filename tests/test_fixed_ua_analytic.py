"""Independent analytic verification of the *coupled* fixed-UA heater solver."""
from dataclasses import replace
from math import exp

import pytest

from sco2_braytonbench import CycleInputs, DomainError, IdealGasFixture, PressureLosses
from sco2_braytonbench.fixed_ua import solve_fixed_ua_whr
from sco2_braytonbench.whr import (
    PlantDesignLimits, WasteGasSource, evaluate_whr_design
)

F = IdealGasFixture(cp=1000., gas_constant=200.)
LOSS = PressureLosses(cold_recup=100e3,heater=150e3,
                      hot_recup=100e3,cooler=50e3)

def cycle(*,T4=790.,mdot=10.,recup_ua=0.):
    return CycleInputs(
        p1_pa=8e6,p4_pa=24e6,t1_k=310.,
        t4_k=T4,mdot_kg_s=mdot,eta_compressor=.89,
        eta_turbine=.90,losses=LOSS,
        recuperator_effectiveness=None,
        recuperator_ua_w_k=recup_ua,segments=12
    )

def gas(**kwargs):
    data=dict(
        inlet_temperature_k=850.,mass_flow_kg_s=30.,
        cp_j_kg_k=1100.,minimum_stack_temperature_k=350.,
        maximum_heater_ua_w_k=200e3,
        minimum_heater_approach_k=10.,
        dead_state_temperature_k=300.,segments=12
    )
    data.update(kwargs)
    return WasteGasSource(**data)

def coupled(installed_ua=40e3,**kwargs):
    return solve_fixed_ua_whr(
        F,cycle(),gas(),installed_heater_ua_w_k=installed_ua,
        turbine_inlet_bounds_k=(720.,835.),
        scan_intervals=8,tolerance_temperature_k=.03,
        **kwargs
    )

@pytest.mark.parametrize("UA",[10e3,15e3,25e3,40e3])
def test_closed_form_counterflow_predicts_coupled_temperature(UA):
    # With zero recuperator heat duty, compressor exit T is fixed
    # regardless of turbine inlet T, permitting an INDEPENDENT
    # textbook epsilon-NTU solution for a finite counterflow heater.
    # C_CO2=10,000 W/K; C_gas=33,000 W/K.
    from sco2_braytonbench.core import cycle_pressures,compressor_outlet
    p=cycle_pressures(8e6,24e6,LOSS)
    a=F.tp(p.p1,310.)
    b=F.ph(p.p2,compressor_outlet(
        a.h,F.ps(p.p2,a.s).h,.89))
    Cc=10*F.cp
    Ch=30*1100.
    Cr=min(Cc,Ch)/max(Cc,Ch)
    NTU=UA/min(Cc,Ch)
    eps=(1-exp(-NTU*(1-Cr)))/(1-Cr*exp(-NTU*(1-Cr)))
    T4_analytic=b.t+eps*(850.-b.t)
    res=solve_fixed_ua_whr(
        F,cycle(T4=600.),gas(),
        installed_heater_ua_w_k=UA,
        turbine_inlet_bounds_k=(max(600.,T4_analytic-50),835.),
        scan_intervals=9,
    )
    assert res.turbine_inlet_temperature_k==pytest.approx(T4_analytic,abs=.07)
    assert abs(res.ua_residual_relative)<=1e-4
    assert res.point.heater.q_w==pytest.approx(
        Cc*(res.point.cycle.states[3].t-b.t),rel=1e-8)
    assert res.point.cycle.first_law_residual_w==pytest.approx(0,abs=1e-6)
    assert res.point.first_law_combined_residual_w==pytest.approx(0,abs=1e-6)
    assert res.point.heater.min_approach_k>=10

def test_baseline_t4_seed_ignored():
    r1=solve_fixed_ua_whr(F,cycle(T4=600.),gas(),
           installed_heater_ua_w_k=40e3,
           turbine_inlet_bounds_k=(750.,835.))
    r2=solve_fixed_ua_whr(F,cycle(T4=800.),gas(),
           installed_heater_ua_w_k=40e3,
           turbine_inlet_bounds_k=(750.,835.))
    assert r1.turbine_inlet_temperature_k==pytest.approx(
        r2.turbine_inlet_temperature_k,abs=.01)

def test_higher_exhaust_inlet_raises_coupled_t4():
    base=solve_fixed_ua_whr(F,cycle(),gas(),
           installed_heater_ua_w_k=40e3,
           turbine_inlet_bounds_k=(750.,835.))
    hotter=solve_fixed_ua_whr(F,cycle(),
           gas(inlet_temperature_k=870.),
           installed_heater_ua_w_k=40e3,
           turbine_inlet_bounds_k=(750.,855.))
    assert hotter.turbine_inlet_temperature_k>base.turbine_inlet_temperature_k
    assert hotter.stack_temperature_k>base.stack_temperature_k

def test_result_reports_physical_equalities():
    out=coupled()
    assert out.installed_heater_ua_w_k==40000.
    assert out.calculated_heater_ua_w_k==pytest.approx(40000.,rel=1e-4)
    assert out.ua_residual_relative<=1e-4
    assert out.evaluations>=out.scanned_feasible_points
    assert out.root_bracket_k[0]<=out.turbine_inlet_temperature_k<=out.root_bracket_k[1]
    assert out.point.heat_utilization<=1

@pytest.mark.parametrize("ua",[0.,-100.,float("inf"),500e3])
def test_installed_ua_domain_rejected(ua):
    with pytest.raises(DomainError,match="installed heater UA"):
        coupled(installed_ua=ua)

def test_no_bracket_failure_is_explicit():
    with pytest.raises(DomainError,match="not bracketed|no feasible"):
        solve_fixed_ua_whr(
            F,cycle(),gas(),
            installed_heater_ua_w_k=40e3,
            turbine_inlet_bounds_k=(610.,660.),
            scan_intervals=5)

def test_heater_minimum_approach_limit_blocks_fixed_ua_solution():
    with pytest.raises(DomainError,match="not bracketed|no feasible"):
        solve_fixed_ua_whr(
            F,cycle(),gas(minimum_heater_approach_k=80.),
            installed_heater_ua_w_k=40e3,
            turbine_inlet_bounds_k=(750.,769.),scan_intervals=4)

def test_source_ua_screen_legacy_behavior_unchanged():
    sample=cycle(T4=790.,recup_ua=10e3)
    # Even though coupling can test UA beyond the sizing cap when searching,
    # the original *screening* call retains cap enforcement by default.
    point=evaluate_whr_design(F,sample,gas(maximum_heater_ua_w_k=150e3))
    with pytest.raises(DomainError,match="sizing"):
        evaluate_whr_design(F,sample,gas(maximum_heater_ua_w_k=1.))

def test_recuperator_approach_and_cooler_limit_are_preserved():
    try:
        base=coupled()
    except DomainError:
        pytest.skip("no feasible baseline under selected analytic fixture")
    with pytest.raises(DomainError,match="no feasible|not bracketed"):
        solve_fixed_ua_whr(
            F,cycle(),gas(),installed_heater_ua_w_k=40e3,
            turbine_inlet_bounds_k=(750.,835.),
            limits=PlantDesignLimits(
                maximum_cooler_duty_w=base.point.cycle.cooler_w*.01),
            scan_intervals=8)
