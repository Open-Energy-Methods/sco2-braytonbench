"""Classical pipe-flow verification; no industrial geometry is implied."""
from math import pi, log10
import pytest
from sco2_braytonbench.properties import DomainError
from sco2_braytonbench.hydraulics import CircularPipe,pipe_loss

def test_laminar_hagen_poiseuille_exact():
    d=.01;L=2.;rho=1000.;mu=.001;mdot=.00001
    actual=pipe_loss(CircularPipe(d,L),mdot,rho,mu)
    expected=128*mu*L*(mdot/rho)/(pi*d**4)
    assert actual.regime=="laminar"
    assert actual.pressure_drop_pa==pytest.approx(expected,rel=1e-12)
    assert actual.darcy_friction_factor==pytest.approx(
        64/actual.reynolds_number)

def test_turbulent_haaland_vs_independently_solved_colebrook():
    pipe=CircularPipe(.025,12.,absolute_roughness_m=1e-5,minor_loss_k=1.5)
    result=pipe_loss(pipe,1.2,820.,5e-5)
    assert result.regime=="turbulent_Haaland"
    re=result.reynolds_number
    rr=pipe.absolute_roughness_m/pipe.inner_diameter_m
    f=.02
    for _ in range(80):
        f=1/(-2*log10(rr/3.7+2.51/(re*f**.5)))**2
    assert result.darcy_friction_factor==pytest.approx(f,rel=.015)
    assert result.pressure_drop_pa==pytest.approx(
        result.friction_drop_pa+result.minor_drop_pa)

def test_roughness_and_flow_increase_losses():
    smooth=CircularPipe(.025,12.,0.)
    rough=CircularPipe(.025,12.,.0001)
    a=pipe_loss(smooth,.5,900.,7e-5)
    b=pipe_loss(rough,.5,900.,7e-5)
    c=pipe_loss(rough,1.0,900.,7e-5)
    assert 0<a.pressure_drop_pa<b.pressure_drop_pa<c.pressure_drop_pa

def test_transition_is_explicitly_unmodelled():
    # for Re=3000: m = Re*pi*D*mu/4
    pipe=CircularPipe(.02,1.)
    mdot=3000*pi*pipe.inner_diameter_m*.001/4
    with pytest.raises(DomainError,match="transition"):
        pipe_loss(pipe,mdot,1000.,.001)

@pytest.mark.parametrize("bad",[CircularPipe(.01,0.),CircularPipe(.02,1.,.0)])
def test_nonnegative_pipe_loss(bad):
    assert pipe_loss(bad,0.5,900.,.001).pressure_drop_pa>=0

def test_bad_geometry_rejected():
    with pytest.raises(DomainError):
        CircularPipe(.01,2.,absolute_roughness_m=.02)
