"""TES-v0.7 data isolation, physics-based features, model freeze and tamper gates."""
from copy import deepcopy
import json
import math
import subprocess
import sys
from pathlib import Path

import pytest

from sco2_braytonbench.tes_surrogate import (
    FEATURE_NAMES, FORBIDDEN_INPUT_FIELDS, features, normalized_targets,
    denormalize, clip_with_flag
)
from scripts.tes_generate_synthetic_dataset import (
    generate_dataset,COUNTS_SMOKE
)
import scripts.tes_surrogate_pipeline as pipeline


def sample():
    return {
        "phase":"charge", "phase_fraction":.25,
        "charge_turnovers":2., "discharge_turnovers":3.,
        "initial_k":360., "hot_inlet_k":660.,
        "flow_kg_s":.05, "hv_w_m3_k":500.,
        "fluid_outlet_k":450., "solid_soc":.31,
        "boundary_energy_j":1e6, "first_law_residual_j":0.,
        "courant":.3, "exchange_fluid":.2, "exchange_solid":.1,
    }


def test_features_do_not_consume_current_targets_or_energy_residuals():
    a=sample()
    original=features(a)
    b=deepcopy(a)
    for name in FORBIDDEN_INPUT_FIELDS:
        b[name]="THIS IS AN ILLEGAL LABEL NOT A FEATURE"
    assert features(b)==original
    assert len(original)==len(FEATURE_NAMES)
    assert normalized_targets(a)==pytest.approx((.3,.31))
    with pytest.raises(ValueError):
        normalized_targets(b)


def test_constant_property_normalization_preserves_temperature_affinity():
    a=sample()
    b=deepcopy(a)
    b["initial_k"]=500.
    b["hot_inlet_k"]=800.
    b["fluid_outlet_k"]=590.
    assert features(a)==features(b)
    assert normalized_targets(a)==normalized_targets(b)
    assert denormalize(b,.3)==pytest.approx(590.)
    assert features(dict(a,phase="discharge"))!=features(a)


def test_flagged_bounding_not_hidden():
    assert clip_with_flag(-.4)==(0.,True)
    assert clip_with_flag(1.3)==(1.,True)
    assert clip_with_flag(.4)==(.4,False)
    with pytest.raises(ValueError):
        clip_with_flag(float("nan"))
    with pytest.raises(ValueError):
        features(dict(sample(),phase="unknown"))
    with pytest.raises(ValueError):
        features(dict(sample(),flow_kg_s=0.))


@pytest.fixture
def smoke_dataset(tmp_path,monkeypatch):
    pytest.importorskip("sklearn")
    monkeypatch.setattr(pipeline,"COUNTS",dict(COUNTS_SMOKE))
    source=tmp_path/"dataset"
    manifest=generate_dataset(source,counts=COUNTS_SMOKE,n_cells=8)
    assert manifest["counts"]==COUNTS_SMOKE
    return source,tmp_path


def test_training_never_opens_future_heldouts(smoke_dataset):
    source,tmp_path=smoke_dataset
    # The test/ood CSV files themselves DO NOT EXIST during training.
    # The immutable v0.6 manifest already contains their expected hashes.
    sealed=[]
    for split in ("test","ood"):
        for kind in ("trajectories","run_index"):
            f=source/f"tes_{split}_{kind}.csv"
            new=f.with_suffix(".sealed")
            f.rename(new)
            sealed.append((f,new))
    frozen_dir=tmp_path/"model"
    frozen=pipeline.train(source,frozen_dir)
    assert frozen["test_labels_opened_during_training"] is False
    assert frozen["ood_labels_opened_during_training"] is False
    assert frozen["training_only_splits"]==["train","validation"]
    assert frozen["selected"] in pipeline.CANDIDATES
    assert len(frozen["candidate_validation_results"])==3
    assert (frozen_dir/"tes_rom_model.joblib").exists()
    for p,q in sealed:
        q.rename(p)
    report=pipeline.evaluate(source,frozen_dir,tmp_path/"eval")
    assert report["training_performed_during_evaluate"] is False
    assert report["selection_changed_after_test_access"] is False
    assert report["test_and_ood_run_counts"]=={"test":2,"ood":2}
    assert report["partitions"]["test"]["surrogate"]["samples"]==32
    assert report["partitions"]["ood"]["surrogate"]["samples"]==32
    assert report["partitions"]["test"]["two_cell_physics"]["outlet_rmse_k"]>=0
    assert report["test_acceptance_all_met"]==all(
        report["test_acceptance_criteria"].values())


def test_dataset_hash_tampering_rejected_before_holdout_labels(smoke_dataset):
    source,tmp_path=smoke_dataset
    frozen_dir=tmp_path/"model"
    pipeline.train(source,frozen_dir)
    target=source/"tes_test_trajectories.csv"
    with target.open("a",encoding="utf8") as f:
        f.write("fabricated,hidden,test,row\n")
    with pytest.raises(ValueError,match="source artifact changed"):
        pipeline.evaluate(source,frozen_dir,tmp_path/"eval")


def test_frozen_model_sha_rejects_modified_payload(smoke_dataset):
    source,tmp_path=smoke_dataset
    frozen_dir=tmp_path/"model"
    pipeline.train(source,frozen_dir)
    with (frozen_dir/"tes_rom_model.joblib").open("ab") as f:
        f.write(b"tampered")
    with pytest.raises(ValueError,match="source artifact changed"):
        pipeline.evaluate(source,frozen_dir,tmp_path/"eval")


def test_frozen_selection_must_not_be_relabeled(smoke_dataset):
    source,tmp_path=smoke_dataset
    frozen_dir=tmp_path/"model"
    pipeline.train(source,frozen_dir)
    report_file=frozen_dir/"tes_rom_frozen_selection.json"
    obj=json.loads(report_file.read_text("utf8"))
    obj["training_only_splits"]=["train","validation","test"]
    report_file.write_text(json.dumps(obj),encoding="utf8")
    with pytest.raises(ValueError,match="frozen training/feature contract invalid"):
        pipeline.evaluate(source,frozen_dir,tmp_path/"eval")


def test_validation_metric_has_known_independent_result():
    rows=[dict(sample(),run_id="A",fluid_outlet_k=400,solid_soc=.2),
          dict(sample(),run_id="A",fluid_outlet_k=500,solid_soc=.4),
          dict(sample(),run_id="B",fluid_outlet_k=600,solid_soc=.6)]
    p=[(403,.1),(496,.5),(600,.6)]
    m=pipeline.metrics(rows,p)
    assert m["outlet_rmse_k"]==pytest.approx(math.sqrt(25/3))
    assert m["soc_rmse_fraction"]==pytest.approx(math.sqrt(.02/3))
    assert m["complete_run_outlet_rmse_p95_k"]==pytest.approx(math.sqrt(25/2))
    assert m["runs"]==2 and m["samples"]==3


def test_evaluation_direct_cli_not_only_pytest_import_context(smoke_dataset):
    """Exercise the actual documented script invocation in an isolated process."""
    source,tmp_path=smoke_dataset
    frozen_dir=tmp_path/"model"
    pipeline.train(source,frozen_dir)
    script=Path(pipeline.__file__).resolve()
    completed=subprocess.run([
        sys.executable,str(script),"evaluate",
        "--data",str(source),
        "--model-dir",str(frozen_dir),
        "--out",str(tmp_path/"direct_cli")
    ],cwd=str(script.parents[1]),capture_output=True,text=True)
    assert completed.returncode==0,completed.stderr
    report=json.loads((tmp_path/"direct_cli"/"tes_rom_holdout_report.json").read_text("utf8"))
    assert report["test_and_ood_run_counts"]=={"test":2,"ood":2}
