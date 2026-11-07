"""TES-v0.8 synthetic operating-window and temperature-grade accounting.

This module *post-processes* the conservative two-temperature packed-bed
solver. It does not substitute qualification thresholds into the first-law
energy balance. Temperature-grade integrals approximate the continuous
outlet history with piecewise-linear observations; refine observation
spacing independently of the solver timestep and spatial grid.
"""
from __future__ import annotations

from dataclasses import dataclass
import math

from .tes_metrics import evaluate_tes_performance
from .thermal_storage import (
    PackedBedSpec, PackedBedState, _finite, solid_soc, step_packed_bed,
    stored_energy_j,
)


@dataclass(frozen=True)
class OperatingInputs:
    cold_k: float = 350.0
    hot_inlet_k: float = 650.0
    flow_kg_s: float = 0.05
    charge_turnovers: float = 0.8
    hold_turnovers: float = 0.1
    discharge_turnovers: float = 1.0
    useful_outlet_threshold_k: float = 500.0
    ambient_k: float = 300.0
    observations_per_stage: int = 24
    max_solver_step_s: float | None = None
    state_return_tolerance_k: float = 0.5

    def __post_init__(self) -> None:
        cold = _finite("cold_k", self.cold_k, positive=True)
        hot = _finite("hot_inlet_k", self.hot_inlet_k, positive=True)
        grade = _finite(
            "useful_outlet_threshold_k", self.useful_outlet_threshold_k,
            positive=True,
        )
        _finite("ambient_k", self.ambient_k, positive=True)
        _finite("flow_kg_s", self.flow_kg_s, positive=True)
        _finite("charge_turnovers", self.charge_turnovers, positive=True)
        hold = _finite("hold_turnovers", self.hold_turnovers)
        _finite("discharge_turnovers", self.discharge_turnovers, positive=True)
        tol = _finite("state_return_tolerance_k", self.state_return_tolerance_k)
        if not cold < hot or grade <= cold:
            raise ValueError("require cold < hot and grade > cold")
        if hold < 0 or tol < 0:
            raise ValueError("hold duration and return tolerance must be nonnegative")
        if (type(self.observations_per_stage) is not int
                or self.observations_per_stage < 2):
            raise ValueError("observations_per_stage must be integer >= 2")
        if self.max_solver_step_s is not None:
            _finite("max_solver_step_s", self.max_solver_step_s, positive=True)


@dataclass(frozen=True)
class OperatingResult:
    thermal_turnover_s: float
    charge_duration_s: float
    hold_duration_s: float
    discharge_duration_s: float
    charged_energy_j: float
    recovered_energy_j: float
    useful_discharge_energy_j: float
    reconstructed_discharge_energy_j: float
    observation_quadrature_error_j: float
    useful_discharge_duration_s: float
    first_qualified_time_s: float | None
    first_downcrossing_time_s: float | None
    max_discharge_outlet_k: float
    useful_fraction_of_recovered: float | None
    stored_energy_change_j: float
    first_law_residual_j: float
    first_law_relative_residual: float
    initial_solid_soc: float
    charged_solid_soc: float
    final_solid_soc: float
    charged_solid_capacity_j: float
    charged_fluid_capacity_j: float
    charged_solid_sensible_energy_j: float
    charged_fluid_sensible_energy_j: float
    charged_solid_exergy_j: float
    charged_fluid_exergy_j: float
    charged_total_exergy_j: float
    charged_thermocline_width_m: float | None
    charged_thermocline_monotone: bool
    max_cell_return_error_k: float
    complete_cycle: bool
    gross_round_trip_efficiency: float | None
    total_solver_substeps: int
    max_courant_substep: float


def _qualified_segment(
    t0: float, t1: float, grade: float, inlet: float,
    flow_heat_capacity_w_k: float, duration_s: float,
) -> tuple[float, float, float | None, float | None]:
    """Piecewise-linear temperature-grade integration; no energy correction.

    Return qualified energy, qualified seconds, first upward-entry local time
    (including zero if initially qualified), and downward-crossing local time.
    Equality to the temperature threshold qualifies.
    """
    if t0 >= grade and t1 >= grade:
        return (flow_heat_capacity_w_k * duration_s *
                (0.5 * (t0 + t1) - inlet), duration_s, 0.0, None)
    if t0 < grade and t1 < grade:
        return 0.0, 0.0, None, None
    if t0 == t1:
        return 0.0, 0.0, None, None
    fraction = (grade - t0) / (t1 - t0)
    fraction = min(1.0, max(0.0, fraction))
    if t0 < grade:
        duration = duration_s * (1.0 - fraction)
        energy = flow_heat_capacity_w_k * duration * (
            0.5 * (grade + t1) - inlet
        )
        return energy, duration, duration_s * fraction, None
    duration = duration_s * fraction
    energy = flow_heat_capacity_w_k * duration * (
        0.5 * (t0 + grade) - inlet
    )
    return energy, duration, 0.0, duration_s * fraction


def run_operating_case(spec: PackedBedSpec,
                       inputs: OperatingInputs) -> OperatingResult:
    """Charge, optional no-flow hold, then reverse-discharge same full state.

    Durations use total fluid+solid thermal capacity divided by mdot*cp.
    The discharge-quality threshold only counts energy while its outlet
    satisfies the prescribed grade; ALL withdrawn heat remains in the
    physical first-law ledger, whether qualified or not.
    """
    if not isinstance(inputs, OperatingInputs):
        raise TypeError("inputs must be OperatingInputs")
    turnover = (
        spec.total_fluid_capacity_j_k + spec.total_solid_capacity_j_k
    ) / (inputs.flow_kg_s * spec.fluid_cp_j_kg_k)
    if not math.isfinite(turnover) or turnover <= 0:
        raise ValueError("invalid thermal turnover")
    charge_s = inputs.charge_turnovers * turnover
    hold_s = inputs.hold_turnovers * turnover
    discharge_s = inputs.discharge_turnovers * turnover
    initial = PackedBedState.uniform(spec, inputs.cold_k, inputs.cold_k)
    state = initial
    charged_terms = []
    recovered_terms = []
    quality_terms = []
    full_linear_terms = []
    seconds_terms = []
    first_qualified = None
    first_downcrossing = None
    total_substeps = 0
    max_courant = 0.0
    max_discharge_outlet = -math.inf
    flow_cp = inputs.flow_kg_s * spec.fluid_cp_j_kg_k

    def advance(duration: float, inlet: float, mdot: float):
        nonlocal state, total_substeps, max_courant
        before = state
        step = step_packed_bed(
            spec, before, inlet_k=inlet, mdot_kg_s=mdot,
            duration_s=duration, max_step_s=inputs.max_solver_step_s,
        )
        state = step.state
        total_substeps += step.n_substeps
        max_courant = max(max_courant, step.courant_per_substep)
        return before, step

    for _ in range(inputs.observations_per_stage):
        _, step = advance(
            charge_s / inputs.observations_per_stage,
            inputs.hot_inlet_k, inputs.flow_kg_s,
        )
        charged_terms.append(step.energy_boundary_j)
    charged_state = state
    metrics = evaluate_tes_performance(
        spec, charged_state, cold_k=inputs.cold_k,
        hot_k=inputs.hot_inlet_k, ambient_k=inputs.ambient_k,
    )
    charged_soc = solid_soc(
        spec, charged_state, cold_k=inputs.cold_k,
        hot_k=inputs.hot_inlet_k,
    )
    if hold_s:
        advance(hold_s, inputs.cold_k, 0.0)

    h = discharge_s / inputs.observations_per_stage
    for i in range(inputs.observations_per_stage):
        before, step = advance(h, inputs.cold_k, -inputs.flow_kg_s)
        recovered_terms.append(-step.energy_boundary_j)
        outlet_before = before.fluid_k[0]
        outlet_after = step.outlet_k
        max_discharge_outlet = max(
            max_discharge_outlet, outlet_before, outlet_after,
        )
        energy, seconds, enter, exit_ = _qualified_segment(
            outlet_before, outlet_after,
            inputs.useful_outlet_threshold_k, inputs.cold_k, flow_cp, h,
        )
        quality_terms.append(energy)
        full_linear_terms.append(
            flow_cp * h * (0.5*(outlet_before+outlet_after) - inputs.cold_k)
        )
        seconds_terms.append(seconds)
        if enter is not None and first_qualified is None:
            first_qualified = i * h + enter
        if exit_ is not None and first_downcrossing is None:
            first_downcrossing = i * h + exit_

    charged_energy = math.fsum(charged_terms)
    recovered_energy = math.fsum(recovered_terms)
    useful_energy = math.fsum(quality_terms)
    linear_recovered = math.fsum(full_linear_terms)
    useful_seconds = math.fsum(seconds_terms)
    stored_change = (
        stored_energy_j(spec, state, reference_k=inputs.cold_k)
        - stored_energy_j(spec, initial, reference_k=inputs.cold_k)
    )
    ledger = charged_energy - recovered_energy
    residual = ledger - stored_change
    relative = abs(residual) / max(
        1.0, abs(charged_energy), abs(recovered_energy),
        abs(stored_change),
    )
    max_return = max(
        [abs(a - b) for a, b in zip(initial.fluid_k, state.fluid_k)] +
        [abs(a - b) for a, b in zip(initial.solid_k, state.solid_k)]
    )
    # These checks are physics audits, NOT gate-conditioned conservation.
    scale = max(1.0, abs(charged_energy), abs(recovered_energy))
    if (charged_energy <= 0 or recovered_energy < -scale * 1e-12
            or useful_energy < -scale * 1e-12
            or useful_energy > recovered_energy + abs(linear_recovered - recovered_energy)
            + scale * 1e-9):
        raise ValueError("scenario violates charge/discharge/grade accounting")
    if relative > 1e-9:
        raise ArithmeticError("packed-bed first-law numerical closure failed")
    complete = (
        recovered_energy > 0
        and max_return <= inputs.state_return_tolerance_k
    )
    return OperatingResult(
        thermal_turnover_s=turnover,
        charge_duration_s=charge_s,
        hold_duration_s=hold_s,
        discharge_duration_s=discharge_s,
        charged_energy_j=charged_energy,
        recovered_energy_j=recovered_energy,
        useful_discharge_energy_j=useful_energy,
        reconstructed_discharge_energy_j=linear_recovered,
        observation_quadrature_error_j=linear_recovered-recovered_energy,
        useful_discharge_duration_s=useful_seconds,
        first_qualified_time_s=first_qualified,
        first_downcrossing_time_s=first_downcrossing,
        max_discharge_outlet_k=max_discharge_outlet,
        useful_fraction_of_recovered=(
            useful_energy / recovered_energy if recovered_energy > 0 else None
        ),
        stored_energy_change_j=stored_change,
        first_law_residual_j=residual,
        first_law_relative_residual=relative,
        initial_solid_soc=solid_soc(
            spec, initial, cold_k=inputs.cold_k, hot_k=inputs.hot_inlet_k,
        ),
        charged_solid_soc=charged_soc,
        final_solid_soc=solid_soc(
            spec, state, cold_k=inputs.cold_k, hot_k=inputs.hot_inlet_k,
        ),
        charged_solid_capacity_j=metrics.design_solid_capacity_j,
        charged_fluid_capacity_j=metrics.design_fluid_capacity_j,
        charged_solid_sensible_energy_j=metrics.solid_sensible_energy_j,
        charged_fluid_sensible_energy_j=metrics.fluid_sensible_energy_j,
        charged_solid_exergy_j=metrics.solid_exergy_j,
        charged_fluid_exergy_j=metrics.fluid_exergy_j,
        charged_total_exergy_j=metrics.total_reversible_exergy_j,
        charged_thermocline_width_m=metrics.thermocline_width_m,
        charged_thermocline_monotone=metrics.thermocline_profile_monotone,
        max_cell_return_error_k=max_return,
        complete_cycle=complete,
        gross_round_trip_efficiency=(
            recovered_energy / charged_energy if complete else None
        ),
        total_solver_substeps=total_substeps,
        max_courant_substep=max_courant,
    )
