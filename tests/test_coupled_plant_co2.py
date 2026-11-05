"""Real-CO2, source-heater+cooler installed-UA inverse smoke test.

Narrow operating point to control property-call costs. The nominal
UAs are synthetically sized from a feasible steady state; this is a
self-consistency check, not independent equipment validation.
"""
from dataclasses import replace
import pytest
pytest.importorskip("CoolProp")
from sco2_braytonbench import CycleInputs,CoolPropCO2,PressureLosses
from sco2_braytonbench.whr import WasteGasSource,evaluate_whr_design
from sco2_braytonbench.cooler import CoolerSink,rate_cooler
from sco2_braytonbench.coupled_plant import solve_coupled_plant

def test_real_co2_coupled_heater_and_cooler_inverse():
    fluid=CoolPropCO2()
    nominal=CycleInputs(
        p1_pa=8.5e6,p4_pa=24e6,t1_k=310.,t4_k=650.,
        mdot_kg_s=20.,eta_compressor=.89,eta_turbine=.9,
        losses=PressureLosses(100e3,150e3,100e3,50e3),
        recuperator_effectiveness=None,recuperator_ua_w_k=200e3,
        segments=5)
    source=WasteGasSource(inlet_temperature_k=800.,
        mass_flow_kg_s=100.,cp_j_kg_k=1100.,
        cp_slope_j_kg_k2=.20,cp_reference_temperature_k=300.,
        minimum_stack_temperature_k=350.,
        maximum_heater_ua_w_k=1.2e6,segments=5)
    sink=CoolerSink(
        inlet_temperature_k=285.,mass_flow_kg_s=75.,
        cp_j_kg_k=4180.,installed_ua_w_k=10000.,
        maximum_outlet_temperature_k=340.,segments=5)
    initial=evaluate_whr_design(fluid,nominal,source)
    cooler=rate_cooler(fluid,initial.cycle.states[5],
        initial.cycle.states[0],20.,sink)
    sink=replace(sink,installed_ua_w_k=cooler.required_ua_w_k)
    r=solve_coupled_plant(
        fluid,replace(nominal,t1_k=320.,t4_k=600.),
        source,sink,
        installed_heater_ua_w_k=initial.heater.required_ua_w_k,
        t1_bounds_k=(306.,314.),t4_bounds_k=(630.,670.),
        outer_scan_intervals=4,outer_max_iterations=12,
        cooler_ua_tolerance_relative=7e-4,t1_tolerance_k=.12,
        inner_scan_intervals=4,inner_max_iterations=18,
        inner_ua_tolerance_relative=2e-4,
        inner_t4_tolerance_k=.06)
    assert r.compressor_inlet_temperature_k==pytest.approx(310.,abs=.35)
    assert r.turbine_inlet_temperature_k==pytest.approx(650.,abs=.35)
    assert r.cooler_ua_residual_relative<7e-4
    assert r.heater.ua_residual_relative<2e-4
    assert abs(r.cooler.coolant_energy_residual_w)<1e-5
    assert r.cooler.entropy_generation_w_k>=0
    assert abs(r.heater.point.first_law_combined_residual_w)<1e-5
    assert abs(r.heater.point.cycle.first_law_residual_w)<1e-5
