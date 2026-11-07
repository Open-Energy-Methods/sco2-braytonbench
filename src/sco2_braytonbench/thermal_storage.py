"""Conservative, constant-property 1-D/2-temperature packed-bed TES model.

This is a synthetic, *thermal* finite-volume model, not CFD, a PCM model,
a plant digital twin or an experimentally validated CIC energiGUNE model.

Cell equations (SI):
 C_f dTf_i/dt = |mdot| cp_f (Tf_upwind - Tf_i) + H_i (Ts_i-Tf_i)
 C_s dTs_i/dt = H_i (Tf_i-Ts_i)
where H_i = H_v A dx and fluid holdup C_f includes porosity.

A third-order strong-stability-preserving Runge--Kutta method (SSPRK3)
integrates both state and boundary energy *with identical quadrature*.
An explicit positivity timestep bound subcycles automatically; this is
conservative but does not substitute for time/spatial convergence.
"""
from __future__ import annotations

from dataclasses import dataclass
import math
from typing import Sequence


def _finite(name: str, value: float, *, positive: bool = False) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError(f"{name} must be a finite real number")
    x = float(value)
    if not math.isfinite(x) or (positive and x <= 0):
        raise ValueError(f"{name} must be finite" + (" and >0" if positive else ""))
    return x


@dataclass(frozen=True)
class PackedBedSpec:
    length_m: float
    area_m2: float
    porosity: float
    fluid_density_kg_m3: float
    fluid_cp_j_kg_k: float
    solid_density_kg_m3: float
    solid_cp_j_kg_k: float
    interphase_hv_w_m3_k: float
    n_cells: int

    def __post_init__(self) -> None:
        if type(self.n_cells) is not int or self.n_cells < 1:
            raise ValueError("n_cells must be a strictly positive integer")
        for name in ("length_m", "area_m2", "fluid_density_kg_m3",
                     "fluid_cp_j_kg_k", "solid_density_kg_m3",
                     "solid_cp_j_kg_k"):
            _finite(name, getattr(self, name), positive=True)
        eps = _finite("porosity", self.porosity, positive=True)
        if eps >= 1.0:
            raise ValueError("porosity must be strictly between zero and one")
        hv = _finite("interphase_hv_w_m3_k", self.interphase_hv_w_m3_k)
        if hv < 0:
            raise ValueError("interphase_hv_w_m3_k must be nonnegative")

    @property
    def cell_volume_m3(self) -> float:
        return self.length_m * self.area_m2 / self.n_cells

    @property
    def fluid_cell_capacity_j_k(self) -> float:
        return (self.porosity * self.fluid_density_kg_m3
                * self.fluid_cp_j_kg_k * self.cell_volume_m3)

    @property
    def solid_cell_capacity_j_k(self) -> float:
        return ((1.0 - self.porosity) * self.solid_density_kg_m3
                * self.solid_cp_j_kg_k * self.cell_volume_m3)

    @property
    def interphase_cell_w_k(self) -> float:
        return self.interphase_hv_w_m3_k * self.cell_volume_m3

    @property
    def total_fluid_capacity_j_k(self) -> float:
        return self.n_cells * self.fluid_cell_capacity_j_k

    @property
    def total_solid_capacity_j_k(self) -> float:
        return self.n_cells * self.solid_cell_capacity_j_k

    @property
    def cell_dx_m(self) -> float:
        return self.length_m / self.n_cells


@dataclass(frozen=True)
class PackedBedState:
    """Physical fluid/solid cell temperatures in K, left-to-right order."""

    fluid_k: tuple[float, ...]
    solid_k: tuple[float, ...]

    @classmethod
    def uniform(cls, spec: PackedBedSpec, fluid_k: float, solid_k: float) -> "PackedBedState":
        tf = _finite("fluid_k", fluid_k, positive=True)
        ts = _finite("solid_k", solid_k, positive=True)
        return cls((tf,) * spec.n_cells, (ts,) * spec.n_cells)

    def validate(self, spec: PackedBedSpec) -> None:
        if len(self.fluid_k) != spec.n_cells or len(self.solid_k) != spec.n_cells:
            raise ValueError("each state array must have exactly n_cells entries")
        for i, value in enumerate(self.fluid_k):
            _finite(f"fluid_k[{i}]", value, positive=True)
        for i, value in enumerate(self.solid_k):
            _finite(f"solid_k[{i}]", value, positive=True)


@dataclass(frozen=True)
class PackedBedStepResult:
    state: PackedBedState
    outlet_k: float
    flow_direction: int
    energy_boundary_j: float
    energy_change_j: float
    conservation_residual_j: float
    n_substeps: int
    courant_per_substep: float
    exchange_fluid_per_substep: float
    exchange_solid_per_substep: float
    outlet_trace: tuple[tuple[float, float], ...] | None = None


def stored_energy_j(spec: PackedBedSpec, state: PackedBedState, *, reference_k: float = 0.0) -> float:
    """Total (fluid + solid) sensible energy, relative to a fixed reference."""
    state.validate(spec)
    ref = _finite("reference_k", reference_k)
    cf, cs = spec.fluid_cell_capacity_j_k, spec.solid_cell_capacity_j_k
    return math.fsum(cf * (t - ref) for t in state.fluid_k) + math.fsum(
        cs * (t - ref) for t in state.solid_k
    )


def solid_soc(spec: PackedBedSpec, state: PackedBedState, *,
              cold_k: float, hot_k: float) -> float:
    """Unclipped solid-only state of charge. Out-of-range values are reported."""
    state.validate(spec)
    cold = _finite("cold_k", cold_k, positive=True)
    hot = _finite("hot_k", hot_k, positive=True)
    if hot <= cold:
        raise ValueError("hot_k must exceed cold_k")
    return (math.fsum(t - cold for t in state.solid_k)
            / (spec.n_cells * (hot - cold)))


def _rhs(spec: PackedBedSpec, tf: Sequence[float], ts: Sequence[float],
         inlet_k: float, mdot_kg_s: float) -> tuple[list[float], list[float], float]:
    cf, cs = spec.fluid_cell_capacity_j_k, spec.solid_cell_capacity_j_k
    H = spec.interphase_cell_w_k
    flow_cp = abs(mdot_kg_s) * spec.fluid_cp_j_kg_k
    n = spec.n_cells
    df = [0.0] * n
    ds = [0.0] * n
    if mdot_kg_s >= 0:
        for i in range(n):
            up = inlet_k if i == 0 else tf[i - 1]
            transfer = H * (ts[i] - tf[i])
            df[i] = (flow_cp * (up - tf[i]) + transfer) / cf
            ds[i] = -transfer / cs
        outlet = tf[-1]
    else:
        for i in range(n - 1, -1, -1):
            up = inlet_k if i == n - 1 else tf[i + 1]
            transfer = H * (ts[i] - tf[i])
            df[i] = (flow_cp * (up - tf[i]) + transfer) / cf
            ds[i] = -transfer / cs
        outlet = tf[0]
    return df, ds, flow_cp * (inlet_k - outlet)


def step_packed_bed(
    spec: PackedBedSpec,
    state: PackedBedState,
    *,
    inlet_k: float,
    mdot_kg_s: float,
    duration_s: float,
    safety_factor: float = 0.75,
    max_substeps: int = 250000,
    max_step_s: float | None = None,
    record_outlet_trace: bool = False,
) -> PackedBedStepResult:
    """Advance a held-inlet boundary by SSPRK3 with flux-matched energy ledger.

    Negative mdot reverses the flow direction. A zero-flow interval retains
    fluid/solid interphase exchange but no boundary energy transport.
    """
    state.validate(spec)
    if type(record_outlet_trace) is not bool:
        raise ValueError("record_outlet_trace must be boolean")
    tin = _finite("inlet_k", inlet_k, positive=True)
    flow = _finite("mdot_kg_s", mdot_kg_s)
    dt = _finite("duration_s", duration_s)
    sf = _finite("safety_factor", safety_factor, positive=True)
    if dt < 0 or not (0 < sf <= 1):
        raise ValueError("duration_s must be nonnegative; 0<safety_factor<=1")
    if type(max_substeps) is not int or max_substeps < 1:
        raise ValueError("max_substeps must be a positive integer")
    if max_step_s is not None:
        _finite("max_step_s", max_step_s, positive=True)
    cf, cs = spec.fluid_cell_capacity_j_k, spec.solid_cell_capacity_j_k
    H = spec.interphase_cell_w_k
    advection = abs(flow) * spec.fluid_cp_j_kg_k / cf
    fluid_exchange = H / cf
    solid_exchange = H / cs
    frequency = max(advection + fluid_exchange, solid_exchange)
    if dt == 0.0:
        outlet = state.fluid_k[-1] if flow >= 0 else state.fluid_k[0]
        return PackedBedStepResult(
            state, outlet, 0 if flow == 0 else (1 if flow > 0 else -1),
            0.0, 0.0, 0.0, 0, 0.0, 0.0, 0.0,
            ((0.0, outlet),) if record_outlet_trace else None,
        )
    allowed = (sf / frequency) if frequency else dt
    if max_step_s is not None:
        allowed = min(allowed, max_step_s)
    count = max(1, math.ceil(dt / allowed))
    if count > max_substeps:
        raise ValueError(
            f"required {count} stable substeps exceed max_substeps={max_substeps}"
        )
    h = dt / count
    fluid = list(state.fluid_k)
    solid = list(state.solid_k)
    boundary_energy_terms = []
    outlet_trace = (
        [(0.0, fluid[-1] if flow >= 0 else fluid[0])]
        if record_outlet_trace else None
    )
    for substep_index in range(count):
        df0, ds0, qb0 = _rhs(spec, fluid, solid, tin, flow)
        f1 = [a + h * b for a, b in zip(fluid, df0)]
        s1 = [a + h * b for a, b in zip(solid, ds0)]
        df1, ds1, qb1 = _rhs(spec, f1, s1, tin, flow)
        f2 = [0.75 * a + 0.25 * (b + h * c)
              for a, b, c in zip(fluid, f1, df1)]
        s2 = [0.75 * a + 0.25 * (b + h * c)
              for a, b, c in zip(solid, s1, ds1)]
        df2, ds2, qb2 = _rhs(spec, f2, s2, tin, flow)
        fluid = [(a / 3) + (2.0 / 3) * (b + h * c)
                 for a, b, c in zip(fluid, f2, df2)]
        solid = [(a / 3) + (2.0 / 3) * (b + h * c)
                 for a, b, c in zip(solid, s2, ds2)]
        boundary_energy_terms.append(h * (qb0 / 6 + qb1 / 6 + 2 * qb2 / 3))
        if outlet_trace is not None:
            outlet_trace.append((
                h * (substep_index + 1),
                fluid[-1] if flow >= 0 else fluid[0],
            ))
    final = PackedBedState(tuple(fluid), tuple(solid))
    final.validate(spec)
    initial_u = stored_energy_j(spec, state, reference_k=tin)
    final_u = stored_energy_j(spec, final, reference_k=tin)
    change = final_u - initial_u
    boundary = math.fsum(boundary_energy_terms)
    outlet = fluid[-1] if flow >= 0 else fluid[0]
    return PackedBedStepResult(
        final, outlet, 0 if flow == 0 else (1 if flow > 0 else -1),
        boundary, change, boundary - change, count,
        advection * h, fluid_exchange * h, solid_exchange * h,
        tuple(outlet_trace) if outlet_trace is not None else None,
    )
