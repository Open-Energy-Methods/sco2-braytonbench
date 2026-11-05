"""Explicit, auditable sensible-stream closure with constant or linear cp.

cp(T) = cp_ref + slope*(T-T_ref). No phase change, gas composition,
pressure exergy or fluid-specific transport properties are modelled.
These are transparent exploratory correlations, NOT calibrated air/water.
SI units: T K, cp J/(kg K), enthalpy changes J/kg, entropy J/(kg K).
"""
from dataclasses import dataclass
from typing import Protocol

class SensibleStream(Protocol):
    def cp(self, t_k:float)->float: ...
    def delta_h(self,t1_k:float,t2_k:float)->float: ...
    def delta_s(self,t1_k:float,t2_k:float)->float: ...
    def temperature_for_delta_h(self,t_start_k:float,dh_j_kg:float)->float: ...

from math import isfinite, log, sqrt
from .properties import DomainError


@dataclass(frozen=True)
class LinearCp:
    cp_ref_j_kg_k: float
    slope_j_kg_k2: float = 0.0
    reference_temperature_k: float = 300.0

    def __post_init__(self) -> None:
        if (not all(isfinite(x) for x in (
                self.cp_ref_j_kg_k, self.slope_j_kg_k2,
                self.reference_temperature_k))
                or self.cp_ref_j_kg_k <= 0
                or self.reference_temperature_k <= 0):
            raise DomainError("linear cp reference and temperature must be physical")

    def cp(self, t_k: float) -> float:
        if not isfinite(t_k) or t_k <= 0:
            raise DomainError("sensible-stream temperature must be positive")
        value = self.cp_ref_j_kg_k + self.slope_j_kg_k2 * (
            t_k - self.reference_temperature_k)
        if not isfinite(value) or value <= 0:
            raise DomainError("sensible-stream cp outside declared positive domain")
        return value

    def delta_h(self, t_in_k: float, t_out_k: float) -> float:
        cp_in=self.cp(t_in_k)
        cp_out=self.cp(t_out_k)
        dt=t_out_k-t_in_k
        return 0.5*(cp_in+cp_out)*dt

    def delta_s(self, t_in_k: float, t_out_k: float) -> float:
        self.cp(t_in_k)
        self.cp(t_out_k)
        b=self.slope_j_kg_k2
        a=self.cp_ref_j_kg_k-b*self.reference_temperature_k
        return a*log(t_out_k/t_in_k)+b*(t_out_k-t_in_k)

    def temperature_for_delta_h(self, t_start_k: float, dh_j_kg: float) -> float:
        """Invert sensible enthalpy analytically, on a positive-cp branch."""
        cp0=self.cp(t_start_k)
        if not isfinite(dh_j_kg):
            raise DomainError("nonfinite sensible enthalpy difference")
        if dh_j_kg==0:
            return t_start_k
        b=self.slope_j_kg_k2
        if b==0:
            t=t_start_k+dh_j_kg/cp0
        else:
            rad=cp0*cp0+2*b*dh_j_kg
            if rad<=0 or not isfinite(rad):
                raise DomainError("sensible enthalpy outside monotonic cp domain")
            # Stable near b=0 (avoid cancellation in quadratic inversion).
            den=cp0+sqrt(rad)
            t=t_start_k+2*dh_j_kg/den
        self.cp(t)
        if abs(self.delta_h(t_start_k,t)-dh_j_kg)>1e-8*max(abs(dh_j_kg),1):
            raise DomainError("sensible enthalpy inversion did not close")
        return t
