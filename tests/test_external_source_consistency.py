"""Publicly reported source facts: exact provenance and anomaly gates.

These are TRANSCRIPTION/ARITHMETIC checks, not calibration of
BraytonBench thermal-hydraulic or turbomachinery predictions.
"""
import json
import math
from pathlib import Path
import pytest

PATH=(Path(__file__).resolve().parents[1]/
      "data"/"validation"/"reported_source_cases.json")
DATA=json.loads(PATH.read_text())
SRC=DATA["sources"]

def test_external_evidence_classes_never_mixed():
    assert DATA["epistemic_status"]=="source_transcription_checks_only_not_model_validation"
    assert SRC["stuttgart"]["kind"]=="experimental_derived"
    assert SRC["kaist"]["kind"]=="measured_and_model_corrected"
    assert SRC["sandia"]["kind"]=="predicted_design"
    assert SRC["hzdr_pche"]["kind"]=="numerical_and_economic_figure_data"
    assert SRC["hzdr_tpms"]["kind"]=="CFD_and_geometry_not_experiment"
    assert SRC["kth_spg_msr"]["kind"]=="planned_infrastructure_feasibility_not_lab_dataset"

def test_stuttgart_counts_and_source_anomaly_is_quarantined():
    d=SRC["stuttgart"]
    assert (d["experiment_count"],d["axial_records"],d["local_htc_records"],d["nominal_triplets"])==(54,2508,2398,18)
    a=d["anomaly"]
    assert a["status"]=="quarantine_no_autocorrection"
    assert a["source_q_kw_m2"]>8*a["paired_top_q_kw_m2"]
    assert a["paired_bottom_q_kw_m2"]==pytest.approx(a["paired_top_q_kw_m2"],rel=.001)
    assert d["matched_top_bottom_max_delta_k"]==pytest.approx(86.8129104341,abs=1e-6)

def test_zhang_rated_energy_and_U_discrepancy_open():
    r=SRC["zhang"]["rated"]
    assert SRC["zhang"]["anomaly"]["status"]=="reconcile_do_not_replace_reported_U"
    dhi=r["hot_in_c"]-r["cold_out_c"]
    dlo=r["hot_out_c"]-r["cold_in_c"]
    assert (dhi,dlo)==pytest.approx((3,8.9))
    lmtd=(dlo-dhi)/math.log(dlo/dhi)
    u=r["q_co2_kw"]*1000/(r["area_m2"]*lmtd)
    assert lmtd==pytest.approx(5.42559174788,rel=1e-10)
    assert u==pytest.approx(1368.451199289,rel=1e-8)
    assert u/r["paper_rated_u_w_m2_k"]>1.08
    assert SRC["zhang"]["independent_pressure_study_table2"]["u_w_m2_k"][-1]==1388

def test_kaist_pressure_and_power_semantics():
    k=SRC["kaist"]
    assert k["speed_first"]["rpm"]==12000
    assert k["speed_last"]["rpm"]==36000
    assert k["speed_first"]["flow_kg_min"]<k["speed_last"]["flow_kg_min"]
    assert k["corrected_inlet_last"]["windage_corrected_c"]>k["corrected_inlet_last"]["measured_c"]
    assert k["corrected_inlet_last"]["pin_bar"]/k["corrected_inlet_last"]["pout_bar"]==pytest.approx(k["speed_last"]["turbine_pr"],rel=.001)
    assert "independent_measurement" in k["caution"]
    # Motor input is NOT turbine power or validated shaft output.
    assert k["speed_last"]["motor_input_kw"]>0

def test_sandia_table21_not_used_as_observed_data():
    d=SRC["sandia"]
    assert d["table"]=="2.1"
    assert d["kind"]=="predicted_design"
    assert d["source_design_point"]["rpm"]==75000
