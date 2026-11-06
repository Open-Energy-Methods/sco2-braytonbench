# v1 pre-release technical audit — 6 November 2026

**Scope:** draft PRs #22, #23, #24, #25 and #26 in `Open-Energy-Methods/sco2-braytonbench`; release target = **numerically verified research software**, NOT experimentally validated plant hardware. **Audit author:** ChatGPT-assisted code and mathematical review. This is **not a separate, independent human peer-review sign-off**. **Decision:** integration may proceed as `0.5.0a0` research development if all stacked CI passes; v1.0 tagging remains **BLOCKED** pending human review and [data-rights issue #27](https://github.com/Open-Energy-Methods/sco2-braytonbench/issues/27).

## 1. Reviewed immutable PR heads and evidence

| PR | Reviewed head SHA | Boundary |
|---|---|---|
| [#22](https://github.com/Open-Energy-Methods/sco2-braytonbench/pull/22) | `62b884cb8e217b8e430aa595164d4ce32e0493a8` | WP0/1/2a — release contract, domain guards, exact lumped thermal ODE |
| [#23](https://github.com/Open-Energy-Methods/sco2-braytonbench/pull/23) | `6fc266a20ee2a72fc92a2f9885c7a1b8b252b097` | WP2b — finite gas→wall→quasi-steady Brayton cycle |
| [#24](https://github.com/Open-Energy-Methods/sco2-braytonbench/pull/24) | `46862faa1f59eac8dc1dd2af7a320c86f2eb9889` | WP3 — bypass mass split, mixer, sampled PI |
| [#25](https://github.com/Open-Energy-Methods/sco2-braytonbench/pull/25) | `17721aa249f74246bac5b7f1867945ba275bfdd4` | WP4 — prospective 35-channel/13-case metrology and validation design |
| [#26](https://github.com/Open-Energy-Methods/sco2-braytonbench/pull/26) | Initially `b86d0420827ca9b6f7e8fa30dd9b821a6e39bf63`; subsequently strengthened on same draft branch | WP5 — package/reproducibility gates and quarantined NIST data |

Original WP5 head [run #42253583972](https://github.com/Open-Energy-Methods/sco2-braytonbench/actions/runs/42253583972) completed **20/20 jobs successful**, no failures; each of Python 3.10, 3.11, 3.12 passed **474 tests + 11 optional skips**. Dedicated pinned CoolProp tests and two independent fresh wheel/sdist replays passed. The **changed final head and integrated `main` have to be tested separately**; this earlier result cannot be used to approve a different commit.

## 2. Independent arithmetic of WP2a/WP2b model equations

### WP2a single isothermal wall

The model equation is `C dTw/dt=Kh(Th-Tw)-Kc(Tw-Tc)` at constant inputs, with equilibrium `Teq=(Kh Th+Kc Tc)/(Kh+Kc)`, time constant `tau=C/(Kh+Kc)` and exact `Tw(t)=Teq+(Tw0-Teq) exp(-t/tau)`. Integrating each signed heat rate using **mean wall temperature**, rather than final wall state, correctly yields `Ehot-Ecold=C(Tw_new-Tw_old)`. The dedicated tests exercise the closed-form limit, constant-input many-steps equivalence and sign changes. The wall is an idealized solid **not** a CO₂ fluid inventory.

### WP2b independently re-derived constant-cp/zero-recuperator fixture

From textbook ideal-gas isentropic compression (not the WP2b code), using `P1=8 MPa`, `P4=24 MPa`, pressure rises from prescribed cold-recuperator/heater losses to `P2=24.25 MPa`, `T1=310 K`, `R/cp=0.2`, `eta_c=0.89`:

```text
T3 = T1 + T1 * ((P2/P1)^(R/cp)-1)/eta_c
   = 396.4919038409815 K
```

At synthetic wall 700 K, CO₂ `m cp=10,000 W/K`, `UA_wall,CO2=25,000 W/K`:

```text
T4 = 700 - (700-T3)*exp(-25000/10000)
   = 675.0865383444448 K
H_CO2 = 10000*(1-exp(-2.5))
      = 9179.150013761011 W/K
```

With synthetic exhaust `m cp=30*1100=33,000 W/K`, `UA_g,w=40,000 W/K`:

```text
H_g = 33000*(1-exp(-40000/33000))
    = 23180.341465130343 W/K
Twall,eq = (H_g*850 + H_CO2*T3)/(H_g+H_CO2)
         = 721.3570993594179 K
tau = 2e6/(H_g+H_CO2) = 61.80566840194736 s
Twall(60s) = Twall,eq+(700-Twall,eq)*exp(-60/tau)
           = 713.2673361368766 K
```

These independent numerical targets **agree with** the values asserted in `docs/G4_WP2B_FINITE_SOURCE_WALL_CYCLE.md`. The underlying assumption is a constant-property gas stream into an isothermal solid wall and an installed-UA state-3→4 CO₂ heating path, with a six-state **quasi-steady** power block. It does **not** prove a full dynamic CO₂ Brayton cycle, pressure/mass storage, actual casing `C` or real machine maps.

**Source-integrated first law:** `Eg=Delta_Uwall+Ecooler+Enet`. The software integrates heat rates and shaft/cooler duties at matching RK4 stage weights; small residuals verify **algebraic consistency by construction**. An independent exact ideal-gas exponential and time-step refinement are separate numerical verification. Neither makes an assertion about independent real experimental data.

## 3. WP3 bypass and PI physical interpretation

For a constant-cp source, `m_active=(1-b)m_total`, `m_bypass=b*m_total`, and `Tmix=(1-b)Tactive_exit+b*Tin`. Therefore `m_total cp (Tin-Tmix)=m_active cp (Tin-Tactive_exit)`, which equals the gas-to-wall transfer. The bypass does **not** introduce a second heater.

Sample PI uses `error=Twall-Tsetpoint`, so a hotter wall **increases** bypass and reduces heat recovery. The `Kaw*(u_actual-u_raw)` back-calculation acts on achieved **sample-limited** bypass and is consistent with anti-windup. **Important physical limit:** the implemented `max_rate_fraction_s` constrains the **difference between successive held samples divided by sample duration**. It does *not* integrate a continuously moving valve position within that interval; the solver applies the next bypass fraction over the whole interval. Hence describe it as a *discrete sample-to-sample slew bound*, **not a measured continuously rate-limited actuator** or calibrated valve `Cv`.

An executed **synthetic**, not real-CO₂, matched experiment: endpoint RMSE `11.4628 K → 1.7170 K` (85.02% lower); approximate IAE `812.852 → 140.642 K·s` (82.70% lower); predicted net shaft energy `29.69393 MJ → 28.61394 MJ` (3.64% **lower**) because diverting hot gas sacrifices some recovery. No universal PI superiority, closed-loop stability across arbitrary disturbances, measured system safety or technoeconomic optimality established.

## 4. WP4 metrology and identifiability

For the illustrative constant-cp source heat duty `Q=m cp(Tin-Tout)`, first-order GUM sensitivity variance with independent `m,cp` and temperature correlation `rho` is

```text
u(Q)^2 = (cp*DeltaT*u_m)^2 + (m*DeltaT*u_cp)^2
        + (m*cp)^2 * (u_Tin^2 + u_Tout^2 -2*rho*u_Tin*u_Tout).
```

For `m=2±0.1 kg/s, cp=1000±20 J/kg/K, Tin=400±1 K, Tout=350±2 K` at `rho=0.25`, independent arithmetic gives `Q=100000 W`, variance `45,000,000 W²` and standard `u(Q)=6708.2039325 W` (`k=1`). This is a toy mathematical check, **not CARBOSOLA metrology**. Local Jacobian rank does not establish global identifiability or accurate `UA,Cwall` estimates. No channel is known to be installed/calibrated, and no test is authorized.

## 5. Source/licensing and research-evidence audit

- **Stuttgart:** original Mendeley Data landing page lists **CC BY 4.0** for Theologou et al. (2022) [10.17632/4mvk4nxrkz.1](https://data.mendeley.com/datasets/4mvk4nxrkz/1). The source-extracted 54-run/2,508-axial-record tables require clear original attribution, adapted notice and source preservation. No claim of full independent HTC prediction: many correlations are outside their fitted envelope, and STU-001 source anomaly remains unchanged/quarantined.
- **Mantilla ThermoML:** archive publisher permission is not explicit downstream grant for repackaging an entire 49-observation study. See [data-rights dossier](../DATA_RIGHTS_V1.md) and [issue #27](https://github.com/Open-Energy-Methods/sco2-braytonbench/issues/27). Candidate source archive intentionally **excludes** the transcribed CSV pending written permission, while retaining provenance. Existing public Git visibility must be reviewed separately.
- **Kim (2019):** historical `Nu_fc` exponent sign ambiguity [issue #20](https://github.com/Open-Energy-Methods/sco2-braytonbench/issues/20) remains unresolved. Do not merge experimental [PR #19](https://github.com/Open-Energy-Methods/sco2-braytonbench/pull/19) into the stable v1 line without source confirmation. Equations/coefficients source copied as research hypotheses are not original-paper replication.
- **Other source-model comparisons:** Friedman–Rapp is a 12-state *conceptual* comparator; underlying detailed EES plant is not recovered. The fixed 54-run Stuttgart benchmark with out-of-domain correlation performance is negative/limited evidence, not hardware prediction.

## 6. Release acceptance / unresolved risks

| Gate | Finding |
|---|---|
| WP5 alpha branch full CI at `b86d0420` | **PASS:** 20/20 jobs, plus 474 general tests on each Python version and separate CoolProp runs. |
| Changed final WP5 branch after archive/quarantine and audit | **PENDING new head CI** until matching run completes. |
| Final integrated `main` CI | **PENDING** until sequential merge commits exist. |
| Current planned release version | **0.5.0a0**, not `1.0.0rc1` or `1.0.0`. |
| Dataset redistribution | **PARTIAL:** Stuttgart CC BY confirmed; Mantilla archive remains blocked and excluded. |
| Independent *human* scientific and source licence review | **NOT DONE:** this AI-assisted adversarial desk review is not an independent qualified sign-off. |
| Future experimental CO₂ cycle/thermal/control validation | **OUT OF SCOPE:** must remain transparently excluded from v1 research-software claims. |
| Tag/Zenodo DOI | **NO RELEASE AUTHORIZED** before independent review and permission resolution. |

**Code-integration decision:** it is permissible to merge reviewable research development stages #22–#26 into `main` under their explicit **alpha** status once their CI and exact ancestry are confirmed. This is a *development merge*, not a claim that all publication/reuse rights and experimental validation are settled. The author of this audit did not operate any real sCO₂ system, verify mounted sensors, or review confidential proprietary instrumentation.
