"""Traceable steady single-phase pipe pressure-drop calculations.

Darcy-Weisbach + laminar 64/Re or turbulent Haaland approximation
to Colebrook-White. Geometry (D, length, roughness, K) and fluid
density/viscosity must come from a specific design or are declared
synthetic. This module is not a compressor map or plate-fin HX model.

References:
Haaland (1983), reproduced in https://doi.org/10.3390/jmse10060803
CoolProp PropsSI density/viscosity: https://coolprop.org/coolprop/HighLevelAPI.html

Conditions: fully developed isothermal circular single-phase duct;
fully turbulent regime uses Re>=4000; 2300<Re<4000 is REJECTED.
"""
from dataclasses import dataclass
from math import isfinite, pi, log10
from .properties import DomainError


@dataclass(frozen=True)
class CircularPipe:
    inner_diameter_m:float
    length_m:float
    absolute_roughness_m:float=0.
    minor_loss_k:float=0.

    def __post_init__(self)->None:
        v=vars(self)
        if not all(isfinite(x) for x in v.values()):
            raise DomainError("nonfinite hydraulic geometry")
        if (self.inner_diameter_m<=0 or self.length_m<0 or
            self.absolute_roughness_m<0 or self.minor_loss_k<0 or
            self.absolute_roughness_m>=self.inner_diameter_m):
            raise DomainError("invalid circular pipe geometry")

@dataclass(frozen=True)
class PipeLossResult:
    mass_flow_kg_s:float
    reynolds_number:float
    darcy_friction_factor:float
    mean_velocity_m_s:float
    pressure_drop_pa:float
    friction_drop_pa:float
    minor_drop_pa:float
    regime:str


def pipe_loss(
    geometry:CircularPipe,mdot_kg_s:float,
    density_kg_m3:float,dynamic_viscosity_pa_s:float,
)->PipeLossResult:
    if not all(isfinite(v) and v>0 for v in (
        mdot_kg_s,density_kg_m3,dynamic_viscosity_pa_s)):
        raise DomainError("pipe flow, density and viscosity must be positive")
    d=geometry.inner_diameter_m
    area=pi*d*d/4.
    velocity=mdot_kg_s/(density_kg_m3*area)
    re=density_kg_m3*velocity*d/dynamic_viscosity_pa_s
    if re<2300:
        regime="laminar"
        friction=64./re
    elif re<4000:
        raise DomainError("transition regime Re 2300-4000: correlation undefined")
    else:
        regime="turbulent_Haaland"
        z=((geometry.absolute_roughness_m/d/3.7)**1.11+6.9/re)
        friction=(-1.8*log10(z))**-2
    dynamic_pressure=.5*density_kg_m3*velocity*velocity
    friction_dp=friction*geometry.length_m/d*dynamic_pressure
    minor_dp=geometry.minor_loss_k*dynamic_pressure
    return PipeLossResult(mdot_kg_s,re,friction,velocity,
                          friction_dp+minor_dp,friction_dp,minor_dp,regime)


def co2_pipe_loss(
    geometry:CircularPipe,mdot_kg_s:float,
    pressure_pa:float,temperature_k:float,
)->PipeLossResult:
    """Single-point CO2 density and viscosity, not spatially integrated.

    No expansion/compressible friction integration, wall heat transfer,
    two-phase flow or hydraulic-network iteration is represented.
    """
    if not all(isfinite(x) and x>0 for x in (pressure_pa,temperature_k)):
        raise DomainError("invalid CO2 hydraulic property state")
    try:
        from CoolProp.CoolProp import PropsSI
    except ImportError as e:
        raise ImportError("install sco2-braytonbench[co2] for CO2 pipe properties") from e
    try:
        rho=PropsSI("Dmass","P",pressure_pa,"T",temperature_k,"HEOS::CO2")
        mu=PropsSI("VISCOSITY","P",pressure_pa,"T",temperature_k,"HEOS::CO2")
    except (ValueError,RuntimeError) as e:
        raise DomainError("CO2 density/viscosity call failed") from e
    return pipe_loss(geometry,mdot_kg_s,rho,mu)
