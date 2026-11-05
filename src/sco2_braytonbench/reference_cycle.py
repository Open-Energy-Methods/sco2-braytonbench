"""Friedman-Rapp 2016 Figure 2b: a *conceptual* 12-state cycle.

This is a source-mapped, reduced thermodynamic comparison. It is NOT a
reproduction of the original approximately 400-equation EES plant (Figure 4).
The paper's compressor-turbine branch and unreported detailed state points
cannot be inferred from Table 3, even if aggregate results appear close.
"""
from __future__ import annotations

from dataclasses import dataclass
from math import isfinite
from .core import compressor_outlet, turbine_outlet
from .exchangers import segmented_recuperator
from .properties import DomainError, Properties, State
from .references import fr2016_pressure_map

FR2016_REPORTED = {
    "q_heater_MW": 100.20,
    "w_turbine_MW": 38.08,
    "w_compressor_MW": 13.65,
    "q_cooler_MW": 75.80,
}
FR2016_REPORTED["eta_thermal"] = (
    FR2016_REPORTED["w_turbine_MW"] - FR2016_REPORTED["w_compressor_MW"]
) / FR2016_REPORTED["q_heater_MW"]

@dataclass(frozen=True)
class FR2016Comparison:
    points: dict[int, State]
    w_turbine_j_kg: float
    w_compressor_j_kg: float
    q_heater_j_kg: float
    q_cooler_j_kg: float
    eta_thermal: float
    energy_residual_j_kg: float
    recuperator_min_dt_k: float
    recuperator_ua_per_kg_s_w_k: float

    def equivalent_MW_at_reported_heater_duty(self) -> dict[str, float]:
        """Diagnostic only: normalize to the paper's external heat input."""
        scale = FR2016_REPORTED["q_heater_MW"] / self.q_heater_j_kg
        return {
            "heater": FR2016_REPORTED["q_heater_MW"],
            "turbine": scale * self.w_turbine_j_kg,
            "compressor": scale * self.w_compressor_j_kg,
            "cooler": scale * self.q_cooler_j_kg,
            "net": scale * (self.w_turbine_j_kg - self.w_compressor_j_kg),
        }

def fr2016_conceptual_cycle(
    props: Properties,
    *,
    low_pressure_pa: float,
    low_temperature_k: float,
    high_temperature_k: float = 550.0,
    high_pressure_pa: float = 30e6,
    eta_compressor: float = .85,
    eta_turbine: float = .90,
    recuperator_effectiveness: float = .925,
    segments: int = 30,
    low_pressure_point: int = 8,
    low_temperature_point: int = 7,
) -> FR2016Comparison:
    """Paper Figure 2b mapping, all SI units, reference pressure at point 8.

    Source-mapping sensitivity controls:
    - low_pressure_point = 7 or 8 (precooler outlet or compressor inlet);
    - low_temperature_point = 7 or 8, same choices.
    Source Figure 9 labels T7, favouring 7 for nominal temperature, but the
    detailed EES Figure 4 constraints are not fully identifiable.
    Defaults deliberately retain the initial 7/8 mapping.
    """
    if low_pressure_point not in (7, 8) or low_temperature_point not in (7, 8):
        raise DomainError("low-side mapping must use paper point 7 or 8")
    # Paper Table 2: 7 -> 8 adiabatic piping loses 40 kPa.
    p8 = low_pressure_pa - 40e3 if low_pressure_point == 7 else low_pressure_pa
    p = fr2016_pressure_map(high_pressure_pa, p8)
    s: dict[int, State] = {}
    s[1] = props.tp(p[1], high_temperature_k)
    s[2] = props.ph(p[2], s[1].h)  # adiabatic 1-2 piping
    s[3] = props.ph(p[3], turbine_outlet(
        s[2].h, props.ps(p[3], s[2].s).h, eta_turbine))
    s[4] = props.ph(p[4], s[3].h)  # adiabatic 3-4 piping

    if low_temperature_point == 7:
        s[7] = props.tp(p[7], low_temperature_k)
        s[8] = props.ph(p[8], s[7].h)  # adiabatic 7-8 piping
    else:
        s[8] = props.tp(p[8], low_temperature_k)
        s[7] = props.ph(p[7], s[8].h)  # reverse isenthalpic mapping
    s[9] = props.ph(p[9], compressor_outlet(
        s[8].h, props.ps(p[9], s[8].s).h, eta_compressor))
    s[10] = props.ph(p[10], s[9].h)  # adiabatic 9-10 piping

    recup = segmented_recuperator(
        props, cold=s[10], hot=s[4],
        p_cold_out=p[11], p_hot_out=p[5],
        m_cold=1.0, m_hot=1.0,
        effectiveness=recuperator_effectiveness, n=segments)
    s[11] = recup.cold_out
    s[5] = recup.hot_out
    s[12] = props.ph(p[12], s[11].h)  # adiabatic 11-12 piping
    s[6] = props.ph(p[6], s[5].h)  # adiabatic 5-6 piping

    wt = s[2].h - s[3].h
    wc = s[9].h - s[8].h
    qin = s[1].h - s[12].h
    qout = s[6].h - s[7].h
    if not all(isfinite(x) for x in (wt, wc, qin, qout)):
        raise DomainError("non-finite reference cycle")
    if min(wt, wc, qin, qout) <= 0:
        raise DomainError("infeasible reference-cycle power or heat flow")

    residual = qin - qout - (wt - wc)
    if abs(residual) > 1e-7 * max(abs(qin), abs(qout), abs(wt - wc)):
        raise DomainError("reference conceptual cycle energy closure failed")
    return FR2016Comparison(
        points=s,
        w_turbine_j_kg=wt,
        w_compressor_j_kg=wc,
        q_heater_j_kg=qin,
        q_cooler_j_kg=qout,
        eta_thermal=(wt - wc) / qin,
        energy_residual_j_kg=residual,
        recuperator_min_dt_k=recup.min_approach_k,
        recuperator_ua_per_kg_s_w_k=recup.required_ua_w_k,
    )
