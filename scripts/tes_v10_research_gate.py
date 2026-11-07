#!/usr/bin/env python3
"""TES-v1.0 research-candidate *integrity audit*, not a publication authorization.

Generates an immutable-source content ledger and an explicit account of
software verification versus external governance. Never issues a version tag,
creates a release, purports to authenticate human review or clears rights.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import re

SCHEMA="tes-v10-research-baseline-candidate-1"
PARENT_VERSION="0.5.0a0"
REQUIRED = (
    "pyproject.toml", "CITATION.cff", "LICENSE", "MANIFEST.in", "README.md", "CHANGELOG.md",
    ".github/workflows/tes-v10-candidate-audit.yml",
    "src/sco2_braytonbench/thermal_storage.py",
    "src/sco2_braytonbench/tes_schumann.py",
    "src/sco2_braytonbench/tes_cycles.py",
    "src/sco2_braytonbench/tes_metrics.py",
    "src/sco2_braytonbench/tes_coupling.py",
    "src/sco2_braytonbench/tes_surrogate.py",
    "src/sco2_braytonbench/tes_operating_window.py",
    "scripts/tes_schumann_convergence.py",
    "scripts/tes_generate_synthetic_dataset.py",
    "scripts/tes_surrogate_pipeline.py",
    "scripts/tes_operating_window_study.py",
    "scripts/tes_v09_installed_probe.py",
    "scripts/tes_v09_release_gate.py",
    "scripts/tes_v10_research_gate.py",
    "tests/test_thermal_storage.py",
    "tests/test_tes_cycles.py",
    "tests/test_tes_coupling.py",
    "tests/test_tes_metrics.py",
    "tests/test_tes_dataset.py",
    "tests/test_tes_surrogate.py",
    "tests/test_tes_operating_window.py",
    "tests/test_tes_v09_release_gate.py",
    "tests/test_tes_v10_consistency.py",
    "docs/tes/01_LITERATURE_AND_MODEL_CONTRACT.md",
    "docs/tes/02_BENCHMARK_SPECIFICATION.md",
    "docs/tes/03_CONSERVATION_AND_LIMITS.md",
    "docs/tes/04_SCHUMANN_GRID_VERIFICATION.md",
    "docs/tes/05_CYCLES_AND_METRICS.md",
    "docs/tes/06_SINGLE_PASS_CO2_COUPLING.md",
    "docs/tes/07_PERFORMANCE_METRICS.md",
    "docs/tes/08_FROZEN_SPLIT_SURROGATE.md",
    "docs/tes/09_FROZEN_ROM_RESULTS_2026-11-07.md",
    "docs/tes/10_OPERATING_WINDOW_SENSITIVITY.md",
    "docs/tes/11_OPERATING_WINDOW_RESULTS_2026-11-07.md",
    "docs/tes/12_DISTRIBUTION_AND_REPLAY_GATE.md",
    "docs/tes/13_RESEARCH_BASELINE_TECHNICAL_REPORT.md",
    "docs/tes/14_EXTERNAL_REVIEW_PACKET.md",
    "docs/tes/15_RELEASE_DECISION_REGISTER.md",
    "docs/data_licenses/TES_SOURCE_RIGHTS.md",
)
EXCLUDED = (
    "data/reference/mantilla2010_thermoml_density.csv",
)
EVIDENCE_CLASSES = (
    "analytical_continuum_reference",
    "conservative_finite_volume_solver",
    "synthetic_charge_hold_reverse_discharge",
    "open_single_pass_quasi_steady_cycle",
    "synthetic_512_run_frozen_split_surrogate",
    "synthetic_n96_operating_window_and_factorial",
    "wheel_sdist_python310_311_312_replay",
)
MANUAL = {
    "issue_27_historical_thermoml_rights": "OPEN_REQUIRES_HUMAN_RIGHTS_STEWARD",
    "issue_28_independent_qualified_review": "OPEN_REQUIRES_REAL_HUMAN_REVIEWERS",
    "actual_plant_experimental_validation": "NOT_PERFORMED_AND_OUT_OF_SCOPE",
    "formal_parent_release_decision": "NOT_AUTHORIZED",
}
REQUIRED_PRERELEASE_FLAGS = {
    "parent_version_unchanged": True,
    "independent_human_reviewer_approved": False,
    "historical_third_party_data_rights_cleared": False,
    "measured_facility_validation_performed": False,
    "release_tag_approved": False,
}


def demand(ok: bool, detail: str) -> None:
    if not ok:
        raise ValueError(detail)


def digest(file: Path) -> str:
    h=hashlib.sha256()
    with file.open("rb") as src:
        for piece in iter(lambda:src.read(1024*1024),b""):
            h.update(piece)
    return h.hexdigest()


def normalize_sha(source: str) -> str:
    demand(isinstance(source,str) and
           re.fullmatch(r"[0-9a-f]{40}",source) is not None,
           "source revision must be an exact 40-character commit SHA")
    return source


def audit(root: Path, source_sha: str, out: Path) -> dict:
    root=root.resolve()
    sha=normalize_sha(source_sha)
    files={}
    for name in REQUIRED:
        path=root/name
        demand(path.is_file(),"required TES-v1 candidate evidence missing: "+name)
        demand(path.resolve().is_relative_to(root),
               "TES-v1 candidate path escapes source checkout")
        files[name]=digest(path)
    for name in EXCLUDED:
        demand(not (root/name).exists(),
               "unapproved extracted Mantilla measurements in source snapshot")
    project=(root/"pyproject.toml").read_text(encoding="utf-8")
    citation=(root/"CITATION.cff").read_text(encoding="utf-8")
    demand(re.search(r'(?m)^version = "0\.5\.0a0"$',project) is not None,
           "parent pyproject version must stay research alpha")
    demand(re.search(r'(?m)^version: "0\.5\.0a0"$',citation) is not None,
           "CITATION parent version must stay research alpha")
    demand('license = "BSD-3-Clause"' in project,
           "project license contract drift")
    demand('license: "BSD-3-Clause"' in citation,
           "citation license drift")
    demand("exclude data/reference/mantilla2010_thermoml_density.csv"
           in (root/"MANIFEST.in").read_text("utf-8"),
           "sdist denylist rule removed")
    rights=(root/"docs/data_licenses/TES_SOURCE_RIGHTS.md").read_text("utf-8")
    review=(root/"docs/tes/14_EXTERNAL_REVIEW_PACKET.md").read_text("utf-8")
    for item in ("#27","redistribution","no permission"):
        demand(item.lower() in rights.lower(),
               "rights dossier omits unresolved restriction "+item)
    for item in ("#28","independent","reviewer","CHANGES REQUESTED"):
        demand(item.lower() in review.lower(),
               "review packet incomplete: "+item)
    report={
        "schema":SCHEMA,
        "evidence_class":"research_software_self_audit_only",
        "source_commit":sha,
        "parent_package":"sco2-braytonbench",
        "parent_version":PARENT_VERSION,
        "source_file_sha256":files,
        "source_file_count":len(files),
        "excluded_source_data_paths":list(EXCLUDED),
        "scientific_evidence_families":list(EVIDENCE_CLASSES),
        "manual_gates":MANUAL,
        "pre_release_flags":dict(REQUIRED_PRERELEASE_FLAGS),
        "reviewer_identity_asserted_by_this_program":False,
        "release_authorized":False,
        "tags_created":[],
        "doi_created":None,
        "limitations":[
            "No independent qualified human thermodynamics/software approval",
            "Historical public Git rights for a transcribed NIST ThermoML table are unresolved",
            "No full closed-loop CO2 pressure/mass inventory or actual TES measurement",
            "Surrogate is an 8-cell synthetic output emulator; negative OOD result remains",
            "N96->N192 nominal threshold service differs ~3.4%; model form unquantified",
        ],
    }
    out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(report,indent=2,sort_keys=True,
                              allow_nan=False)+"\n",encoding="utf-8")
    return report


def verify(root:Path,report_path:Path,source_sha:str)->dict:
    """Fail closed if source changed or purported governance status is altered."""
    report=json.loads(report_path.read_text(encoding="utf-8"))
    demand(report.get("schema")==SCHEMA,"unknown review manifest schema")
    demand(report.get("source_commit")==normalize_sha(source_sha),
           "review evidence source commit mismatch")
    demand(report.get("parent_version")==PARENT_VERSION,
           "unapproved parent version promotion")
    demand(report.get("source_file_count")==len(REQUIRED),
           "unexpected evidence file count")
    demand(set(report.get("source_file_sha256",{}))==set(REQUIRED),
           "source evidence inventory drift")
    demand(report.get("manual_gates")==MANUAL,
           "someone altered unresolved manual governance gates")
    demand(report.get("pre_release_flags")==REQUIRED_PRERELEASE_FLAGS,
           "self-audit cannot assert permission or qualified human sign-off")
    demand(report.get("reviewer_identity_asserted_by_this_program") is False,
           "automatic tool must not claim reviewer identity")
    demand(report.get("release_authorized") is False,
           "automatic self-audit cannot authorize release")
    demand(report.get("tags_created")==[] and report.get("doi_created") is None,
           "tag/DOI misrepresentation")
    demand(report.get("scientific_evidence_families")==list(EVIDENCE_CLASSES),
           "evidence families manipulated")
    demand(report.get("excluded_source_data_paths")==list(EXCLUDED),
           "data exclusions changed")
    root=root.resolve()
    for name in REQUIRED:
        p=root/name
        demand(p.is_file() and p.resolve().is_relative_to(root),
               "missing/unsafe source "+name)
        demand(digest(p)==report["source_file_sha256"][name],
               "source content hash mismatch "+name)
    for name in EXCLUDED:
        demand(not (root/name).exists(),
               "uncleared NIST measurement table reintroduced")
    return report


def main():
    p=argparse.ArgumentParser()
    p.add_argument("mode",choices=("audit","verify"))
    p.add_argument("--root",type=Path,default=Path("."))
    p.add_argument("--source-sha",required=True)
    p.add_argument("--out",type=Path,
                   default=Path("evidence/generated/tes_v10/candidate_manifest.json"))
    args=p.parse_args()
    result=(audit(args.root,args.source_sha,args.out) if args.mode=="audit"
            else verify(args.root,args.out,args.source_sha))
    print(json.dumps({
        "source_commit":result["source_commit"],
        "source_files_hashed":result["source_file_count"],
        "candidate_integrity":"PASS",
        "independent_human_review":"NOT_RECORDED",
        "third_party_rights":"NOT_CLEARED",
        "v1_release_authorized":False,
    },sort_keys=True))


if __name__=="__main__":
    main()
