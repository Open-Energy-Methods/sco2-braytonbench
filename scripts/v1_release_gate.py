"""WP5 offline release candidate audit and numerical evidence comparison.

No network access, GitHub tag, Zenodo upload, or plant validation action.
This verifies software distribution and scenario replay, not a verified
experimental sCO2 Brayton cycle or safe industrial controller.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import os
import platform
import re
import tarfile
try:
    import tomllib  # Python >=3.11
except ModuleNotFoundError:  # Python 3.10 metadata audit
    import tomli as tomllib
import zipfile
from pathlib import Path
from typing import Any

SCENARIOS = (
    "v1_thermal_wall/thermal_wall_summary.json",
    "v1_thermal_wall/thermal_wall_trace.csv",
    "v1_wp2b/scenario_summary.json",
    "v1_wp2b/scenario_trace.csv",
    "v1_wp3/control_summary.json",
    "v1_wp3/control_trace.csv",
    "v1_wp4/readiness_audit.json",
    "v1_wp4/campaign_gate_summary.csv",
)
REQUIRED_DOCS = (
    "docs/V1_0_RELEASE_CONTRACT.md",
    "docs/V1_0_VERIFICATION_MATRIX.md",
    "docs/G4_THERMAL_CONTROL_VOLUME_SCOPE.md",
    "docs/G4_WP2B_FINITE_SOURCE_WALL_CYCLE.md",
    "docs/G5_WP3_BYPASS_PI_CONTROL.md",
    "docs/G5_WP3_RESULTS.md",
    "docs/WP4_EXPERIMENTAL_READINESS_PROTOCOL.md",
    "docs/WP5_RELEASE_ACCEPTANCE.md",
)
SOURCE_ROOTS = ("src", "examples", "tests", "scripts", "protocols", "docs", "data")
MUST_SHIP_SDIST = (
    "CITATION.cff",
    "LICENSE",
    "README.md",
    "CHANGELOG.md",
    "CONTRIBUTING.md",
    "MANIFEST.in",
    "protocols/wp4/prospective_test_matrix.csv",
    "protocols/wp4/measurement_channels.csv",
    "protocols/wp4/uncertainty_register.csv",
    "protocols/wp4/prospective_run_manifest.json",
    "examples/waste_heat_bypass_pi_comparison.py",
    "examples/wp4_readiness_audit.py",
    "data/reference/mantilla2010_provenance.yaml",
    "data/validation/stuttgart/README.md",
    "tests/test_experimental_readiness.py",
    "scripts/v1_release_gate.py",
)
MANUAL_BLOCKERS = (
    "Required stacked PRs #22, #23, #24 and #25 await scientific review and integration.",
    "Version/commit/source freeze and v1.0.0-rc1 candidate approval not issued.",
    "Third-party research source data redistribution/attribution rights require review.",
    "Independent governing-equation, numerical reliability and API/limits review pending.",
    "Full integrated-main final-commit CI and explicit reviewer sign-off pending.",
)
SCIENTIFIC_SCOPE_LIMITATIONS = (
    "No experimentally calibrated CARBOSOLA or other whole-cycle dynamic predictions.",
    "No CO2 fluid inventory, dynamic pressure/turbomachinery machinery-map or shaft-inertia model.",
    "Lumped wall, UAs, gas mixing and PI gains are hypothetical except stated real-fluid property calls.",
    "Unresolved Kim Eq.24 research interpretation excluded from stable default claims.",
    "WP4 is prospective: no facility measurements, calibrated sensors, approval or research runs.",
)



def _sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def _check(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def _metadata(root: Path) -> dict[str, Any]:
    py = tomllib.loads((root / "pyproject.toml").read_text("utf-8"))
    project = py["project"]
    version = str(project["version"])
    embargoed = root / "data/reference/mantilla2010_thermoml_density.csv"
    _check(not embargoed.exists(),
           "Uncleared Mantilla NIST ThermoML table must not be present in "
           "candidate source checkout or GitHub tag snapshot; see issue #27")
    _check(project["name"] == "sco2-braytonbench", "unexpected package name")
    _check(project["license"] == "BSD-3-Clause", "wrong project SPDX license")
    _check((root / "LICENSE").read_text("utf-8").startswith(
        "BSD 3-Clause License"), "LICENSE missing or inconsistent")
    _check(project["requires-python"] == ">=3.10",
           "supported Python version contract changed without review")
    citation = (root / "CITATION.cff").read_text("utf-8")
    _check("cff-version: 1.2.0" in citation,
           "citation metadata must declare CFF 1.2.0")
    _check('license: "BSD-3-Clause"' in citation,
           "citation license is inconsistent")
    _check('repository-code: "https://github.com/Open-Energy-Methods/sco2-braytonbench"'
           in citation, "citation repository URL mismatch")
    quoted = re.search(r'^version:\s*["\']?([^"\'\s]+)', citation, re.M)
    _check(quoted is not None and quoted.group(1) == version,
           "CITATION.cff version must equal pyproject.toml package version")
    for doc in REQUIRED_DOCS:
        _check((root / doc).is_file(), f"missing v1 scientific scope documentation: {doc}")
    for source in ("README.md", "CHANGELOG.md", "CONTRIBUTING.md",
                   "MANIFEST.in"):
        _check((root / source).is_file(), f"missing repository file {source}")
    return {
        "package_name": project["name"],
        "version": version,
        "license_spdx": project["license"],
        "python_requires": project["requires-python"],
        "CITATION_cff_version": quoted.group(1),
        "release_status": "unreleased_alpha" if version == "0.5.0a0" else
                          "requires_manual_version_review",
    }


def _file_manifest(root: Path) -> dict[str, str]:
    result = {}
    for entry in (
        "pyproject.toml", "CITATION.cff", "LICENSE", "README.md",
        "CHANGELOG.md", "CONTRIBUTING.md", "MANIFEST.in"
    ):
        f=root/entry
        if f.is_file():
            result[entry] = _sha256(f)
    for directory in SOURCE_ROOTS:
        base = root / directory
        if not base.is_dir():
            continue
        for f in sorted(base.rglob("*")):
            if (f.is_file() and not any(
                segment in {"__pycache__", ".pytest_cache", "generated",
                            "dist", "build"} for segment in f.relative_to(root).parts)
                    and f.suffix in {".py", ".md", ".csv", ".json", ".yaml",
                                      ".yml", ".txt", ".tsv", ".toml"}):
                result[f.relative_to(root).as_posix()] = _sha256(f)
    _check(bool(result), "no source evidence to fingerprint")
    return result


def _read_distributions(dist: Path, version: str) -> dict[str, Any]:
    wheels = sorted(dist.glob("sco2_braytonbench-*.whl"))
    sdists = sorted(dist.glob("sco2_braytonbench-*.tar.gz"))
    _check(len(wheels)==1 and len(sdists)==1,
           "expected precisely one wheel and one sdist")
    wheel, sdist = wheels[0], sdists[0]
    _check(version.replace("-", "_") in wheel.name and
           version.replace("-", "_") in sdist.name,
           "distribution file version mismatch")
    with zipfile.ZipFile(wheel) as archive:
        names = archive.namelist()
        metadata_paths = [x for x in names if x.endswith(".dist-info/METADATA")]
        _check(len(metadata_paths)==1, "wheel METADATA missing or ambiguous")
        metadata=archive.read(metadata_paths[0]).decode("utf-8")
        _check(f"Version: {version}" in metadata,
               "wheel metadata/version mismatch")
        _check("License-Expression: BSD-3-Clause" in metadata
               or "License: BSD-3-Clause" in metadata,
               "wheel license metadata mismatch")
        _check(any("LICENSE" in name and ".dist-info/" in name for name in names),
               "built wheel does not contain BSD license")
        for package_file in (
            "sco2_braytonbench/cycle.py",
            "sco2_braytonbench/thermal_dynamics.py",
            "sco2_braytonbench/dynamic_whr.py",
            "sco2_braytonbench/control_whr.py",
            "sco2_braytonbench/experimental_readiness.py"
        ):
            _check(package_file in names,
                   f"built wheel missing package module {package_file}")
    with tarfile.open(sdist, "r:gz") as archive:
        names={Path(name).as_posix() for name in archive.getnames()}
    for required in MUST_SHIP_SDIST + REQUIRED_DOCS:
        _check(any(name.endswith("/"+required) for name in names),
               f"sdist missing research/reproduction file: {required}")
    embargoed = "data/reference/mantilla2010_thermoml_density.csv"
    _check(not any(name.endswith("/"+embargoed) for name in names),
           "sdist illegally/without approval bundles Mantilla ThermoML extracted data")
    return {
        "wheel": {"filename":wheel.name,"sha256":_sha256(wheel),
                  "size_bytes":wheel.stat().st_size},
        "sdist": {"filename":sdist.name,"sha256":_sha256(sdist),
                  "size_bytes":sdist.stat().st_size},
        "built_wheel_contains_expected_modules":True,
        "source_archive_contains_research_and_test_files":True,
        "binary_identical_across_builds_not_asserted":True,
    }


def _outputs(root: Path) -> dict[str, str]:
    paths={}
    for rel in SCENARIOS:
        path=root/"evidence"/"generated"/rel
        _check(path.is_file(), f"missing numerical evidence: {rel}")
        paths[rel]=_sha256(path)
        if rel.endswith(".json"):
            data=json.loads(path.read_text("utf-8"))
            _check(isinstance(data,dict), f"invalid JSON root: {rel}")
        else:
            with path.open(newline="",encoding="utf-8") as stream:
                table=list(csv.DictReader(stream))
                _check(bool(table), f"empty CSV scenario evidence: {rel}")
    wp2b=json.loads(
        (root/"evidence/generated/v1_wp2b/scenario_summary.json")
        .read_text("utf-8"))
    wp3=json.loads(
        (root/"evidence/generated/v1_wp3/control_summary.json")
        .read_text("utf-8"))
    wp4=json.loads(
        (root/"evidence/generated/v1_wp4/readiness_audit.json")
        .read_text("utf-8"))
    _check(wp2b.get("is_carbsosola_or_measured_CO2") is False,
           "WP2b synthetic scenario misrepresented as measured")
    _check(wp3.get("is_CARBOSOLA_or_measured") is False,
           "WP3 controller scenario misrepresented as measured")
    _check(wp4.get("physical_data_acquisition_performed") is False
           and wp4.get("facility_authorization_received") is False,
           "WP4 wrongly asserts measured experiment or authorization")
    _check(wp4.get("candidate_channel_count")==35
           and wp4.get("proposed_case_count")==13,
           "WP4 baseline prospective design unexpectedly changed")
    _check(all(row.get("blocked_for_measured_validation") is True
               for row in wp4["cases"]), "unauthorized laboratory approval claim")
    return paths


def audit(root: Path, dist: Path, out: Path) -> dict[str, Any]:
    root=root.resolve()
    metadata=_metadata(root)
    report={
        "schema":"sco2-braytonbench-wp5-candidate-1",
        "classification":"software_reproducibility_pre_release_audit",
        "model_not_industrially_or_experimentally_validated":True,
        "environment":{
            "python":platform.python_version(),
            "platform":platform.platform(),
            "github_sha":os.environ.get("GITHUB_SHA","unverified_local_revision"),
            "github_run_id":os.environ.get("GITHUB_RUN_ID","local_not_CI"),
        },
        "project":metadata,
        "source_file_sha256":_file_manifest(root),
        "distribution":_read_distributions(dist.resolve(),metadata["version"]),
        "scenario_evidence_sha256":_outputs(root),
        "software_artifact_checks_passed":True,
        "manual_scientific_and_governance_blockers":list(MANUAL_BLOCKERS),
        "disclosed_scientific_scope_limitations":list(SCIENTIFIC_SCOPE_LIMITATIONS),
        "tag_or_zenodo_release_authorized":False,
        "release_promotion_gate":"BLOCKED_PENDING_INDEPENDENT_REVIEW",
    }
    out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(report,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    return report


def _compare_scalars(reference: Any, candidate: Any, where: str) -> None:
    if (isinstance(reference,bool) or isinstance(candidate,bool)):
        _check(type(reference) is type(candidate) and reference == candidate,
               f"boolean mismatch: {where}")
        return
    if isinstance(reference,(int,float)) and isinstance(candidate,(int,float)):
        _check(math.isfinite(float(reference)) and math.isfinite(float(candidate)),
               f"nonfinite numerical comparison: {where}")
        _check(math.isclose(reference,candidate,rel_tol=2e-9,abs_tol=2e-8),
               f"numeric difference {where}: {reference} != {candidate}")
        return
    _check(type(reference) is type(candidate) and reference==candidate,
           f"categorical mismatch {where}: {reference!r} != {candidate!r}")


def _compare_structures(a: Any,b: Any,path: str) -> None:
    if isinstance(a,dict):
        _check(isinstance(b,dict) and set(a)==set(b),
               f"JSON keys mismatch {path}")
        for key in sorted(a):
            _compare_structures(a[key],b[key],path+"/"+str(key))
    elif isinstance(a,list):
        _check(isinstance(b,list) and len(a)==len(b),
               f"JSON list length mismatch {path}")
        for index,(x,y) in enumerate(zip(a,b)):
            _compare_structures(x,y,path+"/"+str(index))
    else:
        _compare_scalars(a,b,path)


def _compare_csv(a: Path,b: Path,path: str) -> int:
    def load(p: Path):
        with p.open("r",newline="",encoding="utf-8") as stream:
            reader=csv.DictReader(stream)
            fields=reader.fieldnames
            rows=list(reader)
        return fields,rows
    fields_a, rows_a=load(a)
    fields_b, rows_b=load(b)
    _check(fields_a==fields_b and len(rows_a)==len(rows_b),
           f"CSV header/rows mismatch: {path}")
    for index,(ra,rb) in enumerate(zip(rows_a,rows_b)):
        for key in fields_a or []:
            x,y=ra[key],rb[key]
            # Strict comparable categorical values, tolerance only for
            # finite numeric values, so differences cannot be hidden as NaN.
            try:
                u,v=float(x),float(y)
            except (ValueError,TypeError):
                _check(x==y,f"CSV categorical mismatch {path}:{index}:{key}")
            else:
                _compare_scalars(u,v,f"{path}:{index}:{key}")
    return len(rows_a)


def compare(reference: Path,candidate: Path,out: Path) -> dict[str, Any]:
    reference,candidate=reference.resolve(),candidate.resolve()
    counts={}
    for rel in SCENARIOS:
        a=reference/"evidence/generated"/rel
        b=candidate/"evidence/generated"/rel
        _check(a.is_file() and b.is_file(),
               f"wheel/sdist missing comparable scenario: {rel}")
        if rel.endswith(".json"):
            _compare_structures(json.loads(a.read_text("utf-8")),
                                json.loads(b.read_text("utf-8")),rel)
            counts[rel]={"type":"JSON","matched":True}
        else:
            n=_compare_csv(a,b,rel)
            counts[rel]={"type":"CSV","rows":n,"matched":True}
    report={
        "classification":"two_fresh_install_synthetic_scenario_cross_check",
        "same_version_wheel_sdist_numerical_outputs_match_within_tolerance":True,
        "numeric_rtol":2e-9,
        "numeric_atol":2e-8,
        "scenarios":counts,
        "real_sco2_experiment_performed":False,
        "full_python_version_bitwise_reproducibility_asserted":False,
    }
    out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(report,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    return report


def main() -> None:
    parser=argparse.ArgumentParser(description=__doc__)
    subs=parser.add_subparsers(dest="command",required=True)
    a=subs.add_parser("audit")
    a.add_argument("--root",type=Path,default=Path("."))
    a.add_argument("--dist",type=Path,default=Path("dist"))
    a.add_argument("--out",type=Path,required=True)
    b=subs.add_parser("compare")
    b.add_argument("--reference",type=Path,required=True)
    b.add_argument("--candidate",type=Path,required=True)
    b.add_argument("--out",type=Path,required=True)
    args=parser.parse_args()
    report=(audit(args.root,args.dist,args.out)
            if args.command=="audit"
            else compare(args.reference,args.candidate,args.out))
    print(json.dumps({
        "classification":report["classification"],
        "gate":"SOFTWARE_CHECK_PASS",
        "release_promoted":False,
        "output":str(args.out)
    },indent=2))


if __name__=="__main__":
    main()
