"""Small off-design real-CO2 matrix; physical P,T bounds are illustrative."""
import pytest
pytest.importorskip("CoolProp")
from sco2_braytonbench import CycleInputs, CoolPropCO2, PressureLosses
from sco2_braytonbench.whr import WasteGasSource,evaluate_whr_design

F=CoolPropCO2()
LOSS=PressureLosses(cold_recup=100e3,heater=150e3,
                    hot_recup=100e3,cooler=50e3)
SOURCE=WasteGasSource(inlet_temperature_k=800.,
    mass_flow_kg_s=100.,cp_j_kg_k=1100.,
    minimum_stack_temperature_k=350.,
    maximum_heater_ua_w_k=1e6,segments=12)

@pytest.mark.parametrize("t1,p1,t4,m",[
    (310.,8.5e6,600.,20.),
    (315.,8.5e6,650.,20.),
    (320.,9e6,650.,40.),
])
def test_real_co2_multicondition_steady_cycle(t1,p1,t4,m):
    c=CycleInputs(p1_pa=p1,p4_pa=24e6,t1_k=t1,t4_k=t4,
       mdot_kg_s=m,eta_compressor=.89,eta_turbine=.90,
       losses=LOSS,recuperator_effectiveness=None,
       recuperator_ua_w_k=500e3,segments=12)
    point=evaluate_whr_design(F,c,SOURCE)
    assert point.net_shaft_power_w>0
    assert point.cycle.heater_w>0
    assert point.heater.min_approach_k>=SOURCE.minimum_heater_approach_k
    assert point.heat_utilization<=1
    assert abs(point.cycle.first_law_residual_w)<1e-6
    assert abs(point.first_law_combined_residual_w)<1e-6
    assert point.source_exergy_consumed_w>=point.net_shaft_power_w
    assert point.cycle.recuperator.min_approach_k>=0
    s1,s2,s3,s4,s5,s6=point.cycle.states
    assert s2.s>=s1.s-1e-7
    assert s5.s>=s4.s-1e-7
    assert m*(s3.h-s2.h)==pytest.approx(m*(s5.h-s6.h),rel=1e-9)
