import math
import pytest
from sco2_braytonbench import CycleInputs, PressureLosses, IdealGasFixture, solve_cycle, DomainError
from sco2_braytonbench.core import cycle_pressures, compressor_outlet, turbine_outlet

F=IdealGasFixture()
P=PressureLosses(3e4,1.5e5,5e4,1e5)

def conditions(**update):
    d=dict(p1_pa=8e6,p4_pa=25e6,t1_k=310.,t4_k=750.,
           mdot_kg_s=5.,eta_compressor=.89,eta_turbine=.9,
           losses=P,recuperator_effectiveness=.85)
    d.update(update)
    return CycleInputs(**d)

@pytest.mark.parametrize('loss', [PressureLosses(),P,PressureLosses(1e4,1e4,1e4,1e4)])
def test_pressure_closure(loss):
    p=cycle_pressures(8e6,25e6,loss)
    assert p.p2-p.p3==pytest.approx(loss.cold_recup)
    assert p.p3-p.p4==pytest.approx(loss.heater)
    assert p.p5-p.p6==pytest.approx(loss.hot_recup)
    assert p.p6-p.p1==pytest.approx(loss.cooler)

@pytest.mark.parametrize('eta', [.1,.6,.89,1.])
def test_compressor_efficiency(eta):
    assert compressor_outlet(100,200,eta)==pytest.approx(100+100/eta)

@pytest.mark.parametrize('eta', [.1,.6,.9,1.])
def test_turbine_efficiency(eta):
    assert turbine_outlet(200,100,eta)==pytest.approx(200-100*eta)

@pytest.mark.parametrize('inp',[(0,25e6),(-1,25e6),(8e6,1e6)])
def test_invalid_pressure(inp):
    with pytest.raises(DomainError):cycle_pressures(*inp,P)

@pytest.mark.parametrize('eta',[-.1,0,1.1])
def test_invalid_efficiency(eta):
    with pytest.raises(DomainError):compressor_outlet(100,200,eta)

@pytest.mark.parametrize('eta',[-.1,0,1.1])
def test_invalid_turbine_efficiency(eta):
    with pytest.raises(DomainError):turbine_outlet(200,100,eta)

@pytest.mark.parametrize('t', [300.,310.,325.,450.,750.])
def test_ideal_property_inversions(t):
    a=F.tp(8e6,t)
    assert F.ph(8e6,a.h).t==pytest.approx(t)
    assert F.ps(8e6,a.s).t==pytest.approx(t)

@pytest.mark.parametrize('effectiveness',[0,.25,.6,.9,.99])
def test_cycle_conservation(effectiveness):
    a=solve_cycle(F,conditions(recuperator_effectiveness=effectiveness))
    assert a.first_law_residual_w==pytest.approx(0,abs=1e-6)
    assert a.heater_w>=a.net_w
    assert a.recuperator.q_w>=0
    assert 0<a.thermal_efficiency<1

@pytest.mark.parametrize('ua',[0.,1000.,5000.,1e5])
def test_cycle_ua_mode(ua):
    a=solve_cycle(F,conditions(recuperator_effectiveness=None,recuperator_ua_w_k=ua))
    assert a.recuperator.required_ua_w_k==pytest.approx(ua,rel=.002,abs=1e-5)
    assert abs(a.first_law_residual_w)<1e-6

def test_increasing_recuperation_reduces_external_heater_duty():
    low=solve_cycle(F,conditions(recuperator_effectiveness=.2))
    high=solve_cycle(F,conditions(recuperator_effectiveness=.8))
    assert high.heater_w<low.heater_w
    assert high.net_w==pytest.approx(low.net_w)

def test_recuperator_heat_exchange_conserves_energy():
    a=solve_cycle(F,conditions())
    s1,s2,s3,s4,s5,s6=a.states
    assert 5*(s3.h-s2.h)==pytest.approx(5*(s5.h-s6.h))

def test_not_a_real_co2_fixture():
    assert F.cp==1000. and F.gas_constant==200.
