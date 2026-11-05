"""Nested heater/cooler UA equality for finite hot and cold sensible streams.

Input: source and cooler inlet streams, installed exchanger UAs,
CO2 mass flow and pressure boundaries, installed recuperator UA.
Unknowns: T1 (compressor inlet / CO2 cooler outlet) and T4
(turbine inlet / CO2 heater outlet), with both stream outlet Ts.

At each T1, the existing G3.1 heater solver determines T4; the
cooler is rated against its fixed installed UA, then a safe outer
T1 bracket is bisected. This is intentionally conservative and
computationally expensive. It neither simulates an inventory nor
claims a plant-calibrated off-design correlation.
"""
from __future__ import annotations
from dataclasses import dataclass, replace
from math import isfinite

from .cooler import CoolerSink, CoolerRating, rate_cooler
from .cycle import CycleInputs
from .fixed_ua import FixedUAResult, solve_fixed_ua_whr
from .offdesign import FlowScaling
from .properties import DomainError, Properties
from .whr import WasteGasSource, PlantDesignLimits


@dataclass(frozen=True)
class CoupledPlantResult:
    heater: FixedUAResult
    cooler: CoolerRating
    installed_cooler_ua_w_k: float
    cooler_ua_residual_w_k: float
    cooler_ua_residual_relative: float
    outer_iterations: int
    outer_evaluations: int
    scanned_feasible_points: int
    t1_bracket_k: tuple[float,float]
    # If provided, the source equipment parameters have been flow-scaled.
    equipment_flow_scaled: bool

    @property
    def compressor_inlet_temperature_k(self)->float:
        return self.heater.point.inputs.t1_k

    @property
    def turbine_inlet_temperature_k(self)->float:
        return self.heater.turbine_inlet_temperature_k

    @property
    def net_shaft_power_w(self)->float:
        return self.heater.point.net_shaft_power_w


def solve_coupled_plant(
    props: Properties,
    base_inputs: CycleInputs,
    hot_source: WasteGasSource,
    cold_sink: CoolerSink,
    *,
    installed_heater_ua_w_k: float,
    t1_bounds_k: tuple[float,float],
    t4_bounds_k: tuple[float,float],
    limits: PlantDesignLimits | None = None,
    equipment_flow_law: FlowScaling | None = None,
    outer_scan_intervals: int = 4,
    outer_max_iterations: int = 14,
    cooler_ua_tolerance_relative: float = 3e-4,
    t1_tolerance_k: float = 0.07,
    inner_scan_intervals: int = 5,
    inner_max_iterations: int = 20,
    inner_ua_tolerance_relative: float = 1e-4,
    inner_t4_tolerance_k: float = 0.04,
) -> CoupledPlantResult:
    """Solve BOTH fixed-UA equations; never replace either with an inequality.

    The base_inputs.t1_k and .t4_k trial temperatures are ignored.
    More than one sampled distinct feasible root, an unbracketed
    interval, infeasible midpoint, or insufficient convergence
    leads to an explicit DomainError. Finite scanning does not
    mathematically prove global uniqueness; report interval and
    resolution with every result.

    A FlowScaling law is an independent optional toy scenario,
    applied once at mass flow before the thermodynamic root solve.
    """
    if not all(isfinite(x) for x in (*t1_bounds_k,*t4_bounds_k)):
        raise DomainError("nonfinite coupled temperature search bounds")
    lo_t1,hi_t1=t1_bounds_k
    if (lo_t1<=0 or hi_t1<=lo_t1 or
        lo_t1<=cold_sink.inlet_temperature_k+cold_sink.minimum_approach_k):
        raise DomainError("cooler outlet T1 search must exceed cold stream inlet approach")
    if (outer_scan_intervals<2 or outer_max_iterations<1 or
        not isfinite(cooler_ua_tolerance_relative) or
        not 0<cooler_ua_tolerance_relative<=.05 or
        not isfinite(t1_tolerance_k) or t1_tolerance_k<=0):
        raise DomainError("invalid outer cooler root settings")
    if not isfinite(installed_heater_ua_w_k) or installed_heater_ua_w_k<=0:
        raise DomainError("invalid installed heater UA")

    inputs=(equipment_flow_law.at_flow(base_inputs,base_inputs.mdot_kg_s)
            if equipment_flow_law is not None else base_inputs)
    cache: dict[float,tuple[float,FixedUAResult,CoolerRating]|None]={}
    n_calls=0

    def state(t1:float)->tuple[float,FixedUAResult,CoolerRating]|None:
        nonlocal n_calls
        if t1 in cache:
            return cache[t1]
        n_calls+=1
        try:
            heater=solve_fixed_ua_whr(
                props,replace(inputs,t1_k=t1),hot_source,
                installed_heater_ua_w_k=installed_heater_ua_w_k,
                turbine_inlet_bounds_k=t4_bounds_k,limits=limits,
                scan_intervals=inner_scan_intervals,
                max_iterations=inner_max_iterations,
                tolerance_ua_relative=inner_ua_tolerance_relative,
                tolerance_temperature_k=inner_t4_tolerance_k,
            )
            c=heater.point.cycle
            rating=rate_cooler(
                props,c.states[5],c.states[0],inputs.mdot_kg_s,cold_sink)
            residual=rating.required_ua_w_k-cold_sink.installed_ua_w_k
            if not isfinite(residual):
                raise DomainError("nonfinite cooler UA residual")
            cache[t1]=(residual,heater,rating)
        except (DomainError,ValueError,OverflowError):
            cache[t1]=None
        return cache[t1]

    values={}
    for i in range(outer_scan_intervals+1):
        x=lo_t1+(hi_t1-lo_t1)*i/outer_scan_intervals
        values[x]=state(x)
    feasible=[(x,v) for x,v in values.items() if v is not None]
    if not feasible:
        raise DomainError("no feasible heater/cooler operating states in T1 range")

    tolerance=cold_sink.installed_ua_w_k*cooler_ua_tolerance_relative
    near=[(x,v) for x,v in feasible if abs(v[0])<=tolerance]
    positions=list(values)
    brackets=[]
    for lo,hi in zip(positions[:-1],positions[1:]):
        lv,rv=values[lo],values[hi]
        if lv is not None and rv is not None and lv[0]*rv[0]<0:
            brackets.append((lo,hi))
    if len(brackets)>1:
        raise DomainError("multiple detected cooler-UA roots")
    def finish(t:float,bracket:tuple[float,float],iterations:int)->CoupledPlantResult:
        v=state(t)
        if v is None:
            raise DomainError("final coupled plant state became infeasible")
        residual,heater,rating=v
        rel=abs(residual)/cold_sink.installed_ua_w_k
        if rel>cooler_ua_tolerance_relative:
            raise DomainError(
                f"cooler UA equality not converged; relative residual={rel:.5g}")
        if heater.ua_residual_relative>inner_ua_tolerance_relative:
            raise DomainError("heater UA equality not converged")
        return CoupledPlantResult(
            heater=heater,cooler=rating,
            installed_cooler_ua_w_k=cold_sink.installed_ua_w_k,
            cooler_ua_residual_w_k=residual,
            cooler_ua_residual_relative=rel,
            outer_iterations=iterations,outer_evaluations=n_calls,
            scanned_feasible_points=len(feasible),
            t1_bracket_k=bracket,
            equipment_flow_scaled=(equipment_flow_law is not None))

    if near and not brackets:
        t=min(near,key=lambda x:abs(x[1][0]))[0]
        if (len(near)>1 and
            max(x for x,_ in near)-min(x for x,_ in near)
            >(hi_t1-lo_t1)/outer_scan_intervals):
            raise DomainError("multiple separated near-zero cooler-UA states")
        return finish(t,(t,t),0)

    if not brackets:
        residuals=[v[0] for _,v in feasible]
        raise DomainError(
            "fixed cooler UA not bracketed; sampled residual range "
            f"[{min(residuals):.5g}, {max(residuals):.5g}] W/K")


    lo,hi=brackets[0]
    f_lo=values[lo][0]  # type: ignore[index]
    for it in range(1,outer_max_iterations+1):
        mid=(lo+hi)/2
        data=state(mid)
        if data is None:
            raise DomainError(
                "outer root crosses an infeasible heater/cooler state")
        f_mid=data[0]
        if f_lo*f_mid<=0:
            hi=mid
        else:
            lo=mid
            f_lo=f_mid
        if abs(f_mid)<=tolerance and (hi-lo)<=t1_tolerance_k:
            return finish(mid,(lo,hi),it)
    raise DomainError(
        f"outer fixed cooler-UA root did not converge in {outer_max_iterations} "
        f"iterations; bracket width {hi-lo:.5g} K")
