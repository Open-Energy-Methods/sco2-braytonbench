"""Educational lumped liquid-piston / molecular-spring pressure-volume model.

This is NOT nanopore molecular dynamics, a material-calibrated wetting law,
CFD, a hydraulic transient or COMPETENT experimental validation. An ideal-gas
pocket is displaced by an incompressible liquid stroke of volume V_pore.
Hydraulic pressure is p_gas(x) + p_capillary_branch. Branch offsets are
externally specified constants, NOT predicted using a continuum Laplace law.

The distinction between gas work, heat transferred to an isothermal
reservoir, recoverable surface work, and dissipated hysteresis is explicit.
All pressure is absolute (Pa), volume m^3, work J, temperature K.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass
import math
from typing import Literal

GasPath = Literal["isothermal", "reversible_adiabatic"]


def _real(name: str, value: float, *, strict_positive: bool = False) -> float:
    if isinstance(value, bool) or not isinstance(value, (float, int)):
        raise ValueError(f"{name} must be a finite real number")
    x = float(value)
    if not math.isfinite(x) or (strict_positive and x <= 0):
        raise ValueError(f"{name} must be finite" + (" and > 0" if strict_positive else ""))
    return x


@dataclass(frozen=True)
class LiquidPistonSpec:
    gas_initial_pressure_pa: float = 10_000_000.0
    gas_initial_volume_m3: float = 0.002
    gas_initial_temperature_k: float = 300.0
    gas_specific_r_j_kg_k: float = 287.0
    displaced_liquid_volume_m3: float = 0.0005
    intrusion_overpressure_pa: float = 20_000_000.0
    extrusion_overpressure_pa: float = 12_000_000.0
    gas_path: GasPath = "isothermal"
    heat_capacity_ratio: float = 1.4
    samples_per_branch: int = 60

    def __post_init__(self) -> None:
        for name in (
            "gas_initial_pressure_pa", "gas_initial_volume_m3",
            "gas_initial_temperature_k", "gas_specific_r_j_kg_k",
            "displaced_liquid_volume_m3",
        ):
            _real(name, getattr(self, name), strict_positive=True)
        pin = _real("intrusion_overpressure_pa", self.intrusion_overpressure_pa)
        pex = _real("extrusion_overpressure_pa", self.extrusion_overpressure_pa)
        if pex < 0 or pin < pex:
            raise ValueError("require intrusion pressure >= extrusion pressure >= 0")
        if self.displaced_liquid_volume_m3 >= self.gas_initial_volume_m3:
            raise ValueError("gas pocket would vanish; require V_liquid < V_gas_initial")
        if self.gas_path not in ("isothermal", "reversible_adiabatic"):
            raise ValueError("gas_path must be isothermal or reversible_adiabatic")
        gamma = _real("heat_capacity_ratio", self.heat_capacity_ratio)
        if not 1.0 < gamma <= 2.0:
            raise ValueError("ideal-gas adiabatic heat capacity ratio must be (1,2]")
        if type(self.samples_per_branch) is not int or self.samples_per_branch < 2:
            raise ValueError("samples_per_branch must be an integer >= 2")

    @property
    def gas_mass_kg(self) -> float:
        return (self.gas_initial_pressure_pa * self.gas_initial_volume_m3 /
                (self.gas_specific_r_j_kg_k * self.gas_initial_temperature_k))

    @property
    def gas_final_volume_m3(self) -> float:
        return self.gas_initial_volume_m3 - self.displaced_liquid_volume_m3


@dataclass(frozen=True)
class BranchPoint:
    branch: str
    intrusion_fraction: float
    displaced_volume_m3: float
    gas_volume_m3: float
    gas_pressure_pa: float
    gas_temperature_k: float
    hydraulic_pressure_pa: float


@dataclass(frozen=True)
class LiquidPistonCycle:
    spec: LiquidPistonSpec
    points: tuple[BranchPoint, ...]
    gas_compression_work_j: float
    gas_internal_energy_increase_j: float
    reservoir_heat_rejected_on_compression_j: float
    recoverable_surface_energy_j: float
    hysteresis_dissipation_j: float
    hydraulic_input_work_j: float
    hydraulic_recovered_work_j: float
    work_recovery_fraction: float
    loading_energy_residual_j: float
    unloading_energy_residual_j: float
    full_cycle_energy_residual_j: float

    def to_json_dict(self) -> dict:
        result = asdict(self)
        result["evidence_class"] = "illustrative_ideal_gas_constant_branch_capillary_offsets"
        result["not_claimed"] = [
            "nanoporous-material PVT constitutive calibration",
            "liquid invasion/extrusion kinetics or pore-size distribution",
            "experimental evidence", "hydraulic pumps/valves/friction/pressure losses",
            "high-fidelity CFD", "COMPETENT design or storage efficiency",
        ]
        return result


def gas_state(spec: LiquidPistonSpec, intrusion_fraction: float) -> tuple[float, float, float]:
    """(volume m^3, absolute pressure Pa, temperature K) at imposed stroke x."""
    x = _real("intrusion_fraction", intrusion_fraction)
    if not 0 <= x <= 1:
        raise ValueError("intrusion_fraction must belong to [0,1]")
    v = spec.gas_initial_volume_m3 - x * spec.displaced_liquid_volume_m3
    ratio = spec.gas_initial_volume_m3 / v
    if spec.gas_path == "isothermal":
        t = spec.gas_initial_temperature_k
        p = spec.gas_initial_pressure_pa * ratio
    else:
        t = spec.gas_initial_temperature_k * ratio ** (spec.heat_capacity_ratio - 1.0)
        p = spec.gas_initial_pressure_pa * ratio ** spec.heat_capacity_ratio
    if not all(math.isfinite(a) and a > 0 for a in (v, p, t)):
        raise ValueError("nonfinite/nonphysical ideal-gas state")
    return v, p, t


def gas_compression_work(spec: LiquidPistonSpec) -> float:
    """Analytic positive work ON gas for isothermal / reversible adiabatic stroke."""
    a = math.log(spec.gas_initial_volume_m3 / spec.gas_final_volume_m3)
    pv0 = spec.gas_initial_pressure_pa * spec.gas_initial_volume_m3
    if spec.gas_path == "isothermal":
        w = pv0 * a
    else:
        gamma_offset = spec.heat_capacity_ratio - 1
        w = pv0 * math.expm1(gamma_offset * a) / gamma_offset
    if not math.isfinite(w) or w < 0:
        raise ValueError("gas work nonfinite")
    return w


def simulate_liquid_piston(spec: LiquidPistonSpec) -> LiquidPistonCycle:
    """Return a complete prescribed stroke loop with an explicit closed energy ledger.

    An ideal reversible gas is coupled algebraically to a prescribed liquid
    stroke. Intrusion/extrusion capillary overpressure is constant per
    *branch*, making lost work (pin-pex)*dV nonnegative. No independent
    pore/interface energy state or calibrated wetting kinetics is computed.
    The recoverable surface-energy term is a bookkeeping reference
    p_ex*dV; the hysteresis excess is dissipated by assumption.
    """
    if not isinstance(spec, LiquidPistonSpec):
        raise TypeError("spec must be LiquidPistonSpec")
    pts = []
    n = spec.samples_per_branch
    for branch, indices, cap in (
        ("intrusion", range(n + 1), spec.intrusion_overpressure_pa),
        ("extrusion", range(n, -1, -1), spec.extrusion_overpressure_pa),
    ):
        for i in indices:
            x = i / n
            v, p, t = gas_state(spec, x)
            pts.append(BranchPoint(
                branch=branch, intrusion_fraction=x,
                displaced_volume_m3=x * spec.displaced_liquid_volume_m3,
                gas_volume_m3=v, gas_pressure_pa=p, gas_temperature_k=t,
                hydraulic_pressure_pa=p + cap,
            ))
    gw = gas_compression_work(spec)
    surf = spec.extrusion_overpressure_pa * spec.displaced_liquid_volume_m3
    diss = (spec.intrusion_overpressure_pa -
            spec.extrusion_overpressure_pa) * spec.displaced_liquid_volume_m3
    work_in = gw + spec.intrusion_overpressure_pa * spec.displaced_liquid_volume_m3
    work_out = gw + surf
    delta_u = gw if spec.gas_path == "reversible_adiabatic" else 0.0
    rejected_heat = gw if spec.gas_path == "isothermal" else 0.0
    # Loading: W_in = gas deltaU + heat rejected + recoverable
    # surface bookkeeping + hysteretic dissipation.
    residual_load = work_in - (delta_u + rejected_heat + surf + diss)
    # Unloading: W_out = reversible gas deltaU returned plus equal
    # external thermal input (isothermal) or prior deltaU (adiabatic)
    # plus surface energy. No extra hysteretic unloading work assigned.
    residual_unload = work_out - (delta_u + rejected_heat + surf)
    residual_cycle = work_in - work_out - diss
    result = LiquidPistonCycle(
        spec, tuple(pts), gw, delta_u, rejected_heat, surf, diss,
        work_in, work_out, work_out / work_in,
        residual_load, residual_unload, residual_cycle,
    )
    scale = max(1., work_in)
    if max(abs(residual_load), abs(residual_unload), abs(residual_cycle)) > 1e-12 * scale:
        raise AssertionError("lumped energy ledger unexpectedly failed")
    return result
