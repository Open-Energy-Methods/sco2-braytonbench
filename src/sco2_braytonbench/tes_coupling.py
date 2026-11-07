"""Open, single-pass TES discharge -> finite-source Brayton heat exchanger.

This is intentionally NOT a closed HTF recirculation loop or a shared
gas source simultaneously feeding wall and TES. It advances the packed
bed under a prescribed external cold inlet, then evaluates the
*instantaneous endpoint* thermo-fluid boundary of a separately modelled
heater and existing quasi-steady recuperated power block.

Bed interval energy [J] and endpoint rates [W] are DIFFERENT temporal
quantities and never summed together. The through-flow gas enthalpy
drops only once across the existing finite-source heater. No
experimental CARBOSOLA/CIC facility hardware is represented.
"""
from __future__ import annotations

from dataclasses import dataclass
from math import isfinite

from .cycle import CycleInputs
from .properties import Properties, DomainError
from .thermal_storage import (
    PackedBedSpec, PackedBedState, PackedBedStepResult,
    step_packed_bed, _finite
)
from .whr import WasteGasSource, WHRPoint, evaluate_whr_design


@dataclass(frozen=True)
class TESDischargeSnapshot:
    bed_step: PackedBedStepResult
    cycle_point: WHRPoint
    bed_feed_temperature_k: float
    bed_outlet_temperature_k: float
    heater_gas_exit_temperature_k: float
    mass_flow_kg_s: float
    storage_inventory_rate_w: float
    heater_to_co2_rate_w: float
    net_stream_boundary_rate_w: float
    cooler_rate_w: float
    shaft_rate_w: float
    combined_instantaneous_residual_w: float
    instantaneous_stage_time: str = "end_of_interval"


def advance_storage_to_cycle_snapshot(
    props: Properties,
    cycle_inputs: CycleInputs,
    bed: PackedBedSpec,
    initial: PackedBedState,
    *,
    bed_inlet_k: float,
    mass_flow_kg_s: float,
    duration_s: float,
    minimum_gas_heater_exit_k: float,
    maximum_heater_ua_w_k: float,
    minimum_heater_approach_k: float = 10.,
    heater_segments: int = 12,
) -> TESDischargeSnapshot:
    """Check a one-pass TES -> rated gas/CO2 heater -> steady power block.

    Thermal topology: externally specified cold HTF enters bed; bed
    transfers energy to HTF; HTF enters the existing finite exhaust-to-
    CO2 heat exchanger; its exit is a separate EXTERNAL stream boundary.

    No simultaneous waste-heat source is added to this same HTF.
    The entire loop is OPEN; this solver cannot be used as a closed
    recirculating TES/CO2 plant without an additional return-HX solve.
    """
    initial.validate(bed)
    flow = _finite("mass_flow_kg_s", mass_flow_kg_s, positive=True)
    tin = _finite("bed_inlet_k", bed_inlet_k, positive=True)
    dt = _finite("duration_s", duration_s, positive=True)
    stack = _finite("minimum_gas_heater_exit_k",
                    minimum_gas_heater_exit_k, positive=True)
    ua = _finite("maximum_heater_ua_w_k",
                 maximum_heater_ua_w_k, positive=True)
    approach = _finite("minimum_heater_approach_k",
                       minimum_heater_approach_k, positive=True)
    if type(heater_segments) is not int or heater_segments < 3:
        raise ValueError("heater_segments must be integer >=3")
    step = step_packed_bed(
        bed, initial, inlet_k=tin, mdot_kg_s=flow, duration_s=dt
    )
    tout = step.outlet_k
    if tout <= stack or tout - cycle_inputs.t4_k <= approach:
        raise DomainError(
            "TES discharge outlet cannot support specified gas heater "
            "stack floor / hot-end CO2 approach"
        )
    source = WasteGasSource(
        inlet_temperature_k=tout, mass_flow_kg_s=flow,
        cp_j_kg_k=bed.fluid_cp_j_kg_k,
        minimum_stack_temperature_k=stack,
        maximum_heater_ua_w_k=ua,
        minimum_heater_approach_k=approach,
        segments=heater_segments
    )
    point = evaluate_whr_design(props, cycle_inputs, source)
    gas_exit = point.heater.gas_out_k
    stream_capacity = flow * bed.fluid_cp_j_kg_k
    storage_rate = stream_capacity * (tin - tout)  # dU_bed/dt at final state
    heater_rate = stream_capacity * (tout - gas_exit)
    stream_boundary = stream_capacity * (tin - gas_exit)
    # At a single instant the source/bed+cycle balance is:
    # mcp(Tin - Tout_heater) = dU_bed/dt + Q_cooler + W_net.
    combined = (stream_boundary - storage_rate
                - point.cycle.cooler_w - point.cycle.net_w)
    if abs(heater_rate - point.cycle.heater_w) > (
        1e-7 * max(1., abs(point.cycle.heater_w))
    ):
        raise DomainError("HTF heater energy does not equal cycle heater energy")
    if abs(combined) > 1e-7 * max(1., abs(heater_rate)):
        raise DomainError("instantaneous TES/CO2/control volume ledger failed")
    if not all(isfinite(v) for v in (storage_rate, heater_rate, combined)):
        raise DomainError("nonfinite combined TES/cycle energy ledger")
    return TESDischargeSnapshot(
        bed_step=step, cycle_point=point,
        bed_feed_temperature_k=tin,
        bed_outlet_temperature_k=tout,
        heater_gas_exit_temperature_k=gas_exit,
        mass_flow_kg_s=flow,
        storage_inventory_rate_w=storage_rate,
        heater_to_co2_rate_w=heater_rate,
        net_stream_boundary_rate_w=stream_boundary,
        cooler_rate_w=point.cycle.cooler_w,
        shaft_rate_w=point.cycle.net_w,
        combined_instantaneous_residual_w=combined,
    )
