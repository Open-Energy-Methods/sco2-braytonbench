"""Multi-point mesh sensitivity of *rated* recuperator, heater and cooler.

This script intentionally DOES NOT assert convergence of the full nested
dual-installed-UA plant. Each state here is prescribed (T1,T4,mdot);
the resulting heater/cooler UAs are *required* ratings, not fixed-UA
plant solutions. That separation avoids a false claim of installed
area consistency. Uses NIST dry-air (N2/O2) and real liquid water.
"""
from dataclasses import replace
from pathlib import Path
from math import isfinite
import json,platform
from CoolProp import __version__ as cp_version
from sco2_braytonbench import CycleInputs, CoolPropCO2,PressureLosses
from sco2_braytonbench.reference_streams import DryAirNISTShomate,CoolPropLiquidWater
from sco2_braytonbench.cycle import solve_cycle
from sco2_braytonbench.cooler import CoolerSink,rate_cooler
from sco2_braytonbench.exchangers import waste_gas_heater

f=CoolPropCO2()
air=DryAirNISTShomate()
water=CoolPropLiquidWater(pressure_pa=300000.,minimum_temperature_k=280.,
                          maximum_temperature_k=340.)
cases=[
    {"name":"near_critical_8p5MPa_310K","p1":8.5e6,"T1":310.,"T4":650.,"mdot":20.,
     "source_inlet":800.},
    {"name":"warmer_low_side_9MPa_314K","p1":9e6,"T1":314.,"T4":690.,"mdot":20.,
     "source_inlet":850.},
]
sizes=(6,12,24,48)
output=[]
for case in cases:
    runs=[]
    for n in sizes:
        c=CycleInputs(
            p1_pa=case["p1"],p4_pa=24e6,t1_k=case["T1"],
            t4_k=case["T4"],mdot_kg_s=case["mdot"],
            eta_compressor=.89,eta_turbine=.9,
            losses=PressureLosses(100e3,150e3,100e3,50e3),
            recuperator_effectiveness=None,recuperator_ua_w_k=200e3,
            segments=n)
        cycle=solve_cycle(f,c)
        heater=waste_gas_heater(
            f,cycle.states[2],cycle.states[3],case["mdot"],
            case["source_inlet"],100.,1100.,10.,n=n,
            gas_property_model=air)
        cooler=rate_cooler(
            f,cycle.states[5],cycle.states[0],case["mdot"],
            CoolerSink(
                inlet_temperature_k=285.,mass_flow_kg_s=75.,
                cp_j_kg_k=4180.,installed_ua_w_k=100e3,
                maximum_outlet_temperature_k=330.,segments=n,
                fluid_property_model=water))
        assert isfinite(heater.required_ua_w_k)
        assert isfinite(cooler.required_ua_w_k)
        assert abs(cooler.coolant_energy_residual_w)<1e-5
        assert abs(cycle.first_law_residual_w)<1e-5
        assert heater.min_approach_k>=10.
        assert cooler.min_approach_k>=5.
        runs.append({
           "n_segments":n,
           "recuperator_duty_w":cycle.recuperator.q_w,
           "recuperator_min_approach_k":cycle.recuperator.min_approach_k,
           "cycle_thermal_efficiency":cycle.thermal_efficiency,
           "net_shaft_power_w":cycle.net_w,
           "recuperator_ua_required_w_k":cycle.recuperator.required_ua_w_k,
           "heater_ua_required_w_k":heater.required_ua_w_k,
           "heater_min_approach_k":heater.min_approach_k,
           "exhaust_outlet_k":heater.gas_out_k,
           "cooler_ua_required_w_k":cooler.required_ua_w_k,
           "cooler_min_approach_k":cooler.minimum_approach_k,
           "coolant_outlet_k":cooler.coolant_outlet_k,
           "cooler_entropy_generation_w_k":cooler.entropy_generation_w_k,
           "cycle_first_law_residual_w":cycle.first_law_residual_w,
           "cooler_first_law_residual_w":cooler.coolant_energy_residual_w,
        })
    def diff_metric(k):
        lo,hi=runs[-2][k],runs[-1][k]
        return {"abs_24_to_48":abs(hi-lo),
                "rel_24_to_48":abs(hi-lo)/max(abs(hi),1e-12)}
    output.append({"case":case,"meshes":runs,
      "adjacent_refinement":{
        k:diff_metric(k) for k in (
           "recuperator_duty_w","recuperator_min_approach_k",
           "cycle_thermal_efficiency",
           "heater_ua_required_w_k","heater_min_approach_k",
           "cooler_ua_required_w_k","cooler_min_approach_k")}})
report={
 "kind":"component-level real-fluid mesh sensitivity at prescribed cycle states",
 "CoolProp_version":cp_version,"python":platform.python_version(),
 "source_props":"NIST JANAF Shomate 79% N2/21% O2 dry ideal mixture",
 "coolant_props":"CoolProp HEOS Water at 0.3 MPa single-phase liquid",
 "pressure_losses":"explicit fixed-Pa nominal assumptions",
 "recuperator_fixed_UA_W_K":200e3,
 "n_segments":list(sizes),"results":output,
 "caveats":[
  "This is an a-posteriori fixed-state component rating study, not the full coupled-UA plant",
  "A 24-to-48 variation is evidence of local resolution dependence, not a mathematical asymptotic convergence proof",
  "Only two selected points and three exchangers; true near-pinch/critical envelope remains under-sampled",
  "Component pressure profiles are assumed linear, and no measured U, roughness or dimensions are used",
  "NIST dry air is not variable-composition combustion exhaust",
  "CoolProp Water at constant P excludes coolant pumping and two-phase transitions",
 ],
 "gate":"G3_PARTIAL"
}
p=Path("evidence/generated/g33_component_mesh_sensitivity.json")
p.parent.mkdir(parents=True,exist_ok=True)
p.write_text(json.dumps(report,indent=2)+"\n")
for block in output:
    print("CASE",block["case"]["name"])
    for x in block["meshes"]:
        print(f"  n={x['n_segments']:2d}: eta={x['cycle_thermal_efficiency']:.8f} "
              f"Qrecup={x['recuperator_duty_w']:.4f} "
              f"heater_UA={x['heater_ua_required_w_k']:.4f} "
              f"cooler_UA={x['cooler_ua_required_w_k']:.4f} "
              f"dTrecup={x['recuperator_min_approach_k']:.6f} "
              f"dTheater={x['heater_min_approach_k']:.6f}")
    print("REFINEMENT_24_48",json.dumps(block["adjacent_refinement"]))
print("Wrote",p)
