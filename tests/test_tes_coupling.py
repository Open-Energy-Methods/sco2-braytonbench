"""Physical double-counting audit of single-pass TES->cycle coupling."""
import pytest

from sco2_braytonbench import CycleInputs, IdealGasFixture, PressureLosses
from sco2_braytonbench.thermal_storage import PackedBedSpec, PackedBedState
from sco2_braytonbench.tes_coupling import advance_storage_to_cycle_snapshot


def bed(n=16):
    return PackedBedSpec(
        length_m=1., area_m2=1., porosity=.4,
        fluid_density_kg_m3=10., fluid_cp_j_kg_k=1100.,
        solid_density_kg_m3=2600., solid_cp_j_kg_k=800.,
        interphase_hv_w_m3_k=30000., n_cells=n,
    )


def cycle():
    return CycleInputs(
        p1_pa=8e6, p4_pa=24e6, t1_k=310., t4_k=670.,
        mdot_kg_s=10., eta_compressor=.89, eta_turbine=.90,
        losses=PressureLosses(100e3, 150e3, 100e3, 50e3),
        recuperator_ua_w_k=0., segments=6,
    )


def test_single_pass_ideal_gas_cycle_closes_bed_plus_heater_plus_work():
    s = bed()
    r = advance_storage_to_cycle_snapshot(
        IdealGasFixture(cp=1000., gas_constant=200.),
        cycle(), s, PackedBedState.uniform(s, 850, 850),
        bed_inlet_k=650, mass_flow_kg_s=30, duration_s=.5,
        minimum_gas_heater_exit_k=600, maximum_heater_ua_w_k=200000,
        heater_segments=6,
    )
    assert r.bed_step.energy_boundary_j < 0
    assert r.storage_inventory_rate_w < 0
    assert r.bed_outlet_temperature_k > r.heater_gas_exit_temperature_k > 600
    assert r.bed_outlet_temperature_k > cycle().t4_k + 10
    assert r.heater_to_co2_rate_w > 0
    assert r.shaft_rate_w > 0 and r.cooler_rate_w > 0
    assert abs(r.bed_step.conservation_residual_j) < 1e-4
    assert abs(r.combined_instantaneous_residual_w) <= 1e-7 * r.heater_to_co2_rate_w
    assert r.heater_to_co2_rate_w == pytest.approx(r.cycle_point.cycle.heater_w, rel=1e-7)
    assert r.instantaneous_stage_time == "end_of_interval"


def test_infeasible_bed_hot_end_is_rejected_not_fitted():
    s = bed()
    with pytest.raises(ValueError):
        advance_storage_to_cycle_snapshot(
            IdealGasFixture(cp=1000., gas_constant=200.),
            cycle(), s, PackedBedState.uniform(s, 650, 650),
            bed_inlet_k=650, mass_flow_kg_s=-30, duration_s=.5,
            minimum_gas_heater_exit_k=600, maximum_heater_ua_w_k=200000
        )


def test_source_temperature_below_hot_end_approach_is_rejected():
    s = bed()
    with pytest.raises(Exception, match="cannot support specified"):
        advance_storage_to_cycle_snapshot(
            IdealGasFixture(cp=1000., gas_constant=200.),
            cycle(), s, PackedBedState.uniform(s, 675, 675),
            bed_inlet_k=650, mass_flow_kg_s=30, duration_s=.5,
            minimum_gas_heater_exit_k=600, maximum_heater_ua_w_k=200000
        )


def test_real_co2_single_pass_guarded_smoke():
    pytest.importorskip("CoolProp")
    from sco2_braytonbench import CoolPropCO2
    s = bed(10)
    c = CycleInputs(
        p1_pa=8.5e6,p4_pa=24e6,t1_k=310.,t4_k=600.,
        mdot_kg_s=20.,eta_compressor=.89,eta_turbine=.90,
        losses=PressureLosses(100e3,150e3,100e3,50e3),
        recuperator_ua_w_k=500e3, segments=12
    )
    # Use the existing demonstrated feasible real-fluid source conditions
    # rather than inventing a plant-specific operating point.
    s2 = PackedBedSpec(
        length_m=1,area_m2=1,porosity=.4,
        fluid_density_kg_m3=10,fluid_cp_j_kg_k=1100,
        solid_density_kg_m3=2600,solid_cp_j_kg_k=800,
        interphase_hv_w_m3_k=10000,n_cells=10
    )
    r=advance_storage_to_cycle_snapshot(
        CoolPropCO2(),c,s2,PackedBedState.uniform(s2, 800,800),
        bed_inlet_k=750,mass_flow_kg_s=100,duration_s=.1,
        minimum_gas_heater_exit_k=350,
        maximum_heater_ua_w_k=1e6,heater_segments=12
    )
    assert r.shaft_rate_w > 0
    assert abs(r.combined_instantaneous_residual_w) <= 1e-7 * r.heater_to_co2_rate_w
