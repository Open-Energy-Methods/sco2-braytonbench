"""Kim (2019) equation verification; tests do NOT assert empirical validity."""
import math
from pathlib import Path
import pytest
from sco2_braytonbench.kim2019 import (
    KimDomainError,ThermoPoint,registry,integral_means,
    nusselt_components,evaluated_wall,solve_wall
)

def synthetic(p,t):
    # Fixed gas heat capacity and ideal-gas density. Deliberately NOT
    # claimed to be near-critical real CO2, only an analytic check.
    return ThermoPoint(p/(210.*t),3.2e-5,.075,1800.,125000.+1800.*t)

def test_enthalpy_and_analytical_ideal_density_temperature_average():
    p=8e6;tb=300.;tw=360.
    r,m,k,cp,n=integral_means(synthetic,p,tb,tw,max_subintervals=12)
    rho_exact=p/210.*math.log(tw/tb)/(tw-tb)
    assert r==pytest.approx(rho_exact,rel=1e-10)
    assert m==pytest.approx(3.2e-5,rel=1e-13)
    assert k==pytest.approx(.075,rel=1e-13)
    assert cp==pytest.approx(1800.,rel=1e-13)
    assert 1<=n<=12

def test_literal_printed_equation_24_and_alternative_are_distinct():
    c=registry()["coefficients"]["empirical"]["top"]
    re=1e5;pr=2.;Q=3.;Gr=1e8
    R=.7;M=.8;K=1.2;C=1.5
    expected_literal=(1.14*re**(.8-c["n"][0])*pr**(.4-c["n"][1])*
        Q**c["n"][2]*R**c["n"][3]*M**c["n"][4]*K**c["n"][5])
    a,b,cnu=nusselt_components(
        c,re,pr,Q,Gr,R,M,K,C,mode="literal_denominator")
    assert a==pytest.approx(expected_literal,rel=1e-13)
    assert cnu==pytest.approx(math.hypot(a,b))
    fixed,other,nu=nusselt_components(
        c,re,pr,Q,Gr,R,M,K,C,
        mode="signed_numerator_hypothesis")
    expected_hyp=(1.14*re**(.8+c["n"][0])*pr**(.4+c["n"][1])*
        Q**c["n"][2]*R**c["n"][3]*M**c["n"][4]*K**c["n"][5])
    assert fixed==pytest.approx(expected_hyp,rel=1e-13)
    assert a/fixed>100000  # source Eq24/Table4 sign inconsistency
    assert b==pytest.approx(other)

def test_natural_component_is_inverse_of_published_eq_30():
    c=registry()["coefficients"]["empirical"]["bottom"]
    re=1e4;pr=4;Q=1.2;Gr=1e6
    rr=.7;mr=.9;kr=1.1;cr=1.3
    fc,nc,allnu=nusselt_components(c,re,pr,Q,Gr,rr,mr,kr,cr)
    m=c["m"]
    reciprocal=(c["c2"]*Gr**m[0]*pr**m[1]*rr**m[2]*
                mr**m[3]*cr**m[4]*kr**m[5])
    assert nc==pytest.approx(1/reciprocal,rel=1e-12)
    assert allnu==pytest.approx(math.sqrt(fc**2+nc**2))

def test_transcribed_semi_empirical_source_coefficients_unchanged():
    c=registry()["coefficients"]["semi_empirical"]
    assert c["top"]["n"]==pytest.approx([13/24,1/3,1/3,1/3,-2/3,1])
    assert c["bottom"]["m"]==pytest.approx([-.25,-.15,-.5,.35,-.15,-.6])
    assert c["top"]["c2"]==989

@pytest.mark.parametrize("model,interpretation",[
 ("semi_empirical","literal_denominator"),
 ("empirical","signed_numerator_hypothesis"),
])
@pytest.mark.parametrize("orientation",["HB","HT"])
def test_analytic_fixture_wall_state_and_flux_numerical_equation(model,interpretation,orientation):
    p=8e6;tb=310;tw=335.;mass=.012;D=.00775;q=9000.
    st=evaluated_wall(orientation,model,interpretation,p_pa=p,
        tbulk_k=tb,twall_k=tw,q_w_m2=q,
        mass_flow_kg_s=mass,diameter_m=D,properties=synthetic)
    assert st.htc_w_m2_k>0
    assert st.nu==pytest.approx(math.hypot(st.nu_forced,st.nu_natural))
    assert st.beta_bulk_1_k>0
    assert st.gr_q>0
    assert st.quadrature_subintervals>=1

def test_no_middle_wall_equation_or_unapproved_semi_empirical_sign_changes():
    with pytest.raises(KimDomainError,match="only at"):
        evaluated_wall("HM","empirical","literal_denominator",
        p_pa=8e6,tbulk_k=310,twall_k=340,q_w_m2=9000,
        mass_flow_kg_s=.01,diameter_m=.008,properties=synthetic)
    with pytest.raises(KimDomainError,match="semi-empirical"):
        evaluated_wall("HB","semi_empirical","signed_numerator_hypothesis",
        p_pa=8e6,tbulk_k=310,twall_k=340,q_w_m2=9000,
        mass_flow_kg_s=.01,diameter_m=.008,properties=synthetic)

def test_implicit_wall_returns_energy_balance_for_published_semi():
    # The solver must only use q, mass flow, P, Tbulk and geometry.
    q=12000.
    out,n,resid=solve_wall("HB","semi_empirical","literal_denominator",
       p_pa=8e6,tbulk_k=310.,q_w_m2=q,mass_flow_kg_s=.012,
       diameter_m=.00775,properties=synthetic,tmax_k=650.)
    assert out.wall_temperature_k>310.
    assert resid<.002
    assert out.htc_w_m2_k*(out.wall_temperature_k-310.)==pytest.approx(q,rel=.002)
    assert 1<=n<=36

def test_model_parameter_and_unphysical_domain_are_rejected():
    c=registry()["coefficients"]["empirical"]["top"]
    with pytest.raises(KimDomainError):
        nusselt_components(c,0,2,1,1e8,.8,1,1,1)
    with pytest.raises(KimDomainError):
        nusselt_components(c,1e5,2,1,1e8,.8,1,1,1,mode="silent_fix")
    with pytest.raises(KimDomainError):
        integral_means(synthetic,8e6,350,310)
