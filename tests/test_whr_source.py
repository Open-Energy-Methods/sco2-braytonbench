"""SI-unit industrial waste-heat design screening (ANALYTIC fixture only)."""
import pytest
from sco2_braytonbench import CycleInputs,DomainError,IdealGasFixture,PressureLosses
from sco2_braytonbench.whr import (
    WasteGasSource,PlantDesignLimits,evaluate_whr_design,screen_whr_designs,
)

F=IdealGasFixture()
LOSSES=PressureLosses(cold_recup=100e3,heater=150e3,
                      hot_recup=100e3,cooler=50e3)

def design(t4=620.,m=10.,**updates):
    data=dict(p1_pa=8e6,p4_pa=24e6,t1_k=310.,t4_k=t4,
        mdot_kg_s=m,eta_compressor=.89,eta_turbine=.9,
        losses=LOSSES,recuperator_effectiveness=None,
        recuperator_ua_w_k=100e3,segments=12)
    data.update(updates)
    return CycleInputs(**data)

def source(**updates):
    data=dict(inlet_temperature_k=850.,mass_flow_kg_s=30.,
        cp_j_kg_k=1100.,minimum_stack_temperature_k=350.,
        maximum_heater_ua_w_k=500e3,minimum_heater_approach_k=10.,
        dead_state_temperature_k=300.,segments=12)
    data.update(updates)
    return WasteGasSource(**data)

def test_finite_source_mass_energy_and_exergy():
    point=evaluate_whr_design(F,design(),source())
    assert point.net_shaft_power_w>0
    assert point.heater.q_w==pytest.approx(point.cycle.heater_w)
    assert point.heater.gas_out_k<850
    assert point.heater.gas_out_k>350
    assert 0<point.heat_utilization<1
    assert point.first_law_combined_residual_w==pytest.approx(0,abs=1e-7)
    assert point.source_exergy_consumed_w>point.net_shaft_power_w
    assert point.heater.required_ua_w_k<=500e3

def test_source_available_heat_is_finite():
    s=source()
    assert s.available_heat_w==pytest.approx(30*1100*(850-350))

@pytest.mark.parametrize("key,value",[
    ("mass_flow_kg_s",0),("cp_j_kg_k",-100),
    ("minimum_stack_temperature_k",250.),
    ("inlet_temperature_k",340.),
    ("maximum_heater_ua_w_k",0),
    ("minimum_heater_approach_k",-1.),
])
def test_source_domain_rejections(key,value):
    with pytest.raises(DomainError):
        source(**{key:value})

def test_hot_end_temperature_rejected():
    with pytest.raises(DomainError,match="hot-end"):
        evaluate_whr_design(F,design(t4=840),source())

def test_source_stack_or_pinch_constraint_rejected():
    with pytest.raises(DomainError):
        evaluate_whr_design(F,design(m=10),
            source(mass_flow_kg_s=2.))

def test_heater_UA_sizing_cap_rejected():
    with pytest.raises(DomainError,match="UA"):
        evaluate_whr_design(F,design(),
            source(maximum_heater_ua_w_k=100.))

def test_recuperator_must_use_finite_ua():
    with pytest.raises(DomainError,match="finite-UA"):
        evaluate_whr_design(F,design(
            recuperator_effectiveness=.9,recuperator_ua_w_k=None),source())

def test_screen_reports_infeasibilities_and_both_maxima():
    candidates=[
        design(t4=t,m=m)
        for t in (550.,620.,680.,860.)
        for m in (5.,10.,20.)
    ]
    result=screen_whr_designs(F,source(),candidates)
    assert result.evaluated_count==12
    assert len(result.rejected)>0
    assert len(result.feasible)>0
    assert result.maximum_shaft_power.net_shaft_power_w==max(
        x.net_shaft_power_w for x in result.feasible)
    assert result.maximum_cycle_efficiency.cycle_thermal_efficiency==max(
        x.cycle_thermal_efficiency for x in result.feasible)
    assert all(x.reason for x in result.rejected)

def test_no_feasible_candidates_explicit_error():
    with pytest.raises(DomainError,match="no feasible"):
        screen_whr_designs(F,source(),[design(t4=860)])

@pytest.mark.parametrize("bad",[-1.,float("nan")])
def test_minimum_recuperator_approach_constraint_rejects_invalid(bad):
    with pytest.raises(DomainError):
        PlantDesignLimits(minimum_recuperator_approach_k=bad)

def test_cooler_allowance_domain_rejected():
    with pytest.raises(DomainError):
        PlantDesignLimits(maximum_cooler_duty_w=0.)

def test_design_rejected_when_cooler_exceeds_selected_budget():
    base=evaluate_whr_design(F,design(),source())
    assert base.cycle.cooler_w>0
    with pytest.raises(DomainError,match="cooler"):
        evaluate_whr_design(F,design(),source(),limits=PlantDesignLimits(
            maximum_cooler_duty_w=base.cycle.cooler_w/2))

def test_design_rejected_when_recuperator_below_selected_minimum():
    base=evaluate_whr_design(F,design(),source())
    with pytest.raises(DomainError,match="recuperator"):
        evaluate_whr_design(F,design(),source(),limits=PlantDesignLimits(
            minimum_recuperator_approach_k=
            base.cycle.recuperator.min_approach_k+5.))

def test_constraints_change_feasible_grid_count():
    cases=[design(t4=t,m=m) for t in (550.,620.,680.)
           for m in (5.,10.,20.)]
    a=screen_whr_designs(F,source(),cases)
    b=screen_whr_designs(F,source(),cases,limits=PlantDesignLimits(
        maximum_cooler_duty_w=max(x.cycle.cooler_w for x in a.feasible)*.8))
    assert 0<len(b.feasible)<len(a.feasible)
    assert b.evaluated_count==a.evaluated_count
