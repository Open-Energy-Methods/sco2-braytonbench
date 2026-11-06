"""Independent six-state recuperated steady cycle; not the CARBOSOLA rig."""
from dataclasses import dataclass
from math import isfinite
from .core import PressureLosses, cycle_pressures, compressor_outlet, turbine_outlet
from .exchangers import HXResult, segmented_recuperator
from .properties import DomainError, Properties, State

@dataclass(frozen=True)
class CycleInputs:
    p1_pa: float
    p4_pa: float
    t1_k: float
    t4_k: float
    mdot_kg_s: float
    eta_compressor: float
    eta_turbine: float
    losses: PressureLosses
    recuperator_effectiveness: float | None = None
    recuperator_ua_w_k: float | None = None
    segments: int = 30

@dataclass(frozen=True)
class CycleResult:
    states: tuple[State,State,State,State,State,State]
    recuperator: HXResult
    compressor_w: float
    turbine_w: float
    net_w: float
    heater_w: float
    cooler_w: float
    thermal_efficiency: float
    first_law_residual_w: float

def solve_cycle(props:Properties,c:CycleInputs) -> CycleResult:
    if (not isinstance(c.mdot_kg_s, (int, float))
            or not isfinite(c.mdot_kg_s) or c.mdot_kg_s<=0):
        raise DomainError('finite positive cycle mass flow required')
    p=cycle_pressures(c.p1_pa,c.p4_pa,c.losses)
    s1=props.tp(p.p1,c.t1_k)
    s2s=props.ps(p.p2,s1.s)
    s2=props.ph(p.p2,compressor_outlet(s1.h,s2s.h,c.eta_compressor))
    s4=props.tp(p.p4,c.t4_k)
    s5s=props.ps(p.p5,s4.s)
    s5=props.ph(p.p5,turbine_outlet(s4.h,s5s.h,c.eta_turbine))
    r=segmented_recuperator(props,s2,s5,p.p3,p.p6,c.mdot_kg_s,c.mdot_kg_s,
                            effectiveness=c.recuperator_effectiveness,
                            ua_w_k=c.recuperator_ua_w_k,n=c.segments)
    s3,s6=r.cold_out,r.hot_out
    w_c=c.mdot_kg_s*(s2.h-s1.h)
    w_t=c.mdot_kg_s*(s4.h-s5.h)
    q_h=c.mdot_kg_s*(s4.h-s3.h)
    q_c=c.mdot_kg_s*(s6.h-s1.h)
    if min(w_c,w_t,q_h,q_c)<0 or q_h==0:
        raise DomainError('infeasible steady-cycle duty or work signs')
    net=w_t-w_c
    residual=q_h-q_c-net
    if abs(residual)>1e-7*max(q_h,q_c,abs(net),1):
        raise DomainError('cycle energy residual exceeded tolerance')
    return CycleResult((s1,s2,s3,s4,s5,s6),r,w_c,w_t,net,q_h,q_c,net/q_h,residual)
