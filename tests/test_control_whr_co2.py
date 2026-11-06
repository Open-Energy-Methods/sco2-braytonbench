"""Optional real-CoolProp numerical smoke for the new WP3 bypass energy path.

Hypothetical geometry/UA and thermal capacitance; not an experimental
controller validation, not a CARBOSOLA dynamic data comparison.
"""
import pytest

pytest.importorskip("CoolProp")

from sco2_braytonbench import CoolPropCO2, CycleInputs, PressureLosses, solve_cycle
from sco2_braytonbench.dynamic_whr import (
    FiniteGasLoad, WallCycleEquipment, _co2_wall_rating,
)
from sco2_braytonbench.control_whr import (
    SourceBypass, WallPI, control_performance, simulate_bypass_control,
)


def test_real_co2_bypass_mixing_and_wall_PI_single_step():
    props = CoolPropCO2()
    base = CycleInputs(
        p1_pa=8.5e6,p4_pa=24e6,t1_k=310.,t4_k=650.,
        mdot_kg_s=20.,eta_compressor=.89,eta_turbine=.9,
        losses=PressureLosses(100e3,150e3,100e3,50e3),
        recuperator_ua_w_k=200e3,segments=6,
    )
    # This is a manufactured numerical reference state for inverse
    # equipment sizing, not a value measured on real apparatus.
    point=solve_cycle(props,base)
    ua,approach=_co2_wall_rating(props,point,780.,base.mdot_kg_s,6,2.)
    assert approach > 2.
    equipment=WallCycleEquipment(
        wall_capacity_j_k=1e8,
        gas_to_wall_ua_w_k=40e3,
        wall_to_co2_ua_w_k=ua,
        gas_cp_j_kg_k=1100.,
        minimum_stack_temperature_k=360.,
        t4_bounds_k=(633.,665.),
        co2_heater_segments=6,
        root_scan_intervals=4,
        root_max_iterations=28,
        root_temperature_tolerance_k=.09,
        root_ua_tolerance_relative=3e-4,
    )
    controller=WallPI(
        setpoint_temperature_k=780.,kp_fraction_k=.02,
        ki_fraction_k_s=.001,bias_fraction=.2,
        tracking_gain_s=.2,integral_limit_fraction=.5
    )
    result=simulate_bypass_control(
        props,base,equipment,(FiniteGasLoad(850.,100.,1.),),
        SourceBypass(max_fraction=.85,max_rate_fraction_s=.03,
                     minimum_active_mass_flow_kg_s=1.),
        initial_wall_temperature_k=780.,
        initial_bypass_fraction=.2,
        setpoint_temperature_k=780.,
        controller=controller,
    )
    assert len(result)==1
    row=result[0]
    assert row.active_gas_flow_kg_s==pytest.approx(80.)
    assert row.diverted_gas_flow_kg_s==pytest.approx(20.)
    assert row.bypass_fraction==pytest.approx(.2)
    assert row.mixed_gas_outlet_initial_k > (
        row.plant.initial.hot_gas_outlet_temperature_k
    )
    assert row.plant.final.turbine_inlet_temperature_k==pytest.approx(
        650.,abs=.35
    )
    assert row.plant.net_shaft_energy_j>0
    assert abs(row.source_energy_residual_j)<1e-5
    assert abs(row.combined_total_stream_residual_j)<1e-3
    assert abs(control_performance(result).total_energy_residual_j)<1e-3
