"""TES-v0.6: whole-trajectory LHS partition, reproducibility and provenance."""
from pathlib import Path
import csv
import json
import math

import pytest

from scripts.tes_generate_synthetic_dataset import (
    COUNTS_FULL, SEEDS, SAMPLE_TIMES, _lhs, _parameters,
    generate_dataset
)


def test_declared_full_sample_counts_are_not_silently_truncated():
    assert COUNTS_FULL == {
        "train": 256, "validation": 64, "test": 128, "ood": 64
    }
    assert sum(COUNTS_FULL.values()) == 512
    assert len(set(SEEDS.values())) == 4


def test_latin_hypercube_marginal_stratification():
    points = _lhs(20, 6, 1941)
    assert len(points) == 20
    for axis in range(6):
        bins = sorted(int(point[axis] * 20) for point in points)
        assert bins == list(range(20))
    assert points == _lhs(20, 6, 1941)
    assert points != _lhs(20, 6, 1942)


def test_ood_has_truly_outside_train_envelope():
    x = _parameters("ood", (.2,.5,.7,.1,.3,.4))
    assert x["hot_inlet_k"] > 800
    assert x["flow_kg_s"] > .1
    assert x["initial_k"] >= 340
    p = _parameters("train", (.2,.5,.7,.1,.3,.4))
    assert 500 <= p["hot_inlet_k"] <= 800
    assert .01 <= p["flow_kg_s"] <= .1
    assert 340 <= p["initial_k"] <= 430


def _read_rows(path):
    with path.open(newline="",encoding="utf-8") as f:
        return list(csv.DictReader(f))


def test_disjoint_splits_reproducibility_and_energy_ledger(tmp_path):
    counts = {"train": 2, "validation": 1, "test": 2, "ood": 1}
    a=generate_dataset(tmp_path/"a", counts=counts)
    b=generate_dataset(tmp_path/"b", counts=counts)
    assert a == b, "same seeds/inputs must produce byte-identical payloads"
    assert a["split_integrity"]["duplicate_run_ids"] == 0
    assert a["split_integrity"]["distinct_run_ids"] == sum(counts.values())
    assert a["evidence_class"].startswith("entirely-synthetic")
    assert "CIC energiGUNE storage measurements" in a["excluded_claims"]
    assert a["sha256"] == b["sha256"]
    ids = set()
    for split, nruns in counts.items():
        rows = _read_rows(tmp_path/"a"/f"tes_{split}_trajectories.csv")
        runs = _read_rows(tmp_path/"a"/f"tes_{split}_run_index.csv")
        assert len(rows) == nruns*2*SAMPLE_TIMES
        assert len(runs) == nruns
        split_ids={r["run_id"] for r in rows}
        assert len(split_ids)==nruns
        assert not split_ids.intersection(ids)
        ids.update(split_ids)
        for run_id in split_ids:
            sequence = [x for x in rows if x["run_id"] == run_id]
            assert len(sequence)==2*SAMPLE_TIMES
            assert [x["phase"] for x in sequence] == (
                ["charge"]*SAMPLE_TIMES + ["discharge"]*SAMPLE_TIMES
            )
            assert all(float(a["elapsed_s"]) < float(b["elapsed_s"])
                       for a,b in zip(sequence,sequence[1:]))
            assert all(0 < float(x["phase_fraction"]) <= 1 for x in sequence)
        for row in rows:
            assert math.isfinite(float(row["fluid_outlet_k"]))
            assert math.isfinite(float(row["solid_soc"]))
            assert float(row["courant"]) <= .75+1e-12
            assert float(row["exchange_fluid"]) <= .75+1e-12
            assert float(row["exchange_solid"]) <= .75+1e-12
            assert abs(float(row["first_law_residual_j"])) <= max(
                3e-5,abs(float(row["boundary_energy_j"]))*1e-9
            )
            if split=="ood":
                assert float(row["hot_inlet_k"]) > 800
                assert float(row["flow_kg_s"]) > .1
            else:
                assert float(row["hot_inlet_k"]) <= 800
                assert float(row["flow_kg_s"]) <= .1
    assert len(ids)==6


@pytest.mark.parametrize("counts",[
    {"train":0,"validation":1,"test":1,"ood":1},
    {"train":1,"validation":-1,"test":1,"ood":1},
    {"train":1,"validation":1,"test":1},
    {"train":1,"validation":1,"test":1,"ood":True},
])
def test_bad_partition_specifications_rejected(tmp_path,counts):
    with pytest.raises(ValueError):
        generate_dataset(tmp_path/"fail",counts=counts)


def test_bad_cell_count_rejected(tmp_path):
    with pytest.raises(ValueError):
        generate_dataset(
            tmp_path/"fail", counts={"train":1,"validation":1,"test":1,"ood":1},
            n_cells=0
        )
