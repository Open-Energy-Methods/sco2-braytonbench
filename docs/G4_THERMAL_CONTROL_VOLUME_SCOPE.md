# G4-0 — analytically verifiable thermal-wall control-volume foundation

**Status:** staged demonstration for v1.0 WP2a. **NOT** a transient Brayton-cycle, CO₂-inventory dynamic model, heat-exchanger design correlation, or HZDR/CARBOSOLA simulation.

## Physical boundary

One lumped solid thermal mass, temperature `T_w` [K], thermal capacitance `C_w > 0` [J/K], exchanges heat with two *prescribed* infinite thermal reservoirs at `T_hot` and `T_cold` [K] through separately declared constant conductances `K_h, K_c >= 0` [W/K] (at least one nonzero).

```text
HOT THERMAL BOUNDARY -- Q_h --> [ wall: C_w * T_w ] -- Q_c --> COLD THERMAL BOUNDARY
```

The rates are signed with the arrows above. A negative rate indicates heat flow opposite the arrow, not an invalid equation. The wall's first law is:

```math
C_w dT_w/dt = K_h (T_hot - T_w) - K_c (T_w - T_cold)
```

At constant inputs within one interval `dt > 0`:

```text
K_sum = K_h + K_c
T_eq = (K_h*T_hot + K_c*T_cold) / K_sum
tau = C_w / K_sum
T_new = T_eq + (T_old - T_eq)*exp(-dt/tau)
T_wall,avg = T_eq + (T_old - T_eq)*(1-exp(-dt/tau))/(dt/tau)
E_hot = K_h*(T_hot - T_wall,avg)*dt
E_cold = K_c*(T_wall,avg - T_cold)*dt
ΔU_wall = C_w*(T_new - T_old) = E_hot - E_cold
```

Use `expm1`-stable formulas for the small-`dt/tau` limit. The numerical residual is `E_hot - E_cold - ΔU_wall`. All energy terms are signed Joules. A piecewise-constant profile exactly advances this *specified linear model* over each step. This is an analytical model, not a claim of physically measured `K` or `C`.

## Accepted verification

- **One interval:** compare the solved wall state with a separately derived exponential solution.
- **Energy:** wall storage equals time-integrated hot-minus-cold transfer, not just endpoint power-rate balance.
- **Time discretisation:** for unchanged thermal boundaries, one long interval and many smaller intervals have matching final temperature and total energies (within floating-point tolerance).
- **Limits:** equilibrium input gives constant wall state; zero-duration/invalid/nonfinite inputs fail with `DomainError`.
- **Reversibility:** a hotter wall may release heat back toward the nominal hot reservoir; this is still the signed first law.
- **Provenance:** example conductances/capacitance are transparently hypothetical, not fitted CARBOSOLA hardware parameters.

## Beyond this module: WP2b/G4 then full cycle

The existing `solve_coupled_plant` is an algebraic steady-state **two-UA boundary-value solver**. Running it repeatedly under time-varying source temperature does **not** automatically produce CO₂ mass inventory dynamics. A future coupling must define the heat-transfer boundary and stored-energy relation consistently and avoid counting the same exchanger heat twice.

Full variable inventory requires at minimum `dm/dt=Σm_in-Σm_out`, `dU/dt=Σ(mh)_in-Σ(mh)_out+Q-W`, volume/pressure closure and robust `(rho,u)->(p,T)` or equivalent real-fluid inversions, validated across the admissible phase envelope. Pressure dynamics, shaft inertia, machine maps, actuator valve flow and safety protection are all separate OPEN requirements.

The numerical module here may be used as a **thermal dynamics primitive** in research scenarios. It must not be described as a complete transient sCO₂ Brayton-cycle solver or a benchmark against CARBOSOLA experiments.
