"""WP3: finite-source gas bypass, sample-and-hold actuator and thermal-wall PI.

The active gas passes through the existing WP2b gas-to-wall exchanger.
The bypass branch remains at incoming source temperature. Mixing of
both branches occurs *after* the active stream leaves that exchanger.
This makes external source enthalpy extraction equal to the existing
wall input and avoids an unphysical energy-source multiplication.

The only dynamic storage is the WP2b wall. No CO2 mass/pressure
inventory, rotating machinery control, pump/valve flow map, or
experimentally tuned plant controller is represented.
"""
from __future__ import annotations

from dataclasses import dataclass
from math import isfinite, sqrt
from typing import Iterable

from .cycle import CycleInputs
from .dynamic_whr import (
    FiniteGasLoad, WallCycleEquipment, WallCycleInterval, wall_cycle_step
)
from .properties import DomainError, Properties


def _valid_number(name: str, value: float, *, nonnegative: bool = False) -> None:
    if (isinstance(value, bool) or not isinstance(value, (int, float))
            or not isfinite(value)
            or (value < 0 if nonnegative else value <= 0)):
        raise DomainError(f"{name} must be finite and "
                          f"{'nonnegative' if nonnegative else 'positive'}")


def _clip(value: float, lo: float, hi: float) -> float:
    return min(max(value, lo), hi)


@dataclass(frozen=True)
class SourceBypass:
    """A measured-equipment-independent *fraction of hot gas* bypassing the wall.

    0 <= bypass <= max_fraction < 1.0 guarantees strictly positive
    mass flow through the existing WP2b finite hot-gas exchanger.
    The physical valve position is taken to equal diverted source
    mass fraction; no nonlinear valve Cv or pressure network exists.
    """

    max_fraction: float = 0.85
    max_rate_fraction_s: float = 0.025
    minimum_active_mass_flow_kg_s: float = 1.0

    def __post_init__(self) -> None:
        for label in ("max_fraction", "max_rate_fraction_s",
                      "minimum_active_mass_flow_kg_s"):
            _valid_number(label, getattr(self, label))
        if not 0 < self.max_fraction < 1.:
            raise DomainError("maximum bypass must be in (0,1)")


@dataclass(frozen=True)
class WallPI:
    """Sampled wall-temperature PI, with reverse-gain bypass convention.

    Error e = T_wall - setpoint, so a hotter wall orders *more* bypass.
    I state is in bypass fraction and includes a back-calculation
    tracking term against actual rate-limited actuator position.
    """

    setpoint_temperature_k: float
    kp_fraction_k: float
    ki_fraction_k_s: float
    bias_fraction: float = 0.0
    tracking_gain_s: float = 0.2
    integral_limit_fraction: float = 1.5

    def __post_init__(self) -> None:
        _valid_number("wall setpoint", self.setpoint_temperature_k)
        for label in ("kp_fraction_k", "ki_fraction_k_s",
                      "bias_fraction", "tracking_gain_s"):
            _valid_number(label, getattr(self, label), nonnegative=True)
        _valid_number("integral_limit_fraction", self.integral_limit_fraction)
        if self.kp_fraction_k == 0 and self.ki_fraction_k_s == 0:
            raise DomainError("PI requires a nonzero Kp or Ki")


@dataclass(frozen=True)
class BypassControlStep:
    """Source/mixed-outlet and PI state ledger over one source interval."""

    time_start_s: float
    time_end_s: float
    setpoint_temperature_k: float
    start_error_k: float
    end_error_k: float
    bypass_fraction: float
    requested_fraction: float
    unbounded_fraction: float
    applied_rate_fraction_s: float
    integral_fraction_after: float
    active_gas_flow_kg_s: float
    diverted_gas_flow_kg_s: float
    mixed_gas_outlet_initial_k: float
    mixed_gas_outlet_final_k: float
    mixed_gas_outlet_mean_k: float
    source_energy_residual_j: float
    combined_total_stream_residual_j: float
    plant: WallCycleInterval


@dataclass(frozen=True)
class ControlPerformance:
    """Finite sampled-time descriptive metrics, not optimality claims."""

    interval_count: int
    duration_s: float
    sample_endpoint_rmse_k: float
    absolute_error_trapezoid_k_s: float
    maximum_wall_temperature_k: float
    minimum_wall_temperature_k: float
    maximum_bypass_fraction: float
    minimum_bypass_fraction: float
    total_gas_to_wall_energy_j: float
    total_shaft_energy_j: float
    total_cooler_energy_j: float
    total_wall_storage_energy_j: float
    total_energy_residual_j: float


def _next_bypass(
    actuator: SourceBypass,
    controller: WallPI | None,
    wall_temperature_k: float,
    setpoint_k: float,
    previous_fraction: float,
    integral_fraction: float,
    duration_s: float,
) -> tuple[float, float, float, float]:
    """Actuator-command and anti-windup update from *current* wall T only."""
    if controller is None:
        raw = previous_fraction  # fixed open-loop operating point
    else:
        raw = (controller.bias_fraction
               + controller.kp_fraction_k * (wall_temperature_k-setpoint_k)
               + integral_fraction)
    if not isfinite(raw):
        raise DomainError("nonfinite PI command")
    requested = _clip(raw, 0., actuator.max_fraction)
    max_motion = duration_s * actuator.max_rate_fraction_s
    actual = _clip(requested,
                   max(0., previous_fraction-max_motion),
                   min(actuator.max_fraction, previous_fraction+max_motion))
    if controller is None:
        return raw, requested, actual, integral_fraction
    if controller.tracking_gain_s * duration_s > 1.:
        raise DomainError(
            "PI back-calculation sample violates gain*duration <= 1"
        )
    error = wall_temperature_k-setpoint_k
    # Tracking the *achieved* valve position prevents integrator wind-up
    # on both hard-position saturation and sample-to-sample slew limits.
    next_integral = (
        integral_fraction
        + controller.ki_fraction_k_s * error * duration_s
        + controller.tracking_gain_s * (actual-raw) * duration_s
    )
    next_integral = _clip(
        next_integral, -controller.integral_limit_fraction,
        controller.integral_limit_fraction
    )
    return raw, requested, actual, next_integral


def simulate_bypass_control(
    props: Properties,
    base_cycle: CycleInputs,
    equipment: WallCycleEquipment,
    loads: Iterable[FiniteGasLoad],
    actuator: SourceBypass,
    *,
    initial_wall_temperature_k: float,
    initial_bypass_fraction: float,
    setpoint_temperature_k: float,
    controller: WallPI | None = None,
) -> tuple[BypassControlStep, ...]:
    """Simulate fixed-source-bypass open loop or causal sampled PI feedback.

    The input source mass flow is TOTAL gas flow; physical branch split:
        m_active=(1-b)*m_total, m_bypass=b*m_total.
    The original WP2b gas-wall power is evaluated only on m_active.
    The bypass carries *uncooled* gas to the exit mixing junction.
    Source enthalpy through the mixed junction = Q_gas_to_wall.
    """
    _valid_number("initial wall temperature", initial_wall_temperature_k)
    _valid_number("setpoint temperature", setpoint_temperature_k)
    _valid_number("initial bypass", initial_bypass_fraction, nonnegative=True)
    if initial_bypass_fraction > actuator.max_fraction:
        raise DomainError("initial bypass fraction exceeds actuator maximum")
    if controller is not None and (
        controller.setpoint_temperature_k != setpoint_temperature_k
    ):
        raise DomainError("controller setpoint does not match scenario")
    steps: list[BypassControlStep] = []
    wall = initial_wall_temperature_k
    position, integral, time = initial_bypass_fraction, 0., 0.
    for index, load in enumerate(loads):
        try:
            raw, request, applied, next_integral = _next_bypass(
                actuator, controller, wall, setpoint_temperature_k,
                position, integral, load.duration_s
            )
            active_flow = (1.-applied)*load.mass_flow_kg_s
            diverted_flow = applied*load.mass_flow_kg_s
            if active_flow < actuator.minimum_active_mass_flow_kg_s:
                raise DomainError("gas-to-wall branch below minimum active flow")
            active_load = FiniteGasLoad(
                load.inlet_temperature_k, active_flow, load.duration_s
            )
            plant = wall_cycle_step(
                props, base_cycle, equipment, wall,
                active_load, time_start_s=time
            )

            # Mixing junction is outside the dynamic wall CV. For fixed
            # cp_g, energy of gas rejected at full flow must equal Q_wall.
            mixed_start = (
                (1.-applied)*plant.initial.hot_gas_outlet_temperature_k
                + applied*load.inlet_temperature_k
            )
            mixed_end = (
                (1.-applied)*plant.final.hot_gas_outlet_temperature_k
                + applied*load.inlet_temperature_k
            )
            total_gas_capacity = (
                load.mass_flow_kg_s * equipment.gas_cp_j_kg_k
            )
            mixed_average = (
                load.inlet_temperature_k
                - plant.hot_gas_to_wall_energy_j
                / (total_gas_capacity*load.duration_s)
            )
            extracted = (
                total_gas_capacity * load.duration_s
                * (load.inlet_temperature_k-mixed_average)
            )
            source_residual = extracted-plant.hot_gas_to_wall_energy_j
            combined_residual = (
                extracted-plant.cooler_energy_j-plant.net_shaft_energy_j
                -plant.wall_stored_energy_j
            )
            scale = max(abs(extracted), abs(plant.hot_gas_to_wall_energy_j),
                        abs(plant.net_shaft_energy_j),
                        abs(plant.wall_stored_energy_j), 1.)
            if not all(isfinite(v) for v in (
                mixed_start, mixed_end, mixed_average,
                source_residual, combined_residual
            )):
                raise DomainError("nonfinite bypass mixing/energy accounting")
            if (abs(source_residual)>1e-8*scale
                    or abs(combined_residual)>1e-7*scale):
                raise DomainError("source/mixed-stream/cycle energy mismatch")
            if min(mixed_start, mixed_end, mixed_average) < (
                equipment.minimum_stack_temperature_k - 1e-8
            ):
                raise DomainError("mixed exhaust stack below specified floor")
            record = BypassControlStep(
                time_start_s=time,
                time_end_s=plant.time_end_s,
                setpoint_temperature_k=setpoint_temperature_k,
                start_error_k=wall-setpoint_temperature_k,
                end_error_k=plant.final_wall_temperature_k-setpoint_temperature_k,
                bypass_fraction=applied,
                requested_fraction=request,
                unbounded_fraction=raw,
                applied_rate_fraction_s=(applied-position)/load.duration_s,
                integral_fraction_after=next_integral,
                active_gas_flow_kg_s=active_flow,
                diverted_gas_flow_kg_s=diverted_flow,
                mixed_gas_outlet_initial_k=mixed_start,
                mixed_gas_outlet_final_k=mixed_end,
                mixed_gas_outlet_mean_k=mixed_average,
                source_energy_residual_j=source_residual,
                combined_total_stream_residual_j=combined_residual,
                plant=plant
            )
        except DomainError as exc:
            raise DomainError(
                f"WP3 failed at interval {index}, t={time:.6g} s: {exc}"
            ) from exc
        steps.append(record)
        wall = plant.final_wall_temperature_k
        time = plant.time_end_s
        position = applied
        integral = next_integral
    if not steps:
        raise DomainError("WP3 requires one or more source intervals")
    return tuple(steps)


def control_performance(
    records: tuple[BypassControlStep, ...]
) -> ControlPerformance:
    """Sample endpoint RMSE and piecewise trapezoid |error| approximation."""
    if not records:
        raise DomainError("cannot compute control metrics for empty record")
    intervals = len(records)
    duration = records[-1].time_end_s-records[0].time_start_s
    if duration <= 0:
        raise DomainError("nonpositive control trajectory duration")
    sum_duration_error_sq = sum(
        (r.time_end_s-r.time_start_s)*r.end_error_k**2 for r in records
    )
    iae = sum(
        (r.time_end_s-r.time_start_s)
        * (abs(r.start_error_k)+abs(r.end_error_k))/2
        for r in records
    )
    wall_temp = [records[0].plant.initial_wall_temperature_k]
    wall_temp += [r.plant.final_wall_temperature_k for r in records]
    source_energy = sum(r.plant.hot_gas_to_wall_energy_j for r in records)
    shaft_energy = sum(r.plant.net_shaft_energy_j for r in records)
    cooler_energy = sum(r.plant.cooler_energy_j for r in records)
    storage_energy = sum(r.plant.wall_stored_energy_j for r in records)
    return ControlPerformance(
        interval_count=intervals,
        duration_s=duration,
        sample_endpoint_rmse_k=sqrt(sum_duration_error_sq/duration),
        absolute_error_trapezoid_k_s=iae,
        maximum_wall_temperature_k=max(wall_temp),
        minimum_wall_temperature_k=min(wall_temp),
        maximum_bypass_fraction=max(r.bypass_fraction for r in records),
        minimum_bypass_fraction=min(r.bypass_fraction for r in records),
        total_gas_to_wall_energy_j=source_energy,
        total_shaft_energy_j=shaft_energy,
        total_cooler_energy_j=cooler_energy,
        total_wall_storage_energy_j=storage_energy,
        total_energy_residual_j=(
            source_energy-shaft_energy-cooler_energy-storage_energy
        )
    )
