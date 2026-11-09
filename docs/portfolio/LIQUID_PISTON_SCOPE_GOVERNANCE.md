# Liquid-piston module — scope governance addendum (9 November 2026)

**Status:** governance correction to parent **0.7.0a0**; documentation-only and **not** a 0.7.1a0 package release, tag, independent scientific sign-off or new research milestone. Documents a departure from the TES-extension master plan that was not recorded at the time it occurred.

## 1. What was restricted, and why

`sCO2_BraytonBench_TES_Extension_Master_Plan_v0.5.md` (Section 9, carried into v1.0 Section 8) stated explicitly that the posting's liquid-piston / molecular-spring storage mechanism should remain "background only — no application document built from this plan should describe this mechanism as modelled, simulated, or implemented." This was a **research-scope restriction**, not only a rule about how results are worded afterward: the plan's own risk register (v0.5 Section 7 / v1.0 Section 5) separately listed "scope creep into the liquid-piston mechanism under interview-prep pressure" as a risk to guard against, distinct from any wording/overclaim risk.

## 2. What actually happened

`liquid_piston_concept.py`, its tests, and `docs/portfolio/LIQUID_PISTON_CONCEPT.md` were implemented and merged as part of the 0.7.0a0 integration, without first revisiting or formally lifting the master plan's restriction. This is a real scope deviation and is recorded as one here, rather than being retrospectively described as consistent with the original plan.

## 3. Assessment of the implementation itself

The implementation is scientifically honest within the scope it claims for itself, and that scope is narrow:

- It correctly distinguishes reversible isothermal/adiabatic gas compression work, hydraulic work from imposed liquid displacement, assumed (not predicted) intrusion/extrusion pressure offsets, and the resulting hysteresis dissipation.
- The 4 kJ illustrative hysteresis figure is a direct, correctly computed consequence of the assumed inputs: (20 − 12) MPa × 0.5 L = 4 kJ. This demonstrates the energy-accounting method, not the hysteresis behaviour of any real hydrophobic nanoporous material.
- The module's internal energy-conservation residual (~10⁻¹²) demonstrates arithmetic self-consistency of the model as written. **It is not evidence that the model's assumptions — constant branch-offset pressures — describe a real molecular-spring system.** Conflating a tight numerical residual with physical validation would be a mistake; this document exists partly to foreclose that reading.

## 4. Decision

| Question | Decision |
|---|---|
| Delete the implementation | No |
| Archive it | No |
| Present it as a validated liquid-piston model | No |
| Retain it as an exploratory, unvalidated thermodynamic concept | **Yes** |
| Document the departure from the master plan | **Yes (this document)** |
| Present it as completed nanoporous-material research in any application | No |

The module is retained, explicitly reclassified as an exploratory, unvalidated thermodynamic concept, kept separate from the verified TES research baseline (Schumann grid-convergence, charge/discharge coupling, the frozen surrogate with its honestly-reported negative OOD result, and the operating-window study) — none of which are affected by this addendum.

## 5. Conditions for any future development

Before this module could support any claim beyond "illustrative energy-ledger exploration," the following would be needed (per `LIQUID_PISTON_CONCEPT.md`'s own "necessary doctoral research" list, restated here as the standing gate):
1. Independently permissioned measured pressure–stroke–temperature/wetting/drying data and material pore structure.
2. Material-dependent, history-dependent intrusion/extrusion relations replacing the constant branch-offset assumption, fitted only to training experiments.
3. Coupling of non-isothermal gas behaviour, hydraulic friction/pumping work, liquid compressibility, and spatially resolved wetting/thermal physics.
4. Predeclared, held-out validation against independent experimental conditions with quantified uncertainty.
5. Experimental and source-independent scientific review before any predictive claim is made.

## 6. Application-document guidance (CIC energiGUNE and any future posting)

- The TES numerical-verification, surrogate-modelling and operating-window work (Sections 2, 4, 5 of `docs/portfolio/README.md`) should carry substantially more weight in any application than the liquid-piston concept — it is the verified research baseline; the liquid-piston work is exploratory.
- When the liquid-piston work is mentioned at all, the only defensible description is close to:
  > "Developed an exploratory, energy-consistent gas-liquid displacement model illustrating reversible compression work and prescribed pressure-volume hysteresis, while identifying the additional constitutive physics and experimental data required for nanoporous liquid-piston storage modelling."
- No application document should use language implying the hysteresis behaviour, pressure offsets, or energy-storage performance of a real nanoporous material has been modelled, predicted, or validated.

## 7. Integration record and limits of approval

- Reviewed scope decision: retain the illustrative source as a separately classified, unvalidated research concept. No change to numerical TES verification or frozen ML evidence.
- Parent head at decision: `350dae300a14df433c2f9d1e7c85d26fe13ef410` (merge PR #45); the explanatory research figure is an assumed-input illustration, not measured P-V-T data.
- This addendum is a maintainer scope clarification **only**. It does not constitute independent thermodynamics/software release review, copyright/data-rights approval, laboratory validation, or authorization for a stable version tag. Existing repository review/rights issues #27/#28 remain open.
