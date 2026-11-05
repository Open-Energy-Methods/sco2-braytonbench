"""Stuttgart H1: measured local-HTC vs uncalibrated forced-convection baselines.

Data: Theologou et al. (2022), Mendeley DOI 10.17632/4mvk4nxrkz.1, CC BY 4.0.
Original reduced experimental profiles and uncertainties are preserved in CSV.
NO correlation coefficients are fitted on these data.

Reference handling: the published local bulk enthalpies used REFPROP. To avoid
an unverified h=0 reference match, reconstruct each CO2 bulk state using the
measured inlet temperature and the *within-run enthalpy increment*: H_CP(P,Tin)
+ [h_source(x)-h_source(x=0)]. Pressure is held at measured inlet P because
axial pressure records are not available. This is a stated approximation.

The reported local HTC is itself experimentally DERIVED using wall and bulk
states, not an independent raw heat-flux sensor. Reported HTC sigma is used
for a descriptive residual-to-sigma ratio only; it is NOT a full covariance
or expanded experimental uncertainty model.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
from collections import Counter, defaultdict
from pathlib import Path
from statistics import mean, median
from typing import Callable

SOURCE_DOI = "10.17632/4mvk4nxrkz.1"
SOURCE_ANOMALY = "4MM_HM_77.5_10_20_90_A"
MODELS = ("gnielinski_smooth_bulk", "dittus_boelter_heating_bulk")
SPLIT_SALT = "BraytonBench-STU-H1-v1-2026-11-05"


def nominal_family(experiment_id: str) -> str:
    parts = experiment_id.split("_")
    if len(parts) < 4 or parts[1] not in ("HB", "HM", "HT"):
        raise ValueError(f"unexpected experiment identifier {experiment_id!r}")
    parts[1] = "H*"
    return "_".join(parts)


def holdout_families(experiment_ids: list[str], fraction: float = 0.22) -> set[str]:
    groups = sorted({nominal_family(k) for k in experiment_ids})
    ranked = sorted(groups, key=lambda g: hashlib.sha256((SPLIT_SALT + "|" + g).encode()).hexdigest())
    return set(ranked[:max(1,round(len(groups)*fraction))])


def gnielinski_smooth(reynolds: float, prandtl: float, axial_over_d: float) -> float:
    if not (3_000 <= reynolds <= 5_000_000 and 0.5 <= prandtl <= 2000
            and axial_over_d >= 10):
        raise ValueError("outside_Gnielinski_domain")
    f = (0.79 * math.log(reynolds) - 1.64) ** -2
    return ((f / 8) * (reynolds - 1000) * prandtl /
            (1 + 12.7 * math.sqrt(f / 8) * (prandtl ** (2 / 3) - 1)))


def dittus_boelter_heating(reynolds: float, prandtl: float, axial_over_d: float) -> float:
    # Textbook fully-developed turbulent heating reference, not an sCO2
    # buoyancy/pseudocritical-specific correlation.
    if not (reynolds >= 10_000 and 0.7 <= prandtl <= 160 and axial_over_d >= 10):
        raise ValueError("outside_Dittus_Boelter_domain")
    return 0.023 * reynolds ** 0.8 * prandtl ** 0.4


def _float(d: dict, key: str) -> float:
    value = d[key]
    x = float(value)
    if not math.isfinite(x):
        raise ValueError(f"nonfinite_{key}")
    return x


def _read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def _percentiles(values: list[float], q: float) -> float | None:
    if not values:
        return None
    a = sorted(values)
    k = (len(a)-1) * q
    lo = int(k)
    hi = min(len(a)-1,lo+1)
    return a[lo] + (a[hi]-a[lo])*(k-lo)


def _metrics(rows: list[dict]) -> dict:
    if not rows:
        return {"n": 0, "mape_pct": None, "mean_bias_pct": None, "median_ape_pct": None,
                "p90_ape_pct": None, "rmspe_pct": None, "sigma_normalized_median_abs": None,
                "within_reported_1sigma_fraction_descriptive_only": None,
                "mean_run_mape_pct": None}
    residuals = [v["relative_residual_pct"] for v in rows]
    ape = [abs(v) for v in residuals]
    sr = [abs(v["sigma_normalized_residual"]) for v in rows if v["sigma_normalized_residual"] is not None]
    byrun = defaultdict(list)
    for row in rows:
        byrun[row["experiment_id"]].append(abs(row["relative_residual_pct"]))
    return {
        "n": len(rows),
        "n_runs": len(byrun),
        "mape_pct": mean(ape),
        "mean_bias_pct": mean(residuals),
        "median_ape_pct": median(ape),
        "p90_ape_pct": _percentiles(ape, 0.9),
        "rmspe_pct": math.sqrt(mean([e*e for e in residuals])),
        "sigma_normalized_median_abs": median(sr) if sr else None,
        "within_reported_1sigma_fraction_descriptive_only": sum(v <= 1 for v in sr)/len(sr) if sr else None,
        "mean_run_mape_pct": mean([mean(v) for v in byrun.values()]),
    }


def evaluate(index_csv: Path, axial_csv: Path, props: Callable,
             output_dir: Path, *, min_points_per_run: int = 1) -> dict:
    """For production use pass CoolProp.CoolProp.PropsSI as props.

    The fake props injected by tests are for mathematical smoke tests only.
    """
    index_rows = _read_csv(index_csv)
    axial_rows = _read_csv(axial_csv)
    index = {r["experiment_id"]: r for r in index_rows}
    if len(index) != 54 or len(index_rows) != 54:
        raise ValueError("source integrity gate: expected 54 unique experiment records")
    if len(axial_rows) != 2508:
        raise ValueError("source integrity gate: expected 2508 axial records")
    if any(r["experiment_id"] not in index for r in axial_rows):
        raise ValueError("axial data include unregistered experiment")
    source_points = sum(bool(r["heat_transfer_coefficient_w_m2_k"]) for r in axial_rows)
    if source_points != 2398:
        raise ValueError("source integrity gate: expected 2398 local-HTC values")

    baselines = {
        "gnielinski_smooth_bulk": gnielinski_smooth,
        "dittus_boelter_heating_bulk": dittus_boelter_heating,
    }
    families = holdout_families(list(index))
    axes = defaultdict(list)
    for r in axial_rows:
        axes[r["experiment_id"]].append(r)
    first_h = {}
    for experiment_id,rows in axes.items():
        first = min(rows,key=lambda x:_float(x,"axial_position_m"))
        if abs(_float(first,"axial_position_m")) > 1e-10:
            raise ValueError(f"missing inlet enthalpy anchor x=0 for {experiment_id}")
        first_h[experiment_id] = _float(first,"bulk_enthalpy_j_kg")

    output = []
    rejected = []
    model_domain = Counter()
    skipped_anomaly_points = 0
    for experiment_id in sorted(index):
        meta = index[experiment_id]
        if experiment_id == SOURCE_ANOMALY:
            skipped_anomaly_points += sum(bool(r["heat_transfer_coefficient_w_m2_k"])
                                          for r in axes[experiment_id])
            rejected.append({"experiment_id":experiment_id,"reason":"STU-001_source_anomaly_quarantined"})
            continue
        d = _float(meta, "pipe_inner_diameter_mm")/1000
        m = _float(meta, "mass_flow_kg_s")
        pressure = _float(meta, "pressure_in_bar") * 1e5
        t_in = _float(meta, "temperature_in_c") + 273.15
        if m <= 0 or d <= 0 or pressure <= 7.4e6:
            rejected.append({"experiment_id":experiment_id,"reason":"invalid_bulk_inlet_properties"})
            continue
        try:
            h_in_cp = props("Hmass","P",pressure,"T",t_in,"HEOS::CO2")
        except (ValueError,RuntimeError,OverflowError) as exc:
            rejected.append({"experiment_id":experiment_id,"reason":"inlet_property_failure","details":str(exc)[:130]})
            continue
        valid_in_run=0
        for row in sorted(axes[experiment_id],key=lambda x:_float(x,"axial_position_m")):
            if not row["heat_transfer_coefficient_w_m2_k"]:
                continue
            h_obs=_float(row,"heat_transfer_coefficient_w_m2_k")
            if h_obs<=0:
                rejected.append({"experiment_id":experiment_id,"x_m":row["axial_position_m"],"reason":"nonpositive_experimental_htc"})
                continue
            x=_float(row,"axial_position_m")
            # REFPROP vs CoolProp reference-offset alignment by measured inlet T.
            dh=_float(row,"bulk_enthalpy_j_kg")-first_h[experiment_id]
            try:
                t_bulk=props("T","P",pressure,"Hmass",h_in_cp+dh,"HEOS::CO2")
                cp=props("Cpmass","P",pressure,"T",t_bulk,"HEOS::CO2")
                mu=props("VISCOSITY","P",pressure,"T",t_bulk,"HEOS::CO2")
                k=props("CONDUCTIVITY","P",pressure,"T",t_bulk,"HEOS::CO2")
                if not all(math.isfinite(v) and v>0 for v in (t_bulk,cp,mu,k)):
                    raise ValueError("invalid_CoolProp_transport_state")
            except (ValueError,RuntimeError,OverflowError) as exc:
                rejected.append({"experiment_id":experiment_id,"x_m":x,"reason":"CO2_property_failure","details":str(exc)[:130]})
                continue
            re = 4*m/(math.pi*d*mu)
            pr = cp*mu/k
            for model_name,formula in baselines.items():
                try:
                    nu=formula(re,pr,x/d)
                    predicted=nu*k/d
                    if not math.isfinite(predicted) or predicted<=0:
                        raise ValueError("invalid_prediction")
                except ValueError as exc:
                    model_domain[(model_name,str(exc))] += 1
                    continue
                sigma_pct=_float(row,"htc_reported_sigma_pct") if row["htc_reported_sigma_pct"] else None
                relative=100*(predicted-h_obs)/h_obs
                result={
                    "experiment_id":experiment_id,
                    "nominal_family":nominal_family(experiment_id),
                    "split":"held_out" if nominal_family(experiment_id) in families else "development",
                    "orientation":meta["orientation_code"],
                    "diameter_mm":_float(meta,"pipe_inner_diameter_mm"),
                    "axial_position_m":x,
                    "x_over_d":x/d,
                    "pressure_pa_assumed_constant":pressure,
                    "bulk_temperature_k_from_inlet_anchored_delta_h":t_bulk,
                    "measured_wall_temperature_k_diagnostic_only":_float(row,"inner_wall_temperature_c")+273.15 if row["inner_wall_temperature_c"] else None,
                    "reynolds":re,"prandtl":pr,"model":model_name,
                    "predicted_htc_w_m2_k":predicted,
                    "measured_reduced_htc_w_m2_k":h_obs,
                    "reported_htc_sigma_pct":sigma_pct,
                    "relative_residual_pct":relative,
                    "sigma_normalized_residual":relative/sigma_pct if sigma_pct and sigma_pct>0 else None,
                }
                output.append(result)
                valid_in_run += 1
        if valid_in_run < min_points_per_run:
            rejected.append({"experiment_id":experiment_id,"reason":"insufficient_valid_predictions","model_points":valid_in_run})

    per_model={}
    for name in baselines:
        rows=[r for r in output if r["model"]==name]
        by_orientation={o:_metrics([r for r in rows if r["orientation"]==o]) for o in ("HB","HM","HT")}
        by_split={s:_metrics([r for r in rows if r["split"]==s]) for s in ("development","held_out")}
        by_diameter={str(d):_metrics([r for r in rows if r["diameter_mm"]==d]) for d in (4.0,8.0)}
        by_family=defaultdict(list)
        for r in rows:
            by_family[r["nominal_family"]].append(r)
        per_model[name]={
            "overall":_metrics(rows),
            "orientation":by_orientation,"split":by_split,"diameter_mm":by_diameter,
            "mean_nominal_family_mape_pct":mean([_metrics(group)["mape_pct"] for group in by_family.values()]) if by_family else None,
            "n_nominal_families":len(by_family),
        }

    output_dir.mkdir(parents=True,exist_ok=True)
    columns=list(output[0]) if output else ["experiment_id","model","relative_residual_pct"]
    with (output_dir/"local_predictions.csv").open("w",encoding="utf-8",newline="") as handle:
        writer=csv.DictWriter(handle,fieldnames=columns)
        writer.writeheader()
        writer.writerows(output)
    by_model=Counter(r["model"] for r in output)
    result={
        "study":"Stuttgart H1; uncalibrated forced-convection baselines versus experimentally-derived local HTC",
        "source_dataset_doi":SOURCE_DOI,"source_license":"CC BY 4.0",
        "input_counts":{"experiments":54,"axial_records":2508,"reported_local_htc":2398,
                        "quarantined_experiments":1,"quarantined_htc_records":skipped_anomaly_points,
                        "retained_observed_htc":2398-skipped_anomaly_points,
                        "successfully_predicted_by_model":dict(by_model)},
        "split":{"unit":"nominal_family_of_three_orientations","salt":SPLIT_SALT,
                 "held_out_families":sorted(families),"no_parameter_fitting":True},
        "models":per_model,
        "domain_exclusions":[{"model":k[0],"reason":k[1],"n":v}
                             for k,v in sorted(model_domain.items())],
        "exceptions":rejected,
        "assumptions":[
            "Data local HTC is derived from experimental wall, bulk, and heat-flux quantities, not an independent raw sensor",
            "Within each run bulk enthalpy increments referenced to measured inlet T align REFPROP data with CoolProp without asserting absolute enthalpy reference equality",
            "CO2 axial pressure held equal to measured inlet P; no measured axial pressure map supplied",
            "Bulk-fluid properties only; uniform circular-tube forced-convection correlations are orientation-blind",
            "Gnielinski smooth f=(0.79 ln Re-1.64)^(-2), x/D>=10, 3000<=Re<=5e6, 0.5<=Pr<=2000",
            "Dittus-Boelter heating Nu=.023 Re^.8 Pr^.4, x/D>=10, Re>=1e4, 0.7<=Pr<=160",
            "Zero fitted parameters; held-out partition indicates leakage-safe groups for subsequent model development, not a fitted predictive validation",
            "Reported HTC sigma used descriptively without input covariance propagation, and axial residuals from one run are correlated",
            "STU-001 original anomalous q source retained but entire run quarantined from baselines",
            "Baseline is not buoyancy-, wall-property-, thermal-entry-, pseudocritical- or circumferential-stratification-aware",
            "Experimental-source uncertainty and 1D correlation limitations must be independently reviewed before any publication claim"
        ],
        "verification_class":"external_experimental_derived_component_HTC_comparison_not_full_cycle_validation"
    }
    (output_dir/"report.json").write_text(json.dumps(result,indent=2,allow_nan=False)+"\n",encoding="utf-8")
    return result


def main() -> None:
    parser=argparse.ArgumentParser()
    parser.add_argument("--data-dir",type=Path,default=Path("data/validation/stuttgart"))
    parser.add_argument("--out",type=Path,default=Path("evidence/generated/stuttgart_h1"))
    args=parser.parse_args()
    try:
        from CoolProp.CoolProp import PropsSI
        import CoolProp
    except ImportError as e:
        raise SystemExit("CoolProp 8.0.0 required: install with pip install -e '.[co2]'") from e
    report=evaluate(args.data_dir/"experiment_index.csv",args.data_dir/"axial_profiles.csv",PropsSI,args.out)
    report["CoolProp_version"]=CoolProp.__version__
    (args.out/"report.json").write_text(json.dumps(report,indent=2)+"\n",encoding="utf-8")
    print(json.dumps({"CoolProp":CoolProp.__version__,"input_counts":report["input_counts"],
                      "models":{k:{"overall":v["overall"],"held_out":v["split"]["held_out"]}
                       for k,v in report["models"].items()},
                       "domain_exclusions":report["domain_exclusions"]},indent=2))


if __name__=="__main__":
    main()
