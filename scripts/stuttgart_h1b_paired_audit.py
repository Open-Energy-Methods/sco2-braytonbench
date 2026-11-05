"""Paired Stuttgart H1b audit with deterministic nominal-family bootstrap.

Each comparison uses the SAME axial source stations. There is NO
calibration or resplitting. The bootstrap resamples 18 nominal
experiment families, not thousands of correlated axial measurements.
Its percentile interval indicates *between-family sampling
variability*, NOT experimental measurement uncertainty, model
confidence coverage, or external-domain generalization.
"""
import csv
from collections import defaultdict
import json
from pathlib import Path
import random
from statistics import mean,median

SRC=Path("evidence/generated/stuttgart_h1b/h1b_pointwise.csv")
OUT=Path("evidence/generated/stuttgart_h1b/h1b_paired_audit.json")
RANDOM_SEED=20261105
BOOTSTRAPS=10000


def compute(rows:list[dict])->dict:
    bypoint=defaultdict(dict)
    for row in rows:
        key=(row["experiment_id"],row["axial_position_m"])
        if row["model"] in bypoint[key]:
            raise ValueError("duplicate model-station in H1b evidence")
        bypoint[key][row["model"]]=row
    matched=[
        z for z in bypoint.values()
        if "bishop_flux_inverted" in z and "jackson_flux_inverted" in z
    ]
    if not matched:
        raise ValueError("no paired Bishop-Jackson flux-inverted source observations")
    fam=defaultdict(list)
    orient=defaultdict(list)
    held=defaultdict(list)
    q_htc_relative=[]
    for z in matched:
        bishop=z["bishop_flux_inverted"]
        jackson=z["jackson_flux_inverted"]
        if (bishop["split"]!=jackson["split"] or
                bishop["nominal_family"]!=jackson["nominal_family"] or
                bishop["orientation"]!=jackson["orientation"]):
            raise ValueError("different split/identity for paired model results")
        b=abs(float(bishop["relative_residual_pct"]))
        j=abs(float(jackson["relative_residual_pct"]))
        diff=j-b  # positive means Bishop lower error
        fam[bishop["nominal_family"]].append(diff)
        orient[bishop["orientation"]].append(diff)
        if bishop["split"]=="held_out":
            held[bishop["nominal_family"]].append(diff)
        # Confirm that source local HTC is a reduced quantity using
        # source heat flux and measured wall/bulk temperature.
        q=float(bishop["input_heat_flux_w_m2"])
        tw=float(bishop["measured_wall_temperature_k_diagnostic_only"])
        tb=float(bishop["bulk_temperature_k"])
        observed=float(bishop["measured_derived_htc_w_m2_k"])
        q_htc_relative.append(100*((q/(tw-tb))/observed-1))

    families=sorted(fam)
    if len(families)!=18 or len(held)!=4:
        raise ValueError("nominal family and held-out sets have changed")
    means={k:mean(fam[k]) for k in families}
    seed=random.Random(RANDOM_SEED)
    replicates=[]
    for _ in range(BOOTSTRAPS):
        selected=[families[seed.randrange(len(families))]
                  for _ in families]
        replicates.append(mean(means[k] for k in selected))
    replicates.sort()
    # Ordered bootstrap percentiles; not a parametric confidence interval.
    result={
        "meaning":"positive Jackson APE minus Bishop APE favors Bishop",
        "n_paired_axial_stations":len(matched),
        "n_nominal_families":len(families),
        "n_held_out_families":len(held),
        "paired_stationwise_mean_difference_pp":mean(
            [v for x in fam.values() for v in x]),
        "nominal_family_equal_weight_mean_difference_pp":mean(means.values()),
        "n_families_bishop_better":sum(v>0 for v in means.values()),
        "n_families_jackson_better":sum(v<0 for v in means.values()),
        "nominal_family_bootstrap":{
            "seed":RANDOM_SEED,"replicates":BOOTSTRAPS,
            "percentile_2p5_pp":replicates[249],
            "percentile_97p5_pp":replicates[9749],
            "interpretation":"Between-family resampling variability only; no measurement uncertainty covariance or external validation"
        },
        "held_out_family_paired_difference_pp":{
            k:mean(held[k]) for k in sorted(held)
        },
        "orientation_paired_difference_pp":{
            k:mean(orient[k]) for k in sorted(orient)
        },
        "source_HTC_derived_consistency":{
            "median_abs_percent_mismatch_q_over_deltaT":median(
                abs(x) for x in q_htc_relative),
            "mean_abs_percent_mismatch_q_over_deltaT":mean(
                abs(x) for x in q_htc_relative),
            "notes":"This near-identity is expected because HTC is derived from heat flux and wall-to-bulk temperature difference; source HTC and Tw are not independent outcomes"
        },
        "methodological_limits":[
            "Bishop and Jackson compared ONLY on shared Bishop-eligible stations",
            "Fixed source quarantine and original four hold-out nominal families unchanged",
            "18 source families are not independent plant samples",
            "Bootstrap interval is not a predictive uncertainty interval",
            "No coefficients fitted or newly optimized against any held-out data",
        ]
    }
    return result


def main():
    with SRC.open(encoding="utf-8",newline="") as f:
        rows=list(csv.DictReader(f))
    data=compute(rows)
    OUT.parent.mkdir(parents=True,exist_ok=True)
    OUT.write_text(json.dumps(data,indent=2,allow_nan=False)+"\n",
                   encoding="utf-8")
    print(json.dumps(data,indent=2))


if __name__=="__main__":
    main()
