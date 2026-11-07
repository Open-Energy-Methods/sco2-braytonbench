"""Staged packed-bed charge, hold and discharge with a closed energy ledger.

The operating schedule is prescribed externally and is not an industrial
control strategy or a coupled sCO2 plant. Gross round-trip energy ratios
are only labelled as such when the *full cell state* returns to within
an explicitly reported temperature tolerance.
"""
from __future__ import annotations
from dataclasses import dataclass
import math
from typing import Iterable, Literal

from .thermal_storage import (
    PackedBedSpec, PackedBedState, PackedBedStepResult, _finite,
    solid_soc, stored_energy_j, step_packed_bed,
)

StageMode = Literal["charge", "hold", "discharge"]


@dataclass(frozen=True)
class StorageStage:
    name: str
    mode: StageMode
    duration_s: float
    inlet_k: float
    mdot_kg_s: float

    def __post_init__(self) -> None:
        if not isinstance(self.name, str) or not self.name.strip():
            raise ValueError("stage name must be nonblank")
        if self.mode not in ("charge", "hold", "discharge"):
            raise ValueError("mode must be charge/hold/discharge")
        _finite("duration_s", self.duration_s, positive=True)
        _finite("inlet_k", self.inlet_k, positive=True)
        flow = _finite("mdot_kg_s", self.mdot_kg_s)
        if self.mode == "hold" and flow != 0.0:
            raise ValueError("hold mode requires zero through-flow")
        if self.mode != "hold" and flow == 0.0:
            raise ValueError("charge/discharge require a nonzero through-flow")


@dataclass(frozen=True)
class StorageStageRecord:
    name: str
    mode: StageMode
    t_start_s: float
    t_end_s: float
    inlet_k: float
    mass_flow_kg_s: float
    outlet_k: float
    energy_boundary_j: float
    stored_energy_change_j: float
    conservation_residual_j: float
    solid_soc: float
    courant_per_substep: float
    exchange_fluid_per_substep: float
    exchange_solid_per_substep: float
    n_substeps: int


@dataclass(frozen=True)
class StorageScheduleResult:
    state: PackedBedState
    records: tuple[StorageStageRecord, ...]
    charged_energy_j: float
    recovered_energy_j: float
    stored_energy_change_j: float
    conservation_residual_j: float
    solid_usable_capacity_j: float
    initial_solid_soc: float
    final_solid_soc: float
    max_cell_return_error_k: float
    complete_cycle: bool
    gross_energy_efficiency: float | None


def run_storage_schedule(
    spec: PackedBedSpec,
    initial: PackedBedState,
    stages: Iterable[StorageStage],
    *,
    cold_k: float,
    hot_k: float,
    max_step_s: float | None = None,
    state_return_tolerance_k: float = 0.5,
) -> StorageScheduleResult:
    """Advance a declared schedule and report only defensible cycle metrics.

    `charge` and `discharge` are operating modes and also require compatible
    *actual* signed boundary heat. This prevents the run from being
    incorrectly labelled in the generated report.
    """
    initial.validate(spec)
    tolerance = _finite("state_return_tolerance_k", state_return_tolerance_k)
    if tolerance < 0:
        raise ValueError("state_return_tolerance_k must be nonnegative")
    cold = _finite("cold_k", cold_k, positive=True)
    hot = _finite("hot_k", hot_k, positive=True)
    if not hot > cold:
        raise ValueError("hot_k must exceed cold_k")
    items = tuple(stages)
    if not items:
        raise ValueError("schedule must have at least one stage")
    if not all(isinstance(s, StorageStage) for s in items):
        raise ValueError("all stages must be StorageStage values")
    if len(set(stage.name for stage in items)) != len(items):
        raise ValueError("stage names must be unique")
    current = initial
    elapsed = 0.0
    records = []
    for stage in items:
        step: PackedBedStepResult = step_packed_bed(
            spec, current, inlet_k=stage.inlet_k,
            mdot_kg_s=stage.mdot_kg_s,
            duration_s=stage.duration_s, max_step_s=max_step_s,
        )
        E = step.energy_boundary_j
        scale = max(1.0, abs(step.energy_change_j), abs(E))
        sign_tolerance = scale * 2e-12
        if stage.mode == "charge" and E < -sign_tolerance:
            raise ValueError(f"{stage.name}: charge stage extracted net bed energy")
        if stage.mode == "discharge" and E > sign_tolerance:
            raise ValueError(f"{stage.name}: discharge stage added net bed energy")
        if stage.mode == "hold" and abs(E) > sign_tolerance:
            raise AssertionError("zero-flow hold unexpectedly exchanged boundary heat")
        next_time = elapsed + stage.duration_s
        records.append(StorageStageRecord(
            stage.name, stage.mode, elapsed, next_time, stage.inlet_k,
            stage.mdot_kg_s, step.outlet_k, E, step.energy_change_j,
            step.conservation_residual_j,
            solid_soc(spec, step.state, cold_k=cold, hot_k=hot),
            step.courant_per_substep, step.exchange_fluid_per_substep,
            step.exchange_solid_per_substep, step.n_substeps,
        ))
        elapsed = next_time
        current = step.state
    charged = math.fsum(max(0., rec.energy_boundary_j) for rec in records)
    recovered = math.fsum(max(0., -rec.energy_boundary_j) for rec in records)
    boundary = math.fsum(rec.energy_boundary_j for rec in records)
    change = stored_energy_j(spec, current, reference_k=cold) - stored_energy_j(
        spec, initial, reference_k=cold
    )
    max_return = max(
        [abs(a - b) for a, b in zip(initial.fluid_k, current.fluid_k)] +
        [abs(a - b) for a, b in zip(initial.solid_k, current.solid_k)]
    )
    has_both = any(s.mode == "charge" for s in items) and any(
        s.mode == "discharge" for s in items
    )
    complete = has_both and charged > 0 and max_return <= tolerance
    return StorageScheduleResult(
        state=current, records=tuple(records),
        charged_energy_j=charged, recovered_energy_j=recovered,
        stored_energy_change_j=change,
        conservation_residual_j=boundary - change,
        solid_usable_capacity_j=spec.total_solid_capacity_j_k * (hot - cold),
        initial_solid_soc=solid_soc(spec, initial, cold_k=cold, hot_k=hot),
        final_solid_soc=solid_soc(spec, current, cold_k=cold, hot_k=hot),
        max_cell_return_error_k=max_return,
        complete_cycle=complete,
        gross_energy_efficiency=(recovered / charged) if complete else None,
    )
