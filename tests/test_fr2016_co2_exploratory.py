"""Run real-fluid *conceptual* FR2016 comparison, not author-EES replication."""
import pytest
pytest.importorskip("CoolProp")
from CoolProp.CoolProp import PropsSI
from sco2_braytonbench.properties import CoolPropCO2
from sco2_braytonbench.reference_cycle import (
    fr2016_conceptual_cycle, FR2016_REPORTED)

def test_real_co2_conceptual_source_mapping_and_energy():
    r=fr2016_conceptual_cycle(
       CoolPropCO2(),
       low_pressure_pa=1.13*PropsSI("Pcrit","CO2"),
       low_temperature_k=PropsSI("Tcrit","CO2"),
    )
    assert 0<r.eta_thermal<1
    assert len(r.points)==12
    assert abs(r.energy_residual_j_kg)<1e-5
    assert r.recuperator_min_dt_k>=0
    # Deliberately NOT comparing numerical performance against Table 3 with
    # an acceptance threshold. The original EES topology is not identified.
    assert FR2016_REPORTED["eta_thermal"]==pytest.approx(24.43/100.20)
