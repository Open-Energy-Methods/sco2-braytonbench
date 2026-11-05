"""Counterflow segmented HX and external waste-gas heater.

The pressure distribution is an explicit linear engineering assumption, not a
fitted CO2 heat-exchanger correlation. UA is inferred from the prescribed
profiles; no pressure-drop/UA design coupling is asserted.
"""
from dataclasses import dataclass
from math import isfinite, log
from .properties import DomainError, Properties, State

@dataclass(frozen=True)
class HXResult:
    q_w: float
    qmax_w: float
    min_approach_k: float
    required_ua_w_k: float
    cold_out: State
    hot_out: State

def _lmtd(a: float,b: float) -> float:
    if a<=0 or b<=0:
        raise DomainError('temperature crossing or zero approach in heat exchanger')
    if abs(a-b)<1e-9*max(a,b):
        return (a+b)/2
    return (a-b)/log(a/b)

def _temperatures(props: Properties, cold: State,hot: State,
                  p_cold_out: float,p_hot_out: float,m_cold:float,m_hot:float,
                  q:float,n:int) -> tuple[list[float],list[float]]:
    d=[]
    for i in range(n+1):
        x=i/n
        p_c=cold.p+x*(p_cold_out-cold.p)
        p_h=p_hot_out+x*(hot.p-p_hot_out)
        c=props.ph(p_c,cold.h+x*q/m_cold)
        h=props.ph(p_h,hot.h-(1-x)*q/m_hot)
        d.append(h.t-c.t)
    return d, [i/n for i in range(n+1)]

def segmented_recuperator(props:Properties,cold:State,hot:State,
                          p_cold_out:float,p_hot_out:float,
                          m_cold:float,m_hot:float,effectiveness:float | None = None,
                          ua_w_k:float | None = None,n:int=30) -> HXResult:
    if (effectiveness is None)==(ua_w_k is None):
        raise DomainError('choose exactly one of effectiveness or UA')
    if n<3 or m_cold<=0 or m_hot<=0 or p_cold_out<=0 or p_hot_out<=0:
        raise DomainError('invalid HX geometry, mass flow or pressure')
    if p_cold_out>cold.p or p_hot_out>hot.p:
        raise DomainError('recuperator outlet pressures exceed inlet pressures')
    if effectiveness is not None and not 0<=effectiveness<=1:
        raise DomainError('effectiveness outside [0,1]')
    if ua_w_k is not None and (not isfinite(ua_w_k) or ua_w_k<0):
        raise DomainError('invalid UA')
    if hot.t<=cold.t:
        raise DomainError('hot recuperator inlet must exceed cold inlet temperature')
    qcap_c=m_cold*(props.tp(p_cold_out,hot.t).h-cold.h)
    qcap_h=m_hot*(hot.h-props.tp(p_hot_out,cold.t).h)
    qhi=min(qcap_c,qcap_h)
    if qhi<=0:
        raise DomainError('no forward heat transfer possible')
    def profile(q:float)->list[float]:
        return _temperatures(props,cold,hot,p_cold_out,p_hot_out,m_cold,m_hot,q,n)[0]
    if min(profile(0))<=0:
        raise DomainError('input pressure mapping produces reverse exchange')
    lo,hi=0.0,qhi
    for _ in range(70):
        mid=(lo+hi)/2
        if min(profile(mid))>=0: lo=mid
        else: hi=mid
    qmax=lo
    def required_ua(q:float)->float:
        if q==0: return 0.0
        dt=profile(q)
        return sum((q/n)/_lmtd(dt[i],dt[i+1]) for i in range(n))
    if effectiveness is not None:
        q=qmax*effectiveness
    else:
        lo,hi=0.,qmax*(1-1e-9)
        for _ in range(65):
            qmid=(lo+hi)/2
            if required_ua(qmid)>ua_w_k: hi=qmid
            else: lo=qmid
        q=(lo+hi)/2
    if q==qmax and min(profile(q))<1e-9:
        # An infinite-area pinch limit is not a finite-UA design point.
        ua=float('inf')
    else:
        ua=required_ua(q)
    return HXResult(q,qmax,min(profile(q)),ua,
                    props.ph(p_cold_out,cold.h+q/m_cold),
                    props.ph(p_hot_out,hot.h-q/m_hot))

@dataclass(frozen=True)
class HeaterResult:
    q_w: float
    gas_out_k: float
    min_approach_k: float
    required_ua_w_k: float

def waste_gas_heater(props:Properties,co2_in:State,co2_out:State,
                     m_co2:float,t_gas_in:float,m_gas:float,cp_gas:float,
                     min_pinch_k:float=10.,n:int=30) -> HeaterResult:
    if n<3 or min(m_co2,m_gas,cp_gas,t_gas_in)<=0 or min_pinch_k<0:
        raise DomainError('invalid heater inputs')
    if co2_out.p>co2_in.p:
        raise DomainError('heater pressure must not rise')
    q=m_co2*(co2_out.h-co2_in.h)
    if q<=0:
        raise DomainError('heater must add heat to CO2')
    gas_out=t_gas_in-q/(m_gas*cp_gas)
    d=[]
    for i in range(n+1):
        x=i/n
        t_co2=props.ph(co2_in.p+x*(co2_out.p-co2_in.p),co2_in.h+x*q/m_co2).t
        t_gas=gas_out+x*(t_gas_in-gas_out)
        d.append(t_gas-t_co2)
    if min(d)<min_pinch_k:
        raise DomainError(f'infeasible gas heater: pinch {min(d):.4g} K < {min_pinch_k} K')
    ua=sum(q/n/_lmtd(d[i],d[i+1]) for i in range(n))
    return HeaterResult(q,gas_out,min(d),ua)
