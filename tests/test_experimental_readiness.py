"""WP4 prospective metrology: no plant calibration or experiment is asserted."""
from dataclasses import replace
from math import sqrt

import pytest

from sco2_braytonbench.experimental_readiness import (
    ChannelUncertainty, DomainError,
    experimental_readiness_gate, load_sensor_register, load_test_matrix,
    load_uncertainty_register, local_sensitivity_rank,
    sensible_duty_uncertainty, validate_long_series,
)

from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
P = ROOT / "protocols" / "wp4"


def sensors():
    return load_sensor_register(P/"measurement_channels.csv")


def uncertainty():
    return load_uncertainty_register(P/"uncertainty_register.csv", sensors())


def test_prospective_register_and_13_case_matrix_parse_with_no_claimed_data():
    s=sensors()
    plans=load_test_matrix(P/"prospective_test_matrix.csv",s)
    assert len(s)==35
    assert len(plans)==13
    assert all(v.availability=="unconfirmed" for v in s.values())
    assert all(v.calibration_status=="unconfirmed" for v in s.values())
    assert all(v.time_sync_status=="unconfirmed" for v in s.values())
    assert all(row["approval_status"]=="not_requested" for row in plans)
    assert all(row["data_class"]=="proposed" for row in plans)
    assert s["SRC_GAS_CP"].unit=="J/(kg K)"
    assert any("CO2_T5" in row["required_tags"] for row in plans)==False


def test_uncertainty_register_contains_no_fabricated_standard_uncertainties():
    vals=uncertainty()
    assert len(vals)==len(sensors())
    assert all(x.status=="unconfirmed" and x.u_standard is None
               for x in vals.values())
    assert all(x.reference_id=="" for x in vals.values())


def test_readiness_gate_fails_without_calibration_timing_or_approval():
    gate=experimental_readiness_gate(
        ["SRC_T_IN","SRC_T_OUT_ACTIVE","SRC_MDOT_TOTAL","SRC_GAS_CP"],
        sensors(),uncertainty()
    )
    assert gate["ready_for_measured_validation"] is False
    assert gate["required_tag_count"]==4
    assert "formal facility run authorization not verified" in gate["blockers"]
    assert any("SRC_T_IN: current calibration" in x for x in gate["blockers"])
    assert any("SRC_GAS_CP: standard uncertainty" in x for x in gate["blockers"])


def test_generator_required_tags_not_silently_consumed_in_gate():
    g=experimental_readiness_gate(
        (tag for tag in ["SRC_T_IN","SRC_T_OUT_ACTIVE"]),
        sensors(),uncertainty()
    )
    assert g["required_tag_count"]==2
    assert g["ready_for_measured_validation"] is False


def test_gate_can_only_pass_with_explicitly_satisfied_fields_in_test_fixture():
    s=sensors()
    u=uncertainty()
    tag="SRC_T_IN"
    s[tag]=replace(s[tag],availability="installed",
                   calibration_status="current",
                   time_sync_status="verified")
    u[tag]=ChannelUncertainty(tag,"K",0.1,"type_B","synthetic_cert_test","confirmed")
    assert experimental_readiness_gate(
        [tag],s,u,approved_run_authorization=True,
        verified_data_provenance=True
    )["ready_for_measured_validation"] is True
    assert experimental_readiness_gate(
        [tag],s,u,approved_run_authorization=False,
        verified_data_provenance=True
    )["ready_for_measured_validation"] is False


def test_synthetic_long_format_sensor_fixture_has_consistent_si_and_time():
    qc=validate_long_series(
        P/"synthetic_format_fixture.csv",sensors(),
        expected_run_id="SYNTH-WP4-001",max_gap_s=1.5
    )
    assert qc["sample_rows"]==15
    assert qc["channels_seen"]==5
    assert qc["quality_counts"]=={"OK":15,"MISSING":0,"REJECTED":0}
    assert qc["max_gap_violations"]==[]
    assert "NOT_calibration" in qc["evidence_class"]


def test_long_series_detects_gaps_without_inventing_data(tmp_path):
    path=tmp_path/"series.csv"
    text=(P/"synthetic_format_fixture.csv").read_text(encoding="utf-8")
    # Remove one actual synthetic sensor reading from the data stream.
    path.write_text("".join(
        l for l in text.splitlines(keepends=True)
        if not ('"WALL_T_A"' in l and '"1"' in l)
    ),encoding="utf-8")
    qc=validate_long_series(
        path,sensors(),expected_run_id="SYNTH-WP4-001",max_gap_s=1.5
    )
    assert "WALL_T_A" in qc["max_gap_violations"]


@pytest.mark.parametrize("replacement, error",[
    ('"SYNTH-WP4-001","0","SRC_T_IN","nan","K","OK"',
     "nonfinite sensor sample"),
    ('"SYNTH-WP4-001","0","SRC_T_IN","850","Pa","OK"',
     "unit mismatch"),
    ('"OTHER-RUN","0","SRC_T_IN","850","K","OK"',
     "wrong run ID"),
    ('"SYNTH-WP4-001","0","SRC_T_IN","","K","OK"',
     "numeric sample required"),
    ('"SYNTH-WP4-001","0","SRC_T_IN","850","K","MISSING"',
     "missing value must be blank"),
    ('"SYNTH-WP4-001","0","SRC_T_IN","850","K","BAD"',
     "unknown sample quality"),
])
def test_unsafe_data_records_rejected(tmp_path,replacement,error):
    path=tmp_path/"series.csv"
    orig=(P/"synthetic_format_fixture.csv").read_text(encoding="utf-8")
    old='"SYNTH-WP4-001","0","SRC_T_IN","850","K","OK"'
    assert old in orig
    path.write_text(orig.replace(old,replacement,1),encoding="utf-8")
    with pytest.raises(DomainError,match=error):
        validate_long_series(path,sensors(),expected_run_id="SYNTH-WP4-001")


def test_duplicate_timestamp_rejected(tmp_path):
    path=tmp_path/"series.csv"
    orig=(P/"synthetic_format_fixture.csv").read_text(encoding="utf-8")
    orig=orig.replace(
        '"SYNTH-WP4-001","1","SRC_T_IN","850","K","OK"',
        '"SYNTH-WP4-001","0","SRC_T_IN","850","K","OK"',1
    )
    path.write_text(orig,encoding="utf-8")
    with pytest.raises(DomainError,match="duplicate timestamp"):
        validate_long_series(path,sensors(),expected_run_id="SYNTH-WP4-001")


def test_missing_flag_supports_blank_value_without_mislabelled_measurement(tmp_path):
    path=tmp_path/"series.csv"
    orig=(P/"synthetic_format_fixture.csv").read_text(encoding="utf-8")
    orig=orig.replace(
        '"SYNTH-WP4-001","1","SRC_T_IN","850","K","OK"',
        '"SYNTH-WP4-001","1","SRC_T_IN","","K","MISSING"',1
    )
    path.write_text(orig,encoding="utf-8")
    qc=validate_long_series(path,sensors(),expected_run_id="SYNTH-WP4-001")
    assert qc["quality_counts"]["MISSING"]==1
    assert qc["quality_counts"]["OK"]==14


def test_linearized_heat_duty_correlated_standard_uncertainty_by_hand():
    # q = 2*1000*(400-350) = 100 kW
    # variance = (50,000*0.1)^2 + (100*20)^2 +
    # (2,000)^2*(1^2 + 2^2 - 2*0.25*1*2) = 45e6 W^2
    out=sensible_duty_uncertainty(
        2.,1000.,400.,350.,
        u_mass_flow_kg_s=.1,
        u_cp_j_kg_k=20.,
        u_inlet_temperature_k=1.,
        u_outlet_temperature_k=2.,
        inlet_outlet_temperature_correlation=.25
    )
    assert out.heat_rate_w==100000.
    assert out.variance_w2==pytest.approx(45e6)
    assert out.combined_standard_uncertainty_w==pytest.approx(sqrt(45e6))
    assert out.relative_standard_uncertainty==pytest.approx(sqrt(45e6)/1e5)


def test_shared_temperature_calibration_can_cancel_in_temperature_difference():
    out=sensible_duty_uncertainty(
        2.,1000.,400.,350.,
        u_mass_flow_kg_s=0.,
        u_cp_j_kg_k=0.,
        u_inlet_temperature_k=1.,
        u_outlet_temperature_k=1.,
        inlet_outlet_temperature_correlation=1.
    )
    assert out.combined_standard_uncertainty_w==0.
    uncorr=sensible_duty_uncertainty(
        2.,1000.,400.,350.,
        u_mass_flow_kg_s=0.,
        u_cp_j_kg_k=0.,
        u_inlet_temperature_k=1.,
        u_outlet_temperature_k=1.
    )
    assert uncorr.combined_standard_uncertainty_w>0.


def test_zero_temperature_difference_retains_nonzero_uncertainty():
    out=sensible_duty_uncertainty(
        2.,1000.,400.,400.,
        u_mass_flow_kg_s=0.,
        u_cp_j_kg_k=0.,
        u_inlet_temperature_k=1.,
        u_outlet_temperature_k=1.
    )
    assert out.heat_rate_w==0.
    assert out.combined_standard_uncertainty_w>0
    assert out.relative_standard_uncertainty is None


@pytest.mark.parametrize("bad",[-.1,1.1,float("nan"),float("inf"),True])
def test_invalid_correlation_rejected(bad):
    with pytest.raises(DomainError,match="correlation"):
        sensible_duty_uncertainty(
            2.,1000.,400.,350.,u_mass_flow_kg_s=.1,
            u_cp_j_kg_k=20.,u_inlet_temperature_k=1.,
            u_outlet_temperature_k=1.,
            inlet_outlet_temperature_correlation=bad
        )


@pytest.mark.parametrize("bad",[-1.,float("nan"),float("inf"),"bad"])
def test_invalid_standard_uncertainty_rejected(bad):
    with pytest.raises(DomainError):
        sensible_duty_uncertainty(
            2.,1000.,400.,350.,u_mass_flow_kg_s=bad,
            u_cp_j_kg_k=20.,u_inlet_temperature_k=1.,
            u_outlet_temperature_k=1.,
        )


def test_local_identifiability_rank_is_independently_recovered():
    full=local_sensitivity_rank([
        [1.,0.,1.],[0.,1.,1.],[1.,1.,1.],
    ])
    assert full.rank==3 and full.full_column_rank
    unidentifiable=local_sensitivity_rank([
        [1.,0.,1.],[0.,1.,1.],[1.,1.,2.],[2.,1.,3.]
    ])
    assert unidentifiable.rank==2
    assert not unidentifiable.full_column_rank
    # An entirely insensitive parameter cannot be identified.
    zero=local_sensitivity_rank([[1.,0.],[2.,0.]])
    assert zero.rank==1 and not zero.full_column_rank


@pytest.mark.parametrize("matrix", [[],[[]],[[1,2],[3]],[[1,float("nan")]]])
def test_invalid_identifiability_matrix_rejected(matrix):
    with pytest.raises(DomainError):
        local_sensitivity_rank(matrix)


def test_references_are_not_plant_estimates_and_no_confirmation_is_inferred():
    g=experimental_readiness_gate(
        [x for x in sensors()],sensors(),uncertainty()
    )
    assert not g["ready_for_measured_validation"]
    assert len(g["blockers"])>=35
