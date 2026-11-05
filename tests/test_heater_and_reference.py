import pytest
from sco2_braytonbench import DomainError, IdealGasFixture
from sco2_braytonbench.exchangers import waste_gas_heater,segmented_recuperator
from sco2_braytonbench.references import fr2016_pressure_map

F=IdealGasFixture()

@pytest.mark.parametrize('p8',[7.7e6,8.336e6,9.0e6])
def test_reference_pressure_graph(p8):
    a=fr2016_pressure_map(30e6,p8)
    assert len(a.p)==12
    assert a[1]-a[2]==pytest.approx(80e3)
    assert a[3]-a[4]==pytest.approx(10e3)
    assert a[4]-a[5]==pytest.approx(50e3)
    assert a[5]-a[6]==pytest.approx(5e3)
    assert a[6]-a[7]==pytest.approx(100e3)
    assert a[7]-a[8]==pytest.approx(40e3)
    assert a[9]-a[10]==pytest.approx(35e3)
    assert a[10]-a[11]==pytest.approx(30e3)
    assert a[11]-a[12]==pytest.approx(200e3)
    assert a[12]-a[1]==pytest.approx(150e3)

@pytest.mark.parametrize('p8',[1.,-1.,0])
def test_reference_bad_p8(p8):
    with pytest.raises(DomainError):fr2016_pressure_map(30e6,p8)

def test_published_total_loss_ledger():
    assert sum((100,150,30,50))==330
    assert sum((80,10,5,40,35,200))==370

def test_heater_finite_gas_balance():
    a=F.tp(24e6,440)
    b=F.tp(23.8e6,580)
    r=waste_gas_heater(F,a,b,5,700,30,1100,min_pinch_k=10)
    assert r.q_w==pytest.approx(700_000)
    assert r.gas_out_k==pytest.approx(700-700_000/(30*1100))
    assert r.min_approach_k>=10
    assert r.required_ua_w_k>0

@pytest.mark.parametrize('gas_t',[500,575,580])
def test_heater_rejects_pinch_crossing(gas_t):
    with pytest.raises(DomainError):
        waste_gas_heater(F,F.tp(24e6,440),F.tp(23.8e6,580),5,gas_t,30,1100)

def test_heater_no_pressure_gain():
    with pytest.raises(DomainError):
        waste_gas_heater(F,F.tp(24e6,440),F.tp(25e6,580),5,700,30,1100)

@pytest.mark.parametrize('n',[5,10,30,60])
def test_internal_counterflow_recuperation_conserves(n):
    r=segmented_recuperator(F,F.tp(20e6,420),F.tp(8e6,700),19.97e6,7.95e6,5,5,effectiveness=.7,n=n)
    assert r.hot_out.h< F.tp(8e6,700).h
    assert r.cold_out.h>F.tp(20e6,420).h
    assert r.min_approach_k>0
    assert r.q_w/r.qmax_w==pytest.approx(.7)

@pytest.mark.parametrize('eps',[-1,.0,1.,1.1])
def test_effectiveness_bounds(eps):
    if 0<=eps<=1:
        r=segmented_recuperator(F,F.tp(20e6,420),F.tp(8e6,700),19.97e6,7.95e6,5,5,effectiveness=eps)
        assert r.q_w>=0
    else:
        with pytest.raises(DomainError):
            segmented_recuperator(F,F.tp(20e6,420),F.tp(8e6,700),19.97e6,7.95e6,5,5,effectiveness=eps)

def test_requires_one_hx_design_mode():
    with pytest.raises(DomainError):
        segmented_recuperator(F,F.tp(20e6,420),F.tp(8e6,700),19.97e6,7.95e6,5,5)
