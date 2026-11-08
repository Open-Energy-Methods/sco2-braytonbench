#!/usr/bin/env python3
"""TES-v0.9 wheel/sdist distribution, replay, hash and rights-audit gate.

Designed for execution against two *isolated installs* of the same source
commit, in scratch directories with no source package on import path.
It cannot confer third-party redistribution rights or scientific validation.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import os
from pathlib import Path, PurePosixPath
import re
import tarfile
import zipfile

SCHEMA="tes-v09-distribution-replay-1"
PARENT_VERSION="0.7.0a0"
REQUIRED_WHEEL=(
    "sco2_braytonbench/thermal_storage.py",
    "sco2_braytonbench/tes_schumann.py",
    "sco2_braytonbench/tes_cycles.py",
    "sco2_braytonbench/tes_metrics.py",
    "sco2_braytonbench/tes_coupling.py",
    "sco2_braytonbench/tes_surrogate.py",
    "sco2_braytonbench/tes_operating_window.py",
)
REQUIRED_SDIST=(
    "pyproject.toml","LICENSE","README.md","CITATION.cff",
    "MANIFEST.in",
    "scripts/tes_v09_installed_probe.py",
    "scripts/tes_v09_release_gate.py",
    "scripts/tes_schumann_convergence.py",
    "scripts/tes_operating_window_study.py",
    "scripts/tes_generate_synthetic_dataset.py",
    "scripts/tes_surrogate_pipeline.py",
    "examples/tes_charge_discharge.py",
    "examples/tes_coupled_discharge.py",
    "tests/test_tes_v09_release_gate.py",
    "tests/test_tes_operating_window.py",
    "docs/tes/10_OPERATING_WINDOW_SENSITIVITY.md",
    "docs/tes/11_OPERATING_WINDOW_RESULTS_2026-11-07.md",
    "data/reference/mantilla2010_provenance.yaml",
)
REPLAY_ARTIFACTS=(
    "evidence/generated/tes_v09/tes_v09_installed_probe.json",
    "evidence/generated/tes_v03/tes_grid_convergence.csv",
    "evidence/generated/tes_v03/tes_temporal_sensitivity.csv",
    "evidence/generated/tes_v03/tes_verification_manifest.json",
    "evidence/generated/tes_v04/synthetic_storage_stage_trace.csv",
    "evidence/generated/tes_v04/synthetic_storage_summary.json",
    "evidence/generated/tes_v05/synthetic_one_pass_cycle_snapshot.json",
)
# Exact filename prohibition is independent of provenance text, which is kept.
FORBIDDEN_ASSET_NAMES=(
    "mantilla2010_thermoml_density.csv",
    "thermoml_density.csv",
)
FORBIDDEN_EXTENSIONS=(".pdf",".xlsx",".xls",".joblib",".pkl",".pickle")


def demand(condition: bool, description: str) -> None:
    if not condition:
        raise ValueError(description)


def sha256(path: Path) -> str:
    h=hashlib.sha256()
    with path.open("rb") as f:
        for part in iter(lambda:f.read(1024*1024), b""):
            h.update(part)
    return h.hexdigest()


def _paths_checked(members: list[str], kind: str) -> dict:
    """Check archive member names independent of the zip/tar implementation."""
    demand(kind in ("wheel","sdist"),"unrecognized artifact kind")
    demand(len(members)==len(set(members)), "duplicate archive member")
    roots=set()
    names=set()
    for item in members:
        p=PurePosixPath(item)
        demand(item and not p.is_absolute() and ".." not in p.parts,
               "archive contains unsafe path")
        demand("\\" not in item and "\x00" not in item,
               "archive contains unsafe path separators")
        normalized=item.rstrip("/")
        if not normalized:
            continue
        if kind=="sdist":
            if "/" not in normalized:
                # setuptools records its single top-level directory in tar.
                roots.add(normalized)
                continue
            roots.add(normalized.split("/",1)[0])
            relative=normalized.split("/",1)[1]
        else:
            relative=normalized
        names.add(relative)
        lowered=relative.lower()
        demand(not any(lowered.endswith(bad) for bad in FORBIDDEN_ASSET_NAMES),
               "unapproved NIST Mantilla density dataset in distribution")
        demand(not lowered.endswith(FORBIDDEN_EXTENSIONS),
               "disallowed binary/PDF/serialized asset in distribution")
        demand(not relative.startswith(("evidence/generated/","src/evidence/generated/")),
               "transient generated evidence shipped in distribution")
    if kind=="sdist":
        demand(len(roots)==1, "sdist must have exactly one source-root directory")
    required=REQUIRED_WHEEL if kind=="wheel" else REQUIRED_SDIST
    missing=sorted(set(required)-names)
    demand(not missing, "distribution missing required TES files: "+", ".join(missing))
    if kind=="wheel":
        demand(sum(x.endswith(".dist-info/METADATA") for x in names)==1,
               "wheel metadata missing or ambiguous")
        demand(any(".dist-info/" in x and "LICENSE" in x for x in names),
               "wheel missing BSD license")
    return {"kind":kind,"member_count":len(names),
            "required_checked":len(required),
            "source_root":next(iter(roots)) if roots else None,
            "no_uncleared_restricted_assets":True}


def inspect_distributions(dist: Path) -> dict:
    wheels=sorted(dist.glob("sco2_braytonbench-*.whl"))
    sdists=sorted(dist.glob("sco2_braytonbench-*.tar.gz"))
    demand(len(wheels)==1 and len(sdists)==1,
           "require exactly one wheel and one sdist, remove stale dist files")
    wheel,sdist=wheels[0],sdists[0]
    demand(PARENT_VERSION in wheel.name and PARENT_VERSION in sdist.name,
           "distribution version differs from 0.7.0a0")
    with zipfile.ZipFile(wheel) as archive:
        members=archive.namelist()
        wheel_info=_paths_checked(members,"wheel")
        meta_name=next(m for m in members if m.endswith(".dist-info/METADATA"))
        metadata=archive.read(meta_name).decode("utf-8")
        demand(f"Version: {PARENT_VERSION}" in metadata,
               "wheel metadata version mismatch")
        demand("BSD-3-Clause" in metadata,"wheel license metadata mismatch")
    with tarfile.open(sdist,"r:gz") as archive:
        for member in archive.getmembers():
            demand(not member.issym() and not member.islnk(),
                   "sdist symlinks/hardlinks not permitted")
            demand(member.isfile() or member.isdir(),
                   "sdist contains non-file/non-directory entry")
        sdist_info=_paths_checked(archive.getnames(),"sdist")
    return {
        "wheel":{"filename":wheel.name,"sha256":sha256(wheel),
                 "bytes":wheel.stat().st_size,**wheel_info},
        "sdist":{"filename":sdist.name,"sha256":sha256(sdist),
                 "bytes":sdist.stat().st_size,**sdist_info},
    }


def _compare(a,b,location):
    """Exact structural/categorical match; numeric tolerance is explicit."""
    if type(a) is bool or type(b) is bool:
        demand(type(a) is type(b) and a==b,"boolean mismatch "+location)
    elif isinstance(a,(int,float)) and isinstance(b,(int,float)):
        demand(math.isfinite(float(a)) and math.isfinite(float(b)),
               "nonfinite numeric replay "+location)
        demand(math.isclose(a,b,rel_tol=2e-9,abs_tol=2e-8),
               f"numeric replay drift {location}: {a} versus {b}")
    elif isinstance(a,dict):
        demand(isinstance(b,dict) and set(a)==set(b),
               "JSON key mismatch "+location)
        for key in sorted(a):
            _compare(a[key],b[key],location+"/"+str(key))
    elif isinstance(a,list):
        demand(isinstance(b,list) and len(a)==len(b),
               "JSON list length mismatch "+location)
        for i,(x,y) in enumerate(zip(a,b)):
            _compare(x,y,location+"/"+str(i))
    else:
        demand(type(a) is type(b) and a==b,
               "categorical replay mismatch "+location)


def _csv_data(path:Path) -> dict:
    with path.open(newline="",encoding="utf-8") as f:
        reader=csv.DictReader(f)
        headings=reader.fieldnames
        rows=list(reader)
    demand(bool(headings) and bool(rows),"empty CSV replay "+str(path))
    demand(len(headings)==len(set(headings)),"ambiguous CSV headers")
    demand(all(None not in row for row in rows),"malformed CSV row")
    return {"columns":headings,"rows":rows}


def _csv_compare(a:Path,b:Path,where:str) -> int:
    left,right=_csv_data(a),_csv_data(b)
    demand(left["columns"]==right["columns"],"CSV columns differ "+where)
    demand(len(left["rows"])==len(right["rows"]),
           "CSV row counts differ "+where)
    for i,(x,y) in enumerate(zip(left["rows"],right["rows"])):
        for field in left["columns"]:
            va,vb=x[field],y[field]
            try:
                xnum,ynum=float(va),float(vb)
            except (ValueError,TypeError):
                demand(va==vb,"CSV categorical mismatch "+where+"/"+field)
            else:
                _compare(xnum,ynum,f"{where}/{i}/{field}")
    return len(left["rows"])


def replay(reference:Path,candidate:Path,dist:Path,out:Path,
           source_sha:str) -> dict:
    """Wheel and sdist output comparison plus immutable archive provenance."""
    demand(re.fullmatch(r"[0-9a-f]{40}",source_sha) is not None,
           "source SHA must be a 40-char immutable git object id")
    archives=inspect_distributions(dist)
    cases={}
    hashes={}
    for label,root in (("wheel",reference),("sdist",candidate)):
        hashes[label]={}
        for relative in REPLAY_ARTIFACTS:
            target=root/relative
            demand(target.is_file(),"missing isolated-install replay "+label+"/"+relative)
            hashes[label][relative]=sha256(target)
            if relative.endswith(".json"):
                obj=json.loads(target.read_text(encoding="utf-8"))
                demand(isinstance(obj,dict),"JSON result root must be object")
                if relative.endswith("tes_v09_installed_probe.json"):
                    demand(obj.get("schema")=="tes-v09-isolated-installed-replay-1",
                           "installed replay schema drift")
                    demand(obj.get("parent_package")==PARENT_VERSION,
                           "installed package version drift")
                    demand(obj.get("sealed_v07_evaluation_repeated") is False,
                           "v0.7 holdout claims misrepresented")
                    demand(len(obj.get("scenarios",{}))==6,
                           "installed TES scenario family missing")
    for rel in REPLAY_ARTIFACTS:
        a,b=reference/rel,candidate/rel
        if rel.endswith(".json"):
            _compare(json.loads(a.read_text("utf-8")),
                     json.loads(b.read_text("utf-8")),rel)
            cases[rel]={"format":"json","matched":True}
        else:
            count=_csv_compare(a,b,rel)
            cases[rel]={"format":"csv","rows":count,"matched":True}
    report={
        "schema":SCHEMA,
        "classification":"offline_software_distribution_and_numerical_replay",
        "source_commit":source_sha,
        "parent_package_version":PARENT_VERSION,
        "distribution":archives,
        "evidence_hashes":hashes,
        "comparisons":cases,
        "numerical_rtol":2e-9,
        "numerical_atol":2e-8,
        "wheel_sdist_same_scenario_replay":True,
        "unapproved_NIST_Mantilla_table_absent_from_distributions":True,
        "redistribution_rights_legal_clearance_obtained":False,
        "actual_plant_experimental_validation":False,
        "frozen_v07_heldout_retraining_performed":False,
        "reviewer_scientific_approval":False,
        "v1_release_authorized":False,
        "next_gates":["third_party_rights_issue_27",
                      "independent_qualified_review_issue_28",
                      "TES_v1_release_decision"],
    }
    out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(report,indent=2,sort_keys=True,allow_nan=False)+"\n",
                   encoding="utf-8")
    return report


def verify(report_path:Path,dist:Path,reference:Path,candidate:Path) -> dict:
    """Reject post-run changed evidence/distributions and manifest tampering."""
    report=json.loads(report_path.read_text(encoding="utf-8"))
    demand(report.get("schema")==SCHEMA,"distribution manifest schema changed")
    demand(report.get("v1_release_authorized") is False,
           "manifest cannot authorize parent v1 release")
    demand(report.get("wheel_sdist_same_scenario_replay") is True,
           "cross-install verification flag absent")
    demand(set(report.get("evidence_hashes",{}))=={"wheel","sdist"},
           "missing replay type in manifest")
    new=inspect_distributions(dist)
    demand(new==report["distribution"],"distribution archive changed after audit")
    for name,root in (("wheel",reference),("sdist",candidate)):
        demand(set(report["evidence_hashes"][name])==set(REPLAY_ARTIFACTS),
               "evidence inventory changed")
        for relative in REPLAY_ARTIFACTS:
            demand(sha256(root/relative)==report["evidence_hashes"][name][relative],
                   "replay evidence hash mismatch "+name+"/"+relative)
    return report


def main():
    p=argparse.ArgumentParser(description=__doc__)
    sp=p.add_subparsers(dest="action",required=True)
    a=sp.add_parser("audit")
    for sub in (a,):
        sub.add_argument("--dist",type=Path,required=True)
    b=sp.add_parser("replay")
    b.add_argument("--dist",type=Path,required=True)
    b.add_argument("--wheel-root",type=Path,required=True)
    b.add_argument("--sdist-root",type=Path,required=True)
    b.add_argument("--out",type=Path,required=True)
    b.add_argument("--source-sha",required=True)
    c=sp.add_parser("verify")
    c.add_argument("--dist",type=Path,required=True)
    c.add_argument("--wheel-root",type=Path,required=True)
    c.add_argument("--sdist-root",type=Path,required=True)
    c.add_argument("--report",type=Path,required=True)
    args=p.parse_args()
    if args.action=="audit":
        answer=inspect_distributions(args.dist)
    elif args.action=="replay":
        answer=replay(args.wheel_root,args.sdist_root,args.dist,
                      args.out,args.source_sha)
    else:
        answer=verify(args.report,args.dist,args.wheel_root,args.sdist_root)
    print(json.dumps({"action":args.action,
                      "tes_v09_software_gate":"PASS",
                      "v1_release_authorized":False,
                      "wheel_and_sdist_checked":True,
                      "schema":SCHEMA},sort_keys=True))
    return answer

if __name__=="__main__":
    main()
