"""Dimensionless, schedule-conditioned synthetic TES ROM feature contract.

The surrogate learns ONLY from synthetic 1-D two-temperature packed-bed
simulation outputs. At prediction time it requires full prescribed
charge/discharge schedule, geometry and material properties as specified
by the TES-v0.6 generated manifest; it is not an online controller.

No target or sensor-derived fields are read as model inputs.
The thermal PDE is linear in temperature for fixed constant properties.
Consequently both targets are normalized by the known initial-to-hot
temperature span. This is a physical scaling, not use of a hidden label.
"""
from __future__ import annotations

import math

FEATURE_NAMES = (
    "is_discharge", "phase_fraction",
    "charge_turnovers", "discharge_turnovers",
    "elapsed_charge_turnovers", "elapsed_discharge_turnovers",
    "log10_ntu_bed", "log10_mass_flow", "log10_hv",
    "ntu_charge", "ntu_discharge",
)
TARGET_NAMES = ("normalized_outlet", "solid_soc")
FORBIDDEN_INPUT_FIELDS = (
    "fluid_outlet_k", "solid_soc", "boundary_energy_j",
    "first_law_residual_j", "courant", "exchange_fluid", "exchange_solid",
)


def features(row: dict) -> list[float]:
    """Only schedule/parameter fields, no simulated target, post-step or labels."""
    phase = row["phase"]
    if phase not in ("charge", "discharge"):
        raise ValueError("unknown phase")
    f = float(row["phase_fraction"])
    charge = float(row["charge_turnovers"])
    discharge = float(row["discharge_turnovers"])
    flow = float(row["flow_kg_s"])
    hv = float(row["hv_w_m3_k"])
    # The full TES-v0.6 generator fixes L=1 m, A=0.1 m2, cp_f=1000 J/kgK.
    # These are not fitted to validation or test measurements.
    ntu = hv * 0.1 * 1.0 / (flow * 1000.0)
    if not all(math.isfinite(v) for v in (f,charge,discharge,flow,hv,ntu)):
        raise ValueError("nonfinite model feature")
    if not 0 < f <= 1 or min(charge,discharge,flow,hv,ntu) <= 0:
        raise ValueError("invalid physical domain")
    d = float(phase == "discharge")
    x = [
        d, f, charge, discharge,
        f * charge if not d else charge,
        f * discharge if d else 0.0,
        math.log10(ntu), math.log10(flow), math.log10(hv),
        ntu * charge, ntu * discharge,
    ]
    assert len(x) == len(FEATURE_NAMES)
    return x


def normalized_targets(row: dict) -> tuple[float, float]:
    """Used ONLY by training/validation/evaluation code, never inference."""
    initial=float(row["initial_k"])
    hot=float(row["hot_inlet_k"])
    if not (hot > initial > 0):
        raise ValueError("invalid initial/hot reference")
    y = ((float(row["fluid_outlet_k"])-initial)/(hot-initial),
         float(row["solid_soc"]))
    if not all(math.isfinite(v) for v in y):
        raise ValueError("nonfinite target")
    return y


def denormalize(row: dict, theta_out: float) -> float:
    initial=float(row["initial_k"])
    hot=float(row["hot_inlet_k"])
    if not hot>initial>0:
        raise ValueError("invalid physical temperature span")
    return initial+(hot-initial)*theta_out


def clip_with_flag(value: float) -> tuple[float, bool]:
    """Explicitly flag raw normalized prediction outside the passive 0–1 bound."""
    if not math.isfinite(value):
        raise ValueError("surrogate predicted a nonfinite state")
    return max(0.,min(1.,value)), value<0 or value>1
