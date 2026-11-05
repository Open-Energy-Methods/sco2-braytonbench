"""Finite exhaust-gas coupling for a six-state recuperated CO2 cycle.

This is a *design-screening* model: a candidate (T_turbine_in, mdot_CO2)
is evaluated under a bounded available heat-exchanger UA and finite
waste-gas energy inventory. UA_max is a sizing CAP, not a physical
fixed-geometry equality; candidates below the limit assume a permitted
bypass/modulation design. No such actuator has been modelled dynamically.

The model follows the open-loop WHR objective explained by
Mohagheghi & Kapat (2014), but does not reproduce their GA, RRC topology,
compressor-loss convention, terminal dT decision variables or results.
All units are SI.
"""
from __future__ import annotations

from dataclasses import dataclass
from math import isfinite, log
from typing import Iterable

from .cycle import CycleInputs, CycleResult, solve_cycle
from .exchangers import HeaterResult, waste_gas_heater
from .properties import DomainError, Properties


@dataclass(frozen=True)
class WasteGasSource:
    inlet_temperature_k: float
    mass_flow_kg_s: float
    cp_j_kg_k: float
    minimum_stack_temperature_k: float
    maximum_heater_ua_w_k: float
    minimum_heater_approach_k: float = 10.0
    dead_state_temperature_k: float = 300.0
    segments: int = 20

    def __post_init__(self) -> None:
        must_be_positive = (
            "inlet_temperature_k", "mass_flow_kg_s", "cp_j_kg_k",
            "minimum_stack_temperature_k", "maximum_heater_ua_w_k",
            "dead_state_temperature_k",
        )
        for key in must_be_positive:
            x = getattr(self, key)
            if not isfinite(x) or x <= 0:
                raise DomainError(f"{key} must be finite and positive")
        d = self.minimum_heater_approach_k
        if not isfinite(d) or d <= 0:
            raise DomainError("minimum heater approach must be finite and positive")
        if self.minimum_stack_temperature_k <= self.dead_state_temperature_k:
            raise DomainError("stack minimum must exceed the specified dead state")
        if self.inlet_temperature_k <= self.minimum_stack_temperature_k:
            raise DomainError("waste gas must be hotter than the stack floor")
        if self.segments < 3:
            raise DomainError("heater segmentation must be >=3")

    @property
    def capacity_rate_w_k(self) -> float:
        return self.mass_flow_kg_s * self.cp_j_kg_k

    @property
    def available_heat_w(self) -> float:
        """Sensible heat before the prescribed stack-temperature floor."""
        return self.capacity_rate_w_k * (
            self.inlet_temperature_k - self.minimum_stack_temperature_k
        )


@dataclass(frozen=True)
class PlantDesignLimits:
    """Optional non-source-engineering constraints for sensitivity screening.

    The 2014 paper uses recuperator *terminal* dT as a decision variable;
    this class instead uses the resolved local minimum approach. These
    quantities must not be identified as equivalent.
    """
    minimum_recuperator_approach_k: float = 0.0
    maximum_cooler_duty_w: float | None = None

    def __post_init__(self) -> None:
        d = self.minimum_recuperator_approach_k
        if not isfinite(d) or d < 0:
            raise DomainError("recuperator minimum approach must be finite and nonnegative")
        if self.maximum_cooler_duty_w is not None and (
            not isfinite(self.maximum_cooler_duty_w)
            or self.maximum_cooler_duty_w <= 0
        ):
            raise DomainError("maximum cooler duty must be finite and positive")


@dataclass(frozen=True)
class WHRPoint:
    inputs: CycleInputs
    cycle: CycleResult
    heater: HeaterResult
    source_available_w: float
    source_exergy_consumed_w: float
    heat_utilization: float
    first_law_combined_residual_w: float

    @property
    def net_shaft_power_w(self) -> float:
        return self.cycle.net_w

    @property
    def cycle_thermal_efficiency(self) -> float:
        return self.cycle.thermal_efficiency


@dataclass(frozen=True)
class Rejection:
    inputs: CycleInputs
    reason: str


@dataclass(frozen=True)
class WHRScreen:
    feasible: tuple[WHRPoint, ...]
    rejected: tuple[Rejection, ...]
    maximum_shaft_power: WHRPoint
    maximum_cycle_efficiency: WHRPoint

    @property
    def evaluated_count(self) -> int:
        return len(self.feasible) + len(self.rejected)


def evaluate_whr_design(
    props: Properties, inputs: CycleInputs, source: WasteGasSource,
    *, limits: PlantDesignLimits | None = None,
    enforce_heater_ua_cap: bool = True,
) -> WHRPoint:
    """Check one externally selected CO2 mass flow and turbine-inlet T.

    The CO2 cycle is first solved with a finite-UA recuperator. The gas
    source must then supply the *actual* heater enthalpy increase without
    pinch crossing, exceeding heater UA sizing allowance, or crossing the
    stated stack minimum. This does not solve turbine-inlet T from an
    installed heater's equality UA = UA_required.
    """
    if inputs.recuperator_effectiveness is not None:
        raise DomainError("WHR design requires recuperator finite-UA mode")
    if inputs.recuperator_ua_w_k is None:
        raise DomainError("recuperator UA must be explicitly specified")
    if inputs.t4_k >= source.inlet_temperature_k-source.minimum_heater_approach_k:
        raise DomainError("turbine inlet temperature violates source hot-end approach")
    cycle = solve_cycle(props, inputs)
    if cycle.net_w <= 0:
        raise DomainError("nonpositive net shaft power")
    if limits is not None:
        if cycle.recuperator.min_approach_k < (
            limits.minimum_recuperator_approach_k - 1e-8
        ):
            raise DomainError("recuperator below additional minimum approach")
        if (limits.maximum_cooler_duty_w is not None
            and cycle.cooler_w > limits.maximum_cooler_duty_w*(1+1e-8)):
            raise DomainError("cooler exceeds additional duty allowance")
    s3, s4 = cycle.states[2], cycle.states[3]
    heater = waste_gas_heater(
        props, s3, s4, inputs.mdot_kg_s,
        source.inlet_temperature_k, source.mass_flow_kg_s,
        source.cp_j_kg_k, source.minimum_heater_approach_k,
        n=source.segments,
    )
    if heater.gas_out_k < source.minimum_stack_temperature_k - 1e-8:
        raise DomainError("stack temperature below design minimum")
    if (enforce_heater_ua_cap
        and heater.required_ua_w_k > source.maximum_heater_ua_w_k*(1+1e-8)):
        raise DomainError("heater exceeds UA sizing allowance")

    q_exhaust = source.capacity_rate_w_k * (
        source.inlet_temperature_k - heater.gas_out_k
    )
    closure = q_exhaust - cycle.heater_w
    if abs(closure) > 1e-8*max(q_exhaust,cycle.heater_w,1.0):
        raise DomainError("CO2 / exhaust first-law mismatch")

    t0 = source.dead_state_temperature_k
    exergy = source.capacity_rate_w_k * (
        (source.inlet_temperature_k - heater.gas_out_k)
        - t0 * log(source.inlet_temperature_k/heater.gas_out_k)
    )
    if exergy <= 0:
        raise DomainError("nonpositive source exergy consumption")
    if cycle.net_w > exergy*(1+1e-8):
        raise DomainError("net power exceeds extracted waste-gas flow exergy")

    utilization = heater.q_w/source.available_heat_w
    if utilization > 1+1e-8:
        raise DomainError("source heat utilization exceeds availability")
    return WHRPoint(inputs,cycle,heater,source.available_heat_w,
                    exergy,utilization,closure)


def screen_whr_designs(
    props: Properties, source: WasteGasSource,
    candidates: Iterable[CycleInputs],
    *, limits: PlantDesignLimits | None = None
) -> WHRScreen:
    """Deterministic finite-grid screening, NOT a global GA optimization.

    Every candidate is retained as feasible or rejected with the reason.
    The maxima are restricted to the sampled candidates and constraints.
    """
    feasible: list[WHRPoint] = []
    rejected: list[Rejection] = []
    for design in candidates:
        try:
            feasible.append(evaluate_whr_design(props, design, source, limits=limits))
        except DomainError as exc:
            rejected.append(Rejection(design, str(exc)))
    if not feasible:
        raise DomainError("no feasible candidates in the supplied design grid")
    power = max(feasible, key=lambda x: (x.net_shaft_power_w,
                                         x.cycle_thermal_efficiency))
    efficiency = max(feasible, key=lambda x: (x.cycle_thermal_efficiency,
                                              x.net_shaft_power_w))
    return WHRScreen(tuple(feasible),tuple(rejected),power,efficiency)
