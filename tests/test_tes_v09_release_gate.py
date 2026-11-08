"""TES-v0.9 release-gate failure injection and static rights contracts."""
from __future__ import annotations

from copy import deepcopy
import csv
import json
from pathlib import Path

import pytest

from scripts import tes_v09_release_gate as gate


def wheel_members():
    return list(gate.REQUIRED_WHEEL) + [
        "sco2_braytonbench-0.6.0a0.dist-info/METADATA",
        "sco2_braytonbench-0.6.0a0.dist-info/licenses/LICENSE",
    ]


def source_members():
    return ["sco2_braytonbench-0.6.0a0/" + name
            for name in gate.REQUIRED_SDIST]


def test_minimum_complete_packaging_contract_and_source_rights():
    wheel = gate._paths_checked(wheel_members(), "wheel")
    sdist = gate._paths_checked(source_members(), "sdist")
    assert wheel["no_uncleared_restricted_assets"]
    assert sdist["no_uncleared_restricted_assets"]
    assert wheel["required_checked"] == len(gate.REQUIRED_WHEEL)
    assert sdist["required_checked"] == len(gate.REQUIRED_SDIST)
    assert gate.PARENT_VERSION == "0.6.0a0"
    assert len(gate.REPLAY_ARTIFACTS) == 7


@pytest.mark.parametrize("injection", [
    "sco2_braytonbench-0.6.0a0/data/reference/mantilla2010_thermoml_density.csv",
    "sco2_braytonbench-0.6.0a0/docs/copied_paper.pdf",
    "sco2_braytonbench-0.6.0a0/evidence/generated/tes_v07/test.csv",
    "sco2_braytonbench-0.6.0a0/models/unverified.joblib",
    "sco2_braytonbench-0.6.0a0/../another-root/file.py",
    "/absolutely/not/an/archive/name",
])
def test_restricted_assets_and_archive_paths_fail_closed(injection):
    with pytest.raises(ValueError):
        gate._paths_checked(source_members() + [injection], "sdist")


def test_duplicate_and_missing_files_fail_closed():
    with pytest.raises(ValueError,match="duplicate"):
        gate._paths_checked(wheel_members()+[wheel_members()[0]],"wheel")
    with pytest.raises(ValueError,match="missing"):
        gate._paths_checked(wheel_members()[1:],"wheel")
    with pytest.raises(ValueError,match="source-root"):
        gate._paths_checked(source_members()+["second-root/more.py"],"sdist")


def test_provenance_yaml_remains_permitted_while_density_table_is_rejected():
    assert any("mantilla2010_provenance.yaml" in x for x in source_members())
    gate._paths_checked(source_members(),"sdist")
    with pytest.raises(ValueError,match="unapproved NIST"):
        gate._paths_checked(source_members()+[
            "sco2_braytonbench-0.6.0a0/data/reference/MANTILLA2010_THERMOML_DENSITY.CSV"
        ],"sdist")


def test_strict_json_numeric_and_type_comparisons():
    gate._compare({"numbers":[1,2.00000000001],"flag":False,"empty":None},
                  {"numbers":[1.00000000001,2],"flag":False,"empty":None},"root")
    with pytest.raises(ValueError,match="boolean mismatch"):
        gate._compare(False,0,"flag")
    with pytest.raises(ValueError,match="numeric replay drift"):
        gate._compare(10.,11.,"temperature")
    with pytest.raises(ValueError,match="nonfinite"):
        gate._compare(float("nan"),float("nan"),"temperature")
    with pytest.raises(ValueError,match="JSON key mismatch"):
        gate._compare({"a":1},{"b":1},"root")
    with pytest.raises(ValueError,match="categorical"):
        gate._compare(None,0,"null_not_zero")


def test_csv_replay_detects_tampering_and_preserves_field_order(tmp_path):
    a,b = tmp_path/"wheel.csv",tmp_path/"sdist.csv"
    a.write_text("tag,temperature\ncharge,650.000000000\n",encoding="utf8")
    b.write_text("tag,temperature\ncharge,650.000000001\n",encoding="utf8")
    assert gate._csv_compare(a,b,"synthetic") == 1
    b.write_text("tag,temperature\ncharge,675\n",encoding="utf8")
    with pytest.raises(ValueError,match="numeric replay drift"):
        gate._csv_compare(a,b,"synthetic")
    b.write_text("temperature,tag\n650,charge\n",encoding="utf8")
    with pytest.raises(ValueError,match="columns differ"):
        gate._csv_compare(a,b,"synthetic")
    b.write_text("tag,temperature\ncharge,NaN\n",encoding="utf8")
    with pytest.raises(ValueError,match="nonfinite"):
        gate._csv_compare(a,b,"synthetic")


def test_missing_or_tampered_source_evidence_cannot_verify(tmp_path):
    report_file=tmp_path/"manifest.json"
    manifest={
        "schema":gate.SCHEMA,
        "v1_release_authorized":False,
        "wheel_sdist_same_scenario_replay":True,
        "distribution":{},
        "evidence_hashes":{"wheel":{},"sdist":{}},
    }
    report_file.write_text(json.dumps(manifest),encoding="utf8")
    with pytest.raises(ValueError):
        gate.verify(report_file,tmp_path,tmp_path,tmp_path)
    manifest["v1_release_authorized"]=True
    report_file.write_text(json.dumps(manifest),encoding="utf8")
    with pytest.raises(ValueError,match="cannot authorize"):
        gate.verify(report_file,tmp_path,tmp_path,tmp_path)


def test_replay_source_ref_must_be_immutable_sha(tmp_path):
    with pytest.raises(ValueError,match="source SHA"):
        gate.replay(tmp_path,tmp_path,tmp_path,tmp_path/"out.json","main")


def test_manifest_wont_claim_real_lab_or_final_v1_review():
    src=Path(__file__).resolve().parents[1]
    text=(src/"scripts/tes_v09_release_gate.py").read_text("utf-8")
    assert '"actual_plant_experimental_validation":False' in text
    assert '"redistribution_rights_legal_clearance_obtained":False' in text
    assert '"reviewer_scientific_approval":False' in text
    assert '"v1_release_authorized":False' in text
