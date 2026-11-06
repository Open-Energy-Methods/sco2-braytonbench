"""Exactly integrated single solid-wall thermal control volume (G4-0/WP2a).

This is a standalone *analytical* lumped-capacitance fixture. Its fixed
conductances and prescribed reservoir temperatures do not constitute a
transient CO2 Brayton-cycle, CARBOSOLA equipment model or identified hardware.
"""
from __future__ import annotations

from dataclasses import dataclass
from math import expm1, isfinite
from typing import Iterable

from .properties import DomainError


def _finite_positive(label: str, value: float) -> None:
    if not isfinite(value) or value <= 0:
        raise DomainError(f"{label} must be positive and finite")


def _finite_kelvin(label: str, value: float) -> None:
    _finite_positive(label, value)


@dataclass(frozen=True)
class ThermalWall:
    """Lumped solid capacity [J/K] and two conductive paths [W/K].

    A path may have zero conductance, but both cannot be zero.
    """

    capacity_j_k: float
    hot_conductance_w_k: float
    cold_conductance_w_k: float

    def __post_init__(self) -> None:
        _finite_positive("wall heat capacity", self.capacity_j_k)
        for name, value in (
            ("hot conductance", self.hot_conductance_w_k),
            ("cold conductance", self.cold_conductance_w_k),
        ):
            if not isfinite(value) or value < 0:
                raise DomainError(f"{name} must be finite and nonnegative")
        if self.hot_conductance_w_k + self.cold_conductance_w_k <= 0:
            raise DomainError("at least one wall conductance must be positive")
        if not isfinite(self.hot_conductance_w_k + self.cold_conductance_w_k):
            raise DomainError("combined wall conductance must be finite")

    @property
    def time_constant_s(self) -> float:
        return self.capacity_j_k / (
            self.hot_conductance_w_k + self.cold_conductance_w_k
        )


@dataclass(frozen=True)
class ThermalStepInput:
    """Prescribed, constant thermal boundaries over an interval."""

    hot_temperature_k: float
    cold_temperature_k: float
    duration_s: float

    def __post_init__(self) -> None:
        _finite_kelvin("hot reservoir temperature", self.hot_temperature_k)
        _finite_kelvin("cold reservoir temperature", self.cold_temperature_k)
        _finite_positive("thermal step duration", self.duration_s)


@dataclass(frozen=True)
class ThermalStepResult:
    """Exact linear-model interval integrals. Energies signed in Joules."""

    time_start_s: float
    time_end_s: float
    initial_wall_temperature_k: float
    final_wall_temperature_k: float
    mean_wall_temperature_k: float
    equilibrium_temperature_k: float
    hot_energy_j: float
    cold_energy_j: float
    stored_energy_j: float
    energy_residual_j: float


def thermal_wall_step(
    wall: ThermalWall,
    initial_wall_temperature_k: float,
    boundaries: ThermalStepInput,
    *,
    time_start_s: float = 0.0,
) -> ThermalStepResult:
    """Integrate Cw*dTw/dt=Kh*(Th-Tw)-Kc*(Tw-Tc) over one interval.

    Unlike a forward-Euler update, this implements the **exact** exponential
    solution of the stated fixed-conductance, piecewise-constant ODE. The
    interval-mean temperature is used for integrated heat rates, rather
    than substituting an endpoint temperature into the first law.
    """
    _finite_kelvin("initial wall temperature", initial_wall_temperature_k)
    if not isfinite(time_start_s) or time_start_s < 0:
        raise DomainError("time_start_s must be finite and nonnegative")
    kh, kc = wall.hot_conductance_w_k, wall.cold_conductance_w_k
    kt = kh + kc
    dt = boundaries.duration_s
    t_hot, t_cold = boundaries.hot_temperature_k, boundaries.cold_temperature_k
    # Weighted average avoids constructing the dimensionally ill-scaled
    # power numerator in isolation; still check the finite result below.
    teq = (kh / kt) * t_hot + (kc / kt) * t_cold
    exponent = -(dt / wall.time_constant_s)
    decay_minus_one = expm1(exponent)
    delta_t = (teq - initial_wall_temperature_k) * (-decay_minus_one)
    final = initial_wall_temperature_k + delta_t
    # (1-exp(-a))/a = -expm1(-a)/a, well conditioned as a -> 0.
    a = -exponent
    mean_factor = -decay_minus_one / a if a > 0 else 1.0
    mean = teq + (initial_wall_temperature_k - teq) * mean_factor
    ehot = kh * (t_hot - mean) * dt
    ecold = kc * (mean - t_cold) * dt
    stored = wall.capacity_j_k * delta_t
    residual = (ehot - ecold) - stored
    result = ThermalStepResult(
        time_start_s=time_start_s,
        time_end_s=time_start_s + dt,
        initial_wall_temperature_k=initial_wall_temperature_k,
        final_wall_temperature_k=final,
        mean_wall_temperature_k=mean,
        equilibrium_temperature_k=teq,
        hot_energy_j=ehot,
        cold_energy_j=ecold,
        stored_energy_j=stored,
        energy_residual_j=residual,
    )
    if not all(isfinite(v) for v in vars(result).values()):
        raise DomainError("nonfinite thermal control-volume result")
    if result.time_end_s <= result.time_start_s:
        raise DomainError("time interval cannot advance at available precision")
    return result


def simulate_thermal_wall(
    wall: ThermalWall,
    initial_wall_temperature_k: float,
    profile: Iterable[ThermalStepInput],
) -> tuple[ThermalStepResult, ...]:
    """Return every exact step of a prescribed piecewise-constant profile."""
    current = initial_wall_temperature_k
    time = 0.0
    records: list[ThermalStepResult] = []
    for boundaries in profile:
        record = thermal_wall_step(
            wall, current, boundaries, time_start_s=time
        )
        records.append(record)
        current, time = record.final_wall_temperature_k, record.time_end_s
    if not records:
        raise DomainError("thermal profile must contain at least one interval")
    return tuple(records)
