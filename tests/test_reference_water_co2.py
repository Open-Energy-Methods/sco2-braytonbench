"""CoolProp liquid-water reference model, real-CO2 forward cooler integration."""
import pytest
pytest.importorskip("CoolProp")
from CoolProp.CoolProp import PropsSI
from sco2_braytonbench.reference_streams import CoolPropLiquidWater
from sco2_braytonbench.cooler import CoolerSink,rate_cooler
from sco2_braytonbench import CycleInputs,PressureLosses,CoolPropCO2
from sco2_braytonbench.cycle import solve_cycle
from sco2_braytonbench.properties import DomainError
from sco2_braytonbench.hydraulics import CircularPipe,co2_pipe_loss

W=CoolPropLiquidWater(pressure_pa=300000.,
    minimum_temperature_k=280.,maximum_temperature_k=340.)

@pytest.mark.parametrize("T",[285.,295.,310.,330.])
def test_liquid_water_matches_independent_coolprop_h_s_cp(T):
    assert W.cp(T)==pytest.approx(
        PropsSI("Cpmass","P",300000.,"T",T,"HEOS::Water"))
    assert W.delta_h(285.,T)==pytest.approx(
        PropsSI("Hmass","P",300000.,"T",T,"HEOS::Water")-
        PropsSI("Hmass","P",300000.,"T",285.,"HEOS::Water"))
    assert W.temperature_for_delta_h(285.,W.delta_h(285.,T))==pytest.approx(T,abs=1e-6)

def test_liquid_water_rejects_gas_phase():
    with pytest.raises(DomainError):
        CoolPropLiquidWater(pressure_pa=101325.,
                            minimum_temperature_k=300.,
                            maximum_temperature_k=390.)

def test_water_cooler_with_real_co2_energy_and_entropy():
    c=CycleInputs(p1_pa=8.5e6,p4_pa=24e6,t1_k=310.,t4_k=650.,
        mdot_kg_s=20.,eta_compressor=.89,eta_turbine=.90,
        losses=PressureLosses(100e3,150e3,100e3,50e3),
        recuperator_effectiveness=None,recuperator_ua_w_k=200e3,segments=5)
    r=solve_cycle(CoolPropCO2(),c)
    sink=CoolerSink(inlet_temperature_k=285.,
        mass_flow_kg_s=75.,cp_j_kg_k=4180.,installed_ua_w_k=1e5,
        maximum_outlet_temperature_k=330.,segments=5,
        fluid_property_model=W)
    actual=rate_cooler(CoolPropCO2(),r.states[5],r.states[0],20.,sink)
    assert abs(actual.coolant_energy_residual_w)<1e-8*max(actual.rejected_heat_w,1.)
    assert actual.entropy_generation_w_k>0
    assert 285.<actual.coolant_outlet_k<330.
    assert actual.minimum_approach_k>=sink.minimum_approach_k

def test_CO2_hydraulic_single_point_uses_real_density_and_viscosity():
    x=co2_pipe_loss(CircularPipe(.03,2.,absolute_roughness_m=1e-5),
        1.0,8.5e6,310.)
    assert x.regime=="turbulent_Haaland"
    assert x.pressure_drop_pa>0

def test_nist_air_and_real_water_integrated_dual_ua_inverse():
    """Synthetic dual-UA inverse demonstrates reference property interfaces.

    UAs are sized from this same nominal state so it is a numerically
    independent *inverse* check, not independent plant validation.
    """
    from dataclasses import replace
    from sco2_braytonbench.whr import WasteGasSource,evaluate_whr_design
    from sco2_braytonbench.reference_streams import DryAirNISTShomate
    from sco2_braytonbench.coupled_plant import solve_coupled_plant

    props=CoolPropCO2()
    cycle=CycleInputs(
        p1_pa=8.5e6,p4_pa=24e6,t1_k=310.,t4_k=650.,
        mdot_kg_s=20.,eta_compressor=.89,eta_turbine=.9,
        losses=PressureLosses(100e3,150e3,100e3,50e3),
        recuperator_effectiveness=None,recuperator_ua_w_k=200e3,
        segments=5)
    source=WasteGasSource(
        inlet_temperature_k=800.,mass_flow_kg_s=100.,
        cp_j_kg_k=1100.,minimum_stack_temperature_k=350.,
        maximum_heater_ua_w_k=1.2e6,segments=5,
        gas_property_model=DryAirNISTShomate())
    cold=CoolerSink(
        inlet_temperature_k=285.,mass_flow_kg_s=75.,
        cp_j_kg_k=4180.,installed_ua_w_k=1e5,
        maximum_outlet_temperature_k=330.,segments=5,
        fluid_property_model=W)
    nominal=evaluate_whr_design(props,cycle,source)
    r0=rate_cooler(props,nominal.cycle.states[5],
                   nominal.cycle.states[0],20.,cold)
    cold=replace(cold,installed_ua_w_k=r0.required_ua_w_k)
    x=solve_coupled_plant(
        props,replace(cycle,t1_k=318.,t4_k=620.),
        source,cold,installed_heater_ua_w_k=nominal.heater.required_ua_w_k,
        t1_bounds_k=(306.,314.),t4_bounds_k=(630.,670.),
        outer_scan_intervals=4,outer_max_iterations=12,
        cooler_ua_tolerance_relative=.001,t1_tolerance_k=.12,
        inner_scan_intervals=4,inner_max_iterations=18,
        inner_ua_tolerance_relative=.0002,inner_t4_tolerance_k=.07)
    assert x.compressor_inlet_temperature_k==pytest.approx(310.,abs=.5)
    assert x.turbine_inlet_temperature_k==pytest.approx(650.,abs=.5)
    assert x.cooler_ua_residual_relative<.001
    assert x.heater.ua_residual_relative<.0002
    assert x.cooler.entropy_generation_w_k>0
    assert abs(x.cooler.coolant_energy_residual_w)<1e-8*max(x.cooler.rejected_heat_w,1.)
