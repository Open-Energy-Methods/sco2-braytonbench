"""Structural source-mapping sensitivity, separate from author-model replication."""
import pytest
from sco2_braytonbench import DomainError, IdealGasFixture
from sco2_braytonbench.reference_cycle import fr2016_conceptual_cycle, FR2016_REPORTED

pcrit=7.3773e6
tcrit=304.1282
F=IdealGasFixture()

@pytest.mark.parametrize("p_point",[7,8])
@pytest.mark.parametrize("t_point",[7,8])
def test_all_four_mapping_variants_close_energy(p_point,t_point):
    r=fr2016_conceptual_cycle(F,
        low_pressure_pa=1.13*pcrit,
        low_temperature_k=tcrit,
        low_pressure_point=p_point,
        low_temperature_point=t_point)
    assert len(r.points)==12
    assert abs(r.energy_residual_j_kg)<1e-6
    assert r.points[7].p-r.points[8].p == pytest.approx(40000.,abs=1e-7)
    assert r.points[p_point].p == pytest.approx(1.13*pcrit)
    assert r.points[t_point].t == pytest.approx(tcrit)

@pytest.mark.parametrize("bad",[0,3,9,10])
def test_invalid_boundary_state_rejected(bad):
    with pytest.raises(DomainError):
        fr2016_conceptual_cycle(F,
           low_pressure_pa=1.13*pcrit,low_temperature_k=tcrit,
           low_temperature_point=bad)

def test_published_aggregate_does_not_identify_two_turbine_branch_powers():
    # Table 3 gives only the total aggregate. Distinct partitions yield
    # identical aggregate power, demonstrating numerical non-uniqueness
    # without claiming that either split is physically feasible.
    W=FR2016_REPORTED["w_turbine_MW"]
    for fraction in (.2,.8):
        main=fraction*W
        aux=(1-fraction)*W
        assert main+aux==pytest.approx(W)
    assert .2*W!=.8*W
