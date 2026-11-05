"""SI-unit pressure closure and turbomachinery sign contracts."""
from dataclasses import dataclass
from math import isfinite
from .properties import DomainError

@dataclass(frozen=True)
class PressureLosses:
    cold_recup: float = 0.0
    heater: float = 0.0
    hot_recup: float = 0.0
    cooler: float = 0.0

@dataclass(frozen=True)
class Pressures:
    p1: float
    p2: float
    p3: float
    p4: float
    p5: float
    p6: float

def cycle_pressures(p1: float,p4: float,loss: PressureLosses) -> Pressures:
    if not all(isfinite(x) for x in (p1,p4,*vars(loss).values())):
        raise DomainError('all pressure inputs must be finite')
    if p1 <= 0 or p4 <= 0 or any(x < 0 for x in vars(loss).values()):
        raise DomainError('pressures positive, pressure losses nonnegative')
    p3 = p4+loss.heater
    p2 = p3+loss.cold_recup
    p6 = p1+loss.cooler
    p5 = p6+loss.hot_recup
    if not (p2 > p1 and p4 > p5):
        raise DomainError('compressor or turbine cannot operate across given pressures')
    return Pressures(p1,p2,p3,p4,p5,p6)

def compressor_outlet(h_in: float,h_is: float,eta: float) -> float:
    if not all(isfinite(x) for x in (h_in,h_is,eta)) or not 0<eta<=1 or h_is<h_in:
        raise DomainError('invalid compressor efficiency or enthalpy order')
    return h_in+(h_is-h_in)/eta

def turbine_outlet(h_in: float,h_is: float,eta: float) -> float:
    if not all(isfinite(x) for x in (h_in,h_is,eta)) or not 0<eta<=1 or h_is>h_in:
        raise DomainError('invalid turbine efficiency or enthalpy order')
    return h_in-eta*(h_in-h_is)
