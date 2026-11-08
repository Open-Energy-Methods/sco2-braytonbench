# Liquid-piston and molecular-spring storage — bounded, unvalidated modelling concept

**Classification:** Independent preparatory mathematical exploration only. Not a CIC energiGUNE / COMPETENT experimental result, nanoporous constitutive fit, CFD, hydraulic transient or industrial design. No laboratory access, calibration, facility permission or measurements are implied.

## Research question and physical idealisation

A fixed mass of ideal gas in a gas chamber is compressed/expanded by an incompressible liquid displacement volume of Vp. Define stroke fraction x in [0,1] and gas volume Vg(x)=Vg0−xVp.

Under an **isothermal reversible** reference gas path, Tg=Tg0; pg Vg=pg0 Vg0, and Wg,on=pg0 Vg0 ln(Vg0/Vg1). Gas internal energy change is zero; an equal amount of heat must leave the gas during isothermal compression, and must re-enter for reversible isothermal expansion.

Under a **reversible adiabatic** reference, pg Vg^gamma=pg0 Vg0^gamma, Tg/Tg0=(Vg0/Vg)^(gamma−1). The gas compression work equals its increase in internal energy, and no heat crosses the gas boundary. These two alternative idealised paths are not a validated time-dependent thermal model.

The water-side pressure at each imposed x is:

- Intrusion: p_water,in(x) = pg(x) + p_intrusion
- Extrusion: p_water,out(x) = pg(x) + p_extrusion

with p_intrusion >= p_extrusion >= 0. The two *branch offsets* are externally assumed constants, NOT predictions from Kelvin–Laplace, nanoscale contact angles, pore-size distributions or measured wetting kinetics. They allow a transparent illustration of path dependence.

## Analytic first-law and loop-area audit

For a complete stroke ΔV=Vp:

- Hydraulic input work Win = Wg + p_intrusion ΔV.
- Hydraulic recovered work Wout = Wg + p_extrusion ΔV.
- Hysteresis dissipation Dh = Win − Wout = (p_intrusion−p_extrusion) ΔV >= 0.
- Model-internal recovered-work fraction = Wout / Win (NOT total electrical or real storage efficiency).

The p_extrusion ΔV term is a *recoverable reference surface-energy bookkeeping term*, not a measured microscopic free-energy state. For loading the energy identity is Win=ΔUg+Qg,rejected+p_extrusion ΔV+Dh. Isothermal compression rejects Qg,rejected=Wg with ΔUg=0; reversible adiabatic compression stores ΔUg=Wg with Qg,rejected=0. During the reverse stroke, reversible gas work is returned with the associated thermal-bath heat input (isothermal) or internal-energy decrease (adiabatic). The complete loop returns ideal gas and reference surface state, and mechanical work difference is Dh.

**Thermodynamic warning:** An isothermal ideal gas does not accumulate internal energy, even though it can perform work later by consuming heat from a bath; do not report Win or Wout as an independently calibrated storage energy density. The hysteresis offsets are assumptions, not fitted experimental pressure thresholds.

[Illustrative assumed P–V loop figure](figures/04_liquid_piston_illustrative_pv.svg): pressure range in absolute MPa and intrusion volume in mL, with a labelled *4 kJ model-assumed hysteresis area*. It does **not** show experimental observations or fitted pore constitutive behaviour.

## Explicitly illustrative defaults and reproduction

Vg0=0.002 m³, pg0=10 MPa absolute, Tg0=300 K, R=287 J/(kg K), displaced liquid ΔV=0.0005 m³, intrusion excess pressure=20 MPa and extrusion excess=12 MPa. These values are invented for numerical demonstration, NOT source-derived measurements or COMPETENT equipment specifications.

Run:

    python examples/liquid_piston_concept.py --out evidence/generated/liquid_piston_concept

or compare an idealised reversible-adiabatic gas reference:

    python examples/liquid_piston_concept.py --gas-path reversible_adiabatic --out evidence/generated/liquid_piston_adiabatic

The example writes a pressure, temperature, gas-volume and hydraulic-pressure CSV for both branches plus a JSON energy ledger. Tests independently integrate midpoint p*dV, evaluate fixed-mass ideal-gas PVT, verify adiabatic temperature and energy, volume scaling, positive hysteresis dissipation, identical-path zero hysteresis, finite-domain guards and full-cycle conservation.

## Necessary doctoral research before physical prediction

1. Obtain independently permissioned measured pressure–stroke–temperature/wetting/drying data, material pore structure and mass, liquid composition, thermal boundary conditions and repeat cycles.
2. Replace constant pressures with material-dependent, history-dependent intrusion/extrusion relations for partial pore filling, pressure distributions, temperature, rates and nucleation; fit only to training experiments.
3. Couple non-isothermal gas, hydraulic friction and pumping work, liquid compressibility, wall elasticity and spatially resolved wetting/thermal physics. Assess applicability of real-gas EOS and pore-specific multiphase treatment.
4. Predeclare independent held-out gas pressure, temperature, stroke rate and material families; quantify measurement uncertainty, identifiability and prediction intervals. An identical P–V curve fit alone cannot validate underlying nanopore physics.
5. Conduct experimental and source-independent model review before treating the model as a predictor for a prototype.

## Literature context, without numeric borrowing

- Bratko (2024), Reversible Surface Energy Storage in Molecular-Scale Porous Materials: https://pmc.ncbi.nlm.nih.gov/articles/PMC10856011/
- Partial Water Intrusion and Extrusion in Hydrophobic Nanopores for Thermomechanical Energy Dissipation (2024): https://pmc.ncbi.nlm.nih.gov/articles/PMC11284848/
- Intrusion and extrusion of water in hydrophobic nanopores (2017): https://pmc.ncbi.nlm.nih.gov/articles/PMC5715783/
- Local grafting heterogeneities control water intrusion and extrusion in nanopores (2024): https://www.nature.com/articles/s43246-024-00531-2
- COMPETENT description and consortium: https://orbit.dtu.dk/en/projects/next-generation-of-compressed-air-batteries-for-off-grid-and-crit/

**Provenance distinction:** The literature motivates the problem and warns about nanoscale departures from continuum capillarity. Our default pressures and gas volumes are independent illustrative inputs, not published material values or reproduced experiments. No journal figures/data/PDFs are distributed.

**Release governance:** Original Mantilla ThermoML historical rights #27, qualified independent review #28 and parent release authorization remain distinct unresolved requirements.
