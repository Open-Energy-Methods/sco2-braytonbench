"""Independent textbook ideal-gas NTU benchmarks; never call these real-CO2 data."""
from math import exp
import pytest
from sco2_braytonbench import IdealGasFixture
from sco2_braytonbench.exchangers import segmented_recuperator

F=IdealGasFixture(cp=1000.,gas_constant=200.)

@pytest.mark.parametrize("n",[8,15,30,60])
@pytest.mark.parametrize("UA",[4000.,20000.,40000.,100000.])
def test_counterflow_equal_capacity_rate_matches_exact_NTU(UA,n):
    cold=F.tp(20e6,350.)
    hot=F.tp(8e6,700.)
    mc=mh=10.
    r=segmented_recuperator(F,cold,hot,20e6,8e6,mc,mh,ua_w_k=UA,n=n)
    C=mc*F.cp
    NTU=UA/C
    eps=NTU/(1+NTU)
    assert r.q_w==pytest.approx(eps*C*(700-350),rel=1e-7)
    assert r.required_ua_w_k==pytest.approx(UA,rel=1e-7)
    assert r.min_approach_k>0
    assert (r.cold_out.h-cold.h)*mc==pytest.approx(
        (hot.h-r.hot_out.h)*mh)

@pytest.mark.parametrize("mc,mh",[ (5.,15.),(8.,12.),(12.,8.) ])
def test_counterflow_unequal_capacity_rate_matches_closed_form(mc,mh):
    UA=20000.
    cold=F.tp(20e6,350.)
    hot=F.tp(8e6,700.)
    r=segmented_recuperator(F,cold,hot,20e6,8e6,
                            mc,mh,ua_w_k=UA,n=60)
    Cmin=min(mc,mh)*F.cp
    Cmax=max(mc,mh)*F.cp
    Cr=Cmin/Cmax
    NTU=UA/Cmin
    eps=(1-exp(-NTU*(1-Cr)))/(1-Cr*exp(-NTU*(1-Cr)))
    assert r.q_w==pytest.approx(eps*Cmin*(700-350),rel=1e-5)

@pytest.mark.parametrize("ratio",[1.5,2.,3.,4.])
@pytest.mark.parametrize("eta",[.75,.85,1.])
def test_ideal_compressor_temperature_matches_closed_form(ratio,eta):
    from sco2_braytonbench.core import compressor_outlet
    T1=310.
    p1=8e6
    a=F.tp(p1,T1)
    h_iso=F.ps(p1*ratio,a.s).h
    actual=F.ph(p1*ratio,compressor_outlet(a.h,h_iso,eta))
    expect=T1*(1+(ratio**(F.gas_constant/F.cp)-1)/eta)
    assert actual.t==pytest.approx(expect,rel=1e-11)
    assert actual.s>=a.s-1e-9

@pytest.mark.parametrize("ratio",[1.5,2.,3.,4.])
@pytest.mark.parametrize("eta",[.75,.9,1.])
def test_ideal_turbine_temperature_matches_closed_form(ratio,eta):
    from sco2_braytonbench.core import turbine_outlet
    T4=700.
    p4=24e6
    a=F.tp(p4,T4)
    h_iso=F.ps(p4/ratio,a.s).h
    actual=F.ph(p4/ratio,turbine_outlet(a.h,h_iso,eta))
    expect=T4*(1-eta*(1-ratio**(-F.gas_constant/F.cp)))
    assert actual.t==pytest.approx(expect,rel=1e-11)
    assert actual.s>=a.s-1e-9
