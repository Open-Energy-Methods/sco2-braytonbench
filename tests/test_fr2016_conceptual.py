"""This tests source indexing and internal consistency, not EES replication."""
import pytest
from sco2_braytonbench import IdealGasFixture
from sco2_braytonbench.reference_cycle import (
    FR2016_REPORTED, fr2016_conceptual_cycle)

def test_published_table3_aggregate_balance_arithmetic():
    p=FR2016_REPORTED
    assert (p["w_turbine_MW"]-p["w_compressor_MW"])==pytest.approx(24.43)
    assert p["eta_thermal"]==pytest.approx(24.43/100.2)
    # 100.20 + 13.65 - 38.08 - 75.80 = -0.03 MW from rounded print.
    assert p["q_heater_MW"]+p["w_compressor_MW"]-p["w_turbine_MW"]-p["q_cooler_MW"]==pytest.approx(-.03)

@pytest.mark.parametrize("segments",[10,20,30,60])
def test_12_state_conceptual_energy_balance(segments):
    f=fr2016_conceptual_cycle(
       IdealGasFixture(),low_pressure_pa=8.336e6,
       low_temperature_k=304.1282,segments=segments)
    assert len(f.points)==12
    assert abs(f.energy_residual_j_kg)<1e-6
    assert f.recuperator_min_dt_k>=0
    assert f.q_heater_j_kg>0
    assert f.w_compressor_j_kg>0
    assert f.w_turbine_j_kg>0
    m=f.equivalent_MW_at_reported_heater_duty()
    assert m["heater"]==pytest.approx(100.2)
    assert m["turbine"]-m["compressor"]==pytest.approx(m["net"])

def test_source_states_not_our_six_state_labels():
    f=fr2016_conceptual_cycle(IdealGasFixture(),
      low_pressure_pa=8.336e6,low_temperature_k=304.1282)
    assert f.points[1].p==30e6
    assert f.points[2].p==pytest.approx(29.92e6)
    assert f.points[7].p-f.points[8].p==pytest.approx(40e3)
    assert f.points[9].p > f.points[1].p
