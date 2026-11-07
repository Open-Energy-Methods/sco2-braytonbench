#!/usr/bin/env python3
"""TES-v0.7 frozen-split reduced-order model, training and evaluation.

Training reads ONLY the predeclared 256 train and 64 validation synthetic
trajectories. The test and OOD file SHA256 values are copied from the
pre-existing v0.6 generator manifest without opening their labels.

The 'evaluate' entry point is a separate process and cannot fit or
select a hyperparameter; it verifies the immutable dataset/model hashes
before first reading 128 test and 64 OOD trajectories. Results stay
untuned after holdout evaluation. There is no plant-measurement claim.

Model persistence uses joblib/pickle. NEVER load an arbitrary/untrusted
model artifact. A SHA256 hash prevents accidental drift but is NOT a
cryptographic publisher signature.
"""
from __future__ import annotations

import argparse
from collections import defaultdict
import csv
import hashlib
import json
import math
from pathlib import Path
import statistics
import time

from sco2_braytonbench.tes_surrogate import (
    FEATURE_NAMES, TARGET_NAMES, features, normalized_targets,
    denormalize, clip_with_flag,
)

COUNTS = {"train": 256, "validation": 64, "test": 128, "ood": 64}
SAMPLES_PER_RUN = 16
CANDIDATES = {
    "compact": dict(max_iter=140, max_leaf_nodes=15, min_samples_leaf=12,
                    learning_rate=.085, l2_regularization=.05),
    "balanced": dict(max_iter=210, max_leaf_nodes=31, min_samples_leaf=12,
                     learning_rate=.065, l2_regularization=.1),
    "smooth": dict(max_iter=260, max_leaf_nodes=15, min_samples_leaf=18,
                   learning_rate=.045, l2_regularization=1.),
}
SCORING = "validation_outlet_rmse_k_plus_100_times_soc_rmse"
SOURCE_CLASS = "synthetic-1d-2t-8-cell-packed-bed-only"


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def ensure_sha(path: Path, expected: str) -> None:
    actual=digest(path)
    if actual != expected:
        raise ValueError(f"source artifact changed: {path.name}: expected {expected}, got {actual}")


def load_manifest(data: Path) -> dict:
    m=json.loads((data/"tes_dataset_manifest.json").read_text(encoding="utf-8"))
    if (m["counts"] != COUNTS or m["samples_per_run"] != SAMPLES_PER_RUN
            or m["n_cells"] != 8
            or m["evidence_class"] != "entirely-synthetic-two-temperature-finite-volume"
            or m["split_integrity"]["duplicate_run_ids"] != 0
            or m["split_integrity"]["time_row_random_split"]):
        raise ValueError("dataset manifest violates predeclared split or physics contract")
    if len(m["sha256"]) != 8:
        raise ValueError("expected exactly four trajectory and four index tables")
    return m


def read_partition(data: Path, manifest: dict, split: str) -> tuple[list[dict], set[str]]:
    """One partition is read only when explicitly requested by the caller."""
    if split not in COUNTS:
        raise ValueError("unknown split")
    p=data/f"tes_{split}_trajectories.csv"
    index=data/f"tes_{split}_run_index.csv"
    for x in (p,index):
        ensure_sha(x,manifest["sha256"][x.name])
    with p.open(newline="",encoding="utf-8") as f:
        rows=list(csv.DictReader(f))
    with index.open(newline="",encoding="utf-8") as f:
        entries=list(csv.DictReader(f))
    if len(rows) != COUNTS[split]*SAMPLES_PER_RUN or len(entries)!=COUNTS[split]:
        raise ValueError(f"invalid {split} sample or complete-run count")
    ids={x["run_id"] for x in rows}
    if len(ids)!=COUNTS[split] or ids!={e["run_id"] for e in entries}:
        raise ValueError(f"{split} run IDs inconsistent with index")
    grouped=defaultdict(list)
    for row in rows:
        if row["split"] != split:
            raise ValueError("split label mismatch")
        grouped[row["run_id"]].append(row)
        features(row)
        y=normalized_targets(row)
        if not all(math.isfinite(v) for v in y):
            raise ValueError("nonfinite target")
        # Check signed LHS ranges and no fake OOD designated in-domain.
        hot=float(row["hot_inlet_k"])
        flow=float(row["flow_kg_s"])
        if split=="ood":
            if hot<=800 or flow<=.1:
                raise ValueError("OOD must be outside training bounds")
        elif hot>800 or flow>.1:
            raise ValueError("in-domain row outside declared training envelope")
    for run_id,run in grouped.items():
        if (len(run)!=16
           or [x["phase"] for x in run]!=["charge"]*8+["discharge"]*8
           or [float(x["phase_fraction"]) for x in run]!=[i/8 for i in range(1,9)]*2):
            raise ValueError(f"invalid whole-run trajectory ordering: {run_id}")
    return rows,ids


def as_arrays(rows: list[dict]):
    import numpy as np
    X=np.asarray([features(r) for r in rows],dtype="float64")
    y=np.asarray([normalized_targets(r) for r in rows],dtype="float64")
    if X.shape!=(len(rows),len(FEATURE_NAMES)) or y.shape!=(len(rows),2):
        raise ValueError("feature matrix contract changed")
    return X,y


def predict_rows(rows: list[dict], models) -> tuple[list[tuple[float,float]],int]:
    import numpy as np
    X=np.asarray([features(r) for r in rows],dtype="float64")
    raw=np.column_stack((models[0].predict(X),models[1].predict(X)))
    pred=[]
    violations=0
    for row, values in zip(rows,raw):
        theta,flag1=clip_with_flag(float(values[0]))
        soc,flag2=clip_with_flag(float(values[1]))
        violations+=int(flag1)+int(flag2)
        pred.append((denormalize(row,theta),soc))
    return pred,violations


def exact_targets(rows: list[dict]) -> list[tuple[float,float]]:
    return [(float(r["fluid_outlet_k"]),float(r["solid_soc"])) for r in rows]


def metrics(rows: list[dict], predictions: list[tuple[float,float]]) -> dict:
    if len(rows)!=len(predictions):
        raise ValueError("prediction/row length mismatch")
    squared_t=[];squared_s=[];errors_t=[];run_t=defaultdict(list);run_s=defaultdict(list)
    for row,(pred_t,pred_s) in zip(rows,predictions):
        truth_t=float(row["fluid_outlet_k"])
        truth_s=float(row["solid_soc"])
        if not all(math.isfinite(v) for v in (pred_t,pred_s)):
            raise ValueError("nonfinite predictive estimate")
        dt=pred_t-truth_t;ds=pred_s-truth_s
        squared_t.append(dt*dt);squared_s.append(ds*ds)
        errors_t.append(abs(dt))
        run_t[row["run_id"]].append(dt*dt)
        run_s[row["run_id"]].append(ds*ds)
    rmse_t=math.sqrt(math.fsum(squared_t)/len(rows))
    rmse_s=math.sqrt(math.fsum(squared_s)/len(rows))
    group_errors=sorted(math.sqrt(math.fsum(errors)/len(errors))
                        for errors in run_t.values())
    p95=group_errors[math.ceil(.95*len(group_errors))-1]
    return {
        "runs":len(run_t),"samples":len(rows),
        "outlet_rmse_k":rmse_t,
        "outlet_nrmse_percent_of_300k_span":100*rmse_t/300,
        "soc_rmse_fraction":rmse_s,
        "outlet_absolute_error_p95_k":sorted(errors_t)[math.ceil(.95*len(errors_t))-1],
        "complete_run_outlet_rmse_p95_k":p95,
        "outlet_abs_error_median_k":statistics.median(errors_t),
        "outlet_error_bias_k":math.fsum((p[0]-float(r["fluid_outlet_k"]))
                                          for r,p in zip(rows,predictions))/len(rows),
    }


def train(data: Path, out: Path) -> dict:
    from sklearn.ensemble import HistGradientBoostingRegressor
    import joblib
    out.mkdir(parents=True,exist_ok=True)
    m=load_manifest(data)
    # Deliberately do not open the 'test' or 'ood' data files during train.
    train_rows,train_ids=read_partition(data,m,"train")
    validation_rows,val_ids=read_partition(data,m,"validation")
    if train_ids & val_ids:
        raise ValueError("train/validation whole-run leakage")
    X,y=as_arrays(train_rows)
    candidates={}
    best=None
    started=time.perf_counter()
    for name,kwargs in CANDIDATES.items():
        models=tuple(
            HistGradientBoostingRegressor(
                **kwargs,random_state=20261107,early_stopping=False
            ).fit(X,y[:,i]) for i in range(2)
        )
        predictions,violations=predict_rows(validation_rows,models)
        result=metrics(validation_rows,predictions)
        score=result["outlet_rmse_k"]+100*result["soc_rmse_fraction"]
        candidates[name]={
            "validation":result,"selection_score":score,
            "raw_physical_bound_violations":violations,
            "hyperparameters":kwargs
        }
        if best is None or (score,name)<(best[0],best[1]):
            best=(score,name,models)
    assert best is not None
    _,selected,models=best
    path=out/"tes_rom_model.joblib"
    joblib.dump({"models":models,"selected":selected,
                 "feature_names":FEATURE_NAMES,"target_names":TARGET_NAMES},
                path,compress=3)
    frozen={
        "schema":"tes-rom-frozen-train-v0.7",
        "evidence_class":SOURCE_CLASS,
        "training_only_splits":["train","validation"],
        "test_labels_opened_during_training":False,
        "ood_labels_opened_during_training":False,
        "selection_rule":SCORING,
        "selected":selected,
        "feature_names":FEATURE_NAMES,
        "target_names":TARGET_NAMES,
        "candidate_validation_results":candidates,
        "train_runs":len(train_ids),
        "validation_runs":len(val_ids),
        "train_id_sha256":hashlib.sha256("\n".join(sorted(train_ids)).encode()).hexdigest(),
        "validation_id_sha256":hashlib.sha256("\n".join(sorted(val_ids)).encode()).hexdigest(),
        "dataset_manifest_sha256":digest(data/"tes_dataset_manifest.json"),
        "source_split_sha256":dict(m["sha256"]),
        "model_sha256":digest(path),
        "training_wall_seconds":time.perf_counter()-started,
        "scikit_learn_version":__import__("sklearn").__version__,
        "numpy_version":__import__("numpy").__version__,
        "quality_thresholds_predeclared":{
            "test_outlet_rmse_k_lte":10.0,
            "test_soc_rmse_fraction_lte":.05,
            "must_beat_persistence":True,
            "must_beat_2cell_physics_baseline":True,
            "ood_performance_has_no_acceptance_threshold":True,
        },
        "trust_warning":"joblib uses Python pickle; only load trusted local CI-produced model files",
    }
    (out/"tes_rom_frozen_selection.json").write_text(
        json.dumps(frozen,indent=2,sort_keys=True)+"\n",encoding="utf8")
    return frozen


def _naive(rows: list[dict]) -> list[tuple[float,float]]:
    return [(float(r["initial_k"]),0.) for r in rows]


def _coarse_physics(rows: list[dict], *, n_cells: int=2) -> list[tuple[float,float]]:
    """Strong comparison: same verified physical model at coarse N=2.

    Operates only after freeze; no coarse model outputs are fitting labels.
    """
    from sco2_braytonbench.thermal_storage import (
        PackedBedSpec,PackedBedState,solid_soc,step_packed_bed
    )
    # Geometry is a frozen v0.6 dataset contract, independently checked
    # by the manifest. Avoid importing a sibling script when executed via
    # `python scripts/tes_surrogate_pipeline.py` outside pytest.
    def spec(hv_w_m3_k, *, n_cells):
        return PackedBedSpec(
            length_m=1.0, area_m2=0.1, porosity=0.5,
            fluid_density_kg_m3=5.0, fluid_cp_j_kg_k=1000.0,
            solid_density_kg_m3=1000.0, solid_cp_j_kg_k=700.0,
            interphase_hv_w_m3_k=hv_w_m3_k, n_cells=n_cells,
        )
    preds=[]
    current_run=None
    for row in rows:
        rid=row["run_id"]
        if rid!=current_run:
            s=spec(float(row["hv_w_m3_k"]),n_cells=n_cells)
            t0=float(row["initial_k"])
            st=PackedBedState.uniform(s,t0,t0)
            current_run=rid
        step=step_packed_bed(
            s,st,inlet_k=float(row["inlet_k"]),
            mdot_kg_s=float(row["signed_flow_kg_s"]),
            duration_s=float(row["phase_duration_s"])/8,
        )
        st=step.state
        soc=solid_soc(s,st,cold_k=float(row["initial_k"]),
                      hot_k=float(row["hot_inlet_k"]))
        preds.append((step.outlet_k,soc))
    return preds


def _highres_benchmark(rows: list[dict], *, n_runs: int=12) -> tuple[float,int]:
    """Local measured wall time only; not a hardware-independent speedup."""
    first_ids=list(dict.fromkeys(r["run_id"] for r in rows))[:n_runs]
    chosen=[r for r in rows if r["run_id"] in set(first_ids)]
    start=time.perf_counter()
    _coarse_physics(chosen,n_cells=8)
    return time.perf_counter()-start,len(chosen)


def evaluate(data: Path, frozen_dir: Path, out: Path, *,
             fail_on_quality: bool=False) -> dict:
    import joblib
    import sklearn
    out.mkdir(parents=True,exist_ok=True)
    frozen=json.loads((frozen_dir/"tes_rom_frozen_selection.json").read_text("utf-8"))
    if (frozen.get("schema")!="tes-rom-frozen-train-v0.7"
          or frozen.get("test_labels_opened_during_training") is not False
          or frozen.get("ood_labels_opened_during_training") is not False
          or frozen.get("training_only_splits")!=["train","validation"]
          or tuple(frozen["feature_names"])!=FEATURE_NAMES):
        raise ValueError("frozen training/feature contract invalid")
    if frozen["scikit_learn_version"]!=sklearn.__version__:
        raise ValueError("model library version drift; regenerate training artifact")
    m=load_manifest(data)
    ensure_sha(data/"tes_dataset_manifest.json",frozen["dataset_manifest_sha256"])
    if m["sha256"]!=frozen["source_split_sha256"]:
        raise ValueError("dataset split manifest differs from frozen fit")
    model_path=frozen_dir/"tes_rom_model.joblib"
    ensure_sha(model_path,frozen["model_sha256"])
    # Security: joblib may execute code on load. Do not use arbitrary artifacts.
    package=joblib.load(model_path)
    if (package["selected"]!=frozen["selected"]
         or tuple(package["feature_names"])!=FEATURE_NAMES):
        raise ValueError("frozen model identity changed")
    models=package["models"]
    # Only NOW open test/OOD labels, in a separate --stage evaluate process.
    test_rows,test_ids=read_partition(data,m,"test")
    ood_rows,ood_ids=read_partition(data,m,"ood")
    if test_ids & ood_ids:
        raise ValueError("test/OOD whole-run ID leakage")
    outcome={
        "schema":"tes-rom-sealed-evaluation-v0.7",
        "evidence_class":SOURCE_CLASS,
        "training_performed_during_evaluate":False,
        "selection_changed_after_test_access":False,
        "model_sha256":frozen["model_sha256"],
        "dataset_manifest_sha256":frozen["dataset_manifest_sha256"],
        "selected_on_validation_only":frozen["selected"],
        "test_and_ood_run_counts":{"test":len(test_ids),"ood":len(ood_ids)},
        "quality_thresholds":frozen["quality_thresholds_predeclared"],
        "partitions":{},
        "runtime_wall_seconds":{},
        "limitations":[
            "Only generated 8-cell, constant-property 1D sensible packed-bed data",
            "Prescribed complete future schedule is known: NOT a causal online controller",
            "A test set is procedurally sealed; public CSVs are not secret",
            "No physical experiment, calibrated material property or CO2-fluid inventory",
            "Benchmarked wall times are machine-specific; not a universal runtime guarantee",
        ],
    }
    predictions_table=[]
    for split,rows in (("test",test_rows),("ood",ood_rows)):
        started=time.perf_counter()
        prediction,bounds=predict_rows(rows,models)
        model_seconds=time.perf_counter()-started
        naive=_naive(rows)
        coarse_started=time.perf_counter()
        coarse=_coarse_physics(rows,n_cells=2)
        coarse_seconds=time.perf_counter()-coarse_started
        scores={
            "surrogate":metrics(rows,prediction),
            "persistence":metrics(rows,naive),
            "two_cell_physics":metrics(rows,coarse),
            "raw_normalized_bound_violations":bounds,
            "model_inference_seconds":model_seconds,
            "two_cell_baseline_seconds":coarse_seconds,
        }
        outcome["partitions"][split]=scores
        for row,estimate,baseline in zip(rows,prediction,coarse):
            predictions_table.append({
                "split":split,"run_id":row["run_id"],
                "phase":row["phase"],"phase_fraction":row["phase_fraction"],
                "true_outlet_k":row["fluid_outlet_k"],
                "predicted_outlet_k":estimate[0],
                "coarse_two_cell_outlet_k":baseline[0],
                "true_soc":row["solid_soc"],
                "predicted_soc":estimate[1],
                "coarse_two_cell_soc":baseline[1],
            })
    scores=outcome["partitions"]["test"]
    t=scores["surrogate"]; b=scores["persistence"]; c=scores["two_cell_physics"]
    th=frozen["quality_thresholds_predeclared"]
    criteria={
        "outlet_rmse_under_10K":t["outlet_rmse_k"]<=th["test_outlet_rmse_k_lte"],
        "soc_rmse_under_0p05":t["soc_rmse_fraction"]<=th["test_soc_rmse_fraction_lte"],
        "outlet_better_than_persistence":t["outlet_rmse_k"]<b["outlet_rmse_k"],
        "soc_better_than_persistence":t["soc_rmse_fraction"]<b["soc_rmse_fraction"],
        "outlet_better_than_two_cell":t["outlet_rmse_k"]<c["outlet_rmse_k"],
        "soc_better_than_two_cell":t["soc_rmse_fraction"]<c["soc_rmse_fraction"],
    }
    outcome["test_acceptance_criteria"]=criteria
    outcome["test_acceptance_all_met"]=all(criteria.values())
    n8_time,n8_rows=_highres_benchmark(test_rows,n_runs=12)
    outcome["runtime_wall_seconds"]["reference_eight_cell_first_12_test_runs"]=n8_time
    outcome["runtime_wall_seconds"]["reference_eight_cell_samples"]=n8_rows
    outcome["runtime_wall_seconds"]["surrogate_first_12_test_runs"]=(scores["model_inference_seconds"]
         *n8_rows/len(test_rows))
    outcome["runtime_wall_seconds"]["estimated_speed_ratio_eight_cell_over_model"]=(
        n8_time/max(1e-12,outcome["runtime_wall_seconds"]["surrogate_first_12_test_runs"]))
    path=out/"tes_rom_sealed_predictions.csv"
    with path.open("w",newline="",encoding="utf-8") as f:
        writer=csv.DictWriter(f,fieldnames=list(predictions_table[0]))
        writer.writeheader();writer.writerows(predictions_table)
    outcome["predictions_csv_sha256"]=digest(path)
    (out/"tes_rom_holdout_report.json").write_text(
        json.dumps(outcome,indent=2,sort_keys=True)+"\n",encoding="utf8")
    if fail_on_quality and not outcome["test_acceptance_all_met"]:
        raise RuntimeError("PREDECLARED holdout acceptance criteria not met; "
                           "report preserved; DO NOT retune against test set")
    return outcome


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("stage",choices=("train","evaluate"))
    ap.add_argument("--data",type=Path,default=Path("evidence/generated/tes_v06"))
    ap.add_argument("--model-dir",type=Path,default=Path("evidence/generated/tes_v07/frozen"))
    ap.add_argument("--out",type=Path,default=Path("evidence/generated/tes_v07/evaluation"))
    ap.add_argument("--fail-on-quality",action="store_true")
    args=ap.parse_args()
    if args.stage=="train":
        result=train(args.data,args.model_dir)
        print(json.dumps({"selected":result["selected"],
          "validation":result["candidate_validation_results"],
          "test_labels_opened":False},indent=2))
    else:
        result=evaluate(args.data,args.model_dir,args.out,
                        fail_on_quality=args.fail_on_quality)
        print(json.dumps({
            "selected":result["selected_on_validation_only"],
            "test":result["partitions"]["test"],
            "ood":result["partitions"]["ood"],
            "predeclared_acceptance":result["test_acceptance_criteria"],
            "all_met":result["test_acceptance_all_met"],
            "runtime":result["runtime_wall_seconds"],
        },indent=2))


if __name__=="__main__":
    main()
