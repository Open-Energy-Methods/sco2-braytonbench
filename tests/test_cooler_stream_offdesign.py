"""Analytical sensible-flow, recuperator-independent cooler and flow-law tests."""
from dataclasses import replace
from math import exp
import pytest

from sco2_braytonbench import CycleInputs,IdealGasFixture,PressureLosses,DomainError
from sco2_braytonbench.streams import LinearCp
from sco2_braytonbench.cooler import CoolerSink,rate_cooler
from sco2_braytonbench.offdesign import FlowScaling
from sco2_braytonbench.whr import WasteGasSource,evaluate_whr_design

F=IdealGasFixture(cp=1000.,gas_constant=200.)

@pytest.mark.parametrize("slope",[-.3,0.,.3,1.])
@pytest.mark.parametrize("a,b",[(300.,750.),(700.,400.),(320.,350.)])
def test_linear_cp_enthalpy_entropy_and_inverse(slope,a,b):
    model=LinearCp(1100.,slope,300.)
    h=model.delta_h(a,b)
    assert model.temperature_for_delta_h(a,h)==pytest.approx(b,rel=1e-11)
    assert model.delta_h(b,a)==pytest.approx(-h,rel=1e-12)
    assert model.delta_s(a,b)==pytest.approx(-model.delta_s(b,a),rel=1e-12)
    assert h==pytest.approx((model.cp(a)+model.cp(b))*(b-a)/2)

@pytest.mark.parametrize("bad_slope",[-50.,float("inf")])
def test_linear_cp_rejects_bad_domain(bad_slope):
    with pytest.raises(DomainError):
        LinearCp(1100.,bad_slope,300.).cp(700.)

def base(t1=320.,t4=750.,mdot=10.,recup_ua=0.):
    return CycleInputs(p1_pa=8e6,p4_pa=24e6,t1_k=t1,t4_k=t4,
        mdot_kg_s=mdot,eta_compressor=.89,eta_turbine=.9,
        losses=PressureLosses(100e3,150e3,100e3,50e3),
        recuperator_effectiveness=None,recuperator_ua_w_k=recup_ua,
        segments=8)

def source(slope=0.):
    return WasteGasSource(
        inlet_temperature_k=950.,mass_flow_kg_s=50.,
        cp_j_kg_k=1100.,minimum_stack_temperature_k=350.,
        maximum_heater_ua_w_k=500e3,segments=8,
        cp_slope_j_kg_k2=slope)

def coolant(slope=0.):
    return CoolerSink(inlet_temperature_k=285.,mass_flow_kg_s=40.,
        cp_j_kg_k=4200.,installed_ua_w_k=15000.,
        maximum_outlet_temperature_k=360.,segments=12,
        cp_slope_j_kg_k2=slope)

@pytest.mark.parametrize("slope",[0.,.2])
def test_heater_variable_cp_exact_source_balance_and_exergy(slope):
    src=source(slope)
    point=evaluate_whr_design(F,base(),src)
    assert point.first_law_combined_residual_w==pytest.approx(0,abs=1e-6)
    assert point.heater.q_w==pytest.approx(
        src.mass_flow_kg_s*src.heat_capacity.delta_h(
            point.heater.gas_out_k,src.inlet_temperature_k))
    assert point.heat_utilization<=1
    assert point.source_exergy_consumed_w>=point.net_shaft_power_w

@pytest.mark.parametrize("slope",[0.,.1])
def test_cooler_energy_entropy_and_ntu_closed_form(slope):
    point=evaluate_whr_design(F,base(),source())
    hot,cold=point.cycle.states[5],point.cycle.states[0]
    sink=coolant(slope)
    rated=rate_cooler(F,hot,cold,10.,sink)
    assert rated.rejected_heat_w==pytest.approx(point.cycle.cooler_w)
    assert abs(rated.coolant_energy_residual_w)<1e-6
    assert rated.entropy_generation_w_k>0
    assert rated.minimum_approach_k>=sink.minimum_approach_k
    if slope==0:
        Cmin=min(10*F.cp,sink.mass_flow_kg_s*sink.cp_j_kg_k)
        Cmax=max(10*F.cp,sink.mass_flow_kg_s*sink.cp_j_kg_k)
        cr=Cmin/Cmax
        ntu=rated.required_ua_w_k/Cmin
        effectiveness=(1-exp(-ntu*(1-cr)))/(1-cr*exp(-ntu*(1-cr)))
        expected=effectiveness*Cmin*(hot.t-sink.inlet_temperature_k)
        assert rated.rejected_heat_w==pytest.approx(expected,rel=2e-6)

def test_coolant_rejects_insufficient_capacity():
    point=evaluate_whr_design(F,base(),source())
    with pytest.raises(DomainError,match="outlet exceeds"):
        rate_cooler(F,point.cycle.states[5],point.cycle.states[0],10.,
                    replace(coolant(),mass_flow_kg_s=.5))

@pytest.mark.parametrize("ratio",[.5,1.,1.5])
def test_quadratic_flow_loss_and_efficiency_penalty(ratio):
    law=FlowScaling(reference_mass_flow_kg_s=10.,
         pressure_loss_exponent=2.,compressor_efficiency_penalty=.02,
         turbine_efficiency_penalty=.03)
    out=law.at_flow(base(),10*ratio)
    assert out.losses.heater==pytest.approx(150e3*ratio**2)
    assert out.losses.cooler==pytest.approx(50e3*ratio**2)
    assert out.eta_compressor==pytest.approx(.89-.02*(ratio-1)**2)
    assert out.eta_turbine==pytest.approx(.9-.03*(ratio-1)**2)
    assert out.mdot_kg_s==pytest.approx(10*ratio)

def test_flow_outside_declared_domain_fails():
    with pytest.raises(DomainError):
        FlowScaling(reference_mass_flow_kg_s=10.).at_flow(base(),30.)
