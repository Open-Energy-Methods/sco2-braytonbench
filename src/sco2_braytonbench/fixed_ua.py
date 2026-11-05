"""Installed-UA coupled recuperated Brayton cycle and finite exhaust-gas heater.

This solves turbine-inlet temperature T4 as an unknown, not a chosen
screening input: for a given cycle inlet/pressure/mass-flow state, fixed
recuperator UA, gas flow and inlet T, find the point where the entire
heater's REQUIRED counterflow UA equals the INSTALLED UA.

Conservation of energy is enforced on both sides. Root bracketing is
conservative: multiple detected roots, an unbracketed solution or an
invalid (pinch/stack/exergy) interval is reported, not silently fitted.
No bypass or partially-used heat-exchanger area is assumed.

Still a reduced six-state steady-state model using fixed pressure losses,
constant-cp exhaust gas, constant turbomachinery efficiencies and an
imposed compressor inlet state. NOT a CARBOSOLA rig model, MK2014
quantitative reproduction, or a dynamic solution.
"""
from __future__ import annotations

from dataclasses import dataclass, replace
from math import isfinite

from .cycle import CycleInputs
from .properties import DomainError, Properties
from .whr import (
    WHRPoint, WasteGasSource, PlantDesignLimits, evaluate_whr_design
)


@dataclass(frozen=True)
class FixedUAResult:
    point: WHRPoint
    installed_heater_ua_w_k: float
    calculated_heater_ua_w_k: float
    ua_residual_w_k: float
    ua_residual_relative: float
    iterations: int
    evaluations: int
    scanned_feasible_points: int
    root_bracket_k: tuple[float, float]

    @property
    def turbine_inlet_temperature_k(self) -> float:
        return self.point.inputs.t4_k

    @property
    def stack_temperature_k(self) -> float:
        return self.point.heater.gas_out_k


def solve_fixed_ua_whr(
    props: Properties,
    base_inputs: CycleInputs,
    source: WasteGasSource,
    *,
    installed_heater_ua_w_k: float,
    turbine_inlet_bounds_k: tuple[float, float],
    limits: PlantDesignLimits | None = None,
    scan_intervals: int = 12,
    max_iterations: int = 32,
    tolerance_ua_relative: float = 1e-4,
    tolerance_temperature_k: float = 0.03,
) -> FixedUAResult:
    """Solve coupled heater + cycle for physical equality UA_req == UA_inst.

    The base_inputs.t4_k field is IGNORED; only all other cycle values
    (including compressor inlet T, both P, mdot, eta and recup UA)
    are fixed. The externally selected turbine-temperature search
    interval must be documented in any reported results.

    A sign-changing pair of adjacent *feasible* scan points brackets
    a candidate root. No extrapolation over invalid domains is allowed.
    Bisection requires both the temperature and UA tolerances to be met.
    More than one detected root is an explicit error.
    """
    if not (isfinite(installed_heater_ua_w_k)
            and 0 < installed_heater_ua_w_k <= source.maximum_heater_ua_w_k):
        raise DomainError(
            "installed heater UA must be positive and within source sizing allowance"
        )
    if base_inputs.recuperator_effectiveness is not None:
        raise DomainError("fixed-UA heater requires finite-UA recuperator mode")
    if base_inputs.recuperator_ua_w_k is None:
        raise DomainError("recuperator installed UA must be specified")
    if len(turbine_inlet_bounds_k) != 2:
        raise DomainError("specify two turbine inlet temperature bounds")
    t_lo, t_hi = turbine_inlet_bounds_k
    if not all(isfinite(t) for t in (t_lo, t_hi)) or t_hi <= t_lo or t_lo <= 0:
        raise DomainError("invalid turbine inlet temperature interval")
    if t_hi >= source.inlet_temperature_k-source.minimum_heater_approach_k:
        raise DomainError(
            "upper T4 search bound must satisfy the exhaust hot-end approach"
        )
    if (scan_intervals < 2 or max_iterations < 1
            or not isfinite(tolerance_ua_relative)
            or not 0 < tolerance_ua_relative <= 0.05
            or not isfinite(tolerance_temperature_k)
            or tolerance_temperature_k <= 0):
        raise DomainError("invalid coupled solver numerical tolerances")

    calls = 0
    cache: dict[float, tuple[float, WHRPoint] | None] = {}
    failures: list[tuple[float,str]] = []

    def at(t4: float) -> tuple[float, WHRPoint] | None:
        nonlocal calls
        if t4 in cache:
            return cache[t4]
        calls += 1
        try:
            candidate = replace(base_inputs, t4_k=t4)
            point = evaluate_whr_design(
                props, candidate, source, limits=limits,
                enforce_heater_ua_cap=False,
            )
            residual = (
                point.heater.required_ua_w_k - installed_heater_ua_w_k
            )
            if not isfinite(residual):
                raise DomainError("nonfinite heater UA residual")
            cache[t4] = (residual, point)
        except (DomainError, ValueError, OverflowError) as exc:
            cache[t4] = None
            failures.append((t4,str(exc)))
        return cache[t4]

    def result(t: float, bracket: tuple[float,float],
               iterations: int) -> FixedUAResult:
        evaluated = at(t)
        if evaluated is None:
            raise DomainError("coupled solver final point outside valid domain")
        residual, point = evaluated
        rel = abs(residual) / installed_heater_ua_w_k
        if rel > tolerance_ua_relative:
            raise DomainError(
                f"heater UA equality not resolved: relative residual {rel:.3g}"
            )
        return FixedUAResult(
            point=point,
            installed_heater_ua_w_k=installed_heater_ua_w_k,
            calculated_heater_ua_w_k=point.heater.required_ua_w_k,
            ua_residual_w_k=residual,
            ua_residual_relative=rel,
            iterations=iterations,
            evaluations=calls,
            scanned_feasible_points=sum(
                v is not None for v in scan.values()
            ),
            root_bracket_k=bracket,
        )

    scan = {
        t_lo + (t_hi-t_lo)*i/scan_intervals: None
        for i in range(scan_intervals+1)
    }
    for t in scan:
        scan[t] = at(t)
    good = [(t,v) for t,v in scan.items() if v is not None]
    if not good:
        raise DomainError(
            "no feasible coupled cycle/heater points within T4 search interval"
        )

    ua_tol = tolerance_ua_relative * installed_heater_ua_w_k
    exact = [(t, v) for t,v in good if abs(v[0]) <= ua_tol]
    # A scan point with a near-zero UA residual is a valid root candidate,
    # but multiple separated near-zeros or crossing intervals are ambiguous.
    brackets: list[tuple[float, float]] = []
    ts = list(scan)
    for left,right in zip(ts[:-1],ts[1:]):
        lv, rv = scan[left], scan[right]
        if lv is not None and rv is not None and lv[0]*rv[0] < 0:
            brackets.append((left,right))
    if len(brackets)>1:
        raise DomainError(
            f"{len(brackets)} distinct sign-changing UA roots found: "
            "operating point not uniquely identified"
        )
    if exact and not brackets:
        # Prefer the lowest residual. Do not conflate multiple separated
        # nearly-matching observations with a verified unique root.
        if len(exact)>1 and (
                max(t for t,_ in exact)-min(t for t,_ in exact)
                > (t_hi-t_lo)/scan_intervals):
            raise DomainError("multiple separated near-zero UA solutions")
        t = min(exact, key=lambda pair: abs(pair[1][0]))[0]
        return result(t, (t,t), 0)
    if not brackets:
        residuals=[v[0] for _,v in good]
        raise DomainError(
            f"installed heater UA not bracketed within feasible T4 states "
            f"({len(good)}/{len(scan)} feasible); "
            f"feasible UA residual range "
            f"[{min(residuals):.6g}, {max(residuals):.6g}] W/K"
        )

    lo,hi=brackets[0]
    # Bisection is only allowed within the continuous feasible interval.
    rlo=scan[lo][0]  # type: ignore[index]
    rhi=scan[hi][0]  # type: ignore[index]
    best=None
    for iteration in range(1,max_iterations+1):
        mid=(lo+hi)/2
        state=at(mid)
        if state is None:
            raise DomainError(
                "failed physical constraint inside coupled root bracket: "
                "continuous feasible branch not established"
            )
        residual,_=state
        best=mid
        if rlo*residual <= 0:
            hi=mid
            rhi=residual
        else:
            lo=mid
            rlo=residual
        if abs(residual)<=ua_tol and hi-lo<=tolerance_temperature_k:
            return result(mid,(lo,hi),iteration)
    if best is not None:
        residual=at(best)[0]  # type: ignore[index]
        raise DomainError(
            f"fixed-UA bisection not converged in {max_iterations} steps; "
            f"remaining bracket {hi-lo:.6g} K and residual "
            f"{residual:.6g} W/K"
        )
    raise DomainError("fixed-UA bisection terminated without a candidate")
