"""Internal first/second-law thermodynamic identities for HEOS CO2.

These tests check numerical behaviour of a backend, not experimental truth.
"""
import pytest
pytest.importorskip("CoolProp")
from CoolProp.CoolProp import PropsSI
from sco2_braytonbench.core import compressor_outlet,turbine_outlet
from sco2_braytonbench.properties import CoolPropCO2

F="HEOS::CO2"

@pytest.mark.parametrize("p,t",[
    (8e6,308.15),(8e6,313.15),(9e6,313.15),
    (8.336347e6,304.1282),(15e6,450),(30e6,550),
])
def test_cp_matches_enthalpy_temperature_derivative(p,t):
    # T-spacing resolves near-pseudocritical structure without crossing phase
    dt=0.005 if t<320 else 0.02
    h_plus=PropsSI("Hmass","P",p,"T",t+dt,F)
    h_minus=PropsSI("Hmass","P",p,"T",t-dt,F)
    cp_fd=(h_plus-h_minus)/(2*dt)
    cp=PropsSI("Cpmass","P",p,"T",t,F)
    assert cp>0
    assert cp_fd==pytest.approx(cp,rel=.005)

@pytest.mark.parametrize("p,t",[
    (8e6,308.15),(8e6,313.15),(10e6,320),
    (15e6,450),(30e6,550)
])
def test_cp_over_t_matches_entropy_temperature_derivative(p,t):
    dt=.01
    s_plus=PropsSI("Smass","P",p,"T",t+dt,F)
    s_minus=PropsSI("Smass","P",p,"T",t-dt,F)
    dsdt=(s_plus-s_minus)/(2*dt)
    assert dsdt==pytest.approx(PropsSI("Cpmass","P",p,"T",t,F)/t,rel=.005)

@pytest.mark.parametrize("pi,pout,t,eta",[
    (8.4e6,30e6,305,0.85),
    (8.4e6,30e6,320,0.85),
    (10e6,25e6,330,0.89)
])
def test_irreversible_compressor_entropy_generation(pi,pout,t,eta):
    f=CoolPropCO2()
    a=f.tp(pi,t)
    b=f.ph(pout,compressor_outlet(a.h,f.ps(pout,a.s).h,eta))
    assert b.h>a.h and b.s>a.s

@pytest.mark.parametrize("pi,pout,t,eta",[
    (29.92e6,8.5e6,550,0.90),
    (25e6,8.5e6,750,0.9)
])
def test_irreversible_turbine_entropy_generation(pi,pout,t,eta):
    f=CoolPropCO2()
    a=f.tp(pi,t)
    b=f.ph(pout,turbine_outlet(a.h,f.ps(pout,a.s).h,eta))
    assert b.h<a.h and b.s>a.s
