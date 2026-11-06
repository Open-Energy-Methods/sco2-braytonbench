"""WP2b: finite exhaust stream -> stored wall -> quasi-steady Brayton heater.

The **only dynamic inventory** is a lumped solid wall with Cw [J/K].
Each RK4 stage enforces two separate installed-UA heat-transfer paths:
  gas in -> gas out (finite sensible-heat stream, isothermal wall)
  wall -> CO2 state 3 to 4 (segmented, implicit turbine inlet T4)
The existing six-state `solve_cycle` is solved at EACH dynamic stage.
Crucially, its heater duty is the wall-to-CO2 heat transfer, NOT an
additional gas-to-CO2 heater counted alongside the wall.

This is *not* a CO2 mass/inventory dynamic model, compressor/turbine map,
G3.2 two-UA hot/cold cycle, or CARBOSOLA digital twin. Compressor inlet
T1, pressures, flow, pressure losses and turbomachinery efficiencies are
prescribed and remain algebraic/quasi-steady.
"""
from __future__ import annotations

from dataclasses import dataclass, replace
from math import expm1, isfinite
from typing import Iterable

from .cycle import CycleInputs, CycleResult, solve_cycle
from .exchangers import _lmtd
from .properties import DomainError, Properties


def _positive(name: str, value: float) -> None:
    if (isinstance(value, bool) or not isinstance(value, (int, float))
            or not isfinite(value) or value <= 0):
        raise DomainError(f"{name} must be positive and finite")


def _nonnegative(name: str, value: float) -> None:
    if (isinstance(value, bool) or not isinstance(value, (int, float))
            or not isfinite(value) or value < 0):
        raise DomainError(f"{name} must be finite and nonnegative")


@dataclass(frozen=True)
class WallCycleEquipment:
    """Hypothetical fixed equipment; every quantity must be identified to use physically."""

    wall_capacity_j_k: float
    gas_to_wall_ua_w_k: float
    wall_to_co2_ua_w_k: float
    gas_cp_j_kg_k: float
    minimum_stack_temperature_k: float
    t4_bounds_k: tuple[float, float]
    minimum_wall_co2_approach_k: float = 2.
    minimum_gas_wall_approach_k: float = 1.
    co2_heater_segments: int = 8
    root_scan_intervals: int = 7
    root_max_iterations: int = 32
    root_ua_tolerance_relative: float = 1e-4
    root_temperature_tolerance_k: float = 0.02
    maximum_step_fraction: float = 0.4

    def __post_init__(self) -> None:
        for name in ("wall_capacity_j_k", "gas_to_wall_ua_w_k",
                     "wall_to_co2_ua_w_k", "gas_cp_j_kg_k",
                     "minimum_stack_temperature_k",
                     "root_ua_tolerance_relative",
                     "root_temperature_tolerance_k", "maximum_step_fraction"):
            _positive(name, getattr(self, name))
        for name in ("minimum_wall_co2_approach_k",
                     "minimum_gas_wall_approach_k"):
            _nonnegative(name, getattr(self, name))
        if len(self.t4_bounds_k) != 2:
            raise DomainError("turbine-inlet temperature bounds require two values")
        for value in self.t4_bounds_k:
            _positive("turbine-inlet temperature bound", value)
        if self.t4_bounds_k[1] <= self.t4_bounds_k[0]:
            raise DomainError("turbine-inlet temperature bounds must ascend")
        for name, minimum in (("co2_heater_segments", 3),
                              ("root_scan_intervals", 3),
                              ("root_max_iterations", 1)):
            value = getattr(self, name)
            if isinstance(value, bool) or not isinstance(value, int) or value < minimum:
                raise DomainError(f"{name} must be integer >= {minimum}")
        if self.root_ua_tolerance_relative > 0.01:
            raise DomainError("root UA relative tolerance must be <= 0.01")
        if self.maximum_step_fraction > 1:
            raise DomainError("maximum_step_fraction must be <= 1")


@dataclass(frozen=True)
class FiniteGasLoad:
    """Source temperature/flow held constant during one integration interval."""

    inlet_temperature_k: float
    mass_flow_kg_s: float
    duration_s: float

    def __post_init__(self) -> None:
        for name in ("inlet_temperature_k", "mass_flow_kg_s", "duration_s"):
            _positive(name, getattr(self, name))


@dataclass(frozen=True)
class WallCycleInstant:
    """Algebraically solved source and cycle at a specified dynamic wall T."""

    wall_temperature_k: float
    hot_gas_outlet_temperature_k: float
    hot_to_wall_w: float
    wall_to_co2_w: float
    wall_net_heating_w: float
    co2_wall_required_ua_w_k: float
    co2_wall_min_approach_k: float
    gas_wall_outlet_approach_k: float
    cycle: CycleResult

    @property
    def turbine_inlet_temperature_k(self) -> float:
        return self.cycle.states[3].t


@dataclass(frozen=True)
class WallCycleInterval:
    """RK4 time-integrated energy ledger for one piecewise-constant load."""

    time_start_s: float
    time_end_s: float
    input_load: FiniteGasLoad
    initial_wall_temperature_k: float
    final_wall_temperature_k: float
    initial: WallCycleInstant
    final: WallCycleInstant
    hot_gas_to_wall_energy_j: float
    wall_to_co2_energy_j: float
    cooler_energy_j: float
    net_shaft_energy_j: float
    wall_stored_energy_j: float
    wall_energy_residual_j: float
    combined_gas_cycle_wall_residual_j: float


def _co2_wall_rating(
    props: Properties, cycle: CycleResult, wall_temperature_k: float,
    mass_flow_kg_s: float, n: int, minimum_approach_k: float,
) -> tuple[float, float]:
    """Installed isothermal-wall UA required by the actual cycle heater duty.

    CO2 heating path is state 3 -> state 4. Pressure and specific enthalpy
    are linearly interpolated *within* the CO2 wall heater. No second
    gas-to-CO2 heater or heat duty is introduced here.
    """
    s3, s4 = cycle.states[2], cycle.states[3]
    q = cycle.heater_w
    if q <= 0 or s4.p > s3.p:
        raise DomainError("wall-to-CO2 heater duty or pressure is infeasible")
    approaches = []
    for i in range(n + 1):
        x = i / n
        p = s3.p + (s4.p - s3.p) * x
        h = s3.h + (s4.h - s3.h) * x
        t = props.ph(p, h).t
        approaches.append(wall_temperature_k - t)
    d_min = min(approaches)
    if d_min < minimum_approach_k or d_min <= 0:
        raise DomainError("isothermal CO2 wall heating violates minimum approach")
    ua = sum((q / n) / _lmtd(a, b)
             for a, b in zip(approaches[:-1], approaches[1:]))
    if not isfinite(ua) or ua <= 0:
        raise DomainError("nonfinite isothermal wall heater UA")
    return ua, d_min


def solve_wall_cycle_instant(
    props: Properties,
    base_cycle: CycleInputs,
    equipment: WallCycleEquipment,
    wall_temperature_k: float,
    load: FiniteGasLoad,
) -> WallCycleInstant:
    """Solve fixed-UA CO2 heater and finite-gas exchange at a known wall T.

    No measured or invented wall-temperature input is used for a cycle
    prediction in this **synthetic** model: wall T is the *integrated
    dynamic state*, and T4 is an implicit algebraic output.
    """
    _positive("wall temperature", wall_temperature_k)
    if (base_cycle.recuperator_ua_w_k is None
            or base_cycle.recuperator_effectiveness is not None):
        raise DomainError("WP2b requires explicit installed recuperator UA")
    if load.inlet_temperature_k <= wall_temperature_k:
        raise DomainError("hot-gas inlet must exceed wall temperature")
    if load.inlet_temperature_k <= equipment.minimum_stack_temperature_k:
        raise DomainError("gas inlet must exceed the declared stack minimum")

    # A finite sensible gas stream exchanging with an isothermal wall.
    c_g = load.mass_flow_kg_s * equipment.gas_cp_j_kg_k
    fraction = -expm1(-equipment.gas_to_wall_ua_w_k / c_g)
    q_hot = c_g * (load.inlet_temperature_k - wall_temperature_k) * fraction
    t_gas_out = load.inlet_temperature_k - q_hot / c_g
    if (t_gas_out < equipment.minimum_stack_temperature_k
            or t_gas_out - wall_temperature_k
            < equipment.minimum_gas_wall_approach_k):
        raise DomainError("gas-wall approach or stack floor violated")
    if abs(c_g * (load.inlet_temperature_k - t_gas_out) - q_hot) > (
        1e-8 * max(q_hot, 1.)
    ):
        raise DomainError("finite hot-gas first-law balance failed")

    lo, hi = equipment.t4_bounds_k
    hi = min(hi, wall_temperature_k - equipment.minimum_wall_co2_approach_k)
    if hi <= lo:
        raise DomainError("wall too cold to admit a turbine inlet in declared bounds")

    cache: dict[float, tuple[float, CycleResult, float, float] | None] = {}

    def at(t4: float) -> tuple[float, CycleResult, float, float] | None:
        if t4 not in cache:
            try:
                cycle = solve_cycle(props, replace(base_cycle, t4_k=t4))
                if cycle.net_w <= 0:
                    raise DomainError("nonpositive net shaft work")
                ua, pinch = _co2_wall_rating(
                    props, cycle, wall_temperature_k, base_cycle.mdot_kg_s,
                    equipment.co2_heater_segments,
                    equipment.minimum_wall_co2_approach_k,
                )
                cache[t4] = (ua - equipment.wall_to_co2_ua_w_k, cycle, ua, pinch)
            except (DomainError, ValueError, OverflowError):
                cache[t4] = None
        return cache[t4]

    samples = [lo + (hi - lo) * i / equipment.root_scan_intervals
               for i in range(equipment.root_scan_intervals + 1)]
    values = [(t, at(t)) for t in samples]
    feasible = [(t, v) for t, v in values if v is not None]
    if not feasible:
        raise DomainError("no feasible cycle state in wall-heater T4 bounds")
    brackets = []
    for (left, a), (right, b) in zip(values[:-1], values[1:]):
        if a is not None and b is not None and a[0] * b[0] < 0:
            brackets.append((left, right))
    if len(brackets) > 1:
        raise DomainError("multiple detected wall-heater UA roots")
    tolerance = (equipment.wall_to_co2_ua_w_k
                 * equipment.root_ua_tolerance_relative)
    near = [(t, v) for t, v in feasible if abs(v[0]) <= tolerance]
    if not brackets:
        if not near:
            observed = [v[0] for _, v in feasible]
            raise DomainError(
                "wall-to-CO2 installed UA not bracketed; sampled residual "
                f"range [{min(observed):.6g}, {max(observed):.6g}] W/K"
            )
        if len(near) > 1:
            raise DomainError("multiple near-zero wall heater states")
        t_solution, v = near[0]
    else:
        left, right = brackets[0]
        lv = at(left)
        assert lv is not None
        fleft = lv[0]
        v = None
        t_solution = float("nan")
        for _ in range(equipment.root_max_iterations):
            mid = (left + right) / 2
            data = at(mid)
            if data is None:
                raise DomainError("wall-heater root crosses infeasible cycle state")
            if fleft * data[0] <= 0:
                right = mid
            else:
                left, fleft = mid, data[0]
            if (abs(data[0]) <= tolerance
                    and right - left <= equipment.root_temperature_tolerance_k):
                t_solution, v = mid, data
                break
        if v is None:
            raise DomainError("wall-to-CO2 UA root did not converge")
    if v is None or abs(v[0]) > tolerance:
        raise DomainError("wall-to-CO2 UA equality failed")
    _, cycle, ua, pinch = v
    return WallCycleInstant(
        wall_temperature_k=wall_temperature_k,
        hot_gas_outlet_temperature_k=t_gas_out,
        hot_to_wall_w=q_hot,
        wall_to_co2_w=cycle.heater_w,
        wall_net_heating_w=q_hot - cycle.heater_w,
        co2_wall_required_ua_w_k=ua,
        co2_wall_min_approach_k=pinch,
        gas_wall_outlet_approach_k=t_gas_out-wall_temperature_k,
        cycle=cycle,
    )


def wall_cycle_step(
    props: Properties,
    base_cycle: CycleInputs,
    equipment: WallCycleEquipment,
    initial_wall_temperature_k: float,
    load: FiniteGasLoad,
    *,
    time_start_s: float = 0.,
) -> WallCycleInterval:
    """Fixed-step classical RK4, with matching flux quadrature for energies.

    RK4's stored energy is matched to the same stage-weighted heat fluxes:
    E_hot - E_wall_to_CO2 == Cw*(T_final-T_initial) within floating precision.
    This does not prove convergence of the ODE: compare shorter steps.
    """
    _positive("initial wall temperature", initial_wall_temperature_k)
    _nonnegative("time_start_s", time_start_s)
    if not isfinite(time_start_s + load.duration_s) or (
        time_start_s + load.duration_s <= time_start_s
    ):
        raise DomainError("time interval cannot be represented")
    c_g = load.mass_flow_kg_s * equipment.gas_cp_j_kg_k
    hg = c_g * (-expm1(-equipment.gas_to_wall_ua_w_k / c_g))
    tau_bound = equipment.wall_capacity_j_k / (
        hg + equipment.wall_to_co2_ua_w_k
    )
    if load.duration_s > equipment.maximum_step_fraction * tau_bound:
        raise DomainError(
            "RK4 duration exceeds conservative local thermal time-step bound; "
            "subdivide the load interval"
        )
    c_wall = equipment.wall_capacity_j_k
    dt = load.duration_s
    a = solve_wall_cycle_instant(
        props, base_cycle, equipment, initial_wall_temperature_k, load)
    b = solve_wall_cycle_instant(
        props, base_cycle, equipment,
        initial_wall_temperature_k + dt * a.wall_net_heating_w / (2 * c_wall),
        load)
    c = solve_wall_cycle_instant(
        props, base_cycle, equipment,
        initial_wall_temperature_k + dt * b.wall_net_heating_w / (2 * c_wall),
        load)
    d = solve_wall_cycle_instant(
        props, base_cycle, equipment,
        initial_wall_temperature_k + dt * c.wall_net_heating_w / c_wall,
        load)
    stages = (a, b, c, d)
    weights = (1, 2, 2, 1)
    def integrate(fn) -> float:
        return dt * sum(w * fn(s) for w, s in zip(weights, stages)) / 6

    ehot = integrate(lambda s: s.hot_to_wall_w)
    eco2 = integrate(lambda s: s.wall_to_co2_w)
    ecool = integrate(lambda s: s.cycle.cooler_w)
    enet = integrate(lambda s: s.cycle.net_w)
    stored = ehot - eco2
    t_new = initial_wall_temperature_k + stored / c_wall
    end = solve_wall_cycle_instant(props, base_cycle, equipment, t_new, load)
    residual_wall = ehot - eco2 - c_wall * (t_new - initial_wall_temperature_k)
    residual_whole = ehot - ecool - enet - c_wall * (
        t_new - initial_wall_temperature_k
    )
    quantities = (ehot, eco2, ecool, enet, stored,
                  residual_wall, residual_whole, t_new)
    if not all(isfinite(v) for v in quantities):
        raise DomainError("nonfinite WP2b integrated cycle/wall result")
    scale = max(abs(ehot), abs(eco2), abs(stored), abs(ecool), abs(enet), 1.)
    if abs(residual_wall) > scale * 1e-8:
        raise DomainError("WP2b wall integral first-law residual exceeded bound")
    if abs(residual_whole) > scale * 1e-7:
        raise DomainError("WP2b combined gas-wall-cycle first law failed")
    return WallCycleInterval(
        time_start_s=time_start_s,
        time_end_s=time_start_s+dt,
        input_load=load,
        initial_wall_temperature_k=initial_wall_temperature_k,
        final_wall_temperature_k=t_new,
        initial=a, final=end,
        hot_gas_to_wall_energy_j=ehot,
        wall_to_co2_energy_j=eco2,
        cooler_energy_j=ecool,
        net_shaft_energy_j=enet,
        wall_stored_energy_j=c_wall*(t_new-initial_wall_temperature_k),
        wall_energy_residual_j=residual_wall,
        combined_gas_cycle_wall_residual_j=residual_whole,
    )


def simulate_wall_coupled_cycle(
    props: Properties,
    base_cycle: CycleInputs,
    equipment: WallCycleEquipment,
    initial_wall_temperature_k: float,
    loads: Iterable[FiniteGasLoad],
) -> tuple[WallCycleInterval, ...]:
    """Piecewise load scenarios, each time slice solved as genuine stored energy."""
    t = 0.
    wall = initial_wall_temperature_k
    records: list[WallCycleInterval] = []
    for index, load in enumerate(loads):
        try:
            record = wall_cycle_step(
                props, base_cycle, equipment, wall, load, time_start_s=t
            )
        except DomainError as exc:
            raise DomainError(
                f"WP2b failed at interval {index}, t={t:.6g} s: {exc}"
            ) from exc
        records.append(record)
        wall, t = record.final_wall_temperature_k, record.time_end_s
    if not records:
        raise DomainError("WP2b load profile must have at least one interval")
    return tuple(records)
