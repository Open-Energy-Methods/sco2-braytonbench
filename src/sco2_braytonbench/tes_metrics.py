"""Independent sensible packed-bed performance metrics (synthetic scope).

Storage energy, reversible exergy relative to a constant ambient, and
geometric thermocline-width diagnostics are deliberately separated from
numerical conservation and from measured operating efficiency.
"""
from __future__ import annotations
from dataclasses import dataclass
import math

from .thermal_storage import PackedBedSpec, PackedBedState, _finite


@dataclass(frozen=True)
class TESPerformanceMetrics:
    design_solid_capacity_j: float
    design_fluid_capacity_j: float
    solid_sensible_energy_j: float
    fluid_sensible_energy_j: float
    total_reversible_exergy_j: float
    solid_exergy_j: float
    fluid_exergy_j: float
    thermocline_width_m: float | None
    thermocline_profile_monotone: bool


def _sensible_exergy(capacity_j_k: float, temperature_k: float,
                     ambient_k: float) -> float:
    """Constant-cp availability C*[(T-Ta)-Ta*ln(T/Ta)]."""
    delta = (temperature_k - ambient_k) / ambient_k
    return capacity_j_k * ((temperature_k - ambient_k)
                           - ambient_k * math.log1p(delta))


def flow_exergy_difference_w(
    mass_flow_kg_s: float, cp_j_kg_k: float,
    inlet_k: float, outlet_k: float, ambient_k: float
) -> float:
    """Stream exergy flow difference, no pressure/chemical exergy."""
    mdot = _finite("mass_flow_kg_s", mass_flow_kg_s)
    if mdot < 0:
        raise ValueError("provide nonnegative flow magnitude, not flow sign")
    cp = _finite("cp_j_kg_k", cp_j_kg_k, positive=True)
    inlet = _finite("inlet_k", inlet_k, positive=True)
    outlet = _finite("outlet_k", outlet_k, positive=True)
    ambient = _finite("ambient_k", ambient_k, positive=True)
    return mdot * cp * (
        (inlet - outlet) - ambient * math.log(inlet / outlet)
    )


def _crossing_coordinate(xs: list[float], thetas: list[float], level: float) -> float | None:
    for i in range(1, len(xs)):
        a, b = thetas[i-1], thetas[i]
        if (a-level)*(b-level) <= 0 and a != b:
            t = (level-a)/(b-a)
            return xs[i-1] + t*(xs[i]-xs[i-1])
        if a == level:
            return xs[i-1]
    if thetas and thetas[-1] == level:
        return xs[-1]
    return None


def thermocline_width_m(
    spec: PackedBedSpec, state: PackedBedState, *,
    cold_k: float, hot_k: float, lower_fraction: float = .1,
    upper_fraction: float = .9
) -> tuple[float | None, bool]:
    """10–90% solid-temperature width, only if full monotone crossings exist.

    A single uniform, non-monotone, or insufficiently charged profile has
    *undefined* width (None); no fabricated thin thermocline is returned.
    """
    state.validate(spec)
    cold = _finite("cold_k", cold_k, positive=True)
    hot = _finite("hot_k", hot_k, positive=True)
    low = _finite("lower_fraction", lower_fraction)
    high = _finite("upper_fraction", upper_fraction)
    if hot <= cold or not 0 <= low < high <= 1:
        raise ValueError("require hot>cold and 0<=lower<upper<=1")
    theta=[(t-cold)/(hot-cold) for t in state.solid_k]
    if len(theta) < 2:
        return None, True
    decreasing=all(a+1e-12 >= b for a,b in zip(theta,theta[1:]))
    increasing=all(a-1e-12 <= b for a,b in zip(theta,theta[1:]))
    monotone=decreasing or increasing
    if not monotone:
        return None, False
    xs=[(i+.5)*spec.cell_dx_m for i in range(spec.n_cells)]
    lo=_crossing_coordinate(xs,theta,low)
    hi=_crossing_coordinate(xs,theta,high)
    if lo is None or hi is None:
        return None, True
    return abs(hi-lo), True


def evaluate_tes_performance(
    spec: PackedBedSpec,
    state: PackedBedState,
    *,
    cold_k: float,
    hot_k: float,
    ambient_k: float
) -> TESPerformanceMetrics:
    """Geometry/temperature-based performance, not plant cycling data."""
    state.validate(spec)
    cold=_finite("cold_k",cold_k,positive=True)
    hot=_finite("hot_k",hot_k,positive=True)
    ambient=_finite("ambient_k",ambient_k,positive=True)
    if hot<=cold:
        raise ValueError("hot_k must exceed cold_k")
    cf,cs=spec.fluid_cell_capacity_j_k,spec.solid_cell_capacity_j_k
    sx=math.fsum(_sensible_exergy(cs,t,ambient) for t in state.solid_k)
    fx=math.fsum(_sensible_exergy(cf,t,ambient) for t in state.fluid_k)
    width,monotone=thermocline_width_m(
        spec,state,cold_k=cold,hot_k=hot
    )
    return TESPerformanceMetrics(
        design_solid_capacity_j=spec.total_solid_capacity_j_k*(hot-cold),
        design_fluid_capacity_j=spec.total_fluid_capacity_j_k*(hot-cold),
        solid_sensible_energy_j=math.fsum(cs*(t-cold) for t in state.solid_k),
        fluid_sensible_energy_j=math.fsum(cf*(t-cold) for t in state.fluid_k),
        total_reversible_exergy_j=sx+fx,
        solid_exergy_j=sx, fluid_exergy_j=fx,
        thermocline_width_m=width, thermocline_profile_monotone=monotone,
    )
