"""Thermodynamic backend contract. SI units; pressure is absolute.

IdealGasFixture is for deterministic structural tests ONLY; it is not CO2.
"""
from __future__ import annotations
from dataclasses import dataclass
from math import exp, isfinite, log
from typing import Protocol

class DomainError(ValueError):
    """Unphysical input, failed property call, or impossible cycle."""

@dataclass(frozen=True)
class State:
    p: float     # Pa
    t: float     # K
    h: float     # J/kg
    s: float     # J/(kg K)

class Properties(Protocol):
    def tp(self, p: float, t: float) -> State: ...
    def ph(self, p: float, h: float) -> State: ...
    def ps(self, p: float, s: float) -> State: ...

def _positive(name: str, x: float) -> float:
    if not isinstance(x, (int, float)) or not isfinite(x) or x <= 0:
        raise DomainError(f"{name} must be finite and positive")
    return float(x)

@dataclass(frozen=True)
class IdealGasFixture:
    """Artificial constant-cp fluid used only to test numerical plumbing."""
    cp: float = 1000.0
    gas_constant: float = 200.0
    t_ref: float = 300.0
    p_ref: float = 1e5

    def __post_init__(self) -> None:
        for k in ('cp','gas_constant','t_ref','p_ref'):
            _positive(k, getattr(self,k))
        if self.cp <= self.gas_constant:
            raise DomainError('cp must exceed gas_constant')

    def tp(self, p: float, t: float) -> State:
        p,t = _positive('p',p), _positive('T',t)
        return State(p,t,self.cp*(t-self.t_ref),
                     self.cp*log(t/self.t_ref)-self.gas_constant*log(p/self.p_ref))
    def ph(self, p: float, h: float) -> State:
        return self.tp(p, self.t_ref + h/self.cp)
    def ps(self, p: float, s: float) -> State:
        p=_positive('p',p)
        return self.tp(p,self.t_ref*exp((s+self.gas_constant*log(p/self.p_ref))/self.cp))

class CoolPropCO2:
    """Optional CoolProp HEOS CO2 backend; installation is never implicit."""
    def __init__(self) -> None:
        try:
            from CoolProp.CoolProp import PropsSI
        except ImportError as exc:
            raise ImportError('Install sco2-braytonbench[co2] for CoolProp') from exc
        self._props = PropsSI

    def _state(self, key1: str, val1: float, key2: str, val2: float) -> State:
        try:
            p=self._props('P',key1,val1,key2,val2,'HEOS::CO2')
            t=self._props('T',key1,val1,key2,val2,'HEOS::CO2')
            h=self._props('Hmass',key1,val1,key2,val2,'HEOS::CO2')
            s=self._props('Smass',key1,val1,key2,val2,'HEOS::CO2')
        except (ValueError,RuntimeError,OverflowError) as exc:
            raise DomainError(f'CO2 EOS failed at {key1}={val1}, {key2}={val2}') from exc
        if not all(isfinite(v) for v in (p,t,h,s)):
            raise DomainError('CO2 EOS produced nonfinite property')
        return State(p,t,h,s)

    def tp(self, p: float, t: float) -> State:
        return self._state('P',_positive('p',p),'T',_positive('T',t))
    def ph(self, p: float, h: float) -> State:
        return self._state('P',_positive('p',p),'Hmass',h)
    def ps(self, p: float, s: float) -> State:
        return self._state('P',_positive('p',p),'Smass',s)
