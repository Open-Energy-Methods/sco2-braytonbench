"""WP4 desk audit of PROPOSED channels/cases, not an experiment.

Writes a reproducible software/measurement-readiness ledger. The numeric
uncertainty and sensitivity examples below are *synthetic mathematical
fixtures*: NO instrument or calibration value comes from CARBOSOLA.
"""
import csv
import json
from pathlib import Path

from sco2_braytonbench.experimental_readiness import (
    experimental_readiness_gate,
    load_sensor_register, load_test_matrix, load_uncertainty_register,
    validate_long_series, sensible_duty_uncertainty,
    local_sensitivity_rank,
)

BASE=Path("protocols/wp4")
OUT=Path("evidence/generated/v1_wp4")
OUT.mkdir(parents=True,exist_ok=True)
channels=load_sensor_register(BASE/"measurement_channels.csv")
matrix=load_test_matrix(BASE/"prospective_test_matrix.csv",channels)
uncertainties=load_uncertainty_register(BASE/"uncertainty_register.csv",channels)
qc=validate_long_series(
    BASE/"synthetic_format_fixture.csv",
    channels,expected_run_id="SYNTH-WP4-001",max_gap_s=1.5
)
case_results=[]
for case in matrix:
    required=case["required_tags"].split(";")
    readiness=experimental_readiness_gate(
        required,channels,uncertainties,
        approved_run_authorization=False,
        verified_data_provenance=False
    )
    case_results.append({
        "case_id":case["case_id"],
        "stage":case["stage"],
        "data_class":case["data_class"],
        "facility_run_approval":case["approval_status"],
        "required_candidate_channel_count":len(required),
        "blocked_for_measured_validation":not readiness["ready_for_measured_validation"],
        "blocker_count":len(readiness["blockers"]),
        "blockers":readiness["blockers"]
    })
    assert case["approval_status"]=="not_requested"
    assert not readiness["ready_for_measured_validation"]

# Independent toy GUM arithmetic, only to check a correct method and SI.
toy=sensible_duty_uncertainty(
    2.,1000.,400.,350.,
    u_mass_flow_kg_s=.1,u_cp_j_kg_k=20.,
    u_inlet_temperature_k=1.,u_outlet_temperature_k=2.,
    inlet_outlet_temperature_correlation=.25,
)
assert abs(toy.heat_rate_w-100000.)<1e-9
assert abs(toy.variance_w2-45000000.)<1e-6

full=local_sensitivity_rank([[1.,0.,1.],[0.,1.,1.],[1.,1.,1.]])
deficient=local_sensitivity_rank(
    [[1.,0.,1.],[0.,1.,1.],[1.,1.,2.],[2.,1.,3.]]
)
assert full.full_column_rank and not deficient.full_column_rank

report={
    "classification":"WP4 prospective experiment and synthetic method-validation only",
    "no_measured_CARBOSOLA_signals":True,
    "facility_authorization_received":False,
    "sensor_inventory_installed_verified":False,
    "instrument_calibration_certificates_available":False,
    "timestamp_cross_channel_sync_verified":False,
    "candidate_channel_count":len(channels),
    "proposed_case_count":len(matrix),
    "unconfirmed_calibration_channels":sum(
        1 for ch in channels.values()
        if ch.calibration_status=="unconfirmed"
    ),
    "confirmed_uncertainties":sum(
        1 for u in uncertainties.values() if u.status=="confirmed"
    ),
    "synthetic_sample_format_qc":qc,
    "synthetic_constant_cp_uncertainty_example":{
        "mass_flow_kg_s":2.,
        "cp_j_kg_k":1000.,
        "t_in_k":400.,
        "t_out_k":350.,
        "standard_uncertainties":{
            "u_mass_flow_kg_s":.1,"u_cp_j_kg_k":20.,
            "u_Tin_k":1.,"u_Tout_k":2.,
            "T_in_out_correlation":.25
        },
        "heat_rate_w":toy.heat_rate_w,
        "combined_standard_uncertainty_w":toy.combined_standard_uncertainty_w,
        "variance_w2":toy.variance_w2,
        "NOT_a_calibrated_CARBOSOLA_uncertainty":True
    },
    "toy_local_jacobian_rank":{
        "independent":vars(full),
        "dependent":vars(deficient),
        "NO_global_identifiability_claim":True
    },
    "cases":case_results,
    "physical_data_acquisition_performed":False,
}
with (OUT/"readiness_audit.json").open("w",encoding="utf-8") as handle:
    json.dump(report,handle,indent=2)
    handle.write("\n")

flat=[
    {
        "case_id":c["case_id"],
        "stage":c["stage"],
        "proposed":c["data_class"],
        "authorization":c["facility_run_approval"],
        "required_channels":c["required_candidate_channel_count"],
        "blockers":c["blocker_count"],
        "ready_for_measured_validation":not c["blocked_for_measured_validation"],
    } for c in case_results
]
with (OUT/"campaign_gate_summary.csv").open("w",newline="",encoding="utf-8") as handle:
    writer=csv.DictWriter(handle,fieldnames=list(flat[0]))
    writer.writeheader()
    writer.writerows(flat)
print(json.dumps({
    "prospective_channels":len(channels),
    "unapproved_prospective_cases":len(matrix),
    "measured_validation_ready_cases":sum(
        not c["blocked_for_measured_validation"] for c in case_results
    ),
    "synthetic_format_sample_count":qc["sample_rows"],
    "uncertainty_toy_q_w":toy.heat_rate_w,
    "uncertainty_toy_u_w":toy.combined_standard_uncertainty_w,
    "full_rank_fixture":full.rank,
    "dependent_fixture_rank":deficient.rank,
    "warning":"NO actual experiment or instrument calibration claimed"
},indent=2))
