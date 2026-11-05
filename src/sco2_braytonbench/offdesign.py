"""Scenario-only flow scaling laws, NOT validated equipment maps.

At fixed geometry single-phase flow, pressure drop often increases
roughly with squared mass flow; this exponent is a transparent
engineering *assumption*. It is NOT the original MK2014 2%-FPD rule.
Turbomachinery efficiency penalty is purely illustrative and bounded.
"""
from dataclasses import dataclass, replace
from math import isfinite
from .core import PressureLosses
from .cycle import CycleInputs
from .properties import DomainError


@dataclass(frozen=True)
class FlowScaling:
    reference_mass_flow_kg_s: float
    pressure_loss_exponent: float = 2.0
    compressor_efficiency_penalty: float = 0.0
    turbine_efficiency_penalty: float = 0.0
    minimum_efficiency: float = 0.50
    max_relative_flow: float = 1.75
    min_relative_flow: float = 0.50

    def __post_init__(self)->None:
        for v in vars(self).values():
            if not isfinite(v):
                raise DomainError("flow scaling parameters must be finite")
        if (self.reference_mass_flow_kg_s<=0 or
            not 0<=self.pressure_loss_exponent<=4 or
            self.compressor_efficiency_penalty<0 or
            self.turbine_efficiency_penalty<0 or
            not 0<self.minimum_efficiency<=1 or
            self.min_relative_flow<=0 or
            self.max_relative_flow<self.min_relative_flow):
            raise DomainError("invalid flow scaling domain or bounds")

    def at_flow(self, base: CycleInputs, mass_flow_kg_s: float)->CycleInputs:
        if not isfinite(mass_flow_kg_s) or mass_flow_kg_s<=0:
            raise DomainError("invalid target mass flow for scaling")
        ratio=mass_flow_kg_s/self.reference_mass_flow_kg_s
        if not self.min_relative_flow<=ratio<=self.max_relative_flow:
            raise DomainError("flow outside declared scaling domain")
        scale=ratio**self.pressure_loss_exponent
        losses=PressureLosses(
            **{k:v*scale for k,v in vars(base.losses).items()})
        ec=base.eta_compressor-self.compressor_efficiency_penalty*(ratio-1)**2
        et=base.eta_turbine-self.turbine_efficiency_penalty*(ratio-1)**2
        if ec<self.minimum_efficiency or et<self.minimum_efficiency:
            raise DomainError("estimated machine efficiency below assumed lower bound")
        if ec>1 or et>1:
            raise DomainError("estimated machine efficiency above unity")
        return replace(
            base,mdot_kg_s=mass_flow_kg_s,
            losses=losses,eta_compressor=ec,eta_turbine=et)
