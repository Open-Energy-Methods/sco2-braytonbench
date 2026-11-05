"""Lei top/bottom equations independently checked, without sCO2 runtime.

The synthetic ideal-fluid fixture tests implementation arithmetic
and root recovery ONLY. It is not scientific validation of Lei for CO2.
"""
from importlib.util import module_from_spec,spec_from_file_location
from pathlib import Path
from math import log,pi
import math
import pytest

from sco2_braytonbench.lei_mixed_convection import (
    lei_nu_bottom,lei_nu_top,grashof_q,
    lei_wall_state,solve_lei_wall,CorrelationDomainError
)

ROOT=Path(__file__).resolve().parents[1]

def ideal_props(key,a,va,b,vb,fluid):
    assert fluid=="HEOS::CO2"
    x={a:va,b:vb}
    T=x.get("T")
    if T is None:raise ValueError("fixture supports direct T state only")
    p=x["P"]
    return {
       "Dmass":p/(220.*T),
       "CONDUCTIVITY":.074,
       "VISCOSITY":3e-5,
       "Hmass":2100.*T,
       "Cpmass":2100.,
    }[key]

def test_published_lei_bottom_formula_independent():
    re=8.5e4;pr=3.2;rr=.65;kk=1.3
    expected=.27227*re**.64*pr**.731*rr**1.189*kk**.449
    assert lei_nu_bottom(re,pr,rr,kk)==pytest.approx(expected,rel=1e-13)

def test_published_lei_top_formula_independent():
    re=8.5e4;pr=3.2;rr=.65;gr=2e8
    expected=.01482*re**.8175*pr**.5868*rr**.589*gr**.05879
    assert lei_nu_top(re,pr,rr,gr)==pytest.approx(expected,rel=1e-13)

def test_heat_flux_grashof_film_beta_and_units():
    rb=600.;rw=300.;rf=450.;tw=340.;tb=310.
    q=70e3;d=.008;mu=4e-5; k=.085
    beta=(rb-rw)/(rf*(tw-tb))
    nu=mu/rb
    reference=9.80665*beta*q*d**4/(nu**2*k)
    assert grashof_q(rb,rw,rf,tw,tb,q,d,mu,k)==pytest.approx(reference)
    # If q is doubled, Grq doubles exactly.
    assert grashof_q(rb,rw,rf,tw,tb,q*2,d,mu,k)==pytest.approx(reference*2)

@pytest.mark.parametrize("orientation",["HB","HT"])
def test_conditioned_state_against_printed_equation(orientation):
    p=8e6;tb=310.;tw=345.;d=.008;G=650.;mu=3e-5;k=.074
    rb=ideal_props("Dmass","P",p,"T",tb,"HEOS::CO2")
    rw=ideal_props("Dmass","P",p,"T",tw,"HEOS::CO2")
    rf=ideal_props("Dmass","P",p,"T",(tb+tw)/2,"HEOS::CO2")
    re=G*d/mu
    cpbar=2100.;prbar=cpbar*mu/k
    q=85000.
    result=lei_wall_state(
        orientation,re_bulk=re,mu_bulk_pa_s=mu,k_bulk_w_m_k=k,
        rho_bulk_kg_m3=rb,heat_flux_w_m2=q,diameter_m=d,
        bulk_temperature_k=tb,wall_temperature_k=tw,
        pressure_pa=p,props=ideal_props)
    if orientation=="HB":
        ref=.27227*re**.64*prbar**.731*(rw/rb)**1.189
        assert result.grashof_heat_flux is None
    else:
        gr=grashof_q(rb,rw,rf,tw,tb,q,d,mu,k)
        ref=.01482*re**.8175*prbar**.5868*(rw/rb)**.589*gr**.05879
        assert result.grashof_heat_flux==pytest.approx(gr)
    assert result.nu==pytest.approx(ref,rel=1e-10)
    assert result.htc_w_m2_k==pytest.approx(ref*k/d,rel=1e-10)

@pytest.mark.parametrize("orient",["HB","HT"])
def test_flux_inverse_recovers_known_ideal_fluid_wall(orient):
    p=8e6;tb=310.;tw0=370.;d=.008;G=650.;mu=3e-5;k=.074
    rb=ideal_props("Dmass","P",p,"T",tb,"HEOS::CO2")
    # Top Lei Nu depends weakly on heat flux as q^0.05879;
    # obtain q from an independent analytic fixed-wall solution.
    alpha=0.0 if orient=="HB" else 0.05879
    reference=lei_wall_state(
        orient,re_bulk=G*d/mu,mu_bulk_pa_s=mu,
        k_bulk_w_m_k=k,rho_bulk_kg_m3=rb,
        heat_flux_w_m2=1.,diameter_m=d,
        bulk_temperature_k=tb,wall_temperature_k=tw0,
        pressure_pa=p,props=ideal_props)
    q=(reference.htc_w_m2_k*(tw0-tb))**(1/(1-alpha))
    known=lei_wall_state(
        orient,re_bulk=G*d/mu,mu_bulk_pa_s=mu,
        k_bulk_w_m_k=k,rho_bulk_kg_m3=rb,
        heat_flux_w_m2=q,diameter_m=d,
        bulk_temperature_k=tb,wall_temperature_k=tw0,
        pressure_pa=p,props=ideal_props)
    assert known.htc_w_m2_k*(tw0-tb)==pytest.approx(q,rel=1e-12)
    solved,its,resid=solve_lei_wall(
        orient,re_bulk=G*d/mu,mu_bulk_pa_s=mu,k_bulk_w_m_k=k,
        rho_bulk_kg_m3=rb,heat_flux_w_m2=q,diameter_m=d,
        bulk_temperature_k=tb,pressure_pa=p,props=ideal_props)
    assert solved.wall_temperature_k==pytest.approx(tw0,abs=.025)
    assert resid<.002
    assert solved.htc_w_m2_k==pytest.approx(known.htc_w_m2_k,rel=.001)
    assert 1<=its<=23

def test_lei_does_not_invent_middle_correlation():
    with pytest.raises(CorrelationDomainError,match="only HB bottom and HT top"):
        lei_wall_state("HM",re_bulk=10000.,mu_bulk_pa_s=3e-5,
                       k_bulk_w_m_k=.07,rho_bulk_kg_m3=500.,
                       heat_flux_w_m2=70000.,diameter_m=.008,
                       bulk_temperature_k=310.,wall_temperature_k=340.,
                       pressure_pa=8e6,props=ideal_props)

def test_top_grashof_rejects_negative_density_drop():
    with pytest.raises(CorrelationDomainError):
        grashof_q(200.,300.,250.,340.,310.,60000.,.008,3e-5,.07)

def test_real_benchmark_src_integrity_without_any_property_backend():
    import csv
    path=ROOT/"data"/"validation"/"stuttgart"/"experiment_index.csv"
    with path.open(encoding="utf-8",newline="") as f:
        meta=list(csv.DictReader(f))
    assert len(meta)==54
    from collections import Counter
    assert Counter(r["orientation_code"] for r in meta)=={
        "HB":18,"HM":18,"HT":18}
    original=next(r for r in meta if r["experiment_id"]==
                  "4MM_HM_77.5_10_20_90_A")
    assert float(original["heat_flux_kw_m2"])>800.
