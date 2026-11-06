"""Optional, version-pinned CoolProp CO2 numerical WP2b integration smoke.

The installed UAs and wall capacitance are derived/chosen for a
synthetic case, not sourced from CARBOSOLA or any actual hardware.
This checks numerical real-fluid branch compatibility, NOT validation.
"""
from dataclasses import replace

import pytest

pytest.importorskip("CoolProp")

from sco2_braytonbench import (
    CoolPropCO2, CycleInputs, PressureLosses, solve_cycle,
)
from sco2_braytonbench.dynamic_whr import (
    FiniteGasLoad, WallCycleEquipment, _co2_wall_rating,
    solve_wall_cycle_instant, wall_cycle_step,
)


def test_real_co2_fixed_wall_ua_and_single_transient_interval():
    fluid = CoolPropCO2()
    base = CycleInputs(
        p1_pa=8.5e6, p4_pa=24e6, t1_k=310., t4_k=650.,
        mdot_kg_s=20., eta_compressor=.89, eta_turbine=.90,
        losses=PressureLosses(100e3,150e3,100e3,50e3),
        recuperator_ua_w_k=200e3, segments=6,
    )
    # A *new*, hypothetical wall heater is inverse-rated at a chosen
    # nominal real-CO2 cycle point; this is not equipment calibration.
    source_point = solve_cycle(fluid, base)
    ua, minimum = _co2_wall_rating(
        fluid, source_point, 780., base.mdot_kg_s, 6, 2.,
    )
    assert 0 < ua < 1e6
    assert minimum > 2.

    hardware = WallCycleEquipment(
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
    load = FiniteGasLoad(850.,100.,1.)

    rated = solve_wall_cycle_instant(fluid,base,hardware,780.,load)
    assert rated.turbine_inlet_temperature_k == pytest.approx(650.,abs=.3)
    assert rated.co2_wall_required_ua_w_k == pytest.approx(
        ua,rel=hardware.root_ua_tolerance_relative
    )
    assert rated.cycle.heater_w > 0
    assert rated.hot_to_wall_w > 0
    assert rated.hot_gas_outlet_temperature_k > 780.
    assert rated.cycle.first_law_residual_w == pytest.approx(0.,abs=1e-4)

    step = wall_cycle_step(fluid,base,hardware,780.,load)
    assert step.final_wall_temperature_k != pytest.approx(780.,abs=1e-4)
    assert step.final.turbine_inlet_temperature_k > 633.
    assert step.final.turbine_inlet_temperature_k < 665.
    assert abs(step.wall_energy_residual_j) < 1e-4
    assert abs(step.combined_gas_cycle_wall_residual_j) < 1e-3
    assert step.time_end_s == 1.
    assert step.net_shaft_energy_j > 0
