"""TES-v1.0 scientific metamorphic properties and release-failure injection.

These are additional independent invariance/property tests, not proof of
experimental validity or a substitute for external qualified human review.
"""
from __future__ import annotations

from dataclasses import replace
import json
import math
from pathlib import Path

import pytest

from sco2_braytonbench.thermal_storage import (
    PackedBedSpec, PackedBedState, stored_energy_j,
    step_packed_bed,
)
from sco2_braytonbench.tes_metrics import (
    evaluate_tes_performance, thermocline_width_m,
)
from sco2_braytonbench.tes_operating_window import OperatingInputs, run_operating_case
from scripts import tes_v10_research_gate as gate

ROOT=Path(__file__).resolve().parents[1]
GOOD_SHA="a"*40


def spec():
    return PackedBedSpec(1.2,.25,.45,6.,1200.,1800.,850.,1600.,7)


@pytest.mark.parametrize("flow",[-.08,0.,.08])
def test_affine_temperature_equivariance_without_energy_fudge(flow):
    """The linear constant-property PDE commutes with T -> aT+b."""
    s=spec()
    state=PackedBedState(
        tuple(380+5*i for i in range(s.n_cells)),
        tuple(400+3*i for i in range(s.n_cells)),
    )
    a,b=.8,100.
    shifted=PackedBedState(
        tuple(a*t+b for t in state.fluid_k),
        tuple(a*t+b for t in state.solid_k),
    )
    first=step_packed_bed(s,state,inlet_k=620,mdot_kg_s=flow,
                          duration_s=.7,record_outlet_trace=True)
    mapped=step_packed_bed(s,shifted,inlet_k=a*620+b,
                           mdot_kg_s=flow,duration_s=.7,
                           record_outlet_trace=True)
    assert mapped.state.fluid_k == pytest.approx(
        tuple(a*t+b for t in first.state.fluid_k),abs=1e-9
    )
    assert mapped.state.solid_k == pytest.approx(
        tuple(a*t+b for t in first.state.solid_k),abs=1e-9
    )
    assert mapped.outlet_k == pytest.approx(a*first.outlet_k+b,abs=1e-9)
    assert mapped.energy_boundary_j == pytest.approx(
        a*first.energy_boundary_j,abs=1e-7
    )
    assert mapped.outlet_trace is not None
    assert first.outlet_trace is not None
    assert len(mapped.outlet_trace)==len(first.outlet_trace)
    for (t,u),(t2,v) in zip(first.outlet_trace,mapped.outlet_trace):
        assert t == t2
        assert v == pytest.approx(a*u+b,abs=1e-9)


@pytest.mark.parametrize("flow",[-.08,0.,.08])
def test_bulk_area_mass_flow_scaling_conserves_state_and_scales_heat(flow):
    """A->qA, mdot->q*mdot scales every C and H equally."""
    s=spec()
    original=PackedBedState(
        tuple(380+5*i for i in range(s.n_cells)),
        tuple(400+3*i for i in range(s.n_cells)),
    )
    q=3.
    enlarged=replace(s,area_m2=s.area_m2*q)
    first=step_packed_bed(s,original,inlet_k=620,mdot_kg_s=flow,
                          duration_s=.7)
    larger=step_packed_bed(enlarged,original,inlet_k=620,
                           mdot_kg_s=q*flow,duration_s=.7)
    assert larger.state.fluid_k == pytest.approx(first.state.fluid_k,abs=1e-9)
    assert larger.state.solid_k == pytest.approx(first.state.solid_k,abs=1e-9)
    assert larger.energy_boundary_j == pytest.approx(q*first.energy_boundary_j,
                                                     abs=1e-7)
    assert enlarged.total_solid_capacity_j_k == pytest.approx(
        q*s.total_solid_capacity_j_k)
    assert enlarged.total_fluid_capacity_j_k == pytest.approx(
        q*s.total_fluid_capacity_j_k)
    # Re-derive the actual signed energy from the cells, not the solver ledger.
    energy=(
        sum(enlarged.fluid_cell_capacity_j_k*(tf1-tf0)
            for tf0,tf1 in zip(original.fluid_k,larger.state.fluid_k))
        +sum(enlarged.solid_cell_capacity_j_k*(ts1-ts0)
             for ts0,ts1 in zip(original.solid_k,larger.state.solid_k))
    )
    assert energy == pytest.approx(larger.energy_boundary_j,abs=1e-7)


def test_exergy_formula_and_temperature_grade_are_not_the_same_quantity():
    """Closed-form reversible exergy must not be confused with deliverable heat."""
    s=spec()
    state=PackedBedState.uniform(s,550,550)
    reference=300.
    metrics=evaluate_tes_performance(
        s,state,cold_k=350,hot_k=650,ambient_k=reference)
    cf=s.total_fluid_capacity_j_k
    cs=s.total_solid_capacity_j_k
    per_kelvin=550-reference-reference*math.log(550/reference)
    assert metrics.solid_exergy_j == pytest.approx(cs*per_kelvin,rel=1e-12)
    assert metrics.fluid_exergy_j == pytest.approx(cf*per_kelvin,rel=1e-12)
    assert metrics.total_reversible_exergy_j > 0
    cold=PackedBedState.uniform(s,reference,reference)
    zero=evaluate_tes_performance(
        s,cold,cold_k=350,hot_k=650,ambient_k=reference)
    assert abs(zero.total_reversible_exergy_j) < 1e-9
    assert metrics.thermocline_width_m is None


def test_thermocline_width_invariant_under_linear_temperature_transform():
    s=spec()
    state=PackedBedState((425.,)*7,
                         (350.,400.,500.,600.,650.,650.,650.))
    width,ok=thermocline_width_m(s,state,cold_k=350,hot_k=650)
    assert ok and width is not None and width>0
    a,b=1.2,60.
    mapped=PackedBedState(
        tuple(a*t+b for t in state.fluid_k),
        tuple(a*t+b for t in state.solid_k),
    )
    width2,ok2=thermocline_width_m(
        s,mapped,cold_k=a*350+b,hot_k=a*650+b)
    assert ok2
    assert width2 == pytest.approx(width,abs=1e-12)


def test_grade_monotonicity_preserves_full_first_law():
    s=PackedBedSpec(1.,.1,.5,5.,1000.,1000.,700.,500.,8)
    inputs=OperatingInputs(observations_per_stage=8)
    low=run_operating_case(s,replace(inputs,useful_outlet_threshold_k=450))
    high=run_operating_case(s,replace(inputs,useful_outlet_threshold_k=700))
    assert low.recovered_energy_j == pytest.approx(high.recovered_energy_j,
                                                   rel=0,abs=1e-8)
    assert low.charged_energy_j == pytest.approx(high.charged_energy_j,
                                                 rel=0,abs=1e-8)
    assert low.useful_discharge_energy_j >= high.useful_discharge_energy_j
    assert high.useful_discharge_energy_j == 0
    assert high.first_qualified_time_s is None
    assert high.first_downcrossing_time_s is None
    assert low.first_law_relative_residual < 1e-9
    assert high.first_law_relative_residual < 1e-9
    assert not high.complete_cycle
    assert high.gross_round_trip_efficiency is None


def test_candidate_artifact_enumerates_full_scientific_source(tmp_path):
    report=gate.audit(ROOT,GOOD_SHA,tmp_path/"candidate.json")
    assert report["source_file_count"] == len(gate.REQUIRED)
    assert report["source_file_count"] > 30
    assert report["source_commit"] == GOOD_SHA
    assert all(len(x)==64 for x in report["source_file_sha256"].values())
    assert report["release_authorized"] is False
    assert report["pre_release_flags"] == gate.REQUIRED_PRERELEASE_FLAGS
    assert gate.verify(ROOT,tmp_path/"candidate.json",GOOD_SHA)==report


@pytest.mark.parametrize("mutation,match", [
    ({"release_authorized":True},"cannot authorize release"),
    ({"pre_release_flags":{"release_tag_approved":True}},"self-audit cannot"),
    ({"manual_gates":{}},"manual governance"),
    ({"reviewer_identity_asserted_by_this_program":True},"reviewer identity"),
    ({"tags_created":["v1.0.0"]},"tag/DOI"),
    ({"source_commit":"b"*40},"source commit mismatch"),
])
def test_candidate_governance_fraud_is_detected(tmp_path,mutation,match):
    path=tmp_path/"candidate.json"
    report=gate.audit(ROOT,GOOD_SHA,path)
    report.update(mutation)
    path.write_text(json.dumps(report),encoding="utf-8")
    with pytest.raises(ValueError,match=match):
        gate.verify(ROOT,path,GOOD_SHA)


def test_candidate_cannot_silently_modify_source_ledger(tmp_path):
    path=tmp_path/"candidate.json"
    report=gate.audit(ROOT,GOOD_SHA,path)
    manifest=dict(report["source_file_sha256"])
    manifest["src/sco2_braytonbench/thermal_storage.py"]="0"*64
    report["source_file_sha256"]=manifest
    path.write_text(json.dumps(report),encoding="utf8")
    with pytest.raises(ValueError,match="hash mismatch"):
        gate.verify(ROOT,path,GOOD_SHA)


@pytest.mark.parametrize("sha",["main","abc","B"*40,"a"*39,"g"*40])
def test_floating_or_bad_source_revision_is_rejected(sha):
    with pytest.raises(ValueError,match="40-character"):
        gate.normalize_sha(sha)
