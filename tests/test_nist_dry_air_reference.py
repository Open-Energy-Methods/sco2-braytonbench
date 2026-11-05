"""Source-referenced NIST Shomate dry-air chemistry approximation tests.

79/21 molar N2/O2 without Ar/H2O/CO2; NOT combustion exhaust.
Numeric cp values below are computed independently from the printed
NIST coefficient tables for this exact declared mixture.
"""
import pytest
from sco2_braytonbench.properties import DomainError,IdealGasFixture
from sco2_braytonbench.reference_streams import DryAirNISTShomate
from sco2_braytonbench.whr import WasteGasSource,evaluate_whr_design
from sco2_braytonbench.cycle import CycleInputs
from sco2_braytonbench.core import PressureLosses

AIR=DryAirNISTShomate()

@pytest.mark.parametrize("T,cp",[
    (300.,1011.4589314078652),
    (400.,1020.0665139093362),
    (500.,1036.23803991316),
    (600.,1058.0361297963946),
    (700.,1082.3201074716806),
    (800.,1106.4752208199736),
    (950.,1139.1356960038195),
])
def test_nist_published_shomate_coefficients_reproduce_cp(T,cp):
    assert AIR.cp(T)==pytest.approx(cp,rel=2e-12)

@pytest.mark.parametrize("lo,hi",[
    (300.,800.),(450.,550.),(650.,850.),
    (700.,701.),(500.,501.),(400.,500.),(600.,700.),
])
def test_nist_shomate_enthalpy_entropy_inverse(lo,hi):
    dh=AIR.delta_h(lo,hi)
    assert dh>0
    assert AIR.temperature_for_delta_h(lo,dh)==pytest.approx(hi,abs=1e-7)
    assert AIR.delta_h(hi,lo)==pytest.approx(-dh)
    assert AIR.delta_s(lo,hi)==pytest.approx(-AIR.delta_s(hi,lo))
    assert AIR.delta_s(lo,hi)>0

@pytest.mark.parametrize("transition",[500.,700.])
def test_continuous_property_across_polynomial_break(transition):
    assert abs(AIR.delta_h(transition-.00001,transition+.00001))<.05
    assert abs(AIR.delta_s(transition-.00001,transition+.00001))<.0002

@pytest.mark.parametrize("T",[280.,299.,1001.])
def test_air_rejects_out_of_range(T):
    with pytest.raises(DomainError):
        AIR.cp(T)

def test_nist_air_source_coupled_energy_and_exergy():
    air=WasteGasSource(
        inlet_temperature_k=950.,mass_flow_kg_s=50.,
        cp_j_kg_k=1100.,minimum_stack_temperature_k=350.,
        maximum_heater_ua_w_k=1e6,segments=8,
        gas_property_model=AIR,
        dead_state_temperature_k=300.)
    c=CycleInputs(
        p1_pa=8e6,p4_pa=24e6,t1_k=310.,t4_k=690.,
        mdot_kg_s=10.,eta_compressor=.89,eta_turbine=.9,
        losses=PressureLosses(100e3,150e3,100e3,50e3),
        recuperator_effectiveness=None,recuperator_ua_w_k=50e3,segments=8)
    point=evaluate_whr_design(IdealGasFixture(),c,air)
    assert point.first_law_combined_residual_w==pytest.approx(0,abs=1e-6)
    assert point.heater.q_w==pytest.approx(
        air.mass_flow_kg_s*AIR.delta_h(
            point.heater.gas_out_k,air.inlet_temperature_k))
    assert point.source_exergy_consumed_w>point.net_shaft_power_w
