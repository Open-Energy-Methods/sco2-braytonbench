"""Unit/exergy/thermocline metrics use independent analytical identities."""
import math
import pytest

from sco2_braytonbench.thermal_storage import PackedBedSpec, PackedBedState
from sco2_braytonbench.tes_metrics import (
    evaluate_tes_performance, flow_exergy_difference_w, thermocline_width_m
)


def spec(n=5):
    return PackedBedSpec(1.,1.,.4,1000.,1000.,2600.,800.,80000.,n)


def test_uniform_hot_bed_capacity_and_independently_derived_exergy():
    s=spec()
    x=PackedBedState.uniform(s,600,600)
    r=evaluate_tes_performance(s,x,cold_k=350,hot_k=650,ambient_k=300)
    assert r.design_solid_capacity_j == pytest.approx(374400000.)
    assert r.design_fluid_capacity_j == pytest.approx(120000000.)
    assert r.solid_sensible_energy_j == pytest.approx(312000000.)
    assert r.fluid_sensible_energy_j == pytest.approx(100000000.)
    expected=(s.total_solid_capacity_j_k+s.total_fluid_capacity_j_k)*(
        600-300-300*math.log(2))
    assert r.total_reversible_exergy_j == pytest.approx(expected, rel=2e-12)
    assert r.total_reversible_exergy_j >= 0
    assert r.thermocline_width_m is None


def test_ambient_equilibrium_has_zero_exergy():
    s=spec()
    z=evaluate_tes_performance(
        s,PackedBedState.uniform(s,300,300),
        cold_k=250,hot_k=600,ambient_k=300)
    assert z.total_reversible_exergy_j == pytest.approx(0,abs=1e-8)


def test_monotonic_profile_gives_exact_10_90_width():
    s=spec()
    x=PackedBedState((500,)*5,(650,575,500,425,350))
    width,monotone=thermocline_width_m(
        s,x,cold_k=350,hot_k=650)
    assert monotone
    assert width==pytest.approx(.64,abs=1e-12)


def test_nonmonotone_and_incomplete_profile_do_not_fabricate_width():
    s=spec()
    odd=PackedBedState((500,)*5,(350,550,400,600,350))
    assert thermocline_width_m(s,odd,cold_k=350,hot_k=650)==(None,False)
    partial=PackedBedState((400,)*5,(450,445,440,435,430))
    assert thermocline_width_m(s,partial,cold_k=350,hot_k=650)==(None,True)


def test_stream_exergy_change_vs_analytical_cp_relation():
    q=flow_exergy_difference_w(2,1000,400,300,300)
    expected=2*1000*(100-300*math.log(4/3))
    assert q==pytest.approx(expected,rel=1e-12)
    assert q>0
    assert flow_exergy_difference_w(0,1000,400,300,300)==0
    assert flow_exergy_difference_w(2,1000,300,400,300)==pytest.approx(-q)


def test_metric_fail_closed_for_invalid_reference_ranges():
    s=spec()
    x=PackedBedState.uniform(s,500,500)
    with pytest.raises(ValueError):
        evaluate_tes_performance(s,x,cold_k=650,hot_k=350,ambient_k=300)
    with pytest.raises(ValueError):
        evaluate_tes_performance(s,x,cold_k=350,hot_k=650,ambient_k=0)
    with pytest.raises(ValueError):
        thermocline_width_m(s,x,cold_k=350,hot_k=650,lower_fraction=.9,upper_fraction=.1)
    with pytest.raises(ValueError):
        flow_exergy_difference_w(-1,1000,400,300,300)
