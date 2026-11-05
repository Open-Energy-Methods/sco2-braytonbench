"""Finite-medium, fixed-UA cooler rating for a six-state CO2 Brayton model.

Both coolant and CO2 energy balances are explicit. No phase change,
finite sink pressure dynamics, cooling-tower performance, fan/pump power
or measured heat-transfer correlation are claimed. Pressure changes in
CO2 follow the cycle's already-prescribed cooler pressure loss.
"""
from dataclasses import dataclass
from math import isfinite
from .properties import DomainError, Properties, State
from .streams import LinearCp, SensibleStream
from .exchangers import _lmtd


@dataclass(frozen=True)
class CoolerSink:
    inlet_temperature_k: float
    mass_flow_kg_s: float
    cp_j_kg_k: float
    installed_ua_w_k: float
    minimum_approach_k: float = 5.0
    maximum_outlet_temperature_k: float = 340.0
    segments: int = 12
    cp_slope_j_kg_k2: float = 0.0
    cp_reference_temperature_k: float = 300.0
    fluid_property_model: SensibleStream | None = None

    def __post_init__(self) -> None:
        if not all(isfinite(x) and x>0 for x in (
            self.inlet_temperature_k,self.mass_flow_kg_s,
            self.cp_j_kg_k,self.installed_ua_w_k,
            self.maximum_outlet_temperature_k)):
            raise DomainError("invalid finite cooler stream or installed UA")
        if (not isfinite(self.minimum_approach_k) or
            self.minimum_approach_k<=0 or self.segments<3 or
            self.maximum_outlet_temperature_k<=self.inlet_temperature_k):
            raise DomainError("invalid cooler approach, outlet limit or segment count")
        model=self.heat_capacity
        model.cp(self.inlet_temperature_k)
        model.cp(self.maximum_outlet_temperature_k)

    @property
    def heat_capacity(self)->SensibleStream:
        if self.fluid_property_model is not None:
            return self.fluid_property_model
        return LinearCp(self.cp_j_kg_k,self.cp_slope_j_kg_k2,
                        self.cp_reference_temperature_k)


@dataclass(frozen=True)
class CoolerRating:
    rejected_heat_w: float
    coolant_outlet_k: float
    minimum_approach_k: float
    cold_end_approach_k: float
    hot_end_approach_k: float
    required_ua_w_k: float
    coolant_energy_residual_w: float
    entropy_generation_w_k: float


def rate_cooler(
    props: Properties, co2_hot_in: State, co2_cold_out: State,
    m_co2_kg_s: float, sink: CoolerSink,
) -> CoolerRating:
    """Rating result for a *prescribed* CO2 outlet, not yet solved UA equality.

    Counterflow coordinate x=0 is the CO2 outlet/coolant inlet, while
    x=1 is the CO2 inlet/coolant outlet. Equal duty segments use equal
    CO2 enthalpy increments; coolant temperatures use enthalpy inversion.
    """
    if not isfinite(m_co2_kg_s) or m_co2_kg_s<=0:
        raise DomainError("invalid CO2 cooler mass flow")
    if co2_hot_in.p<co2_cold_out.p:
        raise DomainError("CO2 pressure cannot rise through cooler")
    q=m_co2_kg_s*(co2_hot_in.h-co2_cold_out.h)
    if not isfinite(q) or q<=0:
        raise DomainError("cooler must reject positive CO2 heat")
    stream=sink.heat_capacity
    t_cool_out=stream.temperature_for_delta_h(
        sink.inlet_temperature_k,q/sink.mass_flow_kg_s)
    if t_cool_out>sink.maximum_outlet_temperature_k:
        raise DomainError("coolant outlet exceeds admissible temperature")
    approaches=[]
    n=sink.segments
    for i in range(n+1):
        x=i/n
        p=co2_cold_out.p+x*(co2_hot_in.p-co2_cold_out.p)
        h=co2_cold_out.h+x*q/m_co2_kg_s
        t_co2=props.ph(p,h).t
        t_cool=stream.temperature_for_delta_h(
            sink.inlet_temperature_k,x*q/sink.mass_flow_kg_s)
        approaches.append(t_co2-t_cool)
    dt_min=min(approaches)
    if dt_min<sink.minimum_approach_k:
        raise DomainError(f"cooler temperature approach {dt_min:.4g} K below minimum")
    ua=sum((q/n)/_lmtd(approaches[i],approaches[i+1])
           for i in range(n))
    residual=(sink.mass_flow_kg_s*
              stream.delta_h(sink.inlet_temperature_k,t_cool_out)-q)
    entropy=(m_co2_kg_s*(co2_cold_out.s-co2_hot_in.s)+
             sink.mass_flow_kg_s*stream.delta_s(
                sink.inlet_temperature_k,t_cool_out))
    if entropy< -1e-6*max(abs(q)/max(sink.inlet_temperature_k,1.),1.):
        raise DomainError("cooler exhibits negative total entropy production")
    if abs(residual)>1e-8*max(q,1.):
        raise DomainError("cooler energy balance did not close")
    if not isfinite(ua) or ua<=0:
        raise DomainError("invalid calculated cooler UA")
    return CoolerRating(
        rejected_heat_w=q,
        coolant_outlet_k=t_cool_out,
        minimum_approach_k=dt_min,
        cold_end_approach_k=approaches[0],
        hot_end_approach_k=approaches[-1],
        required_ua_w_k=ua,
        coolant_energy_residual_w=residual,
        entropy_generation_w_k=entropy,
    )
