"""Kim et al. (2019) orientation-dependent mixed convection: source audit model.

Original reference: T.H. Kim et al., IJHMT 131 (2019) 1117-1128,
DOI 10.1016/j.ijheatmasstransfer.2018.11.075. The 2019 original PDF
is not redistributable and is NOT included. Coefficients are read from
data/reference/kim2019_coefficients.json, extracted from original Table 4.

IMPORTANT ORIGINAL-SOURCE AMBIGUITY:
The PDF's printed empirical Eq. (24) places Re_b**n1 and Pr_b**n2
IN THE DENOMINATOR; its Table 4 fitted n1/n2 are NEGATIVE. This literal
reading gives enormous Nusselt numbers at representative conditions,
in tension with the original paper's Fig. 10 and Table 6. We preserve
literal_denominator (the printed Eq. 24), plus an *explicitly unverified*
signed_numerator_hypothesis for diagnostic evaluation. Neither may
be silently portrayed as recovered author implementation. The
semi-empirical Eq. 23 is unambiguous and uses literal_denominator.

Temperature-integral averages use quadrature at fixed P, with
cp_avg = (h(Twall)-h(Tbulk))/(Twall-Tbulk). beta_b from nomenclature
is (rho_bulk-rho_avg)/(rho_bulk*(Twall-Tbulk)), NOT the Lei film-beta.
Nu_nc = 1/[Eq. (29)/(30)], combined via Euclidean norm.
No fitted coefficients in this module; no HM middle-wall equation.
"""
from __future__ import annotations
from dataclasses import dataclass
from functools import lru_cache
from math import isfinite,log,exp,hypot,pi
from typing import Callable
import json
from pathlib import Path

GRAVITY=9.80665
GAUSS8_NODES=(-.9602898564975363,-.7966664774136267,
              -.5255324099163290,-.1834346424956498,
               .1834346424956498,.5255324099163290,
               .7966664774136267,.9602898564975363)
GAUSS8_WEIGHTS=(.1012285362903763,.2223810344533745,
                .3137066458778873,.3626837833783620,
                .3626837833783620,.3137066458778873,
                .2223810344533745,.1012285362903763)


class KimDomainError(ValueError):
    """A CO2 state, fitted-domain, or bracket is invalid."""


@dataclass(frozen=True)
class ThermoPoint:
    density:float
    viscosity:float
    conductivity:float
    cp:float
    enthalpy:float

    def validate(self)->None:
        if not all(isfinite(v) and v>0 for v in (
            self.density,self.viscosity,self.conductivity,self.cp)):
            raise KimDomainError("nonpositive or invalid CO2 transport property")
        if not isfinite(self.enthalpy):
            raise KimDomainError("invalid CO2 enthalpy")


class CoolPropCO2Transport:
    """One HEOS::CO2 AbstractState with cached real-fluid PT evaluations.

    Avoids multiplying the overhead of PropsSI calls by 5 properties and
    8 Gauss nodes per wall-root iteration. Not thread-safe.
    """
    def __init__(self):
        try:
            from CoolProp.CoolProp import AbstractState,PT_INPUTS
        except ImportError as exc:
            raise ImportError("install project[co2] with CoolProp 8.0.0") from exc
        self._state=AbstractState("HEOS","CO2")
        self._pt=PT_INPUTS

    @lru_cache(maxsize=100000)
    def __call__(self,p:float,t:float)->ThermoPoint:
        try:
            self._state.update(self._pt,p,t)
            v=ThermoPoint(
                float(self._state.rhomass()),float(self._state.viscosity()),
                float(self._state.conductivity()),float(self._state.cpmass()),
                float(self._state.hmass()))
            v.validate()
            return v
        except (RuntimeError,ValueError,OverflowError) as exc:
            raise KimDomainError("CoolProp HEOS::CO2 PT state outside model") from exc


def registry(path:Path|None=None)->dict:
    if path is None:
        path=Path(__file__).resolve().parents[2]/"data"/"reference"/"kim2019_coefficients.json"
    d=json.loads(Path(path).read_text(encoding="utf-8"))
    if d["schema_version"]!="kim2019-original-paper-table4-v1":
        raise KimDomainError("unreviewed Kim coefficient registry")
    return d


@dataclass(frozen=True)
class KimResult:
    nu:float
    nu_forced:float
    nu_natural:float
    htc_w_m2_k:float
    wall_temperature_k:float
    heat_flux_w_m2:float
    bulk_temperature_k:float
    beta_bulk_1_k:float
    q_b:float
    gr_q:float
    re_b:float
    pr_b:float
    density_average:float
    viscosity_average:float
    conductivity_average:float
    cp_average:float
    quadrature_subintervals:int
    source_form:str


def positive(**v)->None:
    if any(not isfinite(float(z)) or z<=0 for z in v.values()):
        raise KimDomainError("invalid nonpositive "+",".join(v))


def integral_means(
    properties:Callable[[float,float],ThermoPoint],
    p:float,tbulk:float,twall:float, *,
    steps_per_8k:int=1, max_subintervals:int=24,
)->tuple[float,float,float,float,int]:
    """Temperature integral means of (rho, mu, k, cp).

    Uses eight-point Gaussian integration on independently bounded
    temperature intervals. cp average uses an h difference instead of
    trying to resolve a near-pseudocritical cp spike numerically.
    """
    if not (isfinite(tbulk) and isfinite(twall) and twall>tbulk):
        raise KimDomainError("wall must be heated above CO2 bulk")
    positive(p=p)
    if steps_per_8k<1 or max_subintervals<1:
        raise KimDomainError("invalid quadrature controls")
    delta=twall-tbulk
    n=max(1,min(max_subintervals,int(delta*steps_per_8k/8)+1))
    s=[0.,0.,0.]
    for j in range(n):
        low=tbulk+j*delta/n
        half=delta/(2*n)
        mid=low+half
        for x,w in zip(GAUSS8_NODES,GAUSS8_WEIGHTS):
            pt=properties(p,mid+x*half)
            pt.validate()
            s[0]+=w*half*pt.density
            s[1]+=w*half*pt.viscosity
            s[2]+=w*half*pt.conductivity
    hb=properties(p,tbulk).enthalpy
    hw=properties(p,twall).enthalpy
    cpmean=(hw-hb)/delta
    avg=(s[0]/delta,s[1]/delta,s[2]/delta,cpmean,n)
    positive(rho_avg=avg[0],mu_avg=avg[1],k_avg=avg[2],cp_avg=avg[3])
    return avg


def _safe_power_product(constant:float,factors:list[tuple[float,float]])->float:
    positive(constant=constant)
    z=log(constant)
    for v,a in factors:
        positive(base=v)
        if not isfinite(a):
            raise KimDomainError("invalid source exponent")
        z+=a*log(v)
    if z>700 or z< -700:
        raise KimDomainError("Kim source power expression out of finite exponent bounds")
    y=exp(z)
    positive(value=y)
    return y


def nusselt_components(
    coeff:dict,re:float,pr:float,q_b:float,gr_q:float,
    rho_ratio:float,mu_ratio:float,k_ratio:float,cp_ratio:float,
    *,mode:str="literal_denominator",
)->tuple[float,float,float]:
    """Direct source Table 4 algebra and labelled alternative sign convention.

    n1,n2 in printed Eq.24 appear in denominator: Re_b**-n1,
    Pr_b**-n2. The alternative sign convention is a HYPOTHESIS.
    """
    positive(re=re,pr=pr,q_b=q_b,gr_q=gr_q,
             rho_ratio=rho_ratio,mu_ratio=mu_ratio,
             k_ratio=k_ratio,cp_ratio=cp_ratio)
    if mode not in ("literal_denominator","signed_numerator_hypothesis"):
        raise KimDomainError("unknown or misleading Eq24 exponent interpretation")
    n1,n2,n3,n4,n5,n6=coeff["n"]
    m1,m2,m3,m4,m5,m6=coeff["m"]
    if mode=="literal_denominator":
        ere, epr=.8-n1,.4-n2
    else:
        ere,epr=.8+n1,.4+n2
    nufc=_safe_power_product(coeff["c1"],[
        (re,ere),(pr,epr),(q_b,n3),(rho_ratio,n4),
        (mu_ratio,n5),(k_ratio,n6)])
    inverse_nc=_safe_power_product(coeff["c2"],[
        (gr_q,m1),(pr,m2),(rho_ratio,m3),
        (mu_ratio,m4),(cp_ratio,m5),(k_ratio,m6)])
    nu_nc=1./inverse_nc
    nu=hypot(nufc,nu_nc)
    positive(nu=nu)
    return nufc,nu_nc,nu


def evaluated_wall(
    orientation:str,model:str,convention:str,
    *,p_pa:float,tbulk_k:float,twall_k:float,q_w_m2:float,
    mass_flow_kg_s:float,diameter_m:float,
    properties:Callable[[float,float],ThermoPoint],
    coefficients:dict|None=None,
    steps_per_8k:int=1,
)->KimResult:
    """Evaluate a single wall state. Tw provenance is set by caller."""
    if orientation not in ("HB","HT"):
        raise KimDomainError("Kim equations only at HB(bottom) and HT(top)")
    if model not in ("empirical","semi_empirical"):
        raise KimDomainError("unknown Kim model variant")
    if convention=="signed_numerator_hypothesis" and model!="empirical":
        raise KimDomainError("semi-empirical Eq23 does not need a sign hypothesis")
    positive(p_pa=p_pa,tbulk_k=tbulk_k,twall_k=twall_k,
             q_w_m2=q_w_m2,mass_flow_kg_s=mass_flow_kg_s,
             diameter_m=diameter_m)
    if twall_k<=tbulk_k:
        raise KimDomainError("wall not hotter than bulk")
    if coefficients is None:
        coefficients=registry()["coefficients"][model][
            "bottom" if orientation=="HB" else "top"]
    b=properties(p_pa,tbulk_k)
    b.validate()
    rav,mav,kav,cpav,n=integral_means(
        properties,p_pa,tbulk_k,twall_k,steps_per_8k=steps_per_8k)
    beta_b=(b.density-rav)/(b.density*(twall_k-tbulk_k))
    if beta_b<=0:
        raise KimDomainError("source requires positive heated bulk expansion")
    kinvis=b.viscosity/b.density
    q_b=beta_b*q_w_m2*diameter_m/b.conductivity
    gr_q=GRAVITY*beta_b*q_w_m2*diameter_m**4/(
        kinvis**2*b.conductivity)
    re=4*mass_flow_kg_s/(pi*diameter_m*b.viscosity)
    pr=b.viscosity*b.cp/b.conductivity
    nufc,nunc,nu=nusselt_components(
        coefficients,re,pr,q_b,gr_q,rav/b.density,
        mav/b.viscosity,kav/b.conductivity,cpav/b.cp,
        mode=convention)
    return KimResult(nu,nufc,nunc,nu*b.conductivity/diameter_m,
                     twall_k,q_w_m2,tbulk_k,beta_b,q_b,gr_q,
                     re,pr,rav,mav,kav,cpav,n,convention)


def solve_wall(
    orientation:str,model:str,convention:str,
    *,p_pa:float,tbulk_k:float,q_w_m2:float,
    mass_flow_kg_s:float,diameter_m:float,
    properties:Callable[[float,float],ThermoPoint],
    tmax_k:float=650.,
    tolerance_relative:float=0.002,
    max_iter:int=36,
)->tuple[KimResult,int,float]:
    """Local q = h(Tw)*(Tw-Tb) solve with no experimental wall temperature.

    Uses prescribed q'', inlet-pressure aligned experimentally derived
    bulk h, flow and tube geometry. A finite scan detects observed
    sign-change intervals; cannot establish mathematical uniqueness.
    """
    positive(tbulk_k=tbulk_k,tmax_k=tmax_k,q_w_m2=q_w_m2)
    if tmax_k<=tbulk_k+.01 or max_iter<10:
        raise KimDomainError("insufficient wall-root search envelope")
    # Begin near Tb because the literal printed Eq24 can predict
    # absurdly large Nu, making the balance root very close to Tb.
    gaps=(1e-5,5e-5,1e-4,5e-4,.001,.005,.01,.05,
          .1,.5,1.,2.,4.,8.,16.,32.,64.,128.,256.,512.)
    temps=[tbulk_k+g for g in gaps if tbulk_k+g<tmax_k]
    temps.append(tmax_k)
    def flux(t):
        result=evaluated_wall(
            orientation,model,convention,p_pa=p_pa,tbulk_k=tbulk_k,
            twall_k=t,q_w_m2=q_w_m2,
            mass_flow_kg_s=mass_flow_kg_s,diameter_m=diameter_m,
            properties=properties)
        return result.htc_w_m2_k*(t-tbulk_k)-q_w_m2,result
    samples=[]
    for t in temps:
        try:
            v,r=flux(t)
            samples.append((t,v))
        except KimDomainError:
            # Keep sampling but do not bridge across an unphysical
            # subdomain: later bracket endpoints must be consecutive
            # in the original scan, not in the filtered valid list.
            samples.append((t,None))
    brackets=[]
    for (l,vl),(h,vh) in zip(samples,samples[1:]):
        if vl is not None and vh is not None and vl<=0<=vh:
            brackets.append((l,h))
    if len(brackets)!=1:
        raise KimDomainError(f"wall balance brackets={len(brackets)}; not a unique verified root")
    lo,hi=brackets[0]
    for n in range(1,max_iter+1):
        mid=(lo+hi)/2
        residue,out=flux(mid)
        if residue>0:hi=mid
        else:lo=mid
        relative=abs(residue)/q_w_m2
        if relative<=tolerance_relative and hi-lo <=max(1e-8,1e-7*(mid-tbulk_k)):
            return out,n,relative
    raise KimDomainError("Kim wall inverse failed energy or root-width convergence")
