"""Lei et al. orientation-specific TOP/BOTTOM Nusselt correlations.

Source: Theologou et al. (2022), Energy 254, 124171,
Eq. (17), quoting Lei et al. (2017), Int. J. Heat Mass
Transfer 114, 923–933, DOI 10.1016/j.ijheatmasstransfer.2017.06.052.

IMPORTANT: original Lei correlations were fitted to SUPERCRITICAL
WATER in 26/43 mm horizontal pipes. The Stuttgart CO2 4/8 mm test
is **cross-fluid, cross-geometry EXTRAPOLATION ONLY**. These formulas
are not calibrated for CO2 or industrial printed-circuit HX channels.

Only HB (bottom) and HT (top) exist in the published formula. No
middle-wall (HM) correlation or arbitrary angular interpolation.
Either diagnostic measured-wall conditioning or local flux-driven
wall-temperature inversion must be distinctly labelled.
"""
from __future__ import annotations

from dataclasses import dataclass
import math
from typing import Callable
from .stuttgart_correlations import CorrelationDomainError

GRAVITY=9.80665

def _physical(*vs:float)->None:
    if not all(math.isfinite(x) and x>0 for x in vs):
        raise CorrelationDomainError("nonphysical Lei thermodynamic or geometric state")

def lei_nu_bottom(
    re_bulk:float,pr_integrated:float,rho_wall_over_bulk:float,
    k_bulk_over_wall:float,
)->float:
    """Original orientation-specific HB equation, Eq. (17) Theologou."""
    _physical(re_bulk,pr_integrated,rho_wall_over_bulk,k_bulk_over_wall)
    return (0.27227*re_bulk**0.64*pr_integrated**0.731*
            rho_wall_over_bulk**1.189*k_bulk_over_wall**0.449)

def lei_nu_top(
    re_bulk:float,pr_integrated:float,rho_wall_over_bulk:float,
    grashof_heat_flux:float,
)->float:
    """Original orientation-specific HT equation, Eq. (17) Theologou."""
    _physical(re_bulk,pr_integrated,rho_wall_over_bulk,grashof_heat_flux)
    return (0.01482*re_bulk**0.8175*pr_integrated**0.5868*
            rho_wall_over_bulk**0.589*grashof_heat_flux**0.05879)

def grashof_q(
    density_bulk_kg_m3:float,density_wall_kg_m3:float,
    density_film_kg_m3:float,wall_k:float,bulk_k:float,
    heat_flux_w_m2:float,diameter_m:float,
    bulk_dynamic_viscosity_pa_s:float,bulk_conductivity_w_m_k:float,
)->float:
    """Theologou 2022 Sec 3.5 heat-flux Grashof with film beta-bar.

    beta_bar = [rho_b - rho_w]/[rho_f*(T_w-T_b)] (1/K)
    Gr_q = g*beta_bar*q''*D**4/(nu_b**2*k_b);
    nu_b = mu_b/rho_b. For heated sCO2 the density drop must be
    positive. This is NOT the ordinary density-Richardson number.
    """
    _physical(density_bulk_kg_m3,density_wall_kg_m3,
              density_film_kg_m3,wall_k,bulk_k,heat_flux_w_m2,
              diameter_m,bulk_dynamic_viscosity_pa_s,
              bulk_conductivity_w_m_k)
    if wall_k<=bulk_k or density_wall_kg_m3>=density_bulk_kg_m3:
        raise CorrelationDomainError(
            "heated top-wall Gr_q requires positive density drop")
    beta_bar=(density_bulk_kg_m3-density_wall_kg_m3)/(
        density_film_kg_m3*(wall_k-bulk_k))
    nu_b=bulk_dynamic_viscosity_pa_s/density_bulk_kg_m3
    return (GRAVITY*beta_bar*heat_flux_w_m2*diameter_m**4/
            (nu_b**2*bulk_conductivity_w_m_k))

@dataclass(frozen=True)
class LeiWallState:
    nu:float
    htc_w_m2_k:float
    grashof_heat_flux:float|None
    integrated_cp_j_kg_k:float
    wall_temperature_k:float
    wall_conductivity_w_m_k:float
    wall_density_kg_m3:float

def lei_wall_state(
    orientation:str, *, re_bulk:float, mu_bulk_pa_s:float,
    k_bulk_w_m_k:float, rho_bulk_kg_m3:float,
    heat_flux_w_m2:float, diameter_m:float,
    bulk_temperature_k:float, wall_temperature_k:float,
    pressure_pa:float, props:Callable,
)->LeiWallState:
    """Evaluate the exact Lei equation at an assumed Tw; Tw provenance matters.

    HB needs rho_w, lambda_w and cpbar; HT needs also film density
    at Tfilm=(Tw+Tb)/2 and the heat-flux Grashof. HB has no Grq
    multiplier even though buoyancy influenced its original fit.
    """
    if orientation not in ("HB","HT"):
        raise CorrelationDomainError("Lei has only HB bottom and HT top equations")
    _physical(re_bulk,mu_bulk_pa_s,k_bulk_w_m_k,
              rho_bulk_kg_m3,heat_flux_w_m2,diameter_m,
              bulk_temperature_k,wall_temperature_k,pressure_pa)
    if wall_temperature_k<=bulk_temperature_k:
        raise CorrelationDomainError("Lei requires heated wall temperature > bulk")
    try:
        rw=props("Dmass","P",pressure_pa,"T",wall_temperature_k,"HEOS::CO2")
        kw=props("CONDUCTIVITY","P",pressure_pa,"T",wall_temperature_k,"HEOS::CO2")
        hb=props("Hmass","P",pressure_pa,"T",bulk_temperature_k,"HEOS::CO2")
        hw=props("Hmass","P",pressure_pa,"T",wall_temperature_k,"HEOS::CO2")
        rf=(props("Dmass","P",pressure_pa,"T",
                  .5*(bulk_temperature_k+wall_temperature_k),"HEOS::CO2")
            if orientation=="HT" else None)
    except (RuntimeError,ValueError,OverflowError) as exc:
        raise CorrelationDomainError("CO2 property call failed for Lei wall") from exc
    cpbar=(hw-hb)/(wall_temperature_k-bulk_temperature_k)
    _physical(rw,kw,cpbar)
    prbar=cpbar*mu_bulk_pa_s/k_bulk_w_m_k
    ratio=rw/rho_bulk_kg_m3
    gr=None
    if orientation=="HB":
        nu=lei_nu_bottom(re_bulk,prbar,ratio,k_bulk_w_m_k/kw)
    else:
        gr=grashof_q(
            rho_bulk_kg_m3,rw,rf,wall_temperature_k,
            bulk_temperature_k,heat_flux_w_m2,diameter_m,
            mu_bulk_pa_s,k_bulk_w_m_k)
        nu=lei_nu_top(re_bulk,prbar,ratio,gr)
    return LeiWallState(nu,nu*k_bulk_w_m_k/diameter_m,
                        gr,cpbar,wall_temperature_k,kw,rw)

def solve_lei_wall(
    orientation:str, *,
    re_bulk:float,mu_bulk_pa_s:float,k_bulk_w_m_k:float,
    rho_bulk_kg_m3:float,heat_flux_w_m2:float,diameter_m:float,
    bulk_temperature_k:float,pressure_pa:float,props:Callable,
    wall_upper_k:float=650.,
    scan_segments:int=16,max_iterations:int=35,
    tolerance_k:float=0.00001,
    max_energy_residual_relative:float=0.002,
)->tuple[LeiWallState,int,float]:
    """Solve the one-point energy condition q''=HTC(Tw)*(Tw-Tb).

    NO measured Tw used to solve. Bracket scan guards against
    disconnected/multiple detected roots. This finite scan cannot
    prove global uniqueness and does not model transverse flow.
    """
    _physical(heat_flux_w_m2,diameter_m,bulk_temperature_k,
              pressure_pa,tolerance_k,max_energy_residual_relative)
    if wall_upper_k<=bulk_temperature_k+2 or scan_segments<4 or max_iterations<1:
        raise CorrelationDomainError("invalid Lei wall root configuration")
    def evaluate(tw):
        state=lei_wall_state(
            orientation,re_bulk=re_bulk,mu_bulk_pa_s=mu_bulk_pa_s,
            k_bulk_w_m_k=k_bulk_w_m_k,
            rho_bulk_kg_m3=rho_bulk_kg_m3,
            heat_flux_w_m2=heat_flux_w_m2,diameter_m=diameter_m,
            bulk_temperature_k=bulk_temperature_k,
            wall_temperature_k=tw,pressure_pa=pressure_pa,props=props)
        return state.htc_w_m2_k*(tw-bulk_temperature_k)-heat_flux_w_m2,state
    lo_t=bulk_temperature_k+.0001
    scan=[lo_t+(wall_upper_k-lo_t)*i/scan_segments
          for i in range(scan_segments+1)]
    vals=[evaluate(x)[0] for x in scan]
    brackets=[(scan[i],scan[i+1]) for i in range(scan_segments)
              if vals[i]<0<=vals[i+1]]
    if len(brackets)!=1:
        raise CorrelationDomainError(
            f"Lei wall inverse detected {len(brackets)} brackets; "
            "must have one feasible energy root")
    lo,hi=brackets[0]
    for iteration in range(1,max_iterations+1):
        mid=(lo+hi)*.5
        residual,state=evaluate(mid)
        if residual>0:hi=mid
        else:lo=mid
        if hi-lo<=tolerance_k:
            rrel=abs(residual)/heat_flux_w_m2
            if rrel>max_energy_residual_relative:
                raise CorrelationDomainError(
                    f"Lei energy residual {rrel:.3g} exceeds solver tolerance")
            return state,iteration,rrel
    raise CorrelationDomainError("Lei wall inverse did not converge")
