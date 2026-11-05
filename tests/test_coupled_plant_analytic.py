"""Two fixed heat-exchanger UA equalities tested with an ideal-fluid fixture."""
from dataclasses import replace
import pytest
from sco2_braytonbench import CycleInputs,PressureLosses,IdealGasFixture,DomainError
from sco2_braytonbench.whr import WasteGasSource,evaluate_whr_design
from sco2_braytonbench.cooler import CoolerSink,rate_cooler
from sco2_braytonbench.coupled_plant import solve_coupled_plant

F=IdealGasFixture(cp=1000.,gas_constant=200.)

def fixture():
    base=CycleInputs(
        p1_pa=8e6,p4_pa=24e6,t1_k=320.,t4_k=750.,mdot_kg_s=10.,
        eta_compressor=.89,eta_turbine=.9,
        losses=PressureLosses(100e3,150e3,100e3,50e3),
        recuperator_effectiveness=None,
        recuperator_ua_w_k=0.,segments=8)
    src=WasteGasSource(inlet_temperature_k=950.,mass_flow_kg_s=50.,
        cp_j_kg_k=1100.,minimum_stack_temperature_k=350.,
        maximum_heater_ua_w_k=500e3,minimum_heater_approach_k=10.,
        segments=8)
    sink=CoolerSink(inlet_temperature_k=285.,mass_flow_kg_s=40.,
        cp_j_kg_k=4200.,installed_ua_w_k=15000.,
        maximum_outlet_temperature_k=360.,segments=8)
    point=evaluate_whr_design(F,base,src)
    rating=rate_cooler(F,point.cycle.states[5],point.cycle.states[0],10.,sink)
    sink=replace(sink,installed_ua_w_k=rating.required_ua_w_k)
    return base,src,sink,point.heater.required_ua_w_k

def inverse(source=None,cooler=None):
    base,src,sink,UA=fixture()
    return solve_coupled_plant(
        F,replace(base,t1_k=301.,t4_k=710.),source or src,cooler or sink,
        installed_heater_ua_w_k=UA,
        t1_bounds_k=(312.,330.),
        t4_bounds_k=(720.,785.),
        outer_scan_intervals=4,outer_max_iterations=12,
        cooler_ua_tolerance_relative=4e-4,
        inner_scan_intervals=4,inner_max_iterations=14,
        inner_ua_tolerance_relative=2e-4)

def test_inverse_recovers_both_known_HX_operating_states():
    result=inverse()
    assert result.compressor_inlet_temperature_k==pytest.approx(320.,abs=.3)
    assert result.turbine_inlet_temperature_k==pytest.approx(750.,abs=.3)
    assert result.cooler_ua_residual_relative<=4e-4
    assert result.heater.ua_residual_relative<=2e-4
    assert abs(result.cooler.coolant_energy_residual_w)<1e-6
    assert result.cooler.entropy_generation_w_k>=0
    assert abs(result.heater.point.first_law_combined_residual_w)<1e-6

def test_coolant_inlet_perturbation_changes_compressor_inlet():
    base,src,sink,UA=fixture()
    colder=inverse()
    warmer=inverse(cooler=replace(sink,inlet_temperature_k=290.))
    assert warmer.compressor_inlet_temperature_k>colder.compressor_inlet_temperature_k

def test_invalid_cooler_T1_search_domain_rejected():
    base,src,sink,ua=fixture()
    with pytest.raises(DomainError,match="cooler outlet T1"):
        solve_coupled_plant(
            F,base,src,sink,installed_heater_ua_w_k=ua,
            t1_bounds_k=(285.,315.),t4_bounds_k=(720.,785.))

def test_unattainable_cooler_UA_reports_error():
    base,src,sink,ua=fixture()
    with pytest.raises(DomainError,match="not bracketed|no feasible"):
        solve_coupled_plant(
            F,base,src,replace(sink,installed_ua_w_k=1.),
            installed_heater_ua_w_k=ua,
            t1_bounds_k=(312.,330.),t4_bounds_k=(720.,785.),
            outer_scan_intervals=4,inner_scan_intervals=4)
