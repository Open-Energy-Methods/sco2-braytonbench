"""Cross-implementation CO2 checks against published NIST REFPROP 9.1 table.

Source: NIST REFPROP 9.1 User's Guide (2013), printed p.18,
https://www.nist.gov/system/files/documents/srd/REFPROP9.PDF
Tabulated T = 20 deg C; density kg/m3, h kJ/kg, s kJ/(kg K).
These are rounded screen values from NIST and NOT raw measurements.
CoolProp and REFPROP both implement Span-Wagner: successful agreement is a
reference implementation check, NOT independent experimental verification.
"""
import pytest

pytest.importorskip("CoolProp", reason="separate real-CO2 CI job required")
from CoolProp.CoolProp import PropsSI
from sco2_braytonbench.properties import CoolPropCO2

FLUID = "HEOS::CO2"
# NIST user guide REFPROP 9.1 p.18, T = 293.15 K.
REF = {
    5: {"rho": 140.65, "h": 432.38, "s": 1.8051},
    6: {"rho": 782.65, "h": 254.28, "s": 1.1811},
    7: {"rho": 808.60, "h": 249.95, "s": 1.1621},
    8: {"rho": 827.71, "h": 246.91, "s": 1.1475},
    9: {"rho": 843.17, "h": 244.58, "s": 1.1355},
    10: {"rho": 856.31, "h": 242.51, "s": 1.1251},
}

@pytest.mark.parametrize("pressure_mpa", sorted(REF))
def test_nist_refprop_density(pressure_mpa):
    p = pressure_mpa*1e6
    rho = PropsSI("Dmass", "T", 293.15, "P", p, FLUID)
    assert rho == pytest.approx(REF[pressure_mpa]["rho"], rel=.006)

@pytest.mark.parametrize("pressure_mpa", [5, 6, 7, 9, 10])
def test_nist_reference_safe_enthalpy_entropy_differences(pressure_mpa):
    """Avoid comparing absolute h and s across arbitrary reference conventions."""
    base, target = REF[8], REF[pressure_mpa]
    p1, p2 = 8e6, pressure_mpa*1e6
    delta_h = (
        PropsSI("Hmass", "T", 293.15, "P", p2, FLUID) -
        PropsSI("Hmass", "T", 293.15, "P", p1, FLUID)
    )
    delta_s = (
        PropsSI("Smass", "T", 293.15, "P", p2, FLUID) -
        PropsSI("Smass", "T", 293.15, "P", p1, FLUID)
    )
    assert delta_h == pytest.approx((target["h"]-base["h"])*1000, abs=200)
    assert delta_s == pytest.approx((target["s"]-base["s"])*1000, abs=2)

@pytest.mark.parametrize("pressure_mpa,temperature_k,density", [
    (8,308.15,419.), (8,313.15,278.),
    (9,308.15,662.), (9,313.15,486.),
    (10,318.15,498.),
])
def test_near_pseudocritical_reference_density(pressure_mpa,temperature_k,density):
    """Hiroshima Univ. high-pressure-fluid lab tabulates NIST-derived values
    to three significant figures; permissive rounding/implementation tolerance.
    https://highpres.hiroshima-u.ac.jp/supercritical-co2-properties/
    """
    rho = PropsSI("Dmass", "P",pressure_mpa*1e6,"T",temperature_k,FLUID)
    assert rho == pytest.approx(density,rel=.02)

@pytest.mark.parametrize("p,t", [
    (5e6,293.15),(8e6,293.15),(8e6,308.15),(9e6,313.15),
    (8e6,320),(15e6,450),(25e6,550),(30e6,750),
])
def test_tp_ph_ps_roundtrips(p,t):
    props = CoolPropCO2()
    state = props.tp(p,t)
    assert props.ph(p,state.h).t == pytest.approx(t,abs=3e-4)
    assert props.ps(p,state.s).t == pytest.approx(t,abs=3e-4)

def test_critical_point_reference():
    # NIST/CoolProp Span-Wagner critical point, in SI units.
    assert PropsSI("Tcrit",FLUID) == pytest.approx(304.1282,abs=.01)
    assert PropsSI("Pcrit",FLUID) == pytest.approx(7.3773e6,rel=.001)

def test_near_critical_density_sensitivity_exists():
    r1=PropsSI("Dmass","P",8e6,"T",308.15,FLUID)
    r2=PropsSI("Dmass","P",8e6,"T",313.15,FLUID)
    assert r1 > r2 > 0
    assert (r1-r2)/r1 > .2

def test_entropy_generation_of_real_turbomachinery():
    from sco2_braytonbench.core import compressor_outlet,turbine_outlet
    props=CoolPropCO2()
    a=props.tp(8.4e6,310.)
    b=props.ph(30e6,compressor_outlet(a.h,props.ps(30e6,a.s).h,.85))
    assert b.s>=a.s
    h_in=props.tp(29.9e6,550.)
    h_out=props.ph(8.6e6,turbine_outlet(h_in.h,props.ps(8.6e6,h_in.s).h,.90))
    assert h_out.s >= h_in.s
