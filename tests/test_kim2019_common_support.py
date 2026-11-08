"""H1d matched-support audit tests with deliberately incomplete root coverage."""
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path
import csv
import json
import pytest


def _module():
    path = Path(__file__).resolve().parents[1] / "scripts" / "h1d_common_support.py"
    spec = spec_from_file_location("h1d_common_support", path)
    module = module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def _write_fixture(root, *, tamper=False, duplicate=False):
    variants = ("semi_empirical", "empirical_literal", "empirical_hypothesis")
    identifiers = [
        ("test_run", "0.1", "HB", "family_one", "development", "10", "20"),
        ("test_run", "0.2", "HT", "family_two", "held_out", "-40", "-30"),
        ("test_run", "0.3", "HB", "family_three", "development", "15", "5"),
    ]
    fieldnames = [
        "experiment_id", "axial_position_m", "orientation", "nominal_family",
        "split", "diameter_mm", "experimental_reduced_htc_w_m2_k",
        "source_reported_heat_flux_w_m2", "relative_error_pct",
        "matched_jackson_flux_error_pct", "mode", "model",
        "original_source_flux_exceeds_both_dataset_maxima"
    ]
    for name in variants:
        directory = root / ("g35d-kim-" + name)
        directory.mkdir(parents=True)
        items = identifiers if name != "empirical_literal" else identifiers[:2]
        records = []
        for j, (exp, x, ori, fam, split, base, semi) in enumerate(items):
            errors = {
                "semi_empirical": (10, -30, 10),
                "empirical_literal": (30, -10, 0),
                "empirical_hypothesis": (5, -20, 5),
            }
            records.append(dict(zip(fieldnames, [
                exp, x, ori, fam, split, "8", "1200", "30550",
                str(errors[name][j]),
                "99" if tamper and name == "empirical_literal" and j == 0 else base,
                "flux_driven_inverse", name, "True"
            ])))
        if duplicate and name == "semi_empirical":
            records.append(records[0].copy())
        with (directory / "kim_pointwise.csv").open("w", newline="", encoding="utf-8") as fh:
            writer = csv.DictWriter(fh, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(records)
        (directory / "kim_report.json").write_text(json.dumps({
            "variant": name,
            "original_eligible_source_stations": 2318,
            "HB_candidate": 790,
            "HT_candidate": 790,
            "HM_excluded_by_definition": 738,
            "whole_anomalous_run_quarantined": True,
            "no_coefficient_fit": True,
            "source_fit_overlap": {"source_flux_exceeds_max": 1580},
            "holdouts_unchanged": ["one", "two", "three", "four"],
            "model_metrics": {"flux_driven_inverse": {"all": {"n": len(items)}}},
        }), encoding="utf-8")


def test_true_common_station_support_and_held_out_metric(tmp_path):
    _write_fixture(tmp_path)
    result = _module().compare(tmp_path, tmp_path / "out")
    assert result["n_common_all_three"] == 2
    assert result["n_common_held_out"] == 1
    assert result["baseline_jackson_on_common"]["mape_pct"] == pytest.approx(25)
    metrics = result["Kim_models_on_same_stations"]
    assert metrics["semi_empirical"]["mape_pct"] == pytest.approx(20)
    assert metrics["empirical_literal"]["mape_pct"] == pytest.approx(20)
    assert metrics["empirical_hypothesis"]["mape_pct"] == pytest.approx(12.5)
    assert metrics["semi_empirical"]["held_out_mape_pct"] == pytest.approx(30)
    assert result["coverage"]["semi_empirical"]["missing_from_three_way_common"] == 1
    assert (tmp_path / "out" / "common_station_errors.csv").exists()
    markdown = (tmp_path / "out" / "common_station_comparison.md").read_text()
    assert "unverified" in markdown.lower() and "2/1580" in markdown


def test_cross_variant_source_metadata_mismatch_must_fail(tmp_path):
    _write_fixture(tmp_path, tamper=True)
    with pytest.raises(ValueError, match="Source metadata differs"):
        _module().compare(tmp_path, tmp_path / "out")


def test_duplicate_source_station_must_fail(tmp_path):
    _write_fixture(tmp_path, duplicate=True)
    with pytest.raises(ValueError, match="Duplicate"):
        _module().compare(tmp_path, tmp_path / "out")
