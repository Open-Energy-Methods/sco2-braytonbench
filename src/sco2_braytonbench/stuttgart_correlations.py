"""Source-audited wall-property supercritical heat-transfer comparisons.

Bishop et al. expression as transcribed in Theologou et al. (2022),
Energy 254, 124171, equation (15), and Jackson-Hall (1979) temperature
branch formulation as printed in Ye et al. (2022), Int J Refrigeration
140, 57-69, Table 3.

IMPORTANT: Neither expression contains a circumferential buoyancy
correction. Using experimentally measured wall temperature makes the
result DIAGNOSTIC / CONDITIONED, NOT an a-priori HTC prediction.
The alternative flux-driven fixed-point solve does NOT use measured
wall temperature, but does use each experiment's reported heat flux.

Properties: thermodynamic *differences* evaluated by supplied
PropsSI-like backend; no assumption about REFPROP absolute enthalpy.
"""
from __future__ import annotations
import math
from typing import Callable

G_STD=9.80665


class CorrelationDomainError(ValueError):
    pass


def _positive(*values:float)->None:
    if not all(math.isfinite(x) and x>0 for x in values):
        raise CorrelationDomainError("expected finite positive thermophysical variables")


def bishop_nu(
    re_b:float, mu_b:float, k_b:float, cp_mean:float,
    rho_w_over_b:float, x_over_d:float,
)->float:
    """Bishop et al. 1964 / Theologou (2022) Eq. 15.

    Nu = 0.0069 Re_b**0.9 [cpbar*mu_b/k_b]**0.66
         (rho_wall/rho_bulk)**0.43 (1 + 2.4/(x/D)).

    Original Bishop fit was to UPWARD supercritical-water flow,
    not this horizontal sCO2 experiment: all applications here
    are physically extrapolated and explicitly labelled.
    """
    _positive(re_b,mu_b,k_b,cp_mean,rho_w_over_b,x_over_d)
    prbar=cp_mean*mu_b/k_b
    _positive(prbar)
    return (0.0069*re_b**0.9*prbar**0.66*
            rho_w_over_b**0.43*(1+2.4/x_over_d))


def jackson_hall_exponent(tb_k:float,tw_k:float,tpc_k:float)->float:
    """Piecewise Jackson-Hall (1979) exponent for heated wall Tw>Tb.

    In the middle branch the exponent depends on Tb/Tpc, not just
    the wall-to-pseudocritical temperature ratio.
    """
    _positive(tb_k,tw_k,tpc_k)
    if tw_k<=tb_k:
        raise CorrelationDomainError("Jackson requires heated wall Tw>Tb")
    if tw_k<=tpc_k or tb_k>=1.2*tpc_k:
        return 0.4
    z=tw_k/tpc_k-1.
    if tb_k<=tpc_k:
        return 0.4+0.2*z
    return 0.4+0.2*z*(1-5*(tb_k/tpc_k-1.))


def jackson_hall_nu(
    re_b:float,pr_b:float,rho_w_over_b:float,
    cp_mean_over_bulk:float,tb_k:float,tw_k:float,tpc_k:float,
)->float:
    """Jackson-Hall wall/bulk correction form; no angular buoyancy model."""
    _positive(re_b,pr_b,rho_w_over_b,cp_mean_over_bulk)
    n=jackson_hall_exponent(tb_k,tw_k,tpc_k)
    return (0.0183*re_b**0.82*pr_b**0.5*
            rho_w_over_b**0.3*cp_mean_over_bulk**n)


def richardson_density_wall(
    rho_b:float,rho_w:float,diameter_m:float,
    mass_flux_kg_m2_s:float,
)->float:
    """Theologou et al. (2022), Sec. 3.5, Ri=Gr/Re**2.

    For heated fluid with rho_bulk>rho_wall, Ri is positive.
    This is a buoyancy *indicator*, not a Nusselt correction.
    """
    _positive(rho_b,rho_w,diameter_m,mass_flux_kg_m2_s)
    return ((rho_b-rho_w)*rho_b*G_STD*diameter_m/
            mass_flux_kg_m2_s**2)


def wall_property_nusselt(
    model:str, re_b:float,pr_b:float,rho_b:float,mu_b:float,
    k_b:float,cp_b:float,tb_k:float,tw_k:float,
    pressure_pa:float,x_over_d:float,
    props:Callable, tpc_k:float,
)->float:
    """Calculate Nu conditioned on a proposed Tw, not necessarily measured."""
    _positive(rho_b,cp_b,re_b,pr_b,mu_b,k_b,pressure_pa,x_over_d)
    if not math.isfinite(tw_k) or tw_k<=tb_k:
        raise CorrelationDomainError("heated wall Tw must exceed Tb")
    try:
        rho_w=props("Dmass","P",pressure_pa,"T",tw_k,"HEOS::CO2")
        h_w=props("Hmass","P",pressure_pa,"T",tw_k,"HEOS::CO2")
        h_b=props("Hmass","P",pressure_pa,"T",tb_k,"HEOS::CO2")
    except (ValueError,RuntimeError,OverflowError) as exc:
        raise CorrelationDomainError("CO2 wall property call failed") from exc
    cpbar=(h_w-h_b)/(tw_k-tb_k)
    _positive(rho_w,cpbar)
    if model=="bishop_wall_conditioned" or model=="bishop_flux_inverted":
        return bishop_nu(re_b,mu_b,k_b,cpbar,rho_w/rho_b,x_over_d)
    if model=="jackson_wall_conditioned" or model=="jackson_flux_inverted":
        return jackson_hall_nu(re_b,pr_b,rho_w/rho_b,cpbar/cp_b,
                               tb_k,tw_k,tpc_k)
    raise CorrelationDomainError("unsupported wall-property correlation")


def flux_driven_wall_solution(
    model:str,heat_flux_w_m2:float,diameter_m:float,
    re_b:float,pr_b:float,rho_b:float,mu_b:float,k_b:float,cp_b:float,
    tb_k:float,pressure_pa:float,x_over_d:float,tpc_k:float,props:Callable,
    *,wall_upper_k:float=650.,tolerance_k:float=0.04,
    max_iterations:int=18,
)->tuple[float,float,int]:
    """Solve q'' = h_model(Tw)*(Tw-Tb) with NO measured wall T.

    This is an implicit local wall energy condition, holding the
    experiment's reduced bulk state and reported heat flux fixed.
    Bracketing failure is reported, never replaced with a fitted
    correlation factor. Checks local monotonicity by scan.
    """
    _positive(heat_flux_w_m2,diameter_m,tb_k,tolerance_k)
    if not(math.isfinite(wall_upper_k) and wall_upper_k>tb_k+2.):
        raise CorrelationDomainError("invalid wall-temperature bracket")
    if max_iterations<1:
        raise CorrelationDomainError("invalid inverse iteration budget")

    def energy(tw):
        nu=wall_property_nusselt(model,re_b,pr_b,rho_b,mu_b,k_b,
                                 cp_b,tb_k,tw,pressure_pa,x_over_d,
                                 props,tpc_k)
        htc=nu*k_b/diameter_m
        return htc*(tw-tb_k)-heat_flux_w_m2,htc

    lower=tb_k+0.001
    # Increasing fine wall temperature may encounter a plateau but
    # should not leap across a disconnected feasible domain.
    pts=[lower+(wall_upper_k-lower)*i/8 for i in range(9)]
    vals=[energy(t) for t in pts]
    br=[]
    for (x,v),(y,w) in zip(zip(pts,vals),zip(pts[1:],vals[1:])):
        if v[0]<0<=w[0]:
            br.append((x,y))
    if len(br)!=1:
        raise CorrelationDomainError(
            "wall energy balance not uniquely bracketed by scan")
    lo,hi=br[0]
    for count in range(1,max_iterations+1):
        mid=(lo+hi)*0.5
        residual,htc=energy(mid)
        if residual>0:hi=mid
        else:lo=mid
        if hi-lo<=tolerance_k:
            return mid,htc,count
    raise CorrelationDomainError("wall temperature inversion nonconvergent")
