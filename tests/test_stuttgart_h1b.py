"""H1b independent equation, thermodynamic inversion, buoyancy and split gates.

The synthetic ideal-gas property fixture is a software test only.
No experimental-accuracy assertion is made by these tests.
"""
import csv
from importlib.util import module_from_spec,spec_from_file_location
import math
from pathlib import Path
import pytest
from sco2_braytonbench.stuttgart_correlations import (
    bishop_nu,jackson_hall_exponent,jackson_hall_nu,
    richardson_density_wall,wall_property_nusselt,
    flux_driven_wall_solution,CorrelationDomainError,
)

ROOT=Path(__file__).resolve().parents[1]

def h1b():
    spec=spec_from_file_location("stuttgart_h1b",ROOT/"scripts"/"stuttgart_h1b.py")
    m=module_from_spec(spec);spec.loader.exec_module(m)
    return m

def ideal_props(key,in1,val1,in2,val2,fluid):
    assert fluid=="HEOS::CO2"
    v={in1:val1,in2:val2}
    t=v.get("T")
    p=v["P"]
    if t is None:
        t=v["Hmass"]/1500.
    return {
        "Hmass":1500.*t,
        "Dmass":p/(200.*t),
        "Cpmass":1500.,
        "VISCOSITY":4e-5,
        "CONDUCTIVITY":.065,
    }[key]

def test_bishop_direct_independent_printed_equation():
    re=100000.;cpbar=2800.;mu=4e-5;k=.065;rr=.6;x_over_d=150.
    prbar=cpbar*mu/k
    expected=.0069*re**.9*prbar**.66*rr**.43*(1+2.4/150)
    assert bishop_nu(re,mu,k,cpbar,rr,x_over_d)==pytest.approx(expected,rel=1e-12)

@pytest.mark.parametrize("tb,tw,tpc,expected",[
    (295.,304.,307.,.4),
    (300.,315.,307.,.4+.2*(315/307-1)),
    (310.,330.,307.,.4+.2*(330/307-1)*(1-5*(310/307-1))),
    (380.,405.,307.,.4),
])
def test_jackson_piecewise_exponent_published_branches(tb,tw,tpc,expected):
    assert jackson_hall_exponent(tb,tw,tpc)==pytest.approx(expected,rel=1e-12)

def test_jackson_direct_independent_expression():
    re=75000.;pr=4.;rr=.74;cr=1.7
    n=jackson_hall_exponent(306.,350.,308.)
    actual=jackson_hall_nu(re,pr,rr,cr,306.,350.,308.)
    assert actual==pytest.approx(.0183*re**.82*pr**.5*rr**.3*cr**n)

def test_richardson_exact_density_force_ratio():
    # Source paper Sec. 3.5: Ri = [((rho_b-rho_w)/rho_b)
    # g*D^3/(mu_b/rho_b)^2] / [G*D/mu_b]^2.
    rb=500.;rw=250.;d=.008;G=800.;mu=4e-5
    gr=(rb-rw)*9.80665*d**3/(rb*(mu/rb)**2)
    re=G*d/mu
    assert richardson_density_wall(rb,rw,d,G)==pytest.approx(gr/re**2)

@pytest.mark.parametrize("name",[
    "bishop_flux_inverted","jackson_flux_inverted"
])
def test_flux_driven_wall_inversion_recovers_known_synthetic_temperature(name):
    p=8e6;tb=307.;tw_known=355.;d=.008;x_over_d=140.;m=.03
    mu=4e-5;k=.065;cp=1500.;rho=ideal_props("Dmass","P",p,"T",tb,"HEOS::CO2")
    re=4*m/(math.pi*d*mu);pr=cp*mu/k
    nu=wall_property_nusselt(name,re,pr,rho,mu,k,cp,tb,tw_known,
                             p,x_over_d,ideal_props,309.)
    q=nu*k/d*(tw_known-tb)
    tw_solved,h_solved,n=flux_driven_wall_solution(
        name,q,d,re,pr,rho,mu,k,cp,tb,p,x_over_d,309.,ideal_props)
    assert tw_solved==pytest.approx(tw_known,abs=.06)
    assert h_solved==pytest.approx(nu*k/d,rel=.005)
    assert 1<=n<=18

def test_measured_wall_conditioning_cannot_be_described_as_apriori():
    module=h1b()
    assert module.__doc__.find("measured Tw")!=-1 or "measured wall" in module.__doc__.lower()

def test_original_quarantine_and_heldout_family_partition_preserved():
    src=ROOT/"data"/"validation"/"stuttgart"
    rows=list(csv.DictReader((src/"experiment_index.csv").open()))
    assert len(rows)==54
    assert sum(r["experiment_id"]=="4MM_HM_77.5_10_20_90_A" for r in rows)==1
    assert max(float(r["heat_flux_kw_m2"]) for r in rows)>830.
    report=ROOT/"docs"/"G35_STUTTGART_RESULTS.md"
    assert report.exists()

def test_metrics_are_run_and_family_aware():
    m=h1b()
    v=[
      dict(experiment_id="x",nominal_family="g1",relative_residual_pct=100.,reported_htc_sigma_pct=20.),
      dict(experiment_id="x",nominal_family="g1",relative_residual_pct=100.,reported_htc_sigma_pct=20.),
      dict(experiment_id="y",nominal_family="g2",relative_residual_pct=0.,reported_htc_sigma_pct=20.),
    ]
    actual=m.metrics(v)
    assert actual["mape_pct"]==pytest.approx(200/3)
    assert actual["mean_run_mape_pct"]==pytest.approx(50.)
    assert actual["mean_nominal_family_mape_pct"]==pytest.approx(50.)

def test_implicit_wall_rejects_invalid_heat_input():
    with pytest.raises(CorrelationDomainError):
        flux_driven_wall_solution(
            "bishop_flux_inverted",-1.,.008,50000.,4.,
            500.,4e-5,.065,1500.,310.,8e6,100.,309.,ideal_props)
