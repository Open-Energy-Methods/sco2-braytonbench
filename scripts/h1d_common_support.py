"""Exact station-support audit for three Kim 2019 H1d variants.

All flux-driven variants are scored on the INTERSECTION of their successful
Stuttgart HB/HT station IDs. No fitted parameters, no measured-wall input,
and no implicit replacement of failed roots. A matched Jackson baseline
is computed on those exact same stations. Entire dataset is outside the
original Kim published heat-flux range.
"""
from __future__ import annotations

import argparse
import csv
import json
import math
import random
from collections import Counter, defaultdict
from pathlib import Path
from statistics import mean

VARIANTS = ("semi_empirical", "empirical_literal", "empirical_hypothesis")
BASELINE = "matched_jackson_flux_error_pct"
FIELDS = (
    "experiment_id", "axial_position_m", "orientation", "nominal_family",
    "split", "diameter_mm", "experimental_reduced_htc_w_m2_k",
    "source_reported_heat_flux_w_m2", "relative_error_pct", BASELINE
)


def _station(row: dict) -> tuple[str, str, str]:
    return (row["experiment_id"], row["axial_position_m"], row["orientation"])


def _error(row: dict, column: str) -> float:
    value = float(row[column])
    if not math.isfinite(value):
        raise ValueError("Non-finite station error: " + column)
    return value


def read_variant(path: Path, name: str) -> dict:
    """Enforce unambiguous successful source-station ID and provenance."""
    records = {}
    with path.open(newline="", encoding="utf-8") as fh:
        reader = csv.DictReader(fh)
        if not set(FIELDS).issubset(reader.fieldnames or []):
            raise ValueError("Missing required H1d fields in " + str(path))
        for row in reader:
            if row["mode"] != "flux_driven_inverse":
                continue
            if row["model"] != name or row["orientation"] not in ("HB", "HT"):
                raise ValueError("Wrong model or unsupported wall orientation")
            if row["split"] not in ("development", "held_out"):
                raise ValueError("Invalid original Stuttgart holdout split")
            if row["original_source_flux_exceeds_both_dataset_maxima"].lower() != "true":
                raise ValueError("Source-fit domain misrepresented")
            key = _station(row)
            if key in records:
                raise ValueError("Duplicate successful source station " + repr(key))
            _error(row, "relative_error_pct")
            _error(row, BASELINE)
            records[key] = row
    if not records or len(records) > 1580:
        raise ValueError("Implausible source-station coverage")
    return records


def _metrics(rows: list[dict], error_field: str) -> dict:
    if not rows:
        return {"n": 0, "mape_pct": None, "family_macro_mape_pct": None}
    abs_values = [abs(_error(r, error_field)) for r in rows]
    families = defaultdict(list)
    for row, value in zip(rows, abs_values):
        families[row["nominal_family"]].append(value)
    return {
        "n": len(rows),
        "families": len(families),
        "mape_pct": mean(abs_values),
        "signed_bias_pct": mean(_error(r, error_field) for r in rows),
        "family_macro_mape_pct": mean(mean(v) for v in families.values()),
        "held_out_n": sum(r["split"] == "held_out" for r in rows),
        "held_out_mape_pct": (
            mean(abs(_error(r, error_field)) for r in rows
                 if r["split"] == "held_out")
            if any(r["split"] == "held_out" for r in rows) else None
        ),
        "HB_mape_pct": mean(abs(_error(r, error_field)) for r in rows if r["orientation"] == "HB")
                        if any(r["orientation"] == "HB" for r in rows) else None,
        "HT_mape_pct": mean(abs(_error(r, error_field)) for r in rows if r["orientation"] == "HT")
                        if any(r["orientation"] == "HT" for r in rows) else None,
    }


def _paired_bootstrap(rows: list[dict], variant_field: str) -> dict:
    groups = defaultdict(list)
    for r in rows:
        groups[r["nominal_family"]].append(
            abs(_error(r, BASELINE)) - abs(_error(r, variant_field))
        )
    advantages = [mean(groups[name]) for name in sorted(groups)]
    if not advantages:
        raise ValueError("No matched nominal families")
    randomizer = random.Random(20261105)
    draws = sorted(mean(advantages[randomizer.randrange(len(advantages))]
                        for _ in advantages) for _ in range(3000))
    return {
        "matched_families": len(advantages),
        "family_equal_advantage_over_Jackson_pp": mean(advantages),
        "n_families_with_lower_Kim_error": sum(x > 0 for x in advantages),
        "percentile_interval_3000draws_pp": [draws[74], draws[2924]],
        "interpretation": "Between-family resampling only; NOT measurement uncertainty or in-domain performance"
    }


def compare(root: Path, output: Path) -> dict:
    collections = {}
    source_splits = None
    for name in VARIANTS:
        directory = root / ("g35d-kim-" + name)
        report = json.loads((directory / "kim_report.json").read_text(encoding="utf-8"))
        if (report["variant"] != name
            or report["original_eligible_source_stations"] != 2318
            or report["HB_candidate"] != 790
            or report["HT_candidate"] != 790
            or report["HM_excluded_by_definition"] != 738
            or not report["whole_anomalous_run_quarantined"]
            or not report["no_coefficient_fit"]
            or report["source_fit_overlap"]["source_flux_exceeds_max"] != 1580):
            raise ValueError("Changed original H1d data provenance or no-fit gate")
        if source_splits is None:
            source_splits = report["holdouts_unchanged"]
        elif report["holdouts_unchanged"] != source_splits:
            raise ValueError("The variants used different original holdouts")
        observations = read_variant(directory / "kim_pointwise.csv", name)
        if len(observations) != report["model_metrics"]["flux_driven_inverse"]["all"]["n"]:
            raise ValueError("CSV and signed-off model JSON coverage disagree")
        collections[name] = observations

    common_keys = sorted(set.intersection(*(set(c) for c in collections.values())))
    if not common_keys:
        raise ValueError("No common successfully solved stations")
    rows_by_variant = {name: [coll[key] for key in common_keys]
                       for name, coll in collections.items()}
    reference_name = VARIANTS[0]
    aligned = []
    for key in common_keys:
        reference = collections[reference_name][key]
        for name in VARIANTS[1:]:
            compared = collections[name][key]
            for field in ("nominal_family", "split", "diameter_mm",
                          "experimental_reduced_htc_w_m2_k",
                          "source_reported_heat_flux_w_m2", BASELINE):
                if reference[field] != compared[field]:
                    raise ValueError("Source metadata differs across variants at " + repr(key))
        aligned.append({
            "experiment_id": reference["experiment_id"],
            "axial_position_m": reference["axial_position_m"],
            "orientation": reference["orientation"],
            "nominal_family": reference["nominal_family"],
            "split": reference["split"],
            "diameter_mm": reference["diameter_mm"],
            "source_heat_flux_w_m2": reference["source_reported_heat_flux_w_m2"],
            "measured_derived_htc_w_m2_k": reference["experimental_reduced_htc_w_m2_k"],
            "Jackson_error_pct": reference[BASELINE],
            **{name + "_error_pct": collections[name][key]["relative_error_pct"]
               for name in VARIANTS},
        })

    comparison = {
        "status": "out_of_original_fit_domain_common_station_extrapolation_only",
        "source_candidate_HB_HT": 1580,
        "n_common_all_three": len(common_keys),
        "n_common_held_out": sum(r["split"] == "held_out" for r in aligned),
        "n_common_HB": sum(r["orientation"] == "HB" for r in aligned),
        "n_common_HT": sum(r["orientation"] == "HT" for r in aligned),
        "holdouts_unchanged": source_splits,
        "coverage": {
            name: {
                "successful": len(collections[name]),
                "failed_or_unresolved": 1580 - len(collections[name]),
                "missing_from_three_way_common": len(collections[name]) - len(common_keys),
                "by_orientation": dict(Counter(r["orientation"] for r in collections[name].values())),
                "held_out_successful": sum(r["split"] == "held_out" for r in collections[name].values()),
            } for name in VARIANTS
        },
        "baseline_jackson_on_common": _metrics(rows_by_variant[reference_name], BASELINE),
        "Kim_models_on_same_stations": {
            name: {
                **_metrics(rows_by_variant[name], "relative_error_pct"),
                "paired_vs_Jackson": _paired_bootstrap(rows_by_variant[name], "relative_error_pct"),
            } for name in VARIANTS
        },
        "guardrails": [
            "The common-station subset excludes at least one nonconverged root and is not a random sample.",
            "The empirical exponent-sign hypothesis is NOT verified by Kim et al.",
            "All observations exceed the original published Kim 26.9 kW/m2 maximum heat-flux envelope.",
            "Jackson and all three Kim models are evaluated on identical original station IDs.",
            "No original 620-point Kim study reproduction, no industrial PCHE or full-cycle validation.",
        ],
    }
    output.mkdir(parents=True, exist_ok=True)
    (output / "common_station_comparison.json").write_text(
        json.dumps(comparison, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    with (output / "common_station_errors.csv").open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=list(aligned[0]))
        writer.writeheader()
        writer.writerows(aligned)
    with (output / "common_station_comparison.csv").open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=[
            "model", "common_n", "mape_pct", "family_macro_mape_pct",
            "held_out_n", "held_out_mape_pct", "HB_mape_pct", "HT_mape_pct",
            "family_equal_advantage_over_Jackson_pp"
        ])
        writer.writeheader()
        for name, stats in [
            ("Jackson–Hall", comparison["baseline_jackson_on_common"]),
            *[(name, comparison["Kim_models_on_same_stations"][name]) for name in VARIANTS]
        ]:
            writer.writerow({
                "model": name, "common_n": stats["n"],
                "mape_pct": stats["mape_pct"],
                "family_macro_mape_pct": stats["family_macro_mape_pct"],
                "held_out_n": stats["held_out_n"],
                "held_out_mape_pct": stats["held_out_mape_pct"],
                "HB_mape_pct": stats["HB_mape_pct"],
                "HT_mape_pct": stats["HT_mape_pct"],
                "family_equal_advantage_over_Jackson_pp":
                    stats.get("paired_vs_Jackson", {}).get("family_equal_advantage_over_Jackson_pp")
            })
    md = [
        "# H1d — EXACT common-station conditional HTC comparison",
        "",
        f"Common supported HB/HT stations: **{len(common_keys)}/1580**; held-out: **{comparison['n_common_held_out']}**.",
        "These were not selected for small error; they are only the intersection of successful physical root solvers.",
        "All stations exceed the published original Kim heat-flux fit envelope.",
        "",
        "| Flux-driven model | Common n | MAPE | Family macro MAPE | Held-out MAPE |",
        "|---|---:|---:|---:|---:|",
    ]
    for name, stat in [
        ("Jackson–Hall", comparison["baseline_jackson_on_common"]),
        *[(n, comparison["Kim_models_on_same_stations"][n]) for n in VARIANTS]
    ]:
        md.append(f"| {name} | {stat['n']} | {stat['mape_pct']:.2f}% | "
                  f"{stat['family_macro_mape_pct']:.2f}% | {stat['held_out_mape_pct']:.2f}% |")
    md.extend([
        "",
        "**Only same-ID rows are directly comparable.** The literal empirical equation and unverified",
        "empirical sign hypothesis remain separately labelled and should not be treated as author-validated.",
        "The reported family bootstrap is between-family sensitivity, not statistical predictive confidence.",
        "Unresolved root failures and universal source-domain extrapolation remain scientific blockers.",
        "",
    ])
    (output / "common_station_comparison.md").write_text("\n".join(md), encoding="utf-8")
    print("\n".join(md))
    return comparison


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input-root", type=Path, default=Path("evidence/kim-h1d-collected"))
    parser.add_argument("--out", type=Path, default=Path("evidence/generated/kim-h1d-summary"))
    args = parser.parse_args()
    compare(args.input_root, args.out)


if __name__ == "__main__":
    main()
