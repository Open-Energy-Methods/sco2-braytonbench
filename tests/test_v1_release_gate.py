"""WP5: release gate failure-injection tests, without any GitHub or Zenodo action."""
import csv
import json
from pathlib import Path

import pytest

from scripts import v1_release_gate as gate

ROOT=Path(__file__).resolve().parents[1]


def test_metadata_is_present_and_citation_matches_unreleased_package():
    obj=gate._metadata(ROOT)
    assert obj["package_name"]=="sco2-braytonbench"
    assert obj["version"]=="0.6.0a0"
    assert obj["CITATION_cff_version"]==obj["version"]
    assert obj["license_spdx"]=="BSD-3-Clause"
    assert obj["release_status"]=="unreleased_alpha"


def test_complete_source_input_ledger_has_new_research_and_protocols():
    ledger=gate._file_manifest(ROOT)
    for name in (
        "src/sco2_braytonbench/experimental_readiness.py",
        "src/sco2_braytonbench/thermal_dynamics.py",
        "src/sco2_braytonbench/control_whr.py",
        "protocols/wp4/measurement_channels.csv",
        "protocols/wp4/prospective_test_matrix.csv",
        "docs/WP5_RELEASE_ACCEPTANCE.md",
        "scripts/v1_release_gate.py",
    ):
        assert name in ledger
        assert len(ledger[name])==64
    assert not any("__pycache__" in name for name in ledger)


def test_no_release_gate_code_can_imply_actual_tag_authorization():
    assert gate.MANUAL_BLOCKERS
    assert any("review" in text.lower() for text in gate.MANUAL_BLOCKERS)


def test_comparator_allows_small_numeric_roundoff_only():
    gate._compare_scalars(1.,1.+1e-10,"roundoff")
    gate._compare_scalars(True,True,"bool")
    with pytest.raises(ValueError,match="numeric difference"):
        gate._compare_scalars(1.,1.1,"different")
    with pytest.raises(ValueError,match="nonfinite"):
        gate._compare_scalars(1.,float("nan"),"nan")
    with pytest.raises(ValueError,match="boolean mismatch"):
        gate._compare_scalars(False,0,"bool/int alias")


def test_nested_structures_have_exact_keys_and_category_order():
    gate._compare_structures(
        {"info":"synthetic","v":[1.,"two",{"x":5}]},
        {"v":[1.+1e-10,"two",{"x":5.0}],"info":"synthetic"}, "root"
    )
    with pytest.raises(ValueError,match="JSON keys mismatch"):
        gate._compare_structures({"a":1},{"b":1},"root")
    with pytest.raises(ValueError,match="JSON list length"):
        gate._compare_structures([1,2],[1],"root")
    with pytest.raises(ValueError,match="categorical mismatch"):
        gate._compare_structures({"data_class":"synthetic"},
                                 {"data_class":"measured"},"root")


def _mock_outputs(workspace:Path):
    for i,rel in enumerate(gate.SCENARIOS):
        path=workspace/"evidence/generated"/rel
        path.parent.mkdir(parents=True,exist_ok=True)
        if rel.endswith(".json"):
            path.write_text(json.dumps({
                "evidence_class":"synthetic",
                "rows":[{"temperature_k":310.+i,"count":i}]
            }),encoding="utf-8")
        else:
            with path.open("w",newline="",encoding="utf-8") as stream:
                writer=csv.writer(stream)
                writer.writerow(["time_s","temperature_k","data_class"])
                writer.writerow([0,310.+i,"synthetic"])


def test_cross_distribution_replay_includes_all_eight_scenarios(tmp_path):
    a,b=tmp_path/"wheel",tmp_path/"sdist"
    _mock_outputs(a)
    _mock_outputs(b)
    report=gate.compare(a,b,tmp_path/"report.json")
    assert report["same_version_wheel_sdist_numerical_outputs_match_within_tolerance"]
    assert len(report["scenarios"])==8
    assert report["real_sco2_experiment_performed"] is False
    assert (tmp_path/"report.json").is_file()


def test_cross_distribution_replay_rejects_changed_physics(tmp_path):
    a,b=tmp_path/"wheel",tmp_path/"sdist"
    _mock_outputs(a)
    _mock_outputs(b)
    file=b/"evidence/generated/v1_wp3/control_summary.json"
    value=json.loads(file.read_text("utf-8"))
    value["rows"][0]["temperature_k"] += 10.
    file.write_text(json.dumps(value),encoding="utf-8")
    with pytest.raises(ValueError,match="numeric difference"):
        gate.compare(a,b,tmp_path/"report.json")


def test_cross_distribution_replay_rejects_category_forgery(tmp_path):
    a,b=tmp_path/"wheel",tmp_path/"sdist"
    _mock_outputs(a)
    _mock_outputs(b)
    file=b/"evidence/generated/v1_wp4/readiness_audit.json"
    value=json.loads(file.read_text("utf-8"))
    value["evidence_class"]="measured"
    file.write_text(json.dumps(value),encoding="utf-8")
    with pytest.raises(ValueError,match="categorical mismatch"):
        gate.compare(a,b,tmp_path/"report.json")


def test_cross_distribution_replay_rejects_missing_evidence(tmp_path):
    a,b=tmp_path/"wheel",tmp_path/"sdist"
    _mock_outputs(a)
    _mock_outputs(b)
    (b/"evidence/generated/v1_wp2b/scenario_trace.csv").unlink()
    with pytest.raises(ValueError,match="missing comparable scenario"):
        gate.compare(a,b,tmp_path/"report.json")


def test_cross_distribution_replay_rejects_nonfinite_csv(tmp_path):
    a,b=tmp_path/"wheel",tmp_path/"sdist"
    _mock_outputs(a)
    _mock_outputs(b)
    f=b/"evidence/generated/v1_wp2b/scenario_trace.csv"
    f.write_text(
        "time_s,temperature_k,data_class\n0,nan,synthetic\n",
        encoding="utf-8"
    )
    with pytest.raises(ValueError,match="nonfinite"):
        gate.compare(a,b,tmp_path/"report.json")


def test_cross_distribution_replay_rejects_csv_schema_mutation(tmp_path):
    a,b=tmp_path/"wheel",tmp_path/"sdist"
    _mock_outputs(a)
    _mock_outputs(b)
    f=b/"evidence/generated/v1_wp3/control_trace.csv"
    f.write_text("time_s,different,data_class\n0,310,synthetic\n",encoding="utf-8")
    with pytest.raises(ValueError,match="CSV header/rows mismatch"):
        gate.compare(a,b,tmp_path/"report.json")


def test_missing_external_source_archive_fails_with_honest_error(tmp_path):
    with pytest.raises(ValueError,match="precisely one wheel"):
        gate._read_distributions(tmp_path,"0.6.0a0")


def test_unexpected_citation_version_fails_before_release(tmp_path):
    fake=tmp_path/"repo"
    fake.mkdir()
    for name in ("pyproject.toml","LICENSE","CITATION.cff"):
        (fake/name).write_text((ROOT/name).read_text("utf-8"),encoding="utf-8")
    cite=(fake/"CITATION.cff").read_text("utf-8")
    (fake/"CITATION.cff").write_text(
        cite.replace('version: "0.6.0a0"','version: "1.0.0"'),
        encoding="utf-8"
    )
    with pytest.raises(ValueError,match="CITATION.cff version"):
        gate._metadata(fake)


def test_wrong_project_license_fails_closed(tmp_path):
    fake=tmp_path/"repo"
    fake.mkdir()
    for name in ("pyproject.toml","LICENSE","CITATION.cff"):
        (fake/name).write_text((ROOT/name).read_text("utf-8"),encoding="utf-8")
    py=(fake/"pyproject.toml").read_text("utf-8")
    (fake/"pyproject.toml").write_text(
        py.replace('license = "BSD-3-Clause"','license = "MIT"'),encoding="utf-8"
    )
    with pytest.raises(ValueError,match="SPDX license"):
        gate._metadata(fake)


def test_embargoed_thermoml_data_is_not_in_current_source_snapshot():
    """An auto-generated GitHub source archive must not contain these rows."""
    embargoed = ROOT / "data/reference/mantilla2010_thermoml_density.csv"
    assert not embargoed.is_file(), (
        "The release branch contains an unlicensed third-party complete table"
    )
    assert (ROOT/"data/reference/mantilla2010_provenance.yaml").is_file()
    assert (ROOT/"data/reference/README_MANTILLA_OPT_IN.md").is_file()


def test_embargoed_thermoml_data_in_source_fails_release_metadata(tmp_path):
    """Simulate a user accidentally re-introducing the third-party CSV."""
    fake=tmp_path/"repo"
    fake.mkdir()
    for name in ("pyproject.toml","LICENSE","CITATION.cff"):
        (fake/name).write_text((ROOT/name).read_text("utf-8"),encoding="utf-8")
    p=fake/"data/reference/mantilla2010_thermoml_density.csv"
    p.parent.mkdir(parents=True)
    p.write_text("not permitted in release tree",encoding="utf-8")
    with pytest.raises(ValueError,match="must not be present"):
        gate._metadata(fake)
