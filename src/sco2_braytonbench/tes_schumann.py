"""Independent Schumann/Anzelius constant-property inlet-step reference.

This evaluates the continuous, zero-axial-conduction, two-temperature
Schumann equations, independently of thermal_storage.py's finite-volume
discretisation.  Derivation: Laplace transformation in retarded time
tau=t-x/u gives

  F(x,s) = exp[-a s/(s+b)] / s
  S(x,s) = b/(s+b) F(x,s),

  a=Hv*A*x/(mdot*cp_f), b=Hv/[(1-eps)*rho_s*cp_s].

Expanding exp(a*b/(s+b)) yields Poisson series. For z=b*(t-x/u):
  theta_fluid = P[ Poisson(a) <= Poisson(z) ]
  theta_solid = P[ Poisson(a) <  Poisson(z) ].

The Poisson series is evaluated by independent recurrences rather than
using the numerical bed ODE or its spatial stencil. Step value at the
characteristic arrival t=x/u is the right-hand limit.

References: T.E.W. Schumann (1929), DOI:10.1016/S0016-0032(29)91186-8;
F. Avallone (2018), *Modeling of a Thermocline Thermal Energy Storage*,
Politecnico di Milano, section 3.2.1.
"""
from __future__ import annotations
from dataclasses import dataclass
import math

from .thermal_storage import PackedBedSpec, _finite


@dataclass(frozen=True)
class SchumannStep:
    fluid_k: float
    solid_k: float
    reduced_length: float
    reduced_time: float
    pore_transit_s: float


def _poisson_comparison(a: float, z: float) -> tuple[float, float]:
    """Return P(Poisson(a)<=Poisson(z)), P(Poisson(a)<Poisson(z)).

    The finite loop terminates when the Poisson(z) tail is small. Limited
    to moderate dimensionless benchmark inputs to avoid false precision.
    """
    if a < 0 or z < 0 or a > 35 or z > 60:
        raise ValueError("analytical series benchmark requires 0<=a<=35, 0<=z<=60")
    pz = math.exp(-z)
    pa = math.exp(-a)
    cdfa = 0.0
    fluid = 0.0
    solid = 0.0
    mass_z = 0.0
    for k in range(600):
        solid += pz * cdfa
        cdfa += pa
        fluid += pz * cdfa
        mass_z += pz
        if k > max(z + 15, a + 15) and (1.0 - mass_z) < 2e-14:
            return min(1.0, fluid), min(1.0, solid)
        pa *= a / (k + 1)
        pz *= z / (k + 1)
    raise ArithmeticError("Poisson-series truncation not converged")


def schumann_inlet_step(
    spec: PackedBedSpec, *,
    x_m: float,
    t_s: float,
    mdot_kg_s: float,
    initial_k: float,
    inlet_k: float,
) -> SchumannStep:
    """Exact *continuous-PDE* temperature response for positive plug flow.

    Applies to a bed initially at the same uniform fluid/solid T. At
    t=0 the inlet jumps to the held inlet_k. No axial conduction,
    constant properties, no losses, no solid particle gradients.
    """
    x = _finite("x_m", x_m)
    t = _finite("t_s", t_s)
    flow = _finite("mdot_kg_s", mdot_kg_s, positive=True)
    cold = _finite("initial_k", initial_k, positive=True)
    hot = _finite("inlet_k", inlet_k, positive=True)
    if not (0 <= x <= spec.length_m) or t < 0:
        raise ValueError("x_m must be in [0, length_m] and t_s >=0")
    u = flow / (spec.porosity * spec.fluid_density_kg_m3 * spec.area_m2)
    transit = x / u
    a = (spec.interphase_hv_w_m3_k * spec.area_m2
         * x / (flow * spec.fluid_cp_j_kg_k))
    b = (spec.interphase_hv_w_m3_k
         / ((1.0 - spec.porosity) * spec.solid_density_kg_m3
            * spec.solid_cp_j_kg_k))
    z = b * max(0.0, t - transit)
    if t < transit:
        return SchumannStep(cold, cold, a, 0.0, transit)
    thf, ths = _poisson_comparison(a, z)
    span = hot - cold
    return SchumannStep(cold + span * thf, cold + span * ths,
                        a, z, transit)
