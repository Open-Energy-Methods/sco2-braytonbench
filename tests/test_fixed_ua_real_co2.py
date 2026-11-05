"""Real-fluid coupled fixed-installed-UA heater checks.

Independent seed conditions are GENERATED from a valid finite gas-side
heater energy/HX calculation, not from a publication benchmark. The
inverse root must recover that T4 and then respond to a source change.
"""
from dataclasses import replace
import pytest

pytest.importorskip("CoolProp")
from sco2_braytonbench import (
    CoolPropCO2, CycleInputs, PressureLosses, DomainError
)
from sco2_braytonbench.fixed_ua import solve_fixed_ua_whr
from sco2_braytonbench.whr import WasteGasSource,evaluate_whr_design

F=CoolPropCO2()

def model(t4:float,m:float,n:int=10)->CycleInputs:
    return CycleInputs(
        p1_pa=8.5e6,p4_pa=24e6,t1_k=310.,t4_k=t4,
        mdot_kg_s=m,eta_compressor=.89,eta_turbine=.90,
        losses=PressureLosses(100e3,150e3,100e3,50e3),
        recuperator_effectiveness=None,
        recuperator_ua_w_k=200e3,segments=n)

def exhaust(t:float=800.,n:int=10)->WasteGasSource:
    return WasteGasSource(
        inlet_temperature_k=t,mass_flow_kg_s=100.,
        cp_j_kg_k=1100.,minimum_stack_temperature_k=350.,
        maximum_heater_ua_w_k=1.2e6,
        minimum_heater_approach_k=10.,
        dead_state_temperature_k=300.,segments=n)

@pytest.mark.parametrize("t4,m",[(620.,20.),(650.,40.)])
def test_real_co2_installed_ua_inverse_and_conservation(t4,m):
    guess=model(t4,m)
    source=exhaust()
    forward=evaluate_whr_design(F,guess,source)
    target_ua=forward.heater.required_ua_w_k
    result=solve_fixed_ua_whr(
        F,replace(guess,t4_k=590.),source,
        installed_heater_ua_w_k=target_ua,
        turbine_inlet_bounds_k=(t4-32.,t4+32.),
        scan_intervals=8,max_iterations=24)
    assert result.turbine_inlet_temperature_k==pytest.approx(t4,abs=.07)
    assert abs(result.ua_residual_relative)<=1e-4
    assert abs(result.point.cycle.first_law_residual_w)<1e-5
    assert abs(result.point.first_law_combined_residual_w)<1e-5
    assert result.point.heater.min_approach_k>=10.
    assert result.point.heat_utilization<=1.
    assert result.point.net_shaft_power_w<=result.point.source_exergy_consumed_w

def test_real_co2_inlet_temperature_change_changes_turbine_temperature():
    guess=model(650.,20.)
    source=exhaust()
    ua=evaluate_whr_design(F,guess,source).heater.required_ua_w_k
    low=solve_fixed_ua_whr(
        F,guess,source,installed_heater_ua_w_k=ua,
        turbine_inlet_bounds_k=(620.,687.),
        scan_intervals=8)
    high=solve_fixed_ua_whr(
        F,guess,exhaust(t=810.),installed_heater_ua_w_k=ua,
        turbine_inlet_bounds_k=(620.,690.),
        scan_intervals=8)
    assert high.turbine_inlet_temperature_k>low.turbine_inlet_temperature_k
    assert high.stack_temperature_k>low.stack_temperature_k
