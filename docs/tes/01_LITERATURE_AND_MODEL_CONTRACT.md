# TES-v0.1 — Literature and physical-model contract

**Status:** Proposed scientific acceptance; code branch is TES PR #31. Numerical acceptance requires successful exact-head GitHub CI, not document authorship.

**Scope:** constant-property, 1-D, two-temperature (fluid/solid) *sensible packed-bed* thermal storage. This is **not** CFD, PCM, a two-tank reservoir, a liquid-piston, a dynamic sCO₂ fluid inventory or any specific CIC energiGUNE experiment.

## Source dossier

- Schumann, T. E. W. (1929), *Heat transfer: A liquid flowing through a porous prism*, Journal of the Franklin Institute, 208(3), 405–416; DOI [10.1016/S0016-0032(29)91186-8](https://doi.org/10.1016/S0016-0032(29)91186-8). The publisher abstract confirms the step inlet, initially uniform porous prism, adiabatic sides and Bessel-related analytical solution. **The complete original paper was not publicly recovered in this review; we do not claim to have checked its full tables.**
- Avallone, F. (2018), *Modeling of a Thermocline Thermal Energy Storage: application to a Concentrating Solar Power plant*, Politecnico di Milano, [institutional thesis](https://www.politesi.polimi.it/retrieve/a81cb05c-dcd3-616b-e053-1605fe0a889a/Thesis_Avallone.pdf), section 3.2.1. Describes Schumann fluid/solid equations, no axial conduction, constant properties, plug flow and adiabatic boundaries; source for reconstructed PDE context.
- Furnas, C. C. (1932), *Heat Transfer From a Gas Stream to a Bed of Broken Solids*, [UNT Digital Library](https://digital.library.unt.edu/ark:/67531/metadc12530/m1/17/): secondary historical interpretation and assumptions, not present-study experimental validation.

No source document or copyrighted numerical dataset is copied into the repository. The benchmark below is a newly derived analytical evaluation of the standard ideal PDE, not a transcription of Schumann’s graphs.

## Dimensionally correct field equations

For positive flow in +x and total **bulk** bed area A [m²]:

\[
\epsilon\rho_f c_f\,\partial_t T_f+
(\dot m c_f/A)\,\partial_x T_f=
H_v(T_s-T_f),
\]

\[
(1-\epsilon)\rho_s c_s\,\partial_t T_s=
H_v(T_f-T_s).
\]

Here porosity 0<epsilon<1, fluid and solid density [kg/m³], cp [J/(kg K)], volumetric gas–solid conductance Hv [W/(m³ K)] **per total packed-bed volume**, and mass flow [kg/s]. The advection term must contain A; do not multiply a pore velocity by epsilon twice.

An N-cell upwind **finite-volume** approximation uses cell volume V=A L/N and:

\[
C_{f,i}=\epsilon\rho_f c_f V;\qquad
C_{s,i}=(1-\epsilon)\rho_s c_s V;\qquad
H_i=H_v V.
\]

\[
C_{f,i}\,\dot T_{f,i}=|\dot m|c_f(T_{\rm upstream,i}-T_{f,i})+
H_i(T_{s,i}-T_{f,i}),
\]
\[
C_{s,i}\,\dot T_{s,i}=H_i(T_{f,i}-T_{s,i}).
\]

The left boundary is the inlet for positive flow; the right boundary is the inlet for negative flow. Both preserve the same solid coordinates. At zero flow, there is heat exchange in each cell but **no** boundary enthalpy exchange.

## First-law boundary identity

Total sensible energy relative to any constant reference:

\[
U=\sum_i \{C_{f,i}(T_{f,i}-T_{ref})+
C_{s,i}(T_{s,i}-T_{ref})\}.
\]

By telescoping the internal fluid fluxes and cancelling equal/opposite interphase transfer,

\[
dU/dt=|\dot m|c_f(T_{in}-T_{out}).
\]

The solver uses SSPRK3 with boundary heat evaluated using **the same RK stage weights** (1/6,1/6,2/3); numerical energy mismatch should be near floating-point roundoff. A small conservation residual is not evidence of a physically correct experimental Hv or real-bed temperature.

## Positivity and numerical diagnosis

Define advective rate a=|mdot| cp_f / Cf, fluid exchange f=H/Cf, solid exchange s=H/Cs. Every numerical substep obeys dt≤alpha/max(a+f,s), alpha=0.75 by default. Convex forward-Euler stages under this bound are monotone; SSPRK3 preserves that property as a convex method. This ensures physical positivity for positive finite initial/boundary states, but spatial/time **accuracy must be verified separately**.

Report advection Courant a*dt, exchange f*dt and s*dt; a CFL check *alone* misses stiff interphase transfer.

Independent limiting tests:
- Hv=0: isolated upwind fluid advection, solid unchanged.
- mdot=0: each cell an exactly solvable pair of lumped capacitances, equilibrium (Cf Tf0+Cs Ts0)/(Cf+Cs).
- Uniform state equals inlet: exact fixed point.
- Reverse direction: correctly mirrored boundary.
- N variation: total fluid and solid heat capacity are independent of grid.
- Heating then cooling: integrated boundary energy equals full fluid+solid storage change.

## Scientific scope

No pressure drop/momentum equation, phase change, radiation, axial or radial conduction, detailed wall resistance, CO₂ fluid inventory, experimental sensor validation, identified flow-dependent HTCs or facility-specific model is included. Any reference to CIC energiGUNE or HZDR is **motivational only**.

**Honest claim after CI:** Implemented a constant-property 1-D two-temperature TES model with conservative discretization and independent analytical verification. **Not:** experimentally validated thermal storage, CFD, CARBOSOLA/CIC model, nanoporous mechanical storage or trained physical–ML surrogate.
