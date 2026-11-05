"""Demonstration with an artificial constant-cp gas — NOT real-CO2 performance."""
from sco2_braytonbench import CycleInputs, IdealGasFixture, PressureLosses, solve_cycle
from sco2_braytonbench.exchangers import waste_gas_heater

c=CycleInputs(
    p1_pa=8e6, p4_pa=25e6, t1_k=310, t4_k=750,
    mdot_kg_s=5, eta_compressor=.89, eta_turbine=.90,
    losses=PressureLosses(cold_recup=30e3, heater=150e3,
                          hot_recup=50e3, cooler=100e3),
    recuperator_effectiveness=.85,
)
r=solve_cycle(IdealGasFixture(), c)
print(f"Analytic fixture net shaft power: {r.net_w/1e3:.2f} kW")
print(f"Analytic fixture efficiency: {r.thermal_efficiency:.4f}")
print(f"First-law residual: {r.first_law_residual_w:.4g} W")
print("NOTE: These values are NOT CO2 data, benchmarks, or CARBOSOLA predictions.")
