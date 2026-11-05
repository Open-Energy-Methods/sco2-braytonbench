"""Optional EOS smoke checks. They do not demonstrate source-paper reproduction."""
import pytest
pytest.importorskip('CoolProp', reason='CoolProp optional; EOS gate not run')
from sco2_braytonbench.properties import CoolPropCO2

def test_co2_tp_ph_roundtrip():
    p=CoolPropCO2()
    x=p.tp(8e6,320.)
    assert p.ph(8e6,x.h).t==pytest.approx(320,abs=1e-5)

def test_co2_tp_ps_roundtrip():
    p=CoolPropCO2()
    x=p.tp(24e6,500.)
    assert p.ps(24e6,x.s).t==pytest.approx(500,abs=1e-5)
